# EP-C: 記憶紀律（STATE.md Last session 觀察層 + Skill 兩層判定）

> **ep_type**: implementation
> **mode**: docs（全 .md 變更，無 .py callable）
> **規模**: standard（跨 rule/command，中型）
> **來源**: Fable 5 gap analysis（洞見#9 STATE.md / #10 複利 Skills）+ 段落 0 研究 + EP Review（11 findings 採納，含 I-2 設計修正：Open failures 走 kanban）

## 實作總覽

補強 ai-rules 的**記憶紀律**。EP Review 後**設計修正**：原規劃 STATE.md 五區段裁剪為 2 區段，但 review（I-2）指出 **Open failures 非獨有**——`.kanban/Backlog/` 已是跨 session 未結案追蹤（deferred card 即證）。故：

- **STATE.md 縮減為僅 Last session 觀察層**（Open failures 走 kanban Backlog，failure card + repro body）。STATE.md 只承載「自己續工作的 session 主觀觀察」（卡在哪、為何轉向、下次起手點）——這是 /at（任務目標一句）/ handoff（外部一次性）/ kanban（任務追蹤）/ MEMORY.md（harness learnings）都沒有的。
- **A↔C 邊界**（核心）：STATE.md = 觀察層；EP-A S2 recovery = 事實層（git+EP re-derive）。**recovery 不依賴 STATE.md**。但「卡在哪/為何轉向」本質隱含 soft completion signal（轉向=未完成 X）——須 R4-style enforcement 誠實標記 + negative guidance（I-1）。
- **Skill 兩層判定**：落 `flow-review`，補 memory-routing 判定步驟（程序記憶跨專案→Skill vs 專案記憶→STATE/session），加機械 proxy。

---

## UC 盤點（docs mode）

### 受影響 rules/commands 清單

| 檔 | 段（行號） | 變更 | 段落 |
|---|---|---|---|
| `rules/context-management.md` | session 管理（全文 ~20 行） | 補「STATE.md Last session 觀察層」段（邊界 + 觸發 + A↔C enforcement + lifecycle + 路徑） | S1 |
| `commands/at.md` | context 寫入 + resume flow（**L33-117**，非 L33-37） | /at resume 時**讀** STATE.md 補 observation；`.at-contexts` 維持一次性 lifecycle（**不取代**，I-3） | S1 |
| `commands/handoff.md` | **L20-27 `/at` 邊界表**（非 L48-52 schema，I-S3） | 邊界表**下方加 note**（STATE.md 非交接選項；第二輪 review #1：表格行→note，保留 either/or 語義） | S1 |
| `commands/deep-work.md` | completion report（L117-128） | 承接 STATE.md Last session 觀察寫入 | S1 |
| `commands/flow-review.md` | 聚合分析（L23-27）後、決策段（L34-42）前 | 補「memory-routing 判定」子步驟（與 action-routing 正交，I-S2） | S2 |
| `commands/instruction/_common/` | （新共享段） | `state-md-write.md`——STATE.md 寫入步驟共享（DRY，防 3 處 drift，I-S5） | S1 |

### Capabilities / kanban / SYSTEM-MAP
- 元專案無 Capabilities / SYSTEM-MAP → 跳過（正當）
- **EP-A 關係**：EP-C **不改 EP-A**（單向引用：context-management.md → EP-A 文檔；recovery 不讀 STATE.md，EP-A 讀者不需知 STATE.md 存在）。UC 表不列 EP-A 為變更對象（消除 I-4 矛盾）。

---

## Scenario Matrix（docs mode）

| # | 場景 | 觸發 | 預期行為（rg 驗證） | 對應 |
|---|---|---|---|---|
| SM-1 | session 結束（/at/handoff/deep-work 收尾） | 離開前 | 寫 STATE.md Last session 觀察（卡在哪、為何轉向、下次起手點），**嚴守 negative guidance**（✗ 不寫完成度，I-1） | S1 |
| SM-2 | 新 session resume | 開場 | 讀 STATE.md（session 觀察）；**recovery 完成度走 EP-A git+EP re-derive**，STATE 僅供「為什麼」參考 | S1 |
| SM-3 | 跨 session 未結案 failure（bug 沒修完+repro） | Open failures 場景 | **走 kanban Backlog**（failure card + repro body），**不進 STATE.md**（I-2 修正） | S1 |
| SM-4 | flow-review 讀累積教訓 | memory-routing 判定 | 教訓→{跨專案通用→Skill；專案特定→STATE/session；一次性→棄}，**先判記憶去向再判 action 去向**（I-S2） | S2 |
| SM-5 | STATE.md Last session 觀察隱含完成度信號 | resume 讀 STATE | **A↔C enforcement**（I-1）：recovery 以 EP-A git+EP 事實為準；STATE 觀察僅供意圖參考，**不覆蓋完成度事實**；negative guidance 範例防寫入完成度 | S1 |
| SM-6 | STATE.md 膨脹（多 session 累積） | 生命周期觸發 | **Last session 每次 session 結束覆寫**（非累積）；增長上限由 context-management 約束（I-5） | S1 |

