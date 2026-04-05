#!/usr/bin/env python3
"""Migrate FINDINGS.md and RESEARCH_QUEUE.md into the SQLite database."""

import re
import sqlite3
import subprocess
import sys
from pathlib import Path

FINDINGS_PATH = Path(__file__).parent.parent / "private" / "research" / "FINDINGS.md"
QUEUE_PATH = Path(__file__).parent.parent / "private" / "research" / "RESEARCH_QUEUE.md"
DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"


def parse_findings(filepath: Path) -> tuple[list[dict], list[tuple[str, str, str]]]:
    """Parse FINDINGS.md into findings rows and finding_persons rows.

    Returns (findings_list, finding_persons_list).
    """
    text = filepath.read_text(encoding="utf-8")

    # Split on ## F-NNN headings, keeping the heading with its block
    blocks = re.split(r"(?=^## F-\d+)", text, flags=re.MULTILINE)

    findings = []
    person_links = []

    for block in blocks:
        block = block.strip()
        m_id = re.match(r"## (F-\d+):?\s*(.*)", block)
        if not m_id:
            continue

        fid = m_id.group(1)
        title = m_id.group(2).strip()

        # Extract tier
        tier_m = re.search(r"\*\*Tier:\*\*\s*([A-D])\b", block)
        tier = tier_m.group(1) if tier_m else None

        # Extract status (allow multi-word like "PARTIALLY RESOLVED")
        status_m = re.search(r"\*\*Status:\*\*\s*([A-Z][A-Z /]+)", block)
        status = status_m.group(1).strip() if status_m else None

        # Extract date_found
        date_m = re.search(r"\*\*Date found:\*\*\s*([\d-]+)", block)
        date_found = date_m.group(1) if date_m else None

        # Extract queue ref (e.g. "**Queue:** RQ-013")
        queue_m = re.search(r"\*\*Queue(?:\s*ref)?:\*\*\s*(RQ-\d+)", block)
        queue_ref = queue_m.group(1) if queue_m else None

        # Extract person IDs:
        # 1. Try **Person:** or **Persons:** line first
        person_ids = []
        person_line_m = re.search(r"\*\*Persons?:\*\*\s*(.*)", block)
        if person_line_m:
            person_ids = re.findall(r"\(I(\d+)\)", person_line_m.group(1))
        # 2. Fallback: scan entire block for (Ixxxx) patterns
        if not person_ids:
            person_ids = re.findall(r"\(I(\d+)\)", block)

        # Normalize IDs: short IDs get zero-padded to 4 digits
        normalized = set()
        for raw in person_ids:
            if len(raw) <= 3:
                normalized.add(f"I{int(raw):04d}")
            else:
                normalized.add(f"I{raw}")

        for pid in sorted(normalized):
            person_links.append((fid, pid, "subject"))

        # Strip trailing --- separators from raw_markdown
        raw = block.rstrip().rstrip("-").rstrip()

        findings.append({
            "id": fid,
            "title": title,
            "tier": tier,
            "status": status,
            "date_found": date_found,
            "queue_ref": queue_ref,
            "raw_markdown": raw,
        })

    return findings, person_links


def parse_queue(filepath: Path) -> list[dict]:
    """Parse RESEARCH_QUEUE.md into research_tasks rows."""
    text = filepath.read_text(encoding="utf-8")

    # Split on ## RQ-NNN headings
    blocks = re.split(r"(?=^## RQ-\d+)", text, flags=re.MULTILINE)

    tasks = []
    for block in blocks:
        block = block.strip()
        m_id = re.match(r"## (RQ-\d+):?\s*(.*)", block)
        if not m_id:
            continue

        rqid = m_id.group(1)
        title = m_id.group(2).strip()

        prio_m = re.search(r"\*\*Priority:\*\*\s*(\d+)", block)
        priority = int(prio_m.group(1)) if prio_m else 3

        status_m = re.search(r"\*\*Status:\*\*\s*(\w+)", block)
        status = status_m.group(1) if status_m else None

        # Extract people IDs
        people_m = re.search(r"\*\*People:\*\*\s*(.*)", block)
        if people_m:
            raw_ids = re.findall(r"I\d+", people_m.group(1))
            people_ids = ", ".join(raw_ids)
        else:
            people_ids = ""

        goal_m = re.search(r"\*\*Research goal:\*\*\s*(.*)", block)
        goal = goal_m.group(1).strip() if goal_m else None

        where_m = re.search(r"\*\*Where to look:\*\*\s*(.*)", block)
        where_to_look = where_m.group(1).strip() if where_m else None

        raw = block.rstrip().rstrip("-").rstrip()

        tasks.append({
            "id": rqid,
            "title": title,
            "priority": priority,
            "status": status,
            "people_ids": people_ids,
            "goal": goal,
            "where_to_look": where_to_look,
            "raw_markdown": raw,
        })

    return tasks


