---
description: "深層思考代碼審查。/code-review [branch] [base]"
when_to_use: "Review uncommitted changes or a feature branch using multi-axis methodology and deep-thinking (first-principles + second-level consequence tracing)."
usage: "/code-review [target-branch] [base-branch]"
argument-hint: "無參數審查 uncommitted / branch 名稱審查該 branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /code-review — 深層思考代碼審查

基於深層思考審查尚未 commit 的 code。不只是看改了什麼，更要讀相關程式碼確認**為什麼這樣改**。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [review-engine](../skills/review-engine/SKILL.md) — 通用審查邏輯（嚴重度/信心水準/審查者自證/LSP 查證/審查模式判定規則/多層驗證）
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — code 六軸審查方法論（what to check）

按需讀取：
- [security-and-hardening](../skills/security-and-hardening/SKILL.md) — 安全審查細節
- [performance-optimization](../skills/performance-optimization/SKILL.md) — 效能審查細節

Workflow 執行協調：[workflow-review-pattern.md](./instruction/_common/workflow-review-pattern.md)（模式判定見 review-engine；Ultracode 下平行六軸審查）

---

## 審查範圍

| 用法 | 實際執行 | 場景 |
|------|---------|------|
| `/code-review` | `git diff` + `git diff --cached` + `git ls-files --others --exclude-standard` | 審查 uncommitted（預設，含 untracked files） |
| `/code-review feat/xxx` | `git diff HEAD...feat/xxx` | 審查 feature branch |
| `/code-review feat/xxx main` | `git diff main...feat/xxx` | 審查 branch（指定 base） |

**Untracked files 處理**：新檔案沒有「變更前/後」可比對，審查時以完整檔案內容為對象（等同 diff against `/dev/null`），重點檢查架構一致性、命名慣例、與既有程式碼的整合點。

---

## Lint 預檢

對 modified files 執行 `ruff check --select F401,PLC0415`，結果併入審查報告。

| Rule | 抓什麼 | 唯一合理例外 |
|------|--------|-------------|
| F401 | unused import（LLM 重構後殘留） | `__all__` 用途、optional dependency try/except |
| PLC0415 | import 不在檔案頂部（LLM 偷懶） | circular import avoidance |

---

## 審查模式選擇

review 執行預設（force 獨立 / max-agents / model inherit）見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」—— **code-review 是唯一允許 Main LLM 模式**的 review 命令（低 effort 主 LLM 直接審；其餘 review 命令刻意覆蓋為恆獨立）。模式判定規則（effort/max-agents → A/B/C）見 [review-engine](../skills/review-engine/SKILL.md)；max-agents 查 [model-routing 並發上限](../rules/model-routing.md)（agent-workflow defer 到此、不自帶數字）。下方 A/B/C 為本命令的六軸啟用配置：

**A. Workflow 模式**（判定條件見 [review-engine](../skills/review-engine/SKILL.md)）：

使用 Workflow tool，參照 [workflow-review-pattern.md](./instruction/_common/workflow-review-pattern.md) 腳本骨架。

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 軸 agents（最多 6） | ≤ max-agents |
| Verify | Critical findings → 3 verifier + ≥2/3 quorum | 3 × critical |

**啟用軸**：

| 軸 Agent | 審查項目 | 啟用條件 | 優先級 |
|----------|---------|---------|--------|
| Correctness | 邏輯 bugs、邊界案例、測試充分性 | **always** | P0 |
| Readability & Simplicity | 命名、控制流、避免過早抽象 | **always** | P0 |
| Architecture（axis 3，調用 arch-thinking skill） | 設計模式、模組邊界、重用、dep weight | 變更 ≥ 3 files | P1 |
| Security | 輸入驗證、權限檢查 | diff 含 HTTP/auth/credential | P1 |
| Performance | N+1、無界操作 | 變更 ≥ 5 files | P2 |
| Capability Coverage | Capabilities 行為覆蓋 | 大型/中型變更 | P2 |

啟用軸數 > max-agents → 從低優先級（P2 起）合併至前一個 agent（不丟棄任何軸）。

