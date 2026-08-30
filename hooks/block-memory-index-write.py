#!/usr/bin/env python3
"""
PreToolUse hook（matcher Edit|Write|NotebookEdit）: 攔截對 MEMORY.md 的手寫。

MEMORY.md 是 _generate_index.py 的機械投影（條目檔 frontmatter = 單一寫入點）
——手寫索引必漂移：索引只載前「200 行或 25KB」，超限尾端靜默不載 → cluster
查重漏同主題條目 → 近重複寫入正回授（2026-08-30 mosaic 56.6KB 實證）。
Self-gating：同目錄無 _generate_index.py 的專案不攔（裝 script 即 opt-in）。
對應 rule: rules/context-management.md「Memory 生命周期規範」。
覆蓋邊界：僅攔 Edit/Write 工具面的 file_path——Bash redirect（echo >>/tee）不攔
（紀律面處理）。ZCode 端 exit 2 產生 deny 已證（官方文檔）；stderr 指引送達
模型未證（EP A3 deferred）——失敗跡象＝無解釋重試，回滾按 memory-hooks-rollback.md。
hook crash（非 0 非 2 exit）為非阻斷，工具仍執行。
"""

import json
import sys
from pathlib import Path

GENERATOR_NAME = "_generate_index.py"


def is_violation(file_path: str, has_generator: bool) -> bool:
    """寫入目標名為 MEMORY.md，且同目錄裝有 generator（opt-in 條件）。"""
    return Path(file_path).name == "MEMORY.md" and has_generator


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"[block-memory-index-write] stdin parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if file_path:
        gen = Path(file_path).parent / GENERATOR_NAME
        blocked = is_violation(file_path, gen.exists())
    else:
        blocked = False
    if not blocked:
        sys.exit(0)

    # exit 2 + stderr：Claude 端已證會回饋 LLM；ZCode 端 deny 已證、stderr 送達性未證（A3）
    print(
        "[Hook Blocked] MEMORY.md 是 generator 投影，禁手寫。\n"
        "原因：索引由條目檔 frontmatter 機械投影；手寫必漂移"
        "（載入截斷 → 查重漏 → 近重複寫入）。\n"
        "修正方式：改條目檔（frontmatter name/description/type）後執行:\n"
        f"  python3 {gen}（Stop hook 也會自動重生成）",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
