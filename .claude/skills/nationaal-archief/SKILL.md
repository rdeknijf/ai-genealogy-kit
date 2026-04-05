---
name: nationaal-archief
description: |
  Search the Dutch National Archive (Nationaal Archief) for person records.
  Uses the Open Archives API (archive_code=ghn) for indexed person records
  and the GAF inventory API for archive finding aids. Contains WWII records
  (CABR collaboration dossiers, forced labor registration, Red Cross),
  military service records (Stamboeken, Staten van Dienst for army and navy),
  personnel files, VOC records, and petitions. Use this skill when searching
  for: WWII collaboration dossiers (CABR), forced labor (tewerkgestelden),
  military service records, stamboeken, staten van dienst, VOC personnel,
  war-related records, or any Nationaal Archief collection. Triggers on:
  "search nationaal archief", "national archive", "CABR dossier", "military
  service record", "stamboek", "staat van dienst", "tewerkgesteld",
  "forced labor", "VOC records", "/nationaal-archief", or when looking for
  military, WWII, or colonial-era records in the Netherlands. No login required
  for index data.
---

# Nationaal Archief — Dutch National Archive

Search person-level indexed records at the Dutch National Archive. Two
complementary APIs, both JSON, no browser needed.

**Note:** The Nationaal Archief does NOT hold civil registration records
(births, marriages, deaths) — those are at regional archives via WieWasWie
and OpenArchieven. The NA specializes in military, WWII, colonial, and
government records.

## Record types

| Source type | Description | Notes |
|---|---|---|
| Stamboeken | Military service record books | Army and navy |
| Staten van Dienst | Military service records | By birth year cohort |
| CABR dossiers | WWII collaboration investigations | Restricted until 2027, index searchable |
| Tewerkgesteldenregistratie | WWII forced labor registration | |
| Beheersdossier | Post-war management dossiers (NBI) | Property/persons |
| Personeelsadministratie | Personnel files | VOC, government |
| Verzoekschriften | Petitions archive | 1878+ |
| Registratie onderscheidingen | Military decorations/honors | |
| Persoonsdossiers | Personal dossiers | Various origins |

## Primary method: Open Archives API

The Nationaal Archief's indexed person records are available via the same
Open Archives API used by other archive skills. Archive code: `ghn`.

### Step 1: Search for persons

```bash
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=SURNAME&archive_code=ghn&lang=nl&number_show=20"
```

**Parameters:**

| Parameter | Description | Example |
|---|---|---|
| `name` | Search query (surname, full name, or couple) | `Knijf`, `Jan+de+Knijf` |
| `archive_code` | Must be `ghn` for Nationaal Archief | `ghn` |
| `sourcetype` | Filter by record type | `Stamboeken`, `CABR dossiers`, `Tewerkgesteldenregistratie` |
| `number_show` | Results per page (max 100) | `20` |
| `start` | Pagination offset | `0`, `20`, `40` |
| `lang` | Language | `nl`, `en` |
| `sort` | Sort order (negative = desc) | `1` (name), `4` (date), `-4` (date desc) |

**Example searches:**

```bash
# All NA records for "Knijf"
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&archive_code=ghn&lang=nl&number_show=20"

# Military service records only
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&archive_code=ghn&sourcetype=Stamboeken&lang=nl&number_show=20"

# WWII forced labor records
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&archive_code=ghn&sourcetype=Tewerkgesteldenregistratie&lang=nl&number_show=20"

# CABR (collaboration) dossiers
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&archive_code=ghn&sourcetype=CABR+dossiers&lang=nl&number_show=20"
```

**Response fields per result:**

- `personname` — full name
- `eventtype` — event type
- `eventdate` — `{day, month, year}`
- `eventplace` — array of place names
- `sourcetype` — record type (Stamboeken, CABR dossiers, etc.)
- `identifier` — UUID for detail lookup
- `url` — link to OpenArchieven record page

### Step 2: View full record

```bash
curl -s "https://api.openarchieven.nl/1.1/records/show.json?archive=ghn&identifier=UUID&lang=nl"
```

Or view in browser: `https://www.openarchieven.nl/ghn:UUID`

The record page shows the full name, birth date/place, archive reference
numbers (inventory number + dossier number), and source archive details.

## Secondary method: GAF inventory API

For finding archive inventory references (useful when you need the physical
file location for an on-site request):

