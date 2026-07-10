# EP-A: autonomous-execution reliability 層補強

> **ep_type**: implementation
> **mode**: docs（全 .md 變更，無 .py callable — `rg "^def |^class " --type py` 於本 EP 變更範圍 = 0）
> **規模**: standard（跨 skill 概念，中型）
> **來源**: Fable 5 + Symphony gap analysis（前置 workflow 3 agent 查證）+ Symphony elixir 實作接地（core-domain/codex AGENTS.md）

## 實作總覽

補強 `autonomous-execution` skill 的 reliability 層，對應 **deep-work 半夜跑（無人值守）真痛點**。兩個子能力，**均落 autonomous-execution**（緊鄰紅線清單 L36-43，single-source；非 agent-workflow——見段落 0 落點建議）：

1. **workspace 安全不變量**（Symphony 洞見#2）：red-line 行為清單補機械空間不變量
2. **recovery**（Symphony 洞見#1）：per-error self-healing 補 session 級 stall 偵測 + reconciliation

**核心設計原則：借 Symphony 的「思想」，非「實作載體」**。Symphony 綁 always-on service + Linear truth source + Elixir/OTP；solo 場景（無 CI、無 daemon、context 稀缺）只適配其可靠性**思想**（continuation retry、crash-only reconciliation、機械不變量），**不適配**載體（token-gated timer、config-re-read、local-remote 非對稱、supervisor reconciliation）。

---

## UC 盤點（docs mode）

### 受影響 skills/rules 清單

| 檔 | 段（行號） | 變更 | 段落 |
|---|---|---|---|
| `skills/autonomous-execution/SKILL.md` | 紅線清單 L36-43（行為枚舉） | 補「機械空間不變量」子段 | S1 |
| `skills/autonomous-execution/SKILL.md` | Error Self-Healing L68-77（per-error） | 補「Session 級 Recovery」段 | S2 |
| `skills/agent-workflow/SKILL.md` | Worktree 隔離 L62-74 | **交叉引用**（加一行；實質內容不改——操作指南 vs 安全不變量職責分離） | S1 |
| `rules/acceptance-evidence.md` | session-boundary L154（R6 分工） | 釐清與新 recovery 的邊界 | S2 |
| `commands/build.md` | batch ceiling L127（R6 分工） | 釐清觸發點分工 | S2 |

### Capabilities / kanban / SYSTEM-MAP

- 元專案無 Capabilities 表格 / SYSTEM-MAP → **跳過**（正當：ai-rules 是 rules/skills 治理 repo，非 UC-Driven 消費端專案）
- **`.kanban/Backlog/session-boundary-intent-drift-review.md`**（deferred card，2026-07-09）→ **S2 部分回應此 card**（跨 session intent drift 的機械觸發）；S2 完成後評估更新/關閉該 card（收尾步驟）

---

## Scenario Matrix（docs mode）

| # | 場景 | 觸發 | 預期行為（文檔語境，rg 驗證） | Checkpoint | 對應 |
|---|---|---|---|---|---|
| SM-1 | deep-work 半夜跑，LLM 自稱段落 done | completion report 生成 | continuation retry：對照 EP planned deliverable，**normal-exit≠done** → 標記未完整 | EP 段落結算 | S2 |
| SM-2 | 跨 session resume（/at 或手動開新） | 新 session 開始 | crash-only reconciliation：**re-derive 真相**（git state 事實 + EP intent 對照）而非 restore in-memory；不符 → 結算差異報告 | resume 結算 | S2 |
| SM-3 | agent 在 worktree 內跑 Bash 越界（`cd /`、絕對路徑寫 worktree 外、symlink 逃逸） | Bash 命令含路徑運算 | 機械空間不變量指導：路徑相對 worktree root、不逃逸；rg 驗證紅線段已補此指導 | 紅線 + workspace 不變量段 | S1 |
| SM-4 | 連續多段未經人類判讀（context 累積漂移） | batch ceiling 觸發 | 與既有 batch ceiling（build.md L127）**分工釐清**不重疊 | session-boundary | S2（R6） |
| SM-5 | 裸 git worktree（非 EnterWorktree）+ 未限制命名 | agent 自建 worktree | 指導**優先 EnterWorktree**（已限 path/name）；裸 git worktree 需手動 sanitize | workspace 不變量段 | S1 |

---

## 段落 0：全域研究摘要

### 可複用基礎設施（既有，不重造）

