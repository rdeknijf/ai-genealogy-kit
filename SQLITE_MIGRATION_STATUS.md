# SQLite Migration Status

Last updated: 2026-04-05

## Current State

Migration complete. End-to-end tested with a real research task (Janna Poppink
baptism verification, F-1293). All DB operations confirmed working: get-tasks,
get-person, search, add-finding, update-task, next-id, log-run, stats. DB has
1285 findings, 2523 persons, 852 families, 1108 sources. SQLite file tracked
via Git LFS in private repo.

## Completed (2026-04-05)

### Safety commits

- Public repo: `18569c6` — all pending changes (6 new skills, docs, mise.toml, etc.)
- Private repo: `a804aea` — research run 2026-04-04 results + session logs + genealogy.db

### Scripts created (6)

1. `scripts/schema.sql` — 10 tables, FTS5 with auto-sync triggers, 7 indexes
2. `scripts/init_db.py` — creates DB from schema.sql, `--reset` flag, prints counts
3. `scripts/migrate_research.py` — parses FINDINGS.md (1284 unique from 1303 with 15 dupes)
   and RESEARCH_QUEUE.md (17 tasks). M:N person links via `finding_persons` (1672 links).
   Handles duplicate finding IDs (last entry wins).
4. `scripts/migrate_gedcom.py` — imports from `analyze_gedcom.py` functions (not duplicated).
   2523 persons, 852 families, 1583 child links, 1108 sources.
5. `scripts/build_research_state.py` — per-person summaries for 2526 persons (608 with findings).
   Tier distribution: A=13, B=551, C=27, D=9. `--person` flag for incremental rebuild.
6. `scripts/research_db.py` — 12 subcommands (all smoke-tested):
   get-tasks, get-person, get-research-state, search, add-finding, update-task,
   next-id, log-run, stats, sync-from-gedcom, sync-to-markdown, rebuild-research-state

### Files updated (9)

7. `CLAUDE.md` — expanded DB tooling table (12 commands), updated locking
   (FINDINGS.md lock removed, DB uses WAL), autonomous rules use DB commands
8. `.claude/hooks/file-lock.sh` — removed `*FINDINGS.md)` case
9. `scripts/fan_chart.py` — added `tiers_from_db()`, `--db`/`--no-db` flags.
   DB gives more granular tiers (A:3, B:113, C:2 vs B:118 from FINDINGS.md alone)
10. `scripts/research-runner.sh` — prompt uses `research_db.py` commands instead of
    reading markdown. Counts via `stats`. Added `sync-from-gedcom` before loop,
    `sync-to-markdown` after loop.
11. `.claude/skills/research/SKILL.md` — Phase 1: DB queries. Phase 3: `next-id`.
    Phase 4: `add-finding` + `update-task`
12. `.claude/skills/research-unattended/SKILL.md` — architecture: `GEDCOM + genealogy.db`
13. `.claude/skills/harden/SKILL.md` — document step uses `add-finding`
14. `.claude/skills/fan-chart/SKILL.md` — DB as primary tier source
15. `.claude/skills/verify-scans/SKILL.md` — query DB for pending verifications

### Removed

- `scripts/sync_db_to_markdown.py` — superseded by `research_db.py sync-to-markdown`

## End-to-End Test (2026-04-05)

Ran a real research task using only DB commands (no FINDINGS.md reads):

1. `get-tasks` → returned 5 active tasks with context
2. `get-person I800012` → Orgelia Johanna Popping with 5 findings, family, research state
3. `search "Poppings baptism parents"` → found F-912 instantly via FTS5
4. WieWasWie API lookup → confirmed Janna Poppink baptism record (doc 52211690)
5. `add-finding F-1293` → created with auto person-linking
6. `update-task RQ-014` → appended verification note
7. `log-run` → recorded as run_id 1

**Bug found and fixed:** `search "F-912"` crashed — FTS5 interpreted the hyphen
as a column subtraction operator. Fix: auto-quote hyphenated terms in query.

## Earlier Smoke Test Results

- `get-person I0000` → 3.8K chars (was ~500K reading FINDINGS.md)
- `get-person I501685` → 4.6K chars
- `search "Scottish"` → FTS5 with ranked snippets, finds relevant findings
- `add-finding` → auto-ID, auto-markdown, FTS trigger fires immediately
- `update-task` → status + note append works
- `rebuild-research-state --person` → incremental rebuild picks up new findings
- Fan chart `--db` vs `--no-db` → same ancestor count (119/122), DB gives finer tiers
- Round-trip `sync-to-markdown` → cosmetic diffs only (blank lines, priority reorder)

## Known Issues

- **Person count delta**: `analyze_gedcom.py` finds 2523 persons vs `gedcom_query.py`
  2412. Pre-existing parsing difference between the two scripts, not a migration bug.
  The DB uses `analyze_gedcom.py` as specified in the plan.
- **15 duplicate finding IDs** in FINDINGS.md (e.g. F-084, F-198, F-204–F-214, F-1011–F-1012).
  Handled with `INSERT OR REPLACE` (last entry wins). 1303 entries → 1284 unique.
- **Round-trip not identical**: `sync-to-markdown` produces cosmetic differences
  (extra blank lines, priority-based reordering of tasks). Content is preserved.

## Next Steps

1. ~~End-to-end test~~ DONE (2026-04-05)
2. **Test research-runner.sh**: dry-run to verify the updated prompt and counting
3. ~~Commit the migration~~ DONE (public repo)
4. **Run an actual unattended research session** with the new DB-backed workflow
5. Consider deduplicating the 15 duplicate findings in FINDINGS.md

## Key Decisions

- **`raw_markdown` is canonical** in findings/research_tasks. Structured fields
  are best-effort extractions. Parser improves over time without data loss.
- **No ORM, no new deps.** Pure `sqlite3` stdlib + `sqlite3.Row`.
- **Reuse `analyze_gedcom.py` parsing** via imports — no GEDCOM parser duplication.
- **GEDCOM stays source of truth for the tree.** DB caches for queries.
- **FTS5 with auto-sync triggers** — no manual sync needed.
- **FINDINGS.md lock removed** — now a derived artifact, not a concurrent-write target.
- **Duplicate finding IDs**: last entry wins (INSERT OR REPLACE) rather than failing.

## Reference

```bash
# Full migration from scratch
python scripts/init_db.py --reset
python scripts/migrate_research.py
python scripts/migrate_gedcom.py
python scripts/build_research_state.py

# Typical session boot (~5K tokens vs ~500K)
python scripts/research_db.py get-tasks --limit 1
python scripts/research_db.py get-person I0067

# After GEDCOM edits
python scripts/research_db.py sync-from-gedcom
python scripts/research_db.py rebuild-research-state

# Regenerate markdown from DB
python scripts/research_db.py sync-to-markdown
```

## Rollback

Markdown files were never deleted. Full rollback:

```bash
rm private/genealogy.db
git checkout HEAD -- scripts/   # restore pre-migration scripts
# FINDINGS.md and RESEARCH_QUEUE.md are untouched
```
