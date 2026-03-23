---
name: wiewaswie
description: |
  Search Dutch civil registry records (births, marriages, deaths) on WieWasWie.nl
  via direct JSON API calls, with Open Archives API as a secondary source and
  Playwright browser automation as fallback. Use this skill whenever you need to
  look up or verify a person in Dutch civil records, check a birth/marriage/death
  date against official archives, or find parents/spouses from indexed Burgerlijke
  Stand records. Triggers on: "look up on wiewaswie", "check the birth record",
  "find the marriage certificate", "verify this date in the civil registry",
  "/wiewaswie", or any request to search Dutch genealogical records for a specific
  person. Also use when comparing GEDCOM data against official sources or when a
  Tier B verification is needed.
---

# WieWasWie Lookup

Search the WieWasWie database (252M+ indexed Dutch civil registry records) using
direct HTTP API calls. This returns official archive-indexed data -- Tier B
confidence in the genealogy project's verification framework.

## What to extract from the user's request

- **surname** (required)
- **prefix** -- tussenvoegsel like "de", "van", "van de" (optional)
- **first_name** (optional)
- **patronymic** (optional)
- **place** (optional)
- **year_from** / **year_to** (optional)
- **document_type** -- BS Geboorte, BS Huwelijk, BS Overlijden (optional)

## Primary method: WieWasWie JSON API

WieWasWie exposes a hidden JSON API that the Angular frontend uses. This is
the same data as the browser UI but returns in ~0.2 seconds instead of ~20
seconds via Playwright.

### Step 1: Search for records

Make a POST request to the WieWasWie search API:

```bash
curl -s -X POST "https://www.wiewaswie.nl/Umbraco/Api/nl-NL/Service/GetSearchResults" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (compatible; genealogy-research/1.0)" \
  -d '{
    "SearchTerm": "",
    "Page": 1,
    "IsAdvancedSearch": true,
    "PersonA": {
      "Achternaam": "<SURNAME>",
      "Tussenvoegsel": "<PREFIX_OR_EMPTY>",
      "Voornaam": "<FIRSTNAME_OR_EMPTY>",
      "Patroniem": "<PATRONYMIC_OR_EMPTY>",
      "Beroep": "",
      "Rol": "",
      "VoornaamSearchType": 3,
      "TussenvoegselSearchType": 3,
      "AchternaamSearchType": 3,
      "PatroniemSearchType": 3,
      "BeroepSearchType": 3,
      "WithoutTussenvoegsel": false
    },
    "PersonB": {
      "Voornaam": "",
      "Tussenvoegsel": "",
      "Achternaam": "",
      "Patroniem": "",
      "Beroep": "",
      "Rol": "",
      "VoornaamSearchType": 3,
      "TussenvoegselSearchType": 3,
      "AchternaamSearchType": 3,
      "PatroniemSearchType": 3,
      "BeroepSearchType": 3,
      "WithoutTussenvoegsel": false
    },
    "PeriodeVan": "<YEAR_FROM_OR_EMPTY>",
    "PeriodeTot": "<YEAR_TO_OR_EMPTY>",
    "Land": "",
    "Regio": "",
    "Plaats": "<PLACE_OR_EMPTY>",
    "PlaatsSearchType": 3,
    "DocumentType": "<DOCTYPE_OR_EMPTY>",
    "SortColumn": "lastname.sort",
    "SortDirection": 1,
    "FacetCollectieGebied": "",
    "FacetOrganisatie": "",
    "FacetRol": ""
  }'
```

**SearchType values:** 1 = StartsWith, 2 = Synonym, 3 = Exact

**DocumentType values:** "BS Geboorte", "BS Huwelijk", "BS Overlijden", or "" for all.

**Response structure:**

