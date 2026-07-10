# EP-B: agent-workflow scope 邊界補強（委派哲學 + side-discovery）

> **ep_type**: implementation
> **mode**: docs（全 .md 變更，無 .py callable）
> **規模**: standard（跨 skill 概念，中型）
> **來源**: Fable 5 + Symphony gap analysis + Symphony elixir/WORKFLOW.md side-discovery pattern + ref-docs Ch19 AI Contract

## 實作總覽

`agent-workflow` 全篇偏**控制導向**（scope fence 防擴大 L84-92 / git diff 驗產出 / classifier 擋升級 / 逐項 gate），**缺 manager-delegate 連貫框架**——放手元素零散存在（autonomous-execution「不交半成品」L15、build.md「裁量權」L121 / context handoff L111-118、scope fence「創造性任務例外」L92）但從未 articulated 為連貫模型。兩個子能力，**均主要落 agent-workflow**（spawner / 委派者端）：

1. **side-discovery**（Symphony 洞見#6）：scope fence 負空間的 **redirect 通道**——agent 發現 scope 外 meaningful 改進 → 建 Backlog 卡（非擴大 scope、非丟棄）
2. **委派哲學**（Symphony 洞見#7）：連貫化既有放手碎片為 **delegate(goal+tools+context) → let go(within guardrails) → verify(outcome)** 模型

**核心設計原則**：
- **委派不是「純加放手」**——是連貫化既有碎片 + 平衡控制/放手（delegate+verify 非 delegate+trust）
- **委派 vs fence 非矛盾**——不同任務類型（機械 = fence / tight delegation，創造 = 放手 / loose delegation），同光譜兩端
- **借 Symphony 思想非載體**（.codex/skills/ → ai-rules skills/ 體系；linear_graphql 不適用 solo 無 Linear；guardrails flag 非必要，deep-work auto-mode gate 已等價）

---

## UC 盤點（docs mode）

### 受影響 skills/rules 清單

| 檔 | 段（行號） | 變更 | 段落 |
|---|---|---|---|
| `skills/agent-workflow/SKILL.md` | Scope Fence L84-92 | 後插「Side-Discovery redirect」子段 | S1 |
| `skills/agent-workflow/SKILL.md` | 任務分級 L52-60 後（新段） | 加「委派框架」段 | S2 |
| `skills/kanban-board/SKILL.md` | 卡片模板 L62-79 | **交叉引用**（建卡用，不重複模板） | S1 |
| `skills/autonomous-execution/SKILL.md` | 紅線 L32-62、不交半成品 L15 | **交叉引用**（委派放手底線） | S2 |
| `commands/build.md` | context handoff L111-118、裁量權 L119-128、scope-creep L103-107 | **交叉引用**（委派碎片已在此；不重述） | S2 |
| `ep-autonomous-execution-reliability.md`（EP-A） | false-done S2 | **交叉引用**（delegate→verify loop 下游） | S2 |

### Capabilities / kanban / SYSTEM-MAP
- 元專案無 Capabilities 表格 / SYSTEM-MAP → 跳過（正當，同 EP-A）
- 無對應 deferred card（side-discovery / 委派哲學無既有 deferred 記錄）

---

## Scenario Matrix（docs mode）

