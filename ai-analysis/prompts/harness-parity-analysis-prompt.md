# Mosaic_alpha 架構分析任務

> **給 LLM**：以下是一個架構分析任務。你的產出會被用於評估分析品質。依照指示產出報告，不需要討論這個任務本身。

## 任務背景

分析目標是 `/Users/ctai/Github/mosaic_alpha` — 一個基於 NautilusTrader 的台股量化交易系統。這是一個 production codebase，有完整的結構文檔。

## 你要做的事

對 mosaic_alpha 執行**架構分析**，產出 **3 份獨立報告**，每份報告聚焦一個任務。每份報告寫到 `/Users/ctai/Github/mosaic_alpha/ai-analysis/analysis/`，檔名**嚴格使用下方指定的 slug**（不可自取）。

### 報告 1：`{harness}-dependency-audit.md` — 依賴圖審計

**任務**：分析 mosaic_alpha 的模組依賴結構，找出架構問題。

**調查方法**（自己執行，不假設工具可用性）：
1. 讀 `dependency-graph.md`（repo root）取得既有依賴資料
2. 用 `rg "^from mosaic_alpha|^import mosaic_alpha"` 抽樣驗證關鍵依賴邊
3. 用 `rg "^from |^import "` 搭配 `fd -e py` 盤點模組邊界
4. 若有 LSP 工具可用，對可疑的循環依賴用 `findReferences` 驗證；無 LSP 則用 rg 推導（明確標註「未 LSP 驗證」）

**報告骨架**（固定小標題，內容自由）：
```
## 依賴圖審計

### 結構觀察
[整體分層是否符合 Clean Architecture（domain ← use case ← adapter ← infra）？依賴方向是否向內？]

### 🔴 反向耦合 / 循環依賴
[具體 file:line + 為什麼是問題。無則明說「未發現」]

### 🟡 Heavy → Lean 反向耦合
[heavy symbol（numpy/pandas/polars/nautilus）抽進 lean 廣用模組的情況。具體 file:line]

### 消費者數熱點
[被最多模組 import 的模組 top 5 + 為什麼是熱點（改動 ripple 風險）]

### 方法論限制
[這次調查用了哪些工具、哪些無法驗證。誠實標註，不掩蓋]
```

---

### 報告 2：`{harness}-bounded-context-review.md` — Bounded Context 邊界審查

**任務**：審查 mosaic_alpha 的 bounded context（DDD 邊界）是否清晰，有無跨域直接存取內部。

**調查方法**：
1. 讀 `mosaic_alpha/AGENTS.md` 的「模組觸發器」表 — 這是官方的 context 劃分
2. 讀 `architecture.md`（`mosaic_alpha/architecture.md`）理解設計意圖
3. 用 `rg "from mosaic_alpha\.[a-z_]+\.[_A-Z]"` 查跨 context 存取 private（`_` 開頭）的情況
4. 對每個發現的跨域存取，判斷是「合理共用」還是「邊界洩漏」

**報告骨架**：
```
## Bounded Context 邊界審查

### Context 劃分（從 AGENTS.md 歸納）
[列出識別到的 bounded context + 各自職責一句話]

### 結構觀察
[邊界是否清晰？有無 context 職責重疊？]

### 🔴 跨域存取內部（邊界洩漏）
[具體 file:line + 哪個 context 存取了哪個 context 的 _private。無則明說]

### 🟡 職責重疊 / 灰色地帶
[兩個 context 做了類似的事，或邊界模糊的地方]

### 共用 domain service 外溢風險
[被多 context 共用的 service（會計、定價、數據）有無被某 context 強迫改語意的跡象]

### 方法論限制
[同上，誠實標註]
```

---

### 報告 3：`{harness}-core-leaf-matrix.md` — Core/Leaf 審查優先序矩陣

**任務**：產出「審查優先序矩陣」— 哪些模組是 core（改動高風險，需 deep review），哪些是 leaf（可放過）。

**調查方法**：
1. 結合報告 1 的依賴資料 + 報告 2 的 context 劃分
2. 讀 `dependency-graph.md` 的 Hotspots + Ripple Impact Rules（若存在）
3. 對每個 top 消費者數模組，判斷是否在 domain critical path（bug 會 silent-corrupt 全下游）
4. quant 領域 overlay：除權息調整 / volume 張↔股 / 風控 sizing / 會計總量 — 這些 path 上的模組自動升 core

**報告骨架**：
```
## Core/Leaf 審查優先序矩陣

### 判定方法
[你怎麼判定的：資料來源 + 評分邏輯]

### Core 模組（deep human review）
| 模組 | 理由（消費者數 / critical path / ripple）| 建議審查深度 |

### Mid 模組（structure viewport + spot-read）
| 模組 | 理由 |

### Leaf 模組（behavior-only）
| 模組 | 理由 |

### 🔴 高風險組合
[「高消費者數 + 在 critical path + 無測試覆蓋」的模組 — 這些是技術債熱點]

### 方法論限制
[同上]
```

---

## 執行約束

1. **檔名**：`{harness}-dependency-audit.md` / `{harness}-bounded-context-review.md` / `{harness}-core-leaf-matrix.md`。**`{harness}` 替換為你當前所在的 harness 名稱**（ZCode 環境用 `zcode`，Claude Code 環境用 `claude`，全部小寫）。
2. **輸出位置**：`/Users/ctai/Github/mosaic_alpha/ai-analysis/analysis/`（**不是** `_done/` 子目錄）
3. **語言**：繁體中文 + 英文術語
4. **禁止假設工具可用性**：如果你沒有 LSP 工具，用 rg 推導並明確標註「未 LSP 驗證」。如果你有 LSP，用了就標「LSP 驗證」。**不要假裝用了沒用的工具**。
5. **禁止編造**：所有 file:line 必須來自實際讀取/搜尋的程式碼。不確定就標「未確認」，不要腦補。
6. **方法論限制段必填**：每份報告的「方法論限制」段不可省略 — 這段是這次分析的重要產出，不是附屬。
7. **每份報告獨立**：3 份報告可以互相引用結論（如報告 3 引用報告 1 的依賴資料），但每份必須獨立成檔、獨立可讀。

## 完成判定

3 份檔案都寫到指定位置 + 每份都含完整骨架（含方法論限制段）= 完成。完成後簡短回報：3 個檔名 + 每份一句話最關鍵 finding。
