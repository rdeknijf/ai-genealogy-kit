---
name: erfgoed-leiden-optimized
description: |
  Search indexed person records and scanned documents at Erfgoed Leiden en
  Omstreken (erfgoedleiden.nl) via direct Memorix Genealogy REST API calls.
  No browser automation needed — returns structured JSON in ~50ms per query.
  Covers the Leiden region of South Holland province including: Hillegom,
  Katwijk, Kaag en Braassem, Leiden, Leiderdorp, Lisse, Nieuwkoop, Noordwijk,
  Oegstgeest, Teylingen, Zoeterwoude. Also has records for Ter Aar, Zevenhoven,
  Nieuwveen, Woubrugge, Sassenheim, Rijnsburg, Leimuiden, Hoogmade, Alkemade,
  and Achttienhoven. Does NOT cover Alphen aan den Rijn. 398+ Knijf person
  records found here, mainly in Ter Aar (179) and Nieuwkoop (67). Record types
  include DTB (Dopen/Trouwen/Begraven), BS (Geboorte/Huwelijk/Overlijden),
  Bevolkingsregister, Notariele akten, and more. Triggers on: "search Erfgoed
  Leiden", "look up in Leiden archive", "check Leiden records", "Ter Aar
  records", "Nieuwkoop records", "/erfgoed-leiden", or any genealogy research
  in the Leiden/South Holland region. No login required. Parallelizable — run
  multiple queries simultaneously.
---

# Erfgoed Leiden en Omstreken — Leiden Region Archive

Search indexed person records and scanned documents from Erfgoed Leiden en
Omstreken via the Memorix Genealogy REST API. Returns structured JSON directly
— no browser automation needed.

No login required. No authentication beyond the public API key.

## Coverage

**Municipalities with Knijf records:** Ter Aar (179), Leiden (75), Nieuwkoop
(67), Hillegom (29), Zevenhoven (14), Lisse (6), Nieuwveen (6), Woubrugge (6),
Leiderdorp (3), Leimuiden (3), Noordwijk (2), Rijnsburg (2), Sassenheim (2),
Achttienhoven (1), Alkemade (1), Hoogmade (1), Voorhout (1).

**NOT covered:** Alphen aan den Rijn (separate archive), Woerden (Het Utrechts
Archief / RHC Rijnstreek), Gouda (Streekarchief Midden-Holland).

## API details

- **Base URL:** `https://webservices.memorix.nl/genealogy/`
- **API key:** `3288aeb2-c2a5-40b4-941b-f9beb2089511` (public, embedded in page)
- **Platform:** Memorix Genealogy by Picturae (AngularJS frontend, REST+Solr backend)
- **Response format:** JSON
- **Response time:** ~30-50ms per query
- **Max rows per page:** 500 (tested; use 100-250 for typical queries)
- **No rate limiting observed** (but be reasonable)

## Workflow

### 1. Simple person search

Search for persons by name using the `q` parameter.

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=knijf&rows=25'
```

**Response structure:**

```json
{
  "metadata": {
    "pagination": { "total": 398, "rows": 25, "currentPage": 1, "pages": 16 }
  },
  "person": [
    {
      "id": "UUID",
      "deed_id": "UUID",
      "register_id": "UUID",
      "metadata": {
        "voornaam": "Cornelia",
        "achternaam": "Knijf",
        "geslachtsnaam": "Knijf",
        "tussenvoegsel": "",
        "type_title": "overledene",
        "beroep": "zonder",
        "leeftijd": "60 jaar",
        "plaats": "Zevenhoven",
        "plaats_wonen": "Zevenhoven",
        "plaats_geboorte": "Breukelen",
        "datum_overlijden": "18710307",
        "deed_type_title": "BS Overlijden",
        "register_naam": "Overlijdensakten 1863-1872",
        "register_gemeente": "Zevenhoven",
        "inventarisnummer": "61",
        "register_archiefnummer": "132.1.06",
        "person_display_name": "Cornelia Knijf",
        "datum": 18710307,
        "has_assets": "deed"
      }
    }
  ]
}
```

### 2. Advanced person search (by specific fields)

Use `fq` (filter query) with Solr-style field:value syntax. Values with spaces
must be URL-encoded and quoted.

**Search by surname and first name:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=*:*&fq=search_t_geslachtsnaam:%22knijf%22+AND+search_t_voornaam:%22cornelia%22&rows=25'
```

**Available search fields for fq:**

| Field | Description | Example |
|-------|-------------|---------|
| `search_t_geslachtsnaam` | Surname | `"knijf"` |
| `search_t_voornaam` | First name | `"cornelia"` |
| `search_t_tussenvoegsel` | Prefix | `"de"` |
| `search_t_patroniem` | Patronymic | `"jansz"` |

### 3. Filter by record type and municipality

Combine `q` with `fq` for facet filtering.

**Filter by deed type:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=knijf&fq=search_s_deed_type_title:%22BS+Geboorte%22&rows=25'
```

**Filter by municipality:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=knijf&fq=search_s_register_gemeente:%22Ter+Aar%22&rows=25'
```