| # | 場景 | 觸發 | 預期行為（文檔語境，rg 驗證） | 對應 |
|---|---|---|---|---|
| SM-1 | agent 審查/實作發現 scope 外 meaningful 改進 | 發現 out-of-scope 觀察 | side-discovery redirect：建 Backlog 卡（title/desc/acceptance/related/blockedBy），非擴大、非丟棄 | S1 |
| SM-2 | 機械任務 agent 想順手改相鄰區塊 | scope fence 觸發 | fence 擋擴大 + side-discovery 建卡收斂（fence + redirect 共置） | S1 |
| SM-3 | 創造性任務委派（需判斷） | spawn impl agent | delegate(goal+tools+放手)，**非過度 fence**（scope fence L92 已排除創造性） | S2 |
| SM-4 | review 發現 scope-expanding 建議 | code-review finding | accept/defer/decline triage（借 Symphony land skill） | S1 |
| SM-5 | side-discovery 建卡氾濫風險 | agent 建大量低價值卡 | threshold（meaningful）+ batch（結束統一建）+ 人類 triage（每週回顧） | S1 |
| SM-6 | deep-work 半夜跑，agent 發現 scope 外改進 | 自主模式觸發 side-discovery | accept 降級為 defer（建 Backlog 卡 + completion report 標記待確認），不自主擴大 scope（外部 review B4） | S1 |

---

## 段落 0：全域研究摘要

### agent-workflow 現狀傾向（已查證）
- **全篇偏控制導向**：scope fence L84-92、並發控制 L38-50、任務分級 L52-60、classifier 阻擋 L128/L134、自檢 gate L156-183
- **放手元素零散未 articulated**：rules-reminder 注入 L164、build.md context handoff L111-118 + 裁量權 L121、autonomous-execution 不交半成品 L15、scope fence 創造性例外 L92
- **無 manager-delegate 連貫框架**

### gap 真實性（已查證）
- **委派哲學 gap：部分真實**——哲學缺席，但精神碎片存在（4 處）。真實 gap = 碎片未連貫 + 控制/放手平衡點未 articulated
- **side-discovery gap：真實且清晰**——收斂通道完全缺失。scope fence 預防擴大但無 redirect；build.md scope-creep 偵測但無 redirect；Symphony WORKFLOW.md L88-93/L283-287 有完整 pattern（file Backlog issue 五要素）

### Symphony pattern solo 適配（節錄）
- **核心適用**：side-discovery → file Backlog issue（solo = .kanban/Backlog/ 卡，五要素套 kanban-board 模板）、land scope-feedback triage（review 場景 accept/defer/decline）、manager-delegate（需提煉，本 EP）
- **部分適用**：.codex/skills/ 工具集（ai-rules 有 skills/ 但不教「配工具」——委派哲學補）、approval/sandbox（紅線/黃線對應）
- **不適用**：linear_graphql（solo 無 Linear；寫回路徑思想已被 collaboration-constraints 覆蓋）、guardrails flag（非必要，deep-work auto-mode gate 已等價）

### 落點建議（研究判定）
- **side-discovery → agent-workflow**（緊鄰 scope fence L84-92，single-source：fence 負空間必須共置，否則 fence 的 redirect 是死路）。卡片機制交叉引用 kanban-board（不重複模板）
- **委派哲學 → agent-workflow**（非 autonomous-execution：agent-workflow 是委派者/spawner 端，autonomous-execution 是被委派者/agent 端，正交）。交叉引用 autonomous-execution 紅線作放手底線

### 風險假設（R1-R6）
- R1 過度放手（半夜失控）→ delegate+verify 非 delegate+trust
- R2 過度控制（完不成交付）→ 創造性任務不加控制
- R3 side-discovery 建卡氾濫 → threshold + batch + 人類 triage
- R4 委派 ↔ EP-A recovery **互补**（delegate→verify loop）
- R5 委派 vs fence 表面張力 → 不同任務類型，同光譜兩端
- R6 docs-mode 機械強度上限 → 委派是判斷框架非機械閘門，verify 半邊機械性來自 build.md git diff

---

## 段落劃分原則

- **S1 side-discovery 先**：gap 真實清晰、scope fence 共置的自然延伸、具體可落地、de-risk
- **S2 委派哲學後**：上層框架、連貫化多處碎片、含 S1 引用（委派時 agent 發現 scope 外的 redirect）
- 兩段獨立可交付，同改 agent-workflow 不同位置（scope fence L92 後 vs 任務分級 L60 後新段）

---

