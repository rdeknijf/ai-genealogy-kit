---
name: stenen-archief
description: |
  Search Het Stenen Archief (nld.stenenarchief.nl), the Dutch "Stone
  Archive" of transcribed Jewish gravestones. Covers Jewish cemeteries
  across all 12 Dutch provinces - Muiderberg, Ouderkerk aan de Amstel,
  Diemen, Rotterdam (Toepad), Nijkerk, plus Friesland (Leeuwarden,
  Bolsward, Harlingen, Heerenveen, Lemmer, Sneek, Workum, Gorredijk,
  Noordwolde), and cemeteries in every other province. Use this skill
  whenever researching Dutch Jewish ancestors, looking up a grafsteen /
  matzeva, parsing Hebrew patronymics, or checking whether a Dutch
  branch has Jewish roots before declaring a dead end. Strongest
  coverage is 18th-20th century. Triggers on: "Joodse begraafplaats",
  "Jewish cemetery", "Stenen Archief", "grafsteen", "matzeva",
  "Muiderberg", "Ouderkerk", "hsa_view", "/stenen-archief", or any
  query about Dutch-Jewish burial records. Uses direct HTTP calls
  (curl / WebFetch) against the Manticore Search backend - no browser,
  no login, no rate limit. Fully parallelizable.
---

# Het Stenen Archief - Dutch Jewish Cemeteries

Search the transcribed gravestone database maintained by Stichting Het
Stenen Archief. Records include the deceased's name, Hebrew patronymic,
Hebrew and Gregorian death dates, burial date, cemetery, full Hebrew
gravestone text with Dutch transcription and translation, scholarly
commentary, and in most cases a photograph of the stone.

This site is fully accessible over plain HTTP. The `/zoeken` search
page calls an XHR backend that returns an HTML table fragment - no
JavaScript rendering needed, no login required, no rate limit
observed. That makes it ideal for scripted / parallel lookups.

## Scope and coverage

- **Religion:** Jewish cemeteries only (Ashkenazi and some Sephardic).
  Do not use for non-Jewish burials - non-Jewish surnames typically
  return zero hits. Use `online-begraafplaatsen` for general Dutch
  burial records.
- **Geography:** all 12 Dutch provinces. The largest indexes are
  Muiderberg (Noord-Holland, tens of thousands of entries) and
  Ouderkerk aan de Amstel (the old Sephardic Beth Haim).
- **Time period:** primarily 18th-20th century, with the oldest stones
  going back to the 17th century.
- **Friesland cemeteries indexed:** Bolsward, Gorredijk, Harlingen,
  Heerenveen, Leeuwarden, Lemmer, Noordwolde, Sneek, Workum.
- **Why run this even for non-obviously-Jewish branches:** Dutch
  Jewish-Christian intermarriage was not rare, and surname adoption
  (naamsaanname 1811-1812) introduced many non-religious surnames
  into Jewish families. A quick HTTP call costs nothing and can
  rescue a genuinely stuck line.

## Access method: direct HTTP, no browser

### Search endpoint

```
GET https://nld.stenenarchief.nl/manticoresearch.php?q={QUERY}&sort=1
```

| Param | Meaning |
|-------|---------|
| `q`    | Search term: surname, first name, patronym, or cemetery name |
| `sort` | `1` = sort by name, `2` = sort by last-updated date |

The backend is Manticore Search with a "klinkt-als" (sounds-like)
fuzzy matcher. It searches across the deceased's name, their partner,
and their parents simultaneously, so a single query often surfaces
whole family groups. Diacritics and common transliteration variants
are tolerated.

**Example:**

```bash
curl -sL "https://nld.stenenarchief.nl/manticoresearch.php?q=Cohen&sort=1"
```

The response is an HTML table fragment. Each row looks like:

```html
<tr>
  <td><a href="https://stenenarchief.nl/hsa_all/hsa_view.php?editid1=6567">
    Benjamin z.v. Me'ir ha-Cohen onbekend
  </a></td>
  <td>Nijkerk</td>
</tr>
```

Parse `editid1=(\d+)` for the record ID, and the second `<td>` for
the cemetery name. You can also feed the whole fragment to WebFetch
with an extraction prompt.

**Result cap:** large surname queries cap out around 1000 rows.
If you hit the cap, narrow the query: combine with a first name
(`Cohen Benjamin`), a town (`Cohen Leeuwarden`), or search by
patronym instead.

### Record detail page

```
GET https://stenenarchief.nl/hsa_all/hsa_view.php?editid1={ID}
```

Note the domain change from `nld.stenenarchief.nl` (WordPress front
end) to `stenenarchief.nl` (the actual record viewer). Both are part
of the same archive - don't treat them as separate sites.

The useful field values live inside `<span>` elements with stable IDs:

| Span ID | Dutch label | Content |
|---------|-------------|---------|
| `view1_last_name` | Achternaam | Surname, or "onbekend" for pre-emancipation records |
| `view1_patronym` | Patronym | Hebrew-style name: `Benjamin z.v. Me'ir ha-Cohen` |
| `view1_death_date` | Overlijdensdatum | `DD-MM-YYYY` (Gregorian) |
| `view1_death_date_hebrew` | Overlijdensdatum Hebr | e.g. `20 Sivan 5552` |
| `view1_cemetery` | Begraafplaats | Cemetery name |
| `view1_burial_date` | Begraafdatum | `DD-MM-YYYY//HEBREW` |
| `view1_gravestone_text` | Grafsteen tekst | Dutch transcription |
| `view1_gravestone_text_hebrew` | Grafsteen tekst Hebr | Original Hebrew |
| `view1_translation_hebrew_text` | Vertaling Hebr. tekst | Dutch translation of Hebrew |
| `view1_comments_on_hebrew_text` | Commentaar Hebr | Scholarly notes on Hebrew |
| `view1_comments_on_translation` | Commentaar op vertaling | Biblical cross-references |
| `view1_grade` | Gradering | Photo / transcription quality tier (1 = best) |

