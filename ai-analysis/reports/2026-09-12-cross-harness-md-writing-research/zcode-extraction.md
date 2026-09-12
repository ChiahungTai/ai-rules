# ZCode 鏡像提取（七軸）

> 提取者：spec-miner agent（2026-09-12）；鏡像根：`/Users/ctai/Github/ai-rules/ref-docs/harness/zcode/`（下文錨點均相對此根）。鏡像現況勘誤：fd 實測 27 檔＝`cn/docs/` 26 檔＋`en/docs/` **僅 welcome.md 1 檔**——en 側並非同構，以下全以 cn/ 為據。

## 軸 1 Instruction 檔（AGENTS.md）

- claim：ZCode 啟動任務時讀 AGENTS.md，讀取來源只有兩個——用戶全域 `~/.zcode/AGENTS.md` 與當前 Workspace 的 AGENTS.md。
  - `cn/docs/agents.md:66` 「如果希望长期约束 ZCode Agent 的行为，可以添加 AGENTS.md 指令文件。ZCode 会在启动任务时读取该文件，并把其中的项目约定、编码规范、验证方式、注意事项等提供给 Agent。」
  - `cn/docs/agents.md:69-70` 「用户全局指令~/.zcode/AGENTS.md适合写入跨项目通用的个人偏好、协作方式和常用约定。」「Workspace 指令当前 Workspace 中的 AGENTS.md适合写入当前项目专属的工程约定。」
- claim：兩來源拼接順序＝全域在前、工作區在後；工作區視為主要專案來源；兩者皆無則不注入。
  - `cn/docs/agents.md:71` 「如果两个来源都存在，ZCode 会先拼接用户全局指令，再拼接工作区指令；工作区指令会被视为当前任务的主要项目来源。如果两个来源都不存在，则不会注入项目指令内容。」
- claim：CLAUDE.md 不被持續讀取；Claude Code 專案僅 onboarding 一次性遷移複製到 AGENTS.md。
  - `cn/docs/agents.md:72` 「CLAUDE.md 不作为 ZCode Agent 后续运行时持续读取的项目指令文件。对于已有 Claude Code 项目，ZCode 只会在 onboarding 阶段做一次性迁移，将已有内容复制到 AGENTS.md，迁移后以 AGENTS.md 为准。」
- claim：不合併多層 AGENTS.md、不掃子目錄、不展開 @import / @include、不依任務類型選規則檔。
  - `cn/docs/agents.md:78` 「提示：ZCode 只读取用户全局 AGENTS.md 和当前 Workspace 的 AGENTS.md，不会合并多个层级的 AGENTS.md。当前也不会扫描子目录、展开 @import / @include，或根据任务类型自动选择规则文件。」
- claim：subagent 自 v3.7.1 起預設注入兩份 AGENTS.md，可由 `injectAgentsMd: false` 關閉；內建 Explore 預設不注入；v3.7.1 之前不注入。
  - `cn/docs/subagents.md:92` 「自 v3.7.1 起，子智能体默认注入用户级 ~/.zcode/AGENTS.md 与工作区 AGENTS.md，与主 Agent 保持一致；在 frontmatter 中设置 injectAgentsMd: false 可关闭。内置的 Explore 默认不注入。v3.7.1 之前的版本，子智能体不注入 AGENTS.md。」
- claim：qa 將 `~/.zcode/AGENTS.md` 定位為「全局規則」，列為換機必帶檔。
  - `cn/docs/qa.md:112` 「~/.zcode/AGENTS.md全局规则」
- claim（寫作指導）：官方明列 AGENTS.md 適合寫入的內容類型。
  - `cn/docs/agents.md:73-77` 「项目指令文件适合写入稳定、可复用的团队约定，例如：」「项目的技术栈、目录结构和关键模块说明。」「代码风格、命名规范和提交前需要执行的验证命令。」「对高风险文件、生产配置、权限操作的额外注意事项。」「团队希望 Agent 遵守的协作方式，例如先给计划、少做无关重构、优先使用现有工具链。」

## 軸 2 Rules 機制

