---
name: oorlogsbronnen
description: |
  Search the Oorlogsbronnen.nl network of WWII sources — over 1.6 million records
  from 250+ Dutch archives, museums, and libraries, plus 700,000+ indexed persons.
  Use this skill whenever researching Dutch WWII history for family members, looking
  up wartime fates, finding photos or documents from the occupation period, or
  searching for people affected by WWII in the Netherlands. Triggers on: "search
  oorlogsbronnen", "WWII records", "wartime fate", "check war sources", "what
  happened during the war", "/oorlogsbronnen", or any WWII-related genealogy
  research for Dutch persons. No login required.
---

# Oorlogsbronnen.nl — Dutch WWII Sources Network

Search 1.6 million+ WWII sources and 700,000+ indexed persons from 250+ Dutch
archives, museums, and libraries. Aggregates records from NIOD, regional archives,
war museums, commemoration centres, and more.

No login required. Free access.

## Two search entry points

### Sources (Bronnen) — search all records

```
browser_navigate → https://www.oorlogsbronnen.nl/bronnen
```

Search box: "Doorzoek meer dan 1.600.000 bronnen"
Accepts names, events, or locations as search terms.

Filter options on results:
- Source type (archival material, image, book)
- Theme (e.g., Operation Market Garden)
- Location
- Collection (e.g., NIOD materials)
- Copyright status
- Sort by date (ascending/descending)

### Persons (Personen) — search indexed people

```
browser_navigate → https://www.oorlogsbronnen.nl/personen
```

Search box: "Doorzoek meer dan 700.000 personen"

Filter fields for persons:
- First name
- Last name
- Birth date
- Birth location
- Death date
- Death location
- Themes (e.g., NSB when linked to a person)

## Workflow

### 1. Navigate to the persons page

For genealogy research, start with the persons page — it has structured data.

### 2. Enter search term

Type the person's name in the search box. The site has autocomplete suggestions.

### 3. Read results

Results show across categories:
- Images
- Videos
- People
- In-Depth Content

Person results show name, dates, and linked sources.

### 4. View person detail

Click a person result. The detail page shows:
- Name, birth/death dates and locations
- Associated themes
- Linked sources (photos, documents, archival records)
- Links to contributing organizations

## Important context for this family tree

Relevant search targets:
- **Geesje van den Hul** — died 12/13 Oct 1944 in Ede during Battle of Arnhem
  aftermath. Search for war-related records.
- **Putten families** — any Jansen, de Knijf, or related surnames from Putten
  may appear in razzia-related records.
- **Ede/Bennekom/Barneveld** — frontline area during Operation Market Garden
  (Sep-Oct 1944) and subsequent evacuation.

## Technical notes

- **Next.js React app** — this is a Single Page Application. Content loads
  dynamically via JavaScript. Playwright is required (WebFetch won't work).
- **No login required.**
- **Results may include duplicates** — the site aggregates from many sources,
  so the same person may appear multiple times from different collections.

## Output format

```
## Oorlogsbronnen Result — [type]

**Person:** [name]
**Born:** [date] in [place]
**Died:** [date] in [place]

**Sources found:**
- [source 1: type, collection, description]
- [source 2: type, collection, description]

**Contributing organizations:** [list]

**Confidence:** Tier B-C — aggregated WWII source (verify with originals)
```
