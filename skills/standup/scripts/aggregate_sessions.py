#!/usr/bin/env python3
"""
Session aggregator for the standup skill.

Mechanical extractor (scan-project pattern): given a main repo root, enumerate
its worktrees, map each to its Claude Code session dir (~/.claude/projects/),
filter JSONL events by a target date (local tz), and emit a structured digest.
The standup SKILL.md LLM consumes this JSON to write the activity narrative.

Scope is the worktree set of ONE main repo (via `git worktree list`), NOT a
sweep of all projects. Drift-tolerant: session dirs may be named with hyphens
even when the worktree uses underscores (rename history); normalize treats `_`
and `-` as equivalent.

Time filter uses the in-event top-level `timestamp` (UTC ISO-8601), converted
to local tz before taking the date — NOT file mtime (a session file re-read
today still carries yesterday's events).

Usage:
    uv run python aggregate_sessions.py --project-root /path/to/repo
    uv run python aggregate_sessions.py --project-root . --output digest.json
"""

import argparse
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
from pathlib import Path
import subprocess


LOCAL_TZ = datetime.now().astimezone().tzinfo
PROJECTS_DIR = Path.home() / ".claude" / "projects"
CONVERSATIONAL_TYPES = ("user", "assistant")


def git_worktree_paths(repo_root: Path) -> list[Path]:
    """All worktree paths of the main repo (via `git worktree list --porcelain`)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths: list[Path] = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line[len("worktree ") :].strip()))
    return paths


def encode(path: Path) -> str:
    """Encode a path the way Claude Code names session dirs: '/' -> '-'."""
    return str(path).replace("/", "-")


def normalize(s: str) -> str:
    """Case + separator normalization so `_` and `-` match across rename drift."""
    return s.lower().replace("_", "-")


def match_session_dirs(
    worktrees: list[Path], projects_dir: Path = PROJECTS_DIR
) -> dict[Path, Path]:
    """Map each session dir -> its worktree path, tolerating name drift."""
    if not worktrees or not projects_dir.is_dir():
        return {}
    wt_norms = {normalize(encode(p)): p for p in worktrees}
    matched: dict[Path, Path] = {}
    for d in projects_dir.iterdir():
        if not d.is_dir():
            continue
        key = normalize(d.name)
        if key in wt_norms:
            matched[d] = wt_norms[key]
    return matched


def _parse_timestamp(raw: str) -> datetime | None:
    """Parse top-level ISO-8601 'Z' timestamp -> local-aware datetime."""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ)


def extract_events(jsonl_path: Path, target_date) -> list[dict]:
    """Yesterday's conversational events, filtered by in-event timestamp (local)."""
    events: list[dict] = []
    try:
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") not in CONVERSATIONAL_TYPES:
                    continue
                ts = _parse_timestamp(d.get("timestamp", ""))
                if ts is None or ts.date() != target_date:
                    continue
                events.append(d)
    except OSError:
        pass
    return events


def _user_text(content) -> str:
    """Extract user text from a user event's message.content (str or block list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "\n".join(p for p in parts if p)
    return ""


def digest_session(
    jsonl_path: Path, events: list[dict], worktree_name: str
) -> dict:
    """Reduce a session's events to structured material for LLM narrative."""
    user_msgs: list[str] = []
    conclusions: list[str] = []
    tool_calls: list[dict] = []
    seen_tools: set[tuple] = set()

    for d in events:
        msg = d.get("message", {})
        content = msg.get("content")
        if d.get("type") == "user":
            text = _user_text(content)
            if text:
                user_msgs.append(text)
        elif d.get("type") == "assistant":
            if isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    btype = b.get("type")
                    if btype == "text" and b.get("text", "").strip():
                        conclusions.append(b["text"])
                    elif btype == "tool_use":
                        inp = b.get("input", {}) if isinstance(b.get("input"), dict) else {}
                        target = inp.get("file_path") or inp.get("description") or ""
                        name = b.get("name", "")
                        key = (name, target)
                        if key in seen_tools:
                            continue
                        seen_tools.add(key)
                        tool_calls.append({"name": name, "target": target})

    first_user_msg = user_msgs[0][:200] if user_msgs else ""
    return {
        "worktree": worktree_name,
        "session_id": jsonl_path.stem,
        "first_user_msg": first_user_msg,
        "user_message_count": len(user_msgs),
        "user_messages": user_msgs,
        "tool_calls": tool_calls,
        "conclusions": conclusions,
    }


def resolve_target_date(date_arg: str):
    """Resolve --date ('yesterday' or YYYY-MM-DD) to a local date."""
    if date_arg == "yesterday":
        return (datetime.now(LOCAL_TZ).date() - timedelta(days=1))
    return datetime.strptime(date_arg, "%Y-%m-%d").date()


def aggregate(repo_root: Path, date_arg: str) -> dict:
    target_date = resolve_target_date(date_arg)
    worktrees = git_worktree_paths(repo_root)
    session_dirs = match_session_dirs(worktrees)

    sessions: list[dict] = []
    for session_dir, wt_path in sorted(session_dirs.items()):
        wt_name = wt_path.name if wt_path != repo_root else f"{repo_root.name} (main)"
        for jsonl in sorted(session_dir.glob("*.jsonl")):
            events = extract_events(jsonl, target_date)
            if not events:
                continue
            sessions.append(digest_session(jsonl, events, wt_name))

    return {
        "date": target_date.isoformat(),
        "repo": repo_root.name,
        "worktrees": [p.name for p in worktrees],
        "session_dirs_matched": len(session_dirs),
        "sessions": sessions,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate yesterday's Claude sessions across a repo's worktrees."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Main repo root (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: stdout).",
    )
    parser.add_argument(
        "--date",
        default="yesterday",
        help="Target date: 'yesterday' (default) or YYYY-MM-DD.",
    )
    args = parser.parse_args()

    repo_root = args.project_root.resolve()
    result = aggregate(repo_root, args.date)
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        print(
            f"Written to {args.output} "
            f"({len(result['sessions'])} sessions across "
            f"{len(result['worktrees'])} worktrees, date={result['date']})"
        )
    else:
        print(output_json)


if __name__ == "__main__":
    main()
