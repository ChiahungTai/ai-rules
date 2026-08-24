#!/usr/bin/env python3
"""
PreToolUse hook: 強制 mcp__code-review-graph__* 呼叫必帶 repo_root。

共享 HTTP MCP server（com.user.crg-mcp, 127.0.0.1:5555）以 tool-call 的
repo_root 參數路由 repo；省略時 server 落到自身 cwd（中性目錄）→ 查到空
graph，回「graph is empty」的自信假陰性（2026-08-24 spike 實證：NT 查
InstrumentId 回 not_found + "graph is empty"）。此 hook 在客戶端機械阻擋
缺參數呼叫，逼 AI 補 repo_root=<當前 repo root> 再重試。

list_repos_tool / cross_repo_search_tool 不吃 repo_root（registry 級），放行。
Claude 端 stdio（cwd=${CLAUDE_PROJECT_DIR} 展開）default 正確；帶 repo_root
統一適用無害。

exit 2 + stderr = 阻擋並回饋修正指引（同 block-python-c-comment 契約）。
hook crash（非 0 非 2 exit）為非阻斷，工具仍執行。
"""

import json
import sys

PREFIX = "mcp__code-review-graph__"
# registry 級工具無 repo 概念
EXEMPT = {"list_repos_tool", "cross_repo_search_tool"}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        # hook crash = 非阻斷，工具仍執行。記錄但不卡關。
        print(f"[require-crg-repo-root] stdin parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    tool = data.get("tool_name", "")
    if not tool.startswith(PREFIX):
        sys.exit(0)
    if tool.rsplit("__", 1)[-1] in EXEMPT:
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    repo_root = tool_input.get("repo_root")
    if repo_root and str(repo_root).strip():
        sys.exit(0)

    # exit 2 + stderr：harness 將 stderr 回饋給 LLM 作為修正指引
    print(
        "[Hook Blocked] code-review-graph 呼叫缺 repo_root。\n"
        "共享 CRG server 以 repo_root 路由 repo；省略會落到 server cwd 的空 "
        "graph，得到「graph is empty」假陰性（不是工具壞了）。\n"
        "修正：用相同參數重試，並加上 repo_root=<當前 repo root 絕對路徑>。",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
