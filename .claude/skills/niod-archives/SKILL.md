---
name: niod-archives
description: |
  Search NIOD (Institute for War, Holocaust and Genocide Studies) resources for
  WWII and Dutch East Indies genealogy research. Covers three portals: (1) the
  Erelijst van Gevallenen 1940-1945 — an indexed, per-person database of ~18,000
  Dutch war victims across five service groups (KNIL/Indisch Verzet, Koninklijke
  Marine, Verzet, Koopvaardij, Koninklijke Landmacht) — fully searchable via a
  plain HTTP GET form, no browser needed; (2) the NIOD finding aids on
  archieven.nl (institution code 298, ~2.5 km of archival material) — inventory
  titles searchable, but requires the `archieven-nl` skill for JS-rendered
  result lists; (3) cross-reference via Oorlogsbronnen.nl, which already
  aggregates NIOD materials. Use this skill whenever: researching a Dutch WWII
  casualty, looking up KNIL soldiers from the East Indies (1945-1950 period
  included), tracing resistance members, finding Koopvaardij (merchant marine)
  victims, checking if an ancestor is on the Dutch Honour Roll, or searching
  NIOD inventories for context around camps (Neuengamme, Vught), deportation,
  CABR (postwar tribunals), razzias, or collaboration. Triggers on: "search
  NIOD", "erelijst", "honour roll", "war fallen", "KNIL fate", "WWII victim",
  "NIOD archive", "Dutch East Indies military record", "/niod-archives". No
  login required.
---

# NIOD — War, Holocaust and Genocide Studies Archives

NIOD is the Dutch national institute for WWII, Holocaust and genocide research.
It holds ~2.5 km of archival material and curates several indexed databases.
This skill concentrates on the entry points most useful for genealogy:
person-level indexes and inventory search.

No login is required for any of the access methods below.

## Three entry points

| Portal | URL | What it has | Access method |
|--------|-----|-------------|---------------|
| Erelijst van Gevallenen | `https://www.erelijst.nl/zoeken` | ~18,000 indexed Dutch WWII victims (1940-1945, incl. East Indies) | HTTP GET — parse HTML |
| NIOD finding aids | `https://www.archieven.nl/mi/298/` | ~2.5 km archive inventories (archive titles/descriptions) | Use `archieven-nl` skill (JS-rendered) |
| Oorlogsbronnen aggregator | `https://www.oorlogsbronnen.nl/` | Indexed NIOD photos/documents + 1.6M cross-archive sources | Use `oorlogsbronnen` skill |

**Primary win:** the Erelijst is the only NIOD-curated *person* database that
is searchable by surname over plain HTTP. For everything else, NIOD itself
tells you that "many of the archives and collections cannot be searched by
name" — they are inventories, not indexes.

## 1. Erelijst van Gevallenen 1940-1945 (PRIMARY)

The Honour Roll of the Fallen — the Dutch national register of ~18,000 war
victims. NIOD administers it on behalf of the Tweede Kamer (Dutch parliament).

### Search endpoint

```
GET https://www.erelijst.nl/zoeken?title=<surname>
```

Drupal views-exposed-form — all fields are GET parameters. No CSRF, no
session, no JS needed. Full HTML results are rendered server-side.

### Available filters

| Parameter | Meaning | Example |
|-----------|---------|---------|
| `title` | Name (surname or any part) | `title=Knijf` |
| `field_group` | Service group | see list below |
| `field_beroep` | Profession / rank (free text) | `field_beroep=KNIL` |
| `field_geboortedag` / `_maand` / `_jaar` | Birth day/month/year | `field_geboortejaar=1915` |
| `field_geboorteplaats` | Birth place | `field_geboorteplaats=Nijmegen` |
| `field_overlijdensdag` / `_maand` / `_jaar` | Death day/month/year | `field_overlijdensjaar=1945` |
| `field_overlijdensplaats` | Death place | `field_overlijdensplaats=Neuengamme` |
| `page` | Pagination (0-based, 50 results/page) | `page=2` |

### `field_group` values (the five service groups)

