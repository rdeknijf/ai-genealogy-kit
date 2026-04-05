#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "private" / "genealogy.db"

SCHEMA = """
-- Individuals: Cache of GEDCOM INDI records
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY,
    name TEXT,
    birth_year INTEGER,
    death_year INTEGER,
    gedcom_record TEXT
);

-- Families: Cache of GEDCOM FAM records
CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,
    husband_id TEXT,
    wife_id TEXT,
    gedcom_record TEXT,
    FOREIGN KEY(husband_id) REFERENCES people(id),
    FOREIGN KEY(wife_id) REFERENCES people(id)
);

-- Sources: Cache of GEDCOM SOUR records
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    title TEXT,
    gedcom_record TEXT
);

-- Findings: Migration from FINDINGS.md
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    person_id TEXT,
    title TEXT,
    tier TEXT,
    status TEXT,
    date_found TEXT,
    gedcom_says TEXT,
    evidence_found TEXT,
    resolution TEXT,
    notes TEXT,
    raw_markdown TEXT,
    FOREIGN KEY(person_id) REFERENCES people(id)
);

-- Research Queue: Migration from RESEARCH_QUEUE.md
CREATE TABLE IF NOT EXISTS research_queue (
    id TEXT PRIMARY KEY,
    title TEXT,
    priority INTEGER,
    status TEXT,
    people_ids TEXT,
    goal TEXT,
    where_to_look TEXT,
    notes TEXT,
    updates JSON,
    raw_markdown TEXT
);

-- Session Logs: Audit trail for AI sessions
CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    action TEXT,
    affected_ids TEXT,
    summary TEXT
);

-- Enable Full-Text Search on findings
CREATE VIRTUAL TABLE IF NOT EXISTS findings_fts USING fts5(
    id UNINDEXED,
    person_id,
    title,
    content,
    content='findings',
    content_rowid='rowid'
);
"""

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
