# AI Genealogy Kit

## Purpose

AI-assisted genealogy research framework using Claude Code. This project provides:

- Skills for searching 20+ Dutch genealogy archives via Playwright browser automation
- A systematic methodology for verifying family tree data against official records
- Python tools for parsing and analyzing GEDCOM files
- A comprehensive catalog of 40+ Dutch genealogy data sources

## Personal Configuration

If `CLAUDE.local.md` exists, read and follow its instructions at session start.
It contains project-specific overrides (family-specific research notes, server
details, etc.). This file is gitignored — create your own from the example if
needed.

## GEDCOM

The local `private/tree.ged` is the working copy for AI research and analysis.
All personal data lives in `private/` — it has its own git repo with LFS
for binary files (images, scans, PDFs). See `private/README.md`.

## Data Integrity — CRITICAL

NEVER edit the GEDCOM file based on AI inference or unverified secondary sources.
All changes must follow the confidence tier system documented in `private/research/FINDINGS.md`.

| Tier | Source | Action |
|------|--------|--------|
| **A** | Primary source (civil record scan, church book) user has seen | Edit GEDCOM directly |
| **B** | Indexed civil record from official archive with reference | Edit with source citation |
| **C** | Multiple independent secondary sources agree | Flag in private/research/FINDINGS.md for review |
| **D** | Single secondary source or AI inference | Note only, never edit |

When in doubt, **flag it, don't fix it**. Wrong data in a family tree is worse than missing data.

## Archive Access

See `research/DATA_SOURCES.md` for the full catalog of 40+ Dutch
genealogy archives and data sources. Key ones: OpenArchieven, WieWasWie,
FamilySearch, Gelders Archief, Delpher, Archieven.nl.

Most sources work without login via Playwright browser automation.
Project-local skills exist for each source — see `.claude/skills/`.

## Tools & Approach

- Parse and analyze GEDCOM files programmatically (Python with `uv`)
- Use web search to find indexed records, then verify with primary sources
- Cross-reference multiple independent sources before flagging changes
- Track all findings in `private/research/FINDINGS.md` with tier and status
- Keep notes on unresolved questions and research leads

## Research Workflow — Harden First, Then Extend

**Default approach:** When working on any family line, harden (verify)
existing data first before trying to extend further back. This doesn't
block exploration — it establishes how solid each node is so you know
where proven facts end and speculation begins. See `/harden-line` skill.

Researching means determining the right data sources to check based on
the time period and location of the person, in order of logical priority.
Data source skills exist in `.claude/skills/` — use `/onboard-datasource`
to create new ones, `/improve-datasource` to make existing ones faster.

When systematically verifying a line (patrilineal, matrilineal, or any
branch), follow this workflow:

1. **Extract the line** — parse `private/tree.ged` to get all persons in the
   line with their current GEDCOM data
2. **Verify each person** — for every person, look up birth, marriage,
   and death records in official archives. Cross-validate ages across
   records (age at marriage + marriage year = birth year, etc.)
3. **Document** — write findings to `private/research/FINDINGS.md` with tier
4. **Apply** — edit GEDCOM only for Tier A/B evidence

### Sub-agents for parallel verification

Each person's verification is independent — use sub-agents to
parallelize. Launch one agent per person, each tasked with looking up
that person's birth/marriage/death records and returning structured
findings with archive references.

### Playwright concurrency constraint

Archive lookups use Playwright browser automation (skills in
`.claude/skills/`). The Playwright MCP server runs a **single browser
session**, so only one agent can use Playwright at a time. Options:

- **Sequential within one agent**: safest, use when the line is short
- **One agent per source**: split by archive (WieWasWie agent,
  OpenArchieven agent) — each gets its own Playwright session if
  multiple MCP servers are configured, but currently they share one
- **Non-Playwright agents**: use sub-agents for analysis, cross-validation,
  and GEDCOM parsing (no browser needed) while one agent handles all
  browser lookups sequentially

## Goals

1. Understand the current state of the family tree
2. Identify gaps, dead ends, and unverified connections
3. Systematically research and extend family lines
4. Maintain a well-sourced, accurate genealogy
5. Share the tree with family

## File Organization

- `private/` — personal data (own git repo with LFS, gitignored by public repo)
  - `*.ged` — GEDCOM files
  - `research/FINDINGS.md` — research findings
  - `sources/` — scanned documents, certificates, evidence
  - `media/` — photos and scans
- `research/DATA_SOURCES.md` — catalog of Dutch genealogy archives
- `scripts/` — Python tools for parsing and analyzing GEDCOM data
- `.claude/skills/` — data source and research workflow skills
