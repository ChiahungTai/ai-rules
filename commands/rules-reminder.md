---
description: "快速提醒 LLM 最常忘記的規則 — 避免權限提示卡關"
when_to_use: "Remind the LLM of rules most frequently violated: no # in python -c, use rg/fd not grep/find, always uv run, no sed for code, split pipe commands."
usage: "/rules-reminder"
allowed-tools: ["Read"]
---

# Rules Reminder — 最常被忘記的規則

以下是 LLM 最常犯、每次都會觸發權限提示的錯誤。**現在起嚴格遵守，不再犯。**

---

## 1. 多行 `python -c` 禁止 `#` 註解

Claude Code 權限匹配器將 `#` 視為註解截斷命令，導致無法匹配允許規則。

```bash
# ❌ 禁止 — 觸發權限提示
uv run python -c "
# 這是註解
from module import something
print(something)
"

# ✅ 正確 — 無註解
uv run python -c "
from module import something
print(something)
"

# ✅ 正確 — 複雜邏輯寫成 .py 檔案
uv run python scripts/check.py
```

**規則**：多行 `python -c` 中**絕對禁止** `#`。需要註解就寫檔案。

---

## 2. 用 `rg` 取代 `grep`，用 `fd` 取代 `find`

`find -exec` 和 `grep -r` 是 Claude Code 系統硬限制，**無法被任何 allow 規則覆蓋**，每次都需手動批准。

```bash
# ❌ 禁止 — 每次都要手動批准
find . -name "*.py"
grep -r "pattern" .
find . -name "*.py" -exec grep "pattern" {} \;

# ✅ 正確 — auto-allow
fd -e py
rg "pattern"
fd -e py . path/to/search
```

### 快速對照

| 用途 | ❌ 禁止 | ✅ 使用 |
|------|---------|---------|
| 搜尋檔案 | `find . -name "*.py"` | `fd -e py` |
| 搜尋內容 | `grep -r "pattern" .` | `rg "pattern"` |
| 限定副檔名 | `grep -r --include="*.py"` | `rg -t py` |
| 排除目錄 | `grep --exclude-dir=dir` | `rg`（預設遵守 .gitignore） |
| 固定字串 | `grep -rF "exact"` | `rg -F "exact"` |
| 搜尋特定目錄 | `find path -name "*.py"` | `fd -e py . path` |

---

## 3. 所有 Python 命令必須 `uv run`

```bash
# ❌ 禁止
python script.py
python3 script.py
pytest tests/

# ✅ 正確
uv run python script.py
uv run pytest tests/
```

---

## 4. 禁止 `sed` 修改程式碼或文檔

`sed` 不理解程式碼結構，批次替換常造成災難。

```bash
# ❌ 禁止
sed -i 's/old/new/g' script.py
sed -i 's/old/new/g' README.md

# ✅ 正確 — 使用 Edit 工具
# 先 Read → 再 Edit 精確替換
```

---

## 5. 管道命令拆兩步

Claude Code 權限匹配器無法辨識 `|` 管道。

```bash
# ❌ 禁止 — 每次都要手動批准
uv run python script.py | grep "pattern"

# ✅ 正確 — 執行寫檔 → 用 Read/Grep 工具過濾
uv run python script.py > /tmp/output.txt 2>&1
# 然後用 Read 或 rg 讀取 /tmp/output.txt
```

---

## 6. 使用繁體中文 + 英文術語對話

使用者母語是繁體中文，對話和輸出必須使用繁體中文，技術術語保留英文。

```
# ❌ 禁止 — 使用簡體中文
这个模块的功能是什么？
帮我检查一下代码

# ✅ 正確 — 繁體中文 + 英文術語
這個模組的核心職責是什麼？
幫我檢查 code review 的結果
```

**規則**：所有對話、解釋、報告使用繁體中文。專有名詞、術語、程式碼識別符保留英文原樣（API、CLI、CLAUDE.md、doc-decode、filter-tree 等）。

---

## 記憶口訣

> **`#` 是毒藥、`grep`/`find` 是禁區、`uv run` 是王道、`sed` 是地雷、`|` 是陷阱、`簡體字是違規`**

每次寫 Bash 命令前，默念這六條。
