---
paths:
  - "**/*.py"
---

# AI Agent 雙通道輸出慣例

---

## 核心原則

**print 當索引，Logger 當資料庫。** AI Agent 透過 print 理解執行結果，透過 rg 按需查詢 Logger 檔案取得詳細資訊。

> **搜尋規範**：語義查詢用 LSP，文字搜尋用 `rg`，檔案搜尋用 `fd`。詳見 `@~/.claude/rules/lsp-navigation.md` 和 `@~/.claude/rules/modern-cli-preference.md`

**print = state transition, not computation trace。**

如果 output 不遵循此協議，視為 bug。

---

## NT Logger 實際格式

```
2026-05-06T14:41:34.259492000Z [INFO] TRADER-000.FeatureEngine: message_here
│                           │       │              │
│                           │       │              └─ message（我們控制）
│                           │       └─ Logger name（自動帶，=模組名）
│                           └─ level
└─ ISO 8601 timestamp (nanosecond)
```

NT Logger **不輸出檔名/行號**，不支援自訂 formatter。Logger name 已提供模組資訊，message 只需加 action prefix。

---

## 通道職責

| 通道 | 消費者 | 職責 | 何時使用 |
|------|--------|------|----------|
| `print()` | AI Agent (stdout) | 精簡摘要 + rg 搜尋指引 | state transition：流程的最終結果或關鍵決策點 |
| NT Logger → file | AI Agent (rg 按需) | 可搜尋的詳細資訊 | 中間步驟、狀態變化、除錯資訊 |

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

**ui 元件層 log，app 層不重複。** 如果互動來自 `mosaic_alpha/ui` 的元件（Tabulator、Panel），由元件 log；只有 app 直接操作 Bokeh/Panel 時才由 app 層 log。

```python
# ✅ 正確：元件擁有互動，元件 log
class SwingTriagePanel:
    def _handle_selection(self, event):
        self._action_log.log("select_swing", f"{swing_id}")

# ❌ 錯誤：app 層重複 log 同一事件
class TrajectoryViewerApp:
    def _on_swing_selected(self, row):
        self._action_log.log("select_swing", f"{row['swing_id']}")  # 重複

# ✅ 正確：app 直接操作 Panel widget，由 app log
class TrajectoryViewerApp:
    def _on_instrument_change(self, event):
        self._action_log.log("switch_instrument", f"->{new_code}")
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

## NT Logger 慣例

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

### Level 層級定義

| Level | 用途 | 還原能力 |
|-------|------|----------|
| `info` | 狀態轉換（start/done/cache hit） | 還原執行流程 |
| `debug` | 中間計算、參數值 | 重現計算過程 |
| `trace` | 逐筆資料流（預設關閉） | 原始資料留存 |
| `warning` | 異常但可繼續 | 非預期事件追蹤 |
| `error` | 失敗 | 錯誤定位 |

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

## init_logging 配置

```python
from mosaic_alpha.common.logging import init_logging_with_defaults

log_config = init_logging_with_defaults()
# 內部自動處理：
#   - stdout=OFF, file=DEBUG
#   - file_name 從 sys.argv[0] 自動偵測
#   - directory 從 MOSAIC_LOG_PATH 環境變數讀取
#   - max_file_size=0（不 rotation，檔名可預測）
#   - RuntimeError（重複初始化）自動處理
# 自動印出：[LOG] {log_path} (init at {ts})
```

路徑解析優先順序：`directory 參數` > `MOSAIC_LOG_PATH 環境變數` > `/tmp/mosaic_logs/`

---

## 執行自檢清單

- [ ] print 只用於 state transition，不用於中間步驟
- [ ] print 使用 `[OK]`/`[WARN]`/`[FAIL]`/`[LOG]`/`[ACTION]` status tag（不使用 `[INFO]`）
- [ ] `[LOG]` 路徑同一 session 只印一次（避免重複浪費 token）
- [ ] `[ACTION]` 由 ui 元件層 log，app 層不重複
- [ ] 需要深挖時，print 附帶 `[LOG] rg 'pattern' {log_path}`
- [ ] Logger message 以 `action_name: ` 統一 prefix 開頭
- [ ] Logger 不重複 print 的摘要，提供補充細節
- [ ] print 的 rg tag 必須在 Logger 中存在（閉環）
- [ ] init_logging 設定 `level_stdout=OFF`, `level_file=DEBUG`
