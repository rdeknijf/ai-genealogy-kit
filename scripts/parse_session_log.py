#!/usr/bin/env python3
"""Parse a Claude Code stream-json session log into a readable markdown summary.

Consumes the `.jsonl` produced by
`claude -p --output-format stream-json --verbose`. Emits a markdown log on
stdout, and (with --log-run) inserts a row into `research_tasks.task_runs`.

The markdown contains:
- Metadata header (session_id, model, exit_reason, turns, cost, picked task)
- Full final assistant text (so the existing sed `## Session Summary`
  extraction in research-runner.sh keeps working)
- Last ~10 tool calls — only on non-ok exits, for post-mortem diagnostics

Task ID is extracted heuristically: first `RQ-\\d+` found in tool-call
inputs or assistant text.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

RQ_PATTERN = re.compile(r"RQ-\d{3,4}")
DEFAULT_DB = Path(__file__).parent.parent / "private" / "genealogy.db"


def parse(path: Path) -> dict[str, Any]:
    session_id: str | None = None
    model: str | None = None
    result: dict[str, Any] | None = None
    assistant_texts: list[str] = []
    tool_calls: list[dict[str, Any]] = []

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = ev.get("type")
            if t == "system" and ev.get("subtype") == "init":
                session_id = ev.get("session_id") or session_id
                model = ev.get("model") or model
            elif t == "assistant":
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") == "text":
                        assistant_texts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        tool_calls.append(
                            {
                                "name": block.get("name"),
                                "input": block.get("input", {}),
                            }
                        )
            elif t == "result":
                result = ev

    # Task id heuristic: prefer RQ-NNN from update-task/add-finding commands
    # (the actual task worked on), then final assistant text, then frequency.
    from collections import Counter

    # Tier 1: RQ-NNN in update-task or add-finding commands (most reliable)
    action_rqs: list[str] = []
    for tc in tool_calls:
        inp = json.dumps(tc.get("input", {}))
        if "update-task" in inp or "add-finding" in inp:
            action_rqs.extend(RQ_PATTERN.findall(inp))

    if action_rqs:
        task_id = Counter(action_rqs).most_common(1)[0][0]
    else:
        # Tier 2: last assistant text (session summary)
        final_rqs = RQ_PATTERN.findall(assistant_texts[-1]) if assistant_texts else []
        if final_rqs:
            task_id = final_rqs[0]
        else:
            # Tier 3: frequency across all tool calls + assistant text
            rq_counts: Counter[str] = Counter()
            for tc in tool_calls:
                rq_counts.update(RQ_PATTERN.findall(json.dumps(tc)))
            for txt in assistant_texts:
                rq_counts.update(RQ_PATTERN.findall(txt))
            task_id = rq_counts.most_common(1)[0][0] if rq_counts else None

    final_text = assistant_texts[-1] if assistant_texts else ""

    if result is None:
        exit_reason = "unknown"
        num_turns = None
        duration_ms = None
        tokens_used = None
        cost = None
    else:
        if result.get("is_error"):
            exit_reason = result.get("subtype") or "error"
        else:
            exit_reason = result.get("subtype") or "success"
        num_turns = result.get("num_turns")
        duration_ms = result.get("duration_ms")
        usage = result.get("usage") or {}
        tokens_used = usage.get("output_tokens")
        cost = result.get("total_cost_usd")

    return {
        "session_id": session_id,
        "model": model,
        "task_id": task_id,
        "exit_reason": exit_reason,
        "num_turns": num_turns,
        "duration_ms": duration_ms,
        "tokens_used": tokens_used,
        "total_cost_usd": cost,
        "final_text": final_text,
        "tool_call_count": len(tool_calls),
        "last_tool_calls": tool_calls[-10:],
    }


def render_markdown(info: dict[str, Any]) -> str:
    out: list[str] = []
    out.append("# Session log")
    out.append("")
    out.append(f"- Session ID: `{info['session_id'] or 'unknown'}`")
    out.append(f"- Model: `{info['model'] or 'unknown'}`")
    out.append(f"- Task picked: `{info['task_id'] or 'unknown'}`")
    out.append(f"- Exit: `{info['exit_reason']}`")
    if info["num_turns"] is not None:
        out.append(
            f"- Turns: {info['num_turns']} — tool calls: {info['tool_call_count']}"
        )
    if info["total_cost_usd"] is not None and info["duration_ms"] is not None:
        out.append(
            f"- Cost: ${info['total_cost_usd']:.4f} — duration: "
            f"{info['duration_ms'] / 1000:.1f}s"
        )
    out.append("")

    if info["final_text"]:
        out.append("## Final output")
        out.append("")
        out.append(info["final_text"].rstrip())
        out.append("")

    if info["exit_reason"] not in ("success", "ok") and info["last_tool_calls"]:
        out.append("## Last tool calls (diagnostic)")
        out.append("")
        for tc in info["last_tool_calls"]:
            name = tc.get("name") or "?"
            inp = json.dumps(tc.get("input", {}), default=str)
            if len(inp) > 240:
                inp = inp[:240] + "…"
            out.append(f"- `{name}` — {inp}")
        out.append("")

    return "\n".join(out) + "\n"


def log_run(
    db_path: Path,
    info: dict[str, Any],
    started_at: str | None,
    coverage_before: float | None = None,
    coverage_after: float | None = None,
) -> None:
    db = sqlite3.connect(db_path)
    summary = (info["final_text"] or "").strip()
    if len(summary) > 2000:
        summary = summary[:2000] + "…"
    db.execute(
        "INSERT INTO task_runs (task_id, session_id, started_at, ended_at, "
        "tokens_used, summary, exit_reason, coverage_before, coverage_after) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            info.get("task_id"),
            info.get("session_id"),
            started_at,
            None,
            info.get("tokens_used"),
            summary,
            info.get("exit_reason"),
            coverage_before,
            coverage_after,
        ),
    )
    db.commit()
    db.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("jsonl", help="Path to the stream-json .jsonl log")
    ap.add_argument(
        "--log-run",
        action="store_true",
        help="Also insert a row into task_runs",
    )
    ap.add_argument(
        "--started-at",
        default=None,
        help="ISO timestamp when the session started (for --log-run)",
    )
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    ap.add_argument(
        "--coverage-before",
        type=float,
        default=None,
        help="Coverage score before the session (for --log-run)",
    )
    ap.add_argument(
        "--coverage-after",
        type=float,
        default=None,
        help="Coverage score after the session (for --log-run)",
    )
    args = ap.parse_args()

    path = Path(args.jsonl)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    info = parse(path)
    sys.stdout.write(render_markdown(info))

    if args.log_run:
        try:
            log_run(
                Path(args.db),
                info,
                args.started_at,
                coverage_before=args.coverage_before,
                coverage_after=args.coverage_after,
            )
        except Exception as e:
            print(f"warning: log-run failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
