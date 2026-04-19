# Datasource Candidates

Archives and databases discovered during research that might be worth
onboarding as skills. Agents add entries here; Rutger decides which
ones get built.

## How to add an entry

Append a new `##` section with this template:

```markdown
## [Name] — [region/scope]

- **URL:** https://...
- **Discovered:** [date], [finding number or session]
- **Why:** [what records it has, why it would help]
- **Record types:** [BS, DTB, bevolkingsregister, notarial, etc.]
- **Estimated size:** [if known]
- **Access method:** [API / Memorix / MAIS / Playwright / unknown]
- **Priority:** [HIGH / MEDIUM / LOW]
- **Status:** CANDIDATE
```

When a skill is created, change status to `ONBOARDED` and note the skill path.

---

## Henk Beijers Archiefcollectie — Brabant schepenprotocollen

- **URL:** https://www.henkbeijersarchiefcollectie.nl
- **Discovered:** 2026-04-03, F-1186 (RQ-013 session 4)
- **Why:** 60+ Schijndel schepenprotocol transcription files. Proved to be the most valuable source for Van der Kant / de Keteler research. Contains property transfers, estate divisions, witness lists from 1500s-1700s across multiple Brabant villages.
- **Record types:** Schepenprotocollen (transcriptions), estate divisions, property records
- **Estimated size:** Unknown, dozens of transcription files per village
- **Access method:** Google site search + direct .doc/.docx download with text extraction (no API, static HTML)
- **Priority:** HIGH
- **Status:** ONBOARDED — `.claude/skills/henk-beijers/SKILL.md`

## Noord-Hollands Archief bevolkingsregister — Haarlem region

- **URL:** https://noord-hollandsarchief.nl
- **Discovered:** 2026-04-03, F-1171 (RQ-017 session 1)
- **Why:** Needed for Makkelie household data in Haarlem. NHA has gezinskaarten and bevolkingsregister that aren't covered by existing skills. Also has schepelingen registers for maritime research (Dooitse Bakker, RQ-006).
- **Record types:** BS, DTB Dopen, bevolkingsregister, militieregisters, notarial, vredegerecht, overlijdensverklaring, memorie van successie, faillissementsdossier
- **Estimated size:** 12.7M person records
- **Access method:** OpenArchieven JSON API (primary, `archive=nha`) + MAIS URL parameters (`mivast=236`, fallback)
- **Priority:** HIGH
- **Status:** ONBOARDED — `.claude/skills/noord-hollands-archief/SKILL.md`

## Stadsarchief Delft — Delft region

- **URL:** https://zoeken.stadsarchiefdelft.nl
- **Discovered:** 2026-04-03, F-1176 (RQ-017 session 1)
- **Why:** Holds Teunisje Brouwer × Jacob de Knijf marriage record with scan (28 Sep 1923).
- **Record types:** BS, DTB, bevolkingsregister, notarial records
- **Estimated size:** 185+ Knijf records; covers Delft, Maasland, Schipluiden, Pijnacker, Rijswijk
- **Access method:** Clean URL search with session cookie (DeventIT Atlantis Web platform)
- **Priority:** LOW
- **Status:** ONBOARDED — `.claude/skills/erfgoed-delft/SKILL.md`

## ECAL archive 1210 — Doetinchemse IJzergieterij records

- **URL:** https://ecal.nu (within existing ECAL archive)
- **Discovered:** 2026-04-03, F-1184 (RQ-017 session 3)
- **Why:** Factory personnel records for Doetinchem foundries (DRU etc.). Jacob de Knijf worked as vormer (molder) there ~1914-1918. Very niche.
- **Record types:** Factory personnel records, wage books
- **Estimated size:** Small (single archive inventory)
- **Access method:** Physical archive only (not digitized)
- **Priority:** LOW
- **Status:** CANDIDATE

## Gelders Archief online viewer — image browsing for unindexed DTB pages

- **URL:** https://www.geldersarchief.nl/bronnen/archieven?mivast=37&mizig=0&miadt=37&miaet=54&micode=0176_454.01&minr=<MINR>&miview=ldt
- **Discovered:** 2026-04-10, F-1344/F-1345 (RQ-014 session 2)
- **Why:** Critical for Lebbing/Lebbink research. The Didam NDG baptism register (GA 0176/454.01) and Drempt NDG baptism register (GA 0176/986.1) are accessible as images via the GA viewer, but only a fraction is indexed in OpenArchieven. The 1665-1695 pages of Didam 454.01 would show children of Jan Gerritsen × Guetjen Janssen — one of whom may be Geurt Lebbink. The GA viewer works with curl (full HTML, 200) but the image itself requires JavaScript rendering. Headless playwright gets blocked ("Here be dragons" anti-bot). Requires: a non-headless browser session, or user manually browsing with `minr` values derived from OA records.
- **Record types:** DTB Dopen (baptism), DTB Begraven (burial), DTB Trouwen (marriage) — image scans
- **Estimated size:** GA holds all Gelderland DTB records pre-1811; many unindexed pages
- **Access method:** Playwright with headed browser (non-headless) OR user manual access via the GA website
- **Priority:** HIGH
- **Status:** CANDIDATE — blocked by anti-bot on headless playwright

