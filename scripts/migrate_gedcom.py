#!/usr/bin/env python3
"""Migrate GEDCOM data (persons, families, sources) into the SQLite database."""

import re
import sqlite3
import subprocess
import sys
from pathlib import Path

# Reuse parsing from analyze_gedcom.py
sys.path.insert(0, str(Path(__file__).parent))
from analyze_gedcom import (
    extract_field,
    extract_subfield,
    get_families,
    get_individuals,
    parse_gedcom,
    parse_year,
)

GEDCOM_PATH = Path(__file__).parent.parent / "private" / "tree.ged"
DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"


def migrate(db_path: Path = DEFAULT_DB, gedcom_path: Path = GEDCOM_PATH):
    if not gedcom_path.exists():
        print(f"Error: {gedcom_path} not found")
        sys.exit(1)

    print(f"Parsing {gedcom_path.name}...")
    records = parse_gedcom(str(gedcom_path))
    individuals = get_individuals(records)
    families = get_families(records)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # bulk load order doesn't matter

    # Clear existing GEDCOM-derived data
    conn.execute("DELETE FROM family_children")
    conn.execute("DELETE FROM families")
    conn.execute("DELETE FROM persons")
    conn.execute("DELETE FROM sources")

    # --- Persons ---
    for pid, info in individuals.items():
        lines = records.get(pid, [])
        conn.execute(
            "INSERT INTO persons (id, name, surname, sex, birth_date, birth_place, "
            "birth_year, death_date, death_place, death_year, gedcom_blob) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pid,
                info["name"],
                info["surname"],
                info["sex"],
                info["birth_date"],
                info["birth_place"],
                info["birth_year"],
                info["death_date"],
                info["death_place"],
                info["death_year"],
                "\n".join(lines),
            ),
        )

    # --- Families ---
    for fid, info in families.items():
        lines = records.get(fid, [])
        conn.execute(
            "INSERT INTO families (id, husband_id, wife_id, marr_date, marr_place, gedcom_blob) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                fid,
                info["husb"],
                info["wife"],
                info["marr_date"],
                info["marr_place"],
                "\n".join(lines),
            ),
        )
        # Children
        for i, child_id in enumerate(info["children"]):
            conn.execute(
                "INSERT OR IGNORE INTO family_children (family_id, child_id, sort_order) "
                "VALUES (?, ?, ?)",
                (fid, child_id, i),
            )

    # --- Sources ---
    source_count = 0
    for sid, lines in records.items():
        if not re.match(r"S\d+", sid):
            continue
        if "SOUR" not in lines[0]:
            continue

        title = extract_field(lines, "TITL")
        author = extract_field(lines, "AUTH")
        publication = extract_field(lines, "PUBL")

        conn.execute(
            "INSERT INTO sources (id, title, author, publication, gedcom_blob) "
            "VALUES (?, ?, ?, ?, ?)",
            (sid, title, author, publication, "\n".join(lines)),
        )
        source_count += 1

    conn.commit()

    # Validate counts
    db_persons = conn.execute("SELECT count(*) FROM persons").fetchone()[0]
    db_families = conn.execute("SELECT count(*) FROM families").fetchone()[0]
    db_children = conn.execute("SELECT count(*) FROM family_children").fetchone()[0]
    db_sources = conn.execute("SELECT count(*) FROM sources").fetchone()[0]

    # Compare against gedcom_query.py ids if available
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "gedcom_query.py"), "ids"],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout
        indi_m = re.search(r"total:\s*(\d+)\)", output.split("\n")[0])
        fam_m = re.search(r"total:\s*(\d+)\)", output.split("\n")[1])
        sour_m = re.search(r"total:\s*(\d+)\)", output.split("\n")[2])
        expected_indi = int(indi_m.group(1)) if indi_m else None
        expected_fam = int(fam_m.group(1)) if fam_m else None
        expected_sour = int(sour_m.group(1)) if sour_m else None
    except Exception:
        expected_indi = expected_fam = expected_sour = None

    def check(label, actual, expected):
        line = f"{label}: {actual}"
        if expected is not None:
            line += f" (expected {expected})"
            if actual == expected:
                line += " ✓"
            else:
                line += f" ✗ (delta: {actual - expected})"
        print(line)

    check("Persons", db_persons, expected_indi)
    check("Families", db_families, expected_fam)
    print(f"Family-children links: {db_children}")
    check("Sources", db_sources, expected_sour)

    conn.close()
    print("GEDCOM migration complete.")


if __name__ == "__main__":
    migrate()
