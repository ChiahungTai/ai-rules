# AIR-86 批三 candidate ledger（frozen by 5.3 writer，2026-09-13）

> 對照：卡面已決策＋codex-out.txt §C。guide 首度納入（七節骨架留、body 清理）＋**Session 開場導引三行版逐字插入**（卡面定稿，放 intro 後、演化性思維前）。三 rule 依 §C keep-list A-slim。python-standards 只 A-slimming（AIR-85 前禁 pointer-only）。
> 管線同批二：凍結→flash C1（承接）→C2（slim）→機械 gate→deploy→雙審→post-build。

## Band 誠實預估（writer 立場，交雙審裁決）

§C 的 guide 2.6–3.2KB 與三 rule band 是規劃估計——本批誠實 triage 後：guide ≈4.15KB（含導引 +430B insert；§C 估計未含導引）、collaboration ≈2.26K/1.5–1.8K、context ≈1.5K/0.9–1.2K、python ≈1.92K/1.2–1.5K。_corpus 前幾輪已 pointer 化大部分 methodology，剩餘 C-core 佔比高——照批一 C7／批二全上修前例，不為 band 砍 C-core，全數揭露交裁決。**導引 insert 抵銷 guide 大部分削減是本批已知特性**（卡面裁定：導引是 bootstrap 資產優先於 byte）。

## 檔案 1：ai-development-guide.md（4,284B；全文替換）

**定稿全文**：

```markdown
# AI 協作開發指南

跨專案、harness-neutral 協作規範，量化交易優先；專案指令放各 repo AGENTS.md。

改 instruction 前載 instruction-writing skill；禁行數/字數/版本號/日期/Changelog。雙檔與引用規範見 [instruction-writing.md](rules/instruction-writing.md)。

## Session 開場導引

- **先定位現在在哪**：有 STATE.md 先讀最近 session 觀察，再以 active card／board 狀態與 card notes／EP 進度節核對目前工作、已完成處與 resume point；觀察層不能取代現況來源。
- **再決定下一個入口**：標準開發主鏈為 /execution-plan → /implement → /post-build → /commit；需求釐清、審查、修復等分支及各步方法論查 skills/CLAUDE.md 索引與對應 skill。
- **需要跨 context 接續時先結算**：context 將耗盡先把進度與待辦寫回 EP／card；同一工作稍後續跑用 /at，交給另一個 session／repo／provider 用 /handoff。

## 演化性思維

測試保護下優先架構品質/正確性/清晰度，預設不保留向後相容；需確認情境見 [edit-discipline.md](rules/edit-discipline.md)。

## 驗證約束

修改後須實跑，再查語法/import 並依風險驗證；純文檔/註解例外見 [must-execute-before-complete.md](rules/must-execute-before-complete.md)，順序/消費端要求見 [quality-constraints.md](rules/quality-constraints.md)。

| 風險 | 範圍 | 驗證深度 |
|---|---|---|
| 高 | 核心架構、跨 context domain service、會計/風控總量與 sizing、數據庫、安全、重大 API | 完整驗證相關功能 |
| 中 | 新功能、演算法/性能優化 | 核心功能測試＋經驗分析 |
| 低 | 樣式、文檔、配置 | 至少確認語法；執行例外依上述 rule |

評估提供相對複雜度、風險、依賴、里程碑與排序；不預測絕對耗時或精確進度。

## UC-Driven Development

功能先定義 Use Case。AGENTS.md Capabilities＝已完成能力索引，backlog＝承諾池；多卡優先序可由 project blueprint dependency graph 決定（backbone），未被支撐的卡走 kanban triage；操作/refs/precheck 單一源為 kanban-board skill。

文檔角色：AGENTS.md＝導航/完成能力 what/where；architecture.md＝why；SYSTEM-MAP.md＝跨域現狀；dependency-graph.md＝人工依賴/ripple 地圖（機械查詢交 code-reality）；backlog/＝任務卡。長文按需 link，禁全量 transclude。

UC 狀態流轉與 Capabilities 寫入格式（✅/🟢/🟡/📋、未承諾→drafts、scripts/ 不放 Capabilities）見 metadata-sync skill。

規模：大型跨模組/新功能→execution-plan 建卡；中型→更新既有能力/卡；跨檔 refactor 亦按大型/中型，僅單檔小 tweak 算小型。小 bug/doc 免 UC；碰單位邊界/除權息/時區/會計/風控即非 simple，至少列受影響 invariant＋驗證式（silent-corruption 例外）。

動卡第一動設 In Progress；銜接機制（建卡即 commit 防 id 撞、結案兩步、precheck）單一源 kanban-board skill。

## Solo + AI 開發工作流

一人＋AI、無團隊/CI；一 EP＝一 session，段落自含、可結算接續。model 退化先結算再 handoff 新 session；Writer/Reviewer 分離，review 支援跨 session findings 回貼。

## 架構設計紀律

spec/EP/implement/review 用 Clean Architecture＋DDD 視角，不強制模板/過度分層；兩層思考/SOLID 見 [design-thinking.md](rules/design-thinking.md) 與 [edit-discipline.md](rules/edit-discipline.md)，深入用 arch-thinking，介面用 api-and-interface-design skill。

## 量化交易專屬鐵律

- 數據完整性優先：損壞比缺失更危險，禁靜默傳播（正文與 Crash-Only 適用範圍見 [quality-constraints.md](rules/quality-constraints.md)）。
- 回測完全可重現（hash＋config＋seed），波動 >0.01 必須重做。
- 狀態外部化；Live/Backtest 共用邏輯，避免模式分支。
- 隨機 seed 必須可注入，避免 np.random。

## Summary Instructions

壓縮對話必保留：已讀/改路徑、測試結果/錯誤、決策/理由、目標/待辦、已提交未執行命令/skill、待確認提案、背景/中斷工作。數字/比例須實際枚舉或逐字複製，禁憑記憶改寫。
```

