---
name: agent-workflow
description: "Guides Agent spawning, worktree isolation, concurrency control, parallel execution, and delegation. Use when spawning agents, using worktrees, running parallel tasks, delegating to agents, handling scope-external discoveries, invoking /build with --max-agents, or setting up Writer/Reviewer patterns. Triggers on: agent, worktree, spawn, parallel, delegation, side-discovery, scope redirect, manager-delegate, isolation, subagent, background task, auto mode."
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

### Subagent 產出格式：schema 嚴格度（raw material vs deliverable）

spawn agent 時，依「agent 產出是**原料**還是**直接交付**」選 schema 嚴格度：

| 產出性質 | schema | 為什麼 |
|---|---|---|
| **原料**（給主 session 組裝/parse，如 §HR 深審內容、findings 清單） | **free-text 或極簡 schema**（單層、少 required） | agent 價值在分析；strict schema 是約束不是助力 |
| **直接交付**（agent 產出即最終結構，如 rename edit list、verdict 物件） | StructuredOutput schema OK | 結構本身是 deliverable，值得強制 |

**🔴 anti-pattern：complex nested StructuredOutput + 多 required 用於「原料」產出** → **retry-exhausted**（agent 做完真實分析但無法 fit 進 nested schema，反覆重試全廢）。實證：`/codebase-sweep` indicators/ rollout 用 6-agent workflow（nested io_contracts/test_map schema）→ 6/6 retry-exhausted（224 tool uses 白費）；改直接執行（單 session）一次成。

**恢復路徑**（遭遇 retry-exhausted）：
1. **直接執行**（單 session，主 LLM 自己做）— 目錄/任務規模 fit 一個 session 時首選
2. 或 **free-text schema** + 主 session 從 free-text parse 結構
3. 禁：重跑同一 strict schema（必然再 retry-exhaust）

判準自問：「agent 回傳的東西，我是直接用，還是要再組裝/parse？」要再組裝 → free-text。

### 委派框架（Delegation Philosophy）

agent-workflow 偏控制導向（scope fence / git diff 驗產出 / classifier / gate），但放手碎片零散未連貫（[autonomous-execution](../autonomous-execution/SKILL.md)「不交半成品」、[build.md](../../commands/build.md)「裁量權」+ context handoff、scope fence「創造性例外」）。連貫化為 **delegate(goal + tools + context) → let go(within guardrails) → verify(outcome)** 模型。

**連貫模型**：

- **goal**：EP segment / 任務目標（清晰可驗收）
- **tools**：delegation 前配工具集——依任務領域匹配 skill description 觸發詞（任務含「測試」→ TDD skill、含「錯誤」→ debugging skill）；[build.md](../../commands/build.md) Agent Prompt 已有完整 skill invoke 實作清單（rules-reminder / test-driven-development / incremental-implementation / autonomous-execution），此處概念化引用不重列
- **context**：[build.md](../../commands/build.md) context handoff 已是最完整實作——引用不重述
- **let go**：實作層裁量權（build.md「EP 為收斂方向，實作層有發現真相的責任」）；放手底線 = [autonomous-execution](../autonomous-execution/SKILL.md) 紅線/黃線
- **verify**：[build.md](../../commands/build.md) git diff + Agent Review——引用不重述

**平衡（delegate + verify，非 delegate + trust）**：

- **防過度放手**：verify 是委派的**共同體**非事後補丁——純放手無驗證 = scope-creep 近乎 ship 重演。**強度上限**：delegate+verify 假設 verifier（主 LLM）可靠；deep-work 長 session 的 verifier 退化（context fatigue）是已知上限，由 build.md batch ceiling 部分緩解但不完全覆蓋。
- **防過度控制**：創造性任務（設計/實作）**不加 fence**（scope fence 已排除創造性）。委派光譜：機械任務 = tight delegation（fence）；創造性任務 = loose delegation（goal+tools+放手）；混合型（部分機械 + 部分判斷，如重構提升可讀性）= medium delegation（goal + 精簡 fence，只 fence 不可碰區域 + 放手判斷空間）。
- **fence vs 委派非矛盾**：兩者適用**不同任務類型**（同光譜兩端）——fence 是委派的特殊形態（目標極明確時的 tight delegation），委派框架是 scope fence 的上層框架。

