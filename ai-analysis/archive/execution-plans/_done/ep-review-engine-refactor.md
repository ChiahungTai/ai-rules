> **ep_type**: implementation
> **mode**: docs（全為 `commands/`、`skills/` 下的 `.md`，無 `.py` callable 符號）

# EP — 重構 review 命令家族：新增 review-engine skill

## 實作總覽

同一個「審查」動作跨多單位（`/ep-review`、`/code-review`、`/audit-test`、execution-plan EP Review Cycle，**含 build 的 Agent Review**）重複實作且不一致（drift）。本 EP 套用 Clean Architecture：新增 `review-engine` skill 作為 **domain 層**（通用審查邏輯唯一真相源），命令退化為**薄 adapter**（宣告 標的 + profile + 產出，委託 review-engine / workflow-review-pattern），消除 drift。

**已確認設計決策**（深層思考 + 查證結論，不重新討論）：
1. 新增 review-engine skill（domain 層）
2. 各 profile 自訂維度 — review-engine 只管 how to review，不管 what to check
3. review-engine 只收「所有 review 命令都通用」的邏輯；產出動作/stance 留各 adapter
4. 信心水準統一 — `confirmed/evidence-based/inferred` 收進 review-engine，所有命令 finding 都標

**收進 review-engine 的判準**：所有 review 命令都適用（只適用部分命令的不收）。

**EP Review + judge-review 後修正**（F1/F6/F11/F12 等，見末段 EP Review Findings）：
- 審查模式**判定規則**（`effort=ultracode/xhigh 且 max-agents>1 → Workflow`）收 review-engine（消 DRY — build/code-review/ep-review 三處重複定義）；schema/腳本/Workflow 執行留 `workflow-review-pattern.md`（不重複）
- 多層驗證「audit→judge→followup 三層」具體鏈留 audit-test（test 講最細）；review-engine 放通用 why（review→judge→驗收 各層都可能錯）
- **補 ripple**：`build.md`（自帶審查模式判定，真 drift）、`judge-review.md`（自我否證義務）。`deep-work.md` 經 judge-review 查證**降級** —— 只薄委託 agent-review-cycle，不自帶判定，非 drift

---

## UC 盤點

### 受影響命令/skill 清單（元專案無 Capabilities 表格，改掃此）

| 單位 | 角色 | 變更 |
|------|------|------|
| `skills/review-engine/` | **新增** domain skill | 新建 |
| `skills/code-review-and-quality/` | 六軸 + 通用邏輯混合 | 重構：留六軸，通用邏輯移走，嚴重度 5→3 級（Nit/FYI 僅此檔離群，刪 2 行） |
| `commands/ep-review.md` | 審 EP（獨立入口） | 改薄：委託 review-engine；成為「審 EP profile」定義源 |
| `commands/code-review.md` | 審 code | 改薄：委託 review-engine（通用 + 模式判定規則）；六軸/commit/Lint/語音保留 |
| `commands/audit-test.md` | 審 test（read-only 偵測器） | 改薄：委託 review-engine；落盤/健康度/反思/偵測器 stance/三層驗證鏈保留 |
| `commands/execution-plan.md` | 內建 EP Review Cycle | 收斂：刪自帶四維度，引用「審 EP profile」（根治內建 vs 獨立 drift） |
| `commands/build.md` | 段落實作 + 內建 Agent Review | ripple（F6）：`151-166` 自帶審查模式判定 → 判定規則改引用 review-engine |
| `commands/deep-work.md` | 自主實作 + Agent Review | **降級**（judge-review 查證）：只薄委託 agent-review-cycle，**不自帶**審查模式判定 → 非 drift，僅確認委託有效 |
| `commands/judge-review.md` | 評估審查建議 | ripple（F12）：`87-103` 自我否證義務 → 改引用 review-engine |
| `commands/claude/_common/workflow-review-pattern.md` | Workflow 執行協調 + Finding Record | 邊界釐清：保留 schema/腳本/Workflow 執行（F1）；嚴重度定義源標 review-engine |
| `commands/deliverable-review.md` | 人 viewport 交付 | ripple：LSP 輔助引用改指向 review-engine |
| `commands/claude/_common/agent-review-cycle.md` | build 的 Agent Review 範本 | ripple：評估引用點 |
| `skills/using-agent-skills/` | skill routing | ripple：「Five-axis」誤寫修正 + review-engine 入 routing |
| `commands/CLAUDE.md` / `skills/CLAUDE.md` | 索引 | 同步（review-engine 入 skill 索引；命令索引確認無誤述） |

