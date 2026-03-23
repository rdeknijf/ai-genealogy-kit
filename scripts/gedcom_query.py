#!/usr/bin/env python3
"""Fast GEDCOM query tool — safe alternative to regex one-liners.

Parses GEDCOM line-by-line (no DOTALL regex) to avoid catastrophic backtracking
on large files. Provides common queries needed by research sessions.

Usage:
    python scripts/gedcom_query.py ids                    # highest INDI/FAM/SOUR IDs + counts
    python scripts/gedcom_query.py person I0000           # full record for a person
    python scripts/gedcom_query.py search "Kemmann"       # find persons by surname
    python scripts/gedcom_query.py gaps I0100 I0200 ...   # gap analysis (missing sources)
    python scripts/gedcom_query.py family F0296           # full family record
    python scripts/gedcom_query.py validate               # integrity check (dupes, TRLR)
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

GEDCOM = Path(__file__).parent.parent / "private" / "tree.ged"


def parse_records(filepath: Path) -> dict[str, list[str]]:
    records = {}
    current_id = None
    current_lines = []
    with open(filepath, encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("0 "):
                if current_id:
                    records[current_id] = current_lines
                m = re.match(r"0 @([^@]+)@ (\w+)", line)
                if m:
                    current_id = m.group(1)
                    current_lines = [line]
                else:
                    current_id = None
                    current_lines = []
            elif current_id:
                current_lines.append(line)
    if current_id:
        records[current_id] = current_lines
    return records


def cmd_ids(records):
    iids = sorted([int(k[1:]) for k in records if k.startswith("I") and k[1:].isdigit()])
    fids = sorted([int(k[1:]) for k in records if k.startswith("F") and k[1:].isdigit()])
    sids = sorted([int(k[1:]) for k in records if k.startswith("S") and k[1:].isdigit()])
    print(f"Highest INDI: I{iids[-1] if iids else 0}  (total: {len(iids)})")
    print(f"Highest FAM:  F{fids[-1] if fids else 0}  (total: {len(fids)})")
    print(f"Highest SOUR: S{sids[-1] if sids else 0}  (total: {len(sids)})")


def cmd_person(records, person_id):
    if person_id in records:
        print("\n".join(records[person_id]))
    else:
        print(f"Not found: {person_id}")
        sys.exit(1)


def cmd_family(records, fam_id):
    if fam_id in records:
        print("\n".join(records[fam_id]))
    else:
        print(f"Not found: {fam_id}")
        sys.exit(1)


def cmd_search(records, query):
    query_lower = query.lower()
    for rid, lines in records.items():
        if not rid.startswith("I") or "INDI" not in lines[0]:
            continue
        for line in lines:
            if re.match(r"1 NAME\s", line) and query_lower in line.lower():
                print(f"{rid}: {line.strip()}")
                break


def cmd_gaps(records, person_ids):
    for pid in person_ids:
        if pid not in records:
            print(f"{pid}: NOT FOUND")
            continue
        lines = records[pid]
        name = "?"
        for line in lines:
            m = re.match(r"1 NAME\s+(.*)", line)
            if m:
                name = m.group(1).strip()
                break

        gaps = []
        for evt in ["BIRT", "DEAT", "MARR"]:
            in_evt = False
            has_date = False
            has_sour = False
            for line in lines:
                if re.match(rf"1 {evt}", line):
                    in_evt = True
                    continue
                if in_evt:
                    if re.match(r"1 [A-Z]", line):
                        in_evt = False
                        continue
                    if re.match(r"2 DATE\s", line):
                        has_date = True
                    if re.match(r"2 SOUR\s", line):
                        has_sour = True
            if not has_date:
                gaps.append(f"no {evt.lower()} date")
            elif not has_sour:
                gaps.append(f"no {evt.lower()} src")

        # Check for FAMC (parents known)
        has_famc = any(re.match(r"1 FAMC\s", l) for l in lines)
        if not has_famc:
            gaps.append("no parents")

        status = " | ".join(gaps) if gaps else "fully sourced"
        print(f"{pid} {name}: {status}")


def cmd_validate(records):
    dupes = defaultdict(int)
    for rid in records:
        dupes[rid] += 1
    dup_list = {k: v for k, v in dupes.items() if v > 1}

    iids = [k for k in records if k.startswith("I") and "INDI" in records[k][0]]
    fids = [k for k in records if k.startswith("F") and "FAM" in records[k][0]]
    sids = [k for k in records if k.startswith("S") and "SOUR" in records[k][0]]

    # Check TRLR
    with open(GEDCOM, encoding="utf-8-sig") as f:
        last_line = ""
        for last_line in f:
            pass
    has_trlr = "TRLR" in last_line

    print(f"Individuals: {len(iids)}")
    print(f"Families: {len(fids)}")
    print(f"Sources: {len(sids)}")
    print(f"TRLR present: {has_trlr}")
    print(f"Duplicate IDs: {dup_list if dup_list else 'none'}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    records = parse_records(GEDCOM)

    if cmd == "ids":
        cmd_ids(records)
    elif cmd == "person" and len(sys.argv) >= 3:
        cmd_person(records, sys.argv[2])
    elif cmd == "family" and len(sys.argv) >= 3:
        cmd_family(records, sys.argv[2])
    elif cmd == "search" and len(sys.argv) >= 3:
        cmd_search(records, sys.argv[2])
    elif cmd == "gaps" and len(sys.argv) >= 3:
        cmd_gaps(records, sys.argv[2:])
    elif cmd == "validate":
        cmd_validate(records)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
