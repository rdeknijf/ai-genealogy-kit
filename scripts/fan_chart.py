"""Generate a fan chart (SVG) of 7 generations, colorized by research verification tier."""

import math
import os
import re
import sys
from pathlib import Path

# Reuse GEDCOM parsing from analyze_gedcom
sys.path.insert(0, str(Path(__file__).parent))
from analyze_gedcom import parse_gedcom, get_individuals, get_families


# --- Tier colors ---
TIER_COLORS = {
    "A": "#2d8a4e",  # dark green — primary source verified
    "B": "#3b82f6",  # blue — indexed civil record
    "C": "#f59e0b",  # amber — multiple secondary sources
    "D": "#ef4444",  # red — single source / AI inference
}
UNRESEARCHED_COLOR = "#d1d5db"  # light gray — no findings entry
EMPTY_COLOR = "#f3f4f6"        # very light gray — unknown ancestor
ROOT_COLOR = "#8b5cf6"         # purple for root person

TIER_LABELS = {
    "A": "Tier A — Primary source verified",
    "B": "Tier B — Indexed civil record",
    "C": "Tier C — Multiple secondary sources",
    "D": "Tier D — Single source / inference",
}


def derive_tiers_from_gedcom(records: dict, individuals: dict) -> dict[str, str]:
    """Derive verification tiers from GEDCOM source citations.

    Source ID conventions in this project:
    - S600xxx = archive research (civil records with akte numbers) → Tier B
    - S_PLxxx = Playwright/web verified sources → Tier B
    - S00xx   = manual/original sources → Tier B
    - S500xxx = MyHeritage import (other users' trees) → Tier D

    Returns {person_id: tier} based on best source quality found.
    """
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    person_tiers: dict[str, str] = {}

    for pid, person_lines in records.items():
        if pid not in individuals:
            continue

        # Collect all source references from this person's record
        source_ids = set()
        for line in person_lines:
            m = re.search(r'SOUR @([^@]+)@', line)
            if m:
                source_ids.add(m.group(1))

        if not source_ids:
            continue

        # Classify sources and pick the best tier
        best_tier = None
        for sid in source_ids:
            if sid.startswith("S600") or sid.startswith("S_PL") or re.match(r"S\d{4}$", sid):
                tier = "B"  # archive/verified sources
            elif sid.startswith("S500"):
                tier = "D"  # MyHeritage user trees
            else:
                tier = "D"  # unknown source type, be conservative

            if best_tier is None or tier_rank.get(tier, 99) < tier_rank.get(best_tier, 99):
                best_tier = tier

        if best_tier:
            person_tiers[pid] = best_tier

    return person_tiers


def parse_findings(findings_path: str) -> dict[str, str]:
    """Parse FINDINGS.md and return {person_id: best_tier}."""
    person_tiers: dict[str, list[str]] = {}
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}

    text = Path(findings_path).read_text(encoding="utf-8")

    # Split into finding blocks (## F-NNN: ...)
    blocks = re.split(r"(?=^## F-\d+)", text, flags=re.MULTILINE)

    for block in blocks:
        # Extract person ID(s) — may have multiple (I####) references
        person_match = re.search(r"\*\*Person:\*\*.*?\(I(\d+)\)", block)
        if not person_match:
            continue
        # Normalize to match GEDCOM IDs: short IDs (1-3 digits) get zero-padded to 4,
        # longer IDs (like I500050) stay as-is
        raw_num = person_match.group(1)
        if len(raw_num) <= 3:
            pid = f"I{int(raw_num):04d}"
        else:
            pid = f"I{raw_num}"

        # Extract tier
        tier_match = re.search(r"\*\*Tier:\*\*\s*([ABCD])\b", block)
        if not tier_match:
            continue
        tier = tier_match.group(1)

        # Extract status — skip REJECTED findings
        status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", block)
        if status_match and status_match.group(1) == "REJECTED":
            continue

        if pid not in person_tiers:
            person_tiers[pid] = []
        person_tiers[pid].append(tier)

    # Take best (lowest rank) tier per person
    best = {}
    for pid, tiers in person_tiers.items():
        best[pid] = min(tiers, key=lambda t: tier_rank.get(t, 99))

    return best