- `autonomous-execution` 紅線清單（L36-43）— 行為枚舉，**S1 補強對象**
- `autonomous-execution` Error Self-Healing（L68-77）— per-error loop，**S2 擴展對象**
- `agent-workflow` worktree 隔離（L62-74，教 `isolation: "worktree"` = EnterWorktree 機制）— 操作指南，**交叉引用不改**
- **EnterWorktree 工具**：建立 worktree 時限 path 在 `.claude/worktrees/` + name 白名單 `[A-Za-z0-9._-]` — **建立時保護已有；執行時路徑不變量缺失**（R5 已查證）

### gap 真實性（已查證，附行號）

- **recovery gap：真實**。per-error Self-Healing（L68-77）是唯一；build.md L127 batch ceiling 是單 session 軟觸發；acceptance-evidence L154 明文承認跨 session 無觸發機制；deferred card `session-boundary-intent-drift-review.md` 印證。
- **workspace gap：真實但 scope 精準化**。紅線行為枚舉（L36-43）會漏新形態；agent-workflow L71 只「相對路徑」建議（非機械驗證）。**但 EnterWorktree 建立時保護已部分覆蓋**（path + name）→ S1 聚焦「**agent 在 worktree 內執行 Bash 時**的路徑不變量」，非重造建立時保護。

### Symphony pattern solo 適配（節錄）

| 適用 | 不適用（綁 always-on / 載體） |
|---|---|
| continuation retry（normal-exit≠done）— **核心洞察** | token-gated timer（GenServer 並發原語） |
| crash-only reconciliation（思想，真相源置換）— **episodic**：resume 時單次 re-derive | config every-cycle re-read（always-on tick） |
| workspace 機械不變量（執行時路徑） | local-remote 非對稱（solo local-only） |
| AgentRunner crash-on-failure（→ completion report 未解決段） | supervisor reconciliation — **continuous**：持續監督（solo 無上層；與 episodic reconciliation 區別，非「reconciliation 整體不適用」） |

### 落點建議（研究判定）

**recovery + workspace safety 都進 autonomous-execution**（非 agent-workflow）。理由：紅線清單在 autonomous-execution L36-43，機械補強應緊鄰它強化的行為清單（single-source）；agent-workflow worktree 段是「如何用 worktree」的操作指南，加安全不變量會混淆語境。交叉引用即可。

### 風險假設（R1-R6，段落驗證策略涵蓋）

- **R1** solo recovery 真相源 → S2 設計決策（候選：git state 事實 + EP intent 對照）
- **R2** solo stall 定義（無 tick → normal-exit≠done 觸發）→ S2 設計決策
- **R3** session 邊界（/at resume / 手動 / handoff）→ S2 決定處理範圍 + 回應 deferred card
- **R4** docs-mode 機械不變量強度上限（指令 ≠ 強制）→ S1 誠實標記 + hook 補強列未來方向
- **R5** EnterWorktree 既有覆蓋 → S1 已查證（建立時已有，S1 聚焦執行時）
- **R6** 與 batch ceiling / session-boundary review 分工 → S2 釐清

---

## 段落劃分原則

- **S1 workspace safety 先**：R5 已查證（建立時保護已有），scope 精準（執行時路徑不變量），de-risk 快速落地一個 reliability 改進
- **S2 recovery 後**：R1/R2/R3/R6 設計決策重，專注細做
- 兩段獨立可交付，同改 autonomous-execution 不同段（紅線 L36-43 vs Self-Healing L68-77），build 時注意段落順序不破壞前段

---

## S1：workspace 安全不變量

### Context

**UC 引用**：補強「autonomous-execution 紅線（不可逆操作防線）」能力——從行為枚舉擴展為行為 + 機械空間不變量雙層。

**背景**：紅線清單（L36-43）是行為枚舉（`rm -rf`、`git push --force`、`sudo`...），必然漏新形態（新型 symlink 攻擊、路徑遍歷變體）。Symphony 用 `PathSafety`（segment-by-segment canonicalize，canonical path 逃出 root 即 reject）做 code-level enforce。solo 場景：EnterWorktree 建立 worktree 時已限 path + name（R5 查證），**但 agent 在 worktree 內執行 Bash 時無路徑不變量**——可 `cd /`、寫絕對路徑到 worktree 外、跟隨逃逸 symlink。

**依賴錨點**：
- 紅線清單 → 定義 `skills/autonomous-execution/SKILL.md:36-43` / 消費 `commands/deep-work.md`（紅線注入 prompt）
- agent-workflow worktree 隔離 → 定義 `skills/agent-workflow/SKILL.md:62-74` / S1 交叉引用（不改）

