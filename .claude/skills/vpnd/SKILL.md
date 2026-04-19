---
name: vpnd
description: |
  Browse Van Papier Naar Digitaal (vpnd.nl) — a volunteer-run repository
  hosting 338,000 scanned images + 36,000 transcribed index pages of Dutch
  church books (DTB), civil registers, ORA, notarial records, and similar
  pre-1811 genealogical source material, delivered as downloadable PDFs
  organized by province and place. Use this skill whenever research needs
  the original scanned church book for a pre-1811 event and you are not
  sure the local archive has it online, especially for Veluwe, Betuwe,
  Brabant, and Friesland parishes. Complements OpenArchieven / WieWasWie
  (which only index events, not scans). Triggers on: "vpnd", "Van Papier
  Naar Digitaal", "DTB scan", "pre-1811 church book", "scan dopen NG",
  "trouwboek NG", "lidmatenboek", "/vpnd". No login, no API, no browser
  automation needed — static HTML + PDF on Apache. Independent from
  Genealogiedomein.nl (different organization, overlapping mission).
  Tier B evidence.
---

# Van Papier Naar Digitaal (VPND)

Volunteer-run repository that photographs DTB registers and related
pre-1811 source material and publishes the scans as PDFs, grouped by
province and place. Founded by Hans den Braber and Herman de Wit, hosted
under geneaknowhow.net, 2009 EMC Heritage Trust Program winner.

**This is not a search engine** — it is a browse-and-download catalog.
Content is organized as:

```
vpnd.nl/
  statuspagina-<prov>.html         # province status page, per town
  <prov>/<place>_<type>.html       # per-place source list
  bronnen/<prov>/<place>/*.pdf     # the actual scans
```

Where `<prov>` is a 2-letter province code: `gr fr dr ov ge fl ut nh zh
ze nb li` plus `nl_alg` (Netherlands-wide) and `og` (overseas).

## Relationship to Genealogiedomein.nl

VPND is **independent** — no merger, no redirect, no cross-hosting.
Different organizations with overlapping goals. Always check both when
looking for a pre-1811 scan.

## Coverage

**~338,000 image pages + ~36,000 transcribed index pages** across all
12 Dutch provinces plus overseas territories.

Gelderland example: 10,682 pages across ~40 parishes — strong on Veluwe
and Betuwe, **sparse on Achterhoek/Liemers**. Notably **Doesburg,
Doetinchem, Zutphen, Arnhem are NOT covered** — for those, use ECAL
(Erfgoedcentrum Achterhoek Liemers) via MAIS or the Gelders Archief.

**Apeldoorn civil marriages 1796-1811 ARE covered** (inv.nr 49-52,
grouped by month) — directly relevant for "Wormen" / Apeldoorn research.

**Record types** (see `vpnd.nl/afkorting.html`):

| Code | Meaning |
|------|---------|
| NG   | Nederduits Gereformeerd / Hervormd (main Protestant) |
| RK   | Rooms Katholiek |
| DG   | Doopsgezind |
| EL   | Evangelisch Luthers |
| REM  | Remonstrants |
| WG   | Waals Gereformeerd |
| CIV  | Civiel (schepenen, commissarissen — civil marriages 1796-1811) |
| ORA  | Oud Rechterlijk Archief (pre-1811 court records) |

## Access method

**Direct HTTP via curl / WebFetch.** Static Apache-served HTML
(charset windows-1252, FrontPage-era) plus PDF assets. No JavaScript,
no cookies, no rate limits observed. **Never use Playwright here.**

Encoding note: pages are `windows-1252`. If you pipe through Python,
decode explicitly (`encoding='cp1252'`).

## Workflow

### 1. Pick the province

```bash
curl -sL https://www.vpnd.nl/statuspagina-ge.html  # Gelderland
curl -sL https://www.vpnd.nl/statuspagina-ut.html  # Utrecht
```

Each province page is a 5-column table: plaats, bron (source), contributor,
status afbeeldingen (scan date), status transcriptie (A = available).

### 2. Detail page → PDF

Detail pages at `vpnd.nl/<prov>/<place>_<type>.html`:

- `vpnd.nl/ge/almen_dtb.html` — Almen DTB NG
- `vpnd.nl/ge/apeldoorn_dtbciv.html` — Apeldoorn civil marriages
- `vpnd.nl/ge/beusichem_ora.html` — Beusichem ORA

PDFs live at `vpnd.nl/bronnen/<prov>/<place>/<filename>.pdf`. Naming:

```
{place}_{inv.nr}_{type}_{yyyymm}-{yyyymm}.pdf
```

Example: `apeldoorn_49-50_trciv_179603-179604.pdf` = Apeldoorn inv.nr
49-50, civil marriages, March–April 1796.

### 3. Download and view

```bash
curl -sLo /tmp/almen_doop.pdf \
  https://www.vpnd.nl/bronnen/ge/almen/almen_doop_1634-1651.pdf
```

PDFs are **image scans** (not OCR'd). Use `pdftoppm` to render pages or
open directly. Transcribed subsets (column 5 "A = {name}") have separate
HTML/PDF indexes with searchable names.

## Example queries

**Apeldoorn civil marriage PDFs:**

```bash
curl -sL https://www.vpnd.nl/ge/apeldoorn_dtbciv.html \
  | grep -oE 'href="[^"]*\.pdf"' | grep apeldoorn_
```

**Gelderland places with transcription indexes:**

```bash
curl -sL https://www.vpnd.nl/statuspagina-ge.html | grep -B1 'A = '
```

## Output format

```
**Source:** Van Papier Naar Digitaal (vpnd.nl),
{province} / {place} / {record type} {year range}
**URL:** https://www.vpnd.nl/bronnen/{prov}/{place}/{filename}.pdf
**Page:** {page number within PDF}
**Confidence:** Tier B — volunteer-photographed scan of the original
parish/civil register. Upgrade to Tier A when cross-verified against
the owning archive's metadata.
```

## Limitations

- **No search.** Browsing only. Must know place + approximate year.
- **Uneven coverage.** Veluwe and Betuwe strong; Achterhoek (Doesburg,
  Zutphen, Doetinchem) not covered — use ECAL / Gelders Archief.
- **Scans, not transcriptions.** Most PDFs are photographed pages without
  OCR — treat as archive scans.
- **Static 2000s-era HTML.** Windows-1252 encoding — decode explicitly.
- **No API, no RSS, no machine-readable catalog.** Indexing VPND's
  catalog requires scraping per-province status pages.
- **Update cadence unknown.** Many PDFs dated 2011-2012; some newer.

## Related skills

- **genealogiedomein** — separate organization, similar goal, different
  material (especially Achterhoek). Check both.
- **mais** — for ECAL (Achterhoek) which VPND does not cover.
- **openarchieven-api** / **wiewaswie-api** — indexed event records
  without scans; pair with VPND when you have an index hit and need
  the underlying scan.
- **archieven-nl** — central gateway when you need the owning archive.