def build_ahnentafel(root_id: str, individuals: dict, families: dict, max_gen: int) -> dict[int, str]:
    """Build Ahnentafel numbering: 1=root, 2=father, 3=mother, 4=pat.grandfather, etc.
    Returns {ahnentafel_number: person_id}."""
    ahnen = {1: root_id}
    for n in sorted(ahnen.copy().keys()):
        _fill_ahnen(ahnen, n, individuals, families, max_gen)
    return ahnen


def _fill_ahnen(ahnen: dict, n: int, individuals: dict, families: dict, max_gen: int):
    """Recursively fill Ahnentafel positions."""
    gen = int(math.log2(n)) if n > 0 else 0
    if gen >= max_gen:
        return

    pid = ahnen.get(n)
    if not pid:
        return
    person = individuals.get(pid)
    if not person:
        return

    for fam_id in person.get("famc", []):
        fam = families.get(fam_id)
        if not fam:
            continue
        if fam["husb"] and 2 * n not in ahnen:
            ahnen[2 * n] = fam["husb"]
            _fill_ahnen(ahnen, 2 * n, individuals, families, max_gen)
        if fam["wife"] and 2 * n + 1 not in ahnen:
            ahnen[2 * n + 1] = fam["wife"]
            _fill_ahnen(ahnen, 2 * n + 1, individuals, families, max_gen)


