---
name: oktober44-optimized
description: |
  Search the Stichting Oktober 44 database of 589 men deported from Putten to
  Neuengamme concentration camp during the WWII razzia of October 1-2, 1944.
  Uses direct HTTP calls (WebFetch/curl) instead of browser automation — the site
  is static HTML. Use this skill whenever researching Putten families during WWII,
  checking if a person was among the Putten deportees, or investigating wartime
  fates of Veluwe residents. Triggers on: "check Putten razzia", "search Oktober
  44", "was he deported from Putten", "/oktober44", or any WWII research involving
  Putten. Only 48 of the 589 men returned; 552 died in camps. No login required.
  Parallelizable — no browser needed.
---

# Stichting Oktober 44 — Putten Razzia Database

Search the database of men deported from Putten during the razzia of October 1-2,
1944. Contains ~660 records including the 589 deportees and some related persons.

No login required. Static HTML — no JavaScript needed, fully accessible via HTTP.

## Important context

On October 1, 1944, German forces surrounded Putten and deported 589 men and boys
to concentration camps (primarily Neuengamme) as reprisal for a resistance attack.
Only 48 returned. This is one of the most devastating reprisal actions in Dutch
WWII history.

## Primary method: HTTP (WebFetch/curl)

### Browse by letter

The site organizes entries by surname initial. Use WebFetch on:

```
https://oktober44.nl/showman.php?v={LETTER}%25
```

Replace `{LETTER}` with a lowercase letter (a-z). The `%25` is URL-encoded `%`
wildcard. Returns all entries for that letter on a single page.

Ask WebFetch to extract: names, birth dates, birth places, death dates, and
detail page URLs ("Lees meer" links).

### Search by surname

To search for a specific surname, use the letter of the first character:

```
WebFetch → https://oktober44.nl/showman.php?v=K%25
  prompt: "Find all entries with surname matching 'Knoppert'. Extract name, birth date, birth place, death date, and detail page URL."
```

Since there are only ~660 records total across 26 letters, you can also search
by browsing the relevant letter(s).

### View detail page

Detail pages are at:

```
https://oktober44.nl/weggevoerde-mannen/{id}/{name_slug}
```

Use WebFetch to extract all fields:

```
WebFetch → https://oktober44.nl/weggevoerde-mannen/314/gerrit__knoppert
  prompt: "Extract all person details: name, birth date/place, parents, marital status, children, occupation, address, death date/place, burial location, camp numbers, and remarks."
```

**Fields available on detail pages:**

| Dutch label | English | Notes |
|-------------|---------|-------|
| Geboortedatum | Birth date | DD-MM-YYYY |
| Geboorteplaats | Birth place | |
| Zoon van | Parents | "Son of [father] en [mother]" |
| Getrouwd | Marital status | "Ongehuwd" / "Getrouwd met [name]" / "Verloofd met [name]" |
| (children) | Children count | Only if applicable |
| Beroep | Occupation | |
| Woonadres | Address | Sometimes two addresses with `/` |
| Overlijdensdatum | Death date | DD-MM-YYYY |
| Plaats van overlijden | Place of death | Camp name or town |
| Begraafplaats | Burial location | |
| Kamp nr Amersfoort | Amersfoort camp number | |
| Kamp nr Neuengamme | Neuengamme camp number | |
| Sachsenhausen / other | Other camp numbers | Some went through multiple camps |
| Opmerkingen | Remarks | Liberation details for survivors, execution details |

Some entries include gravestone photos in a lightbox gallery.

## Distinguishing survivors from deceased

Same fields are used for all. Survivors have later death dates (1960s-2000s) and
the "Opmerkingen" field contains liberation/release details.

## Fallback: Playwright browser automation

Only needed if the site adds JavaScript-dependent features or blocks HTTP requests.
Currently unnecessary — the site is fully static HTML.

Navigate to `https://oktober44.nl/weggevoerde-mannen`, use the A-Z letter links
or the search box labeled "Zoek op achternaam".

## Output format

```
## Oktober 44 Result — Putten Deportee

**Person:** [name]
**Born:** [date] in [place]
**Parents:** [father] en [mother]
**Marital status:** [status]
**Occupation:** [occupation]
**Address:** [address]

**Died:** [date] in [place]
**Burial:** [location]
**Camp numbers:** Amersfoort [nr], Neuengamme [nr]
**Remarks:** [text]

**Confidence:** Tier B — verified deportee database maintained by Stichting Oktober 44
```
