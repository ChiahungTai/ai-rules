# Codex 鏡像提取（七軸）

> 提取者：spec-miner agent（2026-09-12）；鏡像根：`/Users/ctai/Github/ai-rules/ref-docs/harness/codex/`（下文錨點均相對此根；種子檔存在性已自驗）

## 軸 1 Instruction 檔（AGENTS.md）

- claim：Codex 在每次 run 啟動時建構 instruction chain（TUI 為每個 launched session 一次），非即時熱載。
  - `agent-configuration/agents-md.md:9` 「Codex builds an instruction chain when it starts (once per run; in the TUI this usually means once per launched session). Discovery follows this precedence order:」
  - `agent-configuration/agents-md.md:206` 「Codex rebuilds the instruction chain on every run (and at the start of each TUI session), so there is no cache to clear manually.」
- claim：三層 precedence——global（`~/.codex/`）→ project（自 repo root 走到 cwd）→ merge；global 層 `AGENTS.override.md` 優先於 `AGENTS.md`，且每層只取第一個非空檔。
  - `agent-configuration/agents-md.md:11` 「**Global scope:** In your Codex home directory (defaults to `~/.codex`, unless you set `CODEX_HOME`), Codex reads `AGENTS.override.md` if it exists. Otherwise, Codex reads `AGENTS.md`. Codex uses only the first non-empty file at this level.」
- claim：project 層是 walk-down 語義——從 project root 往下走到 cwd，路徑上每個目錄檢查 `AGENTS.override.md` → `AGENTS.md` → fallback 名單，每目錄至多收一檔。
  - `agent-configuration/agents-md.md:12` 「Starting at the project root (typically the Git root), Codex walks down to your current working directory. If Codex cannot find a project root, it only checks the current directory. In each directory along the path, it checks for `AGENTS.override.md`, then `AGENTS.md`, then any fallback names in `project_doc_fallback_filenames`. Codex includes at most one file per directory.」
- claim：merge 語義＝root 向下串接（concatenate）而非覆蓋；「覆蓋」效果來自後出現者排序在前端 prompt 較後位置。
  - `agent-configuration/agents-md.md:13` 「**Merge order:** Codex concatenates files from the root down, joining them with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt.」
- claim：尺寸限制＝`project_doc_max_bytes` 預設 32 KiB（總量）；空檔跳過；同層 fallback 檢查順序可自訂。
  - `agent-configuration/agents-md.md:15` 「Codex skips empty files and stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default).」
  - `agent-configuration/agents-md.md:159` 「Now Codex checks each directory in this order: `AGENTS.override.md`, `AGENTS.md`, `TEAM_GUIDE.md`, `.agents.md`. Filenames not on this list are ignored for instruction discovery.」
  - `config-file/config-reference.md:1170` 「Maximum bytes read from `AGENTS.md` when building project instructions.」
- claim：project root 判定預設＝含 `.git` 的目錄，可用 `project_root_markers` 自訂（含設空陣列停走父目錄）。
  - `config-file/config-advanced.md:151` 「By default, Codex treats a directory containing `.git` as the project root.」
  - `config-file/config-advanced.md:158` 「Set `project_root_markers = []` to skip searching parent directories and treat the current working directory as the project root.」
- claim：instruction 只在 session 首回合注入限量 project guidance。
  - `config-file/config-advanced.md:744` 「Codex reads `AGENTS.md` (and related files) and includes a limited amount of project guidance in the first turn of a session.」
- claim：可用 `model_instructions_file` 整份替換內建 instructions（取代 `AGENTS.md` 之外的基底）。
  - `config-file/config-reference.md:283` 「Replacement for built-in instructions instead of `AGENTS.md`.」
- claim（寫作指導）：「保持小、當 feedback loop、只放要緊的、近端放置、codify 重複回饋」。
  - `customization/overview.md:21` 「`AGENTS.md` gives Codex durable project guidance that travels with your repository and applies before the agent starts work. Keep it small.」
  - `customization/overview.md:30` 「When the agent makes incorrect assumptions about your codebase, correct them in `AGENTS.md` and ask the agent to update `AGENTS.md` so the fix persists. Treat it as a feedback loop.」
  - `customization/overview.md:32` 「**Updating `AGENTS.md`:** Start with only the instructions that matter. Codify recurring review feedback, put guidance in the closest directory where it applies, and tell the agent to update `AGENTS.md` when you correct something so future sessions inherit the fix.」
  - `agent-configuration/agents-md.md:83` 「Codex stops searching once it reaches your current directory, so place overrides as close to specialized work as possible.」
