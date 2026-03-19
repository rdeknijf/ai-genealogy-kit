---
name: gelders-archief-optimized
description: |
  Access civil registry records from the Gelders Archief (geldersarchief.nl)
  via the Open Archives JSON API instead of Playwright browser automation.
  10-50x faster than the browser-based skill. Use this skill whenever you need
  to search the Gelders Archief person database, view record details (birth,
  marriage, death), or verify a record against indexed data. Triggers on:
  "check gelders archief", "view the record", "look up in the Gelderland archive",
  "/gelders-archief", or when following a "Naar bron" link from WieWasWie that
  points to geldersarchief.nl. The Gelders Archief covers Gelderland province --
  including Ede/Bennekom, Barneveld, Apeldoorn, Nijkerk, Zutphen, and Arnhem.
  No login or API key required.
---

# Gelders Archief -- Optimized (Open Archives JSON API)

Access indexed records from the Gelders Archief in Arnhem via the Open Archives
REST API. Returns structured JSON data with person names, event details, parent
names, archive references, and permalink URLs -- all without browser automation.

No login or API key required. Rate limited to 4 requests/second per IP.

## Primary method: Open Archives JSON API

### Search for persons

```
curl "https://api.openarchieven.nl/1.1/records/search.json?name=<QUERY>&archive_code=gld&number_show=<N>&lang=nl"
```

**Required parameters:**

- `name` -- search query (supports multiple names separated by `&` for
  combined record search, e.g., `Jacob de Knijf & Geesje van den Hul`)

**Optional parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `archive_code` | Always use `gld` for Gelders Archief | none |
| `number_show` | Results per page (max 100) | 10 |
| `start` | Pagination offset | 0 |
| `eventplace` | Filter by place (e.g., `Bennekom`, `Ede`, `Arnhem`) | none |
| `sourcetype` | Filter by source type (see below) | none |
| `relationtype` | Filter by role (see below) | none |
| `sort` | Sort column: 1=Name, 2=Role, 3=Event, 4=Date, 5=Place, 6=Source | 1 |
| `lang` | Language (`nl` or `en`) | `nl` |

**Source types for `sourcetype` parameter:**

- `BS Geboorte` -- birth certificate (Burgerlijke Stand)
- `BS Huwelijk` -- marriage certificate
- `BS Overlijden` -- death certificate

**Relation types for `relationtype` parameter:**

- `Kind` -- child (subject of birth record)
- `Bruidegom` -- groom
- `Bruid` -- bride
- `Overledene` -- deceased
- `Vader` -- father
- `Moeder` -- mother

**Search response structure:**

```json
{
  "query": { "archive": "Gelders Archief", "name": "...", "..." : "..." },
  "response": {
    "number_found": 108,
    "docs": [
      {
        "pid": "Person3043910002",
        "identifier": "755EDE30-21A7-4CA4-B589-006AE10E7E17",
        "archive_code": "gld",
        "personname": "Aaltje de Knijf",
        "relationtype": "Kind",
        "eventtype": "Geboorte",
        "eventdate": { "day": 4, "month": 11, "year": 1891 },
        "eventplace": ["Bennekom"],
        "sourcetype": "BS Geboorte",
        "url": "https://www.openarchieven.nl/gld:755EDE30-..."
      }
    ]
  }
}
```

### Get full record detail

Use the `identifier` from search results to fetch the complete record:

```
curl "https://api.openarchieven.nl/1.1/records/show.json?identifier=<UUID>&archive_code=gld&lang=nl"
```

**Show response structure (birth record example):**

```json
{
  "Person": [
    {
      "@pid": "Person3043910002",
      "PersonName": {
        "PersonNameFirstName": "Aaltje",
        "PersonNamePrefixLastName": "de",
        "PersonNameLastName": "Knijf"
      },
      "Gender": "Vrouw"
    },
    {
      "@pid": "Person3043910003",
      "PersonName": {
        "PersonNameFirstName": "Jacob",
        "PersonNamePrefixLastName": "de",
        "PersonNameLastName": "Knijf"
      },
      "Age": { "PersonAgeLiteral": "37" },
      "Profession": "landbouwer"
    },
    {
      "@pid": "Person3043910004",
      "PersonName": {
        "PersonNameFirstName": "Geesje",
        "PersonNamePrefixLastName": "van den",
        "PersonNameLastName": "Hul"
      },
      "Profession": "zonder beroep"
    }
  ],
  "Event": {
    "EventType": "Geboorte",
    "EventDate": {
      "LiteralDate": "04-11-1891",
      "Year": "1891", "Month": "11", "Day": "04"
    },
    "EventPlace": { "Place": "Bennekom" }
  },
  "RelationEP": [
    { "PersonKeyRef": "Person3043910002", "RelationType": "Kind" },
    { "PersonKeyRef": "Person3043910003", "RelationType": "Vader" },
    { "PersonKeyRef": "Person3043910004", "RelationType": "Moeder" }
  ],
  "Source": {
    "SourcePlace": { "Country": "Nederland", "Place": "Ede" },
    "SourceDate": { "LiteralDate": "04-11-1891" },
    "SourceType": "BS Geboorte",
    "SourceReference": {
      "InstitutionName": "Gelders Archief",
      "Archive": "0207",
      "Collection": "Burgerlijke stand Gelderland, dubbelen",
      "Book": "Ede, Geboorteregister",
      "RegistryNumber": "5304.02",
      "DocumentNumber": "408"
    },
    "SourceDigitalOriginal": "https://permalink.geldersarchief.nl/...",
    "RecordGUID": "{755EDE30-21A7-4CA4-B589-006AE10E7E17}"
  }
}
```

