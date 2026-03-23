---
name: voc-opvarenden
description: |
  Search the VOC Opvarenden database for Dutch East India Company crew records
  (1699-1794). Uses the Nationaal Archief HUB3 API — 853,785 indexed entries
  with rich detail: name, origin, rank, ship, fate (died/returned/deserted),
  service dates, VOC chamber, and links to original scans. Use this skill when:
  "search VOC records", "VOC crew", "VOC opvarenden", "sailed to Batavia",
  "Dutch East India Company", "VOC soldier", "VOC sailor", "/voc-opvarenden",
  or when looking for ancestors who may have sailed with the VOC. Also use when
  checking Daniel Pieterse Knijf (1704, Woerden) or any Knijf/Knijff VOC
  connections. No login required.
---

# VOC Opvarenden — Dutch East India Company Crew (1699-1794)

Search crew records of the VOC. 853,785 entries covering qualified muster
rolls (gekwalificeerde monsterrollen) from 1699-1794.

## Access method: Nationaal Archief HUB3 API

Pure JSON API, no browser needed. This is a **different API** from the
OpenArchieven/GAF endpoints in the `nationaal-archief` skill.

## Step 1: Search by surname

```bash
curl -s "https://service.archief.nl/hub3/api/nt/nt00444?q=SURNAME" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

The response contains two groups:

- `NT00444_Opvarenden` — crew members (primary)
- `NT00444_Begunstigden` — beneficiaries (who received the sailor's pay)

Each group has `rows[]` with `recordID` (UUID) and inline `fields`.

### Search fields in list results

| Field | Description |
|-------|-------------|
| `prs_voornamen` | First name |
| `prs_patroniem` | Patronym (e.g., Jansz) |
| `prs_tussenvoegsels` | Prefix (de, van der, etc.) |
| `prs_achternaam` | Surname |
| `pla_naam_herkomst` | Place of origin |

### Example

```bash
# Search for Knijf (returns 13 crew + 1 beneficiary)
curl -s "https://service.archief.nl/hub3/api/nt/nt00444?q=Knijf" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"

# Search Knijff (different people! 33 crew + 1 beneficiary)
curl -s "https://service.archief.nl/hub3/api/nt/nt00444?q=Knijff" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

**Always search both `Knijf` and `Knijff`** — different spelling variants
appear as different individuals in the index.

## Step 2: Get record detail

```bash
curl -s "https://service.archief.nl/hub3/api/nt/nt00444/RECORD_UUID" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

### Detail fields

| Field name | Label | Example |
|-----------|-------|---------|
| `prs_voornamen` | First name | Aart |
| `prs_patroniem` | Patronym | Jansz |
| `prs_tussenvoegsels` | Prefix | van der |
| `prs_achternaam` | Surname | Knijff |
| `pla_naam_herkomst` | Origin | Delft |
| `prs_datum_indiensttreding` | Entry date | 1725-04-25 |
| `rol_naam_functie_NL` | Rank/function | Matroos |
| `rol_naam_functie_uitleg_NL` | Function description | (full text) |
| `sch_naam_uitgevaren` | Outbound ship | Spiering |
| `prs_datum_uitdiensttreding` | Discharge date | 1732-00-00 |
| `ove_tekst_lokatie_uitdiensttreding_NL` | Discharge location | Batavia |
| `ove_tekst_reden_uitdiensttreding_NL` | **Fate** | Overleden / Gerepatrieerd |
| `ove_tekst_opmerking_uitdiensttreding_NL` | Discharge notes | (full text) |
| `sch_naam_terugreis` | Return ship | NOORDWADDINXVEEN |
| `ove_datum_terugreis_vertrek` | Return departure | 1732-01-01 |
| `ove_datum_terugreis_aankomst` | Return arrival NL | 1732-09-07 |
| `handle` | Scan handle URL | `http://hdl.handle.net/10648/...` |
| `vwz_archivelink` | Archive reference | NL-HaNA/1.04.02/13932//100// |

Plus linked `NT00444_Soldijboeken` sub-record with: ship name, VOC
chamber (Amsterdam/Delft/Rotterdam/etc.), destination, departure date.

### Scan URL

The `handle` field resolves to the NA scan viewer:

```
https://www.nationaalarchief.nl/onderzoeken/archief/1.04.02/invnr/{invnr}/file/NL-HaNA_1.04.02_{invnr}_{folio}
```

## Bonus: Discovery search across all NA indexes

```bash
curl -s "https://service.archief.nl/hub3/api/nt/search?q=SURNAME" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

Returns counts across 15+ NA name indexes including VOC, KNIL, Landmacht,
Marine, emigration. Useful for a broad initial sweep.

## Known Knijf/Knijff in VOC

- **Daniel Knijf** from Woerden (1704, ship Neptunus, soldaat, died Asia 1714)
- **Pieter de Knijf** from Utrecht and Rotterdam (multiple voyages)
- **Gerrit de Knijf** from Utrecht
- **Aart Knijff** from Delft (Matroos, 5+ voyages 1715-1732)

## Limitations

- **1699-1794 only.** Earlier VOC records (1602-1699) not in this index.
- **No pagination.** All results returned in one response.
- **Dates can be partial:** `1732-00-00` means year only.
- **Different from OpenArchieven:** The existing `nationaal-archief` skill
  (`archive_code=ghn`) returns zero VOC crew results. This is a separate API.

## Output format

```
## VOC Opvarende

**Name:** [voornaam] [patroniem] [tussenvoegsels] [achternaam]
**Origin:** [herkomst]
**Rank:** [functie]
**Ship:** [outbound ship] ([chamber])
**Service:** [entry date] - [discharge date]
**Fate:** [reden uitdiensttreding] at [location]
**Return:** [return ship], arrived [date]

**Archive ref:** [archivelink]
**Scan:** [handle URL]

**Confidence:** Tier B — Nationaal Archief VOC indexed record with scan
```
