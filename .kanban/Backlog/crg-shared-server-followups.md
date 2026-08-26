# CRG 共享 server 後續三項

> 源：2026-08-24 CRG 復活 EP（HTTP MCP 共享 server + repo_root hook 強制）。
> 前置已落地：`com.user.crg-mcp` launchd（:5555）、ZCode/Codex 接線、
> `require-crg-repo-root.py` hook、crg-query skill shared-server rule。
> 狀態：📋 待實作（各自獨立，無互相依賴）

## ① `--tools` 白名單修剪（token 成本）

共享 server 預設暴露 30 個 tools，schema 描述注入**每個** ZCode session 的
context（含非 CRG 專案）。量測實際注入 token 量；偏高則 `serve --tools`
白名單限縮到查詢面核心（query_graph/impact/detect_changes/minimal_context/
review_context/flows/communities/architecture/status），build/update 類
留在 CLI/githook。

## ② Claude 端統一走 HTTP（可選）

mosaic 三 worktree 的 `.mcp.json` stdio（`${CLAUDE_PROJECT_DIR}` 展開）
仍正常；統一 HTTP 可少 N 個 per-session server process、集中 log。收益小，
動 mosaic repo 檔案，優先級低。

## ③ Server 端 workspace 推斷升級（repo_root 省略容錯）

Hook 擋客戶端、skill 教指紋，但 Codex 等無 hook 的 harness 仍可能裸呼。
上游（`~/Github/code-review-graph`，凍結中需 user 拍板）加 env 開關：
`CRG_REQUIRE_REPO_ROOT=1` 時 `repo_root=None` → loud error（取代 cwd 走訪
空圖假陰性）。或更強：28 個 repo 級 tools 的 `repo_root` 改 schema required。
比照 lsp-python「server file_path 推斷 EP」思路——帶 file_path 的 tool
call 可由路徑前綴推斷 repo。

**上游耦合提醒（審查 A-F3）**：上游新增 registry 級 tool（無 repo_root）
時，`hooks/require-crg-repo-root.py` 的 `EXEMPT` 集需同步——漏同步會
誤擋＋補 repo_root 後 server schema 又拒絕（兩頭卡死，loud）。

**stderr 回饋實證（審查 A-F1，✅ 2026-08-25 已驗）**：新 session 實測
（handoff V2）——缺 repo_root 的呼叫被 hook 擋下後，指引文字以
`[Hook Blocked] ...` 前綴完整回饋給 LLM（含「用相同參數重試，並加上
repo_root=」修正指令），據以補參數一次重試成功。exit 2 + stderr 路徑
成立，**無需**改 `hookSpecificOutput.permissionDecision` JSON 路徑；
hook matcher `mcp__code-review-graph__`（含 `-`）實測正常命中。
