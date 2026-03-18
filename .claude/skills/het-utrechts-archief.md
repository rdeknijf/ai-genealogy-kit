---
name: het-utrechts-archief
description: |
  Search indexed person records and scanned documents at Het Utrechts Archief
  (hetutrechtsarchief.nl) via Playwright browser automation. This is the main
  archive for Utrecht province, covering ALL municipalities including Woerden,
  Utrecht city, Amersfoort, Zeist, and more. 13.9M+ indexed person records.
  Especially relevant for Woerden DTB records (doop-, trouw-, begraafboeken) for
  the Knijf family pre-1811. Use this skill whenever researching family lines from
  Utrecht province, looking up church records (DTB) for Woerden, or searching civil
  registry records from anywhere in Utrecht province. Triggers on: "search Het
  Utrechts Archief", "look up in Utrecht archive", "check Woerden DTB", "Woerden
  doop records", "Woerden church records", "/het-utrechts-archief", or any genealogy
  research in the Utrecht province area. No login required for viewing indexed
  records and scanned documents.
---

# Het Utrechts Archief — Utrecht Province Archive

Search 13.9M+ indexed person records from Het Utrechts Archief in Utrecht. This is
the primary archive for the entire province of Utrecht, covering all municipalities
including Woerden, Utrecht city, Amersfoort, Zeist, and more.

Especially relevant for this project: Woerden DTB records (doop-, trouw-,
begraafboeken) for the Knijf family pre-1811.

No login required for viewing indexed records and scanned documents.

## Workflow

### 1. Navigate to the person search

```
browser_navigate → https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais?mivast=39&mizig=100&miadt=39&miview=tbl&milang=nl
```

### 2. Fill the search form

The homepage has a simple "Alle velden" text box. Click **"Uitgebreid zoeken"** to
expand the advanced search panel with structured fields.

**Advanced search fields:**

| Group | Field | Description | Notes |
|-------|-------|-------------|-------|
| Persoon | Achternaam | Surname | |
| Persoon | Tussenvoegsel | Prefix | "de", "van", etc. |
| Persoon | Voornaam | First name | |
| Persoon | Rol | Role | Dopeling, Bruidegom, Bruid, Vader, Moeder, Getuige |
| Persoon 2 | Achternaam | Second person surname | Useful for finding couples |
| Persoon 2 | Tussenvoegsel | Second person prefix | |
| Persoon 2 | Voornaam | Second person first name | |
| Persoon 2 | Rol | Second person role | |
| Overige | Bron | Source type dropdown | See Bron options below |
| Overige | Plaats | Place | Municipality name |
| Overige | Periode | Date range | From-to year |
| Overige | Bevat bestand(en) | Has scans | N.v.t / Ja / Nee |

**Bron dropdown options include:**
- Doopinschrijving (baptism — pre-1811)
- Trouwinschrijving (marriage — pre-1811)
- Begraafinschrijving (burial — pre-1811)
- Geboorteakte (birth — post-1811)
- Huwelijksakte (marriage — post-1811)
- Overlijdensakte (death — post-1811)
- Memorie van successie
- Notariële akte
- Persoon in bevolkingsregister
- And more

**Wildcards:** `*` replaces multiple characters (minimum 3 characters before the
`*`), `_` replaces a single character.

Click **"Zoekvelden legen"** to clear all fields.

### 3. Submit and read results

Click the search button. Results appear in a table with columns:
Voornaam, Achternaam, Rol, Plaats, Datum.

Pagination: 20 results per page.

### 4. View record details

Click a result row to expand inline details showing:

- Full structured data (varies by record type — see below)
- Scanned document thumbnails (numbered page links) below the structured data
- Click a thumbnail to open the document viewer

### 5. Extract structured data

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

## URL parameters

The URL parameters ARE reliable for this archive (unlike OpenArchieven). Key
parameters for constructing search URLs directly:

| Parameter | Value | Description |
|-----------|-------|-------------|
| mivast | 39 | Archive ID |
| mizig | 100 | Search type |
| miadt | 39 | Archive ID (repeated) |
| miview | tbl | Table view (use `ldt` for detail view) |
| milang | nl | Language |
| mip1 | | Achternaam |
| mip2 | | Tussenvoegsel |
| mip3 | | Voornaam |
| mip4 | | Rol |
| mip5 | | Plaats |
| mib1 | | Bron code (156=Doopinschrijving, 157=Trouwinschrijving, 112=civil registry) |
| mistart | | Pagination offset (20 per page) |

Note: while URL params work, the form is more reliable for Bron selection since
the numeric codes aren't always obvious. Use the form for complex searches.

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
