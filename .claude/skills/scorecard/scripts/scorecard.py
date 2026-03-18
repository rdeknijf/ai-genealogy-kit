#!/usr/bin/env python3
"""Genealogy research scorecard: compare baseline GEDCOM against current tree.

Usage:
    uv run scripts/scorecard.py [baseline] [current]

Defaults:
    baseline = original_myheritage_baseline.ged
    current  = tree.ged
"""

import re
import sys
from collections import Counter
from pathlib import Path


def parse_ged(path):
    """Parse GEDCOM into records keyed by ID, with UID mapping."""
    records = {}  # id -> (type, lines)
    uid_map = {}  # uid -> id
    with open(path) as f:
        lines = f.readlines()
    cur_id = cur_type = None
    cur_lines = []
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("0 @"):
            if cur_id:
                records[cur_id] = (cur_type, cur_lines)
            m = re.match(r"0 @(\S+)@ (\w+)", line)
            if m:
                cur_id, cur_type = m.group(1), m.group(2)
                cur_lines = [line]
            else:
                cur_id = cur_type = None
                cur_lines = []
        elif cur_id:
            cur_lines.append(line)
            if line.startswith("1 _UID "):
                uid_map[line[7:].strip()] = cur_id
    if cur_id:
        records[cur_id] = (cur_type, cur_lines)
    return records, uid_map


def name(lines):
    for l in lines:
        m = re.match(r"1 NAME (.+)", l)
        if m:
            return m.group(1).replace("/", "").strip()
    return "?"


def has_date(lines, tag):
    hit = False
    for l in lines:
        if l.startswith(f"1 {tag}"):
            hit = True
        elif hit and l.startswith("2 DATE"):
            d = l[7:].strip()
            if d and "No Date" not in d:
                return True
        elif hit and l.startswith("1 "):
            hit = False
    return False


def has_place(lines, tag):
    hit = False
    for l in lines:
        if l.startswith(f"1 {tag}"):
            hit = True
        elif hit and l.startswith("2 PLAC"):
            return True
        elif hit and l.startswith("1 "):
            hit = False
    return False


def has_tag(lines, t):
    return any(l.startswith(f"1 {t}") for l in lines)


def count_tag(lines, t):
    return sum(1 for l in lines if l.startswith(f"1 {t}"))


def count_type(records, rtype):
    return sum(1 for _, v in records.items() if v[0] == rtype)


def get_date_value(lines, tag):
    """Extract the first date string for a given tag (BIRT, DEAT, etc.)."""
    hit = False
    for l in lines:
        if l.startswith(f"1 {tag}"):
            hit = True
        elif hit and l.startswith("2 DATE"):
            d = l[7:].strip()
            if d and "No Date" not in d:
                return d
        elif hit and l.startswith("1 "):
            hit = False
    return None


def parse_year(date_str):
    """Extract a numeric year from a GEDCOM date string."""
    if not date_str:
        return None
    m = re.search(r"\b(\d{4})\b", date_str)
    return int(m.group(1)) if m else None


def compute_generation_depth(records, root_id):
    """BFS up the ancestor tree to find max generation depth."""
    if root_id not in records or records[root_id][0] != "INDI":
        return 0, None
    # Build child-to-family map
    child_to_fam = {}
    fam_parents = {}
    for rid, (rtype, rlines) in records.items():
        if rtype == "INDI":
            for l in rlines:
                m = re.match(r"1 FAMC @(\S+)@", l)
                if m:
                    child_to_fam[rid] = m.group(1)
                    break
        elif rtype == "FAM":
            husb = wife = None
            for l in rlines:
                hm = re.match(r"1 HUSB @(\S+)@", l)
                if hm:
                    husb = hm.group(1)
                wm = re.match(r"1 WIFE @(\S+)@", l)
                if wm:
                    wife = wm.group(1)
            fam_parents[rid] = (husb, wife)

    max_depth = 0
    deepest = root_id
    queue = [(root_id, 0)]
    visited = {root_id}
    while queue:
        pid, depth = queue.pop(0)
        if depth > max_depth:
            max_depth = depth
            deepest = pid
        fam = child_to_fam.get(pid)
        if fam and fam in fam_parents:
            for parent in fam_parents[fam]:
                if parent and parent in records and parent not in visited:
                    visited.add(parent)
                    queue.append((parent, depth + 1))
    return max_depth, deepest


