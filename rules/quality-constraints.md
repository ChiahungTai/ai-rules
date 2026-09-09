---
harness-scope: neutral
---

# 品質約束

## 完整交付標準

方向明確就做到可用：完整核心功能、相關測試、邊界處理與文檔同步。完成後檢查變更所在及上層 AGENTS.md 的架構/API/模組職責描述，必要時同步（含 Claude 端 CLAUDE.md wrapper）。方案需選擇、需求不明、風險需裁決或資源需調整優先級時請示。

## 數據完整性優先（Crash-Only Design）

損壞數據比缺失更危險。無效輸入、溢出、轉型/解析失敗立即崩潰，禁吞錯續行或修補損壞輸入。檢查非空、必要欄位、NaN、inf。

- 狀態外部化（DB/隊列），操作等冪、服務無狀態；停止即崩潰、恢復即初始化，單一路徑支援快速重啟。
- 適用量化交易、高頻、實時風控、批次；不適用長會話、複雜 UI 狀態、UX 優先互動。
- 持久化輸出/備份禁用 `tempfile.TemporaryDirectory`（scope 結束即毀），須放專案外持久路徑。

### 誤用警告：crash-only 不是「graceful 不修」的藉口

Crash-only 是 graceful 意外失敗的後備保證，不豁免可預期的整合 bug、配置錯誤或合約違反。真實案例：ReplayHost SIGTERM 失敗曾被以 crash-only 跳過；正解是 TDD red（xfail strict）釘住 graceful 目標，另開 EP 修復（test-driven-development skill）。

## 主動揭露錯誤（Fail Loud）

未確認成功、跳過步驟/案例/驗證、migration 跳記錄、未驗邊界，都須明列限制，不得報完成或全通過；隔離單元綠燈不代表功能完成。

### 消費端驗證模式

先定位主要消費者，在它的完整流程實跑：scoring/ranking 用 watchlist 真資料；Feature 驅動下游 pipeline 並驗受影響 features 測試；除權息用真股票日/週/月 K；DB 改動跑 fetch→transform→write→read；Step 放回上層 Pipeline。

共用模組變更須驗整個受影響目錄，涵蓋跨檔 parity/interaction/consistency。**測試集必須機械反查，不憑目錄直覺**：用 code-reality `impact_radius` / `scip_refs --callers`，或 `rg "<符號>" tests/ -l`。

### 符號覆蓋 vs 整合路徑覆蓋

symbol 出現在測試不代表新參數/接線/組合被驅動（證據分層見 [acceptance-evidence](acceptance-evidence.md)）。

- 新 public 參數/注入點必測既有符號＋新參數組合；全部 `guard=None` 不涵蓋 guard 注入。用 `rg "<param>=" tests/` 查接線，無命中須補查/補測。
- registry 新成員須斷言 auto-discovery membership（如 `list_*_classes()`）；per-class 測試不證明已註冊。
- 整合器型變更須載入 validation-strategy skill：三條件判定、mock 循環論證、接線 guard＋真實邊界兩層整合測試，缺一即缺口。

## 漸進式驗證（DEPTH-MIN→SAMPLE→FULL）

每次修改先 MIN；邏輯穩定再 SAMPLE；兩者過才 FULL。MIN 選 3–5 個多分支案例，至少一個已知易錯案例。任一失敗先分析、修正、重回 MIN；禁修改後直跑全量或 FULL 失敗盲重跑，避免基本錯誤拖到全量末端才被發現。

風險分級定驗到多深（guide「驗證約束」），漸進順序定如何抵達；高風險需 FULL，仍從 MIN 起。

## 多步驟任務檢查點

跨檔重構、多段實作或三步以上修改，每個重要步驟回報已完成/已驗證/剩餘事項；無法精確描述進度或不確定前步正確時停下釐清，禁盲續。

## 功能驗證標準

每個功能須有可執行範例；API 必須實際呼叫，邊界處理必須驗證。