### Construct Gelders Archief permalink

The permalink to the original Gelders Archief record page (with scan viewer)
can be constructed from the identifier by removing dashes:

```
https://permalink.geldersarchief.nl/<UUID-without-dashes>
```

Example: identifier `755EDE30-21A7-4CA4-B589-006AE10E7E17` becomes
`https://permalink.geldersarchief.nl/755EDE3021A74CA4B589006AE10E7E17`

### Mapping fields to the output format

From the `show` response, extract:

- **Person name**: from Person array, match via RelationEP `RelationType`
- **Father**: RelationType `Vader`
- **Mother**: RelationType `Moeder`
- **Partner**: RelationType `Bruidegom`, `Bruid`, or `other:(ex-)partner`
- **Event date**: `Event.EventDate.LiteralDate` (the event date, not SourceDate)
- **Event place**: `Event.EventPlace.Place`
- **Registration date**: `Source.SourceDate.LiteralDate` (= aktedatum)
- **Registration place**: `Source.SourcePlace.Place` (= akteplaats)
- **Toegangsnummer**: `Source.SourceReference.Archive`
- **Inventarisnummer**: `Source.SourceReference.RegistryNumber`
- **Aktenummer**: `Source.SourceReference.DocumentNumber`
- **Scan link**: `Source.SourceDigitalOriginal`

## Typical workflow

### 1. Search by person name

```bash
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Jacob+de+Knijf&archive_code=gld&eventplace=Bennekom&sourcetype=BS+Geboorte&number_show=20&lang=nl"
```

### 2. Get full record detail for each match

```bash
curl -s "https://api.openarchieven.nl/1.1/records/show.json?identifier=<UUID>&archive_code=gld&lang=nl"
```

### 3. Construct permalink for scan viewing

```
https://permalink.geldersarchief.nl/<UUID-without-dashes>
```

Note: viewing the actual scan images still requires visiting the permalink
in a browser (Playwright fallback), since the scan viewer uses JavaScript.

## Parallel batch lookup

Since this is a REST API (no browser session), multiple lookups can run
in parallel. For verifying a family line with 10 people:

```bash
# Search + show can be done in parallel for independent persons
# Respect the 4 req/sec rate limit
```

This is a major advantage over Playwright, which is limited to a single
sequential browser session.

## Combined two-person search

To find records where two people appear together (e.g., parents on a
child's birth record), use `&` in the name parameter:

```
name=Jacob+de+Knijf+%26+Geesje+van+den+Hul
```

This returns all records mentioning both persons (births, marriages, deaths).

## Birth date vs registration date

The API distinguishes between:

- **Event date** (`Event.EventDate`) = actual birth/marriage/death date
- **Source date** (`Source.SourceDate`) = registration date (aktedatum)

Use the event date for GEDCOM entries.

## Municipalities covered

The Gelders Archief holds civil registration records for all Gelderland
municipalities. Key ones for this family tree:

- **Ede** (includes Bennekom, Lunteren, Otterlo, Ederveen)
- **Barneveld** (includes Voorthuizen, Garderen, Harselaar, Kootwijkerbroek)
- **Apeldoorn** (includes Beekbergen, Loenen)
- **Nijkerk** (includes Hoevelaken)
- **Putten**
- **Ermelo**
- **Zutphen**
- **Arnhem**

## Fallback: Playwright browser automation

If the Open Archives API is unavailable, returns errors, or when you need
to view the actual scan images (handwritten certificates), fall back to
Playwright browser automation.

### Via permalink

```
browser_navigate -> https://permalink.geldersarchief.nl/<UUID-without-dashes>
```

This opens the full record page with scanned documents.

### Via person search form

```
browser_navigate -> https://www.geldersarchief.nl/bronnen/personen?view=maisinternet
```

Fill in the search form fields and submit. The MAIS/Archieven.nl platform
loads results via JavaScript -- WebFetch/curl cannot access the search
results directly (only skeleton HTML is returned).

### Viewing scans

The scan viewer on the Gelders Archief requires JavaScript rendering.
Navigate to the permalink URL and click thumbnail links (1, 2, 3...) to
open the document viewer showing the actual handwritten certificate pages.

## Output format

```
## Gelders Archief Result -- [record type]

**Person:** [name]
**Event:** [type], [event date] in [event place]
**Registered:** [akte date] in [akte place]

**Father:** [name], age [age], [profession]
**Mother:** [name], [profession]

**Archive ref:** Toegangsnr [Archive], Inventarisnr [RegistryNumber], Aktenr [DocumentNumber]
**Permalink:** https://permalink.geldersarchief.nl/[UUID]
**Scan available:** Check permalink

**Confidence:** Tier B (indexed data from official archive via API)
```

## Limitations

- The Open Archives API contains indexed data only -- not all Gelders
  Archief records may be in their dataset (they note the database is
  "voortdurend in opbouw" / continuously being built)
- Scan images are not accessible via API -- use the permalink in a browser
- Rate limit: 4 requests/second per IP (sufficient for genealogy research)
- Maximum 100 results per search page (paginate with `start` parameter)
- The combined `&` search in the name field is powerful but quirky -- test
  with known records first
