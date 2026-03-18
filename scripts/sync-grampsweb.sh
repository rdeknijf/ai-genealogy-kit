#!/usr/bin/env bash
# Sync GEDCOM file to Gramps Web via REST API.
# Usage: ./scripts/sync-grampsweb.sh [gedcom-file]
#
# Requires GRAMPSWEB_USER and GRAMPSWEB_PASSWORD env vars (or prompts).
# Clears the database via SSH + SQLite before importing
# (the REST reset endpoint no longer exists in Gramps Web API 3.7+).
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Load credentials from .env if present
if [[ -f "$PROJECT_DIR/.env" ]]; then
  set -a; source "$PROJECT_DIR/.env"; set +a
fi

GRAMPSWEB_URL="${GRAMPSWEB_URL:?Set GRAMPSWEB_URL in .env (e.g. https://genealogy.example.com)}"
GRAMPSWEB_HOST="${GRAMPSWEB_HOST:?Set GRAMPSWEB_HOST in .env (SSH hostname of your Gramps Web server)}"
GRAMPSWEB_COMPOSE_DIR="${GRAMPSWEB_COMPOSE_DIR:?Set GRAMPSWEB_COMPOSE_DIR in .env (path to docker-compose.yml on server)}"
GRAMPSWEB_DB_ID="${GRAMPSWEB_DB_ID:?Set GRAMPSWEB_DB_ID in .env (Gramps Web database UUID)}"
GEDCOM="${1:-$(ls -t "$( cd "$(dirname "$0")/.." && pwd )"/*.ged 2>/dev/null | head -1)}"

if [[ -z "$GEDCOM" || ! -f "$GEDCOM" ]]; then
  echo "Error: No GEDCOM file found. Pass path as argument or place .ged file in project root." >&2
  exit 1
fi

echo "GEDCOM file: $GEDCOM"
echo "Target:      $GRAMPSWEB_URL"

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

# Step 1: Clear the database via SSH + Docker exec
echo "Clearing existing tree data on $GRAMPSWEB_HOST..."
ssh "$GRAMPSWEB_HOST" "cd $GRAMPSWEB_COMPOSE_DIR && docker compose exec -T grampsweb python3 -c \"
import sqlite3
db = sqlite3.connect('/root/.gramps/grampsdb/$GRAMPSWEB_DB_ID/sqlite.db')
cursor = db.cursor()
for table in ['person', 'family', 'source', 'citation', 'event', 'media', 'place', 'repository', 'note', 'tag', 'reference', 'name_group', 'gender_stats']:
    cursor.execute(f'DELETE FROM {table}')
db.commit()
db.close()
print('Database cleared.')
\""

# Step 2: Restart the stack so the app picks up the clean state
echo "Restarting Gramps Web..."
ssh "$GRAMPSWEB_HOST" "cd $GRAMPSWEB_COMPOSE_DIR && docker compose restart" > /dev/null 2>&1
sleep 5

# Step 3: Get JWT token
echo "Authenticating..."
TOKEN=$(curl -sf -X POST "$GRAMPSWEB_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'username':'$GRAMPSWEB_USER','password':'$GRAMPSWEB_PASSWORD'}))")" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

AUTH="Authorization: Bearer $TOKEN"

# Step 4: Import GEDCOM
echo "Importing $(basename "$GEDCOM")..."
RESPONSE=$(curl -sf -X POST "$GRAMPSWEB_URL/api/importers/ged/file" \
  -H "$AUTH" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@$GEDCOM")

TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['task']['id'])")
echo "Import task: $TASK_ID"

# Step 5: Wait for completion
echo -n "Waiting for import to complete..."
while true; do
  sleep 5
  STATUS=$(curl -sf "$GRAMPSWEB_URL/api/tasks/$TASK_ID" \
    -H "$AUTH" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  case "$STATUS" in
    SUCCESS)
      echo " done!"
      break
      ;;
    FAILURE)
      echo " FAILED!"
      exit 1
      ;;
    *)
      echo -n "."
      ;;
  esac
done

# Step 6: Verify
PEOPLE=$(curl -sf "$GRAMPSWEB_URL/api/metadata/" -H "$AUTH" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['object_counts']['people'])")
echo "Verified: $PEOPLE people in tree."
echo "Done! Visit $GRAMPSWEB_URL to browse the tree."
