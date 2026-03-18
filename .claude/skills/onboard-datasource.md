---
name: onboard-datasource
description: |
  Create a new data source connection skill for a genealogy archive or
  database. Investigates the source to find the fastest access method
  (API > curl > URL fetch > browser automation), documents the search
  workflow, and produces a ready-to-use skill file. Use this skill when:
  "onboard a new data source", "add X as a source", "create a skill for
  X archive", "/onboard-datasource", or when research requires an archive
  that has no existing skill in .claude/skills/. Also trigger proactively
  when during hardening or research you encounter a relevant archive with
  no matching skill — don't wait for the user to ask, just onboard it.
---

# Onboard a New Data Source

Create a data source connection skill for a genealogy archive or record
database. Produces a `.claude/skills/<source-name>.md` that any future
session can use.

## Priority: fastest connection method wins

Always investigate alternatives before resorting to browser automation:

1. **REST/JSON API** (best) — direct HTTP calls, structured responses,
   sub-second. Use `curl` or Python `httpx`/`requests`.
2. **SPARQL / OAI-PMH / SRU / A2A endpoint** — many Dutch archives
   expose these. Structured queries, no browser needed.
3. **URL-based search with predictable HTML** — construct a search URL,
   fetch with `WebFetch` or `curl`, parse the HTML.
4. **Playwright browser automation** (last resort) — only when the site
   requires JavaScript rendering, login sessions, CAPTCHAs, or complex
   form interactions that can't be replicated with HTTP.

## Before you start

Check if a skill already exists: look in `.claude/skills/` and
`research/DATA_SOURCES.md`. If the source is listed in DATA_SOURCES.md
but has no skill, that's your starting point. If neither exists, you're
starting fresh.

## Investigation workflow

### 1. Discover the source

- URL, record types, geographic/time coverage, login requirements

### 2. Find the fastest access method

Check in order — stop as soon as one works:

a. **Public API** — look for `/api/`, `/v1/`, swagger/openapi docs.
   Search the web for `"<archive name>" API`. Check if it runs on a
   known platform (Memorix Maior, Picturae, MAIS Flexis, Axiell) that
   has documented APIs.

b. **OAI-PMH / SRU / SPARQL** — try `<base>/oai/`, `<base>/sru/`,
   `<base>/sparql/`. Many Dutch archives serve A2A XML via OAI-PMH.

c. **Predictable search URLs** — do a search in the browser, check if
   URL query params reproduce the results when fetched directly.

d. **Hidden XHR/fetch calls** — monitor network during a search. Many
   "dynamic" sites call a JSON API behind the UI.

e. **Playwright** — last resort. Document the browser workflow following
   the format of existing skills (see `wiewaswie.md`, `openarchieven.md`).

### 3. Test the access method

- Run 3+ different searches to verify reliability
- Test edge cases: diacritics, date ranges, common names
- Verify response contains needed fields (names, dates, places, parents,
  archive references)

### 4. Write the skill file

Create `.claude/skills/<source-name>.md`. Use an existing skill as your
model — `wiewaswie.md` for browser-based, or whichever is closest to the
access method you found. Every skill needs:

- **Frontmatter:** name, description with trigger phrases and coverage
  area. Make the description "pushy" — include phrases that should trigger
  it (e.g., "also use when searching for records in Gelderland").
- **Coverage:** what records, what region, what time period
- **Access method:** explain which method and why
- **Step-by-step workflow:** exact commands, URLs, parameters, selectors
- **Output format** with confidence tier — match the pattern from other
  skills:
  ```
  **Confidence:** Tier B — official civil registry record from [archive]
  ```
- **Limitations and known issues**

### 5. Update DATA_SOURCES.md

Add the new source to `research/DATA_SOURCES.md` if not already listed.

### 6. Verify end-to-end

Run a real search and confirm it produces usable results.

## Naming convention

Lowercase kebab-case: `scotlandspeople.md`, `nationaal-archief.md`.

## After onboarding

Once the skill works, consider whether it could benefit from
`/improve-datasource` — especially if you had to fall back to Playwright
and suspect an API might exist but couldn't find it in the initial
investigation.
