#!/usr/bin/env python3
"""Idempotent schema migration v2 for the genealogy research database.

Adds:
- negative_searches table (with indexes and unique constraint)
- coverage_before / coverage_after columns to task_runs
- work_type column to research_tasks
- requires_model column to findings (and research_tasks if missing)

Usage:
    python scripts/migrate_v2.py [db_path]   # default: private/genealogy.db
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, col_type: str
) -> bool:
    """Add a column to a table if it doesn't exist. Returns True if added."""
    if _column_exists(conn, table, column):
        print(f"  {table}.{column} already exists, skipping.")
        return False
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    print(f"  Added {column} {col_type} to {table}.")
    return True


def migrate(db_path: Path | str) -> None:
    """Run all v2 migrations idempotently."""
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path)
    changed = False

    # 1. Create negative_searches table
    if not _table_exists(conn, "negative_searches"):
        print("Adding negative_searches table...")
        conn.executescript("""
            CREATE TABLE negative_searches (
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
            );
            CREATE INDEX idx_neg_person ON negative_searches(person_id);
            CREATE INDEX idx_neg_source ON negative_searches(source);
        """)
        changed = True
    else:
        print("negative_searches table already exists, skipping.")

    # 2. Add coverage columns to task_runs
    print("Checking task_runs columns...")
    changed |= _add_column_if_missing(conn, "task_runs", "coverage_before", "REAL")
    changed |= _add_column_if_missing(conn, "task_runs", "coverage_after", "REAL")

    # 3. Add work_type to research_tasks
    print("Checking research_tasks columns...")
    changed |= _add_column_if_missing(conn, "research_tasks", "work_type", "TEXT")
    # Also ensure requires_model exists (added manually in prod, not in schema.sql)
    changed |= _add_column_if_missing(conn, "research_tasks", "requires_model", "TEXT")

    # 4. Add requires_model to findings
    print("Checking findings columns...")
    changed |= _add_column_if_missing(conn, "findings", "requires_model", "TEXT")

    conn.commit()
    conn.close()

    if not changed:
        print("Already up to date.")
    else:
        print("Migration v2 complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v2 schema migration.")
    parser.add_argument(
        "db_path",
        nargs="?",
        default=str(DEFAULT_DB),
        help=f"Path to SQLite database (default: {DEFAULT_DB})",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"Error: database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    migrate(db_path)


if __name__ == "__main__":
    main()
