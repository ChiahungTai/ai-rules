---
description: "基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號]"
when_to_use: "Implement an Execution Plan segment-by-segment using TDD. Use after /execution-plan (with built-in EP Review). Supports parallel agents with --max-agents."
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [段落編號] [--max-agents N]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
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

---

## 執行流程

### 階段 0：EP 快檢

快速確認 EP 品質，**僅嚴重矛盾才停下**，其餘自行判斷並記錄。

**強制輸出**：快檢完成後必須印出 `## EP 快檢：✅ 可實作` 或 `## EP 快檢：⚠️ N 項自行補充`。不得靜默跳過。

**前置流程確認**（僅記錄，不因此停下）：`/spec → /execution-plan（含 EP Review）→ /build`

**EP 品質快掃**：

| 檢查項目 | 通過標準 | 發現問題時 |
|----------|----------|------------|
| 段落結構 | 每段有 Context、Pseudo Code、驗證策略 | 標記缺漏，自行補上 |
| Pseudo Code 可執行性 | 具體到可翻譯為程式碼 | 標記模糊處，自行推斷 |
| 驗證策略具體性 | 有明確測試案例 | 自行補充合理測試 |
| 依賴錨點有效性 | file:line 與實際程式碼一致 | drift 時先更新 EP |

**平行可行性分析**：
1. 建構段落依賴圖，識別可平行段落
2. 套用 max-agents 限制：從系統提示偵測 GLM 模型，決定 Agent 模型和並發上限
3. **有語義約束的段落強制序列**

### 階段 1：準備

1. 讀取 Execution Plan，識別段落結構、依賴關係
2. 查證現有程式碼，驗證依賴錨點
3. **Examples 盤點**：掃描 `demo_*.py`、`examples/**/*.py` 等，建立 `{module} → [example paths]` 映射表
4. 檢查清單：Examples 映射表 ✓ | 測試檔案 ✓ | CLAUDE.md 同步 ✓ | 依賴完整 ✓

### 階段 2：逐段實作

**EP 段落元素 → TDD 步驟**：

| EP 元素 | TDD 步驟 | 說明 |
|---------|---------|------|
| Context | 開始前讀取 | 理解背景 |
| 驗證策略 | RED | 照設計寫測試 |
| Pseudo Code | GREEN | 照設計實作 |
| 核心要點 | REFACTOR | 檢查覆蓋 |

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

#### 4a. Spawn Code Review Agent

Spawn Agent（subagent_type: "Explore"，read-only by design），prompt 包含：
- `git diff` 範圍（所有 build 產出的變更）
- EP 完成度稽核：讀 EP 段落表，對比 git diff，列出 Done / Skipped / Partial
- 標準 code-review 方法論（引用 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md)）
- 相關檔案路徑（必讀）

#### 4b. 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入 Agent 的 review findings。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

#### 4c. 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修改 code。修改完跑 `ruff check --fix && ruff format`。

### 階段 5：UC 狀態更新

**UC-Driven Development 的品質閘門。大型/中型變更必須執行。**

1. **讀取 EP 中引用的 UC ID**（來自段落 Context 的 UC 引用欄位）
2. **更新 USE-CASES.md**：
   - 已完成的 UC：📋→✅，附專案相對路徑
   - 部分完成的 UC：保持 📋，更新描述
3. **寫入或更新 GAPS.md**（未完成的段落）：
   - 新增 GAP 條目，引用對應 UC ID
   - 更新既有 GAP 狀態（如回填進度）
4. **小型變更**（bug fix）：跳過此階段

### 階段 6：完成報告

輸出：實作結果（新增/修改檔案）+ 架構決策記錄 + 待確認清單 + 未解決問題 + Agent 統計（平行模式）+ Agent Review 結果摘要 + UC 狀態變更摘要

---

## 執行約束

### 強制

1. 必須先 EP 快檢
2. 必須完整讀取計畫書
3. 每段必須 TDD（RED → GREEN → REFACTOR）
4. 每段必須獨立驗證（ruff + mypy + pytest）
5. 禁止 `from __future__ import annotations`

### 禁止

- ❌ 跳過測試直接實作
- ❌ 使用 `sed` 修改程式碼
- ❌ 段落範圍外修改
- ❌ 中間狀態提交破損程式碼

---

## 與其他命令的協作

```
/spec → /execution-plan（含 EP Review）→ /build（含 Agent Review）→ [/code-review] → /commit
```

**搭配 `/goal`**：啟動後設定 `all segments implemented, uv run pytest exits 0, ruff clean, mypy clean, all demos run` 搭配 auto mode 效果最佳。

> **Agent Review Cycle 已完成。** 可直接 `/commit`；如需額外審查可跑獨立 `/code-review`。
