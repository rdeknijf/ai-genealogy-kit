#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "private" / "genealogy.db"
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

def sync():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Sync Findings
    print(f"Syncing DB to {FINDINGS_PATH}...")
    cur.execute("SELECT raw_markdown FROM findings ORDER BY id ASC")
    findings = [row["raw_markdown"] for row in cur.fetchall()]
    with open(FINDINGS_PATH, "w", encoding="utf-8") as f:
        f.write(FINDINGS_HEADER)
        f.write("\n\n---\n\n".join(findings))
        f.write("\n---\n")

    # Sync Queue
    print(f"Syncing DB to {QUEUE_PATH}...")
    cur.execute("SELECT raw_markdown FROM research_queue ORDER BY priority ASC, id ASC")
    tasks = [row["raw_markdown"] for row in cur.fetchall()]
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        f.write(QUEUE_HEADER)
        f.write("\n\n---\n\n".join(tasks))
        f.write("\n---\n")

    conn.close()
    print("Sync complete.")

if __name__ == "__main__":
    sync()
