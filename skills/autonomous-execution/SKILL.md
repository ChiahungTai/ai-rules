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

以下情況不自主執行，依紅線/黃線分級處置：

### 🔴 紅線（跳過 + 記錄，絕不自主執行）

**不可逆操作** —— 自主執行風險大於任務完成度。跳過並記錄到 completion report 紅線跳過清單段：

| 類型 | 範例 |
|------|------|
| 檔案刪除（不可逆） | `rm -rf`、`find -delete`、`git clean -fd` |
| Git 遠端 / 歷史破壞 | `git push --force`、`git reset --hard`、影響共享 history 的 `git rebase` |
| Git commit | `git commit`（commit-consent rule 明文「例外：無」—— 所有 commit 需用戶確認，半夜自主跑亦不例外） |
| 系統層變更 | `sudo *`、`brew uninstall`、`chmod` 系統路徑、`osascript`（macOS 自動化） |
| 外部服務狀態 | `docker rm`、`docker stop`、DB `DROP`/`DELETE`、redis `FLUSHDB` |
| 語意型紅線（既有） | 刪除 API、修改 DB schema、變更外部整合介面、安全邏輯、付費操作 |

> 紅線跳過時 deep-work **不阻塞、不語音通知** —— 早上看 completion report 判讀（呼應 [acceptance-evidence](../../rules/acceptance-evidence.md) L6 人類觀察層：半夜自主跑時人類 viewport 是危險操作的唯一兜底）。
>
> **`git commit` 跳過的語義**：deep-work 階段 5 finalization 不自主 commit，變更留在 working tree 等用戶接手（用戶回來後 `/commit` 走 commit-consent 流程）。這對齊 [commit-consent](../../rules/commit-consent.md) rule「例外：無」的硬規則。
>
> **`git commit` 不因 session 性質改變**：紅線「跳過 + 等用戶接手」涵蓋所有 autonomous 場景 —— 半夜無人（記錄到 completion report 後續）、long session 中用戶回來互動（停下來、展示 commit message、等獨立確認）。autonomous mode 的「連續執行」vibe **不延伸到 commit** —— commit 永遠是互動式 gate，即使用戶剛授權過上一個 commit，下一個仍需獨立確認（一次授權 ≠ 永久授權）。

### 🟡 黃線（自主決策 + 記錄到 completion report）

**可逆但有風險** —— 選最合理方案繼續，理由寫入 completion report 待確認清單段：

| 類型 | 範例 | 自主策略 |
|------|------|---------|
| Git local 可逆 | `git tag`、`git stash`、`git add`（stage 可逆） | 自主執行（`git commit` 見紅線段——commit-consent 要求用戶確認） |
| 檔案系統可逆 | `mkdir`、`mv`、`touch`、單檔 `rm`（可重建） | 自主執行 |
| 開發工具執行 | `uv run`、`pytest`、`make`、`docker run`（新增 container） | 自主執行 |
| 依賴變更 | `uv add`、`uv remove`、`brew install <pkg>` | 自主執行，記錄理由 |

> 黃線是「任務關鍵依賴」時（例如中段必須 commit 才能繼續），LLM 自主判斷降級路徑（git stash、worktree 隔離等）。

### 與「不問問題」原則的關係

本分級**不 override** Core Principles 的「不問問題」——歧義仍選最合理方案並記錄。但紅線操作的本質是「做了就無法事後修正」，不適用「選最合理」——選了不等於安全。

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
| Shell 展開 | **禁止 `$VAR`、`$(cmd)`**（觸發 simple_expansion / command_substitution），需要變數時用具體值或寫 `.py` |
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

### 🔴 紅線跳過清單
- [紅線操作 / 跳過理由 / 影響範圍]（半夜自主跑時不阻塞，供早上判讀；定義見 Don't-Self-Decide Boundaries 紅線段）

### ⚠️ 未解決問題
- [技術失敗或無法降級的問題]
```

> 報告開頭若紅線清單非空 → 加註「⚠️ 含 N 項紅線跳過，需人類判讀」。
