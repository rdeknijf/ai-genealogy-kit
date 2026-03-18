#!/usr/bin/env bash
# Export GEDCOM from Gramps Web to local file.
# Usage: GRAMPSWEB_USER=x GRAMPSWEB_PASSWORD=y ./scripts/export-grampsweb.sh [output.ged]
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Load credentials from .env if present
if [[ -f "$PROJECT_DIR/.env" ]]; then
  set -a; source "$PROJECT_DIR/.env"; set +a
fi

GRAMPSWEB_URL="${GRAMPSWEB_URL:?Set GRAMPSWEB_URL in .env (e.g. https://genealogy.example.com)}"
OUTPUT="${1:-$PROJECT_DIR/private/tree.ged}"

# Credentials
GRAMPSWEB_USER="${GRAMPSWEB_USER:-}"
GRAMPSWEB_PASSWORD="${GRAMPSWEB_PASSWORD:-}"
if [[ -z "$GRAMPSWEB_USER" ]]; then
  read -rp "Gramps Web username: " GRAMPSWEB_USER
fi
if [[ -z "$GRAMPSWEB_PASSWORD" ]]; then
  read -rsp "Gramps Web password: " GRAMPSWEB_PASSWORD
  echo
fi

# Authenticate
echo "Authenticating..."
TOKEN=$(curl -sf -X POST "$GRAMPSWEB_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'username':'$GRAMPSWEB_USER','password':'$GRAMPSWEB_PASSWORD'}))")" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Export GEDCOM
echo "Exporting GEDCOM from Gramps Web..."
curl -sf "$GRAMPSWEB_URL/api/exporters/ged/file" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$OUTPUT"

SIZE=$(stat -c%s "$OUTPUT" 2>/dev/null || stat -f%z "$OUTPUT" 2>/dev/null)
echo "Saved: $OUTPUT ($SIZE bytes)"
