#!/usr/bin/env python3
"""Central CLI for the genealogy research database.

Usage:
    python scripts/research_db.py get-tasks [--limit N] [--status S]
    python scripts/research_db.py get-person ID
    python scripts/research_db.py get-research-state ID
    python scripts/research_db.py search QUERY [--limit N]
    python scripts/research_db.py add-finding JSON
    python scripts/research_db.py update-task ID --status S [--note T]
    python scripts/research_db.py next-id [--type finding|indi|fam|sour]
    python scripts/research_db.py log-run JSON
    python scripts/research_db.py stats
    python scripts/research_db.py sync-from-gedcom
    python scripts/research_db.py sync-to-markdown
    python scripts/research_db.py rebuild-research-state [--person ID]
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"
FINDINGS_PATH = Path(__file__).parent.parent / "private" / "research" / "FINDINGS.md"
QUEUE_PATH = Path(__file__).parent.parent / "private" / "research" / "RESEARCH_QUEUE.md"

FINDINGS_HEADER = """# Research Findings

Discrepancies, corrections, and research leads found during analysis.
Each finding has a confidence tier and verification status.

## Confidence Tiers

| Tier | Source | Action |
|------|--------|--------|
| **A** | Primary source (civil record scan, church book) you've seen | Edit GEDCOM directly |
| **B** | Indexed civil record from official archive with reference | Edit with source citation |
| **C** | Multiple independent secondary sources agree | Flag for review |
| **D** | Single secondary source or AI inference | Note only |

## Status Legend

- `OPEN` — needs verification
- `VERIFIED` — confirmed by primary source, applied to GEDCOM
- `REJECTED` — checked and found incorrect
- `APPLIED` — change made based on Tier A/B evidence

---
"""

QUEUE_HEADER = """# Research Queue

Prioritized research leads beyond standard hardening/gap-filling.
These are lines with historical interest, colorful stories, or unverified family lore.
Agents: pick the highest-priority unclaimed item matching your capabilities.

**Important:** Items marked "HUMAN" require Rutger's physical presence, money,
or decision — see `HUMAN_ACTIONS.md` for the full list. Do not attempt these as AI.

## Status Legend

- `QUEUED` — ready to research
- `IN_PROGRESS` — being worked on (note session/date)
- `DONE` — completed, findings in FINDINGS.md
- `BLOCKED` — needs something before it can proceed