## S1：side-discovery（scope-fence 負空間 redirect）

### Context

**UC 引用**：補強「agent-workflow scope fence」能力——從「防擴大」擴展為「防擴大 + redirect 收斂」。

**背景**：scope fence（L84-92）預防機械任務 agent「順手重構」scope 外區塊（L86 實證：4 個補-Logger agent）。但 fence 是**死路**——擋擴大卻無 redirect，發現的 scope 外改進被擋掉（機械任務）或丟棄（實作任務無指引）。build.md scope-creep 偵測（L103-107）也只 flag 進 finding，無建卡供日後。Symphony WORKFLOW.md L88-93 有完整 pattern：發現 meaningful out-of-scope 改進 → file separate issue（title/desc/acceptance/related/blockedBy）→ 放 Backlog。

**依賴錨點**：
- scope fence → 定義 `skills/agent-workflow/SKILL.md:84-92` / S1 緊鄰其後插入
- kanban 卡片模板 → 定義 `skills/kanban-board/SKILL.md:62-79` / S1 交叉引用（不重複）
- build.md scope-creep → 定義 `commands/build.md:103-107` / S1 釐清分工（偵測 vs redirect）

**語義約束**：與 S2 共享「委派時 side-discovery 是 redirect 應用」（S2 引用 S1）。

**成功標準**：scope fence 段後含 side-discovery redirect 子段；agent 發現 scope 外 meaningful 改進有明確收斂通道（建卡）；R3 防氾濫機制（threshold + batch + triage）。

### 修改要點（docs mode）

在 `agent-workflow/SKILL.md` scope fence 段（L84-92）後、`/build` 整合（L94）前，插入「Side-Discovery（scope-fence 負空間 redirect）」子段：

1. **觸發**：agent 審查/實作時發現 **scope 外 meaningful 改進**（非當前任務目標，但值得做）
2. **triage 決策**（借 Symphony land skill L208-211）：
   - **defer**（default）：建 Backlog 卡供日後排程
   - **accept**：擴大 scope（**需用戶/EP 確認**，非自主擴大——與 scope fence「不擴大」一致）。**自主模式（deep-work 半夜跑）用戶不可得 → accept 預設降級為 defer**（建 Backlog 卡 + completion report 標記待用戶確認，對齊紅線 git commit 自主處置 L47-49）（外部 review B1）
   - **decline**：明確不值得，丟棄（記錄原因，避免重複發現）
3. **建卡**（defer 時）：交叉引用 kanban-board 卡片模板（L62-79）——卡片標題 / 目標 / 相關（EP + 連當前任務）/ 驗收標準（**欄位名對齊模板**）。依賴關係寫入「備註」欄標註 `[blocked-by: <任務>]`（blockedBy 非模板標準欄位）。**不重複模板定義**
4. **R3 防氾濫**（三層）：
   - **threshold**：「meaningful」= 獨立發現時會 warrant 一張卡/EP 的改進（非 trivial 觀察）
   - **batch**：side-discovery 先記錄到 completion report，**段落/任務結束時統一建卡**（非執行中斷流程）；**研究 agent 邊界（外部 review ℹ️2）**：Explore 等研究 agent 不產 completion report → side-discovery 記錄於 spawn prompt 回覆，由 spawner 代建卡
   - **人類 triage**：kanban 每週回顧（kanban-board L150-157）清理低價值卡
5. **與 scope fence 共置理由**（single-source）：fence 說「不擴大 scope」、side-discovery 說「發現的 scope 外工作去哪」——兩者必須共置，否則 fence 負空間是死路（擋擴大 + 無 redirect = 工作遺失）

### 驗證策略（文檔驗證）

