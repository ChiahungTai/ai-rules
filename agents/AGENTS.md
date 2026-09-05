# agents/ — 跨 harness subagent 定義

> 部署＝registry 視圖：`~/.zcode/agents` symlink → `agents/zcode/`、`~/.claude/agents` → `agents/claude/`。與 hooks/ 不同（config 引用、無目錄載入點），subagent 兩家都是**目錄載入點**，symlink 成立。ZCode 設定 UI 的新建/編輯會穿頂層 symlink 寫入 `agents/zcode/`（= 產生 repo working tree diff，屬預期行為）。

## registry 結構（per-harness 指定＝registry membership）

```
agents/
  roles/    # role authoring 單一源（frontmatter 白名單 name/description/tools/background＋零 model/
            #   thoughtLevel 鍵——正文 prose 豁免；body：①目標 ②做法 ③角色特定節〔紀律/方法論等，
            #   skills 引用 inline 散在 body〕）
  zcode/    # 生成物（~/.zcode/agents → 此）：roles 投影＋部署預設 pins（lite/vision 帶 model+thoughtLevel）
  claude/   # 生成物（~/.claude/agents → 此）：roles 投影（省略 model/thoughtLevel；tools 減 CR MCP 行）
```

- **「指定哪個 harness 用哪些 agent」＝role 出現在哪些 registry**（機制，非命名紀律）。**registry 內是實檔拷貝非 symlink**——ZCode registry 不載入 file-level symlink（2026-08-29 對照實驗定案：目錄 symlink 可穿透〔頂層 ~/.zcode/agents → agents/zcode 生效〕、檔案 symlink 靜默不載；hardlink 被 clone 破壞不可用）
- **同步紀律（生成式）**：**只改 `roles/`**，改完 `uv run python scripts/sync_agents.py` 重建兩 registry；`--check`＝唯讀 drift gate（生成物 vs roles 不一致→exit 1 列清單，check_single_source 有 invariant 接線）；`--map`＝role→registry 可用性表（文字表機械對帳源）；stale cleanup 只刪 marker-owned 生成物——**unmarked 檔是人工檔，永不自動刪**，與 expected 同名的 unmarked 檔＝fail loud（防 fork 被靜默收編）。**已知刻意分歧（2026-08-30 T2-3，由生成器承載）**：claude 拷貝 tools 減 CR MCP 白名單行（`mcp__plugin_code-reality_code-reality__*` 四顆）
- **pin 單一源紀律**：zcode/ 生成檔的 pins 由 `sync_agents.py` 部署預設表給出（requirement 分類〔tier 詞 full/vision/lite〕由 `--map` 表承載），值抄 model-routing skill tier×provider 權威表（zai 欄＋部署填法 effort），runtime parity guard 對該表校驗（model＋effort 雙層）——改表 → 改 sync_agents dict → 重跑 sync
- **UI 防護規則**：不在 ZCode 設定 UI 編輯 registry 檔（model／思考強度／正文皆然）——zcode/claude/ 是**生成物**（檔頭 ownership marker 標記），UI 編輯會被下次 sync **無預警覆蓋**；要改角色 → 改 `roles/` 源；要改 pins → 改 sync_agents 部署預設表（**在 zcode/ 建 fork 已非合法形態**——同名 unmarked 檔會擋 sync）
- **tier 命名**：能力語義命名（lite-verify／spec-miner，非具體模型名-*——model 每代換名，改名級聯）；例外＝rescue 類（引擎在本質內，如 codex-rescue）。tier 詞彙定義在 `rules/model-routing.md`，此處引用不自帶
- **生效時機**：ZCode 改動需新建 session（快照制；app 重啟續接同對話亦刷新）；CC 定義檔即時監聽。翻轉頂層 symlink／更新 registry 拷貝後以首個新 session 驗證
- **external-runtime 職責**：本 registry 亦承載 external-runtime 委派的入口指派（family／profile 映射見 `skills/model-routing/SKILL.md`，詞彙定義見 `rules/model-routing.md` tier 詞彙句）；詳見下節 thin forwarder 與 flag profile。

