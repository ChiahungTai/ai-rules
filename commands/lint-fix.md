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
1. **預設假設：不是 circular import**。AI 常偷懶放在函數內，99% 只是偷懶，不是真的有循環依賴
2. **真的遇到 circular import 時**：正確解法是重構目錄結構（調整 parent-child 關係），不是局部 import。局部 import 只掩蓋問題
3. **檢查 pyproject.toml 的 per-file-ignores**：如果專案已設定例外，尊重專案配置

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

#### ignore_errors 模組仍應修 type-arg

即使 `pyproject.toml` 有 `ignore_errors = true`（Layer 4），修 type-arg 和 no-untyped-def 仍然有價值：
1. 未來可能移除 ignore_errors（當套件改善型別支援時）
2. IDE（PyCharm、VS Code）使用 pyright/pylance，不讀 mypy overrides
3. 正確的型別標註幫助人類理解程式碼

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

### 優先級 6：第三方套件 Type Gap

當第三方套件的 type annotations 不完整時，遵循 [python-type-gap](../skills/python-type-gap/SKILL.md) skill 的四層處理策略（Type Narrowing → Project Stubs → `# type: ignore[code]` → pyproject.toml Override）。

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
- **遵循 [python-type-gap](../skills/python-type-gap/SKILL.md) skill 的四層策略**，`# type: ignore` 是最後手段
- 必須指定 error code（如 `[no-untyped-call]`、`[operator]`），不用裸 `# type: ignore`
- 只用於第三方套件的 gap，不用於我們自己程式碼的型別問題

## 🎯 品質檢查清單
- [ ] 執行了 ruff check --fix
- [ ] 執行了 ruff format
- [ ] 執行了 mypy
- [ ] 分析了所有 PLC0415 問題
- [ ] 檢查了濫用的 TYPE_CHECKING
- [ ] 識別了舊式 typing 慣例
- [ ] 檢查了裸型別缺參數（`type-arg`：裸 `list`/`dict`）
- [ ] 第三方 type gap 遵循 [python-type-gap](../skills/python-type-gap/SKILL.md) skill 四層策略
- [ ] 每個 `# type: ignore` 都有指定 error code
- [ ] 檢查了 pyproject.toml overrides 是否仍必要
- [ ] 提供了具體的修正建議
- [ ] 建議了修正優先級
