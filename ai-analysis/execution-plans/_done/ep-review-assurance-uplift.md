# EP: solo+AI review guide → ai-rules rule/skill uplift（A1-A8）

> **ep_type**: implementation
> **docs mode**: ✅（變更全為 `.md` — rules/skills/commands，無 `.py` callable）
> **EP Review Cycle 已修正**（3 Explore agent · F1-F5 + Clean Arch top-down + 深層思考方向 push-back）。採納：F2-C1 neutral violation、F3-C1/DT-3 A5 重述+bookkeeping、DT-1 A3 過度工程降級、F4-🟡1/SC-2 A4 落點+跨 harness、DT-2 session-boundary、SC-1/3 場景補、polish 4 項；拒絕 DT-4（S4 不拆）。見末段 EP Review Findings。

## 實作總覽

**問題**：一份 solo+AI code review 研究 guide 對 ai-rules 做 8 維度 audit，4 confirmed_gap（A1/A2/A3/A8）+ 4 partial（A4/A5/A6/A7）。核心立場（guide 範式）：AI code 審查應從「檢查程式碼品質」轉為「驗證 AI 對系統模型的修改符合人類意圖」，且 **evidence 必須獨立於 AI**——silent corruption 情境下 AI 誠實說「沒影響」時最危險。8 個 finding 本質跨專案通用 → 上抽進 ai-rules rule/skill 層。

**A1 是樞紐**：runtime invariant assurance 同時收斂 silent-corruption 抓不到（D2）+ 人審上限（D5）+ AI claim 非獨立（D3）。A8（reviewer 認知上限）是 A1 的論證基礎（人審有結構上限→需 runtime 補）。兩者強配對。

**修復（落點分工，EP Review 後定案）**：
1. **acceptance-evidence.md 為樞紐檔 + 原則家**（承載 A1/A4-原則/A6/A7/A8）——所有**跨 harness 通用原則**落此（neutral rule，bundle 到非 Claude 端）。A1+A8（runtime assurance + 人審上限）一組；A6+A7（RED/session 邊界 + intent-drift Type B 訊號）一組；**A4 的 Claim→Evidence→Trust 原則**亦落此（EP Review F4-🟡1/SC-2：原則進 neutral 讓非 Claude 端讀得到，build.md 作 consumer 機制）。
2. **arch-thinking**（A2 mutation-path + A3 change-type triage）——review 結構機械，同檔 §二。**Claude-side mechanism**（skill 不 bundle）。
3. **build.md**（A4 機制命名+generalize + A5 complex-change trigger + A6 batch-ceiling）——**Claude-side mechanism**（command 不 bundle），引用 acceptance-evidence 原則非重述。
4. **cross-refs**（audit-test / deliverable-review / code-review-and-quality / ep-review）——引用樞紐，不重述。

**三主線**（arch-thinking）：① 依賴規則（原則 single-source 在 acceptance-evidence；A4/A5/A7 引用非重述）② bounded context（acceptance-evidence = 驗收證據/原則層；arch-thinking = 結構機械層；build = 流程閘門層）③ use case（消費者 = review/build 命令家族 + 所有 harness session）。

**關鍵約束**（貫穿全 EP）：
- **原則層表述，禁寫死統計**——guide 的 93.5%/60%/400-line/asymmetric drift 都是 research claim（上游 sourced-not-verified）。進 ai-rules 用原則，**禁數字**（對齊 `_ai-behavior-constraints`）。EP Review F2 確認：研究數字僅出現在 EP 約束聲明 + rg 指令，修改要點零 leak。
- **跨 harness 原則/機制 split**（EP Review SC-2）：neutral rule（acceptance-evidence）= 跨 harness 原則（所有 harness 讀得到）；skill/command = Claude-side 機制（不 bundle，非 Claude 端靠自家機制套用原則）。→ **通用原則（Claim→Evidence→Trust、runtime assurance、intent-drift）必須在 acceptance-evidence 有自帶可操作摘要，不可純引用 Claude-only skill/command**（否則非 Claude 端讀到「見 arch-thinking mutation-path」卻載入不到）。
- **mechanical-gate-philosophy 分歧處理**（EP Review DT-3）：`.kanban/Backlog/mechanical-gate-philosophy-hybrid.md`（已決策、skill 未建）論點「機械閘門 > LLM 自覺」正是 A1/A4/A5 調用。本 EP **不建該 skill**（scope）。A1 在 acceptance-evidence 落**具體機制**並一次確立原則；**A4/A5 純引用 A1 錨點非重述**（EP Review F3-C1 抓出 v1 A5 重述，已修）。三處（A1 錨 + A4 引用 + A5 引用）記入收尾 #8 待 skill 建成回收。
- **條件必填觸發**（A2 觸及 mutable state、A3 triage）：對齊 `execution-plan §1b`「條件必填」pattern，避免 leaf/純 docs 噪音。
- **A3 降級**（EP Review DT-1）：change-type 不作「第四深度軸」（過度工程——修缺陷→compensating-pair `arch-thinking:127-139` 已涵蓋，core/risk-tier 已決定深度，第四軸強迫 LLM 自覺加權=最弱形式）。降為 core identification 內**triage note**（Pain 0 本質：generated/rename/logging→放行；money-path/tribal→必審；其餘隨 core/leaf），非 depth-weighting axis。

---

## 段落 0：研究摘要（rg/LSP 查證 + Explore agent 盤點 + EP Review 校正）

