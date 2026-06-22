---
name: arch-viewport
description: 結構機械能力（City Map 資料/dep weight/Pattern Radar 重用枚舉/domain grounding/LSP 查證），可複用 — illustrate / code-review / ep-review 共用。「機械能力，不決定受眾」。觸發詞：city map、dep weight、lean/heavy、Pattern Radar、重用枚舉、Jaccard、domain grounding、結構查證、結構 viewport、反向耦合。
---

# Architecture Viewport — 結構機械能力（可複用）

結構審查的**機械能力**（列舉 + 查證），給 `/illustrate`（人 viewport）/ `/code-review` axis 3（機器）/ `/ep-review` 共用。**機械能力，不決定受眾** — 渲染心智模型、產 finding 格式、決定受眾，**都不做**（消費命令定）。

頂層視角（分層依賴 / bounded context / use case 驅動）見 [arch-thinking](../arch-thinking/SKILL.md)；本 skill 是**機械層**（列舉 + 查證資料）。

## product-type 雙軌

| 場景 | dep_graph 來源 | 查證工具 |
|------|--------------|---------|
| **code** | 複用 [scan-project](../scan-project/SKILL.md) dep_graph（.py AST，**不重造**） | scan-project 枚舉 primary + lsp-architect 驗證 secondary |
| **docs** | scan-project dep_graph **不適用**（.py only）→ 自己 rg 跨檔畫命令/skill 拓樸 | rg（取代 lsp-architect） |

> scan-project 的 **code↔doc findings**（掃 CLAUDE.md Capabilities）在 docs 場景仍可用；只有 **dep_graph**（.py AST）不適用 docs。

LSP 決策樹見 [lsp-navigation](../../rules/lsp-navigation.md)（本 skill 用 LSP，非重造決策樹）。

## City Map 資料生成（非渲染）

**生成資料**（節點關係 + dep weight + 消費者數）；**視覺渲染**（節點 + 依賴箭頭 ASCII/Mermaid）留 `/illustrate`（既有渲染引擎）。

每節點標註：
- **依賴方向**：A ──uses──▶ B
- **dep weight**：lean（stdlib/輕量）/ heavy（numpy/pandas/polars/nautilus/大型框架）
- **消費者數**：誰 import 它

**反向耦合 flag**：「heavy symbol → lean 廣用模組」= anti-pattern（transitive burden：lean 模組所有消費者被拖入重依賴）。

資料範例（供 illustrate 渲染）：
- `catalog_utils`（lean, 12 consumers）
- `dataframe_utils`（heavy, 3 consumers）
- ⚠️ polars helper 抽進 `catalog_utils`（lean）→ 反向耦合 flag

## Pattern Radar（重用枚舉）

三類重複偵測：

| 類型 | 觸發 | 搜尋 |
|------|------|------|
| Enum 重複 | 新 enum | LSP `workspaceSymbol` + rg 成員值 |
| Function 重複 | 新 func | `workspaceSymbol` + `outgoingCalls` 比對 |
| Data Structure 重複 | 新 dataclass | rg 欄位 overlap（Jaccard） |

**信心度評分**（加權加總）：

| 因子 | Enum | Function | Data Struct |
|------|------|----------|-------------|
| 名稱相似 | +3 | +5 | +3 |
| 值/簽名重疊 | +4 | +4 | +6 |
| Import 路徑已通 | +3 | — | +3 |
| 呼叫圖重疊 | — | +4 | — |
| 欄位重疊 >60%（Jaccard） | — | — | +5 |

**門檻**：HIGH ≥7 / MEDIUM 4-6 / LOW 1-3。只展示 HIGH + MEDIUM；LOW 收 drill-down。

**重用 lifecycle**：重用候選（RC）實作後（抽 helper），**重跑查新 symbol 落點**（dep weight + 消費者）— 實作 RC 是新結構決策，需 re-review 放置點再 commit。

## domain grounding（外部框架語意查證）

外部框架語意宣稱（NT/SJ account/equity/engine / 第三方能力邊界）**強制查 stub/source 附 path:line**。

- 觸發訊號：宣稱含「X 支援/不做 Y」「X 底層是 Z」「跨模型成立」等能力邊界語句
- **未 grounding 標 `open`（未驗證）非 `verified`** — 不隨 fix 寫進 CLAUDE.md 變正式宣稱

**RC-3 邊界**：domain grounding = **review / 結構審查時** grounding；與 [source-driven-development](../source-driven-development/SKILL.md)（實作 grounding）/ [external-api-investigation](../external-api-investigation/SKILL.md)（runtime 調查）/ [nt-query](../nt-query/SKILL.md)（能力查詢）區分，非第四個過載。

## LSP 查證（call chain）

| 查詢 | LSP 操作 |
|------|---------|
| 誰引用 X | `findReferences` |
| 誰呼叫 X | `incomingCalls` |
| X 呼叫誰 | `outgoingCalls` |

**機械分工**：scan-project / Pattern Radar **枚舉**（撈全 + 相似）= primary；`lsp-architect` agent **驗證**（特定 claim → ✅/❌）= secondary（人鎖定嫌疑後才上驗證）。

## 不做

- **渲染心智模型**（節點 + 箭頭視覺）→ `/illustrate`
- **產 finding 格式** → `/code-review`
- **決定受眾**（給人 / 機器）→ 消費命令
