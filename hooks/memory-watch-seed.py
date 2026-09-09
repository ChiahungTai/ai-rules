#!/usr/bin/env python3
"""CC SessionStart watch-seed (AIR-56 follow-up): point the FileChanged
watcher at the ai-rules memory pool.

Why a seed script: FileChanged matcher seeds are cwd-scoped literal filenames
and the pool lives outside every repo cwd (hooks/AGENTS.md wiring note), so
the only way to watch the pool is a SessionStart hook returning absolute
`watchPaths` (CC mirror hooks.md SessionStart Decision Control). This script
lists pool entries (top-level .md, excluding MEMORY.md and _-prefixed files —
the same entry filter `memory_hook_common.is_pool_entry` applies, so we never
watch files the dirty sensor would drop).

Always exits 0; pool missing -> stderr hint + empty watch list; pool empty
-> empty watch list (harmless no-op). Hook runtime is python 3.9 — no 3.10+
syntax in this file.
"""

import json
import sys
from pathlib import Path

POOL = Path.home() / ".claude" / "projects" / "-Users-ctai-Github-ai-rules" / "memory"


def watch_paths():
    if not (POOL / "MEMORY.md").is_file():
        # Pool missing is abnormal on this machine (F4a): surface on stderr
        # instead of silently seeding an empty watch list. Cross-machine /
        # multi-pool derivation is deliberately out of scope here — AIR-54 S2
        # owns the path-governance redesign.
        print(
            f"memory-watch-seed: pool not found at {POOL}; seeding empty watch list",
            file=sys.stderr,
        )
        return []
    return sorted(
        str(p.resolve())
        for p in POOL.glob("*.md")
        if p.name != "MEMORY.md" and not p.name.startswith("_")
    )


def main():
    try:
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "watchPaths": watch_paths(),
            }
        }
        json.dump(payload, sys.stdout)
        sys.stdout.write("\n")
    except Exception:
        # A seed hook must never break session start.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
