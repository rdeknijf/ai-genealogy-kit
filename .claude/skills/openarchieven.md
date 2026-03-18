---
name: openarchieven
description: |
  Search the Open Archieven (openarchieven.nl) aggregated genealogy database via
  Playwright browser automation. Use this skill when searching across multiple Dutch
  and Belgian archives at once — Open Archieven aggregates 363M+ records from dozens
  of regional archives. Triggers on: "search openarchieven", "check open archives",
  "look up in the archives", "/openarchieven", or when you want to cast a wide net
  across all Dutch/Belgian archives rather than searching a specific regional archive.
  No login required. Note: URL-based search parameters are unreliable — always use
  the browser form.
---

# Open Archieven — Aggregated Dutch & Belgian Archives

Search 363M+ genealogical records aggregated from dozens of Dutch and Belgian
archives. Open Archieven indexes civil registry records (births, marriages, deaths),
church records, population registers, and notarial records.

No login required.

## When to use Open Archieven vs other sources

- **WieWasWie** — better for targeted person lookups with structured results
- **Gelders Archief** — better for Gelderland records with scanned documents
- **Open Archieven** — best for casting a wide net across all archives, or when
  the person might be registered in an unknown municipality

## Workflow

### 1. Navigate to search

```
browser_navigate → https://www.openarchieven.nl/
```

The homepage has a simple search box that searches across all archives.

For advanced search with filters:
```
browser_navigate → https://www.openarchieven.nl/search-ext.php
```

Do NOT try to construct search URLs with query parameters — they are unreliable
and often ignore filters. Always use the browser form.

### 2. Fill the search form

**Simple search** (homepage): just type a name in the search box.

**Advanced search** has these fields:
- First person name
- Second person name (for finding couples)
- Search method: Bevat (contains), Exact, Klinkt als (sounds like)
- Archive location (dropdown — dozens of Dutch/Belgian archives)
- Occupation (beroep)
- Date range: Vanaf jaartal (from year), Tot jaartal (to year)
- Place
- Source type dropdown (includes "Huwelijk", etc.)
- Role dropdown (Bruid, Bruidegom, etc.)
- Event type (Geboorte, Huwelijk, Overlijden, etc.)

### 3. Read results

Results show a list with:
- Name
- Event type
- Date
- Place
- Source/archive

Click a result to see the full record detail page.

### 4. Record detail page

Shows structured data similar to WieWasWie:
- Person details (name, gender)
- Parents (vader, moeder)
- Event date and place
- Archive source reference
- Link to the original archive

## Key differences from WieWasWie

- Broader coverage (Belgian archives too)
- Less structured search interface
- Results link back to the source archive for scans
- URL parameters are unreliable — always use the form
- No iframe for details — results open as full pages

## Output format

```
## Open Archieven Result — [record type]

**Person:** [name]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Source archive:** [archive name, location]
**Archive ref:** [reference numbers]
**Original record:** [link to source archive if available]

**Confidence:** Tier B — official archive record via Open Archieven index
```