- claim：**無獨立 rules 機制**——沒有 rules 目錄、rules 檔載入點的任何記載；agents.md:78 反而明說「不会…根据任务类型自动选择规则文件」（rg `rules|规则` 全鏡像命中均屬其他語境：repo-wiki 安全規則過濾、automations 排程規則、hooks matcher 規則、.gitignore 忽略規則，零 rules 檔機制）。
  - `cn/docs/agents.md:78` 「当前也不会扫描子目录、展开 @import / @include，或根据任务类型自动选择规则文件。」
- claim：行為約束的官方載體三分法＝AGENTS.md（手寫、進 repo）／Memory（Agent 自動提煉、本機）／Hooks（事件注入）。
  - `cn/docs/agents.md:83-86` 「AGENTS.md项目记忆」「谁来写你手写Agent 自动提炼」「存在哪项目仓库里，跟着代码走只存在你本机，不进 Git」「适合什么团队约定、编码规范这类需要评审和共享的规则协作过程中积累的零散事实」
  - `cn/docs/hooks.md:35` 「Hook 用来在特定事件时机自动执行动作——在会话开始时注入团队约束、在工具调用前做安全检查、在模型准备结束时校验产出。」
- claim：團隊共享的注入需求官方指引走插件分發（因專案級 hooks 被忽略，見軸 6）。
  - `cn/docs/hooks.md:58` 「需要团队共享的 Hook，请改用插件分发（随插件安装、可随仓库版本管理），或让成员各自配置用户级 Hook。」

## 軸 3 Memory

- claim：Memory 預設關閉，需 v3.6.4+，入口在 設置 → 常規。
  - `cn/docs/memory.md:38` 「Memory 默认关闭，需要 ZCode v3.6.4 及以上版本，按下一节的方式开启。」
- claim：自動提取時機＝每輪對話成功結束後，後台回顧最近交流；有值得保留的就寫一個 Markdown 事實檔並更新 MEMORY.md 索引。
  - `cn/docs/memory.md:53` 「一轮对话成功结束后，后台流程会回顾最近的交流。如果发现值得保留的信息，就把它写成一个小的 Markdown 事实文件，并更新 MEMORY.md 索引；没有则什么都不保存。」
- claim（寫作指導）：官方定義「記什麼」四類——用戶／反饋／項目／參考。
  - `cn/docs/memory.md:46-50` 「用户你的身份、专长和偏好」「反馈对 Agent 工作方式的纠正或确认」「项目项目目标、约束与进展」「参考你提供过的外部资源」
- claim（寫作指導）：官方明列「刻意不記」的內容。
  - `cn/docs/memory.md:51` 「同样重要的是 Memory 刻意不记的内容：代码结构和 Git 历史（Agent 随时可以重新读取）、项目指令文件里已有的内容，以及只在当前对话内有效的临时信息。」
- claim：記憶按專案隔離，存本機 `~/.zcode/cli/memories/projects/<project>/memory/`（MEMORY.md 索引＋每條事實一檔），是普通 Markdown 檔可手編手刪。
  - `cn/docs/memory.md:54` 「记忆按项目隔离：ZCode 在一个工作区学到的内容不会带到另一个工作区。」
  - `cn/docs/memory.md:57-60` 「~/.zcode/cli/memories/projects/<project>/memory/」「├── MEMORY.md        # 索引，一行一条」「└── *.md             # 每条事实一个文件」「删除项目的记忆目录即可完全重置该项目的记忆」
- claim：記憶只在主對話生效，子智能體不讀不寫；對話中可用自然語言增刪；索引載入有大小上限、過多截斷。
  - `cn/docs/agents.md:91` 「项目记忆只在主对话里生效，子智能体不读也不写。」
  - `cn/docs/memory.md:37` 「你也可以在对话中直接管理记忆：说「记住，我们从 staging 分支发布」即可立刻保存；说「忘掉刚才说的发布分支」即可删除对应记忆。」
  - `cn/docs/memory.md:65` 「索引加载有大小上限：记忆过多时会被截断，简短的条目效果最好——自动提取本身也会保持条目精炼。」

## 軸 4 Skills

