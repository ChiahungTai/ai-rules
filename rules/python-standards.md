---
harness-scope: neutral
paths:
  - "**/*.py"
---

# Python 程式設計規範

## 命名約定

- Demo 檔案用 `demo_` 前綴（`demo_<lib>.py`），禁止用 `test_` 前綴。`demo_*.py` 為待處置物（commit 時檔案去處進 scripts/ 或 delete；若行為值得測，build 時另提煉 `test_<feature>.py`）
- 測試檔案用 `test_` 前綴（`test_main.py`）

## `__init__.py` 禁止 re-export

`__init__.py` **禁止** `from .submodule import Symbol` 形式的 re-export（`__all__` 搭配 re-export 一併禁止——只在 `from package import *` 時有效，幾乎不需要），只放 docstring/註解/`__version__`。消費端用完整路徑 import（`from package.module import Class`）。

**為什麼**：re-export 建立隱性依賴鏈——`from package import X` 會先執行 `__init__.py`，若 re-export 重型子模組（pandas、numpy），所有 import 消費者都被迫等待（實測案例：輕量 enum import 從毫秒級膨脹到秒級，兩個數量級）。另：`__init__` 層層 re-export 是循環 import 溫床；符號來源指向 `__init__` 讓 jump-to-def 失準。

### 補充論證：Facade Pattern 為何不適用內部專案

> 回應 Python 社群「公開 API 統一由 `__init__.py` 導出（Facade）」的主張——禁令若不先承認並反駁 Facade 價值，會被社群論述動搖。

Facade 的解耦價值只在「發佈給**外部**消費者的套件」為真；內部專案消費者是同專案 modules/scripts/tests/AI（靠 instruction 檔導航定位），重構解耦收益不存在而代價突出（import 開銷、循環依賴風險、IDE 混淆）。**判準：Facade 價值取決於消費者是否外部**；未來發佈外部套件改用 `_internal` 模式（PyTorch/Open edX 風格：實作放私有子模組，`__init__.py` 只 re-export 穩定 API）。

**審查原則**：每個 `__init__.py` 的內容都必須能回答「為什麼放在這裡而非子模組？」行數不是判準，內容是否合理才是（re-export 原則禁止；handy functions、註冊初始化個案衡量收益 vs 全消費者 import 代價；`__version__`、docstring 無代價合理）。

### 遷移既有 re-export

禁止直接刪除，先改消費端：① `rg -t py "from package import"` 找出所有 re-export 消費者 → ② 逐一改直接路徑 `from package.module import X` → ③ 消費端全改完後才清除 `__init__.py` 的 re-export 行。

> re-export 遷移掃消費端時，相對 import（`from .submodule import X`）消費者同樣要改成完整路徑——相對 import 穿透 `__init__` 邊界，`rg "from \."` 也要掃。

## 型別註解（Python 3.12+）

- ❌ 禁止 `from __future__ import annotations`（將註解轉字串，掩蓋缺失 import 和 circular import）。前向引用用字串註解：`def process(node: "TreeNode") -> None:`
- ❌ 禁止 deprecated typing 別名：`List/Dict/Set/Tuple` → `list/dict/set/tuple`；`Optional[T]`/`Union` → `T | None`/`T1 | T2`。AI（尤其舊模型）常自動補舊寫法，必須修正
- typing 模組僅 import：`Callable, Protocol, TypeVar, ParamSpec, Self, Any`
- **`Self` 優先於字串前向引用**：方法回傳自身 class/subclass 實例時（`@classmethod` 回傳 `cls(...)`、`__enter__`、`copy()`）用 `Self`；字串前向引用 `"OtherClass"` 僅用於引用**其他** class
- ❌ 禁止 `TYPE_CHECKING`（circular import 是架構問題，重構模組結構才是解法）
- **`Any` 使用**：只用在外部邊界（JSON 解析、第三方庫），加註解理由。**查證義務**：用 `Any` 前先讀 `.venv/lib/python*/site-packages/` 實際源碼確認型別——`fd 'py.typed' .venv/.../package/` → 有 `py.typed` 就讀源碼找真實型別，只在確認無法推導時才用 `Any`（AI 偷懶腦補「一定是 Any」是違規）

## Python 命令執行

- 強制 `uv run` 前綴（`uv run python script.py`、`uv run pytest`）；禁止 `python`、`python3`、`PYTHONPATH=$PWD`、外部 `timeout`/`gtimeout`（macOS 無此命令）
- **pytest 一律背景跑**（Claude: `run_in_background: true`），不論從哪個 command 或 context 觸發

## Editable Install

遇到 `ModuleNotFoundError` 時先確認 `uv pip install -e .` 已執行。
