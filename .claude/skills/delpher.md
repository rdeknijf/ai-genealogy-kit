---
name: delpher
description: |
  Search historical Dutch newspapers, magazines, and books on Delpher.nl via Playwright
  browser automation. Use this skill whenever you need to find obituaries, death notices
  (familieberichten), birth/marriage announcements, news articles, or any historical
  newspaper mentions of a person or family. Triggers on: "search delpher", "find in
  newspapers", "check old newspapers", "look for an obituary", "familieberichten",
  "/delpher", or any request to search Dutch historical press for people or events.
  Delpher has 2M+ newspapers (1618-1995), 500K magazines, and 200K books — all OCR'd
  and full-text searchable. No login required.
---

# Delpher — Historical Dutch Newspapers, Magazines & Books

Search Delpher's full-text OCR'd collection of historical Dutch publications.
Particularly useful for finding obituaries, death notices (familieberichten),
birth/marriage announcements, and contextual mentions of family members.

No login required. Everything is freely accessible.

## What to extract from the user's request

- **search terms** — person name, place, event (use quotes for exact phrases)
- **collection** — kranten (newspapers), tijdschriften (magazines), boeken (books), or all
- **date range** — optional, can filter after searching
- **article type** — Familiebericht (family notice), Advertentie (ad), Artikel (article)

## Workflow

### 1. Navigate and search

```
browser_navigate → https://www.delpher.nl/
```

Fill the search box (labeled "Zoeken in alle tekstcollecties") with the query.
Use double quotes around names for exact phrase matching, e.g. `"de Knijf" Bennekom`.

Click the "Zoeken" button. Wait for results — page shows "Bezig met laden" while loading.

### 2. Read the overview

Results show counts per collection type:
- krantenartikelen (newspaper articles)
- tijdschriften (magazines)
- boeken (books)
- externe krantenpagina's (external newspaper pages)
- radiobulletins (radio bulletins)

Click the relevant collection to see individual results.

### 3. Browse results

Each result shows:
- Article title/heading
- Text snippet with search terms highlighted
- Krantentitel (newspaper name)
- Datum (date)

The snippet often contains enough info to identify relevance (name, age, place).

### 4. Filter results

Left sidebar has filters:
- **Periode** — century or custom date range
- **Soort bericht** — Advertentie, Artikel, Familiebericht (most useful for genealogy)
- **Verspreidingsgebied** — Landelijk (national), Regionaal/lokaal
- **Krantentitel** — specific newspaper

For genealogy, filter on "Familiebericht" to find death notices and family announcements.

### 5. View full article

Click an article to see the full text and a scan of the original newspaper page.
The scan shows the actual newspaper layout — useful for reading context around
the OCR'd text, which can have errors especially with older typefaces.

## Search tips

- **Exact name matching**: `"Jan de Knijf"` (with quotes)
- **Name + place**: `"de Knijf" Bennekom` finds the name near the place
- **Obituaries**: filter on "Familiebericht" — these often list age, place, and surviving family
- **Spelling variants**: Try both old and modern spellings. OCR errors are common,
  especially with f/ſ, ij/y, and broken ligatures
- **Date on newspaper**: Use the "Wat stond er in de krant?" feature on the homepage
  to find newspapers from a specific date (e.g., someone's birthday or death date)

## What you'll typically find

| Type | Genealogical value |
|------|-------------------|
| **Familieberichten** | Death notices with age, place, surviving relatives — confirms dates and family relationships |
| **Geboorte/Huwelijk** | Birth and marriage announcements — social context, witnesses |
| **Troepenschepen** | Military transport lists — name, rank, home address |
| **Examenuitslagen** | School exam results — places people in time and location |
| **Rechtswezen** | Legal proceedings — property, disputes, context |
| **Advertenties** | Job ads, business listings — occupations and addresses |

## Output format

```
## Delpher Result — [article type]

**Source:** [newspaper name], [date]
**Type:** [Familiebericht / Artikel / Advertentie]
**Text:** [relevant excerpt with key details]

**Genealogical relevance:** [what this tells us — confirms a date, reveals a relationship, etc.]
**Confidence:** Tier B — contemporary newspaper record
**Link:** [Delpher URL to the article]
```

## Confidence tier

Newspaper mentions are **Tier B** evidence — they're contemporary published records,
though OCR can introduce errors in names/dates. The original scan is always available
to verify the OCR text. Family notices (familieberichten) are particularly reliable
as they were submitted by the family themselves.
