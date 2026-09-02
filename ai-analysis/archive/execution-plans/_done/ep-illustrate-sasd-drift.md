# EP — /illustrate 強化：SA/SD code 解釋 + drift detection

> **ep_type**: implementation（4 段，每段中型變更；非 blueprint）
> **mode**: docs（全為 `.md`，無 `.py` callable 符號；驗證 = 文檔驗證非 TDD）
> **規模**: standard（跨 skill + 多 command 檔 + 新支援檔；🟡 結構性——改受眾中性共用 skill）

## 實作總覽

強化 `/illustrate` 的 code 解釋能力（mode B「理解既有」），注入 SA/SD 角度（system boundary / data-flow / call graph / scenario sequence / class slice），並把 drift detection 做成 mode B + post-EP/post-build checkpoint 的脊柱——直接回應使用者核心恐懼「AI coding 時代人類跟不上產碼速度，只能定期用大方向檢查是否走偏 / 程式碼失控」。

**設計主軸**（已通過 arch-thinking skill + 11-agent workflow 論證，使用者已批准）：
1. **Artifact Menu 為產品主軸**：mode B 三個鬆散標籤（運作流程/資料流/概念圖）→ 5 個 SA/SD artifact，人依「方向問題」選，每 artifact 綁 Mermaid 模板 + CRG-first/LSP-fallback fuel + when-to-use + anti-pattern
2. **3 資料生成能力沉 arch-thinking §二**（mirror 既有 City Map「資料生成（非渲染），渲染交 /illustrate」pattern）：call graph（函數級）/ type structure（contract slice）/ data-flow（靜態骨架）
3. **drift detection 脊柱**：SEED git diff（機械恆可用）→ GENERATE graph facts → BASELINE degradation ladder（EP-claimed optional gold → last commit 機械主幹 → HEAD~1 → current-only）→ DIFF 5 signal class → RENDER overlay；**no-severity 硬規**守住 layer-3 人類 viewport 線

**改動 target（嚴守 skill/command 分工）**：
| # | target | 性質 |
|---|--------|------|
| 1 | `skills/arch-thinking/SKILL.md` §二 +3 能力 + 釐清行；§五 +3 邊界 | S1 地基 |
| 2 | `commands/instruction/_common/illustrate-artifact-menu.md`（新檔）| S2 產品面 |
| 3 | `commands/illustrate.md` mode B 重綁（含 `:24`/`:29`/`:117`/`:151`）+ checkpoint drift + survey 表 + description sync | S3 |
| 4 | `commands/CLAUDE.md:53` pre-existing drift 修復 + `:63` 索引；`skills/CLAUDE.md:28` 索引同步；`commands/code-review.md:106` axis 3 列舉同步 | S3 ripple |
| 5 | `commands/instruction/_common/illustrate-structure-viewport.md`（含 `:4` 列舉）drill + drift rendering | S4 |
| 6 | `commands/instruction/_common/illustrate-deep-analysis.md` 程式碼分析模式改寫 | S4 |
| 7 | `AGENTS.md:49,81` description sync | S3（隨命令同步）|

**段落依賴順序**：S0 研究 → S1（skill 地基，定義資料能力）→ S2（menu 引用 S1 能力）→ S3（命令引用 S2 menu）→ S4（supporting 引用 menu + skill）

**硬約束**（每段必守）：
- `/illustrate` = layer-3 人類 viewport（B 軸）：渲染結構 artifact 給人判讀方向，**不產機器 finding**（severity/file:line 是 `/code-review` axis 3）
- arch-thinking skill **受眾中性**、三家共用（illustrate/code-review/ep-review）：跨命令共用 DATA → 沉 skill；illustrate 特有渲染 → 留命令
- **視角非模板**：不強制 4-layer、不過度工程
- CRG project-dependent：設計必須無 CRG 也能用（LSP/scan-project/rg fallback），有 CRG 時加值；遵循 crg-query assume-present + warn-if-absent（`[WARN]` 一行，不 block 不沉默降級）
- skill 產 DATA / 命令 RENDER（既有 split）

---

## UC 盤點（docs mode → 掃受影響命令/rules）

ai-rules 是定義 AI 規則的 meta repo（無 library Capabilities 表格），UC 盤點改為「受影響命令/rules 行為」。

### 受影響命令行為（= docs mode 的 UC）

| 行為 | 現狀 | 本 EP 動作 | 段落 |
|------|------|-----------|------|
| `/illustrate` mode B code 解釋 | 鬆散「運作流程/資料流/概念圖」，freehand 風險 | 改為 5 SA/SD artifact menu 驅動（default boundary + menu 展開） | S2/S3 |
| `/illustrate` 結構 viewport 三 checkpoint | pre-EP 軟 gate / post-EP / post-build（無 drift 機械化）| 圍繞 drift spine 重構（baseline degradation ladder + 5 signal class）| S3 |
| `/illustrate` drill 互動 | city/flow/reuse/verify/boundary | + `artifact <type> <target>`；formalize city→boundary、flow→sequence 映射 | S4 |
| `arch-thinking` skill §二 機械能力 | 8 子段（City Map 模組級為最細）| +3 資料生成能力（call graph 函數級 / type structure / data-flow）| S1 |
| `/code-review` axis 3 / `/ep-review` F3 | 消費 arch-thinking §二 | 消費資料受眾中性受惠（免改）；description 列舉同步（新能力可調用）| S1 + S3 ripple |

### 新增「能力」（命令行為層）

| 能力 | 狀態 | 實作入口 |
|------|------|---------|
| SA/SD artifact menu 驅動的 code 解釋 | 📋 | `commands/illustrate.md` mode B → `illustrate-artifact-menu.md` |
| drift detection（post-EP / post-build 方向漂移）| 📋 | `illustrate-artifact-menu.md` drift overlay + `illustrate.md` checkpoint |

### kanban / SYSTEM-MAP

- `.kanban/` / `SYSTEM-MAP.md`：ai-rules 無對應（meta repo，非功能專案）→ **正當跳過**（docs mode 元專案規則）。本 EP 不建 kanban card、不更新 SYSTEM-MAP。

### 掃描範圍
- `commands/illustrate.md`、`commands/instruction/_common/illustrate-*.md`（5）、`skills/arch-thinking/SKILL.md`、`commands/CLAUDE.md`、`skills/CLAUDE.md`、`AGENTS.md`、`skills/{crg-query,scan-project,mermaid}/SKILL.md`、`rules/lsp-navigation.md`

---

## Scenario Matrix（docs mode — 文檔語境）