- claim：技能＝一個目錄＋一個 SKILL.md，目錄名即技能名；用戶級放 `~/.zcode/skills/<skill-name>/SKILL.md`，工作區級放 `<工作区>/.zcode/skills/`。
  - `cn/docs/skill.md:45-47` 「一个技能本质上是一个目录加一个 SKILL.md 文件。目录名就是技能名，聊天中也会用这个名字引用。」「ZCode Agent 的用户级技能目录：」「~/.zcode/skills/<skill-name>/SKILL.md」
  - `cn/docs/qa.md:101` 「工作区级：<工作区>/.zcode/skills/<技能名>/SKILL.md」
- claim：frontmatter 必含 `name` 與 `description`，缺失整個技能被忽略並產生診斷；白名單欄位為 name／description／when_to_use／license／metadata，其餘非白名單欄位被忽略。
  - `cn/docs/skill.md:58` 「frontmatter 必须包含 name 和 description，缺失时该技能会被忽略，并在设置页的诊断里给出原因。」
  - `cn/docs/plugin.md:176-182` 「name✅技能名，缺省取所在目录名」「description✅触发说明，写清「什么时候用」；最长 1024 字符」「when_to_use补充触发时机描述」「license许可证」「metadata对象，可放 author / version 等附加信息」「其余非白名单字段（如 homepage）会被忽略，不影响加载。」
- claim：description 上限 1024 字符，超出**整顆丟棄不是截斷**；SKILL.md 正文超 100KB 會被截斷載入。
  - `cn/docs/skill.md:59-60` 「description 上限 1024 字符。超出后整个技能会被丢弃（诊断显示「description 超过 1024 字符」），不是截断——请把长说明放进正文。」「SKILL.md 正文超过 100KB 时会被截断加载。」
- claim：清單預算——每輪注入所有已啟用技能的元數據（名稱＋描述摘要，單條描述最多 250 字符），全部技能共享一個固定預算；超出預算降級為只留技能名，自動觸發率明顯下降。
  - `cn/docs/skill.md:62` 「每轮对话会把所有已启用技能的元数据（名称 + 描述摘要，单条描述最多 250 字符）注入模型上下文，正文只在技能被调用时按需加载。全部技能的元数据共享一个固定预算：安装大量技能导致超出预算时，注入会降级为只保留技能名，模型将难以判断何时该用哪个技能，自动触发率会明显下降。建议只启用常用技能——停用的技能不注入上下文、也不能被调用。」
- claim：跨 harness 匯入——掃描 Claude Code、Codex CLI、OpenClaw、Augment、Windsurf 等外部技能目錄，可選軟鏈（跟隨來源變更）或複製（解耦），目標可全域或專案。
  - `cn/docs/skill.md:72,77-78` 「在 设置 -> 技能 页面右上角点击 导入 图标，ZCode 会自动扫描这些外部 Agent 的技能目录，列出可一键导入的技能。」「软链：创建指向外部技能目录的链接。ZCode 会跟随来源目录的后续变更，但该技能依赖来源路径持续可用。」「复制：把外部技能复制成 ZCode 内的独立副本，与来源解耦，来源后续的修改不会再同步过来。」
- claim：分發無獨立技能市場，打包成插件（技能必須單層目錄，嵌套分組不被識別）。
  - `cn/docs/skill.md:70` 「ZCode 没有独立的技能市场。想把一组技能分发给团队，可以把它们打包成插件（skills/<技能名>/SKILL.md 的单层目录结构），通过插件市场分发……注意插件内的技能必须放在单层目录下，嵌套分组目录里的技能不会被 Agent 识别。」

## 軸 5 Agents（subagents）

- claim：內建兩個——general-purpose（完整工具權限）與 Explore（只讀）；自定義子智能體為 **用戶級 Beta**，存 `~/.zcode/agents/<name>.md`，暫不支援工作區／專案級。
  - `cn/docs/subagents.md:35` 「ZCode 内置了 general-purpose（通用型） 和 Explore 子智能体，现在你还可以在设置中创建自己的 用户级子智能体。」
  - `cn/docs/subagents.md:94` 「仅限用户级。 当前 Beta 管理的是 全局 / 用户级 子智能体，存放在 ~/.zcode/agents/。暂不支持在设置中创建或编辑 工作区 / 项目级 子智能体。」
