# EP: S2 illustrate 擴充 — 結構 viewport 載體 + pre-EP checkpoint

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S2 段展開）
> **本 EP**:master S2 的 implementation 展開 — illustrate 加 city map/call stack/對話式 drill（吸收 arch-review 職責 A 的人 viewport 部分）+ **流程彈性化**（pre-EP 軟 gate）。illustrate 成為**人類 viewport 結構探索載體**（B 軸）+ 通用圖解。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

`/illustrate` 現是通用圖解（概念/架構/流程）。S1 已把 `/arch-review` 機械能力下沉為 [architecture-viewport](../../../skills/architecture-viewport/SKILL.md) skill（City Map 資料 / Pattern Radar / LSP 查證）。S2 讓 illustrate 成為**人類 viewport 結構探索載體** — 調用 skill 渲染 city map/call stack + 對話式 drill，吸收 arch-review 的人 viewport 職責（結構判讀）。**能力下沉、受眾保留**：skill 給資料（S1），illustrate 渲染給人判讀（B 軸，本 EP）。

**流程彈性化**：現狀結構確認在 post-EP（`/arch-review --ep`，[arch-review.md](../../../commands/arch-review.md) `:262-270`），EP 已寫完、結構已貴。S2 前移到 pre-EP — 但**不是剛性「spec→illustrate→ep」**，而是「討論到一定程度時的結構催化劑」（對話討論 → 提醒 illustrate 結構化提案 → 人判讀 → 直接 EP 或先 spec）。**EP 必備起點、spec 可選前置**。**軟 gate**（F4）：pre-EP 是標註+提醒，不硬擋（前移價值靠提醒而非強制，避免流程摩擦）。

**本 EP 範圍**（master S2）：擴充 [illustrate.md](../../../commands/illustrate.md) 本體（核心能力 + pre-EP checkpoint + 決策流程）+ 新增 supporting file（drill 指令）+ 更新 [commands/CLAUDE.md](../../../commands/CLAUDE.md) 流程圖。

**Scope out**：S3 arch-review 移除（本段 arch-review 引用暫留，S3 才清）、S5 code-review axis3（消費端機器 finding，本 EP 只建 illustrate 人 viewport 載體）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S2a** | illustrate.md 本體擴充 — 核心能力加 city map/call stack/結構 viewport（調用 S1 skill）+ pre-EP checkpoint 段（彈性 + 軟 gate）+ 決策流程分支 | S1（skill） |
| **S2b** | 新增 supporting file `illustrate-structure-viewport.md` — drill 指令 + Phase 2 互動式 + 機械分工（從 arch-review.md 搬） | S2a |
| **S2c** | commands/CLAUDE.md 流程圖補 pre-EP illustrate checkpoint + illustrate description 補結構 viewport | S2a/S2b |

3 段，序列（S2a 本體 → S2b supporting → S2c 流程圖同步）。本體精簡，drill 細節分離到 supporting file。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### 掃描範圍
- 能力來源 [arch-review.md](../../../commands/arch-review.md) `:83-110`（City Map + Key Flows 渲染範例）、`:166-181`（drill 指令）、`:185-206`（Phase 2 互動式 + 機械分工）
- 主檔 [illustrate.md](../../../commands/illustrate.md)（`:18-22` 核心能力 / `:24-46` 現有程式碼優先 / `:79-89` 決策流程 / `:96-102` supporting files 表）
- 新檔 `commands/claude/_common/illustrate-structure-viewport.md`
- 流程圖 [commands/CLAUDE.md](../../../commands/CLAUDE.md) `:20-25`（流程圖）/ `:18-37`（命令分類）

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| pre-EP 結構 checkpoint（彈性、軟 gate） | 📋 | `commands/illustrate.md`（S2a） |
| 結構 viewport 載體（city map/call stack/drill，人 viewport B 軸） | 📋 | `commands/illustrate.md` + supporting（S2a/S2b） |

---

## Scenario Matrix（中型變更，docs mode）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 用戶與 LLM 討論新功能到一定程度 | 對話中、要決定方向時 | **提醒** `/illustrate` 畫提案結構（軟 gate：標註+提醒，不硬擋）→ 人判讀 → 直接 EP 或先 spec | 無 | pre-EP checkpoint |
| SM-2 | 人想看 EP/架構整體結構 | post-EP 或任意時點 | `/illustrate --ep` 渲染 city map/call stack/重用/邊界，人判讀（原 arch-review --ep 的活） | 無 | 結構 viewport 載體 |
| SM-3 | 人 drill 結構嫌疑 | 對話式互動 | drill 指令 city/flow/reuse/verify/boundary + 機械分工（scan-project/Pattern Radar 枚舉 primary、lsp-architect 驗證 secondary） | 無 | 結構 viewport 載體 |

