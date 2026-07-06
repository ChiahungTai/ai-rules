---
harness-scope: meta
---

# Rules 層指令

rules/ 是 ai-rules 的行為規範庫。**Claude 與非 Claude 的 rules 載入架構不同**（成因：rules auto-load 是 Claude 獨有功能，非 Claude 沒有）：

- **Claude 端**（雙路徑）：`~/.claude/CLAUDE.md` 是檔案 symlink → `ai-development-guide.md`（guide）；`~/.claude/rules/` 是**目錄 symlink** → `rules/`（rules auto-load，每 session 全載）。repo 改 → 即時生效，**不需 deploy**。
- **非 Claude 端**（ZCode/OpenCode/Codex，單檔）：無 rules auto-load 機制 → 靠 `scripts/deploy_agents.py` 把 **guide + neutral rules 拼裝成單一 AGENTS.md**（snapshot），部署到 `~/.{zcode,config/opencode,codex}/AGENTS.md`。改 rule 後須重跑 deploy 才同步。

## 部署紀律（編輯 rule 時自動生效）

**規則**：編輯此目錄任一 rule 後，執行：

```bash
uv run python scripts/deploy_agents.py
```

→ 重新 bundle guide + neutral rules → 部署到 `~/.{zcode,config/opencode,codex}/AGENTS.md`（非 Claude 端的 rules 唯一來源）。
→ Claude 端不需 deploy（`~/.claude/rules/` 目錄 symlink 即時同步）。
→ 注意：deploy 會將非 Claude 端的 AGENTS.md 從 symlink（live-sync）轉為 generated snapshot — 改 rule 後需重跑 generator 才同步。

### 部署驗證義務（deploy 跑通 ≠ 部署完成）

deploy exit 0 只證明「bundle 生成成功 + 0 斷 ref」，**不證明「各端讀到正確內容」**。改動 rule（尤其 reclassify scope / 拆雙檔 / 新增 rule）後必須獨立驗證**每一端**（架構不同 → 驗證方式不同）：

- **非 Claude 端**（rules 唯一來源是 bundle）：`rg` 抽查 deployed AGENTS.md（如 `~/.zcode/AGENTS.md`）含新/改 rule 的 section marker + 關鍵內容；排除應排除的 claude-specific rule。**漏驗這端 = 非 Claude LLM 讀不到該 rule**（無其他載入途徑）。
- **Claude 端**（rules 來源是 `~/.claude/rules/` dir symlink）：`rg` 抽查 `~/.claude/rules/<rule>.md`（透過 symlink 讀 repo）含完整內容 — 瘦身後的 claude-specific rule 仍保留 Claude 專屬段。
- **多端一致性**：`shasum` 比 deployed 三檔 hash 相同（idempotent）；改 deploy script 後比 pre/post hash 相同（簽名改不影響 bundle）。

禁止：只看 deploy stdout 的 `[OK]` 就宣稱部署完成；只驗單端就推論其他端正常。

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
| `lsp-navigation` | 🟢 neutral | 符號導航決策樹 + 跨 harness LSP 載體對照 |
| `modern-cli-preference` | 🟢 neutral | fd/rg CLI 速查（Claude 權限段括號註隔離）|
| `tool-discipline` | 🟢 neutral | 通用工具紀律（uv run / pipe-exit / 禁 sed / pytest 背景跑）|
| `edit-discipline` | 🟢 neutral | 通用編輯紀律（SRP/DIP/變更紀律/禁混合寫法）|
| `bash-hard-rules` | 🔴 claude-specific | Claude 權限偵測（`#` 換行註解 / `$` 展開）|
| `code-edit-constraints` | 🔴 claude-specific | Claude Edit/Write 工具 API（old_string 精確匹配 / 多位元組降級）|
| `context7` | 🟢 neutral | MCP 標準（三家支援；Context7 跨 harness 文檔查詢）|
| `model-routing` | 🔴 claude-specific | Claude subagent 模型階層 |

**default = neutral**：通用知識預設跨 harness — 新 rule 不標 scope 即進 bundle。Claude 專屬 rule 需顯式標 `harness-scope: claude-specific` 才被排除。`deploy_agents.py` 的斷 ref 檢測會阻塞任何 neutral rule 引用 claude-specific rule 的 deploy（強制修 ref 或重劃 scope）。目前 neutral 18 條、claude-specific 3 條（bash-hard-rules / code-edit-constraints / model-routing）。

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

### 通用模式：跨 harness 載體對照（當工具呼叫方式跨 harness 不同時）

當一個概念跨 harness 通用、但呼叫載體不同時（典型：LSP），用**對照表**表達，而非把某家 harness 的呼叫語法寫成主體。範例見 `lsp-navigation.md`「跨 harness LSP 載體對照」段。模式：

```markdown
### 跨 harness X 載體對照

| harness | 機制 | 呼叫方式 |
|---------|------|---------|
| Claude | ... | ... |
| ZCode | ... | ... |
| OpenCode | ... | ... |
```

判準：一個概念跨 harness 通用、但「怎麼呼叫」各家不同 → 用對照表；若概念本身某家沒有（如 hooks），那不是載體差異而是 scope 差異 → 整段放 claude-specific rule 或括號註。

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