---

## 段落 0：全域研究摘要

### 既有記憶載體職責矩陣（review 修正後）

| 載體 | 職責 | 真相源性質 |
|---|---|---|
| `/handoff`（L20-27 邊界表） | self-contained 交接 prompt（交**另一個** session/repo） | 一次性外部產出 |
| `/at`（L33-117） | 排程 resume，記任務目標，靠 git 推斷進度；`.at-contexts` 一次性 ephemeral | 一次性、session-only |
| auto MEMORY.md | Claude harness-native 自記 learnings（**非 ai-rules 紀律驅動**，I-S4 論證修正） | harness 管理，per-repo |
| **kanban Backlog** | **跨 session 未結案追蹤**（deferred card 即證）—— **Open failures 走此**（I-2） | git-tracked 任務追蹤 |
| `context-management.md` | /clear 重置原則 | 純原則，無載體 |
| flow-feedback→flow-review | session 摩擦→聚合→改 skills/commands | action-routing 迴圈 |
| **STATE.md（本 EP）** | **Last session 觀察**（自己續的 session 主觀） | **觀察層**（非事實層、非任務層） |

### STATE.md 邊界（review I-2 修正：縮減）

原 Fable 五區段 → review 後 **STATE.md 只承載 Last session 觀察**：

| 原區段 | 裁剪決策（review 修正） |
|---|---|
| ~~Open failures~~ | **移除 → 走 kanban Backlog**（I-2：kanban 已是跨 session 未結案追蹤；failure+repro 成 kanban card） |
| Last session | **保留為「觀察層」**（卡在哪、為何轉向、下次起手點） |
| ~~General rules/Verified facts/Lessons~~ | 裁掉（rules always-loaded；MEMORY.md harness-native 已有事實記憶——I-S4：非「與 ai-rules 載體重疊」，而是「harness 已有事實記憶，STATE.md 不重造」） |

### A↔C 張力 + 化解（R2，核心 + I-1 enforcement gap）

**張力**：EP-A S2「不依賴顯式標記 / builder 不需先讀進度追蹤檔」（L169-170）。STATE.md 是「past session 寫的檔」，resume 讀它觸碰 EP-A 精神。更深（I-1）：「卡在哪/為何轉向」**本質隱含 soft completion signal**（轉向=未完成 X），resume LLM 讀到不會做觀察/事實區分——正是 EP-A「靠自覺最不可靠」的失敗模式。

**化解（職責正交 + enforcement 誠實）**：
- EP-A S2 = **事實層**（git+EP re-derive 完成度，機械可信）
- STATE.md = **觀察層**（session 主觀：卡在哪、為何轉向；**禁含完成度宣稱**）
- **enforcement 誠實（I-1，R4-style）**：「禁含完成度」是 docs-mode 紀律（**指導非強制**，無 schema enforce），誠實標記如同 EP-A R4。未來機械補強方向：STATE.md schema 無完成度欄位 / resume re-derive 前不讀 STATE 的流程約束。
- **negative guidance 範例**（I-1）：✗ 不寫「segment 3 未完成、做到一半」；✓ 寫「retry 間隔計算產生 0，推測 BackoffCalculator 邊界條件」（觀察，非進度）

### STATE.md 生命周期 + 路徑（I-5/I-6）

- **生命周期（I-5）**：Last session **每次 session 結束覆寫**（非累積多 session）；增長上限由 context-management 約束（單一 session 觀察不膨脹）
- **路徑（I-6）**：repo root `STATE.md`（**避開 `.claude/` protected path**——auto-mode 下 /at/deep-work 寫入會被擋，at.md L39 已踩過）；**per-project 語義**（每個消費專案自己的 session 觀察，非 ai-rules 統一）；gitignore 決策由各專案（本地 session 觀察，default gitignore）

