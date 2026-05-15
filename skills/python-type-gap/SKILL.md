---
name: python-type-gap
description: Handles third-party package type annotation gaps using a four-layer strategy: isinstance narrowing, project stubs, precise type ignore, pyproject.toml override. Use when mypy reports errors from third-party code, when writing stubs, when reviewing # type: ignore usage, or when cleaning up pyproject.toml mypy overrides.
---

# Python Type Gap — 第三方套件型別缺口的四層處理策略

當第三方套件的 type annotations 不完整時，按以下順序嘗試：

## Layer 1：Type Narrowing（最推薦）

適用：union type 導致的方法解析衝突。

```python
# ❌ 錯誤：# type: ignore 處理 union type
df = catalog.get_bars(...)  # returns pd.DataFrame | pl.DataFrame
if df is None or df.is_empty():  # type: ignore[operator]
    return []
df_pd = df.to_pandas()  # type: ignore[operator]

# ✅ 正確：isinstance type narrowing
import polars as pl

df = catalog.get_bars(...)
if not isinstance(df, pl.DataFrame) or df.is_empty():
    return []
df_pd = df.to_pandas()  # mypy 知道 df 是 pl.DataFrame
```

原理：mypy 在 union type 上找不到一致的方法簽名時會報錯。`isinstance` 讓 mypy 收窄為單一型別，方法解析不再衝突。附帶好處：runtime 真的會驗證型別。

## Layer 2：Project Stubs（推薦）

適用：套件無 type support、inline annotations 缺口多、或有 `py.typed` 但特定子模組缺 stubs。

**前置檢查**：先用 `fd 'py.typed' .venv/.../package/` 確認套件是否已有型別支援（替換 `.../package/` 為實際套件路徑如 `.venv/lib/python3.12/site-packages/polars/`）。

```
stubs/
├── nautilus_trader/    # NT 有 py.typed 但部分子模組缺口多 → stubs 補缺口
├── shioaji/            # 完全沒有 type support → stubs 是唯一型別來源
└── pyarrow/            # 有 py.typed + __getattr__ → Any，但 compute 子模組缺 stubs → partial stubs 只補 compute.pyi
    ├── __init__.pyi    # 只有 __getattr__ → Any，確保 top-level 透傳不覆蓋
    └── compute.pyi     # 只補用到的 8 個函式（year, sum, is_null, ...）
```

判斷標準：
- **無 `py.typed`** → stubs 有效（如 shioaji）
- **有 `py.typed` 但缺口多** → partial stubs 有效（如 nautilus_trader）
- **有 `py.typed` + `__getattr__ → Any`，但特定子模組缺 stubs** → partial stubs 只補缺口子模組，`__init__.pyi` 用 `__getattr__ → Any` 透傳（如 pyarrow）
- **有 `py.typed` 且大部分可用，缺口的子模組也能用 `# type: ignore` 解決** → 看缺口數量決定，3+ 處用 stubs，1-2 處用 `# type: ignore[code]`

### 何時不該寫 Partial Stubs（直接走 Layer 4）

以下情境寫 stubs 的成本遠高於收益，`ignore_errors = true` 是務實選擇：

- 套件使用深度繼承鏈（3+ 層，如 Markdown → HTML → Panel）
- 缺口分散在數十個不同 class 的 `__init__` 參數
- stubs 需覆蓋的 class 數量 > 20
- 每個 class 只需修 1-2 個 type-arg → 成本/收益比太差

### Partial Stubs 關鍵約束

- **`__init__.pyi` 必須有 `__getattr__ → Any`**：確保 top-level 屬性（如 `pa.schema`、`pa.Table`）透傳到已安裝套件的型別資訊。如果沒有它，mypy 會用 stubs 的 `__init__.pyi` 完全取代 site-packages 的型別資訊，導致已正確標註的型別全部變成 Any
- **只補缺口的子模組**：不需要為整個套件寫完整 stubs
- **只 stub 用到的函式**：先 `rg 'pc\.\w+' mosaic_alpha/ -t py --no-filename -o > /tmp/usage.txt`，再用 `sort -u /tmp/usage.txt` 找出實際用量

## Layer 3：精確的 `# type: ignore`

適用：Layer 1-2 都不適用，且是單一呼叫點的第三方 gap。

