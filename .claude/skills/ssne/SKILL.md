---
name: ssne
description: |
  Search the SSNE (Scotland's Soldiers and the Dutch Republic) database at the
  University of St Andrews. Records of Scottish soldiers and families who served
  in the Dutch Republic's military, roughly 1570-1782. Includes the Scots-Dutch
  Brigade. URL-based search, no API but curl-friendly HTML responses. Use this
  skill when: "search SSNE", "Scotland's Soldiers", "Scots-Dutch Brigade",
  "Scottish soldiers in Netherlands", "SSNE number", "/ssne", or when
  researching military connections to Scotland/England in the Dutch Republic era.
  Directly relevant for the Jeths/Jets line (RQ-001): Captain John Henderson
  SSNE 8038, Lt-Col James Balfour SSNE 8009, Col David Balfour SSNE 8033.
  No login required.
---

# SSNE — Scotland's Soldiers and the Dutch Republic

Search records of Scottish soldiers who served in the Dutch Republic's
military (Scots-Dutch Brigade and other units), approximately 1570-1782.
Hosted by the University of St Andrews.

**Base URL:** `https://www.st-andrews.ac.uk/history/ssne/`

## Direct record lookup (fastest)

If you know the SSNE number:

```bash
curl -s "https://www.st-andrews.ac.uk/history/ssne/item.php?id=8038" \
  -H "User-Agent: Mozilla/5.0"
```

Pattern: `item.php?id=<SSNE_NUMBER>`

Confirmed working: 8038 (Henderson), 8009 (Balfour), 8033 (Balfour Sr.)

## Full-text search

```bash
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?text=Henderson" \
  -H "User-Agent: Mozilla/5.0"
```

Searches all fields including biography text. 10 results per page.

## Advanced search

```bash
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?surname=Balfour&country=The+Dutch+Republic&bool=and" \
  -H "User-Agent: Mozilla/5.0"
```

### Parameters (all optional, combinable with `bool=and` or `bool=or`)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `surname` | Surname (loose match) | `Balfour` |
| `first_name` | First name | `John` |
| `title_rank` | Title or rank | `CAPTAIN` |
| `nationality` | Nationality | `SCOT` |
| `region` | Scottish region of origin | `FIFE` |
| `social` | Social status | `OFFICER` |
| `education` | Education | `ST+ANDREWS` |
| `religion` | Religion | `CATHOLIC` |
| `country` | Country of service | `The+Dutch+Republic` |
| `location` | Location/regiment | `THE+SCOTS+BRIGADE` |
| `arrived` | Arrival date | `1629-09-22` |
| `arrived_op` | Date operator | `gte`, `lte`, `eq`, `lt`, `gt`, `not` |
| `rank_a` | Rank on arrival | `CAPTAIN` |
| `departed` | Departure date | `1662-03-07` |
| `departed_op` | Date operator | same as above |
| `rank_b` | Rank on departure | `COLONEL` |
| `capacity` | Capacity | `OFFICER` |
| `purpose` | Purpose | `MILITARY` |
| `source` | Text in sources/biography | any text |
| `identity` | SSNE number | `8038` |
| `identity_op` | Operator | `eq`, `gte`, etc. |
| `bool` | Combine fields | `and` / `or` |
| `sort` | Sort by | `identity`, `surname`, `forename` |
| `order` | Sort direction | `asc` / `desc` |
| `start` | Pagination offset | `10`, `20` |

### Exact-match filter (strict, uppercase)

```bash
# All Hendersons (exact surname match)
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?surname_f=HENDERSON"

# All Scots Brigade members
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?location_f=THE+SCOTS+BRIGADE"
```

The `_f` suffix parameters do exact-match filtering (uppercase).

## Record fields

Individual records (`item.php?id=N`) contain:

**Identity section:**

- Surname (all spelling variants, each linked)
- First name (all variants)
- Title/rank
- Nationality, Region, Social status
- Education, Religion

**Biography:** Free-text narrative with inline cross-references to other
SSNE records (`item.php?id=XXXX`). Includes career details, family
connections, and source citations (books with page numbers).

**Service records:** One entry per posting:

- Country + Location/Regiment
- Arrived date + Rank on arrival
- Departed date + Rank on departure
- Capacity (e.g., OFFICER)
- Purpose (e.g., MILITARY)

## Parsing HTML results

Results are plain HTML (no JavaScript SPA). Use `WebFetch` or parse
with Python/BeautifulSoup. Key HTML patterns:

- Search results: `<table class="results">` with rows per person
- Record detail: `<dl class="item">` for identity, `<dl class="service">`
  for service records
- SSNE number in results: appears in first column

## Useful pre-built queries

```bash
# All Scots Brigade in the Dutch Republic (221 records)
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?location_f=THE+SCOTS+BRIGADE"

# Officers arriving 1620-1650
curl -s "https://www.st-andrews.ac.uk/history/ssne/results.php?capacity=OFFICER&arrived=1620-01-01&arrived_op=gte&departed=1650-12-31&departed_op=lte&bool=and"
```

## Relevance to this tree

- **John Henderson** (SSNE 8038): Captain in Balfour's regiment 1629-1639,
  promoted Sergeant-Major 1639. "Henrison" in Dutch records. Connected to
  Jets family in Doesburg garrison.
- **James Michael Balfour** (SSNE 8009): Lt-Col, witness at Benjamin Jets
  baptism 1641. "Jacob Balfour" in Dutch rendering.
- **David Balfour** (SSNE 8033): Colonel, father of James Michael.
  Regiment at siege of Breda 1637.

## Limitations

- **HTML only.** No JSON API. Parse HTML or use WebFetch.
- **10 results per page.** Use `start=` parameter to paginate.
- **~5,000 records total.** Small but highly specialized database.
- **No scans.** Records are transcribed/compiled from multiple sources.
  Source citations are in the biography text.

## Output format

```
## SSNE Record — [SSNE NUMBER]

**Name:** [surname], [first name]
**Rank/Title:** [title]
**Nationality:** [nationality] ([region])

**Service:**
- [country], [location]: [arrived] ([rank_a]) - [departed] ([rank_b])

**Biography:** [key details from text]
**Sources:** [citations from biography]

**URL:** https://www.st-andrews.ac.uk/history/ssne/item.php?id=[NUMBER]

**Confidence:** Tier B-C — academic database compiled from primary sources
```