### 風險假設（R1-R3，review 後）
- **R1（載體重疊）**：已化解——STATE.md 縮減為僅 Last session 觀察（獨有）；Open failures 走 kanban（I-2）
- **R2（A↔C 張力）**：觀察層 vs 事實層正交 + R4-style enforcement 誠實 + negative guidance（I-1）
- **R3（Skill 兩層判定準則）**：機械 proxy + 具體準則（見 S2）

---

## 段落劃分原則

- **S1 STATE.md Last session 觀察層先**：核心（縮減 + A↔C enforcement + lifecycle/路徑 + /at 不取代）
- **S2 Skill 兩層判定後**：memory-routing（程序→Skill vs 專案→STATE，S1 是其下游落點之一）
- S2 引用 S1（專案記憶落點 = STATE.md）

---

## S1：STATE.md Last session 觀察層

### Context

**UC 引用**：補強「session 跨越記憶」——輕量 Last session 觀察層（Open failures 已走 kanban）。

**背景**：Fable STATE.md 五區段是 team 場景。solo 場景 review 後縮減：Open failures 走 kanban（I-2，非獨有）；STATE.md 只 Last session 觀察（自己續的 session 主觀，補 /at/handoff/kanban/MEMORY.md 都沒有的）。

**依賴錨點**：
- context-management rule → 定義 `rules/context-management.md` / S1 補 STATE.md 段
- /at resume flow → 定義 `commands/at.md:33-117`（I-3 行號修正）/ S1：resume 讀 STATE 補 observation，**不取代 .at-contexts**
- handoff 邊界表 → 定義 `commands/handoff.md:20-27`（I-S3 落點修正）/ S1 加第三行
- deep-work completion report → 定義 `commands/deep-work.md:117-128` / S1 承接寫入
- kanban Backlog → 定義 `.kanban/Backlog/` / S1 標 Open failures 走此（I-2）

**語義約束**：與 EP-A 共享「事實層 vs 觀察層正交」（A↔C，I-1 enforcement）；與 S2 共享「專案記憶落點 = STATE.md」。

**成功標準**：context-management 含 STATE.md 段（縮減 Last session + A↔C enforcement R4-style + negative guidance + lifecycle + 路徑）；/at resume 讀 STATE 不取代 .at-contexts；Open failures 走 kanban。

### 修改要點（docs mode）

1. **context-management.md 補「STATE.md Last session 觀察層」段**：
   - **裁剪定義**：STATE.md 只承載 **Last session 觀察**（卡在哪、為何轉向、下次起手點）。**Open failures 走 kanban Backlog**（I-2，failure+repro 成 kanban card）。**禁含完成度宣稱**（A↔C）。
   - **A↔C enforcement（I-1，R4-style）**：「禁含完成度」是 docs-mode 紀律（**指導非強制**），誠實標記；未來機械補強（schema 無完成度欄 / resume re-derive 前不讀 STATE）。**negative guidance 範例**：✗「segment 3 未完成」/ ✓「retry 間隔算出 0，推測 BackoffCalculator 邊界」。
   - **A↔C 邊界聲明**：STATE.md = 觀察層；EP-A S2 recovery = 事實層（git+EP re-derive）。**recovery 不依賴 STATE.md**——STATE 僅補「為什麼」，不覆蓋「做到哪」。
   - **生命周期（I-5）**：Last session **每次 session 結束覆寫**（非累積）；增長上限約束。**首次 session 無 STATE.md = 正常，resume 跳過讀取**（第二輪 review #4）。
   - **路徑（I-6）**：repo root `STATE.md`（避 `.claude/` protected）；per-project 語義；gitignore 由各專案。
   - **職責矩陣**（防 R1）：rules=always-loaded；MEMORY.md=harness-native learnings；handoff=外部一次性；/at=任務目標；kanban=任務/未結案追蹤（含 Open failures）；**STATE.md=Last session 觀察（獨有）**。
   - **觸發**：「離開前寫」綁 session 結束（/at/handoff/deep-work 收尾）；「開場讀」綁 resume。
2. **/at（L33-117，I-3 行號修正）**：resume 時**讀** STATE.md 補 observation（自己續的 session 觀察）；**`.at-contexts` 維持一次性 ephemeral lifecycle**（session-only、resume 後刪、gitignore）——**不取代**（I-3：一次性 ephemeral vs 持久 STATE.md 是不同 lifecycle，不可混溶）。
3. **handoff（L20-27 邊界表，I-S3 + 第二輪 review #1）**：邊界表是「命令 either/or 決策」語義，STATE.md **不是命令**（非 /at/handoff 替代）→ **表格下方加 note 而非表格行**：「STATE.md（session 觀察累積）非交接選項；/at resume 時讀它補 observation，交接決策仍 /at vs /handoff」。
4. **deep-work（L117-128）**：completion report 步驟加「寫 STATE.md Last session 觀察」。
5. **DRY 共享段（I-S5）**：`commands/instruction/_common/state-md-write.md` 提取 STATE.md 寫入步驟（含 A↔C negative guidance）；/at、handoff、deep-work 引用而非各自重寫——A↔C 邊界紀律單一 enforce 點。