```json
{
  "Total": 5,
  "Persons": [
    {
      "SourceDocumentId": "55972978",
      "PersonId": "55972978|1",
      "Voornaam": "Gijsbert",
      "HasTussenvoegsel": true,
      "Tussenvoegsel": "de",
      "Achternaam": "Knijf",
      "Patroniem": "",
      "AktePlaats": "Ede",
      "AkteDatum": "11-11-1848",
      "DocumentType": "BS Geboorte",
      "HasScan": false
    }
  ],
  "Message": "",
  "Aggs": { ... }
}
```

The `Aggs` field contains facet counts for Role, Organization, Sourcetype, and
CollectionRegion, plus min/max date ranges. These help narrow searches.

### Step 2: Get record details

Fetch the detail page using the `SourceDocumentId`. This requires a session
cookie from WieWasWie (the detail page returns 403 without one).

**Get a session cookie first (one-time per session):**

```bash
curl -s -c /tmp/wiewaswie_cookies.txt -L "https://www.wiewaswie.nl/nl/zoeken/" \
  -H "User-Agent: Mozilla/5.0 (compatible; genealogy-research/1.0)" -o /dev/null
```

**Fetch the detail page:**

```bash
curl -s -b /tmp/wiewaswie_cookies.txt \
  "https://www.wiewaswie.nl/nl/detail/<SourceDocumentId>" \
  -H "User-Agent: Mozilla/5.0 (compatible; genealogy-research/1.0)"
```

Parse the HTML for `<dt>` / `<dd>` pairs. The detail page contains:

**BS Geboorte (birth):**

- Kind (child name), Geslacht (gender)
- Vader (father) with Beroep (occupation) and Leeftijd (age)
- Moeder (mother) with Beroep
- Gebeurtenis, Datum (event date), Gebeurtenisplaats (event place)
- Documenttype, Erfgoedinstelling, Archief, Registratienummer, Aktenummer
- Registratiedatum, Akteplaats, Collectie, Boek

**BS Huwelijk (marriage):**

- Bruidegom (groom) and Bruid (bride) with age, birthplace, occupation
- Parents of both (Vader/Moeder bruidegom, Vader/Moeder bruid)
- Event date and place, archive references

**BS Overlijden (death):**

- Overledene (deceased) with age, Partner, Vader/Moeder
- Event date and place, archive references

### Step 3: Parse the detail HTML

Use Python or grep to extract `<dt>/<dd>` pairs from the HTML:

```python
import re
html_content = "..."  # the fetched HTML
pairs = re.findall(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>', html_content, re.DOTALL)
for label, value in pairs:
    label = re.sub(r'<[^>]+>', '', label).strip()
    value = re.sub(r'<[^>]+>', '', value).strip()
    print(f"{label}: {value}")
```

Also extract links from `<dd>` elements -- these contain links to related
records and to the original scan at the archive's website.

## Secondary method: Open Archives API

Open Archives (openarchieven.nl) provides a free REST API that covers many
of the same records. Use it as a complement or when WieWasWie API is down.
Especially useful because it provides direct URLs to archive detail pages.

**Search endpoint:**

```
GET https://api.openarchieven.nl/1.1/records/search.json?name=<query>&lang=nl&number_show=20
```

**Parameters:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| name | Search query (supports year: "de Knijf 1848") | de Knijf |
| name | Year range in name | de Knijf 1848-1900 |
| eventplace | Filter by place | Ede |
| sourcetype | Filter by source type | BS Geboorte |
| number_show | Results per page (max 100) | 20 |
| start | Pagination offset | 0 |
| sort | Sort column (1-6, negative=desc) | 1 |
| lang | Language (nl/en) | nl |

**Rate limit:** 4 requests per second per IP.

**Response fields per result:** personname, relationtype, eventtype, eventdate
(with day/month/year), eventplace, sourcetype, archive name, archive_code,
and a URL to the Open Archives detail page.

**Record detail:**

```
GET https://api.openarchieven.nl/1.1/records/show.json?archive_code=<code>&identifier=<id>&lang=nl
```

