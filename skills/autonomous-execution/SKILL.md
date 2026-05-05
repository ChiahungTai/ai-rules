---
name: autonomous-execution
description: Guides autonomous execution — decision-making, error recovery, completion reporting. Use when implementing without user interaction, such as EP-based build or deep-work mode. Triggers on: autonomous execution, self-healing, deferred questions, completion report, don't-self-decide boundaries.
---

# Autonomous Execution

Methodology for autonomous implementation when user should not be disturbed. All questions are deferred to a completion report.

## Core Principles

- **不問問題**：遇到歧義時選擇最合理的方案並記錄決策理由
- **不亂要權限**：優先使用 Edit/Write/Read，Bash 僅用於 `uv run` 驗證
- **不趕時間**：充分理解任務後再動手
- **不交半成品**：每個段落必須完整實作、測試通過

## Decision Framework

| 情境 | 決策策略 |
|------|----------|
| 需求/描述有歧義 | 選擇最符合上下文的方案，記錄理由 |
| 多種技術路徑 | 優先選擇簡單、可維護的方案 |
| 命名選擇 | 遵循 python-standards 命名規範 |
| API 設計 | 參考同目錄已有程式碼風格 |
| 錯誤處理 | 遵循 crash-only design 或合理 fallback |
| 測試策略 | 核心邏輯必須有單元測試，邊界情況至少覆蓋一個 |

## Don't-Self-Decide Boundaries

以下情況**不自行處理**，標記為 ⚠️ 等待用戶：

- 刪除現有功能或 API
- 修改數據庫 schema
- 變更外部系統整合介面
- 涉及安全相關邏輯
- 需要付費或消耗資源的操作

## Error Self-Healing

```
錯誤發生
  → 讀取錯誤訊息，理解根因
  → 修改程式碼修正
  → 重新驗證
  → 仍失敗 → 換一種修法
  → 連續 3 次失敗 → 記錄問題，標記為 ⚠️，繼續下一個任務
```

## Permission Minimization

| 操作 | 策略 |
|------|------|
| 修改檔案 | Edit/Write（acceptEdits 模式自動通過） |
| 讀取檔案 | Read/Grep/Glob（無需權限） |
| Python 執行 | 僅用 `uv run pytest` 和 `uv run python` |
| 內聯腳本 | `python -c`、`python3 -c`、`uv run python -c` 等一律**禁止使用 `#` 註解**（會觸發權限提示），需要註解時改寫為 `.py` 檔案 |
| 管道命令 | 拆兩步：執行寫檔 → Read 工具過濾（詳見 @~/.claude/rules/python-standards.md「管道命令」章節） |
| 多行驗證 | 寫成 `.py` 檔案再 `uv run` |

## Completion Report

實作完成後輸出報告，包含：

```markdown
## 實作完成報告

### 實作結果

**新增檔案**:
- [路徑] - [用途]

**修改檔案**:
- [路徑] - [修改摘要]

**測試結果**: ✅ N passed / ❌ M failed

### 架構決策記錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| [決策] | [選項] | [為什麼] |

### 待確認清單（實作過程中的疑慮）

> 以下是我覺得有問題、自行做了決策的地方。請檢查是否合理，如需調整請告知。

| # | 疑慮描述 | 我的作法 | 理由 | 其他可行方案 |
|---|---------|---------|------|------------|
| 1 | [遇到的問題] | [選了什麼做法] | [為什麼選這個] | [方案A / 方案B] |

### ⚠️ 未解決問題
- [標記為 ⚠️ 的未解決問題]
```