```
koninklijk_nederlands_indisch_leger_en_indisch_verzet  -> KNIL + Indisch Verzet
koninklijke_marine                                      -> Royal Navy
verzet                                                  -> Resistance
koopvaardij                                             -> Merchant Marine
koninklijke_landmacht                                   -> Royal Army
```

These correspond to the "five groups of victims" on the Erelijst. `All`
returns the combined set.

### Workflow

1. **Search by surname**
   ```
   curl -sL "https://www.erelijst.nl/zoeken?title=Knijf"
   ```
2. **Parse the result list.** Each hit is an `<h2><a href="...">Name</a></h2>`
   followed by an info block:
   ```
   Geboren: 02-09-1919, Den Haag
   Overleden: 15-04-1943, Kanchanaburi (Thailand)
   Beroep: Soldaat M.M.D.
   Groep: Koninklijk Nederlands-Indisch Leger en Indisch Verzet
   ```
3. **Fetch the detail page** via the `href` from the list. Detail pages add a
   `Pagina` field (page number in the printed Erelijst book) and sometimes
   visitor comments that contain family leads.
4. **Cross-reference** with Oorlogsbronnen, CBG War Victims (East Indies),
   Delpher (obituaries), Oorlogsgravenstichting, and — for KNIL casualties —
   NIMH Indie-gesneuvelden via `openarchieven-api`.

### Example query (tested 2026-04-11)

```
GET https://www.erelijst.nl/zoeken?title=Knijf
-> 3 results:
  - Dirk van der Knijf (Den Haag 1919 -> Kanchanaburi 1943, KNIL Soldaat M.M.D.)
  - Leonardus Albertus Knijff (Nijmegen 1915 -> Atlantische Oceaan 1942, KL Sergeant)
  - Willem Martinus Knijff (Oudenbosch 1914 -> Kester 1940, KL)
```

Dirk van der Knijf is directly relevant to the Anton Knijf (I0018) research
thread: same East Indies military theatre, Burma Railway fate, overlapping
timeframe.

### Useful combined queries

```
# All KNIL + Indisch Verzet deaths in 1945
?field_group=koninklijk_nederlands_indisch_leger_en_indisch_verzet&field_overlijdensjaar=1945

# Resistance deaths in Putten (WWII razzia 1-2 Oct 1944)
?field_group=verzet&field_overlijdensplaats=Putten

# Neuengamme victims (Oktober 44 cross-check)
?field_overlijdensplaats=Neuengamme

# All fallen born in a specific place
?field_geboorteplaats=Ede
```

### Pagination

50 results per page. Add `&page=1` for the second page, `&page=2` for the
third, etc. The pager HTML exposes the highest page number as regular
`<a href>` tags so you can discover the total without a separate count call.

## 2. NIOD finding aids (archive inventories)

Most of NIOD's 2.5 km of material is inventory-only — you find a box, not a
person. The finding aids are on the shared archieven.nl MAIS Flexis platform
(DE REE Archiefsystemen) under institution code **298**.

```
https://www.archieven.nl/mi/298/                                 # portal entry
https://www.archieven.nl/nl/zoeken?miadt=298&mizk_alle=<term>    # keyword search
https://www.archieven.nl/nl/zoeken?miadt=298&micode=<code>&miview=inv2  # inventory by toegangscode
```

**Result lists are JavaScript-rendered** (AJAX via `/maisi_ajax_proxy0.php`),
so use the existing `archieven-nl` skill (Playwright) rather than curl for
listings. The raw HTML contains only the form shell and an empty results
container. Direct inventory URLs with `miview=inv2&micode=<code>` do render
the inventory title server-side, which is enough to confirm a toegangscode
without launching a browser.

### Some NIOD toegangscodes (archive numbers)

| Code | Title |
|------|-------|
| 245 | Erelijst van gevallenen - aanvraagformulieren (application forms, not all digitised) |
| 182 | Joodsche Raad voor Amsterdam |
| 077 | Generalkommissariat fur Verwaltung und Justiz |
| 094 | Nederlandse Unie |
| 250 | Collectie Loe de Jong |

Full list: browse `https://www.archieven.nl/mi/298/` alphabetically.

### CABR — not online

