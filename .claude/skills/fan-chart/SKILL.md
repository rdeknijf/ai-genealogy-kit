---
name: fan-chart
description: |
  Generate a fan chart SVG of the ancestor tree, colorized by research verification
  tier (A/B/C/D/unresearched/unknown). Use when: (1) user asks for a "fan chart",
  "ancestor chart", "pedigree chart", or visual overview of the tree,
  (2) user wants to see research coverage or verification status visually,
  (3) user asks "what have we verified?" or "show me what's been researched",
  (4) /fan-chart command. The chart shows at a glance which ancestors have been
  verified against primary sources and which still need research.
author: Claude Code
version: 1.0.0
date: 2026-03-18
---

# Ancestor Fan Chart

## Purpose

Generates a fan chart (semicircular ancestor diagram) as an SVG file, with each
ancestor colored by their research verification tier from FINDINGS.md. This gives
a visual overview of both tree completeness and research coverage.

## How to Run

```bash
python scripts/fan_chart.py [GENERATIONS]
```

- `GENERATIONS` — number of generations to include (default: 7, which shows root
  plus 6 generations of ancestors = up to 126 ancestor slots)
- Output: `private/fan_chart.svg` (configurable with `--output`)
- Root individual: from `GEDCOM_ROOT_ID` env var (default: I0000)

### Examples

```bash
# Default: 7 generations
python scripts/fan_chart.py

# Compact 5-generation chart
python scripts/fan_chart.py 5

# Full 10-generation chart (up to 1022 ancestors)
python scripts/fan_chart.py 10

# Custom output path
python scripts/fan_chart.py 7 --output private/fan_chart_full.svg
```

After generating, open the SVG in a browser for the user:

```bash
xdg-open private/fan_chart.svg
```

## Color Scheme

| Color | Meaning |
|-------|---------|
| Purple | Root person |
| Green | Tier A — Primary source (scan/church book) verified by user |
| Blue | Tier B — Indexed civil record from official archive |
| Amber | Tier C — Multiple independent secondary sources agree |
| Red | Tier D — Single secondary source or AI inference |
| Gray | Known ancestor, not yet researched (no FINDINGS.md entry) |
| Light gray | Unknown ancestor (brick wall) |

## Data Sources & Tier Derivation

Tiers are derived in two layers:

1. **GEDCOM source citations** (base layer) — every person's SOUR references are
   classified by source ID convention:
   - `S600xxx` (archive research), `S_PLxxx` (Playwright/web), `S00xx` (manual) → **Tier B**
   - `S500xxx` (MyHeritage user trees) → **Tier D**
   - No sources → unresearched (gray)

2. **Research database** (override layer, primary) — `private/genealogy.db`
   findings override the GEDCOM-derived tier via `finding_persons` join. Falls
   back to **FINDINGS.md** if the DB doesn't exist. Use `--no-db` to force
   FINDINGS.md, or `--db <path>` for a non-default database.

This means the chart works with just the GEDCOM file — the DB/FINDINGS.md is
optional but adds finer-grained classification (Tier A from primary source
verification, Tier C from multiple secondary sources).

## What the Chart Shows

- **Ring layout**: Root person in center, each generation in a concentric ring
  outward. Inner rings are wider (fewer people, more text space).
- **Names and dates**: Each segment shows the ancestor's name and birth/death
  years where space permits. Outer generations truncate names.
- **Stats bar**: Bottom of chart shows completeness (known/total), research
  coverage (researched/known), and tier distribution counts.
- **Legend**: Full color legend with tier descriptions.

## Notes

- The chart is a pure SVG with no external dependencies — works in any browser
- Generation count tradeoffs: 5-7 generations are most readable; 8+ gets cramped
  in the outer rings but still works
- The script handles both zero-padded (I0067) and unpadded (I67) person IDs in
  FINDINGS.md, normalizing to match the GEDCOM format
