"""Tests for skills/memory-audit/scripts/memory_telemetry.py (AIR-40 S1).

TDD for normalized write/read events: real SQLite + JSONL fixtures driven
through the CLI via subprocess. No DB-driver mocks. Output must stay outside
sources. Scope is S1 (events + coverage); ranking projection is S2.
"""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
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


def _report_of(out: Path):
    return json.loads(out.read_text())["report"]


def test_s2_projection_counts_top_and_alias_merge(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "alpha.md")
    write_entry(pool, "beta.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            (
                "p1",
                "s1",
                1787000000000,
                tool_part(
                    "Write", str(pool / "alpha.md"), call_id="c1", content="x" * 10
                ),
            ),
            (
                "p2",
                "s1",
                1787000001000,
                tool_part(
                    "Edit", str(pool / "alpha.md"), call_id="c2", content="y" * 5
                ),
            ),
            (
                "p3",
                "s1",
                1787000002000,
                tool_part("Write", str(pool / "beta.md"), call_id="c3", status="error"),
            ),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = _report_of(out)
    assert rep["counts"]["successful"] == 2
    assert rep["counts"]["errors"] == 1
    top_e = {e["entry"]: e for e in rep["top_entries"]}
    assert "alpha.md" in top_e
    assert top_e["alpha.md"]["successful_writes"] == 2, "same-entry events merge"
    assert top_e["alpha.md"]["payload_chars"] == 15
    top_a = {a["actor"]: a for a in rep["top_actors"]}
    assert top_a["s1"]["successful_writes"] == 2
    assert rep["net_file_delta"]["value"] is None
    assert rep["net_file_delta"]["reason"]


def test_s2_reads_excluded_from_write_projection(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "r.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s7", None, None)],
        parts=[
            (
                "p1",
                "s7",
                1787000000000,
                tool_part("Read", str(pool / "r.md"), call_id="c1"),
            ),
            (
                "p2",
                "s7",
                1787000001000,
                tool_part("Write", str(pool / "r.md"), call_id="c2"),
            ),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = _report_of(out)
    assert rep["counts"]["successful"] == 1, "Read events are AIR-41 scope, not writes"
    assert rep["top_entries"] == [
        {
            "entry": "r.md",
            "successful_writes": 1,
            "payload_chars": len("hello world"),
        }
    ]


def test_s2_large_payload_flow_not_stock(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "big.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s2", None, None)],
        parts=[
            (
                "p1",
                "s2",
                1787000000000,
                tool_part(
                    "Edit", str(pool / "big.md"), call_id="c9", content="z" * 900
                ),
            ),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = _report_of(out)
    assert rep["top_entries"][0]["payload_chars"] == 900
    assert rep["net_file_delta"]["value"] is None


def test_s2_index_delta_first_run_baseline_created(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "one.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s3", None, None)],
        parts=[
            (
                "p1",
                "s3",
                1787000000000,
                tool_part("Write", str(pool / "one.md"), call_id="c1"),
            )
        ],
    )
    bdir = tmp_path / "base"
    r, out = run_writes(pool, tmp_path, zdb=zdb, extra=["--baseline-dir", str(bdir)])
    assert r.returncode == 0
    rep = _report_of(out)
    idx = rep["index_delta"]
    assert idx["value"] is None
    assert idx["reason"]
    assert idx.get("baseline_written")
    assert Path(idx["baseline_written"][0]).is_file()


def test_s2_index_delta_second_run_body_only_zero(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "one.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s4", None, None)],
        parts=[
            (
                "p1",
                "s4",
                1787000000000,
                tool_part("Write", str(pool / "one.md"), call_id="c1"),
            )
        ],
    )
    bdir = tmp_path / "base"
    r, _ = run_writes(pool, tmp_path, zdb=zdb, extra=["--baseline-dir", str(bdir)])
    assert r.returncode == 0
    (pool / "one.md").write_text(
        "---\nname: one.md\n---\n\nmuch longer body only\n", encoding="utf-8"
    )
    r2, out2 = run_writes(pool, tmp_path, zdb=zdb, extra=["--baseline-dir", str(bdir)])
    assert r2.returncode == 0
    idx = _report_of(out2)["index_delta"]
    assert idx["value"] is not None
    assert idx["value"]["index_chars"] == 0
    assert idx["value"]["index_lines"] == 0


