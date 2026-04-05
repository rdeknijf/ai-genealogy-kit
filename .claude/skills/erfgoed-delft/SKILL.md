---
name: erfgoed-delft
description: |
  Search indexed person records, civil registry, church records (DTB),
  population registers, and notarial archives at Stadsarchief Delft
  (zoeken.stadsarchiefdelft.nl) via HTTP GET on clean URLs with session
  cookie. No browser automation needed for search — plain curl requests
  with a session cookie return full HTML results. Covers Delft,
  Midden-Delfland, Pijnacker-Nootdorp, Rijswijk, Maasland, and
  Schipluiden. Part of Erfgoed Delft. 185+ Knijf person records found,
  including BS, DTB, bevolkingsregister, and notarial records. Record
  types include DTB dopen/trouwen/begraven, BS geboorten/huwelijken/
  overlijden, bevolkingsregister, ingekomen en vertrokken personen,
  and notariele akten. Scans available for most records. Triggers on:
  "search Delft archive", "Stadsarchief Delft", "Erfgoed Delft",
  "Delft records", "Maasland records", "Schipluiden records",
  "Midden-Delfland records", "Pijnacker records", "Rijswijk archive",
  "/erfgoed-delft", or any genealogy research in the Delft/
  Midden-Delfland area. No login required. Parallelizable — run
  multiple queries simultaneously (each needs its own session cookie).
---

# Stadsarchief Delft — Erfgoed Delft

Search indexed person records from Stadsarchief Delft via clean URL
searches with session cookie. Returns HTML results that are easily
parsed — no browser automation needed for search and result extraction.

No login required. A session cookie from any GET request is sufficient.

## Coverage

**Archive for:** Delft, Midden-Delfland, Pijnacker-Nootdorp, Rijswijk

**Municipalities in records:** Delft, Maasland, Schipluiden,
Pijnacker, Nootdorp, Rijswijk

**Record types:**

- **DTB** (doop-, trouw- en begraafboeken) — church records pre-1811
- **BS** (Burgerlijke Stand) — civil registry post-1811: births,
  marriages, deaths
- **Bevolkingsregister** — population registers
- **Ingekomen en vertrokken personen** — arrival/departure registers
- **Notariele akten** — notarial records

**Platform:** DeventIT Atlantis Web

## Access method

**Clean URL search with session cookie** — the search results page uses
a predictable URL pattern that works with a simple GET request after
establishing a session cookie. No CSRF token needed for the search
itself. Response is HTML, parsed with regex.

**Speed:** ~200-500ms per search (HTML response, no API overhead)

## Workflow

### 1. Establish session cookie

Before any search, make one GET request to establish a PHP session:

```bash
curl -s -c /tmp/delft.jar 'https://zoeken.stadsarchiefdelft.nl/zoeken.php' > /dev/null
```

The cookie jar persists across searches in the same session.

### 2. Person search

Search using the clean URL pattern. All parameters go in the URL path:

```bash
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Voornaam=FIRSTNAME/Achternaam=SURNAME/aantalpp=50/' \
  2>&1
```

**URL parameters (path segments):**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `groep=Personen` | Search category (always `Personen` for genealogy) | `groep=Personen` |
| `Voornaam=X` | First name | `Voornaam=Teunisje` |
| `Achternaam=X` | Surname | `Achternaam=Brouwer` |
| `Tussenvoegsel=X` | Prefix (de, van, van der) | `Tussenvoegsel=de` |
| `Patroniem=X` | Patronymic | `Patroniem=Cornelisdr` |
| `Rol=X` | Role in record | `Rol=bruidegom` |
| `Datering=X` | Date range start | `Datering=1920` |
| `Plaats=X` | Place | `Plaats=Delft` |
| `Archiefnummer=X` | Archive number | `Archiefnummer=15` |
| `aantalpp=N` | Results per page (default 14) | `aantalpp=50` |

**Example searches:**

```bash
# Search for Teunisje Brouwer
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Voornaam=Teunisje/Achternaam=Brouwer/aantalpp=50/'

# Search for all Knijf records
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Achternaam=Knijf/aantalpp=50/'

# Search for Knijf with prefix "de"
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Tussenvoegsel=de/Achternaam=Knijf/aantalpp=50/'

# Search for Johannes Vermeer
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Voornaam=Johannes/Achternaam=Vermeer/aantalpp=50/'
```

