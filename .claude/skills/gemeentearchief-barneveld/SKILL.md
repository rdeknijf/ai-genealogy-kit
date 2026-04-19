---
name: gemeentearchief-barneveld
description: |
  Search Gemeentearchief Barneveld records — distributed across three
  systems: (a) Gelders Archief (BS/DTB via OpenArchieven), (b) the local
  `gab` dataset on OpenArchieven (Militieregisters), and (c) Archieval.nl
  (Atlantis portal shared with Ede + Scherpenzeel for notarial and
  bevolkingsregister 1850-1920). Thin pointer skill — delegates to
  `openarchieven-api` for 95% of queries. Relevant for Jeths research
  (Nijmegen-Barneveld family, RQ-001) and Veluwe ancestors generally.
---

# Gemeentearchief Barneveld

Barneveld's archive does not run its own search backend for person
records. Data is distributed across three platforms:

1. **Gelders Archief** — BS (1811+) and DTB for Barneveld are indexed
   under code `gld` on OpenArchieven.
2. **Barneveld direct OA dataset** — Militieregisters 1813-1941 under
   code `gab`. Only ~9,668 records, auto-included in unfiltered searches.
3. **Archieval.nl** — notarial records and bevolkingsregister 1850-1920,
   shared with Ede and Scherpenzeel ("Archieven in de Vallei").
   JavaScript-rendered Atlantis portal, no public API.

## Primary method: `openarchieven-api`

```bash
# All Barneveld BS/DTB + Militieregisters in one shot
python scripts/openarchieven_search.py "Jeths" --place Barneveld

# Explicit Gelders Archief filter (BS/DTB only)
python scripts/openarchieven_search.py "Jeths" --archive gld --place Barneveld

# Verified Jeths hit count: 4 BS Overlijden records
# (Jan Riksen/Rikzen Jeths, Peter Jeths)
```

Buitenhuis in Barneveld returns 372 mixed `gld:` + `gab:` results —
proof that unfiltered searches pick up both Gelders Archief BS and the
direct Barneveld militia dataset without a separate flag.

## Fallback: Archieval.nl for notarial + bevolkingsregister

Archieval.nl is a three-municipality shared portal requiring CSRF tokens
and browser session. **Browser-only fallback** via `playwright-cli` on
`https://www.archieval.nl/`. Used only for:

- Notarial deeds 1812+
- Bevolkingsregister 1850-1920 (indexed but not on OpenArchieven)
- Scherpenzeel records (small municipality)

No URL pattern recoverable from static HTML — navigate the Atlantis
quick search form in a headed browser session.

## When to use

- **Jeths line (Nijmegen-Barneveld family)** — RQ-001 brick wall.
  Barneveld Jeths are BS Overlijden in GA → use `gld --place Barneveld`.
- **Buitenhuis lookups** — Apeldoorn/Veluwe lead from CLAUDE.local.md.
  Try Barneveld + adjacent municipalities.
- **Militia records (dienstplicht)** — the `gab` dataset on
  OpenArchieven is the only place these are indexed.

## Related skills

- **openarchieven-api** — primary tool, handles 95% of lookups.
- **gemeentearchief-ede** — sister municipality, same Archieval portal.
- **mais** — for Utrecht / Amersfoort / ECAL adjacent searches.