**斷層查證（rg confirmed，精確 per-term；EP Review F1 重驗 20+ 錨點全準確）**：
- A1 runtime-monitoring 機制：`runtime monitor`/`Rushby`/`assurance case`/`live monitor` 全 **0 hits**；`silent corruption` 只在 `execution-plan §1b`（producer 自述）+ `arch-thinking:146`（module-tier 識別）—— runtime 持續保證層缺。
- A2 mutation-path：`code-review-and-quality:24` Correctness「state inconsistencies?」是 sniff 非 count；`arch-thinking:127-139` compensating-pair 方向相反（查「誰抵消 A 的 bug」），並列不重疊。
- A3 change-type：三軸確認（risk-tier=驗證深度 `acceptance-evidence:130` / simple-standard-full=planning-gate `execution-plan:42-52` / docs mode=product-type `execution-plan:251`）；selective-review-matrix（`arch-thinking:141-157`）{core,leaf}×{depth} 無 change-type 軸。**但 EP Review DT-1 判 change-type 邊際價值低（修缺陷→compensating-pair 已涵蓋），降為 triage note 非軸**。
- A4：`build.md:101-105` 直命中（agent 自述 vs git diff）；框架名「Claim→Evidence→Trust」0 hits。`ep-review.md:76`「漏列 invariant 無人查」= no-impact claim variant。
- A5：`build.md:65` escalation keyed to 整合器型（IO）；complex-change→constraint 加嚴 0 hits（Mechanism 1 gap）。
- A6：STOP gate covered（EP Review Cycle `execution-plan:288+`）；RED 強化 covered（`build.md:86-91`）；`build.md:124` 連續 3 次→繼續非 forced re-engage；`acceptance-evidence:118` RED 前移在「仍為設計方向」段；standup 是 activity digest 非 review。**EP Review DT-2：全 repo 無 cross-session intent-drift review 觸發機制**（/at=usage-resume、/handoff=交接、/standup=digest 皆非）——session-boundary 跨 session 場景無 trigger，原則效果限單 session batch-ceiling 軟觸發。
- A7：`acceptance-evidence:19-22` 兩型 = impl-discovery vs design-error（非 guide intent-drift Type A/B）；`audit-test` angle 1（靜態）+ angle 6（動態）= 2-signal 非 3-signal；`deliverable-review:141-145` Type A only；`fix-test:69-73` Type A/B = test-failure 分類（非 intent drift）。
- A8：`acceptance-evidence:133`「L6 疲勞漏看」泛用告誡；`code-review-and-quality:103`「不 rubber-stamp」態度處方。

**消費者清單（受影響檔，逐檔；EP Review F4 補 cross-harness 標註）**：

| 檔案 | scope | 涉及 finding | 同步類型 |
|------|-------|-------------|---------|
| `rules/acceptance-evidence.md` | 🟢 neutral（**bundled，跨 harness**） | A1/A4-原則/A6/A7/A8 | 新段（A1）+ 原則（A4）+ 擴充（A7）+ 提拔（A6/A8） |
| `skills/arch-thinking/SKILL.md` | skill（**Claude-side**） | A2/A3 | 新 step（A2 mutation-path）+ triage note（A3） |
| `commands/build.md` | command（**Claude-side**） | A4-機制/A5/A6 | 命名+generalize（A4，ref acceptance-evidence）+ complex-change trigger（A5，純引用）+ batch ceiling（A6） |
| `commands/ep-review.md` | command（Claude-side） | A4 | cross-ref |
| `commands/audit-test.md` | command（Claude-side） | A7 | angle 6 升級 3-signal |
| `commands/deliverable-review.md` | command（Claude-side） | A7 | 認知誤差點加 Type B |
| `skills/code-review-and-quality/SKILL.md` | skill（Claude-side） | A2 | Correctness sniff cross-ref |

> **cross-harness 含義**（EP Review SC-2）：非 Claude 端只讀 acceptance-evidence.md（bundled）。A2/A3/A4-機制/A5/A6-mechanism 落 skill/command（Claude-only）→ 非 Claude 端讀得到**原則**（acceptance-evidence 自帶可操作摘要）但靠自家機制套用。故 A4 Claim→Evidence→Trust **原則**必須在 acceptance-evidence（非純 build.md）。

**風險假設**：
- guide 上游 sourced-not-verified → 原則層落地，禁統計。
- 行為假設「LLM 照新原則套用」待 L6 真實 session 驗證（docs mode 無 runtime）。
- acceptance-evidence.md 跨 S1/S4 兩段——依賴序 S1→S4（sequential）。
- A2/A6 各有 POC（A2 重跑 mutation-path A/B；A6 RED-operationalize 小 POC）。
- **runtime monitor infra 多數 solo 專案不存在**（EP Review SC-1）→ A1 原則須標降級路徑（無 monitor 時至少 test-time assert + source-time invariant 列舉）。

---

## UC 盤點（元專案 — 受影響命令/rules 清單）

> 元專案無 library Capabilities 表格；UC 盤點 = 受影響命令/rules 行為清單。`.kanban/` 存在；**SYSTEM-MAP 無**（元專案，docs mode 正當跳過）。

### Backlog 關聯
- **`mechanical-gate-philosophy-hybrid.md`**（已決策、未建）：論點與 A1/A4/A5 重疊。本 EP 採「引用非重述」（見實作總覽）；EP 完成後回填該 card 三處回收點（A1 錨 + A4 引用 + A5 引用，收尾 #8）。
- **session-boundary-review command（新建 card）**（EP Review DT-2）：A6 session-boundary 跨 session 場景無觸發機制，建 backlog card 追蹤 deferred command（本 EP 不建，scope）。
- 其餘 Backlog card 與本 EP 無直接關聯。
- **自動建卡**：EP 整體追蹤卡 + session-boundary-review deferred card 建於 `.kanban/Backlog/`。

