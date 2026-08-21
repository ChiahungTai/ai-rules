---
harness-scope: neutral
paths:
  - "**/*.py"
---

# AI Agent 雙通道輸出慣例

> **scope**：跨專案通用日誌原則。Framework-specific 細節（log format、init 入口、suppress policy、framework quirk）在各專案文檔，本檔不重述，避免雙處真理論漂移。

---

## 核心原則

**print 當索引，Logger 當資料庫。** AI Agent 透過 print 理解執行結果，透過 rg 按需查詢 Logger 檔案取得詳細資訊。

**print = state transition, not computation trace。** 如果 output 不遵循此協議，視為 bug。

| 通道 | 消費者 | 職責 | 何時使用 |
|------|--------|------|----------|
| `print()` | AI Agent (stdout) | 精簡摘要 + rg 搜尋指引 | state transition：流程的最終結果或關鍵決策點 |
| Logger → file | AI Agent (rg 按需) | 可搜尋的詳細資訊 | 中間步驟、狀態變化、除錯資訊 |

決策規則：AI 需要此資訊決定下一步 → print；AI 日後可能需要查閱 → logger。

**單檔 vs 分檔**：預設單一 log 檔 + 三維分離（level / namespace / prefix），不分檔。同進程需交叉 timing 對齊 → 單檔；不同消費者且不需交叉 timing → 才分檔。

---

## Namespace 原則（Logger name 強制 module-path）

Logger name 是 log → 源碼的反查鍵，**必須是 module-path**（`Logger(__name__)` 最常見，自動帶；需 runtime-varying 識別用 `Logger(f"{__name__}({adapter})")` 保留 module-path + 動態段），不可 flat name（`Logger("MyService")`——無法反查）。框架 Strategy/Actor 基類自帶 namespace（如 `self.log`）→ 不自建。框架若不輸出檔名/行號，namespace 是**唯一**反查鍵。

---

## print() 慣例

格式：status tag + 精簡摘要——`print(f"[OK] build_features: {n} features, {n_rows} rows")`；需要深挖時附帶 rg 搜尋指引（`[LOG] rg 'train_model' {log_path}`，可用精準 pattern 避噪：`rg 'fit_model.*(start|metric|warn|error)'`）。

| Tag | 含義 |
|-----|------|
| `[OK]` | 成功完成（函式正常返回） |
| `[WARN]` | 異常但可繼續（數值偏低、資料不足） |
| `[FAIL]` | 失敗（拋出異常或無法完成） |
| `[LOG]` | rg 搜尋指引 |
| `[ACTION]` | UI 操作事件（由 ui 元件層 log，app 層不重複——元件擁有互動，元件 log；只有 app 直接操作 UI 框架時才由 app log） |
| `[progress]` | 週期性心跳（長任務定期進度，非 state transition） |

- **`[LOG]` 路徑只印一次**：同一 session 內 log 路徑不變，每次都印是浪費 token（class variable 追蹤已印過）
- **何時不該 print**：中間步驟細節（Loading column X / Processing row i/N）→ Logger；重複 Logger 已有摘要；超過一行內容（DataFrame/dict/list）

---

## Logger 慣例

- **統一 Prefix**：message 以 `action_name: ` 開頭（`logger.info(f"build_features: start, spec={spec_name}, rows={n_rows}")`）——散漫寫法（「開始處理...」「✅ 完成」）rg 無法精準搜
- **Level**：`debug` 中間計算/參數值（重現計算過程）、`info` 狀態轉換 start/done/cache hit（還原流程）、`warning` 異常可續行、`error` 失敗定位
- **閉環規則**：print 的 rg tag 必須在 Logger 中存在（`[OK] build_features` ↔ `build_features:` prefix 的 info 行）；Logger 提供補充細節，不重複 print 摘要

---

## stdlib `logging` 與框架 Logger 並存

stdlib logger 無 handler 時走 `lastResort`（INFO/DEBUG 靜默丟棄），框架 log 檔找不到其輸出。

- **同進程只用一套 Logger 系統**：框架有內建 Logger → 全用框架 Logger，禁混 stdlib `logging.getLogger`
- 必須用 stdlib（框架無 Logger）→ 顯式 `addHandler`，不依賴 lastResort
- **遷移非純機械替換**：`%s` lazy formatting 在部分框架 Logger 不展開 → 改 f-string；`extra=` kwargs 可能拋 TypeError → 欄位併入 message

---

## 執行自檢清單

- [ ] print 只用於 state transition，使用 `[OK]`/`[WARN]`/`[FAIL]`/`[LOG]`/`[ACTION]`/`[progress]` tag（`[progress]` 為心跳的明示例外；不用 `[INFO]`）
- [ ] `[LOG]` 路徑同 session 只印一次；`[ACTION]` 由 ui 元件層 log
- [ ] Logger message 以 `action_name: ` prefix 開頭；name 是 module-path（`Logger(__name__)`）
- [ ] print 的 rg tag 在 Logger 中存在（閉環）；Logger 不重複 print 摘要
- [ ] 同進程只用一套 Logger 系統（框架優先，禁 stdlib 無 handler）；依專案 init_logging 配置 file level ≥ DEBUG（供 rg 查），stdout 交 print 控制
