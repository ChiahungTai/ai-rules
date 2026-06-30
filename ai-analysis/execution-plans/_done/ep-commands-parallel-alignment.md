# EP — Commands × Parallel Alignment（/build、/deep-work 對齊官方 agent-view / workflows）

> **ep_type**: implementation（docs mode）
>
> **背景**：Claude Code 官方釋出三份並行文檔（agents 比較、agent-view、dynamic workflows）。本 EP 把文檔知識**路由到執行層命令**（`/build`、`/deep-work`），而非只塞進參考層 skill。受眾路由見各段。
>
> **證據背書**：dispatch graph 與 substrate layer 來自近 8 日 16 次 `/deep-work` 真實呼叫的 transcript 分析（非推測）。

## 實作總覽

四段。S1（/build）優先——/deep-work 的「委派 /build」路徑繼承它。S2 是主菜（/deep-work 雙層重構）。S3/S4 收斂尾巴，平行。

| 段 | 受眾對應官方文檔 | 範圍 | 規模 |
|----|----------------|------|------|
| S1 | workflows → `/build` Phase 4 | 補 resume / `/workflows` 監控 / acceptEdits-always 三點（加 deep-work 路徑框） | 小 |
| S2 | agent-view + workflows → `/deep-work` | 雙層重構：dispatch graph + substrate layer（agent-view/`-p`/`/at`） | 中 |
| S3 | agents 比較 → `agent-workflow` skill | 收斂為參考層（四方法表 + 指向執行落點） | 中 |
| S4 | — | `agents/README.md` 補 frontmatter（`isolation: worktree` / `permissionMode`） | 小 |

## UC 盤點（docs mode：受影響命令/rules）

| 受影響檔 | 變更性質 | 對應段 |
|---------|---------|--------|
| `commands/build.md` | Phase 4 補三點 + deep-work 路徑框 | S1 |
| `commands/deep-work.md` | dispatch graph + substrate layer 重構（含移除「/execution-plan 前置」假設） | S2 |
| `skills/agent-workflow/SKILL.md` | 四方法表對齊官方 + 執行落點指向 | S3 |
| `agents/README.md` | frontmatter 補 `isolation` / `permissionMode` | S4 |
| `commands/CLAUDE.md` | `/deep-work` 命令索引 description（若 dispatch 定位變） | S2 連動 |

無 `.py` callable 符號變更 → docs mode（驗證 = rg 殘留 + 跨檔一致性 + `/consistency`）。

## Scenario Matrix（docs mode：觸發/預期行為 in 文檔語境）

| # | 場景 | 觸發 | 預期行為（文檔命中） | 對應段 |
|---|------|------|--------------------|--------|
| SM-1 | /build workflow 被停掉 | user 中斷 / 429 | 告知可同 session resume（`/workflows` → `p`） | S1 |
| SM-2 | /build review workflow 背景跑 | Phase 4 Workflow mode | 告知用 `/workflows` 看進度；deep-work 下另可 `claude agents` 看 session 層 | S1 |
| SM-3 | /build 經 workflow spawn impl agent | 未來擴充 | 知會：workflow subagent 自動 acceptEdits，繞過 session mode | S1 |
| SM-4 | /deep-work 跑多命令 loop | EP→build→review | dispatch graph 路由到正確命令；agent-view `--bg` 可脫離 terminal | S2 |
| SM-5 | /deep-work 任務超過一個 usage 窗 | `/at <time>` inline | 認得 `/at` 為接續指令，reset 後 resume | S2 |
| SM-6 | user 離開（「我去洗澡了」） | /deep-work 前景跑 | 文件提示 `--bg`/agent-view 可 detach + 監控 | S2 |
| SM-7 | /deep-work 任務需先規劃 | 無 EP、任務複雜 | 自主調度 /execution-plan（非「user 前置」） | S2 |

## 段落劃分原則