- **rg 殘留**：scope fence 段後含 side-discovery 子段（`rg "side-discovery|Side-Discovery|redirect|Backlog 卡" skills/agent-workflow/SKILL.md`）
- **single-source**：side-discovery 建卡**引用** kanban-board 模板而非重複（rg 確認無模板重複定義）
- **`/consistency`**：agent-workflow/SKILL.md 自洽性（scope fence 與 side-discovery 子段層級、職責互補不矛盾）
- **R3 防氾濫**：確認子段含 threshold/batch/triage 三層（rg `meaningful|batch|triage|每週`）

---

## S2：委派哲學（delegate → let go → verify 連貫框架）

### Context

**UC 引用**：補強「agent-workflow delegation」能力——從控制導向平衡為 delegate+verify 連貫框架。

**背景**：agent-workflow 全篇控制導向，**放手碎片零散未 articulated**：autonomous-execution「不交半成品」L15、build.md「裁量權」L121 + context handoff L111-118、scope fence「創造性任務例外」L92。Symphony 洞見#7：「把 agent 當僵化狀態機節點失敗 → 改交付目標（給工具+放手）」。ref-docs Ch19 AI Contract 四 pillar（Formalized Contract / Dynamic Negotiation / Quality-Focused Iterative Execution / Hierarchical Subcontracts）是理論框架；Ch6 Planning 判準（「does the how need to be discovered, or is it already known?」）= 控制 vs 放手判準。

**依賴錨點**：
- build.md context handoff → 定義 `commands/build.md:111-118` / S2 引用（既有最完整 context handoff）
- build.md 裁量權 → 定義 `commands/build.md:119-128` / S2 引用（既有放手判斷）
- autonomous-execution 不交半成品 → 定義 `skills/autonomous-execution/SKILL.md:15` / S2 引用（完整交付期望）
- autonomous-execution 紅線 → 定義 `skills/autonomous-execution/SKILL.md:32-62` / S2 引用（放手底線）
- EP-A false-done → 定義 `ep-autonomous-execution-reliability.md` S2 / S2 引用（delegate→verify loop 下游）

**語義約束**：與 S1 共享「委派時 side-discovery 是 redirect」（S2 引用 S1）；與 EP-A 共享「delegate→verify loop」（R4）。

**成功標準**：agent-workflow 含委派框架段（delegate→let go→verify 連貫模型）；連貫化 4 處既有碎片；R1/R2 平衡論述（delegate+verify）；R5 fence vs 委派非矛盾論述。

### 修改要點（docs mode）

在 `agent-workflow/SKILL.md` 任務分級段（L52-60）後，加「委派框架（Delegation Philosophy）」段：

1. **連貫模型**：delegate(goal + tools + context) → let go(within guardrails) → verify(outcome)
   - **goal**：EP segment / 任務目標（清晰可驗收）
   - **tools**：skills/ 體系 + rules-reminder 六條 + 必要 mock/fixture（**delegation 前配工具集**——agent-workflow L164 只教 rules-reminder 注入；**build.md:117 已有完整 skill invoke 實作清單**（rules-reminder / test-driven-development / incremental-implementation / autonomous-execution），agent-workflow 層概念化引用**不重列**；對應 Symphony `.codex/skills/` 視角）。**判斷原則（外部 review B5）**：依任務領域匹配 skill description 觸發詞（任務含「測試」→ TDD skill、含「錯誤」→ debugging skill）
   - **context**：build.md context handoff（L111-118）已是最完整實作——引用不重述
   - **let go**：實作層裁量權（build.md L121「EP 為收斂方向，實作層有發現真相的責任」）；放手底線 = autonomous-execution 紅線/黃線（L32-62）
   - **verify**：build.md git diff（L103-107）+ Agent Review——引用不重述