| # | 場景 | 觸發 | 預期行為（文檔層級） | Checkpoint | 對應 |
|---|------|------|---------------------|-----------|------|
| SM-1 | mode B 無 crisp 方向問題，看既有 code | `/illustrate @模組` 無進一步指定 | 渲染 **default boundary diagram** + 展開 menu（非 freehand）；標 audience-B | 無 | mode B default |
| SM-2 | mode B 有具體方向問題 | 「這個 use case 怎麼跑」/「這欄位從哪來」/「改這個誰受影響」 | 依方向問題綁到對應 artifact（sequence/data-flow/call graph），grounded 渲染 | 無 | artifact menu |
| SM-3 | post-build 懷疑漂移（核心恐懼）| build 完，怕程式碼失控 | git diff seed → change-scoped graph facts → drift overlay 5 signal class；**no-severity**；位置 path:line 可點 | baseline = last commit（無 EP）或 EP-claimed | drift detection |
| SM-4 | post-EP 前瞻方向驗證 | EP 寫完，未 build | EP-claimed（optional gold，附 confidence）vs current-actual diff；catch EP 假設不成立（call 不存在 symbol、wrong-layer） | EP-claimed gold | drift detection |
| SM-5 | 非 CRG 專案 | 無 `.code-review-graph/graph.db` | graceful degrade：emit `[WARN]` 一行 + LSP/scan-project/rg fallback；仍渲染（call graph 無 transitive、sequence 單 path） | 無 | fuel fallback |
| SM-6 | conditional class slice | 變更觸及 abstract/Protocol/繼承 shape vs 純 dataclass 新增 | 觸及 abstraction shape → render class slice；純 dataclass → 靜默跳過（YAGNI）| 無 | Q2 決策 |
| SM-7 | 無 EP 的 fix/docs 變更 | 非 build 流程的零星改動 | baseline degradation ladder 落到 last commit → HEAD~1 → current-only（無 diff 僅渲染，仍 grounded 非 freehand）| current-only | drift ladder |
| SM-8 | drift signal 誤判風險 | +edge 可能是合法演化非 scope creep | 每 signal 附 EP/baseline 原話（若 baseline=EP）讓人看「授權了什麼」；no-severity 硬規防「drift=bad」偏見 | 無 | drift render |
| SM-9 | docs mode 消費端（純 docs repo 無 code）| 於無 `.py` 的 repo 呼叫 `/illustrate @模組` | dep_graph/LSP 不適用 docs → fallback rg 跨檔畫命令/skill 拓樸（arch-thinking §二 product-type 雙軌 docs 軌）；標「docs mode：結構靠 rg 跨檔，非 AST/LSP」；data-flow/call graph artifact 降級為文件引用拓樸 | 無 | docs 軌 fallback |
| SM-10 | ZCode harness class slice 降級 | user on ZCode（pyright 無 typeHierarchy + 無 goToImplementation）跑 class slice | best-effort chaining（hover + findReferences on base + rg）產 partial edges；方法論誠實段標「ZCode 無 goToImplementation，繼承鏈 partial」；不宣稱完整階層 | 無 | multi-harness 誠實 |
| SM-11 | CRG↔LSP 效能期待落差 | user 期待 CRG transitive impact radius，但非 CRG 專案 LSP fallback 只给 single-hop | `[WARN] degraded：無 transitive blast radius（CRG 未安裝）`；說明 LSP fallback 為 direct callers/callees only；期待管理（非 silent 給差結果）| 無 | fuel 期待管理 |

---

## 段落劃分原則

- **語義顯式化**：artifact menu 詞彙 = drill 詞彙（Q6 統一單一詞彙表，降 drift）；「§二 既有 LSP 查證 = 單 symbol 驗證，新增 = 多 symbol AGGREGATION」釐清行跨 S1/S2 共享
- **驗證自足**：每段文檔驗證（rg 殘留 + 跨檔一致性 + 導航有效性），不依賴他段執行
- **依賴**：S1 定義資料能力 → S2 menu 引用 → S3 命令引用 menu → S4 supporting 引用。逐段 build

---

## 段落 0：全域研究摘要

> 詳細研究由 Explore agent 完成（file:line 證據），此為 EP 自足濃縮。build agent 以此為 grounding。

### 可複用基礎設施（mirror 對象）
- `### City Map 資料生成（非渲染）`（`skills/arch-thinking/SKILL.md:71-83`）—— 新 3 能力 mirror 此 pattern。核心格式句（`:73-74`）：「**生成資料**（...）；**視覺渲染**（...）留 `/illustrate`（既有渲染引擎）」。每能力只生成資料 items（bullet 形式），不內嵌渲染圖。
- `### LSP 查證（call chain）`（`:117-128`）—— 既有單 symbol 驗證；新能力在此段加 1 行釐清（AGGREGATION vs 驗證，刻意並列不合併）。

### Fuel-source 事實（artifact menu fuel spec 必須引用正確名稱）
- **CRG MCP ops**（`skills/crg-query/SKILL.md:37-44, 51-61`）：`query_graph` callers_of/callees_of、`get_impact_radius`（transitive）、`get_affected_flows`/`get_flow`、`list_communities`/`get_community`/`get_architecture_overview`、`get_hub_nodes`/`get_bridge_nodes`、`detect_changes`、`semantic_search_nodes`。⚠️ **陷阱**：`detect_changes` 是 MCP tool；`analyze_changes` 是內部函式非 MCP tool（`:39,55`），不可誤引。assume-present + warn-if-absent GATE（`:27`）：缺 CRG → emit 一行 `[WARN] CRG graph not available — structural context degraded; install: uvx code-review-graph install && build` + fallback，不 block 不沉默。
- **LSP ops 跨 harness**（`rules/lsp-navigation.md`）：8 標準 ops。`goToImplementation`：Claude 有 / ZCode pyright 無（`:157`）。**`typeHierarchy`：兩家皆無**（`rules/lsp-navigation.md` 全文 rg 0 hits——避免本 EP 自身使用 typeHierarchy 字眼污染計數）→ class slice 繼承只能 **chaining**（hover + documentSymbol + findReferences on base + goToDefinition 拼），誠實標記。
- **scan-project dep_graph 欄位**（`skills/scan-project/reference/unified-snapshot-schema.md:43-58`）：`modules.{file_count, internal_deps, external_deps, imported_by[], fan_out}` / `edges[]` / `hotspots[]`。Graceful degradation（`skills/scan-project/SKILL.md:59-65` + `reference/unified-snapshot-schema.md:111`）：無 `tools/scan_imports.py` 則全空。⚠️ **docs mode**：dep_graph 是 `.py` AST，**不適用 docs 場景**（`arch-thinking:65-66`）—— 但本 EP 描述的能力是給**消費端 Python code 專案**用（ai-rules 定義、消費端執行），spec 本身是文檔，不矛盾。
- **mermaid 約束**（`skills/mermaid/SKILL.md`）：禁 `%%{init}%%`（`:14`）、fill+color 成對（`:20`）、**最多 3 styled group**（`:22` 硬限制）、註解 `%%` 獨占行（`:23`）、安全 4 色 success/fail/warn/info（`:26-31`）、禁純黑/白/灰（`:33`）、emoji 優先（`:36`）、emoji 節點名須引號 `A["🚀 開始"]`（`:36`）。

### 插入點錨點（精確行號，build 直接定位）
- `skills/arch-thinking/SKILL.md` §二 = `:56-190`；新 3 能力插在 **`:83`（City Map 段末）後、`:84`（`### Pattern Radar`）前**
- §五「不做」= `:211-223`；新 3 邊界加在 **`:222` 後**（L222 為現最後「決定受眾」行）
- `commands/illustrate.md`：mode B table row **`:29`**、mode 章節 intro **`:24`**（殘留「概念圖」舊標籤，S3 需同步）、決策流程 B branch **`:117`**、能力 survey 表 **`:141-148`**、委託 Skills §二 列舉 **`:151`**、supporting files 表 **`:156-163`**、frontmatter description **`:2-3`**
- `commands/instruction/_common/illustrate-structure-viewport.md`：檔頭能力來源列舉 **`:4`**、drill 命令 block **`:10-16`**、欄位←發布者 authority annotation **`:47-53`**（吸收為 data-flow first-class edge type）
- `commands/instruction/_common/illustrate-deep-analysis.md`：程式碼分析模式 **`:45-60`**

### Ripple（改定義源後逐檔同步——single-source drift 防護）

