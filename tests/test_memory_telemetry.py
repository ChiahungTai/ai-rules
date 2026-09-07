"""Tests for skills/memory-audit/scripts/memory_telemetry.py (AIR-40 S1).

TDD for normalized write/read events: real SQLite + JSONL fixtures driven
through the CLI via subprocess. No DB-driver mocks. Output must stay outside
sources. Scope is S1 (events + coverage); ranking projection is S2.
"""

import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "memory-audit"
    / "scripts"
    / "memory_telemetry.py"
)

SINCE = "2026-08-01T00:00:00+00:00"
UNTIL = "2026-09-08T00:00:00+00:00"


def write_entry(pool: Path, name: str, origin: str = "sess_owner") -> Path:
    p = pool / name
    p.write_text(
        f"---\nname: {name}\noriginSessionId: {origin}\n---\n\nbody\n",
        encoding="utf-8",
    )
    return p


def make_zdb(
    path: Path,
    sessions=(),
    parts=(),
):
    """sessions: (id, parent, task). parts: (id, session, ts_ms, data_dict)."""
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT, task_type TEXT)"
    )
    db.execute(
        "CREATE TABLE part (id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT)"
    )
    for sid, parent, task in sessions:
        db.execute("INSERT INTO session VALUES (?,?,?)", (sid, parent, task))
    for pid, sid, ts, data in parts:
        db.execute(
            "INSERT INTO part VALUES (?,?,?,?)", (pid, sid, ts, json.dumps(data))
        )
    db.commit()
    db.close()


def tool_part(
    tool,
    file_path,
    status="completed",
    op_start="2026-09-01T10:00:00+00:00",
    op_end="2026-09-01T10:00:05+00:00",
    call_id="call_1",
    content="hello world",
    extra_input=None,
):
    inp = {"file_path": file_path, "content": content}
    inp.update(extra_input or {})
    return {
        "type": "tool",
        "tool": tool,
        "callID": call_id,
        "state": {
            "input": inp,
            "status": status,
            "time": {"start": op_start, "end": op_end},
            "metadata": {},
        },
    }


def run_writes(pool, tmp_path, zdb=None, cc_root=None, extra=()):
    out = tmp_path / "report.json"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "writes",
        "--pool",
        str(pool),
        "--since",
        SINCE,
        "--until",
        UNTIL,
        "--output",
        str(out),
    ]
    if zdb:
        cmd += ["--zcode-db", str(zdb)]
    if cc_root:
        cmd += ["--cc-root", str(cc_root)]
    cmd += list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, check=False), out