**語義約束**：與 S2 共享「docs-mode 強度上限」（R4）——機械不變量在 docs 是「教 LLM 驗證的指導」，強度 < code-level enforce。

**技術選型**：不新增 code（docs mode）；在紅線段後補「機械空間不變量」子段，指導 LLM 在 Bash 路徑運算時自我驗證。

**成功標準**：紅線段含機械空間不變量子段；agent 在 worktree 內 Bash 路徑運算有可遵循的驗證指導；EnterWorktree 優先於裸 git worktree 明確標示。

### 修改要點（docs mode 替代 Pseudo Code）

在 `autonomous-execution/SKILL.md` 紅線清單（L36-49 區域）後，新增「機械空間不變量」子段：

1. **path-in-root**：所有 Bash 路徑運算（讀寫、cd、find/rg 範圍）相對於當前 worktree root；**不寫絕對路徑到 worktree 外**。判定：路徑 resolve 後須在 worktree root 子樹內。
2. **symlink-escape 偵測**：不跟隨 canonical path 逃出 worktree root 的 symlink（canonicalize 驗證：expanded path 在 root 內 ≠ canonical path 在 root 內 → escape，拒絕）。借 Symphony `PathSafety` segment canonicalize 思想（非實作）。
3. **優先 EnterWorktree（建立時補充，非執行時不變量）**[review]：此項是 **spawner 決策**（建立 worktree 時），與 #1/#2（in-worktree agent 執行時不變量）**觸發時機不同**——builder 寫 SKILL.md 時須分開標記，避免同子段混兩種時機。建立 worktree 用 EnterWorktree（已限 path `.claude/worktrees/` + name `[A-Za-z0-9._-]`），**非裸 `git worktree add`**；若必須裸 git worktree，name 需手動 sanitize 同白名單。
4. **R4 強度上限誠實標記**：docs-mode 機械不變量是「指導」非「強制」；LLM 可能不遵循。hook 補強（`settings.json` PreToolUse 攔截 Bash 路徑逃逸）列為**未來方向（另一 EP）**，本段不實作。

交叉引用：agent-workflow worktree 隔離段（L62-74）加一行指回 autonomous-execution 機械不變量子段（「安全不變量定義見 autonomous-execution；此處為 worktree 用法」）。

### 驗證策略（文檔驗證）

- **rg 殘留**：紅線段後確認含「機械空間不變量」子段（`rg "機械空間不變量|symlink-escape|path-in-root" skills/autonomous-execution/SKILL.md`）
- **跨檔一致性**：agent-workflow L62-74 交叉引用指向 autonomous-execution 新子段（rg 驗證 link）
- **`/consistency`**：跑 autonomous-execution/SKILL.md 自洽性檢查（無矛盾、章節連續）
- **導航有效性**：紅線清單與新子段的層級關係正確（`###` 子段在紅線段下）
- **R4 誠實性**：確認子段標記「指導非強制 + hook 補強另議」（rg `指導非強制|hook`）

---

## S2：recovery（Session 級 stall 偵測 + reconciliation）

### Context

**UC 引用**：擴展「autonomous-execution Error Self-Healing」能力——從 per-error（單一錯誤重試 ceiling）擴展為 per-error + session/EP 級（跨段落、跨 session 的 done 驗證 + resume 結算）。

**背景**：Error Self-Healing（L68-77）是 per-error（讀錯→修→連續3次放棄標⚠️）。**缺 session 級**：LLM 自稱段落 done 但 EP 未真完整（normal-exit≠done）；跨 session resume 無結算對賬。Symphony 用 continuation retry（worker 正常 exit 但 issue 仍 active → 不標 done）+ crash-only reconciliation（init 時 re-derive truth from Linear，不 restore in-memory）。solo 無 Linear、無 always-on tick。

**依賴錨點**：
- Error Self-Healing → 定義 `skills/autonomous-execution/SKILL.md:68-77` / 消費 `commands/deep-work.md`、`commands/build.md`（段落結算）
- batch ceiling → 定義 `commands/build.md:127` / S2 釐清分工（R6）
- session-boundary review → 定義 `rules/acceptance-evidence.md:154` / S2 提供觸發機制（回應 deferred card）
- deferred card → 定義 `.kanban/Backlog/session-boundary-intent-drift-review.md` / S2 部分回應

**語義約束**：與 S1 共享 docs-mode 強度上限（R4）；與既有 batch ceiling、session-boundary review 的觸發點/作用域須不重疊（R6）。

