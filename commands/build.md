---
description: "基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號]"
when_to_use: "Implement an Execution Plan segment-by-segment using TDD. Use after /execution-plan (with built-in EP Review). Supports parallel agents with --max-agents."
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [段落編號] [--max-agents N | -a N]"
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
| EP Review 修正 | 掃描 EP review 區段(`## EP Review Findings` 表格,見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)),納入實作 | 列入快檢報告 |

**平行可行性分析**：
1. 建構段落依賴圖，識別可平行段落
2. 套用 max-agents 限制（預設 3，可透過 `--max-agents N` 或 `-a N` 覆蓋）
3. **有語義約束的段落強制序列**

**整合器段落識別**（驅動階段 2 硬閘門、階段 3 真實邊界的觸發）：掃描 EP 段落，標記同時滿足以下者為整合器型（見 [quality-constraints](../rules/quality-constraints.md)「整合器型變更判定」）：

- 主要價值是把 ≥2 個真實外部組件接起來（DB、catalog、SDK、跨進程、跨框架）
- 邊界正確性無法從任一單方文件推導
- 錯了不是調參數而是整天行為全錯

**機械 IO 觸發（三條件的 OR 補充，降 LLM 單點）**：段落 diff 觸及真實 IO 模式（parquet/檔案讀寫、DB 連線、第三方 SDK 呼叫、跨進程/跨框架邊界）→ 即使三條件判「非整合器型」，仍標「**待 L2 評估**」，交階段 3 確認是否真需要 L2。候選撈取 → LLM 裁決兩段式（非硬卡）。排除：純 config/fixture 讀取（非整合器，避免 false positive 稀釋信號）。

整合器型段落標記後，在階段 2/3 對應加嚴（路徑覆蓋硬閘門 + 真實邊界整合測試）。

### 階段 1：準備

1. 讀取 Execution Plan，識別段落結構、依賴關係
2. **Kanban 狀態更新**：掃描 EP 中引用的能力描述，將對應的 `.kanban/Backlog/` cards 搬至 `.kanban/In-Progress/`（反映「正在做」的暫時狀態；搬至 Done/ 在 `/commit` 確認後才執行）
3. **深度查證現有程式碼**（不同於階段 0 的 drift 快掃，此處是理解程式碼上下文與設計意圖）。LSP `goToDefinition` 驗證 dependency anchors 的定義端，`findReferences` 驗證消費端，`hover` 確認關鍵參數型別
4. **Examples 盤點**：掃描 `demo_*.py`、`examples/**/*.py` 等，建立 `{module} → [example paths]` 映射表
5. 檢查清單：Kanban InProgress ✓ | Examples 映射表 ✓ | 測試檔案 ✓ | CLAUDE.md 同步 ✓ | 依賴完整 ✓

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

> **EP 是收斂方向，不是合約**。EP 是規劃層對需求理解的最佳猜測，有預見極限（見 [acceptance-evidence](../rules/acceptance-evidence.md)「認知誤差與 EP 的預見極限」）— 實作落差、設計本身錯，都只能在實作呈現時發現。前線實作 LLM 有裁量權根據實作發現調整；死守 EP 會實作「忠實但錯誤」的東西，反而妨礙人類在呈現時發現認知誤差。

- **EP 為收斂方向，實作層有裁量權**：照 EP 為主軸，但實作時發現 EP 預見極限外的真相（邊界、副作用、組件互動、需求落差）可調整 — 這是「發現真相的責任」而非「偷懶不照 EP」
- 記錄偏差：與 Pseudo Code 有出入時記錄原因（偏差是發現認知誤差的線索，不是違規）
- 記錄疑慮不中斷：先選最合理方案繼續，最後統一讓用戶確認
- 錯誤自癒：連續 3 次失敗 → 標記 ⚠️ 繼續下一段
- **依賴錨點 drift check**：實作每段前驗證錨點，drift 時先更新 EP

#### 驗證

每段完成後：**整合路徑覆蓋檢查** → `ruff check --fix && ruff format` → LSP diagnostics（即時型別檢查）→ `mypy .`（完整驗證）→ `pytest <test> -v`（背景跑）→ Examples 驗證

