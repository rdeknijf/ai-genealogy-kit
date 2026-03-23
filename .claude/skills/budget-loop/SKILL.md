---
name: budget-loop
description: |
  Run research loop cycles until a specified usage budget is exhausted.
  The user sets a session budget (% of 5-hour block) and/or weekly budget
  (% of 7-day block), and the loop keeps running cycles until either
  ceiling is reached, then finishes the current cycle gracefully and stops.
  Triggers on: "/budget-loop", "churn for X%", "use X% of my session",
  "research until X% usage", "keep going for X% of my budget",
  "burn X% session Y% weekly", or any request to run research loops
  with a usage-based stopping condition.
---

# Budget Loop

Run autonomous research cycles (via the research-loop skill) until a
usage budget is exhausted. This skill adds budget-awareness on top of
the existing research loop — it doesn't change how research works, just
controls when to stop.

## Argument parsing

The user provides one or both budgets. Parse from the arguments:

- **Session budget**: percentage of the 5-hour rolling block to spend
  - Patterns: `40% session`, `session 40%`, `40s`, `s40`
- **Weekly budget**: percentage of the 7-day rolling block to spend
  - Patterns: `5% weekly`, `weekly 5%`, `5w`, `w5`

If both are given, stop on whichever ceiling is hit first.
If only one is given, only track that one.

Examples:

- `/budget-loop 40% session` — stop after using 40% more of the 5h block
- `/budget-loop 5% weekly` — stop after using 5% more of the 7d block
- `/budget-loop 40% session 5% weekly` — stop on whichever comes first

## Startup: prevent sleep and read usage

### Inhibit system sleep

The machine must stay awake for the entire duration. At startup, launch
a sleep inhibitor in the background:

```bash
systemd-inhibit --what=sleep:idle --who="Claude Code" --why="budget-loop research" --mode=block sleep infinity &
INHIBIT_PID=$!
```

This blocks both sleep and idle suspend. The process is killed when the
loop finishes (see Stopping section). If `systemd-inhibit` isn't available,
warn the user that the machine might sleep mid-research and ask if they
want to continue anyway.

### Read current usage and calculate ceilings

Read the usage cache file:

```bash
cat ~/.cache/ccstatusline/usage.json
```

This file is maintained by an external process (ccstatusline) and updated
roughly every 180 seconds. The format:

```json
{
  "sessionUsage": 15.0,
  "weeklyUsage": 38.0,
  "extraUsageEnabled": true,
  "extraUsageLimit": 5000,
  "extraUsageUsed": 391,
  ...
}
```

Values are percentages (0-100). Calculate ceilings:

- `sessionCeiling = current sessionUsage + requested session budget`
- `weeklyCeiling = current weeklyUsage + requested weekly budget`

Cap ceilings at 100 — going over 100% means you'll hit the rate limit
anyway, so treat it as "go until rate-limited."

Report the plan to the user before starting:

```
Budget loop starting:
  Session: 15.0% now, ceiling 55.0% (budget: 40%)
  Weekly:  38.0% now, ceiling 43.0% (budget: 5%)
  Stopping on whichever is hit first.
```

If the cache file doesn't exist or can't be read, tell the user and stop.
Don't guess at usage values.

## The loop

Each iteration:

1. **Check budget** — read `~/.cache/ccstatusline/usage.json` and compare
   against ceilings. If either tracked metric is at or above its ceiling,
   stop (don't start a new cycle).

2. **Report status** — briefly log where usage stands:
   ```
   Cycle N starting (session: 23.4% / 55.0%, weekly: 39.1% / 43.0%)
   ```

3. **Run one research cycle** — read and follow the instructions in
   `.claude/skills/research-loop.md`. Execute the full cycle (assess,
   lookup, apply, document). Don't cut it short even if usage might
   exceed the ceiling mid-cycle — the cache updates lag by ~3 minutes
   anyway, and partially applied research is worse than finishing cleanly.

4. **After the cycle completes**, loop back to step 1.

## Stopping

When a ceiling is reached (or both):

- Finish the current cycle completely (all 4 phases)
- Kill the sleep inhibitor:
  ```bash
  kill $INHIBIT_PID 2>/dev/null
  ```
- Report final usage vs starting usage
- Summarize what was accomplished across all cycles:
  - Total cycles completed
  - Findings documented
  - GEDCOM changes applied
  - Open leads for next time

```
Budget loop complete after 3 cycles:
  Session: 15.0% -> 52.3% (budget was 40%, ceiling 55.0%)
  Weekly:  38.0% -> 42.8% (budget was 5%, ceiling 43.0%)  <- hit
  [summary of findings and changes]
```

## Edge cases

- **Already over ceiling at start**: If current usage already exceeds
  what the ceiling would be, tell the user and don't start. Suggest
  waiting for the reset timer.
- **Cache file stale or missing**: If the file can't be read between
  cycles, log a warning but continue for one more cycle. If it fails
  twice in a row, stop and tell the user.
- **Usage jumps**: Other Claude sessions consume the same budget. If
  usage jumps unexpectedly between cycles (someone else is using it too),
  that's fine — just stop at the ceiling as normal.