- claim（寫作指導：何時該更新 AGENTS.md）——重複犯錯、讀太多文件、重複 PR 回饋三觸發條件。
  - `customization/overview.md:36` 「**Repeated mistakes**: If the agent makes the same mistake repeatedly, add a rule.」
  - `customization/overview.md:37` 「**Too much reading**: If it finds the right files but reads too many documents, add routing guidance (which directories/files to prioritize).」
  - `customization/overview.md:38` 「**Recurring PR feedback**: If you leave the same feedback more than once, codify it.」
- claim（寫作指導：global vs repo 分工）——global 檔管溝通風格，repo 檔管團隊/程式碼規則。
  - `customization/overview.md:45` 「Use the global file to shape how Codex communicates with you (for example, review style, verbosity, and defaults), and keep repo files focused on team and codebase rules.」

## 軸 2 Rules 機制

- claim：Codex 的 rules 是**沙箱外命令的執行政策（exec policy）**，與 AGENTS.md instruction 生態無耦合——`rules.md` 全檔零次出現 "instruction"（rg 已驗）。
  - `agent-configuration/rules.md:5` 「Use rules to control which commands Codex can run outside the sandbox.」
  - `agent-configuration/rules.md:7` 「Rules are experimental and may change.」
- claim：rules 檔格式＝`.rules` 檔放 `rules/` 資料夾、緊鄰 active config layer；Codex 啟動時掃每個 active config layer 的 `rules/`（含 team config 與 `~/.codex/rules/`）；project-local `<repo>/.codex/rules/` 只在專案受信任時載入。
  - `agent-configuration/rules.md:11` 「Create a `.rules` file under a `rules/` folder next to an active config layer (for example, `~/.codex/rules/default.rules`).」
  - `agent-configuration/rules.md:42` 「Codex scans `rules/` under every active config layer at startup, including [Team Config](...) locations and the user layer at `~/.codex/rules/`. Project-local rules under `<repo>/.codex/rules/` load only when the project `.codex/` layer is trusted.」
- claim：規則語言＝Starlark（Python-like、可無副作用執行）；核心謂詞 `prefix_rule()`。
  - `agent-configuration/rules.md:135` 「The `.rules` file format uses `Starlark` (see the [language spec](...)). Its syntax is like Python, but it's designed to be safe to run: the rules engine can run it without side effects (for example, touching the filesystem).」
- claim：決策合併語義＝多規則命中取最嚴格（`forbidden` > `prompt` > `allow`）。
  - `agent-configuration/rules.md:60` 「`decision` **(defaults to `"allow"`)**: The action to take when the rule matches. Codex applies the most restrictive decision when more than one rule matches (`forbidden` > `prompt` > `allow`).」
- claim（寫作指導）：`match`/`not_match` 被官方稱為 "inline unit tests"，載入時即驗證。
  - `agent-configuration/rules.md:26` 「# `match` and `not_match` are optional "inline unit tests" where you can / # provide examples of commands that should (or should not) match this rule.」
  - `agent-configuration/rules.md:65` 「`match` and `not_match` **(defaults to `[]`)**: Examples that Codex validates when it loads your rules. Use these to catch mistakes before a rule takes effect.」
- claim：TUI allow-list 操作會寫回 user layer `~/.codex/rules/default.rules`；Smart approvals 開啟時 Codex 可在 escalation 時主動提議 `prefix_rule`。
  - `agent-configuration/rules.md:44` 「When you add a command to the allow list in the TUI, Codex writes to the user layer at `~/.codex/rules/default.rules` so future runs can skip the prompt.」

## 軸 3 Memory

- claim：Codex 有 local memory 機制——local Codex clients 用獨立 local memory store，與 ChatGPT web 的 ChatGPT memory 分離。
  - `customization/memories.md:5` 「Memories let ChatGPT and Codex carry useful context from earlier work into future work.」
  - `customization/memories.md:7` 「ChatGPT web uses ChatGPT memory, while local Codex clients use a separate local memory store and controls.」
