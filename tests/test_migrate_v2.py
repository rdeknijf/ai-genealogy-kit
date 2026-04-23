"""Tests for scripts/migrate_v2.py — idempotent schema migration."""

import sqlite3
from pathlib import Path

import pytest
from migrate_v2 import migrate

SCHEMA_PATH = Path(__file__).parent.parent / "scripts" / "schema.sql"


@pytest.fixture
def fresh_db(tmp_path):
    """Create a temporary SQLite DB from the base schema.sql."""
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.close()
    return path


def _columns(db_path: Path, table: str) -> dict[str, str]:
    """Return {column_name: type} for a table."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    conn.close()
    return {row[1]: row[2] for row in rows}


def _table_exists(db_path: Path, table: str) -> bool:
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    conn.close()
    return row is not None


class TestMigrateV2:
    def test_creates_negative_searches_table(self, fresh_db):
        migrate(fresh_db)

        assert _table_exists(fresh_db, "negative_searches")

        cols = _columns(fresh_db, "negative_searches")
        assert "id" in cols
        assert "person_id" in cols
        assert "source" in cols
        assert "query_fingerprint" in cols
        assert "query_params" in cols
        assert "result_class" in cols
        assert "reason" in cols
        assert "session_id" in cols
        assert "created_at" in cols
        assert "cooldown_until" in cols

        # Verify UNIQUE constraint on (person_id, source, query_fingerprint)
        conn = sqlite3.connect(fresh_db)
        conn.execute(
            "INSERT INTO negative_searches (person_id, source, query_fingerprint, result_class) "
            "VALUES ('I0001', 'openarchieven', 'fp1', 'empty')"
        )
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO negative_searches "
                "(person_id, source, query_fingerprint, result_class) "
                "VALUES ('I0001', 'openarchieven', 'fp1', 'timeout')"
            )
        conn.close()

    def test_adds_task_runs_coverage_columns(self, fresh_db):
        migrate(fresh_db)

        cols = _columns(fresh_db, "task_runs")
        assert "coverage_before" in cols
        assert cols["coverage_before"] == "REAL"
        assert "coverage_after" in cols
        assert cols["coverage_after"] == "REAL"

    def test_adds_work_type_column(self, fresh_db):
        migrate(fresh_db)

        cols = _columns(fresh_db, "research_tasks")
        assert "work_type" in cols
        assert cols["work_type"] == "TEXT"

    def test_adds_findings_requires_model(self, fresh_db):
        migrate(fresh_db)

        cols = _columns(fresh_db, "findings")
        assert "requires_model" in cols
        assert cols["requires_model"] == "TEXT"

    def test_idempotent(self, fresh_db):
        """Running migration twice produces no errors."""
        migrate(fresh_db)
        migrate(fresh_db)  # should not raise

        # Verify structure is still correct after second run
        assert _table_exists(fresh_db, "negative_searches")
        cols = _columns(fresh_db, "task_runs")
        assert "coverage_before" in cols
        assert "coverage_after" in cols

    def test_migration_on_fresh_db(self, fresh_db):
        """Migration works on a DB created from the base schema.sql."""
        migrate(fresh_db)

        # All new structures exist
        assert _table_exists(fresh_db, "negative_searches")
        assert "work_type" in _columns(fresh_db, "research_tasks")
        assert "requires_model" in _columns(fresh_db, "findings")
        assert "requires_model" in _columns(fresh_db, "research_tasks")
        assert "coverage_before" in _columns(fresh_db, "task_runs")

    def test_migration_preserves_data(self, fresh_db):
        """Existing data survives the migration intact."""
        conn = sqlite3.connect(fresh_db)
        conn.execute("PRAGMA foreign_keys = ON")

        # Insert test data before migration
        conn.execute(
            "INSERT INTO persons (id, name, surname, sex, birth_year) "
            "VALUES ('I0099', 'Test Person', 'Person', 'M', 1900)"
        )
        conn.execute(
            "INSERT INTO research_tasks "
            "(id, title, priority, status, people_ids, goal, raw_markdown) "
            "VALUES ('RQ-099', 'Test task', 2, 'QUEUED', 'I0099', "
            "'Test goal', '## RQ-099')"
        )
        conn.execute(
            "INSERT INTO findings (id, title, tier, status, date_found, queue_ref, raw_markdown) "
            "VALUES ('F-099', 'Test finding', 'C', 'OPEN', '2026-04-23', 'RQ-099', '## F-099')"
        )
        conn.execute(
            "INSERT INTO task_runs (task_id, session_id, summary) "
            "VALUES ('RQ-099', 'sess-1', 'Test run')"
        )
        conn.commit()
        conn.close()

        migrate(fresh_db)

        conn = sqlite3.connect(fresh_db)
        conn.row_factory = sqlite3.Row

        # Verify all original data is intact
        person = conn.execute("SELECT * FROM persons WHERE id = 'I0099'").fetchone()
        assert person["name"] == "Test Person"
        assert person["birth_year"] == 1900

        task = conn.execute("SELECT * FROM research_tasks WHERE id = 'RQ-099'").fetchone()
        assert task["title"] == "Test task"
        assert task["status"] == "QUEUED"

        finding = conn.execute("SELECT * FROM findings WHERE id = 'F-099'").fetchone()
        assert finding["title"] == "Test finding"
        assert finding["tier"] == "C"

        run = conn.execute("SELECT * FROM task_runs WHERE session_id = 'sess-1'").fetchone()
        assert run["summary"] == "Test run"

        conn.close()
