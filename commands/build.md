---
description: "基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號]"
when_to_use: "Implement an Execution Plan segment-by-segment using TDD. Use after /execution-plan (with built-in EP Review). Supports parallel agents with --max-agents."
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [段落編號] [--max-agents N | -a N]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent", "Workflow"]
---

# /build — 基於 Execution Plan 逐段實作

基於 Execution Plan 進行逐段實作。每個段落都是 Self-Contained Segment，獨立實作、測試、驗證。

**自主實作模式**：EP 已經過 EP Review Cycle 充分審查（內建於 `/execution-plan`），實作階段自主執行。自主決策、錯誤自癒遵循 [autonomous-execution](../skills/autonomous-execution/SKILL.md)。

委託 Skills（實作時提供方法論）：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [test-driven-development](../skills/test-driven-development/SKILL.md) — TDD 循環
- [incremental-implementation](../skills/incremental-implementation/SKILL.md) — 範圍紀律
- [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md) — 系統化除錯
- [autonomous-execution](../skills/autonomous-execution/SKILL.md) — 自主決策框架
- [python-type-gap](../skills/python-type-gap/SKILL.md) — 第三方套件 type gap（mypy 失敗時）
- [agent-workflow](../skills/agent-workflow/SKILL.md) — 並發控制、模型偵測、Agent spawn 規範

Workflow 審查協調：[workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)（Ultracode 下 Phase 4 使用）

---

## 執行流程

### 階段 0：EP 快檢

快速確認 EP 品質，**僅嚴重矛盾才停下**，其餘自行判斷並記錄。

**強制輸出**：快檢完成後必須印出 `## EP 快檢：✅ 可實作` 或 `## EP 快檢：⚠️ N 項自行補充`。不得靜默跳過。

**前置流程確認**（僅記錄，不因此停下）：`/spec（純輔助·需求釐清，可選）→ /execution-plan（自足，含 EP Review）→ [/ep-validate] → /build`

**docs mode 偵測**：掃描 EP 檔頭是否有 docs mode 聲明（變更全為 `.md` 且無新增/修改 `.py` callable 符號）→ 標記本 EP 為 docs mode，後續階段 2/3 依 docs mode 分支跳過 TDD/mypy/pytest，改 rg 殘留 + 一致性（完整對照見 [execution-plan.md](./execution-plan.md) docs mode）。

**EP 品質快掃**：

| 檢查項目 | 通過標準 | 發現問題時 |
|----------|----------|------------|
| 段落結構 | 每段有 Context、Pseudo Code、驗證策略 | 標記缺漏，自行補上 |
| Pseudo Code 可執行性 | 具體到可翻譯為程式碼 | 標記模糊處，自行推斷 |
| 驗證策略具體性 | 有明確測試案例 | 自行補充合理測試 |
| 依賴錨點有效性 | file:line 與實際程式碼一致 | drift 時先更新 EP |
| 兜底宣稱路徑 | EP「X 段暴露/處理 Y」宣稱附 X→Y call chain 證據（path:line） | 路徑未驗證 → flag（計入「⚠️ N 項自行補充」），Y 須獨立調查 |
| EP Review 修正 | 掃描 EP review 區段(`## EP Review Findings` 表格,見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)),納入實作 | 列入快檢報告 |
| **ep_type 偵測** | **機械掃描** `> **ep_type**:` 欄位（非語義字眼掃描 — 避免描述 blueprint 概念的 implementation EP 自指誤判；預設 implementation） | **blueprint → 不直接 /build**：提示「逐段衍生子 EP」（列段落 + 建議子 EP 路徑 + build 順序），**不腦補**藍圖段落為實作段落（修段落缺 Pseudo Code 時「自行補上」的腦補災難路徑）；implementation → 正常逐段 |

**平行可行性分析**：
1. 建構段落依賴圖，識別可平行段落
2. 套用 max-agents 限制（預設 3，可透過 `--max-agents N` 或 `-a N` 覆蓋）
3. **有語義約束的段落強制序列**