### Backlog 關聯

- 元專案 `.kanban/` 存在。EP 產出後建一張 Backlog 卡追蹤本 EP（能力描述：review 命令家族架構重構 — review-engine domain 抽出）。

### SYSTEM-MAP 影響

- 元專案無 SYSTEM-MAP.md → 跳過（正當跳過：元專案不適用 life-cycle 狀態追蹤）。

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| review 命令家族通用審查邏輯（嚴重度/信心水準/自證/LSP/模式判定規則）單一真相源 | 📋 | `skills/review-engine/SKILL.md` |

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為（文檔語境） | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 跑 `/code-review` | 審 uncommitted/branch | 嚴重度/自證/模式判定規則從 review-engine、Workflow 執行從 workflow-review-pattern、六軸從 code-review-and-quality，行為與改薄前一致 | 無 | review-engine |
| SM-2 | 跑 `/ep-review`（獨立，手動改 EP 後） | 手動改 EP | 與 execution-plan EP Review 用**同一「審 EP profile」**，兩條路徑結果一致（drift 根治） | 無 | review-engine |
| SM-3 | 跑 `/audit-test` | 審 test | 信心水準定義從 review-engine；落盤/健康度/反思/偵測器 stance/三層驗證鏈保留不變 | 無 | review-engine |
| SM-4 | finding 信心水準標註 | 任何 review 命令產 finding | 所有命令 finding 都標 confirmed/evidence-based/inferred；Critical 禁止 inferred | 無 | review-engine |
| SM-5 | review-engine / workflow-review-pattern 不存在或 link 失效 | 各命令 markdown link 指向它們 | 導航斷裂 → 機械驗證：`fd review-engine skills/` + `rg "review-engine\|workflow-review-pattern" commands/ skills/` 確認每個 link target 存在 | fd + rg 驗證 link target | — |
| SM-6 | 嚴重度定義重複 | 改薄後各檔案 | 嚴重度定義**只在** review-engine；其他檔案引用不重複定義（rg 殘留 = 0） | rg 殘留掃描 | review-engine |
| SM-7 | build 仍自帶模式判定（F6 回歸） | 跑 /build 的 Agent Review | 模式判定規則引用 review-engine，不自帶 if/else | `rg "選擇審查模式\|effort=ultracode.*workflow" commands/build.md` 殘留 = 0 | review-engine |

---

## 段落劃分原則

