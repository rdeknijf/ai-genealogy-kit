"""Tests for negative search tracking in research_db.py."""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "research_db.py"
MIGRATE_V2 = Path(__file__).parent.parent / "scripts" / "migrate_v2.py"


def run_db(db_path, *args):
    """Run research_db.py with args, return parsed JSON output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db", str(db_path), *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"research_db.py failed: {result.stderr}\n{result.stdout}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def ensure_negative_searches_table(db_path):
    """Ensure the negative_searches table exists (run migration)."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS negative_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT NOT NULL,
            source TEXT NOT NULL,
            query_fingerprint TEXT NOT NULL,
            query_params TEXT,
            result_class TEXT NOT NULL,
            reason TEXT,
            session_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            cooldown_until TEXT,
            UNIQUE(person_id, source, query_fingerprint)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_neg_person ON negative_searches(person_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_neg_source ON negative_searches(source)")
    conn.commit()
    conn.close()


@pytest.fixture
def neg_db(populated_db):
    """Populated DB with negative_searches table added."""
    ensure_negative_searches_table(populated_db)
    return populated_db


class TestAddNegative:
    def test_adds_negative_search(self, neg_db):
        result = run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "name=Jan&place=Apeldoorn",
            "--result", "empty",
            "--reason", "No indexed DTB records pre-1811",
        )
        assert result["status"] == "created"
        assert result["person_id"] == "I0003"

        conn = sqlite3.connect(neg_db)
        row = conn.execute("SELECT * FROM negative_searches WHERE person_id = 'I0003'").fetchone()
        conn.close()
        assert row is not None

    def test_duplicate_is_upserted(self, neg_db):
        args = [
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "name=Jan&place=Apeldoorn",
            "--result", "empty",
            "--reason", "First attempt",
        ]
        run_db(neg_db, *args)
        result = run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "name=Jan&place=Apeldoorn",
            "--result", "error",
            "--reason", "Second attempt with different result",
        )
        assert result["status"] == "upserted"

        conn = sqlite3.connect(neg_db)
        rows = conn.execute(
            "SELECT * FROM negative_searches WHERE person_id = 'I0003' AND source = 'openarchieven'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_with_session_id(self, neg_db):
        result = run_db(
            neg_db,
            "add-negative",
            "--person", "I0005",
            "--source", "wiewaswie",
            "--fingerprint", "q=test",
            "--result", "timeout",
            "--session-id", "sess-abc123",
        )
        assert result["status"] == "created"

        conn = sqlite3.connect(neg_db)
        row = conn.execute(
            "SELECT session_id FROM negative_searches WHERE person_id = 'I0005'"
        ).fetchone()
        conn.close()
        assert row[0] == "sess-abc123"

    def test_with_cooldown(self, neg_db):
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "delpher",
            "--fingerprint", "q=knijf",
            "--result", "not_indexed",
            "--cooldown", "2027-01-01",
        )
        conn = sqlite3.connect(neg_db)
        row = conn.execute(
            "SELECT cooldown_until FROM negative_searches WHERE person_id = 'I0003' AND source = 'delpher'"
        ).fetchone()
        conn.close()
        assert row[0] == "2027-01-01"


class TestCheckNegatives:
    def test_returns_empty_for_no_negatives(self, neg_db):
        result = run_db(neg_db, "check-negatives", "I0001")
        assert result["person_id"] == "I0001"
        assert result["negatives"] == []

    def test_returns_negatives_for_person(self, neg_db):
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "name=Jan&place=Apeldoorn",
            "--result", "empty",
            "--reason", "No records found",
        )
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "wiewaswie",
            "--fingerprint", "name=Jan&type=birth",
            "--result", "empty",
            "--reason", "No birth records",
        )
        result = run_db(neg_db, "check-negatives", "I0003")
        assert result["person_id"] == "I0003"
        assert len(result["negatives"]) == 2
        sources = {n["source"] for n in result["negatives"]}
        assert sources == {"openarchieven", "wiewaswie"}

    def test_filters_by_source(self, neg_db):
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "q=test1",
            "--result", "empty",
        )
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "wiewaswie",
            "--fingerprint", "q=test2",
            "--result", "empty",
        )
        result = run_db(neg_db, "check-negatives", "I0003", "--source", "openarchieven")
        assert len(result["negatives"]) == 1
        assert result["negatives"][0]["source"] == "openarchieven"

    def test_does_not_return_other_persons(self, neg_db):
        run_db(
            neg_db,
            "add-negative",
            "--person", "I0003",
            "--source", "openarchieven",
            "--fingerprint", "q=test",
            "--result", "empty",
        )
        result = run_db(neg_db, "check-negatives", "I0005")
        assert result["negatives"] == []


class TestBusyTimeout:
    def test_get_db_sets_busy_timeout(self, neg_db):
        """Verify that get_db sets PRAGMA busy_timeout."""
        sys.path.insert(0, str(SCRIPT.parent))
        from research_db import get_db

        conn = get_db(neg_db)
        timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        conn.close()
        assert timeout == 5000
