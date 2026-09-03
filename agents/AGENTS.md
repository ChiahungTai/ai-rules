# agents/ — 跨 harness subagent 定義

> 部署＝registry 視圖：`~/.zcode/agents` symlink → `agents/zcode/`、`~/.claude/agents` → `agents/claude/`。與 hooks/ 不同（config 引用、無目錄載入點），subagent 兩家都是**目錄載入點**，symlink 成立。ZCode 設定 UI 的新建/編輯會穿頂層 symlink 寫入 `agents/zcode/`（= 產生 repo working tree diff，屬預期行為）。

## registry 結構（per-harness 指定＝registry membership）

```
agents/
  shared/   # 內容切片（authoring 單一源）：跨 harness 角色定義（model 省略＝inherit、零 harness 專屬欄位）
  zcode/    # ZCode registry（~/.zcode/agents → 此）：shared 檔的實檔拷貝（sync 產物）＋ ZCode 專屬實體檔（tier-pinned）
  claude/   # CC registry（~/.claude/agents → 此）：shared 檔的實檔拷貝（sync 產物）＋ CC 專屬實體檔（暫空——CC 分層走 spawn-time）
```

- **「指定哪個 harness 用哪些 agent」＝哪個檔出現在哪個 registry**（機制，非命名紀律）。**registry 內是實檔拷貝非 symlink**——ZCode registry 不載入 file-level symlink（2026-08-29 對照實驗定案：目錄 symlink 可穿透〔頂層 ~/.zcode/agents → agents/zcode 生效〕、檔案 symlink 靜默不載；hardlink 被 clone 破壞不可用）
- **同步紀律**：shared/ 是 authoring 單一源——**只改 shared/**，改完 `cp` 到 zcode/＋claude/（三份一起 commit）。**已知刻意分歧（2026-08-30 T2-3）**：ZCode 專屬 CR MCP 白名單行（`mcp__plugin_code-reality_code-reality__*` 四顆，只加在 frontmatter tools）——zcode 拷貝＝shared 全文；**claude 拷貝＝shared 減 MCP 行**（CC 接線未確認是前置，確認後同步補）。sync 檢查＝`cmp shared/<f> zcode/<f>` ＋ claude 差異僅限 MCP 行（`diff shared/<f> claude/<f>` 只出 tools 行的 `mcp__plugin_code-reality_*` 片段）
- **pin 單一源紀律**：zcode/ 檔的 `model:`／`thoughtLevel:` 值以 model-routing skill（`skills/model-routing/SKILL.md`）tier 解析表為單一源——改表 → `rg` 同步 zcode/ pins（角色→tier 表與 tier 詞彙仍在 `rules/model-routing.md`）
- **UI 防護規則**：shared 角色不在 ZCode 設定 UI 編輯（model／思考強度／正文皆然）——UI 編輯落在**拷貝**上，shared/ 不變，下次同步 `cp` 會**無預警覆蓋** UI 編輯；要釘模型 → 在 zcode/ 建 fork（tier-pinned 實檔，不經同步）
- **tier 命名**：能力語義命名（lite-verify／spec-miner，非具體模型名-*——model 每代換名，改名級聯）；例外＝rescue 類（引擎在本質內，如 codex-rescue）。tier 詞彙定義在 `rules/model-routing.md`，此處引用不自帶
- **生效時機**：ZCode 改動需新建 session（快照制；app 重啟續接同對話亦刷新）；CC 定義檔即時監聽。翻轉頂層 symlink／更新 registry 拷貝後以首個新 session 驗證
- **external-runtime 職責**：本 registry 亦承載 external-runtime 委派的入口指派（family／profile 見 `rules/model-routing.md` external-runtime 節與 `skills/model-routing/SKILL.md` 解析表）；詳見下節 thin forwarder 與 flag profile。

## Thin forwarder 與 flag profile

> 治理原則：external-runtime 家族入口＝單一 thin forwarder（工單即介面），**不長特化 agent**——routing 混入 transport agent 的前車之鑑（`~/Github/muse-plugin-cc/FIX-S3-R2.md:49`）。跨 harness agent 定義保持 thin，路由決策在 `rules/model-routing.md`，flag 具體值在 `skills/model-routing/SKILL.md`，工單協議在 `skills/_common/work-order.md`。

- **原則**：muse／codex 家族不新增特化 agent 定義檔；任務以工單為介面派發（派發形態見下方 dispatch face 與收法——muse 預設直呼 bridge CLI，wrapper 為別名），profile 決定 spawn 形態。
- **flag profile 表（形態）**：具體值見 `skills/model-routing/SKILL.md` external-runtime 解析表，本表只寫形態。

| profile | family | spawn 形態 | 說明 |
|---------|--------|------------|------|
| advisory | muse | read-only（bridge 暴露 `--disable-write` 前由工單紅線承載，暴露後改 flag） | 唯讀掃描，禁寫入 |
| implement | muse | `trust-workspace` | 實作寫入型，背景跑 |
| implement | codex | `workspace-write` | 診斷／救援寫入型 |
| review | muse | bridge `review` 子命令（schema verdict） | 產出 accept／reject／needs-fix |
| review | codex | `--output-schema` | 同上，codex 形態 |

> 外部 runtime flag 未暴露項的對策：以工單紅線替代（見 `skills/_common/work-order.md` 紅線首段），flag 暴露列 muse-plugin-cc 側 bridge roadmap（本 repo 不動跨 repo，僅記錄）。

### dispatch face 與收法

- **muse 委派預設＝主 session 直呼 bridge CLI**：背景 Bash＋`.muse-bridge/jobs.json` 輪詢（`rg .muse-bridge/jobs.json`＋`ps` 進程核對），繞開 wrapper 生命週期錯位；wrapper agent 形態為別名（alias），續用時收法＝resume-to-poll。理由：wrapper 在 runtime 未終局時提前 complete 是系統性常態（生命週期錯位，本弧實證：muse×2＋codex×2 均需介入），直呼橋接層不經 wrapper 轉發、終局以 jobs.json 與 working tree 為準
- **codex 委派＝wrapper＋標準收法 resume-to-poll＋prompt 內預寫 env fallback**：prompt 內預寫 plugin root 路徑的 env 兜底（`CLAUDE_PLUGIN_ROOT` 缺失時 `MODULE_NOT_FOUND` 形態），wrapper 標準收法同為 resume-to-poll

### 三態判定（症狀→證據→處置）

| 症狀 | 證據 | 處置 |
|------|------|------|
| transport 未啟動 | env/module 錯誤、log `MODULE_NOT_FOUND`、exit 1、jobs.json 無該 job | 可安全重派 |
| transport 在跑、wrapper 已收 | jobs.json 狀態 running、ps 進程在 | poll 收集，禁重派（雙跑） |
| transport 死中途、wrapper 空轉 | 進程已亡、jobs.json 停滯、無新輸出 | 機械驗收（working tree＋jobs.json 終局）＋TaskStop wrapper |

## 定義檔慣例

markdown + YAML frontmatter，正文 = 系統提示詞。兩家必填欄位同為 `name` / `description`（主 agent 依 description 決定何時委派 — 寫清楚觸發時機）。

### 欄位相容策略

| 類別 | 欄位 | 說明 |
|------|------|------|
| 直接共用 | `name` / `description` / `color` / `maxTurns` / `disallowedTools` / `tools` | tools 只列 built-in 共通名（Read / Bash / Edit / Write / WebFetch / WebSearch / TodoWrite）；`Grep`/`Glob` 是 Claude built-in 名，ZCode runtime 未注入但靜默忽略不報錯（見「tools 清單陷阱」） |
| 省略共用 | `model` | 省略 → 兩家皆 inherit 主 session（Claude 別名 sonnet/opus/... 在 ZCode 無效） |
| 可寫（ZCode 安全忽略） | Claude 專屬：`permissionMode` / `skills` / `hooks` / `memory` / `background` / `isolation` / `effort` / `initialPrompt` | ZCode 官方明說未知欄位靜默忽略不報錯 |
| 禁寫進共用檔 | ZCode 專屬：`thoughtLevel` / `injectAgentsMd` | Claude 對未知欄位容忍度未明 — 需要 per-harness 差異時另建 fork 檔 |
| 語義有差 | `mcpServers` | 兩家都吃名稱參考；ZCode 精確匹配、宣告未連接的服務直接失敗；**同名 server user-level 蓋 project-level**（官方文檔「項目配置覆蓋不了」——user 條目缺專案條目的 headers 會 shadow 專案設定，2026-08-22 實測險釀 lsp-python 回歸後回退）；Claude 另支援 inline 定義 |

### tools 清單陷阱（ZCode）

自訂 tools 清單會排除 **user-config MCP 工具**（設定 UI 勾選清單只含 built-in）；harness 隨附 MCP 不受 allowlist 影響（2026-08-22 實測：自訂清單下 `mcp__4_5v_mcp__analyze_image`、`mcp__web_reader__webReader` 仍注入，`mcp__context7__*`/`mcp__zread__*` 等全部排除——官方文檔「排除全部 MCP」宣稱不精確）。補救：手寫 `mcp__<server>__<tool>` 全名（萬用 `mcp__server__*` 無效靜默忽略——官方文檔宣稱；全名補救已本地驗證——2026-08-22 新會話 probe：5 個全名全部注入，context7 實呼成功、zread 工具存在可呼叫）。需要 MCP 的角色（如 lsp-python）**tools 留空**繼承全部。不認得的工具名靜默忽略、spawn 不報錯：`Grep`/`Glob` 寫進 tools 行在 ZCode 不注入（2026-08-22 probe 實測＋telemetry 全歷史數萬次調用零 Grep/Glob；官方文檔勾選清單仍列二者——文檔與 runtime 不一致）→ 共用定義可列兩家 union，ZCode 端文字/檔案搜尋由 Bash rg/fd 承擔。未連線 server 的全名則是 **spawn 直接報錯**（2026-08-22 實測：tools 列 `mcp__crg__*` 全名在非 mosaic session spawn 失敗，報 "Required MCP tool is not available in the parent startup snapshot" 並列出缺失工具）——全名補救只對 user-level server **且該工具在 spawn session 啟動快照在場**的形態安全；專案層 server（如 mosaic 的 CRG/lsp-python）全名跨專案即炸，不可寫進共用 user-level 定義，需要時另建該專案專用 fork 定義。**通則（2026-08-29 vision-review 實例）**：白名單掛任何 MCP 全名＝綁死「該工具在 spawn session 的啟動快照在場」——連 harness 隨附 MCP 都有不快照在場的 session 形態；跨 session 形態的 agent 定義應去 MCP 化（tools 留空繼承全部，或改 Bash/curl 等替代路徑）。

### 背景執行

長任務角色（review / research 類）建議 frontmatter 加 `background: true` — Claude 端強制始終背景執行（即使主 agent 需要結果）。ZCode **不認識此欄位**（靜默忽略）— ZCode 端背景化是 spawn 端行為：官方文檔僅說前台/後台由主 Agent 自行決定（無 UI 開關、無參數記載），Agent tool 的 `run_in_background: true` 參數為 runtime 實測有效（2026-08-14 session：背景 spawn 成功、主對話未阻塞）。

## ZCode 限制（共用定義的邊界）

- Beta 僅 user 級（無 workspace 層）；內建 `general-purpose` / `Explore` 名稱不可複用（不可建同名覆蓋檔 — Claude 端可以覆蓋 Explore，這是兩家不對稱點）
- 子智能體內**不能再派發子智能體**（Claude 可多層巢狀——官方文檔對深度上限記載版本間不一，勿釘死數字）→ 共用的系統提示詞不可依賴「spawn 下屬 agent」
- 定義修改不熱更新——快照在 session 啟動時建立（同 hooks 行為；2026-08-22 實測雙層快照：新檔案同 session 不進 registry、既有檔的 body 與 tools 修改同 session spawn 均不生效；重啟 app 後**續接同對話即刷新**——session id 不變但快照已更新，無需開新對話）
- 自 v3.7.1 起子智能體預設注入 user 級 + workspace AGENTS.md（與 Claude subagents 載入 CLAUDE.md layers 對稱）
- Beta 灰度上線 — 可用性以「設定 → 子智能體」面板實測為準

## Claude 限制

- 檔案監聽僅涵蓋 session 啟動時已存在的 agents 目錄 — 首次建立本目錄（symlink）後需重啟一次載入
- 需要隔離副本的角色用 `isolation: worktree`（ZCode 無對應，靜默忽略）
