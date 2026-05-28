---
description: "第一性原理代碼審查。/code-review [branch] [base]"
when_to_use: "Review uncommitted changes or a feature branch using multi-axis methodology and first-principles reasoning."
usage: "/code-review [target-branch] [base-branch]"
argument-hint: "無參數審查 uncommitted / branch 名稱審查該 branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /code-review — 第一性原理代碼審查

基於第一性原理審查尚未 commit 的 code。不只是看改了什麼，更要讀相關程式碼確認**為什麼這樣改**。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — 六軸審查方法論

按需讀取：
- [security-and-hardening](../skills/security-and-hardening/SKILL.md) — 安全審查細節
- [performance-optimization](../skills/performance-optimization/SKILL.md) — 效能審查細節

---

## 審查範圍

| 用法 | 實際執行 | 場景 |
|------|---------|------|
| `/code-review` | `git diff` + `git diff --cached` | 審查 uncommitted（預設） |
| `/code-review feat/xxx` | `git diff HEAD...feat/xxx` | 審查 feature branch |
| `/code-review feat/xxx main` | `git diff main...feat/xxx` | 審查 branch（指定 base） |

---

## Lint 預檢

對 modified files 執行 `ruff check --select F401,PLC0415`，結果併入審查報告。

| Rule | 抓什麼 | 唯一合理例外 |
|------|--------|-------------|
| F401 | unused import（LLM 重構後殘留） | `__all__` 用途、optional dependency try/except |
| PLC0415 | import 不在檔案頂部（LLM 偷懶） | circular import avoidance |

---

## 六軸審查 + 第一性原理

### 1. Correctness — 符合規格嗎？
邊界情況、測試充分性

### 2. Readability — 能看懂嗎？
命名清晰、控制流直觀、避免過早抽象

### 3. Architecture — 符合現有架構嗎？
遵循現有模式還是引入新模式？模組邊界乾淨？

### 4. Security — 輸入驗證、密碼安全、權限檢查
diff 涉及 HTTP handler / user input / credential / auth 時，必須讀取 [security-and-hardening](../skills/security-and-hardening/SKILL.md)

### 5. Performance — 無 N+1 查詢、無無界操作

### 6. UC Coverage — 滿足 Use Case 描述嗎？
大型/中型變更時審查：
- 實作是否涵蓋 UC 描述的所有行為？
- 是否有 UC 引用的行為在 diff 中沒有對應實作？
- EP 段落引用的 UC ID 是否與 USE-CASES.md 一致？
小型變更（bug fix）跳過此軸。

### 第一性原理 + 第二層思考
- **讀相關程式碼**：不只看 diff，讀取被修改檔案引用的其他模組
- **確認實作合理性**：為什麼這樣寫？有沒有更簡單的方式？
- **驗證假設**：修改是否基於對現有程式碼的正確理解？
- **追蹤後果**：這個修改的下游影響是什麼？依賴模組是否受影響？
- **審查者自證**：提出問題前必須用 Read/Grep 查證宣稱。聲稱檔案存在 → 讀它；聲稱命名衝突 → 查 import 鏈；聲稱依賴順序有問題 → 追蹤執行順序。無法查證的宣稱標注「未驗證」

深層思考框架見 `~/.claude/rules/deep-thinking.md`

---

## Demo/Examples 影響檢查

不向後相容原則下，API 變更必須同步更新所有 demo/examples：
1. 識別變更的 class/function
2. 搜尋 `demo_*.py` 和 `examples/*.py` 是否 import 被修改模組
3. 驗證受影響的 demo 是否需要更新

---

## 輸出格式

問題分三級：
- **Critical** — 必須修正（邏輯錯誤、安全問題、資料損壞風險）
- **Important** — 建議修正（架構不一致、可讀性、效能隱患）
- **Suggestion** — 可以改善（風格、命名、小優化）

每個發現包含：`檔案:行號`、問題描述、修正建議。

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
/spec → /execution-plan（含 EP Review）→ /build（含 Agent Review）→ /code-review（含 commit message）→ /commit
```

後續：用戶確認 commit message → `/commit`（跳過階段 2 分析，直接執行 lint + commit）
