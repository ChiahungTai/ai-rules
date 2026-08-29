# Skills 技術規範

> 本目錄承載**所有** on-demand 單元：領域知識 skills + 工作流 skills（原 slash commands，已全面遷移——ZCode 端 commands 非 AI first-class 僅可 Read，且 Claude 官方已將 custom commands 合併進 skills；兩端共用本目錄單一載入點）。

## 寫作原則

> **載入時機**：Skill 只在語意匹配觸發時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Skill 不支援 `@` transclusion。引用輔助檔案一律使用 `[描述](path)` markdown link
- **描述檔案內容**：讓 AI 判斷何時該跟隨 link 讀取，而非無條件載入
- **輸出格式模板**：是工作流 skill 的核心交付物規格，不算一般程式碼範例，可接受 >5 行
- **實作程式碼**：避免嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

## 架構

- `~/.claude/skills`、`~/.zcode/skills`、`~/.agents/skills` 三根符號連結指向本目錄，實現 Git 版本控制、跨專案共享和即時更新（ZCode 會同時掃 `.zcode` 與 `.agents` 兩根，清單內 skill 各出現兩次屬預期）。驗證：`readlink ~/.claude/skills`
- `skills/_common/` — 跨 skill 共用子範本（非 skill、無 SKILL.md）；skill 間以 `../_common/<file>` 相對路徑引用
- 工作流 skill 間互相引用以相對路徑 link（`../<name>/SKILL.md`）；散文中 `/name` slash 語意兩端皆有效（Claude slash 直調、ZCode Skill tool 調用）

## Skill 索引

> 現有 skills 依用途分組。Skill 靠 frontmatter `description` 語意匹配自動 discovery，本索引供「一眼看全」之用，非載入機制；詳見各 `skills/<name>/SKILL.md`。
>
> **⚠ drift-prone**：手動維護的現狀清單——新增/移除/改名 skill 需同步此索引，否則與 `skills/` 目錄漂移。可定期用 `skill-cleaner` 稽核。

### 核心開發流程（工作流拓撲）

```
〔pre-EP 軟 gate〕對話討論新功能 →〔提醒〕/illustrate 結構化提案（city map/重用，軟 gate 不硬擋）→ 人判讀 → 確認
/spec（純輔助·需求釐清，可選）→ /execution-plan（自足：段落0全域研究 + UC盤點 + EP Review, LLM 自判；引用 UC ID + SYSTEM-MAP）→ [/ep-validate（可選）]
          ↓ post-EP checkpoint: /illustrate @<ep-*.md>（layer 3 結構：撐得起嗎；方向確認 = 人讀 EP SM 情境 + /ep-review）
  → /implement（含 Agent Review + /audit-test + 階段 5a metadata-sync 結算 [UC 狀態+SYSTEM-MAP+EP 歸檔]，LLM 鏈）
          ↓ post-build checkpoint（看狀況呼叫，不硬定先後）: /illustrate（layer 3 結構 viewport，漂移/重造檢查）/ /debrief（layer 3 改動理解簡報：改了啥/證據/認知誤差點）→ /post-build（收尾鏈編排：/code-review [dual-context] → /judge-review → 修正迴圈 → /consistency → /metadata-sync）→ /commit（純 git 提交；post-build 可拆開手動單跑各命令）
```

**review-pipeline recipe**（變更類型 → review 序列）：
- **討論/規劃期**：`/illustrate`（結構，人 viewport，pre-EP 軟 gate 提醒，可多次）
- **review 期**：post-build 可選 `/illustrate`（漂移/重造檢查，B 軸）→ `/code-review`（六軸含 axis 3 結構 = arch 吸收，top-down，A 軸機器）→ `/judge-review`（**一次**）
- **既有 core 審查（無 change，純審穩固度）**：P1 識別 → selective review matrix（[arch-thinking](arch-thinking/SKILL.md)「core identification」lens）→ 依風險排序逐個 core 跑 `/illustrate` mode B（artifact menu：call graph / sequence / class slice / data-flow / boundary，B 軸人 viewport）+ **人讀 code**（VS Code Cmd+Click 跳轉）→（可選）P2 邊界驗證。B 軸；不排 `/code-review`（正確性靠人讀，非機器 finding）；Console 或 MD 模式。Anthropic selective-review：core = heavy human review、leaf = 放過。

### 工作流 skills — 核心開發流程

