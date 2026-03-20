#!/bin/bash
# Playwright lock for concurrent Claude Code agents.
# Ensures only one agent uses the Playwright browser at a time.
# Uses mkdir for atomic lock acquisition + session_id tracking.
# PreToolUse: acquire lock (waits up to 25s), PostToolUse: release.
set -euo pipefail

INPUT=$(cat)
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')

STALE_SECONDS=300
LOCK_NAME="playwright-browser"
LOCK_DIR="/tmp/${LOCK_NAME}.lock"

allow() {
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
}

if [[ "$EVENT" == "PreToolUse" ]]; then
  TIMEOUT=25
  WAITED=0

  while (( WAITED < TIMEOUT )); do
    # Try atomic lock creation
    if mkdir "$LOCK_DIR" 2>/dev/null; then
      echo "$SESSION_ID" > "$LOCK_DIR/session"
      date +%s > "$LOCK_DIR/timestamp"
      allow
    fi

    # Lock exists — check if it's ours (re-entrant)
    LOCK_OWNER=$(cat "$LOCK_DIR/session" 2>/dev/null || echo "")
    if [[ "$LOCK_OWNER" == "$SESSION_ID" ]]; then
      date +%s > "$LOCK_DIR/timestamp"
      allow
    fi

    # Check for stale lock (owner crashed without cleanup)
    LOCK_TIME=$(cat "$LOCK_DIR/timestamp" 2>/dev/null || echo "0")
    NOW=$(date +%s)
    AGE=$(( NOW - LOCK_TIME ))
    if (( AGE > STALE_SECONDS )); then
      rm -rf "$LOCK_DIR"
      # Loop will retry mkdir on next iteration
      continue
    fi

    sleep 1
    WAITED=$((WAITED + 1))
  done

  # Timed out
  echo "${LOCK_NAME} locked by another agent (waited ${TIMEOUT}s). Retry later." >&2
  exit 2

elif [[ "$EVENT" == "PostToolUse" ]]; then
  LOCK_OWNER=$(cat "$LOCK_DIR/session" 2>/dev/null || echo "")
  if [[ "$LOCK_OWNER" == "$SESSION_ID" ]]; then
    rm -rf "$LOCK_DIR"
  fi
  exit 0
fi
