"""Tests for session_state module — TDD: tests written before implementation."""

from __future__ import annotations

import json

from session_state import (
    extract_state_from_log,
    format_for_prompt,
    load_state,
    merge_state,
    save_state,
)

# --- merge_state tests ---


def test_merge_same_task_increments_count():
    existing = {"current_task": "RQ-034", "session_count_on_task": 3}
    update = {"current_task": "RQ-034"}
    result = merge_state(existing, update)
    assert result["session_count_on_task"] == 4


def test_merge_different_task_resets_count():
    existing = {"current_task": "RQ-034", "session_count_on_task": 3}
    update = {"current_task": "RQ-035"}
    result = merge_state(existing, update)
    assert result["current_task"] == "RQ-035"
    assert result["session_count_on_task"] == 1


def test_merge_persons_completed_union():
    existing = {"persons_completed": ["I0601", "I900056"]}
    update = {"persons_completed": ["I900056", "I0130"]}
    result = merge_state(existing, update)
    assert sorted(result["persons_completed"]) == ["I0130", "I0601", "I900056"]


def test_merge_persons_blocked_update_wins():
    existing = {
        "persons_blocked": {
            "I900075": "old reason",
            "I600014": "Gouda DTB unindexed",
        }
    }
    update = {
        "persons_blocked": {
            "I900075": "GA 0176 Putten DTB not indexed pre-1811",
            "I0130": "new block",
        }
    }
    result = merge_state(existing, update)
    assert result["persons_blocked"]["I900075"] == "GA 0176 Putten DTB not indexed pre-1811"
    assert result["persons_blocked"]["I600014"] == "Gouda DTB unindexed"
    assert result["persons_blocked"]["I0130"] == "new block"


def test_merge_leads_replaced():
    existing = {
        "leads_to_pursue": [
            {"person": "I0130", "source": "gelders-archief", "hint": "old lead"}
        ]
    }
    update = {
        "leads_to_pursue": [
            {"person": "I0200", "source": "wiewaswie", "hint": "new lead"}
        ]
    }
    result = merge_state(existing, update)
    assert len(result["leads_to_pursue"]) == 1
    assert result["leads_to_pursue"][0]["person"] == "I0200"


def test_merge_null_removes_key():
    existing = {"current_task": "RQ-034", "coverage_score": 71.8, "custom_key": "value"}
    update = {"custom_key": None}
    result = merge_state(existing, update)
    assert "custom_key" not in result
    assert result["current_task"] == "RQ-034"


def test_merge_unknown_keys_preserved():
    existing = {"current_task": "RQ-034", "extra_field": "keep me"}
    update = {"current_task": "RQ-035", "another_field": "add me"}
    result = merge_state(existing, update)
    assert result["extra_field"] == "keep me"
    assert result["another_field"] == "add me"


def test_merge_empty_existing():
    update = {
        "schema_version": 1,
        "current_task": "RQ-034",
        "session_count_on_task": 1,
        "persons_completed": ["I0601"],
        "persons_blocked": {"I900075": "reason"},
        "leads_to_pursue": [{"person": "I0130", "source": "ga", "hint": "test"}],
        "negative_searches_added": 5,
        "findings_added": ["F-042"],
        "coverage_score": 71.8,
    }
    result = merge_state({}, update)
    assert result["current_task"] == "RQ-034"
    assert result["session_count_on_task"] == 1
    assert result["persons_completed"] == ["I0601"]


def test_merge_schema_version_keeps_higher():
    existing = {"schema_version": 2}
    update = {"schema_version": 1}
    result = merge_state(existing, update)
    assert result["schema_version"] == 2

    result2 = merge_state({"schema_version": 1}, {"schema_version": 3})
    assert result2["schema_version"] == 3


# --- load_state / save_state tests ---


