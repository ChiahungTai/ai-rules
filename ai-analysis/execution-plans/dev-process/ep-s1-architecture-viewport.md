# EP: S1 architecture-viewport skill（機械能力下沉）

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S1 段展開）
> **本 EP**:master S1 的 implementation 展開 — 從 `arch-review.md:83-206` 抽機械能力（City Map / Pattern Radar / 重用 lifecycle / LSP 查證 / domain grounding），下沉為可複用 skill（給 illustrate / code-review / ep-review 共用）。**機械能力，不決定受眾**。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

`/arch-review` 的機械能力綁死在命令內部，`/code-review` axis 3、`/ep-review`、`/illustrate` 都需要卻各自闕如或重造。下沉為 skill 讓四消費端共用。**能力下沉、受眾保留** — skill 給機械能力（列舉 + 查證），不渲染心智模型（illustrate 人 viewport 職責）、不產 finding 格式（code-review 機器職責）。A/B 軸靠消費命令產出形式區分。

**本 EP 範圍**（master S1）：建 `skills/architecture-viewport/SKILL.md`，4 段對應 skill 章節。吸收 `ep-review-pipeline-grounding` 的 dep weight（#14）、reuse lifecycle（#14）、domain grounding（#17）。**S1a 處理 task #7**（N1 RC-1 措辭：scan-project dep_graph vs findings 精確）。

**Scope out**：S2 illustrate 擴充（master 另段）、S3 arch-review 移除、S5 code-review axis3 調用（消費端，本 EP 只建 skill）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S1a** | skill 骨架 + 受眾明文 + 邊界（scan-project dep_graph vs findings — **N1 task #7** / lsp-navigation） | 無 |
| **S1b** | City Map **資料生成** + dep weight（吸收 #14；視覺渲染留 illustrate） | 無 |
| **S1c** | Pattern Radar 重用枚舉 + lifecycle（吸收 #14 reuse） | 無 |
| **S1d** | domain grounding（吸收 #17）+ LSP 查證 + RC-3 邊界 | 無 |

4 段同檔（skill 各章節），可平行。建議順序 **S1a（骨架）→ S1b ∥ S1c ∥ S1d**。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### 掃描範圍
- 能力來源 [arch-review.md](../../../commands/arch-review.md) `:83-97`（City Map）、`:124-164`（Pattern Radar + 信心度）、`:185-206`（Phase 2 查證）
- 新檔 `skills/architecture-viewport/SKILL.md`
- 邊界參考 [scan-project/SKILL.md](../../../skills/scan-project/SKILL.md)（dep_graph .py only）、[lsp-navigation.md](../../../rules/lsp-navigation.md)
- 收尾 [skills/CLAUDE.md](../../../skills/CLAUDE.md) 索引

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 結構機械能力（City Map/重用/查證/grounding，可複用） | 📋 | `skills/architecture-viewport/SKILL.md`（S1a-d） |

---

## Scenario Matrix（中型變更，docs mode）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | code product-type city map | 結構審查 code | 複用 scan-project dep_graph + dep weight（lean/heavy） | 無 | 機械能力 |
| SM-2 | docs product-type city map | 結構審查 docs | 自己 rg 跨檔畫命令/skill 拓樸（scan-project dep_graph .py only 不適用;findings 仍可用） | 無 | 機械能力 |
| SM-3 | 重用枚舉 | 變更含新 symbol | Pattern Radar（Enum/Fn/DataStruct + Jaccard + 信心度）+ lifecycle（實作後 re-review） | 無 | 機械能力 |
| SM-4 | 外部框架語意宣稱 | 審查含 NT/SJ 宣稱 | domain grounding 強制查 stub/source 附 path:line;未 grounding 標 open 非 verified | 無 | 機械能力 |
| SM-5 | 受眾區分 | 消費命令呼叫 skill | skill 不決定受眾;illustrate 渲染給人（B 軸）/ code-review 產 finding（A 軸） | 無 | 機械能力 |

---

## S1a: skill 骨架 + 受眾明文 + 邊界（含 N1 task #7）

