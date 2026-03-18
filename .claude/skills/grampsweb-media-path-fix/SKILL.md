---
name: grampsweb-media-path-fix
description: |
  Fix for Gramps Web images/photos not displaying after GEDCOM sync. Use when:
  (1) all photos/images are missing in Gramps Web after a sync,
  (2) media API returns 404 for /api/media/<handle>/file but files exist on disk,
  (3) GEDCOM has absolute media paths like /root/gramps/xxx.jpg that don't match
  the container's media volume mount,
  (4) images were uploaded via download-media.sh but disappeared after re-import.
  Root cause: GEDCOM stores absolute container paths that don't match the media
  volume mount point. Fix: use relative paths + GRAMPSWEB_MEDIA_BASE_DIR.
author: Claude Code
version: 1.0.0
date: 2026-03-14
---

# Gramps Web Media Path Fix

## Problem

After syncing a GEDCOM to Gramps Web (which clears the DB and reimports), all
photos/images disappear. The media files are physically present on disk in the
`data/media/` volume, but Gramps Web can't serve them because the GEDCOM
contains absolute paths that don't match the container's volume mount.

## Context / Trigger Conditions

- All images are gone in Gramps Web after running `sync-grampsweb.sh`
- `GET /api/media/<handle>/file` returns 404
- Media files exist at `./data/media/*.jpg` on the host (mapped to `/app/media/` in container)
- GEDCOM contains `1 FILE /root/gramps/xxx.jpg` (absolute paths inside container)
- The path `/root/gramps/` inside the container does NOT contain image files — it only has `gramps60/` plugin data
- The images were originally from MyHeritage CDN URLs, downloaded and uploaded via `download-media.sh`

## Root Cause

Path mismatch between three things:

1. **GEDCOM paths**: `/root/gramps/xxx.jpg` (from Gramps Web export)
2. **Docker volume mount**: `./data/media:/app/media` (where files actually live)
3. **Gramps Web lookup**: uses the path from the DB verbatim — `/root/gramps/xxx.jpg` doesn't exist

When `download-media.sh` uploads via `PUT /api/media/<handle>/file`, Gramps Web
stores the file in `/app/media/`. When the GEDCOM is later exported, Gramps Web
writes the internal Gramps path (`/root/gramps/xxx.jpg`), not the filesystem path.
After a DB clear + reimport, the path in the new DB points to the wrong location.

## Solution

### Step 1: Fix GEDCOM paths (make them relative)

```bash
sed -i 's|1 FILE /root/gramps/|1 FILE |' tree.ged
```

This changes `1 FILE /root/gramps/xxx.jpg` → `1 FILE xxx.jpg`.

### Step 2: Add GRAMPSWEB_MEDIA_BASE_DIR to docker-compose.yml

On buckland, add to the grampsweb service environment:

```yaml
GRAMPSWEB_MEDIA_BASE_DIR: "/app/media"
```

This tells Gramps Web to resolve relative media paths against `/app/media/`.

### Step 3: Re-sync the GEDCOM

```bash
scripts/sync-grampsweb.sh tree.ged
```

## Verification

Test that media files are served:

```bash
# Get a media handle
curl -sf "$URL/api/media/?pagesize=1" -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['handle'])"

# Fetch the file — should return 200
curl -sf -o /dev/null -w "%{http_code}" "$URL/api/media/$HANDLE/file" \
  -H "Authorization: Bearer $TOKEN"
```

## Why This Persists Across Syncs

- The sync script (`sync-grampsweb.sh`) only clears DB tables, not filesystem files
- The media files in `./data/media/` survive the sync
- The GEDCOM (now with relative paths) reimports correctly
- `GRAMPSWEB_MEDIA_BASE_DIR` is set in docker-compose.yml (persists across restarts)

## Notes

- The `.env` file must use single quotes around values containing `$` characters,
  otherwise `source .env` will interpret them as shell variables
- There are 196 media files and 218 media objects (some share the same file)
- Media was originally from MyHeritage CDN URLs — those URLs may expire over time
- See also: [grampsweb-sync-reset-fix](../grampsweb-sync-reset-fix/SKILL.md) for
  the related DB reset issue during sync
