---
name: gemeentearchief-putten
description: |
  Browse Gemeentearchief Putten — the municipal archive of Putten
  (Veluwe) at putten.nl/gemeentearchief. Covers everything EXCEPT the
  589 October 1944 razzia victims (those are in the separate
  `oktober44` skill). Unique material: 16 Puttens Historisch Genootschap
  family parentelen, DTB/lidmaten transcriptions 1597-1771, notarial
  "nadere toegang" PDFs, Puttensche Courant 1922-1931, and the
  naamsaanneming register 1812-1833. BS records go through
  `openarchieven-api` (code `gld` — Gelders Archief). Static HTML, no
  API, no login, no rate limit.
---

# Gemeentearchief Putten

Putten's archive is hosted on the municipal website under the generic
CMS — there is no MAIS / Memorix / OpenArchieven platform. But BS
records for Putten ARE indexed in Gelders Archief via OpenArchieven
(`gld --place Putten`). The Putten site adds unique PHG-curated
material that isn't anywhere else.

**Not to be confused with:**
- `oktober44` skill — the 589 razzia victims database (stichting
  oktober44.nl)
- Streekarchief Voorne-Putten — South Holland islands, unrelated
- Streekarchivariaat Noordwest-Veluwe — covers Elburg/Ermelo/Harderwijk/
  Nunspeet/Oldebroek but **not Putten**

## Access

**Static HTML, curl/WebFetch only.** The site's built-in search
(`/Zoeken?freetext=...`) **does NOT index genealogy HTML pages** —
it only returns PDFs (elections, riolering-plannen, policy).
Zero-genealogy noise. **Do not use site search** — navigate section
index URLs directly.

## BS/DTB via OpenArchieven

```bash
python scripts/openarchieven_search.py "Knoppert" --archive gld --place Putten
# -> 140 records for Knoppert family
```

## Unique Putten-site content (curated by PHG)

### Family parentelen (16 compiled genealogies)

Section index:
`https://www.putten.nl/gemeentearchief/Gemeentearchief/Genealogie`

Per-family pages, e.g.:
`https://www.putten.nl/gemeentearchief/Gemeentearchief/Genealogie/Genealogie_n/Tijmen_Beertsen_Staal`

Each parenteel is a multi-generation HTML tree with Harderwijk Ned.
Ger. DTB citations. Compiled by T. Elbertsen-Hoekstra and other PHG
members from jaarboekje issues.

Use `WebFetch` to read — content is inline HTML, no JS.

### DTB / lidmaten transcriptions 1597-1771

Transcribed from the Harderwijk NG classical church books covering
Puttens members. Section under `/Gemeentearchief/Genealogie/DTB/`.

### Notarial "nadere toegang" PDFs

Four notary indexes with stable `dsresource?objectid=<uuid>&type=pdf`
download URLs:

| Notary | Period | Notes |
|--------|--------|-------|
| Heyblom | 1812-1830 | Oldest available |
| Pliester | 1876-1901 | |
| Reijers | 1918-1919 | Short tenure |
| Deibert | 1919-1925 | |

PDFs are searchable text (extractable with `pdftotext -layout`).

### Puttensche Courant 1922-1931

Local newspaper, digitised text. Useful for death notices, marriage
announcements, obituaries of Putten residents before the war.

### Naamsaanneming 1812-1833

Register of surname adoptions under the Napoleonic decree. Critical
for pre-1811 to post-1811 family linking.

## Verified example

```bash
WebFetch https://www.putten.nl/gemeentearchief/Gemeentearchief/Genealogie/Genealogie_n/Tijmen_Beertsen_Staal
# -> full multi-generation Staal parenteel rooted on Tijmen Beertsen
#    Staal (ca. 1620) with Harderwijk NG DTB citations 1632-1649
```

## When to use

- **Any Putten-area BS lookup** — use openarchieven-api first with
  `gld --place Putten`.
- **Compiled PHG family parentelen** — only place online.
- **Notary deeds 1812-1925** — only indexed access.
- **Complement to `oktober44`** — use for victims' pre-1944 family
  context and for anyone NOT in the razzia database.

## Related skills

- **oktober44** — razzia victims only
- **openarchieven-api** — BS records via Gelders Archief `gld`
- **delpher-api** — for pre-1922 national newspaper notices
