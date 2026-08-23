#!/usr/bin/env python3
"""Show last N human<->assistant exchanges of a ZCode session.

Mechanical extractor (standup pattern): read ~/.zcode/cli/db/db.sqlite
read-only, walk message -> part for one session, keep human input (user
text part without `synthetic` flag) and assistant text parts, print the
tail rounds. Tool results / continuation notes / system reminders all
carry `synthetic: true` and are excluded.

Usage:
    uv run python zcode_tail_chat.py <session-id-or-prefix> [rounds=4] [chars=400]
"""

import json
import sqlite3
import sys
from pathlib import Path

DB = Path.home() / ".zcode/cli/db/db.sqlite"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    prefix, rounds, chars = (
        sys.argv[1],
        int(sys.argv[2]) if len(sys.argv) > 2 else 4,
        int(sys.argv[3]) if len(sys.argv) > 3 else 400,
    )
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    ids = [
        r[0]
        for r in con.execute("SELECT id FROM session WHERE id LIKE ?", (prefix + "%",))
    ]
    if not ids:
        sys.exit(f"[FAIL] no session matches prefix {prefix!r}")
    if len(ids) > 1:
        sys.exit(f"[FAIL] ambiguous prefix, matches: {ids}")
    sid = ids[0]
    events = []
    for seq, role, pdata in con.execute(
        """
        SELECT m.sequence, json_extract(m.data,'$.role'), p.data
        FROM part p JOIN message m ON p.message_id = m.id
        WHERE p.session_id = ? AND json_extract(p.data,'$.type') = 'text'
        ORDER BY m.sequence, p.sequence
        """,
        (sid,),
    ):
        d = json.loads(pdata)
        if role == "user" and d.get("synthetic"):
            continue
        if role == "assistant":
            events.append((seq, "assistant", d.get("text", "")))
        else:
            events.append((seq, "user", d.get("text", "")))
    con.close()
    human_idx = [i for i, e in enumerate(events) if e[1] == "user"]
    if not human_idx:
        sys.exit("[FAIL] no human input found")
    if rounds <= 0:
        sys.exit("[FAIL] rounds must be >= 1")
    start = human_idx[-min(rounds, len(human_idx))]
    print(f"# {sid} — last {rounds} rounds\n")
    for seq, role, text in events[start:]:
        who = "USER" if role == "user" else "AI  "
        body = text.strip().replace("\n", " ")
        if len(body) > chars:
            body = body[:chars] + " …"
        print(f"[{who}] {body}\n")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