- claim（寫作指導：memory 與 AGENTS.md 的分工）——必須恆常生效的團隊規則放 AGENTS.md/checked-in 文檔，memory 只是 recall 層。
  - `customization/memories.md:12` 「Keep required team guidance in `AGENTS.md` or checked-in documentation. Treat memories as a helpful recall layer, not as the only source for rules that must always apply.」
- claim：memory 預設關閉，以 feature flag 開啟；儲存於 `~/.codex/memories/`；官方定位為 generated state、禁手編當控制面。
  - `customization/memories.md:118` 「Local Codex memories are off by default.」
  - `customization/memories.md:124-125` config `[features]`／`memories = true`
  - `customization/memories.md:89` 「The main memory files live under `~/.codex/memories/` and include summaries, durable entries, recent inputs, and supporting evidence from prior chats.」
  - `customization/memories.md:92` 「Treat these files as generated state. You can inspect them when troubleshooting or before sharing your Codex home directory, but don't rely on editing them by hand as your primary control surface.」
- claim：生成行為有節流設計——跳過活躍/短 session、redact secrets、背景更新、idle 才寫、rate-limit 低於門檻跳過。
  - `customization/memories.md:71` 「Codex skips active or short-lived sessions, redacts secrets from generated memory fields, and updates memories in the background instead of immediately at the end of every chat.」
  - `customization/memories.md:75` 「Memories may not update right away when a chat ends. Codex waits until a chat has been idle long enough to avoid summarizing work that's still in progress.」
  - `customization/memories.md:79` 「Memory generation can also skip a background pass when your Codex rate-limit remaining percentage is below the configured threshold, so Codex doesn't spend quota when you're near a limit.」
- claim：settings 面有 generate/use 分離、外部 context 排除、兩個 model override 鍵。
  - `customization/memories.md:134` 「`memories.generate_memories`: controls whether newly created chats can be stored as memory-generation inputs.」
  - `customization/memories.md:136` 「`memories.use_memories`: controls whether Codex injects existing memories into future sessions.」
  - `customization/memories.md:144` 「`memories.extract_model`: overrides the model used for per-chat memory extraction.」／`customization/memories.md:146` 「`memories.consolidation_model`: overrides the model used for global memory consolidation.」

## 軸 4 Skills

