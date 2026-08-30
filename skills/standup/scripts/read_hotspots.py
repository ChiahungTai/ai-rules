#!/usr/bin/env python3
"""Read 重複熱點週報（T2-4 可見性迴路——ZCode db 面）。

aggregate_sessions.py 的 zcode_sessions() 聚合的是日粒度敘事素材；本腳本是
(session,file) 重讀計數——職責不同不可重用。讀 ZCode 遙測 db.sqlite 的
part 表，聚合本週（7 天窗）Read 呼叫的重複次數——Read 紀律（同檔禁無參數
重讀）的衰減熱點。standup 週任務消費：≥5 次重讀＝人工判讀熱點（腳本只報
數據不判斷）。

Run: uv run python skills/standup/scripts/read_hotspots.py [--days 7] [--min 3] [--top 10]
Exit: 0=正常；1=db 開啟失敗（唯讀、fail-loud）。
"""

import argparse
import json
import sqlite3
import time
from pathlib import Path

DB = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--min", type=int, default=3, help="每 (session,file) 最少次數")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    since = int((time.time() - args.days * 86400) * 1000)
    try:
        db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        print(f"[FAIL] db 開啟失敗：{exc}")
        return 1
    try:
        # LIKE prefilter 假設 part.data 為 compact JSON（"tool":"Read" 無空格）——
        # ZCode 改存儲格式（帶空格）時此處會靜默少計，屬已知假設非保證
        rows = db.execute(
            "SELECT p.session_id, p.data FROM part p "
            'WHERE p.time_created >= ? AND p.data LIKE \'%"tool":"Read"%\'',
            (since,),
        ).fetchall()
    finally:
        db.close()

    # 計數 key 用完整 session_id（截斷會把所有 subagent 合併成同 key——
    # 前綴 sess_subagent_agent_ 遠長於 16）；display 才截短
    counts: dict[tuple[str, str], int] = {}
    for session_id, raw in rows:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if data.get("type") != "tool" or data.get("tool") != "Read":
            continue
        state = data.get("state") or {}
        fp = (state.get("input") or {}).get("file_path") or ""
        if not fp:
            continue
        counts[(session_id, fp)] = counts.get((session_id, fp), 0) + 1

    hot = sorted(
        ((k, n) for k, n in counts.items() if n >= args.min),
        key=lambda kv: -kv[1],
    )[: args.top]
    total_reads = sum(counts.values())
    print(
        f"[OK] read_hotspots: {total_reads} reads / {args.days}d, "
        f"{len(counts)} (session,file) pairs, {len(hot)} >= {args.min}x"
    )
    if not hot:
        print("  （無熱點——Read 紀律健康）")
        return 0
    for (sid, fp), n in hot:
        flag = " ⚠️衰減熱點" if n >= 5 else ""
        print(f"  {n:3d}x  {sid[:24]}  {fp}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
