---
name: geneanet
description: |
  Search Geneanet (geneanet.org), the #1 European genealogical database,
  with 9 billion indexed individuals across 2 million published user
  family trees plus archival registers, cemetery records, and a genealogy
  library. Strong coverage for French, Belgian, Luxembourgish, and Dutch
  lines — results often include full Dutch civil registry references
  (Toegangsnummer, Aktenummer) scraped from regional archives, which can
  be cross-verified against WieWasWie or MAIS. Use this skill whenever
  searching for: other researchers' trees, parallel genealogies of a
  surname, European ancestors, French genealogy, Belgian genealogy, or
  cross-references for Dutch brick walls (especially RQ-014 Lebbing,
  Knijff / de Knijf, Van der Kant, Buijtenhuijs, Kemmann, Ferron,
  Jeths). Also trigger on: "search geneanet", "check geneanet",
  "geneanet tree", "parallel trees", "published European tree",
  "French genealogy", "Belgian genealogy", "/geneanet", or when extending
  a line into France, Belgium, Germany, or Luxembourg, or when looking
  for a compiled tree that might unblock a Dutch line with zero hits
  on the indexed civil registry. Free anonymous access for basic
  surname search, pagination, individual detail pages, and archival
  registers. Paywalled: advanced filters (spouse, parents, occupation,
  event type), name variants, hints, cousinage matching. Tree hits are
  Tier D (user-compiled, unverified) but upgrade to Tier B when the
  detail page cites a verifiable Dutch archive reference; archival
  register hits are Tier B. Uses `playwright-cli` in headed persistent
  mode because Cloudflare blocks every non-browser access method.
---

# Geneanet — European Genealogical Database

Search the largest European family tree database: 9 billion individuals,
2 million public trees, 5 million members. Strong coverage for France,
Belgium, Luxembourg, and — thanks to voluntary uploads from Dutch
researchers referencing regional archives — surprisingly deep indirect
coverage of the Netherlands.

**Why this is worth checking for Dutch lines:** many Dutch users upload
trees to Geneanet with full civil registry source references already
pasted into the person's Notes section (Toegangsnummer, Aktenummer,
Inventarisnummer, archive name). A single tree hit can hand you the
exact Het Utrechts Archief or Gelders Archief citation needed to
verify a record that was stuck on a brick wall elsewhere. This makes
Geneanet a valuable *lead generator* even when the tree itself isn't
authoritative.

## Data quality / confidence tier

Tree hits (`gw.geneanet.org/<owner>...`) are **Tier D** by default —
researcher-uploaded with no editorial review. Upgrade a tree hit to
**Tier B** when the detail page's Notes cite a specific Dutch archive
reference (Toegangsnummer + Aktenummer) that you confirm via
`wiewaswie-api`, `mais`, or `openarchieven-api`.

Archival Register hits (`/archival-registers/view/...`) are **Tier B**
when the source collection is named — they're transcriptions of
real primary records contributed by partner archives and volunteer
indexers.

When in doubt, flag a finding with the Geneanet tree URL and the
underlying archive reference separately so whoever reviews can
confirm the primary source exists.

## Access method: headed persistent playwright-cli

Geneanet sits behind Cloudflare's Managed Challenge. During onboarding,
every non-browser access attempt was blocked:

- `curl` with realistic headers → 403
- `curl` robots.txt / sitemap.xml → 403
- `api.geneanet.org` / `/v1/` / `/openapi.json` → 404 (no public API)
- Headless Chrome via Playwright → infinite "Just a moment..." loop

The only method that works is a **headed browser with a persistent
profile** via `playwright-cli`:

```bash
playwright-cli -s=geneanet open --headed --persistent
```

The persistent profile keeps Cloudflare's `cf_clearance` cookie between
runs so warm-starts are fast. An X display is required
(`DISPLAY=:0` on a Linux desktop) — this skill is not usable in a
fully headless CI environment, and subagents that spawn a fresh
browser each run will hit the challenge every time.

Save and reuse session state to skip the cookie banner next time:

```bash
playwright-cli -s=geneanet state-save .playwright-cli/state/geneanet.json
# Later in a new session:
playwright-cli -s=geneanet open --headed --persistent
playwright-cli -s=geneanet state-load .playwright-cli/state/geneanet.json
```

On the very first load of a fresh profile, dismiss the cookie banner
by finding the "OK, accept all" button ref in the snapshot and clicking
it — otherwise the banner overlay may block later clicks.

## Search URL — the one you actually need

All filters available to anonymous users are reproducible as URL query
parameters on the canonical search endpoint:

```
https://en.geneanet.org/fonds/individus/?go=1&nom=<SURNAME>
```

Minimal example — surname-only search:

```bash
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Lebbing"
playwright-cli -s=geneanet snapshot
```

The resulting page title becomes `Individual : LEBBING - Search all
records - Geneanet` and the snapshot shows `<N> results` near the top
and one `link` per result whose accessible name concatenates: surname,
first name, spouse, tree owner, birth year, death year, birth/
marriage/death places.

### URL parameters (free anonymous tier)

| Parameter | Meaning | Notes |
|---|---|---|
| `nom` | Last name | Required |
| `prenom` | First name | |
| `prenom_operateur` | `and` / `or` when multiple first names | |
| `sexe` | `` / `M` / `F` | empty = all genders |
| `place__0__` | City/Town of first place slot | repeatable 0..4 |
| `zonegeo__0__` | Region autocomplete ID | optional |
| `country__0__` | Country name | optional |
| `region__0__` | Region name | optional |
| `subregion__0__` | Subregion name | optional |
| `type_periode` | `between` / `before` / `after` / `minimum_between` / `maximum_between` | |
| `from` | Year lower bound | |
| `to` | Year upper bound | |
| `exact_year` / `exact_month` / `exact_day` | Exact date filter | |
| `page` | Result page number | 10 results per page |
| `go` | Must be `1` to submit | Required |

The full URL that the form generates when submitted (five place slots
+ empty extras) is verbose but all extra empty params are harmless:

```
https://en.geneanet.org/fonds/individus/?sexe=&nom=Lebbing&prenom=&prenom_operateur=and&place__0__=Enkhuizen&type_periode=between&from=1800&to=1850&go=1
```

**Narrowing example** — Lebbing in Enkhuizen, 1800–1850:

```
https://en.geneanet.org/fonds/individus/?go=1&nom=Lebbing&place__0__=Enkhuizen&type_periode=between&from=1800&to=1850
```