- claim：格式＝agentskills.io 開放標準；skill 是含 `SKILL.md` 的目錄，`SKILL.md` 必填 `name` + `description` 兩個 frontmatter 欄位。
  - `build-skills.md:8` 「Skills build on the [open agent skills standard](https://agentskills.io).」
  - `build-skills.md:45` 「A skill is a directory with a `SKILL.md` file plus optional scripts and references. The `SKILL.md` file must include `name` and `description`.」
- claim：discovery＝progressive disclosure——初始只給 name+description（Codex 另含檔案路徑），選中才讀全文。
  - `build-skills.md:33` 「Skills use **progressive disclosure** to manage context efficiently. ChatGPT and Codex start with each skill's name and description, then load the full `SKILL.md` instructions when they decide to use that skill.」
  - `customization/overview.md:130-132` 「- It starts with metadata (`name`, `description`) for discovery」「- It loads `SKILL.md` only when a skill is chosen」「- It reads references or runs scripts only when needed」
- claim：初始 skills list 有硬預算——model context window 的 2%（context 未知時 8,000 字元）；超量先縮 description、再可能省略 skill 並警示；預算只限初始清單，選中後仍讀全文。
  - `build-skills.md:38` 「To avoid crowding out the rest of the prompt, this list uses at most 2% of the model's context window, or 8,000 characters when the context window is unknown. If many skills are installed, Codex shortens skill descriptions first. For large skill sets, Codex may omit some skills from the initial list and show a warning.」
  - `build-skills.md:43` 「This budget applies only to the initial skills list. When Codex selects a skill, it still reads the full SKILL.md instructions for that skill.」
- claim：位置層級＝REPO（cwd 起每層目錄的 `.agents/skills` 直到 repo root）/ USER（`~/.agents/skills`）/ ADMIN（`/etc/codex/skills`）/ SYSTEM（OpenAI 內建）；symlink 會跟隨。
  - `build-skills.md:135` 「Codex reads skills from repository, user, admin, and system locations. For repositories, Codex scans `.agents/skills` in every directory from your current working directory up to the repository root.」
  - `build-skills.md:146` 「Codex supports symlinked skill folders and follows the symlink target when scanning these locations.」
- claim：同名 skill 不 merge——兩者都出現在選擇器。
  - `build-skills.md:135` 「If two skills share the same `name`, Codex doesn't merge them; both can appear in skill selectors.」
- claim：觸發＝explicit（CLI/IDE `$` 或 `/skills`）＋implicit（任務符合 `description`）；可用 `agents/openai.yaml` 的 `allow_implicit_invocation`（預設 `true`）關閉 implicit。
  - `build-skills.md:215` 「`allow_implicit_invocation` (default: `true`): When `false`, Codex won't implicitly invoke the skill based on user prompt; explicit `$skill` invocation still works.」
- claim（寫作指導）：description 觸發可靠度——concise、clear scope and boundaries、front-load key use case and trigger words。
  - `build-skills.md:98` 「Because implicit matching depends on `description`, write concise descriptions with clear scope and boundaries. Front-load the key use case and trigger words so a host can still match the skill if descriptions are shortened.」
- claim（寫作指導）：Best practices 四條。
  - `build-skills.md:219-222` 「- Keep each skill focused on one job.」「- Prefer instructions over scripts unless you need deterministic behavior or external tooling.」「- Write imperative steps with explicit inputs and outputs.」「- Test prompts against the skill description to confirm the right trigger behavior.」

## 軸 5 Agents（subagents）

- claim：custom agent 格式＝**standalone TOML 檔**（非 markdown frontmatter），位置 `~/.codex/agents/`（個人）或 `.codex/agents/`（專案）；一檔一 agent。
  - `agent-configuration/subagents.md:336` 「To define your own custom agents, add standalone TOML files under `~/.codex/agents/` for personal agents or `.codex/agents/` for project-scoped agents.」
  - `agent-configuration/subagents.md:340` 「Each file defines one custom agent. Codex loads these files as configuration layers for spawned sessions, so custom agents can override the same settings as a normal Codex session config.」
- claim：必填欄位三個——`name`、`description`、`developer_instructions`；選填可帶任何 `config.toml` key（`model`、`model_reasoning_effort`、`sandbox_mode`、`mcp_servers`、`skills.config`）。
  - `agent-configuration/subagents.md:345` 「Every standalone custom agent file must define:」
  - `agent-configuration/subagents.md:391` 「You can also include other supported `config.toml` keys in a custom agent file, such as `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`.」
- claim：模型指定解析鏈＝explicit spawn value → `[agents]` default → parent 值；都沒設 reasoning effort 時用該 model 的預設 effort。
  - `agent-configuration/subagents.md:352` 「Before applying the file, Codex resolves each setting from an explicit spawn value, then the corresponding `[agents]` default, then the parent's value.」
  - `agent-configuration/subagents.md:157` 「If you don't configure a subagent model or `model_reasoning_effort`, the subagent inherits the parent agent's model and reasoning effort.」
- claim：內建 agents 三個——`default`、`worker`、`explorer`；同名 custom agent 蓋過內建；`name` 欄位是身分真相源（檔名只是慣例）。
  - `agent-configuration/subagents.md:330` 「Codex ships with built-in agents:」
  - `agent-configuration/subagents.md:381` 「If a custom agent name matches a built-in agent such as `explorer`, your custom agent takes precedence.」
  - `agent-configuration/subagents.md:393` 「Codex identifies the custom agent by its `name` field. Matching the filename to the agent name is the simplest convention, but the `name` field is the source of truth.」
- claim：全域 `[agents]` 設定五鍵（enabled、max_concurrent_threads_per_session、default_subagent_model、default_subagent_reasoning_effort、interrupt_message）。
  - `agent-configuration/subagents.md:369-371`（表格節錄：`agents.enabled`／`agents.default_subagent_model` 等）
- claim（寫作指導）：custom agent 設計——narrow and opinionated；subagent prompt 應講明分工/是否等全部/回傳什麼。
  - `agent-configuration/subagents.md:399` 「The best custom agents are narrow and opinionated. Give each one clear job, a tool surface that matches that job, and instructions that keep it from drifting into adjacent work.」
  - `agent-configuration/subagents.md:130` 「A good subagent prompt should explain how to divide the work, whether Codex should wait for all agents before continuing, and what summary or output to return.」
- claim（使用指導）：read-heavy 適合平行，write-heavy 慎用；理論依據是 context pollution / context rot。
  - `agent-configuration/subagents.md:95` 「As a starting point, use parallel agents for read-heavy tasks such as exploration, tests, triage, and summarization. Be more careful with parallel write-heavy workflows, because agents editing code at once can create conflicts and increase coordination overhead.」
  - `agent-configuration/subagents.md:78` 「- **Context pollution**: useful information gets buried under noisy intermediate output.」
  - `agent-configuration/subagents.md:79` 「- **Context rot**: performance degrades as the chat fills up with less relevant details.」
- claim：delegation 觸發可來自 `AGENTS.md` 或 skill instructions 的請求（instruction 檔可驅動 subagent 行為）。
  - `agent-configuration/subagents.md:56` 「Codex can also follow applicable `AGENTS.md` or skill instructions that request delegation.」

## 軸 6 Hooks＋設定

- claim：hooks＝agentic loop 中跑 scripts/MCP tools 的擴充框架；三層結構 event → matcher group → handlers。
  - `hooks.md:5` 「Hooks are an extensibility framework for Codex. They let you run scripts or MCP tools during the agentic loop, enabling features such as:」
  - `hooks.md:82-87` 「Hooks are organized in three levels:」「- A hook event such as `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, or `Stop`」「- A matcher group that decides when that event matches」「- One or more hook handlers that run when the matcher group matches」
- claim：事件面共 13 個——turn 中 `PreToolUse`/`PermissionRequest`/`PostToolUse`/`PreCompact`/`PostCompact`/`UserPromptSubmit`/`SubagentStop`/`Stop`、`Interrupt`（中斷時、subagent 不跑）、`SessionStart`/`SubagentStart`、`SessionEnd`（主執行緒結束、subagent 不跑）。
  - `hooks.md:25-28` （事件表逐行引文見提取原文）
- claim：載入語義＝**全部疊加不覆蓋**（與 config 的 closest-wins 不同）；同一 layer 同時有 `hooks.json` 與 inline `[hooks]` 則合併＋警告；同事件多個 matching command hooks 並行啟動。
  - `hooks.md:49` 「If more than one hook source exists, Codex loads all matching hooks. Higher-precedence config layers don't replace lower-precedence hooks.」
  - `hooks.md:51` 「If a single layer contains both `hooks.json` and inline `[hooks]`, Codex merges them and warns at startup. Prefer one representation per layer.」
  - `hooks.md:17` 「- Multiple matching command hooks for the same event are launched concurrently, so one hook can't prevent another matching hook from starting.」
- claim：位置＝緊鄰 active config layers（`~/.codex/hooks.json`、`~/.codex/config.toml`、`<repo>/.codex/hooks.json`、`<repo>/.codex/config.toml`）＋plugin-bundled；project-local 僅在專案受信任時載入。
  - `hooks.md:44-58`（位置與 trust 語義節錄）
- claim：非 managed hooks 須 review-and-trust（以 hash 記信任，變更即失效待審）；managed（system/MDM/cloud/`requirements.toml`）免審不可由 user 停用。
  - `hooks.md:66` 「Before a non-managed hook can run, Codex requires you to review and trust the exact hook definition. Codex records trust against the hook's current hash, so new or changed hooks are marked for review and skipped until trusted.」
  - `hooks.md:73` 「Managed hooks from system, MDM, cloud, or `requirements.toml` sources are marked as managed, trusted by policy, and can't be disabled from the user hook browser.」
- claim：config 層級七層 precedence（CLI flags > project `.codex/config.toml` closest-wins > profile > user `~/.codex/config.toml` > cloud-managed > system `/etc/codex/config.toml` > built-in defaults）；untrusted 專案跳過整個 `.codex/` layer（config＋hooks＋rules）。
  - `config-file/config-basic.md:21-37`（precedence 與 untrusted 語義）
  - `config-file/config-advanced.md:92` 「If multiple files define the same key, the closest file to your working directory wins.」
- claim：project-local config 有安全禁區——redirect credentials/provider/notification/telemetry/profile 等鍵被忽略並印警告。
  - `config-file/config-advanced.md:98` 「Project config files can't override settings that redirect credentials, alter host-owned app request metadata, change provider auth, select config profiles, or run machine-local notification/telemetry commands.」

## 軸 7 官方寫作哲學

- claim：prompt 四要素框架——Goal / Context / Output / Boundaries，且明言非必填格式。
  - `prompting.md:17-20` 「- **Goal:** What should ChatGPT do?」「- **Context:** What information or sources will help?」「- **Output:** What format, length, or level of detail do you need?」「- **Boundaries:** What must stay unchanged? What should ChatGPT avoid or check with you before it acts?」
  - `prompting.md:23` 「Use only the parts that help. You don't need to fill in every item or follow a required format.」
- claim：描述結果而非步驟。
  - `prompting.md:27` 「Start with the result, not a detailed list of steps. Include the audience or format when those details change what ChatGPT should produce.」
- claim：boundaries 極簡主義——只加會造成真問題的邊界，一兩條就夠。
  - `prompting.md:104` 「Boundaries are the few instructions ChatGPT needs to avoid creating extra work or taking an action you didn't intend. Add one when changing the wrong detail would make the result unusable, or when you want to review something before it affects other people.」
  - `prompting.md:114` 「Focus on the one or two boundaries that matter most. You don't need to control every step ChatGPT takes.」
- claim：Codex prompt 四件套——行為、程式碼/重現路徑、約束、驗證方式；repro 步驟與 constraints 比高層描述更重要。
  - `prompting.md:311` 「A useful Codex prompt names the behavior you want, points to the relevant code or reproduction steps, preserves important constraints, and says how to verify the change.」
  - `prompting.md:428` 「- Supplied by you: the repro steps and constraints (these matter more than a high-level description).」
- claim：instruction 生態整體分工觀——AGENTS.md／memories／skills／MCP／subagents 五層互補不競爭；AGENTS.md 規則要配強制基建（pre-commit hooks、linters）。
  - `customization/overview.md:15` 「These are complementary, not competing. `AGENTS.md` shapes behavior, memories carry local context forward, skills package repeatable processes, and [MCP](...) connects Codex to systems outside the local workspace.」
  - `customization/overview.md:42` 「Pair `AGENTS.md` with infrastructure that enforces those rules: pre-commit hooks, linters, and type checkers catch issues before you see them, so the system gets smarter about preventing recurring mistakes.」
- claim：code review rules 的寫法指導（AGENTS.md 專區）——concise、講清要 flag 的行為與 safe path、格式/lint 交給 CI。
  - `agent-configuration/agents-md.md:140` 「Keep rules concise, explain the behavior to flag and any safe path or exception, and reserve formatting and lint checks for CI.」
- claim：custom prompts（markdown slash prompts）已 deprecated，官方導向 skills。
  - `custom-prompts.md:5` 「Custom prompts are deprecated. Use [skills](...) for reusable instructions that Codex can invoke explicitly or implicitly.」
- claim：官方建置順序教條——先 AGENTS.md（＋強制基建）→ plugin/skill → MCP → subagents。
  - `customization/overview.md:179-180` 「Build in this order:」「1. [Custom instructions with AGENTS.md](...) so Codex follows your repo conventions. Add pre-commit hooks and linters to enforce those rules.」

## 官方未提及清單

- 軸 1：**無 frontmatter/schema 規格**——`agents-md.md` 全檔無 "frontmatter" 命中（rg 零命中）；AGENTS.md 是純 markdown 指令面，僅 `## Code Review Rules` 一個有語義的保留章節名。截斷粒度兩處描述並存——`agents-md.md:15` 講 combined size（32 KiB 總量），`config-reference.md:1170` 講 per-file，鏡像未給兩者調和的明確行為描述。
- 軸 2：**rules 與 instruction 生態無任何官方橋接**——`rules.md` 全檔零次 "instruction"，純 exec policy。
- 軸 3：**memory 檔案格式/寫入端規格未提及**——官方明言勿手編、無條目結構文件；也無「記憶寫出品質判準」類指導。
- 軸 4：**SKILL.md 必填僅 `name`/`description` 兩欄**——agentskills.io 標準其餘欄位鏡像未列舉；官方只另提選用的 `agents/openai.yaml`（interface/policy/dependencies）。
- 軸 5：**subagent 的 markdown/agent-file 格式未提及**——官方格式就是 TOML config layer，`subagents.md:342` 自承「That can feel heavier than a dedicated agent manifest, and the format may evolve as authoring and sharing mature.」
- 軸 6：hooks 文檔完整，未發現明顯缺口（13 事件、matcher、background、managed hooks 均有專節）。