**技術選型**：不新增 code（docs mode）；在 Self-Healing 段後補「Session 級 Recovery」段，定義 continuation retry（done 驗證）+ crash-only reconciliation（resume 結算）的 solo 形態。

**成功標準**：Self-Healing 段後含 Session 級 Recovery 段；定義 solo 真相源（R1）+ stall 觸發（R2）；與 batch ceiling / session-boundary review 分工明確（R6）；回應 deferred card（R3）。

### 修改要點（docs mode 替代 Pseudo Code）

在 `autonomous-execution/SKILL.md` Error Self-Healing（L68-77）後，新增「Session 級 Recovery」段：

1. **completeness validation（false-done 偵測，normal-exit≠done）**[適配 Symphony L92-97 continuation retry]：
   - solo 最危險 drift = 「LLM 自稱 done 但 EP 段落未真完整」（false-done）
   - 觸發點：**completion report 生成時**（對應 Symphony 的 always-on tick 改寫——solo 無 tick，改在完成報告這個確定時機；不算太晚——攔截 false-done 後 LLM 可繼續補完）
   - 機制：completion report 對照 EP planned deliverable（段落矩陣全 done？）；未完整 → 標記「normal-exit≠done」+ 列缺漏，**不宣稱 EP 完成**
   - **命名釐清（review）**：Symphony stall = 行程活著不推進；solo 此機制 = false-done 偵測（正常 exit 但工作未完整），本質不同——SKILL.md 文字用「completeness validation」/「false-done 偵測」，**不用「stall 偵測」**
   - **範圍限制（review）**：solo 無 always-on tick，本機制**僅偵測虛假完成聲明**；真正的 silent stall（LLM 從不宣稱 done / 卡住）**不可偵測**，需 session 超時 / 用戶返回等外部機制（超出本 EP 範圍）

2. **crash-only reconciliation（resume re-derive）**[適配 Symphony L106-110，真相源置換 R1]：
   - Symphony 真相源 = Linear；**solo 真相源 = git state（事實：working-tree diff vs session 前基準）+ EP 段落定義（意圖：每段 scope + 成功標準，靜態文檔）對照**
   - 觸發點：跨 session resume（/at resume 主要；手動開新 session 次之；handoff 交他人另議——R3）
   - 機制：resume 時 re-derive（git diff 推斷已做事實 vs EP 段落 scope 定義對照 → 推斷哪些段落 done）；**不 restore in-memory**（session 記憶不可信）；**不依賴顯式 done 標記**（deep-work 不 commit，無持久進度追蹤檔）；不符 → 結算差異報告（做了未涵蓋 / 涵蓋未做）
   - R1 真相源設計（review 修正用語）：intent 來自 **EP 段落定義本身**（靜態文檔：scope + 成功標準），**非動態「進度檔」**；reconciliation = 事實（git diff）vs 意圖（EP scope）對照推斷完成度。原「EP 進度結算含 intent」用語誤導（EP 無進度實體），builder 不需先讀進度追蹤檔

3. **R6 分工釐清**（與既有機制不重疊）：
   - **新 Session 級 Recovery**：段落/EP 級 done 驗證（continuation retry）+ resume 結算（reconciliation）
   - **batch ceiling**（build.md L127）：單 session 內 context 累積防漂移軟觸發（建議暫停）
   - **session-boundary review**（acceptance-evidence L154）：跨 session intent drift 審查（原則存在、**本 EP 給它觸發機制**——resume 時觸發，回應 deferred card）
   - 三者作用域不同（段落級 completeness / 單 session context fatigue / 跨 session intent direction），觸發點不重疊
   - **substrate vs review 邊界（review）**：S2 reconciliation = 機械真相 re-derivation（**事實層**：git vs EP scope → 差異報告）；deferred card intent-drift review = **判讀層**（差異報告 → intent 是否漂移）。S2 是 deferred card 的 **substrate + 觸發器，不是 review 本身**——避免 S2 寫成完整 intent-drift review（scope creep）或只 dump git log（過窄）

4. **R3 回應 deferred card**：本段為 `session-boundary-intent-drift-review.md` 的部分實作（給 resume 機械觸發 + re-derive 真相）。S2 完成後評估：更新該 card 標記「部分落地」或關閉（收尾步驟）。

### 驗證策略（文檔驗證 + EP Review 設計合理性）

