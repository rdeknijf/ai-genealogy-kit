#!/usr/bin/env bash
# model-comparison-test.sh — Compare Opus vs Sonnet vs Haiku research quality
#
# Cheap test: gives each model pre-fetched archive data and asks it to
# interpret the records, write findings, and assess confidence. No archive
# lookups needed — tests judgment, not HTTP skills.
#
# Total cost: ~15 turns across all 3 models (5 each).
#
# Usage:
#   ./scripts/model-comparison-test.sh                    # run all 3 models
#   ./scripts/model-comparison-test.sh --models "sonnet haiku"  # subset
#   ./scripts/model-comparison-test.sh --dry-run          # show plan only
#   ./scripts/model-comparison-test.sh --person I600027   # different person

set -euo pipefail
cd "$(dirname "$0")/.."

# --- Configuration ---
MODELS=("opus" "sonnet" "haiku")
MAX_TURNS=15           # very tight — interpret + write findings + summarize
SESSION_TIMEOUT=15m
TEST_DIR="private/research/model-test"
DB_PATH="private/genealogy.db"
GED_PATH="private/tree.ged"
DRY_RUN=false
TEST_PERSON_ID="I600026"   # Aalbert Loois, b.1821 Apeldoorn, d.1900

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --models)   read -ra MODELS <<< "$2"; shift 2 ;;
        --max-turns) MAX_TURNS="$2"; shift 2 ;;
        --person)   TEST_PERSON_ID="$2"; shift 2 ;;
        --timeout)  SESSION_TIMEOUT="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# --- Setup ---
timestamp=$(date '+%Y%m%d-%H%M%S')
run_dir="$TEST_DIR/$timestamp"
mkdir -p "$run_dir"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$run_dir/test.log"; }

# --- Pre-fetch archive data (done once, shared by all models) ---
log "=== Model Comparison Test ==="
log "Person: $TEST_PERSON_ID"
log "Models: ${MODELS[*]}"
log "Max turns: $MAX_TURNS"

# Get person context from DB
person_json=$(python3 scripts/research_db.py get-person "$TEST_PERSON_ID" 2>/dev/null)
person_name=$(echo "$person_json" | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])")
log "Test subject: $person_name"

# Search OpenArchieven
log "Pre-fetching archive records..."
search_results=$(python3 scripts/openarchieven_search.py "$person_name" --place Apeldoorn 2>/dev/null || echo "Search failed")
log "Search results fetched"

# Fetch details for each record found
detail_results=""
while IFS= read -r line; do
    ref=$(echo "$line" | grep -oP 'ref: \K\S+' || true)
    if [[ -n "$ref" ]]; then
        log "  Fetching detail: $ref"
        detail=$(python3 scripts/openarchieven_search.py --detail "$ref" 2>/dev/null || echo "Detail fetch failed for $ref")
        detail_results+="
### Record: $ref
$detail
"
    fi
done <<< "$search_results"

# Save pre-fetched data
cat > "$run_dir/prefetched-data.txt" << PREFETCH
## Person from database
$person_json

## Archive search results (OpenArchieven)
$search_results

## Record details
$detail_results
PREFETCH

prefetched_size=$(wc -c < "$run_dir/prefetched-data.txt")
log "Pre-fetched data: ${prefetched_size} bytes"

