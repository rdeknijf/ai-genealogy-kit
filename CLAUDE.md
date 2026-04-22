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

## Research Database — CRITICAL

The research state is stored in a local SQLite database at `private/genealogy.db`. 
**NEVER** read `FINDINGS.md` or `RESEARCH_QUEUE.md` at startup. Instead, use the `scripts/research_db.py` tool to fetch only the context you need. This saves ~500K tokens per session.

### Database Tooling (`scripts/research_db.py`)

| Command | Purpose |
|---------|---------|
| `get-tasks [--limit N] [--status S]` | Active queue items |
| `get-person ID` | Person + findings + family + research state |
| `get-research-state ID` | Just the summary paragraph |
| `search QUERY [--limit N]` | FTS5 across findings |
| `add-finding JSON` | Insert finding + auto-link persons |
| `update-task ID --status S [--note T]` | Update queue item |
| `next-id [--type finding\|indi\|fam\|sour]` | Next available ID |
| `log-run JSON` | Record session metrics in task_runs |
| `stats` | Table counts, tier/status distribution |
| `sync-from-gedcom` | Refresh persons/families/sources from tree.ged |
| `sync-to-markdown` | Regenerate FINDINGS.md + RESEARCH_QUEUE.md from DB |
| `rebuild-research-state [--person ID]` | Recompute summaries |
| `add-task --title T --model M [...]` | Add a queue item (requires `--model`) |
| `set-model ID --model opus\|sonnet\|haiku\|none` | Tag a finding or task with a model hint |
| `next-model [--quiet]` | Print the model to use for the next session |
| `validate [--strict]` | Flag active tasks missing a `requires_model` hint |

### Model routing

Every new queue item MUST declare `requires_model` (enforced by `add-task`).
Findings can also be tagged via `set-model F-NNN --model opus` when the
*next step* on a specific finding needs deeper reasoning. The research
runner calls `next-model` before each session and launches `claude -p`
with that model.

Pick `opus` for: multi-source synthesis, ambiguous evidence weighing,
hypothesis construction, tree-structure corrections. Pick `sonnet` for:
archive lookups, record extraction, routine cross-referencing (the
default for most work).

Future: expand into `--work-type` (lookup / synthesis / decoding /
tree-edit) and `--complexity` (low / medium / high) so model + role can
be inferred instead of hand-declared.

## Data Integrity — CRITICAL

NEVER edit the GEDCOM file based on AI inference or unverified secondary sources.
All changes must follow the confidence tier system. Findings are stored in `private/genealogy.db` and can be synced to `private/research/FINDINGS.md`.

| Tier | Source | Action |
|------|--------|--------|
| **A** | Primary source (civil record scan, church book) user has seen | Edit GEDCOM directly |
| **B** | Indexed civil record from official archive with reference | Edit with source citation |
| **C** | Multiple independent secondary sources agree | Add to DB as Tier C for review |
| **D** | Single secondary source or AI inference | Note only, never edit |

When in doubt, **flag it, don't fix it**. Wrong data in a family tree is worse than missing data.

## Archive Access

See `research/DATA_SOURCES.md` for the full catalog of 40+ Dutch
genealogy archives and data sources. Key ones: OpenArchieven, WieWasWie,
FamilySearch, Gelders Archief, Delpher, Archieven.nl.

Most sources work without login via Playwright browser automation.
Project-local skills exist for each source — see `.claude/skills/`.

## Tools & Approach

- **Use `scripts/research_db.py`** to manage research state (Tasks, Findings).
- **Use `scripts/gedcom_query.py`** for fast GEDCOM record lookups (though `get-person` in DB is preferred).
- Use web search to find indexed records, then verify with primary sources.
- Cross-reference multiple independent sources before flagging changes.
- Track all findings in the database with tier and status.
- Check `private/research/HUMAN_ACTIONS.md` for things only Rutger can do (archive visits, subscriptions, family questions) — never duplicate these as AI tasks.
- Check `research/DATASOURCE_CANDIDATES.md` for datasources flagged by research agents
  that don't have skills yet. When onboarding new skills, start here.

### Fan Chart — Research Verification Status

Generate a visual fan chart showing ancestors colorized by verification tier:

```bash
python scripts/fan_chart.py [GENERATIONS]    # default: 7
```

Outputs `private/fan_chart.svg`. Colors: green (Tier A), blue (Tier B),
amber (Tier C), red (Tier D), gray (unresearched), light gray (unknown).
Tiers are derived from GEDCOM source citations and database overrides.

## Research Workflow — Harden First, Then Extend

Never extend a line (add earlier ancestors) when the existing connection is unverified.
Extending from wrong data wastes effort and produces a false tree. If a line's foundation
is Tier C/D, harden it to Tier B first — or mark the extension task BLOCKED.

