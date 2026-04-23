import sqlite3
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).parent.parent / "scripts" / "schema.sql"


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary SQLite DB with the genealogy schema."""
    path = tmp_path / "test_genealogy.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.close()
    return path


@pytest.fixture
def db_conn(db_path):
    """Return an open connection to the temporary DB."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def populated_db(db_conn, db_path):
    """DB with sample persons, families, findings, and tasks for testing."""
    db_conn.executescript("""
        INSERT INTO persons (id, name, surname, sex, birth_year, death_year)
        VALUES
            ('I0000', 'Jan Jansen', 'Jansen', 'M', 1990, NULL),
            ('I0001', 'Pieter Jansen', 'Jansen', 'M', 1960, NULL),
            ('I0002', 'Maria Visser', 'Visser', 'F', 1962, NULL),
            ('I0003', 'Hendrik Jansen', 'Jansen', 'M', 1930, 2010),
            ('I0004', 'Cornelia Bakker', 'Bakker', 'F', 1932, 2015),
            ('I0005', 'Willem Visser', 'Visser', 'M', 1928, 2005),
            ('I0006', 'Anna Smit', 'Smit', 'F', 1935, 2020);

        INSERT INTO families (id, husband_id, wife_id)
        VALUES
            ('F0001', 'I0001', 'I0002'),
            ('F0002', 'I0003', 'I0004'),
            ('F0003', 'I0005', 'I0006');

        INSERT INTO family_children (family_id, child_id, sort_order)
        VALUES
            ('F0001', 'I0000', 0),
            ('F0002', 'I0001', 0),
            ('F0003', 'I0002', 0);

        INSERT INTO research_tasks (id, title, priority, status, people_ids, goal, raw_markdown, requires_model)
        VALUES
            ('RQ-001', 'Verify grandparents', 2, 'IN_PROGRESS', 'I0003,I0004', 'Find civil records', '## RQ-001', 'sonnet'),
            ('RQ-002', 'Extend maternal line', 3, 'QUEUED', 'I0005,I0006', 'Find parents', '## RQ-002', 'sonnet'),
            ('RQ-003', 'Done task', 5, 'DONE', 'I0001', 'Completed', '## RQ-003', 'sonnet');

        INSERT INTO findings (id, title, tier, status, date_found, queue_ref, raw_markdown)
        VALUES
            ('F-001', 'Birth record I0003', 'B', 'APPLIED', '2026-04-01', 'RQ-001', '## F-001: Birth'),
            ('F-002', 'Death record I0003', 'B', 'OPEN', '2026-04-02', 'RQ-001', '## F-002: Death');

        INSERT INTO finding_persons (finding_id, person_id, role)
        VALUES
            ('F-001', 'I0003', 'subject'),
            ('F-002', 'I0003', 'subject');
    """)
    db_conn.commit()
    return db_path
