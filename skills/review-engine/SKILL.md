---
name: review-engine
description: review 命令家族通用審查邏輯的 domain 真相源 — 嚴重度分級（Critical/Important/Suggestion）、信心水準（confirmed/evidence-based/inferred）、審查者自證、LSP 查證方法、審查模式判定（Workflow/Agent Tool/Main LLM）、Writer-Reviewer 分離、多層驗證設計。所有 review 命令（ep-review/code-review/audit-test/execution-plan EP Review/build Agent Review）共用。觸發：決定 finding 嚴重度、標信心水準、查證審查宣稱、選審查模式、理解多層驗證鏈。
---

# review-engine — 通用審查邏輯 domain 層

review 命令家族的 **domain 層**：跨 ep-review / code-review / audit-test / execution-plan EP Review / build Agent Review 共用的審查邏輯，**唯一真相源**。各命令是薄 adapter（宣告標的 + profile + 產出，委託本 skill），消除「同一審查動作跨命令重複定義且 drift」。

## 收進判準

一條邏輯收進本 skill 的條件：**所有 review 命令都適用**。只適用部分命令的（如 audit-test 的「偵測器非判官」stance、test 的「套件行為寫 demo」）不收，留該命令。

## 邊界（避免製造新 drift）

| vs | review-engine（本 skill） | 對方 |
|----|--------------------------|------|
| [workflow-review-pattern](../../commands/claude/_common/workflow-review-pattern.md) | **方法論 + 判定規則**（嚴重度意義、信心水準、自證、為何分離、審查模式判定規則） | **Workflow 執行**：DimensionVerdict schema、兩階段腳本、Finding Record 持久化（判定規則 → 決定讀哪個 schema，依賴方向非耦合） |
| [agent-review-cycle](../../commands/claude/_common/agent-review-cycle.md) | （不重疊） | **Agent Tool 模式執行範本**（2-perspective） |
| [architecture-thinking](../architecture-thinking/SKILL.md) / [architecture-viewport](../architecture-viewport/SKILL.md) | **依賴**它們（架構審查需要視角/機械） | 提供架構視角/機械能力 |
| audit-test 三層驗證鏈 | 通用 why（各層都可能錯） | **具體 audit→judge→followup 鏈細節**（test 講最細，留 audit-test） |

**不裝**（留各 adapter）：維度定義（各 profile 自訂）、產出動作（回寫 EP / commit message / 報告）、stance（audit「偵測器非判官」）、Workflow schema/腳本（留 workflow-review-pattern）。

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

**唯一判定規則**（消 build/code-review/ep-review 三處重複定義）：

| 條件 | 模式 | 執行範本 |
|------|------|---------|
| effort = ultracode/xhigh **且** max-agents > 1 | **Workflow** | [workflow-review-pattern](../../commands/claude/_common/workflow-review-pattern.md)（schema + 兩階段腳本 + adversarial verify） |
| max-agents = 1 但 effort = ultracode/xhigh | **Agent Tool**（Fallback） | [agent-review-cycle](../../commands/claude/_common/agent-review-cycle.md)（2-perspective） |
| effort < ultracode | **Main LLM** | 主 LLM 直接審（現有行為） |

判定結果決定讀哪個執行範本的 schema/腳本 —— 這是**依賴方向**（判定 → schema），不是耦合。本 skill 只放判定規則，**不重複** schema/腳本（在 workflow-review-pattern）。

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

維度知識（架構視角/機械）依賴 architecture-thinking + architecture-viewport，非本 skill 包含。
