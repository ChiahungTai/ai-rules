---
harness-scope: neutral
---

# 品質約束

## 完整交付標準

方向明確就做到可用：核心功能、相關測試、邊界處理、文檔同步；完成後檢查變更所在與上層 AGENTS.md 的架構/API/職責描述，必要時同步（含 Claude wrapper）。需方案選擇、需求不明或風險裁決時請示。

## 數據完整性優先（Crash-Only Design）

損壞數據比缺失更危險。無效輸入、溢出、轉型/解析失敗立即崩潰，禁吞錯續行或修補損壞輸入；驗非空、必要欄位、NaN、inf。

- 狀態外部化（DB/隊列），操作等冪、服務無狀態；停止即崩潰、恢復即初始化。
- 適用量化交易、高頻、實時風控、批次；不適用長會話、複雜 UI 狀態、UX 優先互動。
- 持久化輸出/備份禁 `tempfile.TemporaryDirectory`（scope 結束即毀），須放專案外持久路徑。

### 誤用警告：crash-only 不是「graceful 不修」的藉口

crash-only 只保證意外失敗後可恢復，不豁免可預期的整合 bug、配置或合約錯誤。真實案例：ReplayHost SIGTERM 失敗曾被以 crash-only 跳過；正解是 TDD red（xfail strict）釘 graceful 目標再修。

## 主動揭露錯誤（Fail Loud）

未確認成功、跳過步驟/案例/驗證、migration 跳記錄、未驗邊界都須明列限制，禁報完成/全通過；隔離單元綠燈不代表功能完成。功能須有可執行例，API 實際呼叫，邊界實驗。

### 消費端驗證模式

先定位主要消費者並跑完整流程（scoring/ranking 用 watchlist 真資料；除權息用真股票日/週/月 K；DB 改動跑 fetch→transform→write→read）。共用模組驗整個影響面；**測試集須機械反查，不憑目錄直覺**：code-reality `impact_radius`/`scip_refs --callers` 或 `rg "<符號>" tests/ -l`。

symbol 命中不等於新參數/接線/組合被驅動；整合器型變更的 public 注入、registry membership、接線 guard＋真實邊界兩層測試細則見 **validation-strategy skill**（證據分層見 [acceptance-evidence](acceptance-evidence.md)）。

## 漸進式驗證（DEPTH-MIN→SAMPLE→FULL）

一律 DEPTH-MIN→SAMPLE→FULL；失敗先分析/修正並回 MIN，禁改後直跑 FULL 或失敗盲重跑。風險分級決定最終深度；3–5 案、已知陷阱等細則見 validation-strategy skill。

## 多步驟任務檢查點

跨檔重構、多段或三步以上修改，每個重要步驟回報完成/驗證/剩餘；無法精確描述或不確定前步正確時停下釐清，禁盲續。
