# Claude Code 鏡像提取（七軸）

> 提取者：spec-miner agent（2026-09-12）；鏡像根：`/Users/ctai/Github/ai-rules/ref-docs/harness/claude-code/`（下文錨點均相對此根；行號為本次 Read 實測）

## 軸 1 Instruction 檔

- claim：Claude Code 原生只讀 CLAUDE.md，不讀 AGENTS.md；官方建議用 `@AGENTS.md` import 或 symlink 橋接
  - `docs/en/memory.md:129` 「Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them.」
- claim：CLAUDE.md 四個層級（managed policy / user / project / local），表格依載入順序由廣到狹排列——愈 specific 愈後載入
  - `docs/en/memory.md:54` 「The table below lists them in load order, from broadest scope to most specific, so a project instruction appears in context after a user instruction.」
  - `docs/en/memory.md:59-61` 位置：user `~/.claude/CLAUDE.md`；project `./CLAUDE.md` 或 `./.claude/CLAUDE.md`；local `./CLAUDE.local.md`（「add to `.gitignore`」）
- claim：多層檔案是串接（concatenate）而非覆蓋；目錄樹由 root 往下排序，離啟動目錄愈近愈後讀；同層 `CLAUDE.local.md` 排在 `CLAUDE.md` 之後
  - `docs/en/memory.md:157` 「All discovered files are concatenated into context rather than overriding each other. Across the directory tree, content is ordered from the filesystem root down to your working directory. … Within each directory, `CLAUDE.local.md` is appended after `CLAUDE.md`, so your personal notes are the last thing Claude reads at that level.」
- claim：上層目錄的 CLAUDE.md 啟動時載入；子目錄的 CLAUDE.md 延遲載入——Claude 讀到該子目錄檔案時才載入
  - `docs/en/memory.md:63` 「CLAUDE.md and CLAUDE.local.md files in the directory hierarchy above the working directory are loaded at launch. Files in subdirectories load on demand when Claude reads files in those directories.」
- claim：`@path/to/import` 語法支援相對/絕對路徑，遞迴 import 上限四層；import 內容在啟動時展開進 context（不省 token）；backticks 包住可免 import
  - `docs/en/memory.md:97` 「Both relative and absolute paths are allowed. Relative paths resolve relative to the file containing the import, not the working directory. Imported files can recursively import other files, with a maximum depth of four hops.」
  - `docs/en/memory.md:99` 「Import parsing skips Markdown code spans and fenced code blocks. To mention a path in your CLAUDE.md without importing it, wrap it in backticks」
- claim：尺寸限制——官方目標每檔 200 行以內（軟性目標，超長降低 adherence）；硬限制 4 MiB，超過整檔跳過不載
  - `docs/en/memory.md:81` 「**Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence.」
  - `docs/en/memory.md:405` 「Claude Code loads a CLAUDE.md file of up to 4 MiB in full and skips a larger file. Shorter files produce better adherence.」
- claim：CLAUDE.md 內容是以 user message 形式送達（非 system prompt 一部分），無嚴格合規保證——要強制執行須用 hook
  - `docs/en/memory.md:433` 「CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions.」
- claim：層級衝突時官方不裁定優先權——兩條規則矛盾時 Claude 可能任選一條；project-root CLAUDE.md 在 `/compact` 後會從磁碟重讀重注入
  - `docs/en/memory.md:91` 「**Consistency**: if two rules contradict each other, Claude may pick one arbitrarily.」
  - `docs/en/memory.md:462` 「Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session.」
- claim：官方對「怎麼寫好 CLAUDE.md」的四維指導：Size（<200 行）、Structure（markdown headers/bullets）、Specificity（可驗證的具體指令）、Consistency（定期清矛盾）
  - `docs/en/memory.md:79` 「Specific, concise, well-structured instructions work best.」
  - `docs/en/memory.md:83` 「**Structure**: use markdown headers and bullets to group related instructions. Claude scans structure the same way readers do: organized sections are easier to follow than dense paragraphs.」
  - `docs/en/memory.md:85-89` 「**Specificity**: write instructions that are concrete enough to verify. For example: 'Use 2-space indentation' instead of 'Format code properly'…」
