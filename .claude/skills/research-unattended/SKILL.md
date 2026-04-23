---
name: research-unattended
description: |
  Start and babysit autonomous genealogy research sessions running in
  separate background processes. The runner script launches sequential
  `claude -p` sessions that each do 2-3 research cycles with fresh context,
  persisting state in GEDCOM + database (private/genealogy.db) between sessions. This skill
  manages the full lifecycle: starting the runner, monitoring it, restarting
  on crashes, graceful stopping, and consolidating results.
  Use when: "start research", "run research for a while", "autonomous research",
  "babysit research", "unattended research", "/research-unattended", or any
  request to run research unattended. Also use when the user says "keep
  researching" or "do research until I stop you".
---

# Research (Unattended)

Run autonomous genealogy research sessions with a babysitter pattern: a
background script does the research, and you (the Claude session) monitor
it, restart on crashes, and consolidate when done.

Unlike `/research` (which runs cycles in the current session), this skill
launches **separate background processes** that survive context limits
and can run for hours unattended.

## Architecture

```
[You: babysitter session] ---monitors---> [research-runner.sh] ---spawns---> [claude -p sessions]
                                               |                                    |
                                               |                                    v
                                               |                              GEDCOM + genealogy.db
                                               v
                                          runner.log
```

- `scripts/research-runner.sh` loops, launching fresh `claude -p` sessions
- Each session gets fresh context (~3-5K tokens per person via DB queries)
- State persists in `private/tree.ged` and `private/genealogy.db`
- The runner checks API usage between sessions and stops at the ceiling
- You monitor via a 15-minute cron, restarting if it crashes

## Phase 1: Start the runner

Before starting, commit the current state of the private repo as a safety
snapshot so the user can roll back if needed.

Then launch the runner in the background. The `env -u` flags are critical —
without them, `claude -p` refuses to start because it detects nesting.

```bash
: > private/research/logs/runner.log  # truncate in-place (preserves inode for tail -f)
nohup env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
    ./scripts/research-runner.sh \
    --sessions 20 \
    >> private/research/logs/runner.log 2>&1 &
echo "PID: $!"
```

If the user has a usage tracking cache (e.g. ccstatusline), add budget ceilings:

```bash
: > private/research/logs/runner.log  # truncate in-place (preserves inode for tail -f)
nohup env -u CLAUDE_CODE_SESSION -u CLAUDE_CODE_CONVERSATION_ID \
    ./scripts/research-runner.sh \
    --usage-cache ~/.cache/ccstatusline/usage.json \
    --session-ceiling 80 --weekly-ceiling 90 \
    >> private/research/logs/runner.log 2>&1 &
echo "PID: $!"
```

Also inhibit system sleep if not handled by the script:

```bash
systemd-inhibit --what=sleep:idle --who="research-runner" \
    --why="genealogy research" --mode=block sleep infinity &
```

Verify it started after a few seconds:

```bash
sleep 3 && tail -5 private/research/logs/runner.log
```

**Arguments the user might specify:**

- Number of sessions: `--sessions 5` (default, the primary safety limit)
- Session timeout: `--session-timeout 90m` (default, kills hung sessions)
- Max turns per session: `--max-turns 50` (default)
- Usage cache: `--usage-cache <path>` (optional, enables budget ceilings)
- Session ceiling: `--session-ceiling 80` (requires --usage-cache)
- Weekly ceiling: `--weekly-ceiling 90` (requires --usage-cache)

## Phase 2: Set up monitoring

Create a recurring cron (every 15 minutes) that checks on the runner.
Replace `PID` with the actual PID from Phase 1.

The cron prompt should run these checks:

1. `ps -p PID` — is it still running?
2. `tail -8 .../runner.log` — latest status
3. `cat private/research/logs/heartbeat.json` — live session state (turn count,
   cost, stuck detection). If `stuck: true`, the session is retrying the same
   tool call — consider killing it.