2. **R1 平衡（防過度放手）**：delegate **+ verify** 非 delegate + trust。純放手無驗證 = scope-creep 近乎 ship 重演（`_done/ep-agent-output-verification.md` 實證）。verify 是委派的**共同體**非事後補丁。**強度上限（review）**：delegate+verify 假設 verifier（主 LLM）可靠；deep-work 長 session 的 verifier 退化（context fatigue）是此框架已知上限，由 build.md batch ceiling（L127）部分緩解但不完全覆蓋（對齊 EP-A R4 docs-mode 誠實性）
3. **R2 平衡（防過度控制）**：創造性任務（設計/實作）**不加 fence**——scope fence L92 已排除。委派光譜：機械任務 = tight delegation（fence），創造性任務 = loose delegation（goal+tools+放手），**混合型任務（部分機械 + 部分判斷，如重構提升可讀性）= medium delegation**（goal + 關鍵約束 fence 精簡版，只 fence 不可碰區域 + 放手判斷空間）
4. **R5 fence vs 委派非矛盾**：兩者適用**不同任務類型**（同光譜兩端）——fence 是委派的特殊形態（目標極明確時的 tight delegation），非對立。委派框架是 scope fence 的**上層框架**
5. **R4 delegate→verify loop**（交叉引用 EP-A）：委派（本段）上游 → 降低 false-done；EP-A completeness validation（false-done 偵測）下游 → 捕捉殘餘。兩者形成 loop，**互补非重複**。**邊界釐清（review）**：verify 的 git diff 半邊（scope/claim 校驗）與 EP-A completeness 互補不重疊；Agent Review 半邊關注**單段 code 正確性**（段落級），EP-A completeness 關注**跨段落 EP 完成度**（EP 級）——層級不同但都觸及「done 判定」，builder 寫 verify 時引用 build.md Agent Review（段落級），不重述 EP-A 的 EP 級 completeness
6. **S1 引用**：委派時 agent 發現 scope 外 → side-discovery redirect（S1）是委派框架的 redirect 應用
7. **R6 docs-mode 強度上限**：委派是**判斷框架**非機械閘門（無 server-side enforcement，對比 Symphony approval_policy+sandbox）；其 verify 半邊的機械性來自 build.md git diff（已存在）
8. **理論支撐**：**一句話**引用 ref-docs Ch19 AI Contract 四 pillar 名稱 + Ch6 Planning「does the how need to be discovered?」判準——作設計理由背書，**不展開理論內容**（signal 導向：R1/R2/R5 平衡論述是主體，理論是支撐）。**外部引用定位（外部 review B6）**：ref-docs / Symphony 為外部**靈感來源**，build agent 無法在本 repo 查證——核心論證用內部已查證引用（build.md 裁量權 / 紅線）承載，外部位標「靈感來源」非可查證引用

### 驗證策略（文檔驗證 + EP Review 設計合理性）

- **rg 殘留**：agent-workflow 含委派框架段（`rg "委派框架|delegate|Delegation|let go|verify" skills/agent-workflow/SKILL.md`）
- **連貫化驗證**：委派段引用 4 處既有碎片（build.md context handoff/裁量權、autonomous-execution 不交半成品/紅線、scope fence 創造性例外）——rg 確認引用存在，非重述
- **R1/R2/R5 平衡論述**：確認段含「delegate+verify」「創造性不加 fence」「fence vs 委派非矛盾」（rg）
- **EP-A 交叉引用**：確認 delegate→verify loop 引用 EP-A（rg `EP-A|false-done|completeness`）
- **`/consistency`**：agent-workflow/SKILL.md 自洽性（委派框架與既有控制段不矛盾，R5 論述）
- **single-source**：委派段**引用** build.md/autonomous-execution 既有力，非重複定義（rg 確認）

---

## 整合策略