- claim：定義檔＝帶 frontmatter 的 Markdown，正文即系統提示詞；欄位 camelCase 大小寫敏感。
  - `cn/docs/subagents.md:74` 「子智能体定义文件是带 frontmatter 的 Markdown，正文即系统提示词。除了表单里能配置的字段，手工编辑时还支持以下字段（camelCase，大小写敏感）：」
- claim：欄位清單——name/description 必填（缺略忽略＋診斷）、model（inherit 或不填跟隨主 Agent）、thoughtLevel（**欄位名不是 reasoningEffort**，不認識的欄位靜默忽略）、color、tools/disallowedTools、maxTurns、injectAgentsMd、mcpServers。
  - `cn/docs/subagents.md:76-83` 「name / description必填，缺失时该定义文件会被忽略并产生诊断。」「model指定具体模型；写 inherit 或不填表示跟随主 Agent 当前模型。」「thoughtLevel思考强度档位（如 high）。仅在同时配置了具体 model 时生效……注意字段名不是 reasoningEffort——不认识的字段会被静默忽略，不报错。」「tools / disallowedTools可用 / 禁用工具列表」「maxTurns单次调用的最大轮数（正整数）。」「injectAgentsMd是否注入 AGENTS.md，默认注入」「mcpServers声明该子智能体依赖的 MCP 服务名列表（精确匹配）；声明的服务未连接时，调用会直接失败。」
- claim：快照制——修改定義檔或設置頁調整後須新建會話才生效，已啟動會話不熱更新；唯一例外是切換主會話模型時未指定 model 的子智能體立即跟隨。
  - `cn/docs/subagents.md:84` 「生效时机：修改定义文件、或在设置页调整子智能体的模型 / 思考强度后，需要新建会话才会生效，已启动的会话不热更新。例外是切换主会话模型——未指定 model 的子智能体在后续调用中会立即跟随新模型。」
- claim：巢狀禁令——子智能體內不能再派發子智能體；另有 MCP 可見性邊界（只看到主會話啟動時已連接的服務）。
  - `cn/docs/subagents.md:90` 「另外两条边界：子智能体只能看到主会话启动时已连接的 MCP 服务，会话中途新连接的服务对子智能体不可见（新建会话即可）；子智能体内不能再派发子智能体。」
- claim：tools 自訂白名單勾選只含九個內建工具（勾選自訂後 MCP 全不可用）；手工編輯可寫全名 `mcp__<服務名>__<工具名>`，通配寫法無效且靜默忽略。
  - `cn/docs/subagents.md:88-89` 「设置页的勾选列表只包含内置工具（Read / Grep / Glob / Bash / Edit / Write / WebFetch / WebSearch / TodoWrite），因此勾选自定义后 MCP 工具会全部不可用」「把工具全名逐个写进 tools，格式为 mcp__<服务名>__<工具名>。通配写法（如 mcp__server__*）无效，会被静默忽略。」
- claim：後台 Explore 僅只讀工具；內建角色不可編輯正文／刪除／停用，但可單獨指定模型與思考強度。
  - `cn/docs/subagents.md:101` 「出于安全考虑，后台运行的 Explore 子智能体 只有只读工具（读取文件、按文件名查找、按内容搜索），不能修改任何东西。」
  - `cn/docs/subagents.md:95` 「内置角色不可删除或停用。 general-purpose 和 Explore 不能编辑正文、删除或停用，名称也不能被复用」

## 軸 6 Hooks＋設定

- claim：Hook 是本地子進程協議——stdin 寫一行 JSON，以退出碼＋stdout JSON 回傳；七個事件（SessionStart、UserPromptSubmit、PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、Stop）。
  - `cn/docs/hooks.md:36` 「Hook 本质上是一个本地子进程协议：ZCode 向进程的 stdin 写入一行 JSON，进程通过退出码和 stdout JSON 返回结果。」
  - `cn/docs/plugin.md:296` 「当前支持 SessionStart、UserPromptSubmit、PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、Stop 七个事件。」