```python
# ✅ 精確到具體 error code + 第三方 gap
pq.write_table(  # type: ignore[no-untyped-call]
    table, where=str(path), compression="snappy",
)
```

約束：
- 必須指定 error code（`[no-untyped-call]`、`[operator]`），不用裸 `# type: ignore`
- 只用於第三方套件的 gap，不用於我們自己程式碼的型別問題
- 如果同一模組出現 3+ 個 `# type: ignore`，考慮 Layer 4

### `no-any-return` 的替代技巧

當 `wrangler.process()` 等第三方函式回傳 `Any`，觸發 `no-any-return` 時，用 explicit variable annotation。**前提**：函式回傳型別必須接受 `list[Any]`（mypy 認為 `list[Any]` 與 `list[T]` 相容）；若回傳型別是嚴格的 `list[Bar]` 且 mypy 報 `incompatible return`，仍需 `# type: ignore[no-any-return]`。

```python
# ❌ 直接收會觸發 no-any-return
return wrangler.process(df_pd)  # type: ignore[no-any-return]

# ✅ 先賦值給 typed variable
bars: list[Any] = wrangler.process(df_pd)
return bars
```

## Layer 4：pyproject.toml Override（最後手段）

適用：整個子模組的 type gap 無法用上述方法解決。

```toml
# UI framework 的 runtime metaprogramming 本質不可靜態型別化
[[tool.mypy.overrides]]
module = "mosaic_alpha.ui.*"
strict = false
allow_untyped_defs = true
allow_untyped_calls = true
ignore_errors = true
```

約束：
- 必須加註解說明為什麼需要（不能只寫「ignore」）
- 定期 re-evaluate 是否仍需要
- 不用於可以被 Layer 1-3 解決的問題

### 不推薦：全域寬鬆設定

```toml
# ❌ 過度抑制 — polars 1.x 已有完整 py.typed
[[tool.mypy.overrides]]
module = "polars.*"
ignore_errors = true
```

## pyproject.toml MyPy Overrides 清理

定期檢查 `[tool.mypy.overrides]` 是否仍必要。

### 檢查流程

1. **識別冗餘 strict=true**：如果 global 已設 `strict = true`，override 再設一次是冗餘
2. **識別不存在的模組**：override 引用的模組目錄可能已刪除或從未建立
3. **逐項移除測試**：暫時移除 override → 跑 `uv run mypy mosaic_alpha/` → 看是否仍需要
4. **驗證全專案**：`uv run mypy mosaic_alpha/ --strict` 確認所有模組都能通過

### 常見可移除項目

| 類型 | 判斷方式 | 處理 |
|------|---------|------|
| 冗餘 `strict = true` | global 已有 | 直接刪除整個 override |
| 不存在的模組 | `fd -t d -d 1 . mosaic_alpha/` 確認 | 直接刪除整個 override |
| 第三方 blanket ignore | 套件已有 `py.typed` | 移除，改用 Layer 1-3 |
| UI framework ignore | Panel/Bokeh 的 runtime metaprogramming | 保留，加註解 |

## disable_error_code 縮窄食譜

當 `ignore_errors = true` 被替換為 `disable_error_code = [...]` 後，每個 error code 都應驗證是否為「不可修復的第三方缺口」。以下食譜記錄各 error code 的分類和修復方式。

### 可修復的 Error Codes（不應全局壓制）

| Error Code | 修復方式 | 範例 |
|-----------|---------|------|
| `str-bytes-safe` | `float()` / `str()` 包裹 polars 回傳值後再用 f-string | `f"{float(df['close'].mean()):.2f}"` |
| `assignment` | 型別加寬（`dict[str, object]`）、isinstance narrowing、中間變數重新命名 | `stats: dict[str, object] = ...` |
| `no-any-return` | `float()` / `int()` 包裹返回值；複雜型別用 local `# type: ignore[no-any-return]` | `return float(self.config.initial_capital + self.realized_pnl)` |
| `valid-type` | 修正錯誤的型別名稱（`any` → `Any`）或移除 module as type | `-> dict[str, Any]` |
| `call-arg` | 第三方 API kwargs 缺口用 local `# type: ignore[call-arg]` | `figure(x_axis_type="datetime")  # type: ignore[call-arg]` |
| `type-arg` | 為 bare generic 加型別參數 | `dict` → `dict[str, Any]`、`list` → `list[str]` |
| `return-value` | `float()` 包裹 `Any` 返回值給 `.sort(key=...)` | `.sort(key=lambda x: float(x["avg_ret"]))` |

