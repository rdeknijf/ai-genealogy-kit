---
name: online-begraafplaatsen-optimized
description: |
  Search Dutch cemetery and grave records on Online Begraafplaatsen
  (online-begraafplaatsen.nl), a database of 1.2M+ persons across 1,700+ Dutch
  cemeteries with gravestone photos. Uses direct HTTP calls (autocomplete JSON API
  + form POST + HTML parsing) instead of browser automation. Use this skill whenever
  looking for burial records, grave locations, gravestone inscriptions or photos,
  death dates from cemetery records, or family graves that might reveal unknown
  family members. Triggers on: "check the cemetery records", "find the grave",
  "search begraafplaatsen", "gravestone photo", "/online-begraafplaatsen", or any
  request to look up burial/grave information in the Netherlands. No login required.
---

# Online Begraafplaatsen — Dutch Cemetery Database

Search 1.2 million+ persons across 1,700+ Dutch cemeteries. Many entries include
gravestone photos. Updated daily by volunteers.

No login required for searching and viewing records/photos.

## Important note about Dutch graves

Many Dutch graves are cleared (geruimd) after 20-30 years, so older ancestors may
not be found. Jewish cemeteries are never cleared. Family graves (familiegraven) may
list multiple generations on one stone — useful for discovering unknown family members.

## Primary method: HTTP API + HTML parsing

### Quick search: Autocomplete JSON API

For simple surname lookups, use the public JSON API directly:

```bash
curl -s 'https://api.online-begraafplaatsen.nl/bgp/V1/PERSselect?term=Knijf'
```

Returns up to 25 results as JSON:

```json
[
  {"label": "Knijf de, Jacob (1924-1968)", "value": 1194484},
  {"label": "Knijf de, Jan (-1970)", "value": 1061177}
]
```

- `label` — person name with prefix, first name, and years
- `value` — person ID (use for detail page lookup)
- No authentication needed, no CORS restrictions
- Limit: 25 results max, single search term only

Cemetery autocomplete also available:

```bash
curl -s 'https://api.online-begraafplaatsen.nl/bgp/V1/BGPselect?term=Bennekom'
```

### Advanced search: Form POST with CSRF

For searches with separate surname/prefix/first name/cemetery fields and
unlimited results, replicate the search form via curl:

**Step 1: Get CSRF token + session cookie**

```bash
COOKIE_JAR=$(mktemp)
CSRF=$(curl -s -c "$COOKIE_JAR" 'https://www.online-begraafplaatsen.nl/zoeken.asp' \
  | grep -oP 'CSRFToken" value="\K[^"]+')
```

**Step 2: POST the search form**

```bash
curl -s -b "$COOKIE_JAR" \
  'https://www.online-begraafplaatsen.nl/zoeken.asp?command=zoekform' \
  -X POST \
  -d "CSRFToken=$CSRF&Achternaam=Knijf&tussenvoegsel=de&voornaam=Jan&Select1=0&submitbutton=Zoek"
```

Form fields:

| Field | Parameter | Notes |
|-------|-----------|-------|
| Surname | `Achternaam` | WITHOUT prefix. Wildcards `*` and `?` supported |
| Prefix | `tussenvoegsel` | "de", "van der", etc. Single space = no prefix |
| First name | `voornaam` | Wildcards supported |
| Cemetery | `Select1` | Value `0` = all cemeteries |

**Step 3: Parse HTML results**

Results are in `<tr>` rows. Each row contains:

| Column | Content |
|--------|---------|
| naam | Person name with links to detail page |
| geboren | Birth date (dd-mm-yyyy) |
| overleden | Death date (dd-mm-yyyy) |
| lftd | Age at death |
| e.v. | Spouse surname |
| opmerking | Remarks |
| idnr | Person ID |
| aand | Grave plot designation |
| begraafplaats | Cemetery name/location |

Each result has a canonical link: `/graf/{grafid}/{persid}/{Slug}`

Footer shows total: "Er zijn {N} records gevonden in {time} sec."

### View grave detail: WebFetch

Fetch the canonical URL directly — no browser needed:

```
WebFetch → https://www.online-begraafplaatsen.nl/graf/{grafid}/{persid}/{Slug}
```

Ask WebFetch to extract: person names, birth/death dates, ages, cemetery name
and location, plot designation, photo availability, and other persons on the
same grave (family grave members).

The canonical URL is found in search results as `href="/graf/{grafid}/{persid}/{Slug}"`.
If you only have a person ID from the autocomplete API, use the redirect:

```
WebFetch → https://www.online-begraafplaatsen.nl/zerken.asp?p={persid}&redir=canonical
```

## Fallback: Playwright browser automation

Use browser only when:

- Photo viewing is needed (photo URLs are session-bound via `showfoto.asp`)
- The HTTP method returns errors or the site blocks non-browser requests
- Complex interaction with cemetery selection dropdown is required

### 1. Navigate to advanced search

```
browser_navigate → https://www.online-begraafplaatsen.nl/zoeken.asp
```

### 2. Fill the search form

| Field | HTML id | Type | Notes |
|-------|---------|------|-------|
| Achternaam (Surname) | `Achternaam` | text | WITHOUT prefix. Wildcards `*` and `?` supported |
| Tussenvoegsel (Prefix) | `tussenvoegsel` | text | "de", "van der", etc. Single space = no prefix |
| Voornaam (First name) | `voornaam` | text | Wildcards supported |
| Begraafplaats (Cemetery) | `Select1` | select | Value `0` = all cemeteries. 1000+ options |

### 3. Submit

Click the "Zoek" button. Results appear on the same page.

### 4. Read results

Results table and detail page structure are the same as described in the
HTTP method above.

### 5. View grave detail

Click a name to go to the grave detail page.

URL pattern: `/graf/{grafid}/{persid}/{Slug}`

The detail page shows:

**Photo section:**

- Gravestone photo (if available) — click to zoom
- "Er is helaas GEEN foto beschikbaar" if no photo exists

**Person data table:**

- Naam, Geboren, Overleden, Leeftijd
- Multiple persons may appear on one grave (family graves — these are very useful
  for discovering unknown relatives)

**Grave metadata:**

- Begraafplaats (cemetery) with link to cemetery page
- Graf id-nummer
- Begraafplaatsnr
- (Plaats)aanduiding (plot designation, e.g., "07.F.39")

## Quirks

- **Windows-1252 encoding** (not UTF-8). Special Dutch characters use Windows-1252.
- **Surname goes WITHOUT prefix** — "Knijf" not "de Knijf". The tussenvoegsel
  has its own field.
- **Photo URLs are session-bound** — served via `showfoto.asp` with signed hashes.
  Cannot be hotlinked; must view in browser.
- **Autocomplete API max 25 results** — use the form POST for complete results.
- **No pagination observed** — all results appear on one page.
- **No iframes.** Content is plain server-rendered HTML (classic ASP).

## Output format

```
## Online Begraafplaatsen Result

**Person:** [name]
**Born:** [date]
**Died:** [date], age [age]
**Spouse:** [name if shown]

**Cemetery:** [name and location]
**Plot:** [designation]
**Photo:** [available / not available]

**Other persons on grave:** [list if family grave — names, birth/death dates]

**Confidence:** Tier B — volunteer-indexed cemetery record
```