---
"""


def get_db(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def output(data):
    print(json.dumps(data, indent=2, default=str))


# ============================================================
# Subcommands
# ============================================================


def cmd_get_tasks(args):
    db = get_db(args.db)
    query = (
        "SELECT id, title, priority, status, people_ids, goal, requires_model "
        "FROM research_tasks"
    )
    params = []
    if args.status:
        query += " WHERE status = ?"
        params.append(args.status)
    else:
        query += " WHERE status NOT IN ('DONE', 'BLOCKED')"
    query += " ORDER BY priority ASC, id ASC LIMIT ?"
    params.append(args.limit)

    tasks = [dict(r) for r in db.execute(query, params).fetchall()]

    # Promote a model hint from any OPEN linked finding if the task itself
    # has none. Linkage is via findings.queue_ref = research_tasks.id.
    for task in tasks:
        if task.get("requires_model"):
            continue
        row = db.execute(
            "SELECT requires_model FROM findings "
            "WHERE queue_ref = ? AND status = 'OPEN' "
            "AND requires_model IS NOT NULL LIMIT 1",
            (task["id"],),
        ).fetchone()
        if row:
            task["requires_model"] = row["requires_model"]

    output(tasks)
    db.close()


MODEL_RANK = {"haiku": 0, "sonnet": 1, "opus": 2}


def cmd_next_model(args):
    """Return the model to use for the next research session.

    Picks the highest-priority non-terminal task. Uses task.requires_model
    as the base, then escalates if any linked OPEN finding has a higher
    model rank (opus > sonnet > haiku). Falls back to --default if
    nothing is set."""
    db = get_db(args.db)
    default = args.default

    top = db.execute(
        "SELECT id, requires_model FROM research_tasks "
        "WHERE status NOT IN ('DONE', 'BLOCKED') "
        "ORDER BY priority ASC, id ASC LIMIT 1"
    ).fetchone()

    if not top:
        result = {"model": default, "reason": f"no active tasks, default={default}"}
    else:
        model = top["requires_model"] or default
        reason = (
            f"task {top['id']} requires {model}"
            if top["requires_model"]
            else f"task {top['id']} unset, default={default}"
        )
        escalation = db.execute(
            "SELECT id, requires_model FROM findings "
            "WHERE queue_ref = ? AND status = 'OPEN' AND requires_model IS NOT NULL",
            (top["id"],),
        ).fetchall()
        for r in escalation:
            if MODEL_RANK.get(r["requires_model"], -1) > MODEL_RANK.get(model, -1):
                model = r["requires_model"]
                reason = f"finding {r['id']} escalates task {top['id']} to {model}"
        result = {"model": model, "reason": reason}

    if args.quiet:
        print(result["model"])
    else:
        output(result)
    db.close()


def cmd_set_model(args):
    """Set or clear requires_model on a finding (F-NNN) or task (RQ-NNN)."""
    db = get_db(args.db)
    table = "findings" if args.id.startswith("F-") else "research_tasks"
    value = None if args.model == "none" else args.model
    cur = db.execute(
        f"UPDATE {table} SET requires_model = ?, updated_at = datetime('now') WHERE id = ?",
        (value, args.id),
    )
    db.commit()
    updated = cur.rowcount
    db.close()
    print(json.dumps({"id": args.id, "requires_model": value, "updated": updated}))


ALLOWED_MODELS = {"opus", "sonnet", "haiku"}


def cmd_add_task(args):
    """Add a new research queue item. Requires --model.

    Rationale: every new queue item must declare what model it needs so the
    runner can route it. Later this may expand into --work-type and
    --complexity from which model + role can be inferred.
    """
    if args.model not in ALLOWED_MODELS:
        print(
            json.dumps(
                {"error": f"--model must be one of {sorted(ALLOWED_MODELS)}, got {args.model!r}"}
            )
        )
        sys.exit(1)

    db = get_db(args.db)
    tid = args.id
    if not tid:
        row = db.execute(
            "SELECT id FROM research_tasks WHERE id LIKE 'RQ-%' ORDER BY "
            "CAST(REPLACE(id, 'RQ-', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        num = int(row["id"].replace("RQ-", "")) + 1 if row else 1
        tid = f"RQ-{num:03d}"

    raw = args.raw_markdown or (
        f"## {tid}: {args.title}\n\n"
        f"- **Priority:** {args.priority}\n"
        f"- **Status:** {args.status}\n"
        f"- **Model:** {args.model}\n"
        + (f"- **People:** {args.people}\n" if args.people else "")
        + (f"\n**Goal:** {args.goal}\n" if args.goal else "")
    )

    db.execute(
        "INSERT INTO research_tasks (id, title, priority, status, people_ids, goal, "
        "where_to_look, raw_markdown, requires_model) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            tid,
            args.title,
            args.priority,
            args.status,
            args.people or "",
            args.goal or "",
            args.where_to_look or "",
            raw,
            args.model,
        ),
    )
    db.commit()
    db.close()
    print(json.dumps({"id": tid, "requires_model": args.model, "status": "created"}))


def cmd_validate(args):
    """Check DB invariants. Currently: every non-terminal task must declare a model."""
    db = get_db(args.db)
    missing = db.execute(
        "SELECT id, title FROM research_tasks "
        "WHERE status NOT IN ('DONE', 'BLOCKED') AND requires_model IS NULL "
        "ORDER BY priority ASC, id ASC"
    ).fetchall()
    db.close()

    result = {
        "tasks_missing_model": [dict(r) for r in missing],
        "ok": len(missing) == 0,
    }
    output(result)
    if args.strict and missing:
        sys.exit(1)


def cmd_get_person(args):
    db = get_db(args.db)

    # Person data
    person = db.execute("SELECT * FROM persons WHERE id = ?", (args.id,)).fetchone()
    if not person:
        print(json.dumps({"error": f"Person {args.id} not found"}))
        sys.exit(1)

    result = dict(person)
    # Don't include gedcom_blob in JSON output (too large) — summarize
    result.pop("gedcom_blob", None)

    # Family as child (parents)
    parents = db.execute(
        "SELECT f.id as family_id, f.husband_id, f.wife_id, f.marr_date, f.marr_place, "
        "ph.name as father_name, pw.name as mother_name "
        "FROM family_children fc "
        "JOIN families f ON fc.family_id = f.id "
        "LEFT JOIN persons ph ON f.husband_id = ph.id "
        "LEFT JOIN persons pw ON f.wife_id = pw.id "
        "WHERE fc.child_id = ?",
        (args.id,),
    ).fetchall()
    result["parents"] = [dict(r) for r in parents]

    # Family as spouse (marriages + children)
    spouse_fams = db.execute(
        "SELECT f.id as family_id, f.husband_id, f.wife_id, f.marr_date, f.marr_place, "
        "CASE WHEN f.husband_id = ? THEN pw.name ELSE ph.name END as spouse_name, "
        "CASE WHEN f.husband_id = ? THEN f.wife_id ELSE f.husband_id END as spouse_id "
        "FROM families f "
        "LEFT JOIN persons ph ON f.husband_id = ph.id "
        "LEFT JOIN persons pw ON f.wife_id = pw.id "
        "WHERE f.husband_id = ? OR f.wife_id = ?",
        (args.id, args.id, args.id, args.id),
    ).fetchall()

    marriages = []
    for sf in spouse_fams:
        fam = dict(sf)
        children = db.execute(
            "SELECT p.id, p.name, p.birth_year FROM family_children fc "
            "JOIN persons p ON fc.child_id = p.id "
            "WHERE fc.family_id = ? ORDER BY fc.sort_order",
            (sf["family_id"],),
        ).fetchall()
        fam["children"] = [dict(c) for c in children]
        marriages.append(fam)
    result["marriages"] = marriages

    # Findings
    findings = db.execute(
        "SELECT f.id, f.title, f.tier, f.status, f.date_found "
        "FROM findings f "
        "JOIN finding_persons fp ON f.id = fp.finding_id "
        "WHERE fp.person_id = ? ORDER BY f.id",
        (args.id,),
    ).fetchall()
    result["findings"] = [dict(f) for f in findings]

    # Research state
    state = db.execute(
        "SELECT * FROM person_research_state WHERE person_id = ?", (args.id,)
    ).fetchone()
    if state:
        result["research_state"] = dict(state)

    # Research tasks referencing this person
    tasks = db.execute(
        "SELECT id, title, status, goal FROM research_tasks WHERE people_ids LIKE ?",
        (f"%{args.id}%",),
    ).fetchall()
    result["research_tasks"] = [dict(t) for t in tasks]

    output(result)
    db.close()


def cmd_get_research_state(args):
    db = get_db(args.db)
    state = db.execute(
        "SELECT * FROM person_research_state WHERE person_id = ?", (args.id,)
    ).fetchone()
    if not state:
        print(json.dumps({"error": f"No research state for {args.id}"}))
        sys.exit(1)
    output(dict(state))
    db.close()


def cmd_search(args):
    db = get_db(args.db)
    # Auto-quote terms with hyphens (e.g. F-912) so FTS5 doesn't treat
    # the hyphen as a column subtraction operator.
    query = re.sub(r'(?<!")(\b\w+-\w+\b)(?!")', r'"\1"', args.query)
    results = db.execute(
        "SELECT f.id, f.title, f.tier, f.status, "
        "snippet(findings_fts, 1, '>>>', '<<<', '...', 40) as snippet "
        "FROM findings_fts fts "
        "JOIN findings f ON fts.rowid = f.rowid "
        "WHERE findings_fts MATCH ? "
        "ORDER BY rank LIMIT ?",
        (query, args.limit),
    ).fetchall()
    output([dict(r) for r in results])
    db.close()


def cmd_add_finding(args):
    data = json.loads(args.json)
    db = get_db(args.db)

    fid = data.get("id")
    if not fid:
        # Auto-generate next ID
        row = db.execute(
            "SELECT id FROM findings WHERE id LIKE 'F-%' ORDER BY "
            "CAST(REPLACE(id, 'F-', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        if row:
            last_num = int(row["id"].replace("F-", ""))
            fid = f"F-{last_num + 1:03d}" if last_num < 999 else f"F-{last_num + 1}"
        else:
            fid = "F-001"
        data["id"] = fid

    # Build raw_markdown if not provided
    if not data.get("raw_markdown"):
        parts = [f"## {fid}: {data.get('title', '')}"]
        person_ids = data.get("person_ids") or data.get("persons") or []
        if isinstance(person_ids, str):
            person_ids = [p.strip() for p in person_ids.split(",") if p.strip()]

        if len(person_ids) == 1:
            parts.append(f"\n- **Person:** ({person_ids[0]})")
        elif person_ids:
            parts.append(f"\n- **Persons:** {', '.join(f'({p})' for p in person_ids)}")

        parts.append(f"- **Tier:** {data.get('tier', 'D')}")
        parts.append(f"- **Status:** {data.get('status', 'OPEN')}")
        parts.append(f"- **Date found:** {date.today().isoformat()}")

        if data.get("queue_ref"):
            parts.append(f"- **Queue:** {data['queue_ref']}")

        if data.get("evidence"):
            parts.append(f"\n**Evidence found:**\n\n{data['evidence']}")
        if data.get("resolution"):
            parts.append(f"\n**Resolution:** {data['resolution']}")
        if data.get("notes"):
            parts.append(f"\n**Notes:** {data['notes']}")

        data["raw_markdown"] = "\n".join(parts)

    db.execute(
        "INSERT OR REPLACE INTO findings (id, title, tier, status, date_found, queue_ref, raw_markdown, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            fid,
            data.get("title"),
            data.get("tier", "D"),
            data.get("status", "OPEN"),
            data.get("date_found", date.today().isoformat()),
            data.get("queue_ref"),
            data["raw_markdown"],
        ),
    )

    # Link persons — accept both "person_ids" and "persons" keys
    person_ids = data.get("person_ids") or data.get("persons") or []
    if isinstance(person_ids, str):
        person_ids = [p.strip() for p in person_ids.split(",") if p.strip()]
    # Also extract from raw_markdown
    if not person_ids:
        person_ids = list(set(re.findall(r"\(I\d+\)", data["raw_markdown"])))
        person_ids = [p.strip("()") for p in person_ids]

    if not person_ids:
        print(f"WARNING: Finding {fid} has no linked persons. Use 'person_ids' or 'persons' in JSON.", file=sys.stderr)

    for pid in person_ids:
        db.execute(
            "INSERT OR IGNORE INTO finding_persons (finding_id, person_id, role) VALUES (?, ?, 'subject')",
            (fid, pid),
        )

    db.commit()
    db.close()
    print(json.dumps({"id": fid, "persons_linked": len(person_ids), "status": "created"}))


def cmd_update_task(args):
    db = get_db(args.db)

    task = db.execute("SELECT * FROM research_tasks WHERE id = ?", (args.id,)).fetchone()
    if not task:
        print(json.dumps({"error": f"Task {args.id} not found"}))
        sys.exit(1)

    # Update status
    db.execute(
        "UPDATE research_tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (args.status, args.id),
    )

    # Append note to raw_markdown if provided
    if args.note:
        timestamp = date.today().isoformat()
        note_line = f"\n- **Update ({timestamp}):** {args.note}"
        db.execute(
            "UPDATE research_tasks SET raw_markdown = raw_markdown || ? WHERE id = ?",
            (note_line, args.id),
        )

    db.commit()
    db.close()
    print(json.dumps({"id": args.id, "status": args.status, "updated": True}))


def cmd_next_id(args):
    db = get_db(args.db)
    id_type = args.type

    if id_type == "finding":
        row = db.execute(
            "SELECT id FROM findings WHERE id LIKE 'F-%' ORDER BY "
            "CAST(REPLACE(id, 'F-', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        if row:
            num = int(row["id"].replace("F-", "")) + 1
        else:
            num = 1
        result = f"F-{num:03d}" if num < 1000 else f"F-{num}"
    elif id_type == "indi":
        row = db.execute(
            "SELECT id FROM persons ORDER BY "
            "CAST(REPLACE(id, 'I', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        num = int(row["id"].replace("I", "")) + 1 if row else 1
        result = f"I{num}"
    elif id_type == "fam":
        row = db.execute(
            "SELECT id FROM families ORDER BY "
            "CAST(REPLACE(id, 'F', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        num = int(row["id"].replace("F", "")) + 1 if row else 1
        result = f"F{num}"
    elif id_type == "sour":
        row = db.execute(
            "SELECT id FROM sources WHERE id LIKE 'S%' ORDER BY "
            "CAST(REPLACE(id, 'S', '') AS INTEGER) DESC LIMIT 1"
        ).fetchone()
        num = int(row["id"].replace("S", "")) + 1 if row else 1
        result = f"S{num}"
    else:
        print(json.dumps({"error": f"Unknown type: {id_type}"}))
        sys.exit(1)

    print(json.dumps({"type": id_type, "next_id": result}))
    db.close()


def cmd_log_run(args):
    data = json.loads(args.json)
    db = get_db(args.db)
    db.execute(
        "INSERT INTO task_runs (task_id, session_id, started_at, ended_at, tokens_used, summary, exit_reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.get("task_id"),
            data.get("session_id"),
            data.get("started_at"),
            data.get("ended_at", datetime.now().isoformat()),
            data.get("tokens_used"),
            data.get("summary"),
            data.get("exit_reason"),
        ),
    )
    db.commit()
    run_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    print(json.dumps({"run_id": run_id}))


def cmd_stats(args):
    db = get_db(args.db)

    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts_%' ORDER BY name"
    ).fetchall()

    result = {"tables": {}}
    for (name,) in tables:
        count = db.execute(f"SELECT count(*) FROM [{name}]").fetchone()[0]
        result["tables"][name] = count

    # Tier distribution
    tiers = db.execute(
        "SELECT tier, count(*) as cnt FROM findings WHERE tier IS NOT NULL GROUP BY tier ORDER BY tier"
    ).fetchall()
    result["tier_distribution"] = {r["tier"]: r["cnt"] for r in tiers}

    # Status distribution (findings)
    statuses = db.execute(
        "SELECT status, count(*) as cnt FROM findings WHERE status IS NOT NULL GROUP BY status ORDER BY cnt DESC"
    ).fetchall()
    result["finding_status"] = {r["status"]: r["cnt"] for r in statuses}

    # Task status distribution
    task_statuses = db.execute(
        "SELECT status, count(*) as cnt FROM research_tasks GROUP BY status ORDER BY cnt DESC"
    ).fetchall()
    result["task_status"] = {r["status"]: r["cnt"] for r in task_statuses}

    # Research state summary
    state = db.execute(
        "SELECT best_tier, count(*) as cnt FROM person_research_state "
        "WHERE best_tier IS NOT NULL GROUP BY best_tier ORDER BY best_tier"
    ).fetchall()
    result["research_state_tiers"] = {r["best_tier"]: r["cnt"] for r in state}

    output(result)
    db.close()


def cmd_sync_from_gedcom(args):
    """Refresh persons/families/sources from tree.ged."""
    from migrate_gedcom import migrate
    migrate(args.db)


def cmd_sync_to_markdown(args):
    """Regenerate FINDINGS.md and RESEARCH_QUEUE.md from DB."""
    db = get_db(args.db)

    # Findings
    findings = db.execute("SELECT raw_markdown FROM findings ORDER BY "
                          "CAST(REPLACE(id, 'F-', '') AS INTEGER) ASC").fetchall()
    with open(FINDINGS_PATH, "w", encoding="utf-8") as f:
        f.write(FINDINGS_HEADER)
        for i, row in enumerate(findings):
            if i > 0:
                f.write("\n---\n\n")
            f.write(row["raw_markdown"])
            f.write("\n\n")

    # Research tasks
    tasks = db.execute("SELECT raw_markdown FROM research_tasks ORDER BY priority ASC, id ASC").fetchall()
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        f.write(QUEUE_HEADER)
        for i, row in enumerate(tasks):
            if i > 0:
                f.write("\n---\n\n")
            f.write(row["raw_markdown"])
            f.write("\n\n")

    print(f"Synced {len(findings)} findings to {FINDINGS_PATH}")
    print(f"Synced {len(tasks)} tasks to {QUEUE_PATH}")
    db.close()


def cmd_rebuild_research_state(args):
    """Recompute person_research_state summaries."""
    from build_research_state import build_state
    build_state(args.db, args.person)


# ============================================================
# CLI
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="Genealogy Research Database CLI")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Database path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-tasks
    p = subparsers.add_parser("get-tasks", help="Get prioritized research tasks")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--status", help="Filter by status")

    # get-person
    p = subparsers.add_parser("get-person", help="Get person with findings and family context")
    p.add_argument("id", help="Person ID (e.g. I0067)")

    # get-research-state
    p = subparsers.add_parser("get-research-state", help="Get research state summary for a person")
    p.add_argument("id", help="Person ID")

    # search
    p = subparsers.add_parser("search", help="Full-text search across findings")
    p.add_argument("query", help="Search query")
    p.add_argument("--limit", type=int, default=20)

    # add-finding
    p = subparsers.add_parser("add-finding", help="Add a new finding")
    p.add_argument("json", help="JSON data for the finding")

    # update-task
    p = subparsers.add_parser("update-task", help="Update task status")
    p.add_argument("id", help="Task ID (e.g. RQ-001)")
    p.add_argument("--status", required=True, help="New status")
    p.add_argument("--note", help="Progress note to append")

    # next-id
    p = subparsers.add_parser("next-id", help="Get next available ID")
    p.add_argument("--type", default="finding", choices=["finding", "indi", "fam", "sour"])

    # log-run
    p = subparsers.add_parser("log-run", help="Record session metrics")
    p.add_argument("json", help="JSON data for the run")

    # stats
    subparsers.add_parser("stats", help="Table counts and distributions")

    # sync-from-gedcom
    subparsers.add_parser("sync-from-gedcom", help="Refresh persons/families/sources from GEDCOM")

    # sync-to-markdown
    subparsers.add_parser("sync-to-markdown", help="Regenerate FINDINGS.md and RESEARCH_QUEUE.md from DB")

    # rebuild-research-state
    p = subparsers.add_parser("rebuild-research-state", help="Recompute person research summaries")
    p.add_argument("--person", help="Single person ID for incremental rebuild")

    # next-model
    p = subparsers.add_parser(
        "next-model",
        help="Return the model hint for the next session (opus/sonnet)",
    )
    p.add_argument("--default", default="sonnet", help="Fallback model (default: sonnet)")
    p.add_argument("--quiet", action="store_true", help="Print just the model name")

    # set-model
    p = subparsers.add_parser("set-model", help="Set requires_model on a finding or task")
    p.add_argument("id", help="F-NNN or RQ-NNN")
    p.add_argument("--model", required=True, help="Model name (opus/sonnet) or 'none' to clear")

    # add-task — requires --model
    p = subparsers.add_parser(
        "add-task",
        help="Add a new research queue item (requires --model)",
    )
    p.add_argument("--id", help="Task ID (auto-generated if omitted)")
    p.add_argument("--title", required=True)
    p.add_argument("--model", required=True, help="opus | sonnet | haiku")
    p.add_argument("--priority", type=int, default=5)
    p.add_argument("--status", default="QUEUED")
    p.add_argument("--people", help="Comma-separated person IDs", default="")
    p.add_argument("--goal", help="Goal description", default="")
    p.add_argument("--where-to-look", help="Archive hints", default="")
    p.add_argument("--raw-markdown", help="Full markdown body (optional; auto-built if omitted)")

    # validate — flag tasks missing a model hint
    p = subparsers.add_parser(
        "validate",
        help="Check that every active task has requires_model set",
    )
    p.add_argument("--strict", action="store_true", help="Exit non-zero on violations")

    args = parser.parse_args()
    cmd = args.command.replace("-", "_")
    globals()[f"cmd_{cmd}"](args)


if __name__ == "__main__":
    main()
