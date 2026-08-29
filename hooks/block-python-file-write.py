#!/usr/bin/env python3
"""
PreToolUse hook: 攔截 python heredoc 內的檔案寫入呼叫。

原因：sed 禁令與 Edit-first 紀律的繞道形態——`python3 - <<EOF` +
`pathlib.write_text()` / `open(..., 'w')` 直寫檔案，同時繞過 Edit 工具與
sed 禁令（mosaic 兩週遙測實測 319 次）。改檔一律走 Edit/Write 工具。
對應 rule: rules/tool-discipline.md「檔案修改禁令」。
偵測邏輯見 is_violation()。hook crash（非 0 非 2 exit）為非阻斷，工具仍執行。
"""

import json
import re
import sys

HEREDOC_PATTERN = re.compile(r"<<-?\s*['\"]?\w+")
# `\bpython3?\b` 已涵蓋 uv run python 形態（uv 後仍出現 'python' word）
PYTHON_PATTERN = re.compile(r"\bpython3?\b")
# 刻意窄：只抓明確的寫入 API。已知限制（regex 實測）：open() 第一參數含
# 巢狀括號（open(Path(d).name, 'w')、open(os.path.join(a,b), 'w')）不攔
# ——[^)]* 不跨巢狀；spike 首版寧漏抓不誤傷，加寬前先收誤傷率數據。
# os.replace/shutil/copy 等先放行。
WRITE_PATTERN = re.compile(
    r"\.write_text\s*\(|\.write_bytes\s*\("
    r"|open\s*\([^)]*['\"][wax][+b]*['\"]"
)


def is_violation(command: str) -> bool:
    """python heredoc + heredoc 標記之後出現檔案寫入呼叫。

    三者同時成立才攔。純讀 heredoc（計算/查詢/列印）不攔——寫入 pattern
    必須出現在 heredoc 標記之後（m.end() 起搜）。
    """
    m = HEREDOC_PATTERN.search(command)
    if not m:
        return False
    if not PYTHON_PATTERN.search(command):
        return False
    return bool(WRITE_PATTERN.search(command, m.end()))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        # hook crash = 非阻斷，工具仍執行。記錄但不卡關。
        print(f"[block-python-file-write] stdin parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command or not is_violation(command):
        sys.exit(0)

    # exit 2 + stderr：harness 將 stderr 回饋給 LLM 作為修正指引
    print(
        "[Hook Blocked] python heredoc 內含檔案寫入呼叫。\n"
        "原因：python - <<EOF + write_text()/open(...,'w') 是 Edit 工具與 sed 禁令的"
        "繞道形態（遙測實測 319 次），不可追溯、無 read-state 保護。\n"
        "修正方式：改檔一律用 Edit/Write 工具；heredoc 僅用於純計算/查詢。",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
