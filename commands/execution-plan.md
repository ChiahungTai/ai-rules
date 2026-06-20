---
description: "段落式實作計畫書生成器，基於 /spec 規格摘要生成 Self-Contained Segments。/execution-plan \"任務描述\" [PROMPT檔案]"
when_to_use: "Use when a feature or refactor spans 3+ files, needs parallel agent execution, or scope is unclear. Skip for single-file changes, bug fixes, or straightforward tweaks unless high-risk."
usage: "/execution-plan \"實作任務描述\" [PROMPT檔案路徑]"
argument-hint: "<實作任務描述> [可選：PROMPT檔案路徑]"
---

# /execution-plan — 段落式實作計畫書生成器

基於 `/spec` 的規格摘要，生成段落式實作計畫書。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [planning-and-task-breakdown](../skills/planning-and-task-breakdown/SKILL.md) — 依賴圖分析、垂直切片、task sizing
- [agent-workflow](../skills/agent-workflow/SKILL.md) — 並發控制、模型偵測、Agent spawn 規範

---

## 核心概念：Self-Contained Segment

每個段落都是**完全獨立的功能單元**，AI 只需讀取該段落就能完成實作。

特徵：Context 獨立 / 功能完整 / 驗證自足 / 執行獨立

---

## EP 類型（ep_type：blueprint / implementation）

EP 分兩類，由任務規模決定：

| ep_type | 適用 | 結構 | build 行為 |
|---------|------|------|-----------|
| **implementation**（預設） | 小型 / 單一中型變更 | 完整段落（Context + 要點 + Pseudo Code + 驗證策略 + Scenario Matrix） | 正常逐段 /build |
| **blueprint**（綱要 EP） | **≥ 5 段都是中型變更**（每段本身需完整 EP 規劃深度，單一 EP 裝不下） | 段落是藍圖層級（描述要做什麼 + 依賴 + 吸收範圍）+ 每段標「→ 衍生子 EP（路徑）」；**不含可實作 Pseudo Code** | **不直接 /build** — 提示逐段衍生子 EP（見 `/build` 階段 0 ep_type 偵測） |

**欄位格式**（結構化，與 `parent` 一致 — `/build` 機械掃描欄位非語義字眼）：EP 標頭標 `> **ep_type**: blueprint` 或 `> **ep_type**: implementation`（預設 implementation，可不標）。blueprint EP 必標；implementation EP 若描述到 blueprint 概念也標（避免語義掃描自指誤判）。

**衍生機制**：blueprint EP 每段 → 衍生 implementation 子 EP（標 `parent: <master EP 路徑>` + 繼承該段 Context/依賴/吸收範圍）。子 EP 是完整 implementation EP，可獨立 /build。

**觸發條件**（避免過度工程）：任務含 ≥ 5 段都是[中型變更](../ai-development-guide.md)（變更規模分級見 ai-development-guide）→ blueprint；否則 implementation。視複雜度調整 — 小型任務硬拆成 blueprint 是過度工程。

---

## 🔴 UC 盤點（大型/中型變更必填，寫在 Scenario Matrix 之前）

> **核心原則**：UC-Driven Development 要求 CLAUDE.md Capabilities + .kanban/ 是開發的**起點**，不是段落的附屬品。EP 必須在一開始就盤點 UC，後續段落才能引用。

**何時需要**：大型/中型變更必填；小型變更（bug fix、文檔）跳過。

**執行步驟**（生成 EP 時的強制前置動作）：

1. **掃描相關 CLAUDE.md Capabilities + .kanban/ 卡片**：`rg` 搜尋受影響 library 模組目錄的 CLAUDE.md Capabilities 表格 + `.kanban/` cards，列出與本次變更相關的既有 UC
2. **判定 UC 變更類型**：

| 變更類型 | 說明 | EP 中的動作 |
|---------|------|------------|
| 📋 新增 UC | 本次變更引入新能力 | 在此區段定義新 UC（能力描述、實作路徑），後續段落引用 |
| 更新既有 UC | 既有 UC 的能力擴展或行為改變 | 標記能力描述 + 改變摘要，後續段落引用 |
| 無影響 | 既有 UC 不受影響 | 標記「無 UC 變更」即可 |

