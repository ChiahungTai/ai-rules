---
harness-scope: neutral
---

# 工具紀律

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

> 違反 = 閘門失效或工具誤用。每次都遵守。

## 工具選擇原則

- 語義查詢用 LSP（goToDefinition / findReferences / hover），文字搜尋用 `rg`，檔案搜尋用 `fd`（決策樹見 [lsp-navigation.md](lsp-navigation.md)）
- **Agent prompt 必須指定工具**：spawn agent 時，根據任務性質在 prompt 中明確寫「用 LSP hover/ goToDefinition 查簽名」或「用 rg 搜文字」。禁止 agent prompt 只寫「讀取/驗證」不指定工具

## Python 命令執行

- 所有 Python 命令用 `uv run` 前綴（`uv run python script.py`、`uv run pytest`）
- 禁止：`python`、`python3`、`PYTHONPATH=$PWD`

## 檔案修改禁令

- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`（sed 不理解程式碼或 Markdown 語法，批次替換常破壞縮排、誤改字串/註解、毀損多行結構）
- sed 唯一允許用途：過濾日誌輸出、處理純文字資料流（不修改原始檔）

## pytest 背景跑

- `pytest` 用背景跑（不阻塞對話；Claude: `run_in_background: true`；其他 harness 用各家背景機制）

## 閘門命令禁 pipe 到 tail/grep

> **核心原則**：exit code 是閘門依據，pipe 會被最後一環蓋掉。

`uv run mypy . 2>&1 | tail -15` 回報的是 `tail` 的 exit 0，不是 mypy 的 7 errors → 誤判「全綠」。

- 需看 output 用重導檔案再 Read（`uv run mypy . > /tmp/mypy.log` 再 Read）
- 或 `set -o pipefail` 讓 pipe exit = 最後一個非 0 退出碼

## 輸出慣例

- 輸出使用繁體中文 + 英文術語