### 掃描範圍
- 受影響：`rules/acceptance-evidence.md`、`skills/arch-thinking/SKILL.md`、`commands/{build,ep-review,audit-test,deliverable-review}.md`、`skills/code-review-and-quality/SKILL.md`
- Backlog：`.kanban/Backlog/*.md`（4 card 全掃）

### 既有 UC 狀態（受影響命令行為）

| 命令/rule | 現況行為 | 影響 | 說明 |
|-----------|---------|------|------|
| acceptance-evidence.md | 證據階層 L1-L6 + A/B 軸；無 runtime-monitoring 層 | 更新 | + Runtime Invariant Assurance（A1）+ Claim→Evidence→Trust 原則（A4）+ A8 結構上限 + A6 RED operationalize + A7 intent-drift taxonomy |
| arch-thinking | compensating-pair + core identification matrix | 更新 | + mutation-path step（A2）+ change-type triage note（A3，降級非軸） |
| /build | Agent 產出機械驗證 + 整合器加嚴 + §1b→RED | 更新 | A4 命名(ref acceptance-evidence) + A5 complex-change trigger(純引用) + A6 batch ceiling |
| /ep-review | §1b 漏列 invariant 無人查 | 更新 | A4 cross-ref |
| /audit-test | angle 1 靜態 + angle 6 動態（2-signal） | 更新 | A7 angle 6 升級 3-signal |
| /deliverable-review | 認知誤差點 Type A only | 更新 | A7 加 Type B |
| code-review-and-quality | Correctness state inconsistencies sniff | 更新 | A2 cross-ref |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| Runtime Invariant Assurance 原則 | 📋 | rules/acceptance-evidence.md（S1） |
| mutation-path counting（ownership vs write-site 粒度） | 📋 | skills/arch-thinking/SKILL.md（S2） |

---

## Scenario Matrix（docs mode — 命令/rule 行為觸發情境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應 |
|---|------|------|---------|------------|------|
| SM-1 | silent-corruption path 變更 | 觸及 invariant-bearing 模組 | runtime invariant assurance 原則適用——invariant 須 runtime 機械檢查 | A1 新段 | A1 |
| SM-2 | AI 宣稱「不影響 X」 | 任何 no-impact claim | Claim→Evidence→Trust：claim 須獨立機械證據反證，否則退化為 self-report | acceptance-evidence A4 原則 + build.md 機制 | A4 |
| SM-3 | complex/competing-demand 變更觸及 constraint | 風控 limit / 會計守恆 | complex-change constraint tightening 觸發（雙 trigger：IO + 複雜度-約束） | build.md:65 後 | A5 |
| SM-4 | RED 時刻（測試失敗） | 寫 invariant/驗證測試時 | 人類判讀「失敗是否符合預期」（prospective gate） | acceptance-evidence:118 提拔 | A6 |
| SM-5 | 跨 session 接續 / 累積多段 | 開新 session 或多段後 | intent-drift Type B 偵測 + session-boundary review（**註：跨 session 場景目前無觸發機制，效果限單 session batch-ceiling 軟觸發；跨 session 待獨立 command**，DT-2） | A7 + A6 邊界 | A6+A7 |
| SM-6 | 動到 mutable state / invariant-bearing 模組 | 變更觸及狀態寫入點 | mutation-path counting：找所有 write site，判 ownership vs write-site 粒度，CONCLUDE single-writer 在哪個粒度成立 | arch-thinking 新 step | A2 |
| SM-7 | 既有 core 審查（無特定 change） | 審穩固度 | change-type **triage note**（generated/rename/logging→放行；money-path/tribal→必審；其餘隨 core/leaf）——非深度軸，是 triage gate | arch-thinking:141 triage note | A3 |
| SM-8 | leaf 模組 / 純 docs 變更 | 低風險、非 invariant-bearing | **條件必填不觸發**（A1/A2/mutation-path 對 leaf 是噪音）。**反面警示（SC-3）**：誤判非 leaf 為 leaf → mutation-path 漏跑（觸發條件精確度是審查重點） | 條件必填 pattern | 全 |
| SM-9 | **專案無 runtime monitor infra**（EP Review SC-1） | solo 專案多數無 monitor | A1 原則降級：至少 source-time invariant 列舉 + test-time assert 作 monitor 替代（標「不足但有」），非空話 | A1 降級路徑 | A1 |
| SM-10 | **非 Claude harness 讀原則**（EP Review SC-2） | ZCode/OpenCode/Codex session | 讀得到 acceptance-evidence 原則（A1/A4/A6/A7/A8）並靠自家機制套用；讀不到 Claude-only skill/command 機制（A2/A3/A4-機制/A5）——故原則須在 acceptance-evidence 自帶可操作摘要 | cross-harness split | 全 |

---

## 段落劃分原則

**依賴圖**：**S1**（acceptance-evidence 樞紐：A1+A8+A4-原則，確立原則 single-source）→ **{S2 ∥ S3}**（S2 arch-thinking A2+A3；S3 build.md A4-機制+A5；平行，不同檔）→ **S4**（acceptance-evidence A6+A7 + build.md batch-ceiling + cross-refs；最後，依賴 S1 同檔 + S3 build.md）。

**同檔 sequential 約束**：acceptance-evidence（S1→S4）、build.md（S3→S4 batch-ceiling）。

