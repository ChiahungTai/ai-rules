# Bash 硬限制

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

> 違反 = 權限提示卡關。每次都遵守。

- 語義查詢用 LSP（goToDefinition / findReferences / hover），文字搜尋用 `rg`，檔案搜尋用 `fd`
- **Agent prompt 必須指定工具**：spawn agent 時，根據任務性質在 prompt 中明確寫「用 LSP hover/ goToDefinition 查簽名」或「用 rg 搜文字」。禁止 agent prompt 只寫「讀取/驗證」不指定工具
- `python -c` 禁止寫註解 — AI 自用驗證、不需給人看；多行換行後 `#` 會觸發權限提示（CLI 無法判斷跨行註解是否被注入惡意內容）
- 所有 Python 命令用 `uv run` 前綴
- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`
- 禁止 `$VAR`、`$(cmd)` 等 shell 展開（觸發 simple_expansion / command_subshell / subshell 偵測）。需要變數時用具體值或寫 `.py` 檔案
- `pytest` 用背景跑（`run_in_background: true`），不要阻塞對話
- 輸出使用繁體中文 + 英文術語

口訣：`#` 是毒藥、`$` 是禁區、語義用 LSP 文字用 `rg`/`fd`、**agent prompt 寫工具**、`uv run` 是王道、`sed` 是地雷、`pytest` 跑背景、繁體中文
