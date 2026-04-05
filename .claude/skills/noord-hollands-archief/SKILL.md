---
name: noord-hollands-archief
description: |
  Search indexed person records at the Noord-Hollands Archief (NHA) in Haarlem
  via the OpenArchieven JSON API (primary) and MAIS URL-parameter searches
  (fallback for detail views). No browser automation needed. 12.7 million person
  records covering the entire province of Noord-Holland: Haarlem, Amsterdam
  (partial), Hilversum, Alkmaar, Hoorn, Enkhuizen, Den Helder, Zaanstad,
  Beverwijk, Velsen, Heemstede, Bloemendaal, and all other Noord-Holland
  municipalities. Record types include BS (births, marriages, deaths),
  DTB (church baptisms), bevolkingsregister (population registers),
  militieregisters, notarial records, vredegerecht (peace court), memorie van
  successie, and overlijdensverklaringen. Especially relevant for Makkelie
  family in Haarlem, maritime/schepelingen research, and any Noord-Holland
  genealogy. Triggers on: "search Noord-Hollands Archief", "NHA records",
  "Haarlem records", "Haarlem archive", "Noord-Holland genealogy",
  "Makkelie records", "/noord-hollands-archief", or any genealogy research
  in the Noord-Holland province. No login required. Parallelizable — run
  multiple queries simultaneously.
---

# Noord-Hollands Archief (NHA) — Provincial Archive for Noord-Holland

Search 12.7 million indexed person records from the Noord-Hollands Archief in
Haarlem. Primary access via OpenArchieven JSON API; MAIS URL-parameter approach
for detail views and record types not in OpenArchieven.

No login required. No authentication needed.

## Coverage

**Province:** Noord-Holland (all municipalities)

**12.7 million person records** across record types:

| Source type | OpenArchieven name | MAIS code | Approx. records |
|-------------|-------------------|-----------|-----------------|
| BS Geboorte | `BS Geboorte` | `113` | 838K |
| BS Huwelijk | `BS Huwelijk` | `109` | 5.3M |
| BS Overlijden | `BS Overlijden` | `114` | 4.1M |
| DTB Dopen | `DTB Dopen` | `156` | 440K |
| Bevolkingsregister | `Bevolkingsregister` | `112` | 546K |
| Militieregisters | `Militieregisters` | `765` | 733K |
| Vredegerecht | `Vredegerecht` | `55` | 318K |
| Notariele archieven | `Notariële archieven` | `224` | 32K |
| Overlijdensverklaring | — | `549` | (MAIS only) |
| Memorie van successie | — | `275` | (MAIS only) |
| Faillissementsdossier | `Faillissementsdossier` | `297` | 4.4K |

**Key municipalities for current research:**
Haarlem (Makkelie family), Amsterdam (partial overlap with Stadsarchief),
Hilversum, Beverwijk, Velsen (IJmuiden), Den Helder (maritime).

**Note:** Amsterdam civil records are split between NHA and the Stadsarchief.
NHA covers province-level BS records; the Stadsarchief has DTB, population
registers, and archiefkaarten. For Amsterdam, use both skills.

## Method 1: OpenArchieven JSON API (primary — fastest)

Structured JSON, ~100ms per query. Best for name searches with filters.

### 1. Search for persons

```bash
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=SURNAME&number_show=25'
```

**With filters:**

```bash
# By source type
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Makkelie&sourcetype=BS+Geboorte&number_show=25'

# By place
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Makkelie&place=Haarlem&number_show=25'

# By date range
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Bakker&period_start=1800&period_end=1850&number_show=25'

# Combined
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Bakker&place=Haarlem&sourcetype=BS+Huwelijk&period_start=1800&period_end=1900&number_show=25'
```

### Search parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `archive` | Archive code (always `nha`) | `nha` |
| `name` | Person name (surname, or full name) | `Makkelie`, `Jan+Bakker` |
| `place` | Event place | `Haarlem` |
| `sourcetype` | Record type filter | `BS Geboorte` |
| `period_start` | Year from | `1800` |
| `period_end` | Year to | `1900` |
| `number_show` | Results per page (max 100) | `25` |
| `start` | Pagination offset (0-based) | `0`, `25`, `50` |
| `sort` | Sort order (1=relevance, 2=date asc, 3=date desc) | `2` |

### Available source type values