**語義約束（貫穿，single-source）**：
- **原則錨點在 S1** acceptance-evidence：runtime-assurance / 證據獨立性 / Claim→Evidence→Trust / 機械>自述 原則在此確立。A4-機制（build.md）/A5（build.md）/A7-引用 **純引用非重述**（DRY；EP Review F3-C1 抓 v1 A5 重述已修；整合驗證加 rg 確認 build.md 未重述）。
- **A8→A1 論證链**：A8（A 軸天花板「人審結構上限，經驗無關」）→ A1（故需 runtime/invariant 補）。
- **A6→A7 邊界→訊號**：A6 checkpoint（RED + session 邊界），A7 該 checkpoint 查的訊號（Type B + 3-signal）。
- **跨 harness 原則/機制 split**（SC-2）：通用原則在 acceptance-evidence 自帶可操作摘要（非純引用 Claude-only 機制）。
- **條件必填**：A2 mutation-path（觸及 mutable state）、A3 triage note（既有 core 審查）——leaf/純 docs 不觸發（SM-8）。
- **A3 是 triage note 非軸**（DT-1）：不建第四深度軸；change-type triage 是「需不需要審」gate，不是深度加權。
- **禁統計** + **neutral-compliance**（acceptance-evidence 新段 neutral：Claude 機制括號註、禁裸 slash、量化 4-place 作範例非規則本體）。
- **prospective vs retrospective**（A6）：RED 時刻判意圖（prospective，有別於 fix-test retrospective）。

---

## S1: acceptance-evidence.md — A1 Runtime Invariant Assurance + A8 認知上限 + A4 Claim→Evidence→Trust 原則（樞紐）

### Context
- **背景**：A1 樞紐（收斂 D2/D3/D5）。silent corruption 用 runtime invariant check 抓最有效；人類不可替代角色 = 列舉 invariant（獨立於 AI mental model）；spec 完整度是 monitor 上限。A8 論證基礎——人審有結構上限（經驗無關），P0 invariant 不能只靠人審。A4 原則（EP Review F4-🟡1/SC-2）：Claim→Evidence→Trust 作**跨 harness 通用原則**落 acceptance-evidence（neutral，所有 harness 讀得到），build.md 作 consumer 機制。
- **UC 引用**：實作「Runtime Invariant Assurance 原則」+「Claim→Evidence→Trust 原則」（新增 UC 📋）。
- **依賴**：S1 樞紐，S3（A4-機制/A5 引用原則）+ S4（A6/A7 引用）依賴。
- **語義約束**：見段落劃分原則。
- **依賴錨點**：`acceptance-evidence.md` L9-15（證據獨立性）/ L95（證據時效性段末）/ L97（A/B 雙軸起）/ L99-104（A 軸天花板）/ L110-118（設計方向段）/ L133（L6 疲勞）。
- **成功標準**：(a) 新段 `## Runtime Invariant Assurance（設計方向）`（L95 後）確立原則 + 降級路徑（SM-9）；(b) A4 Claim→Evidence→Trust 原則（近 L9-15 證據獨立性，作其 operationalization）；(c) A8 A 軸天花板結構上限論證；(d) 全 neutral（禁裸 slash、量化範例非本體）。

### 修改要點（docs mode）
1. **新增 `## Runtime Invariant Assurance（設計方向）`**（L95 後、L97 前）：
   - **核心命題**（原則錨點）：test 是時間點證據（build-time 通過），runtime monitor 是持續保證；silent-corruption path 的 invariant 須 runtime 機械檢查作 test 之後持續守衛——區分 test-passed-at-build-time vs holds-at-runtime。
   - **獨立性**：runtime check 機械執行，獨立於 AI mental model（呼應 L9-15 證據獨立性）；「該驗什麼 invariant」須人定（AI 可能正確實作錯誤模型）。
   - **spec 是上限**：monitor 上限 = 寫進 spec 的 invariant 完整度。
   - **multi-point placement**（**範例 placement，領域特定非規則本體**——EP Review F2-S1 去「量化」字眼）：runtime check 放多個 defense-in-depth 點，依專案生命週期選。**範例（量化領域）**：test-time assert / 對帳外部 truth / 生產 monitor / 本地 pre-commit（solo 無 CI 取代 CI gate）。
   - **降級路徑（SM-9，EP Review SC-1）**：專案無 runtime monitor infra 時，原則不退化為空話——至少 (i) source-time 強制列舉 invariant（人類列，AI 不列）+ (ii) test-time assert 作 monitor 替代。標「不足但有」。
   - **asymmetric drift 警覺**（原則層，**禁數字**）：AI 在 complex/competing-demand 壓力下傾向破壞 constraint（risk limit 首要受害）→ constraint invariant check 必須機械、不可被 AI lobby。
   - **cross-ref**：呼應 execution-plan §1b（producer 識別 silent-corruption path，本段承接 runtime 層；EP Review F4-ℹ️2 雙向 ref：建議 §1b 加 forward-ref 指本段）；mechanical-gate-philosophy（pending skill）建成後引用。
2. **A4 Claim→Evidence→Trust 原則**（近 L9-15 證據獨立性，作 operationalization——EP Review F4-🟡1/SC-2：落 neutral 讓跨 harness 讀得到）：加一段「**Claim→Evidence→Trust（no-impact claim 校驗原則）**——當 AI/producer 宣稱『不影響 X』（accounting/risk/invariant），claim 須有**獨立機械證據**反證（git diff / rg 殘留 / LSP findReferences），否則 claim 退化為 self-report（呼應證據獨立性 L9-15）。AI 誠實說『沒影響』時最危險——獨立性塌縮點。具體機制見 build.md Agent 產出機械驗證（Claude 端）」。**自帶可操作摘要**（非純引用 Claude-only 機制，SM-10）。
3. **A8 擴充 A 軸天花板段**（L99-104）：在「A 機器自驗...AI 內部自洽」後補——「**人審（B 軸 L6 / reviewer）亦有結構上限**：疲勞、注意力瓶頸、確認偏差是認知結構限制，**經驗無關**；故 P0 invariant 不能只靠人審，需 Runtime Invariant Assurance（見上段）補」。L133 泛用告誡提拔為結構論證（加引用）。

