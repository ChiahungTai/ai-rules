# agents/ — 跨 harness subagent 定義

> 部署與 skills/commands 同款：repo 為單一來源，`~/.claude/agents`、`~/.zcode/agents` symlink → 本目錄。與 hooks/ 不同（config 引用、無目錄載入點），subagent 兩家都是**目錄載入點**，symlink 成立。ZCode 設定 UI 的新建/編輯會直接寫入本目錄（= 產生 repo working tree diff，屬預期行為）。

## 定義檔慣例

markdown + YAML frontmatter，正文 = 系統提示詞。兩家必填欄位同為 `name` / `description`（主 agent 依 description 決定何時委派 — 寫清楚觸發時機）。

### 欄位相容策略

| 類別 | 欄位 | 說明 |
|------|------|------|
| 直接共用 | `name` / `description` / `color` / `maxTurns` / `disallowedTools` / `tools` | tools 只列 built-in 共通名（Read / Grep / Glob / Bash / Edit / Write / WebFetch / WebSearch / TodoWrite） |
| 省略共用 | `model` | 省略 → 兩家皆 inherit 主 session（Claude 別名 sonnet/opus/... 在 ZCode 無效） |
| 可寫（ZCode 安全忽略） | Claude 專屬：`permissionMode` / `skills` / `hooks` / `memory` / `background` / `isolation` / `effort` / `initialPrompt` | ZCode 官方明說未知欄位靜默忽略不報錯 |
| 禁寫進共用檔 | ZCode 專屬：`thoughtLevel` / `injectAgentsMd` | Claude 對未知欄位容忍度未明 — 需要 per-harness 差異時另建 fork 檔 |
| 語義有差 | `mcpServers` | 兩家都吃名稱參考；ZCode 精確匹配、宣告未連接的服務直接失敗；Claude 另支援 inline 定義 |

### tools 清單陷阱（ZCode）

自訂 tools 清單會**排除全部 MCP 工具**（設定 UI 勾選清單只含 built-in）；補救只能手寫 `mcp__<server>__<tool>` 全名（萬用 `mcp__server__*` 無效，靜默忽略）。需要 MCP 的角色（如 lsp-python）**tools 留空**繼承全部。

### 背景執行

長任務角色（review / research 類）建議 frontmatter 加 `background: true` — Claude 端強制始終背景執行（即使主 agent 需要結果）。ZCode **不認識此欄位**（靜默忽略）— ZCode 端背景化是 spawn 端行為：官方文檔僅說前台/後台由主 Agent 自行決定（無 UI 開關、無參數記載），Agent tool 的 `run_in_background: true` 參數為 runtime 實測有效（2026-08-14 session：背景 spawn 成功、主對話未阻塞）。

## ZCode 限制（共用定義的邊界）

- Beta 僅 user 級（無 workspace 層）；內建 `general-purpose` / `Explore` 名稱不可複用（不可建同名覆蓋檔 — Claude 端可以覆蓋 Explore，這是兩家不對稱點）
- 子智能體內**不能再派發子智能體**（Claude 可多層巢狀——官方文檔對深度上限記載版本間不一，勿釘死數字）→ 共用的系統提示詞不可依賴「spawn 下屬 agent」
- 定義修改需**新會話**才生效（per-session 快照，同 hooks 行為）
- 自 v3.7.1 起子智能體預設注入 user 級 + workspace AGENTS.md（與 Claude subagents 載入 CLAUDE.md layers 對稱）
- Beta 灰度上線 — 可用性以「設定 → 子智能體」面板實測為準

## Claude 限制

- 檔案監聽僅涵蓋 session 啟動時已存在的 agents 目錄 — 首次建立本目錄（symlink）後需重啟一次載入
- 需要隔離副本的角色用 `isolation: worktree`（ZCode 無對應，靜默忽略）
