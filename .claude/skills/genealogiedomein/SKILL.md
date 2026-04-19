---
name: genealogiedomein
description: |
  Browse and download free scans of DTB registers (doopboek, trouwboek,
  begraafboek), rechterlijk archief, notarial records, tax rolls, and
  cadastral maps from Genealogiedomein.nl — J.B. Baneman's
  digitaliseringsproject covering the Achterhoek and Liemers regions.
  Scans are hosted on the Genealogiedomein Flickr account as public photo
  albums. Uniquely valuable for pre-1811 NH church records from Didam,
  Zeddam, Winterswijk, Lochem, 's-Heerenberg, Aalten, Bergh, Borculo,
  Doesburg, and ~30 more Achterhoek villages — records that are often NOT
  indexed on OpenArchieven or WieWasWie. Use this skill whenever
  researching families in the Achterhoek or Liemers before 1811, looking
  up NH doopboek/trouwboek entries that no indexed database has, or when
  OpenArchieven returns zero hits for a pre-1811 village in Gelderland.
  Triggers on: "Achterhoek church records", "Didam doopboek", "Zeddam
  doopboek", "NH doopboek <village>", "Liemers", "Genealogiedomein",
  "Baneman", "/genealogiedomein". No login required. No API — content is
  discovered via Google site search and Flickr album URLs extracted from
  small HTM "verwijsfiche" cards.
---

# Genealogiedomein.nl — Achterhoek & Liemers DTB Scans

Genealogiedomein.nl is J.B. Baneman's 15+ year digitiseringsproject for
the Achterhoek and Liemers regions. It hosts free scans of church,
judicial, notarial, and tax records for villages that are often poorly
covered by OpenArchieven, WieWasWie, or the Gelders Archief indexes.

**Why this matters:** the Achterhoek NH doopboeken are largely
un-transcribed. OpenArchieven and WieWasWie index only a fraction. For
any pre-1811 village-level lookup in Didam, Zeddam, Winterswijk, Lochem,
's-Heerenberg, Bergh, Borculo, Doesburg etc., Genealogiedomein.nl often
has the only free scans online.

No login required. No API. The architecture is:

1. Genealogiedomein.nl has an HTML category tree per village
2. Each "scan" entry is a tiny HTM "verwijsfiche" (reference card) file
3. The verwijsfiche contains a link to a Flickr album hosted on the
   `genealogiedomein` Flickr account
4. Flickr photos are public-viewable, large-size (`_h.jpg` = 1600px)
   downloadable via static CDN URLs

Some verwijsfiches point to external sources (FamilySearch, Gelders
Archief) instead of Flickr — check the HTM file.

## Coverage

**Region:** Achterhoek + Liemers (eastern Gelderland)

**Time period:** ~1500 - ~1950, with strong focus on 1600-1811

**Key villages with digitised NH church records (not exhaustive):**

- Didam, Zeddam, 's-Heerenberg, Wehl, Kilder, Beek, Stokkum
- Winterswijk, Aalten, Dinxperlo, Varsseveld, Silvolde
- Doesburg, Drempt, Hummelo, Olburgen, Steenderen, Keppel
- Lochem, Laren, Ruurlo, Vorden, Warnsveld, Zutphen
- Borculo, Eibergen, Neede, Gelselaar, Geesteren
- Ulft, Netterden, Gendringen
- Duits Grensgebied — German border parishes with Dutch ties

**Record types beyond DTB:**

- Oud Rechterlijk Archief (ORA) — judicial records 1500-1811
- Notarieel Archief — notarial records
- Bevolkingsregister 1830-1938 — population registers
- Burgerlijke Stand 1811-1950 — civil registry (Genlias transcripts)
- Verpondingskohier, Overdrachtsbelasting (penningen) — tax rolls
- Kadastrale Gemeente kaarten — cadastral maps
- Dienstplicht, Joodse bevolking, Naamsaanneming 1812

## Access method

Two-phase HTTP workflow. No browser automation needed.

### Phase 1: Discover the verwijsfiche (reference card)

The site's built-in search box **does not find documents by person
name** — it only filters the category tree. For name-based discovery,
use **Google site search**.

For known-village / known-record-type lookup, navigate the category tree
directly:

```
https://www.genealogiedomein.nl/digitaal-mainmenu-27/<village>-digitale-genealogische-brongegevens/
```

### Phase 2: Extract the Flickr album URL from the verwijsfiche

