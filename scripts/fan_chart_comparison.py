"""Generate a side-by-side Before/After fan chart comparing original MyHeritage
GEDCOM against current researched tree, colorized by verification tier."""

import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_gedcom import parse_gedcom, get_individuals, get_families
from fan_chart import (
    TIER_COLORS, TIER_LABELS, UNRESEARCHED_COLOR, EMPTY_COLOR, ROOT_COLOR,
    derive_tiers_from_gedcom, parse_findings, build_ahnentafel,
    _arc_segment, _curved_text, _radial_text, _short_name, _year_range,
    _escape, _darken,
)


def render_half_fan(
    cx, cy, ahnen, individuals, person_tiers, num_generations, max_radius,
    label, subtitle, stats_label,
):
    """Render one fan chart (half of the comparison) and return SVG elements + stats."""
    parts = []

    # Ring radii
    ring_widths = []
    for g in range(num_generations):
        weight = max(1, num_generations - g)
        ring_widths.append(weight)

    ring_radii = []
    r = 40
    ring_radii.append((0, r))
    available = max_radius - r
    for g in range(1, num_generations):
        width = available * ring_widths[g] / sum(ring_widths[1:])
        ring_radii.append((r, r + width))
        r += width

    # Title
    parts.append(f'<text x="{cx}" y="{cy - max_radius - 25}" text-anchor="middle" '
                 f'font-size="20" font-weight="bold" fill="#1f2937">{_escape(label)}</text>')
    parts.append(f'<text x="{cx}" y="{cy - max_radius - 8}" text-anchor="middle" '
                 f'font-size="12" fill="#6b7280">{_escape(subtitle)}</text>')

    # Root circle
    root_pid = ahnen.get(1)
    root_person = individuals.get(root_pid, {}) if root_pid else {}
    root_name = _short_name(root_person.get("name", "?"))
    root_years = _year_range(root_person)

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="39" fill="{ROOT_COLOR}" stroke="#6d28d9" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="10" fill="white" font-weight="bold">'
                 f'{_escape(root_name)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="8" fill="white">'
                 f'{_escape(root_years)}</text>')

    # Generation rings
    for gen in range(1, num_generations):
        inner_r, outer_r = ring_radii[gen]
        num_slots = 2 ** gen
        angle_per_slot = 360.0 / num_slots

        for i in range(num_slots):
            ahnen_num = 2 ** gen + i
            pid = ahnen.get(ahnen_num)

            if pid and pid in person_tiers:
                color = TIER_COLORS[person_tiers[pid]]
                stroke = _darken(color)
            elif pid:
                color = UNRESEARCHED_COLOR
                stroke = "#9ca3af"
            else:
                color = EMPTY_COLOR
                stroke = "#e5e7eb"

            start_angle = i * angle_per_slot - 90
            end_angle = start_angle + angle_per_slot

            parts.append(_arc_segment(cx, cy, inner_r, outer_r, start_angle, end_angle, color, stroke))

            if pid:
                person = individuals.get(pid, {})
                name = _short_name(person.get("name", "?"))
                years = _year_range(person)
                mid_angle = (start_angle + end_angle) / 2
                mid_r = (inner_r + outer_r) / 2
                arc_length = 2 * math.pi * mid_r * (angle_per_slot / 360)
                ring_thickness = outer_r - inner_r

                if arc_length > 30:
                    font_size = min(10, max(6, int(ring_thickness / 4.5)))
                    if gen <= 4:
                        parts.append(_curved_text(cx, cy, mid_r, mid_angle, name, years, font_size))
                    else:
                        parts.append(_radial_text(cx, cy, mid_r, mid_angle, name, years, font_size, ring_thickness))

    # Stats below chart
    total_slots = sum(2**g for g in range(1, num_generations))
    filled = sum(1 for n in range(2, 2**num_generations) if n in ahnen)
    tier_counts = {}
    for n in range(2, 2**num_generations):
        pid = ahnen.get(n)
        if pid and pid in person_tiers:
            t = person_tiers[pid]
            tier_counts[t] = tier_counts.get(t, 0) + 1
    researched = sum(tier_counts.values())

    stat_y = cy + max_radius + 22
    parts.append(f'<text x="{cx}" y="{stat_y}" text-anchor="middle" font-size="13" fill="#1f2937" font-weight="600">'
                 f'{filled} of {total_slots} ancestors known ({filled/total_slots*100:.0f}%)</text>')

    tier_parts = []
    for t in "ABCD":
        if t in tier_counts:
            tier_parts.append(f'Tier {t}: {tier_counts[t]}')
    if not tier_parts:
        tier_parts.append("No verified sources")
    parts.append(f'<text x="{cx}" y="{stat_y + 18}" text-anchor="middle" font-size="11" fill="#6b7280">'
                 f'{_escape(" | ".join(tier_parts))}</text>')

    return '\n'.join(parts), filled, total_slots, tier_counts


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate before/after fan chart comparison.")
    parser.add_argument("generations", nargs="?", type=int, default=9)
    parser.add_argument("--original", default="private/original_myheritage_baseline.ged")
    parser.add_argument("--current", default="private/tree.ged")
    parser.add_argument("--findings", default="private/research/FINDINGS.md")
    parser.add_argument("--output", "-o", default="private/fan_chart_comparison.svg")
    parser.add_argument("--original-root", default="I1", help="Root person ID in original GEDCOM")
    parser.add_argument("--current-root", default="I0000", help="Root person ID in current GEDCOM")
    args = parser.parse_args()

    num_gen = args.generations

    # --- Parse original ---
    print("Parsing original MyHeritage GEDCOM...")
    orig_records = parse_gedcom(args.original)
    orig_individuals = get_individuals(orig_records)
    orig_families = get_families(orig_records)
    orig_tiers = derive_tiers_from_gedcom(orig_records, orig_individuals)
    orig_ahnen = build_ahnentafel(args.original_root, orig_individuals, orig_families, num_gen)
    print(f"  {len(orig_individuals)} people, {len(orig_ahnen)-1} ancestors in {num_gen} gen")

    # --- Parse current ---
    print("Parsing current researched GEDCOM...")
    cur_records = parse_gedcom(args.current)
    cur_individuals = get_individuals(cur_records)
    cur_families = get_families(cur_records)
    cur_tiers = derive_tiers_from_gedcom(cur_records, cur_individuals)
    gedcom_tier_count = len(cur_tiers)

    findings_path = Path(args.findings)
    if findings_path.exists():
        findings_tiers = parse_findings(str(findings_path))
        cur_tiers.update(findings_tiers)
        print(f"  {gedcom_tier_count} tiers from GEDCOM + {len(findings_tiers)} from FINDINGS.md")

    cur_ahnen = build_ahnentafel(args.current_root, cur_individuals, cur_families, num_gen)
    print(f"  {len(cur_individuals)} people, {len(cur_ahnen)-1} ancestors in {num_gen} gen")

    # --- Layout ---
    fan_radius = 480
    chart_w = fan_radius * 2 + 60  # each chart width
    total_w = chart_w * 2 + 80     # two charts + gap
    top_margin = 100
    chart_h = fan_radius * 2 + 80
    bottom_margin = 180
    total_h = top_margin + chart_h + bottom_margin

    cx_left = 30 + fan_radius + 30
    cx_right = chart_w + 80 + fan_radius + 30
    cy = top_margin + fan_radius + 10

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" '
                 f'width="{total_w}" height="{total_h}" '
                 f'style="font-family: \'Segoe UI\', Arial, sans-serif; background: white;">')

    # Main title
    parts.append(f'<text x="{total_w/2}" y="40" text-anchor="middle" font-size="28" font-weight="bold" fill="#1f2937">'
                 f'Family Tree Research Progress</text>')
    root_person_cur = cur_individuals.get(args.current_root, {})
    root_display_name = _short_name(root_person_cur.get("name", "?"))
    parts.append(f'<text x="{total_w/2}" y="65" text-anchor="middle" font-size="14" fill="#6b7280">'
                 f'De Knijf / Peters / Van der Kant / Brands — {num_gen} generations from {_escape(root_display_name)}</text>')

    # Arrow between charts
    arrow_y = cy
    arrow_x1 = cx_left + fan_radius + 15
    arrow_x2 = cx_right - fan_radius - 15
    arrow_mid = (arrow_x1 + arrow_x2) / 2
    parts.append(f'<line x1="{arrow_x1}" y1="{arrow_y}" x2="{arrow_x2 - 10}" y2="{arrow_y}" '
                 f'stroke="#9ca3af" stroke-width="3" marker-end="url(#arrowhead)"/>')
    parts.append('<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" '
                 'refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af"/></marker></defs>')

    # Render both fans
    left_svg, orig_filled, orig_total, orig_tc = render_half_fan(
        cx_left, cy, orig_ahnen, orig_individuals, orig_tiers, num_gen, fan_radius,
        "Before: MyHeritage Import", f"{len(orig_individuals)} people, unverified", "original"
    )
    parts.append(left_svg)

    right_svg, cur_filled, cur_total, cur_tc = render_half_fan(
        cx_right, cy, cur_ahnen, cur_individuals, cur_tiers, num_gen, fan_radius,
        "After: AI-Assisted Research", f"{len(cur_individuals)} people, archive-verified", "current"
    )
    parts.append(right_svg)

    # Shared legend at bottom
    legend_y = top_margin + chart_h + 50
    parts.append(f'<text x="{total_w/2}" y="{legend_y - 15}" text-anchor="middle" '
                 f'font-size="14" font-weight="bold" fill="#1f2937">Verification Tiers</text>')

    legend_items = [
        (ROOT_COLOR, "Root person"),
        (TIER_COLORS["A"], TIER_LABELS["A"]),
        (TIER_COLORS["B"], TIER_LABELS["B"]),
        (TIER_COLORS["C"], TIER_LABELS["C"]),
        (TIER_COLORS["D"], TIER_LABELS["D"]),
        (UNRESEARCHED_COLOR, "Unresearched"),
        (EMPTY_COLOR, "Unknown ancestor"),
    ]

    items_per_row = 4
    item_width = total_w / items_per_row
    for i, (color, label) in enumerate(legend_items):
        col = i % items_per_row
        row = i // items_per_row
        x = 60 + col * item_width
        y = legend_y + row * 26
        stroke = _darken(color) if color not in (EMPTY_COLOR, UNRESEARCHED_COLOR) else "#9ca3af"
        parts.append(f'<rect x="{x}" y="{y - 8}" width="16" height="16" rx="3" '
                     f'fill="{color}" stroke="{stroke}" stroke-width="1"/>')
        parts.append(f'<text x="{x + 22}" y="{y + 4}" font-size="11" fill="#374151">{_escape(label)}</text>')

    # Summary stats
    new_ancestors = cur_filled - orig_filled
    new_verified = sum(cur_tc.values())
    summary_y = legend_y + 70
    parts.append(f'<text x="{total_w/2}" y="{summary_y}" text-anchor="middle" font-size="15" '
                 f'font-weight="bold" fill="#2d8a4e">'
                 f'+{new_ancestors} new ancestors discovered | '
                 f'+{len(cur_individuals) - len(orig_individuals)} people added | '
                 f'{new_verified} records archive-verified</text>')

    parts.append('</svg>')

    svg = '\n'.join(parts)
    out_path = Path(args.output)
    out_path.write_text(svg, encoding="utf-8")
    print(f"\nComparison chart written to {out_path}")
    print(f"Open: file://{out_path.resolve()}")
    print(f"\nHighlights:")
    print(f"  Ancestors: {orig_filled} -> {cur_filled} (+{new_ancestors})")
    print(f"  People: {len(orig_individuals)} -> {len(cur_individuals)} (+{len(cur_individuals)-len(orig_individuals)})")
    print(f"  Verified: {new_verified} records")


if __name__ == "__main__":
    main()