- claim（寫作指導）：CLAUDE.md 該放什麼——「每次 session 都需要 Claude 記住的事實」；多步驟流程或只關局部 codebase 的內容應移去 skill 或 path-scoped rule
  - `docs/en/memory.md:50` 「Keep it to facts Claude should hold in every session: build commands, conventions, project layout, "always do X" rules. If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a [skill] or a [path-scoped rule] instead.」
- claim（寫作指導）：加內容的觸發時機——Claude 犯第二次同樣的錯、code review 抓到它該知道的、你重複打同樣的修正
  - `docs/en/memory.md:43-48` 「Treat CLAUDE.md as the place you write down what you'd otherwise re-explain. Add to it when: * Claude makes the same mistake a second time * A code review catches something Claude should have known about this codebase * You type the same correction or clarification into chat that you typed last session…」
- claim：`/init` 可生成初始 CLAUDE.md，已存在時建議改良而非覆蓋；`/doctor` 會提議修剪（砍 Claude 可從 codebase 推導的內容、保留 pitfalls/rationale/偏離工具預設的慣例）
  - `docs/en/memory.md:72` 「If a CLAUDE.md already exists, `/init` suggests improvements rather than overwriting it. Refine from there with instructions Claude wouldn't discover on its own.」
  - `docs/en/memory.md:458` 「it cuts content Claude can derive from the codebase, such as directory layouts, dependency lists, and architecture overviews, and keeps pitfalls, rationale, and conventions that differ from tool defaults.」

## 軸 2 Rules 機制（`.claude/rules/`）

- claim：`.claude/rules/` 是獨立於 CLAUDE.md 的模組化 rule 目錄，遞迴發現所有 `.md`，建議一檔一主題
  - `docs/en/memory.md:187` 「Place markdown files in your project's `.claude/rules/` directory. Each file should cover one topic, with a descriptive filename like `testing.md` or `api-design.md`. All `.md` files are discovered recursively, so you can organize rules into subdirectories like `frontend/` or `backend/`」
- claim：無 `paths` frontmatter 的 rule 啟動時載入，優先權同 `.claude/CLAUDE.md`；有 `paths` 的只在 Claude 碰到匹配檔案時觸發（非每次 tool use）
  - `docs/en/memory.md:199` 「Rules without [`paths` frontmatter] are loaded at launch with the same priority as `.claude/CLAUDE.md`.」
  - `docs/en/memory.md:220` 「Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use.」
- claim：user 層級 rules 在 `~/.claude/rules/`，載入順序先於 project rules——project rules 優先權較高
  - `docs/en/memory.md:269` 「User-level rules are loaded before project rules, giving project rules higher priority.」
- claim：`paths` glob 展開有預算上限（每條 rule 的整個 paths 清單共 1,000 個展開 pattern、4 MiB）；支援 symlink 共享（circle 會被偵測處理）
  - `docs/en/memory.md:242` 「a rule's whole `paths` list shares one budget of 1,000 expanded patterns and 4 MiB, and patterns without braces don't count against it.」
  - `docs/en/memory.md:250` 「The `.claude/rules/` directory supports symlinks, so you can maintain a shared set of rules and link them into multiple projects. Symlinks are resolved and loaded normally, and circular symlinks are detected and handled gracefully.」
- claim：rules 與 skills 的載入模型分際——rules 每 session 或匹配檔案開啟時載入；skills 只在被呼叫或 Claude 判定相關時載入
  - `docs/en/memory.md:182` 「Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use [skills] instead, which only load when you invoke them or when Claude determines they're relevant to your prompt.」

## 軸 3 Memory（auto memory）

