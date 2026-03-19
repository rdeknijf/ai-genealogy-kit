---
name: gemeentearchief-alphen-optimized
description: |
  Search indexed person records at Gemeentearchief Alphen aan den Rijn
  (gemeentearchief.alphenaandenrijn.nl) via direct HTTP calls to the MAIS AJAX
  proxy. No browser automation needed. Uses the same MAIS/Archieven.nl platform
  as Het Utrechts Archief and Gelders Archief. Covers municipalities: Alphen aan
  den Rijn, Aarlanderveen, Benthuizen, Hazerswoude, Koudekerk, and surrounding
  areas in the Rijnstreek region of South Holland. Has DTB records, Burgerlijke
  Stand, Bevolkingsregister, and Notariele Akten. Known to have "de Knijf" /
  "van der Knijf" records from Aarlanderveen and Benthuizen. Triggers on: "search
  Alphen archive", "look up in Alphen aan den Rijn", "Aarlanderveen records",
  "Benthuizen records", "/gemeentearchief-alphen", or any genealogy research in
  the Alphen aan den Rijn area. No login required.
---

# Gemeentearchief Alphen aan den Rijn (Optimized)

Search indexed person records from the municipal archive of Alphen aan den Rijn.
Uses direct HTTP calls to the MAIS AJAX proxy endpoint instead of Playwright
browser automation, reducing query time from ~15-30s to ~0.5s per search.

No login required for viewing indexed records.

## Coverage

Municipalities: Alphen aan den Rijn, Aarlanderveen, Benthuizen, Hazerswoude,
Koudekerk, and surrounding areas.

**Knijf records:** 863 total person results, mostly "de Knijf" from
Aarlanderveen. 14 DTB results (all begraafinschrijvingen from Benthuizen and
Aarlanderveen -- "van der Knijf" branch). Zero doopinschrijvingen for Knijf.

## Primary method (HTTP via MAIS AJAX proxy)

All data is fetched via curl to the MAIS AJAX proxy endpoint. The proxy returns
server-rendered HTML that can be parsed with regex or an HTML parser. No
JavaScript execution, cookies, or session management required.

### Base URL

```
https://gemeentearchief.alphenaandenrijn.nl/components/com_maisinternet/maisi_ajax_proxy.php
```

**Important:** The SSL certificate may trigger warnings. Use `curl -sk` to skip
certificate verification.

### 1. Search for persons

Construct a URL with query parameters and fetch with curl.

**Simple search (all fields):**

```bash
curl -sk 'https://gemeentearchief.alphenaandenrijn.nl/components/com_maisinternet/maisi_ajax_proxy.php?mivast=105&mizig=100&miadt=105&miview=tbl&milang=nl&mizk_alle=knijf'
```

**Advanced search (specific fields):**

```bash
curl -sk 'https://gemeentearchief.alphenaandenrijn.nl/components/com_maisinternet/maisi_ajax_proxy.php?mivast=105&mizig=100&miadt=105&miview=tbl&milang=nl&mip1=Knijf&mip2=de&mip5=Aarlanderveen&mibj=1800&miej=1850'
```

### Search parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `mivast` | Archive ID (always `105`) | `105` |
| `mizig` | Search type (see below) | `100` |
| `miadt` | Archive ID (always `105`) | `105` |
| `miview` | View type (`tbl` for table) | `tbl` |
| `milang` | Language | `nl` |
| `mizk_alle` | All-fields search term | `knijf` |
| `mip1` | Achternaam (surname) | `Knijf` |
| `mip2` | Tussenvoegsel (prefix) | `de` |
| `mip3` | Voornaam (first name) | `Pieter` |
| `mip4` | Rol (role) | `Kind` |
| `mip5` | Plaats (municipality) | `Aarlanderveen` |
| `mib1` | Bron (source type code) | `113` |
| `mibj` | Period start (yyyy or dd-mm-yyyy) | `1800` |
| `miej` | Period end (yyyy or dd-mm-yyyy) | `1850` |
| `mif1` | Bron filter (same codes as mib1) | `113` |
| `mif2` | Rol filter | `Kind` |
| `mistart` | Pagination offset (0-based) | `0` |
| `miamount` | Results per page (default 20) | `20` |
| `misort` | Sort field and direction | `dat\|asc` |

**Search type (mizig) values:**

| Value | Search type |
|-------|-------------|
| `100` | All persons (across all record types) |
| `323` | DTB (Doop-, trouw- en begraafinschrijvingen) |
| `324` | Civil registry (Burgerlijke Stand) |
| `328` | Notarial deeds |
| `94` | Bevolkingsregister |
| `329` | Gerechtelijke akten |

**Bron (source type) codes:**

| Code | Source type | Era |
|------|------------|-----|
| `156` | Doopinschrijving | Pre-1811 |
| `157` | Trouwinschrijving | Pre-1811 |
| `158` | Begraafinschrijving | Pre-1811 |
| `113` | Geboorteakte | Post-1811 |
| `109` | Huwelijksakte | Post-1811 |
| `114` | Overlijdensakte | Post-1811 |
| `140` | Echtscheidingsakte | Post-1811 |
| `390` | Erkenningsakte | Post-1811 |
| `102` | Persoon in akte | Various |
| `112` | Persoon in bevolkingsregister | Various |
| `31` | Bouwdossier | Various |

**Sort field codes:** `last_mod` (default), `ach` (surname), `voo` (first
name), `rol` (role), `pla` (place), `dat` (date). Direction: `asc` or `desc`.

### 2. Parse search results

The response is HTML. Extract data with regex or an HTML parser.

**Hit count:**

