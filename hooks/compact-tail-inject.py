#!/usr/bin/env python3
"""SessionStart(compact) 注入器——compact 後自動補給 raw tail＋STATE.md。

背景（2026-08-23 compact-lab 實驗）：/compact 摘要會壓掉 verbatim 交付物
（指示要求無效）、harness re-injection 快照可能過時。結構性解法＝compact 後
注入「壓縮前最後幾輪原文」。tail 原文由 db.sqlite part 表唯讀取得。

fail-open：任何錯誤 → 空輸出 exit 0（注入失敗不擋 session）。診斷走 stderr。
stdout 有 32KB 協議上限——預算以 UTF-8 bytes 計（CJK 場景 ensure_ascii=False
下 3 bytes/字元），組完最終 guard。
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

DB = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"
CANDIDATE_PARTS = 30  # SQL 候選集（role 已下推 SQL，此值僅掃描窗口）
TAIL_BUDGET_BYTES = 20000
STATE_BUDGET_BYTES = 4000
OUTPUT_GUARD_BYTES = 30000  # 最終防線（framing＋JSON 結構開銷後仍須 < 32768）
INJECT_MARKER = "<compact-tail-inject>"  # 跳過上代注入，防連續 compact 遞迴膨脹


def fetch_tail(session_id: str) -> str:
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        rows = db.execute(
            "SELECT p.data, m.data, p.time_created FROM part p "
            "JOIN message m ON p.message_id = m.id "
            "WHERE p.session_id = ? AND json_extract(p.data, '$.type') = 'text' "
            "AND json_extract(m.data, '$.role') IN ('user', 'assistant') "
            "AND NOT json_extract(p.data, '$.synthetic') "
            "ORDER BY p.time_created DESC, p.id DESC LIMIT ?",
            (session_id, CANDIDATE_PARTS),
        ).fetchall()
    finally:
        db.close()
    # 由最新往回累積到 bytes 預算——截斷砍最舊，保最新（verbatim 標的在最後）
    blocks: list[str] = []
    used = 0
    for part_data, msg_data, ts in rows:  # 新 → 舊
        text = json.loads(part_data).get("text", "")
        if INJECT_MARKER in text:
            continue
        block = (
            f"### [{json.loads(msg_data).get('role')}] "
            f"{time.strftime('%H:%M:%S', time.localtime(ts / 1000))}\n{text}"
        )
        b = len(block.encode("utf-8"))
        if used + b > TAIL_BUDGET_BYTES:
            break
        blocks.append(block)
        used += b
    return "\n\n".join(reversed(blocks))


def read_state(cwd: str) -> str:
    state = Path(cwd) / "STATE.md" if cwd else None
    if state and state.is_file():
        return (
            state.read_text(encoding="utf-8")
            .encode("utf-8")[:STATE_BUDGET_BYTES]
            .decode("utf-8", errors="ignore")
        )
    return ""


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print("compact-tail-inject: stdin 非 JSON，跳過", file=sys.stderr)
        return
    # 只在 compact 後注入；startup/clear 時完整 context 已在，注入 tail 是重複
    if data.get("source") != "compact":
        print(
            f"compact-tail-inject: source={data.get('source')} 非 compact，跳過",
            file=sys.stderr,
        )
        return
    session_id = data.get("session_id") or ""
    if not session_id:
        # 不 fallback「db 最新 session」——同 worktree 並行 session 下會撈到別的
        # session 的 tail（靜默污染）。無 session_id 寧可不注入（fail-open no-op）。
        print(
            "compact-tail-inject: stdin 無 session_id，跳過（防同 wt 並行 session 污染）",
            file=sys.stderr,
        )
        return
    try:
        tail = fetch_tail(session_id)
        state = read_state(data.get("cwd", ""))
    except Exception as exc:  # fail-open by design
        print(f"compact-tail-inject: fail-open（{exc}）", file=sys.stderr)
        return
    if not tail and not state:
        print("compact-tail-inject: 無可注入內容", file=sys.stderr)
        return
    parts = [
        "<compact-tail-inject>\n以下為 /compact 壓縮前的對話尾部原文與專案 STATE，"
        "由 SessionStart hook 注入。tail 是壓縮前尾段的**原文**——與摘要衝突時的"
        "裁決規則：摘要中若含對尾段內容的明確更正或裁決，以更正為準；其餘以 tail "
        "原文為準（優於任何重新注入的舊快照）。STATE.md 為專案 session 觀察層。\n"
    ]
    if tail:
        parts.append(f"<raw-tail session={session_id}>\n{tail}\n</raw-tail>")
    if state:
        parts.append(f"<state-md>\n{state}\n</state-md>")
    parts.append("</compact-tail-inject>")
    context = "\n\n".join(parts)
    out = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": data.get("hook_event_name", "SessionStart"),
                "additionalContext": context,
            }
        },
        ensure_ascii=False,
    )
    if len(out.encode("utf-8")) > OUTPUT_GUARD_BYTES:  # 組裝後最終 guard
        print(
            f"compact-tail-inject: 輸出 {len(out.encode('utf-8'))} bytes 超_guard，跳過",
            file=sys.stderr,
        )
        return
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
