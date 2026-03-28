---
name: rhc-rijnstreek
description: |
  Search civil records, population registers, and archives at RHC Rijnstreek en
  Lopikerwaard (archief.rhcrijnstreek.nl). Covers Woerden, Bodegraven, Lopik,
  Montfoort, Oudewater, Reeuwijk, IJsselstein, and surrounding areas. Use this
  skill whenever researching family lines from Woerden or the Rijnstreek region,
  looking up van Heukelom records, or searching civil/church records from the
  Woerden area. Triggers on: "search Woerden archive", "look up in RHC Rijnstreek",
  "check Woerden records", "van Heukelom", "/rhc-rijnstreek", or any genealogy
  research in the Woerden/Rijnstreek area. No login required.
---

# RHC Rijnstreek en Lopikerwaard — Woerden Region Archive

Search 1,100+ archives and collections covering Woerden, Bodegraven, Lopik,
Montfoort, Oudewater, Reeuwijk, IJsselstein, and water boards.

No login required for searching. Same Deventit Atlantis platform as Erfgoed
's-Hertogenbosch.

## Browser automation via playwright-cli

All browser interaction uses `playwright-cli` via Bash with a named session:

```bash
playwright-cli -s=rhc open
playwright-cli -s=rhc goto "https://archief.rhcrijnstreek.nl/zoeken.php?overzicht=alles"
playwright-cli -s=rhc snapshot
# Read .playwright-cli/*.yml to find refs, then interact
playwright-cli -s=rhc fill <ref> "search text"
playwright-cli -s=rhc click <ref>
playwright-cli -s=rhc close
```

## Workflow

### 1. Navigate to the search page

```bash
playwright-cli -s=rhc goto "https://archief.rhcrijnstreek.nl/zoeken.php?overzicht=alles"
playwright-cli -s=rhc snapshot
```

### 2. Select the right collection

The page has checkboxes for collections. For genealogy, the most useful are:

| Collection | Content |
|------------|---------|
| **Indexen** | Person records — civil registry, church records, population registers |
| **Streekgenoten** | Local people database |
| Archieven | Archive inventories |
| Bouwvergunningen | Building permits |
| Foto's en kaarten | Photos and maps |
| Kranten | Newspapers |
| Bibliotheek | Library catalog |
| Lokale historie | Local history articles |

For person lookups, uncheck everything except **Indexen** (and optionally
**Streekgenoten**) to focus results.

### 3. Fill the search form

Key field:

| Field | HTML id | Notes |
|-------|---------|-------|
| Alle velden | `formfield-0-alle-velden` | Free text — enter name, place, or other terms |

There is also a "Zoeken met spellingsvarianten" checkbox for fuzzy matching.

The form uses POST with a CSRF token (`unique-token` hidden field). playwright-cli
handles this automatically since it fills and submits in-browser.

### 4. Submit and read results

Find the "Zoeken" button ref in the snapshot and click it. Take a new snapshot
to read results.

### 5. View record detail

Click a result ref to see the full record. Person records show:
- Name, date, place
- Role (Gedoopte, Vader, Moeder, etc.)
- Archive reference (Toegang, Bron)
- Links to related records
- Scans (if digitized)

## Advanced search fields

When "Indexen" is selected, additional fields may appear for narrowing:
- Familienaam (surname)
- Voornaam (first name)
- Periode (date range)
- Plaats (place)
- Rol (role in record)

These work the same as in other Atlantis-platform archives.

## Quirks

- **Same platform as Erfgoed 's-Hertogenbosch** — the Deventit Atlantis interface
  works identically. If you know how to use one, you know both.
- **CSRF token** required for POST — playwright-cli handles this (fills in-browser).
- **jQuery Chosen** for autocomplete dropdowns.
- **Cookie consent banner** on first visit — dismiss via `playwright-cli click`.

## Output format

```
## RHC Rijnstreek Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [Toegang, Bron]
**Scan:** [available / not available]

**Confidence:** Tier B — official archive record from RHC Rijnstreek
```
