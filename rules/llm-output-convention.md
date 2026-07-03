---
paths:
  - "**/*.py"
---

# AI Agent 雙通道輸出慣例

> **scope**：跨專案通用日誌原則。Framework-specific 細節（log format、init 入口、suppress policy、framework quirk）在各專案文檔（如 quant 專案 `<package>/common/LOGGING.md`），本檔不重述，避免雙處真理論漂移。

---

## 核心原則

**print 當索引，Logger 當資料庫。** AI Agent 透過 print 理解執行結果，透過 rg 按需查詢 Logger 檔案取得詳細資訊。

> **搜尋規範**：語義查詢用 LSP，文字搜尋用 `rg`，檔案搜尋用 `fd`。詳見 `@~/Github/ai-rules/rules/lsp-navigation.md` 和 `@~/Github/ai-rules/rules/modern-cli-preference.md`

**print = state transition, not computation trace。**

如果 output 不遵循此協議，視為 bug。

---

## 單檔 vs 分檔

**預設：單一 log 檔 + 三維分離（level / namespace / prefix），不分檔。**

- 同進程、需交叉 timing 對齊 → 單檔
- 不同消費者且不需交叉 timing → 才分檔

三維分離即可在單檔內定位任何 log 行：

| 維度 | 控制什麼 |
|------|---------|
| level | 嚴重度門檻 + 噪音壓制 |
| namespace（Logger name） | 來源反查（log → 源碼） |
| prefix（`action_name: `） | 動作聚類（rg 精準搜） |

---

## Namespace 原則（Logger name 強制 module-path）

Logger name 是 log → 源碼的反查鍵，**必須是 module-path**（如 `Logger("<package>.data.fetchers.<module>")`），不可 flat name（`Logger("fetcher")`）。flat name 讓 AI debug 時無法從 log 定位原始碼。

```python
# ✅ module-path（rg 可從 log 行反查源碼）
_logger = Logger(__name__)                          # 最常見，自動帶 module-path

# ❌ flat name（無法反查）
_logger = Logger("MyService")
```

- **一律用 `Logger(__name__)`**（防 typo）。需要 runtime-varying 識別（adapter、instance）→ `Logger(f"{__name__}({adapter})")`，保留 module-path + 附加動態段
- 框架 Strategy/Actor 基類自帶 namespace（如 `self.log`）→ 不自建 Logger
- 框架若不輸出檔名/行號，namespace 是**唯一**反查鍵，flat name 等於斷掉 debug 路徑

---

## 通道職責

| 通道 | 消費者 | 職責 | 何時使用 |
|------|--------|------|----------|
| `print()` | AI Agent (stdout) | 精簡摘要 + rg 搜尋指引 | state transition：流程的最終結果或關鍵決策點 |
| Logger → file | AI Agent (rg 按需) | 可搜尋的詳細資訊 | 中間步驟、狀態變化、除錯資訊 |

---

## print() 慣例

### 格式規範

```python
# ✅ 正確：status tag + 精簡摘要
print(f"[OK] build_features: {n_features} features, {n_rows} rows")
print(f"[WARN] fit_model: validation_auc={auc:.3f} < threshold=0.6")
print(f"[FAIL] load_data: file not found: {path}")

# ✅ 正確：需要深挖時附帶 rg 搜尋指引
print(f"[OK] train_model: auc=0.72, trees=150")
print(f"[LOG] rg 'train_model' {log_path}")

# ✅ 正確：精準 pattern 避免 noise
print(f"[WARN] fit_model: validation_auc=0.55 < 0.6")
print(f"[LOG] rg 'fit_model.*(start|metric|warn|error)' {log_path}")
```

### Status Tag

| Tag | 含義 | 使用時機 |
|-----|------|----------|
| `[OK]` | 成功完成 | 函式正常返回結果 |
| `[WARN]` | 異常但可繼續 | 數值偏低、資料不足、非致命問題 |
| `[FAIL]` | 失敗 | 函式拋出異常或無法完成 |
| `[LOG]` | rg 搜尋指引 | 指引 AI 用 rg 查詢詳細 log |
| `[ACTION]` | UI 操作事件 | 使用者 UI 操作（選取、切換、調整），供 LLM 理解上下文。由 ui 元件層 log，不重複 |
| `[progress]` | 週期性心跳 | 長時間運作任務的定期進度回報（如回測每 N bars），非 state transition |

### [LOG] 路徑只印一次

`[LOG] rg 'pattern' {log_path}` 中的 log 路徑在同一 session 內不變，每次都印是浪費 token。

```python
# ✅ 正確：class variable 追蹤是否已印過
class UIActionLogger:
    _log_path_printed = False

    def log(self, action, summary, context=None):
        print(f"[ACTION] #{seq} {action}: {summary}")
        if self._log_path is not None and not UIActionLogger._log_path_printed:
            print(f"[LOG] rg 'ui_action.*seq={seq}' {self._log_path}")
            UIActionLogger._log_path_printed = True
```