**Combine multiple filters (AND):**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=knijf&fq=search_s_deed_type_title:%22BS+Geboorte%22+AND+search_s_register_gemeente:%22Ter+Aar%22&rows=25'
```

**Available facet filter fields:**

| Field | Description | Example values |
|-------|-------------|---------------|
| `search_s_deed_type_title` | Record type | `"BS Geboorte"`, `"BS Huwelijk"`, `"BS Overlijden"`, `"DTB Dopen"`, `"DTB Trouwen"`, `"DTB Begraven"`, `"Notariele akten"`, `"Bevolkingsregister"` |
| `search_s_register_gemeente` | Municipality | `"Ter Aar"`, `"Leiden"`, `"Nieuwkoop"`, `"Zevenhoven"`, `"Hillegom"` |
| `search_s_plaats` | Place | Same as gemeente plus sub-locations |
| `search_s_type_title` | Role in record | `"overledene"`, `"vader"`, `"moeder"`, `"kind"`, `"bruid"`, `"bruidegom"`, `"getuige"` |

### 4. Pagination and sorting

**Pagination:**

```bash
&page=2&rows=100
```

**Sorting (use order_ prefixed fields):**

```bash
&sort=order_i_datum+desc    # newest first
&sort=order_i_datum+asc     # oldest first
&sort=order_s_geslachtsnaam+asc  # alphabetical by surname
```

### 5. Get deed (record) details

Fetch the full record by deed ID. Includes scan/asset URLs.

```bash
curl -s 'https://webservices.memorix.nl/genealogy/deed/{deed_id}?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511'
```

**Response includes:**

- `metadata.gemeente` — municipality
- `metadata.type_title` — record type (BS Overlijden, DTB Dopen, etc.)
- `metadata.nummer` — akte number
- `metadata.naam` — register name
- `metadata.diversen` — additional details (remarks, corrections, archive link)
- `metadata.archiefnummer` — archive number
- `metadata.inventarisnummer` — inventory number
- `asset[]` — array of scan images with IIIF URLs

### 6. Get all persons in a deed

To see everyone mentioned in a record (overledene, vader, moeder, getuigen):

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=3288aeb2-c2a5-40b4-941b-f9beb2089511&q=*:*&fq=deed_id:%22{deed_id}%22&rows=25'
```

### 7. Access scan images

Deed details include `asset[]` with IIIF Image API URLs:

| Size | URL pattern |
|------|-------------|
| Thumbnail (100px) | `{iiifUrl}full/!100,100/0/default.jpg` |
| Medium (250px) | `{iiifUrl}full/!250,250/0/default.jpg` |
| Large (640px) | `{iiifUrl}full/!640,480/0/default.jpg` |
| Full size | `{iiifUrl}full/max/0/default.jpg` |
| Download | `asset[].download` field |

The `iiifUrl` is in `asset[].iiifUrl`, e.g.:
`https://elo.memorix.io/resources/iiif/3/{uuid}/`

### 8. Build website URL for user reference

To link users to the record on the website:

**Search results:**

```
https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen/persons?ss={"q":"knijf"}
```

**Single deed (full page view):**

```
https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen/deeds/{deed_id}?person={person_id}
```

## Complete query parameter reference

| Parameter | Description | Example |
|-----------|-------------|---------|
| `apiKey` | API key (required) | `3288aeb2-c2a5-40b4-941b-f9beb2089511` |
| `q` | Search query | `knijf`, `*:*` (all) |
| `fq` | Filter query (Solr syntax) | `search_s_deed_type_title:"BS Geboorte"` |
| `rows` | Results per page (max ~500) | `25`, `100`, `250` |
| `page` | Page number | `1`, `2` |
| `sort` | Sort field and direction | `order_i_datum desc` |

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /person` | Search persons |
| `GET /person/{id}` | Get single person |
| `GET /deed/{id}` | Get deed (record) with assets |
| `GET /register/{id}` | Get register details |
| `GET /config` | Get field/facet configuration |

## Fallback (browser automation)

If the API is unavailable, returns errors, or the API key has been rotated,
fall back to Playwright browser automation. See the original `erfgoed-leiden`
skill for the full browser workflow.

To find the current API key, fetch the search page HTML and extract
`data-api-key` from the `#pic-genealogy` element:

```bash
curl -sL 'https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen/persons' | grep -oP 'data-api-key="\K[^"]+'
```

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Erfgoed Leiden** | Leiden region, Ter Aar, Nieuwkoop, Zevenhoven records |
| Het Utrechts Archief | Utrecht province (Woerden, Utrecht city, Amersfoort) |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik, Montfoort area |
| Gelders Archief | Gelderland province (Ede, Barneveld, Apeldoorn) |
| WieWasWie | National coverage, structured person lookups |
| OpenArchieven | Wide net across all Dutch/Belgian archives |

## Output format

```
## Erfgoed Leiden Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Archiefnummer [nr], Inventarisnummer [nr], Aktenummer [nr]
**Scan available:** Yes/No
**Scan URL:** [IIIF download URL if available]
**Web link:** [website URL for the deed]

**Confidence:** Tier B — official archive record from Erfgoed Leiden
```