> 「視角 §一、機械 §二」描述跨 **5 檔約 8 處**（清單 non-exhaustive，以 rg 為準；5 full-pair「§一+§二」+ 3 §二-only）。其中 **3 處為逐條列舉 §二 能力**（非層級引用），新 3 能力後必 stale，**必須同步列舉**：
> - `commands/illustrate.md:151`（委託 Skills 段，列舉「city map 資料/dep weight/Pattern Radar/LSP 查證」）→ S3 加新 3 能力
> - `commands/instruction/_common/illustrate-structure-viewport.md:4`（檔頭，列舉 6 items）→ S4 加新 3 能力
> - `commands/code-review.md:106`（axis 3，列舉「city map / dep weight / 重用枚舉 / LSP 查證」）→ S3 ripple 加新 3 能力
>
> 「消費資料免改」（受眾中性，code-review/ep-review 不需改就受惠新能力）≠ 「描述列舉免改」—— 後者是文檔層會 stale，需同步。
>
> 其餘層級引用（ep-review `:18,85`、code-review `:81,105`、illustrate `:102` pre-EP checkpoint 段、illustrate-structure-viewport `:4` 檔頭、crg-query `:95`、execution-plan `:317`）多為「§二」層級提及，新增能力不破壞語義；但 `skills/CLAUDE.md:28` 索引行列舉 §二 能力 → **必須加新 3 能力**。
>
> 全 repo sweep 驗證（S3/S4 收尾）：`rg "§二|結構機械|結構資料|city map 資料/dep weight"` 確認 §二 擴充不破壞語義 + 列舉處已同步。

### 風險假設（等級 + 吸收段落）
| 等級 | 風險 | 吸收 |
|------|------|------|
| 🔴 高 | pyright 無 typeHierarchy + ZCode 無 goToImplementation → class slice 只能 chaining | S1 type structure 能力段明文標記「best-effort chaining，非完整階層」+ 方法論誠實性 + SM-10 |
| 🔴 高 | menu 與 skill 兩真相源 drift 無機械 sync gate | S3 收尾加 self-check（rg 比對）；建議未來登記 `/sync-sources` invariant |
| 🔴 高 | docs mode 下 dep_graph/LSP 不適用（本 repo 自身）| 不影響（能力給消費端 code 專案用）；spec 明文標消費端適用；SM-9 覆蓋 docs 消費端 |
| 🟡 中 | CRG project-dependent → 非 CRG 專案 drift 降級 | 沿用 assume-present + warn-if-absent（S1/S2 各 artifact fuel spec）；SM-5/SM-11 |
| 🟡 中 | mermaid max 3 styled group 限制 drift overlay | S2 drift render：5 signal → 3 bucket 顯式映射（marker 重用 style）、emoji 優先 |
| 🟡 中 | 新 3 能力破壞 §二 漸進順序 | 插入位置在「枚舉型資料生成」區塊內（City Map 後），符合現有邏輯 |
| 🟡 中 | section renumbering ripple（S1 段內）| S1 修改採 **heading text 定位 + 從大到小執行**（先 §五 → LSP 查證 → 插入 3 段），避免行號 drift；活躍文檔多為 §二 層級引用 |

---

## S1：arch-thinking §二 +3 資料生成能力 + §五 +3 邊界（skill 地基）

### Context

**背景**：arch-thinking §二 現有 8 機械能力，最細只到 City Map（模組級）。code 解釋需要的函數級 call graph、type structure、data-flow lineage 缺第一類資料生成能力。LSP call ops（incomingCalls/outgoingCalls/findReferences）目前只用於單 symbol 反應式驗證（`:117-128`），未做 AGGREGATION 產資料集。這 3 能力跨命令共用（illustrate 渲染 / code-review axis 3 finding / ep-review F3 驗證）→ 嚴格通過 capability-sink test，沉 skill。

**UC 引用**：實作「arch-thinking skill §二 機械能力擴增」（受影響命令行為表）。code-review axis 3 / ep-review F3 受眾中性受惠（消費免改；description 列舉同步見 S3 ripple）。

**依賴關係**：本段是 S2/S3/S4 的地基——menu 的 artifact fuel spec（S2）、命令能力 survey 表（S3）都引用本段定義的能力名。無上游段落依賴（S1 是起點）。

**語義約束**：與 S2 共享——「§二 既有 LSP 查證 = 單 symbol 反應式驗證（claim→✅/❌）；新增 3 能力 = 多 symbol AGGREGATION（產資料集）——同工具、不同 consumption pattern，刻意並列不合併」（防新能力被誤讀為重複 LSP 查證）。

**基礎設施盤點**：mirror `### City Map 資料生成（非渲染）`（`:71-83`）pattern。CRG ops（段落 0 fuel 事實）、LSP ops（`:117-128`）、scan-project dep_graph（段落 0）。新能力不重造——複用 CRG/LSP/scan-project 為 fuel source。

**依賴錨點**：
- 插入點 → 定義 `skills/arch-thinking/SKILL.md:83`（City Map 段末 `⚠️ polars helper...` 行）/ 消費 `:84`（`### Pattern Radar` 標題）
- §五邊界 → 定義 `skills/arch-thinking/SKILL.md:219`（`**不做**` 段標題）/ 消費 `:222`（現最後一行「決定受眾」）
- skills/CLAUDE.md 索引 → 定義 `skills/CLAUDE.md:28`（arch-thinking 索引行列舉 §二）

**技術選型**：3 能力條件觸發（如既有補償邏輯盤點/變更路徑計數——依問題型別 fire 非 always-on）+ 優先序標記（data-flow > call-graph > type-structure，type-structure 標 YAGNI）。**3 能力 atomic 一次沉**的理由：mutually referencing（data-flow 的 type-bearing edge 消費 call graph edges）+ 共用 fuel baseline（CRG-first / LSP-fallback 同一套）+ 同 mirror City Map pattern（單一資料生成段家族）—— 非關聯三件事，拆開反而割裂共用 fuel/pattern。mirror City Map「資料生成非渲染」——不內嵌渲染。

**成功標準**：§二 新增 3 個 `### Xxx 資料生成（非渲染）` 子段，格式 mirror City Map；LSP 查證段加 1 行釐清；§五 加 3 條邊界；`skills/CLAUDE.md:28` 索引同步；跨檔「§二」層級引用不需改、列舉處同步（S3/S4）。

### 修改要點（docs mode 取代 pseudo code）

> **執行順序**（防 section renumbering）：**從大到小**——先改 §五（`:211-223`）→ 再 LSP 查證段（`:117-128`）加釐清行 → 最後在 `:83` 後插入 3 能力子段。或全用 **heading text 定位**（`## 五、不適用 / 不做`、`### LSP 查證`、`### City Map 資料生成`），不依賴行號。

**1. §二 插入 3 能力子段**（在 `### City Map 資料生成` 段末後、`### Pattern Radar` 前，mirror City Map 格式：標題 `### Xxx 資料生成（非渲染）` + 「生成資料...；渲染交 /illustrate」格式句 + bullet 資料 items + flag 範例）：

- **`### Call Graph 資料生成（函數級，非渲染）`** — 優先序：中（補非 CRG 專案 fallback）。生成資料：函數/方法級 caller→callee edges（scoped 至 entry symbol + N hops，**非全系統**），每條 edge 標 parse-time-static。Fuel：CRG-first（`query_graph` callers_of/callees_of direct + `get_impact_radius` transitive blast——LSP 無法高效做）→ LSP-fallback（incomingCalls/outgoingCalls 跨 N symbol AGGREGATION walk，bounded depth，`[WARN]` 無 transitive degraded）→ scan-project dep_graph 模組級脈絡。**CRG 缺 → emit `[WARN]`（crg-query GATE，假設呈現）+ LSP fallback**。CRG-sourced edges 附 anti-over-reliance label（graph=structure≠behavior；dynamic dispatch/config/reflection 不可見）。資料範例 bullet：`Strategy.on_bar() → Executor.submit_order()`（direct, 2 callers）等。

- **`### Type Structure 資料生成（contract slice，非渲染）`** — 優先序：低（YAGNI 風險）。生成資料：**僅 abstract/Protocol/繼承 realization edges**；concrete members 不產（derivable、low-signal、違 instruction-writing.md + 人審結構上限）。Fuel：**LSP-primary**（CRG 此處弱——持 call/import edges 非 type edges）：hover 取 base classes + documentSymbol 取 members + goToImplementation 取 subclass overrides（Claude 有/ZCode pyright 無→findReferences on base + rg fallback）+ chaining 組裝繼承鏈。**誠實標記**：pyright 無專用 typeHierarchy operation（兩家皆無），繼承是 chaining 非 single call；best-effort，complex hierarchy/metaclass 產 partial edges。