| id | 變更 | 裁定 | 理由 |
|---|---|---|---|
| G-0 | **插入開場導引三行版** | C-insert | 卡面定稿逐字（禁令遵守：無八站名/glyph；STATE 不升高於 board/EP） |
| G-1 | intro 刪「Claude 用 symlink＋auto-load，其餘由 deploy_agents.py 打包到全域位置」 | A | deploy 機制是治理知識（rules/AGENTS.md 域），非 session 行為 bootstrap |
| G-2 | 演化性思維刪「持續測試→重構→確認」 | A | 通用重構循環（模型已知）；C 核（品質優先/預設不保相容）留 |
| G-3 | 驗證約束 | C 保留（含風險表——codex §C 明文保留；EP 規劃首後果時點在場） | 僅原文照舊 |
| G-4 | UC glyph 全表→metadata-sync（C1 承接）；guide 留一行 pointer | S | glyph 消費時點＝寫 Capabilities＝metadata-sync 載入時 |
| G-5 | UC 銜接壓縮 | A | 機制全件在 kanban-board（結案兩步/precheck/開工特赦實證在場）；導引三行版另承載主鏈 |
| G-6 | Solo+AI 刪「compact 分布於規劃後/build 段間」＋「先結算再」微壓 | A | compact/handoff mechanics＝compact-prep/handoff skills 域；導引第三行已承載接續結算 |
| G-7 | 架構設計列舉壓縮（「兩層思考、依賴方向、bounded context、use case」→「兩層思考」） | A | 與 design-thinking rule 內容重複（批一已 slim 過該 rule） |
| G-8 | 鐵律首條中段（無效資料/溢出立即失敗）→pointer 化 | A | 與 quality-constraints L13 正文逐字重複（單源化） |
| G-9 | Summary/規模段 | C 逐字保留 | 規模＝execution-plan 引用標的（skill L40 link 到 guide）；Summary＝compact preserve-list |

## 檔案 2：rules/collaboration-constraints.md（2,488B）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| CO-1 | 理解優先實作／事實查證／破壞性選擇／具體明確／反 Sycophancy／工作目錄 | C 逐字保留 | §C keep-list 全件；AGPL/fork 句＝user ruling |
| CO-2 | Agent 派發段壓縮（保留案例） | A 壓縮 | worktree 確認細節沉 agent-workflow（自檢清單在場）；owning WT 核心＋三條注入 pointer＋案例留 rule |

**CO-2 定稿**（取代 L34-36 兩段）：

```markdown
跨 repo 寫入由主 session 負責；spawned/automation 只在卡 owning WT 操作，agent 寫不進目標或不能判定 owning 就回報主 session，禁把責任丟給受限 agent（案例：監控 session 因規則未載入誤結 owning=main 的卡）。寫檔 agent prompt 必注入三條（禁 /tmp／寫不進就回報／暫存集中 `.agent-tmp/`）；worktree 能力確認與完整自檢清單見 **agent-workflow skill**「Agent tool spawn 前」。
```

## 檔案 3：rules/context-management.md（1,666B）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| CT-1 | Session freshness 段 | C 逐字保留 | 昨日落地新規（3b81937），勿動 |
| CT-2 | durable checkpoint 案例句壓縮 | A 壓縮 | 保留案例錨、壓敘事 |
| CT-3 | 其餘（Session 管理/bullets/STATE/memory pointer） | C 逐字保留 | §C keep-list；STATE/memory 已是 pointer |

**CT-2 定稿**：
- old：`context 揮發且 quota 可能突然耗盡。真實案例：Codex 審查弧只落中間 findings，最終合成留 transcript 後 session 死亡，接手需昂貴考古。`
- new：`context 揮發且 quota 可能突然耗盡（案例：審查弧只落中間 findings、session 死亡後接手需昂貴考古）。`