- **依賴順序**：S1（root）→ S2/S3/S4/S5（並行，只依賴 S1）→ S6（依賴 S3）→ S7（收尾，依賴全部，含 build/judge-review ripple）
- **語義顯式化**：review-engine 是嚴重度/信心水準/自證/LSP/**審查模式判定規則**的唯一真相源；Workflow 執行（schema/腳本）的唯一真相源是 `workflow-review-pattern.md`（判定規則 → 決定讀哪個 schema，是依賴方向非耦合）；「審 EP profile」由 ep-review（S3）定義、execution-plan（S6）引用
- **docs mode**：段落用「修改要點」取代 pseudo code；驗證改文檔驗證（rg 殘留 / 跨檔一致 / `/consistency` / 導航有效性）

---

## S1：新增 review-engine skill（domain 層）

### Context

本 EP 的根段落，所有其他段依賴。review-engine 承載「所有 review 命令都通用」的審查邏輯，收攏自 audit-test（信心水準 + 誠信）、code-review-and-quality（嚴重度 + LSP + 自證）、judge-review（自我否證義務）、build/code-review/ep-review（審查模式判定規則）。

**UC 引用**：實作「review 命令家族通用審查邏輯單一真相源」（UC 盤點 → 新增 UC）。

**邊界（關鍵 — 避免製造新 drift；F1/F11 judge-review 修正後）**：

| vs | review-engine（本 skill） | 對方 |
|----|--------------------------|------|
| `workflow-review-pattern.md`（_common） | **方法論 + 判定規則**：嚴重度的意義、信心水準、自證、為何 Writer/Reviewer 分離、**審查模式判定規則**（effort/max-agents → 模式）、為何多層驗證 | **Workflow 執行**：DimensionVerdict schema、兩階段協調腳本、Finding Record 持久化格式（判定規則 → 決定讀哪個 schema，依賴方向非耦合） |
| `agent-review-cycle.md`（_common） | （不重疊） | **Agent Tool 模式執行範本**（2-perspective） |
| architecture-thinking / viewport（維度 skills） | **依賴**它們（審查需要視角/機械） | 提供架構視角/機械能力（不改） |
| audit-test（三層驗證鏈） | 通用 why（review→judge→驗收 各層都可能錯） | **具體 audit→judge→followup 三層鏈**的細節（test 講最細），留 audit-test |

**為何審查模式判定規則收 review-engine（F1 judge-review 修正）**：判定**規則**（`effort=ultracode/xhigh 且 max-agents>1 → Workflow`）與 schema/腳本**可分** —— 規則是決策，schema 是資料結構，腳本是執行；「判定完讀 schema」是依賴方向（判定→schema）非耦合。查證 build/code-review/ep-review 三處**重複定義**同一條判定規則（DRY 問題）→ 收 review-engine 消重複。review-engine **不重複** schema/腳本（指向 workflow-review-pattern）。agent 原 F1「判定整個留 workflow-review-pattern」的「強耦合」論證不成立（見 EP Review Findings F1 決策）。

**不裝**（留各處）：維度定義、產出動作（回寫 EP / commit / 報告）、stance（audit 的「偵測器非判官」）、Workflow schema/腳本（留 workflow-review-pattern）、三層驗證具體鏈細節（留 audit-test）。

**語義約束**：與 S2-S7 共享「review-engine 是嚴重度/信心水準/自證/LSP/模式判定規則的唯一真相源；Workflow schema/腳本在 workflow-review-pattern」。

**成功標準**：review-engine 存在且涵蓋 6 個通用邏輯區塊（定位 / 嚴重度 / 信心水準 / 自證+誠信+LSP / 模式判定規則+分離 why / 多層驗證 why）；各命令能以 markdown link 引用它（skill 不支援 `@` transclusion）。

### 修改要點

建 `skills/review-engine/SKILL.md`，含：

1. **frontmatter**：`name: review-engine`；`description` 觸發詞涵蓋（review 嚴重度 / 信心水準 / 審查者自證 / LSP 查證 / 審查模式判定 / Writer Reviewer 分離 / Critical Important Suggestion）
2. **定位段**：review 命令家族 domain 層，通用審查邏輯唯一真相源；明列「收進判準 = 所有 review 命令都適用」+ 邊界宣告（vs workflow-review-pattern / agent-review-cycle / 維度 skills / audit-test 三層鏈）
3. **嚴重度框架**：統一 3 級（Critical / Important / Suggestion）— 每級定義 + author action。**明標此為唯一定義源**，workflow-review-pattern schema（已是 3 級 enum）/ 各命令引用此。附註：Nit/FYI 移除理由（**僅 code-review-and-quality 一處離群**；workflow schema 強制 3 級 enum，Nit/FYI 在 Workflow 模式無法表達，是死定義 — F8）
4. **信心水準**：`confirmed`（已查證完整 code/body）/ `evidence-based`（有 file:line + rg/LSP 結果未深驗）/ `inferred`（推理未實證）。規則：**Critical 必須 confirmed 或 evidence-based，禁止 inferred**（從 audit-test 誠信約束收攏）
5. **審查者自證 / 誠信**：通用原則 — 每個 claim 必須查證、無法查證標 `unverified`、findings 非定論（可被下層推翻）、**對外部行為判斷必須實證**（通用原則，F3）。從 audit-test 誠信約束 + code-review-and-quality Reviewer Self-Verification + judge-review 自我否證義務收攏**通用部分**。明標不收：audit-test「偵測器非判官 + read-only」stance（留 audit-test）、audit-test「套件行為 → 寫 demo 跑一次」（test 特化方法，留 audit-test；通用層只放「對外部行為判斷必須實證」原則）
6. **LSP 查證方法**：符號 → LSP（findReferences / goToDefinition / workspaceSymbol / incomingCalls / outgoingCalls）、文字/註解/config → rg、檔案 → fd。**自我否證義務**：找不到 ≠ 不存在（換工具/pattern/位置，三工具都 0 hits 只能標「查證失敗」）。來源：code-review-and-quality LSP-Assisted Review + **judge-review.md:87-103 自我否證義務**（F12）+ `lsp-navigation` rule
7. **審查模式判定規則 + 分離 why + 多層驗證 why**（F1/F11 修正）：
   - **審查模式判定規則**：`effort=ultracode/xhigh 且 max-agents>1 → Workflow`；`max-agents=1 但 ultracode → Agent Tool`；`effort<ultracode → Main LLM`（消 build/code-review/ep-review 三處 DRY）。**Workflow 執行細節指向** workflow-review-pattern.md（schema/腳本），**Agent 執行指向** agent-review-cycle.md —— 本檔不重複 schema/腳本
   - 為何 Writer/Reviewer 分離（避免主 LLM 審自己；acceptance-evidence 證據獨立性）
   - 為何多層驗證（findings 可經 judge-review 評估 / followup-review 驗收，各層都可能錯）— **具體 audit→judge→followup 三層鏈細節指向** audit-test（test 講最細）

### 驗證策略（docs mode）

- `/consistency` 對 SKILL.md（自洽、無矛盾、章節連續）
- `rg "Critical|Important|Suggestion"` 確認 3 級定義**只在** review-engine
- `rg "effort.*ultracode.*max-agents|→ Workflow"` 確認**判定規則**只在 review-engine（build/code-review/ep-review 改引用）
- 確認 schema/腳本**不在** review-engine（在 workflow-review-pattern）
- 導航有效性：SKILL.md 內 markdown link（指向 architecture-thinking/viewport/workflow-review-pattern/agent-review-cycle/lsp-navigation/audit-test）皆存在

---

## S2：code-review-and-quality SKILL 重構

### Context

依賴 S1。現況混合 code 六軸專屬 + 通用審查邏輯（Review Process / 嚴重度 / LSP-Assisted Review / Reviewer Self-Verification / Multi-Model / Honesty）。重構後留 code 六軸，通用邏輯移走引用 review-engine。

**ripple**（F7/NF4 修正）：code-review-and-quality 被約 **17 處引用**（跨 9 個檔案；using-agent-skills 5、code-review 3、execution-plan 2、ep-review 2、餘各 1）。多數引用「六軸方法論」（code-review / execution-plan / agent-review-cycle），改的是嚴重度 + 通用邏輯，這些引用點**多半不需改**（引用六軸非嚴重度細節）。需檢查的引用點見 S7。

**語義約束**：與 S1 共享「review-engine 是通用邏輯真相源」；code-review-and-quality 聚焦 code 六軸。

**成功標準**：SKILL 只剩 code 六軸專屬 + 對 review-engine 的引用；嚴重度 3 級。

### 修改要點

- **嚴重度表**（現 78-82 行）：5 級 → 3 級，刪 Nit/FYI。**誠實標註（F8）**：Nit/FYI 僅本檔一處離群（其餘命令 code-review/audit-test/ep-review 早是 3 級，workflow schema 也強制 3 級），刪 2 行即完成「統一」；非大工程。改為引用 review-engine 的定義，本檔只保留「分類 findings 時用 review-engine 的三級」指引
- **Reviewer Self-Verification**（119-128 行）+ **LSP-Assisted Review**（108-117 行）：移到 review-engine（S1 已收攏），本檔改 markdown link 引用
- **Multi-Model Review Pattern**（130-136 行）：通用（不同 model 不同 blind spot）→ 移 review-engine
- **Honesty in Review**（99-106 行）：通用 → 移 review-engine
- **Dead Code Hygiene**（88-97 行）：偏 code 重構場景，**保留**本檔（code 專屬）
- **Review Process**（59-86 行）：Step 1-5 的通用流程部分標「通用審查流程見 review-engine」；code 專屬的「六軸審查順序」保留
- **保留**：六軸定義（Correctness / Readability & Simplicity / Architecture / Security / Performance / Capability Coverage）+ Security/Performance 引用子 skill
- **頂部加引用**：review-engine（嚴重度/自證/LSP/多層驗證通用邏輯真相源）

### 驗證策略

- `rg` 殘留：通用邏輯（嚴重度 5 級、Reviewer Self-Verification、LSP-Assisted、Multi-Model、Honesty）不該還在本檔重複定義
- 跨檔一致：引用點仍指向有效內容（六軸仍在）
- `/consistency`

---

## S3：ep-review 改薄（成為「審 EP profile」定義源）

### Context

依賴 S1。現況：F1-F5 五維度 + 深層思考 + 回寫原則 + 技術約束 + 邊界（Always/Ask First/Never）+ 報告格式。改薄後成為**「審 EP profile」的定義源**（維度集），S6 execution-plan 引用它，根治兩套維度 drift。

**關鍵設計**：合併後的「審 EP profile」須包含兩者優點 — 架構視角（分層依賴 / bounded context，來自 execution-plan）+ 完整性 / 合規 / 場景（來自 ep-review F1-F5），且**零失落** execution-plan 的「兜底路徑驗證」複合維度（F2）。

**語義約束**：與 S6 共享「審 EP profile 維度集」（ep-review 定義，execution-plan 引用）。

**成功標準**：ep-review 委託 review-engine 通用邏輯；F1-F5 補上架構視角 + 兜底拆解；回寫 EP 保留。

### 修改要點

- **刪**：嚴重度定義（委託 review-engine）、審查模式判定規則（委託 review-engine，F1；保留 ep-review 特有的「直接審查模式 = Workflow off 時單一 Explore agent」描述）
- **「審 EP profile」維度映射表**（F2，確保合併零失落）：

| execution-plan 原維度 | 合併後歸屬 |
|----------------------|-----------|
| ①分層依賴（domain←use case←adapter←infra 向內？循環？） | F3 一致性 補架構視角 |
| ②bounded context（跨域 `_private`？） | F3 一致性 補架構視角 |
| ③use case 覆蓋（EP 撐得起 use case？） | F5 場景覆蓋（對齊） |
| ④兜底路徑驗證（複合） | 拆解 → 實作落差預見（**新增子項**，從「EP 能否被 build 機械執行」角度）+ 語義約束 drift（F3）+ **依賴錨點 drift（F3）**（NF2 補列）+ Rules 合規（F2）+ 遺漏（F4）+ 內部一致性（F3） |

- **F3 一致性**：依上表補架構視角（分層依賴 + bounded context）+ 語義約束 drift 檢查，引用 architecture-thinking/viewport
- **新增「實作落差預見」**：execution-plan 兜底④特有視角（EP pseudo code 看起來對，接起來才發現邊界/副作用）— 併入深層思考或 F3
- **委託 Skills 段**：加 review-engine + workflow-review-pattern
- **保留**：回寫原則（EP 專屬產出 — EP 是 build 唯一真相來源）、深層思考、Always/Ask First/Never 邊界段、五維度本體（補架構 + 兜底拆解後）

### 驗證策略

- `rg` 殘留：嚴重度/模式判定規則不該還在本檔
- 與 execution-plan EP Review 維度一致（S6 協調後兩邊指向同一 profile）；**逐項核對映射表無失落**
- `/consistency`

---

## S4：code-review 改薄

### Context

依賴 **S1**（F5 修正：只需 S1。六軸定義 S2 保留不移除，S4 引用 review-engine 非依賴 code-review-and-quality 改後狀態，可與 S2 並行）。現況：審查範圍 + Lint 預檢 + 審查模式（A/B/C）+ 六軸 + axis 3 + 深層思考 + POC/Demo + 輸出 + Finding 呈現 + commit message + 語音。

**語義約束**：與 S1/S2 共享「通用邏輯在 review-engine，模式判定規則在 review-engine，六軸在 code-review-and-quality」。

**成功標準**：委託 review-engine 通用邏輯 + 模式判定規則；六軸/commit/Lint/語音保留。

### 修改要點

- **刪**：審查模式 A/B/C 的**判定規則**（委託 **review-engine**，F1；保留「本命令啟用六軸」的宣告 + 模式確認印出格式）
- **刪**：嚴重度三級定義（100 行附近深層思考段的嚴重度內容委託 review-engine；保留「分三級輸出」呈現指引，引用 review-engine）
- **深層思考段**（117-124 行）：審查者自證 → 委託 review-engine；保留「讀相關 code 確認為什麼這樣改」code 專屬部分
- **保留**：六軸（引用 code-review-and-quality）、axis 3 architecture-viewport 接線、Lint 預檢、POC/Demo 影響檢查、commit message 產生、語音、Capability Coverage
- **委託 Skills 段**：加 review-engine

### 驗證策略

- `rg` 殘留：模式判定規則/嚴重度定義不該還在本檔
- 六軸仍指向 code-review-and-quality
- `/consistency`

---

## S5：audit-test 改薄

### Context

依賴 S1。現況：六角度 + 嚴重度 + 信心水準 + 誠信約束（4 條）+ 落盤 + 健康度 + 反思閉環 + 執行流程。

**關鍵**：信心水準定義源移到 review-engine（S1），audit-test 引用；「偵測器非判官 + read-only」stance 與「audit→judge→followup 三層驗證鏈細節」是 audit-test 專屬（F11），**不收**。

**語義約束**：與 S1 共享「信心水準定義源在 review-engine」；audit-test 保留 test 專屬 stance + 三層鏈細節。

**成功標準**：委託 review-engine 通用邏輯；落盤/健康度/反思/偵測器 stance/三層鏈保留。

### 修改要點

- **刪**：嚴重度定義（委託）、信心水準定義（377-396 行 → 移 review-engine，本檔引用）、誠信約束的通用部分（#1 信心水準標示、#3 輸出格式 → 移 review-engine）
- **保留**：六角度維度（test profile）、落盤策略（長任務 test 專屬）、健康度計算（test 專屬）、反思閉環（test 專屬）、**「偵測器非判官」read-only stance**（audit-test 專屬，明標「非通用」）、**audit→judge→followup 三層驗證鏈細節**（F11，test 講最細，留本檔；review-engine 只放通用 why）、誠信約束 #2 套件行為實證（test 特化方法，F3，留本檔）
- **stance 釐清段**：明標「audit-test 是 read-only 偵測器（只產 findings 不下判）；review-engine 的通用誠信是『findings 非定論』，不含『不下判』— code-review/ep-review 要下判（給結論/commit/回寫），適用通用誠信但不適用偵測器 stance」
- **委託 Skills 段**：加 review-engine

### 驗證策略

- `rg "confirmed|evidence-based|inferred"` 確認信心水準**定義**只在 review-engine（audit-test 僅引用 + 用於標註）
- `/consistency`

---

## S6：execution-plan EP Review Cycle 收斂（根治內建 vs 獨立 drift）

### Context

依賴 S1 + S3。**drift 核心**：execution-plan 內建四維度（分層依賴 / bounded context / use case 覆蓋 / 兜底），ep-review 用 F1-F5，兩套並存。收斂：execution-plan EP Review 不自帶維度定義，引用「審 EP profile」（S3 ep-review 定義，含兜底拆解）。

**語義約束**：與 S3 共享「審 EP profile 維度集」（ep-review 定義源，execution-plan 引用，單一真相源）。

**成功標準**：execution-plan 無自帶維度定義；與 ep-review 指向同一 profile。

### 修改要點

- **Step 2 四維度表**（248-253 行）：刪自帶定義，改「審 EP profile 見 [/ep-review](./ep-review.md)（S3），含架構視角（分層/bounded context）+ 完整性 + 場景 + 兜底拆解（見 ep-review 維度映射表）」。top-down 審查順序（先結構後正確性）保留
- **agent prompt 引用**（265 行）：architecture-thinking + architecture-viewport **保留**（維度知識）+ **加 review-engine**（嚴重度/自證/模式判定規則）+ code-review-and-quality（方法論）
- **保留**：Step 1 模型偵測、Step 3 平行 spawn、judge-review 接線（286 行）、Apply Changes（290 行）、單一 Agent Fallback（270 行）
- **#B12 註解**（268 行）：更新反映 review-engine（「EP review agent 引用 review-engine（通用 why + 模式判定規則）+ workflow-review-pattern（Workflow 執行 schema/腳本）+ architecture-thinking/viewport（維度）+ code-review-and-quality（方法論）」）

### 驗證策略

- `rg "分層依賴|bounded context|use case 覆蓋"` 確認 execution-plan **不再自帶**這些維度定義（改為引用 ep-review）
- 與 ep-review（S3）維度一致 — 兩邊描述同一 profile
- `/consistency`

---

## S7：索引同步 + ripple 修補（收尾）

### Context

依賴 S1-S6。處理 ripple（code-review-and-quality 約 17 處引用 + build/judge-review + 新增 review-engine 索引）。

**成功標準**：所有 markdown link 有效；索引含 review-engine；無重複定義殘留；build/judge-review ripple 完成。

### 修改要點

- **`skills/CLAUDE.md` 索引**：「品質與審查」群組新增 `review-engine`；`code-review-and-quality` description 更新（移除通用邏輯描述，聚焦「code 六軸審查」）
- **`commands/CLAUDE.md` 命令索引**：review-engine 是 **skill 非 command**，不入命令索引；確認 ep-review/code-review/audit-test/execution-plan/build description 無誤述（F14）
- **ripple 引用點**：
  - **`build.md:151-166`（F6）**：自帶審查模式判定（A. Workflow / B. Agent Tool）+ `{confirmed, stats}` 交接 → 判定規則改引用 review-engine；Workflow 執行仍引用 workflow-review-pattern；Agent Review 本體已正確引用 agent-review-cycle
  - **`deep-work.md`（F6 judge-review 降級）**：查證僅薄委託 agent-review-cycle（`96-106`），**不自帶**審查模式判定 → 非 drift，**僅確認委託仍有效**，不改判定邏輯
  - **`judge-review.md:87-103`（F12）**：自我否證義務 → 改引用 review-engine（S1 #6 已標此為來源）
  - `deliverable-review.md:22`（LSP 輔助引用 code-review-and-quality）→ LSP 查證已移 review-engine，改指向 review-engine
  - `agent-review-cycle.md:47`（方法論引用 code-review-and-quality）→ 六軸方法論仍在 code-review-and-quality；若隱含自證/LSP，加引用 review-engine
  - `using-agent-skills/SKILL.md`：line 168 "Five-axis review" → "six-axis"（誤寫）；line 129 序列範例 + line 30 決策樹 + line 145/151 流程 → review-engine 入 routing（F7：原漏列 line 129）
- **跨檔一致性掃描**：`rg "Critical|Important|Suggestion"` 嚴重度定義只在 review-engine；`rg "confirmed|evidence-based|inferred"` 信心水準定義只在 review-engine；`rg "effort.*ultracode.*max-agents"` 模式判定規則只在 review-engine

### 驗證策略

- `rg` 殘留：全專案無重複的嚴重度/信心水準/模式判定規則**定義**（引用不算）
- `rg "選擇審查模式|effort=ultracode.*workflow=true"` 確認 build.md 不再自帶判定（F6 回歸防護，SM-7）
- 所有新增/修改的 markdown link 有效（`fd`/`rg` 確認指向檔案存在）
- `/consistency` 對 review-engine + 三個改薄命令 + build
- 導航有效性：`fd` 確認引用路徑存在

---

## 整合策略

- **依賴順序**：S1 →（S2, S3, S4, S5 並行）→ S6 → S7
- S2/S3/S4/S5 只依賴 S1，可 `/build --max-agents` 並行
- **整合驗證**（S7 後）：全專案 `rg` 確認（a）嚴重度定義單一源、（b）信心水準定義單一源、（c）模式判定規則單一源（review-engine）、（d）Workflow schema/腳本單一源（workflow-review-pattern）、（e）「審 EP profile」ep-review/execution-plan 一致、（f）所有 markdown link 有效、（g）build 不自帶模式判定

---

## 收尾步驟（docs mode）

1. **受影響命令/rules 行為已反映**：ep-review/code-review/audit-test/execution-plan/build 改薄後行為一致（嚴重度/自證/模式判定規則統一）
2. **索引同步**：`skills/CLAUDE.md` 含 review-engine；`commands/CLAUDE.md` 確認各命令描述無誤述（review-engine 非 command 不入命令索引）
3. **跳過**（docs mode + 元專案）：Capabilities 表格（元專案無）、SYSTEM-MAP（無）、`/audit-test`（無 `.py` 測試）、mypy/ruff/pytest（無 `.py`）
4. **.kanban**：建 Backlog 卡（大型變更）→ build 完搬 Done/

---

## EP Review Findings

EP Review Cycle（單一 Explore agent，glm-5.2）→ 獨立 `/judge-review` 對抗性重審（查證實際程式碼，不盲從 agent）。judge-review 修正 2 處盲從（F1 採納方式、F6 deep-work 誤判）。

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 決策 |
|----|--------|---------|------|------|------|
| F1 | 🟡 | S1 #7 / 邊界表 | 審查模式判定與 workflow-review-pattern schema/腳本強耦合 | ~~判定整個留 workflow-review-pattern~~ → **judge 修正**：判定**規則**收 review-engine（消 DRY），schema/腳本留 workflow-review-pattern（agent「強耦合」論證不成立：規則/schema/腳本可分，是依賴方向非耦合） | ✅ 修正採納 |
| F2 | 🟡 | S3 | 合併維度會失落 execution-plan「兜底路徑驗證」複合維度 | S3 補維度映射表確保零失落 | ✅ 採納 |
| F3 | 💡 | S1 #5 / S5 | audit-test 誠信 #2「套件行為實證」是 test 特化 | 區分通用「對外部行為判斷必須實證」vs test 特化「寫 demo」 | ✅ 採納 |
| F4 | 🟢 | 段落劃分 | 依賴順序正確，S6 依賴 S3 合理 | — | confirmed |
| F5 | 💡 | S4 | 依賴宣告 S1+S2 但只需 S1 | 改依賴 S1 | ✅ 採納 |
| F6 | 🔴 | UC / S7 | build.md + deep-work.md 自帶審查模式選擇 | **judge 修正**：build.md ✅ 真 drift（自帶 effort 判定 + A/B 分支）；deep-work.md ❌ 誤判（rg 證實不在判定散佈清單，僅薄委託 agent-review-cycle）→ 降級為確認委託 | ✅ 部分採納（deep-work 降級） |
| F7 | 🟡 | S2 / S7 | 「9 處引用」數字有誤（實際約 15 處），漏列 using-agent-skills:129 | 修正數字 + 補 line 129 | ✅ 採納 |
| F8 | 🟡 | S1 #3 / S2 | 嚴重度 5→3 級實際只動 code-review-and-quality 一處離群 | 誠實標註工作量（刪 2 行非大工程） | ✅ 採納 |
| F9 | 🟢 | S7 | deliverable-review.md:22 LSP 輔助引用如所述 | — | confirmed |
| F10 | 🟢 | S7 | agent-review-cycle.md:47 方法論引用如所述 | — | confirmed |
| F11 | 🟡 | S1 #8 | 多層驗證「audit→judge→followup 三層」是 audit-test 專屬 | 三層鏈細節留 audit-test，review-engine 放通用 why（agent「三層是 test 專屬」論證有瑕疵 — rg 證實多層概念跨命令 — 但「通用 why vs 具體鏈分開」結論正確） | ✅ 採納 |
| F12 | 🟡 | S1 #6 / S7 | judge-review.md:87-103 自我否證義務與 review-engine #6 重疊 | 補 judge-review 為 ripple | ✅ 採納 |
| F13 | 💡 | SM-5 | checkpoint 標「無」過於寬鬆 | 改機械驗證（fd + rg link target） | ✅ 採納 |
| F14 | 💡 | 收尾 #2 | 措辭暗示 commands/CLAUDE.md 也加 review-engine（它是 skill 非 command） | 修正措辭 | ✅ 採納 |

**judge-review 結論**：獨立重審抓出 2 處盲從 —— F1（agent「強耦合」論證不成立，判定規則該收 review-engine 消 DRY，非整個移出）、F6（deep-work.md 誤判，rg 證實僅薄委託非自帶判定）。其餘查證屬實維持採納。EP 經兩輪審查（EP Review + judge-review）後可進入 build。

### Followup Review（NF1-NF4）處置

第三輪：另一個 `/ep-review` 產 NF1-NF4 → followup-review 驗收 → judge-review 評估 followup-review 處置。

| ID | 嚴重度 | 來源 | 問題 | 決策 |
|----|--------|------|------|------|
| NF1 | 🔴 | /ep-review | deep-work.md 事實錯誤（宣稱 EP 自帶模式選擇） | ❌ **false positive** — EP 早已在 F6 正確降級；ep-review agent 重複 F6 誤判（未逐欄讀 F6 決策欄、虛構 SM-7 guard、自己 rg 證據與結論矛盾）。撤除 gate，EP 不動 |
| NF2 | 🟡 | /ep-review | S3 映射表漏「依賴錨點 drift」 | ✅ **採納（補列）** — 不盲從 followup-review 的 decline；映射表確實漏列，違反 S3「零失落」承諾；補「依賴錨點 drift → F3 一致性」（行號修正 L253 非 L283）。**已回寫 S3** |
| NF3 | 🟡 | /ep-review | S1#3 嚴重度 enum 真相源歧義 | ❌ decline — 已標「明標此為唯一定義源」，歧義低影響 |
| NF4 | 🟡 | /ep-review | 引用數 9→15 有誤 | ✅ 採納 — 實際 17 跨 9 檔；判斷（多數引用六軸非嚴重度）不變。**已回寫 S2/S7** |

**第三輪 judge 結論**：NF1 false positive（ep-review 重複 F6 盲點，正是本 EP 欲收攏的「審查者自證」反向案例）→ 撤除 build gate。NF2 補列 + NF4 數字已回寫 EP。NF3 decline。**EP 現狀可進入 build**。NF1 揭示的 ep-review 品質問題（宣稱 EP 內容有誤需強制逐欄引用原文）為 type-2 設計改善，走 `/flow-feedback`，不阻塞本 EP。
