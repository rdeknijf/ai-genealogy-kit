---
name: graftombe
description: |
  Search Dutch cemetery and grave records on Graftombe.nl, a volunteer-run
  database of Dutch gravestone indexes and photo requests. Complements
  online-begraafplaatsen — different cemeteries, different photo catalog,
  sometimes has family-grave groupings the other site lacks. Uses direct
  HTTP GET + HTML parsing (no browser needed). Use this skill whenever
  looking for burial records, grave locations, gravestone photos, death
  dates from cemetery records, or cross-checking a result already found
  on online-begraafplaatsen. Triggers on: "check graftombe", "second
  cemetery site", "cross-check the grave", "/graftombe", or when
  online-begraafplaatsen has no hit for a known Dutch burial. No login
  required.
---

# Graftombe.nl — Dutch Cemetery Index (secondary source)

Volunteer-indexed Dutch cemetery database. Each record has name,
birth/death dates, cemetery, and a photo catalog number. Gravestone
photos exist in the volunteers' archive but must be requested via
"Aanvraaglijst" — they are **not displayed inline** on the public site.

Detail pages include a **"Familie informatie"** block listing all persons
on the same grave, with cross-links — excellent for discovering unknown
relatives on family graves.

No login required for searching or viewing records.

## Coverage and relationship to online-begraafplaatsen

Graftombe and online-begraafplaatsen cover **overlapping but distinct**
sets of cemeteries. Neither is a superset of the other:

- Online-begraafplaatsen is larger (1.2M+ persons, 1,700+ cemeteries)
- Graftombe has cemeteries and family groupings the other lacks —
  e.g. Woerden (Oud) Hoge Wal Knijff family grave
- Plain-surname variants without "de" prefix surface more naturally on
  Graftombe
- Photos on Graftombe are **catalog-only** (Foto nr like "SANY3023");
  images require a photo request
- Photos on online-begraafplaatsen are inline but session-bound

**Rule of thumb:** search online-begraafplaatsen first, then Graftombe as
a secondary check. Always check both before concluding "no grave found".

## Important quirks

- Recently deceased (last 10 years) **filtered out** from public view
- Dates with formatting errors also filtered
- Character encoding is **UTF-8** (unlike online-begraafplaatsen's Windows-1252)

## Primary method: HTTP GET + HTML parsing

### Search by surname (minimum required)

```bash
curl -s 'https://graftombe.nl/names/search?surname=Knijf&submit=Zoeken' -L
```

**Critical:** `submit=Zoeken` is required — without it, the form just
re-renders and no results are shown.

Query parameters:

| Param | Notes |
|-------|-------|
| `surname` | Required. Min 2 chars, max 65. Prefixes (de, van) at end: "Veen van de" |
| `forename` | Optional, 2–50 chars |
| `birthdate_from` / `birthdate_until` | Optional year, 1700+ |
| `deathdate_from` / `deathdate_until` | Optional year |
| `submit` | Must equal `Zoeken` |

### Result page structure

Results live inside `<table class="... names-table">`. Each `<tr>` has:

| Column | Content |
|--------|---------|
| Voornaam | First name(s) |
| Achternaam | Link to detail: `/names/info/{personid}/{slug}` |
| Begraafplaats | Link to cemetery: `/names/list/parent/{cemid}` |
| Geboortedatum | `dd-mm-yyyy` or year only |
| Overlijdensdatum | `dd-mm-yyyy` or year only |
| Foto nr | Photographer's catalog ref |

Count indicator: `Er zijn <strong>14</strong> namen gevonden.`

Pagination (30 results per page) uses **path segments**, not query params:

```
/names/search/surname/Peters/submit/Zoeken/birthdate_from//birthdate_until//deathdate_from//deathdate_until//page/2
```

### Detail page

```bash
curl -s 'https://graftombe.nl/names/info/1492305/knijf' -L
```

Detail page contains:

- **Person data table**: voornaam, achternaam, begraafplaats (+ link),
  dates, places, foto nr
- **Breadcrumb**: province > city > cemetery
- **Familie informatie** table: all other persons on the same grave,
  each a clickable link — the most valuable feature

### Cemetery search

```bash
curl -s 'https://graftombe.nl/categories/search?q=Woerden' -L
```

Returns cemeteries matching the location, each linked to
`/names/{cemid}/{slug}`.

## Example queries

**Find a known Knijff burial:**

```bash
curl -s 'https://graftombe.nl/names/search?surname=Knijf&submit=Zoeken' -L \
  | grep -oE '/names/info/[0-9]+/[a-z]+'
```

Result: 14 Knijf records including Hendrik Knijf (1859-1897) at Woerden
Oud Hoge Wal — a hit that does **not** appear on online-begraafplaatsen.

**Narrow by birth year:**

```bash
curl -s 'https://graftombe.nl/names/search?surname=Peters&forename=Herman&birthdate_from=1850&birthdate_until=1900&submit=Zoeken' -L
```

**Family constellation on a grave:**

```bash
curl -s 'https://graftombe.nl/names/info/1492305/knijf' -L \
  | grep -A1 'names/info' | head -40
```

## Fallback

If HTTP parsing fails, use `playwright-cli` on `https://graftombe.nl/names/search`.
No login or JavaScript is required, so HTTP should always work.

## Output format

```
## Graftombe Result

**Person:** [first name] [surname]
**Born:** [date]
**Died:** [date]

**Cemetery:** [name], [city], [province]
**Foto nr:** [catalog ref — photo available via request only]

**Others on same grave:** [list with names + dates]

**Confidence:** Tier B — volunteer-indexed cemetery record from Graftombe
```

## Limitations

- Recently deceased (last 10 years) filtered from public view
- Photos require Aanvraaglijst — no inline images
- Pagination limited to 30 per page; common surnames need many fetches
- Surname field is required — cannot search by forename or place alone
- No wildcard support documented
