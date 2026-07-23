---
name: arch-thinking
description: 架構設計、clean architecture、分層依賴、bounded context、use case 驅動、DDD、SOLID、依賴方向、模組邊界、city map、dep weight、Pattern Radar、重用枚舉、Jaccard、domain grounding、結構 viewport、結構查證、LSP 查證、反向耦合、補償邏輯（compensating pair）、挖東牆補西牆、double-count、共用層外溢時使用。提供 Clean Architecture + DDD 設計視角（domain←use case←adapter←infra 分層、bounded context、use case 驅動檢視整體結構）+ 結構機械能力（City Map 資料/dep weight/Pattern Radar 重用枚舉/domain grounding/LSP 查證/lean-heavy），用於 spec/EP/build/review 的設計決策與結構審查。視角非模板。
---

# Architecture Thinking — Clean Architecture + DDD 視角 + 結構機械

用 Clean Architecture + DDD 視角檢視結構（**設計視角**：怎麼判斷），並提供結構查證的**機械能力**（**結構機械**：怎麼撈事實）。單一 skill 承載兩者 — 視角給方向、機械給事實，組合才有湧現價值。**視角非模板** — 注入思考，不強制分層、不過度工程。頂層總綱見 [ai-development-guide.md](../../ai-development-guide.md)「架構設計紀律」。

## 受眾中性（適用整個 skill）

本 skill 的能力（視角 + 機械）**不決定受眾** — 渲染心智模型給人判讀（`/illustrate`，人類 viewport / B 軸）、產機器 finding（`/code-review` axis 3，A 軸）、結構審查（`/ep-review` F3）都由**消費命令**決定，本 skill 刻意中性。

> 三層次區隔（合併檔內不重疊）：**受眾中性**（本段）= 對消費命令的中性承諾；**與既有 skill 邊界**（§四）= 對其他 skill 的職責分工；**不適用 / 不做**（§五）= 場景排除（不適用）+ 職責邊界（不做）。

## 一、設計視角（人類/LLM 思考提示層）

> **架構決策的思考格式**：本 skill 給**視角**（依賴規則 / bounded context / use case 驅動），架構決策的**深度推導**（第一性原理 + 第二層後果追蹤）用 [deep-thinking](../../rules/deep-thinking.md) 輸出格式——視角給方向、deep-thinking 給推導深度，組合才有湧現價值（同本 skill「視角 + 機械組合」哲學）。

### ① 依賴規則（Clean Architecture 分層）

domain ← use case ← adapter ← infra，依賴**向內**（內層不依賴外層）。

設計時自問：新東西落哪層？依賴方向對嗎（有無下層 import 上層）？有無循環？

### ② bounded context（DDD 邊界）

每個 context 邊界清楚，**不跨域直接存取內部**（`_private`）。

設計時自問：這該在哪個 context？有無跨域直接存取？

### ③ use case 驅動

先問**消費者要什麼行為**，再設計結構。

設計時自問：消費者是誰？結構撐得起 use case 嗎？

**共用 domain service 的外溢陷阱**：被多 context 共用的 domain service（會計總量、定價、結算）改語意 = 強迫所有消費者妥協於同一語意。消費者需求**相反**時（一個要含 X、一個不要含），改共用層會同時滿足又打破不同消費者 → **改消費端各取所需，不改共用層**（真實歷史案例：dashboard 要 `available` 含 proceeds / sizing 不要含 → 各自 context 過濾，非改共用 compute）。

### mosaic 範例（領域特定，規則通用）

- **domain**：策略訊號、風控規則（純邏輯，無 IO）
- **use case**：回測、下單、數據更新（編排 domain）
- **adapter**：NT（執行）、SJ（行情）、catalog（持久化）（接外部）
- **infra**：DB、SDK、檔案系統（外部細節）

依賴向內：domain 不依賴 use case / adapter / infra；adapter 依賴 use case interface（非反過來）。

### RC-2 邊界：bounded context vs module boundary

