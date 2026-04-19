---
description: |
  Search Regionaal Archief Nijmegen (RAN) — the Nijmegen city archive — for
  person records (BS, DTB ~1600+, bevolkingsregister, Vierdaagse). RAN is fully
  indexed on OpenArchieven under archive code `ran`, so this skill is a thin
  pointer to `openarchieven-api`. Nijmegen city records are NOT in Gelders
  Archief (`gld`) — they are a separate archive.
---

# Regionaal Archief Nijmegen (RAN)

Nijmegen's city archive holds DTB, BS, bevolkingsregister, and Vierdaagse
inschrijvingsregisters, with DTB Trouwen/Dopen going back to the early 1600s.
Despite being in Gelderland, Nijmegen is **not** in Gelders Archief — it has
its own archive and its own OpenArchieven code.

## Access — use `openarchieven-api`

Person records are fully indexed on OpenArchieven under archive code `ran`.
The existing `scripts/openarchieven_search.py` wrapper already supports it:

```bash
python scripts/openarchieven_search.py "Jeths" --archive ran --limit 10
python scripts/openarchieven_search.py "Knijf" --archive ran --limit 5
python scripts/openarchieven_search.py "Jansen" --archive ran --period 1850-1860
python scripts/openarchieven_search.py --detail ran:2D0DA44A-6797-4FAD-A253-69478E38144E
```

Detail lookups return full persons lists and scan URLs on persistent handles
(`https://hdl.handle.net/21.12122/...`).

## Coverage

| Record type | Notes |
|-------------|-------|
| **DTB Dopen / Trouwen / Begraven** | ~1600 onward — deeper than most Dutch city archives |
| **BS Geboorte / Huwelijk / Overlijden** | Standard post-1811 civil registry |
| **Bevolkingsregister** | Population registers |
| **Vierdaagse inschrijvingsregisters** | Nijmegen Four Days Marches participants |

Non-person collections (notarial acts, permits, image bank, newspapers,
address books) are browsable at `studiezaal.nijmegen.nl` but have no public API.
Fall back to Playwright only if those collections are ever needed.

## When to use this archive

- **Jeths research (RQ-001)** — the Nijmegen-Barneveld family. DTB Trouwen from
  the 1600s is where the Jeths marriages would be recorded.
- **Any ancestor who lived in Nijmegen** — including people who passed through
  for the Vierdaagse.
- **Anyone a cross-search on `gld` (Gelders Archief) failed to find** — they
  may be in `ran` instead.

## Gotchas

- `openarchieven-api` previously described `gld` as covering Nijmegen — this
  was incorrect and has been fixed. Nijmegen city records are exclusively in
  `ran`.
- `studiezaal.nijmegen.nl` is a Nijmegen-specific custom platform, not
  MAIS/Atlantis/Memorix — browser automation does not inherit from those
  existing skills.