## Vorden NDG baptism register (pre-1674) — unindexed pages for Lebbink family

- **URL:** https://permalink.geldersarchief.nl/ (per-record permalinks) and GA viewer `mivast=37&micode=0176_1605`
- **Discovered:** 2026-04-10, F-1354/F-1357 (RQ-014 session 4)
- **Why:** Gerrit Lebbink (active 1660-1672 Brummen/Vorden) had confirmed sons Juriaen Gerritsen (married 1672) and Derck Gerritzen op Kleyn Lebbink (married 1707). The pre-1674 pages of Vorden NDG baptism register (GA 0176/1605) likely contain the baptism of Geurt Lebbink (~1655-1670) and may name his mother. Currently only post-1674 baptisms appear indexed in OA (first indexed baptism: Willem Lebbink 1674). Pages from 1640-1673 are presumably on earlier folios of the same register — accessible via GA viewer but not via OA/WieWasWie API.
- **Record types:** DTB Dopen (baptism) — unindexed image scans only
- **Estimated size:** ~35-40 years of pre-1674 baptism pages in registry 1605
- **Access method:** GA web viewer with JavaScript (Playwright headed browser), or physical visit to Doetinchem
- **Priority:** HIGH — probably contains Geurt Lebbink's baptism
- **Status:** CANDIDATE — blocked by anti-bot on headless playwright

## Doesburg NDG doopregister gap 1676-1705 — GA archief 0176

- **URL:** https://www.geldersarchief.nl/bronnen/archieven?mivast=37&mizig=236&miadt=37&miaet=54&micode=0176_487.3&minr=24869710&miview=ldt
- **Discovered:** 2026-04-10, F-1360/F-1361 (Lebbink research session 3)
- **Why:** Complete inventory of Doesburg NDG (Nederduits Gereformeerd) DTB registers in GA archief 0176 was mapped by systematic minr scanning. All indexed registers confirmed:
  - **0176_487.1**: NDG Dopen, 1615–~1638 (minr ~24864000–24867000)
  - **0176_487.3**: NDG Dopen, 1651–~1676 (minr ~24867350–24869730)
  - **CRITICAL GAP: ~1676–1705 — no NDG doopregister exists in digital GA inventory**
  - **0176_487.5**: NDG Dopen, 01-02-1705–~1780 (minr 24869734–~24873300)
  - **0176_488**: NDG Dopen, 22-10-1783–18-12-1808 (minr ~24873400–24874600)
  - **0176_489.5**: NDG Trouwen (marriages), 1754–~1780 (minr ~24874700–24875600)
  - **0176_490**: NDG Trouwen, 1790+ (minr ~24875800+)
  - **0176_491**: NDG Begraven, 1804+ (minr ~24876400+)
  - **0176_493.1**: Rooms Katholiek (Catholic) Dopen+Huwelijken, 1683+ (minr ~24879000+)
  - **0176_494**: RC Dopen, 1802+ (minr ~24885000+)
  Any Doesburg NDG child baptized between ~1676 and early 1705 is NOT findable in digitized records. The hypothetical Gerrit Lebbink (~1695–1705) falls squarely in this gap. WW has 0 Lebbink/Lebbing NDG entries before 1706. The physical register covering 1676-1705 may be lost, or was never created (plague years, no pastor), or exists undigitized at GA Arnhem.
- **Record types:** DTB Dopen, DTB Trouwen, DTB Begraven — GA MAIS scan viewer
- **Access method:** GA MAIS viewer — use `mizig=236&miadt=37&miaet=54&micode=0176_[code]&minr=[minr]&miview=ldt`. Playwright MCP works (MCP uses headed browser profile); headless playwright-cli is blocked by anti-bot.
- **Priority:** HIGH — affects Geurt Lebbink (I0018 ancestor line)
- **Status:** RESEARCH NOTE — gap documented, physical GA visit or contact needed to check undigitized holdings

## Bossche Protocollen 1406-1500 — Den Bosch

- **URL:** https://www.bhic.nl (BHIC holdings, inv 1185-1269)
- **Discovered:** 2026-04-03, F-1201 (RQ-013 session 5)
- **Why:** Gap period between Stan Ketelaars' 1367-1406 transcriptions and the 1476+ indexed records. Would bridge the Keteler family documentation from 1406 to 1476.
- **Record types:** Schepenprotocollen, property transfers
- **Estimated size:** ~84 inventory numbers covering ~94 years
- **Access method:** Unknown — may be digitized scans at BHIC, transcriptions unknown
- **Priority:** MEDIUM
- **Status:** CANDIDATE

## GA ORA Richterambt Doesburg — Protocol van opdrachten 1600-1805

