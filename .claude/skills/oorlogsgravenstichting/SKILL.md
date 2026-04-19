---
name: oorlogsgravenstichting
description: |
  Search the Dutch War Graves Foundation database (oorlogsgravenstichting.nl) —
  180,000+ registered Dutch war victims with cemetery location, birth/death
  dates, rank, military unit, and category (WWII military, civilian, KNIL,
  Birmaspoorweg, Bersiap, Sjoa, etc.). Uses the site's direct Meilisearch API
  via curl — sub-second responses, no browser needed. Use this skill whenever
  researching WWII fatalities, war victims, Dutch East Indies / KNIL casualties,
  Japanese POWs, Burma Railway workers, resistance fighters, concentration camp
  victims, or any family member who died during WWII or in the Bersiap period.
  Triggers: "war grave", "oorlogsslachtoffer", "WWII casualty", "ereveld",
  "KNIL soldier", "Birmaspoorweg", "Bersiap victim", "/oorlogsgravenstichting",
  or any request for Dutch war victim records. No login required.
---

# Oorlogsgravenstichting — Dutch War Graves Foundation

Search 180,000+ Dutch war victims registered by the Oorlogsgravenstichting
(War Graves Foundation). Covers WWII (Europe + Dutch East Indies), the Bersiap
period in Indonesia, and post-war conflicts including recent peacekeeping
missions. Records include full name, birth/death dates and places, cemetery,
rank, military unit, categories, and often a portrait photo.

**Primary use case for this tree:** Herman Knijf (WWII fatality research) and
any other ancestors who died in 1940-1945 or in Dutch East Indies conflicts.

## Access method: Meilisearch HTTP API

The public search page (`/exact-zoeken`) ships a Bearer-authenticated
Meilisearch search-only API key in its inline JavaScript. Hit the search
endpoint directly — no browser automation, no HTML parsing, sub-second
responses with structured JSON.

```
Endpoint:  https://oorlogsgravenstichting.search.devsandbox.be/indexes/persons/search
Method:    POST
Auth:      Bearer 854fd7b7a7b5ea4918068a0ff78dd9e9acd40f7d450fdc5795ffa8535d770f5a
Index:     persons
```

The token is a Meilisearch search-only key embedded in the public site.
If it ever rotates, grep the current `/exact-zoeken` page for
`devsandbox.be` and copy the new Bearer value.

## Basic text search

```bash
TOKEN='854fd7b7a7b5ea4918068a0ff78dd9e9acd40f7d450fdc5795ffa8535d770f5a'
URL='https://oorlogsgravenstichting.search.devsandbox.be/indexes/persons/search'

curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"q":"Knijf","limit":10}'
```

`q` matches across first_name, last_name, place_of_birth, place_of_death,
cemetery_name and categories. Meilisearch splits space-separated terms with
OR semantics, so `"Herman Knijf"` will surface any Herman OR any Knijf. For
tight name matching, use a filter on `last_name` (see below).

## Structured search with filters

Filterable attributes (verified working):

| Field | Example |
|-------|---------|
| `first_name` | `first_name = Dirk` |
| `last_name` | `last_name = Knijff` |
| `gender` | `gender = Man` / `gender = Vrouw` |
| `place_of_birth` | `place_of_birth = Rotterdam` |
| `place_of_death` | `place_of_death = Auschwitz` |
| `cemetery_name` | `cemetery_name = "Militair Ereveld Grebbeberg"` |
| `profession_rank` | `profession_rank = Sold.` |
| `categories` | `categories = KNIL` |
| `date_of_birth` | `date_of_birth = "13-01-1914"` (dd-mm-yyyy) |
| `date_of_death` | `date_of_death = "11-05-1940"` |
| `last_name_first_letter` | `last_name_first_letter = K` |

NOT filterable (only searchable via `q`): `insertion`, `rank`,
`military_part`, `person_status`.

### Combined filter example

Find any "Knijff" who died at the Grebbeberg in May 1940:

```bash
curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "q":"",
    "filter":"last_name = Knijff AND date_of_death = \"11-05-1940\"",
    "limit":5
  }'
```

Uses Meilisearch filter syntax: `AND`, `OR`, `NOT`, parentheses. String
values with spaces must be double-quoted inside the filter expression.

## Example working query (tested)

```bash
curl -s -X POST 'https://oorlogsgravenstichting.search.devsandbox.be/indexes/persons/search' \
  -H 'Authorization: Bearer 854fd7b7a7b5ea4918068a0ff78dd9e9acd40f7d450fdc5795ffa8535d770f5a' \
  -H 'Content-Type: application/json' \
  -d '{"q":"Knijf","limit":5}'
```

Returns 10 total hits — including Dirk van der Knijf (KNIL, Birmaspoorweg,
died Kanchanaburi 1943) and William Martinus Knijff (Grebbeberg, 11 May 1940).

## Response schema

Each hit contains:

| Field | Description |
|-------|-------------|
| `id` | Internal Meilisearch document ID |
| `card_number` | OGS card number (stable identifier) |
| `title` | Full display name (first + insertion + last) |
| `first_name`, `insertion`, `last_name`, `initials` | Name parts |
| `gender` | `Man` / `Vrouw` |
| `date_of_birth`, `date_of_death` | dd-mm-yyyy strings |
| `place_of_birth`, `place_of_death` | Free-text places |
| `cemetery_name`, `cemetery_id` | Burial location |
| `rank`, `profession_rank`, `profession` | Rank / civilian occupation |
| `military_part` | Unit (e.g. `III-46 R.I.`, `KNIL.`) |
| `categories` | Array of tags (e.g. `["Man","Militair","KNIL","Birmaspoorweg"]`) |
| `picture` | Portrait photo URL (nullable) |
| `person_status` | OGS status code (e.g. `1-Oorlogsslachtoffer`) |
| `uri` | Relative path `personen/{card_number}/{slug}` |
| `url` | Full canonical URL to detail page |
| `last_address` | Last known address (usually null) |

## Pagination

Default `limit` is 20. Use `limit` + `offset`:

```bash
curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"q":"","filter":"categories = Birmaspoorweg","limit":50,"offset":0}'
```

`estimatedTotalHits` in the response tells you the total. Meilisearch caps
practical pagination at ~1000 results — narrow the query with filters when
the total is very large.

## Facets (category distributions)

Useful for exploring what categories exist in the dataset:

```bash
curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"q":"","facets":["categories","gender","cemetery_name","place_of_death"],"limit":0}'
```

Returns `facetDistribution` with counts per value.

## Detail page

The `url` field in each hit links to a public detail page, e.g.
`https://oorlogsgravenstichting.nl/personen/80307/dirk-van-der-knijf`.
The detail page is a Craft CMS template that mostly echoes the same fields
already present in the API response, plus optional user-contributed
photos and a "levensverhaal" (life story) if available.

If you need the levensverhaal or additional portraits, fetch the detail
page with WebFetch:

```
WebFetch -> https://oorlogsgravenstichting.nl/personen/{card_number}/{slug}
```

Ask WebFetch to extract the biography text, any user-contributed photos,
and adoption status (`adopteer een graf`).

## Category taxonomy (partial)

Useful categories seen in results — combine multiple with `AND`:

- `Militair` / `Burger` — military vs civilian
- `KNIL` — Dutch East Indies army
- `Birmaspoorweg` — Burma Railway forced laborers
- `Krijgsgevangene Japan` — Japanese POWs
- `Meidagen 1940` — killed in the May 1940 German invasion
- `Ereveld Grebbeberg` / `Ereveld Loenen` etc. — specific fields of honor
- `Bersiap` — Indonesian independence war 1945-1949
- `Sjoa` — Holocaust victims
- `Aanslag op Rauter`, `Engelandvaarder`, `Verzet` — resistance-related
- `Afghanistan` and peacekeeping mission names — post-war

## Output format

```
## Oorlogsgravenstichting Result

**Person:** [title]
**Born:** [date_of_birth] in [place_of_birth]
**Died:** [date_of_death] in [place_of_death]
**Gender:** [gender]

**Cemetery:** [cemetery_name] (cemetery_id: [cemetery_id])
**Rank / occupation:** [profession_rank]
**Military unit:** [military_part]
**Categories:** [categories joined]

**Photo:** [picture URL or "not available"]
**Detail page:** [url]
**OGS card number:** [card_number]

**Confidence:** Tier B — official registration by the Dutch government's
War Graves Foundation, based on military records and civil registry data.
```

## Quirks and limitations

- **No login, no rate limit observed** — the Bearer token is public and
  search-only. Treat responses as authoritative for the OGS registration
  but cross-check with civil records (BS) for exact birth details.
- **Date format** is always `dd-mm-yyyy` strings, not ISO. When filtering,
  use the exact string as stored.
- **Meilisearch `q` is OR-based** across words — for tight "first + last"
  matching, use a filter on `last_name` and put only the first name in `q`,
  or use both as filters.
- **`last_name` filter is case-sensitive and exact** — `Knijf` and `Knijff`
  are different. Run separate queries for spelling variants.
- **Bearer token may rotate** — if auth fails, re-extract from the
  `/exact-zoeken` page's inline JavaScript (search for `devsandbox.be`).
- **The search host is `devsandbox.be`** — looks like a staging domain but
  it's the production search backend. Do not assume it's unstable; it's
  the same endpoint the live site uses.
- **Scope is Dutch war victims** — includes some German/Allied soldiers
  buried in the Netherlands but primary coverage is Dutch nationals.
- **Autocomplete indexes on `/exact-zoeken`** hit separate Meilisearch
  indexes (`first_name`, `last_name`, `place_of_birth`, `cemetery_name`,
  `profession_rank`, `categories`, `genders`) using the same endpoint and
  Bearer token — use these if you need suggestion-style lookups.