def test_load_missing_file(tmp_path):
    path = tmp_path / "nonexistent.json"
    result = load_state(path)
    assert result == {"schema_version": 1}


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    state = {
        "schema_version": 1,
        "last_updated": "2026-04-23T10:34:13Z",
        "current_task": "RQ-034",
        "session_count_on_task": 3,
        "persons_completed": ["I0601", "I900056"],
        "persons_blocked": {"I900075": "GA 0176 Putten DTB not indexed pre-1811"},
        "leads_to_pursue": [
            {"person": "I0130", "source": "gelders-archief", "hint": "Beekbergen DTB ~1766"}
        ],
        "negative_searches_added": 5,
        "findings_added": ["F-042", "F-043"],
        "coverage_score": 71.8,
    }
    save_state(path, state)
    loaded = load_state(path)
    assert loaded == state


def test_save_atomic(tmp_path):
    """Verify that save uses a temp file (no .tmp left behind on success)."""
    path = tmp_path / "state.json"
    tmp_file = path.with_suffix(".tmp")
    save_state(path, {"schema_version": 1, "current_task": "RQ-001"})
    # The final file exists
    assert path.exists()
    # The temp file should NOT exist after a successful write
    assert not tmp_file.exists()
    # Verify the content is valid JSON
    content = json.loads(path.read_text())
    assert content["current_task"] == "RQ-001"


def test_save_pretty_printed(tmp_path):
    """Verify output is pretty-printed with indent=2."""
    path = tmp_path / "state.json"
    save_state(path, {"schema_version": 1, "key": "val"})
    text = path.read_text()
    # Pretty-printed JSON has newlines and indentation
    assert "\n" in text
    assert '  "' in text


# --- format_for_prompt tests ---


def test_format_for_prompt_complete():
    state = {
        "schema_version": 1,
        "current_task": "RQ-034",
        "session_count_on_task": 3,
        "persons_completed": ["I0601", "I900056"],
        "persons_blocked": {
            "I900075": "GA 0176 Putten DTB not indexed pre-1811",
            "I600014": "Gouda DTB unindexed, needs Streekarchief visit",
        },
        "leads_to_pursue": [
            {
                "person": "I0130",
                "source": "gelders-archief",
                "hint": "Beekbergen DTB ~1766, try browsing scans",
            }
        ],
        "coverage_score": 71.8,
    }
    text = format_for_prompt(state)
    assert "## Previous session state" in text
    assert "RQ-034" in text
    assert "session 3" in text
    assert "I0601" in text
    assert "I900056" in text
    assert "DO NOT search these" in text
    assert "I900075" in text
    assert "GA 0176 Putten DTB not indexed pre-1811" in text
    assert "I600014" in text
    assert "Leads to pursue" in text
    assert "gelders-archief" in text
    assert "Beekbergen DTB" in text
    assert "71.8%" in text


def test_format_for_prompt_empty_state():
    state = {"schema_version": 1}
    text = format_for_prompt(state)
    assert "## Previous session state" in text
    # Empty state should not contain section headers for missing data
    assert "Blocked persons" not in text
    assert "Leads to pursue" not in text
    assert "Completed persons" not in text
    assert "Coverage score" not in text


def test_format_for_prompt_skips_empty_sections():
    state = {
        "schema_version": 1,
        "current_task": "RQ-034",
        "session_count_on_task": 1,
        "persons_completed": [],
        "persons_blocked": {},
        "leads_to_pursue": [],
    }
    text = format_for_prompt(state)
    assert "Completed persons" not in text
    assert "Blocked persons" not in text
    assert "Leads to pursue" not in text


# --- extract_state_from_log tests ---


def test_extract_state_from_log():
    state_dict = {
        "schema_version": 1,
        "current_task": "RQ-034",
        "session_count_on_task": 2,
        "persons_completed": ["I0601"],
    }
    log_text = f"""Some log output here...
Research completed 2 cycles.
<!-- STATE_JSON {json.dumps(state_dict)} STATE_JSON -->
End of session.
"""
    result = extract_state_from_log(log_text)
    assert result is not None
    assert result["current_task"] == "RQ-034"
    assert result["persons_completed"] == ["I0601"]


def test_extract_state_missing_markers():
    log_text = "Just some regular log output with no state markers."
    result = extract_state_from_log(log_text)
    assert result is None


def test_extract_state_malformed_json():
    log_text = "<!-- STATE_JSON {not valid json STATE_JSON -->"
    result = extract_state_from_log(log_text)
    assert result is None