### 驗證策略
- rg 原則錨點：`rg "Runtime Invariant Assurance|Claim→Evidence→Trust" rules/acceptance-evidence.md`
- rg 禁統計：`rg "93.5|60%|400.line" rules/acceptance-evidence.md` → 0
- rg neutral（EP Review F2-C1）：`rg '`/fix-test`|`/build`|`/execution-plan`' rules/acceptance-evidence.md` 新增段 → 僅括號註內；裸 slash 0
- rg single-source（EP Review F3-S1）：A4 原則在 acceptance-evidence，build.md 是機制非定義
- /consistency acceptance-evidence.md

---

## S2: arch-thinking/SKILL.md — A2 mutation-path counting + A3 change-type triage note（review 結構機械）

### Context
- **背景**：A2——assumption delta 是 research gap；**核心認知增量（POC 證實）**：step 本質不是 count writers，是 **ownership 粒度 vs write-site 粒度區分**（baseline 沒區分→single-writer=no 淺；treatment 區分→yes at class boundary 精確）。A3——**EP Review DT-1 降級**：change-type 不作第四深度軸（修缺陷→compensating-pair `arch-thinking:127-139` 已涵蓋；core/risk-tier 已決定深度；第四軸強迫 LLM 自覺加權=最弱形式，與 A1 機械>自述矛盾），降為 core identification 內 **triage note**（Pain 0 本質）。
- **UC 引用**：實作「mutation-path counting」（新增 UC 📋）。
- **依賴**：與 S1 平行（不同檔）；S4 無依賴。
- **語義約束**：A2 與 compensating-pair 並列（方向相反）；A2/A3 條件必填；**A3 是 triage note 非軸**（DT-1）。
- **依賴錨點**：`arch-thinking:127-139`（補償邏輯盤點）/ `:141-157`（core identification）/ `:148`（審查深度 tier）。`code-review-and-quality:24`。
- **成功標準**：(a) A2 新 step `### 變更路徑計數（mutation-path counting）`（§127 後、§141 前），含粒度判斷；(b) A3 triage note（§141-157 core identification 內，**非新軸**）；(c) code-review-and-quality:24 cross-ref。

### 修改要點（docs mode）
1. **`arch-thinking` 新 step `### 變更路徑計數（mutation-path counting）`**（:127 補償邏輯盤點後、:141 前）——**條件必填**（觸及 mutable state/invariant-bearing；leaf/純 docs 跳過）：
   - 用 LSP `findReferences`/rg 找所有 write site（含 in-place field mutation），逐項計數不歸一類
   - **判斷粒度（核心）**：domain invariant（跨層守恆）還是 local overlay？
   - 多 writer：by-design 還是 invariant 破壞？
   - ordering / atomicity
   - **CONCLUDE：single-writer 在哪個粒度成立——ownership 粒度（單一 owning class）vs write-site 粒度（單一寫入點）**。多 write-site 但單一 ownership = by-design overlay。
   - 並列說明：compensating-pair 反向（誰抵消 bug），mutation-path 正向（我新增幾條 writer）——正交。
2. **`arch-thinking` A3 change-type triage note**（:141-157 core identification，:148 審查深度 tier 後）——**降級非軸（EP Review DT-1）**：加「**change-type triage（『需不需要審』gate，非深度加權軸）**——變更類型先 triage：generated/reproducible→放行（可證偽：hand-modified 即升 source 審）；rename/comment/logging→放行；money-path/tribal-knowledge→必審（已被 core/§1b invariant-bearing 涵蓋，此處明示）；其餘隨 core/leaf 深度。**不另立深度軸**——修缺陷的高價值審查（compensating-pair §127-139）已有機制；本 triage 僅補『需不需要審』的入口判斷」。明文：triage（此處，入口 gate）≠ risk-tier（acceptance-evidence，證據深度）≠ scope（execution-plan，planning gate）——語義不同，**勿機械套用為第四深度軸**。
3. **`code-review-and-quality:24`**：Correctness「state inconsistencies?」sniff 後加 cross-ref 指 mutation-path step（非新 checklist 項）。

### 驗證策略
- **A2 POC A/B 重跑（closed loop，去框架）**：標的 mosaic `kc_momentum_naive.py` `self.positions`（或另選 invariant-bearing）。baseline（無 step）vs treatment（含 step）——確認 treatment 產出 ownership/write-site 粒度區分。**去框架重跑**（v1 POC confound：treatment 帶 strategy-local 選項；本次 step 文字不含框架，驗純 step 效應）。POC 寫 `poc/` 檔頭標 S2。
- rg：`rg "變更路徑計數|mutation-path" skills/arch-thinking/SKILL.md`
- rg：`rg "change-type triage" skills/arch-thinking/SKILL.md` + 確認**無「第四軸/overlay axis」字眼**（DT-1 降級）
- /consistency arch-thinking

---

## S3: commands/build.md — A4 機制命名+generalize + A5 complex-change trigger（引用 acceptance-evidence 原則）

