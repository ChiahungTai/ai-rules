---
description: "基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號]"
when_to_use: "Implement an Execution Plan segment-by-segment using TDD. Use after /execution-plan (with built-in EP Review). Supports parallel agents with --max-agents."
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [段落編號] [--max-agents N]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "Workflow"]
---

# /build — 基於 Execution Plan 逐段實作

基於 Execution Plan 進行逐段實作。每個段落都是 Self-Contained Segment，獨立實作、測試、驗證。

**自主實作模式**：EP 已經過 EP Review Cycle 充分審查（內建於 `/execution-plan`），實作階段自主執行。自主決策、錯誤自癒遵循 [autonomous-execution](../skills/autonomous-execution/SKILL.md)。

委託 Skills（實作時提供方法論）：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [test-driven-development](../skills/test-driven-development/SKILL.md) — TDD 循環
- [incremental-implementation](../skills/incremental-implementation/SKILL.md) — 範圍紀律
- [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md) — 系統化除錯
- [autonomous-execution](../skills/autonomous-execution/SKILL.md) — 自主決策框架
- [python-type-gap](../skills/python-type-gap/SKILL.md) — 第三方套件 type gap（mypy 失敗時）
- [agent-workflow](../skills/agent-workflow/SKILL.md) — 並發控制、模型偵測、Agent spawn 規範

Workflow 審查協調：[workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)（Ultracode 下 Phase 4 使用）

---

## 執行流程

### 階段 0：EP 快檢

快速確認 EP 品質，**僅嚴重矛盾才停下**，其餘自行判斷並記錄。

**強制輸出**：快檢完成後必須印出 `## EP 快檢：✅ 可實作` 或 `## EP 快檢：⚠️ N 項自行補充`。不得靜默跳過。

**前置流程確認**（僅記錄，不因此停下）：`/spec → /execution-plan（含 EP Review）→ [/ep-validate] → /build`

**EP 品質快掃**：

| 檢查項目 | 通過標準 | 發現問題時 |
|----------|----------|------------|
| 段落結構 | 每段有 Context、Pseudo Code、驗證策略 | 標記缺漏，自行補上 |
| Pseudo Code 可執行性 | 具體到可翻譯為程式碼 | 標記模糊處，自行推斷 |
| 驗證策略具體性 | 有明確測試案例 | 自行補充合理測試 |
| 依賴錨點有效性 | file:line 與實際程式碼一致 | drift 時先更新 EP |
| EP Review 修正 | 掃描 `> **EP Review 修正**` 標記，納入實作 | 列入快檢報告 |

**平行可行性分析**：
1. 建構段落依賴圖，識別可平行段落
2. 套用 max-agents 限制：從系統提示偵測 GLM 模型，決定 Agent 模型和並發上限
3. **有語義約束的段落強制序列**

### 階段 1：準備

1. 讀取 Execution Plan，識別段落結構、依賴關係
2. **深度查證現有程式碼**（不同於階段 0 的 drift 快掃，此處是理解程式碼上下文與設計意圖）
3. **Examples 盤點**：掃描 `demo_*.py`、`examples/**/*.py` 等，建立 `{module} → [example paths]` 映射表
4. 檢查清單：Examples 映射表 ✓ | 測試檔案 ✓ | CLAUDE.md 同步 ✓ | 依賴完整 ✓

### 階段 2：逐段實作

**EP 段落元素 → TDD 步驟**：

| EP 元素 | TDD 步驟 | 說明 |
|---------|---------|------|
| Context | 開始前讀取 | 理解背景 |
| 驗證策略 | RED | 讀 EP 測試類型 → 分類情境 → 寫對應測試（詳 TDD skill EP Integration） |
| Pseudo Code | GREEN | 照設計實作 |
| 核心要點 | REFACTOR | 對 EP 完成檢查逐項驗證 |

#### 平行模式

**Pre-flight**：有 uncommitted changes 是 Agent dependency → 先 commit；branch 不正確 → 先 checkout

**max-agents > 1 且有可平行段落**時：
1. 依賴圖分層為 waves
2. 同 wave 平行 Agent（上限 max-agents）
3. Wave 合併：讀取 Agent 產出 → 應用到主 worktree → `ruff check --fix && ruff format`

