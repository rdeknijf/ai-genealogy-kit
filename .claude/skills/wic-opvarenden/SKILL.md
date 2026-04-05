---
name: wic-opvarenden
description: |
  Search WIC (West-Indische Compagnie) personnel records at
  westindischecompagnie.info. Two databases: Curacao Soldijboeken 1675-1792
  (3,429 persons) and WIC Personnel 1621-1675 (4,041 persons, 402 ships).
  Also has WIC Military, WIC Ships, Curacao DTB 1659-1800, Curacao Sailors,
  and Aruba marriages 1823-1839. Use this skill when: "search WIC records",
  "West-Indische Compagnie", "WIC crew", "WIC soldier", "sailed to Curacao",
  "Dutch West India Company", "WIC personnel", "/wic-opvarenden", or when
  looking for ancestors who may have sailed with the WIC. No API available —
  HTTP POST + HTML parsing. No login required for search results (detail
  views are restricted).
---

# WIC Opvarenden — West-Indische Compagnie Personnel

Search personnel records of the WIC (Dutch West India Company) at
westindischecompagnie.info. Two main databases covering 1621-1792.

## Access method: HTTP POST + HTML parsing

No JSON API. Submit form data via POST, parse HTML table responses.
Encoding is **Windows-1250** — decode responses accordingly.

## Database 1: Curacao Soldijboeken 1675-1792

3,429 persons from pay ledgers of WIC employees on Curacao.

### Search

```bash
curl -s -X POST "https://www.westindischecompagnie.info/zoek1.php" \
  -d "achternaam=SURNAME&voornaam=&herkomst=" \
  | iconv -f windows-1250 -t utf-8
```

Form fields:

| Field | Description |
|-------|-------------|
| `voornaam` | First name |
| `achternaam` | Surname |
| `herkomst` | Place of origin |

Returns an HTML table with columns: name, ship, rank, year, origin.

### Pagination

Results are paginated at 10 per page. Use the `positie` parameter to
navigate:

```bash
# Page 2 (results 11-20)
curl -s -X POST "https://www.westindischecompagnie.info/zoek1.php" \
  -d "achternaam=SURNAME&voornaam=&herkomst=&positie=10"  \
  | iconv -f windows-1250 -t utf-8

# Page 3 (results 21-30)
curl -s -X POST "https://www.westindischecompagnie.info/zoek1.php" \
  -d "achternaam=SURNAME&voornaam=&herkomst=&positie=20" \
  | iconv -f windows-1250 -t utf-8
```

### Example

```bash
# Search for surname "Knijf" in Curacao Soldijboeken
curl -s -X POST "https://www.westindischecompagnie.info/zoek1.php" \
  -d "achternaam=Knijf&voornaam=&herkomst=" \
  | iconv -f windows-1250 -t utf-8
```

## Database 2: WIC Personnel 1621-1675

4,041 persons across 402 ships from the early WIC period.

### Search

```bash
curl -s -X POST "https://www.westindischecompagnie.info/wic1personeel.php" \
  -d "achternaam=SURNAME&voornaam=&geboorteplaats=" \
  | iconv -f windows-1250 -t utf-8
```

Form fields:

| Field | Description |
|-------|-------------|
| `voornaam` | First name |
| `achternaam` | Surname |
| `geboorteplaats` | Place of birth |

Returns an HTML table with columns: name, origin, rank, date, WIC chamber.

### Pagination

Same as Database 1 — 10 per page, `positie` parameter:

```bash
curl -s -X POST "https://www.westindischecompagnie.info/wic1personeel.php" \
  -d "achternaam=SURNAME&voornaam=&geboorteplaats=&positie=10" \
  | iconv -f windows-1250 -t utf-8
```

### Example

```bash
# Search for surname "Knijf" in WIC Personnel 1621-1675
curl -s -X POST "https://www.westindischecompagnie.info/wic1personeel.php" \
  -d "achternaam=Knijf&voornaam=&geboorteplaats=" \
  | iconv -f windows-1250 -t utf-8
```

## Parsing HTML results

Results come as HTML tables. Extract data with Python or grep. Example
Python parser:

```python
import subprocess, re
from html import unescape

def search_wic_curacao(achternaam="", voornaam="", herkomst=""):
    """Search Curacao Soldijboeken 1675-1792."""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://www.westindischecompagnie.info/zoek1.php",
         "-d", f"achternaam={achternaam}&voornaam={voornaam}&herkomst={herkomst}"],
        capture_output=True
    )
    html = result.stdout.decode("windows-1250")
    # Parse rows from HTML table
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    for row in rows:
        cells = [unescape(re.sub(r"<[^>]+>", "", c).strip())
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)]
        if cells:
            print(cells)

def search_wic_personnel(achternaam="", voornaam="", geboorteplaats=""):
    """Search WIC Personnel 1621-1675."""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://www.westindischecompagnie.info/wic1personeel.php",
         "-d", f"achternaam={achternaam}&voornaam={voornaam}&geboorteplaats={geboorteplaats}"],
        capture_output=True
    )
    html = result.stdout.decode("windows-1250")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    for row in rows:
        cells = [unescape(re.sub(r"<[^>]+>", "", c).strip())
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)]
        if cells:
            print(cells)
```

## Additional databases on the site

The site also hosts these databases (same POST + HTML pattern):

| Database | Endpoint | Coverage |
|----------|----------|----------|
| WIC Military | `wic1militair_plus.php` | WIC military personnel |
| WIC Ships | `wic1schepen_plus.php` | 402 WIC ships |
| Curacao DTB | (church records) | Curacao baptisms/marriages/burials 1659-1800 |
| Curacao Sailors | (maritime records) | Curacao maritime personnel |
| Aruba Marriages | (civil records) | Aruba marriages 1823-1839 |

These can be searched with the same POST + HTML parsing approach. Explore
the site navigation for exact endpoints if needed.

## Detail views — restricted access

Clicking a result row opens a detail popup (`popup9.php` or similar) which
requires a login. The popup shows "Beperkte toegang" (restricted access).
List-level results (name, rank, ship, year, origin) are freely accessible
without login.

## Limitations

- **No API.** HTTP POST with HTML table responses only.
- **Encoding:** Windows-1250, must decode explicitly.
- **10 results per page.** Must paginate with `positie` parameter.
- **Detail views locked.** Only summary data is freely available.
- **Small database.** 3,429 + 4,041 = ~7,470 total persons.
- **No scans.** No links to original document images.

## Output format

```
## WIC Personnel Record

**Name:** [voornaam] [achternaam]
**Origin:** [herkomst / geboorteplaats]
**Rank:** [rank/function]
**Ship:** [ship name]
**Year/Date:** [year or date]
**WIC Chamber:** [chamber, if available]
**Database:** Curacao Soldijboeken 1675-1792 / WIC Personnel 1621-1675

**Source:** westindischecompagnie.info
**Confidence:** Tier C — secondary indexed source, no scan available
```