## Thin forwarder 與 flag profile

> 治理原則：external-runtime 家族入口＝單一 thin forwarder（工單即介面），**不長特化 agent**——routing 混入 transport agent 的前車之鑑（`~/Github/muse-plugin-cc/FIX-S3-R2.md:49`）。跨 harness agent 定義保持 thin，路由決策與解析表在 `skills/model-routing/SKILL.md`（詞彙定義在 `rules/model-routing.md`），flag 具體值見同 skill 解析表，工單協議在 `skills/_common/work-order.md`。

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

- **muse 委派必經 bridge——預設形態＝主 session 直呼 bridge CLI**：背景 Bash 掛 bridge 阻塞呼叫（`task` 阻塞形或 `wait <jobId>`）→ process exit 喚醒主 session、stdout 即終局輸出；`.muse-bridge/jobs.json`／`ps` 核對降級為**診斷手段**（非收法）。繞開 wrapper 生命週期錯位——wrapper 在 runtime 未終局時提前 complete 是系統性常態（本弧實證：muse×2＋codex×2 均需介入），直呼橋接層不經 wrapper 轉發；wrapper agent 形態為別名（alias）。「必經」＝禁繞過 bridge 直呼 `muse exec` 等（ledger 可考性——規範單一源見 `skills/model-routing/SKILL.md`「bridge 必經」）
- **codex 委派＝主 session 背景 Bash 直呼 `codex-companion task`（阻塞形）＋prompt 內預寫 env fallback**：prompt 內預寫 plugin root 路徑的 env 兜底（`CLAUDE_PLUGIN_ROOT` 缺失時 `MODULE_NOT_FOUND` 形態）不變；wrapper 保留 prompt 工程場景（wrapper 內單次阻塞 `task`）——wrapper Bash 10min 上限是約束事實、wrapper≠job 錯位是獨立實證、兩者因果未驗證，預期超時的工單改走直呼
- **LLM 層 fallback 紀律（罕見——原始派發無背景 Bash 掛載時；前景短 arm 仍可用）**：ETA-gate——推估完成時刻前零檢查（一段 `--timeout <eta>` arm）；屆時單次檢查；未終局 → 重掛遞減 timeout 的阻塞 wait arm（起點＝bridge 預設 5min／4min，按 ETA 緊化至 ~30s 級；每 arm 到期＝1 request）——永不做 LLM 層定時輪詢
- **收法經濟學**：LLM 層輪詢每輪＝1+ request 且全 context 重送；push 收法等待期間 0 request、完成時恰好 1 request

> 長跑兩段式（`--background` 拿 jobId → 掛 `wait`）與 timeout 到期訊號拆家系（muse 5min＝exit 124；codex 4min＝正常 exit 0＋`waitTimedOut` 旗標、無 0=forever）見 `skills/model-routing/SKILL.md`「完成回報收法」決策樹。

### 三態判定（症狀→證據→處置）

| 症狀 | 證據 | 處置 |
|------|------|------|
| transport 未啟動 | env/module 錯誤、log `MODULE_NOT_FOUND`、exit 1、jobs.json 無該 job | 可安全重派 |
| transport 在跑、wrapper 已收 | jobs.json 狀態 running、ps 進程在 | 背景 Bash 掛阻塞 `wait` 收，禁重派（雙跑） |
| transport 死中途、wrapper 空轉 | 進程已亡、jobs.json 停滯、無新輸出 | 機械驗收（working tree＋jobs.json 終局）＋TaskStop wrapper |

## 全生命週期 execution contract

> 每個生命週期段必有一行 contract：stage → owning orchestrator → registry name → tier → harness registry → artifact → failure fallback（AIR-28）。**「dispatch 給適合的執行者」含主 session**——判斷密集段（EP 規劃／judge 裁決／post-build 編排／commit consent）依 AIR-24 分工律由 full 主 session 執行，不 agent 化。消費側規範（各命令怎麼查表 dispatch、spawn 形態）單一源在 `skills/agent-workflow/SKILL.md`，本表是主體。