### 驗證策略（文檔驗證）

- **rg 殘留**：context-management 含 STATE.md 段（`rg "STATE.md|Last session|觀察層" rules/context-management.md`）
- **A↔C enforcement（I-1）**：確認含「指導非強制 / negative guidance / recovery 不依賴 STATE」（rg `指導非強制|negative guidance|不依賴|re-derive`）
- **I-2 Open failures→kanban**：確認 STATE.md 段標「Open failures 走 kanban」（rg `Open failures.*kanban|走 kanban`）
- **I-3 /at 不取代**：確認 /at 段「resume 讀 STATE / .at-contexts 維持」（rg `不取代|維持.*lifecycle|讀 STATE`）
- **I-5 lifecycle / I-6 路徑**：確認含「覆寫/累積 + repo root/per-project」（rg `覆寫|repo root|per-project`）
- **I-S5 DRY**：確認 _common/state-md-write.md 存在 + 3 命令引用
- **`/consistency`**：context-management.md 自洽性

---

## S2：Skill 兩層判定（flow-review memory-routing）

### Context

**UC 引用**：補強「教訓蒸餾」——flow-review 補 memory-routing 判定（與既有 action-routing 正交，I-S2）。

**背景**：Fable 洞見#10（複利 Skills）。基建已在（symlink 跨專案）。缺判定紀律。flow-review L34-42 現況是 **action-routing**（共識→去向：EP/kanban/留）；EP-C 加 **memory-routing**（教訓→記憶去向：Skill/STATE/棄）——兩軸正交（I-S2）。

**依賴錨點**：
- flow-review 聚合分析 → 定義 `commands/flow-review.md:23-27` / S2 在此後加 memory-routing（決策段 L34-42 前）
- flow-feedback type-2 → 定義 `commands/flow-feedback.md:32-39` / S2 上游
- S1 STATE.md → 定義 `rules/context-management.md`（S1 新段）/ S2 下游（專案記憶→STATE）

**語義約束**：與 S1 共享「專案記憶落點 = STATE.md」。

**成功標準**：flow-review 含 memory-routing 子步驟（與 action-routing 正交）；機械 proxy（I-S1）；準則具體。

### 修改要點（docs mode）

在 `flow-review.md` 聚合分析（L23-27）後、決策段（L34-42）前，加「memory-routing 判定」子步驟（I-S2：與 action-routing 正交，先判記憶去向再判 action 去向）：

1. **memory-routing 決策樹**（讀 flow-feedback 教訓時）：
   - **跨專案通用？** → **Skill**（程序記憶，symlink 跨專案）
   - **專案特定？** → **STATE.md / session**（專案記憶）
   - **一次性？** → **棄**
2. **機械 proxy（I-S1，降低預測隨意性）**：先看引用形態——教訓引用具體 module/class/file path → 專案特定候選；引用工具/流程/pattern 名 → 跨專案候選。再判通用性 + 重複性。
3. **基建已在聲明**：symlink 讓「寫進 Skill = 自動跨專案」——S2 補觸發判定，非基建。
4. **與 S1 呼應**：專案記憶落點 = STATE.md（S1 Last session 觀察）；程序記憶 = Skill。
5. **不替代人類判斷（B 軸）**：memory-routing 是結構化提示，最終 flow-review 人類討論定案（L51「不替人決定」）。

### 驗證策略（文檔驗證）

- **rg 殘留**：flow-review 含 memory-routing（`rg "memory-routing|程序記憶|專案記憶|跨專案.*通用" commands/flow-review.md`）
- **I-S1 機械 proxy**：確認含「引用形態 / module vs 工具」（rg `引用.*形態|module|工具`）
- **I-S2 正交**：確認 memory-routing 在 action-routing 前 + 標「正交」（rg `正交|先判.*記憶`）
- **B 軸不替代**：確認含「不替人決定」（rg）
- **`/consistency`**：flow-review.md 自洽性

---

## 整合策略

