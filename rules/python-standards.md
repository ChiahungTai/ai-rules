# Python 程式設計規範

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話
>
> **開發環境**: MacBook Pro M1 Max (macOS Darwin 24.6.0)

---

## 正向命名約定

> **核心原則**：使用清晰明確的命名，避免誤導開發工具。

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

### 範例

```python
# Demo 程式使用 demo_ 前綴（檔案: examples/demo.py）
def demo_worker_task():
    ...

# 測試程式才使用 test_ 前綴（檔案: tests/test_worker.py）
def test_worker_task():
    ...
```

---

## import 管理標準

> **核心原則**：import 語句必須在檔案頂部（toplevel）。

### 強制規則

- **必須**：import 語句在檔案頂部
- **例外**：避免循環依賴、條件性依賴、延遲載入

### 範例

```python
# ✅ 正確：檔案頂部 import
from pathlib import Path

def process_data(file_path: Path | None = None) -> dict:
    # 實際邏輯
    ...
```

---

## `__init__.py` 設計原則

> **核心原則**：`__init__.py` 應保持精簡，只暴露公開 API，避免 circular import。

### 絕對約束

- **檔案行數**：< 50 行（不含空行和註解）
- **內容限制**：只包含真正需要公開的 API
- **強制要求**：使用 `__all__` 明確宣告公開 API

### 判斷標準

| 問題 | 決策 |
|------|------|
| 這個類別/函數需要被外部直接 import 嗎？ | 是 → 可以加入 `__init__.py` |
| 加入後會讓 `__init__.py` 超過 50 行嗎？ | 是 → 不要加，用完整路徑 import |
| 加入後造成 circular import 嗎？ | 是 → 重構模組結構或用 TYPE_CHECKING |

### 推薦做法

```python
# ❌ 錯誤：依賴 __init__.py（容易 circular import）
from package import ClassA, ClassB, ClassC

# ✅ 正確：使用完整路徑（清晰、避免 circular）
from package.module_a import ClassA
from package.module_b import ClassB

# ✅ 正確的 __init__.py（精簡、只暴露公開 API）
from .core import PublicAPI

__all__ = ["PublicAPI"]
```

---

## 型別註解標準（Python 3.11+）

> **核心原則**：優先使用內建型別語法，僅在必要時從 `typing` 模組 import。

### ❌ 禁止使用 `from __future__ import annotations`

Python 3.11+ 已原生支援 PEP 563（延遲註解評估）和 PEP 585（泛型型別），此 import 完全多餘。

```python
# ❌ 錯誤：Python 3.11+ 不需要
from __future__ import annotations

# ✅ 正確：直接使用內建型別語法
def process(items: list[str]) -> dict[str, int]:
    ...
```

### 標準型別語法（內建）

- `list[T]`, `dict[K, V]`, `set[T]`, `tuple[T1, T2]`
- `T1 | T2`（聯合型別）, `T | None`（可選型別）

### typing 模組適用範圍

僅以下型別從 `typing` import：
- `Callable`, `Protocol`, `TypeVar`, `ParamSpec`, `Self`

### TYPE_CHECKING 使用限制

> **核心原則**：TYPE_CHECKING 容易被 AI 濫用，使用前必須得到使用者同意。

**🔴 強制約束**：
- AI **不得主動**使用 `TYPE_CHECKING` 解決循環依賴
- 必須先詢問使用者是否同意使用
- 優先考慮其他解決方案（重構模組結構、延遲 import）

**常見濫用模式**：
```python
# ❌ AI 常見的過度使用
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_a import ClassA  # 不必要地複雜化
```

**正確使用時機**（需使用者同意）：
- 真正無法避免的循環依賴
- 僅用於型別提示，不影響運行時行為
- 經過使用者明確同意

### 範例

```python
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

---

## Python 命令執行約束

> **核心原則**：所有 Python 指令必須使用 `uv run` 執行。

### 強制模式

**所有 Python 命令都遵循此模式**：
```bash
uv run [python/pytest/其他] [參數]
```

### 正確範例

```bash
# 執行 Python 腳本
uv run python script.py

# 執行測試
uv run pytest tests/test_example.py -v

# 執行模組
uv run python -m module_name
```

### ❌ 絕對禁止：外部 timeout 命令

```bash
timeout 60 uv run python script.py  # ❌ macOS 預設沒有 timeout 命令
gtimeout 30s uv run pytest  # ❌ gtimeout 有跨平台相容性問題
PYTHONPATH=$PWD uv run python script.py  # ❌ 破壞 uv 環境隔離
python script.py  # ❌ 未使用 uv 管理環境
python3 script.py  # ❌ 未使用 uv 管理環境
```

### ✅ 允許：應用程式內部 --timeout 參數

```bash
# ✅ 應用程式自己處理 timeout，跨平台相容、優雅可控
uv run python examples/demo_app.py --port 5007 --timeout 60000
uv run python scripts/long_running_task.py --timeout 300
```

### macOS 平台相容性說明

- **外部 `timeout` 命令**: macOS 預設不包含（GNU coreutils），禁止使用
- **應用程式內部 `--timeout`**: 跨平台相容，優先採用此做法
- **設計建議**: 需要超時控制時，在應用程式內部用 `argparse` 實現 `--timeout` 參數

---

## 專案安裝模式（Editable Install）

> **核心原則**：使用 UV 管理的專案應安裝為 editable mode，確保模組可從任何路徑 import。

### 強制安裝時機

以下情況**必須先執行** `uv pip install -e .`：

| 情境 | 症狀 | 解決方案 |
|------|------|----------|
| `examples/` 腳本 import 失敗 | `ModuleNotFoundError: No module named 'project_name'` | `uv pip install -e .` |
| 從子目錄執行腳本 | 找不到上層模組 | `uv pip install -e .` |
| 多入口點專案 | 不同目錄的腳本互相 import | `uv pip install -e .` |

### 正確範例

```bash
# ✅ 正確：首次安裝 editable mode
uv pip install -e .

# ✅ 正確：之後直接執行
uv run python examples/demo_script.py

# ❌ 錯誤：跳過安裝直接執行
uv run python examples/demo_script.py  # ModuleNotFoundError
```

### 安裝驗證

```bash
# 確認專案已安裝
uv pip list | grep <project-name>
```

---

## 執行前自檢清單

在執行任何 Python 相關操作前確認：

### 命名與 import
- [ ] Demo 檔案使用 `demo_` 前綴，測試檔案使用 `test_` 前綴
- [ ] import 語句在檔案頂部（除非符合例外條件）
- [ ] `__init__.py` < 50 行，使用 `__all__` 宣告公開 API

### 型別註解
- [ ] 不使用 `from __future__ import annotations`（Python 3.11+ 已原生支援）
- [ ] 使用 `list[T]`, `T1 | T2` 等內建型別語法
- [ ] 僅在必要時從 `typing` import（Callable, Protocol 等）
- [ ] 使用 `TYPE_CHECKING` 前已得到使用者同意

### 命令執行
- [ ] 所有 Python 命令以 `uv run` 開頭
- [ ] 不包含 `timeout`/`gtimeout`/`PYTHONPATH`
- [ ] 不直接使用 `python` 或 `python3`
- [ ] 遇到 ModuleNotFoundError 時，先確認 `uv pip install -e .` 已執行

### 專案狀態
- [ ] 專案已安裝為 editable mode（首次開發或遇到 import 錯誤時確認）

---

> 💡 **核心哲學**: 清晰命名、頂部 import、精簡 `__init__.py`、內建型別優先、強制 `uv run`。這些約束確保程式碼可讀性、避免循環依賴、維持環境隔離。
