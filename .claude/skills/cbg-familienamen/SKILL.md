---
name: cbg-familienamen
description: |
  Look up Dutch surname distributions, origins, and variants on CBG Familienamen
  (cbgfamilienamen.nl). Use this skill whenever you need to understand a surname's
  geographic distribution across the Netherlands, find spelling variants of a Dutch
  surname, look up the etymology or meaning of a family name, or check how common
  a name is. Triggers on: "look up the surname", "where is this name from",
  "distribution of de Knijf", "surname variants", "familienamen", "/cbg-familienamen",
  or any question about Dutch surname geography, meaning, or spelling history.
  No login required. Free.
---

# CBG Familienamen — Dutch Surname Database

Look up Dutch family names in the Nederlandse Familienamenbank. Shows distribution
maps (2007 and 1947 census), name etymology, spelling variants, and historical
documentation for 320,000+ surnames.

No login required. Everything is publicly accessible.

## URL construction

This site uses GET parameters, so you can construct URLs directly — no need to
fill forms. However, Playwright is still useful for reading the rendered content
and viewing map images.

### Search

```
browser_navigate → https://cbgfamilienamen.nl/nfb/lijst_namen.php?operator={op}&naam={surname}
```

Operators:
- `eq` — exact match (default, best for specific lookups)
- `bw` — starts with
- `ew` — ends with
- `cn` — contains
- `rx` — regex (advanced)

If exact match returns one result, the page redirects directly to the detail page.

### Direct detail page

```
https://cbgfamilienamen.nl/nfb/detail_naam.php?gba_naam={name}&nfd_naam={normalized}&info={tab}&operator=eq&taal=
```

**Name format quirk:** The `nfd_naam` parameter uses inverted format with prefix
after the base name: "Knijf, de" (not "de Knijf"). The `gba_naam` uses natural
order: "de Knijf".

## Detail page tabs

| Tab | `info=` value | Content |
|-----|---------------|---------|
| Aantal en verspreiding | `aantal+en+verspreiding` | Counts + distribution maps (default) |
| Analyse en verklaring | `analyse+en+verklaring` | Etymology, name meaning, classification |
| Documentatie | `documentatie` | Historical mentions, bibliography |
| Varianten | `varianten` | All spelling variants and compounds |

Greyed-out tabs (`class="geen_optie"`) have no data for this name.

## What each tab shows

### Aantal en verspreiding (counts & distribution)

- 2007 bearer count (per capitalization variant, e.g., "de Knijf" vs "De Knijf")
- Links to `[kaart]` (absolute map) and `[%kaart]` (relative/percentage map)
- 1947 census count with province-level map
- Distribution map: server-rendered PNG with municipality-level data via hover tooltips
- Names with fewer than 5 bearers show `< 5` for privacy

### Analyse en verklaring (analysis)

- Free-text etymology and meaning explanation
- Classification tags (e.g., "patroniem", "beroepsnaam", "plaatsnaam")
- Name components with links

### Documentatie (documentation)

- Historical mentions with dates, locations, and source abbreviations
- Bibliography references (abbreviations link to full citations)

### Varianten (variants)

- Comprehensive list of all known spelling variants, compounds, and post-name-change forms
- Parenthesized entries are uncertain/disputed variants

## Workflow for genealogy research

1. Search for the surname with `operator=eq`
2. On the detail page, check the **distribution map** — this shows where the name
   is concentrated, which helps identify the family's likely region of origin
3. Check **Varianten** tab — spelling variants can help find records under old spellings
4. Check **Analyse en verklaring** — the etymology may reveal occupational or
   geographic origins
5. Compare 1947 vs 2007 distributions to see migration patterns

## Quirks

- **SSL certificate may fail** in strict mode. If WebFetch fails, use Playwright
  which can be configured to ignore certificate errors.
- **All data is in GET parameters** — you can construct any page URL directly.
- **Maps are PNG images** — the actual per-municipality counts are only visible
  as hover tooltips on the HTML image map overlaid on the PNG.

## Output format

```
## CBG Familienamen — [surname]

**Total bearers (2007):** [count]
**Total bearers (1947):** [count]

**Distribution:** [describe concentration — e.g., "concentrated in Gelderland,
especially Barneveld and Ede municipalities"]

**Name meaning:** [from Analyse en verklaring tab]
**Classification:** [tags — patroniem, beroepsnaam, etc.]

**Known variants:** [list from Varianten tab]

**Historical mentions:** [earliest dated mentions from Documentatie tab]
```
