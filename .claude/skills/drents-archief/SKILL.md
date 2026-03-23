---
name: drents-archief
description: |
  Search the Drents Archief (Drenthe Provincial Archive) via its Memorix
  Genealogy API. 6.7 million person records including civil registration,
  DTB church records, population registers, notarial records, and uniquely
  the Maatschappij van Weldadigheid bedelaarskolonie (beggar colony) records
  from Veenhuizen and Frederiksoord (1822-1866). NOT in OpenArchieven — this
  is the only way to search Drenthe genealogy records programmatically.
  Use this skill when: "search Drents Archief", "Drenthe records",
  "bedelaarskolonie", "beggar colony", "Veenhuizen", "Maatschappij van
  Weldadigheid", "Frederiksoord", "Geheugen van Drenthe", "/drents-archief",
  or when looking for ancestors in the province of Drenthe. No login required.
---

# Drents Archief — Drenthe Provincial Archive

Search person records from the Drenthe provincial archive via the Memorix
Genealogy REST API. 6.7 million person mentions. No browser needed.

**Not in OpenArchieven** — Drents Archief maintains its own standalone
platform and does not feed into the OpenArchieven aggregator.

## API details

**Base URL:** `https://webservices.memorix.nl/genealogy/`
**API Key:** `a85387a2-fdb2-44d0-8209-3635e59c537e`

## Step 1: Search for persons

```bash
curl -s "https://webservices.memorix.nl/genealogy/person?q=SURNAME&apiKey=a85387a2-fdb2-44d0-8209-3635e59c537e&rows=25&page=1"
```

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Name search (required). Supports wildcards `*` | `Taks`, `Christia*+Taks` |
| `apiKey` | Required API key | `a85387a2-fdb2-44d0-8209-3635e59c537e` |
| `rows` | Results per page (default 100) | `25` |
| `page` | Page number | `1`, `2` |
| `f` | Filter (URL-encoded JSON) | See filter section |

### Filter by record type

The `f` parameter takes URL-encoded JSON:

```bash
# Filter to civil registration only
curl -s "https://webservices.memorix.nl/genealogy/person?q=Taks&apiKey=a85387a2-fdb2-44d0-8209-3635e59c537e&f=%7B%22search_s_register_type_title%22%3A%7B%22v%22%3A%22Burgerlijke%20standregister%22%7D%7D"
```

### Available register types

| Filter value | Description | Period |
|-------------|-------------|--------|
| `Burgerlijke standregister` | Civil registration (BS) | 1811-1974 |
| `Doop, Trouw en Begraaf Registers` | DTB church records | 1600-1811 |
| `Bevolkingsregisters` | Population registers | 1850+ |
| `Notarieel` | Notarial records | 1810-1915 |
| `Inschrijfregisters MvW/RWI` | **Bedelaarskolonie registers** | 1822-1866 |
| `Correspondentie MvW` | Colony correspondence | 1818-1847 |

### Response structure

The response JSON has:

- `metadata.pagination.total` — total result count
- `person` — array of person objects (note: singular `person`, not `persons`)

Each person object contains:

| Field | Description |
|-------|-------------|
| `id` | Person UUID (for detail lookup) |
| `deed_id` | Source document UUID |
| `metadata.voornaam` | First name |
| `metadata.geslachtsnaam` | Surname |
| `metadata.person_display_name` | Full display name |
| `metadata.datum_geboorte` | Birth date |
| `metadata.datum` | Event/registration date |
| `metadata.plaats` | Place |
| `metadata.register_naam` | Register name |
| `metadata.register_type_title` | Register type |
| `metadata.register_gemeente` | Municipality |
| `metadata.deed_type_title` | Deed type |
| `metadata.type_title` | Person role (Geregistreerde, Moeder, Vader, etc.) |
| `metadata.diversen` | Free text with HTML (death date, origin, arrival date for MvW) |
| `metadata.has_assets` | `"deed"` if scan available |

## Step 2: Get record detail

```bash
# Person detail
curl -s "https://webservices.memorix.nl/genealogy/person/PERSON_UUID?apiKey=a85387a2-fdb2-44d0-8209-3635e59c537e"

# Deed/document detail (includes scan URLs)
curl -s "https://webservices.memorix.nl/genealogy/deed/DEED_UUID?apiKey=a85387a2-fdb2-44d0-8209-3635e59c537e"
```

The deed detail returns `asset[].thumb.large` and `asset[].download` —
direct image URLs via `images.memorix.nl/dre/`.

## Browser view

```
https://www.drentsarchief.nl/onderzoeken/genealogie/zoeken/persons#/persons/PERSON_UUID
```

## Example: Christiaan Taks (bedelaarskolonie)

```bash
curl -s "https://webservices.memorix.nl/genealogy/person?q=Christia*+Taks&apiKey=a85387a2-fdb2-44d0-8209-3635e59c537e"
```

Returns: Christiaan Taks, born 1810-01-12 Zwolle, arrived Veenhuizen
colony 1856-03-14, died 1856-11-21. Religion: rooms-katholiek. Register
no. 1590. Scan available.

## Workflow

1. Search by surname (+ optional register type filter)
2. Review matches — check `metadata.type_title` for role (Geregistreerde
   = the person themselves, Moeder/Vader = parent mentioned)
3. For records with `has_assets: "deed"`, fetch the deed detail for scan URLs
4. Open browser URL for full context

## Limitations

- **Drenthe only.** No records from other provinces.
- **API key is public** (embedded in the website HTML) but may change.
- **No date range filter** in the API. Filter by register type instead.
- **AlleDropten.nl** (genealogy portal) has invalid TLS — use this API.

## Output format

```
## Drents Archief Result

**Person:** [name] ([role])
**Born:** [date] in [place]
**Register:** [register name] ([type])
**Municipality:** [gemeente]
**Additional:** [diversen field]

**Scan:** [image URL or "available" / "not available"]
**Browser URL:** https://www.drentsarchief.nl/onderzoeken/genealogie/zoeken/persons#/persons/[id]

**Confidence:** Tier B — official provincial archive record from Drents Archief
```
