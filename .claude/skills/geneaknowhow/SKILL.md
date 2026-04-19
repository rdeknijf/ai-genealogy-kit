---
name: geneaknowhow
description: |
  Navigate GeneaKnowhow (geneaknowhow.net) — the most comprehensive
  free directory of Dutch genealogy source pointers, organized by
  province and municipality. It's a ROUTER, not a database: each
  municipality page lists dozens of indexed sources (DTB, BS, notarial,
  tax, land, judicial) with links to the actual host (genealogiedomein,
  archieven.nl, bhic, henkbeijers, familysearch, etc.). Use this skill
  whenever you need to discover "what sources exist for this village"
  before drilling into a specific skill. Covers all 12 Dutch provinces
  plus Flemish and Walloon regions. Static HTML, curl-only, ISO-8859-1
  encoding.
---

# GeneaKnowhow — source directory for Dutch genealogy

GeneaKnowhow is a 2000s-era static HTML site that indexes Dutch
(and Belgian) genealogical sources by province and municipality.
It's a **pointer directory**, not a database — its value is telling
you that obscure sources exist and which dedicated skill to invoke next.

## When to use

- **"What sources exist for <village>?"** — start here before drilling
  into specific skills
- Discovering obscure hosted transcriptions (genealogiedomein,
  archiefman, liemersverleden, etc.) that aren't indexed on
  OpenArchieven or WieWasWie
- Finding cross-references between municipalities and host platforms

**Do NOT use it for:**

- Person name search — GeneaKnowhow catalogs sources, not people
- Anything the `openarchieven-api`, `wiewaswie-api`, or specific
  dedicated skills already cover well

## Access

**Static HTML via curl.** No API, no JavaScript, no login, no rate
limiting. ISO-8859-1 encoding — decode explicitly (`iconv -f latin1`
or Python `encoding='iso-8859-1'`).

**Homepage is useless** (FrontPage frameset). Skip `/digi/bronnen.html`
and hit the content pages directly.

### Province entry points (Dutch)

```
https://www.geneaknowhow.net/digi/{prov}-ni.html
```

| Code | Province |
|------|----------|
| `alg` | Nederland algemeen |
| `fries` | Fryslân |
| `gron` | Groningen |
| `drent` | Drenthe |
| `over` | Overijssel |
| `geld` | Gelderland |
| `flevo` | Flevoland |
| `nhol` | Noord-Holland |
| `zhol` | Zuid-Holland |
| `utrecht` | Utrecht |
| `nbra` | Noord-Brabant |
| `zeel` | Zeeland |
| `limbnl` | Limburg (NL) |

### Flemish / Walloon entry points

`wvlaan`, `ovlaan`, `antw`, `vlbra`, `brussel`, `limbb`, `hainaut`,
`brabwal`, `namen`, `luik`, `lux`, `lux-land`

### Hosted transcriptions

`/script/<province>.html` — where GeneaKnowhow hosts transcriptions
directly rather than linking out.

## Workflow

### 1. Fetch province once per session

```bash
curl -sL https://www.geneaknowhow.net/digi/geld-ni.html \
  | iconv -f iso-8859-1 -t utf-8 > /tmp/geld.html
wc -l /tmp/geld.html  # 7,607 lines for Gelderland
```

### 2. Grep by municipality

```bash
grep -i -A20 'doesburg' /tmp/geld.html | head -50
```

Each `<li>` bullet lists a source with a link to the host platform.

### 3. Follow downstream links

Extract links and route to the appropriate skill:

| Host domain | Skill to use |
|-------------|--------------|
| `genealogiedomein.nl` | `genealogiedomein` |
| `archieven.nl` | `archieven-nl` |
| `bhic.nl` | `memorix` (BHIC is on Memorix) |
| `henkbeijersarchiefcollectie.nl` | `henk-beijers` |
| `familysearch.org` | `familysearch` |
| `archiefman.nl` | direct curl |
| `liemersverleden.nl` | direct curl |
| `open-archieven.nl` | `openarchieven-api` |

## Verified examples

### Doesburg DTB (Gelderland) — Lebbing brick wall

```bash
curl -sL https://www.geneaknowhow.net/digi/geld-ni.html | grep -i doesburg
```

Finds:

- **RK dopen 1672-1811** → genealogiedomein.nl
- **RK trouwen 1672-1811** → genealogiedomein.nl
- **RK overlijdens 1708-1720** → genealogiedomein.nl
- BS geboortes 1811-1900, overlijden 1811-1932, huwelijken
  1812-1850/1913-1942
- Notariële akten 1811-1814 → archiefman.nl
- 10-jarentafels 1811-1960 → liemersverleden.nl
- ~30 additional property/tax/legal entries

### Schijndel (Noord-Brabant)

```bash
curl -sL https://www.geneaknowhow.net/digi/nbra-ni.html | grep -i schijndel
```

Finds: BHIC r.k. dopen 1604-1810 (Memorix) + Henk Beijers
schepenbank transcriptions — already covered by existing skills.

## Output format

GeneaKnowhow itself isn't usually cited — it's a discovery tool. Once
you find a source via GeneaKnowhow, cite the actual host (which has
its own dedicated skill).

## Limitations

- **Not a name index** — cannot search for persons directly
- **Static catalog** — last updates inconsistent, some links dead
- **ISO-8859-1 encoding** — diacritics garble as `?` with default curl
- **FrontPage markup** — tables and structure are ugly; parse with care
- **Overlap** — many entries route to sources already covered by
  dedicated skills. Use GeneaKnowhow only to find the UNCOVERED ones.

## Related skills

- **genealogiedomein** — most frequent downstream destination
- **henk-beijers** — Brabant schepenbank transcriptions
- **archieven-nl** — central gateway for finding aids
- **memorix** — for BHIC (Brabant) downstream links
- **openarchieven-api** — for indexed event records
