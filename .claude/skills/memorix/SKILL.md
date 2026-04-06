---
description: |
  Search person records across 6 Dutch archives on the Memorix Genealogy platform
  via `scripts/memorix_search.py`. Covers BHIC (Brabant), Amsterdam Stadsarchief,
  Drents Archief, Erfgoedcentrum Zutphen, Erfgoed Leiden, and Streekarchief
  Midden-Holland (Gouda). Use this skill whenever researching family lines in
  North Brabant, Amsterdam, Drenthe, Zutphen/Brummen/Lochem/Voorst, Leiden, or
  Gouda/Haastrecht/Schoonhoven. No login required. Parallelizable.
---

# Memorix Archives — 6 Dutch Archives via Python Wrapper

Use `scripts/memorix_search.py` for all searches. Do NOT construct curl commands.

## Archives

| Code | Archive | Coverage |
|------|---------|----------|
| `bhic` | BHIC (24.1M records) | North Brabant: Schijndel, Den Bosch, Eindhoven, Tilburg, Breda |
| `amsterdam` | Amsterdam Stadsarchief | Amsterdam: DTB, civil registry, population registers, person cards |
| `drents` | Drents Archief (6.7M records) | Drenthe province: civil registry, DTB, population registers |
| `zutphen` | Erfgoedcentrum Zutphen | Brummen, Lochem, Voorst, Zutphen |
| `leiden` | Erfgoed Leiden en Omstreken | Leiden region: civil registry, DTB, notarial |
| `gouda` | Streekarchief Midden-Holland | Gouda, Haastrecht, Schoonhoven, Waddinxveen |

## Commands

### Search for persons

```bash
python scripts/memorix_search.py <archive> "<surname>"
python scripts/memorix_search.py <archive> "<surname>" --firstname Jan --place Schijndel
python scripts/memorix_search.py <archive> "<surname>" --type "BS Geboorte" --limit 10
```

### Get record detail (all persons in a deed)

```bash
python scripts/memorix_search.py <archive> --deed <deed_id>
```

Returns all persons, their roles, the event date/place, register name, scan URL,
and transcription notes — everything needed to write a finding.

### Deed type filters

| Filter value | Record type |
|---|---|
| `DTB doopakte` | Baptism (church) |
| `DTB trouwakte` | Marriage (church) |
| `DTB begraafakte` | Burial (church) |
| `BS Geboorte` / `BS geboorteakte` | Birth (civil, post-1811) |
| `BS Huwelijk` / `BS huwelijksakte` | Marriage (civil) |
| `BS Overlijden` / `BS overlijdensakte` | Death (civil) |
| `Notarieel register akte` | Notarial record |

Note: exact deed type strings vary slightly per archive. The wrapper handles
case-sensitive matching, so use the values above as-is.

## Workflow

1. **Search**: `python scripts/memorix_search.py <archive> "<name>" [--place X] [--type Y]`
2. **Detail**: copy `deed:UUID` from search result, run `--deed UUID`
3. **Write finding**: use the detail output to populate `research_db.py add-finding`

## Tips

- Pre-1811 names: search both spellings (van der Cant / van der Kant)
- BHIC has the richest data for Brabant — always search BHIC first for Brabant families
- Amsterdam Stadsarchief has unique collections: archiefkaarten (person cards 1893-1939)
- Use `--json` flag for raw API output when the formatted output is insufficient