- **`### Data-Flow 資料生成（靜態骨架，非 runtime 值）`** — 優先序：**最高**（silent-corruption / 數據完整性對齊）。生成資料：producer→transform→consumer edges，每條附靜態 type/contract（可推導時）。**吸收既有「欄位 ← 發布者」authority annotation**（`illustrate-structure-viewport.md:47-53`）為 first-class edge type。Fuel：hybrid 無單一 source——CRG flows（`get_affected_flows`/`get_flow`）+ LSP outgoingCalls（type-bearing edges，hover 取型別）+ scan-project dep_graph（模組級方向）。**CRG 缺 → emit `[WARN]`（crg-query GATE）+ LSP/scan-project fallback**。**HARD BOUNDARY**：runtime data VALUES out-of-scope（三者皆不產，須 read/run code，acceptance-evidence L4-L5）；明確標與 acceptance-evidence Runtime Invariant Assurance 互補（本能力=靜態結構骨架；Runtime Invariant Assurance=持續 runtime 監控——不同軸、不重疊）。資料範例：`<balance> ← <exec_client>`（authority edge）等。

**2. LSP 查證段（`:117-128`，`### LSP 查證` heading 下）加 1 行釐清**（在 `**機械分工**` 段後）：
> 「§二 既有 LSP 查證 = 單一 symbol 反應式驗證（claim→✅/❌）；上方新增 call graph / type structure / data-flow 資料生成 = 多 symbol AGGREGATION（產資料集，非驗證單一 claim）——同工具、不同 consumption pattern，刻意並列不合併。」

**3. §五「不做」（`:219-223`，`## 五、不適用 / 不做` heading 下 `**不做**` 段）加 3 條邊界**（在「決定受眾」行後）：
- **動態 sequence / runtime call stack 萃取 → 不做**（需 runtime tracing 工具，屬工具層 gap 非 skill 範疇；靜態 call graph 資料由 §二 產，動態 sequence 渲染交 /illustrate 以概念流程呈現）
- **drift-signal 分類（+edge/-edge/+type/broken-caller/boundary-crossing）→ 不做**（viewport/消費者的 framing 非 structural fact；skill 只產 graph facts {caller, callee, transitive set, type edges, data edges}，消費命令套用受眾專屬 framing——illustrate overlay marker vs code-review severity-tagged finding）
- **EP-claimed structure extraction + drift diff + drift 渲染 → /illustrate**（viewport-specific，非結構機械事實）

**4. `skills/CLAUDE.md:28` 索引行同步**：在 arch-thinking 索引行列舉的 §二 能力清單加「call graph（函數級）/type structure（contract slice）/data-flow（靜態骨架）」。

### 驗證策略（docs mode — 文檔驗證）

- **rg 殘留/存在性**：`rg "Call Graph 資料生成|Type Structure 資料生成|Data-Flow 資料生成" skills/arch-thinking/SKILL.md` → 3 hits；`rg "動態 sequence|drift-signal 分類|EP-claimed structure extraction" skills/arch-thinking/SKILL.md` → 3 hits（§五邊界）；`rg "單一 symbol 反應式驗證.*多 symbol AGGREGATION" skills/arch-thinking/SKILL.md` → 1 hit（釐清行）
- **[WARN] / crg-query GATE**：`rg "\[WARN\]|crg-query.*GATE|assume-present" skills/arch-thinking/SKILL.md` → ≥2 hits（call graph + data-flow 段各一）
- **Runtime Invariant 互補邊界**：`rg "Runtime Invariant Assurance" skills/arch-thinking/SKILL.md` → 1 hit（data-flow 段互補邊界落地）
- **pattern 一致性**：3 新能力段標題皆含「（非渲染）」，與 City Map（`:71`）一致；皆有「生成資料...；渲染交 /illustrate」格式句
- **跨檔一致性**：`skills/CLAUDE.md:28` 含新 3 能力；rg「§二|結構機械」全 repo sweep 確認層級引用語義成立
- **導航有效性**：3 新能力段的 CRG/LSP op 名與段落 0 fuel 事實一致；⚠️ 校對 `detect_changes` 非 `analyze_changes`
- **誠實標記**：type structure 段含「pyright 無 typeHierarchy、chaining、best-effort」；data-flow 段含「runtime VALUES out-of-scope + Runtime Invariant Assurance 互補」
- **/consistency**：對 `skills/arch-thinking/SKILL.md` 跑 `/consistency`

---

## S2：新增 illustrate-artifact-menu.md（產品面核心）

### Context

**背景**：mode B 現三標籤（運作流程/資料流/概念圖）讓 LLM 無法把「方向問題」綁到能回答的 artifact → freehand 風險（grounding 核心關切：類圖 zero extraction method）。本段建 artifact menu——人依方向問題選 artifact，每 artifact 綁 Mermaid 模板 + fuel spec + when-to-use + anti-pattern，殺死 freehand。menu 是 illustrate 特有**渲染產物**（audience-B），留命令側**不沉 skill**（capability-sink rule）。

**UC 引用**：實作「SA/SD artifact menu 驅動的 code 解釋」（新增能力 📋）+ 「drift detection」（新增能力 📋 的 overlay spec 落點）。

**依賴關係**：上游 S1（menu 的 fuel spec 引用 S1 定義的 3 能力）。下游 S3（illustrate.md 引用本檔）、S4（drill 映射到本檔 artifact）。

**語義約束**：與 S3/S4 共享——artifact 詞彙 = drill 詞彙（Q6 單一詞彙表）：boundary / data-flow / call-graph / sequence / class-slice。每 artifact 標 audience-B + 「不產 file:line finding（那是 /code-review axis 3）」。

**基礎設施盤點**：fuel 引用 S1 能力 + 段落 0 fuel 事實（CRG/LSP/scan-project op 名）。Mermaid 模板遵守 `skills/mermaid/SKILL.md` 約束（段落 0 A4）。吸收既有「欄位←發布者」authority annotation（`illustrate-structure-viewport.md:47-53`）為 data-flow artifact 的 first-class edge。

**依賴錨點**：
- 新檔路徑 → `commands/instruction/_common/illustrate-artifact-menu.md`
- 引用端 → `commands/illustrate.md:156-163`（supporting files 表，S3 加一行 link）/ `commands/illustrate.md:29`（mode B row，S3 改引用）

**技術選型**：on-demand reference 檔（非 auto-load，控制 instruction-surface 成長）。5 artifact 各 5 元素（方向問題 / Mermaid 模板 / fuel spec / when-to-use / anti-pattern）。drift overlay spec 含 5 signal class + baseline degradation ladder + no-severity 硬規。**Mermaid 範例須完整遵守 mermaid skill 約束**（給 build agent 完整可抄模板，非標籤級描述）。

**成功標準**：新檔含 5 artifact（各 5 元素）+ drift overlay spec；Mermaid 模板遵守 mermaid skill 約束（含完整範例）；每 artifact 標 audience-B + 不產 finding；default artifact（boundary）標示（Q4）；class-slice 標 conditional（Q2）；每 CRG-dependent artifact 標 [WARN]。

### 修改要點

**新增 `commands/instruction/_common/illustrate-artifact-menu.md`**，結構：

**_header_**：載體說明（illustrate.md mode B 的 artifact menu 支撐檔；on-demand；audience-B 人類 viewport；不產 file:line finding）。

**_default + menu 邏輯_**（Q4）：mode B 無 crisp 方向問題 → default **boundary diagram**；有方向問題 → 從 menu 選。

**_5 artifact 各一節_**（每節 5 元素）：

