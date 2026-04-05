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

## Bossche Protocollen 1406-1500 — Den Bosch

- **URL:** https://www.bhic.nl (BHIC holdings, inv 1185-1269)
- **Discovered:** 2026-04-03, F-1201 (RQ-013 session 5)
- **Why:** Gap period between Stan Ketelaars' 1367-1406 transcriptions and the 1476+ indexed records. Would bridge the Keteler family documentation from 1406 to 1476.
- **Record types:** Schepenprotocollen, property transfers
- **Estimated size:** ~84 inventory numbers covering ~94 years
- **Access method:** Unknown — may be digitized scans at BHIC, transcriptions unknown
- **Priority:** MEDIUM
- **Status:** CANDIDATE
