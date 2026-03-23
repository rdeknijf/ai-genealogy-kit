---
name: delpher-optimized
description: |
  Search historical Dutch newspapers, magazines, and books on Delpher.nl via direct
  JSON API — no browser automation needed. Use this skill whenever you need to find
  obituaries, death notices (familieberichten), birth/marriage announcements, news
  articles, or any historical newspaper mentions of a person or family. Triggers on:
  "search delpher", "find in newspapers", "check old newspapers", "look for an
  obituary", "familieberichten", "/delpher", or any request to search Dutch historical
  press for people or events. Delpher has 2M+ newspapers (1618-1995), 500K magazines,
  and 200K books — all OCR'd and full-text searchable. No login required.
---

# Delpher — Historical Dutch Newspapers, Magazines & Books

Search Delpher's full-text OCR'd collection of historical Dutch publications.
Particularly useful for finding obituaries, death notices (familieberichten),
birth/marriage announcements, and contextual mentions of family members.

No login required. Everything is freely accessible.

## What to extract from the user's request

- **search terms** -- person name, place, event (use quotes for exact phrases)
- **collection** -- ddd (newspapers), dts (magazines), boeken (books)
- **date range** -- filter via period facets after searching
- **article type** -- familiebericht, advertentie, artikel, illustratie met onderschrift

## Workflow

### Primary method (JSON API)

Delpher exposes a JSON API at `/nl/api/results` that returns structured data
directly. This is 10-20x faster than browser automation and parallelizable.

#### 1. Search

Construct the search URL and fetch with `curl`:

```bash
curl -s 'https://www.delpher.nl/nl/api/results?query=QUERY&coll=COLL&page=PAGE&maxperpage=MAX&sortfield=SORT&order=ORDER'
```

**Parameters:**

| Parameter | Values | Default | Notes |
|-----------|--------|---------|-------|
| `query` | URL-encoded search string | required | Use `%22` for quotes around exact phrases |
| `coll` | `ddd` (newspapers), `dts` (magazines), `boeken` (books) | required | Must specify one collection per request |
| `page` | 1, 2, 3... | 1 | Pagination |
| `maxperpage` | 1-50 | 20 | Number of results per page |
| `sortfield` | `date`, `relevance` | relevance | Sort order |
| `order` | `asc`, `desc` | desc | Sort direction |

**Facet filters** (append to URL):

- Type: `&facets%5Btype%5D%5B%5D=familiebericht`
- Period: `&facets%5Bperiode%5D%5B%5D=0%2F19e_eeuw%2F`
- Period: `&facets%5Bperiode%5D%5B%5D=0%2F20e_eeuw%2F`
- Geography: `&facets%5Bspatial%5D%5B%5D=Regionaal%2Flokaal`

**Example -- search for familieberichten mentioning "de Knijf" in newspapers, sorted by date:**

```bash
curl -s 'https://www.delpher.nl/nl/api/results?query=%22de+Knijf%22&coll=ddd&page=1&maxperpage=50&facets%5Btype%5D%5B%5D=familiebericht&sortfield=date&order=asc'
```

#### 2. Parse the JSON response

The response is a JSON object:

```json
{
  "numberOfRecords": 253,
  "records": [...],
  "facets": [...]
}
```

**Each record contains:**

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Article heading | "Familiebericht" |
| `type` | Article type | "familiebericht", "artikel", "advertentie" |
| `date` | Publication date | "1979/04/02 00:00:00" |
| `papertitle` | Newspaper name | "Trouw" |
| `spatial` | Geographic scope | "Landelijk", "Regionaal/lokaal" |
| `spatialCreation` | Place of publication | "Meppel" |
| `publisher` | Publisher | "Organisatie Trouw" |
| `source` | Archive holding the original | "Koninklijke Bibliotheek" |
| `edition` | Day/evening edition | "Dag" |
| `volume` | Volume number | "37" |
| `issue` | Issue number | "10811" |
| `metadataKey` | Unique article identifier | "ABCDDD:010825991:mpeg21:a0169" |
| `identifier` | Resolver URL | resolver.kb.nl link |
| `accessible` | Whether content is viewable | "1" |

**Facets** show available filters and counts:

```json
{
  "facets": [
    {"name": "periode", "values": ["0/19e_eeuw/ (144)", "0/20e_eeuw/ (596)"]},
    {"name": "type", "values": ["advertentie (123)", "artikel (366)", "familiebericht (253)"]},
    {"name": "spatial", "values": ["Landelijk (245)", "Regionaal/lokaal (459)"]}
  ]
}
```

#### 3. Get full article OCR text

For any record, fetch the OCR text using the `metadataKey`:

```bash
curl -s 'https://www.delpher.nl/nl/api/resource?coll=ddd&identifier=METADATA_KEY&type=ocr'
```

This returns JSON with a `text` field containing the full OCR transcription.

**Other available resource types:**

| Type | Returns |
|------|---------|
| `ocr` | Plain text OCR of the article |
| `dc` | Dublin Core metadata |
| `dcx` | Extended Dublin Core metadata |
| `alto` | ALTO XML with word coordinates |
| `pdf` | PDF of the page |
| `thumbnail` | Thumbnail image URL |
| `image` | Full-size page image URL |

#### 4. Construct article URLs for linking

