#!/usr/bin/env python3
"""Build per-person research state summaries from findings and GEDCOM gaps."""

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"

TIER_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}


def build_state(db_path: Path = DEFAULT_DB, person_id: str | None = None):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if person_id:
        person_ids = [person_id]
    else:
        # All persons that have findings OR are in the persons table
        rows = conn.execute(
            "SELECT DISTINCT person_id FROM finding_persons "
            "UNION "
            "SELECT id FROM persons"
        ).fetchall()
        person_ids = [r[0] for r in rows]

    count = 0
    for pid in person_ids:
        # Get findings for this person
        findings = conn.execute(
            "SELECT f.id, f.title, f.tier, f.status "
            "FROM findings f "
            "JOIN finding_persons fp ON f.id = fp.finding_id "
            "WHERE fp.person_id = ? "
            "ORDER BY f.id",
            (pid,),
        ).fetchall()

        finding_count = len(findings)

        # Best tier (lowest rank, excluding REJECTED)
        best_tier = None
        for f in findings:
            if f["status"] and "REJECT" in f["status"]:
                continue
            tier = f["tier"]
            if tier and (best_tier is None or TIER_RANK.get(tier, 99) < TIER_RANK.get(best_tier, 99)):
                best_tier = tier

        # Build summary
        summary_parts = []
        if finding_count > 0:
            applied = [f for f in findings if f["status"] and "APPLIED" in f["status"]]
            open_f = [f for f in findings if f["status"] and f["status"] == "OPEN"]
            summary_parts.append(f"{finding_count} findings ({len(applied)} applied, {len(open_f)} open)")

            # List key findings
            for f in findings[:3]:
                summary_parts.append(f"- {f['id']}: {f['title']}")
            if finding_count > 3:
                summary_parts.append(f"  ... and {finding_count - 3} more")
        else:
            summary_parts.append("No findings yet.")

        # Check GEDCOM gaps
        person = conn.execute("SELECT * FROM persons WHERE id = ?", (pid,)).fetchone()
        open_questions = []
        if person:
            if not person["birth_date"] and not person["birth_year"]:
                open_questions.append("Missing birth date")
            if not person["birth_place"]:
                open_questions.append("Missing birth place")
            if not person["death_date"] and not person["death_year"]:
                open_questions.append("Missing death date")

            # Check if parents are known
            parent_fam = conn.execute(
                "SELECT f.husband_id, f.wife_id FROM family_children fc "
                "JOIN families f ON fc.family_id = f.id "
                "WHERE fc.child_id = ?",
                (pid,),
            ).fetchone()
            if not parent_fam:
                open_questions.append("No parents linked")
            elif not parent_fam["husband_id"] or not parent_fam["wife_id"]:
                open_questions.append("Missing one or both parents")

            # Check for source citations in GEDCOM
            if person["gedcom_blob"] and "SOUR" not in person["gedcom_blob"]:
                open_questions.append("No source citations in GEDCOM")

        summary = "\n".join(summary_parts)
        questions = "; ".join(open_questions) if open_questions else None

        conn.execute(
            "INSERT OR REPLACE INTO person_research_state "
            "(person_id, summary, best_tier, finding_count, open_questions, updated_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (pid, summary, best_tier, finding_count, questions),
        )
        count += 1

    conn.commit()

    # Print stats
    total = conn.execute("SELECT count(*) FROM person_research_state").fetchone()[0]
    with_findings = conn.execute(
        "SELECT count(*) FROM person_research_state WHERE finding_count > 0"
    ).fetchone()[0]
    tier_dist = conn.execute(
        "SELECT best_tier, count(*) FROM person_research_state "
        "WHERE best_tier IS NOT NULL GROUP BY best_tier ORDER BY best_tier"
    ).fetchall()

    print(f"Built research state for {count} persons ({total} total in table)")
    print(f"  With findings: {with_findings}")
    for tier, cnt in tier_dist:
        print(f"  Tier {tier}: {cnt}")

    # Validate finding_count consistency
    mismatches = conn.execute(
        "SELECT prs.person_id, prs.finding_count, count(fp.finding_id) as actual "
        "FROM person_research_state prs "
        "LEFT JOIN finding_persons fp ON prs.person_id = fp.person_id "
        "GROUP BY prs.person_id "
        "HAVING prs.finding_count != actual AND prs.finding_count > 0"
    ).fetchall()
    if mismatches:
        print(f"WARNING: {len(mismatches)} persons with mismatched finding_count")

    conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build per-person research state summaries")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Database path")
    parser.add_argument("--person", help="Rebuild for a single person ID")
    args = parser.parse_args()

    build_state(args.db, args.person)


if __name__ == "__main__":
    main()