# Record starting DB state
start_findings=$(python3 scripts/research_db.py stats 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tables']['findings'])")
log "Starting findings count: $start_findings"

if $DRY_RUN; then
    log ""
    log "DRY RUN — pre-fetched data saved to $run_dir/prefetched-data.txt"
    log "Would run ${#MODELS[@]} models with $MAX_TURNS turns each."
    cat "$run_dir/prefetched-data.txt"
    exit 0
fi

# --- Snapshot DB ---
DB_BACKUP="$run_dir/genealogy.db.snapshot"
cp "$DB_PATH" "$DB_BACKUP"

# --- The test prompt (archive data baked in) ---
read -r -d '' TEST_PROMPT << PROMPT || true
You are running a model quality test. You receive pre-fetched archive data
and must interpret it, write findings to the database, and summarize.

## TURN BUDGET: $MAX_TURNS turns. Be efficient.

## Person from database

$person_json

## Archive search results (OpenArchieven)

$search_results

## Record details
$detail_results

## Your task

Analyze the archive records above for person $TEST_PERSON_ID ($person_name).
For EACH record detail:

1. Interpret what the record tells us (who, what event, when, where, parents)
2. Write a finding to the DB using:
   \`python scripts/research_db.py add-finding '<json>'\`
   Use \`python scripts/research_db.py next-id --type finding\` for the ID.
   Include: id, person_ids, tier, status, evidence (one-line summary), source (archive ref).
3. Note any discrepancies with the current DB data.

Do NOT search any archives — all data is provided above.
Do NOT edit the GEDCOM file.

## OUTPUT SUMMARY — MANDATORY

End with:

## Test Results — $TEST_PERSON_ID

### Records interpreted
For each record: what it is, key facts extracted, tier assigned, why that tier.

### Findings written
- **F-XXXX**: one-line description

### Discrepancies
Any conflicts between archive records and current DB data.

### Confidence assessment
How confident are you in each finding? Any ambiguities in the records?
PROMPT

# --- Run each model ---
for model in "${MODELS[@]}"; do
    log ""
    log "=========================================="
    log "  Running model: $model"
    log "=========================================="

    # Restore DB to snapshot
    cp "$DB_BACKUP" "$DB_PATH"

    logfile="$run_dir/${model}.md"
    start_time=$(date +%s)

    exit_code=0
    timeout "$SESSION_TIMEOUT" \
        env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
        claude -p "$TEST_PROMPT" \
        --model "$model" \
        --max-turns "$MAX_TURNS" \
        --output-format text \
        > "$logfile" 2>&1 \
        || exit_code=$?

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    if [[ $exit_code -eq 124 ]]; then
        log "$model: TIMED OUT after $SESSION_TIMEOUT"
    else
        log "$model: completed in ${duration}s (exit code: $exit_code)"
    fi

    # Count findings
    model_findings=$(python3 scripts/research_db.py stats 2>/dev/null | \
        python3 -c "import sys,json; print(json.load(sys.stdin)['tables']['findings'])" 2>/dev/null || echo "$start_findings")
    new_findings=$((model_findings - start_findings))
    log "$model: $new_findings new findings written"

    # Save stats
    cat > "$run_dir/${model}-stats.json" << EOF
{
    "model": "$model",
    "person": "$TEST_PERSON_ID",
    "duration_seconds": $duration,
    "exit_code": $exit_code,
    "new_findings": $new_findings,
    "max_turns": $MAX_TURNS,
    "log_bytes": $(wc -c < "$logfile")
}
EOF

    log "$model: log at $logfile ($(wc -c < "$logfile") bytes)"
    sleep 5
done

# --- Restore original DB ---
cp "$DB_BACKUP" "$DB_PATH"
log ""
log "DB restored to original state"

# --- Comparison summary ---
log ""
log "=== Comparison Summary ==="

summary_file="$run_dir/COMPARISON.md"
cat > "$summary_file" << HEADER
# Model Comparison Test

**Date:** $(date '+%Y-%m-%d %H:%M')
**Person:** $TEST_PERSON_ID ($person_name)
**Max turns:** $MAX_TURNS
**Pre-fetched data:** ${prefetched_size} bytes

## Results

| Model | Duration | Findings | Log size | Exit |
|-------|----------|----------|----------|------|
HEADER

for model in "${MODELS[@]}"; do
    if [[ -f "$run_dir/${model}-stats.json" ]]; then
        stats=$(cat "$run_dir/${model}-stats.json")
        dur=$(echo "$stats" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['duration_seconds']//60}m{d['duration_seconds']%60}s\")")
        findings=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['new_findings'])")
        logsize=$(echo "$stats" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['log_bytes']//1024}KB\")")
        ec=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['exit_code'])")
        echo "| $model | $dur | $findings | $logsize | $ec |" >> "$summary_file"
        log "  $model: ${dur}, ${findings} findings, ${logsize}"
    fi
done

cat >> "$summary_file" << 'CHECKLIST'

## Review Checklist

Compare the three model logs on:

- [ ] Were all records correctly interpreted?
- [ ] Parent names extracted correctly?
- [ ] Confidence tiers appropriate? (civil registry = Tier B)
- [ ] Source references accurate?
- [ ] Any hallucinated facts not in the data?
- [ ] Finding JSON well-formed?
- [ ] Discrepancies noted?
- [ ] Efficient turn usage?

## Logs

CHECKLIST

for model in "${MODELS[@]}"; do
    echo "- [\`${model}.md\`](${model}.md)" >> "$summary_file"
done
echo "" >> "$summary_file"

log ""
log "=== Test Complete ==="
log "Results: $run_dir/COMPARISON.md"
