"""Quick analysis of the GEDCOM export — overview stats, surname distribution, earliest ancestors, gaps."""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def parse_gedcom(filepath: str) -> dict:
    """Parse GEDCOM into a dict of records keyed by ID."""
    records = {}
    current_id = None
    current_record = []

    with open(filepath, encoding="utf-8", errors="replace") as f:
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


def extract_field(lines: list[str], tag: str) -> str | None:
    """Extract first occurrence of a tag at level 1."""
    for line in lines:
        m = re.match(rf"1 {tag}\s*(.*)", line)
        if m:
            return m.group(1).strip() or None
    return None


def extract_subfield(lines: list[str], parent_tag: str, child_tag: str) -> str | None:
    """Extract a level-2 field under a level-1 parent."""
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


def extract_all_subfields(lines: list[str], parent_tag: str, child_tag: str) -> list[str]:
    """Extract all occurrences of a level-2 field under any matching level-1 parent."""
    results = []
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
                results.append(m.group(1).strip())
    return results


def parse_year(date_str: str | None) -> int | None:
    if not date_str:
        return None
    # Handle "ABT 1850", "BEF 1900", "AFT 1800", "CAL 1900", etc.
    date_str = re.sub(r"^(ABT|BEF|AFT|CAL|EST|FROM|TO|BET|AND)\s+", "", date_str)
    m = re.search(r"\b(\d{4})\b", date_str)
    return int(m.group(1)) if m else None


def get_individuals(records: dict) -> dict:
    """Extract individual data."""
    individuals = {}
    for rid, lines in records.items():
        if not any("INDI" in lines[0] for _ in [1]):
            if "INDI" not in lines[0]:
                continue

        name_line = extract_field(lines, "NAME")
        if name_line:
            givn = name_line.replace("/", "").strip()
        else:
            givn = "Unknown"

        surname = None
        m = re.search(r"/([^/]+)/", name_line or "")
        if m:
            surname = m.group(1).strip()

        sex = extract_field(lines, "SEX")
        birth_date = extract_subfield(lines, "BIRT", "DATE")
        birth_place = extract_subfield(lines, "BIRT", "PLAC")
        death_date = extract_subfield(lines, "DEAT", "DATE")
        death_place = extract_subfield(lines, "DEAT", "PLAC")
        birth_year = parse_year(birth_date)
        death_year = parse_year(death_date)

        # Family links
        famc_ids = [re.search(r"@([^@]+)@", l).group(1)
                     for l in lines if re.match(r"1 FAMC", l) and re.search(r"@([^@]+)@", l)]
        fams_ids = [re.search(r"@([^@]+)@", l).group(1)
                     for l in lines if re.match(r"1 FAMS", l) and re.search(r"@([^@]+)@", l)]

        individuals[rid] = {
            "name": givn,
            "surname": surname,
            "sex": sex,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "birth_year": birth_year,
            "death_date": death_date,
            "death_place": death_place,
            "death_year": death_year,
            "famc": famc_ids,  # family as child
            "fams": fams_ids,  # family as spouse
        }

    return individuals


def get_families(records: dict) -> dict:
    """Extract family data."""
    families = {}
    for rid, lines in records.items():
        if "FAM" not in lines[0] or "FAMC" in lines[0] or "FAMS" in lines[0]:
            if not re.match(r"0 @[^@]+@ FAM$", lines[0]):
                continue

        husb = None
        wife = None
        children = []
        marr_date = None
        marr_place = None

        for line in lines:
            m = re.match(r"1 HUSB @([^@]+)@", line)
            if m:
                husb = m.group(1)
            m = re.match(r"1 WIFE @([^@]+)@", line)
            if m:
                wife = m.group(1)
            m = re.match(r"1 CHIL @([^@]+)@", line)
            if m:
                children.append(m.group(1))

        marr_date = extract_subfield(lines, "MARR", "DATE")
        marr_place = extract_subfield(lines, "MARR", "PLAC")

        families[rid] = {
            "husb": husb,
            "wife": wife,
            "children": children,
            "marr_date": marr_date,
            "marr_place": marr_place,
        }

    return families


def find_ancestors(start_id: str, individuals: dict, families: dict) -> dict[str, int]:
    """BFS to find all ancestors with their generation number."""
    ancestors = {start_id: 0}
    queue = [(start_id, 0)]

    while queue:
        pid, gen = queue.pop(0)
        person = individuals.get(pid)
        if not person:
            continue
        for fam_id in person["famc"]:
            fam = families.get(fam_id)
            if not fam:
                continue
            for parent_id in [fam["husb"], fam["wife"]]:
                if parent_id and parent_id not in ancestors:
                    ancestors[parent_id] = gen + 1
                    queue.append((parent_id, gen + 1))

    return ancestors