- claim：兩套互補系統——CLAUDE.md（你寫的指令/rules）與 auto memory（Claude 自己記的 learnings/patterns），都在每次對話開頭載入；都是 context 而非強制設定，要硬擋用 PreToolUse hook
  - `docs/en/memory.md:23` 「Claude Code has two complementary memory systems. Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a [PreToolUse hook] instead.」
- claim：memory 檔四種 type（frontmatter `type` 欄位）：`user`／`feedback`／`project`／`reference`；可從 codebase 推導的東西一律跳過，CLAUDE.md 已寫的也跳過
  - `docs/en/memory.md:344-351` 「* `user`: your role, expertise, and working preferences * `feedback`: corrections you give Claude and approaches you confirm * `project`: ongoing work, deadlines, and decisions that Claude can't derive from the code or git history * `reference`: where to find information outside the project… Claude skips anything it can derive from the codebase, such as architecture, file paths, or debugging fixes. It also skips anything your CLAUDE.md files already say.」
- claim：位置 `~/.claude/projects/<project>/memory/`，路徑由 git repo 推導——同 repo 所有 worktree 與子目錄共享一個 memory 目錄；機器本地（machine-local），不跨機器
  - `docs/en/memory.md:369` 「Each project gets its own memory directory at `~/.claude/projects/<project>/memory/`. The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory.」
  - `docs/en/memory.md:395` 「Auto memory is machine-local. … Files are not shared across machines or cloud environments.」
- claim：MEMORY.md 是索引（一行一條），每次對話載入前 200 行或 25KB（先到者為準）；超限時寫入仍成功但回錯誤要求重寫索引；topic 檔不在啟動時載入，Claude 需要時用標準檔案工具按需讀
  - `docs/en/memory.md:401` 「The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation. Content beyond that threshold is not loaded at session start. Claude keeps `MEMORY.md` concise by moving detailed notes into separate topic files.」
  - `docs/en/memory.md:407` 「Claude Code doesn't load topic files such as `user_role.md` or `feedback_testing.md` at startup. Claude reads them on demand using its standard file tools when it needs the information.」
- claim：主對話的 auto memory 不載入 subagents（fork 例外）；subagent 可用 `memory` 欄位擁有獨立記憶目錄
  - `docs/en/memory.md:409` 「The main conversation's auto memory isn't loaded into [subagents]; the exception is a [fork], which inherits the parent conversation and system prompt. A subagent's own auto memory, enabled with the subagent `memory` field, is a separate directory.」
- claim：memory 檔是 plain markdown，人可隨時編輯/刪除；`/memory` 瀏覽編輯；對 Claude 說「remember…」會存進 auto memory，要進 CLAUDE.md 需明說
  - `docs/en/memory.md:417` 「Auto memory files are plain markdown you can edit or delete at any time.」
  - `docs/en/memory.md:425` 「When you ask Claude to remember something… Claude saves it to auto memory. To add instructions to CLAUDE.md instead, ask Claude directly, like "add this to CLAUDE.md," or edit the file yourself via `/memory`.」

## 軸 4 Skills

- claim：SKILL.md 兩部份——YAML frontmatter（`---` 之間）＋markdown 指令 body；frontmatter 只在開檔第一行是 `---` 時被解析；全欄位 optional，僅 `description` 為 recommended
  - `docs/en/skills.md:328` 「All fields are optional. Only `description` is recommended so Claude knows when to use the skill.」
  - `docs/en/skills.md:330` 「Claude Code reads the frontmatter only when the opening `---` is the file's first line. Otherwise it treats the whole file, `---` markers included, as skill content.」
