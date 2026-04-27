#!/usr/bin/env bash
# check_usage.sh — query Claude usage via OAuth API
#
# Reads the OAuth token from ~/.claude/.credentials.json and calls the
# Anthropic usage endpoint. Writes JSON to a cache file and optionally
# prints human-readable output.
#
# Usage:
#   ./scripts/check_usage.sh                  # print usage summary
#   ./scripts/check_usage.sh --json           # print raw JSON
#   ./scripts/check_usage.sh --cache-file F   # write cache to F (for runner)
#   ./scripts/check_usage.sh --quiet          # only update cache, no output
set -euo pipefail

CREDENTIALS="${CLAUDE_CREDENTIALS:-$HOME/.claude/.credentials.json}"
CACHE_FILE=""
JSON_MODE=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)       JSON_MODE=true; shift ;;
        --cache-file) CACHE_FILE="$2"; shift 2 ;;
        --quiet)      QUIET=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [[ ! -f "$CREDENTIALS" ]]; then
    echo "Error: credentials not found at $CREDENTIALS" >&2
    exit 1
fi

TOKEN=$(jq -r '.claudeAiOauth.accessToken // empty' "$CREDENTIALS")
if [[ -z "$TOKEN" ]]; then
    echo "Error: no OAuth access token in $CREDENTIALS" >&2
    exit 1
fi

RESPONSE=$(curl -sf --max-time 10 \
    -H "Authorization: Bearer $TOKEN" \
    -H "anthropic-beta: oauth-2025-04-20" \
    "https://api.anthropic.com/api/oauth/usage" 2>/dev/null) || {
    echo "Error: usage API request failed" >&2
    exit 1
}

# Write cache file (compatible with runner's check_usage function)
CACHE_JSON=$(echo "$RESPONSE" | jq -c '{
    sessionUsage: (.five_hour.utilization // null),
    sessionResetAt: (.five_hour.resets_at // null),
    weeklyUsage: (.seven_day.utilization // null),
    weeklyResetAt: (.seven_day.resets_at // null),
    extraUsageEnabled: (.extra_usage.is_enabled // null),
    extraUsageLimit: (.extra_usage.monthly_limit // null),
    extraUsageUsed: (.extra_usage.used_credits // null),
    extraUsageUtilization: (.extra_usage.utilization // null)
}')

if [[ -n "$CACHE_FILE" ]]; then
    mkdir -p "$(dirname "$CACHE_FILE")"
    echo "$CACHE_JSON" > "$CACHE_FILE"
fi

if $QUIET; then
    exit 0
fi

if $JSON_MODE; then
    echo "$RESPONSE" | jq .
    exit 0
fi

# Human-readable summary
SESSION=$(echo "$RESPONSE" | jq -r '.five_hour.utilization // "?"')
SESSION_RESET=$(echo "$RESPONSE" | jq -r '.five_hour.resets_at // "?"' | cut -dT -f2 | cut -d. -f1)
WEEKLY=$(echo "$RESPONSE" | jq -r '.seven_day.utilization // "?"')
WEEKLY_RESET=$(echo "$RESPONSE" | jq -r '.seven_day.resets_at // "?"' | cut -dT -f2 | cut -d. -f1)
EXTRA_USED=$(echo "$RESPONSE" | jq -r '.extra_usage.used_credits // "?"')
EXTRA_LIMIT=$(echo "$RESPONSE" | jq -r '.extra_usage.monthly_limit // "?"')
EXTRA_CURRENCY=$(echo "$RESPONSE" | jq -r '.extra_usage.currency // "USD"')

echo "Session (5h): ${SESSION}%  (resets ${SESSION_RESET} UTC)"
echo "Weekly  (7d): ${WEEKLY}%  (resets ${WEEKLY_RESET} UTC)"
echo "Extra usage:  ${EXTRA_CURRENCY} ${EXTRA_USED}/${EXTRA_LIMIT}"
