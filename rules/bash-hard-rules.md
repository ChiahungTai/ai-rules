---
harness-scope: claude-specific
---

# Bash 硬限制（Claude）

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

> Claude Code 專屬的 Bash 權限偵測限制。通用工具紀律（uv run / pipe-exit / 禁 sed / pytest 背景跑 / agent prompt 指定工具）見 [tool-discipline.md](tool-discipline.md)（neutral）。

## Claude 權限偵測限制

> 違反 = 權限提示卡關。每次都遵守。

- `python -c` 禁止寫註解 — AI 自用驗證、不需給人看；多行換行後 `#` 會觸發權限提示（CLI 無法判斷跨行註解是否被注入惡意內容）
- 禁止 `$VAR`、`$(cmd)` 等 shell 展開（觸發 simple_expansion / command_subshell / subshell 偵測）。需要變數時用具體值或寫 `.py` 檔案

口訣：`#` 是毒藥、`$` 是禁區、需要變數就寫 `.py`。

## 例外與降級

- 需要變數展開或跨行註解 → 寫成 `.py` 檔再 `uv run`
- 純驗證想法用乾淨單行 `python -c "..."`（無 `#`）
