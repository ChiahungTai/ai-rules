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
| `context-management` | 🟢 neutral | context 重置原則（Claude 機制用括號註）|
| `commit-consent` | 🟢 neutral | commit 需用戶確認（場景化，不引用命令名）|
| `llm-output-convention` | 🟢 neutral | print/Logger 雙通道（Python 段標註）|
| `bash-hard-rules` | 🔴 claude-specific | Claude 權限系統（find/grep 硬限、`$`/`#` 偵測）|
| `modern-cli-preference` | 🔴 claude-specific | Claude 權限（fd/rg vs find/grep）|
| `lsp-navigation` | 🔴 claude-specific | Claude 原生 LSP 工具 |
| `code-edit-constraints` | 🔴 claude-specific | Claude Edit 工具 |
| `context7` | 🟢 neutral | MCP 標準（三家支援；Context7 跨 harness 文檔查詢）|
| `model-routing` | 🔴 claude-specific | Claude subagent 模型階層 |

**default bundle**：auto-discover 所有 `harness-scope: neutral` rule（目前 14 條）。新增 neutral rule → 加 frontmatter `harness-scope: neutral` → 下次 deploy 自動納入（**不需改 script**）。`--scope` 可手動指定其他 scope 組合（進階）。

## Rule 寫作原則

- **可驗證**：rule 必須含可機械檢查的標準（沒有驗證的規則是噪音）
- **signal 導向**：保留從程式碼猜不到的知識（設計理由、失敗教訓），移除可推導內容
- **harness-scope 自描述**：每條 rule 的 scope（neutral/claude-specific）標在上表，新 rule 需歸類

## Neutral rule 中性化規範

> **適用**：`harness-scope: neutral` 的 rule。這類 rule 會被 `deploy_agents.py` 打包進 bundle，部署到 ZCode / OpenCode / Codex 三家非 Claude harness。寫作時必須假設讀者**不是 Claude** — 不會展開 `@`、不能用 slash command、沒有 `~/.claude/rules/`、沒有 `CLAUDE.md wrapper`。

### 禁止（非 Claude 讀者會斷裂）

| ❌ 禁止 | ✅ 改成 |
|---|---|
| 裸 slash command `/build` `/commit` `/execution-plan` | 流程名 `build` / `commit` / `execution-plan`（無 slash）；Claude 端原文放 `(Claude: /build)` 括號註 |
| `@~/...` 或 `@/path` transclusion | 一般 markdown link；`@` 僅在描述 Claude 機制時用，並標明「Claude 端」 |
| `../commands/xxx.md` `../skills/xxx/SKILL.md` 跨域 ref | 描述該 command/skill 名稱 + `(Claude: commands/xxx.md)` 括號註；或泛化為「跨 harness 機制，路徑從略」 |
| 未標註的 `CLAUDE.md wrapper` | 「Claude 端 CLAUDE.md wrapper」或「instruction 檔（AGENTS.md source；Claude 端 CLAUDE.md wrapper）」 |
| `~/Github/ai-rules/rules/xxx.md` user-specific 絕對路徑 | repo-relative markdown link `[xxx.md](xxx.md)`（同目錄）或 `xxx.md`（純名 + 「source 在 ai-rules repo」） |
| 「Claude 端 `~/.claude/rules/` symlink auto-load」作為主要描述 | 標準載入機制註記（見下方）|

### 標準載入機制註記

多條 neutral rule 共用這句（直接複製）：

```
> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）
```

### 通用模式：括號註隔離 Claude 機制

當內容原則通用、但需提及 Claude 端具體機制時，用 `(Claude: ...)` 括號註隔離：

```markdown
# ✅ 正確：原則為主，Claude 機制括號註
- **任務切換時重置 context**（Claude: `/clear`）
- **commit 需用戶確認**（完整流程見 commit 命令文檔；Claude: `commands/commit.md`）

# ❌ 錯誤：Claude 機制作為主要指令
- **任務切換用 `/clear`**
- **完整流程見 `../commands/commit.md`**
```

括號註**不是殘留** — 它是策略：讓 Claude 讀者讀到完整的 Claude 機制資訊，同時讓非 Claude 讀者知道「這是 Claude 特例，我有對應機制即可」。

### 機械檢查清單（review 用）

新增/修改 neutral rule 後，以下 grep 應無命中（括號註內除外）：

```bash
# 裸 slash command（應只在 (Claude: ...) 內）
rg '`/[a-z][a-z-]+[ `]' rules/*.md | rg -v 'Claude[:：]'

# @ transclusion
rg '@~/|@\.\./|@/[a-z]' rules/*.md

# 跨域相對路徑
rg '\.\./(commands|skills)/' rules/*.md

# 未標註的 CLAUDE.md wrapper
rg 'CLAUDE.md wrapper' rules/*.md | rg -v 'Claude 端'

# user-specific 絕對路徑
rg '~/Github/ai-rules/' rules/*.md
```