def test_s2_index_delta_generator_mismatch_incomparable(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "one.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s5", None, None)],
        parts=[
            (
                "p1",
                "s5",
                1787000000000,
                tool_part("Write", str(pool / "one.md"), call_id="c1"),
            )
        ],
    )
    bdir = tmp_path / "base"
    bdir.mkdir()
    key = str(pool.resolve()).replace("/", "_")
    (bdir / f"{key}.json").write_text(
        json.dumps({"generator_schema": 999, "index_chars": 5, "index_lines": 1}),
        encoding="utf-8",
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb, extra=["--baseline-dir", str(bdir)])
    assert r.returncode == 0
    idx = _report_of(out)["index_delta"]
    assert idx["value"] is None
    assert "incomparable" in (idx["reason"] or "")


def test_s2_deleted_entry_history_kept_separate_from_inventory(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    gone = pool / "gone.md"
    gone.write_text("---\nname: gone.md\n---\nbody", encoding="utf-8")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s6", None, None)],
        parts=[
            ("p1", "s6", 1787000000000, tool_part("Write", str(gone), call_id="c1"))
        ],
    )
    gone.unlink()
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = _report_of(out)
    names = {e["entry"] for e in rep["top_entries"]}
    assert "gone.md" in names, "history events kept in ranking"
    inv = rep.get("current_inventory") or {}
    assert "gone.md" not in {
        p.get("entry") for p in inv.get("entries", []) if isinstance(p, dict)
    }


def test_s2_f3_deterministic_timestamp_and_empty_none(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "t.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("sa", None, None)],
        parts=[
            (
                "p1",
                "sa",
                1787000000000,
                tool_part("Write", str(pool / "t.md"), call_id="c1"),
            ),
            (
                "p2",
                "sa",
                1787000005000,
                tool_part("Edit", str(pool / "t.md"), call_id="c2"),
            ),
        ],
    )
    r1, o1 = run_writes(pool, tmp_path, zdb=zdb)
    r2, _ = run_writes(
        pool, tmp_path, zdb=zdb, extra=["--output", str(tmp_path / "r2.json")]
    )
    assert r1.returncode == 0 and r2.returncode == 0
    rep1, rep2 = _report_of(o1), _report_of(tmp_path / "r2.json")
    assert json.dumps(rep1, sort_keys=True) == json.dumps(rep2, sort_keys=True)
    assert rep1["inventory_timestamp"] == "2026-08-17T20:53:25+00:00"
    r3, _ = run_writes(
        pool,
        tmp_path,
        zdb=zdb,
        extra=[
            "--since",
            "2026-08-20T00:00:00+00:00",
            "--until",
            "2026-08-21T00:00:00+00:00",
            "--output",
            str(tmp_path / "r3.json"),
        ],
    )
    assert r3.returncode == 0
    assert _report_of(tmp_path / "r3.json")["inventory_timestamp"] is None