- S1（context-management + /at/handoff/deep-work + _common 共享段）、S2（flow-review）改不同檔，無衝突
- **A↔C 邊界**：S1 顯式聲明觀察層 vs EP-A 事實層正交 + R4-style enforcement；**EP-C 不改 EP-A**（單向引用 context-management → EP-A 文檔；recovery 不讀 STATE，EP-A 讀者不需知 STATE.md）——消除 I-4 矛盾
- **S2→S1 軟依賴**：S2 專案記憶落點 = STATE.md（S1）；build 時 S1 先
- **跨 EP**：EP-C 可獨立 build（單向引用 EP-A 文檔，不改 EP-A）

---

## 收尾步驟（docs mode）

### 1. 受影響 rule/command 行為已反映
- `rules/context-management.md`：STATE.md Last session 觀察層段
- `commands/flow-review.md`：memory-routing 子步驟
- `commands/at.md` / `handoff.md` / `deep-work.md`：STATE.md 讀寫承接（引用 _common 共享段）
- `commands/instruction/_common/state-md-write.md`：新共享段
- **觸發詞同步**：flow-review frontmatter description 補「memory-routing / Skill 兩層判定 / 程序記憶」；context-management（rule 無 frontmatter，但若索引提及）
- **commands/CLAUDE.md 命令索引（第二輪 review #2）**：/at、handoff、deep-work、flow-review description 確認反映 STATE.md 讀寫 / memory-routing 新行為（尤其 flow-review memory-routing 語義）

### 2. kanban / SYSTEM-MAP
- 元專案無對應 deferred card → 跳過
- 視需要為本 EP 建追蹤 card

### 3. instruction 檔品質
- 對 `context-management.md` + `flow-review.md` + `_common/state-md-write.md` 跑 `/consistency`
- 確認新段落符合 instruction-writing（High Signal、導航種子、無元資訊）

### 4. /audit-test
- docs mode 無新測試 → 跳過

---

## EP Review Cycle（已執行）

Review agent（獨立 context，docs profile，top-down）+ `/judge-review`。**無 🔴 Critical**。核心概念（觀察層正交 + Skill 兩層）成立，但 review 抓到系統性 enforcement + operational 缺口——全採納，**重寫 EP 整合 11 findings**（含 I-2 設計修正：Open failures 走 kanban，STATE.md 縮減）。

| # | 嚴重度 | 決策 | 要點 | 修正 |
|---|---|---|---|---|
| I-1 | 🟡 | ✅ | A↔C enforcement gap（無 R4-style 標記）+ 觀察隱含完成度信號 | S1 補 R4-style 誠實 + negative guidance |
| I-2 | 🟡 | ✅（設計修正） | Open failures 非獨有——kanban Backlog 已是跨 session 未結案追蹤 | STATE.md 縮減為僅 Last session；Open failures 走 kanban |
| I-3 | 🟡 | ✅ | /at lifecycle 混溶（ephemeral vs 持久）+ 行號 under-scope | /at 不取代 .at-contexts（resume 讀 STATE）；行號 L33-117 |
| I-4 | 🟡 | ✅ | UC 表 vs 整合策略「是否改 EP-A」矛盾 | EP-A 移出 UC 變更對象（單向引用，不改 EP-A） |
| I-5 | 🟡 | ✅ | STATE.md 生命周期未定義 | Last session 覆寫（非累積）+ 增長上限 |
| I-6 | 🟡 | ✅ | STATE.md 路徑未定義 | repo root STATE.md（避 .claude/ protected）+ per-project + gitignore |
| I-S1 | 💡 | ✅ | Skill 判定加機械 proxy | 引用形態（module vs 工具）先判 |
| I-S2 | 💡 | ✅ | flow-review 混入第二軸（action vs memory routing） | memory-routing 正交子步驟（聚合分析後、決策段前） |
| I-S3 | 💡 | ✅ | handoff 落點 L48-52 不如 L20-27 邊界表 | 邊界表加第三行 |
| I-S4 | 💡 | ✅ | MEMORY.md 論證（ai-rules 零引用） | 論證改「harness 已有事實記憶，STATE.md 不重造」 |
| I-S5 | 💡 | ✅ | STATE.md 寫入散布 3 命令 DRY drift | `_common/state-md-write.md` 共享段 |

**結構判斷（review）**：核心概念未被推翻，缺口在 S1 補段 + I-2 設計修正（STATE.md 縮減）。重寫後 STATE.md 為輕量 Last session 觀察層（Open failures 走 kanban），A↔C 用 R4-style enforcement + negative guidance 強化，lifecycle/路徑/DRY 補齊。