**整合器段落識別**（驅動階段 2 硬閘門、階段 3 真實邊界的觸發）：掃描 EP 段落，標記同時滿足以下者為整合器型（見 [quality-constraints](../rules/quality-constraints.md)「整合器型變更判定」）：

- 主要價值是把 ≥2 個真實外部組件接起來（DB、catalog、SDK、跨進程、跨框架）
- 邊界正確性無法從任一單方文件推導
- 錯了不是調參數而是整天行為全錯

**機械 IO 觸發（三條件的 OR 補充，降 LLM 單點）**：段落 diff 觸及真實 IO 模式（parquet/檔案讀寫、DB 連線、第三方 SDK 呼叫、跨進程/跨框架邊界）→ 即使三條件判「非整合器型」，仍標「**待真實邊界評估**」，交階段 3 確認是否真需要真實邊界。候選撈取 → LLM 裁決兩段式（非硬卡）。排除：純 config/fixture 讀取（非整合器，避免 false positive 稀釋信號）。

整合器型段落標記後，在階段 2/3 對應加嚴（路徑覆蓋硬閘門 + 真實邊界整合測試）。

### 階段 1：準備

**前置：working tree 乾淨度檢查**：`git status` 確認 working tree 變更都屬於本 EP 範圍。若有**其他功能的 untracked/modified 檔**（與本 EP 無關）→ 提示隔離（`EnterWorktree` / 新 branch / 先 commit 或 stash 舊功能），避免 build/commit 時混入不相關變更（靠 `/commit` 階段 2 git status 兜底，但前置隔離更省事）。

1. 讀取 Execution Plan，識別段落結構、依賴關係
2. **Kanban 狀態更新**：掃描 EP 中引用的能力描述，將對應的 `.kanban/Backlog/` cards 搬至 `.kanban/In-Progress/`（反映「正在做」的暫時狀態；搬至 Done/ 在 `/commit` 確認後才執行）
3. **深度查證現有程式碼**（不同於階段 0 的 drift 快掃，此處是理解程式碼上下文與設計意圖）。LSP `goToDefinition` 驗證 dependency anchors 的定義端，`findReferences` 驗證消費端，`hover` 確認關鍵參數型別
4. **POC + demo 盤點**：掃描 `poc/**/*.py`、`demo_*.py`、`scripts/demo_*.py`、`notebooks/*.ipynb`，建立 `{module} → [poc/demo paths]` 映射表
5. 檢查清單：Kanban InProgress ✓ | POC/demo 映射表 ✓ | 測試檔案 ✓ | CLAUDE.md 同步 ✓ | 依賴完整 ✓

### 階段 2：逐段實作

**EP 段落元素 → TDD 步驟**：

| EP 元素 | TDD 步驟 | 說明 |
|---------|---------|------|
| Context | 開始前讀取 | 理解背景 |
| 驗證策略 | RED | 讀 EP 測試類型 → 分類情境 → 寫對應測試（測試類型選擇紀律見 [validation-strategy](../skills/validation-strategy/SKILL.md)：e2e 優先 / 交易 replay >>> live / 放 scripts/ / 不重驗 pkg；詳 TDD skill EP Integration） |
| Pseudo Code | GREEN | 照設計實作 |
| 核心要點 | REFACTOR | 對 EP 完成檢查逐項驗證 |

**POC → RED 測試銜接**：若本段有對應的 POC（檔頭 `EP 段落:` 標注本段），優先將其「提煉改寫」成該段 RED 測試，非另起爐灶 —— POC 先於 impl、獨立產生（時間獨立性），改寫保留其驗證意圖。「提煉改寫」= 提煉 POC 的驗證意圖（斷言什麼行為）→ 寫成 pytest test function，assert 的對象（被測函數）尚未實作 → 確保 RED 狀態；**非把 POC 整段貼進 test file**（POC 已跑通非 fail）。

#### 平行模式

**Pre-flight**：有 uncommitted changes 是 Agent dependency → 先 commit；branch 不正確 → 先 checkout