def parse_findings(findings_path):
    """Parse FINDINGS.md for tier and status counts."""
    tiers = Counter()
    statuses = Counter()
    archives = Counter()
    dates = Counter()
    if not findings_path.exists():
        return tiers, statuses, archives, dates
    text = findings_path.read_text()
    for m in re.finditer(r"\*\*Tier:\*\*\s*(\w)", text):
        tiers[m.group(1)] += 1
    for m in re.finditer(r"\*\*Status:\*\*\s*(\w+)", text):
        statuses[m.group(1)] += 1
    # Extract archive names from tier lines
    for m in re.finditer(r"from\s+([\w\s]+?)\s+via", text):
        archives[m.group(1).strip()] += 1
    # Extract finding dates
    for m in re.finditer(r"\*\*Date found:\*\*\s*(\d{4}-\d{2}-\d{2})", text):
        dates[m.group(1)] += 1
    return tiers, statuses, archives, dates


def main():
    project = Path(__file__).resolve().parent.parent.parent.parent.parent
    baseline_path = sys.argv[1] if len(sys.argv) > 1 else str(project / "private" / "original_myheritage_baseline.ged")
    current_path = sys.argv[2] if len(sys.argv) > 2 else str(project / "private" / "tree.ged")

    orig, orig_uid = parse_ged(baseline_path)
    curr, curr_uid = parse_ged(current_path)

    # Match records by UID
    uid_matched = {}
    for uid, oid in orig_uid.items():
        if uid in curr_uid:
            uid_matched[curr_uid[uid]] = oid

    # Genuinely new people (no UID match to baseline)
    genuinely_new = []
    for cid, (ctype, clines) in curr.items():
        if ctype != "INDI":
            continue
        if cid in uid_matched or cid == "I88888888":
            continue
        n = name(clines)
        if n == "?":
            continue
        genuinely_new.append((cid, n))

    # Split: research additions (I600xxx) vs Smart Match / Gramps Web additions
    research_new = [(cid, n) for cid, n in genuinely_new if cid.startswith("I6000")]
    smart_match_new = [(cid, n) for cid, n in genuinely_new if not cid.startswith("I6000")]

    # Data enrichments on UID-matched people
    enriched = []
    stats = {
        "birt_date": 0, "birt_plac": 0, "deat_date": 0, "deat_plac": 0,
        "parents": 0, "occu": 0, "sour": 0, "marr": 0,
    }

    for cid, oid in uid_matched.items():
        if orig[oid][0] != "INDI":
            continue
        old_l = orig[oid][1]
        new_l = curr[cid][1]
        ch = []

        if not has_date(old_l, "BIRT") and has_date(new_l, "BIRT"):
            stats["birt_date"] += 1
            ch.append("birth date")
        if not has_place(old_l, "BIRT") and has_place(new_l, "BIRT"):
            stats["birt_plac"] += 1
            ch.append("birth place")
        if not has_date(old_l, "DEAT") and has_date(new_l, "DEAT"):
            stats["deat_date"] += 1
            ch.append("death date")
        if not has_place(old_l, "DEAT") and has_place(new_l, "DEAT"):
            stats["deat_plac"] += 1
            ch.append("death place")
        if not has_tag(old_l, "FAMC") and has_tag(new_l, "FAMC"):
            stats["parents"] += 1
            ch.append("parents linked")
        if not has_tag(old_l, "OCCU") and has_tag(new_l, "OCCU"):
            stats["occu"] += 1
            ch.append("occupation")

        old_sours = set(re.findall(r"1 SOUR @(S\d+)@", "\n".join(old_l)))
        new_sours = set(re.findall(r"1 SOUR @(S\d+)@", "\n".join(new_l)))
        archive_sours = {s for s in (new_sours - old_sours) if s.startswith("S6000")}
        if archive_sours:
            stats["sour"] += len(archive_sours)
            ch.append(f"+{len(archive_sours)} archive source(s)")

        if ch:
            enriched.append((cid, name(new_l), ch))

    # Marriage enrichments
    for cid, oid in uid_matched.items():
        if orig[oid][0] != "FAM":
            continue
        if not has_date(orig[oid][1], "MARR") and has_date(curr[cid][1], "MARR"):
            stats["marr"] += 1

    # Research source records (S600xxx)
    research_sources = []
    for sid, (stype, slines) in curr.items():
        if stype == "SOUR" and sid.startswith("S6000"):
            for l in slines:
                m = re.match(r"1 TITL (.+)", l)
                if m:
                    research_sources.append((sid, m.group(1)))
                    break

    # New research family records (F600xxx)
    new_fams = [cid for cid, (ct, _) in curr.items() if ct == "FAM" and cid.startswith("F6000")]

    # Tree completeness stats (current tree)
    total_indi = 0
    with_birt_date = 0
    with_deat_date = 0
    with_birt_place = 0
    with_any_source = 0
    earliest_year = None
    earliest_person = None
    for cid, (ctype, clines) in curr.items():
        if ctype != "INDI":
            continue
        total_indi += 1
        if has_date(clines, "BIRT"):
            with_birt_date += 1
            yr = parse_year(get_date_value(clines, "BIRT"))
            if yr and (earliest_year is None or yr < earliest_year):
                earliest_year = yr
                earliest_person = name(clines)
        if has_date(clines, "DEAT"):
            with_deat_date += 1
        if has_place(clines, "BIRT"):
            with_birt_place += 1
        if has_tag(clines, "SOUR"):
            with_any_source += 1

    # Generation depth — find the deepest *named* ancestor
    gen_depth, deepest_id = compute_generation_depth(curr, "I0000")
    deepest_name = ""
    if deepest_id and deepest_id in curr:
        deepest_name = name(curr[deepest_id][1])
    # If deepest is unnamed, walk back to find the deepest named one
    if not deepest_name:
        # Re-run BFS collecting all depths
        child_to_fam = {}
        fam_parents = {}
        for rid, (rtype, rlines) in curr.items():
            if rtype == "INDI":
                for l in rlines:
                    m = re.match(r"1 FAMC @(\S+)@", l)
                    if m:
                        child_to_fam[rid] = m.group(1)
                        break
            elif rtype == "FAM":
                husb = wife = None
                for l in rlines:
                    hm = re.match(r"1 HUSB @(\S+)@", l)
                    if hm: husb = hm.group(1)
                    wm = re.match(r"1 WIFE @(\S+)@", l)
                    if wm: wife = wm.group(1)
                fam_parents[rid] = (husb, wife)
        best_depth = 0
        queue = [("I0000", 0)]
        visited = {"I0000"}
        while queue:
            pid, depth = queue.pop(0)
            n = name(curr[pid][1]) if pid in curr else ""
            if n and depth > best_depth:
                best_depth = depth
                deepest_name = n
                gen_depth = depth
            fam = child_to_fam.get(pid)
            if fam and fam in fam_parents:
                for parent in fam_parents[fam]:
                    if parent and parent in curr and parent not in visited:
                        visited.add(parent)
                        queue.append((parent, depth + 1))

    # FINDINGS.md analysis
    findings_path = project / "private" / "research" / "FINDINGS.md"
    tiers, statuses, archives, finding_dates = parse_findings(findings_path)

    # Print scorecard
    print()
    print("=" * 70)
    print("  \U0001f333 GENEALOGY RESEARCH SCORECARD")
    print("  MyHeritage baseline \u2192 AI-researched tree")
    print("=" * 70)
    print()
    print(f"  Baseline: {count_type(orig, 'INDI')} people, {count_type(orig, 'FAM')} families")
    print(f"  Current:  {count_type(curr, 'INDI')} people, {count_type(curr, 'FAM')} families")
    print()

    print("\u2500" * 70)
    print("  \U0001f465 NEW ANCESTORS DISCOVERED")
    print("\u2500" * 70)
    if research_new:
        print(f"\n  Via archive research ({len(research_new)}):")
        for _, n in sorted(research_new):
            print(f"    + {n}")
    if smart_match_new:
        print(f"\n  Via Gramps Web / Smart Matches ({len(smart_match_new)}):")
        for _, n in sorted(smart_match_new):
            print(f"    + {n}")

    print()
    print("\u2500" * 70)
    print("  \U0001f4dc OFFICIAL ARCHIVE SOURCES CITED")
    print("\u2500" * 70)
    for sid, title in sorted(research_sources):
        print(f"  [{sid}] {title}")

    print()
    print("\u2500" * 70)
    print("  \U0001f50d EXISTING RECORDS ENRICHED")
    print("\u2500" * 70)
    print(f"  Birth dates added:        {stats['birt_date']}")
    print(f"  Birth places added:       {stats['birt_plac']}")
    print(f"  Death dates added:        {stats['deat_date']}")
    print(f"  Death places added:       {stats['deat_plac']}")
    print(f"  Parents linked:           {stats['parents']}")
    print(f"  Marriage dates added:     {stats['marr']}")
    print(f"  Occupations added:        {stats['occu']}")
    print(f"  Archive sources attached: {stats['sour']}")
    print()
    if enriched:
        print("  Details:")
        for _, n, ch in sorted(enriched, key=lambda x: x[1]):
            print(f"    {n}: {', '.join(ch)}")

    # Research findings breakdown
    if tiers:
        print()
        print("\u2500" * 70)
        print("  \U0001f4cb RESEARCH FINDINGS")
        print("\u2500" * 70)
        total_findings = sum(tiers.values())
        print(f"  {total_findings} findings documented in FINDINGS.md\n")
        print("  By evidence tier:")
        for tier in ["A", "B", "C", "D"]:
            ct = tiers.get(tier, 0)
            label = {"A": "Primary source (scans viewed)",
                     "B": "Indexed civil registry record",
                     "C": "Multiple secondary sources agree",
                     "D": "Single source / AI inference"}[tier]
            bar = "\u2588" * ct
            print(f"    Tier {tier}: {ct:>3}  {bar}  {label}")
        print()
        print("  By status:")
        for status in ["APPLIED", "VERIFIED", "OPEN", "REJECTED"]:
            ct = statuses.get(status, 0)
            if ct:
                print(f"    {status:<10} {ct:>3}")
        if finding_dates:
            print()
            print("  Research timeline:")
            for date, ct in sorted(finding_dates.items()):
                print(f"    {date}  {ct} finding(s)")

    # Tree completeness
    print()
    print("\u2500" * 70)
    print("  \U0001f3af TREE COMPLETENESS")
    print("\u2500" * 70)
    pct = lambda n: f"{n/total_indi*100:.0f}%" if total_indi else "0%"
    print(f"  {total_indi} people in tree\n")
    print(f"  Has birth date:     {with_birt_date:>5}  ({pct(with_birt_date)})")
    print(f"  Has birth place:    {with_birt_place:>5}  ({pct(with_birt_place)})")
    print(f"  Has death date:     {with_deat_date:>5}  ({pct(with_deat_date)})")
    print(f"  Has source citation:{with_any_source:>5}  ({pct(with_any_source)})")
    print()
    print(f"  Generation depth:   {gen_depth} generations from root")
    print(f"  Deepest ancestor:   {deepest_name}")
    if earliest_year and earliest_person:
        print(f"  Earliest birth:     {earliest_year} ({earliest_person})")

    total_facts = (
        len(research_new) + len(smart_match_new) + len(new_fams)
        + len(research_sources) + sum(stats.values())
    )
    print()
    print("=" * 70)
    print(f"  \U0001f4ca GRAND TOTAL: {total_facts} new facts added to the family tree")
    print()
    print(f"     {len(research_new):>2} new ancestors from archive research")
    print(f"     {len(smart_match_new):>2} new people from Smart Matches")
    print(f"     {len(new_fams):>2} new family connections")
    print(f"     {len(research_sources):>2} official civil registry sources cited")
    print(f"     {sum(stats.values()):>2} data points added to existing records")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
