---
name: review-engine
description: 決定 finding 嚴重度（Critical/Important/Suggestion）、標信心水準（confirmed/evidence-based/inferred）、查證審查宣稱、選審查模式（Workflow/Agent Tool/Main LLM）、理解多層驗證鏈、決定 review 執行預設（force 獨立/max-agents/model/視角/spawn-vs-session）時使用。review 命令家族通用審查邏輯的 domain 真相源 — 審查者自證、LSP 查證方法、Writer-Reviewer 分離、多層驗證設計；ep-review/code-review/audit-test/execution-plan EP Review/build Agent Review 共用。
---

# review-engine — 通用審查邏輯 domain 層

review 命令家族的 **domain 層**：跨 ep-review / code-review / audit-test / execution-plan EP Review / build Agent Review 共用的審查邏輯，**唯一真相源**。各命令是薄 adapter（宣告標的 + profile + 產出，委託本 skill），消除「同一審查動作跨命令重複定義且 drift」。

## 收進判準

一條邏輯收進本 skill 的條件：**所有 review 命令都適用**。只適用部分命令的（如 audit-test 的「偵測器非判官」stance、test 的「套件行為寫 demo」）不收，留該命令。

## 邊界（避免製造新 drift）

| vs | review-engine（本 skill） | 對方 |
|----|--------------------------|------|
| [workflow-review-pattern](../../commands/instruction/_common/workflow-review-pattern.md) | **方法論 + 判定規則**（嚴重度意義、信心水準、自證、為何分離、審查模式判定規則） | **Workflow 執行**：DimensionVerdict schema、兩階段腳本、Finding Record 持久化（判定規則 → 決定讀哪個 schema，依賴方向非耦合） |
| [agent-review-cycle](../../commands/instruction/_common/agent-review-cycle.md) | （不重疊） | **Agent Tool 模式執行範本**（3-perspective） |
| [arch-thinking](../arch-thinking/SKILL.md) | **依賴**它（架構審查需要視角/機械） | 提供架構視角/機械能力 |
| audit-test 三層驗證鏈 | 通用 why（各層都可能錯） | **具體 audit→judge→followup 鏈細節**（test 講最細，留 audit-test） |

**不裝**（留各 adapter）：維度定義（各 profile 自訂）、產出動作（回寫 EP / commit message / 報告）、stance（audit「偵測器非判官」）、Workflow schema/腳本（留 workflow-review-pattern）。

> **Correctness 邊界（lens vs checklist）**：③ Correctness **lens**（視角，執行預設 — base perspective）在 domain（點 4 ③，所有 review 共用）；Correctness **checklist**（what to check：null / boundary / error path 細節）屬 profile，留 [code-review-and-quality](../code-review-and-quality/SKILL.md) ### 1（adapter）。lens 上移、checklist 留 adapter —— 符合本行「維度定義留各 adapter」（checklist 是維度定義；lens 是執行預設）。

---

## 嚴重度框架（3 級，唯一定義源）

workflow-review-pattern 的 schema、各命令的輸出分類，皆引用此。

| 嚴重度 | 意義 | 動作 |
|--------|------|------|
| **Critical** | 安全漏洞、資料損壞、功能損壞、邏輯錯誤 | 必須在合併/commit 前處理 |
| **Important** | 架構不一致、可讀性、效能隱患 | 應處理 |
| **Suggestion** | 風格、命名、小優化 | 作者可忽略 |

> **Nit/FYI 不採用**：code-review-and-quality 早期有 5 級（+Nit/FYI），但 workflow-review-pattern 的 DimensionVerdict schema 強制 3 級 enum —— Nit/FYI 在 Workflow 模式下無法表達，是死定義。統一 3 級。

---

## 信心水準

每個 finding 必須標信心水準，讓下游（judge-review / 用戶）知道哪些需重點查證：

| 信心水準 | 判斷標準 |
|---------|---------|
| **confirmed**（已查證） | 已讀完整 code/body + 比對過具體行/符號 |
| **evidence-based**（有證據） | 有具體 file:line + rg/fd/LSP 結果，但未深入驗證符號語義 |
| **inferred**（推理） | 基於規範/套件行為推理，未實證 |

**規則：Critical 必須 confirmed 或 evidence-based，禁止 inferred**。推理類 finding 必須額外標「⚠️ 未實證，建議實作層跑 demo 確認」並降級為 Suggestion。

---

## 審查者自證 / 誠信

**核心原則**：每個 claim 必須查證，不基於 LLM 訓練資料推測。findings **非定論** — 可被下層（judge-review / 實作查證）推翻，以「可被推翻」的心態輸出。