- **URL:** https://www.genealogiedomein.nl/digitaal-mainmenu-27/doesburg-digitale-genealogische-brongegevens/richterambt-doesburg-afbeeldingen-ora/richterambt-doesburg-afb-ora-inv-nrs-098-113
- **Discovered:** 2026-04-11, F-1371 (RQ-014 session 5)
- **Why:** The ORA Richterambt Doesburg inv.nrs. 098-113 covers "Protocol van opdrachten, vestenissen en andere voluntaire akten" 1600-1805. This is the only known remaining avenue for finding documentary evidence linking Gerrit Lebbing (I800011) to Geurt Lebbink as his father. Guardianship appointments (momberschap), inheritance records, and property transfers routinely name parent-child relationships. Geurt Lebbink was confirmed active in this richterambt 1707-1722. Scans are on Genealogiedomein Flickr albums but are NOT transcribed or indexed — reading requires vision AI on each scan page.
- **Record types:** Voluntaire akten (property transfers, guardianship, wills) — ORA Richterambt Doesburg
- **Estimated size:** 15+ inventory numbers × multiple years = potentially 1000+ pages of scans
- **Access method:** Genealogiedomein Flickr albums (genealogiedomein skill). Browse verwijsfiche per inv.nr, extract photo IDs, resolve + read with vision.
- **Priority:** HIGH — this is the primary remaining digital avenue for the Gerrit Lebbing brick wall
- **Status:** CANDIDATE — no index exists; requires systematic vision scan reading

## Doesburg Stad ORA — Boedels 1501-1810 (probate estates)

- **URL:** https://www.genealogiedomein.nl/digitaal-mainmenu-27/doesburg-digitale-genealogische-brongegevens/oud-rechterlijk-archief-stad-items-1/193-doesburg-stad-boedels-1501-1810
- **Discovered:** 2026-04-12, F-1405 (RQ-014 session 8)
- **Why:** Jan Lebbink estate 1781 (inv.nr. 1723) may be Gerrit Jan Lebbing (I900224, b.1732, son of I800011). Boedel records routinely list heirs — if this is Gerrit Jan, it would confirm siblings of I500210 Fredericus and the broader family structure. Index PDF available via genealogiedomein; actual records at Gelders Archief (GA 0145, Stad Doesburg ORA).
- **Record types:** Probate estates, orphan chamber records, testaments
- **Estimated size:** 1501-1810, many hundreds of cases
- **Access method:** Index PDF downloadable; actual records require GA physical access
- **Priority:** MEDIUM — confirms family structure but won't directly resolve Gerrit's parentage
- **Status:** CANDIDATE

## ECAL — Erfgoedcentrum Achterhoek en Liemers (Doetinchem)

- **URL:** https://ecal.nl/collecties/
- **Discovered:** 2026-04-14, F-1538 (RQ-014 session 21)
- **Why:** OpenArchieven returned a hit: ECAL toegang 3021, inv.41 — "Advocaat-fiscaal tegen Gerrit Lebbink, 1746, Doetinchem". This is a civil/fiscal prosecution of a Gerrit Lebbink in the Doetinchem area in 1746. This person may be a son of Geurt Lebbink born during the Doesburg NDG register gap (~1695-1705), and thus a sibling or cousin of I800011. ECAL covers Achterhoek archives not indexed in OpenArchieven.
- **Record types:** ORA civil cases, DTB, notarial records, bevolkingsregister for Achterhoek region (Doetinchem, Zelhem, Aalten, Winterswijk area)
- **Estimated size:** Large regional archive
- **Access method:** MAIS-based catalog + online scans; some indexed in OpenArchieven; some accessible via ECAL own viewer
- **Priority:** MEDIUM — the 1746 case could reveal Gerrit's parentage if court record states origin
- **Status:** CANDIDATE — specific target: toegang 3021, inv.41

## RHC Vecht en Venen — De Bilt, Maarssen, Woerden area (Utrecht province)

- **URL:** https://rhcvechtenvenen.nl/collecties/
- **Discovered:** 2026-04-17, F-1577 (RQ-017 session)
- **Why:** Bevolkingsregister scans for De Bilt are in this archive (archive code `vev` in OpenArchieven). Teunis Brouwer (I0065, tuinman, De Bilt) is in their 1900–1911 bevolkingsregister (vev:60E65318). OpenArchieven indexes these records but MAIS scan access is blocked via API. A Playwright-based skill would allow viewing the actual register pages to confirm beroep (occupation) fields. Also relevant for later de Knijf family research since Jan de Knijf (I0069) was born in Woerden 1818 and Gijsbert de Knijf (I0071) died in Linschoten 1849.
- **Record types:** Bevolkingsregister, DTB, BS Geboorte/Huwelijk/Overlijden, notarial records for De Bilt, Maarssen, Woerden, Linschoten, Vinkeveen
- **Estimated size:** Large regional archive covering Utrecht province west
- **Access method:** MAIS-based (same platform as many Dutch archives); partial indexing in OpenArchieven but scans need browser access
- **Priority:** MEDIUM — needed to confirm Teunis Brouwer's tuinman occupation from bevolkingsregister scan (would upgrade F-1177 from Tier C to Tier B)
- **Status:** CANDIDATE
