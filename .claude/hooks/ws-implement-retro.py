#!/usr/bin/env python3
"""Stop hook: after ws-implement finishes a plan, make Claude run the retrospective.

ws-implement writes plans/NNN_slug/.ws-implement.run with `started=<ISO>` at § 0 and
`finished=<ISO>` at § 9. When a run is finished and has no `retro=` line yet, this hook
writes plans/NNN_slug/run-metrics.md, marks the run `retro=requested` (so it fires once),
and blocks the stop with the instruction to run the retro. Otherwise it does nothing.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def ran_here(transcript, needle):
    """True when this session's transcript wrote the run marker, i.e. this session ran the plan."""
    if not transcript:
        return False
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            return any(needle in line for line in f)
    except OSError:
        return False


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("stop_hook_active"):
        return  # already continuing because of a stop hook — never loop

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
    for marker in sorted(root.glob("plans/*/.ws-implement.run")):
        fields = dict(
            line.split("=", 1) for line in marker.read_text().splitlines() if "=" in line
        )
        if "finished" not in fields or "retro" in fields:
            continue

        plan_dir = marker.parent
        transcript = event.get("transcript_path")
        if not ran_here(transcript, f"{plan_dir.name}/.ws-implement.run"):
            continue  # another session ran this plan; leave its retro to that session

        metrics = plan_dir / "run-metrics.md"
        if transcript and "started" in fields:
            script = root / ".agents/skills/ws-implement/run-metrics.py"
            out = subprocess.run(
                [sys.executable, str(script), transcript, fields["started"], fields["finished"]],
                capture_output=True, text=True, timeout=60,
            )
            metrics.write_text(f"# Run metrics — {plan_dir.name}\n\n" + (out.stdout or out.stderr))

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with marker.open("a") as f:
            f.write(f"retro=requested {now}\n")

        rel = plan_dir.relative_to(root)
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"ws-implement finished {rel.name}. Before stopping, run the retrospective: "
                f"follow .agents/skills/ws-implement/retro.md using {rel}/run-metrics.md "
                f"and what you saw during the run. Keep it short; don't spawn subagents."
            ),
        }))
        return


if __name__ == "__main__":
    main()