**max-agents > 1 且有可平行段落**時：
1. 依賴圖分層為 waves
2. 同 wave 平行 Agent（上限 max-agents）
3. Wave 合併：讀取 Agent 產出 → 應用到主 worktree → `ruff check --fix && ruff format`
4. **Agent 產出機械驗證**（agent 自述是 L2 同義反覆風險、`git diff` 是 L1 機械證據，見 [acceptance-evidence](../rules/acceptance-evidence.md)）：
   - `git diff --name-only` 列實際變更檔（機械事實）
   - 比對各 Agent 自述「改了哪些檔 / 幾處」vs git 實際 → flag mismatch（**稱「零修改」但 git 顯示有改**最危險，曾釀 scope-creep 近乎 ship）
   - scope-creep：diff 檔是否超出該 Agent prompt 指定 scope → flag 超出（附 prompt scope 引用）
   - mismatch / scope-creep → 列為 finding 進階段 4 Agent Review，**不靜默採信自述**

**Agent Context 邊界**：Agent 看不到主對話歷史、其他 Agent 結果、EP 準備結論。**主 LLM 的 prompt 是 Agent 理解任務的唯一來源。**

**Agent Prompt 必須包含**：
- EP 段落完整內容（Context + Pseudo Code + 驗證策略 + 核心要點）
- 準備階段結論（現有程式碼狀態、架構決策）
- 語義約束
- POC/demo 映射（Agent 回報前必須執行至少一個 demo 驗證）
- 相關檔案路徑（必讀 / 可修改 / 禁止修改）
- Skills invoke 指示（rules-reminder, test-driven-development, incremental-implementation, autonomous-execution）

#### EP 專屬約束

> **EP 是收斂方向，不是合約**。EP 是規劃層對需求理解的最佳猜測，有預見極限（見 [acceptance-evidence](../rules/acceptance-evidence.md)「認知誤差與 EP 的預見極限」）— 實作落差、設計本身錯，都只能在實作呈現時發現。前線實作 LLM 有裁量權根據實作發現調整；死守 EP 會實作「忠實但錯誤」的東西，反而妨礙人類在呈現時發現認知誤差。

- **EP 為收斂方向，實作層有裁量權**：照 EP 為主軸，但實作時發現 EP 預見極限外的真相（邊界、副作用、組件互動、需求落差）可調整 — 這是「發現真相的責任」而非「偷懶不照 EP」
- 記錄偏差：與 Pseudo Code 有出入時記錄原因（偏差是發現認知誤差的線索，不是違規）
- 記錄疑慮不中斷：先選最合理方案繼續，最後統一讓用戶確認
- 錯誤自癒：連續 3 次失敗 → 標記 ⚠️ 繼續下一段
- **依賴錨點 drift check**：實作每段前驗證錨點，drift 時先更新 EP

#### 驗證

每段完成後：**整合路徑覆蓋檢查** → `ruff check --fix && ruff format` → LSP diagnostics（即時型別檢查）→ `mypy .`（完整驗證）→ `pytest <test> -v`（背景跑）→ POC/demo 驗證

> ⚠️ **mypy/pytest 閘門禁 `| tail/grep`**（exit code 被遮蔽 → 誤判通過，見 [bash-hard-rules](../rules/bash-hard-rules.md)）；看 output 重導檔案再 Read。

> **docs mode**：跳過 TDD（RED/GREEN/REFACTOR）、mypy/ruff/pytest、整合路徑覆蓋；改執行「修改 → rg 殘留 → 跨檔一致性 → `/consistency`」。

**整合路徑覆蓋檢查**（機械式硬閘門，見 [acceptance-evidence](../rules/acceptance-evidence.md) L3 + [quality-constraints](../rules/quality-constraints.md) 符號 vs 路徑覆蓋）：本段是否新增/修改 callable 簽名（新參數、新 keyword）或新增注入點（constructor 接受新依賴）？

- 否 → 跳過
- 是 → 對每個新參數/注入點 `rg "<param>=" tests/`
  - **0 hits → 該段不得 pass**，必須先補消費端整合測試（驅動真實消費端流程 + 新參數組合路徑，非僅符號 import）
  - 有 hits → 確認 hits 是「驅動消費端流程」的測試，而非僅符號 import

