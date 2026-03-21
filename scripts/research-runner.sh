#!/usr/bin/env bash
# research-runner.sh — run autonomous research cycles
#
# Each iteration launches a fresh `claude -p` session that does 2-3
# research cycles, then exits. State persists in GEDCOM + FINDINGS.md.
# The next session picks up where the last left off.
#
# Designed to be started by a babysitter Claude session that monitors
# progress, restarts on crashes, and stops it when requested.
#
# Usage:
#   ./scripts/research-runner.sh                     # run 5 sessions (default)
#   ./scripts/research-runner.sh --sessions 20       # run exactly 20 sessions
#   ./scripts/research-runner.sh --usage-cache ~/.cache/ccstatusline/usage.json \
#       --session-ceiling 80 --weekly-ceiling 90     # stop on usage ceilings
#   ./scripts/research-runner.sh --dry-run           # show plan, don't execute

set -euo pipefail
cd "$(dirname "$0")/.."

# --- Configuration ---
USAGE_CACHE=""        # path to usage JSON (optional, e.g. ccstatusline)
LOG_DIR="private/research/logs"
SESSION_CEILING=80    # stop if 5h session usage exceeds this % (requires --usage-cache)
WEEKLY_CEILING=95     # stop if 7d weekly usage exceeds this % (requires --usage-cache)
MAX_SESSIONS=5        # default conservative; override with --sessions N
MAX_TURNS=50          # turns per claude session (~2-3 research cycles)
SESSION_TIMEOUT=90m   # wallclock timeout per session (kill if hung)
DRY_RUN=false
INHIBIT_PID=""

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sessions)   MAX_SESSIONS="$2"; shift 2 ;;
        --usage-cache) USAGE_CACHE="$2"; shift 2 ;;
        --session-ceiling) SESSION_CEILING="$2"; shift 2 ;;
        --weekly-ceiling)  WEEKLY_CEILING="$2"; shift 2 ;;
        --max-turns)  MAX_TURNS="$2"; shift 2 ;;
        --session-timeout) SESSION_TIMEOUT="$2"; shift 2 ;;
        --dry-run)    DRY_RUN=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# --- Helpers ---
mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

has_usage_tracking() {
    [[ -n "$USAGE_CACHE" && -f "$USAGE_CACHE" ]]
}

check_usage() {
    if ! has_usage_tracking; then
        echo "- -"
        return
    fi
    local session weekly
    session=$(jq -r '.sessionUsage // 0' "$USAGE_CACHE" 2>/dev/null || echo 0)
    weekly=$(jq -r '.weeklyUsage // 0' "$USAGE_CACHE" 2>/dev/null || echo 0)
    echo "$session $weekly"
}

over_budget() {
    if ! has_usage_tracking; then
        return 1  # no tracking = rely on --sessions limit
    fi
    read -r session weekly <<< "$(check_usage)"
    if (( $(echo "$session >= $SESSION_CEILING" | bc -l) )); then
        log "Session usage ${session}% >= ceiling ${SESSION_CEILING}%"
        return 0
    fi
    if (( $(echo "$weekly >= $WEEKLY_CEILING" | bc -l) )); then
        log "Weekly usage ${weekly}% >= ceiling ${WEEKLY_CEILING}%"
        return 0
    fi
    return 1
}

cleanup() {
    log "Cleaning up..."
    [[ -n "$INHIBIT_PID" ]] && kill "$INHIBIT_PID" 2>/dev/null || true
    log "Done. Logs in $LOG_DIR/"
}
trap cleanup EXIT

# --- Startup ---
log "=== Overnight Research ==="
log "Max sessions: $MAX_SESSIONS, Max turns: $MAX_TURNS, Timeout: $SESSION_TIMEOUT"
if has_usage_tracking; then
    log "Usage tracking: $USAGE_CACHE"
    log "Ceilings: session=${SESSION_CEILING}%, weekly=${WEEKLY_CEILING}%"
    read -r cur_session cur_weekly <<< "$(check_usage)"
    log "Current usage — session: ${cur_session}%, weekly: ${cur_weekly}%"
    if over_budget; then
        log "Already over budget. Exiting."
        exit 0
    fi
else
    log "No usage tracking — will run exactly $MAX_SESSIONS sessions"
fi

if $DRY_RUN; then
    log "DRY RUN — would start research loop. Exiting."
    exit 0
