---
name: stamboom-nederland
description: |
  Search StamboomNederland (stamboomnederland.nl), a repository of uploaded
  GEDCOM files from Dutch genealogy researchers. Contains thousands of public
  family trees with person records including names, birth/death dates and places,
  patronymics, and family relationships. Uses WebFetch for the first 50 results;
  Playwright required for pagination or advanced search. Affiliated with CBG and
  WieWasWie. Use this skill when searching for: other researchers' family trees,
  uploaded GEDCOMs, published Dutch genealogies, or when looking for compiled
  family history that might connect to your tree. Triggers on: "search
  stamboomnederland", "stamboom nederland", "uploaded GEDCOM", "other researchers'
  trees", "published family tree", "/stamboom-nederland", or when you want to find
  what other genealogists have compiled about a family. Data quality varies —
  treat as Tier D evidence (researcher-compiled, unverified).
---

# StamboomNederland — Dutch GEDCOM Repository

Search uploaded family trees from Dutch genealogy researchers. Thousands of
public GEDCOM projects with person records. Affiliated with CBG and WieWasWie.

**Data quality warning:** These are researcher-uploaded trees with no editorial
review. Treat all data as Tier D (unverified secondary source). Use findings
to guide archive lookups, not as authoritative evidence.

## Primary method: WebFetch with search URL

### Step 1: Search by surname

```
WebFetch -> https://stamboomnederland.nl/shared/search?searchTerm=SURNAME
```

Ask WebFetch: "Extract all person results with names, birth years and places,
death years and places, and any project/tree information."

**Parameters:**

| Parameter | Description | Notes |
|---|---|---|
| `searchTerm` | Surname, place, or keyword | Single parameter, searches all fields |

Returns up to 50 results per page as HTML. Each result shows:

- Person name (surname, first name, tussenvoegsel)
- Birth year and place
- Death year and place
- Gender
- Patronymic (if present)
- Project/tree name

**Example searches:**

```
# Search for "Knijf" (returns Knijf, Knijff, van der Knijf variants)
WebFetch -> https://stamboomnederland.nl/shared/search?searchTerm=Knijf

# Search for "van den Hul"
WebFetch -> https://stamboomnederland.nl/shared/search?searchTerm=van+den+Hul

# Search for "Heezen"
WebFetch -> https://stamboomnederland.nl/shared/search?searchTerm=Heezen
```

### Limitation: pagination requires Playwright

Only the first page (50 results) is accessible via URL. Subsequent pages use
Apache Wicket stateful session links (`wicket:interface=:0:...`) that cannot
be reproduced as bookmarkable URLs.

If more than 50 results are needed:

1. Navigate to the search URL with Playwright
2. Click the page 2/3/4 links in the pagination bar
3. Read results from each page

For most surname searches, 50 results is sufficient to find relevant trees.

## Fallback: Playwright for advanced search

The advanced search form supports additional fields not available via URL:

- First name
- Tussenvoegsel (prefix)
- Surname
- Patronymic
- Birth date (day/month/year with exact/before/after/around qualifier)
- Death date (same)
- Relation filter ("has a relation with...")

### Advanced search workflow (browser only):

1. Navigate to `https://stamboomnederland.nl/`
2. Click "Uitgebreid zoeken" (advanced search) button
3. Fill the form fields
4. Submit and read results
5. Results appear at a stateful Wicket URL — cannot be bookmarked

## Etalage (showcase) pages

Some projects have public showcase pages:

```
https://www.stamboomnederland.nl/etalage/{Username}_{ProjectName}_{ID}/index.html
```

These are large static HTML exports of entire projects (can exceed 4MB).
All persons are listed as in-page anchors (`#p1`, `#p2`, etc.). Not practical
for targeted lookups but useful if you find a relevant project and want to
explore the full tree.

## Login requirements

- **Simple search:** No login required
- **Advanced search:** No login required (session-dependent)
- **Person detail from results:** No login required (session-dependent)
- **Private projects:** Login required

## Quirks

- Built on Apache Wicket (Java) — all navigation beyond the initial search
  URL uses stateful session links
- No JSON API exists — all responses are HTML
- The `searchTerm` parameter searches across all fields (name, place, notes,
  patronymic) — no separate field filtering via URL
- Extra URL parameters (like `firstName`) are silently ignored
- Name variants are included in results (Knijf returns Knijff, van der Knijf, etc.)

## Output format

```
## StamboomNederland Result

**Person:** [name]
**Born:** [year], [place]
**Died:** [year], [place]
**Patronymic:** [if present]
**Project/Tree:** [project name if shown]

**Confidence:** Tier D — researcher-uploaded GEDCOM (unverified, use as research lead only)
```

When results look promising, always verify against official archive records
(civil registration, church books) before flagging in FINDINGS.md.
