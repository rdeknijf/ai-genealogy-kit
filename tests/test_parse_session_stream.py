"""Tests for parse_session_stream — live stream-json parser."""

from __future__ import annotations

import json
import signal
from unittest.mock import patch

from parse_session_stream import StreamParser

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_event(session_id: str = "abc123", model: str = "claude-sonnet-4-20250514") -> str:
    return json.dumps(
        {"type": "system", "subtype": "init", "session_id": session_id, "model": model}
    )


def _assistant_tool_use(
    name: str = "Bash", input_: dict | None = None, tool_id: str = "tu1"
) -> str:
    if input_ is None:
        input_ = {"command": "echo hello"}
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": tool_id, "name": name, "input": input_},
                ],
            },
        }
    )


def _assistant_text(text: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": text}],
            },
        }
    )


def _result_event(cost: float = 1.45, num_turns: int = 25) -> str:
    return json.dumps(
        {
            "type": "result",
            "subtype": "success",
            "num_turns": num_turns,
            "duration_ms": 180000,
            "total_cost_usd": cost,
            "usage": {"input_tokens": 50000, "output_tokens": 8000},
        }
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPassthrough:
    def test_passthrough_writes_all_lines(self, tmp_path):
        """Every line fed to process_line appears in the output .jsonl file."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        lines = [_init_event(), _assistant_text("hi"), _assistant_tool_use(), _result_event()]
        for line in lines:
            parser.process_line(line)
        parser.close()

        written = out.read_text().strip().splitlines()
        assert len(written) == len(lines)
        for original, saved in zip(lines, written):
            assert json.loads(original) == json.loads(saved)

    def test_passthrough_preserves_malformed_lines(self, tmp_path):
        """Non-JSON lines are still written to the output file."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line("not json at all")
        parser.process_line(_init_event())
        parser.close()

        written = out.read_text().strip().splitlines()
        assert len(written) == 2
        assert written[0] == "not json at all"


class TestHeartbeat:
    def test_heartbeat_written(self, tmp_path):
        """Heartbeat file is created after an interval elapses."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"

        clock = [100.0]
        parser = StreamParser(
            str(out), str(hb), heartbeat_interval=60, time_func=lambda: clock[0]
        )

        parser.process_line(_init_event())
        # Advance past the interval
        clock[0] = 170.0
        parser.process_line(_assistant_text("trigger heartbeat"))

        assert hb.exists()
        data = json.loads(hb.read_text())
        assert data["session_id"] == "abc123"
        assert data["model"] == "claude-sonnet-4-20250514"

    def test_heartbeat_not_written_before_interval(self, tmp_path):
        """Heartbeat file is NOT created before interval elapses."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"

        clock = [100.0]
        parser = StreamParser(
            str(out), str(hb), heartbeat_interval=60, time_func=lambda: clock[0]
        )

        parser.process_line(_init_event())
        clock[0] = 110.0  # only 10 seconds later
        parser.process_line(_assistant_text("too early"))

        assert not hb.exists()


class TestSessionExtraction:
    def test_extracts_session_id(self, tmp_path):
        """Session ID from init event appears in heartbeat state."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line(_init_event(session_id="sess-xyz", model="claude-opus-4"))
        state = parser.get_state()

        assert state["session_id"] == "sess-xyz"
        assert state["model"] == "claude-opus-4"


class TestToolCounting:
    def test_counts_tool_calls(self, tmp_path):
        """Tool use events increment the tool_calls counter."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line(_init_event())
        parser.process_line(_assistant_tool_use("Bash", {"command": "ls"}, "tu1"))
        parser.process_line(_assistant_tool_use("Read", {"file_path": "/a"}, "tu2"))
        parser.process_line(_assistant_tool_use("Bash", {"command": "pwd"}, "tu3"))

        state = parser.get_state()
        assert state["tool_calls"] == 3
        assert state["last_tool"] == "Bash"

    def test_counts_multiple_tool_uses_in_single_message(self, tmp_path):
        """A single assistant message with multiple tool_use blocks counts each."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        line = json.dumps(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use", "id": "tu1",
                            "name": "Bash", "input": {"command": "ls"},
                        },
                        {
                            "type": "tool_use", "id": "tu2",
                            "name": "Read", "input": {"file_path": "/x"},
                        },
                    ],
                },
            }
        )
        parser.process_line(line)
        assert parser.get_state()["tool_calls"] == 2


class TestStuckDetection:
    def test_detects_stuck_repeated_tools(self, tmp_path):
        """Three consecutive identical tool calls set stuck=true."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        same_call = _assistant_tool_use("Bash", {"command": "echo stuck"})
        parser.process_line(same_call)
        parser.process_line(same_call)
        assert not parser.get_state()["stuck"]

        parser.process_line(same_call)
        state = parser.get_state()
        assert state["stuck"] is True
        assert state["repeat_count"] == 3

    def test_not_stuck_different_tools(self, tmp_path):
        """Different consecutive tool calls do not trigger stuck."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line(_assistant_tool_use("Bash", {"command": "ls"}, "tu1"))
        parser.process_line(_assistant_tool_use("Read", {"file_path": "/x"}, "tu2"))
        parser.process_line(_assistant_tool_use("Bash", {"command": "pwd"}, "tu3"))

        state = parser.get_state()
        assert state["stuck"] is False
        assert state["repeat_count"] == 1

    def test_stuck_resets_on_different_call(self, tmp_path):
        """Repeat count resets when a different tool call appears."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        same = _assistant_tool_use("Bash", {"command": "echo stuck"})
        parser.process_line(same)
        parser.process_line(same)
        parser.process_line(same)
        assert parser.get_state()["stuck"] is True

        parser.process_line(_assistant_tool_use("Read", {"file_path": "/x"}, "tu2"))
        state = parser.get_state()
        assert state["stuck"] is False
        assert state["repeat_count"] == 1


class TestCostExtraction:
    def test_extracts_cost_from_result(self, tmp_path):
        """Cost from a result event appears in the heartbeat state."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line(_init_event())
        parser.process_line(_result_event(cost=2.75, num_turns=30))

        state = parser.get_state()
        assert state["total_cost_usd"] == 2.75
        assert state["turn"] == 30


class TestAtomicWrite:
    def test_heartbeat_atomic_write(self, tmp_path):
        """Heartbeat is written atomically via temp+rename (no leftover temps)."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb))

        parser.process_line(_init_event())
        parser.write_heartbeat()

        assert hb.exists()
        data = json.loads(hb.read_text())
        assert "session_id" in data
        assert "updated_at" in data

        # No leftover temp files in the directory
        siblings = list(tmp_path.iterdir())
        names = [p.name for p in siblings]
        temp_files = [n for n in names if n.startswith("tmp") or n.startswith(".tmp")]
        assert temp_files == []


class TestCircuitBreaker:
    def test_circuit_breaker_kills(self, tmp_path):
        """When kill_on_stuck threshold is exceeded, SIGTERM is sent."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb), kill_on_stuck=5)

        same_call = _assistant_tool_use("Bash", {"command": "echo stuck"})

        with patch("parse_session_stream.os.killpg") as mock_kill:
            # Feed 5 identical calls — should not kill yet
            for _ in range(5):
                parser.process_line(same_call)
            mock_kill.assert_not_called()

            # 6th call exceeds the threshold
            parser.process_line(same_call)
            mock_kill.assert_called_once()
            args = mock_kill.call_args[0]
            assert args[1] == signal.SIGTERM

    def test_circuit_breaker_disabled_by_default(self, tmp_path):
        """With kill_on_stuck=0, no kill is sent even with many repeats."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb), kill_on_stuck=0)

        same_call = _assistant_tool_use("Bash", {"command": "echo stuck"})

        with patch("parse_session_stream.os.killpg") as mock_kill:
            for _ in range(20):
                parser.process_line(same_call)
            mock_kill.assert_not_called()


class TestCloseWritesFinalHeartbeat:
    def test_close_writes_heartbeat(self, tmp_path):
        """close() writes a final heartbeat even if interval hasn't elapsed."""
        out = tmp_path / "out.jsonl"
        hb = tmp_path / "heartbeat.json"
        parser = StreamParser(str(out), str(hb), heartbeat_interval=9999)

        parser.process_line(_init_event())
        parser.process_line(_assistant_tool_use())
        assert not hb.exists()

        parser.close()
        assert hb.exists()
        data = json.loads(hb.read_text())
        assert data["session_id"] == "abc123"
        assert data["tool_calls"] == 1