```bash
curl -s "https://service.archief.nl/gaf/api/search?q=SURNAME&rows=10&start=0"
```

**Parameters:**

| Parameter | Description |
|---|---|
| `q` | Search term |
| `rows` | Results per page |
| `start` | Pagination offset |
| `dao` | Set to `true` to filter for records with digital scans |
| `eadid` | Filter by specific inventory (e.g., `2.13.259` for army records 1911-1920) |

**Response fields:**

- `unittitle` — record title (often contains person name)
- `eadid` — inventory number (e.g., `2.13.257`)
- `unitid` — unit within inventory
- `availability` — `PHYSICAL` or `DIGITAL`
- `unitdate` — date range
- `subtitle` — archive/collection name

**Useful inventory numbers (eadid):**

| eadid | Description |
|---|---|
| `2.13.257` | Staten van Dienst Koninklijke Marine 1900-1920 |
| `2.13.259` | Staten van Dienst Koninklijke Landmacht 1911-1920 |
| `2.09.16.08` | Nederlands Beheersinstituut dossiers |
| `2.05.117` | Buitenlandse Zaken code-archief 1945-1954 |

## Tertiary method: HUB3 API — Landmacht Stamboeken 1795-1813

Direct JSON API for Napoleonic-era army service record books. Same HUB3 API
pattern as the VOC Opvarenden skill (nt00444), but index **nt00239**.

**Index:** Landmacht Stamboeken 1795-1813 (nt00239)
**Records:** 61,255 entries (49,909 soldaat, 8,446 officier, 2,897 onderofficier)
**Source:** Archive inventory 2.01.15 at the Nationaal Archief
**Scans:** Digitized and viewable online

### Search by surname

```bash
curl -s "https://service.archief.nl/hub3/api/nt/nt00239?q=SURNAME&rows=10" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

**Parameters:**

| Parameter | Description |
|---|---|
| `q` | Search term (surname) |
| `rows` | Results per page |

**Response fields per result:**

- `surname` — family name
- `tussenvoegsel` — name prefix (de, van, van der, etc.)
- `voornaam` / `voorletters` — first name or initials
- `rank` — military rank (soldaat, officier, onderofficier)

### Supplement index: nt00245

A supplementary index **nt00245** ("Landmacht: Stamboeken supplement")
covers the period 1795-1810 with additional entries not in the main index.
Same API pattern:

```bash
curl -s "https://service.archief.nl/hub3/api/nt/nt00245?q=SURNAME&rows=10" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

### When to use

Search both nt00239 and nt00245 when looking for military ancestors during
the Batavian Republic / Napoleonic period (1795-1813). These records
predate the post-1813 Stamboeken available via the Open Archives API and
cover the French-era Dutch army. The NIMH skill also has ~53K Napoleon-era
records via OpenArchieven — check both sources.

## Workflow

### For person searches (WWII, military, colonial):

1. Search via Open Archives API with `archive_code=ghn`
2. Filter by `sourcetype` if you know what record type to look for
3. Fetch full record details for matches
4. Note inventory numbers for physical records that need on-site viewing

### For finding specific archive files:

1. Search GAF API with person name
2. Note `eadid` and `unitid` for the matching inventory entry
3. Check `availability` — if `DIGITAL`, scans may be viewable online
4. If `PHYSICAL`, note the reference for an on-site request

## Limitations

- **CABR dossiers** are "beperkt openbaar" (restricted access) until 2027 —
  the index is searchable but the actual files require on-site viewing with
  special permission
- **Most military records** are physical-only — the index tells you they exist
  but viewing requires a visit to The Hague or a reproduction request
- **Red Cross war archive** (Rode Kruis Oorlogsarchief) is NOT accessible via
  the API — it may require on-site access or a separate search tool
- **No civil registration** — use WieWasWie, OpenArchieven, or regional archives
  for births, marriages, deaths

## Output format

```
## Nationaal Archief Result

**Person:** [name]
**Record type:** [sourcetype]
**Event:** [type], [date] in [place]

**Archive reference:** inventory [eadid], unit [unitid]
**Availability:** [PHYSICAL / DIGITAL]
**OpenArchieven URL:** https://www.openarchieven.nl/ghn:[identifier]

**Confidence:** Tier B — official government archive record via Nationaal Archief index
```

For CABR dossiers, note: "Restricted access — index data only, full dossier
requires on-site viewing."
