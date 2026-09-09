"""Tests for hooks/memory-write-sensor.py + hooks/memory-dirty-sensor.py (AIR-56).

Sensors read CC hook JSON on stdin, append pool-scoped events to
$MEMORY_HOOK_LOG (overridden to tmp in tests). Never touch the live pool:
fixtures build a fake pool (dir + MEMORY.md) under tmp_path.
"""

import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks"
WRITE_SENSOR = HOOKS / "memory-write-sensor.py"
DIRTY_SENSOR = HOOKS / "memory-dirty-sensor.py"


def make_pool(tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "MEMORY.md").write_text("# index\n")
    entry = pool / "note.md"
    entry.write_text("---\nname: note.md\n---\n\nbody\n")
    return pool, entry


def run_sensor(script, payload, tmp_path):
    import os

    log = tmp_path / "hook-events.jsonl"
    env = dict(os.environ, MEMORY_HOOK_LOG=str(log))
    inp = payload if isinstance(payload, str) else json.dumps(payload)
    r = subprocess.run(
        [sys.executable, str(script)],
        input=inp,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    lines = []
    if log.is_file():
        lines = [json.loads(ln) for ln in log.read_text().splitlines() if ln.strip()]
    return r, lines


def test_write_sensor_records_pool_edit(tmp_path):
    """AIR-56: PostToolUse Edit on pool entry emits actor evidence."""
    _, entry = make_pool(tmp_path)
    payload = {
        "session_id": "sess_1",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(entry)},
        "tool_use_id": "tu_1",
        "agent_id": "ag_9",
        "agent_type": "Task",
    }
    r, lines = run_sensor(WRITE_SENSOR, payload, tmp_path)
    assert r.returncode == 0, r.stderr
    assert len(lines) == 1
    ev = lines[0]
    assert ev["kind"] == "post_tool_use"
    assert ev["file_path"] == str(entry.resolve())
    assert (ev["session_id"], ev["tool_use_id"]) == ("sess_1", "tu_1")
    assert ev["agent_id"] == "ag_9"


def test_write_sensor_ignores_non_pool_and_other_tools(tmp_path):
    """AIR-56: non-pool paths / non-Edit-Write tools / MEMORY.md emit nothing."""
    pool, entry = make_pool(tmp_path)
    other = tmp_path / "other.md"
    other.write_text("x")
    cases = [
        {
            "session_id": "s",
            "tool_name": "Read",
            "tool_input": {"file_path": str(entry)},
        },
        {
            "session_id": "s",
            "tool_name": "Edit",
            "tool_input": {"file_path": str(other)},
        },
        {
            "session_id": "s",
            "tool_name": "Write",
            "tool_input": {"file_path": str(pool / "MEMORY.md")},
        },
        {"session_id": "s", "tool_name": "Edit", "tool_input": {}},
    ]
    for payload in cases:
        r, lines = run_sensor(WRITE_SENSOR, payload, tmp_path)
        assert r.returncode == 0
        assert lines == []


def test_sensors_malformed_stdin_still_exit_zero(tmp_path):
    """AIR-56: a sensor must never fail the tool call (exit 0 on garbage)."""
    for script in (WRITE_SENSOR, DIRTY_SENSOR):
        for bad in ("", "not json{", "[1,2]"):
            r, lines = run_sensor(script, bad, tmp_path)
            assert r.returncode == 0, (script, bad)
            assert lines == []


def test_dirty_sensor_records_watcher_not_writer(tmp_path):
    """AIR-56: FileChanged emits dirty evidence with watcher session only."""
    _, entry = make_pool(tmp_path)
    payload = {"session_id": "watcher_A", "file_path": str(entry)}
    r, lines = run_sensor(DIRTY_SENSOR, payload, tmp_path)
    assert r.returncode == 0, r.stderr
    assert len(lines) == 1
    ev = lines[0]
    assert ev["kind"] == "file_changed"
    assert ev["watcher_session"] == "watcher_A"
    assert "session_id" not in ev  # never pose as the writer
    assert ev["file_path"] == str(entry.resolve())


def test_log_override_falls_back_when_relative_or_pool_file(tmp_path):
    """AIR-56 F3: relative override or pool-entry target falls back safely."""
    import os

    _, entry = make_pool(tmp_path)
    payload = {
        "session_id": "s",
        "tool_name": "Write",
        "tool_input": {"file_path": str(entry)},
        "tool_use_id": "t1",
    }
    # relative override -> default log, not cwd (HOME isolated: never touch
    # the real default log from tests)
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    env = dict(os.environ, MEMORY_HOOK_LOG="rel-log.jsonl", HOME=str(fake_home))
    r = subprocess.run(
        [sys.executable, str(WRITE_SENSOR)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(tmp_path),
    )
    assert r.returncode == 0
    assert not (tmp_path / "rel-log.jsonl").is_file()
    # override pointing at a pool entry file -> refused, entry untouched
    before = entry.read_text()
    env = dict(os.environ, MEMORY_HOOK_LOG=str(entry), HOME=str(fake_home))
    r = subprocess.run(
        [sys.executable, str(WRITE_SENSOR)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert r.returncode == 0
    assert entry.read_text() == before


def test_log_rotation_single_generation(tmp_path):
    """F4: >2 MiB log rotates to .prev (old content) and new log holds only the new line."""
    _, entry = make_pool(tmp_path)
    log = tmp_path / "hook-events.jsonl"
    filler_line = json.dumps({"kind": "old", "pad": "x" * 512}) + "\n"
    lines_needed = (2 * 1024 * 1024 // len(filler_line)) + 10
    log.write_text(filler_line * lines_needed)
    assert log.stat().st_size > 2 * 1024 * 1024
    payload = {
        "session_id": "sess_rot",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(entry)},
        "tool_use_id": "tu_rot",
    }
    r, lines = run_sensor(WRITE_SENSOR, payload, tmp_path)
    assert r.returncode == 0, r.stderr
    prev = tmp_path / "hook-events.jsonl.prev"
    assert prev.is_file(), "old generation must survive as .prev"
    assert "old" in prev.read_text()[:200]
    assert len(lines) == 1
    assert lines[0]["session_id"] == "sess_rot"


def test_underscore_prefixed_pool_file_excluded(tmp_path):
    """Pool maintenance files (_inventory.md etc.) are not entries: no event."""
    pool, _ = make_pool(tmp_path)
    underscore = pool / "_inventory.md"
    underscore.write_text("# projection\n")
    payload = {
        "session_id": "sess_u",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(underscore)},
        "tool_use_id": "tu_u",
    }
    r, lines = run_sensor(WRITE_SENSOR, payload, tmp_path)
    assert r.returncode == 0, r.stderr
    assert lines == []
