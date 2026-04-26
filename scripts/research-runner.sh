#!/usr/bin/env bash
# research-runner.sh — run autonomous research cycles
#
# Each iteration launches a fresh `claude -p` session that does 1
# research cycle, then exits. State persists in GEDCOM + database (private/genealogy.db).
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
MAX_TURNS=75          # turns per claude session (full research cycle + documentation)
SESSION_TIMEOUT=120m  # wallclock timeout per session (kill if hung)
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

- **Turns 1-8:** Assess (read queue, check recent findings, understand the task)
- **Turns 9-55:** Lookup + Document INLINE (archive searches, sub-agents —
  write each finding to DB IMMEDIATELY after discovery, not later)
- **Turns 56-68:** Apply GEDCOM (optional — only if you have documented findings
  that need GEDCOM edits. Skip entirely if running low on turns)
- **Turns 69-MAX_TURNS_VALUE:** Write your OUTPUT SUMMARY (see below)

### DOCUMENT INLINE — MOST IMPORTANT RULE

After EACH successful archive lookup, IMMEDIATELY call:
  `python scripts/research_db.py add-finding '<json>'`

Do NOT batch findings for a "Document phase" — that phase no longer exists.
If you get killed at any turn, all findings written so far are safe in the DB.
Findings are the precious output. GEDCOM edits are reproducible from findings.

If you are deep in research at turn ~55, STOP looking up new things and
start your summary. An incomplete summary is far better than no summary at
all. The next session will continue where you left off.

## Previous session context

PREV_SESSION_SUMMARY

## Your task

### Task selection

1. Run `python scripts/research_db.py get-tasks --limit 3` to see available tasks.
   This already excludes DONE and BLOCKED tasks.
2. For each IN_PROGRESS task, run `python scripts/research_db.py search "RQ-NNN"`
   to check what previous sessions already found. If recent findings say "all
   digital sources exhausted" or similar dead-ends, mark it BLOCKED:
   `python scripts/research_db.py update-task RQ-NNN --status BLOCKED --note "Digital sources exhausted, needs physical archive visit"`
   Then pick the next task.
3. Pick ONE task — the highest-priority QUEUED or IN_PROGRESS item with open leads.
4. Run `python scripts/research_db.py get-person <ID>` for each person in the task.

Read and follow the research skill at `.claude/skills/research/SKILL.md`.
Run 1 full research cycle with 3 phases:

1. **Assess** — use `research_db.py get-tasks` and `get-person` to understand the
   task context: people IDs, current data tier, research goals, and where to look.
   Understand what's known vs unknown.

2. **Lookup + Document** — search archives using the skills in `.claude/skills/`
   (wiewaswie.md, openarchieven.md, gelders-archief.md, etc.). Use sub-agents
   for parallel lookups. Follow the "Where to look" guidance in the queue item.
   Also use web search for specialized sources.
   **CRITICAL**: after each successful lookup, IMMEDIATELY write the finding to DB:
   `python scripts/research_db.py add-finding '<json>'`
   Do not accumulate findings — persist each one the moment you have it.
   Update the task status as you go.

3. **Apply** (optional, skip if low on turns) — edit `private/tree.ged` directly:
   - Add/correct dates and places from official records
   - Add source citations (SOUR records) with archive references
   - Add newly discovered parents as INDI+FAM records
   - CRITICAL: use `research_db.py next-id --type indi/fam/sour` to avoid
     ID collisions (see research skill for the exact commands)
   - Only apply Tier A/B evidence (official archive records)
   - For Tier C/D findings, document but do NOT edit the GEDCOM
   - If you run out of turns before Apply, that's fine — the next session
     will pick up documented findings and apply them

## Rules

- Use `research_db.py get-tasks` and `search` to understand what's been done.
  Do NOT read FINDINGS.md or RESEARCH_QUEUE.md directly (saves ~500K tokens).
