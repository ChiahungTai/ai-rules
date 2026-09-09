---
harness-scope: neutral
paths:
  - "**/*.py"
---

# Python 程式設計規範

## 命名約定

demo 用 demo_，禁 test_；測試用 test_。demo 暫存到 commit 時移 scripts/ 或刪除，值得測的行為在 build 另提煉正式測試。

## `__init__.py` 禁止 re-export

只放 docstring/註解/__version__，禁 `from .submodule import Symbol` re-export（含 __all__）；消費端用 `from package.module import Class`。每個例外內容都須回答為何不放子模組，handy function/註冊初始化衡量全消費者代價，不以行數判。

真實案例：重型 re-export 讓輕量 enum import 從毫秒變秒；隱性依賴又促成循環 import、使 jump-to-def 指錯來源。

### 補充論證：Facade Pattern 為何不適用內部專案

Facade 對外部消費者有穩定 API 解耦價值；內部 modules/scripts/tests/AI 共同重構，收益不足以抵銷 import/循環/IDE 代價。判準是消費者是否外部；未來發佈外部套件可用 _internal 私有實作＋__init__ 只導出穩定 API。

### 遷移既有 re-export

禁先刪：先查全消費者（含 `from package import` 與 `from .` 相對 import），逐一改完整 module 路徑，全部改完才清 __init__ re-export。文字掃描用 rg，符號查證依 symbol-query-routing。

## 型別註解（Python 3.12+）

- 禁 from __future__ import annotations，字串化會掩蓋缺失/circular import；其他 class 前向引用用字串。
- 禁 TYPE_CHECKING，循環須重構解決；回傳自身/子類用 Self（cls、enter、copy 等）。
- 禁 List/Dict/Set/Tuple/Optional/Union 舊 typing，改內建泛型與 T | None / T1 | T2。
- typing 只 import Callable、Protocol、TypeVar、ParamSpec、Self、Any。
- Any 限 JSON/第三方外部邊界並註明理由——先查 venv 套件 py.typed 與 source 型別，確認無法推導才用，禁猜。

## Python 命令執行

強制 uv run 前綴，禁 python/python3/PYTHONPATH（詳 tool-discipline）；另禁外部 timeout/gtimeout（macOS 無此命令）。pytest 背景跑；ModuleNotFoundError 先確認 uv pip install -e .。