### 3. Parse search results

Results are HTML table rows. Extract with this Python code:

```python
import re

def parse_delft_results(html):
    """Parse Stadsarchief Delft person search results."""
    clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()

    # Total results
    total_match = re.search(r'Resultaten in Personen:\s*(\d+)', html)
    total = int(total_match.group(1)) if total_match else 0

    # Extract detail IDs and result rows
    results = []
    rows = re.findall(
        r'<tr[^>]*class="custom-table-row[^"]*"[^>]*>(.*?)</tr>',
        html, re.DOTALL
    )
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        cells_clean = [clean(c) for c in cells]

        # Extract detail ID from link
        detail_match = re.search(r'detail\.php\?[^"]*id=(\d+)', row)
        detail_id = detail_match.group(1) if detail_match else None

        if len(cells_clean) >= 7:
            results.append({
                'detail_id': detail_id,
                'achternaam': cells_clean[1],
                'tussenvoegsel': cells_clean[2],
                'voornaam': cells_clean[3],
                'rol': cells_clean[4],
                'plaats': cells_clean[5],
                'datum': cells_clean[6],
                'bron': cells_clean[7] if len(cells_clean) > 7 else '',
            })

    return {'total': total, 'results': results}
```

**Column order in result table:**

| Column | Field |
|--------|-------|
| 0 | Detail link |
| 1 | Achternaam (surname) |
| 2 | Tussenvoegsel (prefix) |
| 3 | Voornaam (first name) |
| 4 | Rol (role) |
| 5 | Plaats (place) |
| 6 | Datum (date) |
| 7 | Bron (source type) |

### 4. Get record detail

Fetch full record details by ID:

```bash
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/detail.php?nav_id=0-1&id=DETAIL_ID&index=0'
```

**Parse detail fields:**

```python
def parse_delft_detail(html):
    """Parse Stadsarchief Delft detail page."""
    clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()

    # Extract key-value fields
    fields = {}
    pairs = re.findall(
        r'<td\s+class="key"[^>]*>(.*?)</td>\s*<td\s+class="value"[^>]*>(.*?)</td>',
        html, re.DOTALL
    )
    for label, value in pairs:
        l = clean(label).replace('\xa0', '').strip()
        v = clean(value)
        if l and v:
            fields[l] = v

    # Extract persons (links with target="_blank" to detail.php)
    persons = []
    person_links = re.findall(
        r'<a\s+href="[^"]*detail\.php\?[^"]*id=(\d+)[^"]*"[^>]*target="_blank"[^>]*>(.*?)</a>',
        html
    )
    for pid, name_html in person_links:
        name = clean(name_html)
        if '(' in name:
            persons.append({'id': pid, 'name': name})

    # Extract scan image URL
    scans = re.findall(r'(HttpHandler/[^"]+\.jpg)', html)
    scan_urls = list(set(
        f'https://zoeken.stadsarchiefdelft.nl/{s}' for s in scans
    ))

    return {
        'fields': fields,
        'persons': persons,
        'scan_urls': scan_urls,
    }
```

**Common detail fields:**

| Field | Description |
|-------|-------------|
| `Soort akte` | Record type (Burgerlijke Stand, DTB, etc.) |
| `Bron` | Source (BS huwelijken, BS geboorten, DTB dopen, etc.) |
| `Inventarisnummer` | Archive reference (e.g., 15.272) |
| `Nummer` | Akte/record number |
| `Datum` | Date of record |
| `Plaats` | Place |
| `Datum huwelijk` | Marriage date (ISO format, on marriage records) |

### 5. Access scan images

Scans are served from the `HttpHandler` path:

```
https://zoeken.stadsarchiefdelft.nl/HttpHandler/AR{archief}_{inventaris}_{page}.jpg
```

Example: `https://zoeken.stadsarchiefdelft.nl/HttpHandler/AR0015_00272_154v.jpg`

The scan URL is found in the detail page HTML. No authentication needed
to view scans.

### 6. Pagination

Add `pagina=N` to the URL path (0-based page number):

```bash
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Achternaam=Knijf/aantalpp=50/pagina=1/'
```

