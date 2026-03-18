---
name: genealogie-online
description: |
  Search published Dutch family trees on Genealogie Online
  (genealogieonline.nl) via Playwright browser automation. Contains 1,108+
  Knijf person records across multiple published trees including "Stamboom
  De Knijff en verwanten", "Genealogie Van der Mersch-De Knijff", "Stamboom
  Glasmeier-Buhrs", and many others. This is a secondary source (Tier D) —
  other researchers' trees, not official archive records. Useful for finding
  leads, dates, places, and family connections to verify against primary
  sources. Triggers on: "search Genealogie Online", "published trees",
  "other researchers", "check family trees online", "/genealogie-online",
  or when looking for leads about a person across multiple researcher trees.
  No login required for viewing.
---

# Genealogie Online — Published Dutch Family Trees

Search published family trees from Dutch genealogists. Contains trees
uploaded by researchers across the Netherlands, searchable by person name.

No login required for viewing person records and tree data.

## Coverage

1,108+ Knijf person records across multiple publications. Key trees:

- **Stamboom De Knijff en verwanten** — dedicated Knijff family tree
- **Genealogie Van der Mersch-De Knijff** — Knijff genealogy
- **Stamboom Glasmeier-Buhrs** — has Gijsbert de Knijf (1780-1849) with
  parents Jan Pieterse Knijff & Klaasje Hogervegt
- **Genealogie Mostert** — van der Knijf records
- **Stamboom Peek** — Knijf records including Gijsbert Jorisz Knijf
- **Stamboom Broere** — Gijsbert Gijsbertsz Knijf (1714-1806)
- **Genealogie Verkroost** — Gijsbert Gijsberts Knijf (1720)

Top first names: Jan, Arend, Maria, Pieter, Arie, Cornelia, Cornelis,
Gerrit, Elisabeth, Neeltje, Teuntje, Gijsbert.

## Confidence

**Tier D** — other researchers' published trees. No guarantee of accuracy.
Always verify findings against official archive records (Tier A/B) before
editing the GEDCOM.

## Workflow

### 1. Navigate to person search

```
browser_navigate → https://www.genealogieonline.nl/zoeken/?q=knijf&t=person
```

### 2. Simple search

The URL parameter `q` is the surname search term, `t=person` restricts to
person results.

```
https://www.genealogieonline.nl/zoeken/?q={surname}&t=person
```

### 3. Advanced search

The search page has fields at the bottom:

| Field | URL param | Description |
|-------|-----------|-------------|
| Familienaam | q | Surname |
| Voornaam | vn | First name |
| Familienaam partner | pa | Partner surname |
| Plaatsnaam | pn | Place name |
| Geboortejaar >= | gv | Birth year from |
| Geboortejaar <= | gt | Birth year to |
| Overlijdensjaar >= | ov | Death year from |
| Overlijdensjaar <= | ot | Death year to |
| Beroep | oc | Occupation |
| Aantal resultaten | ta | Results per page (10/15/25/50/100) |

Checkbox: "Alleen personen met bronvermeldingen" — filter to persons with
source citations only.

Full URL pattern:

```
?publication=0&exclude=0&q={surname}&pa={partner}&pn={place}&vn={firstname}&ta=15&gv={birthfrom}&gt={birthto}&ov={deathfrom}&ot={deathto}&oc={occupation}&gn=&vv=&lastdays=0
```

### 4. Read results

Results show: person name (linked), birth-death years, publication name.

Each result has filter/exclude links to show only that publication or
exclude it.

15 results per page by default. Pagination with `&start=15`, `&start=30`.

Refinement suggestions appear:
- "Verfijn zoekopdracht met voornaam:" — click a first name to filter
- "Verfijn zoekopdracht met plaats:" — click a place to filter

### 5. View person details

Click a person name to open their page in the publication. Shows:
- Personal data (birth date/place, death date/place, occupation)
- Parents
- Marriage(s) with dates
- Children
- Timeline visualization
- Family tree chart (grandparents, parents, siblings, children)

Tabs: Details, Directe familie, Bronnen, Suggesties, Context.

### 6. Check sources

Click "Bronnen" tab to see if the researcher cited sources. Many entries
have no sources ("De getoonde gegevens hebben geen bronnen.").

## Related resources

The search results also link to:
- **Open Archieven** — official archive records (7,750 Knijf records)
- **Stamboom Forum** — 17 people researching Knijf, 63 forum posts
- **Stamboom Gids** — 3 websites about Knijf

## Spelling variants

The site suggests synonyms: Knijff, Knijft, Kniffen. Try all variants.

## URL structure

**Person search:** `https://www.genealogieonline.nl/zoeken/?q={q}&t=person`

**Person page:** `https://www.genealogieonline.nl/{publication-slug}/{person-id}.php`

**Publication index:** `https://www.genealogieonline.nl/{publication-slug}/`

## Output format

```
## Genealogie Online Result — [publication name]

**Person:** [name] ([birth year]-[death year])
**Born:** [date] in [place]
**Died:** [date] in [place]

**Father:** [name]
**Mother:** [name]
**Partner:** [name], married [date] in [place]

**Children:** [list]

**Source citations:** Yes/No
**Publication:** [name] by [author]

**Confidence:** Tier D — published researcher tree on Genealogie Online
```