### 階段 3：整合驗證

> **scope 邊界（階段 2 vs 階段 3）**：階段 2 抓「新參數/注入點的接線路徑」（機械 rg 初篩）；階段 3 抓「既有接線的行為正確性」（需真實邊界跑）。**鐵律：階段 2 rg 有 hits ≠ 階段 3 真實邊界已滿足** — 符號出現在 tests（如被測單元自己的單元測試）≠ 消費端驅動該符號的路徑被覆蓋。例（真實歷史案例）：`rg "<符號>=" tests/` 有 hits 但全在被測單元自己的測試，消費端 integration 路徑不存在 — 符號有測 ≠ 消費路徑有測，bug 漏到補 integration test 才抓到。

全量 Lint + mypy + pytest（背景跑）+ POC/demo 全量驗證。全量跑只是 baseline。

> **docs mode**：跳過全量 mypy/pytest，改全量 rg 殘留 + `/consistency`。

**整合器型段落必須有真實邊界整合測試**（見 [quality-constraints](../rules/quality-constraints.md)「整合器型變更判定」+「兩層整合測試」）：主要價值是接 ≥2 個真實外部組件的段落，完成定義必須含接線 guard（`unit_tests/`）+ 真實邊界（`integration_tests/`），不能只靠 mock — mock 循環論證會讓 mock 假設即 bug 來源。

### 階段 4：Agent Review Cycle

**Writer/Reviewer 分離**：用獨立 Agent context 做品質閘門，避免主 LLM 審查自己的 code。
review 執行預設（force 獨立 / max-agents 預設 3 / model inherit / 3-perspective）見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」—— 本段僅定義 build 特有流程。**3-perspective**（① clean + ② UC-anchored + ③ Correctness，多樣性 > 數量）完整設計見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)。

#### Step 1: 確認 max-agents

`--max-agents N` 或 `-a N` 參數控制平行 Agent 數量（預設 3，見 review-engine review 執行預設）。用戶可手動調整。
印出確認：`[Review Agent] max=N`

> **classifier unavailable**（spawn 收 note、無 findings）→ **重試 spawn ≤ 2 次**（間歇常成功），非直接降級主 LLM 自審（會丟失獨立 review）；仍失敗才降級 + 顯式標記 fallback。完整處置見 [agent-workflow](../skills/agent-workflow/SKILL.md)「Auto Mode」+「spawn 失敗階梯」（429 / continuous）。

#### Step 2: 選擇審查模式

審查模式判定規則（effort/max-agents → Workflow/Agent Tool/Main LLM）見 [review-engine](../skills/review-engine/SKILL.md)。偵測 effort level，印出確認：`[Review Mode] effort=ultracode, workflow=true, max=N` 或 `[Review Mode] effort=standard, workflow=false, max=N`

**A. Workflow 模式**（判定條件見 [review-engine](../skills/review-engine/SKILL.md)）：

用 Workflow tool 協調 3-perspective（① clean + ② UC-anchored + ③ Correctness；perspective 定義 + prompt 見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)）；腳本骨架、DimensionVerdict schema、adversarial verify 見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)。

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 3 perspective agents（max-agents<3 時依 [agent-review-cycle](./claude/_common/agent-review-cycle.md) 降級序：Correctness > clean > UC） | ≤ max-agents |
| Verify | Critical findings → 3 verifier + ≥2/3 quorum | 3 × critical findings |

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 進入「/judge-review」步驟（現有流程不變）。

##### Workflow 執行行為（官方文檔對齊）

