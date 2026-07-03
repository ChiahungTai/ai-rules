---
paths:
  - "**/*.py"
---

# Python 程式設計規範

## 命名約定

- Demo 檔案用 `demo_` 前綴（`demo_<lib>.py`），禁止用 `test_` 前綴。`demo_*.py` 為待處置物（commit 時檔案去處進 scripts/ 或 delete，見 /commit 階段 2.7；若行為值得測，build 時另提煉 `test_<feature>.py`）
- 測試檔案用 `test_` 前綴（`test_main.py`）

## `__init__.py` 設計

### 🔴 禁止 re-export

`__init__.py` **禁止** `from .submodule import Symbol` 形式的 re-export。

**為什麼**：re-export 建立隱性依賴鏈。`from package import X` 會先執行 `__init__.py`，如果裡面 re-export 了重型子模組（pandas、numpy 等重型依賴），所有 import 消費者都被迫等待。實測案例：一個 re-export `logging.py`（拉重型框架）+ `cost.py`（拉 pandas）的 `__init__.py`，讓輕量 enum import 從毫秒級膨脹到秒級（兩個數量級）。

### ❌ 錯誤：re-export（LLM 最愛犯的錯）

```python
# package/__init__.py — 禁止這樣寫
from .logging import <heavy_init_fn>               # 拉重型框架（秒級）
from .cost import <CostCalculator>                 # 拉 pandas（數百 ms）
from .enums import <LightEnum>                     # 輕量（ms 級），但被迫等上面兩個

__all__ = ["<heavy_init_fn>", "<CostCalculator>", "<LightEnum>"]
```

後果：`from package.enums import <LightEnum>` 表面上只 import enums，但 Python 先解析 `__init__.py` → 觸發所有 re-export → 秒級延遲。

### ✅ 正確：`__init__.py` 只放註解或空

```python
# package/__init__.py
"""Package docstring."""

# Import policy: 無 re-export
# 消費端用完整路徑 import（from package.module import Class），
# 不透過 __init__.py re-export。
```

消費端直接 `from package.module import Class`，`__init__.py` 雖仍被 Python 執行，但無重型 re-export，開銷可忽略。

### 消費端正確寫法

```python
# ✅ 直接從子模組 import
from <package>.common.enums import <EnumClass>
from <package>.common.logging import <init_fn>

# ❌ 透過 __init__.py re-export import（不應存在）
from <package>.common import <EnumClass>
```

### 規範摘要

- **審查原則**：每個 `__init__.py` 的內容都必須能回答「為什麼放在這裡而非子模組？」行數不是判準，內容是否合理才是。適用所有內容——re-export（原則禁止，見上）、handy functions / 註冊初始化（如 `features/_auto_register_all()`，個案衡量：收益是否大於對所有消費者的 import 代價）、`__version__` / docstring（無代價，合理）
- **禁止** `from .submodule import Symbol` re-export
- **禁止** `__all__` 搭配 re-export（`__all__` 只在 `from package import *` 時有效，幾乎不需要）
- 消費端用完整路徑 import（`from package.module import Class`）
- **唯一例外**：套件發佈給外部使用的 public API（Facade Pattern，內部專案不適用，詳見下段）

### Facade Pattern 為何不適用內部專案

> 補充論證：回應 Python 社群常見「公開 API 統一由 `__init__.py` 導出（Facade Pattern）」的主張。禁令若不先承認並反駁 Facade 的價值，會被這套社群論述動搖。

Facade Pattern 的價值在**解耦內部實作與外部介面**——使用者不必知道內部目錄結構，重構時 import 路徑不崩潰。**這個價值在「發佈給外部消費者的套件」為真**：使用者不該知道、也無需知道內部結構。

但內部專案的消費者是同專案的 modules/scripts/tests/AI，本來就靠 instruction 檔（AGENTS.md）導航定位，Facade 的「重構解耦」收益不存在，代價卻突出：

