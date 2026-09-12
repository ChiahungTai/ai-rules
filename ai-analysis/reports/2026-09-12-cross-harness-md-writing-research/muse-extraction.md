# Muse Code 鏡像提取（七軸）

> 提取者：spec-miner agent（2026-09-12）；鏡像根 `/Users/ctai/Github/ai-rules/ref-docs/harness/meta/`（`fd` 自驗：muse-code/ 11 md、cookbook/ 6 md；api-reference/ 依指示跳過）。行號均為本次 Read 實測。

## 軸 1 Instruction 檔（AGENTS.md）

- claim：載入採 walk-up 制——從 workspace root 向上走到最近 `.git` 邊界，逐層檢查四檔、同層首個存在者勝出。
  - `muse-code/configuration.md:41` 「From your workspace root, Muse Code walks up to the nearest `.git` boundary. At each directory level, it checks `AGENTS.md`, `CLAUDE.md`, `.agents/AGENTS.md`, then `.claude/CLAUDE.md`; the first existing file in that order wins for that level. Precedence when guidance conflicts:」
- claim：衝突優先序兩條——project 勝 user、深層勝淺層；語義是「wins」（替換）非 merge。
  - `muse-code/configuration.md:43-44` 「- **Project rules win over user rules.**」「- Among project files, the **deeper file wins** over a shallower one.」
