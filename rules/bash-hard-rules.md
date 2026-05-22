# Bash 硬限制

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

> 違反 = 權限提示卡關。每次都遵守。

- `fd` 取代 `find`，`rg` 取代 `grep`
- 多行 `python -c` 中換行後禁止 `#` 註解（newline + `#` 觸發權限提示）
- 所有 Python 命令用 `uv run` 前綴
- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`
- 禁止 `$VAR`、`$(cmd)` 等 shell 展開（觸發 simple_expansion / command_subshell / subshell 偵測）。需要變數時用具體值或寫 `.py` 檔案
- `pytest` 用背景跑（`run_in_background: true`），不要阻塞對話
- 輸出使用繁體中文 + 英文術語

口訣：`#` 是毒藥、`$` 是禁區、`rg`/`fd` 取代 `grep`/`find`、`uv run` 是王道、`sed` 是地雷、`pytest` 跑背景、繁體中文