**整合路徑覆蓋檢查**（機械式硬閘門，見 [acceptance-evidence](../rules/acceptance-evidence.md) L3 + [quality-constraints](../rules/quality-constraints.md) 符號 vs 路徑覆蓋）：本段是否新增/修改 callable 簽名（新參數、新 keyword）或新增注入點（constructor 接受新依賴）？

- 否 → 跳過
- 是 → 對每個新參數/注入點 `rg "<param>=" tests/`
  - **0 hits → 該段不得 pass**，必須先補消費端整合測試（驅動真實消費端流程 + 新參數組合路徑，非僅符號 import）
  - 有 hits → 確認 hits 是「驅動消費端流程」的測試，而非僅符號 import

### 階段 3：整合驗證

> **scope 邊界（階段 2 vs 階段 3）**：階段 2 抓「新參數/注入點的接線路徑」（機械 rg 初篩）；階段 3 抓「既有接線的行為正確性」（需真實邊界跑）。**鐵律：階段 2 rg 有 hits ≠ 階段 3 L2 已滿足** — 符號出現在 tests（如被測單元自己的單元測試）≠ 消費端驅動該符號的路徑被覆蓋。例（真實歷史案例）：`rg "<符號>=" tests/` 有 hits 但全在被測單元自己的測試，消費端 integration 路徑不存在 — 符號有測 ≠ 消費路徑有測，bug 漏到補 integration test 才抓到。

全量 Lint + mypy + pytest（背景跑）+ Examples 全量驗證。全量跑只是 baseline。

**整合器型段落必須有真實邊界整合測試**（見 [quality-constraints](../rules/quality-constraints.md)「整合器型變更判定」+「兩層整合測試」）：主要價值是接 ≥2 個真實外部組件的段落，完成定義必須含 L1 接線 guard（`unit_tests/`）+ L2 真實邊界（`integration_tests/`），不能只靠 mock — mock 循環論證會讓 mock 假設即 bug 來源。

### 階段 4：Agent Review Cycle

**Writer/Reviewer 分離**：用獨立 Agent context 做品質閘門，避免主 LLM 審查自己的 code。
**2-perspective Review**（① Intent-anchored + ② Fresh）：多樣性 > 數量 — 兩異質 perspective 比多個同錨定 agent 覆蓋更廣。完整設計見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)。

#### Step 1: 確認 max-agents

`--max-agents N` 或 `-a N` 參數控制平行 Agent 數量，預設 3。用戶可手動調整。
印出確認：`[Review Agent] max=N`

#### Step 2: 選擇審查模式

偵測 effort level。印出確認：`[Review Mode] effort=ultracode, workflow=true, max=N` 或 `[Review Mode] effort=standard, workflow=false, max=N`

**A. Workflow 模式**（effort = ultracode/xhigh 且 max-agents > 1）：

用 Workflow tool 協調 2 perspective（perspective 定義 + prompt 見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)）；腳本骨架、DimensionVerdict schema、adversarial verify 見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)。

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 2 perspective agents | ≤ max-agents |
| Verify | Critical findings → 3 verifier + ≥2/3 quorum | 3 × critical findings |

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 進入「/judge-review」步驟（現有流程不變）。

**B. Agent Tool 模式**（Fallback，非 ultracode）：2-perspective review（① Intent-anchored + ② Fresh），完整流程見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)。

#### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

#### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修改 code。修改完跑 `ruff check --fix && ruff format`。

### 階段 5：收尾步驟（EP 強制）

**執行 EP 收尾段定義的三項動作。未完成不得宣稱實作完成。**

**讀取 EP 收尾段**：EP 結構末段的「收尾步驟」定義了本 EP 的具體收尾範圍。讀取後按以下三項執行：

#### 5a. 消費場景提煉（大型/中型變更）

