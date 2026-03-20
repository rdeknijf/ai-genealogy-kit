---
name: streekarchief-midden-holland-optimized
description: |
  Search indexed person records at Streekarchief Midden-Holland (samh.nl)
  via the Memorix Genealogy REST API. No browser automation needed — returns
  structured JSON in ~50ms per query. Based in Gouda, covers municipalities:
  Gouda, Haastrecht, Schoonhoven, Waddinxveen, Noord-Waddinxveen,
  Moerkapelle, Moordrecht, Ammerstol, Broek, Vlist, and surrounding areas
  in the Midden-Holland region of South Holland. 3M+ person records with
  DTB (doop/trouw/begraven), BS (geboorte/huwelijk/overlijden), and
  Inschrijvingaktes. 36 Knijf results found, including Gijsbert de Knijf
  records in Gouda and van der Knijf in Waddinxveen. Scans available for
  most records. Triggers on: "search Gouda archive", "Streekarchief
  Midden-Holland", "SAMH", "Haastrecht records", "Schoonhoven records",
  "/streekarchief-midden-holland", or any genealogy research in the
  Gouda/Midden-Holland area. No login required. Parallelizable — run
  multiple queries simultaneously.
---

# Streekarchief Midden-Holland — Gouda Region Archive

Search 3M+ indexed person records from the regional archive of Midden-Holland
via the Memorix Genealogy REST API. Returns structured JSON directly — no
browser automation needed.

No login required. No authentication beyond the public API key.

## Coverage

3,061,801 person records. Municipalities: Gouda, Haastrecht, Schoonhoven,
Waddinxveen, Noord-Waddinxveen, Moerkapelle, Moordrecht, Ammerstol,
Broek c.a., Vlist, and surrounding areas.

**Knijf records:** 36 results — de Knijf in Gouda/Haastrecht, van der
Knijf in Noord-Waddinxveen/Broek/Moerkapelle, Knijf in Gouda/Schoonhoven/
Waddinxveen/Vlist.

## API details

- **Base URL:** `https://webservices.memorix.nl/genealogy/`
- **API key:** `99a56f3a-da0b-11e9-9805-d77cd3614b0e` (public, embedded in page)
- **Platform:** Memorix Genealogy by Picturae (AngularJS frontend, REST+Solr backend)
- **Response format:** JSON
- **Response time:** ~30-50ms per query
- **Max rows per page:** 500 (use 100-250 for typical queries)
- **No rate limiting observed** (but be reasonable)

## Workflow

### 1. Simple person search

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e&q=Knijf&rows=25'
```

**Response structure:**

```json
{
  "metadata": {
    "pagination": { "total": 36, "rows": 25, "currentPage": 1, "pages": 2 }
  },
  "person": [
    {
      "id": "UUID",
      "deed_id": "UUID",
      "register_id": "UUID",
      "metadata": {
        "voornaam": "Gijsbert",
        "achternaam": "Knijf",
        "geslachtsnaam": "Knijf",
        "tussenvoegsel": "de",
        "type_title": "Vader",
        "plaats": "Gouda",
        "datum": "1873-11-13",
        "deed_type_title": "Overlijdensakte",
        "register_naam": "...",
        "register_gemeente": "Gouda",
        "person_display_name": "Gijsbert de Knijf",
        "has_assets": "deed"
      }
    }
  ]
}
```

### 2. Advanced person search (by specific fields)

Use `fq` (filter query) with Solr-style field:value syntax.

**Search by surname and first name:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e&q=*:*&fq=search_t_geslachtsnaam:%22Knijf%22+AND+search_t_voornaam:%22Gijsbert%22&rows=25'
```

**Available search fields for fq:**

| Field | Description | Example |
|-------|-------------|---------|
| `search_t_geslachtsnaam` | Surname | `"Knijf"` |
| `search_t_voornaam` | First name | `"Gijsbert"` |
| `search_t_tussenvoegsel` | Prefix | `"de"` |
| `search_t_patroniem` | Patronymic | `"jansz"` |