**delegate→verify loop（與 Recovery 段互补）**：委派（本段）上游 → 降低 false-done；[autonomous-execution](../autonomous-execution/SKILL.md)「Session 級 Recovery」completeness validation（false-done 偵測）下游 → 捕捉殘餘。兩者形成 loop，**互补非重複**。**邊界**：verify 的 git diff 半邊（scope/claim 校驗）與 Recovery 段 completeness 互補不重疊；Agent Review 半邊關注**單段 code 正確性**（段落級），Recovery 段 completeness 關注**跨段落 EP 完成度**（EP 級）——builder 寫 verify 時引用 build.md Agent Review（段落級），不重述 Recovery 段的 EP 級 completeness。

**委派時 side-discovery**：agent 發現 scope 外 → Side-Discovery 段（scope-fence 負空間 redirect）是委派框架的 redirect 應用。

> **docs-mode 強度上限**：委派是**判斷框架**非機械閘門（無 server-side enforcement）；其 verify 半邊的機械性來自 build.md git diff（已存在）。理論支撐：ref-docs Ch19 AI Contract 四 pillar（Formalized Contract / Dynamic Negotiation / Quality-Focused Iterative Execution / Hierarchical Subcontracts）+ Ch6 Planning「does the how need to be discovered, or is it already known?」判準（控制 vs 放手）——外部靈感來源；核心論證用內部已查證引用（build.md 裁量權 / 紅線）承載。

### Worktree 隔離

**Worktree 基於 committed state 建立，看不到 uncommitted changes。**

Pre-flight 檢查：
1. **Uncommitted dependency**：Agent 需要看到 uncommitted changes？→ **先 commit**，再 spawn
2. **Branch check**：當前 branch 是否正確 base？不是 → 先 checkout
3. **多 Agent 協作**：先把前置工作 commit 到 feature branch，再從該 branch spawn

**Prompt 路徑紀律**：Agent 在 worktree 中 CWD 是 worktree 目錄。**用相對路徑**，不要用主 worktree 絕對路徑。

**安全不變量**（path-in-root / symlink-escape 偵測 / 優先 EnterWorktree）定義見 [autonomous-execution](../autonomous-execution/SKILL.md)「機械空間不變量」段；此處僅為 worktree 用法，不重述安全不變量定義（single-source）。

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

### Side-Discovery（scope-fence 負空間 redirect）

Scope Fence（上）擋機械任務 agent「順手重構」scope 外區塊，但 fence 是**死路**——擋擴大卻無 redirect，發現的 scope 外改進被丟棄。Side-discovery 補 **redirect 通道**：agent 發現 scope 外 meaningful 改進 → 建 Backlog 卡（非擴大 scope、非丟棄）。fence 說「不擴大」、side-discovery 說「scope 外工作去哪」——兩者共置（single-source），否則 fence 負空間是死路（擋擴大 + 無 redirect = 工作遺失）。

**觸發**：agent 審查/實作時發現 **scope 外 meaningful 改進**（非當前任務目標，但值得做）。

**triage 決策**：

- **defer**（default）：建 Backlog 卡供日後排程
- **accept**：擴大 scope——**需用戶/EP 確認，非自主擴大**（與 scope fence「不擴大」一致）；**自主模式（deep-work 半夜跑）用戶不可得 → accept 預設降級為 defer**（建 Backlog 卡 + completion report 標記待用戶確認，對齊 [autonomous-execution](../autonomous-execution/SKILL.md) 紅線 git commit 自主處置）
- **decline**：明確不值得，丟棄（記錄原因，避免重複發現）

**建卡**（defer 時）：用 [kanban-board](../kanban-board/SKILL.md) 卡片模板（標題 / 目標 / 相關 / 驗收標準——欄位名對齊模板，不在此重複定義）。依賴關係在「備註」欄標 `[blocked-by: <當前任務>]`（blockedBy 非標準欄位，見 kanban-board 模板）。

**防氾濫三層**：

- **threshold**：「meaningful」= 獨立發現時會 warrant 一張卡/EP 的改進（非 trivial 觀察）
- **batch**：side-discovery 先記錄到 completion report，**段落/任務結束時統一建卡**（非執行中斷流程）；研究 agent（Explore 等）不產 completion report → 記錄於 spawn prompt 回覆，由 spawner 代建卡
- **人類 triage**：kanban 每週回顧（kanban-board）清理低價值卡

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
- [ ] Agent 產出 commit 前需用戶確認（[outward-action-consent](../../rules/outward-action-consent.md)）

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
