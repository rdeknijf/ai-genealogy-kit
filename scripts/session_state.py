"""Session state management for research runner handoff.

Replaces prose session summaries with structured JSON state that
persists between research sessions. The state file tracks which
task is active, which persons are completed/blocked, and what
leads remain to pursue.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

# Keys that use set-union merge semantics
_SET_UNION_KEYS = {"persons_completed"}

# Keys that use dict-merge semantics (update wins on conflict)
_DICT_MERGE_KEYS = {"persons_blocked"}

# Keys that are always replaced from the update
_REPLACE_KEYS = {
    "last_updated",
    "leads_to_pursue",
    "negative_searches_added",
    "findings_added",
    "coverage_score",
}


def merge_state(existing: dict, update: dict) -> dict:
    """Merge an update into existing state with typed merge rules.

    Pure function — no I/O. Rules:
    - schema_version: keep the higher value
    - current_task: replace; if same task, increment session_count_on_task;
      if different, reset to 1
    - persons_completed: set union by ID
    - persons_blocked: dict merge (update wins on conflict)
    - leads_to_pursue: replace entirely
    - negative_searches_added, findings_added, coverage_score, last_updated: replace
    - null in update: remove key from result
    - Unknown keys: keep from existing, add from update
    """
    result = dict(existing)

    # Handle schema_version: keep the higher value
    if "schema_version" in update and update["schema_version"] is not None:
        existing_ver = existing.get("schema_version", 0)
        update_ver = update["schema_version"]
        result["schema_version"] = max(existing_ver, update_ver)

    # Handle current_task + session_count_on_task together
    if "current_task" in update and update["current_task"] is not None:
        old_task = existing.get("current_task")
        new_task = update["current_task"]
        result["current_task"] = new_task
        if old_task == new_task:
            result["session_count_on_task"] = existing.get("session_count_on_task", 0) + 1
        else:
            result["session_count_on_task"] = 1
    elif "session_count_on_task" in update and update["session_count_on_task"] is not None:
        result["session_count_on_task"] = update["session_count_on_task"]

    # Handle set-union keys
    for key in _SET_UNION_KEYS:
        if key in update and update[key] is not None:
            existing_set = set(existing.get(key, []))
            update_set = set(update[key])
            result[key] = sorted(existing_set | update_set)

    # Handle dict-merge keys
    for key in _DICT_MERGE_KEYS:
        if key in update and update[key] is not None:
            merged = dict(existing.get(key, {}))
            merged.update(update[key])
            result[key] = merged

    # Handle replace keys
    for key in _REPLACE_KEYS:
        if key in update and update[key] is not None:
            result[key] = update[key]

    # Handle unknown keys: add from update, keep from existing
    known_keys = (
        _SET_UNION_KEYS
        | _DICT_MERGE_KEYS
        | _REPLACE_KEYS
        | {"schema_version", "current_task", "session_count_on_task"}
    )
    for key in update:
        if key not in known_keys and update[key] is not None:
            result[key] = update[key]

    # Handle null removal: any key set to None in update is removed
    for key, value in update.items():
        if value is None and key in result:
            del result[key]

    return result


def load_state(path: Path) -> dict:
    """Load session state from JSON file.

    Returns a minimal state with schema_version=1 if the file
    doesn't exist.
    """
    if not path.exists():
        return {"schema_version": 1}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict) -> None:
    """Atomically save session state to JSON file.

    Writes to a temp file first, then renames to avoid partial writes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, indent=2) + "\n")
    os.replace(tmp_path, path)


def format_for_prompt(state: dict) -> str:
    """Format session state into text for injection into the research prompt.

    Skips sections that are empty/missing so the prompt stays clean.
    """
    lines = ["## Previous session state", ""]

    task = state.get("current_task")
    if task:
        count = state.get("session_count_on_task", 1)
        lines.append(f"Current task: {task} (session {count} on this task)")

    completed = state.get("persons_completed", [])
    if completed:
        lines.append(f"Completed persons: {', '.join(completed)}")

    blocked = state.get("persons_blocked", {})
    if blocked:
        lines.append("Blocked persons (DO NOT search these):")
        for person_id, reason in blocked.items():
            lines.append(f"  - {person_id}: {reason}")

    leads = state.get("leads_to_pursue", [])
    if leads:
        lines.append("Leads to pursue:")
        for lead in leads:
            person = lead.get("person", "?")
            source = lead.get("source", "?")
            hint = lead.get("hint", "")
            lines.append(f"  - {person} → {source}: {hint}")

    score = state.get("coverage_score")
    if score is not None:
        lines.append(f"Coverage score: {score}%")

    return "\n".join(lines)


def extract_state_from_log(log_text: str) -> dict | None:
    """Extract a STATE_JSON block from session log output.

    Looks for: <!-- STATE_JSON {...} STATE_JSON -->
    Returns the parsed dict, or None if not found or malformed.
    """
    pattern = r"<!--\s*STATE_JSON\s+(.*?)\s+STATE_JSON\s*-->"
    match = re.search(pattern, log_text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return None