- `/spec` — 需求釐清（User Story + UC 定位 + Scenario Matrix + 邊界，純輔助；`--write` 寫需求 MD）
- `/execution-plan` — 段落式實作計畫書，自足生成 Self-Contained Segments（含段落0全域研究 + UC盤點 + Scenario Matrix + EP Review Cycle；ep_type blueprint/implementation 支援大型任務綱要+子 EP 結構），掃描 SYSTEM-MAP.md 取得功能上下文
- `/ep-review` — 深層思考審查 Execution Plan 合理性（已內建於 `/execution-plan`，可獨立使用）
- `/ep-validate` — POC 驅動的 EP 技術假設驗證（高技術風險 EP 的動態驗證）
- `/judge-review` — 評估其他 AI 的審查建議，基於深層思考框架決定是否採納
- `/implement` — 基於 Execution Plan 逐段實作（TDD + 階段 5a metadata-sync 結算：UC 狀態 + SYSTEM-MAP + EP 歸檔）（原 `/build`，ZCode 保留名改名；文內「build 階段」即本 skill 階段）
- `/post-build` — build 後收尾鏈編排（diff triage → code 鏈 [dual-context code-review → judge-review → 修正迴圈] → docs 鏈 [consistency → metadata-sync] → 收尾報告；止步於 /commit 前）
- `/code-review` — 深層思考六軸代碼審查（含 axis 3 結構 = arch 吸收，top-down；UC 覆蓋度；中型以上 dual-context 雙審查者：fresh-eyes + primed）
- `/debrief` — AI 改動理解簡報（layer 3，行動後）：七段倒金字塔——意圖／行為黑盒子（行為 vs 純結構判定；docs 變更渲染 behavior delta）／前後差異／分組檔案地圖／波及缺口／驗證證據（demo-checklist，NONE 逼問+清單完整性）／認知誤差點；無參數=uncommitted（fallback：EP baseline 任務弧，無則 HEAD~1）；`--ep` 方向確認已移除（改人讀 EP + /ep-review）
- `/illustrate` — 結構 viewport + 技術圖解（SA/SD artifact menu：call graph / sequence / class slice / data-flow / boundary；city map / drill / drift detection；console / md）+ **4 mode 導向**（設計決策 / 理解既有 / 審查驗證 / 溝通傳達）；核心流程三 checkpoint（pre-EP 軟 gate / post-EP / post-build drift detection，見上圖），結構能力調 arch-thinking skill
- `/followup-review` — 審查者回頭驗收實作結果
- `/commit` — Commit 入口（lint 閘門 → POC/Demo 處置 → message → 確認）；finalization 已在 build 階段 5a 結算，commit 前可跑 `/metadata-sync` 更新
- `/metadata-sync` — metadata finalization（兩 mode：build 階段 5a 結算 / standalone 補漏——commit 前更新或事後補漏，偵測漏掉的 Capabilities/Kanban/SYSTEM-MAP/arch/EP 歸檔/flow-feedback，確認後修補；`--check` 僅報告不執行）

### 工作流 skills — 自主實作

- `/deep-work` — 用戶離開時的自主實作引擎（收尾寫 STATE.md Last session 觀察）
- `/at` — 排程工作接續（對應 Unix `at`，LLM provider reset usage 後自動 resume；resume 讀 STATE.md 補 observation）
- `/usage-ping` — usage reset 探測叫醒（一次性 one-shot 階梯：Claude Code 3 發有界重試 / ZCode 單發 pending 鎖定，每 trigger 1 call 零工具、召回走 Stop hook sentinel；週期-網格：固定時刻 reset 單條 recurring cron，每 trigger 2 calls；滾動窗口（GLM 5h 類）無法自動輪詢——讀 UI 邊界重跑一次性，或無參數保底 now+301min、落地後重跑＝手動接力（鏈模式已棄用：冷 context landing 退化迴圈）；落地即確認配額回來；只排時間不接任務，接任務用 /at）
- `/handoff` — 產出 self-contained 交接 prompt（進度+決策脈絡+下一步），交另一個 session/repo/provider；與 /at 分工（handoff 交別人 / /at 自己續）；STATE.md 非交接選項（Last session 觀察 / 每 session 覆寫，/at resume 讀）
- `/compact-prep` — /compact 前置外部化：落檔 raw tail＋memory 新鮮度檢查＋提醒 user compact 後首句讓 AI 讀 tail 檔，user 再手動 /compact；ZCode 實測 SessionStart(compact) hook 死路（Claude Code 端可用：hook 注入環境職責縮減為 memory 檢查）；另含 compact-audit 搭檔段（重大弧線壓縮後摘要審計，選配）

