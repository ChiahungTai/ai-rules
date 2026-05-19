---
name: agent-workflow
description: Guides Agent spawning, worktree isolation, and concurrency control. Use when spawning agents, using worktrees, running parallel tasks, or invoking /build with --max-agents. Triggers on: agent, worktree, spawn, parallel, isolation, subagent, background task.
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
---

# Agent 與 Worktree 使用規範

**Agent 是工具不是預設。** 依任務複雜度分級使用，由模型自適應控制並發上限。

## 並發控制：自適應模型偵測

### Step 1：偵測自身模型

從系統提示詞的 model 資訊判斷當前 GLM 模型：

| 系統提示詞中的模型 ID | 對應模型 | GLM 模型 |
|---------------------|---------|---------|
| `claude-haiku-*` / `glm-4.7` | haiku | glm-4.7 |
| `claude-sonnet-*` / `glm-5.1` | sonnet | glm-5.1 |
| `claude-opus-*` / `glm-5-turbo` | opus | glm-5-turbo |

### Step 2：查表決定 Agent 策略

| 主 session GLM 模型 | Agent 模型 | 並發上限 | 說明 |
|--------------------|-----------|---------|------|
| `glm-4.7` (haiku) | haiku | **1** | rate limit 2，保守用 1 |
| `glm-5.1` (sonnet) | sonnet | **4** | rate limit 10，安全用 4 |
| `glm-5-turbo` (opus) | **sonnet**（降級） | **1** | rate limit 1，Agent 降級避開 bottleneck |

**spawn Agent 前必須印出確認**：`[Agent] model=sonnet, max=4, current=0`

## 任務分級

| 場景 | Agent 使用 | 說明 |
|------|-----------|------|
| 簡單修改（1-2 檔案） | 不用 Agent | 主 session 直接做更快 |
| 研究探索 | 1 個 foreground Agent（`Explore` 類型） | 只需 Read/Grep，不需要 worktree |
| 技術驗證 PoC | 1 個 Agent + `isolation: "worktree"` | 失敗自動清理，零污染 |
| 中型實作（3-8 檔案） | 1-N 個 Agent + worktree | 按模型並發上限控制 |
| 大型改動（20+ 檔案） | `/batch` 命令 | 自動拆分 5-30 單元，每單元獨立 worktree |

## Worktree 隔離

### Pre-flight 檢查（spawn 前）

**Worktree 基於 committed state 建立，看不到 uncommitted changes。**

1. **Uncommitted dependency**：Agent 需要看到 uncommitted changes？→ **先 commit**，再 spawn
2. **Branch check**：當前 branch 是否正確 base？不是 → 先 checkout
3. **多 Agent 協作**：先把前置工作 commit 到 feature branch，再從該 branch spawn

### Prompt 路徑紀律

Agent 在 worktree 中 CWD 是 worktree 目錄。**Prompt 用相對路徑**，不要用主 worktree 絕對路徑（會導致 Agent 編輯主 worktree 而非 worktree）。

### 何時用 `isolation: "worktree"`

- PoC 驗證、平行實作、風險操作

### 何時不用

- 純研究（foreground Agent 即可）、單檔案修改、改動少時不用 isolation 更簡單

## PoC → Implement 流程

1. Agent 跑 PoC（worktree）→ 失敗自動清理 / 成功讀取結果
2. **審查 Agent 產出**（不要假設正確）→ 跑測試、code-review、修正設計瑕疵
3. 確認方向後實作 → 小範圍主 session 做，大範圍再 spawn Agent

**品質預期**：核心邏輯 ~80% 正確，細節（邊界條件、錯誤處理、命名）常需修正。

## `/build` 整合

`/build --max-agents N` 的 N 受模型並發上限限制。未傳入時預設使用查表的並發上限。

## 自檢清單

spawn Agent 前確認：
- [ ] 已偵測自身模型並查表確認 Agent 模型和並發上限
- [ ] 已印出 `[Agent] model=X, max=N, current=M`
- [ ] 當前 Agent 數量未超過上限
- [ ] 任務確實需要 Agent
- [ ] Prompt 包含足夠 context + 相對路徑 + rules-reminder 指引（Agent 看不到 auto-loaded rules）
- [ ] Uncommitted changes：需要 → 先 commit；Branch：不正確 → 先 checkout
- [ ] 失敗 Agent 的 worktrees 已清理（`git worktree list`）
- [ ] Agent 產出 commit 前需用戶確認（[commit-consent](../../rules/commit-consent.md)）
