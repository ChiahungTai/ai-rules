# 品質約束

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 完整交付標準

> **核心原則**：方向明確時必須完整執行到可用狀態，絕不交付半成品。

### 執行哲學

**🎯 確定性優先**：當技術方向明確、需求清晰時，應完整地做到品質標準

### ✅ 必須完成

- 核心功能完整實現
- 相關測試全部通過
- 邊界情況妥善處理
- 文檔同步更新
- 對應目錄的 CLAUDE.md 同步更新
- 達到可用狀態

### CLAUDE.md 同步檢查

實作完成後，檢查修改檔案所在目錄及其上層目錄是否有 CLAUDE.md 需要更新：

1. **識別變更範圍**：哪些檔案被修改/新增/刪除
2. **檢查對應 CLAUDE.md**：變更檔案所在目錄及上層目錄的 CLAUDE.md
3. **判斷是否需要更新**：變更是否影響 CLAUDE.md 中描述的架構、API、模組職責等

### ❓ 停下請示的時機

- 技術方案不確定，有多種可行路徑
- 需求不明確或有歧義需要澄清
- 發現潛在風險需要用戶決策
- 資源限制或優先級需要調整

---

## 數據完整性優先（Crash-Only Design）

> **核心原則**：損壞數據比沒有數據更災難，無效輸入必須立即崩潰。

### Crash-Only Design 核心理念

**崩潰哲學**：
- **唯一停止方式**：崩潰是停止系統的唯一方法
- **唯一啟動方式**：從崩潰狀態恢復是啟動的唯一方法
- **單一代碼路徑**：恢復邏輯即是初始化邏輯
- **快速重啟**：系統設計為崩潰後能快速重啟

### 數據完整性原則

- **損壞數據 > 沒有數據**：錯誤的數據比缺失數據更災難
- **算術溢出檢查**：立即崩潰而非靜默錯誤傳播
- **類型轉換失敗**：拒絕處理無效數據
- **格式解析錯誤**：崩潰而非嘗試修復損壞輸入

### 推薦做法：Crash-only design - 立即崩潰

```python
def process_trading_data(data):
    # 嚴格驗證，失敗即崩潰
    assert not data.empty, "Input data cannot be empty"
    assert all(col in data.columns for col in ['price', 'volume']), "Missing required columns"
    assert data['price'].notna().all(), "Price data contains NaN values"

    # 算術溢出檢查
    result = calculate_position_size(data['price'], data['volume'])
    assert not np.isinf(result).any(), "Calculation resulted in infinite values"

    return result
```

### 系統架構設計

- **外部化狀態**：關鍵狀態保存在外部（資料庫、消息隊列）
- **等冪操作**：重啟後可安全重試所有操作
- **狀態恢復**：啟動時從持久化存儲恢復完整狀態
- **無狀態服務**：服務層保持無狀態，便於快速重啟

### 適用場景

**適合 Crash-Only 的場景**：
- 量化交易系統（數據完整性至關重要）
- 高頻率交易（延遲比複雜恢復更重要）
- 實時風控系統（快速失敗防止風險擴散）
- 批次處理任務（重啟比繼續更簡單）

**不適用的場景**：
- 長時間運行的用戶會話
- 複雜的 UI 狀態管理
- 需要保持連接的網路服務
- 用戶體驗優先的交互式應用

---

## 主動揭露錯誤（Fail Loud）

> **核心原則**：無法確認成功時，必須明確說明，絕不回報「完成」。

### 強制規則

- **跳過就是失敗**：跳過了任何步驟、測試、驗證 → 不得回報「完成」
- **不確定性必須可見**：無法驗證結果時，明確標注未驗證項目
- **預設揭露而非隱藏**：寧可多報問題，也不要默默跳過

### 禁止行為

- 測試跳過了部分案例卻說「測試通過」
- Migration 靜默跳過了 30 筆記錄卻說「遷移完成」
- 功能沒驗證邊界案例卻說「功能完成」
- 用隔離的單元測試通過就宣稱「功能完成」— 功能是給特定消費端用的，必須在該消費端上下文中驗證

### 消費端驗證模式

功能是給特定消費端用的，單元測試通過不等於功能可用。必須在**實際消費端上下文**中驗證。

**判斷方式**：功能的主要消費者是誰？在那個消費者的完整流程中跑一次。