```
https://www.delpher.nl/nl/kranten/view?coll=ddd&identifier=METADATA_KEY
```

For magazines: replace `kranten` with `tijdschriften` and `ddd` with `dts`.
For books: replace `kranten` with `boeken` and `ddd` with `boeken`.

#### 5. Pagination strategy

- First request: check `numberOfRecords` to know total results
- For genealogy, usually filter on `familiebericht` first (reduces result set)
- Use `maxperpage=50` to get more results per request
- Iterate pages: `page=1`, `page=2`, etc.
- For large result sets, combine search terms to narrow down

### SRU endpoint (alternative)

The KB also exposes an SRU 1.2 endpoint for more advanced queries:

```bash
curl -s 'https://jsru.kb.nl/sru/sru?version=1.2&operation=searchRetrieve&x-collection=DDD_artikel&query=%22de+Knijf%22&recordSchema=ddd&maximumRecords=20'
```

This returns XML with the same metadata. Use when you need:

- CQL query syntax for complex boolean searches
- Specific index searches (title, creator, date ranges)
- Integration with library search tools

The JSON API is simpler and preferred for most genealogy use cases.

### Fallback (browser automation)

If the API is unavailable, returns errors, or the response format changes,
fall back to Playwright browser automation:

#### Navigate and search

```
browser_navigate -> https://www.delpher.nl/
```

Fill the search box (labeled "Zoeken in alle tekstcollecties") with the query.
Use double quotes around names for exact phrase matching, e.g. `"de Knijf" Bennekom`.

Click the "Zoeken" button. Wait for results -- page shows "Bezig met laden" while loading.

#### Read the overview

Results show counts per collection type:

- krantenartikelen (newspaper articles)
- tijdschriften (magazines)
- boeken (books)
- externe krantenpagina's (external newspaper pages)
- radiobulletins (radio bulletins)

Click the relevant collection to see individual results.

#### Browse results

Each result shows:

- Article title/heading
- Text snippet with search terms highlighted
- Krantentitel (newspaper name)
- Datum (date)

#### Filter results

Left sidebar has filters:

- **Periode** -- century or custom date range
- **Soort bericht** -- Advertentie, Artikel, Familiebericht (most useful for genealogy)
- **Verspreidingsgebied** -- Landelijk (national), Regionaal/lokaal
- **Krantentitel** -- specific newspaper

For genealogy, filter on "Familiebericht" to find death notices and family announcements.

#### View full article

Click an article to see the full text and a scan of the original newspaper page.

## Search tips

- **Exact name matching**: `%22Jan+de+Knijf%22` (URL-encoded quotes)
- **Name + place**: `%22de+Knijf%22+Bennekom` finds the name near the place
- **Obituaries**: add `&facets%5Btype%5D%5B%5D=familiebericht` to filter
- **Spelling variants**: try both old and modern spellings. OCR errors are common,
  especially with f/s, ij/y, and broken ligatures
- **Date sorting**: use `&sortfield=date&order=asc` for chronological order
- **Parallel searches**: run multiple curl commands simultaneously for different
  name variants or collections (impossible with browser automation)

## What you'll typically find

| Type | Genealogical value |
|------|-------------------|
| **Familieberichten** | Death notices with age, place, surviving relatives -- confirms dates and family relationships |
| **Geboorte/Huwelijk** | Birth and marriage announcements -- social context, witnesses |
| **Troepenschepen** | Military transport lists -- name, rank, home address |
| **Examenuitslagen** | School exam results -- places people in time and location |
| **Rechtswezen** | Legal proceedings -- property, disputes, context |
| **Advertenties** | Job ads, business listings -- occupations and addresses |

## Output format

```
## Delpher Result -- [article type]

**Source:** [newspaper name], [date]
**Type:** [Familiebericht / Artikel / Advertentie]
**Text:** [OCR text excerpt with key details]

**Genealogical relevance:** [what this tells us -- confirms a date, reveals a relationship, etc.]
**Confidence:** Tier B -- contemporary newspaper record
**Link:** https://www.delpher.nl/nl/kranten/view?coll=ddd&identifier=[metadataKey]
```

## Confidence tier

Newspaper mentions are **Tier B** evidence -- they're contemporary published records,
though OCR can introduce errors in names/dates. The original scan is always available
to verify the OCR text. Family notices (familieberichten) are particularly reliable
as they were submitted by the family themselves.

## Quick reference

```bash
# Search newspapers for familieberichten
curl -s 'https://www.delpher.nl/nl/api/results?query=%22SURNAME%22&coll=ddd&facets%5Btype%5D%5B%5D=familiebericht&maxperpage=50&sortfield=date&order=asc'

# Search magazines
curl -s 'https://www.delpher.nl/nl/api/results?query=%22SURNAME%22&coll=dts&maxperpage=50'

# Search books
curl -s 'https://www.delpher.nl/nl/api/results?query=%22SURNAME%22&coll=boeken&maxperpage=50'

# Get OCR text for an article
curl -s 'https://www.delpher.nl/nl/api/resource?coll=ddd&identifier=METADATA_KEY&type=ocr'

# Get metadata for an article
curl -s 'https://www.delpher.nl/nl/api/resource?coll=ddd&identifier=METADATA_KEY&type=dcx'
```
