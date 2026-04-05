#!/usr/bin/env python3
import sqlite3
import re
from pathlib import Path

GEDCOM_PATH = Path(__file__).parent.parent / "private" / "tree.ged"
DB_PATH = Path(__file__).parent.parent / "private" / "genealogy.db"

def parse_gedcom(filepath):
    records = {}
    current_id = None
    current_record = []
    with open(filepath, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("0 "):
                if current_id and current_record:
                    records[current_id] = current_record
                match = re.match(r"0 @([^@]+)@ (\w+)", line)
                if match:
                    current_id = match.group(1)
                    current_record = [line]
                else:
                    current_id = None
                    current_record = []
            elif current_id:
                current_record.append(line)
    if current_id and current_record:
        records[current_id] = current_record
    return records

def extract_field(lines, tag):
    for line in lines:
        m = re.match(rf"1 {tag}\s*(.*)", line)
        if m:
            return m.group(1).strip() or None
    return None

def extract_subfield(lines, parent_tag, child_tag):
    in_parent = False
    for line in lines:
        if re.match(rf"1 {parent_tag}", line):
            in_parent = True
            continue
        if in_parent:
            if re.match(r"1 \w+", line):
                in_parent = False
                continue
            m = re.match(rf"2 {child_tag}\s+(.*)", line)
            if m:
                return m.group(1).strip()
    return None

def parse_year(date_str):
    if not date_str: return None
    date_str = re.sub(r"^(ABT|BEF|AFT|CAL|EST|FROM|TO|BET|AND)\s+", "", date_str)
    m = re.search(r"\b(\d{4})\b", date_str)
    return int(m.group(1)) if m else None

def migrate():
    records = parse_gedcom(GEDCOM_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Migrating GEDCOM records...")
    
    # People
    for rid, lines in records.items():
        if "INDI" in lines[0]:
            name = extract_field(lines, "NAME")
            birt_date = extract_subfield(lines, "BIRT", "DATE")
            deat_date = extract_subfield(lines, "DEAT", "DATE")
            cur.execute("INSERT OR REPLACE INTO people (id, name, birth_year, death_year, gedcom_record) VALUES (?, ?, ?, ?, ?)",
                        (rid, name, parse_year(birt_date), parse_year(deat_date), "\n".join(lines)))

    # Families
    for rid, lines in records.items():
        if "FAM" in lines[0]:
            husb = extract_field(lines, "HUSB")
            if husb: husb = husb.strip("@")
            wife = extract_field(lines, "WIFE")
            if wife: wife = wife.strip("@")
            cur.execute("INSERT OR REPLACE INTO families (id, husband_id, wife_id, gedcom_record) VALUES (?, ?, ?, ?)",
                        (rid, husb, wife, "\n".join(lines)))

    # Sources
    for rid, lines in records.items():
        if "SOUR" in lines[0]:
            title = extract_field(lines, "TITL")
            cur.execute("INSERT OR REPLACE INTO sources (id, title, gedcom_record) VALUES (?, ?, ?)",
                        (rid, title, "\n".join(lines)))

    conn.commit()
    conn.close()
    print("GEDCOM migration complete.")

if __name__ == "__main__":
    migrate()
