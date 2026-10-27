#!/usr/bin/env python3
"""run-metrics.py <main-transcript.jsonl> <since-ISO> [until-ISO]
   run-metrics.py --plan plans/<code>/NNN_slug

Print a Markdown metrics table for one ws-implement run, read from Claude Code
transcripts: the main session plus every subagent it spawned in the window.
Tokens are summed from each assistant message's `usage`; time is first → last
message. `--plan` reads the window from the plan's `Run: <start> → <end>` line and picks
the newest Claude Code transcript of this workspace that mentions the plan. Run by the
ws-implement retro (retro.md); safe to run by hand.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def scan(path, since, until):
    """Return (first, last, msgs, tools, tok) for messages inside the window."""
    first = last = None
    msgs = tools = 0
    tok = {"in": 0, "cache_write": 0, "cache_read": 0, "out": 0}
    model = None
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        t = d.get("timestamp")
        if not t:
            continue
        t = ts(t)
        if t < since or (until and t > until):
            continue
        first = first or t
        last = t
        m = d.get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant":
            continue
        msgs += 1
        model = m.get("model") or model
        content = m.get("content")
        if isinstance(content, list):
            tools += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use")
        u = m.get("usage") or {}
        tok["in"] += u.get("input_tokens", 0)
        tok["cache_write"] += u.get("cache_creation_input_tokens", 0)
        tok["cache_read"] += u.get("cache_read_input_tokens", 0)
        tok["out"] += u.get("output_tokens", 0)
    return first, last, msgs, tools, tok, model


def k(n):
    return f"{n / 1000:.0f}k" if n >= 1000 else str(n)


def mins(a, b):
    return f"{(b - a).total_seconds() / 60:.1f}" if a and b else "–"


def row(name, model, effort, r):
    first, last, msgs, tools, tok, seen_model = r
    fresh = tok["in"] + tok["cache_write"]
    return (f"| {name} | {seen_model or model or '?'} | {effort or '–'} | {mins(first, last)} | "
            f"{msgs} | {tools} | {k(fresh)} | {k(tok['cache_read'])} | {k(tok['out'])} |"), tok


def from_plan(plan_dir):
    """(transcript, since, until) for a plan: its `Run:` line + this workspace's newest transcript."""
    plan_dir = Path(plan_dir)
    m = re.search(r"^Run:\s*(\S+)\s*→\s*(\S*)", (plan_dir / "plan.md").read_text(), re.M)
    if not m:
        sys.exit(f"{plan_dir}/plan.md has no `Run: <start> → <end>` line")
    root = Path.cwd().resolve()
    projects = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(root))
    candidates = sorted(projects.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        with open(path, encoding="utf-8", errors="ignore") as f:
            if any(plan_dir.name in line for line in f):
                return path, m.group(1), m.group(2) or None
    sys.exit(f"no Claude Code transcript in {projects} mentions {plan_dir.name}")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--plan":
        path, since, until = from_plan(sys.argv[2])
        main_path, since, until = path, ts(since), ts(until) if until else None
    elif len(sys.argv) >= 3:
        main_path = Path(sys.argv[1])
        since = ts(sys.argv[2])
        until = ts(sys.argv[3]) if len(sys.argv) > 3 else None
    else:
        sys.exit(__doc__)

    lines = ["| Agent | Model | Effort | Minutes | Turns | Tool calls | Fresh input | Cache read | Output |",
             "|---|---|---|---|---|---|---|---|---|"]
    total = {"in": 0, "cache_write": 0, "cache_read": 0, "out": 0}

    r = scan(main_path, since, until)
    wall = (r[0], r[1])
    text, tok = row("main session", None, None, r)
    lines.append(text)
    for key in total:
        total[key] += tok[key]

    sub_dir = main_path.with_suffix("") / "subagents"
    subs = 0
    for f in sorted(sub_dir.glob("agent-*.jsonl")) if sub_dir.is_dir() else []:
        r = scan(f, since, until)
        if not r[2]:
            continue
        meta = {}
        meta_path = f.with_suffix(".meta.json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
        text, tok = row(meta.get("description", f.stem), meta.get("model"), meta.get("effort"), r)
        lines.append(text)
        subs += 1
        for key in total:
            total[key] += tok[key]

    print(f"Run window: {since.isoformat()} → {(until or wall[1] or since).isoformat()} · "
          f"wall clock {mins(*wall)} min · {subs} subagent(s)\n")
    print("\n".join(lines))
    print(f"| **total** | | | | | | **{k(total['in'] + total['cache_write'])}** | "
          f"**{k(total['cache_read'])}** | **{k(total['out'])}** |")
    print("\nFresh input = uncached + cache-write tokens (the expensive part); "
          "cache read is ~10× cheaper. Codex runs are not in Claude transcripts — add them by hand.")


if __name__ == "__main__":
    main()