- **claim 必須查證**：聲稱檔案存在 → Read 它；聲稱命名衝突 → LSP `findReferences` 查 import 鏈；聲稱依賴順序有問題 → LSP `incomingCalls`/`outgoingCalls` 追蹤；聲稱 dead code → LSP `findReferences`（zero hits = 確認）
- **無法查證標 `unverified`**：不得當成事實陳述
- **對外部行為判斷必須實證**（通用原則）：對套件/演算法/數值特性的判斷，不能只靠推理 — 寫最小 demo 跑一次、或引用套件 source（`.venv/lib/...`）具體行號佐證，否則標 inferred + 降級

**不收**（留各命令）：audit-test 的「偵測器非判官 + read-only」stance（只產 findings 不下判）、audit-test「套件行為 → 寫 demo 跑一次」的 test 特化方法。本 skill 只放通用「對外部行為判斷必須實證」原則。

> **對抗性自查義務**：建議「跳過」任何驗證/審查步驟時，懷疑自己的推進偏好（確認偏差）—— 先有結論再找支持證據 ≠ 嚴謹查證得到結論。對 agent 嚴格（不盲從）、對自己也同等對抗性。

---

## LSP 查證方法

符號查證用 LSP（~50ms，100% 涵蓋），文字搜尋用 rg，檔案用 fd。完整決策樹見 [lsp-navigation](../../rules/lsp-navigation.md)。

| 查證對象 | 工具 |
|---------|------|
| 符號定義 / 引用 / 型別 / 呼叫鏈 / 介面實作 | LSP（goToDefinition / findReferences / hover / incomingCalls / outgoingCalls / goToImplementation / workspaceSymbol） |
| 註解、字串、config 值、日誌、TODO | rg（LSP 不索引非程式碼） |
| 檔案搜尋 | fd（LSP 不處理檔案系統） |

> **圖譜 facts 後備（CRG，companion）**：衝擊半徑 / transitive callers / affected flows / community 等**圖譜級**結構事實，在 CRG 裝了的專案用 CRG（見 [crg-query](../crg-query/SKILL.md)）—— LSP 查單一 symbol（定義/簽名/單點引用），CRG 查 transitive impact/flows（review 的 Architecture 軸 ripple、change scoping）。LSP-vs-CRG 分工 + assume/warn-if-absent + anti-over-reliance（graph=structure≠behavior，dynamic dispatch/config 不在圖裡）見 crg-query；CRG 未安裝 → `[WARN]` + fallback LSP/scan-project（不靜默降級）。

### 自我否證義務

**「找不到」≠「不存在」**。查證 0 hits 時必須：

1. **換工具**：rg 0 hits → LSP `findReferences`（覆蓋動態引用、避免 pattern 失誤）
2. **換 pattern**：`rg "<Class>\("` 失敗 → 試 `rg "<Class>"`（去 `(`，建構方式可能不同）、`workspaceSymbol`
3. **換位置**：以為在某檔 → `workspaceSymbol` 全域查定義位置
4. **標「查證失敗」而非「不存在」**：三工具都 0 hits，仍只能標「查證失敗，無法確認」—— **禁止標「不存在」**（查證者可能是 pattern 失誤，非程式碼不存在）

> 真實案例：審查者 rg 稱「`<ExecutorClass>` 無建構點」→ 不採納 finding。獨立查證：LSP `findReferences` 立刻列出 import 行 + 建構行。審查者 rg pattern 失誤，把「自己沒查到」誤判為「程式碼不存在」。

> 審查 EP/計畫文件時同理：宣稱「文件內容有誤」的 finding，必須**逐欄引用文件原文**（含決策欄，非只問題欄），並標出與結論矛盾的證據 —— 否則易產生 false positive（讀漏決策欄、虛構 guard 內容）。

---

## 審查模式判定規則

**本段職責 = 判定規則**（domain：effort/max-agents → 抽象 mode）；**派發到 adapter 範本是命令層職責**（use-case）—— 判定為某 mode 後，各命令自取執行範本（Workflow → [workflow-review-pattern](../../commands/instruction/_common/workflow-review-pattern.md)；Agent Tool → [agent-review-cycle](../../commands/instruction/_common/agent-review-cycle.md)）。不強求消除導覽連結（docs 互指可容忍），重點是 domain 不內嵌派發。

**通用判定規則**（消 build/code-review/ep-review 三處重複定義；例外見下表最右欄）：

| 條件 | 抽象 mode | 例外（不走此 mode） | 命令層自取的執行範本 |
|------|----------|-------------------|-------------------|
| effort = ultracode/xhigh **且** max-agents > 1 | **Workflow** | — | [workflow-review-pattern](../../commands/instruction/_common/workflow-review-pattern.md)（schema + 兩階段腳本 + adversarial verify） |
| max-agents = 1 但 effort = ultracode/xhigh | **Agent Tool**（Fallback） | — | [agent-review-cycle](../../commands/instruction/_common/agent-review-cycle.md)（3-perspective） |
| effort < ultracode | **Main LLM** | build / ep-review / execution-plan（品質閘門，連 standard effort 也強制獨立 agent、不走 Main LLM；僅 code-review 等無強制分離命令適用） | 主 LLM 直接審（現有行為） |