---

## S2a: illustrate.md 本體擴充 — 核心能力 + pre-EP checkpoint + 決策流程

### Context
- **背景**：illustrate 核心能力（`:18-22`）加 city map/call stack/結構 viewport（調用 architecture-viewport skill，B 軸人 viewport）。新增「pre-EP checkpoint（彈性 + 軟 gate）」段。決策流程（`:79-89`）加「結構 viewport / pre-EP」分支。
- **UC 引用**：更新「圖解」+ 新增「pre-EP 結構 checkpoint」
- **依賴**：S1（[architecture-viewport](../../../skills/architecture-viewport/SKILL.md) skill — City Map 資料 / Pattern Radar / LSP 查證來源）
- **語義約束**：illustrate 成為**人類 viewport 結構探索載體**（B 軸）+ 通用圖解。**軟 gate**（F4）：pre-EP 標註+提醒不硬擋。對齊用戶「illustrate 是討論中催化劑，非固定節點」。
- **依賴錨點**：[illustrate.md](../../../commands/illustrate.md) `:18-22`（核心能力）、`:24-46`（現有程式碼優先 — 結構 viewport 延伸此原則）、`:79-89`（決策流程）；搬入 [arch-review.md](../../../commands/arch-review.md) `:83-110`（City Map + Key Flows 渲染範例）
- **成功標準**：
  - [ ] 核心能力（`:18-22`）加：**city map**（調用 architecture-viewport skill，含 dep weight lean/heavy + 反向耦合 flag）、**call stack**（重要節點呼叫鏈，LSP incomingCalls/outgoingCalls）、**結構 viewport**（調用 skill，B 軸人 viewport — city map + flows + boundaries + 重用枚舉）
  - [ ] 新增「pre-EP checkpoint（彈性 + 軟 gate）」段：**討論中介入**（非線性 spec→illustrate→ep，而是對話討論 →〔提醒〕illustrate 結構化提案 → 確認 → EP）+ **軟 gate 明文**（標註+提醒不硬擋）+ **EP 必備、spec 可選** + 引用 [architecture-thinking](../../../skills/architecture-thinking/SKILL.md)（S0c 視角）
  - [ ] 決策流程（`:79-89`）加「結構 viewport / pre-EP」分支（結構 viewport 觸發時調用 skill 渲染）
  - [ ] 委託 skills 段（`:91-92`）加 `architecture-viewport`（結構 viewport 能力來源）

### 修改要點
1. **核心能力**（`:18-22`）：加 city map/call stack/結構 viewport（調用 S1 skill）
2. **新增「pre-EP checkpoint（彈性 + 軟 gate）」段**（在決策流程前）：討論中介入 + 軟 gate + EP 必備 spec 可選 + 引用 architecture-thinking
3. **決策流程**（`:79-89`）：加「結構 viewport / pre-EP」分支
4. **委託 skills**（`:91-92`）：加 architecture-viewport

### 驗證策略（docs mode）
- **rg 閘門**：`rg "city map|call stack|結構 viewport|pre-EP|軟 gate|討論.*催化|architecture-viewport" commands/illustrate.md` → 命中
- **跨檔一致**：city map/call stack 能力與 architecture-viewport skill 對應
- **`/consistency`**：跑 illustrate.md

---

## S2b: 新增 supporting file illustrate-structure-viewport.md（drill + 機械分工）

### Context
- **背景**：drill 指令（city/flow/reuse/verify/boundary）+ Phase 2 互動式調查 + 機械分工從 [arch-review.md](../../../commands/arch-review.md) `:166-206` 搬到 illustrate 的 supporting file（避免本體過肥）。illustrate 本體引用此 file。能力來源標 architecture-viewport skill。
- **依賴**：S2a（本體已建立結構 viewport 概念）
- **依賴錨點**：[arch-review.md](../../../commands/arch-review.md) `:166-181`（drill 指令 — city/flow/reuse/verify/boundary）、`:185-206`（Phase 2 互動式調查表 + 機械分工）
- **成功標準**：
  - [ ] 新檔 `commands/claude/_common/illustrate-structure-viewport.md`：
    - **drill 指令**（從 arch-review `:166-181` 搬）：`city <module>`（放大依賴細節）/ `flow <use-case>`（畫另一 flow）/ `reuse <RC-XXX>`（深入重用嫌疑）/ `verify <symbol>`（lsp-architect 驗 refs/call chain）/ `boundary <module>`（細看邊界）+ 自然語言 free-form
    - **Phase 2 互動式調查表**（從 `:185-194` 搬）：重用嫌疑 / 結構可疑 / 邊界 / free-form → LLM 調查方式
    - **機械分工**（從 `:196-206` 搬）：scan-project/Pattern Radar **枚舉 primary**（撈全 + 相似，餵人 whole-picture）/ `lsp-architect` **驗證 secondary**（人鎖定嫌疑後驗證）/ illustrate **渲染**
    - 標明「能力來源 [architecture-viewport](../../../skills/architecture-viewport/SKILL.md) skill；從 arch-review 搬入」
  - [ ] [illustrate.md](../../../commands/illustrate.md) supporting files 表（`:96-102`）加此檔 + 何時讀取（結構 viewport / drill 時）