def find_end_of_line_ancestors(start_id: str, individuals: dict, families: dict) -> list[dict]:
    """Find ancestors where the line ends (no known parents)."""
    ancestors = find_ancestors(start_id, individuals, families)
    end_of_line = []

    for pid, gen in ancestors.items():
        if gen == 0:
            continue
        person = individuals.get(pid)
        if not person:
            continue
        has_parents = False
        for fam_id in person["famc"]:
            fam = families.get(fam_id)
            if fam and (fam["husb"] or fam["wife"]):
                has_parents = True
                break
        if not has_parents:
            end_of_line.append({
                "id": pid,
                "name": person["name"],
                "surname": person["surname"],
                "generation": gen,
                "birth_year": person["birth_year"],
                "birth_place": person["birth_place"],
                "sex": person["sex"],
            })

    return sorted(end_of_line, key=lambda x: x["generation"], reverse=True)


def main():
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
    elif Path("tree.ged").exists():
        filepath = Path("tree.ged")
    else:
        ged_files = list(Path(".").glob("*.ged"))
        if not ged_files:
            print("No .ged files found. Pass a path or place tree.ged in the project root.")
            sys.exit(1)
        filepath = ged_files[0]
    print(f"Parsing {filepath.name}...")
    records = parse_gedcom(str(filepath))
    individuals = get_individuals(records)
    families = get_families(records)

    print(f"\n{'='*60}")
    print(f"GEDCOM OVERVIEW")
    print(f"{'='*60}")
    print(f"Individuals: {len(individuals)}")
    print(f"Families:    {len(families)}")

    # Gender distribution
    males = sum(1 for i in individuals.values() if i["sex"] == "M")
    females = sum(1 for i in individuals.values() if i["sex"] == "F")
    print(f"Males:       {males}")
    print(f"Females:     {females}")

    # Date range
    birth_years = [i["birth_year"] for i in individuals.values() if i["birth_year"]]
    if birth_years:
        print(f"Birth years: {min(birth_years)} – {max(birth_years)}")

    # Surname distribution
    surnames = Counter(i["surname"] for i in individuals.values() if i["surname"])
    print(f"\n{'='*60}")
    print(f"TOP 30 SURNAMES")
    print(f"{'='*60}")
    for surname, count in surnames.most_common(30):
        print(f"  {count:4d}  {surname}")

    # Birth place distribution
    places = Counter(i["birth_place"] for i in individuals.values() if i["birth_place"])
    print(f"\n{'='*60}")
    print(f"TOP 20 BIRTH PLACES")
    print(f"{'='*60}")
    for place, count in places.most_common(20):
        print(f"  {count:4d}  {place}")

    # Find root individual (typically I1 in most GEDCOM exports)
    root_id = "I1"
    if root_id in individuals:
        print(f"\n{'='*60}")
        print(f"DIRECT ANCESTORS OF {individuals[root_id]['name']}")
        print(f"{'='*60}")

        ancestors = find_ancestors(root_id, individuals, families)
        gen_counts = Counter(ancestors.values())
        max_gen = max(gen_counts.keys()) if gen_counts else 0

        print(f"Total direct ancestors found: {len(ancestors) - 1}")
        print(f"Deepest generation: {max_gen}")
        print(f"\nAncestors per generation:")
        for gen in range(1, max_gen + 1):
            expected = 2 ** gen
            actual = gen_counts.get(gen, 0)
            pct = actual / expected * 100
            print(f"  Gen {gen:2d} ({2**gen:5d} expected): {actual:4d} found ({pct:5.1f}%)")

        # End-of-line ancestors
        eol = find_end_of_line_ancestors(root_id, individuals, families)
        print(f"\n{'='*60}")
        print(f"END-OF-LINE ANCESTORS (where research stops)")
        print(f"{'='*60}")
        print(f"Total: {len(eol)}")
        print(f"\nDeepest (furthest back):")
        for a in eol[:20]:
            yr = f"b.{a['birth_year']}" if a["birth_year"] else "date unknown"
            pl = a["birth_place"] or ""
            print(f"  Gen {a['generation']:2d}: {a['name']:<40s} {yr:<12s} {pl}")

        print(f"\nShallowest (closest gaps — easiest to fill):")
        shallow = sorted(eol, key=lambda x: x["generation"])
        for a in shallow[:20]:
            yr = f"b.{a['birth_year']}" if a["birth_year"] else "date unknown"
            pl = a["birth_place"] or ""
            print(f"  Gen {a['generation']:2d}: {a['name']:<40s} {yr:<12s} {pl}")

    # People with no dates at all
    no_dates = [i for i in individuals.values()
                if not i["birth_year"] and not i["death_year"]]
    print(f"\n{'='*60}")
    print(f"DATA QUALITY")
    print(f"{'='*60}")
    print(f"People with no birth or death year: {len(no_dates)} ({len(no_dates)/len(individuals)*100:.1f}%)")

    no_birth_place = [i for i in individuals.values() if not i["birth_place"]]
    print(f"People with no birth place:         {len(no_birth_place)} ({len(no_birth_place)/len(individuals)*100:.1f}%)")

    # Sources
    sources_count = sum(1 for rid in records if re.match(r"S\d+", rid))
    print(f"Sources in file:                    {sources_count}")


if __name__ == "__main__":
    main()
