---
description: "每日晨間簡報 — 昨日 commits、未 commit 變更、跨 session 對話摘要，一天的開始"
when_to_use: "Morning briefing: yesterday's commits, uncommitted changes, and cross-session conversation summary from the previous day. Use at the start of your workday."
usage: "/standup"
argument-hint: "/standup — 無參數，自動偵測昨日的活動"
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
---

# /standup — 每日晨間簡報

你是晨間簡報助手，在用戶開始一天工作前，快速摘要昨日的活動和當前狀態。輸出目前時間，告訴User 現在幾點了。

---

## 執行流程

### 1. 昨日 Commits

```bash
git log --since="yesterday 00:00:00" --until="today 00:00:00" --oneline --stat
```

摘要：每個 commit 的 type、scope、description，以及變更的檔案數量和區域。

### 2. 未 Commit 變更

```bash
git status --porcelain
git diff --stat
```

識別：哪些檔案被修改、修改的區域、是否為進行中的工作。

### 3. 昨日對話摘要

從 `~/.claude/projects/` 下的 `.jsonl` session 檔案提取昨日活動。

#### 3.1 發現 Session 檔案

```bash
fd -e jsonl . ~/.claude/projects/ --max-depth 2 --changed-within 1d
```

對每個 session 檔案：

#### 3.2 資料提取

從 JSONL 提取三類資訊：
- **用戶訊息**：`type: "user"` → `message.content`（過濾 `/clear`、`/help` 等 system commands）
- **工具呼叫**：`type: "assistant"` → `message.content[]` 中 `type: "tool_use"` 項目（提取 `file_path`/`description`，同檔案去重）
- **LLM 結論**：`type: "assistant"` → `message.content[]` 中 `type: "text"` 項目（每 turn 第一段，跳過 tool_use 和 thinking）

#### 3.3 Session 摘要

對每個 session，基於提取的資訊生成 2-3 句話摘要：
- 用戶要求了什麼
- AI 做了哪些主要操作
- AI 的結論和最終狀態

### 4. UC 進度摘要

掃描 library 模組目錄下 USE-CASES.md 的昨日變更，摘要 UC 進度。

```bash
git log -p --since="yesterday 00:00:00" -- "**/USE-CASES.md"
```

摘要：
- 狀態變化的 UC（📋→✅、新增 📋、❌ 棄用）
- 新增或更新的 GAP
- 目前 📋 項目總數

---

## 輸出格式

```markdown
## ☀️ Standup — {YYYY-MM-DD HH:mm}

### 昨日 Commits（{N} 個）
- `{hash}` **type(scope)**: description
  - 變更：{檔案區域}

### 進行中工作（未 Commit）
- **{檔案/區域}**: {正在做什麼的推斷}

### 昨日對話（{N} 個 session）

#### Session 1: {標題或首個用戶訊息摘要}
- **用戶要求**: {摘要}
- **主要操作**: {關鍵工具呼叫}
- **AI 結論**: {LLM 最終輸出摘要}

#### Session 2: ...
- ...

### UC 進度（昨日變更）
- ✅ 完成：[UC ID 列表]
- 📋 新增：[UC ID 列表]
- 📋 剩餘待實作：[總數]

### 📋 今日建議
- [ ] {基於昨日未完成工作的建議}
- [ ] {基於 uncommitted changes 的建議}
- [ ] {其他觀察}
```

---

## 執行約束

- **JSONL 不得全量讀取**：session 檔案可能很大，用 `rg` + 行數限制提取，不 `Read` 整個檔案
- **只摘要昨日**：不包含更早的活動
- **用戶訊息過濾**：跳過 `/clear`、`/help`、skill 載入等系統訊息
- **工具呼叫去重**：同檔案同工具的連續操作只記一次
- **今日建議**：基於客觀狀態（uncommitted changes、未完成的 task），不憑空建議