### 工作流 skills — 品質工具

- `/lint-fix` — ruff + mypy 自動修正
- `/fix-test` — 測試失敗分類修復（先分類 A/B/C/D/E 再修復，防止盲目讓測試通過）+ 階段 4.5 TWINS 同類缺陷 sweep
- `/audit-test` — 測試品質稽核（反模式偵測、覆蓋對稱性、mock 健康度，只讀不寫）
- `/smell-detector` — 壞味道偵測（layer 3，行動前/審既有）：架構審查＋重構前期研究＋測試優化盤點；兩 mode——`<dir|files>` zoom 變焦批判（質疑存在：6 判準+查證誠信+Domain 層判準 4/5）/ `--baseline <dir>` 廣角盤點（per-directory 4 檔+invariants+--status/--stale/--arch）；測試 smell 三類（資源/怪獸/結構，與 /audit-test 正交）；read-only 偵測器，修復走 /implement、/fix-test
- `/corpus-recall` — 行動前敘事脈絡檢索（topic→前因後果卡片，與 smell-detector 對仗＝行動前偵察雙軸）：symbol/模組/關鍵詞→callstack-plan 錨點＋tour 景點＋manifest 交叉＋md 內文＋hub_refs 影響域的機械求全，LLM 判讀 confidence 三級；輸出相關鏈（職責一句＋為何相關＋走讀/深讀雙入口）——corpus 超過瀏覽閾值後的檢索前門；無語料誠實停不硬湊
- `/consistency` — 文檔品質檢查（自洽性、矛盾性、順序、自包含、精準度、Signal/Noise）
- `/sync-sources` — 跨檔 single-source invariant 機械檢查（含非 Claude 部署 bundle 新鮮度）
- `/distill-spec` — 蒸餾肥大的 spec 文檔

### 工作流 skills — instruction file 維護

- `/instruction-init` — 為任意專案自動產生 instruction file 體系（root + 模組都雙檔：AGENTS.md source + CLAUDE.md @AGENTS.md wrapper，bottom-up）
- `/instruction-clean` — 清理 Markdown 元資訊；`--distill` 蒸餾低 signal 內容（保守防護欄：預設 conservative、NEVER 清單禁觸失敗教訓/設計理由/約束、換形為主僅元資訊直刪、縮減 >30% 逐條列出）
- `/instruction-sync` — 檢查文檔與程式碼同步性
- `instruction-writing` — instruction file 撰寫完整規範（reference skill：rule 留 always-on 核心，此處承載完整規範＋元資訊禁止行為表與論證＋文檔自洽五維檢查；rule+skill 分層控制 bundle 尺寸）
- `/daily-maintain` — 每日自動維護（排程用），自動修正低風險問題 + commit
- `/project-review` — 互動式專案審查（人類用），findings + kanban + doc health

### 工作流 skills — 流程演化回饋

- `/flow-feedback` — session 摩擦收集器：不順 session 後，user 植入摩擦 + AI map 到 skills/commands，產 type-1（時機）/type-2（設計）建議 + 具體例子，寫 `ai-analysis/flow-feedback/`
- `/flow-review` — 定期讀累積 flow-feedback，找重複摩擦 + 聚合 type-2 設計缺陷 + memory-routing 判定（教訓→Skill/STATE/棄），跟 user 討論改善 skills/commands（B 軸）；定案 → /execution-plan（大改，必要時先 /spec 釐清需求）/ kanban（小改）→ /implement

### 工作流 skills — 日常工具

- `/task-status` — Kanban-centric 進度儀表板（Capabilities 完成率 + Kanban lane 分佈 + 模組 Breakdown）
- `/doc-health` — Capabilities + Kanban 健康檢查（12 角度驗證文件準確性）；`--report` 產出完整能力地圖；`--sync-system-map` 用 Capabilities 狀態同步 SYSTEM-MAP.md
- `/rebase <branch|all> [--autostash]` — Trunk-based rebase。**原則：trunk 永不被 rebase**，故已對齊的 feature 由 trunk 上 `merge --ff-only` 吸收（非 rebase）；feature 可 rebase onto trunk 或另個 feature；Phase 3 報告其他 feature 落後狀況 + 提示自行同步，不自動 rebase。`all` 批次：feature 上 = 同步所有 feature onto trunk、trunk 上 = 吸收所有 ff-able feature（5 停止點菜單，不自動跳過；目標集合 = `git branch` 動態列舉 − trunk，禁寫死）

