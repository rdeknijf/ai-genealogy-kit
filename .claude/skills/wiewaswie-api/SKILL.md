---
description: |
  Search 252M+ Dutch civil registry records via `scripts/wiewaswie_search.py`.
  WieWasWie is the largest indexed collection of Dutch BS records. Auto-falls back
  to OpenArchieven if Cloudflare blocks the request. Use for birth, marriage, and
  death record lookups. No login required for search.
---

# WieWasWie — 252M+ Civil Records via Python Wrapper

Use `scripts/wiewaswie_search.py` for all searches. Do NOT construct curl commands.

## Commands

```bash
python scripts/wiewaswie_search.py "<surname>"
python scripts/wiewaswie_search.py "<surname>" --firstname Jan --prefix de --place Woerden
python scripts/wiewaswie_search.py "<surname>" --type "BS Geboorte" --year-from 1850 --year-to 1900
python scripts/wiewaswie_search.py --detail <SourceDocumentId>
```

## Document type filters

| Filter | Record type |
|--------|-------------|
| `BS Geboorte` | Birth certificate |
| `BS Huwelijk` | Marriage certificate |
| `BS Overlijden` | Death certificate |
| `DTB Dopen` | Baptism (church, pre-1811) |
| `DTB Trouwen` | Marriage (church) |
| `DTB Begraven` | Burial (church) |

## Fallback behavior

WieWasWie's API is sometimes blocked by Cloudflare. When this happens, the
wrapper automatically falls back to OpenArchieven (which has most of the same
records). The output will note "(OpenArchieven fallback)" when this occurs.

## Tips

- WieWasWie includes records from ALL Dutch provinces
- The `id:` in search results can be used with `--detail` for full record info
- Known gap: Apeldoorn BS Huwelijk indexing stops after Dec 1947;
  Apeldoorn BS Geboorte is NOT indexed in WieWasWie

## Supersedes

This replaces the old `wiewaswie` skill. The old skill's Playwright fallback
for detail pages is no longer needed — use `--detail` instead.