| 功能類型 | 消費端 | 驗證方式 |
|---------|--------|---------|
| scoring / ranking 函數 | watchlist pipeline | 用 pipeline 真實資料跑一次完整流程 |
| 新 Feature | 使用該 Feature 的下游 pipeline | 跑整個 `tests/unit_tests/features/`（跨模組交互） |
| 除權息調整邏輯 | catalog + indicators | 真實除權息股票做日/週/月 K 驗證 |
| DB schema 變更 | 整個 data pipeline | 從 fetch → transform → write → read 全跑一次 |
| Pipeline Step | 上層 Pipeline | 在 Pipeline 完整流程中跑，不只測單一 Step |

**跨模組影響擴散**：修改共用模組（如 `_validate_output`、`fill_null`、`column_metadata`）時，影響會跨測試檔案（parity test、interaction test、consistency test）。必須跑整個受影響目錄而非單一檔案。例如：修改 `features/column_metadata.py` 的預設值，可能同時影響 parity test（欄位比對）、interaction test（Feature 組合）、consistency test（跨 Interval 一致性），三者分在不同測試檔案中。

### 符號覆蓋 vs 整合路徑覆蓋

理論基礎見 [acceptance-evidence](./acceptance-evidence.md) 證據階層 L3。消費端驗證模式的盲點：**符號覆蓋**（symbol 出現在 tests）≠ **整合路徑覆蓋**（新參數 / 新接線 / 多組件組合被實際驅動）。

- **新 public 參數 / 注入點**：既有符號 + 新參數組合必須被測試。例：把 `<GuardComponent>` 注入既有 `<Strategy>` 的 `<N>` 個 `<submit_order>()` 點 — `<Strategy>` 有 `<M>` 個 `<on_bar>()` 測試，但全是 `<guard>=None` 的回測路徑，新注入路徑零測試。機械檢查：`rg "<param>=" tests/` → 0 hits = 路徑未覆蓋。
- **新增 registry 成員**：auto-discovery 接線必須被斷言。per-class 單元測試只證明邏輯正確，不證明接上 registry。機械檢查：在 test files 搜尋 `list_*_classes()` membership 斷言。

### 整合器型變更判定

整合器型變更的完成定義必須含**真實邊界整合測試**（L3+），不能只靠 mock。EP 段落同時滿足以下 → 整合器型：

- 主要價值是把 ≥2 個真實外部組件接起來（DB、catalog、第三方 SDK、跨進程、跨框架）
- 邊界正確性無法從任一單方文件推導（必須實際接起來跑）
- 錯了不是「調參數」而是「整天行為全錯」（時區偏移整天、序列化整批毀損）

**mock 循環論證陷阱**：當 EP 主要價值是「把外部組件接對」，mock 測試的假設本身可能是 bug 來源 — mock 驗證「假設成立的話行為正確」，無法驗證「假設本身是否成立」。例：catalog 存 naive Taiwan-local 時間，`tz_localize("UTC")` 只貼標不轉換，mock 假設「catalog 回傳正確 UTC」就是 bug 來源，mock unit test 結構上抓不到 +8h 時區偏移。

### 兩層整合測試

整合器型變更兩層都要，缺任一即缺口：

| 測試類型 | 性質 | 目錄 | marker |
|--|--|--|--|
| 接線 guard | 純邏輯、無 IO（registry lookup、membership 斷言） | `tests/unit_tests/` | `quick` |
| 真實邊界 | 真實 DB / Catalog / 資料，跑完整消費端 pipeline | `tests/integration_tests/` | `integration` |

**不可互代**：接線 guard 廉價（毫秒）擋高頻接線 regression；真實邊界昂貴（秒級以上）擋跨層 schema / 展開失敗。命名含 `_integration` 但純邏輯仍留 unit_tests（依依賴判斷，不看名稱）。

---

## 多步驟任務檢查點

> **核心原則**：完成每個重要步驟後回報狀態，無法描述當前狀態時必須停下。

### 強制規則

- **每步回報**：完成重要步驟後，主動回報「已完成、已驗證、剩餘事項」
- **迷失就停**：無法精確描述當前進度時，停止並重新釐清狀態
- **禁止盲目續行**：不確定前面步驟是否正確時，不繼續後續步驟

### 適用場景

- 跨多個檔案的重構
- 多段落實作（`/build` 以外的長任務）
- 任何需要 3 個以上步驟的修改

---

## 功能驗證標準

> **核心原則**：功能開發和 API 設計必須提供可執行範例驗證功能。

- **可執行範例**：每個功能必須有可實際執行的使用範例
- **API 驗證**：API 設計必須通過實際呼叫驗證可用性
- **邊界測試**：必須驗證邊界情況的處理
