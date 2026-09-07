"""Read-only fatal-assumption probe for AIR-40/41; metadata only, no message bodies.

Run with uv run python <this file>. Writes only evidence/telemetry.json beside
the task. Not a production collector; immutable interpretation limits are in EP.
"""

import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path


def main():
    home = Path.home()
    pool = home / ".claude/projects/-Users-ctai-Github-ai-rules/memory"
    stop = datetime.now(UTC)
    start = stop - timedelta(days=90)
    connection = sqlite3.connect(
        f"file:{home}/.zcode/cli/db/db.sqlite?mode=ro", uri=True
    )
    connection.execute("BEGIN")
    bounds = connection.execute(
        "select min(time_created), max(time_created), count(*) from part"
    ).fetchone()
    rows = connection.execute(
        """select p.id,p.session_id,p.time_created,p.data,s.parent_id,s.task_type
        from part p join session s on s.id=p.session_id
        where p.time_created >= ? and p.time_created < ?
        and json_extract(p.data,'$.type')='tool'
        and json_extract(p.data,'$.state.input.file_path') like '%/memory/%'
        order by p.time_created,p.id""",
        (int(start.timestamp() * 1000), int(stop.timestamp() * 1000)),
    ).fetchall()
    connection.close()
    events = []
    for pid, sid, ts, raw, parent, task_type in rows:
        d = json.loads(raw)
        state = d.get("state", {})
        inp = state.get("input") or {}
        path = Path(inp["file_path"]).expanduser().resolve()
        if (
            path.parent != pool.resolve()
            or path.name.startswith("_")
            or path.name == "MEMORY.md"
        ):
            continue
        tool = d.get("tool")
        if tool not in ("Read", "Edit", "Write"):
            continue
        events.append(
            {
                "source": "zcode",
                "id": pid,
                "call_id": d.get("callID"),
                "operation_time": state.get("time"),
                "input_sha256": hashlib.sha256(
                    json.dumps(inp, sort_keys=True).encode()
                ).hexdigest(),
                "session": sid,
                "time": datetime.fromtimestamp(ts / 1000, UTC).isoformat(),
                "entry": path.name,
                "tool": tool,
                "status": state.get("status"),
                "parent": parent,
                "task_type": task_type,
                "payload_chars": len(inp.get("content", inp.get("new_string", ""))),
                "edit_literal_delta": len(inp.get("new_string", ""))
                - len(inp.get("old_string", ""))
                if tool == "Edit"
                else None,
                "replace_all": inp.get("replace_all", False),
                "metadata_keys": list((state.get("metadata") or {}).keys()),
            }
        )
    cc_root = home / ".claude/projects/-Users-ctai-Github-ai-rules"
    cc_files = sorted(cc_root.rglob("*.jsonl"))
    cc_bounds = []
    cc_pending = {}
    cc_results = {}
    cc_bad = 0
    for f in cc_files:
        with f.open() as stream:
            for line_no, line in enumerate(stream, 1):
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    cc_bad += 1
                    continue
                ts = d.get("timestamp")
                if ts:
                    cc_bounds.append(ts)
                blocks = (d.get("message") or {}).get("content", [])
                if not isinstance(blocks, list):
                    continue
                sid = d.get("sessionId", f.stem)
                for b in blocks:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_result":
                        cc_results[(sid, b.get("tool_use_id"))] = (
                            "error" if b.get("is_error") else "completed"
                        )
                    if b.get("type") != "tool_use" or b.get("name") not in (
                        "Read",
                        "Write",
                        "Edit",
                    ):
                        continue
                    inp = b.get("input") or {}
                    rawpath = inp.get("file_path", "")
                    if not rawpath or not ts:
                        continue
                    path = Path(rawpath).expanduser()
                    if not path.is_absolute():
                        path = Path(d.get("cwd", str(cc_root))) / path
                    path = path.resolve()
                    if (
                        path.parent != pool.resolve()
                        or path.name == "MEMORY.md"
                        or path.name.startswith("_")
                    ):
                        continue
                    when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if not start <= when < stop:
                        continue
                    key = (sid, b["id"])
                    cc_pending[key] = {
                        "source": "claude",
                        "id": b["id"],
                        "session": sid,
                        "time": ts,
                        "entry": path.name,
                        "tool": b["name"],
                        "status": "unmatched",
                        "source_file": str(f.relative_to(cc_root)),
                        "line": line_no,
                        "payload_chars": len(
                            inp.get("content", inp.get("new_string", ""))
                        ),
                    }
    for key, event in cc_pending.items():
        event["status"] = cc_results.get(key, "unmatched")
        events.append(event)
    inventory = []
    for f in sorted(pool.glob("*.md")):
        if f.name == "MEMORY.md" or f.name.startswith("_"):
            continue
        content = f.read_text()
        fm = content.split("---", 2)[1] if content.startswith("---") else ""
        origin = re.search(r"^\s*originSessionId:\s*(.+)$", fm, re.MULTILINE)
        related = [
            e for e in events if e["entry"] == f.name and e["status"] == "completed"
        ]
        writes = [e for e in related if e["tool"] in ("Write", "Edit")]
        inventory.append(
            {
                "entry": f.name,
                "current_chars": len(content),
                "mtime": datetime.fromtimestamp(f.stat().st_mtime, UTC).isoformat(),
                "origin": origin.group(1).strip() if origin else None,
                "successful_reads": sum(e["tool"] == "Read" for e in related),
                "writers": sorted({e["session"] for e in writes}),
                "last_writer": max(writes, key=lambda e: e["time"])["session"]
                if writes
                else None,
            }
        )
    top = defaultdict(lambda: {"events": 0, "payload_chars": 0})
    for e in events:
        if e["tool"] in ("Write", "Edit") and e["status"] == "completed":
            v = top[(e["source"], e["session"], e["entry"])]
            v["events"] += 1
            v["payload_chars"] += e["payload_chars"]
    report = {
        "window": {"start": start.isoformat(), "end": stop.isoformat()},
        "zcode_bounds": {
            "first": datetime.fromtimestamp(bounds[0] / 1000, UTC).isoformat(),
            "last": datetime.fromtimestamp(bounds[1] / 1000, UTC).isoformat(),
            "global_parts": bounds[2],
        },
        "cc": {
            "files": len(cc_files),
            "first": min(cc_bounds) if cc_bounds else None,
            "last": max(cc_bounds) if cc_bounds else None,
            "malformed_lines": cc_bad,
            "scope": "ai-rules main transcript directory only; removed worktree dirs not enumerated",
        },
        "counts": dict(
            Counter(f"{e['source']}:{e['tool']}:{e['status']}" for e in events)
        ),
        "top_writes": [
            dict(source=k[0], session=k[1], entry=k[2], **v)
            for k, v in sorted(
                top.items(), key=lambda kv: kv[1]["payload_chars"], reverse=True
            )[:12]
        ],
        "origin_last_writer_mismatch": [
            i
            for i in inventory
            if i["origin"] and i["last_writer"] and i["origin"] != i["last_writer"]
        ],
        "inventory": inventory,
        "events": events,
        "limitations": [
            "Not full 90-day coverage; bounds are observations not retention guarantees.",
            "Main CC directory only; no claim of all worktrees/harnesses.",
            "Read purpose unclassified; audit reads are included.",
            "Payload is not net growth; origin is not operation actor.",
            "Shell/MCP writes and reads not normalized.",
            "Live pool inventory is sampled after DB transaction; not an atomic historical snapshot.",
        ],
    }
    clone_groups = defaultdict(list)
    for e in events:
        if e["source"] == "zcode" and e["status"] == "completed":
            key = (
                e["tool"],
                e["entry"],
                e["input_sha256"],
                json.dumps(e["operation_time"], sort_keys=True),
            )
            clone_groups[key].append(e)
    report["clone_candidate_groups"] = [
        v for v in clone_groups.values() if len({e["session"] for e in v}) > 1
    ]
    report["limitations"].append(
        "Raw counts/top_writes include fork and side-chat copied events; NOT final actor rankings. clone_candidate_groups require lineage adjudication."
    )
    report["origin_mismatch_count"] = len(report["origin_last_writer_mismatch"])
    report["origin_last_writer_mismatch"] = report["origin_last_writer_mismatch"][:3]
    report["clone_candidate_group_count"] = len(report["clone_candidate_groups"])
    report["clone_candidate_groups"] = report["clone_candidate_groups"][:2]
    report["observed_zero_body_read_count"] = sum(
        i["successful_reads"] == 0 for i in inventory
    )
    del report["events"]
    out = Path(__file__).parents[1] / "evidence/telemetry.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {k: report[k] for k in ("zcode_bounds", "cc", "counts", "top_writes")},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(
        f"[OK] inventory={len(inventory)} origin_last_writer_mismatch={report['origin_mismatch_count']} evidence={out}"
    )


if __name__ == "__main__":
    main()