- S1、S2 同改 `agent-workflow/SKILL.md` 不同位置（scope fence L92 後 vs 任務分級 L60 後新段）；**S2 item 6 引用 S1（委派時→side-discovery redirect），建議 S1 先 build**（外部 review B2，修正「段落順序無強依賴」措辭矛盾）；兩段改不同位置，build 順序不破壞前段
- **跨 EP build 順序（外部 review B3）**：S2 item 5 delegate→verify loop 交叉引用 EP-A false-done——EP-A S2 false-done 尚未落地（EP-A 未 build）。**EP-A 須先 build**，EP-B 的 agent-workflow 交叉引用才指向存在的 autonomous-execution Recovery 段。reference target 為 EP-A 文檔（ep-autonomous-execution-reliability.md）+ EP-A build 後的 SKILL.md Recovery 段
- 交叉引用網：agent-workflow（S1/S2）→ kanban-board（建卡模板）、autonomous-execution（放手底線）、build.md（context handoff/裁量權/verify）、EP-A（delegate→verify loop）
- **delegate→verify loop 反向引用（review #3）**：EP-A build Recovery 段時加一行反向指引——「上游委派框架見 agent-workflow 委派段（delegate→verify loop 上游）；本段為 false-done 下游偵測」。EP-A 尚未 build，反向引用在 EP-A build 時加（不擴 EP-B scope、不改 EP-A EP 檔）
- 理論：ref-docs Ch19/Ch6

---

## 收尾步驟（docs mode）

### 1. 受影響 skill 行為已反映
- `agent-workflow/SKILL.md`：scope fence 段（side-discovery redirect 子段）+ 新委派框架段反映新能力
- **觸發詞同步**：`agent-workflow/SKILL.md` frontmatter `description` + `skills/CLAUDE.md` skill 索引 description 補觸發詞「delegation, side-discovery, scope redirect, manager-delegate」（當前偏 spawn/並發，缺委派/scope redirect）

### 2. kanban / SYSTEM-MAP
- 元專案無對應 deferred card → 跳過（正當）
- 視需要為本 EP 建追蹤 card（.kanban/Backlog/）

### 3. instruction 檔品質
- 對 `agent-workflow/SKILL.md` 跑 `/consistency`（自洽性、signal/noise）
- 確認新段落符合 instruction-writing（High Signal 設計理由、導航種子、無元資訊）

### 4. /audit-test
- docs mode 無新測試 → 跳過

---

## EP Review Cycle（已執行）

Review agent（獨立 context，docs profile，top-down）+ `/judge-review` 全數採納。**無 Critical**。10 處行號引用全部驗證準確。

| # | 嚴重度 | 信心 | 要點 | 採納 | 修正位置 |
|---|---|---|---|---|---|
| 1 | 🟡 Important | evidence | L158 tools 漏看 build.md:117 既有 skill injection → single-source 違規風險 | ✅ | S2 item 1 |
| 2 | 🟡 Important | evidence | R4 verify Agent Review 半邊（段落級）vs EP-A completeness（EP 級）done 判定重疊區未釐清 | ✅ | S2 item 5 |
| 3 | 🟡 Important | evidence | delegate→verify loop 單向（EP-A 零引 EP-B）→ 反向引用在 EP-A build 時加 | ✅ | 整合策略 |
| 4 | 💡 Suggestion | evidence | side-discovery 卡 blockedBy 非 kanban 模板欄位 → 欄位名對齊模板 | ✅ | S1 item 3 |
| 5 | 💡 Suggestion | inferred | R1 delegate+verify 假設 verifier 可靠，半夜退化未標 | ✅ | S2 item 2 |
| 6 | 💡 Suggestion | inferred | tight/loose 二元缺混合型（medium delegation） | ✅ | S2 item 3 |
| 7 | 💡 Suggestion | inferred | 理論引用深度未限，over-write 風險 | ✅ | S2 item 8 |

**結構判斷（review）**：EP 整體穩固可 build。spawner/agent 正交落點成立；side-discovery 共置 scope fence single-source 正確；R5 光譜論述成立；delegate+verify 是 outcome review（非 re-control，不構成「控制重新包裝成委派」）；引用全驗證準確。findings 均為邊界釐清與漏改預防，不動搖委派框架 + side-discovery 核心設計。