| stage | owning orchestrator | registry name | tier | harness registry | artifact（輸入→輸出） | failure fallback |
|-------|--------------------|---------------|------|------------------|----------------------|------------------|
| 開卡（backlog 建卡＋建卡 commit） | 主 session 直做 | — | full | — | 任務敘述→卡檔＋commit | —（機械命令，kanban-board skill） |
| 研究（EP 段落 0／規格挖掘） | spawn | cr-research／spec-miner | lite | zcode | 問題→file:line 錨點＋逐字引用 | 重試≤2（1302）→主 session 自做 |
| EP 規劃 | 主 session 直做（判斷密集） | — | full | — | 需求→ep.md（含 EP review 迴圈） | — |
| EP review（雙家族） | 主 session 編排：GLM 側 spawn code-reviewer×2；muse 側**背景 Bash 直呼 bridge（不佔 agent 並發）** | code-reviewer（fresh）＋code-reviewer-primed（primed）；muse review（bridge 工單） | full（省略 model）為基準；條件式降 lite（保護面厚度，model-routing skill） | zcode＋claude（生成）；muse 經 bridge | diff＋EP→findings→judge 處置表 | classifier／1302 重試≤2→顯式降級記錄；muse 額度不足→in-harness 雙 context（顯式記錄） |
| build 實作段 | 主 session 編排；機械可規格化段 spawn | impl-flash | lite | zcode | EP 段→code＋測試＋驗證證據 | 失敗家系處置（註 a）→主 session 直做該段；lite 測試＝規格陳述→驗收證據 full 複驗 |
| build 內 Agent Review | spawn（3-perspective） | code-reviewer（fresh）＋code-reviewer-primed（primed）；Important+ 錨點驗證＝lite-verify | reviewers＝full（省略 model）為基準；錨點驗證＝lite | 全 zcode＋claude（生成） | diff→findings（錨點驗證後浮出） | 失敗家系處置（註 a）→主 session 自審＋fallback 標記 |
| judge 裁決 | 主 session 直做（判斷密集；不派 agent） | — | full | — | findings→✅/❌/⚠️ 處置表 | — |
| post-build 編排 | 主 session 直做（判斷密集） | — | full | — | 收尾鏈：code-review（dual-context）→judge-review→修正→consistency→metadata-sync→殼 refresh | — |
| 機械驗證／consistency gate | spawn | lite-verify | lite | zcode | 查證清單→逐項機械證據（rg 命中／exit code／file:line） | 失敗家系處置（註 a）→主 session 跑組合命令 |
| 視覺驗收 | spawn | vision-review | vision | zcode | 圖檔→逐張 verdict | 失敗家系處置（註 a）→標「未驗證」（禁主 session 直讀圖） |
| archify 圖渲染 | spawn | archify-gen | lite | zcode | 機械底稿→workflow/architecture/sequence 圖＋HTML＋殼槽位換裝（**只接 archify 圖**——mermaid/HTML 塊不派此 agent，由主 session 產，mmdc 是機械 CLI；選型判準 diagram-selection skill） | 失敗家系處置（註 a）→主 session 手產＋vision 驗收照跑 |
| 多源查證 | spawn | cross-verify-investigator | lite | zcode | 問題＋軸清單→交叉對帳 verdict＋unverified | 軸源缺場→該軸 unverified 不阻斷（skills/cross-verify） |
| commit preparation | 主 session（對帳可 spawn） | lite-verify（finalization 對帳） | lite | zcode | working tree→對帳清單＋訊息草稿 | 主 session 直做 |
| **commit consent＋執行** | **主 session 互動（永遠；任何 dispatch 不覆蓋）** | — | full | — | 草稿＋變更摘要→用戶確認→git commit | —（outward-action-consent rule；autonomous 紅線清單例外見該 rule） |
| memory 結案蒸餾 | spawn | mem-distill | lite | zcode | 肥大條目→收斂重寫 | 主 session 直做（寫入六問自檢） |

