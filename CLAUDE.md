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
- Check `private/research/RESEARCH_QUEUE.md` for prioritized research leads beyond standard hardening
- Keep notes on unresolved questions and research leads

### Fan Chart — Research Verification Status

Generate a visual fan chart showing ancestors colorized by verification tier:

```bash
python scripts/fan_chart.py [GENERATIONS]    # default: 7
```

Outputs `private/fan_chart.svg`. Colors: green (Tier A), blue (Tier B),
amber (Tier C), red (Tier D), gray (unresearched), light gray (unknown).
Tiers are derived from GEDCOM source citations, with FINDINGS.md overrides.
See `/fan-chart` skill for details.

## Research Workflow — Harden First, Then Extend

**Default approach:** When working on any family line, harden (verify)
existing data first before trying to extend further back. This doesn't
block exploration — it establishes how solid each node is so you know
where proven facts end and speculation begins. See `/harden` skill.

Researching means determining the right data sources to check based on
the time period and location of the person, in order of logical priority.
Data source skills exist in `.claude/skills/` — use `/onboard-datasource`
to create new ones, `/improve-datasource` to make existing ones faster.

### Flag missing datasources (MANDATORY)

During research, if you identify a relevant data source that has no
skill in `.claude/skills/` — **tell the user and note it**. This includes:

- An archive for a region/country with no existing skill
- A specialized record type (military, notarial, guild, colonial) that
  a different database covers better than what we have
- A database mentioned in `research/DATA_SOURCES.md` that would help
  but has no skill yet (e.g., Militieregisters.nl, NIMH, KNIL records)
- A source discovered during research that isn't in DATA_SOURCES.md at all

When this happens: (1) mention it to the user in your output, (2) add a
note in `private/research/FINDINGS.md` under the relevant finding, and
(3) if the source would be broadly useful, suggest onboarding it.

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

### Playwright concurrency

Most archive skills (12/18) now use HTTP APIs and don't need a browser.
For the remaining browser-dependent archives (FamilySearch, MyHeritage,
erfgoed-s-hertogenbosch, het-utrechts-archief, rhc-rijnstreek), use the
`browser-researcher` subagent (`.claude/agents/browser-researcher.md`).

**Each `browser-researcher` spawn gets its own isolated Playwright
browser** via inline `mcpServers`. Multiple instances run in parallel
without locking or contention.

Options for parallel research:

- **`browser-researcher` subagents** (preferred): each gets its own
  browser via inline MCP — true parallelism, no lock needed
- **Separate `claude` CLI instances**: each process spawns its own MCP
  servers — also parallel, no lock needed
- **Main session's shared Playwright plugin**: serialized by the
  `playwright-lock.sh` hook. Use for quick one-off browser lookups
  from the main session; avoid for parallel sub-agent work
- **Non-browser agents**: use for analysis, GEDCOM parsing, and
  cross-validation — no browser overhead

### Locking for concurrent agents

Three independent locks protect shared resources:

| Resource | Lock | Hook | Wait timeout |
|----------|------|------|-------------|
| `private/tree.ged` | `gedcom-tree-ged` | `.claude/hooks/file-lock.sh` | 5s |
| `private/research/FINDINGS.md` | `research-findings` | `.claude/hooks/file-lock.sh` | 5s |
| Playwright browser | `playwright-browser` | `.claude/hooks/playwright-lock.sh` | 25s |

All locks use atomic `mkdir` in `/tmp/`, track ownership by session ID,
and expire after 5 minutes (stale lock cleanup). No action needed — the
hooks run automatically on Edit/Write and Playwright MCP tool calls.

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
- `scripts/` — Python tools for GEDCOM analysis (`analyze_gedcom.py`) and visualization (`fan_chart.py`)
- `.claude/skills/` — data source and research workflow skills