The show endpoint returns less detail than WieWasWie (typically just names,
dates, document numbers, and scan URLs -- no parents/ages/occupations). Use
it mainly for the scan links and archive references.

**Match endpoint (for quick person matching):**

```
GET https://api.openarchieven.nl/1.0/records/match.json?name=<surname>&birthyear=<year>&lang=nl
```

## Fallback: Playwright browser automation

If both APIs fail (e.g., server maintenance, rate limiting, unexpected errors),
fall back to the original browser workflow.

### 1. Navigate to advanced search

```
browser_navigate -> https://www.wiewaswie.nl/nl/zoeken/?advancedsearch=1
```

### 2. Fill the search form

Use `browser_fill_form` with these fields:

| Field | Label | Type | Notes |
|-------|-------|------|-------|
| Surname | "Achternaam" | textbox | |
| Prefix | "Tussenvoegsel" | textbox | "de", "van", etc. |
| First name | "Voornaam" | textbox | |
| Patronymic | "Patroniem" | textbox | |
| Year from | first spinbutton | spinbutton | These are spinbuttons, not textboxes |
| Year to | second spinbutton | spinbutton | Same -- spinbutton |
| Place | "Plaats" | textbox | Use the municipality name |

### 3. Submit and read results

Click the "Zoek" button, then take a snapshot. Results appear as a table:
Achternaam, Voornaam, Patroniem, Plaats, Datum, Documenttype, Scan.

### 4. Open a result's details

Click the result row. The detail view loads **inside an iframe** -- take a
snapshot after clicking to read its content.

### 5. Extract structured data

The iframe uses term/definition pairs (`<dt>`/`<dd>`). See the detail field
descriptions above.

## Birth date vs registration date

Dutch civil records carry two dates, and confusing them is a common source
of errors in family trees:

- **Gebeurtenisdatum** = the actual event date (when the baby was born)
- **Registratiedatum** = when the event was declared at the town hall

Births were typically registered 1-3 days after the actual birth. The search
results in WieWasWie show the *registration* date (AkteDatum). The detail view
shows both. For GEDCOM, use the **gebeurtenisdatum** (the actual birth date).

## Place names

Dutch civil records use the **municipality** (gemeente), not the village.
If a village name returns no results, try the municipality instead:

- Bennekom, Lunteren, Otterlo -> **Ede**
- Voorthuizen, Garderen, Barneveld village, Harselaar -> **Barneveld**
- Zwartebroek -> **Barneveld** or **Nijkerk**

## Output format

```
## WieWasWie Result -- [document type]

**Person:** [name]
**Event:** [type], [gebeurtenisdatum] in [gebeurtenisplaats]
**Registered:** [registratiedatum] in [akteplaats]

**Father:** [name], [occupation], age [age]
**Mother:** [name], [occupation]

**Archive:** [erfgoedinstelling], archief [nr], reg [nr], akte [nr]
**Collection:** [collectie]
**Scan:** [naar bron URL if available]
**Linked records:** [list any gelinkte akten]

**Confidence:** Tier B -- official civil registry record from [archive name]
```

## Pre-1811 DTB records: patronymic search technique

**Critical insight:** Before ~1811, Dutch church records (DTB) used patronymics
(father's first name as child's surname), not fixed family surnames. WieWasWie
indexes these records under the patronymic form, so **surname searches fail**
for people born before ~1780.

**Example:** Hendrik Jeths (b. 1767) is indexed as "Hendrik Aarts Jets" --
patronymic "Aarts" (son of Aart) + variant spelling "Jets". Searching for
surname "Jeths" returns zero results.

### The technique

Instead of searching by surname, search by **first name + role + place + date range**:

```json
{
  "PersonA": {
    "Voornaam": "Hendrik",
    "Achternaam": "",
    "Rol": "kind"
  },
  "PeriodeVan": "1765",
  "PeriodeTot": "1770",
  "Plaats": "Beekbergen",
  "DocumentType": "DTB Dopen"
}
```

