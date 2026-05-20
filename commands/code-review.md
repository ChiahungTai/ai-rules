---
description: "第一性原理代碼審查。/code-review [branch] [base]"
when_to_use: "Review uncommitted changes or a feature branch using five-axis methodology and first-principles reasoning."
usage: "/code-review [target-branch] [base-branch]"
argument-hint: "無參數審查 uncommitted / branch 名稱審查該 branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /code-review — 第一性原理代碼審查

基於第一性原理審查尚未 commit 的 code。不只是看改了什麼，更要讀相關程式碼確認**為什麼這樣改**。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — 五軸審查方法論

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

## 五軸審查 + 第一性原理

### 1. Correctness — 符合規格嗎？
邊界情況、測試充分性

### 2. Readability — 能看懂嗎？
命名清晰、控制流直觀、避免過早抽象

### 3. Architecture — 符合現有架構嗎？
遵循現有模式還是引入新模式？模組邊界乾淨？

### 4. Security — 輸入驗證、密碼安全、權限檢查
diff 涉及 HTTP handler / user input / credential / auth 時，必須讀取 [security-and-hardening](../skills/security-and-hardening/SKILL.md)

### 5. Performance — 無 N+1 查詢、無無界操作

### 第一性原理層面
- **讀相關程式碼**：不只看 diff，讀取被修改檔案引用的其他模組
- **確認實作合理性**：為什麼這樣寫？有沒有更簡單的方式？
- **驗證假設**：修改是否基於對現有程式碼的正確理解？

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

## 流程位置

```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review → /commit
```

後續：`/claude:sync` → `/consistency` → `/commit`
