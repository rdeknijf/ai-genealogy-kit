-- Genealogy research database schema
-- SQLite with WAL mode for concurrent reads

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- ============================================================
-- GEDCOM cache tables
-- ============================================================

CREATE TABLE IF NOT EXISTS persons (
    id TEXT PRIMARY KEY,           -- e.g. I0000, I501685
    name TEXT,                     -- full GEDCOM name (with slashes removed)
    surname TEXT,
    sex TEXT,
    birth_date TEXT,
    birth_place TEXT,
    birth_year INTEGER,
    death_date TEXT,
    death_place TEXT,
    death_year INTEGER,
    gedcom_blob TEXT               -- raw GEDCOM lines joined by newline
);

CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,           -- e.g. F0001
    husband_id TEXT REFERENCES persons(id),
    wife_id TEXT REFERENCES persons(id),
    marr_date TEXT,
    marr_place TEXT,
    gedcom_blob TEXT
);

CREATE TABLE IF NOT EXISTS family_children (
    family_id TEXT NOT NULL REFERENCES families(id),
    child_id TEXT NOT NULL REFERENCES persons(id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (family_id, child_id)
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,           -- e.g. S600001
    title TEXT,
    author TEXT,
    publication TEXT,
    gedcom_blob TEXT
);

-- ============================================================
-- Research state tables
-- ============================================================

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,           -- e.g. F-001
    title TEXT,
    tier TEXT,                     -- A, B, C, D
    status TEXT,                   -- OPEN, VERIFIED, REJECTED, APPLIED, PARTIALLY RESOLVED
    date_found TEXT,
    queue_ref TEXT,                -- e.g. RQ-001
    raw_markdown TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    requires_model TEXT
);

CREATE TABLE IF NOT EXISTS finding_persons (
    finding_id TEXT NOT NULL REFERENCES findings(id),
    person_id TEXT NOT NULL,
    role TEXT DEFAULT 'subject',   -- subject, parent, spouse, etc.
    PRIMARY KEY (finding_id, person_id)
);

CREATE TABLE IF NOT EXISTS research_tasks (
    id TEXT PRIMARY KEY,           -- e.g. RQ-001
    title TEXT,
    priority INTEGER DEFAULT 3,
    status TEXT,                   -- QUEUED, IN_PROGRESS, DONE, BLOCKED
    people_ids TEXT,               -- comma-separated person IDs
    goal TEXT,
    where_to_look TEXT,
    raw_markdown TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    requires_model TEXT,
    work_type TEXT                  -- lookup, synthesis, disambiguation, verification, tree_edit
);

CREATE TABLE IF NOT EXISTS task_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT REFERENCES research_tasks(id),
    session_id TEXT,
    started_at TEXT,
    ended_at TEXT,
    tokens_used INTEGER,
    summary TEXT,
    exit_reason TEXT,
    coverage_before REAL,
    coverage_after REAL
);

CREATE TABLE IF NOT EXISTS negative_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id TEXT NOT NULL,
    source TEXT NOT NULL,
    query_fingerprint TEXT NOT NULL,
    query_params TEXT,
    result_class TEXT NOT NULL,     -- 'empty', 'error', 'timeout', 'not_indexed'
    reason TEXT,
    session_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    cooldown_until TEXT,
    UNIQUE(person_id, source, query_fingerprint)
);

CREATE TABLE IF NOT EXISTS person_research_state (
    person_id TEXT PRIMARY KEY REFERENCES persons(id),
    summary TEXT,
    best_tier TEXT,
    finding_count INTEGER DEFAULT 0,
    open_questions TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Full-text search on findings
-- ============================================================

CREATE VIRTUAL TABLE IF NOT EXISTS findings_fts USING fts5(
    title,
    raw_markdown,
    content='findings',
    content_rowid='rowid'
);

-- Auto-sync triggers for FTS5
CREATE TRIGGER IF NOT EXISTS findings_ai AFTER INSERT ON findings BEGIN
    INSERT INTO findings_fts(rowid, title, raw_markdown)
    VALUES (new.rowid, new.title, new.raw_markdown);
END;

CREATE TRIGGER IF NOT EXISTS findings_ad AFTER DELETE ON findings BEGIN
    INSERT INTO findings_fts(findings_fts, rowid, title, raw_markdown)
    VALUES ('delete', old.rowid, old.title, old.raw_markdown);
END;

CREATE TRIGGER IF NOT EXISTS findings_au AFTER UPDATE ON findings BEGIN
    INSERT INTO findings_fts(findings_fts, rowid, title, raw_markdown)
    VALUES ('delete', old.rowid, old.title, old.raw_markdown);
    INSERT INTO findings_fts(rowid, title, raw_markdown)
    VALUES (new.rowid, new.title, new.raw_markdown);
END;

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_findings_tier ON findings(tier);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);
CREATE INDEX IF NOT EXISTS idx_finding_persons_person ON finding_persons(person_id);
CREATE INDEX IF NOT EXISTS idx_research_tasks_status ON research_tasks(status);
CREATE INDEX IF NOT EXISTS idx_persons_surname ON persons(surname);
CREATE INDEX IF NOT EXISTS idx_persons_birth_year ON persons(birth_year);
CREATE INDEX IF NOT EXISTS idx_family_children_child ON family_children(child_id);
CREATE INDEX IF NOT EXISTS idx_neg_person ON negative_searches(person_id);
CREATE INDEX IF NOT EXISTS idx_neg_source ON negative_searches(source);
