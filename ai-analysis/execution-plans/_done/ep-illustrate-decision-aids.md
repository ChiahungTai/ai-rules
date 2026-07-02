# EP — /illustrate 決策輔助強化（導航深度 + 設計替代 + 行動路徑）

> **ep_type**: implementation（docs mode）
>
> **背景**：post-hoc 評估 mosaic_alpha `a760bf60`（Jun 26）/illustrate（mode A 設計決策）發現——illustrate 產出高品質結構 artifact、user 深度 engage（達成 B 軸人 viewport 催化思考的目標），但從「結構分析」到「助決策」還差一步。兩個證據導向本次改善。

## 證據（transcript，非推測）

- **F1 證據**：`a760bf60:124` illustrate city map 畫 `ExecClient → AccountState → Cache`，但 `a760bf60:126` user 立刻問「**balance_free 是 data client 還是 ExecClient?**」——city map 導航到模組層，沒 pin 到「欄位 ← 發布 client」，user 得再問。
- **F2/F3 證據**：`a760bf60:124` illustrate flag EP1 paper override 是邊界 + 建議「寫成 augmentation 契約不變量（文件化）」，但 `a760bf60:126` user 朝「**繼承是否更根本（重構）**」想——illustrate 給「現狀分析 + 文件化建議」，user 要「設計替代方案 + 重構路徑」。

## 實作總覽

兩段，平行（無依賴），皆 docs mode。

| 段 | 改善 | 落點 | 證據 |
|----|------|------|------|
| **S1** | city map 導航深度——審 authority 時加「欄位 ← 發布者」annotation | `commands/claude/_common/illustrate-structure-viewport.md` | F1 |
| **S2** | mode A 決策輔助——邊界案例列設計替代方案 + 行動路徑分流（文件化 vs 重構） | `commands/illustrate.md` | F2 + F3 |

無 `.py` callable 變更 → docs mode（驗證 = rg 殘留 + 跨檔一致性 + `/consistency`）。

## Scenario Matrix（docs mode）

| # | 場景 | 觸發 | 預期行為 | 對應段 |
|---|------|------|---------|--------|
| SM-1 | user 問「X 欄位是誰發布的」 | city map 審 authority | city map 本身已標「欄位 ← 發布者」，不用再問 | S1 |
| SM-2 | illustrate flag 邊界案例 / smell | mode A 邊界 | 列 2-3 設計替代 + tradeoff（不只分析現狀） | S2 |
| SM-3 | illustrate 給改善建議 | 邊界 case 結論 | 分流「文件化契約（保守）」vs「重構修正（根本）」+ 取捨，user 選 | S2 |

---

## S1 — city map 導航深度（欄位 ← 發布者）

### Context

`illustrate-structure-viewport.md` 現有「位置標示（可點擊）」段（repo-root path:line）。city map 渲染到「模組層」，但 user 審 authority（誰是權威源）時需要「欄位 ← 發布者」粒度（F1 證據：user 得追問）。

### 修改要點

在「位置標示」段後補一小節「**city map 導航深度**」：
- 預設：city map 渲染到模組層（不過載）。
- **審 authority / 資料流時**：加「欄位 ← 發布者」annotation（如 `account_for_venue ← ExecClient AccountState`、`price ← DataClient`）——導航從「模組→符號」下到「欄位→發布者」。
- 觸發判準：user 問「誰發布 X」「X 權威源」「data vs exec client」等 authority 語境 → 自動加這層；否則不加（避免噪音）。

### 驗證（docs mode）
- `rg "欄位.*發布者|導航深度|authority" commands/claude/_common/illustrate-structure-viewport.md` 命中。
- `/consistency illustrate-structure-viewport.md`。

---

## S2 — mode A 決策輔助（設計替代方案 + 行動路徑分流）

### Context

`illustrate.md` mode A（設計決策）目前偏「分析現狀 + flag 邊界」（F2 證據：user 要替代方案）。flag 邊界後的建議偏「文件化」（F3 證據：user 想重構）。mode A 的 DNA 是「結構分析」，缺「方案探索 + 行動路徑」。

### 修改要點

1. **4-mode 表 mode A 行**：「city map + 流程 + 重用枚舉」補「**＋ 邊界案例列設計替代**」。
2. **決策流程 mode A 分支**：「讀 code → city map + 流程 + 重用枚舉 → 渲染」補「**→ 邊界案例列 2-3 設計替代 + tradeoff**」。
3. **新增小節「邊界案例的行動路徑分流」**（mode A 輸出指引）：flag 邊界 / smell 時，給兩條行動路徑 + 取捨——
   - **文件化契約**（保守、快速、低風險）：把不變量寫進 CLAUDE.md。
   - **重構修正**（根本、風險高）：改結構（繼承 / strategy / 重寫）。
   - 讓 user 選，不預設。

### 驗證（docs mode）
- `rg "設計替代|行動路徑|文件化.*重構|alternatives" commands/illustrate.md` 命中。
- `/consistency illustrate.md`。

---

## 收尾步驟

1. **導航文檔 `/consistency` 閘門**：對 S1/S2 改過的 `illustrate-structure-viewport.md`、`illustrate.md` 跑 `/consistency`，🔴/🟡 修正後才算收尾。
2. 無 Capabilities / Kanban（元專案 docs mode）。
3. /audit-test：N/A（無測試）。
