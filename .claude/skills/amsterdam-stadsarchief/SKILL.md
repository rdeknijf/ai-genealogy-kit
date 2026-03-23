---
name: amsterdam-stadsarchief
description: |
  Search the Amsterdam Stadsarchief (archief.amsterdam) person index via the
  Memorix JSON API. Contains DTB records (pre-1811 baptisms, burials, marriages),
  bevolkingsregisters (population registers 1851-1893), archiefkaarten (person
  cards 1893-1939), persoonskaarten (1939-1994), gezinskaarten (family cards),
  militieregisters, notarial records, WWII records, and more. Does NOT contain
  Burgerlijke Stand (civil births/marriages/deaths 1811+) — those are unindexed
  scans only. No login or browser needed. Use this skill when searching for:
  Amsterdam DTB records, Amsterdam population registers, bevolkingsregister,
  archiefkaarten, persoonskaarten, Amsterdam pre-1811 records, or any Amsterdam
  Stadsarchief collection. Triggers on: "search amsterdam stadsarchief",
  "archief amsterdam", "amsterdam bevolkingsregister", "amsterdam DTB",
  "archiefkaart", "persoonskaart", "/amsterdam-stadsarchief".
---

# Amsterdam Stadsarchief — Memorix Person Index API

Search the Amsterdam Stadsarchief person index via JSON API. No browser needed.

**IMPORTANT:** This index does NOT contain Burgerlijke Stand records (births,
marriages, deaths 1811+). Those exist only as unindexed scans. For BS records,
check WieWasWie or OpenArchieven first — Amsterdam BS is poorly indexed everywhere.

## API Details

- **Base URL:** `https://webservices.memorix.nl/genealogy/`
- **API Key:** `eb37e65a-eb47-11e9-b95c-60f81db16c0e`
- **Auth:** None required. CORS open.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /person` | Search persons |
| `GET /person/<uuid>` | Person detail |
| `GET /deed/<uuid>` | Deed/record detail (with scan images) |
| `GET /register/<uuid>` | Register detail (with scan images for archiefkaarten) |

## Step 1: Search for persons

```bash
curl -s "https://webservices.memorix.nl/genealogy/person?apiKey=eb37e65a-eb47-11e9-b95c-60f81db16c0e&q=SURNAME&rows=25&page=1"
```

### Parameters

| Param | Description | Example |
|---|---|---|
| `q` | Full-text search | `Lebbing`, `Jan+Uijtenhooren` |
| `rows` | Results per page | `25` |
| `page` | Page number (1-indexed) | `1` |
| `fq` | Filter query (Solr syntax) | See below |
| `sort` | Sort field + direction | `order_i_datum asc` |

### Filter (fq) values

Filter by collection:

```bash
# DTB Dopen (baptisms, pre-1811)
fq=search_s_register_type_title:"DTB+Dopen"

# Bevolkingsregister 1874-1893
fq=search_s_register_type_title:"Bevolkingsregister+1874-1893"

# Archiefkaarten (person cards 1893-1939)
fq=search_s_register_type_title:"Archiefkaarten"

# Persoonskaarten (1939-1994)
fq=search_s_register_type_title:"Persoonskaarten"

# Gezinskaarten (family cards 1893-1939)
fq=search_s_register_type_title:"Gezinskaarten"

# Militieregisters
fq=search_s_register_type_title:"Militieregisters"

# WWII police reports
fq=search_s_register_type_title:"Politierapporten+'40-'45"

# Multiple: use OR
fq=search_s_register_type_title:"DTB+Dopen"+OR+search_s_register_type_title:"DTB+Begraven"
```

Filter by person role:

```bash
fq=search_s_type_title:"Kind"        # Child (in baptism)
fq=search_s_type_title:"Vader"       # Father
fq=search_s_type_title:"Bruidegom"   # Groom
fq=search_s_type_title:"Bruid"       # Bride
```

### Available collections

| Collection | Period | Notes |
|---|---|---|
| DTB Dopen | pre-1811 | Church baptisms |
| DTB Begraven | pre-1811 | Church burials |
| Begraafregisters | pre-1811 | Cemetery burials |
| Ondertrouwregister | 1565-1811 | Pre-marriage registration |
| Bevolkingsregister 1851-1853 | 1851-1853 | Population register |
| Bevolkingsregister 1853-1863 | 1853-1863 | Population register |
| Bevolkingsregister 1864-1874 | 1864-1874 | Population register |
| Bevolkingsregister 1874-1893 | 1874-1893 | With addresses |
| Archiefkaarten | 1893-1939 | Person cards |
| Persoonskaarten | 1939-1994 | Person cards |
| Gezinskaarten | 1893-1939 | Family cards |
| Militieregisters | 1828-1940 | Military service |
| Notariële archieven | 1578-1915 | Notarial records |

## Step 2: Parse results

Response JSON has `person` array. Each person:

```json
{
  "id": "uuid",
  "deed_id": "uuid",
  "register_id": "uuid",
  "metadata": {
    "voornaam": "Jan",
    "geslachtsnaam": "Lebbing",
    "tussenvoegsel": "",
    "datum": "1870-01-01",
    "type_title": "Geregistreerde",
    "deed_type_title": "Registratie",
    "register_type_title": "Bevolkingsregister 1874-1893",
    "diversen": "<html with archive URL>",
    "plaats": "Amsterdam"
  }
}
```

## Step 3: Get scans

For most records, fetch the deed:

```bash
curl -s "https://webservices.memorix.nl/genealogy/deed/DEED_UUID?apiKey=eb37e65a-eb47-11e9-b95c-60f81db16c0e"
```

Scan URLs in `asset[].thumb.large`:
`https://images.memorix.nl/ams/thumb/640x480/<uuid>.jpg`

Full size: `asset[].download`:
`https://images.memorix.nl/ams/download/fullsize/<uuid>.jpg`

For **Archiefkaarten**, scans are at register level — use `register_id` instead.

## Example searches

```bash
# All Lebbing in DTB Dopen
curl -s "https://webservices.memorix.nl/genealogy/person?apiKey=eb37e65a-eb47-11e9-b95c-60f81db16c0e&q=Lebbing&fq=search_s_register_type_title:%22DTB+Dopen%22&rows=25&page=1&sort=order_i_datum+asc"

# Ferron in bevolkingsregister 1874-1893
curl -s "https://webservices.memorix.nl/genealogy/person?apiKey=eb37e65a-eb47-11e9-b95c-60f81db16c0e&q=Ferron&fq=search_s_register_type_title:%22Bevolkingsregister+1874-1893%22&rows=25&page=1"

# Kemmann archiefkaarten
curl -s "https://webservices.memorix.nl/genealogy/person?apiKey=eb37e65a-eb47-11e9-b95c-60f81db16c0e&q=Kemmann&fq=search_s_register_type_title:%22Archiefkaarten%22&rows=25&page=1"
```

## Web viewer URL

From the `diversen` field:
`https://archief.amsterdam/archief/<archiefnummer>/<inventarisnummer>`

## Output format

```
## Amsterdam Stadsarchief Result

**Person:** [name]
**Collection:** [register_type_title]
**Date:** [datum]
**Role:** [type_title]

**Archive:** Stadsarchief Amsterdam, archief [nr], inventaris [nr]
**Scan:** [image URL or "at register level"]

**Confidence:** Tier B — official Amsterdam city archive record
```
