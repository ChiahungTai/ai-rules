"""AIR-41 S1/S2: body Read observation — coverage-limited candidates.

Reuses AIR-40 fixtures (make_zdb/tool_part/write_entry) via import; the
`reads` subcommand must never turn missing sources into "successfully
observed zero reads" (EP R4/R9).
"""

import json
import subprocess
import sys
from pathlib import Path

from test_memory_telemetry import (
    SINCE,
    UNTIL,
    make_zdb,
    write_entry,
)

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "memory-audit"
    / "scripts"
    / "memory_telemetry.py"
)


def read_part(
    file_path,
    status="completed",
    op_start="2026-09-01T10:00:00+00:00",
    call_id="r1",
    extra_input=None,
):
    inp = {"file_path": file_path}
    inp.update(extra_input or {})
    return {
        "type": "tool",
        "tool": "Read",
        "callID": call_id,
        "state": {
            "input": inp,
            "status": status,
            "time": {"start": op_start, "end": op_start},
            "metadata": {},
        },
    }


def run_reads(pool, tmp_path, zdb=None, cc_root=None, extra=()):
    out = tmp_path / "reads.json"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "reads",
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


def test_r1_body_read_counted_index_read_excluded(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "note.md")
    (pool / "MEMORY.md").write_text("- [note](note.md)\n", encoding="utf-8")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            ("p1", "s1", 1787000000000, read_part(str(pool / "note.md"), call_id="r1")),
            (
                "p2",
                "s1",
                1787000001000,
                read_part(str(pool / "MEMORY.md"), call_id="r2"),
            ),
        ],
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text())
    obs = {o["entry"]: o for o in rep["observations"]}
    assert obs["note.md"]["body_reads"], "successful entry Read counted"
    assert "MEMORY.md" not in obs, "MEMORY.md is the index, not an entry"
    assert obs["note.md"]["zero_body_read"] is False


def test_r2_error_unmatched_not_counted_but_diagnosed(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "e.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            (
                "p1",
                "s1",
                1787000000000,
                read_part(str(pool / "e.md"), status="error", call_id="r1"),
            ),
        ],
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    obs = {o["entry"]: o for o in rep["observations"]}
    assert obs["e.md"]["zero_body_read"] is True
    assert rep["coverage"]["read_errors"] >= 1


def test_r2b_partial_read_counts_as_contact_with_partial_flag(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "p.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            (
                "p1",
                "s1",
                1787000000000,
                read_part(
                    str(pool / "p.md"),
                    call_id="r1",
                    extra_input={"offset": 5, "limit": 3},
                ),
            ),
        ],
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    obs = {o["entry"]: o for o in json.loads(out.read_text())["observations"]}
    reads = obs["p.md"]["body_reads"]
    assert len(reads) == 1
    assert reads[0]["partial"] is True
    assert reads[0]["range"] == {"offset": 5, "limit": 3}


def test_r5_zero_read_candidate_with_mechanical_exemptions(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "cold.md").write_text(
        "---\nname: cold.md\nrank: cold\n---\nbody\n", encoding="utf-8"
    )
    (pool / "hot.md").write_text(
        "---\nname: hot.md\nrank: hot\n---\nbody\n", encoding="utf-8"
    )
    import os

    recent = pool / "recent.md"
    recent.write_text("---\nname: recent.md\n---\nbody\n", encoding="utf-8")
    now = 1787100000.0
    os.utime(recent, (now, now))
    old = 1755000000.0
    os.utime(pool / "cold.md", (old, old))
    os.utime(pool / "hot.md", (old, old))
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[("s1", None, None)], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    cands = {c["entry"]: c for c in rep["candidates"]["no_body_read"]}
    assert "cold.md" in cands, "old cold zero-read entry is a candidate"
    assert cands["cold.md"]["exemptions"] == {"hot": False, "recent_30d": False}
    assert cands["hot.md"]["exemptions"]["hot"] is True, "hot rank exempts"
    assert cands["recent.md"]["exemptions"]["recent_30d"] is True, (
        "recent mtime exempts"
    )
    inv = {i["entry"]: i for i in rep["inventory"]}
    assert inv["cold.md"]["rank"] == "cold" and inv["hot.md"]["rank"] == "hot"


def test_r4_missing_source_partial_not_global_zero(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "solo.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[
            ("p1", "s1", 1787000000000, read_part(str(pool / "solo.md"), call_id="r1"))
        ],
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)  # no --cc-root
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    assert rep["coverage"]["partial"] is True, "cc source absent => partial coverage"
    assert rep["candidates"]["coverage_limited"] is True
    assert rep["coverage"]["instrumented"] == ["zcode"], "manifest of scanned sources"


def test_r9_manifest_lists_uninstrumented_harnesses(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "m.md")
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    assert set(rep["coverage"]["uninstrumented"]) >= {"codex", "muse", "bash-rg"}
