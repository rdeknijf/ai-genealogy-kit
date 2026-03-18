---
name: online-begraafplaatsen
description: |
  Search Dutch cemetery and grave records on Online Begraafplaatsen
  (online-begraafplaatsen.nl), a database of 1.2M+ persons across 1,700+ Dutch
  cemeteries with gravestone photos. Use this skill whenever looking for burial
  records, grave locations, gravestone inscriptions or photos, death dates from
  cemetery records, or family graves that might reveal unknown family members.
  Triggers on: "check the cemetery records", "find the grave", "search
  begraafplaatsen", "gravestone photo", "/online-begraafplaatsen", or any request
  to look up burial/grave information in the Netherlands. No login required.
---

# Online Begraafplaatsen — Dutch Cemetery Database

Search 1.2 million+ persons across 1,700+ Dutch cemeteries. Many entries include
gravestone photos. Updated daily by volunteers.

No login required for searching and viewing records/photos.

## Important note about Dutch graves

Many Dutch graves are cleared (geruimd) after 20-30 years, so older ancestors may
not be found. Jewish cemeteries are never cleared. Family graves (familiegraven) may
list multiple generations on one stone — useful for discovering unknown family members.

## Search via advanced form

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

The form has a CSRF token, but since Playwright fills and submits in-browser,
this is handled automatically.

### 3. Submit

Click the "Zoek" button. Results appear on the same page.

### 4. Read results

Results appear in a table with columns:

| Column | Content |
|--------|---------|
| naam | Person name (linked to grave detail) |
| geboren | Birth date (dd-mm-yyyy) |
| overleden | Death date (dd-mm-yyyy) |
| lftd | Age at death |
| e.v. | Spouse surname |
| opmerking | Remarks |
| idnr | Person ID |
| aand | Grave plot designation |
| begraafplaats | Cemetery name/location |

Footer shows total count: "Er zijn {N} records gevonden in {time} sec."

Results can be sorted by clicking column headers.

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

## Alternative: autocomplete API

For quick lookups, the site has a public JSON API:

```
GET https://api.online-begraafplaatsen.nl/bgp/V1/PERSselect?term={query}
```

Returns up to 25 results as `[{label: "Knijf de, Jan (-1970)", value: 1061177}]`.
The value is the person ID — navigate to `zerken.asp?p={persid}&redir=canonical`.

Cemetery autocomplete:
```
GET https://api.online-begraafplaatsen.nl/bgp/V1/BGPselect?term={query}
```

These APIs require no authentication and have no CORS restrictions.

## Quirks

- **Windows-1252 encoding** (not UTF-8). Special Dutch characters use Windows-1252.
- **Surname goes WITHOUT prefix** — "Knijf" not "de Knijf". The tussenvoegsel
  has its own field.
- **Photo URLs are session-bound** — served via `showfoto.asp` with signed hashes.
  Cannot be hotlinked; must view in browser.
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