1. **System / Module Boundary**（default）
   - 方向問題：新東西落在對的 context/layer 嗎？AI 在重造既有模組嗎？邊界被跨越嗎？
   - Mermaid：`flowchart` + `subgraph` per bounded context/layer；directed edges = 允許依賴方向；dashed edges = leak/forbidden（跨層/跨域）
   - Fuel：CRG-first（`list_communities` + `get_architecture_overview` + `get_hub_nodes`/`get_bridge_nodes`）/ fallback（scan-project `dep_graph.modules.imported_by[]` + AGENTS.md Capabilities）。**CRG 缺 → emit `[WARN]`（crg-query GATE）+ scan-project/AGENTS.md fallback**。⚠️ caveat：community ≠ module boundary（目錄+AGENTS.md 是真相，community 只 coupling hint）
   - When-to-use：mode B 理解整體骨架 / EP（新節點落對 context 嗎）/ post-build drift（boundary-crossing signal）
   - Anti-pattern：raw 全系統拓樸 dump

2. **Data-Flow Lineage / DFD**（最高優先級，silent-corruption 對齊）
   - 方向問題：我在意的 data 從哪來、誰 transform、誰消費？新 code 插在 pipeline 對的點嗎？
   - Mermaid：`flowchart LR`（nodes = producers/transforms/consumers；edge labels = data type 或 contract）
   - Fuel：hybrid（CRG `get_affected_flows`/`get_flow` + LSP outgoingCalls type-bearing edges + scan-project dep_graph 模組方向 + 吸收「欄位 ← 發布 client」authority edge）。**CRG 缺 → emit `[WARN]`（crg-query GATE）+ LSP/scan-project fallback**。**runtime data VALUES：三者皆無——須 read/run code（L4-L5），標 static-skeleton-only**
   - When-to-use：mode B 追蹤 field 來源 / EP（讀對 source、插對 pipeline 點）/ post-build drift（producer shifted 或 consumer 期望 field 被停發 = silent-corruption 前兆）
   - Anti-pattern：宣稱 runtime 值（只產靜態骨架）

3. **Change-scoped Call Graph**（drift 主幹 substrate）
   - 方向問題：我改這個，誰受影響？
   - Mermaid：`graph`（**pruned impact-radius subgraph，禁全系統**）；CRG-sourced edges 附 anti-over-reliance label
   - Fuel：CRG-first（`query_graph` callers_of/callees_of direct + `get_impact_radius` transitive blast）/ fallback（LSP incomingCalls/outgoingCalls AGGREGATION walk——S1 能力，無 transitive，`[WARN]` degraded）/ scan-project dep_graph 模組級脈絡
   - When-to-use：post-build drift（主用——change blast radius）/ mode B 理解 call 結構 / EP（call 方向 vs DIP：domain←use case←adapter）
   - Anti-pattern：全系統 call graph（重造 /code-review 結構軸 + 耗盡人類注意力）

4. **Scenario Sequence**（OOAD 動態）
   - 方向問題：這個 use case，對的 component 以對的順序跨對的邊界協作嗎？
   - Mermaid：`sequenceDiagram`（lifelines = components/boundaries；messages = calls；layer 分 group + notes）。**單一 scenario**（whole-system sequence 是噪音）
   - Fuel：CRG-first（`get_affected_flows`/`get_flow`——real call chains，唯一高效 source）/ fallback（LSP outgoingCalls 從 entrypoint recursive walk，manual single-path，`[WARN]` single-path-only）。**consume S1 call-graph 資料 scoped to one scenario**（不另立 data-gen）。anti-over-reliance：parse-time edges 漏 dynamic dispatch/config/reflection
   - When-to-use：mode B（use case 怎麼跑）/ EP（component 協作順序、跨禁制 layer 嗎）/ post-build drift（scenario 路徑上的新邊）
   - Anti-pattern：全系統 sequence；宣稱 runtime tracing（靜態概念流程 viewport-only）

5. **Contract Class Slice**（OOAD/UML，conditional——Q2）
   - 方向問題：這個模組由什麼 abstraction 錨定，新 code 是遵循/擴展它還是 fork 它？
   - Mermaid：`classDiagram`（**僅 abstracts/Protocols + inheritance/realization edges；hide concrete members**）
   - Fuel：**LSP-primary ALWAYS**（CRG 此處弱——持 call/import edges 非 type edges）：hover base + documentSymbol members + goToImplementation overrides（Claude 有/ZCode 無）+ findReferences on base 組裝繼承鏈。**誠實標記**：pyright 無 typeHierarchy op 故 chaining。fallback：rg for class defs
   - When-to-use：**conditional**——僅變更觸及 abstract/Protocol/繼承 shape 時 render；純 dataclass 新增靜默跳過（YAGNI）。mode B（模組由什麼 abstraction 錨定）/ EP（新 code 榮譽或 fork 既有 Protocol 嗎）/ post-build drift（+type = parallel-abstraction candidate——是否重造既有）
   - Anti-pattern：full class diagram（每 concrete class + attrs + methods——derivable + 人審結構上限）

**_完整 Mermaid 範例_**（build agent 可抄模板，遵守 mermaid skill 約束——max 3 styled group、fill+color 成對、emoji 引號、安全 4 色、禁 init）：

boundary artifact 範例（default）：
```
flowchart LR
  subgraph Domain["📦 Domain"]
    A["Strategy"]
  end
  subgraph Adapter["🔌 Adapter"]
    B["Executor"]
  end
  A --> B
  B -.->|"leak?"| A
```
> 約束自檢：無 `%%{init}%%`；emoji 節點名引號；subgraph = 2（≤3）；dashed edge 標 leak（無 style 行即免 fill+color，若加 style 須成對）。

**_Drift Overlay Spec_**（drift detection 共用段）：
- **5 signal class**（視覺 marker，**非 finding**）：`+edge`（新 call 不在 baseline，scope-creep candidate）/ `-edge`（baseline 宣稱 call 不在 build，under-build）/ `+type`（新 class/Protocol，parallel-abstraction candidate）/ `broken-caller`（caller 簽名/contract 不符，contract-drift）/ `boundary-crossing`（邊違反 baseline layer/context，layer-violation）
- **5→3 bucket 映射**（mermaid max-3-styled-group 硬限制，marker 重用 style 不倍增）：
  - bucket **added**（➕）= `{+edge, +type}` —— 一個 style
  - bucket **removed/broken**（➖）= `{-edge, broken-caller}` —— 一個 style
  - bucket **violated**（⚠️）= `{boundary-crossing}` —— 一個 style
  - 共 3 styled group（合規）；Console ASCII 用 `+`/`-`/`!` 三 marker 對應
- **baseline degradation ladder**：① EP-claimed（gold，**OPTIONAL**——LLM-heuristic parse EP，每 bucket 附 confidence label，低信心可 dismiss；非 load-bearing）→ ② last commit（機械主幹：`git show HEAD:<code>` 取 HEAD 版本 code → 重產 graph facts → diff current 產出的 graph facts）→ ③ HEAD~1 → ④ current-only（無 diff，僅渲染 change-scoped artifact，仍 grounded 非 freehand）
- **no-severity 硬規**：NO severity、NO file:line fix recommendation、NO「this is wrong」verdict——僅「this moved; you judge direction」。每個 +edge 旁附 EP/baseline 原話（若 baseline 是 EP）讓人看「授權了什麼」（SM-8 防 drift=bad 偏見）
- **skill/command 分工重申**：drift-signal 分類由 illustrate 套用（S1 §五 counter-rule：skill 只產 graph facts）

**_drift rendering 範例_**（Console ASCII + MD）：

