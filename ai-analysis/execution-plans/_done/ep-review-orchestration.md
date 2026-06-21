> **ep_type**: implementation
> **mode**: docs（全為 commands/skills/rules 下 `.md`，無 `.py` callable）

# EP: review 執行層 orchestration 集中（預設/失敗階梯/多視角/mode 解耦）

## 動機（self-contained 背景）

`ep-review-engine-refactor` 抽出了 review 的 **domain 層**（方法論：嚴重度/信心/自證/mode 判定規則），但 **execution orchestration 層**（預設行為 / 失敗處理 / 視角配置 / spawn-vs-session / mode 派發）**從沒被抽出** — 散落跨 review-engine + agent-workflow + agent-review-cycle + 各命令，部分根本沒定義。症狀：

- review 命令 **auto-detect mode**（LLM 在裁量點偷懶退 Main LLM / 搞錯）— 實證不佳，要改 force 獨立。
- **429 / 持續失敗**沒處理（classifier retry 有，429/continuous 無）。
- **spawn vs 另開 session** 沒統一模型（user 兩個都用，另開抓得到 spawn 漏的）。
- **視角**寫死 2-perspective，沒「為何」也沒 >2 配置規則。
- review-engine mode 表**指名 adapter**（domain→adapter 耦合）。

本 EP 把 execution 職責**歸位**到對的家（不新增層，避免過度工程）：預設 → review-engine；失敗/並發 → agent-workflow；視角 → agent-review-cycle；mode 派發 → 解耦。

**設計決策（已 lock）**：
1. review **不 auto-detect**，force 獨立 agent；agent **數量視 max-agents**（預設 3）；agent **model 預設 = 主 session（inherit）**，可調降一級；此預設集中一處可調。
2. **>2 配置**（授權決定）：base 恆 ① clean + ② UC-anchored；extra 優先序到 cap：UC>6→UC-split，否則 architecture > adversarial > consumer；絕不複製 lens。
3. **另開 session handoff 套件** = 持久化 finding + git diff + 標的/EP/UC 路徑。
4. review-engine mode 表 **domain→adapter 解耦**（產抽象決策，各命令自取 template）。

**Scope out**：max-agents 參數仍 build-only（低並發命令 auto-detect 已足，且 max-agents 已集中 model-routing 為並發真相源）；classifier retry（既有）；followup-review 角色改正（獨立小修，另列）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | review-engine 加「review 執行預設」集中段（force 獨立 / max-agents 預設3 / model inherit 預設可降級 / 2-agent clean+UC / >2 配置 / spawn+session） | 無 |
| S2 | agent-workflow 失敗階梯（429/continuous 統一：retry→serialize→降級+標記）+ deep-work 偏好 serialize | 無 |
| S3 | agent-review-cycle 補 2-perspective「為何」（clean=bias / UC=覆蓋度 正交）+ >2 配置規則（同 S1，執行範本落點） | S1 |
| S4 | review-engine mode 表 domain→adapter 解耦（抽象 mode 決策，不指名 adapter；各命令自取 template） | 無 |
| S5 | 各 review 命令薄引用「review 執行預設」+ model-routing 調和（review command agent = inherit 預設，覆蓋通用 review→降級） | S1, S4 |

五段獨立可收斂；S1 是核心（集中預設），其餘歸位/引用。

---

## UC 盤點（docs mode — 元專案無 Capabilities，掃受影響命令/rules）

### 受影響命令/rules 清單
- `skills/review-engine/SKILL.md`（S1 預設段、S4 mode 解耦）
- `skills/agent-workflow/SKILL.md`（S2 失敗階梯）
- `commands/claude/_common/agent-review-cycle.md`（S3 視角「為何」+ >2）
- `commands/{ep-review,code-review,audit-test,execution-plan,build}.md`（S5 薄引用）
- `rules/model-routing.md`（S5 review agent model 調和）

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| review 執行預設單一源（force 獨立/max-agents/model/視角/spawn-vs-session） | 📋 | `skills/review-engine/SKILL.md` S1 |
| spawn 失敗階梯（429/continuous 統一） | 📋 | `skills/agent-workflow/SKILL.md` S2 |

---

## Scenario Matrix（docs mode — 觸發/預期為文檔語境：rg 命中 / 行為描述）