### 修改要點
1. **新檔 `illustrate-structure-viewport.md`**：drill 指令 + Phase 2 互動式 + 機械分工（從 arch-review `:166-206` 搬 + 標 skill 來源 + 標 B 軸人 viewport）
2. **illustrate.md supporting files 表**（`:96-102`）：加此檔

### 驗證策略（docs mode）
- **rg 閘門**：`rg "city <module>|flow <use-case>|reuse <RC|verify <symbol>|boundary <module>|枚舉 primary|lsp-architect 驗證 secondary|能力來源.*architecture-viewport" commands/claude/_common/illustrate-structure-viewport.md` → 命中
- **`/consistency`**：跑 supporting file（確認與 skill 邊界不衝突）

---

## S2c: commands/CLAUDE.md 流程圖 + illustrate description

### Context
- **背景**：流程圖（[commands/CLAUDE.md](../../../commands/CLAUDE.md) `:20-25`）反映 pre-EP illustrate checkpoint（彈性）。`/illustrate` description 補「結構 viewport，三時點（pre-EP/post-EP/post-build）」。**注意**：S3 才移除 arch-review，本段流程圖先補 illustrate pre-EP（arch-review 引用暫留，S3 清）。
- **依賴**：S2a/S2b
- **依賴錨點**：[commands/CLAUDE.md](../../../commands/CLAUDE.md) `:20-25`（流程圖）、`:18-37`（命令分類 + `/illustrate` description 在「其他」段末行）
- **成功標準**：
  - [ ] 流程圖（`:20-25`）補 pre-EP illustrate checkpoint：**對話討論 →〔提醒〕illustrate（軟 gate）→ 確認 → execution-plan**（spec 可選、EP 必備）— arch-review 引用暫留（S3 移除）
  - [ ] `/illustrate` description（命令索引「其他」段）補「**結構 viewport**（city map/call stack/drill），三時點（pre-EP/post-EP/post-build），人 viewport B 軸」— 對齊 S3 遷移預期

### 修改要點
1. **流程圖**（`:20-25`）：在 `/spec` 前補 pre-EP illustrate（軟 gate 提醒）— 對話 → illustrate → execution-plan
2. **`/illustrate` description**（命令索引）：補結構 viewport + 三時點

### 驗證策略（docs mode）
- **rg 閘門**：`rg "pre-EP|illustrate.*checkpoint|三時點|結構 viewport|軟 gate" commands/CLAUDE.md` → 命中
- **`/consistency`**：跑 commands/CLAUDE.md（確認流程圖與 illustrate.md 一致）

---

## 收尾

### 受影響索引同步
- [commands/CLAUDE.md](../../../commands/CLAUDE.md)：流程圖（pre-EP illustrate checkpoint）+ `/illustrate` description（結構 viewport + 三時點）— 本段（S2c）處理
- [skills/CLAUDE.md](../../../skills/CLAUDE.md)：無（illustrate 非 skill；S1 已加 architecture-viewport 索引）

### 回母 EP
本 EP 完成（master S2 build+commit）後，master 綱要 S2 段標 ✅。

### 風險與緩解
- **illustrate 職責變廣**（通用圖解 + 結構 viewport）→ 模式/參數區分（`@ep`/`@dir`/主題）+ supporting file 分離 drill 細節（本體精簡，S2b）
- **pre-EP 軟 gate vs 硬 gate 張力** → 明文「標註+提醒不硬擋」，保留前移價值又不卡流程（F4）
- **S2 與 S3 時序**：S2 先補 illustrate（arch-review 暫留），S3 才移除 arch-review — 流程圖本段先補 illustrate pre-EP，arch-review 引用 S3 清（避免 S2 階段流程圖斷裂）
