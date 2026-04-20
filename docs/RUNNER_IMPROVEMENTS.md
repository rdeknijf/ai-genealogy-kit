# Research Runner — Process Improvement Anchor

Living backlog for `scripts/research-runner.sh` and the autonomous research
loop. Diagnosis lives here so we can pick up where we left off.

## Context: what we saw on 2026-04-19 overnight

- 17 sessions ran, 13 productive (18 findings), last 4 sessions hit
  `--max-turns 50` in 4-6 min each with **zero output** (each log was
  literally `Error: Reached max turns (50)` — 29 bytes).
- Root cause: turns burned on tool calls before the agent reached its
  mandatory summary step. With `--output-format text`, nothing before the
  final text message is captured, so failed sessions leave no trace.
- `task_runs` table exists but the runner doesn't populate it — so we
  can't answer "which task did that failed session pick?" retroactively.
- The live queue contained a broad `IN_PROGRESS` task (gap-filling a
  whole family line). Broad tasks act like tarpits: easy leads get
  harvested early, later sessions churn on dead ends without converging
  on any single record.

## Completed

- **Observability pass (2026-04-20).** Runner now uses
  `--output-format stream-json --verbose`, writes a raw `.jsonl` per
  session, and post-processes via `scripts/parse_session_log.py` to
  produce a human-readable `.md` plus a `task_runs` row. Failed sessions
  now surface which task was picked and the last few tool calls.

## Next (in proposed leverage order)

### 1. Task-shape rules

Broad `IN_PROGRESS` tasks should not be eligible for the runner. A task
is runnable only if its `goal` names a specific target: record ID,
folio, person pair, or narrow hypothesis. Enforce via
`research_db.py validate --strict`.

- Add a `scope` column to `research_tasks`: `narrow` (default) vs
  `parent`. Only `narrow` tasks are pulled by the runner.
- When a session concludes the remaining leads on a parent task, it
  must spawn named narrow children before BLOCK-ing.

### 2. Auto-retire IN_PROGRESS tasks with repeated failures

Once `task_runs` is populated, we can count consecutive failures per
task. Rule: 3 consecutive runs on the same task with 0 findings →
runner auto-BLOCKs it with note `"N failed attempts — needs human
scoping"`.

### 3. Force early summary stub

Change the runner prompt so the agent writes a summary stub at turn 1
(just `RQ-NNN` + empty findings list), then refines as it works. Even a
max-turns exit then leaves a breadcrumb — which task was picked and
why. Lower `--max-turns` to `30` for narrow tasks; 50 rewards thrashing.

### 4. Queue quality gate

`validate --strict` should refuse non-BLOCKED tasks that lack a named
target. Prevents reintroducing tarpits.

## How to pick this up

1. Read this file + the git log for `scripts/research-runner.sh` and
   `scripts/parse_session_log.py` to see the current shape.
2. Check `task_runs` for real failure-mode data:
   ```sql
   SELECT task_id, exit_reason, COUNT(*)
   FROM task_runs WHERE started_at > date('now','-14 days')
   GROUP BY task_id, exit_reason;
   ```
3. Pick the next item off the backlog above and iterate.