| # | 場景 | 觸發 | 預期行為（文檔） | 對應 |
|---|------|------|----------------|------|
| SM-1 | 跑 review 命令 | 任何 review | force 獨立 agent（不走 Main LLM 自審）；不 auto-detect | S1/S5 |
| SM-2 | review spawn 429 | 並發撞限 | retry → 降並發 → serialize（deep-work 停此）→ 降級+標記 | S2 |
| SM-3 | review spawn 持續失敗 | classifier/crash 反覆 | retry ≤2 → serialize → 降級 Main LLM 自審 + 顯式標記 fallback（非靜默） | S2 |
| SM-4 | 高風險變更要 >2 agent | user --max-agents>2 或大變更 | base clean+UC + extra 依序（UC>6 split / architecture / adversarial / consumer），不複製 lens | S1/S3 |
| SM-5 | user 另開 session review | build/review 後 user 開新 session | handoff = 持久化 finding + diff + 標的路徑；最強獨立性 | S1 |
| SM-6 | review engine mode 派發 | 查 mode | 產抽象 mode 決策，不指名 adapter；各命令自取 template | S4 |

---

## S1：review-engine 加「review 執行預設」集中段

### Context
review-engine 是 review domain 真相源（本 session 建立）。execution 預設散落/缺失 → 集中於此（單一可調處）。讀者：各 review 命令引用此，不自帶預設。

### 修改要點
`skills/review-engine/SKILL.md` 加「## review 執行預設（單一源 — 各 review 命令引用）」段：

1. **不 auto-detect，force 獨立 agent**：review 命令預設 spawn 獨立 agent（Agent Tool/Workflow），**不接受 LLM 裁量退 Main LLM 自審**（實證：偷懶/搞錯）。Main LLM 自審僅 spawn 持續失敗降級時啟用 + 顯式標記。
2. **agent 數量 = max-agents**（預設 **3**；與 build 一致，受 model-routing 並發上限 cap）。
3. **agent model 預設 = 主 session（inherit）**；**可調降一級**（model-routing 降級映射）。此為 review command 專屬預設，覆蓋 model-routing 通用「review→降級」（見 S5 調和）。
4. **預設 2 agent = ① clean（Fresh，無 anchor）+ ② UC-anchored（Intent）**：兩 lens 正交、同時跑 — clean 抓作者 rationalize（bias），UC 抓漏覆蓋/偏意圖（coverage）。
5. **>2 配置**（opt-in，高風險/大變更；受 max-agents cap）：base 恆 ①+②；extra（第3+）優先序到 cap — **UC 數 >6 → UC-split**（extra 拿 UC 子集，深度，唯一給 UC 給 extra 的情境）；否則 **architecture(axis 3) > adversarial/edge > consumer-perspective**；**絕不** 2nd clean / 2nd 同 UC（複製 lens，同家族共享盲點，邊際≈0）。
6. **spawn vs 另開 session 共存**（非二選一）：spawn（命令內，即時，同家族天花板）；另開 session（user 手動，最強獨立，抓 spawn 漏的）。**另開 handoff 套件** = 持久化 finding（EP review 區段/kanban，tracked）+ git diff + 標的/EP/UC 路徑。高風險建議兩個都跑。

### 驗證策略（docs mode）
- `rg "review 執行預設|force 獨立|max-agents.*預設 3|inherit.*降一級|clean.*UC-anchored"` review-engine → 命中
- `rg "UC-split|architecture.*adversarial|絕不.*2nd clean"` review-engine → 命中（>2 配置）
- `/consistency`

---

## S2：agent-workflow 失敗階梯（429/continuous 統一）+ deep-work serialize

### Context
spawn 失敗處理目前只有 classifier retry（本 session 加）。429/continuous 無定義。agent-workflow 是 general spawn 機械層，失敗階梯歸此（所有 spawn 命令共用）。deep-work 無時間壓力 → 偏好 serialize（保獨立性），不急降級。

### 修改要點
`skills/agent-workflow/SKILL.md` 加「## spawn 失敗階梯（general，所有 spawn 共用）」段：

```
429 單次 → backoff retry（同 spawn 重試）
429 持續 → 降並發（N → N/2 → … 最深 = serialization，concurrency=1，一次一個循序）
             • deep-work（無人、無時間壓力）停在此 — 用時間換獨立性，保所有 lens
非 429 失敗（crash/timeout）→ retry ≤2（同 classifier 模式）
全失敗（serialization 仍 429，少見）→ 降級主 LLM 自審 + 顯式標記 fallback（警示獨立 review 丟失，非靜默）
```

關鍵區分：**serialization 是降並發的一步，不是降級**。降級（丟獨立性）只在 concurrency=1 還持續 429 才發生。deep-work 甚至可**預設低並發**（不急，何必冒 429 平行）。

### 驗證策略（docs mode）
- `rg "失敗階梯|429|serialize|降並發|降級.*標記"` agent-workflow → 命中
- `rg "deep-work.*serialize|無時間壓力"` agent-workflow → 命中
- `/consistency`

