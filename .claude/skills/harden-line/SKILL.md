---
name: harden-line
description: |
  Systematically verify ("harden") a family line by checking every person
  against official archive records. Hardening means turning unverified tree
  data into source-backed facts with a clear confidence assessment per
  person. Use this skill whenever starting work on any family line — it is
  the default first step before extending or exploring. Triggers on:
  "harden the line", "verify the X line", "check this branch",
  "research the X family", "work on the X line", "what do we know about X",
  "/harden-line", or any request to investigate a family branch. Also use
  when the user asks to extend a line — harden what exists first, then
  explore beyond.
---

# Harden a Family Line

"Hardening" means systematically verifying every person and connection in
a family line against official records and recording the confidence level
of each node. The goal is to know exactly how solid each person is — not
to block research, but to understand what's proven and what's speculative.

## Why harden first

Hardening should be the default first step when working on a line. Not
because unverified data is forbidden, but because:

- You need to know where the solid ground ends and speculation begins
- Extending from a wrong base wastes effort
- It reveals which gaps are worth investigating
- Family members can see which parts of the tree are proven vs tentative

Hardening does NOT mean you can't explore beyond the verified chain. It
means you know the difference between "verified" and "exploring."

## What hardening checks per person

For each person, try to find official records for:

1. **Birth** — date, place, parents' names
2. **Marriage(s)** — date, place, spouse, both sets of parents, ages
3. **Death** — date, place, age (cross-validates birth year)
4. **Parent-child link** — confirmed by the person appearing as child in
   a parent's record OR as parent in their own child's record

Cross-validation catches errors: age at marriage + marriage year ≈ birth
year. Father's name in birth record = husband in parents' marriage. These
consistency checks matter more than any single record.

Not every record will exist, and not every person married. The hardening
status reflects what IS available, not what SHOULD be.

### Records by era

The type of records available depends on the time period and location:

- **1811+** (Netherlands) — civil registry (burgerlijke stand): birth,
  marriage, death certificates. Best coverage, most structured.
- **1650–1811** (Netherlands) — church records (DTB: dopen, trouwen,
  begraven), notarial acts, tax rolls. Coverage varies by parish.
- **Pre-1650** — sporadic. Tax records, court proceedings, guild records,
  land transfers. Individual records may be the only evidence.
- **Foreign records** — different systems entirely. Scottish records go
  back to 1553 (Old Parish Records). Use `/onboard-datasource` if no
  skill exists for the region.

A person from 1550 with a single notarial mention can still be PARTIAL
if that record confirms their existence and a family connection.

## Workflow

### 1. Extract the line

Parse `private/tree.ged` to get every person in the line with current data.
Use a Python script to extract: name, birth, death, marriage, parents,
spouse, children, and existing source citations.

### 2. Assess current state

For each person, determine what's verified and what's not. Present as a
table showing the verification gaps.

### 3. Verify person by person

Start from the most recent generation (best-documented) and work backward.
For each person:

a. **Search official archives** — determine the right sources based on
   time period and location, then look up birth, marriage, death records.
   Check `.claude/skills/` for existing data source skills. If the person
   is from a region or country with no skill, use `/onboard-datasource`
   to create one first. **If you discover a relevant datasource that has
   no skill** (e.g., military records, colonial archives, specialized
   databases), tell the user and note it in FINDINGS.md — missing
   datasources are important to flag so they can be onboarded.
b. **Cross-validate** — check internal consistency across records
c. **Document** — write findings to `research/private/research/FINDINGS.md` with tier and
   source reference
d. **Flag discrepancies** — if a record contradicts the GEDCOM, flag it
   clearly for user review

### 4. Apply verified data

- Tier A/B findings → edit GEDCOM with source citation (after user review)
- Tier C findings → flag in private/research/FINDINGS.md
- Discrepancies → discuss with user before any edit

### 5. Report the hardening status

After the pass, produce a summary table:

```
| Gen | Person | Birth | Marriage | Death | Parent link | Status |
|-----|--------|-------|----------|-------|-------------|--------|
| 1   | Name   | ✅ B  | ✅ B     | ✅ B  | ✅ B        | HARD   |
| 2   | Name   | ✅ B  | n/a      | ✅ B  | ✅ B        | HARD   |
| 3   | Name   | ❌    | ❌       | ❌    | ❌          | SOFT   |
```

- **HARD** — all available record types verified at Tier A/B
- **PARTIAL** — some checks verified, others missing but no contradictions
- **SOFT** — unverified, from secondary sources only

"n/a" means the record type doesn't apply or is not expected to exist
(e.g., no marriage, or pre-civil-registry period where records are scarce).
A person can be HARD without a marriage record.

## Parallelization

Each person's verification is independent. Use sub-agents where possible,
but respect the Playwright concurrency constraint (one browser session).
Non-browser work (GEDCOM parsing, cross-validation, private/research/FINDINGS.md writing)
can run in parallel with browser lookups.

## After hardening

Once the hardening pass is complete, the status table shows where to
focus next:

- **SOFT nodes** at the end of a line → these are the brick wall. Explore
  beyond them, but clearly label any new finds as speculative until
  verified.
- **PARTIAL nodes** in the middle → these are verification gaps. Fill
  them to strengthen the chain.
- **Discrepancies** → resolve these before extending. A wrong parent-child
  link means everything above it may be fiction.

If data source lookups were slow during hardening, consider running
`/improve-datasource` on the skills that were bottlenecks.