Gravestone photos are embedded in `div.r-images`. The URL is in the
`data-images` JSON attribute, e.g.
`https://www.stenenarchief.nl/fotos/nijkerk(090)/(90)011.jpg`.

**Recommended extraction:** use WebFetch against the detail URL with a
prompt like: "Extract the person's name, patronym, cemetery, death
date (Gregorian and Hebrew), father name from the patronym, burial
date, and the gravestone photo URL." The span IDs are stable enough
that this works without custom regex.

### Browse by province

```
GET https://nld.stenenarchief.nl/{Province}
```

e.g. `/Friesland`, `/Noord-Holland`, `/Drenthe`. Each province page
lists its cemeteries with links like:

```
https://www.stenenarchief.nl/cemetery/{CemeteryName}
https://www.stenenarchief.nl/hsa_all/hsa_list.php?qs={Name}~cemetery~startswith
```

Useful when you know someone died in a specific town but cannot find
them by surname alone - browse the cemetery and filter locally.

## Search workflow

1. **Fuzzy-search the manticore endpoint** with the ancestor's surname
   (or Hebrew given name if surname is unknown).
2. **Filter the returned table** by the cemetery column if you know
   the geographic region. For a Frisian line, keep only rows with
   Friesland cemeteries; for Amsterdam, keep Muiderberg / Ouderkerk /
   Diemen.
3. **Fetch promising detail pages** via `editid1`. Extract Gregorian
   death date, patronym (often the only way to identify the father),
   and cemetery.
4. **Cross-reference** with civil registry death records (WieWasWie,
   OpenArchieven) and Delpher obituaries. A Stenen Archief hit alone
   is Tier B; confirmed against a BS death record it becomes Tier A.
5. **Archive the photo URL** in your finding. The grave image is a
   primary source - worth storing alongside the transcription.

## Example queries

```bash
# Common surname sweep (will hit ~1000 row cap)
curl -sL "https://nld.stenenarchief.nl/manticoresearch.php?q=Cohen&sort=1"

# Town/toponym search - catches anyone whose record mentions Leeuwarden
# as birthplace, origin, or patronym
curl -sL "https://nld.stenenarchief.nl/manticoresearch.php?q=Leeuwarden&sort=1"

# Full record detail
curl -sL "https://stenenarchief.nl/hsa_all/hsa_view.php?editid1=6567"

# Enumerate all cemeteries in Friesland
curl -sL "https://nld.stenenarchief.nl/Friesland"

# Cemetery page for Leeuwarden
curl -sL "https://www.stenenarchief.nl/cemetery/Leeuwarden"
```

## Output format

Format findings as:

```
## Stenen Archief Result - Jewish Cemetery Record

**Name:** [last_name / patronym]
**Cemetery:** [cemetery], [province]
**Died:** [DD-MM-YYYY] ([Hebrew date])
**Buried:** [DD-MM-YYYY]
**Father (from patronym):** [Hebrew father name, if parseable]
**Gravestone photo:** [URL]
**Source:** Het Stenen Archief, record [editid1]
**URL:** https://stenenarchief.nl/hsa_all/hsa_view.php?editid1=[ID]

**Confidence:** Tier B - transcribed gravestone with photo held by
Stichting Het Stenen Archief. Upgrade to Tier A once the user has
seen the photo and confirmed the transcription against it, or once
a civil registry BS death record corroborates.
```

## Limitations and gotchas

- **Jewish cemeteries only.** Do not use as a general Dutch burial
  index - `online-begraafplaatsen` covers the non-Jewish landscape.
- **Hebrew patronyms, not modern surnames.** Many pre-1812 records
  list "X son of Y ha-Cohen" with no family surname. To bridge into
  modern civil records, look at the naamsaanname registers of
  1811-1812 (held by Noord-Hollands Archief and others).
- **Aggressive fuzzy matching.** Sounds-like matching can return
  unrelated names that happen to sound similar. Always verify against
  the detail page before treating a hit as genuine.
- **Result cap ~1000 rows.** Common surnames (Cohen, Levie, de Vries)
  will hit the cap. Narrow with first name, cemetery, or patronym.
- **Cemetery labels are inconsistent.** Rotterdam appears as
  "Rotterdam (Toepad)"; Muiderberg as itself; Ouderkerk as "Ouderkerk
  aan de Amstel". Don't rely on exact string match when filtering -
  use `contains` / prefix match.
- **Two domains.** `nld.stenenarchief.nl` runs the WordPress front
  end, search endpoint, and province browse pages.
  `stenenarchief.nl` (and `www.stenenarchief.nl`) hosts the record
  viewer (`hsa_view.php`, `hsa_list.php`) and gravestone photos.
  Both belong to the same archive.

## Related skills

- `online-begraafplaatsen` - general Dutch cemetery database (non-Jewish)
- `cbg-verzamelingen` - CBG holdings including Dutch-Jewish genealogy
- `wiewaswie-api` - civil registry BS death records (cross-reference)
- `openarchieven-api` - indexed person records from Dutch archives
- `delpher-api` - newspaper obituaries and familieberichten
