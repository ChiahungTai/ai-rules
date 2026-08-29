#!/usr/bin/env python3
"""SessionStart(compact) 注入器——compact 後自動補給 raw tail＋STATE.md。

背景（2026-08-23 compact-lab 實驗）：/compact 摘要會壓掉 verbatim 交付物
（指示要求無效）、harness re-injection 快照可能過時。結構性解法＝compact 後
注入「壓縮前最後幾輪原文」。tail 原文由 Claude Code transcript JSONL
（stdin hook input 的 transcript_path）唯讀取得。

平台支援：Claude Code 官方支援 SessionStart + matcher "compact"
（hooks-guide「Re-inject context after compaction」官方食譜；2026-08-30 接線
進 settings.json）。ZCode 端 compact source 不派發 SessionStart
（2026-08-24 L4 實證）——該端維持 compact-prep 手動三動作，本 hook 不註冊。

fail-open：任何錯誤 → 空輸出 exit 0（注入失敗不擋 session）。診斷走 stderr。
stdout 有 32KB 協議上限——預算以 UTF-8 bytes 計（CJK 場景 ensure_ascii=False
下 3 bytes/字元），組完最終 guard。
"""

import json
import sys
from pathlib import Path

CANDIDATE_ENTRIES = 60  # 由最新往回的掃描窗口
TAIL_BUDGET_BYTES = 20000
STATE_BUDGET_BYTES = 4000
OUTPUT_GUARD_BYTES = 30000  # 最終防線（framing＋JSON 結構開銷後仍須 < 32768）
INJECT_MARKER = "<compact-tail-inject>"  # 跳過上代注入，防連續 compact 遞迴膨脹


def _texts_of(message: dict) -> list[str]:
    """CC transcript message.content 的 text 抽取（str 或 block list 兩型）。"""
    content = message.get("content")
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
    return []


def fetch_tail(transcript_path: str) -> str:
    """由 transcript JSONL 尾段累積 raw text 到 bytes 預算。

    截斷砍最舊、保最新（verbatim 標的在最後）。排除 compact 摘要列、
    sidechain（subagent）列、含上代注入 marker 的列。
    """
    entries: list[tuple[str, str, str]] = []  # (role, hh:mm:ss, text)
    with open(transcript_path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") not in ("user", "assistant"):
                continue
            if e.get("isCompactSummary") or e.get("isSidechain"):
                continue
            text = "\n".join(t for t in _texts_of(e.get("message") or {}) if t).strip()
            if not text or INJECT_MARKER in text:
                continue
            ts = str(e.get("timestamp", ""))
            hhmmss = ts.split("T")[-1][:8] or ts[:8]
            entries.append((e["type"], hhmmss, text))
    blocks: list[str] = []
    used = 0
    for role, hhmmss, text in reversed(entries[-CANDIDATE_ENTRIES:]):  # 新 → 舊
        block = f"### [{role}] {hhmmss}\n{text}"
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
    # 只在 compact 後注入；startup/resume/clear 時完整 context 已在，注入是重複
    if data.get("source") != "compact":
        print(
            f"compact-tail-inject: source={data.get('source')} 非 compact，跳過",
            file=sys.stderr,
        )
        return
    session_id = data.get("session_id") or ""
    transcript_path = data.get("transcript_path") or ""
    if not transcript_path:
        # transcript_path 是唯一的原文資料源；缺了無法安全取 tail（不能猜別的
        # session 檔——同 worktree 並行 session 會撈到別人的對話）→ fail-open no-op
        print(
            "compact-tail-inject: stdin 無 transcript_path，跳過（無法安全定位原文）",
            file=sys.stderr,
        )
        return
    try:
        tail = fetch_tail(transcript_path)
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
            f"compact-tail-inject: 輸出 {len(out.encode('utf-8'))} bytes 超上限，跳過",
            file=sys.stderr,
        )
        return
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