def test_s2_f4_fork_copy_folded_in_projection(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "f.md")
    zdb = tmp_path / "z.db"
    op = tool_part("Write", str(pool / "f.md"), call_id="co")
    op_copy = tool_part("Write", str(pool / "f.md"), call_id="cc")
    make_zdb(
        zdb,
        sessions=[("sp", None, None), ("sf", "sp", "side")],
        parts=[
            ("po", "sp", 1787000002000, op),
            ("pc", "sf", 1787000003000, op_copy),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = _report_of(out)
    assert rep["counts"]["copies_folded"] == 1
    assert rep["top_entries"] == [
        {
            "entry": "f.md",
            "successful_writes": 1,
            "payload_chars": len("hello world"),
        }
    ], "copy must not double-count in ranking"


def test_s2_f4_same_content_unrelated_sessions_ambiguous(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "u.md")
    zdb = tmp_path / "z.db"
    op = tool_part("Write", str(pool / "u.md"), call_id="c1")
    op2 = tool_part("Write", str(pool / "u.md"), call_id="c2")
    make_zdb(
        zdb,
        sessions=[("sx", None, None), ("sy", None, None)],
        parts=[
            ("px", "sx", 1787000000000, op),
            ("py", "sy", 1787000000000, op2),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = _report_of(out)
    assert rep["counts"]["ambiguous"] >= 1
    assert rep["counts"]["successful"] == 2


def test_s2_f8_corrupt_baseline_incomparable(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "k.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("sb", None, None)],
        parts=[
            (
                "p1",
                "sb",
                1787000000000,
                tool_part("Write", str(pool / "k.md"), call_id="c1"),
            )
        ],
    )
    bdir = tmp_path / "b"
    bdir.mkdir()
    key = str(pool.resolve()).replace("/", "_")
    (bdir / f"{key}.json").write_text("{not json", encoding="utf-8")
    r, out = run_writes(pool, tmp_path, zdb=zdb, extra=["--baseline-dir", str(bdir)])
    assert r.returncode == 0
    idx = _report_of(out)["index_delta"]
    assert idx["value"] is None
    assert idx["incomparable"]


def test_r1_output_protection_relative_and_symlink(tmp_path):
    """R1: source protection must compare canonical paths, not raw strings."""
    import sqlite3 as sq

    db = tmp_path / "src.sqlite"
    con = sq.connect(db)
    con.execute(
        "CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT, task_type TEXT)"
    )
    con.execute(
        "CREATE TABLE part (id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT)"
    )
    con.commit()
    con.close()
    before = db.read_bytes()
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "e.md").write_text("---\nname: e.md\n---\nbody\n", encoding="utf-8")

    # relative path pointing at the same file as a source db
    rel = db.relative_to(tmp_path)
    r, _ = run_writes(pool, tmp_path, zdb=rel, extra=["--output", str(rel)])
    assert r.returncode == 2, "relative same-file output must be refused"
    assert db.read_bytes() == before, "refusal must leave the source untouched"

    # symlink alias pointing at the same file
    link = tmp_path / "alias.sqlite"
    link.symlink_to(db)
    r2, _ = run_writes(pool, tmp_path, zdb=db, extra=["--output", str(link)])
    assert r2.returncode == 2, "symlink alias output must be refused"
    assert db.read_bytes() == before


def test_r1b_baseline_dir_inside_pool_refused(tmp_path):
    """R1: --baseline-dir inside a pool/source must be refused."""
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "b.md").write_text("---\nname: b.md\n---\nbody\n", encoding="utf-8")
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, _ = run_writes(
        pool,
        tmp_path,
        zdb=zdb,
        extra=["--baseline-dir", str(pool / "baselines")],
    )
    assert r.returncode == 2, "baseline dir inside the pool must be refused"
    assert not (pool / "baselines").exists(), "no snapshot written into the pool"


def test_r2_operation_window_filters_events(tmp_path):
    """R2: events enter by operation time when present, record as fallback."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "w.md")
    inside = tool_part(
        "Edit",
        str(pool / "w.md"),
        op_start="2026-09-01T10:00:00+00:00",
        op_end="2026-09-01T10:00:05+00:00",
        call_id="op_in",
    )
    # record 08-20 (inside SINCE..UNTIL) but operation 2026-07-15 (outside)
    outside = tool_part(
        "Edit",
        str(pool / "w.md"),
        op_start="2026-07-15T10:00:00+00:00",
        op_end="2026-07-15T10:00:05+00:00",
        call_id="op_out",
    )
    from datetime import datetime

    ts_in = int(datetime(2026, 8, 20, tzinfo=UTC).timestamp() * 1000)
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            ("p_out", "s1", ts_in, outside),
            # record far before window; operation inside window
            ("p_in", "s1", 1783000000000, inside),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    ids = {e["id"] for e in rep["events"]}
    assert "p_in" in ids, (
        "operation inside window must be included even if record is outside"
    )
    assert "p_out" not in ids, (
        "record inside window but operation outside must be excluded"
    )


def test_r3_malformed_partial(tmp_path):
    """R3: unreadable/malformed CC data must raise coverage_limited."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "m.md")
    cc_root = tmp_path / "cc"
    cc_root.mkdir()
    (cc_root / "bad.jsonl").write_text("{not json}\n", encoding="utf-8")
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    out = tmp_path / "reads.json"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "reads",
        "--pool",
        str(pool),
        "--zcode-db",
        str(zdb),
        "--cc-root",
        str(cc_root),
        "--since",
        SINCE,
        "--until",
        UNTIL,
        "--output",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    assert rep["coverage"]["claude"]["malformed"] >= 1
    assert rep["coverage"]["partial"] is True, (
        "malformed lines mean incomplete observation"
    )
    assert rep["candidates"]["coverage_limited"] is True


def test_r4_cross_pool_basename_collision_fails(tmp_path):
    """R4: two pools sharing an entry basename must fail loud, not blend."""
    p1 = tmp_path / "p1"
    p2 = tmp_path / "p2"
    for p in (p1, p2):
        p.mkdir()
        (p / "note.md").write_text("---\nname: note.md\n---\nbody\n", encoding="utf-8")
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    out = tmp_path / "reads.json"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "reads",
            "--pool",
            str(p1),
            "--pool",
            str(p2),
            "--zcode-db",
            str(zdb),
            "--since",
            SINCE,
            "--until",
            UNTIL,
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2, "cross-pool basename collision must fail"


def test_f2_alias_dedup_and_second_pool_refused(tmp_path):
    """F2: aliases dedup to one pool; a second distinct pool is refused."""
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "n.md").write_text("---\nname: n.md\n---\nbody\n", encoding="utf-8")
    alias = tmp_path / "alias"
    alias.symlink_to(pool)
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_writes(pool, tmp_path, zdb=zdb, extra=["--pool", str(alias)])
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert len(rep["report"]["current_inventory"]["entries"]) == 1, (
        "same-pool alias must dedup, not double-count entries"
    )
    assert rep["coverage"]["pools"] == [str(pool.resolve())]

    other = tmp_path / "other"
    other.mkdir()
    (other / "x.md").write_text("---\nname: x.md\n---\nbody\n", encoding="utf-8")
    r2, _ = run_writes(pool, tmp_path, zdb=zdb, extra=["--pool", str(other)])
    assert r2.returncode == 2, "a second distinct pool must be refused"


def test_f1_narrow_window_long_drift(tmp_path):
    """F1: selection must follow the operation clock, not a fixed margin."""
    from datetime import UTC, datetime

    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "w.md")
    op = "2026-09-01T10:00:00+00:00"
    part = tool_part("Write", str(pool / "w.md"), op_start=op, op_end=op, call_id="c1")
    record_ms = int(datetime(2026, 9, 1, 9, 59, 58, tzinfo=UTC).timestamp() * 1000)
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[("s1", None, None)], parts=[("p1", "s1", record_ms, part)])
    r, out = run_writes(
        pool,
        tmp_path,
        zdb=zdb,
        extra=[
            "--since",
            "2026-09-01T10:00:00+00:00",
            "--until",
            "2026-09-01T10:00:01+00:00",
        ],
    )
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert rep["report"]["counts"]["successful"] == 1, (
        "1s window with 2s record/op drift: operation clock must still admit the event"
    )


