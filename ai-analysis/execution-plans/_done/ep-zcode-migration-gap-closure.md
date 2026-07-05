# EP: ZCode 遷移差距閉合（hooks / MCP / shioaji / LSP / commands）

> **ep_type**: implementation（docs mode — config + .md 變更，無 .py logic）

## 動機（self-contained 背景）

跨 harness 轉型後（commit `431a1d9`→`54853cf`），需閉合 ZCode 3.2.5 vs Claude Code 在「日常使用」的實質差距。本 EP 基於 Deep audit（settings 全維度對比 + 對話紀錄使用情境抽樣）+ hooks 技術衝突查證，收斂出 4 個可執行段落。

**核心發現**（決定段落範圍）：

| 差距 | 真相 | 處置 |
|------|------|------|
| **Hooks** | binary 有 hooks 基礎設施（RPC channel 註冊），但對 native ZCode Agent（桌面 app 路徑）不觸發——[`zai-org/feedback#32`](https://github.com/zai-org/feedback/issues/32) P2 open，回報者連 plugin hooks 也測過無效。**不是設定問題，是 binary bug**（信心度 8.5/10） | ❌ 列為已知不可遷移限制，文件化即可 |
| **4 個 MCP server** | ZCode user MCP 僅 `context7`；Claude 有 5 個（缺 zai-mcp-server / web-reader / zread / web-search-prime） | ✅ S1 補到 cli/config.json |
| **shioaji marketplace + plugin** | ZCode 未加 shioaji-plugins marketplace → 無法裝 shioaji（台股交易 API） | ✅ S2 加 marketplace + 啟用 plugin |
| **LSP** | **各家 harness 有自己的 LSP 機制，無統一載體**：Claude / OpenCode 原生內建 LSP plugin（Claude 有 12 種語言）；ZCode 無原生 → mosaic_alpha 已用自建 `lsp-python` MCP（http，per-project）替代。ai-rules 純文檔 repo（僅 3 個獨立 .py 腳本）不需 LSP。 | ✅ S3 文件化「LSP 跨 harness 無統一載體，ZCode 需自建 MCP server 替代」 |
| **Permission 模型** | ZCode `yolo` + 精確匹配 vs Claude glob + `auto`。yolo 是用戶選擇，配合 autonomous-execution 紅線安全網（commit `4754ade`） | ❌ 不動（已是最佳妥協） |
| **`~/.agents/commands` 未建** | skills 已 symlink，commands 缺（zcode-configuration-guide skill 列為掃描路徑） | ✅ S4 補 symlink |
| **autoCompact 缺失** | ZCode 無對應 key | ❌ 不 fix（無法 fix），僅記錄 |

**Scope out**：
- 不嘗試遷移 hooks（binary bug，#32 未修）
- 不 fix autoCompact（ZCode 無對應）
- 不動 Permission 模型（yolo + 紅線安全網已是最佳妥協）
- 不為 ai-rules 建 LSP（純文檔 repo）
- 不改 hooks/ 目錄現況（已標 Claude 專屬，正確）

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S1** | 補 4 個 MCP server 到 `~/.zcode/cli/config.json` | 無 |
| **S2** | 加 shioaji-plugins marketplace + 安裝 plugin | 無 |
| **S3** | 文件化 LSP 跨 harness 結論（無統一載體，04 報告 §7 補段） | 無 |
| **S4** | `~/.agents/commands` symlink 補建 + 文件化 hooks 不可遷移結論（修訂） | 無 |

4 段，並行無依賴。S1/S2 是部署面 config 變更（ZCode 端），S3/S4 是 ai-rules repo 文件變更。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### 掃描範圍
- `~/.zcode/cli/config.json`（user MCP + plugins）
- `~/.zcode/cli/plugins/known_marketplaces.json`（marketplace 清單）
- `~/.agents/skills`（已 symlink）、`~/.agents/commands`（缺）
- `ai-analysis/reports/superpowers/04-multi-harness機制對照.md` §7（待補遷移結果）
- `AGENTS.md` 結構段（hooks 條目待修訂措辭）
- 參考：`~/.claude.json` top-level `mcpServers`（5 個 user MCP 定義來源）

### 受影響 UC（無新 UC，皆為既有狀態修訂）
| 項目 | 現況 | 目標 |
|------|------|------|
| ZCode user MCP | 1 個（context7） | 5 個（補 4 個） |
| ZCode marketplace | 1 個（claude-plugins-official） | 2 個（補 shioaji-plugins） |
| `~/.agents/commands` | 不存在 | symlink → repo commands/ |
| 04 報告 §7 | 寫「configuration-file hooks 不支援」 | 補「plugin hooks 也對 native Agent 不支援，hooks 完全不可遷移」+ LSP 跨 harness 結論 |

---

## Scenario Matrix（中型變更，docs mode 文檔語境）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | ZCode session 啟動 | 每次 session 開啟 | MCP servers 載入（hook 不觸發 = 已知限制，不阻塞） | 無 | S1/S2 |
| SM-2 | 用戶跑 `rg` 查詢 | 日常搜尋 | 不彈窗（yolo mode happy path） | 無 | 既有 yolo |
| SM-3 | 用戶跑 `rm`（紅線） | 刪除操作 | 跳過+記錄（autonomous-execution 紅線安全網，commit `4754ade` 已實作） | 無 | 既有紅線 |
| SM-4 | context7 MCP 連線 | 文件查詢 | 既有 happy（user MCP 已連） | 無 | 既有 |
| SM-5 | web-reader/zread/zai-mcp-server/web-search-prime 連線 | 網頁閱讀/repo 文件搜尋/截圖 OCR/進階搜尋 | S1 補 4 個 MCP 後 happy | 重啟 ZCode | S1 |
| SM-6 | shioaji plugin 載入 | 台股交易 API | S2 加 marketplace 後 happy | 重啟 + GUI 啟用 | S2 |
| SM-7 | dry run `/code-review` slash command 觸發 | 程式碼審查 | commands symlink happy（已 symlink，測試觸發） | 無 | 既有 |
| SM-8 | dry run `/judge-review` + `/commit` 全流程 | 整合驗證（用戶指定 dry run） | 完整流程跑通 + 無權限卡關 + 語音不響（hooks 不可遷移確認） | 無 | 整合 |

---

## S1: 補 4 個 MCP server 到 ZCode user config

### Context
- **背景**：ZCode user MCP 僅 `context7`（在 `~/.zcode/cli/config.json` 的 `mcp.servers`）。Claude 在 `~/.claude.json` top-level `mcpServers` 有 5 個：`context7` / `web-search-prime` / `zai-mcp-server` / `web-reader` / `zread`。差距 4 個。
- **影響**：截圖 OCR（`extract_text_from_screenshot`）、網頁閱讀（`webReader`）、repo 文件搜尋（`search_doc`/`read_file`/`get_repo_structure`）、進階搜尋（`web_search_prime`）全斷。這 4 個都在 Claude `permissions.allow` 被白名單，是 actively used 工具。
- **UC 引用**：SM-5

### 修改要點
1. 讀 `~/.claude.json` 的 top-level `mcpServers`，抄 4 個 server 定義（`web-search-prime` / `zai-mcp-server` / `web-reader` / `zread`）
2. 寫入 `~/.zcode/cli/config.json` 的 `mcp.servers`（保留既有 `context7`）
3. **跨 harness 相容性已驗證**（ep-validate 查證）：4 個 MCP 都是 http/stdio+npx 無 Claude-specific 依賴，ZCode schema 支援 http type（mosaic_alpha lsp-python 證實）→ 直接抄即可。

### 驗證
- `python3 -c "import json; print(list(json.load(open('/Users/ctai/.zcode/cli/config.json'))['mcp']['servers'].keys()))"` 確認 5 個 server
- 重啟 ZCode → 觀察 session 啟動 log 確認 `mcpServerCount:5`
- 跑 `mcp__web-reader__webReader`（或 ZCode 等價工具呼叫）確認連線

### 風險
- **MCP 跨 harness 相容性已驗證**（ep-validate 查證）：4 個 MCP 都是 `http`（z.ai API + Bearer token）或 `stdio + npx`（npm 套件），**無 Claude-specific 依賴**。ZCode schema 支援 `type: http` + `headers`（mosaic_alpha lsp-python 已證實運作）→ 4 個 MCP 可直接抄。
- **zai-mcp-server 的 apiKey**：若需 apiKey 從 Claude env 帶，ZCode 端要另外配

---

## S2: shioaji marketplace + plugin

### Context
- **背景**：Claude `settings.json` 有 `extraKnownMarketplaces: { shioaji-plugins: { source: { github: Sinotrade/Shioaji } } }` + `enabledPlugins: { shioaji@shioaji-plugins: true }`。ZCode `known_marketplaces.json` 僅 claude-plugins-official 1 個，無 shioaji。
- **影響**：台股交易 API（shioaji）工作流在 ZCode 完全斷。
- **UC 引用**：SM-6

### 修改要點
1. 讀 `~/.zcode/cli/plugins/known_marketplaces.json`，加 shioaji-plugins entry（source: github Sinotrade/Shioaji）
2. 用 ZCode GUI Settings → Plugin Management 安裝 shioaji（或寫入 config.json 的 enabledPlugins）
3. **風險**：ZCode plugin 載入機制可能與 Claude 不同（之前發現 plugin hooks 對 native ZCode Agent 也無效，但 plugin 提供的 skills/commands/MCP 可能仍可用）

### 驗證
- `cat ~/.zcode/cli/plugins/known_marketplaces.json` 確認 shioaji-plugins 加入
- 重啟 ZCode → GUI Settings → Plugin Management 確認 shioaji 出現並可啟用
- 啟用後跑 shioaji 工具（如 `mcp__shioaji__*` 或 skill invoke）確認運作

### 風險
- **shioaji plugin 可能含 Claude-specific hooks**：若 plugin 的 hooks 對 native Agent 無效（#32 結論），但 skills/commands/MCP 仍可用 → 可接受（hooks 部分為已知限制）
- **shioaji 可能需 API credentials**：台股券商帳號可能在 Claude env 已配，ZCode 端要另外設定

---

## S3: 文件化 LSP 跨 harness 結論（無統一載體）

### Context
- **背景**：各家 harness 有自己的 LSP 機制，**無統一跨 harness 載體**：
  - **Claude Code**：原生內建 LSP plugin 系統（`claude-plugins-official` 有 12 種語言：pyright/rust-analyzer/clangd/gopls/jdtls/csharp/kotlin/lua/php/ruby/swift/typescript）。全域，影響所有專案。
  - **OpenCode**：原生內建 LSP（使用者補充，機制待考）。
  - **ZCode**：官方 plugin 無 LSP。mosaic_alpha 已用自建 `lsp-python` MCP server（http://127.0.0.1:8000，`tools/lsp_mcp/`）**替代**——per-project workspace（`x-workspace-id` header 路由），6 個 tool（hover/definition/references/diagnostics/rename_symbol/edit_file）。
- **ai-rules 純文檔 repo**：僅 3 個獨立 .py 腳本（`hooks/block-python-c-comment.py` / `ref-docs/harness/crawl.py` / `scripts/deploy_agents.py`），無跨檔依賴，不需 LSP。
- **UC 引用**：無新 UC，是 04 報告 §7 的內容補充

### 修改要點
在 `ai-analysis/reports/superpowers/04-multi-harness機制對照.md` §7 補一小節「LSP 跨 harness 載體結論」：
- **結論（修正）**：LSP **無統一跨 harness 載體**。Claude/OpenCode 原生內建；ZCode 無原生，需自建 MCP server 替代（mosaic_alpha 的 `lsp-python` 是先驅案例，非通用解）。
- **mosaic_alpha `lsp-python` 的價值**：ZCode 端的替代方案，per-project + 可控（自建 6 tool）；**不是跨 harness 標準**（Claude/OpenCode 用原生反而更簡單）。
- **ai-rules 場景**：純文檔 repo，LSP 無價值（3 個獨立腳本無跨檔依賴）。

### 驗證
- `rg "LSP 跨 harness" ai-analysis/reports/superpowers/04-multi-harness機制對照.md` 確認段落加入
- `/consistency` 跑 04 報告

---

## S4: `~/.agents/commands` symlink 補建 + 文件化 hooks 不可遷移（修訂）

### Context
- **背景（commands）**：`~/.agents/skills` 已 symlink → repo skills/，但 `~/.agents/commands` 不存在。`zcode-configuration-guide` skill 列 `~/.agents/commands` 為掃描路徑之一。
- **背景（hooks 文件修訂）**：04 報告 §7 目前寫「configuration-file hooks 不支援」，但 hooks 衝突查證證實**plugin hooks 也對 native Agent 不支援**（#32 回報者測過）→ 需修訂為「hooks 在 ZCode 端完全不可遷移」。
- **UC 引用**：SM-1（hooks 不觸發 = 已知限制）

### 修改要點
1. `ln -s /Users/ctai/Github/ai-rules/commands ~/.agents/commands`
2. 在 `ai-analysis/reports/superpowers/04-multi-harness機制對照.md` §7 修訂 hooks 結論：
   - 原：「configuration-file hooks 不支援（官方 issue #32）」
   - 改：「hooks 在 ZCode 端完全不可遷移——configuration-file hooks 對 native Agent 不觸發，plugin hooks 也對 native Agent 不支援（[`zai-org/feedback#32`](https://github.com/zai-org/feedback/issues/32) 回報者測過兩者）。binary 有 hooks 基礎設施（RPC channel 註冊）但 native Agent 路徑不分派事件。hooks 是 Claude 專屬功能，跨 harness 用 rules/skills/commands 替代。」
3. 對應更新 `AGENTS.md` 的 hooks 條目措辭（強化「完全不可遷移」結論）

### 驗證
- `ls -la ~/.agents/commands` 確認 symlink 建立
- `ls ~/.agents/commands | wc -l` 確認 34 個 command 進入
- `rg "完全不可遷移" ai-analysis/reports/superpowers/04-multi-harness機制對照.md` 確認修訂
- `/consistency` 跑 04 報告 + AGENTS.md

---

## 收尾步驟

1. **AGENTS.md / CLAUDE.md 反映新狀態**：
   - hooks 條目措辭修訂（完全不可遷移）
   - 不需動 skills/commands 結構（已跨 harness）
2. **04-multi-harness機制對照.md §7 補「遷移結果」**：
   - hooks：不可遷移（binary bug）
   - MCP：補齊 4 個（S1）
   - LSP：無統一跨 harness 載體（Claude/OpenCode 原生內建；ZCode 需自建 MCP server 替代）
   - commands：`~/.agents/commands` symlink 補建（S4）
3. **部署面驗證**：
   - 4 個 MCP server 連線（S1）
   - shioaji plugin 載入（S2）
   - `~/.agents/commands` symlink（S4）

---

## 整合驗證（dry run = SM-7 + SM-8，用戶指定）

依用戶選擇，最終驗證跑 `code-review → judge-review → commit` 工作流：

1. **製造一個小變更**：在 ai-rules repo 加一個無害註解（如 04 報告加一行 `<!-- dry-run test -->`）
2. **跑 `/code-review`**：
   - 確認 slash command 觸發（commands symlink 路徑）
   - 確認 Skill invoke（review-engine 等）
   - 確認 Bash 執行（rg / git status）
   - 確認 TodoWrite 運作
3. **跑 `/judge-review`**（若有 findings）：
   - 確認持久化寫入（`.review/main.md`）
   - 確認語音 sentinel 邏輯（雖 hooks 不可遷移，但 LLM 主動 `say` 仍可行）
4. **跑 `/commit`**：
   - 確認 commit-consent 流程（展示再確認）
   - 確認 git commit 執行
5. **全程驗證**：
   - ✅ 無權限卡關（yolo + 紅線安全網運作）
   - ✅ hooks 不響（hooks 不可遷移的預期行為，非 bug）
   - ✅ MCP 工具可用（S1 補齊後 web-reader 等）

---

## 風險與降級

| 風險 | 機率 | 降級路徑 |
|------|------|---------|
| S1 zread MCP 跨 harness 不相容（依賴 Claude plugin 環境） | 中 | 標記「需另建 ZCode 版本」，其他 3 個 MCP 仍補 |
| S2 shioaji plugin 含 Claude-specific hooks | 低 | skills/commands/MCP 部分仍可用，hooks 部分為已知限制 |
| S2 shioaji 需券商 credentials | 中 | 記錄為「需另配 credentials」，plugin 結構先就位 |
| dry run 在 ZCode 觸發但流程卡住 | 低 | 記錄卡住點，轉為下次 EP |

---

## 驗證策略（docs mode）

- **rg 閘門**：
  - `rg "完全不可遷移" ai-analysis/reports/superpowers/04-multi-harness機制對照.md`（S4 修訂驗證）
  - `rg "LSP 跨 harness" ai-analysis/reports/superpowers/04-multi-harness機制對照.md`（S3 補段驗證）
- **`/consistency`**：跑 04 報告 + AGENTS.md（S3/S4 文件變更）
- **部署面閘門**：
  - `python3 -c "import json; print(len(json.load(open('/Users/ctai/.zcode/cli/config.json'))['mcp']['servers']))"` → 預期 5
  - `cat ~/.zcode/cli/plugins/known_marketplaces.json | python3 -c "import json,sys; print(list(json.load(sys.stdin).keys()))"` → 預期含 shioaji
  - `ls ~/.agents/commands` → 預期 34 entries
- **dry run**：S1-S4 完成後跑 SM-7 + SM-8 整合驗證

---

## EP Review Findings

> `/ep-review` 標準模式審查（effort=standard, workflow=false, Main LLM）。每條 finding 已查證磁碟實況。

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| R1 | 🔴 必須修正 | S1 / S3 / V1 查證證據 | **關鍵證據檔案不存在**：EP 三處引用 `mosaic_alpha/.zcode/config.json` 的 lsp-python MCP 作為「ZCode 支援 http MCP schema」實證（行 88「mosaic_alpha lsp-python 證實」/ 行 96「已證實運作」/ 行 248 查證證據）。磁碟查證：`mosaic_alpha/` repo **無 `.zcode/` 目錄**（`fd -t d '\.zcode' /Users/ctai/Github/mosaic_alpha/` → 0 hits），只有 `tools/lsp_mcp/`（原始碼）+ `ai-analysis/execution-plans/ep-python-lsp-mcp-server*.md`（規劃文件）。→ S1 V1「跨 harness 相容性已驗證」的證據鏈斷裂 | build 前**重新查證** mosaic_alpha 是否實際部署 lsp-python MCP（可能路徑：`.agents/mcp.json` / 該專案 workspace 設定 / 從未部署只是規劃）。若無實證 → S1 改回「待驗證」並加 POC 步驟（跑一個 MCP 補上、重啟、確認連線） | needs-confirmation |
| R2 | 🟡 建議討論（採納） | S4 修改要點 3 / 收尾步驟 1 | **部分修訂已是 no-op**：S4 宣稱要「修訂 AGENTS.md hooks 條目為『完全不可遷移』」。磁碟查證：`AGENTS.md:74` **已寫**「configuration-file **與 plugin hooks** 對 native ZCode Agent **皆無效**」— 此修訂已完成（非新工作）。**04 報告 §7 行 200 標題仍寫「configuration-file hooks 不支援（官方確認）」**，內文行 205 雖提及「plugin hooks 也測過無效」但標題未升級 → 只有 04 報告標題修訂有實質工作 | S4 拆為兩部分：(a) AGENTS.md hooks 條目 = **no-op 標註**（避免 build LLM 誤以為是待辦）；(b) 04 報告 §7 標題 + 結論段修訂 = **唯一實質工作** | implemented |
| R3 | 🔴 必須修正 | EP 標題 + S3 | **EP 標題列 LSP，但 S3 只「文件化結論」未處理實際差距**：上一輪系統化檢查發現 `~/.zcode/AGENTS.md` 含 7 處 LSP 指令（4 條 neutral rules 洩漏 — `instruction-writing.md` 15 處最嚴重、`llm-output-convention.md` 1 處、`collaboration-constraints.md` 1 處、`rules/AGENTS.md` 1 處），ZCode LLM 讀到會嘗試呼叫不存在的 LSP tool。EP S3 只文件化「LSP 跨 harness 無統一載體」，**未修正這些洩漏指令**。SM-8 dry run 跑 `/judge-review` 時會在「符號查證優先 LSP findReferences」步驟觸發此問題（EP 行 91 引用 lsp-navigation.md 是 claude-specific 不會載入，但 neutral rules 洩漏的指令會） | 兩選項：(a) **擴大 S3 scope**：除文件化結論外，加一步「盤點 neutral rules 內 LSP 指令，改寫為『符號查詢：Claude 用 LSP / 其他 harness 用 rg + workspaceSymbol-equivalent』」；(b) **正式 scope out 並改 EP 標題**：標題移除 LSP，另開 EP 處理 LSP 洩漏。**當前 EP 標題與 S3 scope 不符** | needs-confirmation |
| R4 | 🟡 建議討論（採納） | SM-8 / 整合驗證步驟 1 | **dry run 製造的變更選擇不當**：EP 行 189 製造「在 04 報告加 `<!-- dry-run test -->`」做為 review 標的。但 04 報告本身是 S3/S4 要修改的目標檔，dry-run test 行會與 S3/S4 變更混在 diff，code-review 會看到混合變更。dry run 目的是驗證 commands symlink + skill invoke + bash 連鎖，**任何變更都可以**，不需要動 04 報告 | 改用無關檔案（如暫時加 `README.md` 一行註解，dry run 完刪除）或**直接用 S3/S4 自己的變更做 dry run**（更真實，且不製造人工測試痕跡） | implemented |
| R5 | 🟡 建議討論（未確認） | S1 風險段 | **apiKey 處理僅「另配」未給降級路徑**：行 97 提「zai-mcp-server 的 apiKey：若需 apiKey 從 Claude env 帶，ZCode 端要另外配」但未說如何查 Claude 配置 + 如何寫入 ZCode config。build 時會卡在實際看 Claude config 才發現 token 來源 | build 前 `python3 -c "import json; m=json.load(open('/Users/ctai/.claude.json')); print({k:v.get('env',{}) for k,v in m['mcpServers'].items()})"` 查 4 個 MCP 的 env/config 結構，預先標記哪些需要 token + token 來源 | needs-confirmation |
| R6 | 🟢 提醒 | S4 驗證段 | **commands 數 34 驗證條件不準確**：`ls ~/.agents/commands \| wc -l` 計算包含子目錄（如 `instruction/`）+ `CLAUDE.md`（非命令）。實測 `commands/*.md` = 34 但涵蓋非命令檔 | 改用 `fd -e md commands/ \| wc -l` 或明文「34 個 .md 檔（含 instruction/ 子目錄與 CLAUDE.md wrapper）」 | implemented |

### 回寫紀錄

- ✅ R1（resolved）：build 實測 `mosaic_alpha/.zcode/config.json` EXISTS（含 lsp-python http MCP）。EP 查證用 `fd -t d '\.zcode'` 漏 `-H` flag → false negative（fd 預設不顯示隱藏目錄）。證據鏈閉合，S1 V1 成立。
- 🟡 R2（implemented）：S4 拆分已記錄（AGENTS.md = no-op、04 報告 = 實質工作）
- 🔴 R3（needs-confirmation）：LSP 洩漏議題超出 EP 預設 scope — 需用戶決策（擴大 S3 / 另開 EP / 正式 scope out）
- 🟡 R4（implemented）：SM-8 dry run 製造變更方式已修正（建議直接用 S3/S4 變更）
- 🟡 R5（needs-confirmation）：apiKey 查證步驟已加入建議
- 🟢 R6（implemented）：commands 數驗證條件已修正

## EP Validate Findings

> **結論**：docs mode EP，無致命技術假設，**無需 POC**（ep-validate.md:48「純配置文檔不需要」）。唯一技術不確定性（S1 MCP 跨 harness 相容性）已透過靜態查證解決。

| ID | 嚴重度 | EP 段落 | 問題（查證結果） | 建議 | 狀態 |
|----|--------|---------|----------------|------|------|
| V1 | 🟢 low | S1 | MCP 跨 harness 相容性：查證 Claude 5 個 MCP 都是 http/stdio+npx 無 Claude-specific 依賴；ZCode schema 支援 http type（mosaic_alpha lsp-python 證實）→ 4 個 MCP 可直接抄 | 修正 S1 風險評估（從「待驗證」改「已驗證可攜」） | verified |
| V2 | ℹ️ info | 全 EP | docs mode（config + .md 變更，無 .py logic）→ 無技術演算法假設需 POC 驗證 | 跳過 POC，直接進 `/ep-review` | verified |

**無 ❌ 假設錯誤 / 無 ⚠️ 部分通過** — EP 可直接進 `/ep-review`（靜態審查）→ `/build`。

### 查證證據

- `~/.claude.json` top-level `mcpServers`：5 個 server（web-search-prime / zai-mcp-server / web-reader / context7 / zread）
- `~/.zcode/cli/config.json`：現有 context7（stdio+npx，運作中）
- `mosaic_alpha/.zcode/config.json`：lsp-python 用 `type:http` + `headers`（證實 ZCode 支援 http MCP schema）