- Pick ONE task — don't work on multiple items per session.
- **Negative search tracking — MANDATORY**: Before any archive lookup, check
  `research_db.py check-negatives <person_id>`. After any failed lookup,
  record it with `research_db.py add-negative`. This prevents wasting turns
  retrying known dead ends.
- **BLOCKED workflow:** If you conclude a task cannot progress without human
  action (physical archive visit, subscription needed, family question), mark
  it BLOCKED with a note explaining what's needed. Then pick the next task —
  do NOT keep working a dead end.
- **No synthesis findings:** Do NOT write findings that merely summarize or
  synthesize what's already known. Only write findings for NEW evidence,
  NEW records found, or NEW conclusions with specific archive references.
  If you found nothing new, say so in the output summary — not as a finding.
- Each cycle must make progress on the queue item (new lookups, new findings).
- Run the GEDCOM validation script after edits (see research skill).
- **Flag missing datasources:** if you identify a relevant archive or database
  that has no skill in `.claude/skills/`, add it to `research/DATASOURCE_CANDIDATES.md`
  using the template in that file. Also mention it in your session summary under
  "Missing datasources". Examples: a regional archive for a new region, a
  specialized collection (military, notarial, guild records), or an online
  database with indexed records that would speed up future research.

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

### Structured state (MANDATORY — the runner parses this)
<!-- STATE_JSON
{
    "current_task": "RQ-NNN",
    "persons_completed": ["Ixxxx"],
    "persons_blocked": {"Ixxxx": "reason"},
    "leads_to_pursue": [{"person": "Ixxxx", "source": "archive", "hint": "what to try"}],
    "findings_added": ["F-NNN"]
}
STATE_JSON -->
PROMPT

# --- Main loop ---
# Run idempotent schema migration (adds negative_searches, coverage columns, etc.)
log "Running schema migration..."
python3 scripts/migrate_v2.py 2>&1 | { grep -v "Already" || true; }

# Sync GEDCOM to DB before starting
log "Syncing GEDCOM to research database..."
python3 scripts/research_db.py sync-from-gedcom 2>&1 | tail -4

session_num=0
total_findings=0
STATE_FILE="private/research/session_state.json"
HEARTBEAT_FILE="$LOG_DIR/heartbeat.json"

# Validate state file: clear current_task if it points to a BLOCKED/DONE task
if [[ -f "$STATE_FILE" ]]; then
    PYTHONPATH=scripts python3 -c "
import sqlite3
from pathlib import Path
from session_state import load_state, save_state
state = load_state(Path('$STATE_FILE'))
task_id = state.get('current_task')
if task_id:
    db = sqlite3.connect('private/genealogy.db')
    row = db.execute('SELECT status FROM research_tasks WHERE id = ?', (task_id,)).fetchone()
    if not row or row[0] in ('BLOCKED', 'DONE', 'SUPERSEDED'):
        state.pop('current_task', None)
        state['session_count_on_task'] = 0
        save_state(Path('$STATE_FILE'), state)
        print(f'Cleared stale current_task {task_id} (status: {row[0] if row else \"not found\"})')
    db.close()