def test_f3_missing_time_no_confirmed_copy(tmp_path):
    """F3: missing operation times must surface ambiguity, never a fold."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "w.md")
    base = tool_part("Write", str(pool / "w.md"), call_id="c1")
    child = tool_part("Write", str(pool / "w.md"), call_id="c2")
    del base["state"]["time"]
    del child["state"]["time"]
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("sp", None, None), ("sc", "sp", None)],
        parts=[
            ("p1", "sp", 1787000000000, base),
            ("p2", "sc", 1787000000500, child),
        ],
    )
    r, out = run_writes(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    assert rep["aliases"] == [], "no time evidence — must not confirm a copy"
    assert rep["report"]["counts"]["ambiguous"] == 1
    assert rep["report"]["counts"]["successful"] == 2


def test_n1_subsecond_iso_window_boundaries(tmp_path):
    """N1: SQLite datetime() truncates subseconds — SQL preselection must
    stay a superset of the Python half-open window judgment."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "w.md")
    since = "2026-09-01T10:00:00.250000+00:00"
    until = "2026-09-01T10:00:00.750000+00:00"

    def run_with(op):
        part = tool_part(
            "Write", str(pool / "w.md"), op_start=op, op_end=op, call_id="c"
        )
        zdb = tmp_path / f"z-{op.split('.')[1][:6]}.db"
        make_zdb(
            zdb,
            sessions=[("s1", None, None)],
            parts=[("p1", "s1", 1787000000000, part)],
        )
        r, out = run_writes(
            pool, tmp_path, zdb=zdb, extra=["--since", since, "--until", until]
        )
        assert r.returncode == 0, r.stderr
        return json.loads(out.read_text())["report"]["counts"]["successful"]

    # inside the subsecond window
    assert run_with("2026-09-01T10:00:00.500000+00:00") == 1, (
        "subsecond op inside window must be admitted (datetime() truncation)"
    )
    # exactly at until — half-open window excludes it
    assert run_with("2026-09-01T10:00:00.750000+00:00") == 0, (
        "op == until must stay excluded (Python half-open precision)"
    )
    # just below the lower bound, same second as since — SQL may fetch, Python excludes
    assert run_with("2026-09-01T10:00:00.100000+00:00") == 0


