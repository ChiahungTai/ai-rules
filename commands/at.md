---
description: "排程工作接續 — 在指定時間自動 resume 當前工作（CronCreate one-shot，session-only）"
when_to_use: "LLM provider reset usage 後需要自動接續工作時"
usage: "/at <時間> [任務簡述]"
argument-hint: "HH:MM 或 +Xh/+Xm | 任務簡述（可選）"
allowed-tools: ["Read", "Write", "Bash", "Glob", "CronCreate", "CronDelete", "CronList"]
---

# /at — 排程工作接續

在指定時間自動 resume 當前工作。對應 Unix `at` 命令（one-shot 排程）。

適用 LLM provider usage reset 後自動接續。Terminal 需保持開啟。

> **與 `/handoff` 分工**：本命令是「時間接續」（usage 用盡，**自己 resume**）；要把工作交給**另一個** session/provider 並行或接手，用 [`/handoff`](handoff.md)。

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

2. **提取 task hint**：時間之後的所有文字為任務簡述（**任務目標** — resume 接續的依據）；無則標記「用戶未提供具體描述，resume 時看 git log 推斷進度」。

> **不捕獲 git snapshot**：/at 預設是「usage reset 後接續」，resume 時狀態可能已變（quota 期間其他進度）。context 只記**任務目標**，resume 時看**當前 git log/status** 知進度到哪 — 不比對排程時 snapshot（舊狀態無意義）。

### Phase 2：寫入 Context 檔案

> **路徑選擇理由**：判斷 auto mode 是否放行的條件是「路徑是否為 protected path」,與是否 gitignore 無關。`.claude/` 是 protected path(auto mode classifier 硬擋、accept-edits mode 彈框);`.at-contexts/` 不是 protected path,所有 edit mode 零摩擦放行。故 context 寫 `.at-contexts/`。

寫入 `.at-contexts/at-context-{YYYYMMDD-HHMM}.md`(排程時間戳,避免衝突)。

**Context 檔案格式**：

```markdown
---
scheduled_at: "{ISO 時間}"
resume_at: "{ISO 時間}"
project_path: "{當前專案路徑}"
---

# 排程接續任務

## 任務目標
{task hint}

## ⛔ 給 Resume LLM 的指令
這是排程任務（usage reset 後接續），不是閒聊。你必須：
1. 先執行 `git log --oneline -10` + `git status` 看**當前進度**（做到哪、剩什麼）
2. 根據任務目標 + 當前進度，接續未完成的工作（不比對排程時狀態 — quota 期間進度可能已變）
3. 完成後刪除此檔案
```

**寫 STATE.md**（session 結束）：若本 session 有轉向 / 卡點觀察，寫 repo root `STATE.md` 補「為什麼」（覆寫非累積；步驟見 [state-md-write](./instruction/_common/state-md-write.md)）。`.at-contexts` 維持一次性 ephemeral lifecycle（session-only、resume 後刪、gitignore），STATE.md 是持久觀察層——**兩者不取代**（不同 lifecycle，不可混溶）。

### Phase 3：建立 CronCreate

呼叫 `CronCreate`：

```
cron: "{分} {時} {日} {月} *"
recurring: false
prompt: |
  🔴 排程接續任務 — 用戶於 {scheduled_time} 排程此工作在 {resume_time} 自動接續。

  立即執行：
  1. 讀取 context 檔案：{context_file_path}（任務目標）
  2. 執行 `git log --oneline -10` + `git status` 看**當前進度**（不比對排程時 snapshot — quota 期間進度可能已變）
  3. 根據任務目標 + 當前進度，接續未完成的工作
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

> `{context_file_path}` = `.at-contexts/at-context-{YYYYMMDD-HHMM}.md`（Phase 2 寫入的 context 檔路徑）

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

1. **讀 context 檔案** → 了解**任務目標**（`.at-contexts/` 非 protected path，讀取零摩擦）
2. **讀 STATE.md**（repo root，若存在）→ 補 **Last session 觀察**（卡在哪、為何轉向、下次起手點）——「為什麼」參考；**完成度走 recovery 事實層**（git + EP re-derive，見 [autonomous-execution](../skills/autonomous-execution/SKILL.md)「Session 級 Recovery」），STATE 不覆蓋完成度
3. **看當前進度** → `git log --oneline -10` + `git status` 知做到哪（**不比對排程時 snapshot** — quota 期間進度可能已變，看當前才準）
4. **接續未完成** → 建進度提醒 sentinel（`touch /tmp/.claude-voice-pending`），根據任務目標 + 當前進度，自主完成剩餘（同 `/deep-work` 模式）
5. **清理** → 完成後刪除 context 檔案
6. **通知** → 清 sentinel（`rm -f /tmp/.claude-voice-pending`）+ 套 [voice-notification skill](../skills/voice-notification/SKILL.md)「任務完成」樣板 say（隨機稱謂）

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
- **session-only 排程（不持久化）**：cron 存活在當前 session，靠 terminal 保持開啟維持；session 結束即消失。一次性接續用途足夠（善用 usage reset 後的配額窗口內接續工作）
- **清理**：Resume 完成後必須刪除 context 檔案，避免殘留
- **多個排程**：若 `.at-contexts/` 已有 `at-context-*` 檔案，提示用戶確認是否有衝突
- **版控排除（一次性設定，與 auto-mode 放行無關）**：`.at-contexts/` 含任務目標描述，建議加入該專案 `.gitignore` 或全域 `core.excludesFile`，避免誤 commit
- **語音通知**：遵循 `voice-notification` skill 規範
