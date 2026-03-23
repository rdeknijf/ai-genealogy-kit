---
name: nimh
description: |
  Search NIMH (Nederlands Instituut voor Militaire Historie) records for Dutch
  military personnel. 178,897 records accessible via OpenArchieven API
  (archive_code=nim): Stamboeken (141K), Persoonskaarten (64K), Persoonsdossiers
  (26K), Krijgsgevangenedossiers/POW files (22K), Koninklijke Besluiten/decorations
  (16K), Flying Personnel (900). Coverage ~1700-1929. Also documents the formal
  request process for post-1920 military records. Use this skill when: "search
  NIMH", "military history", "navy records", "marine records", "stamboek",
  "krijgsgevangene", "POW records", "military decoration", "/nimh", or when
  looking for Dutch military service records. Also use for KNIL-adjacent searches
  (note: KNIL pension records are at SAIP, not NIMH). No login required for
  online records.
---

# NIMH — Nederlands Instituut voor Militaire Historie

Search Dutch military personnel records from the Netherlands Institute for
Military History. Part of the Ministry of Defence.

## Online records: OpenArchieven API

NIMH's indexed records are in OpenArchieven under archive code `nim`.

```bash
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=SURNAME&archive_code=nim&lang=nl&number_show=25"
```

### Record types available

| Source type | Records | Description |
|-------------|---------|-------------|
| Stamboeken | 141,348 | Regimental service records (1700-1929) |
| Persoonskaarten | 64,758 | Personnel cards |
| Persoonsdossiers | 26,457 | Personal files |
| Krijgsgevangenedossier | 22,579 | WWII POW files |
| Koninklijk Besluit | 16,251 | Royal decrees (decorations) |
| Database Vliegend Personeel | 901 | Flying personnel |

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Surname (required) | `Brouwer` |
| `archive_code` | Must be `nim` | `nim` |
| `sourcetype` | Filter by record type | `Stamboeken`, `Krijgsgevangenedossier` |
| `number_show` | Results per page (max 100) | `25` |
| `start` | Pagination offset | `0`, `25` |

### Example searches

```bash
# All NIMH records for "Brouwer"
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Brouwer&archive_code=nim&lang=nl&number_show=25"

# Only Stamboeken (military service books)
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Brouwer&archive_code=nim&sourcetype=Stamboeken&lang=nl&number_show=25"

# POW records
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Brouwer&archive_code=nim&sourcetype=Krijgsgevangenedossier&lang=nl&number_show=25"

# Military decorations
curl -s "https://api.openarchieven.nl/1.1/records/search.json?name=Brouwer&archive_code=nim&sourcetype=Koninklijk+Besluit&lang=nl&number_show=25"
```

### Response fields

Same as other OpenArchieven searches:

- `personname`, `relationtype`, `eventtype`, `eventdate`, `eventplace`
- `sourcetype`, `archive_code`, `identifier`, `url`

Record detail: `https://api.openarchieven.nl/1.1/records/show.json?archive=nim&identifier=UUID&lang=nl`

Browser view: `https://www.openarchieven.nl/nim:UUID`

## Archieven.nl sub-databases (browser-based)

These have more detailed search forms than the OpenArchieven API:

| Database | URL | Records |
|----------|-----|---------|
| Napoleon army | `archieven.nl` search with `miadt=2231` | 53,000 |
| Merchant Marine WWII | `archieven.nl` search with `miadt=2231` | 65,000 |
| Dapperheidsonderscheidingen | `archieven.nl` search with `miadt=2231` | 1815-1963 |
| Women's Auxiliary Corps | `archieven.nl` search with `miadt=2231` | WWII |

These overlap with the OpenArchieven data but offer different filters
(role, date range). Use as a fallback if API search is insufficient.

## Post-1920 records (formal request)

Personnel records for people **born after 1920** are NOT in any online
database. They must be requested from the Ministry of Defence:

**URL:** `https://www.defensie.nl/onderwerpen/archief/persoonsarchief`

**What you get:**

- Staat van Dienst (career overview: postings, ranks, training, deployments)
- Personeelsdossier (supporting documents)

**Process:**

- Available for deceased persons
- Free of charge
- Submit request online or by mail
- Response time: 1-3 months

## KNIL note

NIMH has some KNIL-adjacent records (stamboeken with colonial postings),
but dedicated KNIL pension and service records are at **SAIP** (Stichting
Administratie Indonesische Pensioenen) — `saip.nl`. SAIP has no skill yet.

## Limitations

- Online records cap around 1929 for most collections
- Only ~10% of records have indexed dates
- Marine pre-1870 records partially lost
- Most physical records require a visit to The Hague

## Output format

```
## NIMH Result

**Person:** [name]
**Record type:** [sourcetype]
**Event:** [type], [date] in [place]

**Archive reference:** NIMH via OpenArchieven
**Record URL:** https://www.openarchieven.nl/nim:[identifier]

**Confidence:** Tier B — official military archive record via NIMH index
```