### [ACTION] 分層原則

**ui 元件層 log，app 層不重複。** 如果互動來自 UI 元件層的元件，由元件 log；只有 app 直接操作 UI 框架時才由 app 層 log。

```python
# ✅ 正確：元件擁有互動，元件 log
class <Component>:
    def _handle_interaction(self, event):
        self._action_log.log("<component_action>", "<detail>")

# ❌ 錯誤：app 層重複 log 同一事件
class <App>:
    def _on_interaction(self, row):
        self._action_log.log("<component_action>", "<detail>")  # 重複

# ✅ 正確：app 直接操作 UI widget，由 app log
class <App>:
    def _on_app_action(self, event):
        self._action_log.log("<app_action>", "<detail>")
```

### 決策規則

若 AI 需要此資訊決定下一步 → print
若 AI 日後可能需要查閱 → logger

### 何時不該 print

```python
# ❌ 中間步驟細節 → Logger
print(f"Loading column {col_name}...")
print(f"Processing row {i}/{total}...")

# ❌ 重複 Logger 已有的摘要
print(f"Model loaded: {model_path}")

# ❌ 超過一行的內容（DataFrame、dict、list）
print(df.head())
```

---

## Logger 慣例

### 統一 Prefix

Logger name = 模組名（自動帶），message 以 `action_name: ` 開頭。

```python
# ✅ 正確：統一 prefix
logger.info(f"build_features: start, spec={spec_name}, rows={n_rows}")
logger.debug(f"build_features: col={col_name}, null_pct={null_pct:.2%}")
logger.info(f"build_features: done, features={result.shape[1]}")

# ❌ 散漫寫法（rg 無法精準搜尋）
logger.info("開始處理...")
logger.info(f"✅ 完成，共 {n} 個 features")
```

### Level 層級

| Level | 用途 | 還原能力 |
|-------|------|----------|
| `debug` | 中間計算、參數值 | 重現計算過程 |
| `info` | 狀態轉換（start/done/cache hit） | 還原執行流程 |
| `warning` | 異常但可繼續 | 非預期事件追蹤 |
| `error` | 失敗 | 錯誤定位 |
| `trace`（部分框架） | 逐筆資料流（預設關閉） | 原始資料留存 |

### 與 print 的互補（閉環規則）

print 的 rg tag 必須在 Logger 中存在，形成閉環：

```python
def build_features(df, spec_name):
    logger.info(f"build_features: start, spec={spec_name}, rows={len(df)}")
    logger.debug(f"build_features: col={col}, null_pct={pct:.2%}")
    logger.info(f"build_features: done, features={result.shape[1]}")

    print(f"[OK] build_features: {result.shape[1]} features, {result.shape[0]} rows")
    print(f"[LOG] rg 'build_features' {log_path}")
```

Logger 提供補充細節（print 沒說的），不重複 print 的摘要。

---

## stdlib `logging` 與框架 Logger 並存

stdlib `logging` 與框架內建 Logger 是兩套不相連系統；stdlib logger 無 handler 時走 `lastResort`（INFO/DEBUG 靜默丟棄），框架 log 檔找不到其輸出。

- **同進程只用一套 Logger 系統**：框架有內建 Logger → 全用框架 Logger，不要混 stdlib `logging.getLogger`
- 若必須用 stdlib（框架無 Logger）→ 顯式配 handler（`addHandler`），不要依賴 lastResort
- **遷移 stdlib → 框架 Logger 非純機械替換**，注意 API 差異：
  - `%s` lazy formatting 在部分框架 Logger 不展開 → 改 f-string
  - `extra=` kwargs 在部分框架 Logger 拋 TypeError → 移除，欄位併入 message

---

## 執行自檢清單

- [ ] print 只用於 state transition，不用於中間步驟
- [ ] print 使用 `[OK]`/`[WARN]`/`[FAIL]`/`[LOG]`/`[ACTION]` status tag（不使用 `[INFO]`）
- [ ] `[LOG]` 路徑同一 session 只印一次（避免重複浪費 token）
- [ ] `[ACTION]` 由 ui 元件層 log，app 層不重複
- [ ] 需要深挖時，print 附帶 `[LOG] rg 'pattern' {log_path}`
- [ ] Logger message 以 `action_name: ` 統一 prefix 開頭
- [ ] Logger name 是 module-path（`Logger(__name__)`），非 flat name
- [ ] Logger 不重複 print 的摘要，提供補充細節
- [ ] print 的 rg tag 必須在 Logger 中存在（閉環）
- [ ] 依專案 init_logging 配置 file level ≥ DEBUG（供 rg 查），stdout 交 print 控制（細節見各專案文檔）
- [ ] 同進程只用一套 Logger 系統（框架 Logger 優先，禁混 stdlib `logging.getLogger` 無 handler）
