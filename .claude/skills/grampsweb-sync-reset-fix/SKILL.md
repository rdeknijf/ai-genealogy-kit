---
name: grampsweb-sync-reset-fix
description: |
  Fix for Gramps Web GEDCOM sync creating duplicate records. Use when:
  (1) sync-grampsweb.sh fails at "Deleting existing tree data" with 404,
  (2) Gramps Web shows 2x or 3x the expected number of people after import,
  (3) /api/trees/-/reset/ returns 404 on Gramps Web API 3.7+,
  (4) imported person doesn't show in tree view but appears in relations.
  The REST reset endpoint was removed in Gramps Web API 3.7+. The fix is to
  clear the SQLite database directly via SSH + Docker exec before importing.
author: Claude Code
version: 1.0.0
date: 2026-03-14
---

# Gramps Web Sync Reset Fix

## Problem

The `sync-grampsweb.sh` script used `/api/trees/-/reset/` to clear the tree
before importing a GEDCOM. This endpoint was removed in Gramps Web API 3.7+,
causing the script to fail. Importing without resetting creates duplicate
records (every person, family, event appears 2x, 3x, etc.).

## Context / Trigger Conditions

- `sync-grampsweb.sh` fails with exit code 22 at the "Deleting existing tree data" step
- Gramps Web API returns 404 for `POST /api/trees/-/reset/`
- After a raw import, `GET /api/metadata/` shows `object_counts.people` at 2x or 3x the expected count
- A newly added person shows in relation/search views but not in the main tree view (because the tree view renders the old duplicate)

## Solution

Clear the database directly via SSH + Docker exec on buckland:

```bash
ssh buckland "cd /home/rdeknijf/services/grampsweb && \
  docker compose exec -T grampsweb python3 -c \"
import sqlite3
db = sqlite3.connect('/root/.gramps/grampsdb/09674c1b-3c9c-4fd3-b742-248cd5de3448/sqlite.db')
cursor = db.cursor()
for table in ['person', 'family', 'source', 'citation', 'event', 'media', 'place', 'repository', 'note', 'tag', 'reference', 'name_group', 'gender_stats']:
    cursor.execute(f'DELETE FROM {table}')
db.commit()
db.close()
\""
```

Then restart the stack so the app picks up the clean state:

```bash
ssh buckland "cd /home/rdeknijf/services/grampsweb && docker compose restart"
```

Wait ~5 seconds, then import via the API as normal:

```bash
curl -X POST "$GRAMPSWEB_URL/api/importers/ged/file" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@private/tree.ged"
```

The import returns a task ID — poll `/api/tasks/$TASK_ID` until `state` is `SUCCESS`.

## Verification

After import completes, check the metadata endpoint:

```bash
curl -sf "$GRAMPSWEB_URL/api/metadata/" -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'People: {d[\"object_counts\"][\"people\"]}')"
```

The count should match the number of INDI records in the GEDCOM (currently ~1784).

## Notes

- The sync script (`scripts/sync-grampsweb.sh`) was updated on 2026-03-14 to use this approach
- The database ID `09674c1b-3c9c-4fd3-b742-248cd5de3448` is the tree "De Knijf" on buckland
- Importing without clearing first is additive — it creates new copies of every record
- The container restart is necessary; clearing SQLite while the app is running can cause stuck import tasks
- The `DELETE /api/trees/-/` endpoint returns 405 (Method Not Allowed) — also not an option
- See also: [grampsweb-media-path-fix](../grampsweb-media-path-fix/SKILL.md) for media/images disappearing after sync
