---
name: openarchieven
description: |
  Search the Open Archieven (openarchieven.nl) aggregated genealogy database.
  Uses the free JSON API (api.openarchieven.nl) as primary method with Playwright
  browser automation as fallback. Open Archieven aggregates 363M+ records from
  dozens of Dutch and Belgian archives. Triggers on: "search openarchieven",
  "check open archives", "look up in the archives", "/openarchieven", or when
  you want to cast a wide net across all Dutch/Belgian archives rather than
  searching a specific regional archive. No login or API key required for search.
---

# Open Archieven -- Aggregated Dutch & Belgian Archives

Search 363M+ genealogical records aggregated from dozens of Dutch and Belgian
archives. Open Archieven indexes civil registry records (births, marriages,
deaths), church records, population registers, and notarial records.

No login or API key required for search, show, and match endpoints.

## When to use Open Archieven vs other sources

- **WieWasWie** -- better for targeted person lookups with structured results
- **Gelders Archief** -- better for Gelderland records with scanned documents
- **Open Archieven** -- best for casting a wide net across all archives, or when
  the person might be registered in an unknown municipality

## Primary method: JSON API

The Open Archives API at `api.openarchieven.nl` provides free, structured JSON
access to all records. Rate limit: 4 requests per second per IP.

### 1. Search for persons

Use WebFetch or curl to call the search endpoint:

```
https://api.openarchieven.nl/1.1/records/search.json?name=QUERY&lang=en&number_show=NUMBER
```

**Required parameter:**

- `name` -- search query (supports advanced syntax, see below)

**Optional parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| `number_show` | Results per page (max 100) | `10`, `50`, `100` |
| `start` | Pagination offset | `0`, `10`, `20` |
| `archive_code` | Filter by archive | `cod`, `ghn`, `nha`, `ran` |
| `sourcetype` | Filter by source type | `BS Geboorte`, `BS Huwelijk`, `BS Overlijden` |
| `eventplace` | Filter by event location | `Apeldoorn`, `Amsterdam` |
| `country_code` | Filter by country | `nl`, `be`, `fr`, `sr` |
| `sort` | Sort column (negative = desc) | `1`=Name, `4`=Date, `-4`=Date desc |
| `lang` | Language | `en`, `nl` |

**Name query syntax:**

- Simple surname: `name=Knijf`
- Full name: `name=Jan+de+Knijf`
- Couple search (finds marriage records): `name=Jan+de+Knijf+%26+Maria` (use `&` encoded as `%26`)
- With year: `name=Knijf+1850`
- With year range: `name=Knijf+1800-1850`

**Common sourcetype values for filtering:**

- `BS Geboorte` -- civil registration births
- `BS Huwelijk` -- civil registration marriages
- `BS Overlijden` -- civil registration deaths
- `DTB Dopen` -- church baptism records
- `DTB Trouwen` -- church marriage records
- `DTB Begraven` -- church burial records
- `Bevolkingsregister` -- population register

**Example search calls:**

```bash
# Search for surname "Knijf", first 20 results
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&lang=en&number_show=20"

# Search for marriage records of "Knijf" in Apeldoorn
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&sourcetype=BS+Huwelijk&eventplace=Apeldoorn&lang=en&number_show=20"

# Search for a couple (finds records linking both names)
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Jan+de+Knijf+%26+Maria&lang=en&number_show=10"

# Sort by date descending, Netherlands only
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&country_code=nl&sort=-4&lang=en&number_show=20"
```

**Response structure:**

```json
{
  "query": { "name": "Knijf", "number_show": 10, ... },
  "response": {
    "number_found": 7756,
    "start": 0,
    "docs": [
      {
        "pid": "Person5767150_2",
        "identifier": "53df6711-0499-bb12-67ec-08429b85dd1a",
        "archive_code": "cod",
        "archive_org": "CODA",
        "archive": "CODA",
        "personname": "Anna E. Knijf",
        "relationtype": "Registered",
        "eventtype": "Registration",
        "eventdate": { "day": "", "month": "", "year": "1927" },
        "eventplace": ["Apeldoorn"],
        "sourcetype": "Population register",
        "url": "https://www.openarchieven.nl/cod:53df6711-.../en"
      }
    ]
  }
}
```

### 2. Get full record details

Once you have an `archive_code` and `identifier` from search results, fetch the
full record:

```
https://api.openarchieven.nl/1.1/records/show.json?archive=ARCHIVE_CODE&identifier=IDENTIFIER&lang=en
```

**Example:**

