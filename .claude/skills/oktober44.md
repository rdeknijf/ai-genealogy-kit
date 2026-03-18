---
name: oktober44
description: |
  Search the Stichting Oktober 44 database of 589 men deported from Putten to
  Neuengamme concentration camp during the WWII razzia of October 1-2, 1944.
  Use this skill whenever researching Putten families during WWII, checking if
  a person was among the Putten deportees, or investigating wartime fates of
  Veluwe residents. Triggers on: "check Putten razzia", "search Oktober 44",
  "was he deported from Putten", "/oktober44", or any WWII research involving
  Putten. Only 48 of the 589 men returned; 552 died in camps. No login required.
---

# Stichting Oktober 44 — Putten Razzia Database

Search the database of men deported from Putten during the razzia of October 1-2,
1944. Contains ~660 records including the 589 deportees and some related persons.

No login required. Static HTML, no JavaScript-heavy UI.

## Important context

On October 1, 1944, German forces surrounded Putten and deported 589 men and boys
to concentration camps (primarily Neuengamme) as reprisal for a resistance attack.
Only 48 returned. This is one of the most devastating reprisal actions in Dutch
WWII history.

## Search

### 1. Navigate to the deportee page

```
browser_navigate → https://oktober44.nl/weggevoerde-mannen
```

### 2. Search by surname

The page has a search box labeled "Zoek op achternaam" with a "Zoeken" button.
Type the surname (or part of it) and click "Zoeken".

Alternatively, use the A-Z letter links below the search box to browse by
surname initial. Clicking a letter loads all entries for that letter via:
`showman.php?v={letter}%`

All entries for a letter appear on a single page — no pagination.

### 3. Scan the listing

Each entry shows:
- **Name** (bold)
- Geboortedatum (birth date, DD-MM-YYYY)
- Geboorteplaats (birth place)
- Overlijdensdatum (death date, DD-MM-YYYY — blank if unknown)
- "Lees meer" link to detail page

Find the matching person and click "Lees meer".

### 3. Detail page

URL pattern: `https://oktober44.nl/weggevoerde-mannen/{id}/{name_slug}`

Fields available:

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

## Alternative: browse all records

Since there are only ~660 records, you can iterate all 26 letters to find any
person. The URL `showman.php?v=%` may return all records at once.

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
