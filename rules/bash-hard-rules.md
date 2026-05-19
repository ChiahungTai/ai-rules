# Bash 硬限制

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

> 違反 = 權限提示卡關。每次都遵守。

- `fd` 取代 `find`，`rg` 取代 `grep`
- 多行 `python -c` 禁止 `#` 註解
- 所有 Python 命令用 `uv run` 前綴
- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`
- 管道 `|` 改拆兩步（寫檔 → Read/rg 讀取）
- 輸出使用繁體中文 + 英文術語

口訣：`#` 是毒藥、`rg`/`fd` 取代 `grep`/`find`、`uv run` 是王道、`sed` 是地雷、管道拆兩步、繁體中文