- **commit 拆兩半**：preparation（finalization 對帳、訊息草擬——agent 可做）＋consent gate（主 session 互動——永遠，contract 表其他行不覆蓋此行）
- **註 a（spawn 失敗態家系——重試語義單一源）**：見 model-routing skill「spawn 失敗態辨識」——1302／classifier unavailable 重試≤2；1301 禁同 prompt 重試；1308 等窗口重置（重置前重派無效）；429 走 backoff／降並發。**禁把「重試≤2」泛化到全失敗類**（實例：1308 重派只會再敗）
- **CC dispatch**：本表 registry name 欄的全名在兩 registry 皆生成在場——CC `--agent <name>` 全 10 名可用；未知名稱仍立即退出（反向守衛）

### registry projection map

> 跨 harness 可用性的**機械對帳源＝`uv run python scripts/sync_agents.py --map`**（輸出 role／requirement／zcode／claude 四欄表）；本節文字表是導覽副本，drift 以 --map 為準。生成後全 10 role 在兩 registry 皆在場（roles/ 單一源→雙投影）。

| agent | requirement | zcode | claude | 備註 |
|-------|-------------|-------|--------|------|
| code-reviewer | full | ✅ | ✅ | claude 拷貝 tools 減 CR MCP 行（生成器承載的已知分歧） |
| code-reviewer-primed | full | ✅ | ✅ | 同上 |
| cross-verify-investigator | lite | ✅ | ✅ | 軸＝prompt 參數（AIR-28 S3）；**去 MCP 化**（tools 不掛 CR MCP 全名——cr 軸走 CLI，避免 spawn 綁死「CR plugin 在啟動快照在場」，見下方 tools 清單陷阱） |
| archify-gen | lite | ✅ | ✅ | — |
| cr-research | lite | ✅ | ✅ | — |
| impl-flash | lite | ✅ | ✅ | **範式但書**：其 tools 行含 `Grep`/`Glob`——ZCode 靜默忽略死欄（見「tools 清單陷阱」），新定義不照抄，文字/檔案搜尋走 Bash rg/fd |
| lite-verify | lite | ✅ | ✅ | — |
| mem-distill | lite | ✅ | ✅ | — |
| spec-miner | lite | ✅ | ✅ | — |
| vision-review | vision | ✅ | ✅ | 影像需求——pin 禁降非影像款（生成期防線） |

## harness 軸（dispatch matrix——每家怎樣調用 role）

> dispatch 兩跳：先選 harness（本表），再在該 harness 綁定的 provider 內按 requirement 查 [model-routing](../skills/model-routing/SKILL.md) tier×provider 權威表取 model+effort。role 定義單一源＝`roles/`（見 registry 結構節）。

| harness | provider 綁定 | 調用形態 | role 來源 | evidence status |
|---------|--------------|---------|-----------|----------------|
| zcode | zai | registry spawn（背景；快照制——新 session 載入） | `agents/zcode/` 生成檔（pins＝部署預設） | repo-observed |
| cc（Claude Code） | zai（**本機配置**——CC 當前掛 GLM backend；原生家 Anthropic 未訂閱，訂閱後視性價比重配） | `--agent <name> --bg` named-agent＋Agent tool（spawn-time model/effort） | `agents/claude/` 生成檔 | repo-observed（2.1.261 實測：named-agent 可用、未知名稱即退出；session 跑 glm-5.3） |
| muse code | meta | **雙身分**：user 直用開發 harness（該弧主力，muse-spark-1.3 全棧）＋ ZCode 端 bridge 工單委派（`task`／`review`，必經） | 直用＝repo AGENTS.md 載入（全域部署點未查證）；委派＝roles/ body 填工單 Role contract（work-order §2） | repo-observed |
| codex（companion） | OpenAI | companion `task` 工單（`--model`/`--effort` passthrough） | 同上 | repo-observed |
| grok-build | xai | 工單（同族委派 plugin 形態） | 同上 | **未安裝**·dispatch contract 未證實〔hooks/AGENTS.md〕——引用前先查證，不得假設可用 |

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