Each digitised record is served as a tiny static HTM file (the
"verwijsfiche" = reference card). The HTM contains one `<a href="...">`
pointing to the Flickr album.

Download the HTM:

```bash
curl -sL "https://www.genealogiedomein.nl/<verwijsfiche-path>/file" -o /tmp/vf.htm
grep -oE 'flickr\.com/[^"]+' /tmp/vf.htm
```

### Phase 3: Extract photo IDs from the Flickr album page

Fetch the album HTML (no auth needed, ~600KB):

```bash
curl -sL -A "Mozilla/5.0" "https://www.flickr.com/photos/genealogiedomein/sets/<ALBUM_ID>/" -o /tmp/album.html
grep -oE '"id":"[0-9]{10}"' /tmp/album.html | sort -u
```

### Phase 4: Resolve large-size URLs

Flickr's page 1 renders only the first 20 photos with pre-baked
`_h.jpg` URLs. For photos beyond 20 OR for the authoritative
1600px URL, fetch each photo's `/sizes/h/` page and extract the
static URL. The `_h.jpg` variant has a **different secret** than
the `_b.jpg` / `_m.jpg` variants, so you cannot just swap suffixes.

```python
import re, subprocess, concurrent.futures as cf

def resolve(pid: str) -> str:
    out = subprocess.run(
        ["curl", "-sL", "-A", "Mozilla/5.0",
         f"https://www.flickr.com/photos/genealogiedomein/{pid}/sizes/h/"],
        capture_output=True, text=True,
    ).stdout
    m = re.search(rf'live\.staticflickr\.com/\d+/{pid}_[a-z0-9]+_h\.jpg', out)
    return f"https://{m.group(0)}" if m else ""

with cf.ThreadPoolExecutor(max_workers=10) as ex:
    urls = list(ex.map(resolve, photo_ids))
```

### Phase 5: Download scans

```bash
curl -sL -o "scan_0001.jpg" "https://live.staticflickr.com/8446/7885271542_c741c9ca9e_h.jpg"
```

Typical scan: 500-900 KB JPEG, 1600x1000-ish px. 20 scans ~= 12 MB.

## Workflow: browsing the Didam NH doopboek (RQ-014 Lebbing)

The Didam Nederduits Gereformeerde Gemeente doopboek is split across
two Flickr albums, covering the full period 1697-1768. This is the
target source for finding children of Jan (Gerritsen) × Guetjen /
Guurtje, registered under patronymic "Jansen" not surname "Lebbing".

| Period | Photos | Flickr album ID |
|--------|--------|-----------------|
| 1697-1719 (RBS 454.3) | 20 | `72157631299841730` |
| 1719-1768 (RBS 454.3) | 30 | `72157631465619634` |

**Verwijsfiche URLs (authoritative entry points):**

- 1697-1719: `https://www.genealogiedomein.nl/digitaal-mainmenu-27/didam-digitale-genealogische-brongegevens/didam-afbeeldingen-n-h-doopboek/3639-didam-afbeeldingen-n-h-doopboek-periode-1697-1719/file`
- 1719-1768: `https://www.genealogiedomein.nl/digitaal-mainmenu-27/didam-digitale-genealogische-brongegevens/didam-afbeeldingen-n-h-doopboek/3649-didam-afbeeldingen-n-h-doopboek-periode-1719-1768/file`

**Total: 50 scans covering ~71 years.** That's fewer than one photo
per year on average — the doopboek is thin because NH Didam was small
(the village was predominantly Catholic). Each photo typically shows
one full page spread with multiple baptism entries.

### End-to-end: download all Didam NH doopboek scans

