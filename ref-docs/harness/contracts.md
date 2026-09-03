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
| **Hook** | `settings.json` 的 `hooks` key；事件 PreToolUse/PostToolUse/Stop/SessionStart/…；handler `command`/`http`/`mcp_tool`/`prompt`/`agent`（`hooks.md:33,71,302`） | （鏡像未提及） | user-level config hooks 3.7.7+ 實測可用（7 事件子集、無 Notification/SessionEnd、專案層被忽略；`zcode/cn/docs/hooks.md`；詳 04 報告 §7 修訂） |
| **MCP** | `.mcp.json`（project）；`~/.claude.json`（user/local）；`{"mcpServers":{}}`；stdio/http/sse/ws（`mcp.md:299,349`） | `opencode.json` 的 `mcp` 欄位（`config.md:520`） | `~/.zcode/cli/config.json`（鍵 `mcp.servers`）；workspace `<root>/.zcode/config.json`；**相容 `.agents/mcp.json`**（鍵 `mcpServers`）；可從 Claude/Codex/OpenCode 匯入（`mcp-services.md:46,61`） |
| **主設定檔** | `settings.json`（user `~/.claude/`、project `.claude/`、local、managed）；雜組態在 `~/.claude.json`（`settings.md:80,119`） | `opencode.json`（JSON/JSONC）；六層載入優先序（遠端 < 全域 < `OPENCODE_CONFIG` < 專案 < `.opencode/` < `OPENCODE_CONFIG_CONTENT`）（`config.md:7,40`） | `config.json`：用戶 `~/.zcode/cli/config.json`、workspace `<root>/.zcode/config.json`（`mcp-services.md:59`） |

## 開放標準相容性（跨 harness 關鍵）

- **`AGENTS.md` = 跨 harness 最大公約數**：OpenCode 主推、ZCode 主推、Claude Code 可用 `@AGENTS.md` import 或 `/init` 整合（不原生讀）（`memory.md:127,145`）。
- **`CLAUDE.md` 三家分歧**：Claude 原生讀；OpenCode 作 fallback 讀；**ZCode 不讀**（僅 onboarding 一次性遷移）（`agents.md:49`）。
- **`.agents/` 開放標準**：OpenCode（`.agents/skills/`、`~/.agents/skills/`）與 ZCode（`.agents/mcp.json`）皆當相容路徑掃；Claude 鏡像未提及（`opencode/skills.md:13`、`zcode/mcp-services.md:64`）。
- **`SKILL.md` 三家一致**（同 Agent Skills 標準），frontmatter 豐富度差異大：Claude 最豐、OpenCode 最精簡（5 欄）、ZCode 範例 2 欄。
- **Hook**：Claude 有；ZCode 3.7.7+ 實測支援 user-level hooks（`~/.zcode/cli/config.json`，stdin 含 Claude snake_case alias，腳本零改動可攜；專案層 hooks 被整體忽略、事件無 Notification/SessionEnd）；OpenCode 鏡像內未提及 hook（佐證：zcode.z.ai/cn/docs/hooks；實測紀錄 [04-multi-harness機制對照 §7 修訂](../../ai-analysis/reports/superpowers/04-multi-harness機制對照.md)）。
- **Subagent 定義同構**：兩家皆 markdown + YAML frontmatter（`name`/`description` 必填，正文 = 系統提示詞）；user 目錄載入點 `~/.claude/agents/`、`~/.zcode/agents/` 皆為目錄掃描 → symlink 部署可行。ZCode 為 Beta：僅 user 級、不可巢狀派發、自訂 tools 清單排除 MCP 工具（Claude 支援 `mcp__` patterns）、未知 frontmatter 欄位靜默忽略。

## 功能對照（2026-08-14 實查：線上文檔 + 本 session 實測）

> 擴充機制面（ai-rules 消費的那一層）幾乎都有對應物；深度與事件/欄位覆蓋多為 Claude 子集。