判定結果決定讀哪個執行範本的 schema/腳本 —— 這是**依賴方向**（判定 → schema），不是耦合。本 skill 只放判定規則，**不重複** schema/腳本（在 workflow-review-pattern）。

> 各命令的覆蓋宣告見各自檔案（例外已編入上表最右欄，不再以註腳形式存在 —— 避免「唯一判定規則」式承諾迫使例外被低估、被讀者忽略）。

### 為何 Writer/Reviewer 分離

用獨立 Agent context 審查，避免主 LLM 審自己寫的 code/EP。理論基礎：[acceptance-evidence](../../rules/acceptance-evidence.md) 證據獨立性 — AI 同寫 impl + test 時獨立性塌縮，審查同理（同 LLM 審自己的計畫/實作 = 零獨立性 = 證據強度低）。獨立 context 提升證據獨立性（雖同家族 LLM 共享系統偏誤，quorum 對共同盲點無效 — 見 acceptance-evidence A/B 軸）。

### 為何多層驗證

review finding 可經多層驗證，**各層都可能錯**：

| 層 | 抓什麼錯 |
|----|---------|
| review（偵測/審查） | 品質問題（主要產出 findings） |
| [judge-review](../../commands/judge-review.md)（評估） | review 的 false positive / 過度陳述 |
| [followup-review](../../commands/followup-review.md)（驗收） | 實作是否正確套用採納的 finding |

每一層都是獨立查證機會，不假定上層正確。**具體 audit→judge→followup 三層鏈的細節**（各層盲點、偵測器 stance）見 [audit-test](../../commands/audit-test.md) — test 場景講最細；本 skill 只放通用的「各層都可能錯」原則。

---

## review 執行預設（單一源 — 各 review 命令引用）

> 各 review 命令（ep-review / code-review / audit-test / execution-plan EP Review / build Agent Review）的**執行層預設**集中於此 —— 消除「預設行為跨命令重複定義且 drift」。各命令保留自己的 profile（維度）+ 產出動作，執行預設（force 獨立 / max-agents / model / 視角 / spawn-vs-session）引用本段。

1. **不 auto-detect，force 獨立 agent（預設）**：review 命令預設 spawn 獨立 agent（Workflow / Agent Tool），**不接受 LLM 在裁量點偷懶退 Main LLM 自審**（實證：auto-detect 時 LLM 偷懶 / 搞錯退 Main LLM）。合法 Main LLM（mode 表判定的低 effort code-review）與 spawn 失敗降級（顯式標記 fallback，見 [agent-workflow](../agent-workflow/SKILL.md)「spawn 失敗階梯」）除外。

2. **agent 數量 = max-agents**（預設 **3**，與 [build](../../commands/build.md) 一致；受並發上限 cap，Claude: `rules/model-routing.md`）。

3. **agent model 預設 = 主 session（inherit）**；**可調降一級**（降級映射；Claude: `rules/model-routing.md`）。此為 review **command** agent 專屬預設，**覆蓋** model-routing 通用「review→降級」—— review command 是品質閘門需強度；其他 review-ish agent（verify / research / explore，非 review command）維持降級（見 model-routing carve-out；Claude: `rules/model-routing.md`）。

4. **預設 3 agent = ① clean（Fresh，無 anchor）+ ② UC-anchored（Intent）+ ③ Correctness（邊界正確性 lens）**：三 lens 正交（**錨定方式不同**）、同時跑。
   - **① clean（Fresh）** 抓作者 rationalize〔bias〕—— 無 anchor 讀 code 自身 merits（**code smell 視角**），不被「該做 X」綁住
   - **② UC-anchored（Intent）** 抓漏覆蓋 / 偏意圖〔coverage〕—— 逐 UC 檢驗 impl 滿足度、EP 偏離
   - **③ Correctness（邊界正確性）** 抓邏輯 bugs / 邊界案例（跨日 / 空值 / 溢出 / 空資料）/ 測試充分性〔correctness〕—— **主動質疑邊界事實**，不錨定意圖、不靠 code smell
   - **三者錨定方式不同 → 正交**（故不適用「共享錨定遞減」移除理由）：① 無錨讀 smell / ② 錨 EP / ③ 質疑邊界事實
   - **為何 ③ 同 session 有效**（F1 證偽 agent-review-cycle 舊論述「clean 自然覆蓋正確性」）：clean 是 smell 視角，不主動質疑邊界 → `max(fill_dates)` 跨日 bug 看起來不怪 → 漏。③ Correctness 主動質疑邊界事實，**不共享 writer 意圖假設** → 對**非系統性偏誤**邊界 bug 同 session 可抓。**例外**：系統性偏誤（LLM 普遍弱項，如某類邊界推理）同家族也漏 → layer 2 code-review（見 acceptance-evidence 系統性偏誤）
   - 單跑任一有盲點，同時跑互補。執行範本見 [agent-review-cycle](../../commands/instruction/_common/agent-review-cycle.md) —— 此 3-perspective 是 Agent Tool 範本的 base 視角（build Agent Review 用）；code-review 六軸、ep-review F1-F5 等以**維度 profile** 分配 agent（見各命令 + 上方 mode 表），非此 clean/UC/Correctness 3-perspective。

