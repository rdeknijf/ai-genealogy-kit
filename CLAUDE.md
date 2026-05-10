# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Development Commands

```bash
# Tests (pytest, scripts dir on pythonpath)
python -m pytest                       # all tests
python -m pytest tests/test_session_state.py  # single file
python -m pytest -k "test_merge"       # by name pattern

# Lint
ruff check scripts/ tests/
ruff format --check scripts/ tests/

# Research runner (always via Docker, never on host)
cd services/genealogy-runner && docker compose run --rm genealogy-runner -c \
    "./scripts/research-runner.sh --sessions 5 --usage-tracking --weekly-ceiling proportional"

# Dry-run (validates config without launching sessions)
./scripts/research-runner.sh --dry-run --sessions 1
```

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
| `coverage-score [--gedcom PATH] [--quiet]` | Weighted research coverage percentage |
| `add-negative --person ID --source S --fingerprint F --result R` | Record a failed search |
| `check-negatives ID [--source S]` | List negative searches for a person |

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

**Screenshot file paths**: Always save screenshots to `private/scans/`
with a descriptive filename. When using `browser_take_screenshot`, set
`filename` to `private/scans/<descriptive-name>.png`. Never save
screenshots to the repo root.

### Locking and concurrency

| Resource | Mechanism |
|----------|-----------|
| `private/tree.ged` | File lock via `.claude/hooks/file-lock.sh` (atomic mkdir in `private/locks/`, 5s wait) |
| `private/genealogy.db` | SQLite WAL mode (concurrent reads, sequential writes) |

FINDINGS.md is now a derived artifact regenerated via `research_db.py sync-to-markdown`.
No file lock needed — the DB is the source of truth.

Note: `playwright-cli` uses named sessions (`-s=name`) for parallelism —
no browser lock needed.

## Research Strategies by Goal

Match the record type to the question you're trying to answer. The wrong
record type wastes time; the right one can answer multiple questions at once.

| Goal | Primary record | Why |
|------|---------------|-----|
| **Find unknown parents** | **Marriage record** of the child | Names both parents (+ birthplaces, ages, occupations). One record = up to 4 new ancestors. Always try this first. |
| **Extend a line backward** | **Marriage record** of the earliest known ancestor | Same logic — if you know X but not X's parents, find X's marriage record. |
| **Verify a birth** | Birth record (post-1811) or church baptism (pre-1811) | Confirms date, place, parents. |
| **Verify a death** | Death record | Often names parents and spouse — useful secondary confirmation of parent links. |
| **Confirm a parent-child link** | Marriage record + birth record | Two independent sources naming the same parents = Tier B. |
| **Break a pre-1811 wall** | Church baptism records in surrounding parishes | Before civil registration, try neighboring parishes, notarial archives, membership rolls. |

**The marriage record rule:** when the goal is to discover unknown parents
or extend the tree, search for **marriage records first**. They are the
single highest-yield document in Dutch genealogy. A spouse's marriage record
names both sets of parents and gives birthplaces that unlock further searches.
This applies to ALL lines, not just specific families.

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

## Research Runner Architecture

The autonomous research runner (`scripts/research-runner.sh`) runs inside
Docker (`services/genealogy-runner/`) and loops through `claude -p` sessions.

Key components:

- **`research-runner.sh`** — main loop: budget checks → model selection →
  session launch → state merge → auto-block stalled tasks
- **`parse_session_stream.py`** — live stream parser that writes `.jsonl`,
  updates `heartbeat.json`, and kills stuck sessions
- **`parse_session_log.py`** — post-hoc parser: extracts task ID, cost,
  exit reason from completed `.jsonl` files
- **`session_state.py`** — structured JSON state handoff between sessions
  (`merge_state`, `extract_state_from_log`, `format_for_prompt`)
- **`check_usage.sh`** — queries Claude OAuth API for usage percentages

Session flow: each `claude -p` session gets the research prompt with
`MAX_TURNS_VALUE` substituted, picks a task from the DB, searches archives
via subagents, writes findings inline, and emits a `STATE_JSON` block in
its output summary that gets merged into `private/research/session_state.json`.

Per-model budget tracking: Sonnet and Opus have separate usage buckets.
The runner calls `next-model` (from `research_db.py`) to pick the model
based on the next task's `requires_model` field, then checks
`model_over_budget` before launching.

## Public vs Private Content

The public repo (`ai-genealogy-kit`) must NEVER contain:

- Person names, GEDCOM IDs, or family-specific data
- Research queue items referencing specific people
- Content from `private/research/` files
- Family photos, scans, or documents

When editing files in the public repo, review every line for accidental
private content before committing. All binary files (images, PDFs, scans)
must go through Git LFS in the private repo — never commit binaries directly.

## Primary Goal — Kids' Pedigree

The default research objective is always: **fill and harden the direct
ancestor pedigree of the kids** (Freya I501635, Balder I501886). Target
generations 3-9+ with 100% filled and verified.

- Coverage is measured from the kids: `coverage-score --root I501635 --generations 9`
- When no specific task is given, the fallback is: find the generation with
  the most gaps in the kids' pedigree and work on filling/verifying them
- Direct ancestors' immediate families (siblings, spouses) are in scope when
  they help verify the direct line (e.g., marriage records naming parents)
- Never broaden collateral branches or non-blood relations unless explicitly asked
- Note anything interesting (famous ancestors, unusual names, strange stories)
  but don't let it divert from pedigree work

## File Organization

- `private/` — personal data (own git repo with LFS, gitignored by public repo)
  - `tree.ged` — working GEDCOM file
  - `genealogy.db` — SQLite research database (source of truth)
  - `research/session_state.json` — runner state handoff between sessions
  - `research/logs/` — session `.jsonl` logs + `runner.log` + `heartbeat.json`
  - `scans/` — Playwright screenshots and downloaded archive scans
- `scripts/` — Python tools and the research runner
  - `research_db.py` — central CLI for DB operations
  - `research-runner.sh` — autonomous session loop (run via Docker)
  - `session_state.py` — state merge logic
  - `parse_session_stream.py` / `parse_session_log.py` — session parsers
  - `openarchieven_search.py`, `wiewaswie_search.py`, etc. — archive API wrappers
  - `fan_chart.py` — SVG pedigree visualization
  - `schema.sql` — DB schema (used by tests and `init_db.py`)
- `services/genealogy-runner/` — Docker compose for the runner container
- `research/DATA_SOURCES.md` — catalog of Dutch genealogy archives
- `.claude/skills/` — one skill per data source + workflow skills
- `tests/` — pytest suite (uses in-memory SQLite with `schema.sql`)

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