**docs mode（純文檔變更）**：Security / Performance 軸 N/A（文檔不涉及 HTTP/auth/credential、無 N+1/無界操作），跳過此二軸避免噪音；Correctness / Readability & Simplicity / Architecture / Capability Coverage 仍適用（文檔正確性、可讀、結構、行為覆蓋）。docs mode 觸發判準見 [execution-plan.md](./execution-plan.md) docs mode 段。

每個 Review agent prompt 包含：
- `git diff` 範圍
- 該軸的檢查項目清單（如上表）
- 相關檔案路徑（必讀）
- 方法論引用（code-review-and-quality；Architecture 軸引用 arch-thinking（視角+機械）；Security 軸額外引用 security-and-hardening）
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）
- schema: DimensionVerdict（定義在 workflow-review-pattern.md）

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 合成 results → 分三級（Critical/Important/Suggestion）→ POC/Demo 影響檢查 → commit message 產生。

印出確認：`[Code Review Mode] effort=ultracode, workflow=true, max=N`

**B. Agent Tool 模式**（Fallback；判定條件見 [review-engine](../skills/review-engine/SKILL.md)）：

單一 Explore agent 做所有啟用軸（Writer/Reviewer 分離效果）。印出確認：`[Code Review Mode] effort=ultracode, workflow=false, agent=true`

**C. Main LLM 模式**（判定條件見 [review-engine](../skills/review-engine/SKILL.md)）：

Main LLM 直接做所有軸（現有行為）。印出確認：`[Code Review Mode] effort=standard, workflow=false`

---

## 六軸審查 + 深層思考

