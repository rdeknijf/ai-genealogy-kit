---
name: ecal
description: |
  Search indexed person records at Erfgoedcentrum Achterhoek en Liemers (ECAL)
  via direct HTTP calls to the MAIS AJAX proxy. No browser automation needed.
  Uses the same MAIS/Archieven.nl platform as Gemeentearchief Alphen and Het
  Utrechts Archief. 2.4 million indexed persons covering eastern Gelderland:
  Aalten, Berkelland (Borculo, Eibergen, Neede, Ruurlo), Bronckhorst (Hummelo,
  Keppel, Vorden), Doetinchem, Montferland ('s-Heerenberg, Didam), Oost Gelre
  (Groenlo, Lichtenvoorde), Oude IJsselstreek (Gendringen, Dinxperlo),
  Winterswijk. Specializes in population registers (2M), notarial records
  (172K), militia registers (92K), and schutterij/civic guard records (26K).
  Note: DTB/BS civil registry records are NOT here — those flow through Gelders
  Archief to WieWasWie/OpenArchieven. Triggers on: "search ECAL", "Achterhoek
  records", "Doetinchem archive", "Winterswijk records", "/ecal", or genealogy
  research in the Achterhoek/Liemers region. No login required.
---

# Erfgoedcentrum Achterhoek en Liemers (ECAL)

Search indexed person records from the regional archive for eastern Gelderland.
Uses direct HTTP calls to the MAIS AJAX proxy endpoint — no browser needed.

No login required for viewing indexed records.

## Coverage

**Municipalities:** Aalten, Berkelland (incl. Borculo, Eibergen, Neede, Ruurlo),
Bronckhorst (incl. Hummelo en Keppel, Hengelo, Vorden), Doetinchem,
Montferland (incl. Bergh, 's-Heerenberg, Didam), Oost Gelre (incl. Groenlo,
Lichtenvoorde), Oude IJsselstreek (incl. Gendringen, Dinxperlo), Winterswijk.

**Total indexed persons:** 2,453,576

**Important:** DTB (doop-, trouw-, begraafboeken) and Burgerlijke Stand (civil
registry) records are NOT in ECAL's own person index. Those flow through
Gelders Archief to WieWasWie/OpenArchieven. Use the `gelders-archief` or
`wiewaswie` skills for birth/marriage/death records in this region.

ECAL's unique value is **population registers** (2M), **notarial records**
(172K), **militia registers** (92K), and **schutterij records** (26K).

## Primary method (HTTP via MAIS AJAX proxy)

All data is fetched via curl to the MAIS AJAX proxy endpoint. The proxy returns
server-rendered HTML that can be parsed with regex or an HTML parser. No
JavaScript execution, cookies, or session management required.

### Base URL

```
https://www.ecal.nu/archieven/maisi_proxy.php
```

### 1. Search for persons

Construct a URL with query parameters and fetch with curl.

**Simple search (all fields):**

```bash
curl -s 'https://www.ecal.nu/archieven/maisi_proxy.php?mivast=26&mizig=100&miadt=26&miview=tbl&milang=nl&mizk_alle=SURNAME'
```

**Advanced search (specific fields):**

```bash
curl -s 'https://www.ecal.nu/archieven/maisi_proxy.php?mivast=26&mizig=100&miadt=26&miview=tbl&milang=nl&mip1=SURNAME&mip2=TUSSENVOEGSEL&mip5=PLAATS&mibj=1800&miej=1850'
```

### Search parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `mivast` | Archive ID (always `26`) | `26` |
| `mizig` | Search type (see below) | `100` |
| `miadt` | Archive ID (always `26`) | `26` |
| `miview` | View type (`tbl` for table) | `tbl` |
| `milang` | Language | `nl` |
| `mizk_alle` | All-fields search term | `jansen` |
| `mip1` | Achternaam (surname) | `Jansen` |
| `mip2` | Tussenvoegsel (prefix) | `van` |
| `mip3` | Voornaam (first name) | `Jan` |
| `mip4` | Rol (role) | `Geregistreerde` |
| `mip5` | Plaats (municipality) | `Doetinchem` |
| `mib1` | Bron (source type code) | `112` |
| `mibj` | Period start (yyyy or dd-mm-yyyy) | `1800` |
| `miej` | Period end (yyyy or dd-mm-yyyy) | `1850` |
| `mif1` | Bron filter (same codes as mib1) | `112` |
| `mistart` | Pagination offset (0-based) | `0` |
| `miamount` | Results per page (default 20) | `20` |
| `misort` | Sort field and direction | `dat\|asc` |

**Search type (mizig) values:**

| Value | Search type |
|-------|-------------|
| `100` | All persons (across all record types) |

**Bron (source type) filter codes:**

| Code | Source type | Records |
|------|------------|---------|
| `112` | Persoon in bevolkingsregister | 2,036,951 |
| `224` | Notariele akte | 171,987 |
| `285` | Persoon in genealogie | 105,962 |
| `265` | Persoon in militieregister | 91,727 |
| `555` | Persoon in schutterij | 25,999 |
| `373` | Persoon in landstorm | 6,078 |
| `788` | Persoon in kohier (tax registers) | 5,946 |
| `203` | Dossier | 808 |
| `418` | Persoon in proces verbaal | 799 |

### 2. Parse search results

The response is HTML. Extract data with regex or an HTML parser. Same format
as the gemeentearchief-alphen skill.

**Hit count:**

```python
import re
hits_match = re.search(r'mi_hits_count">(\d+)<', html)
total = int(hits_match.group(1)) if hits_match else 0
```

**Result rows:**

```python
rows = re.findall(
    r'<tr[^>]*class="mi_(odd|even) rowlink"[^>]*'
    r'data-id="([^"]+)"[^>]*'
    r"data-qr='([^']*)'[^>]*>"
    r'(.*?)</tr>',
    html, re.DOTALL
)

for parity, data_id, data_qr, content in rows:
    cells = re.findall(r'<td[^>]*class="mi_value">(.*?)</td>', content, re.DOTALL)
    # cells[0] = icon/type (extract alt="..." for record type name)
    # cells[1] = Voornaam
    # cells[2] = Achternaam
    # cells[3] = Rol
    # cells[4] = Plaats
    # cells[5] = Datum

    record_type_match = re.search(r'alt="([^"]+)"', cells[0])
    record_type = record_type_match.group(1) if record_type_match else 'unknown'
    voornaam = re.sub(r'<[^>]+>', '', cells[1]).strip()
    achternaam = re.sub(r'<[^>]+>', '', cells[2]).strip()
    rol = re.sub(r'<[^>]+>', '', cells[3]).strip()
    plaats = re.sub(r'<[^>]+>', '', cells[4]).strip()
    datum = re.sub(r'<[^>]+>', '', cells[5]).strip()
```

### 3. Get record details

Use the `data-qr` parameters from a result row, adding `miview=ahd`:

```bash
curl -s 'https://www.ecal.nu/archieven/maisi_proxy.php?mivast=26&mizig=100&miadt=26&miaet=54&micode=CODE&minr=NR&milang=nl&miview=ahd'
```

Parse detail fields the same way as gemeentearchief-alphen (strip script tags,
extract label:value pairs from HTML).

### 4. Pagination

For large result sets, iterate with `mistart`:

```bash
# Page 1 (results 0-19)
...&mistart=0&miamount=20
# Page 2 (results 20-39)
...&mistart=20&miamount=20
```

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **ECAL** | Population registers, notarial records, schutterij, militia for Achterhoek/Liemers |
| Gelders Archief / WieWasWie | Birth, marriage, death records for this region |
| OpenArchieven | Aggregated search across multiple archives |

## Output format

```
## ECAL Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Archive ref:** [reference numbers]
**Scan available:** Yes/No

**Confidence:** Tier B — official archive record from ECAL
```
