---
paths:
  - "**/*.py"
---

# Python 程式設計規範

## 命名約定

- Demo 檔案用 `demo_` 前綴（`demo_shioaji.py`），禁止用 `test_` 前綴
- 測試檔案用 `test_` 前綴（`test_main.py`）

## `__init__.py` 設計

- < 100 行，只暴露公開 API，用 `__all__` 宣告
- 消費端用完整路徑 import（`from package.module import Class`），不依賴 `__init__.py`

## 型別註解（Python 3.11+）

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
