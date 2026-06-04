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

## 🔴 UC 盤點（大型/中型變更必填，寫在 Scenario Matrix 之前）

> **核心原則**：UC-Driven Development 要求 USE-CASES.md 是開發的**起點**，不是段落的附屬品。EP 必須在一開始就盤點 UC，後續段落才能引用。

**何時需要**：大型/中型變更必填；小型變更（bug fix、文檔）跳過。

**執行步驟**（生成 EP 時的強制前置動作）：

1. **掃描相關 USE-CASES.md**：`rg` 搜尋受影響 library 模組目錄下的 `USE-CASES.md`，列出與本次變更相關的既有 UC
2. **判定 UC 變更類型**：

| 變更類型 | 說明 | EP 中的動作 |
|---------|------|------------|
| 📋 新增 UC | 本次變更引入新能力 | 在此區段定義新 UC（ID、簡述、實作路徑），後續段落引用 |
| 更新既有 UC | 既有 UC 的能力擴展或行為改變 | 標記 UC ID + 改變摘要，後續段落引用 |
| 無影響 | 既有 UC 不受影響 | 標記「無 UC 變更」即可 |

3. **輸出格式**（放在 EP 的 top-level，段落之前）：

```markdown
## UC 盤點

### 掃描範圍
- [列出掃描的 USE-CASES.md 路徑]

### 既有 UC 狀態
| UC ID | 狀態 | 影響 | 說明 |
|-------|------|------|------|
| D-18 | ✅ | 更新 | 擴展消費場景 |

### 新增 UC
| UC ID | 狀態 | 簡述 | 實作路徑 |
|-------|------|------|---------|
| D-35 | 📋 | [能力描述] | [library 模組相對路徑] |
```

4. **段落引用**：每個段落的 Context 必須引用此處盤點的 UC ID（如「實作 D-35」「更新 D-18」）

**為什麼放這裡**：UC 放在段落深處時，AI 傾向跳過或事後補寫。強制在 EP 最前面盤點，確保 UC 在段落設計之前就存在，段落才能正確引用。

---

## Scenario Matrix（大型/中型變更必填）

> **核心原則**：規劃時強制思考「使用者會遇到哪些情境」，避免實作完成才發現漏掉錯誤路徑或邊界案例。矩陣產出後散到 UC 的「消費場景」欄位。

**何時需要**：大型/中型變更必填；小型變更（bug fix、文檔）跳過。

**格式**（放在 UC 盤點之後、段落劃分原則之前，作為 top-level 區段）：

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應 UC |
|---|------|------|---------|------------|---------|
| SM-1 | [使用者意圖] | [CLI flag / 事件 / 錯誤操作] | [系統該怎麼反應] | [恢復點 / 無] | [UC ID 或「—」] |

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
- **UC 引用**：本段落實作的 UC ID（如「實作 D-31」）。大型變更必須引用；中型變更更新既有 UC；小型變更可不引用
- **依賴關係**：與其他段落的依賴和整合點
- **語義約束**：與其他段落共享的隱含假設（型別定義、命名慣例、架構決策）。無則寫「無」，有則寫「與 S{N} 共享 [具體假設]」
- **基礎設施盤點**：設計 pseudo code 前的必做步驟（讀 CLAUDE.md 可複用基礎設施 → `rg` 搜尋相關元件 → 列出可複用元件或寫「無」）
- **依賴錨點**：EP 對現有程式碼的雙向錨定 — 每個依賴同時標注定義端與消費端（格式：`symbol` → 定義 `path/def.py:42` / 消費 `path/caller.py:156`）。`/build` 時直接定位雙端，省去搜尋成本。執行前驗證錨點，drift 時先更新 EP
- **技術選型** + **成功標準**

### 2. 核心實作要點

主要類別、關鍵方法、設計決策、整合方式

### 3. Pseudo Code

類別結構 + 方法實現 + Call Stack + 錯誤處理。檔案結構用樹狀展示（非 mermaid）。空殼 class 用詳細註解標示設計意圖。

### 4. 驗證策略

Examples 設計 + 測試計畫 + 完成檢查 + 整合測試

**測試計畫內容**：描述測試的種類和情境，不寫數量（數字每次修改都過時，對決策無價值）。應包含：
- **測試類型分佈**：單元 / 整合 / E2E / 外部 API mock
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

- [ ] UC 盤點已完成（大型/中型變更：掃描 USE-CASES.md、列出新增/更新 UC）
- [ ] Scenario Matrix 已填寫（大型/中型變更；涵蓋 happy path、錯誤操作、邊界、效能期待差異）
- [ ] 標題明確且獨立
- [ ] Context 包含所有必要背景
- [ ] UC 引用已標記（引用 UC 盤點區段的 UC ID；大型必須，中型可選）
- [ ] Pseudo Code 具體可執行
- [ ] 驗證策略完整可執行
- [ ] 整合點清晰定義
- [ ] 語義約束已顯式標記
- [ ] 基礎設施盤點已完成
- [ ] 依賴錨點已標記

---

## EP Review Cycle

**Writer/Reviewer 分離**：用獨立 Agent context 審查 EP，避免主 LLM 審查自己的計畫。
**適應式多 Agent Review**：依模型並發上限和 EP 複雜度決定 spawn 幾個 review agent。

