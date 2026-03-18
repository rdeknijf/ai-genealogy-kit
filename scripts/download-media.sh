#!/usr/bin/env bash
# Download all media from MyHeritage CDN URLs and upload to Gramps Web.
# Usage: GRAMPSWEB_USER=x GRAMPSWEB_PASSWORD=y ./scripts/download-media.sh
set -euo pipefail

GRAMPSWEB_URL="${GRAMPSWEB_URL:?Set GRAMPSWEB_URL in .env}"

# Auth
TOKEN=$(curl -sf -X POST "$GRAMPSWEB_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${GRAMPSWEB_USER}\",\"password\":\"${GRAMPSWEB_PASSWORD}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Authenticated. Fetching media list..."

# Get all media objects (paginate)
PAGE=1
PAGESIZE=50
ALL_MEDIA=$(mktemp)

while true; do
  BATCH=$(curl -sf "$GRAMPSWEB_URL/api/media/?page=$PAGE&pagesize=$PAGESIZE" \
    -H "Authorization: Bearer $TOKEN")
  COUNT=$(echo "$BATCH" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
  echo "$BATCH" >> "$ALL_MEDIA"
  if [ "$COUNT" -lt "$PAGESIZE" ]; then break; fi
  PAGE=$((PAGE + 1))
done

# Extract handles and URLs for media with http URLs (not yet uploaded)
MEDIA_LIST=$(python3 -c "
import json, sys
all_items = []
for line in open('$ALL_MEDIA'):
    line = line.strip()
    if line:
        all_items.extend(json.loads(line))
for item in all_items:
    path = item.get('path', '')
    if path.startswith('http'):
        print(f\"{item['handle']}\t{path}\")
")

TOTAL=$(echo "$MEDIA_LIST" | grep -c '.' || true)
echo "Found $TOTAL media objects with remote URLs."

if [ "$TOTAL" -eq 0 ]; then
  echo "All media already uploaded!"
  rm -f "$ALL_MEDIA"
  exit 0
fi

TMPDIR=$(mktemp -d)
SUCCESS=0
FAIL=0

echo "$MEDIA_LIST" | while IFS=$'\t' read -r HANDLE URL; do
  FILENAME=$(basename "$URL")
  TMPFILE="$TMPDIR/$FILENAME"

  # Download
  if curl -sf "$URL" -o "$TMPFILE" 2>/dev/null; then
    SIZE=$(stat -c%s "$TMPFILE" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 0 ]; then
      # Upload to Gramps Web
      HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" \
        -X PUT "$GRAMPSWEB_URL/api/media/$HANDLE/file" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: image/jpeg" \
        --data-binary "@$TMPFILE")
      if [ "$HTTP_CODE" = "200" ]; then
        SUCCESS=$((SUCCESS + 1))
        echo "[$SUCCESS/$TOTAL] Uploaded: $FILENAME"
      else
        FAIL=$((FAIL + 1))
        echo "[$FAIL] Upload failed (HTTP $HTTP_CODE): $FILENAME"
      fi
    else
      FAIL=$((FAIL + 1))
      echo "SKIP (empty): $FILENAME"
    fi
    rm -f "$TMPFILE"
  else
    FAIL=$((FAIL + 1))
    echo "SKIP (download failed): $FILENAME"
  fi
done

rm -rf "$TMPDIR" "$ALL_MEDIA"
echo "Done. Uploaded: $SUCCESS, Failed: $FAIL"