1. **Get Next Task** — `python scripts/research_db.py get-tasks`
2. **Get Context** — `python scripts/research_db.py get-person <ID>` for each person in the task.
3. **Verify** — search archives, look up birth, marriage, and death records.
4. **Document** — `python scripts/research_db.py add-finding '<JSON>'`
   **CRITICAL**: JSON MUST include `"persons":["I####"]` with the GEDCOM IDs
   of all persons the finding relates to. Without this, the finding won't be
   linked and won't appear on fan charts or in research states.
5. **Update Queue** — `python scripts/research_db.py update-task <RQ-ID> --status DONE --note "Found birth record..."`
6. **Apply** — edit GEDCOM ONLY for Tier A/B evidence.
7. **Re-evaluate queue** — after onboarding new datasource skills, check BLOCKED
   tasks: `python scripts/research_db.py get-tasks --status BLOCKED`. If a blocked
   task cited "no skill for region X" and a skill now exists, unblock it.

### Sub-agents for parallel verification

Each person's verification is independent — use sub-agents to
parallelize. Launch one agent per person, each tasked with looking up
that person's birth/marriage/death records and returning structured
findings with archive references.

### Browser automation via playwright-cli

Most archive skills use HTTP APIs or Python wrapper scripts and don't need a browser.
For the remaining browser-dependent archives (FamilySearch, MyHeritage,
erfgoed-s-hertogenbosch, rhc-rijnstreek), use `playwright-cli` via Bash.

**Named sessions** (`-s=familysearch`, `-s=myheritage`) allow unlimited
parallel browsers without locking or contention.

Options for parallel research:

- **`browser-researcher` subagents** (preferred): each uses its own
  named `playwright-cli` session — true parallelism, no lock needed
- **Separate `claude` CLI instances**: each uses its own sessions
- **Main session**: use `playwright-cli` directly for quick lookups
- **Non-browser agents**: use for analysis, GEDCOM parsing, and
  cross-validation — no browser overhead

Key `playwright-cli` features for research:
- `state-save`/`state-load` — persist login sessions (FamilySearch, MyHeritage)
- `run-code` — execute JavaScript (e.g., remove cookie overlays)
- `screenshot` — capture document scans
- Snapshots save to `.playwright-cli/*.yml` files (token-efficient)

### Locking and concurrency

| Resource | Mechanism |
|----------|-----------|
| `private/tree.ged` | File lock via `.claude/hooks/file-lock.sh` (atomic mkdir, 5s wait) |
| `private/genealogy.db` | SQLite WAL mode (concurrent reads, sequential writes) |

FINDINGS.md is now a derived artifact regenerated via `research_db.py sync-to-markdown`.
No file lock needed — the DB is the source of truth.

Note: `playwright-cli` uses named sessions (`-s=name`) for parallelism —
no browser lock needed.

## Autonomous Research Rules

These rules apply to research-runner sessions and any unattended research agents.

### Persist findings immediately

Write findings to the database via `research_db.py add-finding` and update
tasks via `research_db.py update-task` after EACH research cycle, not at the
end of the session. Sessions can hit max turns or context limits at any time —
unwritten findings are permanently lost.

### Worker limits and commit discipline

- Maximum **3 concurrent** research worker subagents per runner session
- Research workers must **never commit or push** — only the management agent
  (research-runner or the human) may commit
- Workers write to the DB via `research_db.py` only

### No duplicate verification

Before requesting human verification of an archive scan, search the database
(`research_db.py search`) and verification records to confirm the scan
has not already been verified. Never present the same scan twice.

### Subagent tool awareness

When spawning browser-research subagents, explicitly state that Playwright is
available via `playwright-cli`. Subagents often forget they have browser access
and fail on JavaScript-rendered archive pages.

### Prefer API over browser

Always prefer HTTP API access over Playwright browser automation — APIs are
10-50x faster. Most archive skills already use APIs. When creating
or updating datasource skills, check for API endpoints first. Only fall back
to Playwright when no API exists.

## Public vs Private Content

The public repo (`ai-genealogy-kit`) must NEVER contain:

- Person names, GEDCOM IDs, or family-specific data
- Research queue items referencing specific people
- Content from `private/research/` files
- Family photos, scans, or documents

When editing files in the public repo, review every line for accidental
private content before committing. All binary files (images, PDFs, scans)
must go through Git LFS in the private repo — never commit binaries directly.

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

All binary files in `private/` are tracked by Git LFS. Before committing
any new binary (image, PDF, scan), verify LFS tracking with `git lfs track`.

## Memory (QMD)

Rutger has a persistent knowledge base searched by QMD (BM25, instant).
The genealogy project has extensive context in `~/ai/memory/projects.md`
(~200 lines of genealogy data) and `~/ai/memory/people.md` (family members).

At session start, search QMD for relevant context:

```bash
qmd search "genealogy" --collection memory
```

After writing new facts to memory files, re-index:

```bash
qmd update
```
