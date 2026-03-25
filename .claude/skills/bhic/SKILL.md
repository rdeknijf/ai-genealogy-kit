---
name: bhic
description: |
  Search indexed person records at BHIC (Brabants Historisch Informatie Centrum)
  via the Memorix Genealogy REST API. No browser automation needed — returns
  structured JSON in ~50ms per query. 24.1 million person records covering all
  of North Brabant province: DTB church records (doop/trouw/begraaf), Burgerlijke
  Stand (geboorte/huwelijk/overlijden), bevolkingsregister (population registers),
  militieregisters, notariele akten, gevangenenregisters, and more. Municipalities
  include 's-Hertogenbosch, Eindhoven, Tilburg, Breda, Schijndel, Nuland, Berlicum,
  Helmond, Oss, Veghel, Sint-Oedenrode, Boxtel, Vught, and all other Brabant
  municipalities. Use this skill whenever researching family lines in North Brabant,
  looking up DTB or BS records for Brabant parishes, or verifying Van der Kant/Cant
  records in the Schijndel/Nuland area. Triggers on: "search BHIC", "Brabant
  records", "Schijndel DTB", "Nuland records", "North Brabant archive",
  "Brabants Historisch Informatie Centrum", "/bhic", or any genealogy research
  in the North Brabant province. No login required. Parallelizable — run
  multiple queries simultaneously.
---

# BHIC — Brabants Historisch Informatie Centrum

Search indexed person records from BHIC via the Memorix Genealogy REST API.
Returns structured JSON directly — no browser automation needed.

No login required. No authentication beyond the public API key.

## Coverage

**Province:** North Brabant (all municipalities)

**24.1 million person records** across record types:

- **DTB** (doop-, trouw- en begraafboeken) — church records pre-1811, both
  Roman Catholic and Dutch Reformed. Includes baptisms, marriages, burials.
- **BS** (Burgerlijke Stand) — civil registry post-1811: births, marriages,
  deaths.
- **Bevolkingsregister** — population registers.
- **Militieregisters** — militia/conscription registers 1814-1942.
- **Gevangenenregisters** — prison registers 1834-1929.
- **Notariele akten** — notarial records.
- **Raad van Brabant** — court records 1586-1811.

**Key municipalities for current research:**
Schijndel (Van der Kant/Cant line), Nuland, Berlicum, Vinkel,
's-Hertogenbosch, Den Dungen, Sint-Oedenrode, Veghel.

## API details

- **Base URL:** `https://webservices.memorix.nl/genealogy/`
- **API key:** `24c66d08-da4a-4d60-917f-5942681dcaa1` (public, embedded in page)
- **Platform:** Memorix Genealogy by Picturae (AngularJS frontend, REST+Solr backend)
- **Response format:** JSON
- **Response time:** ~30-80ms per query
- **Max rows per page:** 500 (use 100-250 for typical queries)
- **No rate limiting observed** (but be reasonable)
- **Tenant:** `bhic`

## Workflow

### 1. Simple person search

