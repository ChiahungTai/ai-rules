#!/usr/bin/env python3
"""CR 使用量挖掘（corrections-weekly 的 CR 健檢機械面——ZCode db 面）。

撈時間窗內所有 sessions（含 subagent——升級①的 cr-research 用量算數；
side_chat/fork 亦計入——全 workspace 消費語義，判讀時知悉計數含這些形態）
的 tool part，統計 CR 消費三指標：CR 家族 skill 調用（cr-query＋code-reality）、
CR MCP 工具呼叫（mcp__plugin…code-reality…）、對照 Bash rg 呼叫量
（`rg ` 開頭＋` rg ` 中綴；無空格複合形態殘差不計）。輸出計數＋distinct
sessions 供 LLM 判讀趨勢（腳本不判讀——advisory 面）。

Run: uv run python cr_usage.py [--days 7]
Exit: 0=正常（含零使用）；1=db 失敗（唯讀、fail-loud）。
"""

import argparse
import sqlite3
import time
from pathlib import Path

DB = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()
    if args.days <= 0:
        ap.error("--days 必須 > 0")

    since = int((time.time() - args.days * 86400) * 1000)
    try:
        db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        print(f"[FAIL] db 開啟失敗：{exc}")
        return 1
    try:
        rows = db.execute(
            "SELECT s.id, json_extract(p.data, '$.tool') AS tool, "
            "json_extract(p.data, '$.state.input.command') AS cmd "
            "FROM part p JOIN session s ON p.session_id = s.id "
            "WHERE p.time_created >= ? "
            "AND json_extract(p.data, '$.type') = 'tool' "
            "AND (json_extract(p.data, '$.tool') LIKE 'mcp__plugin%' "
            "     OR json_extract(p.data, '$.tool') IN ('Bash', 'Skill'))",
            (since,),
        ).fetchall()
        skill_rows = db.execute(
            "SELECT s.id, json_extract(p.data, '$.state.input.skill') AS skill "
            "FROM part p JOIN session s ON p.session_id = s.id "
            "WHERE p.time_created >= ? "
            "AND json_extract(p.data, '$.type') = 'tool' "
            "AND json_extract(p.data, '$.tool') = 'Skill'",
            (since,),
        ).fetchall()
    except sqlite3.Error as exc:
        print(f"[FAIL] 查詢失敗：{exc}")
        return 1
    finally:
        db.close()

    cr_skill_map, cr_skill_total, cr_mcp, rg = {}, set(), {}, 0
    for sid, skill in skill_rows:
        s = str(skill or "")
        if "cr-query" in s or "code-reality" in s:
            cr_skill_map.setdefault(s, set()).add(sid)
            cr_skill_total.add(sid)
    for sid, tool, cmd in rows:
        name = tool or ""
        if name.startswith("mcp__plugin") and "code-reality" in name:
            cr_mcp.setdefault(name, set()).add(sid)
        elif name == "Bash" and cmd:
            c = str(cmd)
            if c.startswith("rg ") or " rg " in c:
                rg += 1

    def line(label: str, mapping: dict) -> None:
        for name in sorted(mapping, key=lambda k: -len(mapping[k])):
            print(f"{label}\t{len(mapping[name])} sessions\t{name}")

    print(f"[OK] cr_usage: {args.days}d 窗")
    print("== CR Skill 調用（cr-query＋code-reality）==")
    if cr_skill_map:
        print(f"cr-skill-total\t{len(cr_skill_total)} sessions")
        line("cr-skill", cr_skill_map)
    else:
        print("（零）")
    print("== CR MCP 工具（distinct sessions）==")
    if cr_mcp:
        line("cr-mcp", cr_mcp)
    else:
        print("（零）")
    print(f"== 對照：Bash rg 呼叫 part 數 ==\n{rg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