" 2>/dev/null || true
fi
prev_findings_count=$(python3 scripts/research_db.py stats 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tables']['findings'])" 2>/dev/null || echo 0)
log "Starting findings count: $prev_findings_count"
run_coverage=$(python3 scripts/research_db.py coverage-score --gedcom private/tree.ged --quiet 2>/dev/null || echo "?")
log "Starting coverage: ${run_coverage}%"

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

    # Prepare log file (raw stream-json + post-processed markdown)
    logfile="$LOG_DIR/unattended-$(date '+%Y%m%d-%H%M%S')-session${session_num}.md"
    jsonlfile="${logfile%.md}.jsonl"
    session_started_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

    # Substitute cycle number and max-turns into prompt
    prompt="${RESEARCH_PROMPT//CYCLE_NUM/$session_num}"
    prompt="${prompt//MAX_TURNS_VALUE/$MAX_TURNS}"

    # Read structured state file for session context (replaces prose summary)
    if [[ -f "$STATE_FILE" ]]; then
        state_context=$(PYTHONPATH=scripts python3 -c "
from session_state import load_state, format_for_prompt
from pathlib import Path
state = load_state(Path('$STATE_FILE'))
print(format_for_prompt(state))
" 2>/dev/null || echo "(No previous session state available.)")
    else
        state_context="(This is the first session — no previous context.)"
    fi
    prompt="${prompt//PREV_SESSION_SUMMARY/$state_context}"

    # Measure coverage before session
    coverage_before=$(python3 scripts/research_db.py coverage-score --gedcom private/tree.ged --quiet 2>/dev/null || echo "")

    # Pick the model for this session based on the next queued task's
    # requires_model (or any linked OPEN finding's requires_model).
    # Falls back to sonnet if no hint is set.
    session_model=$(python3 scripts/research_db.py next-model --quiet 2>/dev/null || echo sonnet)
    log "Session $session_num model: $session_model"

    # Launch claude -p piped through the live stream parser
    # The parser writes the .jsonl file, updates heartbeat.json every 60s,
    # and kills stuck sessions (>5 consecutive identical tool calls)
    exit_code=0
    timeout "$SESSION_TIMEOUT" bash -c '
        env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
        claude -p "$1" \
        --model "$2" \
        --max-turns "$3" \
        --output-format stream-json \
        --verbose \
        2>&1 \
        | python3 scripts/parse_session_stream.py \
            --output "$4" \
            --heartbeat-file "$5" \
            --heartbeat-interval 60 \
            --kill-on-stuck 5
    ' _ "$prompt" "$session_model" "$MAX_TURNS" "$jsonlfile" "$HEARTBEAT_FILE" \
        || exit_code=$?
    if [[ $exit_code -eq 124 ]]; then
        log "Session $session_num TIMED OUT after $SESSION_TIMEOUT"
    fi

    # Measure coverage after session (before parse, so we can pass to log_run)
    coverage_after=$(python3 scripts/research_db.py coverage-score --gedcom private/tree.ged --quiet 2>/dev/null || echo "")

    # Post-process stream-json into human-readable markdown and log task_runs row
    coverage_args=""
    [[ -n "$coverage_before" ]] && coverage_args="$coverage_args --coverage-before $coverage_before"
    [[ -n "$coverage_after" ]] && coverage_args="$coverage_args --coverage-after $coverage_after"
    if [[ -s "$jsonlfile" ]]; then
        python3 scripts/parse_session_log.py "$jsonlfile" \
            --log-run --started-at "$session_started_at" $coverage_args \
            > "$logfile" 2>/dev/null || echo "Error: parse failed" > "$logfile"
    else
        echo "Error: empty stream-json output (timeout=$exit_code)" > "$logfile"
    fi

    picked_task=$(grep -oP 'Task picked: `\KRQ-\d+' "$logfile" | head -1 || echo "?")
    exit_reason=$(grep -oP 'Exit: `\K[^`]+' "$logfile" | head -1 || echo "?")
    log "Session $session_num complete. Task: ${picked_task:-?}, Exit: ${exit_reason:-?}. Log: $logfile"

    # Count new findings from DB (authoritative) and session log (backup)
    current_findings=$(python3 scripts/research_db.py stats 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tables']['findings'])" 2>/dev/null || echo "$prev_findings_count")
    if [[ -z "$prev_findings_count" ]]; then
        new_findings=$({ grep -oP 'F-\d{1,4}' "$logfile" 2>/dev/null || true; } | sort -u | wc -l)
    else
        new_findings=$((current_findings - prev_findings_count))
        [[ $new_findings -lt 0 ]] && new_findings=0
    fi
    prev_findings_count="$current_findings"
    total_findings=$((total_findings + new_findings))
    log "New findings this session: $new_findings (DB total: $current_findings)"

    # Auto-block stalled tasks: if the last 2 runs on the same task each produced ≤1 finding,
    # mark the task BLOCKED. Counts actual DB findings created during each run's time window
    # (not F-NNN regex on summary text, which misses findings from timed-out sessions).
    if [[ "$picked_task" != "?" ]]; then
        stall_count=$(python3 -c "
import sqlite3
db = sqlite3.connect('private/genealogy.db')
db.execute('PRAGMA busy_timeout = 5000')
runs = db.execute(
    'SELECT id, started_at, ended_at FROM task_runs WHERE task_id = ? ORDER BY id DESC LIMIT 2',
    ('$picked_task',)
).fetchall()
if len(runs) >= 2:
    low = 0
    for run_id, started, ended in runs:
        if started:
            end = ended or '9999-12-31'
            # Normalize ISO 'T' separator to space for consistent comparison with findings.created_at
            s_norm = started.replace('T', ' ').rstrip('Z')
            e_norm = end.replace('T', ' ').rstrip('Z')
            count = db.execute(
                'SELECT COUNT(*) FROM findings WHERE created_at >= ? AND created_at <= ?',
                (s_norm, e_norm)
            ).fetchone()[0]
        else:
            count = 0
        if count <= 1:
            low += 1
    print(low)
else:
    print(0)
db.close()
" 2>/dev/null || echo 0)
        if [[ "$stall_count" -ge 2 ]]; then
            log "Auto-blocking $picked_task: 2 consecutive sessions with ≤1 finding"
            python3 scripts/research_db.py update-task "$picked_task" \
                --status BLOCKED \
                --note "Auto-blocked by runner: 2 consecutive low-yield sessions on $(date '+%Y-%m-%d')" \
                2>/dev/null || true
            # Clear current_task in state file so next session picks a new task
            if [[ -f "$STATE_FILE" ]]; then
                PYTHONPATH=scripts python3 -c "
from pathlib import Path
from session_state import load_state, save_state
s = load_state(Path('$STATE_FILE'))
s.pop('current_task', None)
s['session_count_on_task'] = 0
save_state(Path('$STATE_FILE'), s)
" 2>/dev/null || true
            fi
        fi
    fi

    # Log coverage delta
    if [[ -n "$coverage_before" && -n "$coverage_after" ]]; then
        log "Coverage: ${coverage_before}% → ${coverage_after}%"
    fi

    # Extract structured state from session output and merge into state file
    if [[ -f "$logfile" ]]; then
        PYTHONPATH=scripts python3 -c "
from pathlib import Path
from session_state import load_state, save_state, merge_state, extract_state_from_log

state_path = Path('$STATE_FILE')
existing = load_state(state_path)

# Extract STATE_JSON from session log
log_text = Path('$logfile').read_text()
session_update = extract_state_from_log(log_text)

if session_update:
    try:
        session_update['coverage_score'] = float('${coverage_after}')
    except (ValueError, TypeError):
        pass
    merged = merge_state(existing, session_update)
    save_state(state_path, merged)
elif '${picked_task}' != '?':
    update = {'current_task': '${picked_task}'}
    try:
        update['coverage_score'] = float('${coverage_after}')
    except (ValueError, TypeError):
        pass
    merged = merge_state(existing, update)
    save_state(state_path, merged)
" 2>/dev/null || true
    fi

    # Brief cooldown to let usage cache update
    sleep 30
done

# Sync DB back to markdown for human readability
log "Syncing DB to markdown..."
python3 scripts/research_db.py sync-to-markdown 2>&1 | head -2

final_findings=$(python3 scripts/research_db.py stats 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tables']['findings'])" 2>/dev/null || echo "?")
final_coverage=$(python3 scripts/research_db.py coverage-score --gedcom private/tree.ged --quiet 2>/dev/null || echo "?")
log "=== Unattended Research Complete ==="
log "Sessions run: $session_num"
log "New findings this run: $total_findings (DB total: $final_findings)"
log "Coverage: ${run_coverage}% → ${final_coverage}%"
log "Logs: $LOG_DIR/unattended-*.md"
