---
harness-scope: neutral
---

# 品質約束

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 完整交付標準

> **核心原則**：方向明確時必須完整執行到可用狀態，絕不交付半成品。

- ✅ 必須完成：核心功能完整實現、相關測試全部通過、邊界情況妥善處理、文檔同步更新、對應目錄的 instruction 檔（AGENTS.md source；Claude 端 CLAUDE.md wrapper）同步更新
- **instruction 檔同步檢查**：實作完成後，識別變更檔案範圍 → 檢查所在目錄及上層目錄的 AGENTS.md → 判斷變更是否影響其描述的架構、API、模組職責
- ❓ 停下請示：技術方案有多種可行路徑、需求不明確、發現風險需用戶決策、資源限制需調整優先級

---

## 數據完整性優先（Crash-Only Design）

> **核心原則**：損壞數據比沒有數據更災難，無效輸入必須立即崩潰。

- **崩潰哲學**：崩潰是停止系統的唯一方法、從崩潰狀態恢復是啟動的唯一方法（恢復邏輯即初始化邏輯，單一代碼路徑）、系統設計為崩潰後快速重啟
- **數據完整性**：算術溢出立即崩潰而非靜默傳播、類型轉換失敗拒絕處理、格式解析錯誤崩潰而非嘗試修復損壞輸入
- **架構**：關鍵狀態外部化（DB/隊列）、操作等冪（重啟可安全重試）、服務層無狀態
- **適用**：量化交易、高頻、實時風控、批次處理。**不適用**：長時間用戶會話、複雜 UI 狀態、UX 優先的互動應用

- **推薦做法**：嚴格驗證，失敗即崩潰——`assert not data.empty`、必要欄位存在、`notna().all()`、`not np.isinf(result).any()`；禁 try/except 吞錯續行。

### 誤用警告：crash-only 不是「graceful 不修」的藉口

> **核心原則**：crash-only 是 defense-in-depth 的**後備保證**（graceful shutdown 意外失敗時系統仍正確），**不是**「graceful 可預期地壞掉也不修」的合理化——整合 bug、配置錯誤、合約違反是可修 bug，該修，不可用 crash-only 跳過。披著「設計哲學」外衣的跳過比一般 bug 更危險，code review 難抓。

**實例**：mosaic ReplayHost SIGTERM 在 daemon-thread 下 graceful shutdown 失敗（NT loop signal handler 衝突），曾錯誤主張「crash-only 接受不 work」跳過可修 bug——正解是 TDD red（xfail strict 釘住 graceful 目標，見 test-driven-development skill）+ 另開 EP 修復。

---

## 主動揭露錯誤（Fail Loud）

> **核心原則**：無法確認成功時，必須明確說明，絕不回報「完成」。

- **跳過就是失敗**：跳過了任何步驟、測試、驗證 → 不得回報「完成」
- **不確定性必須可見**：無法驗證結果時，明確標注未驗證項目；寧可多報問題，不默默跳過
- 禁止：測試跳過部分案例卻說「測試通過」；migration 靜默跳過記錄卻說「完成」；沒驗邊界卻說「功能完成」；**用隔離單元測試通過就宣稱功能完成**

### 消費端驗證模式

功能是給特定消費端用的，單元測試通過不等於功能可用。必須在**實際消費端上下文**中驗證——問「功能的主要消費者是誰？在那個消費者的完整流程中跑一次」。

| 功能類型 | 消費端 | 驗證方式 |
|---------|--------|---------|
| scoring / ranking 函數 | watchlist pipeline | 用 pipeline 真實資料跑一次完整流程 |
| 新 Feature | 使用該 Feature 的下游 pipeline | 跑整個 `tests/unit_tests/features/`（跨模組交互） |
| 除權息調整邏輯 | catalog + indicators | 真實除權息股票做日/週/月 K 驗證 |
| DB schema 變更 | 整個 data pipeline | 從 fetch → transform → write → read 全跑一次 |
| Pipeline Step | 上層 Pipeline | 在 Pipeline 完整流程中跑，不只測單一 Step |

**跨模組影響擴散**：修改共用模組（如 `_validate_output`、`column_metadata`）時，影響跨測試檔案（parity / interaction / consistency test）——必須跑整個受影響目錄而非單一檔案。

### 符號覆蓋 vs 整合路徑覆蓋

理論基礎見 [acceptance-evidence](./acceptance-evidence.md) 證據階層 L3。**符號覆蓋**（symbol 出現在 tests）≠ **整合路徑覆蓋**（新參數 / 新接線 / 多組件組合被實際驅動）：

- **新 public 參數 / 注入點**：既有符號 + 新參數組合必須被測試。例：把 guard 注入既有 Strategy 的 `submit_order()` 點 — Strategy 有多個 `on_bar()` 測試但全是 `guard=None` 回測路徑，新注入路徑零測試。機械檢查：`rg "<param>=" tests/` → 0 hits = 路徑未覆蓋。
- **新增 registry 成員**：auto-discovery 接線必須被斷言。per-class 單元測試只證明邏輯正確，不證明接上 registry。機械檢查：在 test files 搜尋 `list_*_classes()` membership 斷言。

### 整合器型變更判定

整合器型變更判定（三條件）、mock 循環論證陷阱與兩層整合測試（接線 guard＋真實邊界，缺任一即缺口）見 validation-strategy skill「整合器型變更判定」章。

---

## 多步驟任務檢查點

> **核心原則**：完成每個重要步驟後回報狀態，無法描述當前狀態時必須停下。

- **每步回報**：完成重要步驟後，主動回報「已完成、已驗證、剩餘事項」
- **迷失就停**：無法精確描述當前進度時，停止並重新釐清；不確定前面步驟是否正確時，禁止盲目續行
- 適用：跨多檔重構、多段落實作（Claude: `/implement`）、3 步以上修改

---

## 功能驗證標準

- **可執行範例**：每個功能必須有可實際執行的使用範例；API 設計必須通過實際呼叫驗證可用性
- **邊界測試**：必須驗證邊界情況的處理