- claim：user-level hooks 住 `~/.zcode/cli/config.json` 且必須 `hooks.enabled: true`；**專案級 hooks 整體忽略**（無論 enabled 值，日誌記 `config_project_hooks_ignored`，設置頁已隱藏工作區入口）。
  - `cn/docs/hooks.md:55` 「~/.zcode/cli/config.json当前用户的所有工作区必须在该文件中设置 hooks.enabled: true」
  - `cn/docs/hooks.md:58` 「项目级 Hook 当前不会执行。 出于安全策略，写在 <workspace>/.zcode/config.json 或 <workspace>/zcode.json 里的 hooks 配置在当前版本会被整体忽略（无论 hooks.enabled 是否为 true，日志中记为 config_project_hooks_ignored）」
- claim：config.json hooks 結構（根級 hooks.enabled/timeoutMs/maxOutputBytes/events；事件下 matcher 組陣列；每條 type/command/args/enabled/timeoutMs）。
  - `cn/docs/hooks.md:62-84` 範例原文（JSON 結構：根級 `hooks.enabled/timeoutMs/maxOutputBytes/events`；`PreToolUse` 下 matcher 組陣列；每條 `type: process`＋`command`＋`args`＋`enabled`＋`timeoutMs`）
- claim：執行順序 user Hook → 插件 Hook；session 啟動捕獲快照，修改不熱更新。
  - `cn/docs/hooks.md:59-60` 「执行顺序是 user Hook → 已启用插件 Hook。同一来源内按数组顺序执行。」「每个 session 启动时会捕获一份 Hook 配置快照。修改文件、在设置页保存或启停插件后，请新建 session 验证」
- claim：遷移兼容——`.agents/settings.json` / `.claude/settings.json` 只讀展示不執行，須設置頁顯式導入；stdin 同時帶 camelCase 與 snake_case alias。
  - `cn/docs/hooks.md:57` 「.agents/settings.json / .claude/settings.json迁移旧配置只读展示，不直接执行；需在设置页显式导入到 .zcode」
  - `cn/docs/hooks.md:151` 「同一份输入同时保留 ZCode camelCase 字段与 Claude Code snake_case alias，旧插件可以继续读取 snake_case。」
- claim：退出碼 0＝成功解析、2＝阻斷快捷、其他非零＝可恢復失敗不崩 turn；Stop 連續 block 最多 3 次；聚合時 deny > ask > allow。
  - `cn/docs/hooks.md:224-227` 「0成功，解析 stdout」「2阻断快捷方式；在可阻断事件中产生 block / deny」「其他非零当前 Hook 可恢复失败，记录诊断，turn 不会因此整体崩溃」
  - `cn/docs/hooks.md:222` 「连续续跑达到 3 次后会强制结束，防止无限循环。」
  - `cn/docs/hooks.md:196` 「多个 Hook 聚合时，deny 优先于 ask，ask 优先于 allow。」
- claim：設定檔地圖（qa 換機清單）——`~/.zcode/cli/config.json`（MCP/權限/插件技能開關/Hooks）、`~/.zcode/v2/config.json`（模型供應商）、`~/.zcode/AGENTS.md`、`~/.zcode/agents|skills|commands/`；MCP 用戶級鍵 `~/.zcode/cli/config.json` `mcp.servers`，工作區級 `<项目根>/.zcode/config.json`。
  - `cn/docs/qa.md:110-113` 「~/.zcode/cli/config.jsonMCP 服务、权限默认值、插件与技能开关、Hooks 等 Agent 配置」「~/.zcode/v2/config.json模型供应商配置（含 API Key、Base URL、模型列表）」「~/.zcode/AGENTS.md全局规则」「~/.zcode/agents/、~/.zcode/skills/、~/.zcode/commands/自定义子智能体、技能、命令」
  - `cn/docs/mcp-services.md:73-74` 「用户（所有工作区可用）~/.zcode/cli/config.jsonmcp.servers」「工作区（仅当前项目可用）<项目根>/.zcode/config.jsonmcp.servers」

## 軸 7 官方寫作哲學

- claim：AGENTS.md 內容選擇原則——寫「穩定、可複用」的約定，且最重要的放 Workspace 層。
  - `cn/docs/agents.md:73` 「项目指令文件适合写入稳定、可复用的团队约定」
  - `cn/docs/agents.md:78` 「建议将最重要、最稳定的项目规则放在当前 Workspace 的 AGENTS.md 中。」
