---
name: agent-workflow
description: Guides Agent spawning, worktree isolation, concurrency control, and parallel execution patterns. Use when spawning agents, using worktrees, running parallel tasks, invoking /build with --max-agents, or setting up Writer/Reviewer patterns. Triggers on: agent, worktree, spawn, parallel, isolation, subagent, background task, auto mode.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
---

# Agent 與平行執行規範

Claude Code 提供多種平行模式，依任務規模和協調需求選擇。

## 平行模式選擇

| 模式 | 適用場景 | 協調需求 | 說明 |
|------|---------|---------|------|
| **Agent tool + worktree** | 互動式平行實作 | 中（手動 spawn） | 本 skill 主要涵蓋 |
| **Writer/Reviewer 雙 session** | 無偏差 code review | 低（兩個 terminal） | 審查者用新 session 避免 bias |
| **Agent teams** | 複雜多步驟工作流 | 高（自動協調） | 共享 tasks、messaging、team lead |
| **Auto mode** | 無人值守自主執行 | 無 | `claude --permission-mode auto -p` |

---

## Agent Tool + Worktree（互動式）

### 並發控制：自適應模型偵測

**Step 1**：從系統提示詞的 model 資訊判斷當前 GLM 模型：

| 系統提示詞中的模型 ID | 對應模型 | GLM 模型 |
|---------------------|---------|---------|
| `claude-haiku-*` / `glm-4.7` | haiku | glm-4.7 |
| `claude-sonnet-*` / `glm-5.1` | sonnet | glm-5.1 |
| `claude-opus-*` / `glm-5-turbo` | opus | glm-5-turbo |

**Step 2**：查表決定 Agent 模型和並發上限：

| 主 session GLM 模型 | Agent 模型 | 並發上限 | 說明 |
|--------------------|-----------|---------|------|
| `glm-4.7` (haiku) | haiku | **1** | rate limit 2，保守用 1 |
| `glm-5.1` (sonnet) | sonnet | **4** | rate limit 10，安全用 4 |
| `glm-5-turbo` (opus) | **sonnet**（降級） | **1** | rate limit 1，Agent 降級避開 bottleneck |

**spawn Agent 前必須印出確認**：`[Agent] model=sonnet, max=4, current=0`

### 任務分級

| 場景 | Agent 使用 | 說明 |
|------|-----------|------|
| 簡單修改（1-2 檔案） | 不用 Agent | 主 session 直接做更快 |
| 研究探索 | 1 個 foreground Agent（`Explore` 類型） | 只需 Read/Grep，不需要 worktree |
| 技術驗證 PoC | 1 個 Agent + `isolation: "worktree"` | 失敗自動清理，零污染 |
| 中型實作（3-8 檔案） | 1-N 個 Agent + worktree | 按模型並發上限控制 |
| 大型改動（20+ 檔案） | `/batch` 命令 | 自動拆分 5-30 單元，每單元獨立 worktree |

### Worktree 隔離

**Worktree 基於 committed state 建立，看不到 uncommitted changes。**

Pre-flight 檢查：
1. **Uncommitted dependency**：Agent 需要看到 uncommitted changes？→ **先 commit**，再 spawn
2. **Branch check**：當前 branch 是否正確 base？不是 → 先 checkout
3. **多 Agent 協作**：先把前置工作 commit 到 feature branch，再從該 branch spawn

**Prompt 路徑紀律**：Agent 在 worktree 中 CWD 是 worktree 目錄。**用相對路徑**，不要用主 worktree 絕對路徑。

何時用 `isolation: "worktree"`：PoC 驗證、平行實作、風險操作。
何時不用：純研究（foreground Agent 即可）、單檔案修改、改動少時不用 isolation 更簡單。

### PoC → Implement 流程

1. Agent 跑 PoC（worktree）→ 失敗自動清理 / 成功讀取結果
2. **審查 Agent 產出**（不要假設正確）→ 跑測試、code-review、修正設計瑕疵
3. 確認方向後實作 → 小範圍主 session 做，大範圍再 spawn Agent

**品質預期**：核心邏輯 ~80% 正確，細節（邊界條件、錯誤處理、命名）常需修正。

### `/build` 整合

`/build --max-agents N` 的 N 受模型並發上限限制。未傳入時預設使用查表的並發上限。

---

## Writer/Reviewer 雙 Session

**新鮮 context 能提升審查品質** — Claude 審查自己剛寫的 code 時有 bias。

```
Session A（Writer）                      Session B（Reviewer）
─────────────────────                    ─────────────────────
實作 rate limiter
                                         審查 @src/middleware/rateLimiter.ts
                                         找 edge cases、race conditions、
                                         與現有 middleware 的一致性
根據 Session B 的 feedback 修正
```

也可以用於測試：一個 session 寫測試，另一個寫通過測試的程式碼。

---

## Agent Teams

自動協調多個 session 的平行工作流。適合需要 shared tasks、messaging 和 team lead 的複雜場景。

（此功能為 Claude Code 內建，詳細設定見 Claude Code 官方文檔。）

---

## Auto Mode

無人值守自主執行。classifier model 在命令執行前審查，阻擋 scope 升級、未知基礎設施、和惡意內容驅動的操作。

```bash
claude --permission-mode auto -p "fix all lint errors"
```

**注意**：非互動式 `-p` 模式下，如果 classifier 反覆阻擋操作，auto mode 會中止（沒有用戶可回退）。

---

## 自檢清單

### Agent tool spawn 前

- [ ] 已偵測自身模型並查表確認 Agent 模型和並發上限
- [ ] 已印出 `[Agent] model=X, max=N, current=M`
- [ ] 當前 Agent 數量未超過上限
- [ ] 任務確實需要 Agent
- [ ] Prompt 包含足夠 context + 相對路徑 + rules-reminder 指引（Agent 看不到 auto-loaded rules）
- [ ] Uncommitted changes：需要 → 先 commit；Branch：不正確 → 先 checkout
- [ ] 失敗 Agent 的 worktrees 已清理（`git worktree list`）
- [ ] Agent 產出 commit 前需用戶確認（[commit-consent](../../rules/commit-consent.md)）

### 選擇平行模式時

- [ ] 互動式平行實作 → Agent tool + worktree
- [ ] 無偏差審查 → Writer/Reviewer 雙 session（開新 terminal）
- [ ] 無人值守 → Auto mode（`--permission-mode auto`）

### 常見失敗模式

| 模式 | 症狀 | 修正 |
|------|------|------|
| **Kitchen sink** | 一個 session 塞太多不相關任務 | `/clear` 切換任務 |
| **反覆修正** | 同一問題修正 2 次仍失敗 | `/clear` + 重寫更好的 prompt |
| **過度探索** | "investigate" 不限範圍，讀了幾百個檔案 | 限縮範圍或用 subagent |
| **信任未驗證** | 產出看似合理但沒驗證 | 必須提供驗證（測試、截圖、腳本） |