```python
import re, subprocess, os, concurrent.futures as cf

ALBUMS = {
    "1697-1719": "72157631299841730",
    "1719-1768": "72157631465619634",
}
OUT_DIR = "private/sources/genealogiedomein/didam-nh-doop"
os.makedirs(OUT_DIR, exist_ok=True)

def resolve_and_download(period: str, pid: str) -> tuple[str, int]:
    sizes_url = f"https://www.flickr.com/photos/genealogiedomein/{pid}/sizes/h/"
    html = subprocess.run(
        ["curl", "-sL", "-A", "Mozilla/5.0", sizes_url],
        capture_output=True, text=True,
    ).stdout
    m = re.search(rf'live\.staticflickr\.com/\d+/{pid}_[a-z0-9]+_h\.jpg', html)
    if not m:
        return pid, 0
    url = f"https://{m.group(0)}"
    path = f"{OUT_DIR}/didam_{period}_{pid}.jpg"
    subprocess.run(["curl", "-sL", "-o", path, url], check=True)
    return pid, os.path.getsize(path)

for period, album_id in ALBUMS.items():
    album_url = f"https://www.flickr.com/photos/genealogiedomein/sets/{album_id}/"
    album_html = subprocess.run(
        ["curl", "-sL", "-A", "Mozilla/5.0", album_url],
        capture_output=True, text=True,
    ).stdout
    photo_ids = sorted(set(re.findall(r'"id":"(7[89][0-9]{8})"', album_html)))
    print(f"{period}: {len(photo_ids)} photos")
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        for pid, size in ex.map(lambda p: resolve_and_download(period, p), photo_ids):
            print(f"  {pid}: {size} bytes")
```

Total download time: ~10-15 seconds for all 50 scans.

### Reading the handwriting with Claude vision

The photos are at ~1600 px width, sufficient for 18th-century clerical
Dutch handwriting. Pass each downloaded JPEG through the Read tool
(images are rendered as multimodal content) and ask Claude to extract
every baptism entry in the format:

```
Date | Child | Father | Mother | Witnesses | Notes
```

Specifically for the Lebbing lookup (RQ-014), ask for any entry where
the father is recorded as "Jan Gerritsen", "Jan Gerrits", "Jan",
"Johannes", or similar with mother "Guetjen", "Goetjen", "Guurtje",
"Gurtjen", or "Geurtje". The surname "Lebbing" itself will almost
certainly NOT appear — the family was registered under patronymic.

### Paired source: Didam NH trouwboek and marriage transcripts