Console ASCII（call graph with drift markers + legend）：
```
  Strategy.on_bar() ──+──▶ Executor.submit()      [+edge: 新 call]
                   ──!──▶ RiskGuard.check()       [!: broken-caller]
  Executor.submit() ─────────▶ (nothing)          [-edge: baseline 宣稱未實作]
  legend: + added(➕)  - removed(➖)  ! violated/broken(⚠️)
```
MD Mermaid overlay（3 styled bucket，fill+color 成對，emoji）：
```
flowchart LR
  S["Strategy"] --> E["Executor"]
  S --> R["⚠️ RiskGuard"]
  classDef added fill:#d4edda,color:#155724
  classDef broken fill:#f8d7da,color:#721c24
  class S,E added
  class R broken
```

### 驗證策略（docs mode）

- **結構完整性**：5 artifact 各含 5 元素（方向問題/Mermaid/fuel/when-to-use/anti-pattern）——rg heading 計數 + 人工核對
- **Mermaid 約束遵守**：rg `%%{init` → 0 hits（禁）；每個 style 範例 fill+color 成對（rg `classDef.*fill.*color`）；無單獨黑/白/灰；emoji 節點名用引號；**drift overlay styled group ≤ 3**（數 bucket mapping 的 classDef 行）
- **[WARN] / crg-query GATE**（每 CRG-dependent artifact）：`rg "\[WARN\]|crg-query.*GATE|assume-present" commands/instruction/_common/illustrate-artifact-menu.md` → ≥4 hits（boundary + data-flow + call graph + sequence 各一；class-slice LSP-primary 不需）
- **5→3 bucket 映射**：drift overlay spec 含 added/removed/violated 3 bucket 定義；rg `bucket` → ≥3 hits
- **fuel op 名正確**：rg 比對 CRG op（callers_of/callees_of、get_impact_radius、get_affected_flows/get_flow、list_communities、get_architecture_overview）與段落 0 A1；⚠️ 無 `analyze_changes` 誤用
- **audience-B 標註**：每 artifact 含「不產 file:line finding」或對等標記
- **Q2/Q4 決策落地**：boundary 標 default；class-slice 標 conditional（純 dataclass 跳過）
- **導航有效性**：從 `illustrate.md` supporting files 表可 link 到本檔（S3 加 link 後驗）
- **/consistency**：對本檔跑 `/consistency`

---

## S3：illustrate.md 命令本體重綁 + description sync + drift 修復

### Context

**背景**：把 illustrate.md 的 mode B 定義（含 `:24` intro 殘留「概念圖」）、決策流程、checkpoint、能力 survey 表、委託 Skills 列舉（`:151`）都重綁到 S2 的 artifact menu + drift spine。同步修 pre-existing drift（CLAUDE.md:53）+ description 真相源 + skills/CLAUDE.md:28 索引 + code-review.md:106 axis 3 列舉。

**UC 引用**：更新「mode B code 解釋」「結構 viewport 三 checkpoint」+ 實作「drift detection」命令端落點。

**依賴關係**：上游 S1（能力 survey 表引用新能力）、S2（mode B 引用 menu）。本段是命令端整合 + ripple 同步。

**語義約束**：與 S2 共享 artifact 詞彙；與 S4 共享 checkpoint/drift 描述（本段定義命令端，S4 定義 drill/render 細節）。

**基礎設施盤點**：現有 mode 章節 intro `:24`、mode B row `:29`、決策流程 `:117`、能力 survey `:141-148`、委託 Skills §二 列舉 `:151`、supporting files `:156-163`、frontmatter `:2-3`。description 真相源：AGENTS.md `:49,81`、commands/CLAUDE.md `:53,63`、code-review.md `:106`。

**依賴錨點**：
- `commands/illustrate.md:24`（intro「概念圖」）/ `:29`（mode B row）/ `:117`（決策流程 B）/ `:141-148`（survey）/ `:151`（委託 §二 列舉）/ `:156-163`（supporting files）/ `:2-3`（frontmatter）
- `commands/CLAUDE.md:53`（pre-existing drift）/ `:63`（命令索引）
- `commands/code-review.md:106`（axis 3 列舉 ripple）
- `AGENTS.md:49,81`（受眾表）
- `skills/CLAUDE.md:28`（S1 已改 §二，本段確認索引行含新能力）

**技術選型**：mode B 改為參照 menu（非 inline 展開，避免 menu 與命令兩真相源 drift）；checkpoint 圍繞 drift spine 重構但保留三時點架構；能力 survey 表 +3 ✅已沉 / +3 ❌留 illustrate。

**成功標準**：mode 章節 intro `:24` + mode B row `:29` + 決策流程 `:117` 綁 menu（非 freehand，無殘留「概念圖」）；委託 Skills `:151` 列舉同步新能力；三 checkpoint 含 drift degradation ladder；survey 表 +6 行；4 真相源 description 同步；CLAUDE.md:53 drift 修復；code-review.md:106 + skills/CLAUDE.md:28 列舉同步。

### 修改要點

**1. frontmatter（`:2-3`）**：description / when_to_use 加「SA/SD code 解釋 artifact menu（call graph/sequence/class slice/data-flow/boundary）+ drift detection」關鍵詞（保觸發詞前置）。

**2. mode 章節 intro（`:24`）**：「能力（city map / 假設驗證 / diff / **概念圖**）服務 mode」→ 把「概念圖」改為「SA/SD artifact」（或泛稱 artifact menu），與 `:29` 同步殺死舊標籤（否則 EP 收尾 rg sweep `概念圖` 會 fail）。

**3. mode B row（`:29`）**：`運作流程 + 資料流 + 概念圖` → `參照 [artifact menu](./instruction/_common/illustrate-artifact-menu.md)：call graph / sequence / class slice / data-flow / system boundaries`。加註：「mode B artifact = 方向問題 + Mermaid 模板 + CRG-first/LSP-fallback fuel，**非 freehand**；靜態結構由 arch-thinking skill 資料 grounding，動態 sequence 為概念流程 viewport-only。default = boundary diagram（無 crisp 方向問題時）」。

**4. 決策流程 B branch（`:117`）**：`讀 code → 運作流程 / 資料流 / 概念圖 → 渲染 → 人理解` → `讀 code → 依方向問題從 artifact menu 選 artifact（default boundary）→ grounded 渲染 → 人理解`。

**5. 三 checkpoint 圍繞 drift spine 重構**（pre-EP / post-EP / post-build 段）：加 drift degradation ladder + 5 signal class 引用（細節在 S2 menu 的 drift overlay spec，命令端只 frame 三時點）：
- post-EP = diff EP-claimed（optional gold）vs current-actual pre-build（catches EP 假設不成立）
- post-build = diff EP-claimed（或 last commit）vs built actual（5 signal class 為主產出——正是「程式碼失控」恐懼的機械化呈現）
- 加 baseline degradation ladder 一行（EP gold → last commit → HEAD~1 → current-only）

**6. 能力 survey 表（`:141-148`）+6 行**：
- +3 ✅已沉（跨 illustrate/code-review/ep-review）：`call graph（函數級）資料生成`、`type structure（contract slice）資料生成`、`data-flow（靜態骨架）資料生成` → arch-thinking skill
- +3 ❌留 illustrate：`artifact menu（5 artifact + drift overlay spec）`、`drift diff（5 signal class）`、`drift rendering（Console/MD overlay）` → illustrate-artifact-menu.md / illustrate-structure-viewport.md

**7. 委託 Skills §二 列舉（`:151`）同步**：arch-thinking 能力列舉（「city map 資料/dep weight/Pattern Radar/LSP 查證」）→ 加「call graph（函數級）/type structure（contract slice）/data-flow（靜態骨架）」。

**8. supporting files 表（`:156-163`）+1 行**：`illustrate-artifact-menu.md` — artifact menu + drift overlay（mode B / drift checkpoint 時讀）。

