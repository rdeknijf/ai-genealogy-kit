---
name: genealogie-online-optimized
description: |
  Search published Dutch family trees on Genealogie Online
  (genealogieonline.nl) using their JSON Search API — no browser needed.
  Contains 1,108+ Knijf person records across multiple published trees
  including "Stamboom De Knijff en verwanten", "Genealogie Van der
  Mersch-De Knijff", "Stamboom Glasmeier-Buhrs", and many others. This
  is a secondary source (Tier D) — other researchers' trees, not official
  archive records. Useful for finding leads, dates, places, and family
  connections to verify against primary sources. Triggers on: "search
  Genealogie Online", "published trees", "other researchers", "check
  family trees online", "/genealogie-online", or when looking for leads
  about a person across multiple researcher trees. No login required.
---

# Genealogie Online — Published Dutch Family Trees (Optimized)

Search published family trees from Dutch genealogists. Contains trees
uploaded by researchers across the Netherlands, searchable by person name.

No login or authentication required for any access method.

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

## Primary method: JSON Search API

Genealogie Online provides an official Search API that returns structured
JSON. This is the preferred method — no browser needed, sub-100ms
responses, parallelizable, minimal context tokens.

### Search endpoint

```
https://www.genealogieonline.nl/zoeken/?q={surname}&t=person&output=json
```

Append `&output=json` to any search URL to get a JSON array of person
objects instead of HTML.

### JSON response format

Each result is an object with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID (format: `{publication_id}_{person_id}`) |
| `achternaam` | string | Surname |
| `voornaam` | string | Given name(s) |
| `geb_jaar` | integer | Birth year (absent if unknown) |
| `ovl_jaar` | integer | Death year (absent if unknown) |
| `url` | string | Full URL to person detail page |
| `publ_titel` | string | Publication title |
| `publ_url` | string | Publication base URL |

Example response:

```json
[
  {
    "id": "33_I21249",
    "achternaam": "van der KNIJF",
    "voornaam": "AREND",
    "geb_jaar": 1835,
    "ovl_jaar": 1910,
    "url": "https://www.genealogieonline.nl/genealogie_mostert/I21249.php",
    "publ_titel": "Genealogie Mostert",
    "publ_url": "https://www.genealogieonline.nl/genealogie_mostert/"
  }
]
```

### Search parameters

All parameters work with `&output=json`:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Surname (required) | `q=knijf` |
| `vn` | First name | `vn=gijsbert` |
| `pa` | Partner surname | `pa=lugt` |
| `pn` | Place name | `pn=amsterdam` |
| `gv` | Birth year from | `gv=1700` |
| `gt` | Birth year to | `gt=1800` |
| `ov` | Death year from | `ov=1900` |
| `ot` | Death year to | `ot=1920` |
| `oc` | Occupation | `oc=tuinder` |
| `ta` | Results per page (max 100) | `ta=100` |
| `start` | Pagination offset | `start=100` |
| `publication` | Filter to one publication | `publication=33` |
| `t` | Result type | `t=person` |
| `output` | Response format | `output=json` |

### Pagination

- Default: 15 results per page
- Maximum: 100 results per page (`ta=100`)
- Use `start` parameter for pagination: `start=0`, `start=100`, etc.
- Continue fetching until a page returns fewer than `ta` results

### Workflow: Search for persons

1. **Construct the JSON search URL:**

```
https://www.genealogieonline.nl/zoeken/?q={surname}&t=person&output=json&ta=100
```

Add filters as needed (vn, gv, gt, pn, etc.).

2. **Fetch with WebFetch or curl:**

```
WebFetch → URL above
```

Or in a script:

```bash
curl -s "https://www.genealogieonline.nl/zoeken/?q=knijf&vn=gijsbert&gv=1700&gt=1800&t=person&output=json&ta=100"
```

3. **Parse the JSON array.** Each object has name, years, URL, and
   publication. The `id` field contains the publication ID before the
   underscore (e.g., `33` in `33_I21249`), useful for the `publication`
   filter.

4. **Paginate if needed.** If the result count equals `ta`, fetch the
   next page with `start={ta}`:

