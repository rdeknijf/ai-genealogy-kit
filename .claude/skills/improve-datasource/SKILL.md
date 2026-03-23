---
name: improve-datasource
description: |
  Take an existing data source skill and make it faster and more reliable.
  Investigates whether the current access method (usually Playwright browser
  automation) can be replaced with a faster one (API, curl, direct HTTP).
  Use this skill when: "speed up X source", "improve the X skill",
  "make X faster", "/improve-datasource", "this is taking forever",
  "the lookups are so slow", or when a data source skill is too slow or
  unreliable. Also consider triggering after a hardening run where browser
  automation was a bottleneck.
---

# Improve a Data Source Skill

Take an existing `.claude/skills/<source>.md` and find a faster, more
reliable way to access the same data.

## Why this matters

Playwright browser automation: 5-30 seconds per search, fragile (UI
changes break it), sequential (one browser session), burns context with
snapshot data.

A curl/API call: <1 second, structured data, parallelizable. For a
hardening run of 30 lookups, that's 15 minutes vs 30 seconds.

## Workflow

### 1. Read the current skill

Understand: access method, URL patterns, extracted data, known issues.

### 2. Find a faster method

Follow the same access method priority from `/onboard-datasource` —
API > OAI-PMH/SRU > URL fetch > Playwright. The difference here is that
you already have a working skill, so you can use the browser to discover
the hidden API behind the UI:

a. **Network analysis** — navigate to the search page, monitor network
   requests during a search (`browser_network_requests`), identify the
   actual data call (JSON responses, API endpoints)
b. **Replicate with curl** — try to call that endpoint directly and check
   if it works without cookies/auth
c. **API documentation search** — `site:<domain> api`, GitHub repos that
   interact with the archive, platform vendor docs (Memorix Maior,
   Picturae, MAIS Flexis, Axiell, etc.)
d. **Alternative access** — check if the same data is available via
   A2A/OAI-PMH, open data dumps, or aggregators (OpenArchieven,
   WieWasWie, FamilySearch may already index this archive)

### 5. Benchmark

| Metric | Current | Proposed |
|--------|---------|----------|
| Time per search | | |
| Structured output | | |
| Auth required | | |
| Parallelizable | | |

### 6. Update the skill

- Make the fast method the primary workflow
- Keep Playwright as a "Fallback" section at the bottom
- Test with 3+ searches
- Note what was tried and didn't work (prevents future re-investigation)

### 7. Consider bulk patterns

For high-volume lookups:

- Batch endpoints (multiple queries per call)
- Pagination (fetch all records for a surname, filter locally)
- Local caching (save results so repeated lookups are instant)
- Export/download (CSV or XML dumps from the archive)

## Output

```
## Data Source Improvement: <source name>

**Before:** <method>, ~X seconds per search
**After:** <method>, ~Y seconds per search
**Speedup:** Xz faster

**What changed:** <list>
**What was tried but didn't work:** <list with reasons>
```