def make_fan_chart_svg(
    ahnen: dict[int, str],
    individuals: dict,
    person_tiers: dict[str, str],
    num_generations: int,
) -> str:
    """Generate an SVG fan chart."""
    # SVG dimensions
    size = 1200
    cx, cy = size / 2, size / 2  # center
    max_radius = size / 2 - 80   # leave margin for legend

    # Ring widths — inner rings wider (fewer people, more text space)
    # Gen 0 = center circle, Gen 1-N = rings
    ring_widths = []
    total_weight = 0
    for g in range(num_generations):
        weight = max(1, num_generations - g)  # inner rings get more space
        ring_widths.append(weight)
        total_weight += weight

    ring_radii = []  # (inner_r, outer_r) for each generation
    r = 45  # start radius (center circle for root)
    ring_radii.append((0, r))  # gen 0 = center circle
    available = max_radius - r
    for g in range(1, num_generations):
        width = available * ring_widths[g] / sum(ring_widths[1:])
        ring_radii.append((r, r + width))
        r += width

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size + 160}" '
                 f'width="{size}" height="{size + 160}" '
                 f'style="font-family: \'Segoe UI\', Arial, sans-serif; background: white;">')

    # Title
    parts.append(f'<text x="{cx}" y="30" text-anchor="middle" font-size="22" font-weight="bold" fill="#1f2937">'
                 f'Ancestor Fan Chart — Research Verification Status</text>')

    # Root person — center circle
    root_pid = ahnen.get(1)
    root_person = individuals.get(root_pid, {}) if root_pid else {}
    root_name = _short_name(root_person.get("name", "?"))
    root_years = _year_range(root_person)

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{ROOT_COLOR}" stroke="#6d28d9" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="11" fill="white" font-weight="bold">'
                 f'{_escape(root_name)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="9" fill="white">'
                 f'{_escape(root_years)}</text>')

    # Draw each generation ring
    for gen in range(1, num_generations):
        inner_r, outer_r = ring_radii[gen]
        num_slots = 2 ** gen
        angle_per_slot = 360.0 / num_slots

        for i in range(num_slots):
            ahnen_num = 2 ** gen + i
            pid = ahnen.get(ahnen_num)

            # Determine color
            if pid and pid in person_tiers:
                color = TIER_COLORS[person_tiers[pid]]
                stroke = _darken(color)
            elif pid:
                color = UNRESEARCHED_COLOR
                stroke = "#9ca3af"
            else:
                color = EMPTY_COLOR
                stroke = "#e5e7eb"

            # Angles (0° = top, clockwise)
            start_angle = i * angle_per_slot - 90  # offset so 0° is top
            end_angle = start_angle + angle_per_slot

            # Draw arc segment
            parts.append(_arc_segment(cx, cy, inner_r, outer_r, start_angle, end_angle, color, stroke))

            # Add text label if person exists and segment is wide enough
            if pid:
                person = individuals.get(pid, {})
                name = _short_name(person.get("name", "?"))
                years = _year_range(person)
                mid_angle = (start_angle + end_angle) / 2
                mid_r = (inner_r + outer_r) / 2

                # Calculate arc length to decide text size and whether to show
                arc_length = 2 * math.pi * mid_r * (angle_per_slot / 360)
                ring_thickness = outer_r - inner_r

                if arc_length > 30:  # enough space for text
                    font_size = min(11, max(7, int(ring_thickness / 4)))
                    # For outer generations with thin arcs, use radial text
                    if gen <= 4:
                        parts.append(_curved_text(cx, cy, mid_r, mid_angle, name, years, font_size))
                    else:
                        parts.append(_radial_text(cx, cy, mid_r, mid_angle, name, years, font_size, ring_thickness))

    # Legend
    legend_y = size + 50
    parts.append(f'<text x="60" y="{legend_y - 20}" font-size="14" font-weight="bold" fill="#1f2937">Legend</text>')

    legend_items = [
        (ROOT_COLOR, "Root person"),
        (TIER_COLORS["A"], TIER_LABELS["A"]),
        (TIER_COLORS["B"], TIER_LABELS["B"]),
        (TIER_COLORS["C"], TIER_LABELS["C"]),
        (TIER_COLORS["D"], TIER_LABELS["D"]),
        (UNRESEARCHED_COLOR, "Unresearched — no findings entry"),
        (EMPTY_COLOR, "Unknown — ancestor not yet identified"),
    ]

    for i, (color, label) in enumerate(legend_items):
        x = 60 + (i % 2) * 520
        y = legend_y + (i // 2) * 28
        stroke = _darken(color) if color not in (EMPTY_COLOR, UNRESEARCHED_COLOR) else "#9ca3af"
        parts.append(f'<rect x="{x}" y="{y - 10}" width="18" height="18" rx="3" '
                     f'fill="{color}" stroke="{stroke}" stroke-width="1"/>')
        parts.append(f'<text x="{x + 24}" y="{y + 3}" font-size="12" fill="#374151">{_escape(label)}</text>')

    # Stats
    total_slots = sum(2**g for g in range(1, num_generations))
    filled = sum(1 for n in range(2, 2**num_generations) if n in ahnen)
    researched = sum(1 for n in range(2, 2**num_generations) if ahnen.get(n) in person_tiers)
    tier_counts = {}
    for n in range(2, 2**num_generations):
        pid = ahnen.get(n)
        if pid and pid in person_tiers:
            t = person_tiers[pid]
            tier_counts[t] = tier_counts.get(t, 0) + 1

    stats_y = legend_y + 85
    stats = f"Ancestors: {filled}/{total_slots} known ({filled/total_slots*100:.0f}%)"
    stats += f" | Researched: {researched}/{filled} ({researched/filled*100:.0f}% of known)" if filled else ""
    for t in "ABCD":
        if t in tier_counts:
            stats += f" | {t}: {tier_counts[t]}"
    parts.append(f'<text x="{cx}" y="{stats_y}" text-anchor="middle" font-size="11" fill="#6b7280">{_escape(stats)}</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


def _arc_segment(cx, cy, inner_r, outer_r, start_deg, end_deg, fill, stroke) -> str:
    """Generate SVG path for an arc segment (annular sector)."""
    # Small gap between segments
    gap = 0.3
    start_deg += gap
    end_deg -= gap

    sr = math.radians(start_deg)
    er = math.radians(end_deg)

    # Outer arc
    ox1 = cx + outer_r * math.cos(sr)
    oy1 = cy + outer_r * math.sin(sr)
    ox2 = cx + outer_r * math.cos(er)
    oy2 = cy + outer_r * math.sin(er)

    # Inner arc
    ix1 = cx + inner_r * math.cos(sr)
    iy1 = cy + inner_r * math.sin(sr)
    ix2 = cx + inner_r * math.cos(er)
    iy2 = cy + inner_r * math.sin(er)

    large_arc = 1 if (end_deg - start_deg) > 180 else 0

    d = (f"M {ix1:.2f} {iy1:.2f} "
         f"L {ox1:.2f} {oy1:.2f} "
         f"A {outer_r:.2f} {outer_r:.2f} 0 {large_arc} 1 {ox2:.2f} {oy2:.2f} "
         f"L {ix2:.2f} {iy2:.2f} "
         f"A {inner_r:.2f} {inner_r:.2f} 0 {large_arc} 0 {ix1:.2f} {iy1:.2f} Z")

    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>'


def _curved_text(cx, cy, r, angle_deg, name, years, font_size) -> str:
    """Place text along the arc at the midpoint of a segment."""
    rad = math.radians(angle_deg)
    tx = cx + r * math.cos(rad)
    ty = cy + r * math.sin(rad)

    # Rotate text to follow the arc — flip if on the bottom half
    text_angle = angle_deg + 90  # perpendicular to radius = along arc
    if 0 < angle_deg < 180:  # bottom half, flip
        text_angle += 180

    parts = []
    parts.append(f'<g transform="translate({tx:.1f},{ty:.1f}) rotate({text_angle:.1f})">')
    parts.append(f'<text text-anchor="middle" y="-2" font-size="{font_size}" fill="#1f2937" font-weight="500">'
                 f'{_escape(name)}</text>')
    if years and font_size >= 8:
        parts.append(f'<text text-anchor="middle" y="{font_size}" font-size="{max(6, font_size - 2)}" fill="#6b7280">'
                     f'{_escape(years)}</text>')
    parts.append('</g>')
    return '\n'.join(parts)


def _radial_text(cx, cy, r, angle_deg, name, years, font_size, ring_thickness) -> str:
    """Place text radially (pointing outward) for narrow outer segments."""
    rad = math.radians(angle_deg)
    tx = cx + r * math.cos(rad)
    ty = cy + r * math.sin(rad)

    # Text reads outward from center
    text_angle = angle_deg
    if 90 < angle_deg < 270 or -270 < angle_deg < -90:
        text_angle += 180

    # Truncate name for small segments
    max_chars = int(ring_thickness / (font_size * 0.55))
    display_name = name[:max_chars] + ".." if len(name) > max_chars else name

    parts = []
    parts.append(f'<g transform="translate({tx:.1f},{ty:.1f}) rotate({text_angle:.1f})">')
    parts.append(f'<text text-anchor="middle" y="3" font-size="{font_size}" fill="#1f2937">'
                 f'{_escape(display_name)}</text>')
    parts.append('</g>')
    return '\n'.join(parts)


def _short_name(full_name: str) -> str:
    """Shorten a name for display."""
    if not full_name:
        return "?"
    # Remove middle names — keep first given + surname
    parts = full_name.split()
    if len(parts) <= 2:
        return full_name
    # Keep first name and last part (surname)
    return f"{parts[0]} {parts[-1]}"


def _year_range(person: dict) -> str:
    """Format birth–death years."""
    by = person.get("birth_year")
    dy = person.get("death_year")
    if by and dy:
        return f"{by}–{dy}"
    elif by:
        return f"*{by}"
    elif dy:
        return f"†{dy}"
    return ""


def _darken(hex_color: str) -> str:
    """Darken a hex color by 20%."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * 0.75), int(g * 0.75), int(b * 0.75)
    return f"#{r:02x}{g:02x}{b:02x}"


def _escape(text: str) -> str:
    """Escape text for SVG XML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def tiers_from_db(db_path: str) -> dict[str, str]:
    """Query best tier per person from the research database."""
    import sqlite3
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT fp.person_id, f.tier FROM findings f "
        "JOIN finding_persons fp ON f.id = fp.finding_id "
        "WHERE f.tier IS NOT NULL AND (f.status IS NULL OR f.status != 'REJECTED')"
    ).fetchall()
    conn.close()

    person_tiers: dict[str, list[str]] = {}
    for r in rows:
        pid = r["person_id"]
        if pid not in person_tiers:
            person_tiers[pid] = []
        person_tiers[pid].append(r["tier"])

    return {
        pid: min(tiers, key=lambda t: tier_rank.get(t, 99))
        for pid, tiers in person_tiers.items()
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate ancestor fan chart colorized by research tier.")
    parser.add_argument("generations", nargs="?", type=int, default=7,
                        help="Number of generations to show (default: 7)")
    parser.add_argument("--gedcom", default="private/tree.ged",
                        help="Path to GEDCOM file")
    parser.add_argument("--findings", default="private/research/FINDINGS.md",
                        help="Path to FINDINGS.md")
    parser.add_argument("--output", "-o", default="private/fan_chart.svg",
                        help="Output SVG path (default: private/fan_chart.svg)")
    parser.add_argument("--db", default="private/genealogy.db",
                        help="Path to research database")
    parser.add_argument("--no-db", action="store_true",
                        help="Skip database tier source, use FINDINGS.md only")
    args = parser.parse_args()

    ged_path = Path(args.gedcom)
    findings_path = Path(args.findings)
    db_path = Path(args.db)
    root_id = os.environ.get("GEDCOM_ROOT_ID", "I0000")
    num_generations = args.generations

    if not ged_path.exists():
        print(f"GEDCOM not found: {ged_path}")
        sys.exit(1)

    print("Parsing GEDCOM...")
    records = parse_gedcom(str(ged_path))
    individuals = get_individuals(records)
    families = get_families(records)

    print(f"Loaded {len(individuals)} individuals, {len(families)} families")

    # Derive tiers: GEDCOM sources as base layer
    person_tiers = derive_tiers_from_gedcom(records, individuals)
    gedcom_count = len(person_tiers)
    print(f"Derived tiers for {gedcom_count} persons from GEDCOM source citations")

    # Override layer: DB (primary) or FINDINGS.md (fallback)
    if not args.no_db and db_path.exists():
        db_tiers = tiers_from_db(str(db_path))
        person_tiers.update(db_tiers)
        print(f"DB overrides/additions for {len(db_tiers)} persons")
    elif findings_path.exists():
        findings_tiers = parse_findings(str(findings_path))
        person_tiers.update(findings_tiers)
        print(f"FINDINGS.md overrides/additions for {len(findings_tiers)} persons")

    # Build Ahnentafel
    print(f"Building ancestor tree from {root_id} ({num_generations} generations)...")
    ahnen = build_ahnentafel(root_id, individuals, families, num_generations)
    print(f"Found {len(ahnen) - 1} ancestors")

    # Generate SVG
    svg = make_fan_chart_svg(ahnen, individuals, person_tiers, num_generations)

    out_path = Path(args.output)
    out_path.write_text(svg, encoding="utf-8")
    print(f"Fan chart written to {out_path}")
    print(f"Open in browser: file://{out_path.resolve()}")


if __name__ == "__main__":
    main()