- **rg 殘留**：Self-Healing 段後含「Session 級 Recovery」段（`rg "normal-exit|continuation retry|crash-only reconciliation|re-derive" skills/autonomous-execution/SKILL.md`）
- **R1/R2 設計合理性**（EP Review 審查，非執行測試）：真相源（git+EP 對照）是否承載 intent？stall 定義（normal-exit≠done）在 solo 無 tick 是否可偵測？
- **R6 分工無重疊**：rg 驗證新段明確區分 batch ceiling / session-boundary review；跨檔（build.md、acceptance-evidence.md）引用一致
- **`/consistency`**：autonomous-execution/SKILL.md 自洽性（Self-Healing 與新 Recovery 段層級、職責不矛盾）
- **R3 deferred card 關聯**：確認新段標注回應 deferred card；收尾時評估更新 card

---

## 整合策略

- S1、S2 同改 `autonomous-execution/SKILL.md` 不同段（紅線 L36-43 vs Self-Healing L68-77），**段落順序**：S1 先（紅線段在文件較前），S2 後（Self-Healing 段較後），build 逐段不互相破壞
- 交叉引用：agent-workflow worktree 段（L62-74）加一行指回 S1 機械不變量子段
- R6 分工：S2 完成後，確認 build.md batch ceiling（L127）+ acceptance-evidence session-boundary（L154）的描述與新 Recovery 段不矛盾（必要時微調那兩處的「分工」一句）

---

## 收尾步驟（docs mode）

### 1. 受影響 skill 行為已反映
- `autonomous-execution/SKILL.md`：紅線段（機械不變量子段）+ Self-Healing 段（Session 級 Recovery）反映新能力
- `agent-workflow/SKILL.md`：worktree 段交叉引用已加
- **觸發詞同步（review #6）**：S1 workspace safety 不在現有 description 觸發詞（auto-discovery 對「worktree path safety」「workspace invariant」不會觸發本 skill）。**明確指定更新**：`autonomous-execution/SKILL.md` frontmatter `description` + `skills/CLAUDE.md` skill 索引 description 補觸發詞「workspace safety, path invariants, session recovery, false-done 偵測」（S2 recovery 可被既有「錯誤恢復」涵蓋，但 S1 需顯式補，否則 auto-discovery 漏）

### 2. kanban card 更新（元專案有 .kanban）
- **`.kanban/Backlog/session-boundary-intent-drift-review.md`**：S2 完成後評估——標記「部分落地（resume 機械觸發 + re-derive）」或關閉（若 S2 完整回應其诉求）
- 視需要為本 EP 建追蹤 card

### 3. instruction 檔品質
- 對 `autonomous-execution/SKILL.md` 跑 `/consistency`（自洽性、signal/noise）
- 確認新段落符合 instruction-writing（High Signal 設計理由、導航種子、無元資訊）

### 4. /audit-test
- docs mode 無新測試 → 跳過（正當跳過：無 .py 測試程式）

---

## EP Review Cycle（已執行）

Review agent（獨立 context，docs mode profile，top-down 先結構後正確性）+ `/judge-review` 全數採納。**無 Critical**。

| # | 嚴重度 | 信心 | 要點 | 採納 | 修正位置 |
|---|---|---|---|---|---|
| 1 | 🟡 Important | evidence | R1 真相源「EP 進度」用語模糊——intent 來自 EP 段落定義（靜態）非動態進度檔 | ✅ | S2 item 2 |
| 2 | 💡 Suggestion | evidence | R2「stall」命名誤導 → completeness validation / false-done + silent stall 限制 | ✅ | S2 item 1 |
| 3 | 💡 Suggestion | inferred | R6：S2 reconciliation（substrate 事實層）vs deferred card（review 判讀層）邊界顯式區分 | ✅ | S2 item 3 |
| 4 | 💡 Suggestion | evidence | Symphony 表 crash-only（episodic）vs supervisor（continuous）表面矛盾加註 | ✅ | 段落 0 表 |
| 5 | 💡 Suggestion | evidence | S1 item #3 EnterWorktree 是建立時行為，標記與 #1/#2 執行時區分 | ✅ | S1 item 3 |
| 6 | 💡 Suggestion | inferred | frontmatter + 索引 description 補 workspace safety / session recovery 觸發詞 | ✅ | 收尾 item 1 |

**結構判斷（review）**：EP 整體穩固可 build。recovery + workspace 進 autonomous-execution 的 single-source 論證成立（items #1/#2 執行時不變量 + S2 Self-Healing 擴展，均為 in-worktree 自主執行代理消費）；R6 三方分工實質不重疊（completeness / fatigue / direction 三軸）；Symphony 適配判斷正確（思想移植非載體移植）；R4 誠實標記 + hook 分期合理；引用 5 處行號 + deferred card 全部驗證準確。