> **六軸定義**（Correctness / Readability & Simplicity / Architecture / Security / Performance / Capability Coverage）見 [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — **單一真相源**（完整定義沉 skill）。本命令：上方啟用軸表的「審查項目」是 agent-prompt 啟用條件 + 摘要（agent 看的），非定義重複；另定義執行方式（top-down、axis 3 接線、Capability Coverage 審查細節、深層思考）。
>
> **Correctness 三層**（消歧）：**lens**（base perspective，所有 review 共用視角）見 [review-engine](../skills/review-engine/SKILL.md) 點 4 ③；**checklist**（what to check 細節）見 code-review-and-quality ### 1；本命令上方啟用軸表是 **agent-prompt 摘要**（非定義）。

**top-down 審查順序**：axis 3（Architecture，結構）先於細部正確性（Correctness 等）— 結構錯了正確性審白費。

### axis 3：Architecture — 調用 [arch-thinking](../skills/arch-thinking/SKILL.md) skill
- **機器產 finding（A 軸）**：city map / dep weight / 重用枚舉 / LSP 查證，調用 skill 取結構資料 → 產 finding（變更融入既有結構？在重造？）
  - **CRG（若裝了）**：axis 3 的 impact radius / 跨檔 callers / affected flows 用 CRG `get_impact_radius` / `query_graph callers_of` / `get_affected_flows` 機械產（取代手動 LSP 逐層追蹤）；change scoping 用 `detect_changes` + `get_minimal_context`（只讀 impacted nodes）。LSP-vs-CRG 分工 + assume+warn-if-absent 見 [crg-query](../skills/crg-query/SKILL.md)。
- **受眾明文**：axis 3 與 `/illustrate` 用同一 skill，但 axis 3 產**機器 finding**（A 軸）、illustrate **渲染給人判讀**（B 軸）

### Capability Coverage — 滿足 Capabilities 描述嗎？
大型/中型變更時審查：
- 實作是否涵蓋模組 instruction 檔（AGENTS.md 為主，legacy CLAUDE.md）Capabilities 表格描述的所有行為？
- 是否有 Capabilities 引用的行為在 diff 中沒有對應實作？
- EP 段落引用的能力描述是否與 Capabilities 表格或 .kanban/ 卡片一致？
- Capabilities 入口路徑是否指向 library 模組（非 scripts/ —— scripts/ 是 demo 入口非能力入口）？
- 實作是否涵蓋「消費場景」描述的所有情境（happy path、錯誤操作、邊界、效能期待差異）？
小型變更（bug fix）跳過此軸。

### 深層思考（第一性原理 + 第二層思考）
- **讀相關程式碼**：不只看 diff，讀取被修改檔案引用的其他模組
- **確認實作合理性**：為什麼這樣寫？有沒有更簡單的方式？
- **驗證假設**：修改是否基於對現有程式碼的正確理解？
- **追蹤後果**：這個修改的下游影響是什麼？依賴模組是否受影響？
- **審查者自證**：提出問題前必須查證宣稱（LSP 查證方法 + 自我否證義務：找不到 ≠ 不存在）— 完整方法見 [review-engine](../skills/review-engine/SKILL.md)

深層思考框架見 `~/Github/ai-rules/rules/deep-thinking.md`

---

## POC/Demo 影響檢查

不向後相容原則下，API 變更必須同步更新所有消費端：
1. 識別變更的 class/function
2. LSP `findReferences` 找到所有消費者，再用 rg 搜尋 `demo_*.py`、`poc/` 中的字串引用（不含 `examples/`——`scripts/demo_*.py` 已擔負 demo 職責）
3. 驗證受影響的消費端是否需要更新

---

## 輸出格式

問題分三級（Critical/Important/Suggestion 的定義 + 信心水準標註）見 [review-engine](../skills/review-engine/SKILL.md) 嚴重度框架。

每個發現包含：`檔案:行號`、問題描述、修正建議、信心水準（confirmed/evidence-based/inferred）。

---

## Finding 呈現

finding 預設留在審查報告/對話，供用戶 `/copy` 搬到實作 LLM（**人主導工作流**，不靠持久化追蹤）。**跨命令自動化場景**（接 `/judge-review`/`/followup-review`）才寫 `.review/<branch>.md`（Finding Record 表格，欄位見 [workflow-review-pattern.md](./instruction/_common/workflow-review-pattern.md)）—— code-review 立場 optional（接 `/judge-review`→`/followup-review` 鏈才寫）；一旦進入該鏈，judge-review/followup-review 預設讀寫持久化（它們即此「跨命令自動化場景」，故二者步驟內固定讀寫、非再條件判斷）。`/commit` 階段 6 成功後清除。

```
## Code Review Findings — <branch>

| ID | 嚴重度 | 檔案:行 | 問題 | 建議 | 狀態 | 決策 |
|----|--------|---------|------|------|------|------|
| F1 | 🔴 critical | src/foo.py:42 | ... | ... | open | — |
```

Suggestion 級留在報告即可,不持久化(避免噪音)。

---

## Commit Message 產生

審查完成後，基於已分析的 diff 直接產生 commit message。**格式 / 語言規範見 [commit.md](./commit.md) 階段 4 — 單一真相源**（task #10：避免雙重定義 drift）。

**type 對應審查結論**（code-review 特有，映射審查發現 → type）：

| 審查判斷 | type | 說明 |
|----------|------|------|
| 新功能、新模組 | `feat` | 新增能力 |
| 修正邏輯錯誤、安全問題 | `fix` | 修正既有問題 |
| 架構調整、模式統一 | `refactor` | 不改行為的結構改善 |
| 效能改善 | `perf` | 回應 Performance 軸發現 |
| 測試補充 | `test` | 回應 Correctness 軸發現 |
| 文檔、instruction 檔 | `docs` | 文檔同步 |

**產生時機**：審查結論為「無 Critical 問題」或「用戶確認 Critical 可接受」時才產生。有未解決 Critical 問題 → 只輸出審查報告，不產生 commit message。

---

## 流程位置

> **canonical review flow（詳細）以本檔為單一源** —— 其他命令畫 flow 須引用此處、不重畫（防 flow drift；機械追蹤見 [/sync-sources](./sync-sources.md)）。commands/CLAUDE.md 的 review-pipeline recipe 是高層概觀，非重畫。

```
/spec（純輔助·需求釐清，可選）→ /execution-plan（含 EP Review）→ [/ep-validate] → /build（含 Agent Review）→ /code-review（六軸含 axis 3 結構 = arch 吸收，top-down，含 commit message）→ /judge-review（一次）→ /commit
```

後續：用戶確認 commit message → `/commit` 捷徑（跳過階段 2 Git 狀態分析；保留 2.7 POC/Demo 處置閘門；見 [commit](./commit.md) 捷徑模式）

---

## 語音通知

遵循 [voice-notification skill](../skills/voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始程式碼審查"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「審查完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```