### 不可修復的 Error Codes（第三方缺口，需全局壓制）

| Error Code | 來源 | 說明 |
|-----------|------|------|
| `no-untyped-def` | Demo 函式缺參數標註 | 範例程式不要求完整標註 |
| `no-untyped-call` | Shioaji / Panel 未標註函式 | 呼叫未標註的第三方 API |
| `operator` | Polars `Any` 算術 | `Any + float` 無法靜態解析 |
| `union-attr` | Polars 寬聯合型別 stubs | `.mean()` 回傳 `int \| float \| date \| ... \| None` |
| `arg-type` | Polars `Any` / NautilusCatalog union | `get_bars()` 回傳 `pd.DataFrame \| pl.DataFrame` |
| `attr-defined` | NT / Bokeh 動態屬性 | `config.initial_capital` 等 runtime 動態生成的屬性 |

### 修復模式速查

#### `str-bytes-safe` — f-string 中的 `Any` 值

當 polars 方法回傳 `Any`（因為 `.mean()` / `.std()` 等回傳寬聯合型別），直接在 f-string 中格式化會觸發 `str-bytes-safe`。

```python
mean_val = df["close"].mean()  # mypy sees Any (Polars stubs gap); runtime: int | float | date | None
print(f"mean={mean_val:.2f}")  # ❌ str-bytes-safe

print(f"mean={float(mean_val):.2f}")  # ✅ float() 包裹
print(f"range={str(df['datetime'].min())}")  # ✅ str() 包裹（日期型）
```

#### `type-arg` — bare generic 加型別參數

```python
def get_stats() -> dict:           # ❌ bare dict
def get_stats() -> dict[str, Any]: # ✅ 加型別參數

def load_data() -> list:              # ❌ bare list
def load_data() -> list[dict[str, Any]]: # ✅ 巢狀也加

from collections import deque
buf: deque = deque()       # ❌
buf: deque[Any] = deque()  # ✅
```

需要時加 `from typing import Any`。

#### `assignment` — 型別加寬與 narrowing

```python
# NautilusCatalog union 回傳 → 加寬型別
interval_dfs: dict[str, pl.DataFrame | pd.DataFrame] = {}

# dict[str, object] 回傳 → 用 int(float(...)) 鏈式轉換
val = int(float(stats.get("count", 0)))  # float(object) → arg-type (suppressed), int(float) → legal

# isinstance narrowing
df = df_real if isinstance(df_real, pd.DataFrame) else df_real.to_pandas()
```

#### `no-any-return` — 包裹或 local ignore

```python
# 簡單型別 → explicit conversion
def get_equity(self) -> float:
    return float(self.config.initial_capital + self.realized_pnl)

# 複雜型別（DataFrame / dict）→ local ignore
def load_data(self) -> pl.DataFrame:
    return self.catalog.get_bars(...)  # type: ignore[no-any-return]
```

#### `call-arg` — 第三方 API kwargs

```python
fig = figure(
    width=700, height=400,
    x_axis_type="datetime",  # Bokeh stubs 不認這個 kwarg
)  # type: ignore[call-arg]
```

#### `return-value` — sort key 中的 `Any`

```python
# dict[str, Any] 取出的值是 Any，sort key 期望 comparable type
candidates.sort(key=lambda x: x["avg_ret"])       # ❌ return-value
candidates.sort(key=lambda x: float(x["avg_ret"])) # ✅ float() 包裹
```

### 驗證流程

從 `disable_error_code` 中逐個移除 error code 的標準流程：

1. 暫時從 `disable_error_code` 移除目標 code
2. `uv run mypy examples/ --no-error-summary > /tmp/mypy.txt`
3. `rg -F "[code-name]" /tmp/mypy.txt | wc -l` 計數
4. 分類：可修復（用食譜）vs 不可修復（保留壓制）
5. 可修復的用 agent 並行處理（按檔案分組）
6. 修完後驗證 `uv run mypy examples/` 零錯誤
7. 確認 `uv run ruff check examples/` 通過
