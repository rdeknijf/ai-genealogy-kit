#!/usr/bin/env python3
import sqlite3
import re
import json
import sys
from pathlib import Path

FINDINGS_PATH = Path(__file__).parent.parent / "private" / "research" / "FINDINGS.md"
QUEUE_PATH = Path(__file__).parent.parent / "private" / "research" / "RESEARCH_QUEUE.md"
DB_PATH = Path(__file__).parent.parent / "private" / "genealogy.db"

def normalize_id(pid):
    if not pid: return None
    m = re.match(r"(I|F|S)(\d+)", pid)
    if m:
        prefix = m.group(1)
        num = m.group(2)
        if len(num) < 4:
            return f"{prefix}{num.zfill(4)}"
    return pid

def parse_findings(filepath):
    findings = []
    if not filepath.exists():
        print(f"Warning: {filepath} not found.")
        return []
        
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r"\n+---\n+", content)
    print(f"Total blocks found in FINDINGS.md: {len(blocks)}")
    
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block or block.startswith("# ") or block.startswith("## Confidence") or block.startswith("## Status"): 
            continue
        
        m_id = re.search(r"## (F-\d+):?\s*(.*)", block)
        if not m_id: continue
        
        fid = m_id.group(1)
        title = m_id.group(2)
        
        person_match = re.search(r"- \*\*Person:\*\* (.*?) \((I\d+)\)", block)
        person_id = normalize_id(person_match.group(2)) if person_match else None
        
        tier_match = re.search(r"- \*\*Tier:\*\* ([A-D])", block)
        tier = tier_match.group(1) if tier_match else None
        
        status_match = re.search(r"- \*\*Status:\*\* ([^ \n(]+)", block)
        status = status_match.group(1) if status_match else None
        
        date_match = re.search(r"- \*\*Date found:\*\* (.*)", block)
        date_found = date_match.group(1) if date_match else None
        
        gedcom_match = re.search(r"\*\*GEDCOM says:\*\* (.*?)(?=\n\*\*|$)", block, re.DOTALL)
        gedcom_says = gedcom_match.group(1).strip() if gedcom_match else None
        
        evidence_match = re.search(r"\*\*Evidence found:\*\* (.*?)(?=\n\*\*|$)", block, re.DOTALL)
        evidence_found = evidence_match.group(1).strip() if evidence_match else None
        
        resolution_match = re.search(r"\*\*Resolution:\*\* (.*?)(?=\n\*\*|$)", block, re.DOTALL)
        resolution = resolution_match.group(1).strip() if resolution_match else None
        
        notes_match = re.search(r"\*\*Notes:\*\* (.*?)(?=\n\*\*|$)", block, re.DOTALL)
        notes = notes_match.group(1).strip() if notes_match else None
        
        findings.append((fid, person_id, title, tier, status, date_found, gedcom_says, evidence_found, resolution, notes, block))
    
    return findings

def parse_queue(filepath):
    tasks = []
    if not filepath.exists():
        print(f"Warning: {filepath} not found.")
        return []

    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r"\n+---\n+", content)
    print(f"Total blocks found in RESEARCH_QUEUE.md: {len(blocks)}")

    for block in blocks:
        block = block.strip()
        if not block or block.startswith("# ") or block.startswith("## Status"): 
            continue
        
        m_id = re.search(r"## (RQ-\d+):?\s*(.*)", block)
        if not m_id: continue
        
        rqid = m_id.group(1)
        title = m_id.group(2)
        
        prio_match = re.search(r"- \*\*Priority:\*\* (\d+)", block)
        priority = int(prio_match.group(1)) if prio_match else 3
        
        status_match = re.search(r"- \*\*Status:\*\* ([^ \n]+)", block)
        status = status_match.group(1) if status_match else None
        
        people_match = re.search(r"- \*\*People:\*\* (.*)", block)
        people_ids_raw = people_match.group(1) if people_match else ""
        pids = [normalize_id(p.strip()) for p in re.findall(r"(I\d+)", people_ids_raw)]
        people_ids = ", ".join(pids)
        
        goal_match = re.search(r"- \*\*Research goal:\*\* (.*)", block)
        goal = goal_match.group(1) if goal_match else None
        
        where_match = re.search(r"- \*\*Where to look:\*\* (.*)", block)
        where_to_look = where_match.group(1) if where_match else None
        
        updates = []
        for line in block.split("\n"):
            if "- **Findings (" in line or "- **Cycle " in line or "- **Current data:**" in line:
                updates.append(line.strip())
        
        tasks.append((rqid, title, priority, status, people_ids, goal, where_to_look, "", json.dumps(updates), block))
        
    return tasks

def migrate():
    findings = parse_findings(FINDINGS_PATH)
    tasks = parse_queue(QUEUE_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("DELETE FROM findings")
    cur.execute("DELETE FROM research_queue")
    
    if findings:
        print(f"Migrating {len(findings)} findings...")
        cur.executemany("INSERT OR REPLACE INTO findings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", findings)
    
    if tasks:
        print(f"Migrating {len(tasks)} research tasks...")
        cur.executemany("INSERT OR REPLACE INTO research_queue VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tasks)
    
    cur.execute("DROP TABLE IF EXISTS findings_fts")
    cur.execute("CREATE VIRTUAL TABLE findings_fts USING fts5(id UNINDEXED, person_id, title, content)")
    cur.execute("INSERT INTO findings_fts(id, person_id, title, content) SELECT id, person_id, title, COALESCE(evidence_found,'') || ' ' || COALESCE(resolution,'') || ' ' || COALESCE(notes,'') FROM findings")
    
    conn.commit()
    conn.close()
    print("Markdown migration complete.")

if __name__ == "__main__":
    migrate()
