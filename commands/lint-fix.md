---
description: "執行 ruff 和 mypy 檢查並自動修正問題"
when_to_use: "Run ruff format, ruff check --fix, and mypy on Python files. Use after writing or modifying Python code to enforce style and type conventions."
usage: "/lint-fix [檔案或目錄路徑]"
argument-hint: "預設檢查當前目錄，可指定檔案或目錄"
allowed-tools: ["Bash", "Read", "Edit", "Grep"]
---

# Lint Fix - Python 程式碼品質自動修正工具

你是 Python 程式碼品質修正專家，專精於使用 ruff 和 mypy 自動修正常見的程式碼問題。

## 🎯 核心目標

1. **自動修正 AI 寫 code 的常見壞習慣**
2. **強制執行 Python 3.12+ 的現代型別慣例**
3. **減少 code review 時的重複工作**

## 🚀 執行流程

### 1. Ruff 自動修正
```bash
# 自動修正可修正的問題（尊重 pyproject.toml 的 per-file-ignores）
uv run ruff check --fix $ARGUMENTS
```

### 2. Ruff 格式化
```bash
# 格式化程式碼（含 import 排序）
uv run ruff format $ARGUMENTS
```

### 3. MyPy 型別檢查
```bash
# 執行型別檢查（warn_unused_ignores 會抓濫用的 # type: ignore）
uv run mypy $ARGUMENTS
```

## 🔍 問題分析與建議

當發現無法自動修正的問題時，按以下優先級分析：

### 優先級 1：import outside toplevel (PLC0415)

#### ❌ 錯誤做法：直接在函數內 import 偷懶
```python
# AI 常偷懶這樣做，通常不是真的 circular import
def process_data(data):
    import pandas as pd  # ❌ 偷懶
    return pd.DataFrame(data)
```

#### ✅ 正確做法：toplevel import
```python
import pandas as pd

def process_data(data):
    return pd.DataFrame(data)
```

#### 判斷標準
1. **檢查 pyproject.toml 的 per-file-ignores**：如果專案已設定例外，尊重專案配置
2. **分析是否真的有 circular import**：
   - 大部分情況沒有，AI 只是偷懶
   - 如果真的有，建議討論架構重構

### 優先級 2：`__init__.py` 太肥

#### ❌ 錯誤做法：塞太多東西到 `__init__.py`
```python
# __init__.py 超過 50 行，有很多 from xxx import yyy
from .module_a import ClassA
from .module_b import ClassB
from .module_c import func_c
# ... 很多 import
```

#### ✅ 正確做法：只暴露公開 API
```python
# __init__.py 保持精簡
from .core import PublicAPI

__all__ = ["PublicAPI"]
```

### 優先級 3：濫用 TYPE_CHECKING

#### ❌ 錯誤做法：不必要地使用 TYPE_CHECKING
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from somewhere import SomeType  # ❌ 大部分情況不需要

def process(x: "SomeType"):  # string forward reference
    pass
```

#### ✅ 正確做法：直接 toplevel import
```python
# Python 3.12+ 直接 import 即可
from somewhere import SomeType

def process(x: SomeType):
    pass
```

### 優先級 4：舊式 typing 慣例

#### ❌ 錯誤做法：使用舊式型別
```python
from typing import List, Dict, Optional

def process(items: List[str], config: Optional[Dict[str, int]] = None) -> Dict[str, int]:
    ...
```

#### ✅ 正確做法：Python 3.12+ 內建型別
```python
# 優先使用內建型別語法
def process(
    items: list[str],
    config: dict[str, int] | None = None
) -> dict[str, int]:
    ...
```

#### 修正規則
- `List[T]` → `list[T]`
- `Dict[K, V]` → `dict[K, V]`
- `Set[T]` → `set[T]`
- `Tuple[T1, T2]` → `tuple[T1, T2]`
- `Optional[T]` → `T | None`
- `Union[T1, T2]` → `T1 | T2`

#### `type-arg`：裸型別缺參數（mypy strict）

mypy strict 模式要求泛型型別必須帶參數，裸 `list`、`dict` 會觸發 `type-arg` 錯誤。

```python
# ❌ 裸型別缺參數
def get_indicators(self) -> list: ...
def build_config(self) -> dict: ...

# ✅ 帶型別參數
def get_indicators(self) -> list[IndicatorDef]: ...
def build_config(self) -> dict[str, Any]: ...
```

### 優先級 5：濫用 Any

#### ❌ 錯誤做法：動不動就用 Any
```python
from typing import Any

def process(data: Any) -> Any:  # ❌ 太寬鬆
    ...
```

#### ✅ 正確做法：用具體型別
```python
def process(data: dict[str, int | float]) -> list[str]:
    ...
```

#### 何時使用 Any
- 真的無法確定型別的動態程式碼
- 與缺乏型別註解的第三方庫互動
- **必須加註解釋為什麼需要 Any**

### 優先級 6：第三方套件 Type Gap 的四層處理策略

當第三方套件的 type annotations 不完整時，按以下順序嘗試：

#### Layer 1：Type Narrowing（最推薦）

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

#### Layer 2：Project Stubs（推薦）

適用：套件無 type support、inline annotations 缺口多、或有 `py.typed` 但特定子模組缺 stubs。

**前置檢查**：先用 `fd 'py.typed' .venv/.../package/` 確認套件是否已有型別支援。

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

#### Partial Stubs 關鍵約束

- **`__init__.pyi` 必須有 `__getattr__ → Any`**：確保 top-level 屬性（如 `pa.schema`、`pa.Table`）透傳到已安裝套件的型別
- **只補缺口的子模組**：不需要為整個套件寫完整 stubs
- **只 stub 用到的函式**：先 `rg 'pc\.\w+' mosaic_alpha/ -t py --no-filename -o > /tmp/usage.txt`，再用 `sort -u /tmp/usage.txt` 找出實際用量

#### Layer 3：精確的 `# type: ignore`

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