3. **掃描 .kanban/Backlog/ 關聯 + 自動建卡**（如果存在）：
   - 搜尋專案根目錄的 `.kanban/Backlog/` 目錄
   - 找出本次 EP 對應的 Backlog 卡片（能力描述 + 名稱）
   - EP 可能對應多張 Backlog 卡片，全部列出
   - **自動建卡**（EP 產出後執行）：
     1. 收集 EP 中所有「新增 UC」（UC 盤點 → 新增 UC 表格中的 📋 項目）
     2. 對照 `.kanban/Backlog/` 已有卡片，篩出**缺少卡片的能力**
     3. 為每個缺少卡片的能力在 `.kanban/Backlog/` 建立卡片（格式見 `/spec` 階段 3 的 Kanban Backlog 卡片格式）
     4. 為 EP 整體建立一張 Backlog 卡片（追蹤 EP 進度），內容引用所有相關能力
   - 無 `.kanban/` 目錄時：提醒用戶建立（`mkdir -p .kanban/{Backlog,Next-Up,In-Progress,Done}`），建立後再建卡

4. **掃描 SYSTEM-MAP.md 關聯**（如果存在）：
   - 搜尋專案根目錄的 `SYSTEM-MAP.md`
   - 找出本次 EP 影響的功能區塊及其生命週期狀態
   - 在 EP 中標注「本次 EP 影響 SYSTEM-MAP 中的功能：X（狀態），Y（狀態）」

5. **輸出格式**（放在 EP 的 top-level，段落之前）：

```markdown
## UC 盤點

### Backlog 關聯
- 列出相關 Backlog 卡片（能力描述 + 名稱）
- 自動建卡結果：新建 N 張卡片（列出能力描述 + 檔名）或「所有 UC 已有卡片」

### SYSTEM-MAP 影響
- [SYSTEM-MAP.md 存在時] 列出受影響功能 + 當前生命週期狀態（如「每日收盤 Pipeline 🏃」「Paper Trading Terminal ⚠️」）
- [SYSTEM-MAP.md 不存在時] 提醒用戶：目前無 SYSTEM-MAP.md，建議建立
- 無對應功能時寫「無」

### 掃描範圍
- [列出掃描的 CLAUDE.md Capabilities 路徑 + .kanban/ cards]

### 既有 UC 狀態
| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| 每日增量 K 線更新 | ✅ | CLAUDE.md Capabilities | 更新 | 擴展消費場景 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| [能力描述] | 📋 | [library 模組相對路徑] |
```

6. **段落引用**：每個段落的 Context 必須引用此處盤點的能力描述（如「實作 [能力描述]」「更新 [能力描述]」）

**為什麼放這裡**：UC 放在段落深處時，AI 傾向跳過或事後補寫。強制在 EP 最前面盤點，確保 UC 在段落設計之前就存在，段落才能正確引用。

---

## Scenario Matrix（大型/中型變更必填）

> **核心原則**：規劃時強制思考「使用者會遇到哪些情境」，避免實作完成才發現漏掉錯誤路徑或邊界案例。矩陣產出後散到 UC 的「消費場景」欄位。

**何時需要**：大型/中型變更必填；小型變更（bug fix、文檔）跳過。

**格式**（放在 UC 盤點之後、段落劃分原則之前，作為 top-level 區段）：

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | [使用者意圖] | [CLI flag / 事件 / 錯誤操作] | [系統該怎麼反應] | [恢復點 / 無] | [能力描述 或「—」] |

**必須涵蓋的場景類型**：
- Happy path（正常使用）
- 錯誤操作（缺參數、缺前置條件、assert fail 路徑）
- 邊界案例（空資料、跨日、回補多天）
- 效能期待差異（秒級、幾十秒、慢、線性放大）

**欄位含義**：見 [ai-development-guide.md](../ai-development-guide.md) 的「Scenario Matrix」段落

**散到 UC**：實作完成後，`/build` 階段 5a 從矩陣提煉自包含描述寫入對應 UC 的「消費場景」欄位（不引用 EP/SM 編號，因為 EP 可能歸檔或刪除）。

---

## 段落設計標準

每個段落必須包含：

### 1. Context

- **背景資訊**：基於 `/spec` 規格摘要
- **UC 引用**：本段落實作的能力描述（如「實作 [能力描述]」）。大型變更必須引用；中型變更更新既有 UC；小型變更可不引用
- **依賴關係**：與其他段落的依賴和整合點
- **語義約束**：與其他段落共享的隱含假設（型別定義、命名慣例、架構決策）。無則寫「無」，有則寫「與 S{N} 共享 [具體假設]」
- **基礎設施盤點**：設計 pseudo code 前的必做步驟（讀 CLAUDE.md 可複用基礎設施 → LSP `workspaceSymbol` + `rg` 搜尋相關元件 → 列出可複用元件或寫「無」）
- **依賴錨點**：EP 對現有程式碼的雙向錨定 — 每個依賴同時標注定義端與消費端（格式：`symbol` → 定義 `path/def.py:42` / 消費 `path/caller.py:156`）。用 LSP `goToDefinition` 驗證定義端、`findReferences` 驗證消費端。`/build` 時直接定位雙端，省去搜尋成本。執行前驗證錨點，drift 時先更新 EP
- **技術選型** + **成功標準**