**Agent Context 邊界**：Agent 看不到主對話歷史、其他 Agent 結果、EP 準備結論。**主 LLM 的 prompt 是 Agent 理解任務的唯一來源。**

**Agent Prompt 必須包含**：
- EP 段落完整內容（Context + Pseudo Code + 驗證策略 + 核心要點）
- 準備階段結論（現有程式碼狀態、架構決策）
- 語義約束
- Examples 映射（Agent 回報前必須執行至少一個 Example 驗證）
- 相關檔案路徑（必讀 / 可修改 / 禁止修改）
- Skills invoke 指示（rules-reminder, test-driven-development, incremental-implementation, autonomous-execution）

#### EP 專屬約束

- **照著 EP 寫，不要自己發明**
- 記錄偏差：與 Pseudo Code 有出入時記錄原因
- 記錄疑慮不中斷：先選最合理方案繼續，最後統一讓用戶確認
- 錯誤自癒：連續 3 次失敗 → 標記 ⚠️ 繼續下一段
- **依賴錨點 drift check**：實作每段前驗證錨點，drift 時先更新 EP

#### 驗證

每段完成後：`ruff check --fix && ruff format` → `mypy .` → `pytest <test> -v`（背景跑）→ Examples 驗證

### 階段 3：整合驗證

全量 Lint + mypy + pytest（背景跑）+ Examples 全量驗證

### 階段 4：Agent Review Cycle

**Writer/Reviewer 分離**：用獨立 Agent context 做品質閘門，避免主 LLM 審查自己的 code。
**適應式多 Agent Review**：依模型並發上限和變更複雜度決定 spawn 幾個 review agent。

#### Step 1: 偵測模型 → 查表

從系統提示詞偵測 GLM 模型，查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md) 決定 max-agents。
印出確認：`[Review Agent] model=X, max=N`

#### Step 2: 選擇審查模式

偵測 effort level。印出確認：`[Review Mode] effort=ultracode, workflow=true, max=N` 或 `[Review Mode] effort=standard, workflow=false, max=N`

**A. Workflow 模式**（effort = ultracode/xhigh 且 max-agents > 1）：

使用 Workflow tool，參照 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md) 腳本骨架。

**啟用維度**（沿用下表 Agent Tool 模式的維度定義和啟用條件）：

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 維度 agents | ≤ max-agents |
| Verify | Critical findings → 3 verifier + ≥2/3 quorum | 3 × critical findings |

每個 Review agent prompt 包含（同 Agent Tool 模式）：
- `git diff` 範圍（所有 build 產出的變更）
- 該維度的檢查項目清單
- 相關檔案路徑（必讀）
- 引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) 方法論
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）
- schema: DimensionVerdict（定義在 workflow-review-pattern.md）

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 進入「/judge-review」步驟（現有流程不變）。

**B. Agent Tool 模式**（Fallback，max-agents = 1 或非 ultracode）：

##### Adaptive Agent 數量

**max-agents = 1**（haiku/opus）→ 跳至下方「單一 Agent Prompt（Fallback）」。

**max-agents > 1**（如 sonnet = 4）→ 根據變更特徵啟用維度：

| 維度 Agent | 審查項目 | 啟用條件 | 優先級 |
|-----------|---------|---------|--------|
| EP 合規 | EP 完成度稽核：Done / Skipped / Partial | **always**（有 EP 時） | P0 |
| 正確性 | 邏輯 bugs、邊界案例、error handling | 變更 ≥ 3 files | P1 |
| 架構與安全 | 設計模式、耦合、安全性 | 變更 ≥ 5 files 或含 API changes | P2 |

啟用維度數 > max-agents → 從低優先級（P2 起）合併至前一個 agent（不丟棄任何維度）。

##### 平行 Spawn

同時 spawn 所有啟用的 review agents（subagent_type: "Explore"，read-only by design）。

每個 agent prompt 包含：
- `git diff` 範圍（所有 build 產出的變更）
- 該維度的檢查項目清單（如上表）
- 相關檔案路徑（必讀）
- 引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) 方法論
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）

#### 單一 Agent Prompt（Fallback，max-agents = 1）

