---
name: cbg-verzamelingen
description: |
  Search CBG Verzamelingen (cbgverzamelingen.nl), the digital catalog of the
  Dutch Centre for Family History (CBG) in The Hague. Contains 10.5M+ records
  across 12 collections: family announcements (9.25M), police gazette (419K),
  Dutch East Indies sources (300K), memorial cards (230K), family dossiers (82K),
  war sources incl. Red Cross cards (11K), photographs, manuscripts, and more.
  Uses URL parameters + WebFetch (no browser needed). Use this skill when
  searching for: family announcements (rouwadvertenties, geboorteadvertenties),
  family dossiers, Red Cross WWII cards, Dutch East Indies records, bidprentjes
  (memorial cards), police gazette entries, or any CBG collection. Triggers on:
  "search CBG", "CBG verzamelingen", "family dossier", "bidprentje", "Red Cross
  card", "rouwadvertentie", "familieadvertentie", "Oost-Indie records",
  "/cbg-verzamelingen", or when looking for non-civil-registry family history
  materials in the Netherlands.
---

# CBG Verzamelingen — Dutch Centre for Family History

Search 10.5 million+ records across 12 collections at the CBG (Centrum voor
Familiegeschiedenis) in The Hague. Server-side rendered HTML — no JavaScript
or browser needed.

## Collections

| Collection | Dutch name | Records | Notes |
|---|---|---|---|
| Family announcements | Familieadvertenties | 9.25M | Birth, marriage, death notices from newspapers |
| Police gazette | Algemeen Politieblad | 419K | Wanted persons, missing persons, deserters |
| Dutch East Indies | Oost-Indische bronnen | 300K | Colonial-era records |
| Memorial cards | Bidprentjes | 230K | Catholic/Protestant memorial prayer cards |
| Family dossiers | Familiedossiers | 82K | Compiled genealogical research per family |
| Printed family materials | Familiedrukwerk | 67K | Family books, printed genealogies |
| Photographs | Foto's | 41K | Historical photos |
| War sources | Oorlogsbronnen | 11K | Red Cross cards of Dutch WWII dead |
| Manuscripts | Handschriften | 7K | Handwritten genealogies |
| Unknown collection | Onbekende verzameling | 1.8K | |
| Family archives | Familiearchieven | 1.7K | Donated family archive collections |
| Genealogical collections | Genealogische verzamelingen | 523 | |

## Access: URL parameters + WebFetch (no browser needed)

No JSON API exists. The site is server-side rendered — all results are in the
HTML response. WebFetch extracts them directly.

### Step 1: Quick count — which collections have hits?

```
WebFetch -> https://cbgverzamelingen.nl/zoeken?search=SURNAME
```

Ask WebFetch: "List all collections with their hit counts for this search."

This returns a page showing per-collection result counts without individual
records. Use it to decide which collection to drill into.

### Step 2: Search within a specific collection

```
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=cbgsearch&search=QUERY&collection=COLLECTION_NAME
```

**Parameters:**

| Parameter | Required | Values |
|---|---|---|
| `view` | Yes | `cbgsearch` (must be set to get actual results) |
| `search` | Yes | Name, place, date, or keyword. Wildcards: `?` (single char), `*` (multiple) |
| `collection` | Yes | Exact Dutch name from the table above |
| `start` | No | Pagination offset (0, 50, 100, ...). 50 results per page |
| `sort` | No | `order_s_per_naam desc`, `order_s_per_voornaam desc`, `order_s_per_geboorte desc` |

Ask WebFetch: "Extract all person results with names, birth dates/places,
death dates/places, and any detail page links."

**Example searches:**

```
# Family announcements for "Knijf"
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=cbgsearch&search=Knijf&collection=Familieadvertenties

# Family dossiers for "van den Hul"
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=cbgsearch&search=van+den+Hul&collection=Familiedossiers

# War sources (Red Cross cards) for "Heezen"
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=cbgsearch&search=Heezen&collection=Oorlogsbronnen

# Page 2 of results
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=cbgsearch&search=Knijf&collection=Familieadvertenties&start=50
```

### Step 3: View record detail

Detail pages use a UUID:

```
WebFetch -> https://cbgverzamelingen.nl/zoeken?view=detail&id=UUID
```

Ask WebFetch: "Extract all metadata: person name, birth/death dates and places,
registration code, title, signature, events, and any links to scans."

The UUID is found in the href of result links from Step 2.

## Login requirements

- **Search results and metadata:** No login required
- **Viewing scans/images:** Requires free CBG account (OAuth via `account.cbg.nl`)

For genealogy research, the metadata (names, dates, places) is usually
sufficient. Flag records with scans for manual review if needed.

## Quirks

- The `view=cbgsearch` parameter is **required** — without it, you only get
  collection-level counts, not individual records
- Collection names must be exact Dutch names (case-sensitive)
- Wildcards `?` and `*` work in the search field
- 50 results per page; paginate with `start=0`, `start=50`, etc.
- Tussenvoegsel (prefix) is part of the search term — search "de Knijf" or "Knijf"

## Output format

```
## CBG Verzamelingen Result

**Collection:** [collection name]
**Person:** [name]
**Born:** [date], [place]
**Died:** [date], [place]

**Registration code:** [if shown]
**Detail URL:** https://cbgverzamelingen.nl/zoeken?view=detail&id=[UUID]

**Confidence:** Tier C — CBG indexed collection (secondary source, verify with primary records)
```

For war sources (Red Cross cards), upgrade to Tier B if the card references
an official government record.
