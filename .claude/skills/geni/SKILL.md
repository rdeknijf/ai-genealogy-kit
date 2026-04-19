---
name: geni
description: |
  Search Geni.com, the MyHeritage-owned "world family tree" platform,
  for surname matches across merged collaborative profiles. Free public
  HTML search via `curl` — no login needed for result rows with profile
  ID, slug, place, birth/death estimates, and immediate family. Detail
  pages are Incapsula-protected, so use playwright-cli session `-s=geni`
  for those. Complements the `myheritage` skill — although MyHeritage
  owns Geni, the datasets are treated as separate products. Use this
  skill to find parallel trees for Dutch surnames (Knijff, Lebbing,
  Jeths, Van der Kant) that don't appear in MyHeritage SmartMatches.
---

# Geni.com — world tree published profiles

Geni.com is a MyHeritage-owned collaborative "world family tree" — one
merged public tree rather than individual user trees. Surname search
returns ~20 hits per page, with full metadata visible without login.
Dataset is distinct from MyHeritage SuperSearch even though both are
owned by the same company.

## Relationship to `myheritage` skill

The `myheritage` skill covers Rutger's authenticated MyHeritage family
site (SmartMatches + SuperSearch). Geni is a different product with a
different data pool. Worth checking both — e.g., a "Aagje Knijff,
Kamerik, Utrecht, NL, ca. 1748-1808" profile surfaced on Geni that
isn't in the MyHeritage match results for the same person.

## Access method

### Search — free, curl-friendly

```bash
curl -sL 'https://www.geni.com/search?search_type=people&names=Knijff' \
  -A 'Mozilla/5.0'
```

Pagination via `&page=N`. 20 results per page, often 20+ pages for
common surnames.

Each result row is a `<tr class="profile-layout-grid">` with:

- Profile ID (long numeric, e.g. `6000000013090709971`)
- URL slug
- Place of birth / residence
- Birth/death year (estimate or exact)
- Immediate family links

### Detail pages — Incapsula-protected

```bash
playwright-cli -s=geni goto 'https://www.geni.com/people/{slug}/{profile_id}'
playwright-cli -s=geni snapshot
```

Curl returns a challenge iframe on detail pages. The persistent
playwright session `-s=geni` bypasses it after the first manual pass.

## Example query

```bash
curl -sL 'https://www.geni.com/search?search_type=people&names=Knijff' \
  -A 'Mozilla/5.0' | grep -oE 'profile-layout-grid[^>]*>[^<]+' | head -20
```

Top Knijff match: profile ID `6000000013090709971`.

## What's paywalled / inaccessible

- **REST API** (`/api/profile/search`) — requires OAuth registration.
  Cookie auth explicitly rejected. Not usable for anonymous calls.
- **Geni Pro features** — tree exports, merge tools, etc.
- **Ancestry paths** — some require subscription.

Surname search rows are NOT paywalled and contain enough metadata to
triangulate against WieWasWie/OpenArchieven for Tier B verification.

## Output format

```
**Source:** Geni.com — collaborative world tree
**Profile ID:** {numeric}
**URL:** https://www.geni.com/people/{slug}/{profile_id}
**Name:** {name}
**Born/Died:** {dates}
**Place:** {place}
**Immediate family:** {parents / spouses / children links}
**Confidence:** Tier D (single published tree — cross-verify before use)
```

Default confidence is **Tier D** — Geni profiles are user-generated,
often from other online trees, rarely with primary-source citations.
Use Geni to find leads, not as evidence.

## Limitations

- Detail pages require playwright session (Incapsula)
- No programmatic REST access without OAuth
- User-generated — many profiles are merged speculatively
- Duplicate profiles common — the "merge world tree" ideal hasn't
  fully deduplicated
- Dutch surnames often mis-tagged (e.g. "de Knijf" split into
  "Knijf, de" or just "Knijf")

## Related skills

- **myheritage** — sibling product, different dataset
- **stamboom-nederland** — Dutch-only uploaded GEDCOMs
- **genealogie-online** — Dutch published trees (free JSON API)