- claim：Skill description 是觸發機制的核心——必須寫清「什麼時候用」，越具體越可靠；長說明放正文不塞 description。
  - `cn/docs/skill.md:59` 「不是截断——请把长说明放进正文。」
  - `cn/docs/skill.md:66` 「描述写得太泛：description 没有写清「什么时候用」，模型无从判断。触发条件写得越具体，自动触发越可靠。」
  - `cn/docs/plugin.md:178` 「description✅触发说明，写清「什么时候用」；最长 1024 字符，越准越易被自动调用」
  - `cn/docs/plugin.md:106` 「技能skills/<名>/SKILL.md，frontmatter 写清 name / description，描述越准越易被自动触发」
- claim：技能數量是上下文預算問題——官方處方是「只啟用常用技能」。
  - `cn/docs/skill.md:62` 「建议只启用常用技能——停用的技能不注入上下文、也不能被调用。」
- claim：Command vs Skill 分工——一句簡單提示詞用 Command，一套完整工作方法做 Skill；Skill 四大適配訊號（固定流程／固定輸出格式／背景知識清單模板範例／跨專案跨對話重用）。
  - `cn/docs/skill.md:95-99` 「任务有固定流程，例如 code review、接口排查、发版说明、测试报告。」「团队对输出格式有固定要求。」「任务需要附带背景知识、检查清单、模板或示例文件。」「同一个能力会在多个项目或多次对话里重复使用。」「如果只是保存一句简单提示词，可以优先使用 Command；如果需要一套完整工作方法，就更适合做成 Skill。」
  - `cn/docs/commands.md:62` 「如果只是保存一段简单提示词，使用 Command 即可；如果流程需要脚本、模板或示例文件，可以考虑使用 Skill。」
- claim：subagent 的 description 決定自動選用率；系統提示詞職責＝角色、邊界、規則。
  - `cn/docs/subagents.md:69` 「描述展示给主 Agent 的简短说明。主 Agent 依据它判断何时调用该子智能体——描述越准确，越容易在合适的任务中被自动选用。」
  - `cn/docs/subagents.md:71` 「系统提示词描述这个子智能体的角色、边界和规则。」
- claim：Memory 寫入哲學——可再讀取的不記（代碼結構/Git 歷史）、指令檔已有的不記、臨時資訊不記；條目越短越好。
  - `cn/docs/memory.md:51` 「Memory 刻意不记的内容：代码结构和 Git 历史（Agent 随时可以重新读取）、项目指令文件里已有的内容，以及只在当前对话内有效的临时信息。」
  - `cn/docs/memory.md:65` 「简短的条目效果最好——自动提取本身也会保持条目精炼。」

## 官方未提及清單

- 軸 1：AGENTS.md 尺寸／截斷限制——零記載（100KB 截斷只存在於 SKILL.md 正文 skill.md:60；**注意：ai-rules 側 rules/AGENTS.md 記有 ZCode 實測 100KiB 硬編碼截斷——那是實機 reverse-engineer 事實，非官方文檔記載**）
- 軸 1：多層／子目錄 AGENTS.md 合併解析——官方明說不支援（agents.md:78），非缺載
- 軸 2：獨立 rules 目錄／規則檔機制——無（agents.md:78 明說不自動選規則檔）
- 軸 4：SKILL.md 的 `model`、`allowed-tools` 欄位——技能白名單無此二欄（plugin.md:176-182）；`allowed-tools` 只存在於 command .md frontmatter（plugin.md:169）
- 軸 5：subagent frontmatter 的 `effort` 欄位——不存在，欄位名為 `thoughtLevel` 且明文警告「字段名不是 reasoningEffort」（subagents.md:78）
- 軸 5：工作區／專案級子智能體——明說暫不支援（subagents.md:94）
- 軸 6：專案層 hooks 執行——明說整體忽略（hooks.md:58），非缺載
- 軸 7：AGENTS.md 結構章法、signal/noise、長度預算等深度寫作方法論——文檔定位是產品設定指南而非 authoring guide；深度寫作指導僅 skill.md 三小節與 plugin.md 欄位速查表承載
- 鏡像結構：en/ 側同構對照不可行——`en/docs/` 僅 welcome.md 一檔（fd 實測）