The Centraal Archief Bijzondere Rechtspleging (postwar criminal justice
files, ~30 million pages, all Dutch collaboration cases) is held at the
Nationaal Archief, not NIOD. The digitised portion has been consultable in
the NIOD reading room since 2025, but it is **not searchable online** — it
requires on-site consultation under the Archief- en Privacywet regime. If
research needs CABR, flag it as a `HUMAN_ACTIONS.md` item (reading-room
visit); don't try to automate it.

### Clipping collection

NIOD's long-running knipselcollectie (press clippings on people and subjects)
is searchable by keyword via the archieven.nl search as a material type. Use
`mizk_alle=<name>` and filter for material type "knipsel" in the result pane.

## 3. Oorlogsbronnen — already have a skill

Oorlogsbronnen.nl aggregates NIOD materials alongside 250+ other Dutch WWII
archives. For any NIOD-related discovery that isn't a pure Erelijst lookup,
start with the existing `oorlogsbronnen` skill — it will surface NIOD items
along with matches from regional archives, museums, photo collections, and
the Oktober44 razzia database.

## Priority order for WWII / East Indies research

1. **Erelijst (this skill)** — confirmed war dead, seconds per lookup, Tier B
2. **Oorlogsbronnen** (`oorlogsbronnen` skill) — broad aggregator
3. **Oktober44** (`oktober44` skill) — Putten razzia victims specifically
4. **Oorlogsgravenstichting** (`oorlogsgravenstichting` skill) — war graves
5. **CBG War Victims** (via `cbg-verzamelingen` skill) — Dutch East Indies
6. **Delpher** (`delpher-api`) — newspaper obituaries, honour lists
7. **NIOD finding aids** (`archieven-nl` skill, code 298) — inventories only
8. **CABR** — human-only, NIOD reading room

## Output format

```
## NIOD Erelijst Result

**Person:** [full name]
**Born:** [dd-mm-yyyy], [place]
**Died:** [dd-mm-yyyy], [place]
**Profession / rank:** [value]
**Group:** [one of the five service groups]
**Page in Erelijst book:** [nnn]
**URL:** https://www.erelijst.nl/[slug-or-node-id]

**Confidence:** Tier B - indexed national honour roll, curated by NIOD on
behalf of the Tweede Kamer. Treat the date and place as reliable; cross-check
against a BS death record or an official unit casualty list before editing
the GEDCOM.
```

For NIOD finding-aid results (inventory titles, knipsel hits, photo records),
confidence is Tier C by default — the finding aid tells you *where* an
archive is, not *what* is in it at the individual-document level.

## Known issues and quirks

- **`archives.niod.nl` does not exist.** The string "archives.niod.nl" is not
  a real hostname — DNS will not resolve it. The actual portal is
  `www.archieven.nl/mi/298/`. This caught me out during onboarding.
- **Broken URL slugs on erelijst.nl.** A number of entries have raw Drupal
  token placeholders in their URL slug, e.g.
  `/%5Bfield_voornaam-raw%5D-%5Bfield_tussenvoegsel-raw%5D-%5Bfield_achternaam-raw%5D-107`.
  These URLs still resolve because of the trailing numeric node id (here
  `107`). Do not "fix" a slug to a clean form like `/dirk-van-der-knijf` —
  it 404s. Always reuse the `href` value the search result gives you
  verbatim.
- **archieven.nl result lists require JS.** The initial request returns an
  empty results container; records load via `/maisi_ajax_proxy0.php`. Use
  the existing `archieven-nl` Playwright skill for listings. Direct
  inventory URLs (`miview=inv2&micode=<code>`) do render the inventory
  *title* server-side, which is enough to confirm a toegangscode.
- **No OAI-PMH for NIOD.** The shared `harvest.archieven.nl/OAI/OAIHandler`
  endpoint exists, but NIOD (institution 298) is not in its set list —
  only "Open data" archives are harvested there.
- **CABR is not online.** Reading-room only. Don't promise automated CABR
  lookups in research output.
- **Erelijst is WWII-focused.** East Indies tours after formal Japanese
  surrender (1945-1949 police actions) are only partially covered under the
  KNIL group. For complete coverage of 1945-1949 KNIL deaths, also query
  the NIMH Indie-gesneuvelden dataset via `openarchieven-api`.
