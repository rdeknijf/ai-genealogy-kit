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
[You: babysitter session] ---monitors---> [docker compose: genealogy-runner] ---runs---> [research-runner.sh] ---spawns---> [claude -p sessions]
                                                      |                                         |
                                                      |                                         v
                                                      |                                   GEDCOM + genealogy.db
                                                      v
                                                 runner.log
```

- The Docker container (`services/genealogy-runner/`) provides a consistent
  environment with `bc`, `jq`, `sqlite3`, `claude`, and Playwright pre-installed
- `scripts/research-runner.sh` loops inside the container, launching fresh
  `claude -p` sessions
- Each session gets fresh context (~3-5K tokens per person via DB queries)
- State persists in `private/tree.ged` and `private/genealogy.db` (bind-mounted)
- The runner checks API usage between sessions and stops at the ceiling
- You monitor via a 15-minute cron, restarting if it crashes

**IMPORTANT:** Always run via Docker compose. Never run `research-runner.sh`
directly on the host — it lacks `bc`, `jq`, and other dependencies.

## Phase 1: Start the runner

Before starting, commit the current state of the private repo as a safety
snapshot so the user can roll back if needed.

Then launch the runner via Docker compose:

```bash
: > private/research/logs/runner.log  # truncate in-place (preserves inode for tail -f)
cd services/genealogy-runner
nohup docker compose run --rm genealogy-runner -c \
    "./scripts/research-runner.sh --sessions 20 --usage-tracking --weekly-ceiling proportional" \
    >> ../../private/research/logs/runner.log 2>&1 &
echo "PID: $!"
cd ../..
```

Verify it started after a few seconds:

```bash
sleep 8 && tail -10 private/research/logs/runner.log
```

**Arguments the user might specify:**

- Number of sessions: `--sessions 5` (default, the primary safety limit)
- Session timeout: `--session-timeout 120m` (default, kills hung sessions)
- Max turns per session: `--max-turns 75` (default)
- Usage tracking: `--usage-tracking` (queries Claude OAuth API directly)
- Session ceiling: `--session-ceiling 80` (requires --usage-tracking)
- Weekly ceiling: `--weekly-ceiling proportional` (auto-scales to elapsed
  fraction of billing week) or a fixed percentage like `90`

## Phase 2: Set up monitoring

Create a recurring cron (every 15 minutes) that checks on the runner.

The cron prompt should run these checks:

1. `docker ps --filter name=genealogy-runner --format '{{.Status}}'` — container running?
2. `tail -8 private/research/logs/runner.log` — latest status
3. `cat private/research/logs/heartbeat.json` — live session state (turn count,
   cost, stuck detection). If `stuck: true`, the session is retrying the same
   tool call — consider killing it.
4. `scripts/check_usage.sh` or equivalent — current session/weekly usage
5. `cd private && git diff --stat` — are files being modified?

If the container died unexpectedly (no "Budget ceiling reached" message),
restart it with the docker compose command from Phase 1.

If it finished normally (budget ceiling or all sessions done), proceed to
Phase 4 (consolidation).

**Example cron prompt:**

```
Check on the Docker research runner.
1. docker ps --filter name=genealogy-runner --format '{{.Status}}'
2. tail -8 private/research/logs/runner.log
3. cat private/research/logs/heartbeat.json
4. cd private && git diff --stat
If container died, restart via docker compose. If finished normally, consolidate and /ping.
```

## Phase 3: Graceful stop

When the user wants to stop after the current session finishes:

```bash
# Stop the container gracefully (sends SIGTERM, waits for current session)
docker stop genealogy-runner
```

To stop immediately (not recommended — may leave partial edits):

```bash
docker kill genealogy-runner
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

### Always use Docker compose

The host machine lacks `bc`, `jq`, and other tools the runner needs. The
Docker image (`services/genealogy-runner/`) has everything pre-installed.
**Never run `research-runner.sh` directly on the host.**

The `docker compose run` command is run from `services/genealogy-runner/`.
The compose file bind-mounts `~/projects/genealogy` as `/workspace` and
`~/.claude` for OAuth tokens.

### CLAUDE_CODE_SESSION env var

Inside the Docker container, `claude -p` doesn't inherit the babysitter's
session env vars (the container has a clean environment), so the `env -u`
wrapper in the script handles this transparently.

### Usage tracking

Use `--usage-tracking` (not `--usage-cache`). This queries the Claude OAuth
API directly via `scripts/check_usage.sh` — no external cache needed, no
staleness issues. Combine with `--weekly-ceiling proportional` to auto-scale
the ceiling to the elapsed fraction of the billing week.

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
