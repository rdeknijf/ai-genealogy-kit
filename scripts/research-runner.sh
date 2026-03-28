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
MAX_TURNS=75          # turns per claude session (~2-3 research cycles + summary)
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
log "=== Unattended Research ==="
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
    systemd-inhibit --what=sleep --who="genealogy-research" \
        --why="genealogy research loop" --mode=block sleep infinity &
    INHIBIT_PID=$!
    log "Sleep inhibited (PID $INHIBIT_PID)"
else
    log "WARNING: systemd-inhibit not available, machine may sleep"
fi

# --- The prompt sent to each session ---
read -r -d '' RESEARCH_PROMPT << 'PROMPT' || true
You are running autonomous research session CYCLE_NUM.

## TURN BUDGET — CRITICAL

You have a HARD LIMIT of MAX_TURNS_VALUE tool-call turns. You CANNOT see
the counter, so you must manage your own budget:

- **Turns 1-10:** Assess (read queue, read GEDCOM, understand the task)
- **Turns 11-50:** Lookup + Apply (archive searches, sub-agents, GEDCOM edits)
- **Turns 51-60:** Document (write findings to FINDINGS.md, update queue status)
- **Turns 61-MAX_TURNS_VALUE:** Write your OUTPUT SUMMARY (see below)

If you are deep in research at turn ~50, STOP looking up new things and
start documenting + summarizing. An incomplete summary is far better than
no summary at all. The next session will continue where you left off.

## Your task

Pick ONE highest-priority QUEUED item from `private/research/RESEARCH_QUEUE.md`
and investigate it. Do NOT work on multiple queue items in a single session.

Read and follow the research skill at `.claude/skills/research/SKILL.md`.
Run 1-2 full research cycles. Each cycle has 4 phases:

1. **Assess** — read the RESEARCH_QUEUE item for context: people IDs, current data
   tier, research goals, and where to look. Parse `private/tree.ged` to get the
   current GEDCOM data for those persons. Understand what's known vs unknown.

2. **Lookup** — search archives using the skills in `.claude/skills/`
   (wiewaswie.md, openarchieven.md, gelders-archief.md, etc.). Use sub-agents
   for parallel lookups. Follow the "Where to look" guidance in the queue item.
   Also use web search for specialized sources.

3. **Apply** — edit `private/tree.ged` directly:
   - Add/correct dates and places from official records
   - Add source citations (SOUR records) with archive references
   - Add newly discovered parents as INDI+FAM records
   - CRITICAL: check highest existing INDI/FAM/SOUR IDs first to avoid
     collisions (see research skill for the exact commands)
   - Only apply Tier A/B evidence (official archive records)
   - For Tier C/D findings, document but do NOT edit the GEDCOM

4. **Document** — append findings to `private/research/FINDINGS.md` with
   finding number, person ID, tier, status, evidence, and archive refs.
   Update the queue item's status in RESEARCH_QUEUE.md (QUEUED → IN_PROGRESS → DONE).

## Rules

- Read `private/research/FINDINGS.md` AND `private/research/RESEARCH_QUEUE.md`
  FIRST to see what's been done and avoid duplicate work.
- Pick ONE QUEUED item — don't work on multiple items per session.
- Continue an IN_PROGRESS item if it has open leads.
- Each cycle must make progress on the queue item (new lookups, new findings).
- Run the GEDCOM validation script after edits (see research skill).
- **Flag missing datasources:** if you identify a relevant archive or database
  that has no skill in `.claude/skills/`, note it in your findings. Examples:
  a military database for a soldier ancestor, a regional archive for a new
  region, or a specialized collection (KNIL, notarial, guild records). Include
  the datasource name, URL if known, and why it would help.

## OUTPUT SUMMARY — MANDATORY

Your text output MUST end with a structured summary. This is the ONLY thing
the runner script sees. Write it BEFORE any remaining GEDCOM edits if you
are running low on turns. Format:

## Session Summary — [RQ-NNN]: [title]

### Queue item worked on
**[RQ-NNN]** (Priority N, status)

### Findings documented (N new)
- **F-NNN**: one-line description
- ...

### GEDCOM changes applied
- +N INDI, +N FAM, +N SOUR (or "no edits")
- Validation: [clean / issues]

### Status
**[DONE / IN_PROGRESS / BLOCKED]** — [what remains]

### Missing datasources
[any flagged, or "none"]
PROMPT

# --- Main loop ---
session_num=0
total_findings=0
prev_findings_count=$({ grep -cP '^## F-\d+' private/research/FINDINGS.md 2>/dev/null || true; })
log "Starting findings count: $prev_findings_count"

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
    logfile="$LOG_DIR/unattended-$(date '+%Y%m%d-%H%M%S')-session${session_num}.md"

    # Substitute cycle number and max-turns into prompt
    prompt="${RESEARCH_PROMPT//CYCLE_NUM/$session_num}"
    prompt="${prompt//MAX_TURNS_VALUE/$MAX_TURNS}"

    # Launch claude -p with the research prompt
    # Unset session env vars to avoid "cannot nest inside another session" error
    # timeout kills hung sessions (e.g. stuck sub-agents or browser calls)
    exit_code=0
    timeout "$SESSION_TIMEOUT" \
        env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
        claude -p "$prompt" \
        --max-turns "$MAX_TURNS" \
        --output-format text \
        > "$logfile" 2>&1 \
        || exit_code=$?
    if [[ $exit_code -eq 124 ]]; then
        log "Session $session_num TIMED OUT after $SESSION_TIMEOUT"
    fi

    log "Session $session_num complete. Log: $logfile"

    # Count new findings from FINDINGS.md (authoritative) and session log (backup)
    current_findings=$({ grep -cP '^## F-\d+' private/research/FINDINGS.md 2>/dev/null || true; })
    if [[ -z "$prev_findings_count" ]]; then
        # First session — can't diff, fall back to log grep
        new_findings=$({ grep -oP 'F-\d{1,4}' "$logfile" 2>/dev/null || true; } | sort -u | wc -l)
    else
        new_findings=$((current_findings - prev_findings_count))
        [[ $new_findings -lt 0 ]] && new_findings=0
    fi
    prev_findings_count="$current_findings"
    total_findings=$((total_findings + new_findings))
    log "New findings this session: $new_findings (total in FINDINGS.md: $current_findings)"

    # Brief cooldown to let usage cache update
    sleep 30
done

final_findings=$({ grep -cP '^## F-\d+' private/research/FINDINGS.md 2>/dev/null || true; })
log "=== Unattended Research Complete ==="
log "Sessions run: $session_num"
log "New findings this run: $total_findings (FINDINGS.md total: $final_findings)"
log "Logs: $LOG_DIR/unattended-*.md"
