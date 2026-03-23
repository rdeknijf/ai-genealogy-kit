---
name: het-utrechts-archief-optimized
description: |
  Search indexed person records and scanned documents at Het Utrechts Archief
  (hetutrechtsarchief.nl) via direct URL-parameter searches and WebFetch — no
  browser automation needed. This is the main archive for Utrecht province,
  covering ALL municipalities including Woerden, Utrecht city, Amersfoort, Zeist,
  and more. 13.9M+ indexed person records. Especially relevant for Woerden DTB
  records (doop-, trouw-, begraafboeken) for the Knijf family pre-1811. Use this
  skill whenever researching family lines from Utrecht province, looking up church
  records (DTB) for Woerden, or searching civil registry records from anywhere in
  Utrecht province. Triggers on: "search Het Utrechts Archief", "look up in Utrecht
  archive", "check Woerden DTB", "Woerden doop records", "Woerden church records",
  "/het-utrechts-archief", or any genealogy research in the Utrecht province area.
  No login required. Parallelizable — no browser needed.
---

# Het Utrechts Archief — Utrecht Province Archive

Search 13.9M+ indexed person records from Het Utrechts Archief in Utrecht via
direct URL-parameter searches and WebFetch. No browser automation needed.

This is the primary archive for the entire province of Utrecht, covering all
municipalities including Woerden, Utrecht city, Amersfoort, Zeist, and more.

Especially relevant for this project: Woerden DTB records (doop-, trouw-,
begraafboeken) for the Knijf family pre-1811.

No login required for viewing indexed records and scanned documents.

## Primary method: URL parameters + WebFetch

### 1. Search by URL parameters

Construct the search URL directly — the MAIS system accepts GET parameters:

```
https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl&mip1={surname}&mip3={firstname}
```

Use WebFetch to parse the results:

```
WebFetch → https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl&mip1=Knijf
  prompt: "Extract all search results: name, role, place, date. Show the total number of results and pagination info."
```

### URL parameters reference

| Parameter | Description | Example |
|-----------|-------------|---------|
| `mivast` | Archive ID (always 39) | `39` |
| `mizig` | Search type (always 100) | `100` |
| `miadt` | Archive ID (always 39) | `39` |
| `miview` | View: `tbl` (table) or `ldt` (detail) | `tbl` |
| `milang` | Language | `nl` |
| `mip1` | Achternaam (surname) | `Knijf` |
| `mip2` | Tussenvoegsel (prefix) | `de` |
| `mip3` | Voornaam (first name) | `Jan` |
| `mip4` | Rol (role) | `Dopeling`, `Vader`, `Moeder` |
| `mip5` | Plaats (place) | `Woerden` |
| `mib1` | Bron code (source type) | See table below |
| `mij1` | Periode van (year from) | `1700` |
| `mij2` | Periode tot (year to) | `1811` |
| `mistart` | Pagination offset | `0`, `20`, `40` |

**Bron codes (mib1):**

| Code | Source type |
|------|-----------|
| 156 | Doopinschrijving (baptism — pre-1811) |
| 157 | Trouwinschrijving (marriage — pre-1811) |
| 158 | Begraafinschrijving (burial — pre-1811) |
| 109 | Geboorteakte (birth — post-1811) |
| 110 | Huwelijksakte (marriage — post-1811) |
| 112 | Overlijdensakte (death — post-1811) |

**Wildcards:** `*` replaces multiple characters (min 3 chars before `*`), `_` replaces a single character.

### 2. Example searches

**All Knijf records in Woerden, pre-1811 baptisms:**

```
WebFetch → https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl&mip1=Knijf&mip5=Woerden&mib1=156
```

**All de Knijf marriage records:**

```
WebFetch → https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl&mip1=Knijf&mip2=de&mib1=110
```

### 3. Pagination

Results show 20 per page. Use `mistart` to paginate:

- Page 1: `mistart=0` (or omit)
- Page 2: `mistart=20`
- Page 3: `mistart=40`

### 4. View record details

Click through to detail view by changing `miview=tbl` to `miview=ldt` and adding
the record's navigation index. Or use WebFetch on the detail URL from the results.

**Record detail fields vary by record type:**

**Doopinschrijving (baptism — pre-1811):**
Doopdatum, Dopeling, Akteplaats, Aktedatum, Geboortedatum, Vader, Moeder,
Gezindte, Toegangsnummer, Inventarisnummer, Paginanummer.

**Trouwinschrijving (marriage — pre-1811):**
Trouwdatum, Bruidegom, Bruid, Akteplaats, and related fields.

**Begraafinschrijving (burial — pre-1811):**
Begraafdatum, Overledene, Akteplaats, and related fields.

**Geboorteakte / Huwelijksakte / Overlijdensakte (civil registry — post-1811):**
Similar fields to other Dutch civil registry archives.

## Pre-1811 vs post-1811 records

This distinction is critical for searching correctly:

- **Pre-1811** records use church record types: Doopinschrijving,
  Trouwinschrijving, Begraafinschrijving. Roles: Dopeling (baptized person),
  Vader, Moeder, Getuige (witness), Bruidegom (groom), Bruid (bride).

- **Post-1811** records use civil registry types: Geboorteakte, Huwelijksakte,
  Overlijdensakte.

## Patronymics (pre-1811)

For pre-1811 patronymic-era searches, people may NOT have fixed surnames. Search
by first name + father's name, or browse all records for a place/period. The Knijf
surname may not appear consistently in early records.

## Woerden DTB records

DTB records for Woerden use Toegangsnummer codes with a W-prefix (e.g. W020 for
NH dopen). These are especially relevant for tracing the Knijf family before 1811.

## Fallback: Playwright browser automation

Only needed if the URL-parameter search stops working or for the advanced search
form with autocomplete dropdowns.

Navigate to the search page:

```
browser_navigate → https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl
```

Click "Uitgebreid zoeken" for the advanced search panel with structured fields.

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Het Utrechts Archief** | Best for Utrecht province records, especially Woerden DTB |
| WieWasWie | Broader national coverage but may not have all Utrecht DTB records |
| OpenArchieven | Aggregator, may duplicate Het Utrechts Archief data |
| RHC Rijnstreek | Also covers Woerden area, has archive inventories |
| Gelders Archief | For Gelderland province only |

## Output format

```
## Het Utrechts Archief Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Toegangsnr [nr], Inventarisnr [nr], Paginanr [nr]
**Scan available:** Yes/No [number of pages]

**Confidence:** Tier A (if scan read) / Tier B (indexed data only)
```
