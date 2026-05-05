---
description: "第一性原理代碼審查 — 未 commit 的 code，多找相關程式碼確認實作合理性"
usage: "/code-review [選項]"
argument-hint: "[可選：指定檔案或範圍]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /code-review — 第一性原理代碼審查

基於第一性原理審查尚未 commit 的 code。不只是看改了什麼，更要讀相關程式碼確認**為什麼這樣改**。

## 📚 委託 Skills

審查時自動載入：

- **`code-review-and-quality`** — 五軸審查方法論（correctness, readability, architecture, security, performance）
- **`security-and-hardening`** — 安全審查細節
- **`performance-optimization`** — 效能審查細節

---

## 審查範圍

審查 staged 變更或最近的 commits。

> 🔧 **搜尋約束**：`fd` 取代 `find`、`rg` 取代 `grep`。詳見 `@~/.claude/rules/modern-cli-preference.md`

## 五軸審查 + 第一性原理

### 1. Correctness — 符合規格嗎？
- 是否符合 spec 或 task 的要求？
- 邊界情況是否處理？
- 測試是否充分？

### 2. Readability — 能看懂嗎？
- 命名清晰？控制流直觀？結構有組織？
- 是否有三行相似程式碼可以提取的過早抽象？

### 3. Architecture — 符合現有架構嗎？
- 遵循現有模式還是引入新模式？
- 模組邊界乾淨？依賴方向正確？

### 4. Security — 輸入驗證、密碼安全、權限檢查

### 5. Performance — 無 N+1 查詢、無無界操作

### 第一性原理層面
- **讀相關程式碼**：不只看 diff，讀取被修改檔案引用的其他模組
- **確認實作合理性**：為什麼這樣寫？有沒有更簡單的方式？
- **驗證假設**：修改是否基於對現有程式碼的正確理解？

## Demo/Examples 影響檢查

不向後相容原則下，API 變更必須同步更新所有使用該 API 的 demo/examples。

### 檢查流程

1. **識別變更模組**：從 diff 中提取被修改的 class/function
2. **追蹤 import 鏈**：搜尋 `demo_*.py` 和 `examples/*.py` 是否 import 被修改的模組
3. **驗證兼容性**：讀取受影響的 demo，確認是否使用已變更的 API
4. **標記需要更新的 demo**：列出需要同步修改的 demo 檔案

### 輸出

- ✅ 無受影響的 demo/examples
- ⚠️ `[demo_path]` — 使用了已變更的 `[class/function]`，需要更新

## 輸出格式

問題分三級：
- **Critical** — 必須修正（邏輯錯誤、安全問題、資料損壞風險）
- **Important** — 建議修正（架構不一致、可讀性問題、效能隱患）
- **Suggestion** — 可以改善（風格、命名、小優化）

每個發現包含：`檔案:行號`、問題描述、修正建議。

---

## 📚 與其他命令的協作

### 流程位置
```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review
```

### 前置命令
- `/build` — 實作完成後的程式碼審查

### 後續命令
- `/claude:sync` — 同步 CLAUDE.md 與程式碼
- `/consistency` — 文檔品質檢查
- `/commit-message` — 生成提交訊息