> **注意**：Capabilities 表格更新和 Kanban 搬至 **Done/** 在 `/commit` 階段 3 確認後才執行。原因：build 完成不代表會 commit（可能 code-review 後決定重做），提前更新永久狀態會造成 Capabilities 與實際程式碼不一致。（Kanban 搬至 InProgress/ 已在階段 1 完成，屬暫時狀態。）

1. **從 EP Scenario Matrix 提煉「消費場景」**：將矩陣中所有引用該 UC 的場景，提煉成自包含一句話描述（不引用 EP/SM 編號），暫存於 build context，供後續 `/commit` 階段 3 寫入 Capabilities 表格或 Kanban card

#### 5b. SYSTEM-MAP.md 更新（大型/中型變更）

1. **讀取 SYSTEM-MAP.md**（如果存在於專案根目錄）
2. **定位受影響的功能區塊**：根據本次更新的能力描述，找到 SYSTEM-MAP.md 中引用這些能力的功能
3. **更新功能生命週期狀態**：
   - 所有引用 UC 都 ✅ 且測試通過 → 功能狀態升級（✅→✅🔍 或 📋→✅ Built）
   - 有已知問題或未驗證 → 標記 ⚠️ 並附說明
   - 移除已修復的 ⚠️ 標記
4. **更新全域狀態統計**（如果文件尾端有統計表）

#### 5c. CLAUDE.md 更新（大型/中型變更）

1. **識別受影響模組**：從 git diff 中找出變更檔案所在目錄及上層目錄的 CLAUDE.md
2. **檢查更新需求**：變更是否影響 CLAUDE.md 中描述的架構、模組職責、導航指引、可複用基礎設施
3. **更新**：新增/修改受影響段落，遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準（Signal/Noise ratio、導航優先、禁止元資訊）

#### 5d. /audit-test（所有變更）

執行 `/audit-test` 對新增/修改的測試進行品質稽核（階段 2 已逐段檢查整合路徑覆蓋，此處複驗整體 + 其他角度如反模式、mock 健康度、測試必要性）。稽核結果附於完成報告。

**小型變更**（bug fix）：僅執行 5d（/audit-test），跳過 5a、5b、5c。

### 階段 6：完成報告

輸出：實作結果（新增/修改檔案）+ 架構決策記錄 + 待確認清單 + 未解決問題 + Agent 統計（平行模式）+ Agent Review 結果摘要 + 能力狀態變更摘要 + SYSTEM-MAP 功能狀態變更 + /audit-test 稽核結果

---

## 執行約束

### 強制

1. 必須先 EP 快檢
2. 必須完整讀取計畫書
3. 每段必須 TDD（RED → GREEN → REFACTOR）
4. 每段必須獨立驗證（ruff + mypy + pytest）
5. 禁止 `from __future__ import annotations`
6. 必須執行收尾步驟（階段 5）：大型/中型 → Capabilities + Kanban 更新 + SYSTEM-MAP 更新 + CLAUDE.md 更新 + /audit-test；小型 → /audit-test

### 禁止

- ❌ 跳過測試直接實作
- ❌ 使用 `sed` 修改程式碼
- ❌ 段落範圍外修改
- ❌ 中間狀態提交破損程式碼
- ❌ 跳過收尾步驟宣稱完成

---

## 與其他命令的協作

```
/spec → /execution-plan（含 EP Review）→ [/ep-validate] → post-EP: /deliverable-review --ep（layer 3 方向）→ /arch-review --ep（layer 3 結構）→ /build（含 Agent Review + /audit-test, LLM 鏈）→ post-build（看狀況呼叫，不硬定先後）: /arch-review（layer 3 結構）/ /deliverable-review（layer 3 demo 交付）→ [/code-review] → /commit
```

**搭配 `/goal`**：啟動後設定 `all segments implemented, uv run pytest exits 0, ruff clean, mypy clean, all demos run` 搭配 auto mode 效果最佳。

> **Agent Review Cycle（LLM 鏈, layer 1）已完成。** 機器自驗天花板 = AI 自洽,commit 前建議跑 `/deliverable-review`（layer 3 demo 交付）跨越認知誤差、`/arch-review`（layer 3 結構 viewport）跨越重造盲點;如需 LLM 第二意見可跑獨立 `/code-review`（layer 1/2）。

---

## 語音通知

遵循 `voice-notification` skill：
- **開始**：`say -v Meijia -r 180 "開始實作 EP，主人請稍候"`
- **完成**：`say -v Meijia -r 180 "主人！實作完成，所有段落已驗證通過～"`