```bash
curl -s "https://api.openarchieven.nl/1.1/records/show.json?archive=cod&identifier=53df6711-0499-bb12-67ec-08429b85dd1a&lang=en"
```

The show endpoint returns the complete A2A record including:

- All persons mentioned (with names, birth dates, birth places)
- Event details (type, date, place)
- Relationships between persons (father, mother, bride, groom, etc.)
- Source archive details and reference numbers
- Links to scanned images (when available)

**Alternative formats** (same parameters):

- `.xml` -- A2A XML schema
- `.gedcom` -- GEDCOM 5.5.5 format
- `.ttl` -- RDF Turtle
- `.nt` -- N-Triples

### 3. Match a person by name and birth year

For finding birth and death records of a specific person:

```
https://api.openarchieven.nl/1.0/records/match.json?name=NAME&birthyear=YEAR&lang=en
```

This returns Open Archives URIs for matching birth and death records. Useful for
cross-referencing a known person.

### 4. List available archives

To discover valid `archive_code` values:

```bash
curl -s "https://api.openarchieven.nl/1.1/stats/archives.json"
```

Returns all archives with their codes, names, and homepage URLs.

**Common archive codes:**

| Code | Archive |
|------|---------|
| `cod` | CODA (Apeldoorn) |
| `ghn` | Nationaal Archief |
| `nha` | Noord-Hollands Archief |
| `ran` | Regionaal Archief Nijmegen |
| `elo` | Erfgoed Leiden en omstreken |
| `dar` | Drents Archief |
| `bhi` | Brabants Historisch Informatie Centrum |
| `hco` | Collectie Overijssel |
| `gae` | Gemeentearchief Ede |

### 5. Pagination

Use `start` and `number_show` for pagination:

```bash
# Page 1: results 0-99
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&number_show=100&start=0&lang=en"

# Page 2: results 100-199
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&number_show=100&start=100&lang=en"
```

The `number_found` field in the response tells you the total number of results.

## Workflow

### Step 1: Search via API

Use curl or WebFetch to search:

```bash
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=SURNAME&lang=en&number_show=20"
```

Parse the JSON response. Extract `personname`, `eventtype`, `eventdate`,
`eventplace`, `sourcetype`, `archive_code`, `identifier`, and `url` from each
result in `response.docs`.

### Step 2: Filter and identify relevant records

From the search results, identify records matching the target person by:

- Name match
- Date range
- Location
- Event type (birth, marriage, death)
- Relation type (e.g., bride, groom, father, mother)

### Step 3: Fetch full record details

For each relevant record, call the show endpoint:

```bash
curl -s "https://api.openarchieven.nl/1.1/records/show.json?archive=ARCHIVE_CODE&identifier=IDENTIFIER&lang=en"
```

Extract all persons, relationships, and source details from the response.

### Step 4: Present results

Format findings using the output format below.

## Fallback: Playwright browser automation

If the API is unavailable, returns errors, or if you need to use the advanced
search form with filters not available in the API:

### 1. Navigate to search

```
browser_navigate -> https://www.openarchieven.nl/
```

The homepage has a simple search box that searches across all archives.

For advanced search with filters:

```
browser_navigate -> https://www.openarchieven.nl/search-ext.php
```

### 2. Fill the search form

**Simple search** (homepage): just type a name in the search box.

**Advanced search** has these fields:

- First person name
- Second person name (for finding couples)
- Search method: Bevat (contains), Exact, Klinkt als (sounds like)
- Archive location (dropdown -- dozens of Dutch/Belgian archives)
- Occupation (beroep)
- Date range: Vanaf jaartal (from year), Tot jaartal (to year)
- Place
- Source type dropdown (includes "Huwelijk", etc.)
- Role dropdown (Bruid, Bruidegom, etc.)
- Event type (Geboorte, Huwelijk, Overlijden, etc.)

### 3. Read results

Results show a list with:

- Name
- Event type
- Date
- Place
- Source/archive

Click a result to see the full record detail page.

### 4. Record detail page

Shows structured data similar to WieWasWie:

- Person details (name, gender)
- Parents (vader, moeder)
- Event date and place
- Archive source reference
- Link to the original archive

## Key differences from WieWasWie

- Broader coverage (Belgian archives too)
- Has a free JSON API (unlike WieWasWie)
- Results link back to the source archive for scans
- No iframe for details -- results open as full pages

## Output format

```
## Open Archieven Result -- [record type]

**Person:** [name]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Source archive:** [archive name, location]
**Archive ref:** [reference numbers]
**Original record:** [link to source archive if available]
**Open Archieven URL:** [url from API result]

**Confidence:** Tier B -- official archive record via Open Archieven index
```