### 2. 核心實作要點

主要類別、關鍵方法、設計決策、整合方式

### 3. Pseudo Code

類別結構 + 方法實現 + Call Stack + 錯誤處理。檔案結構用樹狀展示（非 mermaid）。空殼 class 用詳細註解標示設計意圖。

### 4. 驗證策略

POC/demo 設計 + 測試計畫 + 完成檢查 + 整合測試。**測試類型選擇紀律見 [validation-strategy](../skills/validation-strategy/SKILL.md)**（e2e 優先 > 單元隔離 / 交易 replay >>> live / 放 scripts/ / 不重驗 package NT·bokeh·panel）+ 結構視角見 [architecture-thinking](../skills/architecture-thinking/SKILL.md)。

**測試計畫內容**：描述測試的種類和情境，不寫數量（數字每次修改都過時，對決策無價值）。應包含：
- **測試類型分佈**：單元 / 整合 / E2E / 外部 API mock（選擇紀律見 validation-strategy）
- **關鍵情境覆蓋**：happy path、邊界案例、error handling、冪等性
- **已知未覆蓋的風險**：哪些路徑沒測到、為什麼

---

## 段落劃分原則

依賴圖分析、垂直切片、task sizing 遵循 [planning-and-task-breakdown](../skills/planning-and-task-breakdown/SKILL.md)。

EP 專屬約束：
- **語義顯式化**：段落間共享的隱含假設必須顯式標記
- **驗證自足性**：每段有獨立驗證策略

---

## 段落設計檢查清單

- [ ] UC 盤點已完成（大型/中型變更：掃描 CLAUDE.md Capabilities + .kanban/、列出新增/更新 UC、Backlog 關聯）
- [ ] Backlog 自動建卡已完成（新增 UC 已有對應 Backlog 卡片 + EP 整體追蹤卡片）
- [ ] Scenario Matrix 已填寫（大型/中型變更；涵蓋 happy path、錯誤操作、邊界、效能期待差異）
- [ ] 標題明確且獨立
- [ ] Context 包含所有必要背景
- [ ] UC 引用已標記（引用 UC 盤點區段的能力描述；大型必須，中型可選）
- [ ] Pseudo Code 具體可執行
- [ ] 驗證策略完整可執行
- [ ] 整合點清晰定義
- [ ] 語義約束已顯式標記
- [ ] 基礎設施盤點已完成
- [ ] 依賴錨點已標記

---

## docs mode（純文檔/rules 改動）

EP 變更全為 `rules/`、`skills/`、`commands/` 下的 `.md`（無 `.py` 邏輯）時進入 docs mode —— 段落元素裁剪程式碼導向部分，驗證改為文檔驗證。

**觸發判準**：變更全為 `.md` **且** 無新增/修改 `.py` callable 符號（`rg "^def |^class " --type py` 於本 EP 變更範圍為 0）→ docs mode。純 `.py` 搬移（無邏輯改）→ docs mode + 保留 mypy/pytest baseline。

**EP 元素對照**：

| EP 段落元素 | 程式碼 mode | docs mode |
|------------|------------|-----------|
| UC 盤點 | 掃 library Capabilities | 掃「受影響命令/rules 清單」（元專案無 Capabilities 表格）|
| kanban / SYSTEM-MAP | 強制 | 元專案 / 無對應時跳過（正當跳過，標記理由）|
| Context 錨點 | file:line 符號（LSP）| file:line 文檔行號錨點（rg 驗證行號指向預期內容）|
| Scenario Matrix | 大型/中型必填 | 影響命令行為時仍填，但「觸發/預期行為」改文檔語境（rg 命中/0 殘留），非程式執行結果 |
| Pseudo Code | 類別 + Call Stack | **裁剪**（文檔無類別）；以「修改要點」替代 |
| 驗證策略 | POC/demo + 測試 + 整合測試 | 改為文檔驗證（rg 殘留、跨檔一致性、`/consistency`、導航有效性）|
| TDD / mypy / ruff / pytest | 強制 | **跳過**（`/build` 階段 2 僅「修改 → rg 殘留 → 跨檔一致性 → `/consistency`」）|
| 整合路徑覆蓋 | `rg "<param>="` | **跳過**（或改為跨檔引用一致性 rg）|
| EP Review 維度 | Call Stack / Pattern Alignment | 改為「文檔一致性 + 設計合理性 + 引用 drift + 漏改」|
| 收尾 Capabilities + Kanban | 強制 | 元專案跳過；改為「受影響命令/rules 行為已反映 + `commands/CLAUDE.md` 命令索引 description 同步」|