```
&start=100  (second page)
&start=200  (third page)
```

### Workflow: View person details

Person detail pages do NOT have a JSON format. Use WebFetch to fetch the
HTML page directly — it contains rich Schema.org microdata that WebFetch
can extract cleanly.

1. **Get the person URL** from the search JSON result's `url` field.

2. **Fetch with WebFetch:**

```
WebFetch → {person_url}
Prompt: "Extract all person data: name, gender, birth date/place,
death date/place, occupations, parents (names and URLs), spouse(s)
(name, dates, marriage date/place, URL), children (name, gender,
dates, URL), grandparents, siblings, and source citations."
```

The HTML contains Schema.org `itemscope`/`itemprop` annotations for:

- Person: name, givenName, familyName, gender, birthDate, deathDate
- Places: birthPlace, deathPlace (with addressLocality, addressRegion,
  addressCountry)
- Spouse: name, givenName, familyName, birthDate, deathDate, URL
- Parents: name, givenName, familyName, gender, URL
- Children: name, givenName, familyName, gender, birthDate, deathDate, URL

3. **For programmatic parsing**, the key HTML patterns are:

- Birth date: `<meta itemprop="birthDate" content="YYYY-MM-DD"/>`
- Death date: `<meta itemprop="deathDate" content="YYYY-MM-DD"/>`
- Person div: `<div itemscope itemtype="http://schema.org/Person">`
- Parent div: `<div itemprop="parent" itemscope ...>`
- Spouse span: `<span itemprop="spouse" itemscope ...>`
- Children div: `<div itemprop="children" itemscope ...>`
- Meta description: summary sentence with birth, death, marriage,
  parents, and children count

### Workflow: Bulk search across spelling variants

Run multiple JSON searches in parallel for all surname variants:

```
knijf, knijff, knijft, kniffen, de knijf, de knijff, van der knijf
```

The JSON API is stateless and parallelizable — all variants can be
fetched simultaneously.

### Workflow: Filter to a specific publication

1. Search normally and note the publication ID from the `id` field
   (number before underscore).
2. Add `&publication={id}` to limit results to that tree.

Example: all Knijf records in Genealogie Mostert (publication 33):

```
https://www.genealogieonline.nl/zoeken/?q=knijf&publication=33&t=person&output=json&ta=100
```

## Fallback: Browser automation (Playwright)

If the JSON API is unavailable, returns errors, or if JavaScript-rendered
content is needed (e.g., timeline visualizations, interactive family tree
charts), fall back to Playwright.

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

The search page has fields at the bottom. Use the same URL parameters
documented above.

### 4. Read results

Results show: person name (linked), birth-death years, publication name.
15 results per page by default. Pagination with `&start=15`, `&start=30`.

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

Click "Bronnen" tab to see if the researcher cited sources.

## Additional APIs

### OAI-PMH endpoint

List all publications via OAI-PMH 2.0:

```
https://www.genealogieonline.nl/oai/oai2.php?verb=ListRecords&metadataPrefix=oai_dc
```

Supports: Identify, ListMetadataFormats, ListSets, ListRecords,
ListIdentifiers, GetRecord.

### Publications CSV

Full list of all publications as CSV:

```
https://www.genealogieonline.nl/api/publications/genealogie_online_list_all_publications.csv
```

Fields: title, URL, author, contact, creation date, last update.

### XML/RSS output

Search results also available as RSS/XML:

```
https://www.genealogieonline.nl/zoeken/?q={surname}&t=person&output=xml
```

## Related resources

- **Open Archieven** — official archive records (7,750 Knijf records)
- **Stamboom Forum** — 17 people researching Knijf, 63 forum posts
- **Stamboom Gids** — 3 websites about Knijf

## Spelling variants

The site suggests synonyms: Knijff, Knijft, Kniffen. Try all variants.

## URL structure

**Search JSON:** `https://www.genealogieonline.nl/zoeken/?q={q}&t=person&output=json`

**Search HTML:** `https://www.genealogieonline.nl/zoeken/?q={q}&t=person`

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
