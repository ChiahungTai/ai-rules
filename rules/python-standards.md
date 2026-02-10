# Python 程式設計規範

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 正向命名約定

> **核心原則**：使用清晰明確的命名，避免誤導開發工具。

### 推薦做法：使用清晰的命名前綴

```python
# Demo 程式使用 demo_ 前綴
# 檔案: examples/demo.py
def demo_worker_task():
    ...

# 測試程式才使用 test_ 前綴
# 檔案: tests/test_worker.py
def test_worker_task():
    ...
```

### 命名規範

| 類型 | 規範 | 範例 |
|------|------|------|
| 檔案 | snake_case | `main.py`, `test_example.py` |
| 變數/函式 | snake_case | `user_name`, `calculate_total()` |
| 類別 | PascalCase | `DataProcessor`, `ApiClient` |
| 常數 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_BASE_URL` |
| 測試檔案 | `test_` 前綴 | `test_main.py` |
| **實驗/範例檔案** | **禁止 `test_` 前綴** | ❌ `test_shioaji.py` ✅ `demo_shioaji.py` |
| Private 方法 | `_` 前綴 | `_internal_method()` |

---

## import 管理標準

> **核心原則**：import 語句必須在檔案頂部（toplevel）加入。

### toplevel import 原則

import 語句必須在檔案頂部加入，不得在函數或類內部 import

### 允許局部 import 的例外情況

- 避免循環依賴（circular import）
- 條件性依賴（optional dependencies）
- 延遲載入以減少啟動時間

### 推薦做法

```python
# 檔案頂部
from pathlib import Path

def process_data(file_path: Path | None = None) -> dict:
    # 實際邏輯
    ...
```

---

## `__init__.py` 設計原則

> **核心原則**：`__init__.py` 應保持精簡，只暴露公開 API，避免 circular import。

### ❌ 錯誤做法：塞太多東西到 `__init__.py`

```python
# __init__.py 超過 50 行，有很多 from xxx import yyy
from .module_a import ClassA
from .module_b import ClassB
from .module_c import func_c
from .module_d import ClassD
from .utils import helper1, helper2, helper3
# ... 很多 import

# 這會導致：
# 1. 啟動時載入所有模組（影響性能）
# 2. 高 circular import 風險
# 3. 難以追蹤依賴關係
```

### ✅ 正確做法：只暴露公開 API

```python
# __init__.py 保持精簡（通常 < 20 行）
from .core import PublicAPI

__all__ = ["PublicAPI"]
```

### 判斷標準

| 問題 | 決策 |
|------|------|
| 這個類別/函數需要被外部直接 import 嗎？ | 是 → 可以加入 `__init__.py` |
| 加入後會讓 `__init__.py` 超過 50 行嗎？ | 是 → 不要加，用完整路徑 import |
| 加入後造成 circular import 嗎？ | 是 → 重構模組結構或用 TYPE_CHECKING |

### 推薦的 import 方式

```python
# ❌ 依賴 __init__.py（容易 circular import）
from package import ClassA, ClassB, ClassC

# ✅ 使用完整路徑（清晰、避免 circular）
from package.module_a import ClassA
from package.module_b import ClassB
from package.module_c import ClassC
```

### `__init__.py` 自檢清單

撰寫 `__init__.py` 前確認：
- [ ] 檔案行數 < 50 行（不含空行和註解）
- [ ] 只包含真正需要公開的 API
- [ ] 不會造成 circular import
- [ ] 使用 `__all__` 明確宣告公開 API
- [ ] 內部實作細節不暴露

---

## 型別註解標準（Python 3.11+）

> **核心原則**：優先使用內建型別語法，僅在必要時從 `typing` 模組 import。

### 標準型別語法

Python 3.11+ 使用內建型別作為泛型型別：

- **串列**: `list[T]`
- **字典**: `dict[K, V]`
- **集合**: `set[T]`
- **元組**: `tuple[T1, T2]`
- **聯合型別**: `T1 | T2`
- **可選型別**: `T | None`

### typing 模組適用範圍

以下型別無內建替代，從 `typing` 模組 import：

- `Callable` - 函數型別
- `Protocol` - 結構子型別
- `TypeVar` - 泛型型別變數
- `ParamSpec` - 參數規格變數
- `Self` - 當前類別實例

### 推薦做法

```python
# 優先從 typing import 必要的特殊型別
from typing import Callable, Protocol

def process_items(
    items: list[str],
    config: dict[str, int] | None = None,
    callback: Callable[[str], bool] | None = None
) -> dict[str, int]:
    if config is None:
        config = {}
    return {"count": len(items), **config}

# Protocol 定義結構子型別
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()
```

### 型別註解自檢清單

撰寫型別註解前確認：
- [ ] 使用 `list[T]` 等內建泛型語法
- [ ] 使用 `T1 | T2` 聯合型別語法
- [ ] 僅在無內建替代時才從 `typing` import
- [ ] 型別註解清晰表達意圖，提升可讀性

---

## Python 命令執行約束

> **核心原則**：所有 Python 指令必須使用 `uv run` 執行。

### 必須使用的標準模式

所有 Python 命令都遵循此模式：
```bash
uv run [python/pytest/其他] [參數]
```

### 正確做法

```bash
# 執行 Python 腳本
uv run python script.py

# 執行測試
uv run pytest

# 執行特定測試檔案
uv run pytest tests/test_example.py -v

# 執行模組
uv run python -m module_name

# 套件管理後執行
uv run pip install requests && uv run python script.py
```

### ❌ 禁止使用的模式

```bash
timeout 60 uv run python script.py  # ❌ timeout 會干擾 uv 環境管理
gtimeout 30s uv run pytest  # ❌ gtimeout 有跨平台問題
PYTHONPATH=$PWD uv run python script.py  # ❌ 破壞環境隔離
python script.py  # ❌ 未使用 uv 管理環境
python3 script.py  # ❌ 未使用 uv 管理環境
```

### 執行命令前自檢清單

在執行任何 Python 命令前確認：
- [ ] 以 `uv run` 開頭
- [ ] 不包含 `timeout`/`gtimeout`
- [ ] 不包含 `PYTHONPATH`
- [ ] 不直接使用 `python`（沒有 uv run）