docs mode 的 `/build` 執行分支見 [build.md](./build.md) 階段 0/2/3。

### ripple 語義反向撈（格式/術語統一類變更）

> docs mode EP 涉及**格式統一、術語改名、共用規範對齊**類變更時，ripple 靠逐檔枚舉會漏（LLM 想不到的檔案就漏）。逐檔枚舉之外補機械掃描，撈「自稱共用」與「定義源」兩類語義線索。

**觸發條件**（僅這類變更，避免過度工程）：EP 目標是統一格式 / 改名 / 對齊共用規範（非純新增、非純論述）。

**語義反向撈**（逐檔枚舉之外補）：
1. **自稱共用規範**：`rg "共用規範|與.*共用"` 撈所有自稱與權威源共用格式的檔頭/段落，逐一致性比對
2. **定義源**（術語改名時）：改名 ripple 必須含**定義該術語的源頭命令**（描述規範者，非僅使用），否則術語從上游再生

**限制**：語義撈降低漏率不消除 —— pattern 會漏同義表述（「遵循 template」「對齋」）、會 near-miss（「機械軸」≠「機械閘門」）。是「機械補人類遺忘」、需人工判讀命中，非 100% 覆蓋。

---

## EP Review Cycle

**Writer/Reviewer 分離**：用獨立 Agent context 審查 EP，避免主 LLM 審查自己的計畫。
**適應式多 Agent Review**：依模型並發上限和 EP 複雜度決定 spawn 幾個 review agent。

### Step 1: 偵測模型 → 查表

從系統提示詞偵測 GLM 模型，查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md) 決定 max-agents。
印出確認：`[Review Agent] model=X, max=N`

### Step 2: Adaptive Agent 數量

> EP Review 總用獨立 agent（強制品質閘門），不走 review-engine 的 Main LLM 模式 —— 刻意覆蓋。差別僅在單一 vs 平行：

**max-agents = 1**（haiku/opus）→ 跳至下方「單一 Agent Prompt（Fallback）」，行為等同原 single-agent。

**max-agents > 1**（如 sonnet = 4）→ 根據 EP 特徵啟用維度。**top-down 審查順序**：先結構（分層依賴/bounded context）後細部正確性（use case 覆蓋/兜底）— 結構錯了正確性審白費（視角見 [architecture-thinking](../skills/architecture-thinking/SKILL.md)）。

審查維度（「審 EP profile」：分層依賴 / bounded context / use case 覆蓋 / 場景 / 完整性 / 合規 / 遺漏 / 兜底拆解）定義見 [/ep-review](./ep-review.md) 五維度 + 維度映射表 — 本 Cycle 不自帶維度定義，與獨立 `/ep-review` 共用同一 profile（根治內建 vs 獨立 drift）。啟用：所有維度 always；啟用維度數 > max-agents → 從低優先級（場景/遺漏起）合併至前一個 agent（不丟棄任何維度）。

### Step 3: 平行 Spawn

同時 spawn 所有啟用的 review agents（subagent_type: "Explore"，read-only by design）。

每個 agent prompt 包含：
- EP 完整內容
- 該維度的檢查項目清單（見 [/ep-review](./ep-review.md) 五維度 + 維度映射表）
- 相關檔案路徑（必讀）
- 引用 [review-engine](../skills/review-engine/SKILL.md)（通用：嚴重度/信心水準/審查者自證/LSP 查證/模式判定規則）+ [architecture-thinking](../skills/architecture-thinking/SKILL.md)（Clean Arch 視角）+ [architecture-viewport](../skills/architecture-viewport/SKILL.md)（結構機械能力）+ [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) 方法論
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）

> **agents→skills 統一**（#B12 探討）：agent 審查知識（通用審查邏輯、Clean Arch 視角、結構機械能力、方法論）沉 skill 統一引用，agent prompt 只組裝 — 非各命令內嵌審查邏輯。EP review agent 引用 review-engine（通用）+ architecture-thinking + architecture-viewport（維度）+ code-review-and-quality（方法論），與 `/code-review`、`/illustrate` 共用同一組 skill（整脊「能力下沉」一致性）。

### 單一 Agent Prompt（Fallback，max-agents = 1）

