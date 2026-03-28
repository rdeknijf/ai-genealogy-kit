---
name: collectie-overijssel
description: >-
  Search civil registry records at Collectie Overijssel (formerly Historisch
  Centrum Overijssel / HCO) via the OpenArchieven JSON API. 2M+ records with
  7.2M person references covering ALL Overijssel municipalities: Zwolle,
  Deventer, Kampen, Enschede, Almelo, Hengelo, Holten, Markelo, Goor, Rijssen,
  Hellendoorn, Hardenberg, Ommen, Dalfsen, Staphorst, and many more. Currently
  BS records only (Geboorte, Huwelijk, Overlijden) — DTB church records
  (pre-1811) are NOT indexed. Use this skill when: "search Overijssel records",
  "Collectie Overijssel", "HCO records", "Holten records", "Deventer records",
  "Kampen civil records", "/collectie-overijssel", or any genealogy research
  in Overijssel province. Also use when searching for Knopers, Bloemendaal,
  or other Overijssel families. No login required.
---

# Collectie Overijssel (HCO)

Collectie Overijssel (formerly Historisch Centrum Overijssel, HCO) is the
provincial archive for Overijssel. Based in Zwolle, it holds records for
all municipalities in the province.

Website: <https://collectieoverijssel.nl>

## Coverage

### Indexed and searchable (via API)

- **BS Geboorte** (civil births) — 1811+
- **BS Huwelijk** (civil marriages) — 1811–1932
- **BS Overlijden** (civil deaths) — 1811–1960
- **Total:** ~2M records, 7.2M person references
- **Coverage:** ALL Overijssel municipalities

### NOT indexed (scans only, HUMAN action)

- **DTB Dopen** (baptisms) — pre-1811 church records
- **DTB Trouwen** (marriages) — pre-1811 church records
- **DTB Begraven** (burials) — pre-1811 church records
- **Bevolkingsregister** (population registers) — not in current dataset

DTB records have been digitized as scans on collectieoverijssel.nl but are
NOT searchable by person name. Indexing is in progress ("in the coming years").
For pre-1811 research in Overijssel, use FamilySearch films or browse scans
directly on the HCO website.

## Access method: OpenArchieven JSON API

Uses the standard OpenArchieven API with `archive=hco`. No login or API key
required. Sub-second response times.

### Search by person name

```bash
curl -s "https://api.openarchieven.nl/1.0/records/search.json?archive=hco&name={surname}&number_of_records=10"
```

### Search with filters

```bash
curl -s "https://api.openarchieven.nl/1.0/records/search.json?archive=hco&name={surname}&eventplace={place}&number_of_records=10"
```

### Search parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `archive` | Always `hco` | `hco` |
| `name` | Surname (required for search) | `Knopers` |
| `eventplace` | Filter by place | `Holten` |
| `sourcetype` | Record type filter | `BS Huwelijk` |
| `period_start` | Start year | `1850` |
| `period_end` | End year | `1900` |
| `number_of_records` | Results per page (max 100) | `25` |
| `start` | Pagination offset | `0` |

**Source type values:** `BS Geboorte`, `BS Huwelijk`, `BS Overlijden`

**Note:** The `place` parameter does NOT work for HCO — use `eventplace` instead.

### View full record detail

```bash
curl -s "https://api.openarchieven.nl/1.0/records/show.json?archive=hco&identifier={UUID}"
```

Returns A2A XML-style JSON with all persons in the record, their roles,
dates, places, and archive references.

### Browse record on OpenArchieven (with scan links)

```
https://www.openarchieven.nl/hco:{UUID}
```

## Output format

When reporting findings from HCO:

```markdown
**Source:** Collectie Overijssel, {sourcetype}, {place}, {date}
**Archive ref:** HCO via OpenArchieven, ID {UUID}
**URL:** https://www.openarchieven.nl/hco:{UUID}
**Confidence:** Tier B — official civil registry record from Collectie Overijssel
```

## Municipalities covered

All of Overijssel province, including but not limited to:

- **Salland:** Deventer, Diepenveen, Olst, Raalte, Heino, Dalfsen, Ommen
- **Twente:** Enschede, Hengelo, Almelo, Borne, Delden, Goor, Markelo,
  Holten, Rijssen, Wierden, Haaksbergen, Losser, Oldenzaal, Denekamp
- **Kop van Overijssel:** Kampen, Zwolle, IJsselmuiden, Zwartsluis,
  Hasselt, Genemuiden, Staphorst, Meppel-adjacent
- **Vechtdal:** Hardenberg, Gramsbergen, Coevorden-adjacent
- **Land van Vollenhove:** Vollenhove, Blokzijl, Steenwijk-adjacent

## Limitations

1. **No DTB records** — pre-1811 church records are NOT in the API. For
   pre-1811 research, browse scans on collectieoverijssel.nl or use
   FamilySearch films.
2. **No bevolkingsregister** — population registers are not indexed.
3. **Place filter requires `eventplace`** — the `place` parameter returns
   an API error for HCO. Always use `eventplace` for place filtering.
4. **Birth records partially indexed** — births 1811–1912 are being added
   incrementally. Some may be missing.

## For pre-1811 Overijssel research

When DTB records are needed and this skill can't help:

1. **FamilySearch catalog** — search for the municipality + "Doop" or
   "Trouw" or "Begraaf". Many Overijssel DTB films are digitized.
2. **collectieoverijssel.nl** → Onderzoek → select municipality → browse
   DTB scan images directly (HUMAN action, not API-searchable).
3. **AlleFriezen** (tresoar.nl) — for Overijssel municipalities near the
   Friesland border.
4. **WieWasWie** — sometimes has Overijssel DTB records indexed from
   other contributing archives.

## Parallelizable

No browser needed — run multiple API queries simultaneously.