| 能力 | Claude Code | ZCode | 對等度 |
|------|------------|-------|--------|
| Instructions | CLAUDE.md layers | AGENTS.md 原生（subagent 亦注入，v3.7.1+） | ✅ |
| Skills / Commands | SKILL.md / `.claude/commands` | 同格式 + `.agents/` 相容路徑 | ✅ |
| Hooks | 完整事件 + 5 種 type | 3.7.7 user-level 可用；7 事件子集、process/command 兩 type、專案層被忽略（實測：`zcode/cn/docs/hooks.md` + 04 報告 §7 修訂） | ⚠️ 子集 |
| Subagents | 巢狀、豐富 frontmatter（skills/hooks/memory/isolation） | Beta user 級；不可巢狀、frontmatter 精簡、未知欄位靜默忽略（`zcode/cn/docs/subagents.md`） | ⚠️ 子集 |
| MCP | 完整 + inline 定義 | 完整；subagent 自訂 tools 清單會殺 MCP 工具（須手寫全名，萬用無效） | ✅（有陷阱） |
| Plugins | marketplace | `.zcode-plugin` manifest，相容 Claude plugin（Browser Use 即官方 plugin，`zcode/cn/docs/browser-use.md`） | ✅ |
| Memory | CLAUDE.md + auto-memory + agent memory | Memory 功能 v3.6.4+（預設關、自動提取、專案隔離、`~/.zcode/cli/memories/`，`zcode/cn/docs/memory.md`） | ✅ |
| 排程 | cron / scheduled tasks | Automations 定時任務（重複規則、綁會話投遞、上限 20、僅本地，`zcode/cn/docs/automations.md`） | ✅ |
| 瀏覽器自動化 | Playwright MCP | 內建瀏覽器面板 + 官方 Browser Use plugin（防網頁注入指令、Chrome 登入態導入） | ✅ 各有千秋 |
| 背景執行 | v2.1.198+ 預設背景 + background agents | 背景 subagent（spawn 端 `run_in_background`，runtime 實測）+ 閒時任務 | ✅ |
| 權限 | 宣告式 glob 白名單 + 多模式 | 4 檔 GUI 模式 + SQLite 精確匹配記憶（04 報告 §7） | ⚠️ 無宣告式白名單 |
| LSP | 原生 plugin set | 無原生 → 自建 MCP 替代（lsp-navigation「跨 harness LSP 載體對照」） | ❌ workaround |

**Claude 有、ZCode 無**：巢狀 subagent、agent teams、`/fork`、headless `-p`/Agent SDK（CI 自動化）、宣告式權限 glob、原生 LSP、hook 的 prompt/agent/http/mcp_tool type、subagent per-agent hooks/skills/memory/isolation、設定熱載入（ZCode 全靠 per-session 快照）。

**ZCode 有、Claude 無**：Repo Wiki（自動架構指南、宣稱帶 source location、隨 code 自動刷新、存 `~/.zcode/v2/repo-wiki/` 不進 repo，`zcode/cn/docs/repo-wiki.md`）、閒時任務（算力富餘免費執行）、飛書/微信 Bot Channel、內建瀏覽器 UI（element 選成 context）。

## Auto-memory 載入截斷（2026-09-03 雙端源碼反組譯，CLI 三版同構）

兩家同語義：**200 行 或 25,000 字元（UTF-16 code units，CJK 一字計 1）先到者截**——截斷處附 WARNING（易忽略）、尾端條目不進 context；注入路徑不剝 frontmatter（K9r 讀碼：`Wut()` 直收 `indexContent` 全文，行數含 frontmatter 行）。

| | 行數限 | 大小限 | 證據 |
|---|---|---|---|
| ZCode | 200（`Vut`） | 25,000 字元（`mre=25e3`——`Wut()` 以 `t.length` 比較） | `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs` |
| Claude Code | 200（`YD`） | 25,000 字元（`GF=25000`——`mLe()` 回傳 `byteCount:t.length`：**欄位名叫 byteCount、計量是 `.length`＝字元**；TextEncoder 在另一 scope 屬 crypto，勿誤讀） | `~/.local/share/claude/versions/<v>` |

「25KB」＝兩端警告把 25,000 字元 ÷1024 顯示成 "24.4KB" 的**假象**——全鏈無 bytes 量測。重跑驗證（量詞須彈性——常數前綴不足 100 字元，`.{100}` 會 0 hits）：

```bash
rg -a -o '.{30}mre=[0-9*]+.{30}' /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs
rg -a -o '.{0,100}YD=200,GF=25000.{0,60}' ~/.local/share/claude/versions/$(ls -t ~/.local/share/claude/versions/ | head -1)
```

治理配套（ai-rules 端）：generator 硬 gate chars 22,500（真線 90%）／lines 190＋bytes 24,000 info 預警——單一源在 `skills/memory-audit/scripts/generate_index.py` 註解。


## 對 ai-rules 的啟示

ai-rules 現為 CLAUDE.md 體系。要真正跨 harness，最小可攜單位是 **`AGENTS.md`**（兩家原生讀、第三家可 import）；`SKILL.md` 內容格式可攜但**語意不可攜**（ai-rules 的 skills 深度綁 `/build`、`/commit`、`.kanban/` 等 Claude 工作流）。Hook 在 ZCode 3.7.7+ 已有對等物（user-level config hooks，stdin 相容 Claude snake_case）——腳本可跨 harness 共用，僅註冊 config per-harness（且無目錄載入點，不能用 symlink 部署）；OpenCode 走 plugin lifecycle 對應（`tool.execute.before` ≈ CC `PreToolUse`，需改寫 JS/TS plugin，見 [03-OpenCode退路.md](../../ai-analysis/reports/superpowers/03-OpenCode退路.md)）。