- **bounded context（本 skill）**：DDD 語義邊界 — context 間不跨域存取內部。檢視**整體結構**。
- **module boundary（[api-and-interface-design](../api-and-interface-design/SKILL.md)）**：介面合約邊界 — Hyrum's Law、Validate at Boundaries、合約穩定性。**設計介面**。

**分工**：設計 API / 介面 → `api-and-interface-design`；檢視整體結構 / 分層 → 本 skill。兩者互補（介面是 adapter 邊界的具體化）。

## 二、結構機械（agent 可執行工具層）

> 本段為 agent 可執行的機械能力（列舉 + 查證 + LSP 操作），與上層設計視角（人類/LLM 思考提示）層次不同 — 消費端按受眾取用。給 `/illustrate`（人 viewport）/ `/code-review` axis 3（機器）/ `/ep-review` 共用。

### product-type 雙軌

| 場景 | dep_graph 來源 | 查證工具 |
|------|--------------|---------|
| **code** | 複用 [scan-project](../scan-project/SKILL.md) dep_graph（.py AST，**不重造**） | scan-project 枚舉 primary + LSP 驗證 secondary（見 [lsp-navigation](../../rules/lsp-navigation.md)） |
| **docs** | scan-project dep_graph **不適用**（.py only）→ 自己 rg 跨檔畫命令/skill 拓樸 | rg（docs 場景取代 LSP） |

> scan-project 的 **code↔doc findings**（掃 instruction 檔 Capabilities）在 docs 場景仍可用；只有 **dep_graph**（.py AST）不適用 docs。

LSP 決策樹見 [lsp-navigation](../../rules/lsp-navigation.md)（本 skill 用 LSP，非重造決策樹）。

### City Map 資料生成（非渲染）

**生成資料**（節點關係 + dep weight + 消費者數）；**視覺渲染**（節點 + 依賴箭頭 ASCII/Mermaid）留 `/illustrate`（既有渲染引擎）。

每節點標註：**依賴方向**（A ──uses──▶ B）/ **dep weight**（lean=stdlib/輕量；heavy=numpy/pandas/polars/nautilus/大型框架）/ **消費者數**（誰 import 它）。

**反向耦合 flag**：「heavy symbol → lean 廣用模組」= anti-pattern（transitive burden：lean 模組所有消費者被拖入重依賴）。

資料範例（供 illustrate 渲染）：
- `catalog_utils`（lean, 12 consumers）
- `dataframe_utils`（heavy, 3 consumers）
- ⚠️ polars helper 抽進 `catalog_utils`（lean）→ 反向耦合 flag

### Pattern Radar（重用枚舉）

三類重複偵測：

| 類型 | 觸發 | 搜尋 |
|------|------|------|
| Enum 重複 | 新 enum | LSP `workspaceSymbol` + rg 成員值 |
| Function 重複 | 新 func | `workspaceSymbol` + `outgoingCalls` 比對 |
| Data Structure 重複 | 新 dataclass | rg 欄位 overlap（Jaccard） |

**信心度評分**（加權加總）：

| 因子 | Enum | Function | Data Struct |
|------|------|----------|-------------|
| 名稱相似 | +3 | +5 | +3 |
| 值/簽名重疊 | +4 | +4 | +6 |
| Import 路徑已通 | +3 | — | +3 |
| 呼叫圖重疊 | — | +4 | — |
| 欄位重疊 >60%（Jaccard） | — | — | +5 |

**門檻**：HIGH ≥7 / MEDIUM 4-6 / LOW 1-3。只展示 HIGH + MEDIUM；LOW 收 drill-down。

**重用 lifecycle**：重用候選（RC）實作後（抽 helper），**重跑查新 symbol 落點**（dep weight + 消費者）— 實作 RC 是新結構決策，需 re-review 放置點再 commit。

### domain grounding（外部框架語意查證）

外部框架語意宣稱（NT/SJ account/equity/engine / 第三方能力邊界）**強制查 stub/source 附 path:line**。

- 觸發訊號：宣稱含「X 支援/不做 Y」「X 底層是 Z」「跨模型成立」等能力邊界語句
- **未 grounding 標 `open`（未驗證）非 `verified`** — 不隨 fix 寫進 instruction file 變正式宣稱