This takes the unfiltered 4,353 Lebbing hits down to 134 — strong
signal that the place filter actually fires (see "silent param
ignores" below for the ones that don't).

### Pagination

Bookmarkable — append `&page=N`:

```
https://en.geneanet.org/fonds/individus/?go=1&nom=Lebbing&page=2
https://en.geneanet.org/fonds/individus/?go=1&nom=Lebbing&page=436
```

No stateful session links (unlike StamboomNederland), so large result
sets can be walked programmatically. For bulk surname sweeps, walking
`&page=N` is much cheaper than opening many detail pages.

## Free vs paid boundary

The advanced search form at `/fonds/individus/` shows these fields
**disabled** when not signed in. Their URL params are **silently
ignored** for anonymous users — the search still runs but the filter
has no effect:

- Spouse last name / first name
- Occupation
- Father's last name / first name
- Mother's last name / first name
- Event type filter (restrict to Birth / Marriage / Death only)
- "Only results which contain Father / Mother / Both" constraint
- "Apply name variants to all search criteria" toggle

Other paywalled features (require a free account or Geneanet Premium):

- **Hints** — automatic matching of your own GEDCOM against Geneanet
- **Alerts** — saved searches with email notification
- **Search for Relatives** (cousinage) — cross-tree cousin matching
- Some **Archives and Documents** scanned image overlays — the indexed
  text is free but the scan viewer requires Premium for certain
  collections

**Free for anonymous users** (the useful majority for Dutch research):

- Surname + first name search with place + year-range filters
- Pagination to any result page
- Full individual detail pages on any public tree
  (`gw.geneanet.org/<owner>?n=<surname>&p=<firstname>&type=fiche`)
- Family Tree / Profile / Timeline / Ancestry Chart views on public
  trees
- Archival Register text records (civil registry indexes, passenger
  lists, parish book transcripts)
- Cemetery / Save Our Graves photo database
- Surname origin and geographic distribution pages
- Collections Catalog browsing

Most of Geneanet's value for Dutch research is in the free tier
because Dutch data flows in from community-contributed trees, not
Geneanet's own paid scans.

## Individual detail pages (the real gold)

Each search result links to a per-researcher tree hosted on
`gw.geneanet.org` — this is a separate GeneWeb-based subdomain per
tree. URL pattern:

```
https://gw.geneanet.org/<owner>?n=<surname>&oc=<order>&p=<firstname>&type=fiche
```

Fields you can extract from the snapshot of a detail page:

- Heading: `<Gender> <First Name> <Last Name>`
- `Born <date> - <place>`
- `Deceased <date> - <place>, aged <N> years old`
- `Parents` list with links to each parent's detail page
- `Spouses` list with marriage date, place, and spouse link
- `Notes` — often contains Dutch archive references like:
  - `Aktedatum: 19-02-1841`
  - `Akteplaats: Utrecht`
  - `Aktenummer: 248`
  - `Toegangsnummer: 481 Burgerlijke Stand van de gemeenten in de provincie Utrecht 1811-1902`
  - `Inventarisnummer: 707-01`
- `Sources` — free-text source citation (e.g. `Het Utrechts Archief`)
- `Family Tree Preview` — two-generation mini-pedigree embedded as
  an HTML table in the snapshot

**Why this matters:** when Notes contains a Toegangsnummer and an
Aktenummer, you can verify the underlying civil record immediately
via the `wiewaswie-api` or `mais` skills using the same toegang and
inventaris numbers. This upgrades the finding from Tier D to Tier B
without ever leaving the archive web — and typically takes less
than a minute per person.

## Archival Registers (Tier B, free)

Separately from user trees, Geneanet ingests transcribed archive
indexes — passenger lists, burial registers, military rolls, parish
books, notarial indexes. These appear in the same search results but
with a different link pattern:

```
https://en.geneanet.org/archival-registers/view/<archive_id>/<page>?individu_filter=<person_id>
```

In the snapshot, the accessible name of an archival register hit
says `Archives : <collection title>` (instead of `Family tree of
<owner>`) and includes a `Place of record` field. Example seen during
onboarding: `Index to passenger lists of vessels arriving at
Baltimore, 1820-97`.

These are transcriptions of primary sources — cite the underlying
archive and treat as Tier B when the collection is named.

## Example queries for this tree

```bash
# RQ-014 brick wall — Lebbing in Noord-Holland, early 19th century
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Lebbing&place__0__=Enkhuizen&type_periode=between&from=1780&to=1870"

# Knijff / de Knijf spelling variants — search each manually because
# the name-variant toggle is Premium-only
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Knijff&prenom=Cornelis"
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Knijf"
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=de+Knijf"

# Van der Kant branch (Leerdam)
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=van+der+Kant&place__0__=Leerdam"

# Kemmann line (Hannover migration)
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Kemmann&country__0__=Germany"

# Ferron line — Geneanet is particularly strong on French/Walloon names
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Ferron"

# Buijtenhuijs (1400s brick wall)
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Buijtenhuijs"
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Buytenhuys"

# Jeths / Yates — Scottish connection research
playwright-cli -s=geneanet goto "https://en.geneanet.org/fonds/individus/?go=1&nom=Jeths"
```

## Reading results from the snapshot

After each `goto`, the snapshot YAML contains:

- A text element like `<N> results` showing the total hit count — if
  this number doesn't change when you add a filter, the filter is
  silently ignored (see paid fields above)
- A list of `link` elements, each with an `accessible name` string
  that concatenates name, spouse, tree owner, birth year, death year,
  and event places. Parse that flat text directly rather than drilling
  into nested refs — it's faster and the refs change between pages
- A pagination `list` at the bottom with links to
  `/fonds/individus/?go=1&nom=...&page=N`

For each result you want to follow, the link's `/url:` field is the
direct `gw.geneanet.org/<owner>` URL — `goto` that and snapshot again.

**Do not reuse refs from the results page** on the detail page — refs
are per-snapshot and stale the moment you navigate away.

## Rate limits and etiquette

No published rate limit, but Cloudflare re-challenges the session on
rapid bursts. Observed during onboarding:

- 5–6 navigations per minute: fine
- More than ~15 per minute: triggers a fresh "Just a moment..."
  interstitial
- Opening a new browser each time (instead of reusing the session):
  also triggers a fresh challenge

Keep a sane pace. Always reuse the persistent session. For bulk
surname sweeps, prefer walking `&page=N` over opening many detail
pages — the result pages carry enough data (name, spouse, year, place,
tree owner) to triage which detail pages are worth opening.

## Output format

For tree hits:

```
## Geneanet Result

**Person:** <name>
**Born:** <year>, <place>
**Died:** <year>, <place>
**Spouse:** <name> (married <year>, <place>)
**Parents:** <father name>, <mother name>
**Tree owner:** <username>
**Tree URL:** https://gw.geneanet.org/<owner>?n=<surname>&p=<firstname>&type=fiche
**Archive refs (from Notes):** Toegangsnummer <N>, Aktenummer <N>, <archive name>

**Confidence:** Tier D — researcher-uploaded tree on Geneanet.
                Upgrade to Tier B if Notes cite a verifiable
                Toegangsnummer/Aktenummer and you confirm it via
                wiewaswie-api or mais.
```

For archival register hits:

```
## Geneanet Archival Register Hit

**Person:** <name>
**Collection:** <collection title>
**Place of record:** <place>
**Year:** <year>
**Archive ref:** https://en.geneanet.org/archival-registers/view/<id>/<page>

**Confidence:** Tier B — transcribed archive index record on Geneanet.
```

## Quirks and known issues

- **Cloudflare first-request loop.** The first `goto` of a fresh
  session often lands on `Page Title: Just a moment...`. Wait 1–2
  seconds and snapshot again. If the page title is still "Just a
  moment..." after three snapshots in a row, close the session and
  reopen with `--headed --persistent`. Headless mode has never been
  observed to pass this challenge.
- **Silent param ignores.** URL params for disabled fields
  (spouse_nom, profession, father_nom, etc.) look like they worked
  but filter nothing. Always verify by comparing the result count
  against the unfiltered baseline.
- **Unstable internal IDs.** Trailing numeric IDs on result elements
  (e.g. `data-id-es=arbres_utilisateur_1_10630431_52705`) are
  Geneanet's internal doc IDs. They're not stable across crawls —
  don't store them as citations.
- **Two subdomains, one database.** `gw.geneanet.org/<owner>` is a
  separate GeneWeb-based subdomain per tree. It rarely triggers
  Cloudflare itself once the main `en.geneanet.org` cookie is set.
- **No built-in name variants.** Knijf ↔ Knijff ↔ de Knijf are only
  applied with a Premium toggle. For anonymous use, search each
  spelling variant manually and merge results.
- **Language subdomains are cosmetic.** `en.`, `fr.`, and `nl.` all
  hit the same database. Stick with `en.` so field labels in the
  snapshot are in English and easier to parse.
- **French/Belgian/Luxembourgish bias.** Geneanet is French-founded
  and French users dominate the tree uploads. For pure Dutch lines,
  always cross-check with `openarchieven-api` and `wiewaswie-api`
  before concluding that Geneanet has nothing to add — a zero-result
  Geneanet search does not mean the person isn't in another Dutch
  database.
- **No public REST API.** Despite the existence of
  `api.geneanet.org`, it returns 404 for all documented paths. Every
  discoverable endpoint (including `robots.txt` and `sitemap.xml`) is
  Cloudflare-protected. The headed browser is the only working
  access method.