### Context
- **背景**：A4——`build.md:101-105` 直命中機制；**EP Review F4-🟡1/SC-2**：Claim→Evidence→Trust **原則**在 acceptance-evidence（S1，neutral 跨 harness），build.md 是 **consumer 機制**（命名 + generalize 應用，引用原則非定義）。A5——Mechanism 2 covered，Mechanism 1（complex-change→constraint 加嚴）gap。**EP Review F3-C1**：v1 A5 重述 asymmetric drift 原則，改純引用。
- **依賴**：與 S2 平行；引用 S1 原則（A4-機制 ref acceptance-evidence Claim→Evidence→Trust；A5 純引用 runtime-assurance asymmetric drift）。
- **語義約束**：A4-機制/A5 **純引用 S1 原則非重述**（F3-C1；整合驗證 rg 確認）；A4=claim 校驗、A5=constraint trigger 機制不同。
- **依賴錨點**：`build.md:57-65`（整合器 + :65 加嚴）/ `:101-105`（Agent 產出機械驗證）。`ep-review.md:76`。
- **成功標準**：(a) A4 build.md:101 命名機制為「Claim→Evidence→Trust 校驗」+ ref acceptance-evidence 原則 + generalize；(b) A5 complex-change constraint tightening（:65 後，純引用 asymmetric drift + 新 trigger）；(c) ep-review:76 cross-ref。

### 修改要點（docs mode）
1. **`build.md:101` A4 命名+generalize（ref acceptance-evidence 原則）**：在「Agent 產出機械驗證」後命名「**Claim→Evidence→Trust 校驗**（原則見 acceptance-evidence 證據獨立性 + Claim→Evidence→Trust 段）」並 generalize：「此機制適用**所有 no-impact claim**（agent/producer 宣稱『沒影響 X』）：claim 須獨立機械證據反證（git diff/rg/LSP），否則退化為 self-report」。
2. **`build.md` A5 complex-change constraint tightening（純引用，EP Review F3-C1）**（:57-65 整合器識別後、:65 加嚴旁）：加 trigger「**complex-change constraint tightening**——當變更觸及『會被 rationalize 放寬的約束』（風控 limit / 會計守恆 / single-writer）且 complex/competing-demand 升高時，constraint 審查自動加嚴」。**asymmetric drift 原則純引用**：「asymmetric drift 原則（AI 壓力下傾向破壞 constraint，check 須機械不可被 lobby）見 acceptance-evidence Runtime Invariant Assurance 段」——**不重述原則**（v1 違規已修），本處只加 trigger 機制（IO 邊界 + 複雜度-約束雙 escalation）。
3. **`ep-review.md:76` cross-ref**：「漏列 invariant 無人查」後引用「Claim→Evidence→Trust 校驗（原則 acceptance-evidence / 機制 build.md）」——producer 宣告「沒動 X invariant」= no-impact claim 須獨立證據反證。

### 驗證策略
- rg：`rg "Claim→Evidence→Trust" commands/build.md` → 命名 + ref acceptance-evidence
- **rg single-source（EP Review F3-S1/F3-C1）**：`rg "asymmetric drift|壓力下.*破壞 constraint|不可被.*lobby" commands/build.md` → 僅引用句（指 acceptance-evidence），**無原則重述**
- rg：`rg "complex-change|constraint tightening" commands/build.md`
- /consistency build.md + ep-review.md

---

## S4: acceptance-evidence.md A6+A7 + build.md batch-ceiling + cross-refs（intent-drift pair）

### Context
- **背景**：A6——RED operationalize + batch ceiling + session-boundary review 缺；`acceptance-evidence:118` RED 前移在設計方向段。A7——intent-drift Type A/B taxonomy + 3-signal 缺。A6+A7 邊界→訊號配對。**EP Review DT-2**：session-boundary 跨 session 無觸發機制，需誠實標記 + backlog card。
- **依賴**：S1（同檔，A6/A7 引用 A1/A4 原則）+ S3（build.md batch-ceiling 相鄰）。**最後執行**。
- **語義約束**：A6→A7 邊界→訊號；A7 Type A/B ≠ fix-test（test-failure）≠ 認知誤差兩型；prospective vs retrospective。
- **依賴錨點**：`acceptance-evidence.md` L17-30（認知誤差，A7）/ L110-118（設計方向，A6）。`build.md:124`。`audit-test.md` angle 6（:199-210）/ `deliverable-review.md:141-145`。
- **成功標準**：(a) A6 RED operationalize（acceptance-evidence:118 提拔）+ batch ceiling（build.md:124）+ session-boundary（**誠實標記 + backlog card**，DT-2）；(b) A7 Type A/B + 3-signal（acceptance-evidence:17-30）；(c) audit-test angle 6 升級 3-signal；(d) deliverable-review 加 Type B。

### 修改要點（docs mode）
1. **`acceptance-evidence.md` A6 RED operationalize**（L110-118）：第 5 點 RED 前移**提拔為可操作**——build 在每段 RED 時刻印「失敗訊號 + EP 該段預期行為」對照，標「**人類 RED checkpoint**」（prospective 可選暫停點，判「失敗是否符合預期」）。明文 prospective vs retrospective：本 checkpoint 前瞻判意圖（有別於 **fix-test** retrospective 判舊測試意圖——**neutral 寫法：括號註 `(Claude: /fix-test)`，禁裸 slash，EP Review F2-C1**）。
2. **`build.md:124` A6 batch ceiling**（錯誤自癒旁）：加「**batch ceiling**——累積多段未經人類判讀 → 建議暫停跑 session-boundary review（防 context 累積漂移）」。:124 單段重試上限 vs batch ceiling 累積段落上限（雙 ceiling）。
3. **`acceptance-evidence.md` A6 session-boundary review**（L110-118，**EP Review DT-2 誠實標記**）：加「**session-boundary review**——跨 session 接續時判讀累積目標是否漂移。**誠實標記**：跨 session 場景目前**無觸發機制**（全 repo 無 resume-review trigger；/at /handoff /standup 皆非），本原則效果限**單 session batch-ceiling 軟觸發**；跨 session 觸發待獨立 command（見 `.kanban/Backlog/` deferred card）」。原則層不建新 command（scope）。
4. **`acceptance-evidence.md` A7 intent-drift Type A/B + 3-signal**（L17-30 認知誤差段）：加 intent-drift 專用 taxonomy（區別既有 impl-discovery/design-error）：
   - **Type A（Specification Drift，靜態）**：AI 誤解 prompt → code 正確但不是要的。偵測：意圖先於 code 寫下保留；completion analysis 對照原 plan。
   - **Type B（Context/Goal Drift，動態）**：AI 不知 convention/invariant，或隨段落/跨 session 目標悄然偏移。偵測：invariant check + pattern divergence + 跨 session 目標描述 drift。
   - **3-signal correlation**：判 passing test 真通過還是 silent drift——關聯①原始 test intent ②當前 test result ③引入的 code changes。coverage 增加≠能指出 code 仍做意圖中的事。
   - 明文：Type A/B（intent drift 動靜態）**≠** fix-test Type A/B（test-failure 分類）**≠** 既有 impl-discovery/design-error（認知誤差來源）——三者別混淆（neutral 寫法：fix-test 用名稱 + 括號註，禁裸 slash）。