### 7. Filter by record type

Apply filters via query parameters on the result page:

```bash
# Filter by Burgerlijke Stand only
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Achternaam=Knijf/aantalpp=50/?filters%5BSoort%20Akte%5D%5B%5D=Burgerlijke%20Stand'

# Filter by Bevolking (population register)
curl -s -b /tmp/delft.jar -L \
  'https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Achternaam=Knijf/aantalpp=50/?filters%5BSoort%20Akte%5D%5B%5D=Bevolking'
```

**Available filters (from facets):**

| Filter | Values |
|--------|--------|
| `Soort Akte` | `Burgerlijke Stand`, `Bevolking`, `DTB`, `Notarieel` |
| `Bron` | `BS geboorten`, `BS huwelijken`, `BS overlijden`, `DTB dopen`, `DTB trouwen`, `DTB begraven`, `bevolkingsregister`, `Notariele akte` |
| `PlaatsFilter` | `Delft`, `Maasland`, `Schipluiden`, etc. |
| `Periode` | `1600 - 1619`, `1900 - 1919`, `1920 - 1939`, etc. |

### 8. Build website URL for user reference

**Search results:**

```
https://zoeken.stadsarchiefdelft.nl/zoeken/groep=Personen/Voornaam=X/Achternaam=Y/aantalpp=14/
```

**Single record detail:**

```
https://zoeken.stadsarchiefdelft.nl/detail.php?id=RECORD_ID
```

## Wildcard and spelling

The search supports spelling variants by default (similar to other
Dutch archive platforms). For exact matches, try quotes or specific
field combinations. The surname `Knijf` will also match `de Knijf`
and `van der Knijf`.

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Stadsarchief Delft** | Delft, Maasland, Schipluiden, Pijnacker, Rijswijk records |
| Gemeentearchief Alphen | Alphen aan den Rijn area |
| Erfgoed Leiden | Leiden, Ter Aar, Nieuwkoop |
| Streekarchief Midden-Holland | Gouda, Haastrecht, Schoonhoven |
| Het Utrechts Archief | Utrecht province |
| WieWasWie | National coverage (but may miss Delft-specific records) |

## Fallback (browser automation)

If the clean URL search stops working (e.g., session handling changes),
fall back to Playwright browser automation at
`https://zoeken.stadsarchiefdelft.nl/zoeken.php?overzicht=alles`:

1. Open the page, dismiss cookie banner
2. Use JavaScript to uncheck all groups, then check only Personen:
   ```
   eval "(function(){ var cbs=document.querySelectorAll('input.beschrijvingsgroep.root'); cbs.forEach(function(cb){if(cb.checked){cb.click();}}); var p=document.getElementById('beschrijvingsgroep-152287426'); if(p && !p.checked) { p.click(); } return 'done'; })()"
   ```
3. Wait for AJAX to load form fields (~2s)
4. Fill Voornaam and Achternaam textboxes
5. Click the "Zoeken" button in the form

## Output format

```
## Stadsarchief Delft Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Archief [nr], Inventarisnummer [inv], Akte [nr]
**Scan available:** Yes/No
**Scan URL:** [image URL if available]
**Web link:** https://zoeken.stadsarchiefdelft.nl/detail.php?id=[ID]

**Confidence:** Tier B — official archive record from Stadsarchief Delft
```

## Limitations

- **Session cookie required:** Each curl session needs a prior GET to
  establish a PHP session cookie. The cookie expires after ~24 minutes
  of inactivity.
- **HTML parsing required:** No JSON API — results are HTML that must
  be parsed with regex. The parsing is reliable but not as clean as
  Memorix/Picturae API responses.
- **No full-text search of record content:** Only indexed fields
  (name, date, place, role) are searchable. Transcription notes in
  scans are not indexed.
- **Pagination uses page numbers:** `aantalpp` controls items per page,
  `pagina` is the 0-based page number.
- **Detail page requires nav_id:** The `nav_id=0-1` parameter links
  the detail page to the search context. Using `nav_id=0-1` works for
  direct access; the `index` parameter is optional.
- **Spelling variants:** Pre-1811 records use variable spellings.
  Search for both `Knijf` and `van der Knijf`, `Knijff`, etc.