# ---- AIR-49 P2: decay subcommand (usage-driven candidates) ----


def _epoch(year: int, month: int, day: int) -> int:
    return int(datetime(year, month, day, tzinfo=UTC).timestamp())


def write_entry_ranked(pool: Path, name: str, rank=None, mtime_epoch=None) -> Path:
    """Entry fixture with optional frontmatter rank and backdated mtime."""
    lines = [f"name: {name}", "originSessionId: s"]
    if rank:
        lines.append(f"rank: {rank}")
    p = pool / name
    p.write_text("---\n" + "\n".join(lines) + "\n---\n\nbody\n", encoding="utf-8")
    if mtime_epoch is not None:
        os.utime(p, (mtime_epoch, mtime_epoch))
    return p


def read_part(file_path, op_start, call_id):
    return tool_part(
        "Read", file_path, op_start=op_start, op_end=op_start, call_id=call_id
    )


def run_decay(pool, tmp_path, zdb=None, cc_root=None, extra=()):
    """Decay has no --output flag: it always writes the fixed pair
    <pool>/_decay-candidates.{json,md} (EP F3)."""
    cmd = [
        sys.executable,
        str(SCRIPT),
        "decay",
        "--pool",
        str(pool),
        "--since",
        SINCE,
        "--until",
        UNTIL,
    ]
    if zdb:
        cmd += ["--zcode-db", str(zdb)]
    if cc_root:
        cmd += ["--cc-root", str(cc_root)]
    cmd += list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_decay_zero_read_unused_and_exempt_notes(tmp_path):
    """Rule 1: zero in-window reads and not exempted -> unused; exempted
    zero-read entries (hot rank / recent-30d mtime) go to the notes section,
    never to candidates. Aggregate rows carry the EP per-entry fields."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry_ranked(pool, "unused.md", rank="core", mtime_epoch=_epoch(2026, 7, 1))
    write_entry_ranked(pool, "hot-zero.md", rank="hot", mtime_epoch=_epoch(2026, 7, 1))
    write_entry_ranked(
        pool, "fresh-zero.md", rank="core", mtime_epoch=_epoch(2026, 8, 20)
    )
    write_entry_ranked(pool, "read.md", rank="core", mtime_epoch=_epoch(2026, 7, 1))
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            (
                "p1",
                "s1",
                1787000000000,
                read_part(str(pool / "read.md"), "2026-08-15T00:00:00+00:00", "c1"),
            )
        ],
    )
    r = run_decay(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads((pool / "_decay-candidates.json").read_text())
    assert rep["type"] == "decay_candidates"
    assert [c["entry"] for c in rep["candidates"]["unused"]] == ["unused.md"]
    exempted = {c["entry"]: c for c in rep["candidates"]["exempted_zero_read"]}
    assert set(exempted) == {"hot-zero.md", "fresh-zero.md"}
    assert exempted["hot-zero.md"]["exemptions"]["hot"] is True
    assert exempted["fresh-zero.md"]["exemptions"]["recent_30d"] is True
    u = rep["candidates"]["unused"][0]
    for field in ("entry", "rank", "mtime", "reads_count", "last_read_ts", "exempted"):
        assert field in u, f"EP aggregate field missing: {field}"
    assert u["reads_count"] == 0
    assert u["last_read_ts"] is None
    assert u["exempted"] is False
    assert [c["entry"] for c in rep["candidates"]["healthy"]] == ["read.md"]
    assert rep["counts"]["entries"] == 4


def test_decay_boundary_days_29_30_31(tmp_path):
    """Rule 3 boundary: last_read exactly 30 days before window end stays
    healthy (strict >); 31 days decays; flag --max-unused-days is honored."""
    pool = tmp_path / "pool"
    pool.mkdir()
    cases = {
        "d29.md": "2026-08-10T00:00:00+00:00",
        "d30.md": "2026-08-09T00:00:00+00:00",
        "d31.md": "2026-08-08T00:00:00+00:00",
    }
    parts = []
    for i, (name, ts) in enumerate(cases.items()):
        write_entry_ranked(pool, name, rank="core", mtime_epoch=_epoch(2026, 7, 1))
        parts.append(
            (f"p{i}", "s1", 1787000000000 + i, read_part(str(pool / name), ts, f"c{i}"))
        )
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[("s1", None, None)], parts=parts)
    r = run_decay(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads((pool / "_decay-candidates.json").read_text())
    assert [c["entry"] for c in rep["candidates"]["decaying"]] == ["d31.md"]
    assert {c["entry"] for c in rep["candidates"]["healthy"]} == {"d29.md", "d30.md"}
    r2 = run_decay(pool, tmp_path, zdb=zdb, extra=["--max-unused-days", "31"])
    assert r2.returncode == 0, r2.stderr
    rep2 = json.loads((pool / "_decay-candidates.json").read_text())
    assert rep2["candidates"]["decaying"] == [], "31d must stay healthy at flag=31"
    assert rep2["parameters"]["max_unused_days"] == 31


def test_decay_usage_ordering_and_rank_promotion(tmp_path):
    """Rule 2: remaining entries sort by reads asc then last_read asc.
    Cold entries with heavy in-window reads surface as promotion candidates."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry_ranked(
        pool, "cold-busy.md", rank="cold", mtime_epoch=_epoch(2026, 7, 1)
    )
    write_entry_ranked(
        pool, "cold-stale.md", rank="cold", mtime_epoch=_epoch(2026, 7, 1)
    )
    write_entry_ranked(
        pool, "core-active.md", rank="core", mtime_epoch=_epoch(2026, 7, 1)
    )
    read_specs = [
        ("cold-stale.md", "2026-08-01T00:00:00+00:00"),  # 38d before UNTIL
        ("core-active.md", "2026-09-01T00:00:00+00:00"),
        ("core-active.md", "2026-09-02T00:00:00+00:00"),
        ("core-active.md", "2026-09-03T00:00:00+00:00"),
        ("core-active.md", "2026-09-04T00:00:00+00:00"),
        ("core-active.md", "2026-09-05T00:00:00+00:00"),
        ("cold-busy.md", "2026-08-20T00:00:00+00:00"),
        ("cold-busy.md", "2026-08-21T00:00:00+00:00"),
        ("cold-busy.md", "2026-08-22T00:00:00+00:00"),
    ]
    parts = [
        (f"p{i}", "s1", 1787000000000 + i, read_part(str(pool / name), ts, f"c{i}"))
        for i, (name, ts) in enumerate(read_specs)
    ]
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[("s1", None, None)], parts=parts)
    r = run_decay(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads((pool / "_decay-candidates.json").read_text())
    assert [c["entry"] for c in rep["candidates"]["decaying"]] == ["cold-stale.md"]
    healthy = [c["entry"] for c in rep["candidates"]["healthy"]]
    assert healthy == ["cold-busy.md", "core-active.md"], "usage asc ordering"
    promo = [c["entry"] for c in rep["candidates"]["rank_promotion"]]
    assert promo == ["cold-busy.md"], "cold with >=3 in-window reads"
    r2 = run_decay(pool, tmp_path, zdb=zdb, extra=["--promotion-min-reads", "4"])
    assert r2.returncode == 0, r2.stderr
    rep2 = json.loads((pool / "_decay-candidates.json").read_text())
    assert rep2["candidates"]["rank_promotion"] == []
    # core-rank heavy reader must never appear in promotion
    assert "core-active.md" not in promo


def test_decay_empty_pool(tmp_path):
    """Empty pool: success, all candidate lists empty, both files written."""
    pool = tmp_path / "pool"
    pool.mkdir()
    zdb = tmp_path / "z.db"
    make_zdb(zdb)
    r = run_decay(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads((pool / "_decay-candidates.json").read_text())
    assert rep["counts"]["entries"] == 0
    for section in rep["candidates"].values():
        assert section == []
    md = (pool / "_decay-candidates.md").read_text(encoding="utf-8")
    assert "Coverage" in md


def test_decay_alias_dedup_and_multi_pool_refused(tmp_path):
    """zcode symlink <-> CC real pool alias dedups to one pool (output lands
    in the resolved real pool); a second distinct pool is refused."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry_ranked(pool, "n.md", rank="core", mtime_epoch=_epoch(2026, 7, 1))
    alias = tmp_path / "alias"
    alias.symlink_to(pool)
    zdb = tmp_path / "z.db"
    make_zdb(zdb)
    cmd = [
        sys.executable,
        str(SCRIPT),
        "decay",
        "--pool",
        str(pool),
        "--pool",
        str(alias),
        "--since",
        SINCE,
        "--until",
        UNTIL,
        "--zcode-db",
        str(zdb),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
    rep = json.loads((pool.resolve() / "_decay-candidates.json").read_text())
    assert rep["counts"]["entries"] == 1, "same-pool alias must dedup"
    assert rep["pool"] == str(pool.resolve())
    other = tmp_path / "other"
    other.mkdir()
    write_entry_ranked(other, "x.md", rank="core", mtime_epoch=_epoch(2026, 7, 1))
    cmd2 = [
        sys.executable,
        str(SCRIPT),
        "decay",
        "--pool",
        str(pool),
        "--pool",
        str(other),
        "--since",
        SINCE,
        "--until",
        UNTIL,
        "--zcode-db",
        str(zdb),
    ]
    r2 = subprocess.run(cmd2, capture_output=True, text=True, check=False)
    assert r2.returncode == 2, "a second distinct pool must be refused"


def test_decay_md_json_shape_fixed_path_deterministic(tmp_path):
    """Output pair lands at the fixed underscore-prefixed path (invisible to
    the inventory projection), md carries the four sections + coverage
    statement + 'candidates are not verdicts', rerun is deterministic."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry_ranked(pool, "z-zero.md", rank="core", mtime_epoch=_epoch(2026, 7, 1))
    zdb = tmp_path / "z.db"
    make_zdb(zdb)
    (tmp_path / "cc-empty").mkdir()
    r1 = run_decay(pool, tmp_path, zdb=zdb, cc_root=tmp_path / "cc-empty")
    assert r1.returncode == 0, r1.stderr
    json_path = pool / "_decay-candidates.json"
    md_path = pool / "_decay-candidates.md"
    assert json_path.is_file() and md_path.is_file()
    raw1 = json_path.read_text()
    rep1 = json.loads(raw1)
    md1 = md_path.read_text(encoding="utf-8")
    for kw in (
        "Unused",
        "豁免註記",
        "衰減候選",
        "Rank 升級候選",
        "Coverage 聲明",
        "候選非判決",
        "muse",
        "codex",
    ):
        assert kw in md1, f"md section/statement missing: {kw}"
    assert rep1["coverage"]["partial"] is not None
    r2 = run_decay(pool, tmp_path, zdb=zdb, cc_root=tmp_path / "cc-empty")
    assert r2.returncode == 0, r2.stderr
    assert json_path.read_text() == raw1, "rerun must be deterministic"
    assert md_path.read_text(encoding="utf-8") == md1
    # decay artifacts are underscore-prefixed: next run's inventory still N
    assert rep1["counts"]["entries"] == 1


def test_decay_fixed_output_source_protection(tmp_path):
    """F4: a pool resolving inside a source tree (cc-root) must be refused —
    R1 canonical-path semantics applied to the decay fixed outputs; source
    bytes stay identical and no candidates pair is written."""
    cc_root = tmp_path / "transcripts"
    pool = cc_root / "pool-inside-source"
    pool.mkdir(parents=True)
    write_entry_ranked(pool, "entry-a.md")
    before = sorted(p.read_bytes() for p in cc_root.rglob("*") if p.is_file())
    r = run_decay(pool, tmp_path, cc_root=cc_root)
    assert r.returncode != 0
    assert "decay fixed output inside sources refused" in r.stderr + r.stdout
    assert not (pool / "_decay-candidates.json").exists()
    after = sorted(p.read_bytes() for p in cc_root.rglob("*") if p.is_file())
    assert before == after


def test_date_only_window_strings_accepted(tmp_path):
    """date-only --since/--until（SKILL 呼叫慣例形態）不得與 epoch-derived
    aware 事件比較時 TypeError——naive 一律視為 UTC（09-09 回測實證）。"""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry_ranked(pool, "entry-a.md")
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "decay",
            "--pool",
            str(pool),
            "--since",
            "2026-09-04",
            "--until",
            "2026-09-08",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "[OK] entries=1" in r.stdout + r.stderr


def test_decay_fixed_output_symlink_refused(tmp_path):
    """R3: a symlinked fixed decay output (pointing at a pool entry) must be
    refused — write_text would follow it and clobber the entry bytes."""
    pool = tmp_path / "pool"
    pool.mkdir()
    entry = write_entry_ranked(pool, "entry-a.md")
    raw = entry.read_bytes()
    (pool / "_decay-candidates.md").symlink_to(entry)
    r = run_decay(pool, tmp_path, cc_root=tmp_path / "cc-empty")
    assert r.returncode != 0
    assert "decay fixed output is a symlink, refused" in r.stderr + r.stdout
    assert entry.read_bytes() == raw