| Source type | Description |
|-------------|-------------|
| `BS Geboorte` | Civil birth certificate (post-1811) |
| `BS Huwelijk` | Civil marriage certificate (post-1811) |
| `BS Overlijden` | Civil death certificate (post-1811) |
| `DTB Dopen` | Church baptism record (pre-1811) |
| `Bevolkingsregister` | Population register |
| `Militieregisters` | Militia/conscription register |
| `Notariële archieven` | Notarial records |
| `Vredegerecht` | Peace court records |
| `Faillissementsdossier` | Bankruptcy dossier |

### 2. Parse response

```json
{
  "response": {
    "number_found": 95,
    "docs": [
      {
        "pid": "Person2735418083",
        "identifier": "3374C7E3-CACF-45D6-B0F9-CDD24042F0FC",
        "archive_code": "nha",
        "archive_org": "Noord-Hollands Archief",
        "personname": "Alida Wilhelmina Makkelie",
        "relationtype": "Bruid",
        "eventtype": "Huwelijk",
        "eventdate": {"day": 25, "month": 9, "year": 1940},
        "eventplace": ["Haarlem"],
        "sourcetype": "BS Huwelijk",
        "url": "https://www.openarchieven.nl/nha:3374C7E3-CACF-45D6-B0F9-CDD24042F0FC"
      }
    ]
  }
}
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `personname` | Full name |
| `relationtype` | Role in record (Kind, Vader, Moeder, Bruidegom, Bruid, Overledene, etc.) |
| `eventtype` | Event type (Geboorte, Huwelijk, Overlijden, Doop, Inschrijving) |
| `eventdate` | Date as `{day, month, year}` object |
| `eventplace` | Place as array |
| `sourcetype` | Record type |
| `identifier` | Unique record identifier (UUID) |
| `url` | Link to OpenArchieven viewer |

### 3. Get all persons in a record

Multiple persons from the same deed share the same `identifier`. Search by
name and then group results by `identifier` to find family relationships:

```python
from collections import defaultdict
by_id = defaultdict(list)
for doc in data['response']['docs']:
    by_id[doc['identifier']].append(doc)
# Each group = one deed with child, father, mother, witnesses
```

### 4. Pagination

```bash
# Page 1
...&start=0&number_show=25
# Page 2
...&start=25&number_show=25
```

### 5. Construct web link

From any result:

```
https://www.openarchieven.nl/nha:{identifier}
```

## Method 2: MAIS URL parameters (fallback — for detail views)

Use when you need record details not available via OpenArchieven (e.g., full
transcription fields, archive reference numbers, certificate numbers, or
record types only in MAIS like overlijdensverklaringen and memories van
successie).

### 1. Search for persons

```
https://noord-hollandsarchief.nl/personen/databases?view=maisinternet&mivast=236&mizig=100&miadt=236&miview=tbl&milang=nl&mip1={surname}
```

Use WebFetch to parse results, or curl + regex.

### URL parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `mivast` | Archive ID (always `236`) | `236` |
| `mizig` | Search type (always `100`) | `100` |
| `miadt` | Archive ID (always `236`) | `236` |
| `miview` | View: `tbl` (table) or `ldt` (detail) | `tbl` |
| `milang` | Language | `nl` |
| `mip1` | Achternaam (surname) | `Makkelie` |
| `mip2` | Tussenvoegsel (prefix) | `van` |
| `mip3` | Voornaam (first name) | `Pieter` |
| `mip4` | Rol (role) | `Overledene`, `Vader` |
| `mip5` | Plaats (place) | `Haarlem` |
| `mib1` | Bron code (source type) | See table above |
| `mibj` | Period from (year or dd-mm-yyyy) | `1800` |
| `miej` | Period to (year or dd-mm-yyyy) | `1900` |
| `mistart` | Pagination offset (0-based) | `0`, `20` |
| `mizk_alle` | All-fields search | `Makkelie` |

**Wildcards:** `*` replaces multiple characters (min 3 chars before `*`),
`_` replaces a single character.

### 2. Parse search results (curl + regex)

```python
import re

# Hit count (note: uses dots as thousands separator)
hits_match = re.search(r'mi_hits_count">([^<]+)<', html)
total = hits_match.group(1).strip().replace('.', '') if hits_match else '0'

# Result rows
rows = re.findall(
    r'<tr[^>]*class="mi_(odd|even) rowlink"[^>]*'
    r'data-id="([^"]+)"[^>]*'
    r"data-qr='([^']*)'[^>]*>"
    r'(.*?)</tr>',
    html, re.DOTALL
)