- **可恢復**：workflow 被中斷（user stop / 429 序列化）可同 session resume —— 已完成 agent 回快取結果、其餘 live 重跑（`/workflows` → 選執行 → `p`）。under `/deep-work` 多階段 loop 中，每階段 workflow 各自可 resume。
- **監控**：review workflow 背景跑時用 `/workflows` 看階段 / agent 計數 / 令牌。under `/deep-work` 雙視角：`claude agents`（session 層）+ `/workflows`（workflow 層）。
- **acceptEdits-always**：workflow 生成的 subagent **始終在 acceptEdits 執行，無視 session mode**（[官方 workflows 文檔](https://code.claude.com/docs/zh-TW/workflows)）。目前 review agent 全 `Explore`（read-only）無風險；若未來 build 經 workflow spawn impl agent，**edit 會繞過 session 權限自動准** —— 自主路徑（`/deep-work` + auto-mode）下，classifier + acceptEdits 是唯一防線，須知會。

**B. Agent Tool 模式**（Fallback，非 Workflow 條件 = max-agents=1 或非 ultracode）：build 的 Agent Review force 獨立 agent、不走 Main LLM（review 執行預設 + 刻意覆蓋通用判定，見 [review-engine](../skills/review-engine/SKILL.md)）。3-perspective（① clean + ② UC-anchored + ③ Correctness）完整流程見 [agent-review-cycle.md](./claude/_common/agent-review-cycle.md)。

#### adaptive 觸發映射（extra agent 機械觸發）

base ① clean + ② UC-anchored + ③ Correctness 之外，extra agent 由**段落風險特徵機械觸發**（非 LLM 語義判「高風險」）。映射框架定義見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」點 5；build 提供 adapter 信號翻譯成通用特徵：

| build 既有信號 | review-engine 通用特徵 | 觸發 extra agent |
|------------------|----------------------|-----------------|
| 階段 0 整合器標記（機械 IO 觸發，`:63`） | `外部整合` | adversarial |
| 階段 2 路徑覆蓋觸發（新簽名/注入點，`:132`） | `公開簽名變更` | architecture + consumer-perspective |
| EP UC 盤點計數 >6（半機械：LLM 數 EP UC 清單，非純 diff） | `UC 數 >6` | UC-split |

**範圍（只接線既有信號，不新造偵測）**：build adapter 只翻譯上表兩個既有機械信號（IO + 簽名）+ EP UC 計數。**無特徵命中 → 僅 base ①+②，不開 extra**（機械避免浪費，非 LLM 判）。**跨模組特徵在 build 無 adapter**（無既有偵測，不新造；跨模組 ripple 交階段 6 layer 旗標導向 layer 2，不在 build 段落自檢 — 同 session 看不全跨模組 ripple）。

**依賴方向（DIP）**：build 是 adapter（提供特徵偵測 + 翻譯成通用特徵名）；review-engine 是 domain（定義特徵→agent 映射）。build 引用 review-engine 通用特徵名，review-engine 不列 build 特有名詞。

**cap + 優先序**：extra 受 max-agents cap + 優先序（見 review-engine 點 5：architecture > adversarial/edge > consumer-perspective）；多特徵命中 + cap 不足時依序取最高，截斷其餘並輸出截斷提示：

> ⚠️ cap 截斷：max-agents=N，base 佔 3，僅 (N-3) extra 額度。命中 [特徵清單]，取 [最高優先 agent]，其餘 [被截斷 agent] 截斷 — 建議提高 `--max-agents` 或跑 `/code-review` 補截斷軸。

#### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

#### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修改 code。修改完跑 `ruff check --fix && ruff format`。

#### loop 迭代收斂（Loop engineering — apply 後 re-review）

apply 後**不是一輪結束**，而是 loop 迭代收斂（self-correcting）：apply 修正可能引入新問題或舊 finding 未修對 → re-review 確認。

1. **re-review**（同 base 3-perspective）審 apply 後的 diff
2. **pass 判定**：re-review findings **再 invoke /judge-review**（非主 LLM 自判，保 Writer/Reviewer 分離）
3. judge-review 有新 ✅ 採納 → 再 apply → re-review（迭代）
4. **收斂條件**：judge-review 無新 ✅ 採納（pass）或**達迭代上限 3 輪**（純防無限 loop，**與 base 3-perspective 的「3」無關**——兩個獨立的 3）

**達上限硬性處置**（loop 未收斂）：標 ⚠️「loop 未收斂（達 3 輪上限，仍有未修 finding）」+ **阻止 Capabilities/Kanban 升級**（階段 5 / `/commit` 升級條件加「loop 須收斂」）+ **layer 旗標導向 layer 2**（階段 6 layer 旗標條件加「loop 未收斂」）。

> **Loop engineering 邊界**：build 內 loop（base 3-perspective 補 Correctness lens 後）收斂「視角覆蓋內」的錯（邏輯邊界、語意、結構）；**同 session 盲點類**（設計假設、系統性偏誤）loop 結構性抓不到 → 階段 6 layer 旗標導向 layer 2（loop 外部收斂）。不假裝 build loop 全閉環。

### 階段 5：收尾步驟（EP 強制）

**執行 EP 收尾段定義的三項動作。未完成不得宣稱實作完成。**

**讀取 EP 收尾段**：EP 結構末段的「收尾步驟」定義了本 EP 的具體收尾範圍。讀取後按以下三項執行：

#### 5a. 消費場景提煅（大型/中型變更）

**委派** [metadata-sync](../skills/metadata-sync/SKILL.md) skill（build mode）的「消費場景提煅」子項——從 EP Scenario Matrix 提煉引用該 UC 的場景為自包含一句話（不引用 EP/SM 編號），暫存 build context 供 `/commit` 階段 3 寫入。

> Capabilities 表格更新 / Kanban 搬 Done 在 `/commit` 結算（build 提前做會造成永久狀態與程式碼不一致）；Kanban 搬 In-Progress/（暫時狀態）已在階段 1 完成。

#### 5b. SYSTEM-MAP 進度預覽（大型/中型變更）

**委派** [metadata-sync](../skills/metadata-sync/SKILL.md) skill（build mode）的「SYSTEM-MAP 預覽」子項——受影響功能生命週期 `📋→✅ Built`（全 UC ✅ + 測試通過 + build loop 收斂）；**不升級 Verified**（commit 才結算）；loop 未收斂（達 3 輪上限）→ 阻止升級 + 標 ⚠️。

> **為什麼委派**：SYSTEM-MAP 更新邏輯原在 build 5b 與 `/commit` 階段 3 兩處各列（drift）；收斂到 skill 單一源，build/commit 只是不同 mode（build 預覽 / commit 結算）。

#### 5c. CLAUDE.md + architecture.md 更新（大型/中型變更）

> **為什麼兩份一起**：CLAUDE.md（what / where）與 architecture.md（why / whole-picture）同為導航文檔（見 [ai-development-guide](../ai-development-guide.md) 文檔體系）。涉及設計變更時兩份都要看，避免 architecture.md 漂移成 LLM 讀不到現狀設計。純 feature（不改設計）只更 CLAUDE.md。

1. **識別受影響模組**：從 git diff 中找出變更檔案所在目錄及上層目錄的 CLAUDE.md
2. **檢查更新需求**：變更是否影響 CLAUDE.md 中描述的架構、模組職責、導航指引、可複用基礎設施
3. **更新 CLAUDE.md**：新增/修改受影響段落，遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準（Signal/Noise ratio、導航優先、禁止元資訊）
4. **更新 architecture.md（若專案有此檔）**：本次變更若涉及**設計決策 / 設計原則 / 模組結構 / 新抽象層**，同步更新對應段落（新增原則、調整 data flow、模組職責表）。純 feature 實作（不改設計）跳過。

#### 5d. /audit-test（所有變更）

執行 `/audit-test` 對新增/修改的測試進行品質稽核（階段 2 已逐段檢查整合路徑覆蓋，此處複驗整體 + 其他角度如反模式、mock 健康度、測試必要性）。稽核結果附於完成報告。

**小型變更**（bug fix）：僅執行 5d（/audit-test），跳過 5a、5b、5c、5e。

#### 5e. 導航文檔 /consistency 品質閘門（大型/中型變更）

> **核心原則**：導航文檔（CLAUDE.md / architecture.md / SYSTEM-MAP.md，見 [ai-development-guide](../ai-development-guide.md) 文檔體系）任一份內部 drift 都誤導 LLM。本次修改過的導航文檔必須通過單檔自洽閘門。

1. 對 5b（SYSTEM-MAP.md）、5c（CLAUDE.md / architecture.md）**本次修改過**的文檔，逐一執行 `/consistency <doc>`（單檔內部自洽：術語 / 章節 / 引用 / 邏輯 / 格式）
2. 🔴 / 🟡 inconsistency → 修正後才算 build 收尾（不把不一致文檔留給 `/commit`）
3. **scope 邊界**：/consistency 是單檔內部自洽，**非跨檔**。跨文檔一致性（三份互相矛盾）由 `/doc-health`（maintain Phase 3）處理，非本步驟

### 階段 6：完成報告

輸出：實作結果（新增/修改檔案）+ 架構決策記錄 + 待確認清單 + 未解決問題 + Agent 統計（平行模式）+ Agent Review 結果摘要 + 能力狀態變更摘要 + SYSTEM-MAP 功能狀態變更 + architecture.md 設計變更（若有）+ /consistency 導航文檔結果 + /audit-test 稽核結果

**layer 旗標（硬性 — commit 前方向提示）**：偵測本 EP 變更是否觸及**跨模組**（`git diff --name-only` top-level 模組目錄計數 ≥2；模組目錄 = 專案 bounded context 根目錄，各專案自訂）、**公開簽名變更**（階段 2 路徑覆蓋觸發）、**整合器段落**（階段 0 標記）、或 **build loop 未收斂**（階段 4 達 3 輪上限）。命中 → 完成報告必含：

> ⚠️ 本 build 僅 layer 1（AI 自洽天花板）。此變更觸及 [跨模組/公開簽名/外部整合]，**建議跑跨 session `/code-review`（layer 2）** 抓全貌漣漪 / 同 session 盲點（段落自檢 + Agent Review 都是 layer 1，看不全跨模組 ripple）。

此旗標是**新增**硬性 code-review 導向提示；檔尾「與其他命令的協作」段的既有軟提醒（涵蓋 deliverable-review/illustrate/code-review）**保留不動**。

---

## 執行約束

### 強制

1. 必須先 EP 快檢
2. 必須完整讀取計畫書
3. 每段必須 TDD（RED → GREEN → REFACTOR）—— docs mode EP 除外
4. 每段必須獨立驗證（ruff + mypy + pytest）—— docs mode EP 除外（改 rg 殘留 + 跨檔一致性 + `/consistency`）
5. 禁止 `from __future__ import annotations`
6. 必須執行收尾步驟（階段 5）：大型/中型 → metadata-sync build mode 預覽（5a/5b：消費場景提煅 + SYSTEM-MAP 進度預覽）+ CLAUDE.md / architecture.md 內容同步（5c）+ /audit-test（5d）+ /consistency 導航文檔閘門（5e）；小型 → /audit-test（5d）

### 禁止

- ❌ 跳過測試直接實作
- ❌ 使用 `sed` 修改程式碼
- ❌ 段落範圍外修改
- ❌ 中間狀態提交破損程式碼
- ❌ 跳過收尾步驟宣稱完成

---

## 與其他命令的協作

```
/spec（純輔助·需求釐清，可選）→ /execution-plan（含 EP Review）→ [/ep-validate] → post-EP: /deliverable-review --ep（layer 3 方向）→ /illustrate --ep（layer 3 結構）→ /build（含 Agent Review + /audit-test, LLM 鏈）→ post-build（看狀況呼叫，不硬定先後）: /illustrate（layer 3 結構 viewport）/ /deliverable-review（layer 3 demo 交付）→ [/code-review] → /commit
```

**搭配 `/goal`**：啟動後設定 `all segments implemented, uv run pytest exits 0, ruff clean, mypy clean, all demos run` 搭配 auto mode 效果最佳。

> **Agent Review Cycle（LLM 鏈, layer 1）已完成。** 機器自驗天花板 = AI 自洽,commit 前建議跑 `/deliverable-review`（layer 3 demo 交付）跨越認知誤差、`/illustrate`（layer 3 結構 viewport）跨越重造盲點;如需 LLM 第二意見可跑獨立 `/code-review`（layer 1/2）。

---

## 語音通知

遵循 [voice-notification skill](../skills/voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始實作 EP"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「實作完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```