Spawn Agent（subagent_type: "Explore"），prompt 包含：
- `git diff` 範圍（所有 build 產出的變更）
- EP 完成度稽核：讀 EP 段落表，對比 git diff，列出 Done / Skipped / Partial
- 標準 code-review 方法論（引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md)）
- 相關檔案路徑（必讀）

#### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

#### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修改 code。修改完跑 `ruff check --fix && ruff format`。

### 階段 5：收尾步驟（EP 強制）

**執行 EP 收尾段定義的三項動作。未完成不得宣稱實作完成。**

**讀取 EP 收尾段**：EP 結構末段的「收尾步驟」定義了本 EP 的具體收尾範圍。讀取後按以下三項執行：

#### 5a. USE-CASES.md 更新（大型/中型變更）

1. **讀取 EP 中引用的 UC ID**（來自段落 Context 的 UC 引用欄位）
2. **更新對應 library 模組的 USE-CASES.md**：
   - 已完成的 UC：📋→✅，附專案相對路徑；若原在「待實作」章節，搬到對應的正確章節
   - 部分完成的 UC：📋→🔧，內嵌剩餘細節（前置條件、設計要點、測試計畫 — 測試類型分佈 + 情境覆蓋 + 已知風險，不寫數量）
   - 進行中的 UC：🔧→🟡（如 backfill 正在跑）
3. **從 EP Scenario Matrix 提煉「消費場景」寫入 UC**：將矩陣中所有引用該 UC 的場景，提煉成自包含一句話描述（不引用 EP/SM 編號，因為 EP 可能歸檔或刪除），填入 UC 的「消費場景」欄位
4. **更新 UC-BACKLOG.md 狀態**（如果 EP 有「Backlog 關聯」且 UC-BACKLOG.md 存在）：
   - 讀取 EP「Backlog 關聯」列出的 BACKLOG item IDs
   - 對每個 BACKLOG item，檢查其引用的所有 UC 狀態（從對應的 USE-CASES.md，不限本次更新的）
   - 更新 UC-BACKLOG.md 中對應 item 的狀態：所有引用 UC ✅ → item 標為完成；部分 ✅ → 標記進度

#### 5b. CLAUDE.md 更新（大型/中型變更）

1. **識別受影響模組**：從 git diff 中找出變更檔案所在目錄及上層目錄的 CLAUDE.md
2. **檢查更新需求**：變更是否影響 CLAUDE.md 中描述的架構、模組職責、導航指引、可複用基礎設施
3. **更新**：新增/修改受影響段落，遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準（Signal/Noise ratio、導航優先、禁止元資訊）

#### 5c. /audit-test（所有變更）

執行 `/audit-test` 對新增/修改的測試進行品質稽核。稽核結果附於完成報告。

**小型變更**（bug fix）：僅執行 5c（/audit-test），跳過 5a、5b。

### 階段 6：完成報告

輸出：實作結果（新增/修改檔案）+ 架構決策記錄 + 待確認清單 + 未解決問題 + Agent 統計（平行模式）+ Agent Review 結果摘要 + UC 狀態變更摘要 + /audit-test 稽核結果

---

## 執行約束

### 強制

1. 必須先 EP 快檢
2. 必須完整讀取計畫書
3. 每段必須 TDD（RED → GREEN → REFACTOR）
4. 每段必須獨立驗證（ruff + mypy + pytest）
5. 禁止 `from __future__ import annotations`
6. 必須執行收尾步驟（階段 5）：大型/中型 → UC 更新 + CLAUDE.md 更新 + /audit-test；小型 → /audit-test

### 禁止

- ❌ 跳過測試直接實作
- ❌ 使用 `sed` 修改程式碼
- ❌ 段落範圍外修改
- ❌ 中間狀態提交破損程式碼
- ❌ 跳過收尾步驟宣稱完成

---

## 與其他命令的協作

```
/spec → /execution-plan（含 EP Review）→ [/ep-validate] → /build（含 Agent Review）→ [/code-review] → /commit
```

**搭配 `/goal`**：啟動後設定 `all segments implemented, uv run pytest exits 0, ruff clean, mypy clean, all demos run` 搭配 auto mode 效果最佳。

> **Agent Review Cycle 已完成。** 可直接 `/commit`；如需額外審查可跑獨立 `/code-review`。