S1→S2 序列依賴（deep-work 委派 build 須繼承 S1 的框）。S3/S4 與 S1/S2 平行（無依賴）。S2 是唯一的單向門級文件決策（改 /deep-work entry 假設），其餘雙向門。

---

## S1 — /build Phase 4 補強（優先）

### Context

`/build` Phase 4（Agent Review Cycle）已對齊官方 workflows 文檔的品質模式（3-perspective + adversarial verify + loop-until-dry，見 `workflow-review-pattern.md`）。**核心整合已完成，本段不重寫**，僅補官方文檔點出而 build 未提及的三個行為，並為「under /deep-work 自主路徑」加框（該路徑下監控責任與安全語境不同）。

**受眾**：workflows 文檔 → `/build` Phase 4（執行層）。

**依賴錨點**：`commands/build.md` 階段 4「Agent Review Cycle」段落（Workflow 模式 + loop 迭代收斂段）；`commands/claude/_common/workflow-review-pattern.md`（已定義 schema + 兩階段）。

### 修改要點

1. **resume 引導（b1）**：在 Phase 4 Workflow 模式段補一句——workflow 執行被中斷（user stop / 429 序列化）時，可同 session resume：已完成 agent 回快取結果，其餘 live 重跑（官方：`/workflows` → 選執行 → `p`）。deep-work 多階段 loop 中，每階段 workflow 各自可 resume。
2. **`/workflows` 監控引導（b2）**：補一句——review workflow 背景跑時，用 `/workflows` 看階段 / agent 計數 / 令牌；deep-work 下雙視角：`claude agents`（session 層，deep-work substrate）+ `/workflows`（workflow 層）。
3. **acceptEdits-always 安全註記（b3）**：在 Workflow 模式段加註——workflow 生成的 subagent **始終在 acceptEdits 模式執行，無視 session mode**（官方原話）。目前 review agent 全 `Explore`（read-only）無風險；但若未來 build 經 workflow spawn impl agent，**edit 會繞過 session 權限自動准**——自主路徑（deep-work + auto-mode）下，classifier + acceptEdits 是唯一防線，須知會。

### 驗證策略（docs mode）

- rg 殘留：`rg "resume|/workflows|acceptEdits" commands/build.md` 命中新增三點。
- 跨檔一致：與 `workflow-review-pattern.md` 的 resume/監控用語一致（不重複 schema 細節，只指向）。
- `/consistency commands/build.md` 單檔自洽。

---

## S2 — /deep-work 雙層重構（主菜）

### Context

`/deep-work` 現況（`commands/deep-work.md`）的兩個骨幹都太窄，與真實使用脫節：

1. **dispatch 只有二分支**（`:37-45`：`/build <EP>` vs 任意任務）——transcript 顯示真實路由更豐富（plan-loop、/code-review、/at 接續、complex debug）。
2. **substrate 只有單入口**（`:27-35`：`claude --permission-mode auto -p`）——16 次呼叫 0 次用 agent-view/`--bg`，但「我去洗澡了」顯示 user-away 需求真實存在；agent-view 是未實踐的真缺口。

**受眾**：agent-view 文檔（substrate）+ workflows 文檔（多階段 loop）→ `/deep-work`（執行層）。

**證據**：見本 EP 開頭「證據背書」+ Scenario Matrix SM-4~7。

**依賴錨點**：`commands/deep-work.md`「前置：進入 auto-mode」（`:27-35`）、「流程 dispatch」（`:37-45`）、「與其他命令的協作」（`:165-170`，含「前置：/execution-plan」假設）；`commands/at.md`（/at 接續語意）；`commands/build.md` Phase 4（S1 補強後）。

### 修改要點

#### 層 1：dispatch graph（取代 `:37-45` 二分支）

