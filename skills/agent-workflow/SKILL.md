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

Claude Code 官方四個**首類並行方法**（[官方比較](https://code.claude.com/docs/zh-TW/agents)），依「誰協調 / worker 是否互通 / 是否編輯同檔」選擇。**執行細節落在執行層命令**（`/deep-work` substrate、`/build` Phase 4），本 skill 是選擇參考。

| 方法 | 它是什麼 | 何時用 | 執行落點 |
|------|---------|--------|---------|
| **Subagents**（Agent tool + worktree） | 一個 session 內委派 worker，獨立 context 回摘要 | 側任務會用搜尋/日誌/檔案內容淹沒主對話 | 本 skill 主要涵蓋；`/build` Agent Review |
| **Agent view**（`claude agents` / `--bg`） | 一個螢幕調度 + 監控背景 session（supervisor 接管、survive terminal 關閉） | 多個獨立任務、user-away 可 peek/attach 監控 | **`/deep-work`** substrate layer（研究預覽 v2.1.139+） |
| **Agent teams** | 多個協調 session，共享任務清單 + 互傳訊息（leader 管理；實驗性，預設禁用） | 要 Claude 自己分派 + 保持 worker 同步 | Claude Code 內建（見官方文檔） |
| **Dynamic workflows**（Workflow tool / `ultracode`） | JS 腳本協調數十~數百 subagent，可對抗驗證 / 多角度起草 / loop 收斂 | 任務太大、需交叉驗證、大規模遷移/審計 | **`/build` Phase 4** Workflow 模式；[workflow-review-pattern](../../commands/instruction/_common/workflow-review-pattern.md) |

**其他相關（非並行方法，與上面正交）**：

- **Writer/Reviewer 雙 session**：開新 terminal 審查避免 bias（pattern，非 surface）
- **Auto mode**（`claude --permission-mode auto -p`）：無人值守的**權限模式**（autonomy enabler），非並行方法 —— 詳見下方「Auto Mode」
- **Worktrees**：給並行 session 各自 git checkout，避免編輯同檔（搭配上述方法用；agent-view bg session 自動 worktree）

---

## Agent Tool + Worktree（互動式）

### 並發控制：自適應模型偵測

**Step 1**：從系統提示詞的 model 資訊判斷當前 GLM 模型：

| 系統提示詞中的模型 ID | 對應模型 | GLM 模型 |
|---------------------|---------|---------|
| `claude-haiku-*` / `glm-4.7` | haiku | glm-4.7 |
| `claude-sonnet-*` / `glm-5.1` | sonnet | glm-5.1 |
| `claude-opus-*` / `glm-5-turbo` | opus | glm-5-turbo |

**Step 2**：依 Step 1 偵測的模型，查「rate limit 與並發上限」表得**並發上限**（單一源 — 本檔不自帶數字，避免 provider 改限額時這裡 drift；Claude: `rules/model-routing.md`）。

**spawn Agent 前必須印出確認**：`[Agent] model=<依 model-routing 任務類型>, max=N, current=M`

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

### Scope Fence（機械任務 prompt 模板 — negative-space）

機械任務（rename / 補 log / format / 批次替換）的 Agent prompt 只有「做什麼」不夠，必須加 **negative-space scope fence** —— 否則 Agent 易「順手重構」scope 外區塊（實證：4 個補-Logger agent 各自找到已有 Logger 的區塊順手改 severity / 合併 / 丟 callback 名，需 4 處 pure-revert）。模板三要素：

- **DO NOT** modify blocks that already contain `<pattern>`（例：`Logger.` 已存在的 except 塊 —— 別動）
- 只 touch 符合 `<criteria>` 的區塊（例：silent `except: pass` 或 print-only 塊）
- 完成後自驗：`rg <pattern> <edited_file>` 確認沒碰不該碰的

**適用判準**：機械任務（pattern 明確、意圖單一）強制；設計 / 實作任務（需創造性判斷）不強制。與 build 階段 2「Agent 產出機械驗證」攻守 —— fence 事前預防、git diff 事後驗證。

### `/build` 整合

`/build --max-agents N` 的 N 由用戶指定，預設 3（受並發上限 cap；Claude: `rules/model-routing.md`）。

---

## Writer/Reviewer 雙 Session

**新鮮 context 能提升審查品質** — AI agent 審查自己剛寫的 code 時有 bias。

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

**注意**：非互動式 `-p` 模式下，如果 classifier **反覆阻擋**操作（主動擋 scope 升級 / 惡意），auto mode 中止（沒有用戶可回退）。

**classifier unavailable ≠ 阻擋**（服務端間歇故障，非主動擋）：spawn Agent 收 classifier unavailable note（只回警告、無 findings）→ **先重試 spawn（≤ 2 次，間歇常成功）**；仍 unavailable 才降級主 LLM 自審 + **顯式標記 fallback**（警示獨立 review 丟失，非靜默降級）。GLM / 非 Claude harness 的 classifier 間歇 unavailable 是已知風險，重試是正解非異常（Claude: `rules/model-routing.md`）。

---

## spawn 失敗階梯（general，所有 spawn 共用）

spawn 失敗處理依失敗類型分階梯 —— classifier unavailable retry 見上方「Auto Mode」；本段涵蓋 **429 / 持續失敗**（所有 spawn 命令共用的 general 階梯）：

```
429 單次 → backoff retry（同 spawn 重試）
429 持續 → 降並發（N → N/2 → … 最深 = serialization，concurrency=1，一次一個循序）
              • deep-work（無人、無時間壓力）停在此 — 用時間換獨立性，保所有 lens
非 429 失敗（crash / timeout）→ retry ≤ 2（同 classifier 模式）
全失敗（serialization 仍 429，少見）→ 降級主 LLM 自審 + 顯式標記 fallback（警示獨立 review 丟失，非靜默）
```

**關鍵區分**：serialization 是**降並發的一步，不是降級**。降級（丟獨立性）只在 concurrency=1 還持續 429 才發生。deep-work（無人、無時間壓力）甚至可**預設低並發** —— 不急，何必冒 429 平行；用時間換獨立性，保所有 lens。

---

## 自檢清單

### Agent tool spawn 前

- [ ] 已偵測自身模型，查「並發上限」表確認（Claude: `rules/model-routing.md`）；Agent **model 依任務類型**
- [ ] 已印出 `[Agent] model=X, max=N, current=M`
- [ ] 當前 Agent 數量未超過上限
- [ ] 任務確實需要 Agent
- [ ] Prompt 包含足夠 context + 相對路徑 + rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules，必須在 prompt 開頭明確寫入：`fd` 取代 `find`、`rg` 取代 `grep`、`uv run` 前綴 Python、禁止 `sed` 修改 `.py/.md`、禁止 `$` shell 展開、輸出繁體中文）
- [ ] **若任務涉及 mock / PropertyMock / fixture**：prompt 主動注入專案 `tests/AGENTS.md`（legacy `tests/CLAUDE.md`）的 mock 規範段落摘要（agent 不會自己讀專案 instruction 檔，必須主動注入；見 [context-engineering](../context-engineering/SKILL.md)「Rule Freshness」）
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