5. **`audit-test.md` angle 6 升級 3-signal**（:199-210）：加第三訊號——關聯 test intent + result + changes 三訊號判 silent drift（升級 2-signal 為 3-signal）。
6. **`deliverable-review.md:141-145` 加 Type B**：認知誤差點（Type A only）加 **Type B 動態漂移**（隨段落/跨 session 目標偏移）。

### 驗證策略
- **A6 小 POC**：模擬 build RED 時刻——確認「失敗訊號 + EP 預期行為」對照觸發人類判讀（prospective gate 非空原則）
- rg：`rg "人類 RED checkpoint|batch ceiling|session-boundary review" rules/acceptance-evidence.md commands/build.md`
- rg：`rg "Type A|Type B|3-signal" rules/acceptance-evidence.md`
- rg neutral（EP Review F2-C1）：`rg '`/fix-test`' rules/acceptance-evidence.md` → 0 裸 slash（僅括號註）
- rg：`rg "3-signal|三訊號" commands/audit-test.md`；`rg "Type B|動態漂移" commands/deliverable-review.md`
- 別混淆標註：A7 三型別區分文字存在
- /consistency acceptance-evidence + audit-test + deliverable-review

---

## 整合策略

- **S1**（樞紐：runtime-assurance + 人審上限 + Claim→Evidence→Trust 原則）→ **{S2 ∥ S3}**（arch-thinking 機械 + build claim/constraint 機制，平行不同檔）→ **S4**（intent-drift pair + cross-refs，最後）。
- **同檔 sequential**：acceptance-evidence（S1→S4）、build.md（S3→S4）。
- **原則 single-source**：runtime-assurance / 證據獨立性 / Claim→Evidence→Trust / 機械>自述 錨 S1；A4-機制/A5/A7 引用非重述（**EP Review F3-C1 修 A5 重述**）。
- **整合驗證**：全鏈原則用詞一致 + 條件必填不觸發 leaf（SM-8 含 false-negative 警示 SC-3）+ 禁統計全綠 + neutral-compliance（acceptance-evidence 新段無裸 slash）+ Type A/B 三型別不混淆 + **single-source rg**（EP Review F3-S1：確認 build.md 未重述 acceptance-evidence 原則）+ cross-harness 原則/機制 split（SM-10）。
- /sync-sources + /consistency（7 檔）。

## 收尾步驟（docs mode）

1. **`scripts/deploy_agents.py`**：acceptance-evidence.md neutral rule → 重跑 deploy → 抽查 deployed AGENTS.md（`~/.zcode/AGENTS.md` 等）含 Runtime Invariant Assurance + Claim→Evidence→Trust 新段 + 排除 claude-specific + **neutral-compliance**（無裸 slash，EP Review F2-C1）。
2. **bundle 驗證**：shasum idempotent + 新段 neutral-compliance 抽查。
3. **Claude 端載入**：skills/commands 改動驗 symlink。
4. **`/sync-sources`**：若 A1/A4 引入新 single-source invariant，加 invariant 機械驗證。
5. **`commands/CLAUDE.md` / `skills/CLAUDE.md` 索引** + **`rules/AGENTS.md` rule overview（acceptance-evidence 行描述加 Runtime Invariant Assurance）+ root `AGENTS.md` acceptance-evidence 入口摘要**（EP Review F2-S2）。
6. **`/consistency`**：受影響 7 檔。
7. **`/audit-test`**：docs mode 無 .py，跳過。
8. **Backlog 回填（EP Review DT-3，三處回收點）**：`mechanical-gate-philosophy-hybrid.md` 加註「mechanical-gate 原則三處待回收：A1 錨點（acceptance-evidence Runtime Invariant Assurance 段）+ A4 引用點（build.md Claim→Evidence→Trust）+ A5 引用點（build.md complex-change constraint tightening）——待 mechanical-gate skill 建成統一回收」。另建 **session-boundary-review deferred card**（DT-2）。
9. **EP 歸檔**：搬 `_done/`。

---

## EP Review Findings

> EP Review Cycle（3 Explore agent · F1-F5 + Clean Arch top-down + 深層思考方向）。採納清單已寫入 EP（implemented），拒絕標理由。