- **import 開銷**：re-export 重型子模組（pandas 等重型依賴），無關消費者被迫等待（見上方實測）
- **循環依賴風險**：`__init__.py` 一層層 re-export 互相依賴，是循環 import 溫床
- **IDE 混淆**：符號來源指向 `__init__` 而非真實定義，jump-to-def 失準

**判準**：Facade 的價值取決於「消費者是否外部」。內部專案消費者靠導航而非 import 路徑簡潔度，故全面禁止 re-export。

**若未來發佈外部套件**：用 `_internal` 模式（PyTorch/Open edX 風格）——實作放私有子模組，`__init__.py` 只 re-export 穩定 API。而非把所有內部符號 re-export。

### 遷移既有 re-export

遇到既有 `__init__.py` 含 re-export 時，按以下步驟遷移（禁止直接刪除，必須先改消費端）：

1. **找出消費端**：`rg -t py "from package import" path/to/package/` 找出所有透過 re-export import 的消費者
2. **逐一改直接路徑**：將 `from package import X` 改為 `from package.module import X`
3. **移除 re-export**：消費端全數改完後，清除 `__init__.py` 中的 re-export 行

## 型別註解（Python 3.12+）

### ❌ 禁止 `from __future__ import annotations`

將所有註解轉為字串，掩蓋缺失 import 和 circular import。前向引用用字串註解：`def process(node: "TreeNode") -> None:`

### ❌ 禁止 deprecated typing 別名

| 禁止 | 正確 |
|------|------|
| `List[T]`, `Dict[K,V]`, `Set[T]`, `Tuple[T1,T2]` | `list[T]`, `dict[K,V]`, `set[T]`, `tuple[T1,T2]` |
| `Optional[T]`, `Union[T1,T2]` | `T \| None`, `T1 \| T2` |

AI（尤其舊模型）常自動補上舊寫法，必須修正。

### typing 模組僅 import：Callable, Protocol, TypeVar, ParamSpec, Self, Any

### `Self` 優先於字串前向引用

當方法回傳**自身 class 或 subclass 實例**時，用 `Self` 取代字串註解 `"ClassName"`。適用情境：`@classmethod` 回傳 `cls(...)`、`__enter__` 回傳 self、`copy()` 回傳同型別實例。

字串前向引用 `"OtherClass"` 僅用於引用**其他** class，`Self` 無法表達此語義。

### ❌ 禁止 `TYPE_CHECKING`

Circular import 是架構問題，重構模組結構才是解法。`TYPE_CHECKING` 只是掩蓋問題。

### `Any` 使用

只用在外部邊界（JSON 解析、第三方庫），加註解說明理由。

**查證義務**：使用 `Any` 前，必須先讀 `.venv/lib/python*/site-packages/` 中的實際源碼確認型別。很多情況下套件已有正確的回傳型別（`py.typed`），AI 偷懶不看源碼直接腦補「一定是 `Any`」是違規行為。查證流程：`fd 'py.typed' .venv/.../package/` → 有 `py.typed` 就去讀源碼找真實型別 → 只在確認無法推導時才用 `Any`。

## Python 命令執行

### 強制 `uv run`

```bash
uv run python script.py
uv run pytest tests/test_example.py -v
```

- **pytest 一律背景跑**（`run_in_background: true`），不論從哪個 command 或 context 觸發
- 禁止：`python`、`python3`、`PYTHONPATH=$PWD`、外部 `timeout`/`gtimeout`（macOS 無此命令）

### 🔴 禁止：多行 `python -c` 中換行後使用 `#` 註解

Claude Code 偵測引號內「換行後接 `#`」會觸發權限提示。`#` 緊接開頭引號（`"# comment\n..."`）不觸發，但換行後的 `#`（`"\n# comment\n..."`）會。需要註解時改寫為 `.py` 檔案。

## Editable Install

遇到 `ModuleNotFoundError` 時先確認 `uv pip install -e .` 已執行。
