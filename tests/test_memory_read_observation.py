"""AIR-41 S1/S2: body Read observation — coverage-limited candidates.

Reuses AIR-40 fixtures (make_zdb/tool_part/write_entry) via import; the
`reads` subcommand must never turn missing sources into "successfully
observed zero reads" (EP R4/R9).
"""

import json
import subprocess
import sys
from datetime import UTC
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


def test_i1_rank_mirror_fences_and_metadata_fallback(tmp_path):
    """I1: rank parse mirrors the pool generator, not split+regex guessing."""
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "meta.md").write_text(
        "---\nname: meta.md\nmetadata:\n  rank: hot\n---\nbody\n", encoding="utf-8"
    )
    (pool / "proj.md").write_text(
        "---\nname: proj.md\nproject:\n  rank: hot\n---\nbody\n", encoding="utf-8"
    )
    (pool / "fallback.md").write_text(
        "---\nrank:\nmetadata:\n  rank: cold\n---\nbody\n", encoding="utf-8"
    )
    (pool / "nofm.md").write_text(
        "intro prose\n---\nrank: hot\n---\nbody\n", encoding="utf-8"
    )
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    inv = {i["entry"]: i["rank"] for i in json.loads(out.read_text())["inventory"]}
    assert inv["meta.md"] == "hot", "nested metadata.rank placement recognized"
    assert inv["proj.md"] == "core", "non-metadata parent indent must not match"
    assert inv["fallback.md"] == "cold", (
        "empty top-level rank falls back to metadata.rank"
    )
    assert inv["nofm.md"] == "core", (
        "body fence without leading frontmatter never hallucinates"
    )


def test_i2_unpaired_reads_count_as_contact(tmp_path):
    """I2: unmatched/unknown Reads are contact, never zero-body-read."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "u.md")
    part = read_part(str(pool / "u.md"), call_id="r1")
    del part["state"]["status"]  # zcode state without status -> "unknown"
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb, sessions=[("s1", None, None)], parts=[("p1", "s1", 1787000000000, part)]
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    obs = {o["entry"]: o for o in rep["observations"]}
    assert obs["u.md"]["zero_body_read"] is False
    assert obs["u.md"]["body_reads"][0]["status"] == "unknown"
    assert rep["coverage"]["unpaired_reads"] >= 1


def test_i3_window_shortfall_flags_partial(tmp_path):
    """I3: bounds starting after the window start is observable, not silent."""
    from datetime import datetime

    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "w.md")
    late = tmp_path / "late.db"
    make_zdb(
        late,
        sessions=[("s1", None, None)],
        parts=[("p1", "s1", 1787000000000, read_part(str(pool / "w.md")))],
    )
    r, out = run_reads(pool, tmp_path, zdb=late)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    assert rep["coverage"]["window_shortfall"] is True, (
        "first record post-dates --since"
    )
    assert rep["candidates"]["coverage_limited"] is True

    early = tmp_path / "early.db"
    pre_window_ms = int(datetime(2026, 7, 30, tzinfo=UTC).timestamp() * 1000)
    make_zdb(
        early,
        sessions=[("s1", None, None)],
        parts=[
            # pre-window row: excluded from events but anchors global bounds
            ("p0", "s1", pre_window_ms, read_part(str(pool / "w.md"), call_id="r0")),
            ("p1", "s1", 1787000000000, read_part(str(pool / "w.md"), call_id="r1")),
        ],
    )
    r2, out2 = run_reads(pool, tmp_path, zdb=early)
    assert r2.returncode == 0
    rep2 = json.loads(out2.read_text())
    assert rep2["coverage"]["window_shortfall"] is False, (
        "records older than --since prove the window is fully observed"
    )


def test_i4_reads_without_entry_rename_clue(tmp_path):
    """I4: rename/delete identity clue surfaced; LLM-side slot not faked."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "new_name.md")
    zdb = tmp_path / "z.db"
    make_zdb(
        zdb,
        sessions=[("s1", None, None)],
        parts=[("p1", "s1", 1787000000000, read_part(str(pool / "old_name.md")))],
    )
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    obs = {o["entry"]: o for o in rep["observations"]}
    assert obs["new_name.md"]["zero_body_read"] is True, "candidate still listed"
    cands = rep["candidates"]
    assert "old_name.md" in cands["reads_without_entry"], (
        "read of a missing entry is the rename/delete identity clue (EP R6)"
    )
    assert "maintenance_only_unconfirmed" not in cands, (
        "LLM-side classification never emitted as a fake empty slot"
    )


def test_i1b_rank_mirror_quote_whitespace_family(tmp_path):
    """F1: quote/whitespace family — generator top-level is double-pass
    (frontmatter unquote + parse_rank strip), nested is single-pass."""
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "qtop.md").write_text("---\nrank: ' hot '\n---\nbody\n", encoding="utf-8")
    (pool / "qempty.md").write_text(
        "---\nrank: ''\nmetadata:\n  rank: cold\n---\nbody\n", encoding="utf-8"
    )
    (pool / "qmeta.md").write_text(
        "---\nmetadata:\n  rank: ' hot '\n---\nbody\n", encoding="utf-8"
    )
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0, r.stderr
    inv = {i["entry"]: i["rank"] for i in json.loads(out.read_text())["inventory"]}
    assert inv["qtop.md"] == "hot", "top-level quoted+inner-space: double-pass"
    assert inv["qempty.md"] == "cold", "quoted empty top falls back to metadata"
    assert inv["qmeta.md"] == "core", "nested quoted+inner-space: single-pass"


def test_f2_reads_report_carries_generator_identity(tmp_path):
    """F2: the docstring's generator_schema claim must hold on reads path."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "g.md")
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    assert rep["generators"] == {str(pool.resolve()): "absent"}, (
        "no generator in fixture pool -> absent, but the key must ride along"
    )


def test_f4_cc_unmatched_read_counts_as_contact(tmp_path):
    """CC Read tool_use without tool_result stays contact (in-flight/cut)."""
    pool = tmp_path / "pool"
    pool.mkdir()
    write_entry(pool, "c.md")
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
                            "name": "Read",
                            "input": {"file_path": str(pool / "c.md")},
                        }
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    zdb = tmp_path / "z.db"
    make_zdb(zdb, sessions=[], parts=[])
    r, out = run_reads(pool, tmp_path, zdb=zdb, cc_root=cc_root)
    assert r.returncode == 0
    rep = json.loads(out.read_text())
    obs = {o["entry"]: o for o in rep["observations"]}
    assert obs["c.md"]["zero_body_read"] is False
    assert obs["c.md"]["body_reads"][0]["status"] == "unmatched"
    assert obs["c.md"]["body_reads"][0]["source"] == "claude"
    assert rep["coverage"]["unpaired_reads"] >= 1