- claim：frontmatter 欄位全表（`docs/en/skills.md:334-355`）：`name`、`description`、`when_to_use`、`argument-hint`、`arguments`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`disallowed-tools`、`model`、`effort`、`context`、`agent`、`background`、`hooks`、`paths`、`shell`、`metadata`、`license`、`compatibility`
- claim：清單截斷限制——skill listing 中每條 `description`＋`when_to_use` 合併截斷於 1,536 字元；整份 listing 的字元預算＝模型 context window 的 1%，溢出時從最少使用的 skill 開始丟 description（name 永遠全列）
  - `docs/en/skills.md:337` 「Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage.」
  - `docs/en/skills.md:1052` 「The listing always contains every skill name, but if you have many skills, Claude Code shortens descriptions to fit the listing's character budget… The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the skills you invoke least, so the skills you use most keep their full text.」
- claim：位置四層——Enterprise（managed settings）、Personal `~/.claude/skills/`、Project `.claude/skills/`、Plugin；同名衝突 enterprise > personal > project；skill 永遠贏過同名 command 檔
  - `docs/en/skills.md:115-120` 位置表
  - `docs/en/skills.md:130` 「if a skill and a command share the same name, the skill takes precedence.」
- claim：`paths` frontmatter 限定觸發時機——Claude 工作於匹配 glob 的檔案時才自動載入（格式同 path-specific rules）；nested `.claude/skills/` 目錄下的 skills 延遲載入（Claude 首次讀/編該子目錄檔案時）
  - `docs/en/skills.md:351` 「Glob patterns that limit when this skill is activated. … When set, Claude loads the skill automatically only when working with files matching the patterns.」
  - `docs/en/skills.md:167` 「Skills in nested `.claude/skills/` directories below your starting directory aren't loaded at startup. They load the first time Claude reads or edits a file inside that subdirectory, and stay available for the rest of the session.」
- claim（寫作指導）：skill body 保持簡潔——載入後內容跨 turn 留在 context，每行都是重複 token 成本；「說要做什麼，別敘述 how/why」
  - `docs/en/skills.md:311` 「Keep the body itself concise. Once a skill loads, its content [stays in context across turns], so every line is a recurring token cost. State what to do rather than narrating how or why, and apply the same conciseness test you would for [CLAUDE.md content].」
- claim（寫作指導）：SKILL.md 500 行以內，詳細參考材料移到同目錄支援檔
  - `docs/en/skills.md:472` 「<Tip>Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.</Tip>」
- claim（寫作指導）：description 寫法——放入使用者會自然說的關鍵詞；觸發太頻繁就讓 description 更具體；官方提供 skill-creator eval 流程（baseline 對照、A/B 版本比較、description tuning）
  - `docs/en/skills.md:1034` 「1. Check the description includes keywords users would naturally say」
  - `docs/en/skills.md:802` 「The check for both is a baseline comparison. Collect a few realistic prompts, run each one in a fresh session with the skill available and again with it disabled, and compare the results. A fresh session matters because leftover context from authoring the skill will mask gaps in the written instructions.」
- claim：custom commands 已併入 skills——`.claude/commands/deploy.md` 與 `.claude/skills/deploy/SKILL.md` 都產生 `/deploy`，行為相同
  - `docs/en/skills.md:16` 「**Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way.」

## 軸 5 Agents（subagents）

- claim：定義檔＝markdown＋YAML frontmatter，body 就是 system prompt；僅 `name` 與 `description` 必填；subagent 只收到自己的 system prompt＋環境細節，不收 Claude Code 主 system prompt
  - `docs/en/sub-agents.md:288` 「The following fields can be used in the YAML frontmatter. Only `name` and `description` are required.」
  - `docs/en/sub-agents.md:265` 「The frontmatter defines the subagent's metadata and configuration. The body becomes the system prompt that guides the subagent's behavior. Subagents receive only this system prompt plus basic environment details like the working directory, not the Claude Code system prompt.」
