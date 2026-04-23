#!/usr/bin/env python3
"""Live stream-json parser for monitoring Claude Code research sessions.

Reads stream-json from stdin line by line, writes each line to a .jsonl file,
and periodically writes a heartbeat file with session state. Detects stuck
sessions (repeated identical tool calls) and optionally kills the parent
process group via SIGTERM.

Usage as a pipeline filter:

    claude -p --output-format stream-json --verbose \\
        | python scripts/parse_session_stream.py \\
            --output /path/to/session.jsonl \\
            --heartbeat-file /path/to/heartbeat.json \\
            --heartbeat-interval 60 \\
            --kill-on-stuck 5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _fingerprint(name: str, input_: Any) -> str:
    """Hash of (tool_name, input) for duplicate detection."""
    payload = json.dumps({"name": name, "input": input_}, sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()[:8]


class StreamParser:
    """Stateful parser for Claude Code stream-json output.

    Call ``process_line()`` for each line of input.  Call ``get_state()`` to
    inspect the current heartbeat payload, and ``write_heartbeat()`` to
    force-write the heartbeat file.
    """

    def __init__(
        self,
        output_path: str,
        heartbeat_path: str,
        heartbeat_interval: int = 60,
        kill_on_stuck: int = 0,
        time_func: Any = None,
    ) -> None:
        self.output_path = Path(output_path)
        self.heartbeat_path = Path(heartbeat_path)
        self.heartbeat_interval = heartbeat_interval
        self.kill_on_stuck = kill_on_stuck
        self._time = time_func or time.time

        # Open output file for line-buffered appending
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._out = open(self.output_path, "a", buffering=1)  # noqa: SIM115

        # Session state
        self.session_id: str | None = None
        self.model: str | None = None
        self.turn: int = 0
        self.tool_calls: int = 0
        self.total_cost_usd: float = 0.0
        self.last_tool: str | None = None
        self.last_tool_input_hash: str | None = None
        self.repeat_count: int = 0
        self.stuck: bool = False

        # Track consecutive fingerprints for stuck detection
        self._last_fingerprint: str | None = None

        # Heartbeat timing
        self._last_heartbeat_at: float = self._time()

    def process_line(self, line: str) -> None:
        """Process one line of stream-json input."""
        # Always passthrough to output file first
        self._out.write(line.rstrip("\n") + "\n")
        self._out.flush()

        # Parse JSON (skip malformed lines silently)
        stripped = line.strip()
        if not stripped or not stripped.startswith("{"):
            return
        try:
            ev = json.loads(stripped)
        except json.JSONDecodeError:
            return

        self._handle_event(ev)
        self._update_heartbeat()

    def _handle_event(self, ev: dict[str, Any]) -> None:
        t = ev.get("type")

        if t == "system" and ev.get("subtype") == "init":
            self.session_id = ev.get("session_id") or self.session_id
            self.model = ev.get("model") or self.model

        elif t == "assistant":
            content = ev.get("message", {}).get("content") or []
            for block in content:
                if block.get("type") == "tool_use":
                    self._handle_tool_use(block)

        elif t == "result":
            if ev.get("total_cost_usd") is not None:
                self.total_cost_usd = ev["total_cost_usd"]
            if ev.get("num_turns") is not None:
                self.turn = ev["num_turns"]

    def _handle_tool_use(self, block: dict[str, Any]) -> None:
        name = block.get("name", "")
        input_ = block.get("input", {})
        fp = _fingerprint(name, input_)

        self.tool_calls += 1
        self.last_tool = name
        self.last_tool_input_hash = fp

        if fp == self._last_fingerprint:
            self.repeat_count += 1
        else:
            self._last_fingerprint = fp
            self.repeat_count = 1

        self.stuck = self.repeat_count >= 3

        # Circuit breaker
        if self.kill_on_stuck > 0 and self.repeat_count > self.kill_on_stuck:
            self.write_heartbeat()  # persist state before killing
            os.killpg(os.getpgrp(), signal.SIGTERM)

    def _update_heartbeat(self) -> None:
        """Write heartbeat if the configured interval has elapsed."""
        now = self._time()
        if now - self._last_heartbeat_at >= self.heartbeat_interval:
            self.write_heartbeat()
            self._last_heartbeat_at = now

    def write_heartbeat(self) -> None:
        """Force write heartbeat file (atomic: temp + rename)."""
        state = self.get_state()
        data = json.dumps(state, indent=2)

        # Atomic write: temp file in same directory, then rename
        self.heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.heartbeat_path.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(data)
            os.replace(tmp_path, str(self.heartbeat_path))
        except BaseException:
            # Clean up temp on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def get_state(self) -> dict[str, Any]:
        """Return the current heartbeat state dict."""
        return {
            "session_id": self.session_id,
            "model": self.model,
            "turn": self.turn,
            "tool_calls": self.tool_calls,
            "total_cost_usd": self.total_cost_usd,
            "last_tool": self.last_tool,
            "last_tool_input_hash": self.last_tool_input_hash,
            "repeat_count": self.repeat_count,
            "stuck": self.stuck,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def close(self) -> None:
        """Flush output and write a final heartbeat."""
        self.write_heartbeat()
        self._out.close()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Live stream-json parser for Claude Code sessions."
    )
    ap.add_argument(
        "--output", required=True, help="Path for the raw .jsonl passthrough file"
    )
    ap.add_argument(
        "--heartbeat-file", required=True, help="Path for the periodic heartbeat JSON"
    )
    ap.add_argument(
        "--heartbeat-interval",
        type=int,
        default=60,
        help="Seconds between heartbeat writes (default: 60)",
    )
    ap.add_argument(
        "--kill-on-stuck",
        type=int,
        default=0,
        help="Kill process group after N consecutive identical tool calls (0=disabled)",
    )
    args = ap.parse_args()

    parser = StreamParser(
        output_path=args.output,
        heartbeat_path=args.heartbeat_file,
        heartbeat_interval=args.heartbeat_interval,
        kill_on_stuck=args.kill_on_stuck,
    )

    try:
        for line in sys.stdin:
            parser.process_line(line)
    except KeyboardInterrupt:
        pass
    finally:
        parser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