for parity, data_id, data_qr, content in rows:
    cells = re.findall(r'<td[^>]*class="mi_value">(.*?)</td>', content, re.DOTALL)
    # cells[0] = record type icon (extract alt="..." for type name)
    # cells[1] = Voornaam (first name)
    # cells[2] = Achternaam (surname)
    # cells[3] = Rol (role)
    # cells[4] = Plaats (place)
    # cells[5] = Datum (date)
    record_type = re.search(r'alt="([^"]+)"', cells[0])
    record_type = record_type.group(1) if record_type else 'unknown'
```

### 3. Get record detail

Use the `data-qr` parameters from a result row with `miview=ldt`:

```
https://noord-hollandsarchief.nl/personen/databases?view=maisinternet&{data_qr}&miview=ldt
```

Best parsed with WebFetch:

```
WebFetch -> {detail_url}
  prompt: "Extract all person details: names, dates, places, parents, archive reference, certificate number, scan availability."
```

Detail pages include:

- Full person names, dates, places
- Parents (vader/moeder)
- Partner
- Archive reference (archiefnummer, inventarisnummer)
- Certificate number (aktenummer)
- Persistent handle URL (`hdl.handle.net/21.12102/...`)
- Digitization status

### 4. Persistent handle URL

Many records have a persistent identifier:

```
https://hdl.handle.net/21.12102/{GUID}
```

This redirects to the NHA archive viewer and serves as a stable citation link.

## Which method to use

| Scenario | Method |
|----------|--------|
| Search by name, date, place | OpenArchieven API |
| Filter by record type | OpenArchieven API |
| Get family relationships (all persons in deed) | OpenArchieven API (group by identifier) |
| Get full record detail (parents, cert number, archive ref) | MAIS + WebFetch |
| Record types only in MAIS (overlijdensverklaring, memorie van successie) | MAIS URL params |
| Wildcard searches | MAIS URL params |
| Bulk enumeration | OpenArchieven API (paginate) |

## Example searches

```bash
# All Makkelie birth records in Haarlem via OpenArchieven
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Makkelie&sourcetype=BS+Geboorte&place=Haarlem&number_show=25'

# Bakker military records via OpenArchieven
curl -s 'https://api.openarchieven.nl/1.0/records/search.json?archive=nha&name=Bakker&sourcetype=Militieregisters&number_show=25'

# Makkelie in MAIS (all record types including MAIS-only)
curl -s 'https://noord-hollandsarchief.nl/personen/databases?view=maisinternet&mivast=236&mizig=100&miadt=236&miview=tbl&milang=nl&mip1=Makkelie'

# Doopinschrijving for Bakker in Haarlem via MAIS
curl -s 'https://noord-hollandsarchief.nl/personen/databases?view=maisinternet&mivast=236&mizig=100&miadt=236&miview=tbl&milang=nl&mip1=Bakker&mib1=156&mip5=Haarlem'
```

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Noord-Hollands Archief** | All Noord-Holland province records, Haarlem BS/DTB, militieregisters, notarial |
| Amsterdam Stadsarchief | Amsterdam-specific DTB, bevolkingsregister, archiefkaarten, persoonskaarten |
| WieWasWie | National coverage, structured person lookups |
| OpenArchieven | Broad cross-archive search (NHA records included) |

## Output format

```
## Noord-Hollands Archief Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** NHA, archiefnummer [nr], inventarisnummer [nr], aktenummer [nr]
**Persistent URL:** [hdl.handle.net link if available]
**OpenArchieven:** [URL]

**Confidence:** Tier B — official indexed record from Noord-Hollands Archief
```

## Limitations

- **Bevolkingsregister:** Not well indexed in OpenArchieven for NHA (546K
  records vs 12M+ total). Use MAIS for bevolkingsregister searches if
  OpenArchieven returns few results.
- **DTB coverage:** Only baptisms (DTB Dopen) are indexed; DTB marriages and
  burials appear to have very limited or no indexing.
- **Scans:** Many records are digitized but scans are not always directly
  linked from the API. Use the persistent handle URL or OpenArchieven viewer
  to access scans.
- **Overlijdensverklaringen and memories van successie:** Only available via
  the MAIS interface, not in OpenArchieven.
- **Hit count format:** MAIS uses dots as thousands separator (e.g., "1.119"
  means 1,119). Strip dots before parsing as integer.