> **設計原則**：/deep-work 是**自主 MODE（overlay）**，可疊加在任意 LLM-chain 程序上，不剛性枚舉命令。dispatch graph 示例涵蓋 **observed（transcript 佐證）+ reasonable（設計判斷，未觀察但合理）**——避免過擬合觀察（agent-view 即「合理但 0 觀察」的代表）。

```
/deep-work <ARG>  ──自主 overlay，ARG 決定程序 + 疊加自主行為──

  ├─ ARG 命名 LLM-chain 命令 → 委派該命令 + 自主疊加
  │   • observed：/build、/execution-plan、/code-review、/ep-review、/ep-validate
  │   • reasonable（未觀察但合理）：
  │       /fix-test、/lint-fix（自癒 loop）、/audit-test、/consistency（自主品質）、
  │       /followup-review（驗收）、/metadata-sync（結算）、
  │       /handoff（跨 provider）、/sequential-batch（rate-limit 批次）
  │
  ├─ ARG = 任務描述 → deep-work 自選程序：
  │   • 複雜（需規劃）→ /execution-plan → /build（可加 /ep-validate、/ep-review）
  │   • fix/debug/研究 → 自身階段（complex；可自癒接 /fix-test、/lint-fix）
  │   • 完成後自主品質閘門 → /audit-test、/code-review
  │
  └─ ARG 內含接續/substrate 指令：
      • /at <time> → 跨 session 接續修飾詞（reset 後 resume；inline，非獨立分支）
      • substrate 見層 2（agent-view / -p / /handoff / /sequential-batch）
```

關鍵決策（記錄）：
- **`/execution-plan` 從「前置」改「可自主調度」**——transcript #7、#15 證實 user 期望 deep-work 任務中自主產 EP。現況 `:167`「前置：/execution-plan（先生成計畫書）」改為 dispatch graph 一支（仍可由 user 前置，但非假設）。
- **「任務描述」路徑標明 complex**——transcript 證實是 debug/多 agent 研究（非小型），自身階段不降級。

#### 層 2：substrate layer（取代 `:27-35` 單入口）

| 入口 | 何時 | 與 auto-mode 關係 |
|------|------|----------------|
| **agent-view `claude agents` / `--bg`**（長程 loop 推薦） | EP→build→review 多命令、user 要可監控/介入、要關 terminal | 用 dir `defaultMode: auto`（repo 已設），免旗標；須先互動接受 auto 一次 |
| **headless `claude -p`**（一次性） | 要 stdout 報告、單一短任務 | 現況保留 |
| **`/at` 組合**（跨 session） | 任務超過一個 usage 窗 | `--bg` 派發 → 用盡 → /at reset 後 resume |

關鍵決策（記錄）：
- **agent-view 為推薦 substrate**——user-away（「我去洗澡了」）+ 多命令 loop 是 deep-work 核心場景，agent-view 的 supervisor（survive terminal close / peek / attach）是原生解。`-p` 降為「要 stdout 的一次性場景」。
- **與 /at、/handoff 分工**（避免混淆）：agent-view = 本機背景長程（同 session）；/at = 跨 session 接續（reset 後）；/handoff = 跨 session/repo/provider 交接。三者正交可組合。
- **agent-view 寫作深度**：定位 + 三入口表 + 監控一句。**不寫快捷鍵/狀態圖示**（研究預覽 v2.1.139+，介面可能 drift），全交官方文檔。

#### 層 3：命令索引連動

`commands/CLAUDE.md` 的 `/deep-work` description（若現況「用戶離開時的自主實作引擎」仍準確則不動；dispatch 定位若變則同步一句）。

### 驗證策略（docs mode）

- rg 残留：`rg "dispatch graph|agent-view|claude agents|--bg|/at 接續" commands/deep-work.md` 命中新增層。
- 跨檔一致：dispatch graph 的 /build 委派引用 S1 補強後的 Phase 4；/at 語意與 `commands/at.md` 一致；substrate 與 `agent-workflow` skill（S3）不重複（skill 只指向 /deep-work）。
- `/consistency commands/deep-work.md` 單檔自洽。