5. **>3 配置**（機械特徵觸發，非 LLM 語義判「高風險」；受 max-agents cap）：base 恆 ①+②+③（3）；extra（第 4+）由**消費命令提供的段落風險特徵**觸發 —— **通用風險特徵 → extra agent 映射**（單一源，domain）：`外部整合` → adversarial、`公開簽名變更` → architecture+consumer-perspective、`跨模組` → architecture、`UC 數 >6` → UC-split（extra 拿 UC 子集做深度，唯一給 UC-anchored 開 extra 的情境）。`跨模組` 映射目前無 adapter 接線，保留供未來消費命令。**特徵偵測由消費命令提供**（adapter）；review-engine 只定義映射框架（domain），**不列消費命令特有名詞**（DIP — domain 不被 adapter 污染）。extra 優先序到 cap —— **architecture（axis 3）> adversarial / edge > consumer-perspective**（保留原 agent type 清單與優先序；多特徵命中 + cap 不足依此序取最高，截斷其餘並提示）；**絕不** 2nd clean / 2nd **同一** lens —— 複製 lens 同家族共享盲點，邊際覆蓋 ≈0（UC-split 是不同子集做深度，非複製；多樣性 > 數量）。

6. **spawn vs 另開 session 共存**（非二選一）：
   - **spawn**（命令內、即時、同家族 LLM 天花板）—— 預設路徑
   - **另開 session**（user 手動、最強獨立、抓 spawn 漏的）—— 高風險建議補跑
   - **另開 handoff 套件** = 持久化 finding（EP review 區段 / kanban，tracked）+ git diff + 標的 / EP / UC 路徑 —— 讓新 session 不靠記憶還原審查標的
   - **跨 session 鏈**（另開 session 時，persistence 串起每步；不靠對話記憶 —— 跨 session 不在）：`review` 寫 finding → `judge-review` 寫決策（✅ / ❌ / ⚠️）→ apply（主 agent / impl LLM 改）→ `followup-review` 讀持久化逐項驗收（verified / closed / open）。findings 交接格式見 [workflow-review-pattern](../../commands/instruction/_common/workflow-review-pattern.md) Finding Record。

---

## 與各 review 命令的關係

各命令是薄 adapter，引用本 skill 取通用邏輯，自帶 profile（維度）+ 產出動作：

| 命令 | 標的 | profile（維度）來源 | 產出動作 |
|------|------|-------------------|---------|
| [ep-review](../../commands/ep-review.md) | EP | 自訂（架構 + 完整性 + 場景 + 兜底拆解） | 回寫 EP |
| [code-review](../../commands/code-review.md) | git diff | [code-review-and-quality](../code-review-and-quality/SKILL.md) 六軸 | findings + commit message |
| [audit-test](../../commands/audit-test.md) | test files | 自訂六角度 | 偵測報告 + 健康度（read-only） |
| execution-plan EP Review / build Agent Review | EP / code | 各自 profile | 回寫 EP / apply |

**模式使用**（審查模式判定規則見上「審查模式判定規則」段；此處說明各命令實際用哪些）：
- **code-review**：完整三模式（Workflow / Agent Tool / **Main LLM**）— 可選審查，effort 低時允許主 LLM 直接審
- **ep-review / execution-plan EP Review / build Agent Review**：總用獨立 agent（Workflow / Agent Tool），**刻意不走 Main LLM** —— 內建流程的強制品質閘門（Writer/Reviewer 分離）
- **audit-test**：不經模式判定（read-only 單一 agent 偵測，不做平行審查）

維度知識（架構視角/機械）依賴 arch-thinking，非本 skill 包含。

> **`/codebase-sweep`（非 review 命令家族，但複用本 skill 的 severity/confidence 框架標其 §HR findings）**：baseline per-directory sweep，產 `codebase-review/<dir>/` 4 檔；**非** change-driven（不審 diff、不 spawn review agents）→ **不適用本段執行預設**（force 獨立/max-agents/3-perspective 是 change review 的）；自有 baseline 流程（廣到精細 + 受眾分離，見 [codebase-sweep](../../commands/codebase-sweep.md)）。