### 3. Filter by record type and municipality

**Filter by deed type:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e&q=Knijf&fq=search_s_deed_type_title:%22Geboorteakte%22&rows=25'
```

**Filter by municipality:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e&q=Knijf&fq=search_s_register_gemeente:%22Gouda%22&rows=25'
```

**Available facet filter fields:**

| Field | Description | Example values |
|-------|-------------|---------------|
| `search_s_deed_type_title` | Record type | `"Doopakte"`, `"Geboorteakte"`, `"Huwelijksakte"`, `"Overlijdensakte"`, `"Inschrijvingaktes"` |
| `search_s_register_gemeente` | Municipality | `"Gouda"`, `"Haastrecht"`, `"Schoonhoven"`, `"Waddinxveen"`, `"Moordrecht"` |
| `search_s_plaats` | Place | Same as gemeente plus sub-locations |
| `search_s_type_title` | Role in record | `"Vader"`, `"Moeder"`, `"Overledene"`, `"Kind"`, `"Bruid"`, `"Bruidegom"`, `"Getuige"` |

### 4. Pagination and sorting

```bash
&page=2&rows=100
&sort=order_i_datum+desc    # newest first
&sort=order_i_datum+asc     # oldest first
&sort=order_s_geslachtsnaam+asc  # alphabetical by surname
```

### 5. Get deed (record) details

```bash
curl -s 'https://webservices.memorix.nl/genealogy/deed/{deed_id}?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e'
```

Response includes metadata and `asset[]` with scan image URLs (IIIF).

### 6. Get all persons in a deed

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=99a56f3a-da0b-11e9-9805-d77cd3614b0e&q=*:*&fq=deed_id:%22{deed_id}%22&rows=25'
```

### 7. Access scan images

Deed details include `asset[]` with IIIF Image API URLs:

| Size | URL pattern |
|------|-------------|
| Thumbnail | `{iiifUrl}full/!100,100/0/default.jpg` |
| Medium | `{iiifUrl}full/!250,250/0/default.jpg` |
| Large | `{iiifUrl}full/!640,480/0/default.jpg` |
| Full size | `{iiifUrl}full/max/0/default.jpg` |

### 8. Build website URL for user reference

**Search results:**

```
https://samh.nl/bronnen/genealogie/persons?ss={"q":"Knijf"}
```

**Single deed:**

```
https://samh.nl/bronnen/genealogie/deeds/{deed_id}?person={person_id}
```

## Other collections

The archive also has (browser-only):

- **Archieven** — archive inventories
- **Bouwtekeningen** — building permits
- **Beeldbank** — image bank
- **Kranten** — newspapers (at kranten.samh.nl)
- **Bibliotheek** — library catalog

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /person` | Search persons |
| `GET /person/{id}` | Get single person |
| `GET /deed/{id}` | Get deed (record) with assets |
| `GET /register/{id}` | Get register details |
| `GET /config` | Get field/facet configuration |

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Streekarchief Midden-Holland** | Gouda, Haastrecht, Schoonhoven, Waddinxveen, Moerkapelle area |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik, Montfoort, Oudewater |
| Erfgoed Leiden | Leiden, Ter Aar, Nieuwkoop, Hillegom |
| Gemeentearchief Alphen | Alphen aan den Rijn, Aarlanderveen, Benthuizen |
| Het Utrechts Archief | Utrecht province (Woerden overlaps with RHC Rijnstreek) |

## Fallback (browser automation)

If the API is unavailable or the API key has been rotated, fall back to
Playwright at `https://samh.nl/bronnen/genealogie/persons`.

To find the current API key:

```bash
curl -sL 'https://www.samh.nl/bronnen/genealogie' | grep -oP 'data-api-key="\K[^"]+'
```

## Output format

```
## Streekarchief Midden-Holland Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [reference]
**Scan available:** Yes/No
**Web link:** [website URL]

**Confidence:** Tier B — official archive record from Streekarchief Midden-Holland
```