- claim：user 規則永遠載入；project 規則須先 trust workspace——未信任的 checkout 直接忽略 project `AGENTS.md`/`CLAUDE.md`。
  - `muse-code/configuration.md:46` 「Your machine-wide user rules always load. **Project rules load only after you [trust the workspace](/docs/muse-code/permissions#trust-scopes).** On an untrusted checkout, Muse Code ignores project `AGENTS.md` and `CLAUDE.md` until you trust it.」
- claim：trust 是一次性開關——信任 workspace 即載入該專案本地的 skills、rules、hooks，並按 workspace root 記憶。
  - `muse-code/permissions.md:71` 「The first time you open a workspace, Muse Code asks whether to trust it. When you trust a workspace, Muse Code loads its project-local skills, rules, and hooks. Muse Code remembers this trust for each workspace root.」
- claim：`muse init` 是官方種子指令——只寫一個 `AGENTS.md`、不動 settings.json；`--force` 整檔覆寫。
  - `muse-code/configuration.md:32` 「`muse init` seeds your project's agent rules. It writes a single `AGENTS.md` into the current directory. It creates no other files, and does **not** change `settings.json`:」
  - `muse-code/configuration.md:39` 「Without `--force`, it stops if `AGENTS.md` already exists. With `--force`, it overwrites the file completely, so save any existing content first.」
- claim（安全面寫作事實）：`--yolo` 信任 workspace 後載入 `AGENTS.md`，官方明文將 fork/PR checkout 上的這些檔定性為攻擊者可控指令。
  - `muse-code/permissions.md:107` 「`--yolo` removes both layers and trusts the workspace, so it loads the checkout's `AGENTS.md`, rules, and skills. On a pull-request or fork checkout, those files are attacker-controlled instructions.」
- claim（官方行為約束樣態）：instruction 檔連帶的預設保守行為寫進文檔——任務結束不等於 commit 請求。
  - `muse-code/configuration.md:49` 「it won't commit, amend, or push your work unless you ask it to in the session, it keeps scratch files outside your checkout, and it reverts incidental edits it didn't need. The end of a task is not a request to commit.」

## 軸 2 Rules 機制

- claim：「rules」作為載體名稱存在，但無獨立機制文檔——它只與 skills/hooks 並列出現在 trust/載入語境，無檔案路徑、格式、載入點說明。
  - `muse-code.md:35` 「When you trust the workspace, Muse Code loads the project's skills, rules, and hooks.」
  - `muse-code/interactive.md:50` 「Neither changes on-disk [memory or rules](/docs/muse-code/configuration#local-memory).」
- claim：rules 的載入門檻與 skills/hooks 同組（trust 後才載），有別於 memory（見軸 3）。
  - `muse-code/configuration.md:110` 「Skills, rules, and hooks differ: they load only after you trust it.」

## 軸 3 Memory

- claim：三 scope——personal-project（預設，機器上 repo 外）、project（`.agents/memory/` 進 repo）、personal（跨專案機器級）。
  - `muse-code/configuration.md:93-97` 「There are three scopes:」「- **Personal project memory** (the default): stored on your machine outside the repo, private to you, scoped to this project.」「- **Project memory**: committed to the repo under `<repo>/.agents/memory/`, shared with everyone who clones it.」「- **Personal memory**: your machine-wide notes, across all projects.」
- claim：索引結構官方規範——`MEMORY.md` 當索引、一主題一檔。
  - `muse-code/configuration.md:99` 「Keep an index in `MEMORY.md` and one Markdown file per topic:」
  - `muse-code/configuration.md:103` 「├── MEMORY.md        # index: one line per topic file」
- claim（官方「什麼該記」指導，最高價值）：記「agent 光靠通用知識會記錯的 durable 專案事實」。
  - `muse-code/configuration.md:107` 「Put durable, project-specific facts here: deployment procedures, the reason a workaround exists, a service's unusual behavior. Facts the agent could get wrong from general knowledge alone are the ones worth recording.」
- claim：recall 機制——session 開場只注入索引（`MEMORY.md`＋其餘檔案路徑清單，上限 48 檔），內容按需讀取；背景 observer 可在回合前插入相關筆記。
  - `muse-code/configuration.md:114` 「At the start of a session, Muse Code injects an *index* of your memory: `MEMORY.md` plus a list of the other Markdown files (their paths, not their contents), up to 48 files.」
- claim：memory 是唯一在未信任 workspace 仍載入的指令面，官方明文標記為 prompt-injection 攻擊面。
  - `muse-code/configuration.md:110` 「Muse Code reads committed project memory into the model's context even in an **untrusted** workspace. Skills, rules, and hooks differ: they load only after you trust it. Treat a repo's `MEMORY.md` as a prompt-injection surface, and review it on checkouts you don't control.」
- claim：沙箱內 `.agents` 目錄唯讀——agent 不能改寫自己的 memory。
  - `muse-code/permissions.md:77` 「Inside the writable workspace, the `.git`, `.muse`, and `.agents` directories stay read-only, so the agent can't rewrite its own history, configuration, or memory.」

## 軸 4 Skills

- claim：skill 定義——「可按需載入的可重複工作流封裝：一組指令＋可選工具與檔案」。
  - `muse-code/extending.md:55` 「A skill packages a repeatable workflow the agent can load on demand: a set of instructions, and optionally tools and files, that turn "explain how we do X" into a single invocation.」
- claim：四源掃描路徑，含跨 harness 自動發現——user 源除自有路徑外，預設也掃 `~/.claude/skills` 與 `$CODEX_HOME/skills`（fallback `~/.codex/skills`）；project 源也掃 repo 內 `.codex/skills`、`.claude/skills`；外來根可用偏好＋rollout gate 關閉。
  - `muse-code/extending.md:60` 「**User**: your account-wide skills in `$XDG_CONFIG_HOME/muse/skills` and `~/.agents/skills`, available in every project. Muse Code also discovers `~/.claude/skills` and `$CODEX_HOME/skills` by default, falling back to `~/.codex/skills` when `CODEX_HOME` is unset. A user preference and rollout gate can disable these foreign personal skill roots.」
  - `muse-code/extending.md:61` 「**Project**: skills committed to a repo under `<repo>/.agents/skills/<skill-id>/SKILL.md`, shared with anyone who clones it. Muse Code also scans repo-local `.codex/skills` and `.claude/skills`.」
- claim：`muse skills` CLI 全套（list/inspect/enable/install/validate/import）。
  - `muse-code/extending.md:67-72` 「muse skills list                    # every skill, all sources」「muse skills inspect <skill-id>」「muse skills enable <skill-id> --scope project」「muse skills install ./my-skill --scope user」「muse skills validate ./my-skill     # check it before installing」「muse skills import --from claude    # or: --from codex」
- claim：內建 skills 官方點名——`/plan`（產 grounded、decision-complete 的計畫後停下等核准）、`/grill`、`/taste`、`/grill-and-record`（把定案決策寫回專案文檔）。
  - `muse-code/extending.md:75` 「Built-in skills include `/plan` (turn a task into a grounded, decision-complete plan, then stop for approval), `/grill` (stress-test a plan or design before you build), and `/taste` (a design-quality gate for frontend work). The related `/grill-and-record` skill also records the settled decisions in your project docs.」
- claim（寫作品質的官方實證）：changelog 記錄官方整段重寫內建 skill 的「clearer guidance」，且 skill 文字品質被當資安面治理（隱藏終端控制字元直接拒絕）。
  - `muse-code/changelog.md:51` 「Rewrote the built-in plan, doctor, and source-control skills with clearer guidance」
  - `muse-code/changelog.md:61` 「**Security:** skill text containing hidden terminal-control characters is rejected, preventing display spoofing」

## 軸 5 Agents

- claim：subagent＝lead 為單一 bounded task 產生的子代理；worktree isolation 逐子請求，隔離失敗絕不靜默退回共享 checkout。
  - `muse-code/extending.md:21` 「A **subagent** is a child agent that the lead spawns for one bounded task. Children share the lead's checkout unless the lead requests worktree isolation for that child.」
  - `muse-code/extending.md:23` 「It never silently falls back to the shared checkout.」
- claim：容量機制——單一 agent tree 預設同時 8 個（含 root），`agents.execution_capacity` 於 settings.json 可設 1–64；未設定的 `ultra` root 用 64。
  - `muse-code/extending.md:33` 「One agent tree can execute eight agents at once by default, including the root agent. Set `agents.execution_capacity` from 1 through 64 in `settings.json` to change the limit. An unconfigured `ultra` root uses 64.」
- claim（官方「何時派 subagent」指導）：任務可拆且各自 bounded、可獨立驗證、否則會搶同一批檔案→派；嚴格序列→單 agent。
  - `muse-code/extending.md:27` 「Use subagents when a job splits into tasks that are each bounded, independently verifiable, and would otherwise contend for the same files. Keep the work on one agent when the steps are strictly sequential.」
- claim：四個背景 observer agents（memory recall／skill recall／goal tracking／verification）預設全開；observer 只提案，reconciler 決定，僅被接受的提案抵達主 agent。
  - `muse-code/extending.md:41` 「An observer never answers for you: it proposes, a reconciler decides, and only an accepted proposal reaches the main agent.」
  - `muse-code/extending.md:48` 「All four observers, including verification, are on by default.」
- claim：取消是協作式——未達 checkpoint 的已取消子代理會跑完、寫到一半的寫入會寫完；子代理只有在其 task 明確要求時才 commit。
  - `muse-code/extending.md:36-37` 「Cancellation is cooperative: a cancelled child that never reaches a checkpoint keeps running, and one mid-write finishes that write.」「A child commits changes only when its task explicitly asks it to.」

## 軸 6 Hooks＋設定

- claim：hook 事件恰 13 個，一 hook 綁一事件；`SessionEnd` 純觀察性（不能阻擋終止、不能為後續請求注入 context）。
  - `muse-code/extending.md:94` 「The available events are `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreLLMCall`, `PostLLMCall`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `Stop`, and `SessionEnd`. `SessionEnd` runs during orderly session termination. It is observational: its output cannot block termination, inject context for a later request, or stop the session.」
- claim：hooks 三源——project `.muse/hooks.json`（trust 後才跑）、user settings（免專案 trust）、managed（`managed_hooks_path` 指向，免專案 trust）。
  - `muse-code/extending.md:83-87` 「- **Project**: committed to the repo at `<project-root>/.muse/hooks.json`.」「Project hooks run only after you trust the project folder. User hooks run from your own settings without a separate hook-level trust step. Managed hooks also run without a project-trust step, so whoever controls the managed hooks file controls what executes.」
- claim：hook 沙箱外執行語義——hook 命令直接過 shell、在治理 agent 自身工具的 sandbox 與 approval 之外；唯一硬化是清空環境＋小 allowlist。
  - `muse-code/extending.md:89-90` 「> [!WARNING] Hooks run outside the sandbox」「> Only add hooks whose commands you've read. A hook's command runs directly through your shell, **outside** the [sandbox and approval](/docs/muse-code/permissions) that govern the agent's own tools. The only hardening is a cleared environment with a small allowlist.」
- claim：無 `muse hooks` 命令族、無 per-hook trust 指令——改設定後開新 session 重載。
  - `muse-code/extending.md:98` 「There is no active `muse hooks` command family or per-hook trust command. Fix the reported configuration and start a new session to reload it.」
- claim：settings.json schema 頂層契約——必須 `"schema_version": 1`；缺 key 會讓每個指令啟動即失敗 `malformed settings file`；但整檔缺失反而合法（套用預設）。
  - `muse-code/configuration.md:28` 「`settings.json` must set `"schema_version": 1`. A file that omits that key fails every command at startup with `malformed settings file`. An unrecognized value fails with `unsupported settings schema version`. A **missing** file is fine, because Muse Code applies defaults. Create the file only when you have something to set, and always include `"schema_version": 1`.」
- claim：settings.json 內容清單——model 預設、TUI 偏好、tool 設定、MCP servers、`hooks` block＋`managed_hooks_path`、`runtime_capabilities` map（可關 observer agents）、telemetry。
  - `muse-code/configuration.md:23-24` 「- a first-class `hooks` block, plus a `managed_hooks_path` pointer (see [hooks](/docs/muse-code/extending#hooks))」「- a `runtime_capabilities` map that toggles capabilities such as the [observer agents](/docs/muse-code/extending#observer-agents)」

## 軸 7 官方寫作哲學

- claim（workflow 請求寫法，專節「Structure effective workflow requests」）：每個 child 給 bounded 責任＋定義最終交付物；會改檔的任務要明說 parallel writers 是否用 isolated worktrees；唯讀 child 留共享 workspace。
  - `muse-code/workflows.md:68` 「Give each child a bounded responsibility and define the final deliverable. This prompt gives Muse Code enough structure while leaving implementation details to the workflow author:」
  - `muse-code/workflows.md:81` 「For tasks that change files, state whether parallel writers should use isolated worktrees. Isolation gives each child a separate Git worktree and prevents concurrent writes from colliding:」
  - `muse-code/workflows.md:89` 「Keep read-only children in the shared workspace. Isolation requires a Git repository and can be rejected if its prerequisites are unavailable. It does not silently fall back to shared placement.」
- claim（何時用 workflow vs 主 agent 的官方判準）：小改動、短解釋、需要單一連續推理鏈的緊耦合變更留在主 agent；workflow 適用平行審計／獨立方案比較／多源研究後查證／遷移切分／實作-驗證-合成序列。
  - `muse-code/workflows.md:37` 「Keep a task on the main agent when it is a small edit, a short explanation, or a tightly coupled change that needs one continuous line of reasoning.」
  - `muse-code/workflows.md:29-35` 「Use workflows for work such as:」「- Auditing several subsystems in parallel.」「- Comparing independent implementation approaches.」「- Researching a question across several sources, then checking the claims.」「- Splitting a migration into isolated ownership areas.」「- Running an implementation, verification, and synthesis sequence.」
- claim（agent 設計原則：narrow tool surface）：官方兩處同義——工具面越小越好推理、越省；settingSources 置空使 run hermetic and reproducible。
  - `agent-frameworks.md:131` 「**`allowedTools`**: restrict the agent to the tools the task needs. A smaller surface is easier to reason about and cheaper to run.」
  - `agent-frameworks.md:133` 「**`settingSources: []`**: don't inherit ambient user or project settings, so runs are hermetic and reproducible.」
  - `agent-frameworks.md:343` 「**Give the agent only the tools it needs.** Allowlist tools and declare only the MCP servers you trust; don't inherit ambient user or project configuration. A narrow tool surface is safer and cheaper.」
- claim（官方 system prompt 範本）：minimal 版強調 minimal、well-tested changes；長版強調 focused, verified changes。
  - `agent-frameworks.md:64` 「systemPrompt: "You are a coding agent. Make minimal, well-tested changes.",」
  - `agent-frameworks.md:198-199` 「base_instructions: "You are a coding agent operating in a terminal. Use the available tools to read and edit files and run shell commands, and complete the user's task with focused, verified changes.",」
- claim（config 即寫作哲學）：durable project knowledge 一次設定、跨 session 免重複——instruction/memory 檔的存在理由官方一句話版本。
  - `muse-code/configuration.md:13` 「Set Muse Code up once for your machine and once per project, and give the agent the durable project knowledge it needs. This way, you don't repeat yourself every session. User settings live in a JSON file. Project instructions and memory travel with the repository.」
- claim（session 命名與訊息寫作指導）：名稱描述 ownership 或 purpose；跨 session 訊息只用於協調/狀態/證據/review 請求，禁傳 secrets、禁假設對方已執行。
  - `muse-code/session-messaging.md:92` 「Use names that describe ownership or purpose, such as `api-review-482731`, `frontend-migration-482731`, or `release-check-482731`.」
  - `muse-code/session-messaging.md:142` 「Use session messages for coordination, status, evidence, and review requests. Don't use them to transfer secrets or to assume that another session executed a command.」
- claim（instruction 文字品質影響答案品質的官方實證）：0.1.x 曾 rollback 一次內建 instruction 變更，因其使答案品質退化。
  - `muse-code/changelog.md:154` 「and a rollback of a built-in instruction change that had regressed answer quality.」
- claim（production patterns 的 agent 可靠性原則）：等 terminal event 而非 stream 靜默、設兩層 timeout、無人值守必沙箱＋per-run 工作目錄＋scrubbed allowlist 環境。
  - `agent-frameworks.md:340-342` 「- **Wait for the terminal event.** Completion is the `result` message (Claude Agent SDK) or a `turn/completed` matching your turn id (Codex), not the stream going quiet or the process exiting.」「- **Set two timeouts.** Pair an overall wall-clock cap with an idle watchdog that resets on every event.」「- **Sandbox unattended agents.** Removing the approval step [...] lets the agent act on its own. Run it inside an OS sandbox with a dedicated per-run working directory and a scrubbed, allowlisted environment.」

## 官方未提及清單

- 軸 1：AGENTS.md 內容層寫法指導（怎麼寫好/結構建議）——configuration.md 對「怎麼寫 AGENTS.md」零指導（全文 `rg -n "AGENTS\.md"` 九處皆機制描述）
- 軸 1：instruction 檔截斷/尺寸限制——無 AGENTS.md 尺寸語義
- 軸 1：多檔 merge 語義——文檔唯一衝突語義是 "wins"（`configuration.md:41`），無逐段合併描述
- 軸 2：獨立 rules 檔的路徑/格式/發現機制——無 rules 專門文檔（全部命中皆 trust 並列語境或 permission prefix rules）
- 軸 3：memory 寫入閘/治理機制——官方只寫讀取/recall 與沙箱唯讀保護，未寫任何寫入 API 或閘
- 軸 4：SKILL.md frontmatter 欄位契約——欄位驗證只存在於 `muse skills validate` 指令層，未文檔化欄位
- 軸 5：subagent 定義檔格式——`permissions.md:27` 提到 "A child can narrow that toolset through its agent definition" 但鏡像無該定義格式文檔
- 軸 6：settings.json 完整欄位 schema——僅敘述式欄位清單，無逐欄 schema 表
- 軸 7：agent-patterns.md 索引指向的五篇子文檔未鏡像——cookbook 僅 6 檔；cookbook/muse-code.md 指向的十篇子文檔同樣未鏡像
