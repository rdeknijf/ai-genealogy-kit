---
name: gemeentearchief-ede
description: |
  Search the Gemeentearchief Ede (gemeentearchief.ede.nl / Archieval portal)
  for DTB, civil registry (BS), population register, and notarial records
  covering Ede, Bennekom, Lunteren, Wekerom, Otterlo, Ederveen, Harskamp,
  and Hoenderloo. Use whenever researching Veluwe ancestors in the Ede
  municipality — especially those who lived in Bennekom, Lunteren, or
  Harskamp. Complements gemeentearchief-barneveld (same Archieval platform)
  for the wider Gelderse Vallei / southern Veluwe area. Pre-1811 DTB scans
  are at Gelders Archief (also reachable via openarchieven-api `--archive gld`).
---

# Gemeentearchief Ede — via OpenArchieven wrapper

**All Ede records are indexed in OpenArchieven under archive code `gae`.**
Use `scripts/openarchieven_search.py` — do NOT hit archieval.nl directly.

The native Archieval.nl portal (shared with Barneveld and Scherpenzeel) is
an Atlantis-based platform that requires session cookies, CSRF tokens, and
POST forms, and returns no JSON. OpenArchieven's index is faster, fully
structured, and has the same records. If you need the original scan, the
detail view gives you a scan URL that points back to Archieval / Gelders
Archief.

## Coverage

| Record type | Via |
|---|---|
| BS Geboorte / Huwelijk / Overlijden | `--archive gae` (Ede indexed directly) |
| Bevolkingsregister (reconstructed) | `--archive gae` |
| Persoonskaarten / Militieregisters | `--archive gae` |
| Notarial archives | `--archive gae` |
| DTB Dopen / Trouwen / Begraven (pre-1811) | `--archive gld` (Gelders Archief holds Ede DTB scans) |

Geographic scope: Ede, Bennekom, Lunteren, Wekerom, Otterlo, Ederveen,
Harskamp, Hoenderloo (modern Ede municipality).

## Commands

```bash
# Search Ede BS/bevolkingsregister (post-1811)
python scripts/openarchieven_search.py "<name>" --archive gae

# Filter by type and period
python scripts/openarchieven_search.py "de Knijf" --archive gae \
  --type "BS Geboorte" --period 1890-1895

# Filter by place (useful for Bennekom specifically)
python scripts/openarchieven_search.py "<name>" --archive gae --place Bennekom

# Pre-1811 DTB: fall back to Gelders Archief
python scripts/openarchieven_search.py "<name>" --archive gld --place Ede \
  --type "DTB Dopen"

# Get full record detail (parents, witnesses, scan URL)
python scripts/openarchieven_search.py --detail gae:<uuid>
```

## Source type filters

Same as openarchieven-api: `BS Geboorte`, `BS Huwelijk`, `BS Overlijden`,
`DTB Dopen`, `DTB Trouwen`, `DTB Begraven`, `Bevolkingsregister`,
`Militieregisters`, `Persoonskaarten`.

## Verified examples

1. `Knijf` across Ede municipality: 132 records, covering 1844 through 1952
2. `de Knijf` + `BS Geboorte` + `1890-1895`: 14 matched birth acts in Ede
3. Record `gae:7CEDC33B-96B3-40CC-8848-FD0D0D5EA43F`: Aaltje de Knijf,
   born 4-11-1891 Ede

## Output format

```
**Confidence:** Tier B — indexed civil record from Gemeentearchief Ede
(OpenArchieven ref: gae:<uuid>, original scan via archieval.nl / Gelders Archief)
```

## Limitations

- Detail lookups on single-person records (e.g. Persoonskaarten) can trip
  a pre-existing bug in `openarchieven_search.py --detail` — the search
  listing itself is always reliable.
- The public Archieval.nl portal itself has no open API; direct scraping
  requires CSRF token, session cookie, and POST forms. Not worth it when
  OpenArchieven already mirrors the data.
- Pre-1811 church records: Ede's DTB scans live at Gelders Archief — use
  `--archive gld --place Ede`.

## Sister archives on the same Archieval platform

- **Barneveld** → openarchieven archive code `gab`
- **Scherpenzeel** → records mostly via Gelders Archief (`gld`)

See `gemeentearchief-barneveld` skill for the complementary Veluwe coverage.