### 工作流 skills — 依賴升級（收盤後執行）

- `/upgrade-nt` — 升級 NautilusTrader（breaking changes 掃描 + 跨 worktree 一致性 + SJ external API 測試）
- `/upgrade-sj` — 升級 Shioaji（breaking changes 掃描 + Volume 單位驗證 + SJ external API 測試）

### 工作流 skills — 其他

- `/swing-analysis` — Swing Analysis 協作模式（Trajectory Viewer + 日誌監控）

### 開發流程（spec → 交付）
- `test-driven-development` — TDD 驅動實作（RED → GREEN → 重構；AI 失敗模式反制：反 rationalization、mock 階層、xfail strict）
- `arch-thinking` — Clean Architecture + DDD 設計視角 + 結構機械（分層依賴/bounded context/use case 驅動[含共用層外溢]；city map/dep weight/Pattern Radar/domain grounding/LSP 查證/補償邏輯盤點/call graph（函數級）/type structure（contract slice）/data-flow（靜態骨架）；視角非模板；受眾中性；與 api-and-interface-design 分工）
- `debugging-and-error-recovery` — 系統性根因除錯（非猜測；no-guessing 熔斷、用戶糾正訊號表）
- `external-api-investigation` — 外部 API / 整合器真實行為調查（monkey-patch dry-run、查 stub、問 domain；實證優先於讀 code 推理）
- `autonomous-execution` — 無人介入自主執行的決策 / 錯誤恢復 / 完成回報 / workspace safety / path invariants / session recovery（false-done 偵測）

> 通用方法論（發散收斂、任務分解/垂直切片、增量交付、spec-first、官方文檔 grounding）屬 LLM 原生能力，不設 skill——相關委託點已改為就地摘要。