### Context
- **背景**：建 skill 骨架 + 「機械能力不決定受眾」明文 + 與 scan-project / lsp-navigation 邊界。**處理 task #7**（N1 RC-1 措辭精確化：scan-project 的 dep_graph vs findings）。
- **UC 引用**：新增「結構機械能力」
- **依賴**：無（新檔）
- **語義約束**：skill 只給機械能力（列舉 + 查證），不決定受眾（產出給人/機器由消費命令定）。
- **依賴錨點**：無（新檔）。參考 [scan-project/SKILL.md](../../../skills/scan-project/SKILL.md) `:4/:27`（dep_graph = AST-parsed Python import，.py only）、[lsp-navigation.md](../../../rules/lsp-navigation.md)（LSP 決策樹）
- **成功標準**：
  - [ ] `skills/architecture-viewport/SKILL.md` 骨架 + frontmatter description（觸發詞：city map / dep weight / Pattern Radar / 重用枚舉 / domain grounding / 結構查證 / 結構 viewport）
  - [ ] 「機械能力，不決定受眾；消費命令決定產出給人（illustrate）/ 機器（code-review）」明文
  - [ ] **scan-project 邊界（N1 task #7 精確措辭）**：code 場景**複用 scan-project dep_graph**（.py AST，不重造）;docs 場景 scan-project 的 **dep_graph 不適用**（.py only）→ 自己 rg 跨檔畫命令/skill 拓樸;**但 scan-project 的 code↔doc findings（掃 CLAUDE.md）仍可用**
  - [ ] lsp-navigation 邊界：本 skill 用 LSP，決策樹引用 lsp-navigation rule（非重造）
  - [ ] 機械分工：scan-project 枚舉 primary、lsp-architect agent 驗證 secondary

### 修改要點
1. 建 `skills/architecture-viewport/SKILL.md`：frontmatter + 開頭「機械能力不決定受眾」明文 + 邊界段（N1 精確 scan-project 措辭 + lsp-navigation）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "不決定受眾|dep_graph 不適用|code↔doc findings|lsp-navigation|枚舉 primary" skills/architecture-viewport/SKILL.md` → 命中
- **`/consistency`**：跑 skill 檔
- **task #7**：S1a 落地 N1 精確措辭後，關閉 task #7

---

## S1b: City Map **資料生成** + dep weight（吸收 #14；視覺渲染留 illustrate）

### Context
- **背景**：City Map（模組 + 依賴方向 + dep weight lean/heavy + 消費者數）。吸收 review-pipeline #14（重型 helper 抽進 lean 廣用模組 anti-pattern）。
- **依賴**：S1a（骨架）
- **依賴錨點**：[arch-review.md](../../../commands/arch-review.md) `:83-97`（元件 A City Map）
- **成功標準**：
  - [ ] City Map **資料生成**（非渲染）：節點關係 + **dep weight**（lean = stdlib/輕量;heavy = numpy/pandas/polars/nautilus/大型框架）+ 消費者數（誰 import）— **視覺渲染**（節點 + 依賴箭頭 ASCII/Mermaid）留 illustrate（既有渲染引擎,arch-review.md:204）
  - [ ] 「heavy symbol → lean 廣用模組」反向耦合 flag（transitive burden：lean 模組所有消費者被拖入重依賴）
  - [ ] 資料範例（供 illustrate 渲染）（catalog_utils(lean, 12 consumers) vs dataframe_utils(heavy, 3 consumers)）

### 修改要點
1. SKILL.md 加 City Map 段（dep weight + 反向耦合 flag + 資料範例（供 illustrate 渲染），從 arch-review `:83-97` 抽 + #14 dep weight）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "dep weight|lean|heavy|消費者數|反向耦合|transitive burden" skills/architecture-viewport/SKILL.md` → 命中

---

## S1c: Pattern Radar 重用枚舉 + lifecycle（吸收 #14 reuse）