```python
import re
hits_match = re.search(r'mi_hits_count">(\d+)<', html)
total = int(hits_match.group(1)) if hits_match else 0
```

If total is 0, the search returned no results.

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

    # For detail lookup, extract micode and minr from data_qr
    micode = re.search(r'micode=([^&]+)', data_qr).group(1)
    minr = re.search(r'minr=([^&]+)', data_qr).group(1)
    miaet = re.search(r'miaet=([^&]+)', data_qr).group(1)
```

**Note:** For DTB search (mizig=323), the table columns differ:
Registratiedatum, Beschrijving, Gemeente.

### 3. Get record details

Use the `data-qr` parameters from a result row, adding `miview=ahd`:

```bash
curl -sk 'https://gemeentearchief.alphenaandenrijn.nl/components/com_maisinternet/maisi_ajax_proxy.php?mivast=105&mizig=100&miadt=105&miaet=54&micode=111.1.08-72&minr=5583710&milang=nl&miview=ahd'
```

The detail response is ~28KB of HTML containing all structured record fields.

**Parse detail fields:**

```python
# Strip script tags
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '|', text)
parts = [p.strip() for p in text.split('|') if p.strip()]

fields = {}
current_label = None
for part in parts:
    if part.endswith(':') and len(part) < 50:
        current_label = part.rstrip(':')
    elif current_label and part not in ('&nbsp;', ''):
        fields[current_label] = part
        current_label = None
```

Typical detail fields include: Aktedatum, Aktenummer, Datum overlijden,
Plaats overlijden, Overledene, Voornaam, Tussenvoegsel, Achternaam, Geslacht,
Geboorteplaats, Woonplaats, Leeftijd, Beroep, Burgerlijke staat, Partner,
Vader, Moeder, Aangever, Gemeente, Opmerkingen.

**Permanent URL:** Extract from the detail HTML:

```python
purl = re.search(r'proxy\.archieven\.nl/105/[A-F0-9]+', html)
```

### 4. Pagination

For large result sets, iterate with `mistart`:

```bash
# Page 1 (results 0-19)
...&mistart=0&miamount=20
# Page 2 (results 20-39)
...&mistart=20&miamount=20
# etc.
```

### 5. Facet filters

The results HTML contains facet filter counts inline. Extract them:

```python
# Bron facets (source type distribution)
bron_facets = re.findall(
    r'mi-filter-alt="([^"]+)"[^>]*>\s*<a[^>]*>([^<]*)\((\d+)\)',
    html
)
# Returns: [('Begraafinschrijving', '...', '24'), ('Geboorteakte', '...', '163'), ...]
```

### Performance

| Operation | Timing | Size |
|-----------|--------|------|
| Search (20 results) | ~0.5s | ~63KB |
| Detail view | ~0.15s | ~28KB |
| DTB search | ~0.3s | ~47KB |

Compared to Playwright: search takes ~15-30s, detail ~5-10s. This is a
**30-100x speedup**.

## Fallback (browser automation)

If the AJAX proxy is unavailable, returns errors, or the HTML structure changes:

### 1. Navigate to person search

**All persons (across all record types):**

```
browser_navigate -> https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=100&miadt=105&miview=tbl&milang=nl
```

**DTB records only (Doop-, trouw- en begraafinschrijvingen):**

```
browser_navigate -> https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=323&miadt=105&miview=tbl&milang=nl
```

**Civil registry only (Burgerlijke Stand):**

```
browser_navigate -> https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=324&miadt=105&miview=tbl&milang=nl
```

### 2. Simple search

Fill in the "Alle velden" textbox and click "Zoek".

URL parameter: `&mizk_alle=knijf`

### 3. Advanced search

Click **"Uitgebreid zoeken"** to expand the advanced search panel.

**Persoon fields:**

| Field | Description |
|-------|-------------|
| Achternaam | Surname |
| Tussenvoegsel | Prefix ("de", "van der", etc.) |
| Voornaam | First name |
| Rol | Role (Dopeling, Vader, Moeder, Getuige, etc.) |

**Overige fields:**

| Field | Description |
|-------|-------------|
| Plaats | Municipality |
| Bron | Source type dropdown |
| Periode | Date range (dd-mm-yyyy, mm-yyyy, or yyyy) |

### 4. Read results

Results table: columns vary by search type.

- **All persons:** Voornaam, Achternaam, Rol, Plaats, Datum
- **DTB:** Registratiedatum, Beschrijving, Gemeente

Facet filters available: Bron, Gemeente (for DTB), Rol (for all persons).

### 5. View record details

Click a result row to expand inline details (same MAIS interface as other
archives). Shows structured data, archive reference, and scan links.

### 6. Scans

Records link to scans when available. The archive holds originals of DTB
records dating from 1661-1812.

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Gemeentearchief Alphen** | Alphen, Aarlanderveen, Benthuizen, Hazerswoude, Koudekerk records |
| Erfgoed Leiden | Leiden, Ter Aar, Nieuwkoop, Hillegom -- does NOT cover Alphen |
| Het Utrechts Archief | Utrecht province (Woerden, Utrecht city) -- does NOT cover Alphen |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik area |

## MAIS platform note

This optimization pattern applies to ALL archives on the MAIS/Archieven.nl
platform. The AJAX proxy path is always:

```
/components/com_maisinternet/maisi_ajax_proxy.php
```

Only the `mivast` and `miadt` values differ per archive. This same technique
can optimize Het Utrechts Archief, Gelders Archief, and any other MAIS-based
archive skill.

## Output format

```
## Gemeentearchief Alphen Result -- [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [reference numbers]
**Scan available:** Yes/No

**Confidence:** Tier B -- official archive record from Gemeentearchief Alphen aan den Rijn
```