### 品質與審查
- `review-engine` — review 命令家族通用審查邏輯 domain 真相源（嚴重度/信心水準/審查者自證/LSP 查證/審查模式判定/Writer-Reviewer 分離/多層驗證/**review 執行預設單一源**：force 獨立 / max-agents / model / 視角 / spawn-vs-session）；ep-review/code-review/audit-test/execution-plan EP Review/implement Agent Review 共用
- `code-review-and-quality` — code 六軸審查 profile（what to check，含 Security/Performance 軸 checklist 與 Capability Coverage 單源）；通用邏輯見 review-engine
- `python-type-gap` — 第三方套件型別缺口的四層策略
- `validation-strategy` — 驗證策略紀律（e2e 優先/交易 replay>live/放 scripts//不重驗 package；與 TDD 流程分工）
- `acceptance-evidence` — 驗收證據深層理論（reference skill：認知誤差與 EP 預見極限、Intent Drift 兩型、filter trap、L3 整合實例、Runtime Invariant Assurance、B 軸演進、盤點執行點雙掃；rule 留 L1-L6/A-B 軸 always-on 核心——rule+skill 分層控制 bundle 尺寸）

### 架構與演進
- `api-and-interface-design` — 穩定 API / 模組邊界 / 公開介面設計（Hyrum's Law、邊界驗證、agent-friendly interface）

### 專案維運
- `git-workflow-and-versioning` — git commit / branch / 衝突 / 平行流
- `kanban-board` — Tasks.md 看板卡片管理（讀 / 建 / 移動 / 回顧）
- `maintain` — `/daily-maintain`（自動）與 `/project-review`（互動）共用的 4-phase 維護核心（勿直接呼叫）
- `scan-project` — 統一專案知識掃描（imports + Capabilities + kanban → dep_graph / findings）
- `standup` — 每日晨間簡報昨日活動 digest（跨 worktree session 聚合 + commit/kanban/SYSTEM-MAP transition；ZCode 23:20 定時任務整合）
- `agent-workflow` — Agent 派發 / worktree 隔離 / 並發控制 / spawn 預設背景 / 委派框架（delegation）/ side-discovery / Rule Freshness（spawn 時注入）/ Writer-Reviewer / spawn 失敗階梯（429 降並發→serialization）
- `self-contained-prompt` — 交接 prompt 設計原則（接手方三層 / schema / 決策脈絡 / drift / 機密）；/handoff 與 agent-review-cycle 共用
- `skill-cleaner` — 稽核 skill：重複 / 未用 / prompt-budget / compact
- `memory-audit` — auto memory 稽核/清理（兩級：full 四層=索引量測+內容核實 vs repo+清理+盤點 / lite=git log 增量核實；索引整潔≠記憶健康、內容核實預設必做；狀態戳 `_audit-state.md`；advisory→核可→執行三分離）
- `dependency-upgrade-watch` — 偵測 nautilus_trader / shioaji 版本漂移，主動建議 /upgrade-nt|/upgrade-sj（碰 pyproject.toml 時 auto-load）
- `zcode-session-query` —（ZCode 專用）跨 session 查詢與參考：查 session id / 讀指定 session 尾部真人互動（scripts/zcode_tail_chat.py）/ ReadSessionContext（handoff 策略；relevant 大 session 逾時）；handoff / relay 的「讀進來」側；id 禁手打、sqlite3 CLI 無聲空輸出改 python ro uri

### 工具與查詢
- `nt-query` — NautilusTrader **v2**（Rust+PyO3）能力 / 實作 / 用法合約 / v1→v2 移植查詢（docs-first + LSP-on-in-package-stubs + MIGRATION_V2 契約 + v2 名稱紀律）
- `nt-v1-query` — NautilusTrader **v1**（legacy Cython runtime — 消費端現行 runtime）查詢（docs-first + LSP-on-Cython-stubs + designer intent；消費端遷移 v2 後退休）
- `crg-query` — code-reality 知識圖譜查詢紀律（LSP-vs-code-reality 分工：symbol 真相→code-reality SCIP（Rust）／LSP（hover/簽名/即時）／impact·callers·flows·community→code-reality engine（graph_query 家族，讀 .code-reality/graph.db 自有格式；CRG MCP 已於 2026-08-26 cutover 退役）；GATE（assume + warn 不靜默降級）；anti-over-reliance：graph=structure 非 behavior；engine 在場才 fire，平行 nt-query）
- `code-reality` — code_reality 工具鏈程序層（meta 層工具，Rust carrier `code-reality <tool> --repo`、住獨立 repo `~/Github/code-reality`：snapshot／transition／hub_refs（含 hazard 分層安全網——防「0 refs 可刪」誤判）／runtime_edges／boundary／boundary_build／delta_tour／chain_tour／graph_audit（Rust 完整度稽核）／scip_refs（SCIP 索引 refs 真相源——graph_audit 缺差對照）／tour_validate／tour_upgrade／tour_manifest——全工具讀 `.code-reality/graph.db` 自有格式（2026-08-27 cutover；純 producer graph 為常態——`import_legacy` 已完全移除〔W5〕）；repo profile `.code-reality.toml` schema、存在性偵測單一真相源、claims 口徑限制；與 crg-query 分工：crg-query 管查詢紀律、本 skill 管工具鏈程序與 EP 對照）
- `tour-bootstrap` — repo 導覽建置程序（Chain 場景／Delta 時間層，地圖層 Overview 視重複度盤點退役；優先序裁定＝corpus 前門與動線；`.tour` 語言契約——CodeTour 消費端正則決定的 line/pattern/tour link/file link 規則；機械驗證清單＋AI 不代終審停點；建在 code-reality 工具層之上，斷點③已解——callstack 生成走 blueprint-bootstrap）
- `blueprint-bootstrap` — blueprint 知識庫建置程序（人讀合成視角 scaffold：骨架＋半滿＋🤖/👤 狀態標記＋誘導問題＋治理模板；**callstack 場景敘事生成＝斷點③解法**——重複度盤點前置→鏈枚舉→逐幀實證→coverage 稽核→findings，產出餵 tour-bootstrap 場景層；既有 blueprint 走 audit 模式不重建；位置＝instruction-init 之上、tour-bootstrap 之下）
- `mermaid` — pragmatism-first Mermaid 圖表生成（theme 無關設計：禁 init、fill+color 成對跨主題可讀）
- `rules-reminder` — 常被違反的規則（rg/fd、無 `#`、`uv run`、無 `$` 展開、獨立呼叫批次化、改檔前先 Read）
- `lsp-navigation` — LSP 深層參考（reference skill：rg 陷阱案例群、方法論限制 loopback、Agent prompt 工具指定模板、跨 harness 載體對照、workspace staleness/reindex 處置、驗證輸出格式；rule 留統一速查/Tool Discovery gate 核心——rule+skill 分層控制 bundle 尺寸）
- `context7` — Context7 MCP 文檔查詢（library/framework/SDK/API 用法先查最新文檔再回答，優先於 web search；跨 harness MCP 支援）
- `voice-notification` — 三通道語音通知（系統召回 / 進度提醒 / 完成通知）

### UI / 協作
- `frontend-ui-engineering` — Panel/Bokeh 互動 dashboard / 視覺化
- `ui-collab` — 互動式 UI 的 LLM 協作模式（`[ACTION]` 操作日誌）

### 領域特定
- `trading-analysis` — 股票 / 市場走勢三層分析（經典 TA → 量化 → 第二層思考）
- `broker-flow-analysis` — 台股券商分點進出（BSR）盤底接手 playbook + 單分點角色診斷（反散槍 focal-point 紀律）
- `golden-sample-research` — golden-sample 研究方法論（正樣本收割→歸納 setup 籤名→分類器；過程紀律 domain 中立）
- `pre-attack-setup` — 台股攻擊前 setup 分類（收斂/多頭拉回）→ 大漲 watchlist + 分K策略路由

## Frontmatter 配置

> **跨 harness 支援度**：ZCode 僅規範 `name`/`description`（目錄名即技能名）；下表其餘欄位是 Claude 端機制，ZCode 端**靜默忽略**（實測 `context: fork` + `agent:` 被忽略、內容直接注入當前 session 執行）——寫工作流時不可依賴這些欄位在 ZCode 生效，相容行為寫進 body。

> **上限是 harness-specific**：Claude 端 `description + when_to_use` 合計截斷 **1536 字元**（對齊 `skill-cleaner.ts` 的 `MAX_DESCRIPTION_CHARS`；可用 `maxSkillDescriptionChars` 覆寫），清單預算由 `skillListingBudgetFraction` 控制；ZCode 端 description **>1024 字元整顆 drop**（非截斷）、清單注入每條摘要 ~250 字元、全體共享固定預算（ZCode 官方 skill 文檔）。**寫 description 兩端約束都取交集：精簡、觸發詞前置**。

```yaml
---
name: skill-name                    # 顯示名稱；預設取目錄名
description: 功能 + 何時使用 + 觸發詞    # auto-discovery 唯一依據，見下方寫法
when_to_use: 觸發短語 / 範例請求       # 附加到 description，計入 1536 上限
paths: ["**/*.py"]                   # glob 限制 auto-load（只在此檔被碰時載入 body）
allowed-tools: [Bash(uv pip *)]      # skill 作用時預批准工具（免每次權限提示）
disallowed-tools: [AskUserQuestion]  # 作用時移除工具（自主 loop 用）
disable-model-invocation: true      # 純人類觸發 → 不進 listing（見決策原則，預設不設）
user-invocable: false               # 背景知識 → 從 / 選單隱藏（仍可被 model invoke）
context: fork                       # 在 subagent 隔離執行（配 agent:；無對話歷史）
agent: Explore                      # context: fork 時的 subagent 型別
model: opus|sonnet|haiku|inherit    # 作用時覆寫模型（下個 prompt 恢復）
effort: medium                      # 作用時覆寫 effort
---
```

### 欄位決策原則

- **`disable-model-invocation` 預設不設** —— AI 在自主流程（deep-work、EP→build→commit 鏈）會高頻自動 invoke dev-loop 命令；設了會打斷既有工作流（transcript 實證：execution-plan/spec/implement/commit 等在自主流程被 AI 高頻自動 invoke）。consent（如 outward-action-consent）已在 skill 層確保，**不需**在 invocation 層再加。只有「transcript 實證 AI 不會想 invoke」的純人類工具命令才考慮設 —— 依據 transcript 非受眾表
- **`paths`** 限縮 auto-load 範圍 —— 領域特化 skill（查特定套件、特定副檔名）用 glob 避免跨專案誤觸發；注意 paths 只擋 body auto-load，**description 仍在 listing**
- **`context: fork`** 隔離長任務 —— 適合 self-contained 任務（無對話歷史依賴），用 `agent:` 選 subagent 型別
- **`allowed-tools` vs settings 權限**：`allowed-tools` 是 skill 作用時的預批准；基礎權限仍由 settings.json 管理
- **`user-invocable: false`** 用於背景知識（不該被人類 `/invoke`）；`disable-model-invocation: true` 用於人類專屬 workflow（不該被 AI 自動觸發）

### description 寫法

`description` 是 auto-discovery 唯一依據，清單截斷時**從尾部丟**：

- **觸發詞前置** —— 「何時使用 + 同義觸發詞」放前面，功能描述放後；截斷時保住觸發詞
- **涵蓋多種說法** —— 使用者實際會打的詞（中英文同義詞都列）
- **< 1536 字元**（含 when_to_use）
