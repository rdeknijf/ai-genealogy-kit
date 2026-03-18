---
name: erfgoedcentrum-zutphen
description: |
  Search civil records, church records, population registers, and archives at
  Erfgoedcentrum Zutphen (erfgoedcentrumzutphen.nl). Covers Brummen, Lochem,
  and Zutphen — 815,000+ historical documents with 1.1 million personal references.
  Use this skill whenever researching family lines from Zutphen (Peters, Remmers,
  Heezen families), looking up birth/marriage/death records from Zutphen, or
  searching population registers for the Zutphen area. Triggers on: "search
  Zutphen archive", "look up in Zutphen", "check Zutphen records", "Peters
  Zutphen", "Remmers Zutphen", "/erfgoedcentrum-zutphen", or any genealogy
  research in the Zutphen/Brummen/Lochem area. No login required.
---

# Erfgoedcentrum Zutphen — Zutphen Region Archive

Search 815,000+ historical documents with 1.1 million+ personal references
covering Brummen, Lochem, and Zutphen. Includes civil registration, church
records, population registers, private archives, and building permits.

No login required for searching and viewing records.

## Key family lines in this archive

- **Peters** — Jakobus Peters (I214), born 1872 Zutphen, and ancestors
- **Remmers** — Frederika Remmers (I500050), born 1825 Zutphen
- **Heezen** — Berendina Johanna Heezen (I500048), wife of Jakobus Peters
- **Harmanus Gillius Peters** and **Johannes Frederik Peters** — both from Zutphen

## Workflow

### 1. Navigate to the search page

The main site at `erfgoedcentrumzutphen.nl` may redirect to their search portal.
Try the direct search URL:

```
browser_navigate → https://erfgoedcentrumzutphen.nl/onderzoeken/genealogie
```

If this redirects, follow the redirect to the search portal.

### 2. Search for a person

The search interface likely uses the same Deventit Atlantis platform as other
Dutch archives (Erfgoed 's-Hertogenbosch, RHC Rijnstreek). Look for:

- A free text search field ("Alle velden")
- Collection checkboxes (select "Indexen" or "Personen" for person records)
- Optional fields: Familienaam, Voornaam, Periode, Plaats

Fill in the surname and click "Zoeken".

### 3. Read results

Results show in a table with person records from the archive. Each result shows:
- Name
- Date
- Place
- Source type
- Archive reference

### 4. View record detail

Click a result to see the full record. Person records typically show:
- Full name and role (Gedoopte, Vader, Moeder, etc.)
- Event date and place
- Related persons (parents, spouse)
- Archive reference (Toegang, Inventaris, Akte)
- Link to scan (if digitized)

## Alternative access

Zutphen records are also partially indexed in:
- **OpenArchieven** — search for "Zutphen" in the archive filter
- **WieWasWie** — search with Plaats = "Zutphen"
- **Gelders Archief** — holds the Zutphen civil registry (toegangsnr 0207A)

For the Peters/Remmers/Heezen lines, you may get better results searching these
other platforms first, then following links to the original Zutphen archive.

## Quirks

- **The main site may redirect** — `erfgoedcentrumzutphen.nl` redirects to their
  search portal. Follow the redirect.
- **Likely Atlantis platform** — same interface as Erfgoed 's-Hertogenbosch and
  RHC Rijnstreek. CSRF token required (Playwright handles automatically).
- **815,000+ documents** — large collection, use specific search terms.

## Output format

```
## Erfgoedcentrum Zutphen Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [Toegang, Inventaris, Akte]
**Scan:** [available / not available]

**Confidence:** Tier B — official archive record from Erfgoedcentrum Zutphen
```
