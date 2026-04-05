#!/usr/bin/env python3
import sqlite3
import json
import sys
import argparse
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "private" / "genealogy.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def cmd_get_tasks(args):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, title, priority, status, goal FROM research_queue WHERE status != 'DONE' ORDER BY priority ASC, id ASC LIMIT ?", (args.limit,))
    tasks = [dict(r) for r in cur.fetchall()]
    print(json.dumps(tasks, indent=2))
    db.close()

def cmd_get_person(args):
    db = get_db()
    cur = db.cursor()
    
    # Get person data
    cur.execute("SELECT * FROM people WHERE id = ?", (args.id,))
    person = cur.fetchone()
    if not person:
        print(f"Error: Person {args.id} not found.")
        sys.exit(1)
    
    person_dict = dict(person)
    
    # Get associated findings
    cur.execute("SELECT id, title, tier, status, date_found, resolution FROM findings WHERE person_id = ?", (args.id,))
    findings = [dict(r) for r in cur.fetchall()]
    person_dict["findings"] = findings
    
    # Get associated tasks
    cur.execute("SELECT id, title, status, goal FROM research_queue WHERE people_ids LIKE ?", (f"%{args.id}%",))
    tasks = [dict(r) for r in cur.fetchall()]
    person_dict["tasks"] = tasks
    
    print(json.dumps(person_dict, indent=2))
    db.close()

def cmd_search(args):
    db = get_db()
    cur = db.cursor()
    # Use FTS5
    cur.execute("SELECT id, title, content FROM findings_fts WHERE findings_fts MATCH ? LIMIT 10", (args.query,))
    results = [dict(r) for r in cur.fetchall()]
    print(json.dumps(results, indent=2))
    db.close()

def cmd_add_finding(args):
    data = json.loads(args.json)
    db = get_db()
    cur = db.cursor()
    
    # Map fields
    cur.execute("""
        INSERT INTO findings (id, person_id, title, tier, status, date_found, gedcom_says, evidence_found, resolution, notes, raw_markdown)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("id"), data.get("person_id"), data.get("title"), data.get("tier"),
        data.get("status", "OPEN"), data.get("date_found"), data.get("gedcom_says"),
        data.get("evidence_found"), data.get("resolution"), data.get("notes"),
        data.get("raw_markdown", "")
    ))
    
    # Sync FTS
    cur.execute("INSERT INTO findings_fts(id, person_id, title, content) VALUES (?, ?, ?, ?)",
                (data.get("id"), data.get("person_id"), data.get("title"), 
                 f"{data.get('evidence_found', '')} {data.get('resolution', '')} {data.get('notes', '')}"))
    
    db.commit()
    db.close()
    print(f"Successfully added finding {data.get('id')}")

def cmd_update_task(args):
    db = get_db()
    cur = db.cursor()
    
    # Get current updates
    cur.execute("SELECT updates FROM research_queue WHERE id = ?", (args.id,))
    row = cur.fetchone()
    if not row:
        print(f"Error: Task {args.id} not found.")
        sys.exit(1)
    
    updates = json.loads(row["updates"]) if row["updates"] else []
    if args.note:
        import datetime
        timestamp = datetime.date.today().isoformat()
        updates.append(f"- **Cycle** ({timestamp}): {args.note}")
    
    cur.execute("UPDATE research_queue SET status = ?, updates = ? WHERE id = ?",
                (args.status, json.dumps(updates), args.id))
    db.commit()
    db.close()
    print(f"Successfully updated task {args.id} to status {args.status}")

def main():
    parser = argparse.ArgumentParser(description="Genealogy Research Database Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # get-tasks
    p_tasks = subparsers.add_parser("get-tasks", help="Get prioritized research tasks")
    p_tasks.add_argument("--limit", type=int, default=5)
    
    # get-person
    p_person = subparsers.add_parser("get-person", help="Get person context including findings")
    p_person.add_argument("id", help="Person ID (e.g. I123)")
    
    # search
    p_search = subparsers.add_parser("search", help="Search findings using FTS")
    p_search.add_argument("query", help="Search query")
    
    # add-finding
    p_add = subparsers.add_parser("add-finding", help="Add a new finding")
    p_add.add_argument("json", help="JSON data for the finding")
    
    # update-task
    p_update = subparsers.add_parser("update-task", help="Update task status and add notes")
    p_update.add_argument("id", help="Task ID (e.g. RQ-001)")
    p_update.add_argument("--status", required=True, help="New status")
    p_update.add_argument("--note", help="Progress note to append")
    
    args = parser.parse_args()
    
    if args.command == "get-tasks": cmd_get_tasks(args)
    elif args.command == "get-person": cmd_get_person(args)
    elif args.command == "search": cmd_search(args)
    elif args.command == "add-finding": cmd_add_finding(args)
    elif args.command == "update-task": cmd_update_task(args)

if __name__ == "__main__":
    main()
