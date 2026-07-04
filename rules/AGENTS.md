---
harness-scope: meta
---

# Rules 層指令

rules/ 是 ai-rules 的行為規範庫。Claude 端經 `~/.claude/rules/` symlink auto-load 全載每個 session；非 Claude 端（ZCode/OpenCode/Codex）靠 generator（`scripts/deploy_agents.py`）打包 neutral subset 進各自的 AGENTS.md。

## 部署紀律（編輯 rule 時自動生效）

**規則**：編輯此目錄任一 rule 後，執行：

```bash
uv run python scripts/deploy_agents.py
```

→ 重新 bundle guide + neutral rules → 部署到 `~/.{zcode,config/opencode,codex}/AGENTS.md`（非 Claude 端）。
→ Claude 端**不需** redeploy（rules/ 經 `~/.claude/rules/` auto-load 即時生效）。
→ 注意：deploy 會將非 Claude 端的 AGENTS.md 從 symlink（live-sync）轉為 generated file（snapshot）— 改 rule 後需重跑 generator 才同步。

## harness-scope 分類

frontmatter `harness-scope:` 是**單一真相源**（每條 rule 自帶）。`deploy_agents.py` 掃 frontmatter auto-discover — 新增 rule 只需加 frontmatter、**不需改 script**。下表是 derived overview：

| rule | scope | 說明 |
|---|---|---|
| `deep-thinking` | 🟢 neutral | 決策框架（第一性原理＋第二層）|
| `progressive-validation` | 🟢 neutral | DEPTH-MIN/SAMPLE/FULL 驗證 |
| `quality-constraints` | 🟢 neutral | crash-only / fail-loud / 消費端驗證 |
| `acceptance-evidence` | 🟢 neutral | L1-L6 證據階層 / A/B 軸 |
| `must-execute-before-complete` | 🟢 neutral | 改了要跑、非靜態檢查 |
| `collaboration-constraints` | 🟢 neutral | anti-sycophancy / 事實查證 |
| `self-consistency` | 🟢 neutral | 文檔自洽檢查 |
| `_ai-behavior-constraints` | 🟢 neutral | instruction file 禁元資訊 |
| `instruction-writing` | 🟢 neutral | 雙檔模型 meta-rule（large 但仍打包）|
| `python-standards` | 🟢 neutral | Python 標準（language；Python 專案適用）|
| `context-management` | 🟡 borderline | 原則通用、`/clear` 是 Claude 機制（需輕適配）|
| `commit-consent` | 🟡 borderline | 原則通用、`/commit` 是 Claude 命令 |
| `llm-output-convention` | 🟡 borderline | print/Logger 通用、Python/Claude flavor |
| `bash-hard-rules` | 🔴 claude-specific | Claude 權限系統（find/grep 硬限、`$`/`#` 偵測）|
| `modern-cli-preference` | 🔴 claude-specific | Claude 權限（fd/rg vs find/grep）|
| `lsp-navigation` | 🔴 claude-specific | Claude 原生 LSP 工具 |
| `code-edit-constraints` | 🔴 claude-specific | Claude Edit 工具 |
| `context7` | 🟢 neutral | MCP 標準（三家支援；Context7 跨 harness 文檔查詢）|
| `model-routing` | 🔴 claude-specific | Claude subagent 模型階層 |

**default bundle**：auto-discover 所有 `harness-scope: neutral` rule（目前 10 條，~24K tokens, ~2.4% of 1M）。新增 neutral rule → 加 frontmatter `harness-scope: neutral` → 下次 deploy 自動納入（**不需改 script**）。加 borderline 用 `--scope neutral,borderline`（~28K tokens）。

## Rule 寫作原則

- **可驗證**：rule 必須含可機械檢查的標準（沒有驗證的規則是噪音）
- **signal 導向**：保留從程式碼猜不到的知識（設計理由、失敗教訓），移除可推導內容
- **harness-scope 自描述**：每條 rule 的 scope（neutral/borderline/claude-specific）標在上表，新 rule 需歸類
