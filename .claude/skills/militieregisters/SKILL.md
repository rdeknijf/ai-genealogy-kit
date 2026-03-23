---
name: militieregisters
description: |
  Search Dutch militia/conscription registers (militieregisters) for all males
  aged 18-20 between 1811-1940. Uses the OpenArchieven API with sourcetype
  filter. Records contain name, registration date/place, and link to scan
  (which shows parents, physical description, occupation, regiment).
  2.4 million indexed records across 20 archives. Use this skill when:
  "search militieregisters", "conscription record", "militia register",
  "loteling", "national service record", "physical description of ancestor",
  "/militieregisters", or when looking for a male ancestor born 1793-1922
  (eligible for conscription at age 18-20). Also use when you need parents'
  names or physical descriptions for a Dutch male in the 19th/early 20th century.
  No login required.
---

# Militieregisters — Dutch Conscription Records (1811-1940)

Search conscription registers for all Dutch males. These records are
genealogically valuable because they list **parents' names** and
**physical descriptions** (height, hair/eye color, face shape).

The original `militieregisters.nl` site is defunct. The data lives in
**OpenArchieven** with `sourcetype=Militieregisters`.

## Coverage

- **Period:** 1811-1940 (males registered at age 18-20)
- **Records:** 2,466,133 person entries across 20 archives
- **Geographic gaps:** No Zeeland, Groningen, Drenthe, Overijssel (except
  Enschede), Limburg, or most of Gelderland (except Nijmegen, Ede,
  Barneveld, Zutphen). Coverage is partial, not nationwide.

### Participating archives

| Code | Archive | Region |
|------|---------|--------|
| `nha` | Noord-Hollands Archief | Noord-Holland |
| `saa` | Stadsarchief Amsterdam | Amsterdam |
| `srt` | Stadsarchief Rotterdam | Rotterdam |
| `hua` | Het Utrechts Archief | Utrecht |
| `frl` | AlleFriezen | Friesland |
| `rat` | Regionaal Archief Tilburg | Tilburg |
| `bhi` | BHIC | Noord-Brabant |
| `eal` | ECAL | Achterhoek/Liemers |
| `ran` | Regionaal Archief Nijmegen | Nijmegen |
| `gae` | Gemeentearchief Ede | Ede |
| `gab` | Gemeentearchief Barneveld | Barneveld |
| `szu` | Regionaal Archief Zutphen | Zutphen |
| `eem` | Archief Eemland | Eemland |
| `ade` | Archief Delft | Delft |
| `wba` | West Brabants Archief | West-Brabant |
| `sha` | Streekarchief Langstraat | Langstraat/Heusden |
| `ens` | Stadsarchief Enschede | Enschede |
| `svp` | Streekarchief Voorne-Putten | Voorne-Putten |
| `nle` | Het Flevolands Archief | Flevoland |
| `aal` | Stadsarchief Aalst | Aalst (Belgium) |

## Search method: OpenArchieven API

```bash
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=SURNAME&sourcetype=Militieregisters&number_show=25&lang=nl"
```

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Surname (required) | `Knijf`, `de+Knijf` |
| `sourcetype` | Must be `Militieregisters` | `Militieregisters` |
| `eventplace` | Filter by municipality | `Barneveld`, `Amsterdam` |
| `archive_code` | Filter to specific archive | `gae`, `nha` |
| `number_show` | Results per page (max 100) | `25` |
| `start` | Pagination offset | `0`, `25`, `50` |
| `sort` | Sort order | `1` (name), `4` (date) |

### Example searches

```bash
# All militieregisters for "Knijf" (46 results)
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&sourcetype=Militieregisters&number_show=25&lang=nl"

# Filter to Barneveld
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Knijf&sourcetype=Militieregisters&eventplace=Barneveld&number_show=25&lang=nl"

# Brouwer in Utrecht
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Brouwer&sourcetype=Militieregisters&archive_code=hua&number_show=25&lang=nl"
```

### Response fields

```json
{
  "personname": "Adrianus Wilhelm Knijf",
  "relationtype": "Geregistreerde",
  "eventtype": "Registratie",
  "eventdate": {"day": 9, "month": 9, "year": 1873},
  "eventplace": ["Rotterdam"],
  "sourcetype": "Militieregisters",
  "archive_code": "srt",
  "archive_org": "Stadsarchief Rotterdam",
  "identifier": "9dfdae47-daaa-c4f9-9240-f9377df277ef",
  "url": "https://www.openarchieven.nl/srt:9dfdae47-..."
}
```

**Important:** The API returns only name, date, place, and URL. The
genealogically rich fields (parents, physical description, occupation,
regiment) are on the **scan image** linked from the record page. Always
click through to the URL to read the full register entry.

### Record detail

```bash
curl -s "https://api.openarchieven.nl/1.1/records/show.json?archive=ARCHIVE_CODE&identifier=UUID&lang=nl"
```

## Workflow

1. Search by surname (+ optional place filter)
2. Review matches — filter by date/place to find the right person
3. Open the `url` to view the full record page
4. Read the scan image for parents, physical description, regiment

## Limitations

- **Shallow index:** API returns name + date + place only. Rich fields
  require reading the scan.
- **No first name filter:** Only surname search is supported.
- **Partial coverage:** 20 of ~130 Dutch archives. Major gaps in
  Gelderland, Zeeland, Groningen, Drenthe, Overijssel, Limburg.
- **Also in WieWasWie:** Some records (especially Noord-Holland 1870-1941)
  are in WieWasWie with richer indexed fields. Check both.

## Output format

```
## Militieregister Result

**Person:** [name]
**Registration:** [date] in [place]
**Archive:** [archive name] ([archive code])
**Record URL:** [url]

**Confidence:** Tier B — official conscription register from [archive]
(Note: parents and physical description on scan, not in index)
```
