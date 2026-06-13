---
description: "排程工作接續 — 在指定時間自動 resume 當前工作（對應 Unix at 命令，CronCreate durable）"
when_to_use: "LLM provider reset usage 後需要自動接續工作時"
usage: "/at <時間> [任務簡述]"
argument-hint: "HH:MM 或 +Xh/+Xm | 任務簡述（可選）"
allowed-tools: ["Read", "Write", "Bash", "Glob", "CronCreate", "CronDelete", "CronList"]
---

# /at — 排程工作接續

在指定時間自動 resume 當前工作。對應 Unix `at` 命令（one-shot 排程）。

適用 LLM provider usage reset 後自動接續。Terminal 需保持開啟。

---

## 執行流程

### Phase 1：解析時間 + 捕獲 Context

1. **解析用戶輸入**：

   | 輸入格式 | 解析方式 | 範例 |
   |---------|---------|------|
   | `HH:MM` | 今天指定時間；已過 → 明天 | `14:30` → 今天 14:30 |
   | `+Xh` | 相對 X 小時後 | `+5h` → 5 小時後 |
   | `+Xm` | 相對 X 分鐘後 | `+30m` → 30 分鐘後 |

   計算 cron 表達式（5-field：`分 時 日 月 週`），pinned 到具體日/月，DoW = `*`。

2. **自動捕獲 git 快照**：
   - `git branch --show-current`
   - `git status --short`
   - `git log -5 --oneline`
   - `git stash list`

3. **提取 task hint**：時間之後的所有文字為任務簡述；無則標記「用戶未提供具體描述，請根據 git 狀態推斷」。

### Phase 2：寫入 Context 檔案

寫入 `.claude/at-context-{YYYYMMDD-HHMM}.md`（排程時間戳，避免衝突）。

**Context 檔案格式**：

```markdown
---
scheduled_at: "{ISO 時間}"
resume_at: "{ISO 時間}"
project_path: "{當前專案路徑}"
---

# 排程接續任務

## 任務簡述
{task hint}

## Git 快照（排程時）
- **Branch**: {branch}
- **Status**: {git status}
- **Recent commits**: {git log -5 --oneline}
- **Stash**: {stash list 或 "無"}

## ⛔ 給 Resume LLM 的指令
這是排程任務，不是閒聊。你必須：
1. 先執行 git status 和 git log -5 確認當前狀態
2. 比對上方快照和當前狀態，找出差異
3. 根據任務簡述和差異，繼續工作
4. 完成後刪除此檔案
```

### Phase 3：建立 CronCreate

呼叫 `CronCreate`：

```
cron: "{分} {時} {日} {月} *"
recurring: false
durable: true
prompt: |
  🔴 排程接續任務 — 用戶於 {scheduled_time} 排程此工作在 {resume_time} 自動接續。

  立即執行：
  1. 讀取 context 檔案：{context_file_path}
  2. 執行 git status、git log -5 了解當前狀態
  3. 根據 context 檔案中的任務描述和 git 狀態，繼續未完成的工作
  4. 完成後刪除 context 檔案 {context_file_path}

  ⛔ 禁止事項：
  - 禁止回答「目前沒有需要做的事」— 用戶明確排程了這次接續
  - 禁止靜默結束 — 如果無法判斷任務，產出 git 狀態報告
  - 禁止詢問用戶確認 — 這是自主執行模式

  如果 context 檔案不存在或無法判斷任務：
  → 執行 git status + git log -5 + git stash list
  → 產出「當前狀態報告」
  → 不要靜默結束
```

### Phase 4：確認 + 通知

印出排程摘要：

```
✅ 排程已建立（/at）
- Resume 時間：{HH:MM}
- Cron ID：{job_id}
- Context：{context_file_path}
- 任務：{task hint}
```

語音通知：`say -v Meijia -r 180 "已排程在 HH:MM 接續工作"`

---

## Resume 後的行為

Resume 觸發時，LLM 應：

1. **讀 context 檔案** → 了解任務和背景
2. **驗證 git 狀態** → 確認 context 快照與現實一致
3. **執行任務** → 自主完成（同 `/deep-work` 模式）
4. **清理** → 完成後刪除 context 檔案
5. **通知** → 語音通知完成

---

## 使用範例

```bash
# 指定時間接續
/at 14:30

# 指定時間 + 任務簡述
/at 14:30 繼續 /build docs/execution-plan.md 段落 3

# 相對時間（5 小時後）
/at +5h

# 相對時間 + 任務
/at +5h 重構 data_loader.py
```

---

## 執行約束

- **Terminal 必須保持開啟**：CronCreate 在 Claude Code session 中觸發
- **`durable: true`**：持久化到 `.claude/scheduled_tasks.json`，短暫中斷可恢復
- **清理**：Resume 完成後必須刪除 context 檔案，避免殘留
- **多個排程**：若 `.claude/` 已有 `at-context-*` 檔案，提示用戶確認是否有衝突
- **語音通知**：遵循 `voice-notification` skill 規範