def test_completed_write_full_provenance(tmp_path):
    """W1: completed Write carries actor/session/id/time/path/payload."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "a-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[
            (
                "part_1",
                "sess_main",
                1787000000000,
                tool_part("Write", str(target), call_id="call_w1"),
            )
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    evs = [e for e in rep["events"] if e["status"] == "completed"]
    assert len(evs) == 1
    e = evs[0]
    assert (e["session"], e["tool"]) == ("sess_main", "Write")
    assert e["canonical_path"].endswith("a-note.md")
    assert e["payload_chars"] == len("hello world")
    assert e["operation_start"] == "2026-09-01T10:00:00+00:00"
    assert e["source_ref"]


def test_error_and_unmatched_separated(tmp_path):
    """W2: error Write and result-less CC tool_use never count as success."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "b-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[
            (
                "part_e",
                "sess_main",
                1787000001000,
                tool_part("Write", str(target), status="error", call_id="call_e"),
            )
        ],
    )
    cc_root = tmp_path / "cc"
    cc_root.mkdir()
    (cc_root / "s1.jsonl").write_text(
        json.dumps(
            {
                "sessionId": "cc_1",
                "timestamp": "2026-09-01T11:00:00Z",
                "cwd": str(tmp_path),
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "tu_1",
                            "name": "Edit",
                            "input": {"file_path": str(target), "new_string": "x"},
                        }
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb, cc_root=cc_root)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert [e for e in rep["events"] if e["status"] == "completed"] == []
    by_status = {e["status"] for e in rep["events"]}
    assert {"error", "unmatched"} <= by_status


def test_fork_copy_folded_with_alias(tmp_path):
    """W3: fork copy (same input+op time, ancestor present) folds to one canonical."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "c-note.md")
    zdb = tmp_path / "z.sqlite"
    op = tool_part("Write", str(target), call_id="call_orig")
    op_copy = tool_part("Write", str(target), call_id="call_changed")
    make_zdb(
        zdb,
        sessions=[
            ("sess_parent", None, "interactive"),
            ("sess_fork", "sess_parent", "side_chat"),
        ],
        parts=[
            ("part_o", "sess_parent", 1787000002000, op),
            ("part_c", "sess_fork", 1787000003000, op_copy),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    canon = [e for e in rep["events"] if e.get("copy_of") is None]
    copies = [e for e in rep["events"] if e.get("copy_of")]
    assert len(canon) == 1 and len(copies) == 1
    assert copies[0]["copy_of"] == canon[0]["id"]
    assert rep["aliases"], "folded copy must leave an alias record"


def test_fork_new_and_retimed_content_independent(tmp_path):
    """W4: fork-new content and same-content-different-time stay independent."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "d-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[
            ("sess_parent", None, "interactive"),
            ("sess_fork", "sess_parent", "side_chat"),
        ],
        parts=[
            (
                "part_o",
                "sess_parent",
                1787000004000,
                tool_part("Write", str(target), call_id="call_o"),
            ),
            (
                "part_n",
                "sess_fork",
                1787000005000,
                tool_part(
                    "Write",
                    str(target),
                    call_id="call_n",
                    content="brand new",
                    op_start="2026-09-01T12:00:00+00:00",
                    op_end="2026-09-01T12:00:05+00:00",
                ),
            ),
            (
                "part_r",
                "sess_fork",
                1787000006000,
                tool_part(
                    "Write",
                    str(target),
                    call_id="call_r",
                    op_start="2026-09-01T13:00:00+00:00",
                    op_end="2026-09-01T13:00:05+00:00",
                ),
            ),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    canon = [e for e in rep["events"] if e.get("copy_of") is None]
    assert len(canon) == 3


def test_missing_parent_actor_unknown(tmp_path):
    """W5: event whose session row is gone lands in unknown, off certain lists."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "e-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[],
        parts=[("part_x", "sess_gone", 1787000007000, tool_part("Write", str(target)))],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert len(rep["events"]) == 1
    assert rep["events"][0]["actor"] == "unknown"
    assert rep["unknown"], "unknown attribution must be listed separately"


def test_malformed_and_unknown_shape_diagnosed(tmp_path):
    """W6: bad JSONL + unknown part shape → coverage diagnostics, no fake success."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "f-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[("part_u", "sess_main", 1787000008000, {"type": "tool", "weird": 1})],
    )
    cc_root = tmp_path / "cc"
    cc_root.mkdir()
    (cc_root / "bad.jsonl").write_text(
        '{"sessionId": "cc_1", broken\n', encoding="utf-8"
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb, cc_root=cc_root)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert [e for e in rep["events"] if e["status"] == "completed"] == []
    cov = json.dumps(rep["coverage"])
    assert "malformed" in cov or "unknown" in cov


def test_missing_source_fails_loud(tmp_path):
    """W6b: unreadable source DB fails loud instead of empty success."""
    pool = tmp_path / "pool"
    pool.mkdir()
    r, _ = run_writes(pool, tmp_path, zdb=tmp_path / "nope.sqlite")
    assert r.returncode != 0


def test_write_without_before_state_delta_unknown(tmp_path):
    """W7: Write with no provable before-state → net delta unknown, not zero."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "g-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[("part_w", "sess_main", 1787000009000, tool_part("Write", str(target)))],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    e = rep["events"][0]
    assert e["prior_known"] is False
    assert e["net_delta"] is None


def test_path_alias_and_relative_resolution(tmp_path):
    """W8: symlinked pool dir and cwd-relative paths normalize to canonical."""
    real_pool = tmp_path / "real"
    real_pool.mkdir()
    target = write_entry(real_pool, "h-note.md")
    pool = tmp_path / "pool"
    pool.symlink_to(real_pool, target_is_directory=True)
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[
            (
                "part_a",
                "sess_main",
                1787000010000,
                tool_part("Write", str(target), call_id="call_a"),
            )
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert rep["events"][0]["canonical_path"] == str(target.resolve())


def test_empty_readable_sources_success_empty(tmp_path):
    """W9: readable-but-empty sources → success with zero events (zero is allowed)."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "i-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(zdb)
    cc_root = tmp_path / "cc"
    cc_root.mkdir()
    r, out = run_writes(pool, tmp_path, zdb=zdb, cc_root=cc_root)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert rep["events"] == []
    assert rep["coverage"]["zcode"]["readable"] is True


def test_rerun_deterministic_sources_intact(tmp_path):
    """W10: same snapshot reruns identically; sources untouched; no output in pool."""
    pool = tmp_path / "pool"
    pool.mkdir()
    target = write_entry(pool, "j-note.md")
    zdb = tmp_path / "z.sqlite"
    make_zdb(
        zdb,
        sessions=[("sess_main", None, "interactive")],
        parts=[("part_1", "sess_main", 1787000011000, tool_part("Write", str(target)))],
    )
    before = hashlib.sha256(zdb.read_bytes()).hexdigest()
    outs = []
    for _ in range(2):
        r, out = run_writes(pool, tmp_path, zdb=zdb)
        assert r.returncode == 0, r.stderr
        outs.append(out.read_text())
    assert outs[0] == outs[1]
    assert hashlib.sha256(zdb.read_bytes()).hexdigest() == before
    assert list(pool.glob("report*.json")) == []
    r, _ = run_writes(
        pool, tmp_path, zdb=zdb, extra=["--output", str(pool / "report.json")]
    )
    assert r.returncode != 0, "output inside sources must be refused"
