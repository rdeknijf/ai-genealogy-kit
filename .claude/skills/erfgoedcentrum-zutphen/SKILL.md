---
name: erfgoedcentrum-zutphen-optimized
description: |
  Search civil records, church records, population registers, and archives at
  Erfgoedcentrum Zutphen (erfgoedcentrumzutphen.nl) via the Memorix Genealogy
  REST API. No browser automation needed — returns structured JSON in ~50ms per
  query. Covers Brummen, Lochem, and Zutphen — 815,000+ historical documents
  with 1.1 million personal references. Use this skill whenever researching
  family lines from Zutphen (Peters, Remmers, Heezen families), looking up
  birth/marriage/death records from Zutphen, or searching population registers
  for the Zutphen area. Triggers on: "search Zutphen archive", "look up in
  Zutphen", "check Zutphen records", "Peters Zutphen", "Remmers Zutphen",
  "/erfgoedcentrum-zutphen", or any genealogy research in the
  Zutphen/Brummen/Lochem area. No login required. Parallelizable — run
  multiple queries simultaneously.
---

# Erfgoedcentrum Zutphen — Zutphen Region Archive

Search 815,000+ historical documents with 1.1 million+ personal references
covering Brummen, Lochem, and Zutphen via the Memorix Genealogy REST API.
Returns structured JSON directly — no browser automation needed.

No login required. No authentication beyond the public API key.

## Key family lines in this archive

- **Peters** — Jakobus Peters (I214), born 1872 Zutphen, and ancestors
- **Remmers** — Frederika Remmers (I500050), born 1825 Zutphen
- **Heezen** — Berendina Johanna Heezen (I500048), wife of Jakobus Peters
- **Harmanus Gillius Peters** and **Johannes Frederik Peters** — both from Zutphen

## API details

- **Base URL:** `https://webservices.memorix.nl/genealogy/`
- **API key:** `509544d0-1c67-11e4-9016-c788dee409dc` (public, embedded in page)
- **Platform:** Memorix Genealogy by Picturae (AngularJS frontend, REST+Solr backend)
- **Response format:** JSON
- **Response time:** ~30-50ms per query
- **Max rows per page:** 500 (use 100-250 for typical queries)
- **No rate limiting observed** (but be reasonable)

## Workflow

### 1. Simple person search

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=Peters&rows=25'
```

**Response structure:**

```json
{
  "metadata": {
    "pagination": { "total": 5058, "rows": 25, "currentPage": 1, "pages": 203 }
  },
  "person": [
    {
      "id": "UUID",
      "deed_id": "UUID",
      "register_id": "UUID",
      "metadata": {
        "voornaam": "Jakobus",
        "achternaam": "Peters",
        "geslachtsnaam": "Peters",
        "type_title": "kind",
        "plaats": "Zutphen",
        "datum": "1872-05-15",
        "deed_type_title": "BS Geboorte",
        "register_naam": "Geboorteregister 1872",
        "register_gemeente": "Zutphen",
        "inventarisnummer": "...",
        "person_display_name": "Jakobus Peters",
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
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=*:*&fq=search_t_geslachtsnaam:%22Peters%22+AND+search_t_voornaam:%22Jakobus%22&rows=25'
```

**Available search fields for fq:**

| Field | Description | Example |
|-------|-------------|---------|
| `search_t_geslachtsnaam` | Surname | `"Peters"` |
| `search_t_voornaam` | First name | `"Jakobus"` |
| `search_t_tussenvoegsel` | Prefix | `"de"` |
| `search_t_patroniem` | Patronymic | `"jansz"` |

### 3. Filter by record type and municipality

**Filter by deed type:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=Peters&fq=search_s_deed_type_title:%22BS+Geboorte%22&rows=25'
```

**Filter by municipality:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=Peters&fq=search_s_register_gemeente:%22Zutphen%22&rows=25'
```

**Combine multiple filters (AND):**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=Peters&fq=search_s_deed_type_title:%22BS+Geboorte%22+AND+search_s_register_gemeente:%22Zutphen%22&rows=25'
```

**Available facet filter fields:**

| Field | Description | Example values |
|-------|-------------|---------------|
| `search_s_deed_type_title` | Record type | `"BS Geboorte"`, `"BS Huwelijk"`, `"BS Overlijden"`, `"DTB Dopen"`, `"DTB Trouwen"`, `"DTB Begraven"`, `"Notarieel register akte"`, `"Bevolkingsregister"`, `"Weeskamer inschrijvingen"` |
| `search_s_register_gemeente` | Municipality | `"Zutphen"`, `"Brummen"`, `"Lochem"` |
| `search_s_plaats` | Place | Same as gemeente plus sub-locations |
| `search_s_type_title` | Role in record | `"overledene"`, `"vader"`, `"moeder"`, `"kind"`, `"bruid"`, `"bruidegom"`, `"getuige"`, `"notarieel geregistreerde"`, `"Weeskamer geregistreerde"` |

### 4. Pagination and sorting

**Pagination:**

```bash
&page=2&rows=100
```

**Sorting:**

```bash
&sort=order_i_datum+desc    # newest first
&sort=order_i_datum+asc     # oldest first
&sort=order_s_geslachtsnaam+asc  # alphabetical by surname
```

### 5. Get deed (record) details

```bash
curl -s 'https://webservices.memorix.nl/genealogy/deed/{deed_id}?apiKey=509544d0-1c67-11e4-9016-c788dee409dc'
```

Response includes metadata (gemeente, type, akte number, register name, archive/inventory numbers) and `asset[]` with scan image URLs.

### 6. Get all persons in a deed

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=509544d0-1c67-11e4-9016-c788dee409dc&q=*:*&fq=deed_id:%22{deed_id}%22&rows=25'
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
https://erfgoedcentrumzutphen.nl/onderzoeken/genealogie#/persons?ss={"q":"Peters"}
```

**Single deed:**

```
https://erfgoedcentrumzutphen.nl/onderzoeken/genealogie#/deeds/{deed_id}?person={person_id}
```

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /person` | Search persons |
| `GET /person/{id}` | Get single person |
| `GET /deed/{id}` | Get deed (record) with assets |
| `GET /register/{id}` | Get register details |
| `GET /config` | Get field/facet configuration |

## Alternative access

Zutphen records are also partially indexed in:

- **OpenArchieven** — search for "Zutphen" in the archive filter
- **WieWasWie** — search with Plaats = "Zutphen"
- **Gelders Archief** — holds the Zutphen civil registry (toegangsnr 0207A)

## Fallback (browser automation)

If the API is unavailable or the API key has been rotated, fall back to
Playwright browser automation at `https://erfgoedcentrumzutphen.nl/onderzoeken/genealogie`.

To find the current API key:

```bash
curl -sL 'https://erfgoedcentrumzutphen.nl/onderzoeken/genealogie' | grep -oP 'data-api-key="\K[^"]+'
```

## Output format

```
## Erfgoedcentrum Zutphen Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Archiefnummer [nr], Inventarisnummer [nr], Aktenummer [nr]
**Scan available:** Yes/No
**Web link:** [website URL for the deed]

**Confidence:** Tier B — official archive record from Erfgoedcentrum Zutphen
```
