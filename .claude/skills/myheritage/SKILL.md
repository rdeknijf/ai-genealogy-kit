---
name: myheritage
description: |
  Search and browse MyHeritage via Playwright browser automation. Use this skill
  when you need to: (1) check matches for a person — Smart Matches against other
  trees or Record Matches against historical records, (2) search MyHeritage
  SuperSearch for historical records across 39B entries, (3) browse connected
  family sites, (4) use photo tools (colorize, enhance, animate old photos).
  Triggers on: "search myheritage", "check myheritage matches", "look up on
  myheritage", "/myheritage", "what does myheritage have for [person]", or when
  you want a secondary cross-reference for a person already found in official
  archives. Requires login — credentials in .env. Read-only — do NOT edit the tree.
---

# MyHeritage — Matches, Records & Cross-Reference Research

Search 39 billion records and browse matches on your MyHeritage family site.
MyHeritage is used **read-only** as a secondary research tool — Gramps Web
(or your local GEDCOM) is the source of truth.

**Requires login** — credentials stored in `.env` as `MYHERITAGE_USER` and
`MYHERITAGE_PASSWORD`.

## Setup

Before using this skill, set these variables in your `.env`:

```
MYHERITAGE_SITE_ID=your-site-id-here
```

Find your Site ID by logging into MyHeritage and checking the URL on your
family site page — it's the long alphanumeric string in the URL path.

## When to use MyHeritage vs other sources

| Source | Use when |
|--------|----------|
| **WieWasWie** | Need structured Dutch civil registry records (Tier B) |
| **OpenArchieven** | Wide net across 363M+ Dutch/Belgian records |
| **FamilySearch** | International records, church records, scanned images |
| **MyHeritage matches** | Want to cross-reference a person against other trees + record databases. Good for finding birth/death places, occupations, parents, siblings you haven't found elsewhere |
| **MyHeritage SuperSearch** | 39B records including 19B newspapers, family trees from other platforms. Broader than Dutch-only sources |
| **Connected sites** | Want to check large trees from other researchers for overlapping family lines |

**Confidence:** MyHeritage data is **Tier C or D** — use it to guide archive
lookups, not as authoritative evidence. Smart Matches are user-contributed trees
(Tier D). Record Matches from indexed civil records are Tier C (cross-reference
with the original archive for Tier B).

## Reading your Site ID

At session start, read the `MYHERITAGE_SITE_ID` from `.env`. All MyHeritage
URLs below use `{SITE_ID}` as a placeholder — substitute your actual value.

## Login workflow

MyHeritage requires authentication. The Playwright session persists cookies,
so login is only needed once per browser session.

### 1. Check if already logged in

Navigate to any MyHeritage page:

```
browser_navigate → https://www.myheritage.com/research
```

If the snapshot shows a user name button with "Rekeningopties" in the header,
you're logged in. Skip to the appropriate workflow below.

If it shows `button "Log in"`, proceed to step 2.

### 2. Remove cookie overlays

MyHeritage has aggressive cookie banners that block interaction. Remove them
with `browser_run_code` BEFORE trying to click anything:

```javascript
async (page) => {
  await page.evaluate(() => {
    ['cookie_preferences_banner_root', 'cookie_preferences_dialog_root'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.remove();
    });
    document.querySelectorAll('.cookie_banner_overlay, .modal_overlay').forEach(el => el.remove());
  });
  return 'Overlays removed';
}
```

### 3. Log in

Click the "Log in" button. A dialog appears with email and password fields:

- Fill `textbox "E-mailadres"` with `MYHERITAGE_USER` from `.env`
- Fill `textbox "Wachtwoord"` with `MYHERITAGE_PASSWORD` from `.env`
- Click `button "Inloggen"`

**Important:** Read credentials from `.env` using the Read tool — do NOT
hardcode them.

After login, a banner may show "De grens van de stamboom is overschreden"
(tree limit exceeded). This is normal on the Basic plan — ignore it.

### 4. Ensure correct site

After login, check the header for your site name. If it shows a different
site, the session defaulted to another one. The Site ID in the URLs below
ensures the correct site is used.

## Workflow A: Browse matches for a person (Discovery Hub)

### 1. Navigate to Discovery Hub

```
browser_navigate → https://www.myheritage.com/discovery-hub/{SITE_ID}/matches-by-people
```

This shows a paginated list of persons sorted by match value, with tabs:

- **Alle overeenkomsten** — all matches (Record + Smart combined)
- **Record Matches** — matches to historical records
- **Smart Matches** — matches to other users' trees

Each person entry shows:
- Person name and relationship to tree owner
- Spouse and children
- "Nieuwe info:" summary of what the match offers (dates, places, parents, etc.)
- "Beoordeel N matches" link to review matches for that person

### 2. Find a specific person

Click the "Vind een persoon" (Find a person) button to search by name within
the matches list. Alternatively, use the direct URL:

