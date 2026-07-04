---
harness-scope: claude-specific
---

# Bash 硬限制

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

> 違反 = 權限提示卡關。每次都遵守。

- 語義查詢用 LSP（goToDefinition / findReferences / hover），文字搜尋用 `rg`，檔案搜尋用 `fd`
- **Agent prompt 必須指定工具**：spawn agent 時，根據任務性質在 prompt 中明確寫「用 LSP hover/ goToDefinition 查簽名」或「用 rg 搜文字」。禁止 agent prompt 只寫「讀取/驗證」不指定工具
- `python -c` 禁止寫註解 — AI 自用驗證、不需給人看；多行換行後 `#` 會觸發權限提示（CLI 無法判斷跨行註解是否被注入惡意內容）
- 所有 Python 命令用 `uv run` 前綴
- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`
- 禁止 `$VAR`、`$(cmd)` 等 shell 展開（觸發 simple_expansion / command_subshell / subshell 偵測）。需要變數時用具體值或寫 `.py` 檔案
- `pytest` 用背景跑（`run_in_background: true`），不要阻塞對話
- 輸出使用繁體中文 + 英文術語
- **lint/test 閘門命令禁止 pipe 到 tail/grep**：exit code 是閘門依據，pipe 會被最後一環蓋掉。`uv run mypy . 2>&1 | tail -15` 回報的是 `tail` 的 exit 0，不是 mypy 的 7 errors → 誤判「全綠」。需看 output 用重導檔案再 Read（`uv run mypy . > /tmp/mypy.log` 再 Read），或 `set -o pipefail` 讓 pipe exit = 最後一個非 0 退出碼

口訣：`#` 是毒藥、`$` 是禁區、語義用 LSP 文字用 `rg`/`fd`、**agent prompt 寫工具**、`uv run` 是王道、`sed` 是地雷、`pytest` 跑背景、**閘門命令不 pipe**、繁體中文
