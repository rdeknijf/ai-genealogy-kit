---
description: |
  Search 363M+ indexed person records across dozens of Dutch archives via
  `scripts/openarchieven_search.py`. Covers Gelders Archief, Noord-Hollands Archief,
  Collectie Overijssel, Nationaal Archief, NIMH military records, and more.
  Use this skill for any Dutch civil registry (BS), church (DTB), or military
  record lookup. No login required. Parallelizable.
---

# OpenArchieven — 363M+ Records via Python Wrapper

Use `scripts/openarchieven_search.py` for all searches. Do NOT construct curl commands.

## Archives

| Code | Archive | Coverage |
|------|---------|----------|
| `gld` | Gelders Archief | Gelderland: Apeldoorn, Arnhem, Nijmegen, Bennekom |
| `nha` | Noord-Hollands Archief | Haarlem + North Holland: 12.7M records |
| `hco` | Collectie Overijssel | Zwolle, Deventer, Kampen, Enschede: 2M+ records |
| `ghn` | Nationaal Archief | National records, WWII CABR, colonial |
| `nim` | NIMH | Military: stamboeken (141K), persoonskaarten (64K) |
| `hua` | Het Utrechts Archief | Utrecht province (limited in OA; HUA has more via MAIS) |
| _(none)_ | All archives | Omit `--archive` to search everywhere |

Run `python scripts/openarchieven_search.py --list-archives` for the full list.

## Commands

### Search for persons

```bash
python scripts/openarchieven_search.py "<name>" [--archive CODE] [--place PLACE] [--type TYPE] [--period START-END] [--limit N]
```

### Get record detail (all persons, source reference, scan URL)

```bash
python scripts/openarchieven_search.py --detail <archive_code>:<identifier>
```

The `ref:` field in search results is the argument for `--detail`.

### Source type filters

| Filter | Record type |
|--------|-------------|
| `BS Geboorte` | Birth (civil, post-1811) |
| `BS Huwelijk` | Marriage (civil) |
| `BS Overlijden` | Death (civil) |
| `DTB Dopen` | Baptism (church, pre-1811) |
| `DTB Trouwen` | Marriage (church) |
| `DTB Begraven` | Burial (church) |
| `Bevolkingsregister` | Population register |
| `Militieregister` | Militia/conscription |

## Workflow

1. **Search**: `python scripts/openarchieven_search.py "<name>" --archive gld --place Apeldoorn`
2. **Detail**: copy `ref:` from result, run `--detail gld:UUID`
3. **Write finding**: use the detail output to populate `research_db.py add-finding`

## Tips

- Omit `--archive` to search all 363M records (useful when you don't know which archive has the record)
- Use `--period 1800-1860` to narrow by date range
- For Gelderland: always use `--archive gld` (fastest, most complete)
- For military records: `--archive nim --type Stamboek`
- Known gap: Apeldoorn BS Geboorte is NOT fully indexed; Apeldoorn BS Huwelijk stops after Dec 1947
- Pre-1811 church records: try `DTB Dopen`, `DTB Trouwen`, `DTB Begraven`
- The detail view includes scan URLs when available

## Supersedes

This skill replaces the individual skills for: openarchieven, gelders-archief,
nationaal-archief, nimh, noord-hollands-archief, collectie-overijssel,
militieregisters. Those old skills still exist but point to the same API —
use this wrapper instead.
