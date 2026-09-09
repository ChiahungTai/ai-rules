#!/usr/bin/env python3
"""CC FileChanged sensor (AIR-56): memory pool mutation dirty-bit, evidence only.

FileChanged fires on watched-file disk change (Edit/Write/Bash/external —
mirror docs). It CANNOT attribute: the session_id in its input is the WATCHER,
not the writer. So this sensor emits dirty evidence only; the collector
attaches it per entry (`dirty_after_tracked`) and the hash leg decides.

Scope contract (fail-loud):
- Same shared pool filter (`memory_hook_common.is_pool_entry`).
- Wiring limitation (verified 09-09): FileChanged matchers are cwd-scoped
  literal filenames; the memory pool lives OUTSIDE any repo cwd, so the pool
  cannot be watched in our topology. This script ships logic-verified
  (stdin->log); live wiring stays unverified until a pool-under-cwd topology
  exists. The hash leg remains the external-write backstop.
- Always exits 0. Hook runtime is python 3.9 — no 3.10+ syntax.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_hook_common import emit, is_pool_entry, utc_now


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (ValueError, OSError):
        return 0
    try:
        if not isinstance(data, dict):
            return 0
        # FileChanged input carries the changed path under file_path (CC
        # mirror); fall back to tool_input.file_path defensively.
        tool_input = data.get("tool_input") or {}
        raw_path = data.get("file_path") or tool_input.get("file_path", "")
        canon = is_pool_entry(raw_path)
        if canon is None:
            return 0
        emit(
            {
                "kind": "file_changed",
                "source": "claude",
                "ts": utc_now(),
                "watcher_session": data.get("session_id"),
                "file_path": canon,
            }
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