---

## S3 — agent-workflow skill 收斂參考層

### Context

`skills/agent-workflow/SKILL.md`「平行模式選擇」表（`:19-25`）現列 Agent tool+worktree / Writer-Reviewer / Agent Teams / Auto mode——**漏 agent-view 與 dynamic workflows 兩個官方首類**，且 Auto mode（權限模式）被誤列為並行方法。同時 6+ review 命令已用 Workflow 路徑，正典 skill 卻不提。

**受眾**：agents 比較文檔 → `agent-workflow` skill（參考層，唯一屬於參考層的）。

**依賴錨點**：`skills/agent-workflow/SKILL.md:19-25`（四模式表）、`:110-114`（Agent Teams 段）、`:118-128`（Auto Mode 段）。

### 修改要點

1. **四方法表對齊官方**：subagents / agent-view / agent-teams / dynamic-workflows 四首類。Writer-Reviewer 降為「pattern（非 surface）」註記；Auto mode 移出「並行方法」，改列「autonomy enabler」（與並行方法分組）。
2. **agent-view 段**：定位 + 何時用（獨立任務、user-away 監控）+ 一句「執行細節見 `/deep-work` substrate layer」。不重複 /deep-work 的入口表。
3. **dynamic workflows 段**：定位 + 何時用（大規模、對抗驗證）+ 一句「review 命令的 Workflow 編排見 `workflow-review-pattern.md`」。不重複 schema。
4. **指向執行落點**：明示 agent-view/workflows 的執行細節在 `/deep-work`（substrate）與 `/build` Phase 4（review workflow），skill 只做「選擇哪個方法」的參考，避免雙源 drift。

### 驗證策略（docs mode）

- rg 残留：`rg "agent-view|dynamic workflow|claude agents" skills/agent-workflow/SKILL.md` 命中。
- 跨檔一致：與 /deep-work（S2）/build（S1）的 agent-view/workflow 用語一致；不重複 `workflow-review-pattern.md` 的 schema/兩階段。
- `/consistency skills/agent-workflow/SKILL.md`。

---

## S4 — agents/README.md frontmatter 補齊

### Context

`agents/README.md:11-19` frontmatter 表只列 `name`/`description`/`model`/`tools`。官方 subagent frontmatter 另有 `isolation: worktree`（agent-view 文檔明列）與 `permissionMode`。與上輪 `skills/CLAUDE.md` frontmatter 收斂同類缺口。

**依賴錨點**：`agents/README.md:11-19`（frontmatter 範例）、`:34-39`（設計原則）。

### 修改要點

1. frontmatter 表補 `isolation: worktree`（何時：寫檔/平行實作 agent；read-only verify agent 不設）+ `permissionMode`（何時：鎖定 agent 權限模式）。
2. 補決策原則一句：`model: inherit` 是為讓 spawner 套 model-routing 相對降級（frontmatter 無法表達相對規則）；agent-view 直派會跑 session model（揭露，非 bug）。

### 驗證策略（docs mode）

- rg 残留：`rg "isolation|permissionMode" agents/README.md` 命中。
- 跨檔一致：與 `skills/CLAUDE.md` frontmatter 表的欄位語意一致（agents 版不重複 skill 專屬欄位如 paths/disable-model-invocation）。
- `/consistency agents/README.md`。

---

## 收尾步驟

1. **導航文檔 `/consistency` 閘門**（大型/中型）：對 S1/S2/S3/S4 各自改過的檔跑 `/consistency <doc>`，🔴/🟡 inconsistency 修正後才算收尾。
2. **commands/CLAUDE.md 命令索引**：S2 若改 /deep-work dispatch 定位，同步索引 description（若無變則跳過）。
3. **無 Capabilities / Kanban**（元專案，docs mode 跳過）。
4. **/audit-test**：N/A（無測試變更）。