### Context
- **背景**：Pattern Radar（Enum/Fn/DataStruct 重複枚舉 + Jaccard + 信心度）+ 重用 lifecycle（實作後 re-review）。吸收 review-pipeline #14 reuse lifecycle。
- **依賴**：S1a
- **依賴錨點**：[arch-review.md](../../../commands/arch-review.md) `:124-164`（元件 D 重用枚舉 + 信心度表）
- **成功標準**：
  - [ ] Pattern Radar 三類：Enum 重複（LSP workspaceSymbol + rg 成員）/ Function 重複（workspaceSymbol + outgoingCalls）/ Data Structure 重複（rg 欄位 Jaccard）
  - [ ] 信心度評分（名稱相似/值簽名重疊/import 路徑/呼叫圖/欄位 Jaccard >0.6）+ 門檻（HIGH ≥7 / MEDIUM 4-6 / LOW 1-3）
  - [ ] **重用 lifecycle**：RC 實作後 re-review 放置點（實作抽 helper → 重跑查新 symbol 落點）（吸收 #14 reuse）

### 修改要點
1. SKILL.md 加 Pattern Radar 段（三類 + 信心度 + 門檻，從 arch-review `:124-164` 抽）+ lifecycle 段（#14 reuse）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "Pattern Radar|Jaccard|信心度|lifecycle|實作後.*re-review|HIGH.*MEDIUM" skills/architecture-viewport/SKILL.md` → 命中

---

## S1d: domain grounding + LSP 查證 + RC-3 邊界（吸收 #17）

### Context
- **背景**：domain grounding（外部框架語意強制查 stub/source 附 path:line）+ LSP 查證（findReferences/incomingCalls/outgoingCalls）。吸收 review-pipeline #17（review 未 grounding NT 宣稱）。
- **依賴**：S1a
- **依賴錨點**：[arch-review.md](../../../commands/arch-review.md) `:185-206`（Phase 2 查證分工）;review-pipeline #17（domain grounding 來源）
- **成功標準**：
  - [ ] **domain grounding**：外部框架語意宣稱（NT/SJ account/equity/engine/第三方能力邊界）強制查 stub/source 附 path:line;未 grounding 標 `open`（未驗證）非 `verified` — 不隨 fix 寫進 CLAUDE.md 變正式宣稱
  - [ ] 觸發訊號：宣稱含「X 支援/不做 Y」「X 底層是 Z」「跨模型成立」等能力邊界語句
  - [ ] LSP 查證：findReferences（誰引用）/ incomingCalls（誰呼叫）/ outgoingCalls（呼叫誰）
  - [ ] **RC-3 邊界**：domain grounding = review/結構審查時;與 source-driven（實作 grounding）/ external-api-investigation（runtime 調查）/ nt-query（能力查詢）區分,非第四個過載

### 修改要點
1. SKILL.md 加 domain grounding 段（強制查 + 觸發訊號 + open 非 verified）+ LSP 查證段 + RC-3 邊界

### 驗證策略（docs mode）
- **rg 閘門**：`rg "domain grounding|path:line|findReferences|incomingCalls|outgoingCalls|RC-3|open.*verified" skills/architecture-viewport/SKILL.md` → 命中

---

## 收尾

### 受影響索引同步
- [skills/CLAUDE.md](../../../skills/CLAUDE.md)：索引加 `architecture-viewport`（架構與演進段 — 結構機械能力，可複用）
- `lsp-architect` agent 定位：architecture-viewport 的**查證 helper**（agent，非 skill — skill 不能擁有 agent，但 agent 是 skill 的查證手段）

### 回母 EP
本 EP 完成（master S1 build+commit）後,master 綱要 S1 段標 ✅。

### 風險與緩解
- **skill 高扇入**（3 命令共用 illustrate/code-review/ep-review）→ DRY 代價,skill 修改影響面大 → /consistency 閘門 + 頂層總綱（S0 architecture-thinking）指導
- **product-type 雙軌**（code 複用 scan-project dep_graph / docs 自己 rg）→ S1a 邊界明文,避免混用
- **domain grounding 第四個載體**（RC-3）→ 明文「review/結構審查時」獨立邊界,與 3 既有 grounding 區分
