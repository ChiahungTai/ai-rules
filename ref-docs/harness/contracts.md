# Harness 契約對照

各 harness（Claude Code / OpenCode / ZCode）的契約維度對照，**萃取自本地鏡像**（`claude-code/`、`opencode/`、`zcode/`，見 [`manifest.json`](manifest.json) 的 `generated_at` 為新鮮度基準）。

> 過時以原站為準；每格附鏡像內的 `檔:行` 佐證以便查證。「（鏡像未提及）」= 該維度在所讀頁面沒寫，非保證不存在（可能在未鏡像的頁面）。

## 對照表

| 維度 | Claude Code | OpenCode | ZCode |
|------|-------------|----------|-------|
| **專案/全域指令檔** | 專案 `./CLAUDE.md` 或 `./.claude/CLAUDE.md`；全域 `~/.claude/CLAUDE.md`；規則目錄 `.claude/rules/*.md`（記憶體 `memory.md:60,127,171`） | **主推 `AGENTS.md`**；`CLAUDE.md` 為 fallback（可用 env var 關）；全域 `~/.config/opencode/AGENTS.md`（`rules.md:1,64,84`） | **讀 `AGENTS.md`**（全域 `~/.zcode/AGENTS.md` + workspace）；**不讀 CLAUDE.md**（僅 onboarding 一次性遷移成 AGENTS.md）（`agents.md:46-55`） |
| **Skill** | `SKILL.md`（遵循 [Agent Skills](https://agentskills.io) 開放標準）；frontmatter 最豐富（`name`/`description`/`when_to_use`/`allowed-tools`/`context:fork`/`paths`…）；目錄 `~/.claude/skills/`、`.claude/skills/`（`skills.md:19,103,227`） | `SKILL.md`；只識別 5 欄（`name`/`description`/`license`/`compatibility`/`metadata`），未知欄忽略；掃 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`、`~/.claude/skills/` 等（`skills.md:9,31`） | `SKILL.md`（範例僅 `name`+`description`）；`~/.zcode/skills/<name>/`；**可從 Claude Code/Codex/Augment/Windsurf 一鍵匯入**（單向導入）（`skill.md:39,51`） |
| **Subagent / Agent** | `~/.claude/agents/`、`.claude/agents/`（`settings.md:66`；格式在 `sub-agents.md`） | markdown + frontmatter（`mode`/`model`/`tools`/`temperature`…）於 `~/.config/opencode/agents/`、`.opencode/agents/`，或 `opencode.json` 的 `agent` 區塊（`agents.md:139,185`） | `~/.zcode/agents/<name>.md`；**僅用戶級（Beta）**，不支援工作區級子智能體（`subagents.md:65,67`） |
| **Slash command** | markdown 檔，**已合併入 skills**（同名 skill 優先）；`.claude/commands/<name>.md`（`skills.md:14`、`commands.md:11`） | markdown + frontmatter（`description`/`agent`/`model`/`subtask`）；`~/.config/opencode/commands/`、`.opencode/commands/`；支援 `$ARGUMENTS`/`@file`（`commands.md:17,77`） | `.md` 檔；`~/.zcode/commands/`（用戶級，工作區級在專案目錄下）；可從外部 Agent 匯入；內建 `/goal`、`/compact`（`commands.md:36,42`） |
| **Hook** | `settings.json` 的 `hooks` key；事件 PreToolUse/PostToolUse/Stop/SessionStart/…；handler `command`/`http`/`mcp_tool`/`prompt`/`agent`（`hooks.md:33,71,302`） | （鏡像未提及） | （鏡像未提及） |
| **MCP** | `.mcp.json`（project）；`~/.claude.json`（user/local）；`{"mcpServers":{}}`；stdio/http/sse/ws（`mcp.md:299,349`） | `opencode.json` 的 `mcp` 欄位（`config.md:520`） | `~/.zcode/cli/config.json`（鍵 `mcp.servers`）；workspace `<root>/.zcode/config.json`；**相容 `.agents/mcp.json`**（鍵 `mcpServers`）；可從 Claude/Codex/OpenCode 匯入（`mcp-services.md:46,61`） |
| **主設定檔** | `settings.json`（user `~/.claude/`、project `.claude/`、local、managed）；雜組態在 `~/.claude.json`（`settings.md:80,119`） | `opencode.json`（JSON/JSONC）；六層載入優先序（遠端 < 全域 < `OPENCODE_CONFIG` < 專案 < `.opencode/` < `OPENCODE_CONFIG_CONTENT`）（`config.md:7,40`） | `config.json`：用戶 `~/.zcode/cli/config.json`、workspace `<root>/.zcode/config.json`（`mcp-services.md:59`） |

## 開放標準相容性（跨 harness 關鍵）

- **`AGENTS.md` = 跨 harness 最大公約數**：OpenCode 主推、ZCode 主推、Claude Code 可用 `@AGENTS.md` import 或 `/init` 整合（不原生讀）（`memory.md:127,145`）。
- **`CLAUDE.md` 三家分歧**：Claude 原生讀；OpenCode 作 fallback 讀；**ZCode 不讀**（僅 onboarding 一次性遷移）（`agents.md:49`）。
- **`.agents/` 開放標準**：OpenCode（`.agents/skills/`、`~/.agents/skills/`）與 ZCode（`.agents/mcp.json`）皆當相容路徑掃；Claude 鏡像未提及（`opencode/skills.md:13`、`zcode/mcp-services.md:64`）。
- **`SKILL.md` 三家一致**（同 Agent Skills 標準），frontmatter 豐富度差異大：Claude 最豐、OpenCode 最精簡（5 欄）、ZCode 範例 2 欄。
- **Hook 是 Claude 獨有特徵**（鏡像內 OpenCode/ZCode 相關頁未提及 hook）。

## 對 ai-rules 的啟示

ai-rules 現為 CLAUDE.md 體系。要真正跨 harness，最小可攜單位是 **`AGENTS.md`**（兩家原生讀、第三家可 import）；`SKILL.md` 內容格式可攜但**語意不可攜**（ai-rules 的 skills 深度綁 `/build`、`/commit`、`.kanban/` 等 Claude 工作流）。Hook 則是 Claude 專屬能力，跨 harness 無對等物——以 hook 強制的行為在其他 harness 需改寫成 rule/skill 層的提醒。
