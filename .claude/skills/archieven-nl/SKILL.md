---
name: archieven-nl
description: |
  Search across all Dutch archives via Archieven.nl — the central gateway to
  finding aids, person indexes, and image banks from dozens of participating
  archives. Use this skill whenever you need to search broadly across multiple
  Dutch archives at once, find which archive holds specific records, locate
  archive inventories (inventarissen), or search for persons across all indexed
  Dutch archives. Triggers on: "search archieven.nl", "find which archive has",
  "search across all archives", "look up in archieven", "/archieven-nl", or
  when you want to cast an even wider net than OpenArchieven. No login required.
---

# Archieven.nl — Central Dutch Archives Gateway

Search across finding aids, person indexes, images, and more from dozens of
participating Dutch archives. Not a record database itself but a gateway that
aggregates data from regional and municipal archives.

No login required. Free access.

## When to use Archieven.nl vs other sources

- **OpenArchieven** — indexes civil registry records (births, marriages, deaths)
- **Archieven.nl** — indexes archive inventories, person names in archives,
  images, newspapers, building permits, local history. Better for finding *which
  archive holds what*, and for records not in civil registries.

## Search categories

| Category | `mizig=` | What it searches |
|----------|----------|-----------------|
| Personen | `310` | Person names across all indexed archives |
| Beeld & Geluid | `210` | Images, audio, film |
| Kranten | `319` | Historical newspapers |
| Locaties | `332` | Street addresses, locations |
| Vergunningen | `299` | Building permits |

## Workflow

### 1. Navigate to person search

```
browser_navigate → https://www.archieven.nl/nl/zoeken?mizig=310
```

### 2. Fill the search fields

The person search has fields for:
- **Achternaam** (surname) — main name field
- **Voornaam** (first name)
- **Periode** (date range)
- **Instelling** (institution/archive — filter to specific archive)
- **Bron** (source — filter to specific source type)

### 3. Search syntax

Archieven.nl supports powerful search operators:
- `$` prefix — find similar words (e.g., `$mulder` returns "muller", "mulders")
- `?` — replace single letter
- `*` — replace multiple letters
- `"Jan Mulder"` — exact phrase (use quotes)
- `-de -den` — exclude terms (prefix with minus)
- Case-insensitive

### 4. Submit and read results

Results load via AJAX — wait for them to appear after submitting. The results
table shows person records from contributing archives.

Results can be displayed in table view (`miview=tbl`) or other formats.
Pagination is available for large result sets.

### 5. View record detail

Click a result to see the full record from the contributing archive. This may
link to the archive's own website for scans and detailed information.

## URL construction

Search URLs use GET parameters:
```
https://www.archieven.nl/nl/zoeken?mizig=310&miadt=0&mivast=0&milang=nl&mif3={surname}&mistart=0&miview=tbl
```

Parameters:
- `mizig` — search category (310 = personen)
- `mif3` — surname field
- `miadt` — archive institution filter (0 = all)
- `mistart` — pagination offset
- `miview` — display mode (tbl = table)
- `mires` — results per page

## Open Data portal

Archieven.nl has an open data portal at `opendata.archieven.nl` with OAI-PMH
support for harvesting 236,000+ datasets. Useful for bulk data access.

## Quirks

- **AJAX-loaded results** — content loads dynamically via JavaScript. WebFetch
  won't see results; Playwright is required.
- **Slow initial load** — the search page and results can be slow.
- **Many contributing archives** — results come from different archives with
  different data quality and formats.
- **No login required.**

## Output format

```
## Archieven.nl Result

**Person:** [name]
**Date:** [date]
**Place:** [place]
**Archive:** [contributing archive name]
**Source:** [source type and reference]

**Link to original:** [URL to archive's own record page]

**Confidence:** Tier B-C — indexed archive record via Archieven.nl gateway
```