## 檔案 4：rules/python-standards.md（2,053B；只 A-slimming，禁 pointer-only）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| PY-1 | 舊 typing 禁令 bullet 壓一行 | A 壓縮 | 卡面既定「禁舊 typing 壓一行」 |
| PY-2 | Facade 補充論證壓縮 | A 壓縮 | 留判準（消費者是否外部）與 _internal 出路，壓敘事 |
| PY-3 | 遷移段壓縮 | A 壓縮 | 機制保留（禁先刪/全消費者/rg+symbol 分工） |
| PY-4 | 命名/re-export 主體/真實案例/其餘型別 bullets/命令 pointer | C 逐字保留 | 反主流裁定＋案例（卡面明留） |

**PY-1 定稿**（兩 bullets→一）：
- old：`- 禁 List/Dict/Set/Tuple/Optional/Union 舊 typing，改內建泛型與 T | None / T1 | T2。
- typing 只 import Callable、Protocol、TypeVar、ParamSpec、Self、Any。`
- new：`- 禁 List/Dict/Set/Tuple/Optional/Union 舊 typing——改內建泛型與 T | None / T1 | T2；typing 只 import Callable、Protocol、TypeVar、ParamSpec、Self、Any。`

**PY-2 定稿**：
- old：`Facade 對外部消費者有穩定 API 解耦價值；內部 modules/scripts/tests/AI 共同重構，收益不足以抵銷 import/循環/IDE 代價。判準是消費者是否外部；未來發佈外部套件可用 _internal 私有實作＋__init__ 只導出穩定 API。`
- new：`Facade 只對外部消費者有價值；內部共同重構，收益不足抵銷 import/循環/IDE 代價——判準是消費者是否外部；發佈外部套件可用 _internal 私有實作＋__init__ 只導出穩定 API。`

**PY-3 定稿**：
- old：`禁先刪：先查全消費者（含 \`from package import\` 與 \`from .\` 相對 import），逐一改完整 module 路徑，全部改完才清 __init__ re-export。文字掃描用 rg，符號查證依 symbol-query-routing。`
- new：`禁先刪：先查全消費者（含相對 import）逐一改完整 module 路徑，全部改完才清 __init__ re-export；文字 rg、符號依 symbol-query-routing。`

## C1 承接（一支 skill）

**skills/metadata-sync/SKILL.md**——在「為什麼結算在 build 不在 commit」段落（以 `靠 commit \`git add\` 納入 finalization 檔規範。` 結尾）之後插入：

```markdown
> **UC 狀態流轉（自 guide 承接 2026-09-13）**：✅→主要實作模組 Capabilities（同一 UC 一處，`能力|入口|狀態`，入口含 CLI＋函式）；🟢→附限制；❌→移出；📋/🔧→backlog To Do；🟡→In Progress；未承諾→drafts。scripts/ 是人類 demo，不放 Capabilities。
```

agent-workflow skill：無需補（案例留 collaboration rule；spawn 前自檢清單已在場）。

## 機械 gate（flash 執行後自跑）

1. `wc -c` 四目標檔＋metadata-sync 前後量測
2. 負詞彙（guide/rules 內 0 hits）：`持續測試→重構→確認`、`UC 狀態：✅`、`銜接：execution-plan`（09-13 erratum 修訂：原詞 `建卡即 commit 防 id 撞` 與 G-5 定稿括號標籤撞——probe 已證舊句 0 hits）、`deploy_agents.py 打包到全域位置`、`compact 分布於規劃後/build 段間`、`優先目標 repo session`；python：`禁 List/Dict/Set/Tuple/Optional/Union 舊 typing，改內建泛型與 T | None / T1 | T2`（舊 bullet 形態）
3. 正向存活：guide `| 高 | 核心架構`、`碰單位邊界/除權息/時區/會計/風控即非 simple`、`一 EP＝一 session`、`回測完全可重現`、`先定位現在在哪`（導引在場）；collaboration `禁猜測實作`、`盲改指標會靜默污染回測`、`機械衝突訊號`、`誤結 owning=main`；context `Session freshness`、`resume read-set`；python `重型 re-export 讓輕量 enum import 從毫秒變秒`、`__all__`
4. metadata-sync 含 `UC 狀態流轉`＋`未承諾→drafts`（glyph 抵達）
5. 跨檔引用存活：execution-plan skill 對 guide 的 `中型變更` link 標的仍在（規模段保留）；root AGENTS.md 對 guide 章節列舉（演化/驗證/UC-Driven/架構/量化鐵律）仍成立
6. `uv run pytest`（364 基線）＋`uv run python scripts/deploy_agents.py --dry-run` 綠

## 偏差回報義務

同批二：文本不一致、gate 紅、ledger 未涵蓋語義依賴→停手回報。
