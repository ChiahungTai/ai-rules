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
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — 六軸審查方法論

按需讀取：
- [security-and-hardening](../skills/security-and-hardening/SKILL.md) — 安全審查細節
- [performance-optimization](../skills/performance-optimization/SKILL.md) — 效能審查細節

Workflow 審查協調：[workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)（Ultracode 下平行六軸審查）

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

偵測 effort level 和模型並發上限（查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md)）。

**A. Workflow 模式**（effort = ultracode/xhigh 且 max-agents > 1）：

使用 Workflow tool，參照 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md) 腳本骨架。

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 軸 agents（最多 6） | ≤ max-agents |
| Verify | Critical findings → 3 verifier + ≥2/3 quorum | 3 × critical |

**啟用軸**：

| 軸 Agent | 審查項目 | 啟用條件 | 優先級 |
|----------|---------|---------|--------|
| Correctness | 邏輯 bugs、邊界案例、測試充分性 | **always** | P0 |
| Readability | 命名、控制流、避免過早抽象 | **always** | P0 |
| Architecture | 設計模式、模組邊界 | 變更 ≥ 3 files | P1 |
| Security | 輸入驗證、權限檢查 | diff 含 HTTP/auth/credential | P1 |
| Performance | N+1、無界操作 | 變更 ≥ 5 files | P2 |
| UC Coverage | Capabilities 行為覆蓋 | 大型/中型變更 | P2 |

啟用軸數 > max-agents → 從低優先級（P2 起）合併至前一個 agent（不丟棄任何軸）。

每個 Review agent prompt 包含：
- `git diff` 範圍
- 該軸的檢查項目清單（如上表）
- 相關檔案路徑（必讀）
- 方法論引用（code-review-and-quality；Security 軸額外引用 security-and-hardening）
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）
- schema: DimensionVerdict（定義在 workflow-review-pattern.md）

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 合成 results → 分三級（Critical/Important/Suggestion）→ Demo/Lab 影響檢查 → commit message 產生。

印出確認：`[Code Review Mode] effort=ultracode, workflow=true, max=N`

**B. Agent Tool 模式**（Fallback，max-agents = 1 但 effort = ultracode/xhigh）：

單一 Explore agent 做所有啟用軸（Writer/Reviewer 分離效果）。印出確認：`[Code Review Mode] effort=ultracode, workflow=false, agent=true`

**C. Main LLM 模式**（effort < ultracode）：

Main LLM 直接做所有軸（現有行為）。印出確認：`[Code Review Mode] effort=standard, workflow=false`

---

## 六軸審查 + 深層思考

### 1. Correctness — 符合規格嗎？
邊界情況、測試充分性

### 2. Readability — 能看懂嗎？
命名清晰、控制流直觀、避免過早抽象

### 3. Architecture — 符合現有架構嗎？
遵循現有模式還是引入新模式？模組邊界乾淨？

### 4. Security — 輸入驗證、密碼安全、權限檢查
diff 涉及 HTTP handler / user input / credential / auth 時，必須讀取 [security-and-hardening](../skills/security-and-hardening/SKILL.md)

### 5. Performance — 無 N+1 查詢、無無界操作

### 6. UC Coverage — 滿足 Capabilities 描述嗎？
大型/中型變更時審查：
- 實作是否涵蓋 CLAUDE.md Capabilities 表格描述的所有行為？
- 是否有 Capabilities 引用的行為在 diff 中沒有對應實作？
- EP 段落引用的能力描述是否與 Capabilities 表格或 .kanban/ 卡片一致？
- Capabilities 入口路徑是否指向 library 模組（非 scripts/）？
- 實作是否涵蓋「消費場景」描述的所有情境（happy path、錯誤操作、邊界、效能期待差異）？
小型變更（bug fix）跳過此軸。

