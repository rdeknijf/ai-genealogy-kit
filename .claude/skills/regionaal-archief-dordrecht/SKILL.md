---
name: regionaal-archief-dordrecht
description: |
  Search person records, population registers, civil records, church records,
  and notarial archives at Regionaal Archief Dordrecht (RAD) via HTTP GET on
  the MAIS-Flexis platform. No browser automation needed — plain curl requests.
  Covers Dordrecht, Zwijndrecht, Dubbeldam, Papendrecht, Sliedrecht, and the
  wider Drechtsteden area. 3+ million indexed persons. Use this skill whenever
  researching family lines from the Dordrecht/Zwijndrecht area, looking up
  records that OpenArchieven doesn't have (especially bevolkingsregister entries
  and older DTB records), or when you need scans of population register pages.
  Triggers on: "search Dordrecht archive", "check RAD", "Regionaal Archief
  Dordrecht", "Dordrecht bevolkingsregister", "Zwijndrecht records",
  "/regionaal-archief-dordrecht", or any genealogy research in the Drechtsteden
  area. Key families: van Leeuwen (Dordrecht), Los (Zwijndrecht/Dubbeldam),
  van der Ven (Zwijndrecht). No login required. Parallelizable.
---

# Regionaal Archief Dordrecht (RAD) — MAIS-Flexis HTTP Search

Search 3+ million indexed person records covering Dordrecht, Zwijndrecht,
Dubbeldam, Papendrecht, Sliedrecht, and surrounding Drechtsteden via plain
HTTP GET requests. No browser automation or API key needed.

OpenArchieven indexes some RAD records (archive code `rad`) but misses many
population register entries and older records. This skill searches the RAD
directly for what OpenArchieven doesn't have.

## Person search

```bash
curl -s "https://www.regionaalarchiefdordrecht.nl/archief/?mivast=46&miadt=46&mizig=100&miview=tbl&milang=nl&micols=1&mip1=SURNAME&mip3=FIRSTNAME"
```

### URL parameters

| Parameter | Field | Example |
|-----------|-------|---------|
| `mip1` | Achternaam (surname) | `Los`, `van+Leeuwen` |
| `mip2` | Tussenvoegsel (prefix) | `van`, `de`, `van+der` |
| `mip3` | Voornaam (first name) | `Bertus`, `Herman` |
| `mip4` | Rol (role in document) | `Overledene`, `Bruid` |
| `mip5` | Plaats (place) | `Dordrecht`, `Zwijndrecht` |
| `mibj` | Begin datum (start date) | `1900` or `01-01-1900` |
| `miej` | Eind datum (end date) | `1950` or `31-12-1950` |
| `mivast` | Always `46` | `46` |
| `miadt` | Always `46` | `46` |
| `mizig` | Search type, always `100` for persons | `100` |
| `miview` | `tbl` for table view | `tbl` |
| `milang` | Language | `nl` |
| `micols` | Columns | `1` |

### Wildcards

- `*` matches any string (e.g., `Le*` matches Leeuwen, Lebbing)
- `?` matches single character
- `$` exact match only
- Use quotes for exact phrase: `"van Leeuwen"`

### Parsing results

Results are HTML table rows. Extract data from `<tr>` elements with class
`mi_odd` or `mi_even`:

```python
import re

def parse_rad_results(html):
    """Parse MAIS-Flexis person search results."""
    rows = re.findall(
        r'<tr[^>]*class="mi_(odd|even) rowlink"[^>]*>(.*?)</tr>',
        html, re.DOTALL
    )
    results = []
    for _, row in rows:
        cells = re.findall(r'<td class="mi_value">(.*?)</td>', row, re.DOTALL)
        if len(cells) >= 6:
            # Strip HTML tags from cells
            clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()
            results.append({
                'type': clean(cells[0]),  # Record type (e.g., "Persoon in bevolkingsregister")
                'voornaam': clean(cells[1]),
                'achternaam': clean(cells[2]),
                'rol': clean(cells[3]),
                'plaats': clean(cells[4]),
                'datum': clean(cells[5]),
            })
    return results
```

Also extract the total result count:

```python
total = re.search(r'(\d+)\s*resultaten', html)
count = int(total.group(1)) if total else 0
```

## Detail record

To view a full record, use the detail URL from the search result's `data-qr`
attribute, switching `miview` to `ldt`:

```bash
curl -s "https://www.regionaalarchiefdordrecht.nl/archief/?mivast=46&mizig=100&miadt=46&miview=ldt&milang=nl&mip1=SURNAME&mip3=FIRSTNAME&micode=ARCHIVE_CODE&minr=RECORD_NR&miaet=54"
```

The `micode` and `minr` values come from the search result row's `data-qr`
attribute. Parse them:

```python
qr = row_element.get('data-qr', '')
micode = re.search(r'micode=([^&]+)', qr).group(1)
minr = re.search(r'minr=([^&]+)', qr).group(1)
```

Detail pages contain labeled fields like:
- Voornaam, Achternaam, Geboortedatum, Geboorteplaats
- Vader, Moeder, Partner
- Bron (source), Archief (archive number)

Extract with: `re.findall(r'<th[^>]*>(.*?)</th>.*?<td[^>]*>(.*?)</td>', html)`

## Scan images

Population register scans are linked from detail pages. Look for links
containing `/scans/` or image URLs. The RAD has digitized most population
registers (bevolkingsregister) from 1850-1937.

## Archive codes in RAD

Common `micode` prefixes:

| Code | Collection |
|------|-----------|
| `627.*` | Burgerlijke Stand en Bevolking Zwijndrecht |
| `256.*` | Burgerlijke Stand Dordrecht |
| `11.*` | DTB Dordrecht (Hervormde Kerk) |
| `150.*` | Notarieel Archief Dordrecht |

## Coverage vs OpenArchieven

| What | RAD direct | OpenArchieven (rad) |
|------|-----------|-------------------|
| BS (civil records) | Yes | Yes (mostly) |
| Bevolkingsregister | **Yes — with scans** | Partial (index only) |
| DTB (church records) | Yes | Partial |
| Notarial records | Yes | Some |
| Person search | 3M+ indexed | Subset |

**Use RAD directly when:**
- Searching bevolkingsregister (population register) entries
- You need scan images of register pages
- OpenArchieven returns no results for a Dordrecht/Zwijndrecht person
- Looking for notarial or older DTB records

**Use OpenArchieven when:**
- You need structured JSON output
- Searching across multiple archives simultaneously
- The record type is BS (civil records) — usually well-indexed in OA

## Example searches

### Find Herman van Leeuwen in Dordrecht

```bash
curl -s "https://www.regionaalarchiefdordrecht.nl/archief/?mivast=46&miadt=46&mizig=100&miview=tbl&milang=nl&micols=1&mip1=van+Leeuwen&mip3=Herman&mip5=Dordrecht"
```

### Find Bertus Los in Zwijndrecht, 1920-1950

```bash
curl -s "https://www.regionaalarchiefdordrecht.nl/archief/?mivast=46&miadt=46&mizig=100&miview=tbl&milang=nl&micols=1&mip1=Los&mip3=Bertus&mip5=Zwijndrecht&mibj=1920&miej=1950"
```

### Find all Los marriages in Dordrecht area

```bash
curl -s "https://www.regionaalarchiefdordrecht.nl/archief/?mivast=46&miadt=46&mizig=100&miview=tbl&milang=nl&micols=1&mip1=Los&mip4=Bruidegom"
```

## Contact

- Studiezaal: studiezaal@dordrecht.nl
- Phone: +31 (0)78 - 770 53 48
- For records in privacy period, contact the studiezaal directly