**RC-3 邊界**：domain grounding = **review / 結構審查時** grounding；與 [source-driven-development](../source-driven-development/SKILL.md)（實作 grounding）/ [external-api-investigation](../external-api-investigation/SKILL.md)（runtime 調查）/ [nt-query](../nt-query/SKILL.md)（能力查詢）區分，非第四個過載。

### LSP 查證（call chain）

| 查詢 | LSP 操作 |
|------|---------|
| 誰引用 X | `findReferences` |
| 誰呼叫 X | `incomingCalls` |
| X 呼叫誰 | `outgoingCalls` |

**機械分工**：scan-project / Pattern Radar **枚舉**（撈全 + 相似）= primary；**LSP 驗證**（特定 claim → ✅/❌，見 [lsp-navigation](../../rules/lsp-navigation.md)）= secondary（人鎖定嫌疑後才上驗證）。

> **圖譜 facts（CRG，companion）**：transitive impact radius / 跨檔 callers·flows / hub·community 等**圖譜級**結構事實，在 CRG 裝了的專案用 CRG（見 [crg-query](../crg-query/SKILL.md)）—— 三層 facts 互補：scan-project 給 folder/module 級枚舉、LSP 查單一 symbol、CRG 查 transitive graph。本 skill 的 City Map 資料 / hub / dep weight 在 CRG 專案可由 CRG `get_hub_nodes`/`get_impact_radius` 機械產，取代手推（但仍受 crg-query anti-over-reliance 約束：graph=structure≠behavior）。CRG 沒裝 → `[WARN]` + fallback scan-project/LSP（crg-query 的 assume+warn-if-absent）。

### 補償邏輯盤點（compensating pair detection）

**修缺陷前的反向搜尋** — 補 `findReferences` 的盲區。`findReferences` 查「誰依賴 X」（反向依賴），抓不到「誰在抵消 X 的 bug」（補償邏輯）：補償點 B **不引用**缺陷函式 A，B 引用「A 算錯」這個事實。修 A 不拆 B → A 從「錯但被抵消」變「對但重複」（double-count）或「對但歸零」。

**機械**（修缺陷函式 A 前，反向搜尋補丁 B）：
1. 反向 rg 補償訊號：`offset|compensate|手動補|workaround|FIXME|hack` + docstring「不含 X，在 Y」「為了抵銷」
2. **兩處 docstring 互相矛盾** = 補償邏輯指紋（一處說「含」、一處說「不含」— 其中一處常是補丁的藉口）
3. domain grounding 查「同名概念（proceeds / equity / total）是否被多層各算一次」
4. 找到補丁 B → **A 與 B 綁定一起改**（拆補丁 = 修缺陷的原子操作）；補「A+B 組合路徑」整合測試（見 [acceptance-evidence](../../rules/acceptance-evidence.md) L3 — 符號覆蓋綠 ≠ 組合路徑被測）

**與 ripple 的差異**：ripple 追「A 變 → 依賴 A 的 B 壞嗎」（單向，`findReferences` 可撈）；補償是「B 依賴 A 的 bug」（非引用關係，需主動反向搜訊號）。

> 真實歷史案例：修「漏算 SHORT proceeds」的 compute 函式（缺陷 A）沒拆上游 sizing 函式裡手動 `+ proceeds` 的補丁（B）→ proceeds 算兩次 → baseline 虛高 → 風控 breaker 永不觸發。`findReferences(A)` 不會帶到 B（B 不引用 A，B 抵消的是 A 的 bug）。

### 變更路徑計數（mutation-path counting）

**觸及 mutable state / invariant-bearing 模組時的變更審查**（條件必填 — leaf / 純 docs 跳過）。assumption delta 的手動紀律:自問「這個改動新增第幾條 state mutation path?破了哪個 invariant?」—— 語義 diff 工具只到 AST / behavior 層,無 invariant 層（research gap），solo 須手動計數。

**機械**（用 LSP `findReferences` / rg 找所有 write site）:

1. 找所有 write site（含 in-place field mutation），逐項計數，**不歸一類**
2. **判斷粒度（核心認知增量）**:被改的 state 是 domain invariant（跨層守恆，如 cash / position / risk limit）還是 local overlay（strategy-local optimistic update）?
3. 多 writer:by-design（optimistic update 多 site）還是 invariant 破壞?
4. ordering / atomicity
5. **CONCLUDE:single-writer 在哪個粒度成立** —— **ownership 粒度**（單一 owning class，多 write-site 仍 by-design overlay）vs **write-site 粒度**（單一寫入點）。多 write-site 但單一 ownership = by-design overlay，非 invariant 破壞。

**與補償邏輯盤點（上方）的關係**:compensating-pair 反向（誰抵消我的 bug，修缺陷語境）;mutation-path 正向（我新增幾條 writer，審查變更語境）—— 方向相反，正交不重疊，並列使用。

> 真實案例（mosaic POC A/B）:strategy `self.positions` overlay —— baseline（無此 step）找 6 writer 答「single-writer = no」（淺，易誤判該修）;treatment（含粒度判斷）找 12 writer（含 in-place mutation）答「single-writer = yes at class boundary（ownership 粒度）」—— ownership vs write-site 粒度區分是核心認知增量，避免「多 write-site = 該修」的淺判。

### core identification for review prioritization

**消費前述機械產出做「審查優先序」判定** — 把 dep weight / 消費者數 / hotspot / ripple 框成 core vs leaf 判定 + 審查深度建議，供 `/illustrate`（人 viewport，B 軸）渲染 selective review matrix 讓人判讀「先審哪、審多深」。**受眾中性**（見本文 §受眾中性）：產判定 + 建議，**不產**機器 finding、不釘嚴重度、不給 file:line 處方（那交 `/code-review`）。

**定義**（新詞錨定）：
- **core**（heavy human review）：高 `消費者數`（`imported_by`）+ lean/廣用 + 高 ripple（在 `dependency-graph.md` Ripple Impact Rules）的模組；**或**位於 domain critical path（bug 會 silent-corrupt 全下游）。
- **leaf**（放過 / behavior-only）：terminal consumer（library 內少被依賴）+ 低 ripple + 非 critical path。
- **審查深度 tier**：deep human review（core，逐行讀）/ structure viewport + spot-read（中）/ behavior-only（leaf）。
- **change-type triage**（「需不需要審」入口 gate，**非深度加權軸**）：變更類型先 triage —— generated / reproducible（protobuf stub、build artifact）→ 放行（可證偽判準：一旦 hand-modified 即升 source 必審）;rename / comment / logging → 放行;money-path / tribal-knowledge → 必審（已被 core / silent-corruption path 涵蓋，此處明示）;其餘隨 core / leaf 深度。**不另立深度軸** —— 修缺陷的高價值審查由補償邏輯盤點承接;本 triage 僅補「需不需要審」的入口判斷。change-type triage（此處，入口 gate）≠ risk-tier（acceptance-evidence，證據深度）≠ scope（execution-plan，planning gate）—— 語義不同，**勿機械套用為第四深度軸**（過度工程：第四軸強迫 LLM 自覺加權，是最弱形式）。

**資料來源（reference，不重造）**：
- [`scan-project`](../scan-project/SKILL.md) `dep_graph.modules.imported_by[]`（消費者數）+ `hotspots[]`（hotspot tier）。
- `dependency-graph.md`（[`maintain`](../maintain/SKILL.md) 步驟 1.3 持續維護的 Hotspots + Ripple Impact Rules — 持續真相源，非 snapshot；循環依賴集群若存在，其 ripple 會落在 Ripple Impact Rules 內）。
- 本 skill City Map 資料生成既有 dep weight / 反向耦合 flag。

**domain overlay**（不硬編特定領域）：project 可定義 domain-specific core overlay（bug 會污染全下游的 path）。**範例**（quant）：除權息調整 / volume 張↔股 / 風控 sizing / 會計總量。

