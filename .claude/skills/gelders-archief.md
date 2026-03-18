---
name: gelders-archief
description: |
  Access civil registry records and scanned documents at the Gelders Archief
  (geldersarchief.nl) via Playwright browser automation. Use this skill whenever you
  need to view the actual scanned birth/marriage/death certificate from Gelderland,
  verify a record's details against the original handwritten document, or search
  the Gelders Archief's person database. Triggers on: "check gelders archief",
  "view the scan", "see the original certificate", "look up in the Gelderland archive",
  "/gelders-archief", or when following a "Naar bron" link from WieWasWie that points
  to geldersarchief.nl. The Gelders Archief covers Gelderland province — including
  Ede/Bennekom, Barneveld, Apeldoorn, Nijkerk, Zutphen, and Arnhem. No login required
  for viewing records and scans.
---

# Gelders Archief — Gelderland Province Archive

Access indexed records and original scanned documents from the Gelders Archief in
Arnhem. This is the primary archive for Gelderland province, which covers many
branches of the de Knijf/Knijff family tree (Ede, Bennekom, Barneveld, Apeldoorn).

No login required for viewing records and scanned documents.

## Two ways to access

### 1. Via permalink from WieWasWie

WieWasWie results include a "Naar bron" link that goes directly to the Gelders
Archief record. These URLs look like:
```
https://permalink.geldersarchief.nl/[UUID]
```
They redirect to the full record page with scanned documents.

### 2. Via person search

```
browser_navigate → https://www.geldersarchief.nl/bronnen/personen?view=maisinternet
```

This opens the person database search. Fill in name fields and search.

## Record page layout

When viewing a specific record (via permalink or search), the page shows:

**Structured data fields:**
- Aktenummer (record number)
- Aktedatum (record date — this is the registration date)
- Akteplaats (registration place — the municipality)
- Geboortedatum / Huwelijksdatum / Overlijdensdatum (event date)
- Geboorteplaats (event place — often the village within the municipality)
- Kind / Bruidegom / Bruid / Overledene (the subject)
- Vader (father)
- Moeder (mother)
- Aktesoort (record type: Geboorteakte, Huwelijksakte, Overlijdensakte)
- Toegangsnummer (archive access number, e.g., "0207")
- Inventarisnummer (inventory number, e.g., "5312.02")

**Scanned pages:**
Below the structured data, there are numbered thumbnail links (1, 2, 3, etc.)
that open a document viewer showing the actual handwritten certificate pages.
Click a thumbnail to open the scan viewer.

## Viewing scans

The scan viewer shows the original handwritten document. These are the primary
sources — Tier A evidence if you can read the handwriting. The scans are high
resolution and can be zoomed.

To navigate between scan pages, use the numbered links or "Volgende" (next).

Note: 19th century Dutch handwriting (especially pre-1850) can be difficult to
read. Common challenges: the long s (ſ), abbreviations, varying ink quality.

## Birth date vs registration date (same as WieWasWie)

The Gelders Archief shows both:
- **Geboortedatum** = actual birth date
- **Aktedatum** = registration date (when declared at town hall)

Use the geboortedatum for GEDCOM entries.

## Municipalities covered

The Gelders Archief holds civil registration records for all Gelderland
municipalities. Key ones for this family tree:

- **Ede** (includes Bennekom, Lunteren, Otterlo, Ederveen)
- **Barneveld** (includes Voorthuizen, Garderen, Harselaar, Kootwijkerbroek)
- **Apeldoorn** (includes Beekbergen, Loenen)
- **Nijkerk** (includes Hoevelaken)
- **Putten**
- **Ermelo**
- **Zutphen**
- **Arnhem**

## Output format

```
## Gelders Archief Result — [record type]

**Person:** [name]
**Event:** [type], [event date] in [event place]
**Registered:** [akte date] in [akte place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Toegangsnr [nr], Inventarisnr [nr], Aktenr [nr]
**Scan available:** Yes/No [number of pages]

**Confidence:** Tier A (if scan read) / Tier B (indexed data only)
```