---

## S3：agent-review-cycle 2-perspective「為何」+ >2 配置

### Context
agent-review-cycle 是 Agent Tool 模式 review 執行範本，有 2-perspective（Intent-anchored + Fresh）但沒寫「為何」（bias↔覆蓋度正交），也沒 >2 配置。S1 定義預設（含 >2 規則），S3 在執行範本呼應 + 補「為何」。

### 修改要點
`commands/claude/_common/agent-review-cycle.md`：
1. 2-perspective 段補「**為何同時兩個**」：① Fresh（clean，無 anchor）抓作者 rationalize〔bias〕；② Intent-anchored（UC）抓漏覆蓋/偏意圖〔coverage〕— 兩 lens 正交，單跑任一有盲點（clean 漏該查的 UC；UC 被錨定看不到合理化），同時跑互補。
2. 加「**>2 配置**」：引用 review-engine「review 執行預設」>2 規則（UC>6 split / architecture>adversarial>consumer / 不複製 lens）。執行範本據此組 prompt。

### 驗證策略（docs mode）
- `rg "為何同時|bias.*coverage|正交"` agent-review-cycle → 命中
- `rg ">2|UC-split|不複製 lens"` agent-review-cycle → 命中
- `/consistency`

---

## S4：review-engine mode 表 domain→adapter 解耦

### Context
review-engine mode 表（Workflow/Agent Tool/Main LLM）直接指名 adapter（→ workflow-review-pattern / agent-review-cycle）= domain 知道 adapter（依賴方向向外）。strict Clean Arch 要 domain 產**抽象 mode 決策**，由 use-case（各命令）派發到 adapter。

### 修改要點
`skills/review-engine/SKILL.md` mode 表：
- mode 表保留**判定規則**（effort/max-agents → 抽象 mode：Workflow / Agent Tool / Main LLM），但**淡化對 adapter 模板的指名** — 改為「判定為 Workflow 模式 → 各命令自取 [workflow-review-pattern]；Agent Tool → [agent-review-cycle]」（派發由命令層，非 domain 內嵌）。
- 保留「Main LLM 模式適用範圍」註記（本 session 已加 — 僅 code-review；build/ep-review/execution-plan 刻意覆蓋）。

> 不強求完全消除連結（docs 系統導航性互指可容忍）— 重點是 mode 表**職責是判定規則**（domain），**派發是命令層職責**（use-case），語意上分開。

### 驗證策略（docs mode）
- `rg "判定規則|各命令自取|派發"` review-engine mode 段 → 命中
- `/consistency`

---

## S5：各 review 命令薄引用 + model-routing 調和

### Context
各 review 命令（ep-review/code-review/audit-test/execution-plan/build 的 review 段）目前各自帶 mode/perspective 描述 → 改薄引用 review-engine「review 執行預設」（單一源）。另：model-routing 通用規則「review→降級」與 S1 的「review command agent = inherit 預設」需調和。

### 修改要點
1. `commands/{ep-review,code-review,audit-test}.md` + `execution-plan.md` EP Review 段 + `build.md` Agent Review 段：mode/perspective 描述改「**見 [review-engine] review 執行預設**」（薄引用，不自帶預設細節；保留各命令特有的 profile/產出）。
2. `rules/model-routing.md`：「review/verify/research/explore agent → 降級」加** carve-out**：「review **command**（ep-review/code-review/audit-test/execution-plan EP Review/build Agent Review）的 agent model 預設 **inherit（主 session）**，見 review-engine review 執行預設；其他 review-ish agent（verify/research/explore 非 review command）維持降級」。

### 驗證策略（docs mode）
- `rg "review 執行預設"` 各 review 命令 → 命中（薄引用）
- `rg "review command.*inherit|carve-out|覆蓋.*review→降級"` model-routing → 命中
- 各命令不再自帶 max-agents/model/perspective 預設細節（rg 殘留 = 0 於這些欄位）
- `/consistency`

---

## 收尾步驟（docs mode）

1. **受影響命令行為已反映**：各 review 命令薄引用預設、不自帶；force 獨立 / 失敗階梯 / >2 配置行為一致。
2. **`commands/CLAUDE.md` / `skills/CLAUDE.md` 索引**：確認 review-engine description 含「review 執行預設單一源」；各命令 description 無誤述。
3. **跳過**（docs mode + 元專案）：Capabilities 表格、SYSTEM-MAP、mypy/ruff/pytest、/audit-test（無 .py 測試）。
4. 本 EP 完成後搬 `execution-plans/_done/`。