### Step 1: 偵測模型 → 查表

從系統提示詞偵測 GLM 模型，查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md) 決定 max-agents。
印出確認：`[Review Agent] model=X, max=N`

### Step 2: Adaptive Agent 數量

**max-agents = 1**（haiku/opus）→ 跳至下方「單一 Agent Prompt（Fallback）」，行為等同原 single-agent。

**max-agents > 1**（如 sonnet = 4）→ 根據 EP 特徵啟用維度：

| 維度 Agent | 審查項目 | 啟用條件 | 優先級 |
|-----------|---------|---------|--------|
| 技術可行性 | Call Stack 可行性 + Pattern Alignment + 下游依賴發現 + 邊界條件 | **always** | P0 |
| 計畫品質 | 完整性 + 內部一致性 + 遺漏風險 | EP ≥ 3 segments | P1 |
| 合規與 UC | Rules 合規 + UC 覆蓋度 | 有 UC references | P2 |
| 語義約束 | 段落間共享假設 + 依賴錨點 drift | EP ≥ 4 segments 且有跨段落語義約束 | P3 |

啟用維度數 > max-agents → 從低優先級（P3 起）合併至前一個 agent（不丟棄任何維度）。

### Step 3: 平行 Spawn

同時 spawn 所有啟用的 review agents（subagent_type: "Explore"，read-only by design）。

每個 agent prompt 包含：
- EP 完整內容
- 該維度的檢查項目清單（如上表）
- 相關檔案路徑（必讀）
- 引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) 方法論
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）

### 單一 Agent Prompt（Fallback，max-agents = 1）

Spawn Agent（subagent_type: "Explore"），prompt 包含：
- EP 完整內容
- Dry Run 驗證：
  1. **Call Stack 可行性**：pseudo code 每步能否跑通？
  2. **Pattern Alignment（最重要）**：EP 設計假設的 usage pattern 是否與 callers 實際 pattern 一致？
  3. **下游依賴發現**：有沒有 EP 沒提到的 callers？
  4. **邊界條件**：空值、null、缺少欄位等
- 四維度審查（引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md)）：
  1. **完整性**：每段有驗收標準？檔案完整列出？依賴遺漏？邊界考量？
  2. **Rules 合規**：命名、code-edit-constraints、_ai-behavior-constraints、CLAUDE.md 更新需求
  3. **內部一致性**：段落間依賴順序、同一檔案修改矛盾、技術方案一致、語義約束標記
  4. **遺漏風險**：Demo、測試、`__init__.py`、配置檔案、受影響模組
  5. **UC 覆蓋度**：大型變更的 UC 是否被 EP 段落完整覆蓋？每個引用的 UC 是否有對應段落？
- 相關檔案路徑（必讀）

### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修正 EP。**修正必須寫入 EP 段落本身**（加入 `> **EP Review 修正**：[修正內容]`），不是只記在審查報告裡。build 可能由不同 LLM session 執行，看不到審查報告。

---

## 收尾步驟（所有功能段落完成後必做）

> **核心原則**：EP 必須包含收尾段，列出所有功能段落完成後的強制收尾動作。`/build` 階段 5 執行。未完成收尾不得宣稱 EP 實作完成。

每個 EP 的收尾段必須包含以下三項：

### 1. USE-CASES.md 更新

- 將 EP 引用的 UC 狀態從 📋 更新為 ✅（或 🔧/🟡）
- 已完成 UC 搬到正確章節（不留在「待實作」區）
- 清理暫時性資訊（前置條件、測試計畫），保留已知限制和結果摘要
- **從 EP Scenario Matrix 提煉「消費場景」寫入對應 UC**（大型/中型變更）：將矩陣中所有引用該 UC 的場景，提煉成自包含一句話描述（不引用 EP/SM 編號，因為 EP 可能歸檔或刪除），填入 UC 的「消費場景」欄位

### 2. CLAUDE.md 更新

- 檢查受影響模組目錄的 CLAUDE.md，確認架構描述反映變更
- 新增/修改：模組職責、導航指引、可複用基礎設施
- 遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準（Signal/Noise ratio、導航優先）

### 3. /audit-test

- 執行 `/audit-test` 對新增/修改的測試進行品質稽核
- 確認無反模式、覆蓋對稱性合理、mock 健康度良好
- 稽核結果附於 `/build` 完成報告

**小型變更**（bug fix）：僅執行 /audit-test，跳過 UC 和 CLAUDE.md 更新。

---

## 輸出

- **位置**：`ai-analysis/execution-plans/`
- **檔名**：從任務描述自動衍生（kebab-case）
- **結構**：實作總覽 → **UC 盤點** → Scenario Matrix → 段落劃分原則 → 各段落（Context → 要點 → Pseudo Code → 驗證）→ 整合策略 → 收尾步驟

---

## 流程位置

```
/spec → /execution-plan（含 EP Review）→ /build（含 Agent Review）→ [/code-review] → /commit
```

前置：`/spec`
後續：`/build`（如需額外審查可跑獨立 `/ep-review` 或 `/judge-review`）