#### `no-any-return` 的替代技巧

當 `wrangler.process()` 等第三方函式回傳 `Any`，觸發 `no-any-return` 時，用 explicit variable annotation。**前提**：函式回傳型別必須接受 `list[Any]`（mypy 認為 `list[Any]` 與 `list[T]` 相容）；若回傳型別是嚴格的 `list[Bar]` 且 mypy 報 `incompatible return`，仍需 `# type: ignore[no-any-return]`。

```python
# ❌ 直接收會觸發 no-any-return
return wrangler.process(df_pd)  # type: ignore[no-any-return]

# ✅ 先賦值給 typed variable
bars: list[Any] = wrangler.process(df_pd)
return bars
```

#### Layer 4：pyproject.toml Override（最後手段）

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

#### 不推薦：全域寬鬆設定

```toml
# ❌ 過度抑制 — polars 1.x 已有完整 py.typed
[[tool.mypy.overrides]]
module = "polars.*"
ignore_errors = true
```

### 優先級 7：pyproject.toml MyPy Overrides 清理

定期檢查 `[tool.mypy.overrides]` 是否仍必要。

#### 檢查流程

1. **識別冗餘 strict=true**：如果 global 已設 `strict = true`，override 再設一次是冗餘
2. **識別不存在的模組**：override 引用的模組目錄可能已刪除或從未建立
3. **逐項移除測試**：暫時移除 override → 跑 `uv run mypy mosaic_alpha/` → 看是否仍需要
4. **驗證全專案**：`uv run mypy mosaic_alpha/ --strict` 確認所有模組都能通過

#### 常見可移除項目

| 類型 | 判斷方式 | 處理 |
|------|---------|------|
| 冗餘 `strict = true` | global 已有 | 直接刪除整個 override |
| 不存在的模組 | `fd -t d -d 1 . mosaic_alpha/` 確認 | 直接刪除整個 override |
| 第三方 blanket ignore | 套件已有 `py.typed` | 移除，改用 Layer 1-3 |
| UI framework ignore | Panel/Bokeh 的 runtime metaprogramming | 保留，加註解 |

## 📋 輸出格式

### 標準輸出結構
```
## 執行摘要
[簡述執行結果，修正了多少問題]

## Ruff 修正結果
[列出自動修正的問題]

## MyPy 檢查結果
[列出型別問題]

## 需要手動處理的問題
### PLC0415: import outside toplevel
[檔案:行號] 建議：...

### 型別問題
[檔案:行號] 建議：...

## 建議修正優先級
1. [高優先級問題]
2. [中優先級問題]
3. [低優先級問題]
```

## 🔧 執行約束

### 必須遵守
- **使用 uv run**：所有 Python 命令必須使用 `uv run`
- **尊重專案配置**：使用現有的 `pyproject.toml`，不覆蓋
- **分析前先查證**：確認問題真的存在，不基於猜測

### 分析 circular import 時
1. 檢查是否在 `pyproject.toml` 的 per-file-ignores 中
2. 如果不在，分析導入鏈是否真的循環
3. 建議重構架構而非使用局部 import

### 處理 `# type: ignore` 時
- `warn_unused_ignores = true` 會標記不必要的
- 每個被標記的都應該檢查是否真的需要
- **優先嘗試 type narrowing（isinstance）或 stubs**，`# type: ignore` 是最後手段
- 必須指定 error code（如 `[no-untyped-call]`、`[operator]`），不用裸 `# type: ignore`
- 只用於第三方套件的 gap，不用於我們自己程式碼的型別問題

### 處理第三方套件 type gap 時（按優先級）
1. **先試 isinstance type narrowing** — 解決 union type 衝突
2. **再試 project stubs/** — 適用於無 `py.typed`、缺口多、或特定子模組缺 stubs 的套件
3. **最後才用 `# type: ignore[error-code]`** — 精確到單一呼叫點
4. **不使用全域 `ignore_errors = true`** — 除非是 UI framework 等本質不可靜態型別化的場景

## 🎯 品質檢查清單
- [ ] 執行了 ruff check --fix
- [ ] 執行了 ruff format
- [ ] 執行了 mypy
- [ ] 分析了所有 PLC0415 問題
- [ ] 檢查了濫用的 TYPE_CHECKING
- [ ] 識別了舊式 typing 慣例
- [ ] 檢查了裸型別缺參數（`type-arg`：裸 `list`/`dict`）
- [ ] 嘗試了 isinstance type narrowing 替代 `# type: ignore`
- [ ] 嘗試了 stubs/ 替代 `# type: ignore`（適用於無 py.typed、缺口多、或特定子模組缺 stubs 的套件）
- [ ] 每個 `# type: ignore` 都有指定 error code
- [ ] 檢查了 pyproject.toml overrides 是否仍必要（冗餘 strict=true、不存在的模組、已移除的 blanket ignore）
- [ ] 提供了具體的修正建議
- [ ] 建議了修正優先級