**9. description 真相源同步**：
- `AGENTS.md:49`（LLM blind spot 表）/ `:81`（受眾表）：/illustrate 描述加「SA/SD artifact menu + drift」
- `commands/CLAUDE.md:63`（命令索引）：/illustrate 行加「SA/SD code 解釋 + drift detection」
- 🔴 **修 `commands/CLAUDE.md:53` pre-existing drift**：selective review matrix 段把 mode B 從 "city map / call path" 改為一致描述（「mode B（artifact menu：call graph / sequence / class slice / data-flow / boundary，B 軸人 viewport）」）
- `skills/CLAUDE.md:28`（S1 已改 §二）：確認索引行含新 3 能力（data-flow / call graph / type structure）

**10. code-review.md:106 axis 3 列舉同步**（ripple）：axis 3 description 列舉（「city map / dep weight / 重用枚舉 / LSP 查證」）→ 加「call graph（函數級）/type structure/data-flow」。理由：消費資料受眾中性免改（code-review 不需改就受惠新能力），但 **description 列舉是文檔層會 stale**，同步讓使用者讀 axis 3 知道可調新能力產更細 finding。

### 驗證策略（docs mode）

- **rg 殘留**：`rg "運作流程 \+ 資料流 \+ 概念圖|概念圖" commands/illustrate.md` → 0 hits（mode B 舊標籤 + intro 殘留全清）；`rg "artifact menu|illustrate-artifact-menu" commands/illustrate.md` → hits（綁定）
- **跨檔一致性**：rg「mode B」於 commands/CLAUDE.md / AGENTS.md —— 描述與 illustrate.md:29 一致（修復 :53 drift 後）；`rg "city map / call path" commands/CLAUDE.md` → 0 hits（drift 修復）
- **survey 表**：含 3 ✅ + 3 ❌ 新行；rg `已沉.*arch-thinking` 與 `留.*illustrate` 配對
- **列舉同步**：`commands/illustrate.md:151` + `commands/code-review.md:106` 含新 3 能力；`skills/CLAUDE.md:28` 含新 3 能力
- **description 同步**：4 真相源（illustrate frontmatter、AGENTS.md ×2、CLAUDE.md 命令索引）含「SA/SD / drift」關鍵詞
- **drift ladder**：三 checkpoint 段含 degradation ladder 引用
- **/consistency**：對 illustrate.md + commands/CLAUDE.md + code-review.md 跑 `/consistency`
- **/sync-sources**：跑 `/sync-sources`（檢查 audience classification 一致）

---

## S4：illustrate-structure-viewport.md（drill + drift rendering）+ illustrate-deep-analysis.md（程式碼分析模式）

### Context

**背景**：supporting files 端——drill 擴充（mid-session 切 artifact）+ drift rendering 格式（kill freehand 不一致圖）+ deep-analysis 程式碼分析模式改寫（移除泛泛 freehand 意涵，指向 grounded skill+menu）。同步 structure-viewport 檔頭 `:4` 的 §二 能力列舉。

**UC 引用**：更新「drill 互動」+ 支撐 artifact menu 的渲染格式。

**依賴關係**：上游 S2（drill 映射到 menu artifact；drift rendering 引用 menu overlay spec）、S1（drill verify 仍指 LSP 反應式驗證；檔頭 `:4` 列舉同步新能力）。

**語義約束**：artifact 詞彙 = menu 詞彙（Q6）：drill `artifact <type>` 的 type 用 menu name（boundary/data-flow/call-graph/sequence/class-slice）。

**基礎設施盤點**：檔頭能力來源列舉 `:4`、drill block `:10-16`、authority annotation `:47-53`（S1 已吸收為 data-flow edge，本段確認 viewport 端引用一致）、deep-analysis 程式碼分析模式 `:45-60`。

**依賴錨點**：
- `illustrate-structure-viewport.md:4`（檔頭 §二 列舉）/ `:10-16`（drill block）/ `:47-53`（authority annotation，data-flow 引用）
- `illustrate-deep-analysis.md:45-60`（程式碼分析模式）

**技術選型**：drill `artifact <type> <target>` 沿用既有 drill pattern（city/flow/reuse/verify/boundary）——formalize 映射，低新增成本。drift rendering 格式遵守 mermaid skill 約束（max 3 styled group → 5 signal 用 3 bucket marker 重用 style）。

**成功標準**：檔頭 `:4` 列舉同步新能力；drill 加 `artifact` 指令（含 call-graph 範例）+ city→boundary/flow→sequence 映射；drift rendering 格式段（Console ASCII markers / MD Mermaid 3-bucket overlay）；deep-analysis 程式碼分析模式指向 skill+menu（無 freehand）。

### 修改要點

**1. `illustrate-structure-viewport.md` 檔頭能力來源列舉（`:4`）同步**：「能力來源：City Map 資料 / dep weight / Pattern Radar / domain grounding / LSP 查證 / product-type 雙軌」→ 加「call graph（函數級）/ type structure（contract slice）/ data-flow（靜態骨架）」。

**2. `illustrate-structure-viewport.md` drill block（`:10-16`）擴充**：
- 加 `artifact <type> <target>`（mid-session 切 active menu artifact，如 `artifact sequence <use-case>`、`artifact class-slice <module>`、`artifact data-flow <field>`、`artifact call-graph <symbol>`（drift 主用——change blast radius））
- formalize 映射行：`city` → boundary artifact；`flow` → sequence artifact；`reuse` → Pattern Radar（mode A）；`verify` → LSP 反應式驗證（不變，仍非 holistic 判讀）；`boundary` → boundary artifact
- 加一行：「menu artifact selection replaces 舊鬆散 運作流程/資料流/概念圖 labels；drill switches artifact，verify stays reactive」

**3. `illustrate-structure-viewport.md` 新增 drift rendering 格式段**（引用 S2 menu drift overlay spec，此處定義 viewport 端格式）：
- **Console**：ASCII call graph with drift markers（`+`/`-`/`!` inline on edges + legend mapping marker→signal-class；對應 S2 3 bucket：added/removed-violated/violated）
- **MD**：Mermaid `flowchart`/`classDiagram` with 3 styled bucket（**max 3 styled group——5 signal class 用 added{+edge,+type} / removed-broken{-edge,broken-caller} / violated{boundary-crossing} 3 bucket，每 bucket 一個 style**）；fill+color 成對；emoji 優先標狀態；位置用 repo-root 相對 path:line（VS Code Cmd+Click，沿用既有「位置標示」慣例）
- 重申 no-severity / no-file:line-fix / 無「this is wrong」verdict——僅「this moved; you judge direction」（每個 drift-rendering site 重複此 constraint，防 audience split 崩潰）

**4. `illustrate-deep-analysis.md` 程式碼分析模式（`:45-60`）改寫**：
- 泛泛「代碼架構分析：關鍵類別、方法、設計模式」/「模組間依賴：介面定義、數據傳遞」→ 明確引用：「代碼架構分析 → 調 [arch-thinking](../../../skills/arch-thinking/SKILL.md) skill（City Map 模組級 + call graph 函數級 + type structure contract slice + data-flow lineage）；渲染 artifact 見 [illustrate-artifact-menu](./illustrate-artifact-menu.md)」
- 移除 freehand 意涵（指向 grounded 能力，非泛泛 bullet）

### 驗證策略（docs mode）

- **rg 殘留**：`rg "artifact <type>|artifact sequence|artifact class-slice|artifact data-flow|artifact call-graph" illustrate-structure-viewport.md` → hits；`rg "關鍵類別、方法、設計模式" illustrate-deep-analysis.md` → 0 hits（泛泛清除）
- **檔頭列舉同步**：`illustrate-structure-viewport.md:4` 含新 3 能力
- **drift rendering**：含 Console ASCII markers + MD Mermaid 3-bucket overlay 段；rg `no-severity|this moved` → hit（硬規重申）；styled bucket ≤ 3（added/removed-broken/violated）
- **mermaid 約束**：drift overlay 範例 fill+color 成對、emoji 引號、無 init、≤3 group
- **映射一致性**：drill 映射（city→boundary、flow→sequence）與 S2 menu artifact 詞彙一致（Q6）
- **導航有效性**：deep-analysis 引用 arch-thinking + artifact-menu link 路徑正確（rg link target 存在）
- **/consistency**：對兩檔跑 `/consistency`

