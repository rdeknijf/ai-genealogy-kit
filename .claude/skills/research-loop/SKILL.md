---
name: research-loop
description: |
  Run an autonomous genealogy research cycle: assess the GEDCOM tree, find
  the highest-value gaps, look up records via archive skills, apply
  corrections, and document findings. Works outward from the root individual,
  prioritizing closer generations first. Use this skill whenever the user
  wants autonomous research done on the tree — "do some research", "harden
  lines", "fill gaps", "explore edges", "work on the tree for a while",
  "/research-loop", or any open-ended request to improve the family tree
  without a specific person or line in mind. Also use when the user sets
  up a /loop for recurring research. Unlike /harden-line (which focuses
  on ONE specific line), this skill picks the best targets across ALL
  lines and maximizes impact per cycle.
---

# Research Loop

An autonomous research cycle that assesses the tree state, identifies
the highest-value work, performs archive lookups, applies corrections,
and documents everything. Each cycle is self-contained and produces
measurable progress.

## Prerequisites

Before starting, check project configuration for:

- **Root individual** — the person to work outward from (defined in
  CLAUDE.local.md or CLAUDE.md)
- **GEDCOM path** — the working GEDCOM file location
- **Findings file** — where research findings are documented
- **Available archive skills** — check `.claude/skills/` for data source
  skills (e.g., wiewaswie.md, openarchieven.md, familysearch.md)
- **Confidence tiers** — the project's evidence classification system
  (usually defined in CLAUDE.md or the findings file header)

## Cycle structure

Each cycle has 4 phases. The whole cycle should take ~15 minutes.

### Phase 1: Assess (2 min)

Parse the GEDCOM and trace the root individual's ancestors to identify
gaps. For each direct ancestor, check:

- Birth: has date AND place AND event-level source (SOUR under BIRT)?
- Death: has date AND place AND event-level source (SOUR under DEAT)?
- Marriage: has date AND place AND source?
- Parents linked (FAMC)?

**Privacy filter — skip recent people automatically:**

Before selecting targets, filter out anyone whose records fall within
archive privacy periods. Unless the user specifically asks to research
a recent person, skip them silently:

- **Birth records:** restricted if born < 110 years ago (~1916+)
- **Death records:** restricted if died < 50 years ago (~1976+)
- **Marriage records:** restricted if married < 75 years ago (~1951+)

These are approximate Dutch civil registry thresholds. Don't waste
lookup cycles on records that won't be publicly available online.

**Priority order** for which generation to work on:

1. Great-grandparents (gen 3) — closest, most impactful
2. Great-great-grandparents (gen 4) — still close family
3. Great-great-great-grandparents (gen 5) — extending the tree
4. Beyond — only after closer generations are solid

**Within a generation**, prioritize:

- Missing death/birth DATES over missing sources on known dates
- Missing sources on verified findings (findings file says APPLIED but
  GEDCOM event lacks SOUR) over new lookups
- Persons with concrete open leads from previous research

**Use `scripts/gedcom_query.py`** for all GEDCOM queries:

```bash
python scripts/gedcom_query.py ids                    # highest IDs + counts
python scripts/gedcom_query.py gaps I0100 I0200 ...   # gap analysis
python scripts/gedcom_query.py person I0100            # full record
python scripts/gedcom_query.py search "Kemmann"        # find by surname
python scripts/gedcom_query.py validate                # integrity check
```

**NEVER use `re.DOTALL` regex over the full GEDCOM content.** Patterns like
`re.search('0 @I\d+@ INDI(.*?)(?=\n0 @)', content, re.DOTALL)` cause
catastrophic backtracking on large files (100% CPU for 45+ minutes).
Always use `gedcom_query.py` or line-by-line parsing instead.

### Phase 2: Lookup (8 min)

Launch a background agent for archive lookups using the appropriate
data source skill. The agent should do lookups **sequentially** when
using Playwright-based skills (single browser session constraint).

**Batch efficiently:** Group lookups by archive/region so the agent
doesn't need to switch between different search interfaces.

**Agent prompt template:**

```
You are a genealogy research agent. Perform archive lookups.
Read the skill at `.claude/skills/<data-source>.md` first.

Do these lookups SEQUENTIALLY:

## Lookup N: [Person name] [event type]
- What we know: [birth/death date, place, spouse, parents]
- Search: [archive] — surname "[X]", first name "[Y]",
  document type "[birth/marriage/death]",
  year_from [N], year_to [N], place "[Z]"
- Extract: [date, place, age, parents, spouse, akte, archive ref]

Return ALL findings in structured format with full archive references.
```

**While the agent runs**, do non-browser work in parallel:

- GEDCOM data cleanup (duplicate records, impossible dates)
- Cross-validation of existing data
- Updating findings file with leads and status changes
- Adding inline source citations where findings exist but SOUR tags
  are missing

### Phase 3: Apply (3 min)

For each record found by the agent:

1. **Check source ID space** — find the highest existing source ID:
   ```bash
   grep -oP 'S\d+' <gedcom_path> | sort -t'S' -k2 -n -u | tail -5
   ```
   Start new sources ABOVE the highest number. Source ID collisions
   cause data integrity issues and are hard to debug — previous
   sessions may have used IDs that look available but aren't.

2. **Edit the GEDCOM event** — add `2 SOUR @SXXXXXX@` with inline
   `3 DATA / 4 TEXT` containing the archive reference.

3. **Add source records** before `0 TRLR`:
   ```gedcom
   0 @SXXXXXX@ SOUR
   1 TITL [Document type] [Place] [Year]
   1 AUTH [Archive name]
   1 PUBL [Archive reference, register, akte number]
   ```

4. **Fix dates/ages** if the record contradicts the GEDCOM (common
   issues: registration date recorded instead of actual event date,
   approximate age ranges instead of exact age from records).

5. **Add new persons** if marriage records reveal parents not yet in
   the GEDCOM. Create INDI + FAM records and link via FAMC.

   **CRITICAL: Check INDI and FAM ID space first** — just like source IDs,
   you must verify the IDs you assign don't already exist:
   ```bash
   grep -oP 'I\d+' <gedcom_path> | sort -t'I' -k2 -n -u | tail -5
   grep -oP 'F\d+' <gedcom_path> | sort -t'F' -k2 -n -u | tail -5
   ```
   Start new records ABOVE the highest number. INDI/FAM ID collisions are
   worse than source collisions — they silently cause GEDCOM parsers to
   link the wrong person as a parent, spouse, or child. A previous session
   created records I600007-I600010 and F600004-F600005 that collided with
   existing records, corrupting family links for 4 people.

### Phase 4: Document (2 min)

Add findings to the project's findings file with:

- Finding number (sequential)
- Person ID and name
- Confidence tier and status
- Full evidence with archive references and scan URLs
- Cross-validation notes (age checks, parent name matches)
- What was corrected in the GEDCOM

### Validate

After all edits, run a quick integrity check:

```bash
python scripts/gedcom_query.py validate
```
print(f'Duplicate source IDs: {set(src_dups) if src_dups else "none"}')
print(f'Trailer present: {"0 TRLR" in content}')
```

## Summarize

End each cycle with a brief summary:

- Findings documented (numbers and descriptions)
- GEDCOM corrections applied
- Stats delta (sources, individuals, families)
- Remaining open leads for the next cycle
- **Missing datasources** — any relevant archives or databases discovered
  during research that have no skill in `.claude/skills/` (include name,
  URL, and why it would help)

## Common pitfalls

### INDI/FAM/Source ID collisions

Always check ALL existing IDs (INDI, FAM, and SOUR) before adding new
records. Previous sessions may have used IDs in the range you're about
to use. A collision means two different records share the same ID:

- **Source collisions** silently corrupt citation references
- **INDI collisions** are worse — a parser links the wrong person as
  parent, spouse, or child. Example: I600009 was both "Ortje Willems"
  and "Albert Loois", causing a 19th-century spinster to appear as a
  20th-century factory worker's family link.
- **FAM collisions** break entire family units

To check, use the validation script in the Validate section, which
detects all three types of duplicate IDs.

### Registration date vs event date

Many civil registries record events 1-3 days after they happen. The
GEDCOM should store the actual event date (birth, death), not the
registration date. Marriage records are typically registered on the
day of the ceremony.

### Multiple event blocks

GEDCOM allows multiple instances of the same event tag (e.g., two
`1 BIRT` blocks). One may have the date/place while another has the
source citation. Check for this pattern before concluding a source is
missing.

### Privacy periods

Recent death records may not be publicly indexed. The restriction
period varies by archive and country (commonly 50-100 years for deaths,
75-115 years for births). Don't waste lookups on records that can't be
found online.

### Common names

Very common names (e.g., "Jan Jansen", "John Smith") return hundreds
of results. Always narrow searches by year range, place, and verify
identity by checking parent names in the record detail.

### Place name normalization

Official records often use the municipality name rather than the
village name. Both are correct — include both when possible
(e.g., "Silvolde, Wisch" rather than just "Wisch").

### Child legitimization notes

Marriage records noting child legitimization ("wettiging", etc.) mean
the couple had children before marrying. Document this — it affects
family chronology and may explain birth records under the mother's
maiden name.