Spawn Agent（subagent_type: "Explore"），prompt 包含：
- EP 完整內容
- Dry Run 驗證：
  1. **Call Stack 可行性**：pseudo code 每步能否跑通？
  2. **Pattern Alignment（最重要）**：EP 設計假設的 usage pattern 是否與 callers 實際 pattern 一致？
  3. **下游依賴發現**：有沒有 EP 沒提到的 callers？
  4. **邊界條件**：空值、null、缺少欄位等
- Clean Arch 審查（**top-down**：先結構後正確性，引用 [architecture-thinking](../skills/architecture-thinking/SKILL.md) + [code-review-and-quality](../skills/code-review-and-quality/SKILL.md)）：
  1. **分層依賴**：domain←use case←adapter←infra 依賴向內？有循環？Call Stack 可行？
  2. **bounded context**：不跨域存取 `_private`？邊界清楚？職責單一？
  3. **use case 覆蓋**：消費者要什麼行為？EP 撐得起？UC 完整覆蓋？每段有驗收標準？檔案完整？依賴遺漏？
  4. **兜底路徑驗證**：EP 預見極限（實作落差）+ 語義約束 drift + Rules 合規（命名、code-edit-constraints、_ai-behavior-constraints、CLAUDE.md 更新）+ 遺漏風險（Demo、測試、`__init__.py`、配置、受影響模組）+ 內部一致性
- 相關檔案路徑（必讀）

### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修正 EP。**修正必須寫入 EP 段落本身**（加入 EP review 區段表格，格式見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md) Finding Record），不是只記在審查報告裡。build 可能由不同 LLM session 執行，看不到審查報告。

---

## 收尾步驟（所有功能段落完成後必做）

> **核心原則**：EP 必須包含收尾段，列出所有功能段落完成後的強制收尾動作。`/build` 階段 5 執行。未完成收尾不得宣稱 EP 實作完成。

每個 EP 的收尾段必須包含以下三項：

### 1. CLAUDE.md Capabilities + Kanban 更新

- 已完成 UC：在對應模組 CLAUDE.md Capabilities 表格新增一行（能力 + 入口 + ✅）
- 移動 Kanban 卡片至 Done/ lane
- **原子操作**：Capabilities 新增 + Kanban 卡片移動必須同時完成
- **從 EP Scenario Matrix 提煉「消費場景」**（大型/中型變更）：將矩陣中所有引用該 UC 的場景，提煉成自包含一句話描述（不引用 EP/SM 編號），寫入 Capabilities 表格備註或 Kanban card 描述

### 2. SYSTEM-MAP.md 更新（如果存在）

- 根據 UC 狀態變化，更新 SYSTEM-MAP.md 中受影響功能的 life-cycle 狀態
- 更新全域狀態統計表（如有）
- 移除已修復的 ⚠️ 標記

### 3. CLAUDE.md 更新

- 檢查受影響模組目錄的 CLAUDE.md，確認架構描述反映變更
- 新增/修改：模組職責、導航指引、可複用基礎設施
- 遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準（Signal/Noise ratio、導航優先）

### 4. /audit-test

- 執行 `/audit-test` 對新增/修改的測試進行品質稽核
- 確認無反模式、覆蓋對稱性合理、mock 健康度良好
- 稽核結果附於 `/build` 完成報告

**小型變更**（bug fix）：僅執行 /audit-test，跳過 UC 和 CLAUDE.md 更新。

---

## 輸出

- **位置**：`ai-analysis/execution-plans/`（相對於專案根目錄）
- **檔名**：從任務描述自動衍生（kebab-case，`ep-` 前綴）
- **結構**：實作總覽 → **UC 盤點** → Scenario Matrix → 段落劃分原則 → 各段落（Context → 要點 → Pseudo Code → 驗證）→ 整合策略 → 收尾步驟

> **🔴 路徑警告**：Claude Code plan mode 的硬編碼路徑是 `~/.claude/plans/`，**那不是 EP 的存放位置**。EP 必須寫到專案目錄下的 `ai-analysis/execution-plans/ep-<name>.md`。若已寫入 `~/.claude/plans/`，完成後必須複製到正確位置。

---

## 流程位置

```
〔pre-EP 軟 gate〕對話討論 →〔提醒〕/illustrate 結構化提案（軟 gate 不硬擋）→ 確認
/spec（spec 可選前置）→ /execution-plan（含 EP Review, Clean Arch 視角 top-down）→ [/ep-validate] → /build（含 Agent Review）→ [/code-review] → /commit
```

前置：`/spec`（可選；pre-EP illustrate 結構確認為軟 gate 提醒，不硬擋）
後續：`/ep-validate`（可選，高技術風險時）→ `/build`（如需額外審查可跑獨立 `/ep-review` 或 `/judge-review`）