The NH trouwboek 1697-1719 scans are also on Flickr (verwijsfiche
`3637`). The marriage transcripts 1637-1809 ("goed leesbare
handgeschreven afschriften") by Knipscheer are hosted **externally**
on FamilySearch:

- Image viewer: `https://www.familysearch.org/ark:/61903/3:1:3Q9M-CS15-1QBW-D?cat=144526`
- Catalogue: Gelders Archief toegang 0176, RBS 454.2

The Knipscheer transcripts are hand-written 19th-century copies that
are much easier to read than the original records. When a marriage is
in scope, ALWAYS check the transcript first via the `familysearch`
skill.

| Period | Source | Location |
|--------|--------|----------|
| Trouwboek 1697-1719 original | Flickr album | verwijsfiche 3637 |
| Huwelijken 1637-1664 afschrift | FamilySearch | Knipscheer 6687 |
| Huwelijken 1665-1698 afschrift | FamilySearch | Knipscheer 6686 |
| Huwelijken 1697-1719 afschrift | FamilySearch | Knipscheer 6685 |
| Huwelijken 1719-1768 afschrift | FamilySearch | Knipscheer 6684 |
| Huwelijken 1768-1809 afschrift | FamilySearch | Knipscheer 6683 |

## Workflow: generic village lookup (pre-1811 DTB)

1. **Identify the village** and record type needed.

2. **Discover the verwijsfiche** via Google:

   ```
   WebSearch: site:genealogiedomein.nl <village> doopboek afbeeldingen
   WebSearch: site:genealogiedomein.nl <village> trouwboek afbeeldingen
   ```

   Or navigate the category tree:

   ```
   https://www.genealogiedomein.nl/digitaal-mainmenu-27/<village>-digitale-genealogische-brongegevens/
   ```

3. **Download the verwijsfiche**:

   ```bash
   curl -sL "<verwijsfiche-url>/file" -o /tmp/vf.htm
   grep -oE 'flickr\.com/[^"]+' /tmp/vf.htm
   ```

4. **Extract photo IDs** from the Flickr album and **resolve + download
   large-size URLs** via the 5-phase workflow above.

5. **Read the scans** via Claude vision for the target name/date.

## Site-search limitations

- The genealogiedomein.nl built-in search (`?filter[search]=`) echoes
  the query but returns the default category tree, not matching
  documents. **Do not rely on it.**
- Document titles rarely include person names — scans are titled by
  period ("1697-1719"), not indexed by family.
- **Use Google `site:genealogiedomein.nl` for name or village discovery.**
  Google has indexed the HTML category pages but NOT the Flickr image
  content.
- Flickr photo titles are sequential numbers ("0001 (fotonummer) -
  Didam..."), not dates. You must visually scan the images to find
  a specific entry.

## Flickr gotchas

- **Anonymous view renders only 20 photos per page** with pre-baked
  `_h.jpg` URLs on the album page. For albums with >20 photos, resolve
  the rest via `/sizes/h/` on each photo page.
- **The `_h.jpg` (1600px) variant uses a different secret** than
  `_b.jpg` (1024px) or `_m.jpg` (500px). You cannot swap suffixes —
  you must fetch the `/sizes/h/` page to get the real URL.
- `_k.jpg` (2048px) and `_o.jpg` (original) are **usually 410 Gone** for
  this account — the uploader only enabled large-size sharing up to `_h`.
- Flickr album URLs use `/sets/<id>/` or `/albums/<id>/` — both work.
- User-agent required: `Mozilla/5.0` — bare curl UA returns abbreviated
  HTML that's missing the photo ID JSON blob.

## HTM verwijsfiche URL convention

File IDs are assigned by Joomla JDownloads. The URL pattern is:

```
/<category-path>/<numeric-id>-<slug>/file
```

Example:

```
https://www.genealogiedomein.nl/digitaal-mainmenu-27/
  didam-digitale-genealogische-brongegevens/
  didam-afbeeldingen-n-h-doopboek/
  3639-didam-afbeeldingen-n-h-doopboek-periode-1697-1719/file
```

The `/file` suffix triggers the attachment download; without it, you
get the HTML wrapper page. Always append `/file` to the verwijsfiche
link.

## Output format

When reporting findings from Genealogiedomein.nl:

```
**Source:** Genealogiedomein.nl — <village> NH <record type> <period>
**Archive ref:** Gelders Archief, toegang 0176 (RBS), inv.nr. <...>
**Record:** <transcription of baptism/marriage entry>
**Photo URL:** https://live.staticflickr.com/<server>/<photoid>_<secret>_h.jpg
**Album URL:** https://www.flickr.com/photos/genealogiedomein/sets/<album_id>/
**Verwijsfiche:** https://www.genealogiedomein.nl/<verwijsfiche-path>
**Confidence:** Tier A — primary source scan read directly (when Claude
vision transcription is confirmed); Tier B when quoting an existing
index/transcription alongside the scan
```

Baptism/marriage records read directly from scans are **Tier A**
(primary source). These are the same scans the Gelders Archief would
show on a reading-room microfilm — Baneman just made them free.

## Rate limits

- **Genealogiedomein.nl**: Joomla site, no rate limit observed. Be
  polite — 1-2 req/sec for discovery, space out bulk fetches.
- **Flickr static CDN** (`live.staticflickr.com`): no observed rate
  limit for anonymous downloads. 10 parallel downloads is fine.
- **Flickr photo pages** (for `/sizes/h/` resolution): 10 parallel
  requests works; >20 may hit throttling.

## Known limitations

- **Scans are NOT OCR'd or transcribed** — every lookup requires
  Claude vision reading the handwriting. Budget ~1 vision call per
  scan page for targeted lookups.
- **No name-level search index** — Google indexes only the category
  page titles, not scan contents.
- **Not every record is on Flickr** — some verwijsfiches link to
  FamilySearch, Gelders Archief Memorix, or external viewers. Check
  the HTM content before assuming.
- **Coverage is uneven** — some villages have the full NH DTB stack,
  others only have a single period or only tax/cadastral records.
  Always check the category page index first.
- **RK (Catholic) records are sparse on this site** — Baneman's focus
  is NH and civic administration. For RK doopboeken in the Achterhoek,
  try the Gelders Archief Memorix viewer or FamilySearch directly.
  **Relevant for RQ-014 (Lebbing/Didam): Didam was predominantly
  Catholic, so the NH doopboek is thin. If the target family was RK,
  the scans here may not contain them at all.**
- **Photos have windows-1252 encoded titles** in the HTM verwijsfiche
  files; use `iconv -f cp1252 -t utf-8` if diacritics matter.

## Related skills

- **openarchieven-api** — check first for indexed BS/DTB entries. If
  the Achterhoek village returns zero hits pre-1811, fall back to
  genealogiedomein for the raw scans.
- **familysearch** — for Knipscheer marriage transcripts linked from
  genealogiedomein verwijsfiches.
- **wiewaswie-api** — same reasoning as openarchieven.
- **verify-scans** — use to present downloaded genealogiedomein scans
  to the human for Tier A confirmation.