**觸發**：人類要 audit 既有 code 骨幹穩固度（無特定 change）→ 先跑本 lens 產 matrix 分配審查資源，再逐個 core heavy review。對照 Anthropic selective-review：core 重投入、leaf 放過。

### 分析方法論誠實性（報告內部一致性）

**結構審查報告（本 skill 機械產出消費的格式）必含「方法論限制」段** — 誠實記錄用了什麼工具、什麼無法驗證，讓消費者（人 / 下個 session）能判讀結論可信度。這是機械能力落地的**品質閘門**，非附屬。

| 必填欄位 | 說明 |
|---------|------|
| 用了哪些工具 | LSP operation（hover/findReferences/...）/ rg / fd — 每類結論標明主工具 |
| 哪些無法驗證 | 未跑動態依賴分析、未跑 pytest --cov、workspace 在 worktree 非 production 等 |
| LSP workspace 狀態 | LSP 結果是 workspace 狀態相依（見 [lsp-navigation](../../rules/lsp-navigation.md)「Workspace 狀態相依性」）；私有 symbol findReferences 矛盾時先懷疑 reindex 時機，再懷疑工具能力 |
| 主觀研判標記 | 「刻意設計 vs 債」「可辯護 vs 該修」基於 DDD/Clean Architecture 原則推論，非機械結論 |

**反例（真實案例，cross-harness 驗證）**：同一 `_PREV_COUNT` 符號，Claude session `findReferences` 只回 intra-file（誤推論為「LSP 對私有 symbol 固有 false-negative」），ZCode session 卻成功回傳跨檔引用 — 根因是 pyright workspace reindex 時機。**方法論限制段誠實記錄此差異，比「LSP 不可靠」的錯誤結論更有價值** — 它讓下個 session 知道要 reindex 而非換工具。

## 三、流程注入點（spec/EP/build/review 各階段）

設計視角三主線在各階段的注入：

| 階段 | ① 依賴規則 | ② bounded context | ③ use case 驅動 |
|------|-----------|-------------------|----------------|
| **spec** | 研究「既有分層？」（非「功能怎麼塞」） | 邊界定義（Always / Ask First / Never） | UC 盤點 |
| **EP / illustrate** | 畫提案 city map「新東西落哪層？」 | city map 凸顯跨域存取 | 畫 use case flow「結構撐得起嗎」（人 gate） |
| **build** | 遵循依賴方向 | — | 段落引用 UC |
| **review** | 查反向依賴、循環（機械：`findReferences`） | findReferences 查跨域 | 回歸 use case 行為 |

機械能力在各階段被調用：如 review 階段同時用**視角**判反向依賴 + **機械** LSP `findReferences` 撈實際引用；illustrate 階段用**機械** City Map/Pattern Radar 撈結構資料供人判讀。

## 四、與既有 skill 邊界

- [source-driven-development](../source-driven-development/SKILL.md)：實作時 grounding 於文檔。本 skill 是**結構視角**（非文檔查證）+ domain grounding 是**審查時** grounding（非實作 grounding）— 兩者不重疊（domain grounding 四路區分詳 §二 RC-3）。
- [debugging-and-error-recovery](../debugging-and-error-recovery/SKILL.md)：除**自己 code** 的 bug。本 skill 是**設計視角**（預防性，非除錯）。
- [acceptance-evidence](../../rules/acceptance-evidence.md)：測試 / 驗收**證據階層**。本 skill 是設計層（證據階層是驗收層）。
- [api-and-interface-design](../api-and-interface-design/SKILL.md)：見 RC-2 邊界。

## 五、不適用 / 不做

**不適用**（場景排除）：
- 除錯 → `debugging-and-error-recovery`
- 查 API 用法 / 文檔 → `source-driven-development` / `context7-mcp`
- 測試策略 → `test-driven-development` / `validation-strategy`
- 強制套四層模板（本 skill 是視角，非模板）

**不做**（職責邊界，非流程注入）：
- **渲染心智模型**（節點 + 箭頭視覺）→ `/illustrate`
- **產 finding 格式**（嚴重度 / file:line）→ `/code-review`
- **決定受眾**（給人 / 機器）→ 消費命令
