---
name: cabr
description: |
  Search the CABR (Centraal Archief Bijzondere Rechtspleging) — the Dutch
  post-war collaboration trial files — via the "Oorlog voor de Rechter"
  project at oorlogvoorderechter.nl. 425,000+ dossiers on persons investigated
  for collaboration with Nazi Germany during WWII (NSB members, Waffen-SS
  volunteers, Landwacht, economic collaboration, etc.). Uses the Spinque REST
  API behind the site — pure JSON, no browser, no login. Use this skill
  whenever researching a Dutch ancestor's WWII behaviour, checking if someone
  had a CABR dossier, verifying NSB/SS rumours, cross-referencing wartime
  fates, or following up Oorlogsbronnen/NIOD hits. Triggers on: "search CABR",
  "CABR dossier", "collaboration file", "NSB member", "was he in the NSB",
  "Waffen-SS volunteer", "Bijzondere Rechtspleging", "/cabr", or any
  WWII-era Dutch person where collaboration is plausible. Handle results
  sensitively — this is a legally restricted archive with strict privacy
  rules. No login required for the name index. Full dossier content requires
  in-person access at authorized reading rooms.
---

# CABR — Centraal Archief Bijzondere Rechtspleging

Search the Dutch post-war collaboration court archive via Oorlog voor de
Rechter (`oorlogvoorderechter.nl`). The archive contains ~425,000 dossiers
on persons investigated by the Bijzondere Rechtspleging (Special
Jurisdiction) tribunals after WWII for collaboration with the German
occupier. About 30 million pages; ~1/3 digitized so far, with scanning
ongoing through 2027.

The public-facing name index opened online on **2026-01-02** after a
temporary voorziening was agreed with the Autoriteit Persoonsgegevens (AP).
Before that date the archive was effectively closed to the general public.

## Access model — read this before searching

The CABR is subject to an exceptional privacy regime. There are three
concentric rings of access:

| Layer | What | Who can access |
|-------|------|----------------|
| **Name index** (online) | Name + birth date/place + role + dossier ID | Anyone, via oorlogvoorderechter.nl — this skill |
| **Digitized dossiers** (~1/3 of pages) | Full scans of documents | Only on-site terminals at Nationaal Archief + 12 regional archives + NIOD (as of Feb 2026) |
| **Paper dossiers** (~2/3) | Physical files | Only in the Nationaal Archief reading room in The Hague |

Rules the project enforces:

- Only persons known or presumed deceased are shown. Living persons and
  persons born <110 years ago whose death is unknown are hidden.
- The site requires acknowledgement that use is for personal, historical,
  scientific, or journalistic research — not for shaming or harassment.
- Publishing verbatim accusation text, photos, or document contents from
  dossiers is not permitted without NA/AVG review.

**This skill only touches the public name index.** Full dossier content
cannot be retrieved via API — it requires an in-person visit. Document
that distinction in any finding you write.

## Access method — Spinque REST API (no browser)

Behind the Next.js frontend sits a Spinque search platform. The API is
unauthenticated, returns JSON, and is 10-50x faster than Playwright. Base:

```
https://rest.spinque.com/4/oorlogvoorderechter/api/nadere_toegang
```

General URL shape (from the Spinque query-api library, verified against
the live frontend chunks):

```
{base}/e/{endpoint}/p/{param}/{value}/results?config=production&count={N}
```

Useful endpoints discovered in the frontend bundle (`nadere_toegang`
workspace, `production` config):

| Endpoint | Purpose | Param |
|----------|---------|-------|
| `actor_search` | Search persons by name/term | `query` |
| `query_suggest` | Autocomplete suggestions | `topic` |

Appending `results,count` (comma, not slash) returns a JSON array of two
objects: the result list plus a `{total, stats}` block with cutoff
statistics — useful to see how many hits exist beyond the page you pulled.

Results expose a rich Schema.org `Person` payload per hit: `givenName`,
`familyName`, `additionalName` (alternate spellings), `birthDate`,
`birthPlace`, `homeLocation`, `role` (usually `Verdachte`), and an
`identifier` plus an upstream NA handle URL
(`https://dos.bo.nationaalarchief.net/id/persoon/nt00488/<uuid>`). That
`nt00488` archive code is the canonical Nationaal Archief inventory
number for the CABR.

## Step 1 — Search by name

```bash
Q=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "Jansen")
curl -sA "Mozilla/5.0" \
  "https://rest.spinque.com/4/oorlogvoorderechter/api/nadere_toegang/e/actor_search/p/query/${Q}/results,count?config=production&count=20"
```

Notes:

- URL-encode the query — diacritics work (`müller` → `m%C3%BCller`), and
  Spinque also returns matches under the normalized spelling (`Muller`).
- The API is keyword-based; partial names work. For common surnames use
  exact-phrase-style queries such as `"van der Berg"` or combine
  surname + birth place in the term.
- Watch `probability` in each item: 1.0 = exact match, 0.8x = fuzzy,
  ~0.4 = weak. Filter aggressively for genealogy work; false positives
  are common on short surnames.
- The JSON for `results,count` is a top-level array with two objects.
  Parse with `json.loads()` and index `[0]` for results, `[1]` for the
  count/stats block.

## Step 2 — Autocomplete / spelling variants

Names in CABR are spelled inconsistently (the archive preserves the
spelling used by 1940s police and tribunals). Use `query_suggest` before
committing to a full name search:

```bash
curl -sA "Mozilla/5.0" \
  "https://rest.spinque.com/4/oorlogvoorderechter/api/nadere_toegang/e/query_suggest/p/topic/knij/results?config=production&count=10"
```

Returns ranked string suggestions. Run `actor_search` on any variants that
plausibly match your target before concluding "not in CABR".

## Step 3 — Resolve a hit to a dossier

Each person has an `identifier` (e.g. `300018`) and an upstream NA handle.
The frontend builds the detail page at
`https://oorlogvoorderechter.nl/persoon/?id=<identifier>`, but that route
is client-rendered and returns 404 to scrapers — **you cannot extract
dossier content over HTTP**. For a finding, record:

- Full name including `additionalName` variants
- Birth date and place
- Home location at time of investigation
- Role (`Verdachte` = suspect, `Slachtoffer` = victim, etc.)
- The NA handle URL (the `dos.bo.nationaalarchief.net/id/persoon/nt00488/<uuid>`)
- The `identifier` (stable, short, citeable)
- A note that full dossier content requires on-site access

Anything beyond the index (actual documents, verdicts, photos) is a
**Human Action** task — add it to `private/research/HUMAN_ACTIONS.md`
rather than treating it as AI-fetchable.

## Example — Knijf search (verified 2026-04-11)

```bash
curl -sA "Mozilla/5.0" \
  "https://rest.spinque.com/4/oorlogvoorderechter/api/nadere_toegang/e/actor_search/p/query/knijf/results,count?config=production&count=10"
```

Returns 10 of 10 total hits (all Knijf/Knijff spellings), including:

- Theodorus Knijf (1900-06-03, Nijmegen) — identifier 300018 — probability 1.0
- Wilhelmina Knijf (1897-05-13, Rotterdam) — identifier 526165
- Albertus Antonius Knijf (1909-05-04, 's-Gravenhage) — identifier 299993
- ... plus seven more

Handle every hit as **unverified lead** until cross-referenced with birth
place and parents against the GEDCOM. Name-only matches in CABR are not
enough to link a record to a specific ancestor.

## Output format — findings

When recording CABR results as a research finding, use this template and
store it as **Tier C** evidence (single index, not yet corroborated):

```
CABR name-index hit: <full name>
- Born: <birthDate> in <birthPlace>
- Lived: <homeLocation>
- Role: <role> (suspect, victim, etc.)
- NA handle: <url>
- Identifier: <identifier>
- Source: Oorlog voor de Rechter / CABR name index (NA, nt00488),
  retrieved via Spinque API on <YYYY-MM-DD>
- Note: Full dossier not viewable online. Requires on-site visit to
  Nationaal Archief (Den Haag) or one of 12 regional reading rooms.

Confidence: Tier C — CABR name index is an authoritative pointer but
contains no primary record content. Upgrade to Tier B only after an
on-site visit confirms the dossier matches this ancestor.
```

## Privacy, ethics, and legal guardrails

Because this data is uniquely sensitive, apply extra caution:

1. **Deceased-only filter is already enforced by the site** — don't try to
   bypass it. Hidden persons stay hidden.
2. **Never publish dossier content** (photographs, accusation text, NSB
   membership numbers, verdicts) to a public repo, Gramps Web, or any
   family-shareable document. The public genealogy tree
   (`genealogy.deknijf.com`) must not expose CABR content.
3. **Treat hits as leads, not verdicts.** Being investigated by the
   Bijzondere Rechtspleging did not mean a conviction; many were acquitted
   or received minor administrative sanctions. Present findings neutrally:
   "was investigated by CABR" — not "was a collaborator".
4. **Consider family sensitivity before sharing.** WWII collaboration is
   still an active wound in many Dutch families. Notify Rutger before
   surfacing a positive hit for a close ancestor.
5. **Rate-limit yourself.** The Spinque API has no visible quotas but
   hammering it is rude. Batch reasonably and cache locally.

## Limitations

- **No full-text search inside dossiers.** The index covers person
  metadata only. You cannot search for "verrader" or a village name
  and get every dossier that mentions it.
- **No dossier download.** Scans are viewable only on locked-down
  terminals inside reading rooms — they cannot be exported, emailed,
  or photographed.
- **Incomplete digitization.** Only ~1/3 of the 30M pages are scanned as
  of early 2026. A name might exist in paper but not yet in the index.
- **Living persons and <110-year-old births with unknown death are
  invisible** — they will never appear in `actor_search` results.
- **The `dossier_search` endpoint from an older frontend build is no
  longer defined** on the `nadere_toegang` workspace (tested 2026-04-11).
  The current production config exposes `actor_search` and
  `query_suggest` only. If you see references to `dossier_search` in
  older skill snippets, they will return
  `"no endpoint dossier_search defined"`.

## Related skills and sources

- `oorlogsbronnen` — wider WWII source network (NIOD, museums). Use first
  for general WWII research; fall back to CABR only when collaboration
  is specifically suspected.
- `archieven-nl` — catalog-level access to the NA inventory (nt00488).
  Useful to resolve the upstream handle to a finding aid.
- Nationaal Archief reading-room reservation:
  `https://www.nationaalarchief.nl/onderzoeken/digitale-cabr-dossiers-doorzoeken`
  — the official place to book a terminal.
