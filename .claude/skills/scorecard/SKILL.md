---
name: scorecard
description: |
  Generate a research scorecard comparing the original MyHeritage GEDCOM baseline
  against the current tree to show all discoveries made by AI research. Use when:
  (1) user asks "what have we discovered?", "show me the score", "scorecard",
  "/scorecard", (2) user wants to show progress to family members,
  (3) after a research session to summarize what was accomplished.
  Compares by UID matching (not record IDs) to handle Gramps Web renumbering.
author: Claude Code
version: 1.0.0
date: 2026-03-15
---

# Genealogy Research Scorecard

## Problem

After research sessions that add ancestors, enrich records, and cite archive
sources, it's hard to see the cumulative impact. The scorecard compares the
original MyHeritage export against the current tree to quantify everything
that's been discovered.

## Context / Trigger Conditions

- User asks for a scorecard, progress summary, or "what have we found"
- User wants to show family members what the AI research has accomplished
- End of a research session — summarize the session's additions
- `/scorecard` command

## Solution

Run the scorecard script:

```bash
uv run .claude/skills/scorecard/scripts/scorecard.py
```

Optional arguments for custom paths:

```bash
uv run .claude/skills/scorecard/scripts/scorecard.py [baseline.ged] [current.ged]
```

Defaults to `original_myheritage_baseline.ged` and `tree.ged` in the project root.

## How It Works

1. **UID matching** — MyHeritage assigns `_UID` fields to every record.
   Gramps Web renumbers record IDs (I500xxx → I0xxx), but UIDs persist.
   The script matches records across files by UID, not by GEDCOM ID.

2. **New people detection** — Anyone in the current tree with no UID match
   in the baseline is genuinely new. Split into:
   - Research additions (I600xxx series — added by archive research)
   - Smart Match additions (other IDs — came via Gramps Web)

3. **Enrichment detection** — For UID-matched people, compares birth dates,
   places, death dates, parent links, occupations, and archive source
   citations (S600xxx series).

4. **Source counting** — Only counts S600xxx sources (our archive citations),
   not the original MyHeritage sources.

5. **Family connections** — Counts new F600xxx family records.

## Output

A formatted scorecard showing:

- New ancestors discovered (research vs Smart Match)
- Official archive sources cited (with titles)
- Existing records enriched (birth/death dates, places, parents, occupations)
- Per-person enrichment details
- Grand total of new facts

## Notes

- The baseline file (`original_myheritage_baseline.ged`) must exist in the
  project root. This is the unmodified first export from MyHeritage.
- The I600xxx/F600xxx/S600xxx ID convention is specific to this project's
  research workflow — records added by AI research use this range to avoid
  conflicts with Gramps Web's auto-numbering.
- GEDCOM slash formatting differences (e.g., `de Knijf` vs `/de Knijf/`)
  are NOT counted as changes — the script compares by UID, not name text.