| ID | 嚴重度 | EP 段 | 問題 | 決策 | 處置（已入 EP） |
|----|--------|-------|------|------|----------------|
| F2-C1 | 🔴 Important | S4 | acceptance-evidence.md（neutral bundled）含裸 slash `/fix-test`，違 neutral 規範 | ✅ 採納 | S4 修改要點 1/4 + 驗證 rg 改 neutral 寫法（fix-test 名稱 + 括號註） |
| F3-C1 | 🔴 Important | S3 | A5 重述 asymmetric drift 原則（近乎逐字 S1），違 single-source + 加劇散落 | ✅ 採納 | S3 修改要點 2 改純引用 + 整合驗證加 single-source rg |
| DT-1 | 🔴 Important | S2 A3 | change-type 第四軸過度工程（修缺陷→compensating-pair 已涵蓋；第四軸強迫 LLM 自覺加權=最弱形式） | ✅ 採納（降級非砍） | S2 A3 改 triage note（非軸）+ SM-7 改 triage gate + 語義約束 |
| F4-🟡1 | 🟡 Important | S3 A4 | Claim→Evidence→Trust 命名落點（build.md vs review-engine/acceptance-evidence）未說明；single-source 張力 | ✅ 採納（落 acceptance-evidence） | A4 原則移 acceptance-evidence（S1，neutral 跨 harness），build.md 作 consumer 機制——兼解 SC-2 |
| SC-2 | 🟡 Important | 關鍵約束 | 非 Claude 端讀得到原則、讀不到落地機制（skill/command 不 bundle） | ✅ 採納 | 加跨 harness 原則/機制 split 約束 + SM-10 + A4/A1 原則自帶可操作摘要 |
| DT-2/SC-4 | 🟡 Important | S4 | session-boundary review 跨 session 無觸發機制，原則淪空話 | ✅ 採納 | S4 #3 誠實標記 + 建 deferred backlog card + SM-5 標註 |
| DT-3 | 🟡 Important | 收尾 #8 | mechanical-gate 回收 bookkeeping 不全（只記 A1，漏 A4/A5） | ✅ 採納 | 收尾 #8 改三處回收點（A1 錨 + A4 引用 + A5 引用） |
| SC-1 | 🟡 Important | SM/S1 | 漏「runtime monitor infra 不存在」降級場景 | ✅ 採納 | 加 SM-9 + A1 降級路徑（test-time assert + source 列舉） |
| F2-S1 | 🟢 Suggestion | S1 | `量化 illustration` 措辭易誤導 | ✅ 採納 | 改「範例 placement（領域特定非規則本體）」 |
| F2-S2 | 🟢 Suggestion | 收尾 | 漏 rules/AGENTS.md + root AGENTS.md 同步 | ✅ 採納 | 收尾 #5 補 |
| F3-S1 | 🟢 Suggestion | 整合驗證 | 漏 single-source 機械驗證 rg | ✅ 採納 | 整合驗證 + S3 驗證策略加 rg |
| SC-3 | 🟢 Suggestion | SM-8 | 條件必填只測正確跳過，未測誤判 | ✅ 採納 | SM-8 加 false-negative 反面警示 |
| F4-ℹ️2 | ℹ️ 提醒 | S1 | §1b cross-ref 單向 | ✅ 採納 | S1 建議 §1b 加 forward-ref（可選） |
| F1-ℹ️1 | ℹ️ 提醒 | 段落0 | L32「STOP gate」characterization 寬鬆（實為 EP fast-check stop） | ✅ 採納 | 段落0 改精確（EP Review Cycle 為 STOP gate，L32 為 fast-check） |
| DT-4 | 🟢 Suggestion | S4 | 6 子項跨 4 檔，建議拆 S4a/S4b | ❌ 不採納 | A6+A7 強配對（邊界→訊號）+ 同檔 sequential 保護，拆開增語義不一致風險；build 由主 session 處理可承擔認知負載 |
| DT-5 | 🟢 Suggestion | 總覽 | A3 是最弱項可砍 | ⚠️ 部分 | 與 DT-1 合併處理——降級非砍（Pain 0 有 confirmed_gap 價值，triage note 保留） |

**審查結論**：可直接執行（所有 🔴/🟡 已寫入 EP）。EP Review 三 agent 一致認高品質（20+ 錨點零 drift、禁統計零 leak、Type A/B 三型別正確區分）；方向 push-back（A3 過度工程、A4 落點、session-boundary、cross-harness）均已採納入 EP。

## Code Review Findings（跨 session post-build，judge-review 評估）

> 實作完成後跨 session `/code-review`（docs mode，無 Critical/Important）+ 本 session `/judge-review` 評估。機械驗證全綠（single-source / neutral / cross-refs / Type A/B 三型別 / 驗收層術語）。

| ID | 嚴重度 | 問題 | 決策 | 處置 |
|----|--------|------|------|------|
| CR-S1 | Suggestion | `acceptance-evidence.md:7` 載入機制 boilerplate 被 full-Write 從全形 `；（）` 改成半形 `;()` —— 18 sibling rule 全用全形，破壞 `rules/AGENTS.md` 逐字 invariant（實作端 transcription error） | ✅ 採納 | 已還原全形 + re-deploy（bundle 19 條 rule 現全形一致） |
| CR-S2 | Suggestion | `arch-thinking:155` mutation-path 真實案例用 `self.positions` + 6/12 counts，較 sibling（L139 用領域概念）更具體 | ❌ 不採納 | 同檔既有 convention 已含 mosaic ref（L38 `available`、L139 SHORT proceeds）;案例明確標「mosaic POC A/B」;ai-rules 為 mosaic 共用 skill 之家;reviewer 評可接受。邊際泛化效益 < 具體 illustration 價值 |

**commit-readiness**：deploy 義務已滿足（收尾 deploy + S1 修後 re-deploy，bundle 含 3 新段 + boilerplate 一致）。可 commit。