fi

# Inhibit sleep
if command -v systemd-inhibit &>/dev/null; then
    systemd-inhibit --what=sleep:idle --who="overnight-research" \
        --why="genealogy research loop" --mode=block sleep infinity &
    INHIBIT_PID=$!
    log "Sleep inhibited (PID $INHIBIT_PID)"
else
    log "WARNING: systemd-inhibit not available, machine may sleep"
fi

# --- The prompt sent to each session ---
read -r -d '' RESEARCH_PROMPT << 'PROMPT' || true
You are running autonomous overnight research session CYCLE_NUM.

## Your task

Read and follow the research-loop skill at `.claude/skills/research-loop.md`.
Run 2-3 full research cycles. Each cycle has 4 phases:

1. **Assess** — parse `private/tree.ged`, trace ancestors from the children:
   Freya (I501635) and Balder (I501886). This covers both sides: De Knijf/Peters
   (father) and Van der Kant/Brands (mother). Find gaps (missing dates, missing
   sources, missing parents). Prioritize gen 4-6 (great-grandparents and beyond
   from the kids' perspective). Skip people born after 1916 (privacy period).

2. **Lookup** — search archives using the skills in `.claude/skills/`
   (wiewaswie.md, openarchieven.md, gelders-archief.md, etc.). Use sub-agents
   for parallel lookups. Target birth, marriage, and death records.

3. **Apply** — edit `private/tree.ged` directly:
   - Add/correct dates and places from official records
   - Add source citations (SOUR records) with archive references
   - Add newly discovered parents as INDI+FAM records
   - CRITICAL: check highest existing INDI/FAM/SOUR IDs first to avoid
     collisions (see research-loop skill for the exact commands)
   - Only apply Tier A/B evidence (official archive records)

4. **Document** — append findings to `private/research/FINDINGS.md` with
   finding number, person ID, tier, status, evidence, and archive refs.

## Rules

- Read `private/research/FINDINGS.md` FIRST to see recent entries and avoid
  duplicate work. Previous overnight sessions already ran.
- Each cycle must target DIFFERENT persons than prior cycles in this session.
- Run the GEDCOM validation script after edits (see research-loop skill).
- End with a summary: findings documented, GEDCOM changes applied, what's next.
PROMPT

# --- Main loop ---
session_num=0
total_findings=0

while [[ $session_num -lt $MAX_SESSIONS ]]; do
    session_num=$((session_num + 1))

    # Check budget before each session
    if over_budget; then
        log "Budget ceiling reached after $((session_num - 1)) sessions."
        break
    fi

    read -r cur_session cur_weekly <<< "$(check_usage)"
    if has_usage_tracking; then
        log "--- Session $session_num/$MAX_SESSIONS (usage: session=${cur_session}%, weekly=${cur_weekly}%) ---"
    else
        log "--- Session $session_num/$MAX_SESSIONS ---"
    fi

    # Prepare log file
    logfile="$LOG_DIR/overnight-$(date '+%Y%m%d-%H%M%S')-session${session_num}.md"

    # Substitute cycle number into prompt
    prompt="${RESEARCH_PROMPT//CYCLE_NUM/$session_num}"

    # Launch claude -p with the research prompt
    # Unset session env vars to avoid "cannot nest inside another session" error
    # timeout kills hung sessions (e.g. stuck sub-agents or browser calls)
    timeout "$SESSION_TIMEOUT" \
        env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
        claude -p "$prompt" \
        --max-turns "$MAX_TURNS" \
        --output-format text \
        > "$logfile" 2>&1
    exit_code=$?
    if [[ $exit_code -eq 124 ]]; then
        log "Session $session_num TIMED OUT after $SESSION_TIMEOUT"
    fi

    log "Session $session_num complete. Log: $logfile"

    # Count new findings (rough: grep for F-NNN patterns in the log)
    new_findings=$({ grep -oP 'F-\d{1,4}' "$logfile" 2>/dev/null || true; } | wc -l)
    total_findings=$((total_findings + new_findings))
    log "Findings referenced this session: $new_findings (total: $total_findings)"

    # Brief cooldown to let usage cache update
    sleep 30
done

log "=== Overnight Research Complete ==="
log "Sessions run: $session_num"
log "Total findings referenced: $total_findings"
log "Logs: $LOG_DIR/overnight-*.md"