---

## 整合策略

- **詞彙單一源**（Q6）：artifact 詞彙（boundary/data-flow/call-graph/sequence/class-slice）定義在 S2 menu，S3 命令 + S4 drill 全部引用——rg 確認無同義變體
- **drift spine 貫穿**：S1 產 graph facts（§五 counter-rule：不產 signal class）→ S2 定義 5 signal class + 3 bucket + degradation ladder → S3 命令端 frame 三 checkpoint → S4 渲染格式。no-severity 硬規在每個 drift-rendering site 重複
- **fuel 一致性**：所有 artifact 的 CRG/LSP op 名以段落 0 A1/A2 為單一源；S1/S2 引用一致；⚠️ `detect_changes` 非 `analyze_changes`
- **[WARN] 一致性**：每 CRG-dependent artifact（boundary/data-flow/call-graph/sequence；class-slice LSP-primary 免）都標 crg-query GATE [WARN]
- **跨命令受眾中性**：S1 新能力給 illustrate（渲染）/ code-review（finding）/ ep-review（驗證）共用——消費免改；description 列舉同步（illustrate:151 / code-review:106 / skills/CLAUDE.md:28 / structure-viewport:4）

---

## 收尾步驟（docs mode）

### 1. 模組 instruction 檔 Capabilities + Kanban
- ai-rules 為 meta repo（無 library Capabilities 表格、無功能 kanban）→ **正當跳過**（docs mode 元專案規則）。改為：受影響命令行為已反映（mode B / checkpoint / drift 在命令檔更新）+ `commands/CLAUDE.md` 命令索引 description 同步（S3 已做）。

### 2. SYSTEM-MAP.md
- ai-rules 無 SYSTEM-MAP.md（meta repo）→ 跳過。

### 3. instruction 檔更新
- 已由各段落完成（S1-S4 即 instruction 檔更新本身）。遵循 instruction-writing.md（Signal/Noise、導航優先、禁元資訊）。

### 4. /audit-test
- docs mode 無新增測試 → 跳過 `/audit-test`（無測試可稽核）。

### 5. docs mode 專屬收尾驗證
- **`/consistency`** 對所有改動檔跑一次（arch-thinking SKILL.md / illustrate.md / illustrate-artifact-menu.md / illustrate-structure-viewport.md / illustrate-deep-analysis.md / commands/CLAUDE.md / commands/code-review.md / skills/CLAUDE.md / AGENTS.md）
- **`/instruction:sync`**（或 `--recursive`）：機械驗證 illustrate.md → artifact-menu / structure-viewport / deep-analysis link target 存在 + 新檔 navigation effective（本 EP 新增檔 + 多處 link 變動，導航有效性須機械驗證）
- **rg 跨檔一致性 sweep**：artifact 詞彙單一源、CRG/LSP op 名一致、mode B 描述 4 真相源一致、**無遺留「運作流程/資料流/概念圖」舊標籤**（含 illustrate.md:24/29/117）、無 `analyze_changes` 誤用、§二 能力列舉處（illustrate:151 / code-review:106 / structure-viewport:4 / skills/CLAUDE.md:28）皆同步
- **`/sync-sources`**：跑一次（檢查 audience classification 一致；雖 menu/skill 兩真相源無專屬 invariant，rg sweep + /instruction:sync 為替代）
- **單一詞彙表校驗**（Q6）：rg 確認 menu artifact name = drill artifact type = 命令引用名，無變體

### 6. pre-existing drift 清單（順手修，S3 吸收）
- ✅ `commands/CLAUDE.md:53` mode B "city map / call path" 不一致 —— S3 修復

### 7. 建議（非本 EP 範圍，記錄供未來）
- menu/skill 兩真相源 drift：建議未來登記 `/sync-sources` check_single_source.py REGISTRY 一條 invariant（artifact menu 詞彙 ↔ skill §二 能力清單 ↔ 各命令列舉處），機械閘門長期保護

---

## EP Review Findings（EP Review Cycle 套用紀錄）

> 審查：3 Agent（force 獨立、subagent_type Explore、read-only）+ judge-review。無 Critical。全部 findings 採納並套用至上方段落。

| ID | 維度 | 嚴重度 | finding | 套用位置 |
|----|------|--------|---------|---------|
| B-F1 | F3 | Important | ripple 行號 `:143` 偏移（實際 `:102`）| 段落 0 Ripple 段改 `:102` |
| A-F1/B-F4 | F3 | Important | ripple 計數「6 處」實際 8 處 | 段落 0 Ripple 改「5 檔約 8 處 non-exhaustive」|
| C-F1 | F1 | Important | `illustrate.md:24` 殘留「概念圖」致收尾 sweep fail | S3 修改要點 #2 + 段落 0 錨點 + 收尾 sweep |
| C-F2 | F3 | Important | `illustrate.md:151` + `structure-viewport:4` 逐條列舉 stale | S3 #7 + S4 #1 + 段落 0 Ripple 標列舉處 |
| C-F6 | F3 | Suggestion→採納 | `code-review.md:106` axis 3 列舉 stale（消費免改 ≠ 描述免改）| S3 #10 + 段落 0 Ripple + 整合策略 |
| A-F2 | F3 | Important | Boundary/Data-Flow fuel 缺 `[WARN]`（silent-degrade 風險）| S2 artifact 1/2 fuel + S2 驗證 + S1 call-graph/data-flow + 整合策略 |
| B-F6 | F2 | Suggestion→採納 | drift 5 signal → max-3-group 映射未定 | S2 Drift Overlay Spec 5→3 bucket 映射 + S4 |
| C-F9 | F1 | Suggestion→採納 | mermaid 範例標籤級描述，首次 build 違反風險 | S2 完整 boundary 範例 + drift rendering 範例 |
| C-F3 | F5 | Important | SM 缺 docs 消費端/ZCode 降級/效能落差 | SM-9/10/11 |
| B-F2 | F2 | Important | mermaid SKILL.md 行號 off-by-one（`:21`→`:22`, `:22`→`:23`）| 段落 0 A4 |
| B-F3 | F3 | Important | typeHierarchy「全 repo 0 hits」被 EP 自身污染 | 段落 0 A2 改「lsp-navigation.md 該檔 0 hits」|
| A-F5 | F3 | Suggestion→採納 | `<graph>` placeholder 語義鬆 | S2 baseline ladder 改 `git show HEAD:<code>` 重產 facts |
| C-F5 | F1 | Suggestion→採納 | 收尾缺 `/instruction:sync` | 收尾 step 5 |
| C-F7 | F1 | Suggestion→採納 | S1 段內行號 drift 未警示 | S1 修改要點執行順序（從大到小/heading text）+ 風險表 |
| A-F3 | F3 | Suggestion→採納 | Runtime Invariant Assurance rg check 缺 | S1 驗證 + Data-Flow 段 |
| A-F4 | F3 | Suggestion→採納 | 3 能力 atomic 沉缺論證 | S1 技術選型補論證 |
| C-F4 | F1 | Suggestion→採納 | 摘要表少列 AGENTS.md | 實作總覽 target 表 #7 |
| B-F5 | F2 | Suggestion→採納 | scan-project 行號未標檔名 + off-by-one | 段落 0 A3 標檔名 + `:59-65` |
| C-F8 | F5 | Suggestion→採納 | drill 缺 `artifact call-graph` 範例 | S4 #2 補範例 |

**審查結論**：結構撐得起 build（capability-sink / 受眾中性 / 段落依賴 / 兜底假設全 PASS）；引用準確（op 名 / mermaid 約束 / 詞彙單一源全對）；完整性達標（docs mode + Q1-Q6 落地 + 收尾主軸）。18 項 findings 全採納套用。