Search for persons by name using the `q` parameter.

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1&q=van+der+Kant&rows=25'
```

**Response structure:**

```json
{
  "metadata": {
    "pagination": { "total": 1317, "rows": 25, "currentPage": 1, "pages": 53 }
  },
  "person": [
    {
      "id": "UUID",
      "deed_id": "UUID",
      "register_id": "UUID",
      "entity_type": "dtb_d_vader",
      "metadata": {
        "voornaam": "Henricus",
        "achternaam": "Cant",
        "geslachtsnaam": "Cant",
        "tussenvoegsel": "van der",
        "type_title": "vader",
        "deed_type_title": "DTB doopakte",
        "register_type_title": "doop-, trouw- en begraafboeken",
        "datum": "1725-03-12",
        "register_naam": "Rooms-Katholiek doopboek 1719-1725",
        "register_gemeente": "Schijndel",
        "plaats": "Schijndel",
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
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1&q=*:*&fq=search_t_geslachtsnaam:%22Cant%22+AND+search_t_voornaam:%22Petrus%22&rows=25'
```

**Available search fields for fq:**

| Field | Description | Example |
|-------|-------------|---------|
| `search_t_geslachtsnaam` | Surname | `"Cant"` or `"Kant"` |
| `search_t_voornaam` | First name | `"Petrus"` |
| `search_t_tussenvoegsel` | Prefix | `"van der"` |
| `search_t_patroniem` | Patronymic | `"Gerardi"` |

**Important for Van der Kant research:** The surname changed over time:
- Pre-1811: usually `van der Cant` (with "C")
- Post-1811: usually `van der Kant` (with "K")
- Search for BOTH spellings to get complete coverage

### 3. Filter by record type and municipality

Combine `q` with `fq` for facet filtering.

**Filter by deed type (DTB baptisms in Schijndel):**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1&q=van+der+Cant&fq=search_s_deed_type_title:%22DTB+doopakte%22+AND+search_s_register_gemeente:%22Schijndel%22&rows=25'
```

**Filter by municipality only:**

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1&q=van+der+Kant&fq=search_s_register_gemeente:%22Nuland%22&rows=25'
```

**Available deed type values:**

| Deed type | Description |
|-----------|-------------|
| `DTB doopakte` | Baptism record |
| `DTB trouwakte` | Marriage record (church) |
| `DTB begraafakte` | Burial record |
| `BS geboorteakte` | Civil birth certificate |
| `BS huwelijksakte` | Civil marriage certificate |
| `BS overlijdensakte` | Civil death certificate |
| `registratie bevolkingsregister` | Population register entry |
| `registratie militieregister` | Militia register entry |

**Available facet filter fields:**

| Field | Description |
|-------|-------------|
| `search_s_deed_type_title` | Record type (see table above) |
| `search_s_register_type_title` | Register category |
| `search_s_register_gemeente` | Municipality |

### 4. Get deed detail (all persons in one record)

```bash
curl -s 'https://webservices.memorix.nl/genealogy/deed/{deed_id}?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1'
```

Returns all persons mentioned in the deed (dopeling, vader, moeder, getuigen)
plus the `diversen` field with transcription notes.

### 5. Get register detail (scan images)

```bash
curl -s 'https://webservices.memorix.nl/genealogy/register/{register_id}?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1'
```

Returns register metadata and an `asset` array with scan images:

```json
{
  "asset": [
    {
      "uuid": "UUID",
      "filename": "1455_018_001.jp2",
      "thumb.small": "https://images.memorix.nl/bhic/thumb/100x100/UUID.jpg",
      "thumb.large": "https://images.memorix.nl/bhic/thumb/640x480/UUID.jpg",
      "download": "https://images.memorix.nl/bhic/download/default/UUID.jpg"
    }
  ]
}
```

**Scan URL pattern:** `https://images.memorix.nl/bhic/thumb/640x480/{asset_uuid}.jpg`

### 6. Pagination

Use `page` parameter (1-based) to paginate through results:

```bash
curl -s 'https://webservices.memorix.nl/genealogy/person?apiKey=24c66d08-da4a-4d60-917f-5942681dcaa1&q=van+der+Kant&rows=100&page=2'
```

### 7. Construct BHIC web link for a person

To generate a clickable link to the BHIC website for a specific record:

```
https://www.bhic.nl/memorix/genealogy/search/persons/detail/{person_id}
```

For a deed:

```
https://www.bhic.nl/memorix/genealogy/search/deeds/detail/{deed_id}
```

## Entity types (person roles)

| entity_type | Role in record |
|-------------|----------------|
| `dtb_d_dopeling` | Baptized child |
| `dtb_d_vader` | Father (in baptism) |
| `dtb_d_moeder` | Mother (in baptism) |
| `dtb_d_getuige` | Witness (in baptism) |
| `dtb_t_bruidegom` | Groom |
| `dtb_t_bruid` | Bride |
| `dtb_b_overledene` | Deceased (in burial) |
| `bs_g_kind` | Child (civil birth) |
| `bs_g_vader` | Father (civil birth) |
| `bs_g_moeder` | Mother (civil birth) |
| `bs_h_bruidegom` | Groom (civil marriage) |
| `bs_h_bruid` | Bride (civil marriage) |
| `bs_o_overledene` | Deceased (civil death) |
| `bs_o_vader` | Father of deceased |
| `bs_o_moeder` | Mother of deceased |
| `br_a_geregistreerde` | Registered person (population register) |

## Output format

When reporting findings from BHIC:

```
**Source:** BHIC Memorix — [deed_type_title], [register_naam], [register_gemeente]
**Archive ref:** BHIC archief [archiefnummer], inv [inventarisnummer]
**Record:** [person names, dates, places from metadata]
**Scan:** [image URL if available]
**Confidence:** Tier B — official indexed record from BHIC
```

## Limitations

- **Scans:** Available for most DTB and some BS records. Check `has_assets`
  field — value `"deed"` means scan of the specific page, `"register"` means
  scan of the full register (browse to find the right page).
- **Catholic vs Reformed:** Schijndel had both RK (Rooms-Katholiek) and NG
  (Nederduits Gereformeerd) churches. The Van der Kant/Cant family was
  primarily Catholic — search both but focus on RK records.
- **Spelling variation:** Pre-1811 records use Latin forms and Dutch variants
  interchangeably: Cant/Kant, Gerardus/Gerit/Gerrit, Henricus/Hendrik,
  Petrus/Peter, Martinus/Marten. Always search both.
- **No full-text search of deed content:** The `diversen` field (deed notes)
  is not searchable via the person endpoint. You must retrieve the deed
  detail to see transcription notes.
- **Rows=0 returns empty:** Always request at least rows=1.