This returns ALL children named Hendrik baptized in Beekbergen 1765-1770.
Scan the results for patronymics matching the expected father's name.

### When to use this technique

- Person born before ~1780 (patronymic era)
- DocumentType is DTB Dopen, DTB Trouwen, or DTB Begraven
- Standard surname search returns 0 results
- You know the person's first name and approximate location/date

### Patronymic patterns to recognize

| Indexed name | Meaning | Family surname |
|-------------|---------|----------------|
| Hendrik Aarts Jets | Hendrik, son of Aart Jets | Jeths |
| Aart Rijkse | Aart, son of Rijk | Jeths |
| Rijk Aarts | Rijk, son of Aart | Jeths |
| Aert Isacks | Aert, son of Isaac | Jeths |
| Jan Riksen | Jan, son of Rijk | Jeths |

The surname "Jets/Jeths/Jethsen" appears intermittently alongside patronymics.
Church records may use surname, patronymic, or both depending on the minister.

### Verified results

This technique found 4 baptism records in the Jeths line (1666-1767) that
were invisible to surname searches, enabling verification back to 1666.

## Recommended workflow for hardening runs

For batch lookups (e.g., verifying an entire family line), use this sequence:

1. **Search via WieWasWie API** -- fast (~0.2s), returns SourceDocumentIds
2. **Get session cookie once** -- curl to /nl/zoeken/, save cookie jar
3. **Fetch details in sequence** -- curl each /nl/detail/{id} with cookie
4. **Cross-reference with Open Archives** -- for scan URLs and alternative
   archive references

Each lookup takes ~0.5s total (search + detail) vs ~20s with Playwright.
For a 30-person hardening run, that is ~15 seconds vs ~10 minutes.

## Known indexing gaps

Not all civil registry records are indexed on WieWasWie. When a lookup
returns no results, it may be an indexing gap rather than a missing record.
Check the patterns below before concluding a record doesn't exist.

### Ede overlijden registers ~1811-1832

**Confirmed gap (2026-03-20):** Three independent lookups for Ede deaths
in 1816, 1826, and 1832 all failed, while records from the same Gelders
Archief collection (0207) in neighboring municipalities (Apeldoorn,
Scherpenzeel, Zutphen, Putten) for the same period ARE indexed. An Ede
death from 1833 WAS found, suggesting the gap ends around 1832-1833.

**Workaround:** For Ede deaths before ~1833, skip WieWasWie and go
directly to Gelders Archief scans via their online beeldbank or request
the relevant register pages.

### De Bilt overlijden registers ~1900-1910

Death record of Aletta Bos (d. 1906, De Bilt) not found. De Bilt is in
Utrecht province (Het Utrechts Archief, not Gelders Archief). These
records may not be indexed yet.

### Apeldoorn huwelijk + geboorte registers (20th century)

**Confirmed gap (2026-03-20):** Apeldoorn BS Huwelijk indexing stops
after **December 1947**. Apeldoorn BS Geboorte is **not indexed at all**
for the 20th century. Death records continue through at least 1960.
All indexed records come from Gelders Archief collection 0207A
("Burgerlijke stand Gelderland, dubbelen 1903-1980"). The scans exist
in the collection, but the person index is incomplete.

**Workaround:** Browse Gelders Archief scans directly (requires
Playwright for scan viewer navigation), or contact CODA Apeldoorn
(coda-apeldoorn.nl/archief) for the original registers.

### General patterns

- Early civil registers (1811-1820s) are more likely to have gaps
- Smaller municipalities may have incomplete indexing
- Always try OpenArchieven as a fallback — different indexing projects
- If both WieWasWie and OpenArchieven fail, the record likely exists
  but isn't digitized/indexed yet — try direct archive scan access

## Login status

The JSON API and detail page work without CBG login for basic searches.
Premium features (wildcards, PersonB searches for two people at once) are
not available without login. The detail page needs a session cookie but
not authentication.