- claim：欄位全表（`docs/en/sub-agents.md:290-308`）：`name`、`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`maxTurns`、`skills`、`mcpServers`、`hooks`、`memory`、`background`、`effort`、`isolation`、`color`、`initialPrompt`、`experimental`
- claim：載入點五層優先序：Managed settings > `--agents` CLI flag > `.claude/agents/`（project）> `~/.claude/agents/`（user）> plugin `agents/`
  - `docs/en/sub-agents.md:165-169` 「| Managed settings | Organization-wide | 1 (highest) | … | `--agents` CLI flag | Current session | 2 | … | `.claude/agents/` | Current project | 3 | … | `~/.claude/agents/` | All your projects | 4 | … | Plugin's `agents/` directory | Where plugin is enabled | 5 (lowest) |」
- claim：model 指定四層解析序——per-invocation 參數 > frontmatter `model`（`inherit` 選主對話模型）> `CLAUDE_CODE_SUBAGENT_MODEL` 環境變數 > 主對話模型
  - `docs/en/sub-agents.md:347-352` 「Claude Code resolves the subagent's model in this order: 1. The per-invocation `model` parameter 2. The subagent definition's `model` frontmatter, where `inherit` selects the main conversation's model 3. The [`CLAUDE_CODE_SUBAGENT_MODEL`] environment variable… 4. The main conversation's model」
- claim：巢狀限制——預設最多主對話往下三層；到深度上限時 Claude Code 從子代理收走 `Agent` tool（fork 例外）；可用 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 調整
  - `docs/en/sub-agents.md:983` 「By default, a subagent can spawn subagents of its own, up to three layers below the main conversation. At the depth limit, Claude Code withholds the `Agent` tool from every subagent except a [fork]」
- claim：description 合計預算 15,000 tokens，超過啟動時警告——官方解法是砍 description、把細節移進只在該 subagent 執行時才載入的 system prompt
  - `docs/en/sub-agents.md:27` 「Those descriptions take up context, so keep them short. When the combined descriptions of your subagents, except the built-in ones, exceed 15,000 tokens, Claude Code shows a [warning at startup with the total token count]. Trim the `description` fields of your subagents, and move detail into each subagent's system prompt, which only loads when that subagent runs.」
- claim：Explore 與 Plan 內建子代理跳過 CLAUDE.md 與 git status；其他內建與 custom 子代理都載入全部 CLAUDE.md 層級；無 frontmatter 欄位可改變哪些代理跳過
  - `docs/en/sub-agents.md:1033` 「**CLAUDE.md files**: every level of the [CLAUDE.md hierarchy] the main conversation loads, including `~/.claude/CLAUDE.md`, project rules, `CLAUDE.local.md`, and managed policy files. The built-in Explore and Plan agents skip this.」
  - `docs/en/sub-agents.md:1038` 「Explore and Plan are the only subagents that omit CLAUDE.md and git status. There is no frontmatter field or per-agent setting to change which agents skip them.」
- claim（寫作指導）：best practices 四條——專注單一任務、description 具體到能路由到對的 subagent、只給必要 tool 權限、project subagents 進版本控制
  - `docs/en/sub-agents.md:1182-1186` 「**Design focused subagents:** each subagent should excel at one specific task * **Write descriptions that single out one subagent:** … * **Limit tool access:** grant only necessary permissions for security and focus * **Check into version control:** share project subagents with your team」

## 軸 6 Hooks＋設定

- claim：hooks 定義於 JSON settings 檔，七個定義位置：user settings、project settings、project local、managed policy、plugin `hooks/hooks.json`、skill frontmatter、subagent frontmatter
  - `docs/en/hooks.md:253-261` 位置表
- claim：hook 條目跨 settings 層級合併（merge）而非取代；`disableAllHooks` 無法從 managed 以外層級停用 managed hooks
  - `docs/en/hooks.md:278` 「Hook entries merge across settings levels rather than replacing each other: user, project, and local settings add their own hooks without removing managed ones, and the [`disableAllHooks`] setting can't disable managed hooks from outside managed settings.」
- claim：hook 事件面（`docs/en/hooks.md` Hook events 節）：`SessionStart`、`Setup`、`InstructionsLoaded`、`UserPromptSubmit`、`UserPromptExpansion`、`MessageDisplay`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`PermissionDenied`、`Notification`、`SubagentStart`、`SubagentStop`、`TaskCreated`、`TaskCompleted`、`Stop`、`StopFailure`、`TeammateIdle`、`ConfigChange`
  - `docs/en/best-practices.md:231`（引文出自 best-practices.md）「[Hooks] run scripts automatically at specific points in Claude's workflow. Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens.」
- claim：settings 四檔＋managed——User `~/.claude/settings.json`／Shared project `.claude/settings.json`／Project local `.claude/settings.local.json`／Managed `managed-settings.json`；優先序最高到最低：managed > command line > project local > shared project > user
  - `docs/en/settings.md:463` 「Claude Code reads settings from four files, and an organization can also deliver managed settings from the claude.ai console.」
  - `docs/en/settings.md:49` 「Settings precedence, highest first: managed settings, command line, project local, shared project, user. A key set at a higher level overrides the same key set lower down.」
- claim：CLAUDE.md 指令與 settings 強制的分際——settings 由 client 無條件執行；CLAUDE.md 只塑造行為、非硬性執行層
  - `docs/en/memory.md:319` 「Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not an hard enforcement layer.」（引文按鏡像原文微調）

## 軸 7 官方寫作哲學

- claim（最高價值）：一行一問的取捨測試——「刪掉這行會讓 Claude 犯錯嗎？」不會就砍；冗長的 CLAUDE.md 會讓 Claude 忽略你真正的指令
  - `docs/en/best-practices.md:174` 「Keep it concise. For each line, ask: *"Would removing this cause Claude to make mistakes?"* If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions!」
- claim：無固定格式，但「短＋人類可讀」是官方建議
  - `docs/en/best-practices.md:160` 「There's no required format for CLAUDE.md files, but keep it short and human-readable.」
- claim：把 CLAUDE.md 當程式碼維護——出錯時 review、定期 prune、靠觀察 Claude 行為是否實際改變來測試變更；單條指令被跳過就對那一行加 "IMPORTANT"（強調多行＝都不突出）
  - `docs/en/best-practices.md:186` 「Treat CLAUDE.md like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts.」
  - `docs/en/best-practices.md:188` 「If Claude keeps skipping one instruction, add emphasis such as "IMPORTANT" to that line alone. If you emphasize many lines, none of them stands out. Check CLAUDE.md into git so your team can contribute. The file compounds in value over time.」
- claim：Include/Exclude 對照表——收：Claude 猜不到的 Bash 指令、偏離預設的 code style、測試指令、repo 禮儀、專案特有架構決策、環境怪癖、非顯而易見的 gotcha；排：Claude 讀 code 就能推導的、標準語言慣例、詳細 API 文檔（改連結）、常變資訊、長解釋/教學、逐檔描述、「write clean code」類自明實踐
  - `docs/en/best-practices.md:176-184` 「| ✅ Include | ❌ Exclude | | Bash commands Claude can't guess | Anything Claude can figure out by reading code | | Code style rules that differ from defaults | Standard language conventions Claude already knows | … | Self-evident practices like "write clean code" |」
- claim：每檔 CLAUDE.md 只放廣泛適用的內容；偶爾才需要的領域知識/流程改用 skills（按需載入不撐爆每次對話）
  - `docs/en/best-practices.md:172` 「CLAUDE.md is loaded every session, so only include things that apply broadly. For domain knowledge or workflows that are only relevant sometimes, use [skills] instead. Claude loads them on demand without bloating every conversation.」
- claim（blog）：CLAUDE.md 精簡＋人類可讀，當成「人與 Claude 都要能快速理解的文檔」；每次新增應解決真實遇到的問題，禁理論性擔憂
  - `blog/using-claude-md-files.md:44` 「The recommendation is to keep this file concise and human-readable, treating it like documentation that both humans and Claude need to understand quickly.」
  - `blog/using-claude-md-files.md:43` 「Each addition should solve a real problem you have encountered, not theoretical concerns about what Claude might need.」
- claim（blog）：Start simple, expand deliberately——抗拒一次寫出完整 CLAUDE.md 的誘惑；拆檔＋在 CLAUDE.md 內引用是 context/prompt engineering 的選項；禁敏感資訊
  - `blog/using-claude-md-files.md:183` 「It's tempting to create a comprehensive CLAUDE.md right away. Resist that urge.」
  - `blog/using-claude-md-files.md:184` 「CLAUDE.md is added to Claude Code's context every time, so from a context engineering and prompt engineering standpoint, keep it concise. One option: break up information into separate markdown files and reference them inside the CLAUDE.md file.」
  - `blog/using-claude-md-files.md:185` 「Don't include sensitive information, API keys, credentials, database connection strings, or detailed security vulnerability information—especially if you commit to version control. Since CLAUDE.md becomes part of Claude's system prompt, treat it as documentation that could be shared publicly.」
- claim（blog）：最有效的 CLAUDE.md 解決真實問題——記錄你重複輸入的指令、十分鐘才能講清的架構 context、防止 rework 的 workflow；客製化是持續實踐非一次性設定
  - `blog/using-claude-md-files.md:188` 「The most effective CLAUDE.md files solve real problems: they document the commands you type repeatedly, capture the architectural context that takes ten minutes to explain, and establish workflows that prevent rework. Your file should reflect how your team actually develops software—not theoretical best practices that sound good but don't match reality.」
  - `blog/using-claude-md-files.md:189` 「Treat customization as an ongoing practice rather than a one-time setup task. … A well-maintained CLAUDE.md evolves with your codebase, continuously reducing the friction of working with AI assistance on complex software.」
- claim（blog）：instructions 具體性原則跨機制一致——「The more specific and concise your instructions, the more consistently Claude follows them」；模糊/矛盾指令是合規失敗主因
  - `docs/en/memory.md:23` 「The more specific and concise your instructions, the more consistently Claude follows them.」
  - `docs/en/memory.md:440` 「Look for conflicting instructions across CLAUDE.md files. If two files give different guidance for the same behavior, Claude may pick one arbitrarily.」
- claim（blog）：best practices 的底層約束——context window 填滿快且效能隨之退化，多數 best practices 都由這一條約束推導
  - `docs/en/best-practices.md:19` 「Most best practices are based on one constraint: Claude's context window fills up fast, and performance degrades as it fills.」
  - `docs/en/best-practices.md:23` 「LLM performance degrades as context fills. When the context window is getting full, Claude may start "forgetting" earlier instructions or making more mistakes. The context window is the most important resource to manage.」

## 官方未提及清單

- 軸 1：CLAUDE.md 超過 200 行的硬截斷——未提及（200 行是軟性目標 "target under 200 lines"；硬限制只有 4 MiB 整檔跳過。已搜：`200 lines`、`25KB`、`4 MiB`、`truncat`）
- 軸 1：AGENTS.md 原生 auto-load——官方明文否定（`docs/en/memory.md:129` "Claude Code reads `CLAUDE.md`, not `AGENTS.md`"；橋接只有 import/symlink 兩途）
- 軸 2：`.claude/rules/` 以外的獨立 rules 檔案格式——未提及（鏡像僅記載 markdown＋`paths` YAML frontmatter 一種格式）
- 軸 4：skill description 的品質評分/自動驗證內建於核心——未提及（官方把 eval 外包給 skill-creator plugin 與 agentskills.io 外部文檔）
- 軸 5：subagent system prompt（markdown body）的行數/長度建議——未提及（只有 description 合計 15,000-token 預算與「move detail into system prompt」的間接指導）
- 軸 7：`blog/agent-view-in-claude-code.md` 與 instruction 寫作——零相關（`blog/introduction-to-agentic-coding.md` 僅 §105-106 提及 CLAUDE.md 存在，無寫作指導）