### 深層思考（第一性原理 + 第二層思考）
- **讀相關程式碼**：不只看 diff，讀取被修改檔案引用的其他模組
- **確認實作合理性**：為什麼這樣寫？有沒有更簡單的方式？
- **驗證假設**：修改是否基於對現有程式碼的正確理解？
- **追蹤後果**：這個修改的下游影響是什麼？依賴模組是否受影響？
- **審查者自證**：提出問題前必須查證宣稱。聲稱命名衝突 → LSP `findReferences` 查 import 鏈；聲稱依賴順序有問題 → LSP `incomingCalls` / `outgoingCalls` 追蹤執行順序；聲稱 dead code → LSP `findReferences`（zero hits = 確認）；聲稱檔案存在 → Read 它。LSP 無法涵蓋的（字串、註解引用）用 rg 補充。無法查證的宣稱標注「未驗證」

深層思考框架見 `~/.claude/rules/deep-thinking.md`

---

## Demo/Lab 影響檢查

不向後相容原則下，API 變更必須同步更新所有消費端：
1. 識別變更的 class/function
2. LSP `findReferences` 找到所有消費者，再用 rg 搜尋 `demo_*.py`、`lab/`、`examples/` 中的字串引用
3. 驗證受影響的消費端是否需要更新

---

## 輸出格式

問題分三級：
- **Critical** — 必須修正（邏輯錯誤、安全問題、資料損壞風險）
- **Important** — 建議修正（架構不一致、可讀性、效能隱患）
- **Suggestion** — 可以改善（風格、命名、小優化）

每個發現包含：`檔案:行號`、問題描述、修正建議。

---

## Finding 持久化

Critical / Important finding 寫入 `.review/<branch>.md`(Finding Record 表格,欄位定義見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)),狀態初始 `open`。跨 session、跨命令可追蹤(`/judge-review` 更新決策、`/followup-review` 驗收、`/commit` 檢查殘留 Critical)。

```
## Code Review Findings — <branch>

| ID | 嚴重度 | 檔案:行 | 問題 | 建議 | 狀態 | 決策 |
|----|--------|---------|------|------|------|------|
| F1 | 🔴 critical | src/foo.py:42 | ... | ... | open | — |
```

Suggestion 級留在報告即可,不持久化(避免噪音)。

---

## Commit Message 產生

審查完成後，基於已分析的 diff 直接產生 commit message。

**格式**：`<type>(<scope>): <description>`

**語言規範**：

| 部分 | 語言 | 範例 |
|------|------|------|
| type | 英文 | `feat`, `fix`, `refactor` |
| scope | 英文 | `data`, `commands`, `ui` |
| description | **繁體中文**（術語保留英文） | `新增 DataGateway 統一數據介面` |
| body | 繁體中文 + 英文術語 | 說明為什麼這樣改 |

**type 對應審查結論**：

| 審查判斷 | type | 說明 |
|----------|------|------|
| 新功能、新模組 | `feat` | 新增能力 |
| 修正邏輯錯誤、安全問題 | `fix` | 修正既有問題 |
| 架構調整、模式統一 | `refactor` | 不改行為的結構改善 |
| 效能改善 | `perf` | 回應 Performance 軸發現 |
| 測試補充 | `test` | 回應 Correctness 軸發現 |
| 文檔、CLAUDE.md | `docs` | 文檔同步 |

**產生時機**：審查結論為「無 Critical 問題」或「用戶確認 Critical 可接受」時才產生。有未解決 Critical 問題 → 只輸出審查報告，不產生 commit message。

---

## 流程位置

```
/spec → /execution-plan（含 EP Review）→ [/ep-validate] → /build（含 Agent Review）→ /code-review（含 commit message）→ /commit
```

後續：用戶確認 commit message → `/commit`（跳過階段 2 分析，直接執行 lint + commit）

---

## 語音通知

遵循 `voice-notification` skill：
- **開始**：`say -v Meijia -r 180 "開始程式碼審查"`
- **完成**：`say -v Meijia -r 180 "主人！審查完成，請看報告～"`
