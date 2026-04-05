#!/usr/bin/env python3
"""Initialize the genealogy research SQLite database from schema.sql."""

import argparse
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"


def init_db(db_path: Path, reset: bool = False):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)

    if reset:
        # Drop all tables (order matters for foreign keys)
        conn.execute("PRAGMA foreign_keys = OFF")
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()]
        for t in tables:
            conn.execute(f"DROP TABLE IF EXISTS [{t}]")
        # Also drop FTS virtual tables
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts%'"
        ).fetchall():
            conn.execute(f"DROP TABLE IF EXISTS [{r[0]}]")
        conn.commit()
        print(f"Reset: dropped {len(tables)} tables")

    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()

    # Print table list and row counts
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts_%' "
        "ORDER BY name"
    ).fetchall()

    print(f"Database: {db_path}")
    print(f"Tables ({len(tables)}):")
    for (name,) in tables:
        count = conn.execute(f"SELECT count(*) FROM [{name}]").fetchone()[0]
        print(f"  {name:<30s} {count:>8d} rows")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Initialize genealogy research database")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Database path")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")
    args = parser.parse_args()

    init_db(args.db, args.reset)


if __name__ == "__main__":
    main()
