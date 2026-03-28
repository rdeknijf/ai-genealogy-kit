---
name: erfgoed-s-hertogenbosch
description: |
  Search civil records, church records (DTB), population registers, and notarial
  records at Erfgoed 's-Hertogenbosch (erfgoedshertogenbosch.nl). Covers
  's-Hertogenbosch, Rosmalen, Bokhoven, Empel, Engelen, Nuland, Orthen, and Vinkel.
  Use this skill whenever researching family lines in Den Bosch or Rosmalen, looking
  up baptism records (DTB Dopen), marriage or death records from 's-Hertogenbosch,
  or searching population registers for the Brabant branches of the family tree.
  Triggers on: "search Den Bosch archive", "look up in 's-Hertogenbosch",
  "check Rosmalen records", "erfgoed Den Bosch", "/erfgoed-s-hertogenbosch",
  or any genealogy research in the 's-Hertogenbosch area. No login required.
---

# Erfgoed 's-Hertogenbosch — Den Bosch Heritage Archive

Search 900+ archives covering 's-Hertogenbosch, Rosmalen, Bokhoven, Empel,
Engelen, Nuland, Orthen, and Vinkel. Includes civil registration, DTB church
records, population registers (1810-1939), housing registers (1930-1994),
servant records (1860-1939), and notarial records.

No login required for searching and viewing records.

The search portal is on a separate subdomain: `zoeken.erfgoedshertogenbosch.nl`.

## Browser automation via playwright-cli

All browser interaction uses `playwright-cli` via Bash with a named session:

```bash
playwright-cli -s=denbosch open
playwright-cli -s=denbosch goto "<url>"
playwright-cli -s=denbosch snapshot
# Read .playwright-cli/*.yml to find refs, then interact
playwright-cli -s=denbosch fill <ref> "search text"
playwright-cli -s=denbosch click <ref>
playwright-cli -s=denbosch close
```

## Workflow

### 1. Navigate to person search

```bash
playwright-cli -s=denbosch goto "https://zoeken.erfgoedshertogenbosch.nl/zoeken.php?zoeken[beschrijvingsgroepen][]=38089355"
playwright-cli -s=denbosch snapshot
```

The `beschrijvingsgroepen` parameter pre-selects "Personen en locaties" which is
the genealogy-relevant collection.

### 2. Fill the search form

The form uses POST with a CSRF token. Playwright handles this automatically since
you fill and submit in-browser.

Key fields:

| Field | HTML id | Notes |
|-------|---------|-------|
| Familienaam | `formfield-14-familienaam` | Surname — include prefix (e.g., "de Knijf") |
| Vrij zoeken | `formfield-4-vrij-zoeken` | Free text search across all fields |
| Periode (van) | `formfield-10-periode-van` | Date from, format: dd-mm-jjjj |
| Periode (tot) | `formfield-10-periode-tot` | Date to, format: dd-mm-jjjj |
| Rol | `formfield-18-rol` | Role filter — autocomplete (Gedoopte, Vader, Moeder, etc.) |
| Plaats | `formfield-24-plaats` | Place — autocomplete |
| Soort bron | `formfield-28-soort-bron` | Source type — autocomplete (DTB Dopen, etc.) |

There is also a "Zoeken met spellingsvarianten" checkbox (`#zoeken_spellingsvariant`)
that enables fuzzy matching on surname spelling — useful for older records.

### 3. Submit and read results

Click the "Zoeken" submit button. Results appear as a table with columns:
Beschrijving, Naam, Rol, Datum, Plaats.

Results are paginated (14 per page). Total count shown in heading.

### 4. View a record

Click a result to open the detail page. For person records, this shows:

- **Identificatie** — record ID code
- **Datum** — event date
- **Soort** — record type (e.g., "DTB Dopen", "BS Overlijden")
- **Toegang** — archive collection reference
- **Bron** — source reference
- **Kerk** — church (for DTB records)
- **Kerkelijke Gezindte** — denomination

**Personen section** lists all persons in the record:
- Naam (name)
- Geslacht (gender: m/v)
- Rol (role: Gedoopte, Vader, Moeder, Bruidegom, Bruid, etc.)
- Wettig (legitimate: Ja/Nee)

### 5. Check for scans

Some records have digitized scans attached. Look for scan images below the record
data. Many DTB person records do NOT have scans — the "Digitaliseren" button will
be disabled with "niet beschikbaar" tooltip.

## Filtering results

On the results page, use the "Soort bron" filter checkboxes in the left sidebar
to narrow by source type:
- DTB Dopen (baptisms)
- Begraveningen (DTB) (burials)
- Ondertrouw voor 1811 (marriage banns pre-1811)
- And others specific to 's-Hertogenbosch

## Record types available

| Type | Period | Content |
|------|--------|---------|
| DTB Dopen | ~1560-1811 | Baptism records from various churches |
| DTB Trouwen | ~1560-1811 | Marriage records |
| DTB Begraven | ~1560-1811 | Burial records |
| BS Geboorte | 1811+ | Civil birth records |
| BS Huwelijk | 1811+ | Civil marriage records |
| BS Overlijden | 1811+ | Civil death records |
| Bevolkingsregister | 1810-1939 | Population registers |
| Notariele akten | Various | Notarial records |
| Huisvestingsregister | 1930-1994 | Housing registers |

## Quirks

- **CSRF token**: The form requires a `unique-token` hidden field. playwright-cli
  handles this automatically since it fills and submits in-browser.
- **Autocomplete fields**: Rol, Plaats, Soort bron use jQuery Chosen dropdowns.
  Type the value and select from suggestions.
- **Date format**: dd-mm-jjjj (day-month-year, 4-digit year).
- **Cookie consent banner** appears until dismissed.
- **Platform**: Deventit Atlantis — same platform used by several Dutch archives.
- **nav_id parameter**: Used for search context in URLs (e.g., `nav_id=0-0` for
  results, `nav_id=0-1` for detail view).

## Output format

```
## Erfgoed 's-Hertogenbosch Result — [record type]

**Person:** [name]
**Role:** [Gedoopte / Vader / Moeder / etc.]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Record type:** [DTB Dopen / BS Overlijden / etc.]
**Church:** [if DTB]
**Archive ref:** [Toegang, Bron]
**Record ID:** [Identificatie code]
**Scan:** [available / not available]

**Confidence:** Tier B — official archive record from Erfgoed 's-Hertogenbosch
```