def migrate(db_path: Path = DEFAULT_DB):
    if not FINDINGS_PATH.exists():
        print(f"Error: {FINDINGS_PATH} not found")
        sys.exit(1)
    if not QUEUE_PATH.exists():
        print(f"Error: {QUEUE_PATH} not found")
        sys.exit(1)

    findings, person_links = parse_findings(FINDINGS_PATH)
    tasks = parse_queue(QUEUE_PATH)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # person IDs may not be in persons table yet

    # Clear existing data
    conn.execute("DELETE FROM finding_persons")
    conn.execute("DELETE FROM findings")
    conn.execute("DELETE FROM research_tasks")

    # Insert findings (use REPLACE to handle duplicate IDs — last entry wins)
    dupes = set()
    seen = set()
    for f in findings:
        if f["id"] in seen:
            dupes.add(f["id"])
        seen.add(f["id"])

    if dupes:
        print(f"Note: {len(dupes)} duplicate finding IDs (last entry wins): {sorted(dupes)[:5]}...")

    for f in findings:
        conn.execute(
            "INSERT OR REPLACE INTO findings (id, title, tier, status, date_found, queue_ref, raw_markdown) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f["id"], f["title"], f["tier"], f["status"], f["date_found"],
             f["queue_ref"], f["raw_markdown"]),
        )

    # Insert finding_persons (clear first since we may have replaced findings)
    conn.execute("DELETE FROM finding_persons")
    for fid, pid, role in person_links:
        conn.execute(
            "INSERT OR IGNORE INTO finding_persons (finding_id, person_id, role) VALUES (?, ?, ?)",
            (fid, pid, role),
        )

    # Insert research_tasks
    for t in tasks:
        conn.execute(
            "INSERT INTO research_tasks (id, title, priority, status, people_ids, goal, where_to_look, raw_markdown) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (t["id"], t["title"], t["priority"], t["status"], t["people_ids"],
             t["goal"], t["where_to_look"], t["raw_markdown"]),
        )

    conn.commit()

    # Validate counts
    db_findings = conn.execute("SELECT count(*) FROM findings").fetchone()[0]
    db_persons = conn.execute("SELECT count(*) FROM finding_persons").fetchone()[0]
    db_tasks = conn.execute("SELECT count(*) FROM research_tasks").fetchone()[0]

    # Compare with grep counts
    grep_findings = int(subprocess.run(
        ["grep", "-cP", r"^## F-\d+", str(FINDINGS_PATH)],
        capture_output=True, text=True
    ).stdout.strip() or "0")

    grep_tasks = int(subprocess.run(
        ["grep", "-cP", r"^## RQ-\d+", str(QUEUE_PATH)],
        capture_output=True, text=True
    ).stdout.strip() or "0")

    unique_findings = len(seen)
    dupe_count = grep_findings - unique_findings
    print(f"Findings:  {db_findings} in DB, {grep_findings} in FINDINGS.md "
          f"({dupe_count} duplicates)", end="")
    if db_findings == unique_findings:
        print(" ✓")
    else:
        print(f" ✗ (expected {unique_findings} unique)")

    print(f"Person links: {db_persons}")

    print(f"Tasks:     {db_tasks} in DB, {grep_tasks} in RESEARCH_QUEUE.md", end="")
    if db_tasks == grep_tasks:
        print(" ✓")
    else:
        print(f" ✗ (delta: {db_tasks - grep_tasks})")

    # Integrity checks
    nulls = conn.execute("SELECT count(*) FROM findings WHERE raw_markdown IS NULL").fetchone()[0]
    if nulls:
        print(f"WARNING: {nulls} findings with NULL raw_markdown")

    null_ids = conn.execute("SELECT count(*) FROM findings WHERE id IS NULL").fetchone()[0]
    if null_ids:
        print(f"WARNING: {null_ids} findings with NULL id")

    bad_pids = conn.execute(
        "SELECT count(*) FROM finding_persons WHERE person_id NOT GLOB 'I[0-9]*'"
    ).fetchone()[0]
    if bad_pids:
        print(f"WARNING: {bad_pids} finding_persons with non-standard person_id format")

    conn.close()

    if db_findings != unique_findings or db_tasks != grep_tasks:
        sys.exit(1)

    print("Research migration complete.")


if __name__ == "__main__":
    migrate()