4. Usage cache — current session/weekly usage
5. `cat private/research/session_state.json` — structured state from last completed session
6. `git diff --stat` — are files being modified?

If the process died unexpectedly (no "Budget ceiling reached" message),
restart it with the same command from Phase 1.

If it finished normally (budget ceiling or all sessions done), proceed to
Phase 4 (consolidation).

**Example cron prompt:**

```
Check on the research runner (PID XXXX).
1. ps -p XXXX — still running?
2. tail -8 private/research/logs/runner.log
3. cat ~/.cache/ccstatusline/usage.json | jq '{sessionUsage, weeklyUsage}'
4. git diff --stat (in private repo)
If crashed, restart. If finished normally, consolidate and /ping.
```

## Phase 3: Graceful stop

When the user wants to stop after the current session finishes:

```bash
# Find the child claude -p process
CLAUDE_PID=$(pgrep -P RUNNER_PID -f claude | head -1)

# Background watcher: wait for session to finish, then kill runner
( while kill -0 $CLAUDE_PID 2>/dev/null; do sleep 5; done
  sleep 2
  kill RUNNER_PID 2>/dev/null
) &
```

This lets the current research session complete its work (including writing
to GEDCOM and database) before stopping the loop.

To stop immediately (not recommended — may leave partial edits):

```bash
kill RUNNER_PID
```

## Phase 4: Consolidation

After the runner stops:

1. **Check final stats:**
   ```bash
   python3 scripts/analyze_gedcom.py private/tree.ged | head -10
   ```

2. **Generate fan chart:**
   ```bash
   python3 scripts/fan_chart.py 7
   ```

3. **Prep commit** (show to user, don't commit without approval):
   ```
   feat(research): autonomous research — N sessions, +X people, +Y families
   ```

4. **Notify the user** via `/ping` if they asked for it.

## Known issues and gotchas

### CLAUDE_CODE_SESSION env var

`claude -p` detects it's inside another Claude session via environment
variables and refuses to run. The `env -u CLAUDE_CODE_SESSION -u
CLAUDE_CODE_CONVERSATION_ID` wrapper is mandatory.

### Usage cache staleness — CRITICAL

The `~/.cache/ccstatusline/usage.json` file is updated by the main Claude
Code session's statusline hook. `claude -p` subprocesses do **NOT** trigger
cache updates. During unattended research, the cache freezes when the
babysitter session is sleeping (between ScheduleWakeup intervals).

**Consequences if not addressed:**
- Runner reads stale session=100% after a 5h reset → bails immediately in
  an infinite loop ("Already over budget. Exiting.")
- Runner reads stale session=3% for hours → never hits session-ceiling

**Workaround:** Force-refresh the cache at the start of each babysitter
wake-up by piping minimal JSON to ccstatusline:

```bash
echo '{"workspace":{"current_dir":"/home/rdeknijf/projects/genealogy"},"model":{"id":"claude-opus-4-6","display_name":"Opus 4.6"}}' \
  | /home/rdeknijf/.npm-global/bin/ccstatusline > /dev/null
```

This makes the babysitter's ScheduleWakeup cadence (~50 min) the effective
cache-refresh cadence. The runner's `over_budget` check then reads
reasonably fresh data on its next between-session check.

### pipefail + grep

The script uses `set -euo pipefail`. Any `grep | wc -l` pipeline where
grep finds 0 matches will exit with code 1, killing the script. The fix
is `{ grep ... || true; } | wc -l`. This was a bug that was fixed in the
script, but be aware if modifying the script.

### Sessions self-committing

The `claude -p` sessions may commit their own changes to the private repo.
This is fine — it means work is saved incrementally. Check `git log` to
see what they committed.

### Session log buffering

`claude -p --output-format text` buffers all output until the session
completes. Session log files will be 0 bytes while a session is running.
This is normal — check the runner log and `git diff` instead.