```
browser_navigate → https://www.myheritage.com/discovery-hub/{SITE_ID}/matches-for-person/{personId}
```

Person IDs can be found from the matches list (in the href of each person's link).

### 3. Review matches for a person

Click "Beoordeel N matches" to see all matches for that person. Each match shows:

- **Source:** other user's tree name, or historical record collection
- **Match type:** Smart Match (tree) or Record Match (historical record)
- **Data available:** names, dates, places, relationships
- **Side-by-side comparison** of your data vs the match

### 4. Extract useful data

From the match detail, extract:
- Birth date and place (if missing from your tree)
- Death date and place
- Occupation
- Parents' names
- Siblings
- Marriage details
- Archive references (for Record Matches)

**Do NOT confirm or reject matches** — this would modify the tree.

## Workflow B: SuperSearch (historical records)

Search 39 billion records across all categories.

### 1. Navigate to SuperSearch

```
browser_navigate → https://www.myheritage.com/research?s={SITE_ID}
```

### 2. Fill the search form

| Field | Label | Type |
|-------|-------|------|
| First names | "Voorna(a)m(en)" | textbox |
| Last name | "Achternaam" | textbox |
| Birth year | "Geboortejaar" | textbox |
| Place | "Plaats" | textbox |

Click "Voeg details toe" (Add details) to expand additional fields:
- Father, Mother, Partner (each with first name + last name)
- Death year and place
- More options (gender, etc.)

### 3. Submit and read results

Click "Zoeken" (Search). Results are grouped by category with counts.
Each result shows: person name, dates, place, collection name.

### 4. View a result

Click a result to see details. On the free plan:
- **Summary data** is visible (names, dates, places, relationships)
- **Full record details** may require a Data subscription for some collections
- **Original images** are typically behind the paywall

### 5. Record categories (with counts)

| Category | Records |
|----------|---------|
| Kranten (Newspapers) | 19.4B |
| Stambomen (Family Trees) | 9.5B |
| Geboorte/Huwelijk/Overlijden (BMD) | 4.7B |
| Volkstellingen (Censuses) | 1.8B |
| Adreslijsten (Directories) | 1.0B |
| Boeken (Books/Publications) | 856M |
| Foto's (Photos) | 472M |
| Immigratie (Immigration) | 294M |
| Scholen (Education) | 282M |
| Leger (Military) | 275M |
| Publieke records | 265M |
| Overheid/Eigendom/Rechtbank | 172M |

## Workflow C: Browse connected family sites

After login, navigate to your family site settings to find connected sites.
These are other researchers' trees where you've been added as a member.
Each connected site has its own Site ID in the URL.

To browse a connected site's tree:

```
browser_navigate → https://www.myheritage.com/family-trees/{site-slug}/{CONNECTED_SITE_ID}
```

Connected sites with PremiumPlus plans may show more data than your own plan allows.

## Workflow D: Photo tools

Navigate to the photo world:

```
browser_navigate → https://www.myheritage.com/photo-world/{SITE_ID}
```

Available tools (limited free uses per day):
- **In Color** — colorize black & white photos
- **Photo Enhancer** — improve resolution and quality
- **Deep Nostalgia** — animate still photos
- **LiveMemory** — create video from photos

## Output format

### For Discovery Hub matches

```
## MyHeritage Match — [Smart Match / Record Match]

**Person:** [name]
**Relationship:** [relationship to tree owner]

**New info from match:**
- Birth: [date] in [place]
- Death: [date] in [place]
- Occupation: [occupation]
- Father: [name]
- Mother: [name]
- Siblings: [names]

**Match source:** [other tree name / record collection]
**Person ID:** [personId from URL]

**Confidence:** Tier D — Smart Match from user-contributed tree
(or Tier C — Record Match from indexed historical record)
```

### For SuperSearch results

```
## MyHeritage SuperSearch Result — [record type]

**Person:** [name]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]
**Spouse:** [name] (if applicable)

**Collection:** [collection name]
**Category:** [BMD / Census / Military / etc.]
**Full record:** [visible / requires Data subscription]

**Confidence:** Tier C — indexed record via MyHeritage SuperSearch
(verify with original archive for Tier B)
```

## Key quirks

- **Language:** The UI is in Dutch (myheritage.nl). Button labels, field names,
  and messages are all Dutch.
- **Cookie overlays:** Must be force-removed before any interaction — they block
  clicks even after "accepting" them. Always run the overlay removal code first.
- **Tree limit banner:** "De grens van de stamboom is overschreden" appears on
  every page on the Basic plan. Ignore it — it doesn't block read operations.
- **Site switching:** If the account has multiple sites, always use URLs with the
  correct Site ID from `.env` to ensure you're on the right site.
- **Do NOT edit:** Do not confirm/reject matches, add people, or modify anything.
  The tree is read-only. Your local GEDCOM / Gramps Web is the source of truth.
- **Name prefixes:** Dutch name prefixes ("de", "van", "van de") may be handled
  differently. Try with and without prefix if results are sparse.
