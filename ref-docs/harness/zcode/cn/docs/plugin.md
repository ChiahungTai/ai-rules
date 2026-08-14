Plugin | ZCODE Docs
开始使用
ZCode for GLM-5.3
安装
连接模型
用户反馈与支持
核心功能
ZCode Agent
目标模式
浏览器自动化
任务与文件管理
Wiki
Memory
自动化
闲时任务
编辑历史对话
远程开发
Remote Control
Bot Channel
子智能体
Plugin
Skill
MCP
Command
Hooks
使用统计
深度集成
安全操作确认
智能体开发环境工具
帮助
快捷键表
常见问题解答 (Q&A)
核心功能复制全文
Plugin
Plugin 用来扩展 ZCode 的能力。一个插件可以把技能、命令、子智能体、MCP 服务器等能力打包在一起，让团队把可复用的工具沉淀成统一的扩展包，在同一个工作台里一键启用。
插件里有什么
一个插件可以同时包含多种能力。ZCode 会根据插件目录里的内容自动识别它包含哪些组件，并在列表中以标签或数量的形式展示：
组件说明
Skill（技能）教 Agent 如何完成特定任务的技能文件
Command（命令）可通过 / 调用的快捷命令
Agent（子智能体）随插件一起注册的子智能体
MCP 服务器随插件注册的外部工具服务，会出现在 MCP 列表的 Plugin MCP 服务器 分组中
Hook（钩子）在特定事件触发的自动化钩子
启用插件后，它附带的可运行组件——技能、命令和 MCP 服务器——会注册到当前工作台；停用后这些组件也会一起停用。
浏览与安装插件
进入 设置 -> 插件，看到的就是插件商店。顶部是一个搜索框，输入关键词可以跨所有来源查找插件；下方分成 公开 与 个人 两个分段：
公开：ZCode 收录的插件目录，顶部是精选推荐，其余按「开发者工具」「生产力」「实用工具」「指南」「模板」等类别分组，分组内容多时可以展开查看全部。
个人：你自己添加的插件市场，先展示推荐条目，其余按市场名称分组。ZCode 已经为你预置了 Claude Code 的插件市场，不用自己添加就能在这个分段里浏览和安装；想接入别的来源时，再用右上角的 创建 添加市场源。
插件页需要在打开工作区后才可用。如果提示「打开一个工作区以管理插件」，先打开任意项目 / 工作区即可。公开目录来自 GitHub，网络访问不畅时目录、详情和安装都可能加载失败；列表没及时更新时，点右上角的 刷新 重新拉取。
找到想要的插件后，点卡片上的 安装 即可，状态会依次变为「安装中…」和「已安装」。新装的插件默认启用，组件立即可用。
点击任意插件可打开详情页，ZCode 会加载它实际包含的技能、命令、子智能体、MCP 服务器和 Hooks，并附上开发者、类别、版本、网站等信息，让你在安装前先看清它会带来哪些能力。已安装的插件如果有新版本，详情页底部也会直接给出更新入口。
添加自己的插件市场
你不必局限于公开目录。点右上角的 创建 -> 添加插件市场，在弹层里指定一个来源即可：
GitHub 仓库（例如 owner/repo 或其链接）
Git URL
本地的市场清单文件或目录，也可以直接把文件夹拖进来，或点 选择目录
添加前 ZCode 会先校验这个市场，成功后它发布的插件会以市场名称分组出现在 个人 分段里，你可以像其他插件一样浏览安装。
点搜索框上方的齿轮图标可以打开 市场源 面板，查看每个市场收录了多少插件、上次更新时间，并单独 刷新该市场 或 移除该市场。ZCode 自带的官方目录只能刷新，不会被移除。
想自己做一个插件或搭建团队市场？见下方 开发自己的插件，里面有插件目录结构、plugin.json / marketplace.json 的字段速查和完整 JSON 用例。
内置插件
ZCode 内置了一批 官方插件。其中两个开箱即用、默认启用；其余随包内置，需要时再开启即可。
插件能力默认状态
document-skills用于生成 DOCX、PDF 等文档的内置技能默认启用
skill-creator创建和编辑你自己的本地技能默认启用
android-emulatorAndroid 开发工作流与模拟器自动化默认关闭
ios-simulatoriOS 开发工作流与模拟器自动化（macOS）默认关闭
restore-legacy-sessions迁移并恢复旧版本的会话默认关闭
其中最值得一提的是 android-emulator 和 ios-simulator 这两个移动开发插件——启用后，ZCode Agent 就能直接驱动 Android 模拟器或 iOS 模拟器，把构建运行、安装启动、界面验证等环节都放进同一条对话流里，不必再在 IDE、模拟器和命令行之间来回切换，移动开发体验更连贯、更高效。
管理插件
装过插件后，搜索框下方会出现一条 已安装 图标带，点图标直接进入该插件详情。点这一行右侧的齿轮图标，则进入 管理已安装 页面，本机所有插件会以列表形式展开，显示名称、版本、来源标签和它包含的组件数量。
在这里可以完成几件事：
通过右上角的筛选器按启用 / 停用状态过滤。
查看插件来源标签，例如 内置，或某个市场的名称。
通过右侧开关启用或停用插件。
点 检查更新，让 ZCode 拉取各插件的最新版本，有更新的插件会带上标记。注意版本对比的口径：「最新版本」取自市场 marketplace.json 里该插件条目声明的 version，「已安装版本」取自插件自身的 plugin.json。如果市场条目发版时忘了更新 version，即使插件代码已更新也不会提示可更新；自建市场发版务必同步修改 marketplace.json。检测结果基于本地缓存的市场清单，怀疑不准时先到市场源面板 刷新该市场 再检查。
点击插件条目，查看它包含的具体技能、命令、MCP 等组件，并可在此卸载。内置官方插件同样可以卸载。
由于插件变更需要重新加载 Agent 运行环境，启用或停用插件后，ZCode 会自动刷新受影响的技能和会话，让改动生效。停用插件后，它的全部组件会立即从会话中移除，再次启用即可恢复。
停用还是卸载？ 停用只是让插件暂时不生效，随时可以开回来；卸载则把它从列表中移除。内置插件的安装包随应用一起分发，卸载它时 ZCode 会记录一条屏蔽标记，应用升级后也不会把它装回来——想重新使用，在市场里重新安装即可。
在远程工作区里，本机装的插件默认不会跟过去。连上 SSH 或 WSL 远程后，可以用工作区标题栏 同步 下拉里的 同步 Plugin 把它们搬过去，管理已安装 页面右上角也有同样的入口，详见 远程开发 → 把本地配置同步到远端。
配置插件
有些插件需要你先提供参数才能工作，例如默认设备、开关或路径。点开插件详情，展开底部的 高级信息，在 配置 区填写可填项——必填项会标注「必填」，填完点 保存配置。
标记为敏感的项（例如 API 密钥）会提示「该值需要安全存储接入后才能配置」，当前暂不支持在界面里直接填写。遇到这类插件，按其说明在系统层面准备好密钥即可。
装好的插件怎么用
插件启用后，它带来的能力会自动出现在客户端对应位置，无需额外设置：
能力在哪里用
技能合适时机会自动触发；也可在输入框输入 /，从「技能」分组手动选用。在 设置 -> 技能 的「Plugin 技能」分组可统一查看。
命令在输入框输入 /，从「命令」分组选用，可输入关键词搜索命令或技能。
子智能体会话中可被自动调度执行任务；在 设置 -> 子智能体 的「插件子智能体」分组可查看（来自插件，只读）。
MCP 服务器在 设置 -> MCP 中显示为 Plugin MCP 服务器，随插件启停自动加载。
开发自己的插件
只需会写 JSON 和 Markdown，不用改 ZCode 本体。做好后，通过上面的 添加自己的插件市场 把本地目录加进来，即可在客户端里直接安装测试。
一个插件长什么样
插件就是一个文件夹：根目录放一份清单 plugin.json，再按需放各类组件目录（全部可选）。
my-plugin/
├── .zcode-plugin/
│   └── plugin.json    清单（唯一必需）
├── commands/          斜杠命令，每个一个 .md
├── skills/            技能，每个子目录含 SKILL.md
├── agents/            子智能体 .md
├── hooks/hooks.json   钩子
└── .mcp.json          MCP 服务声明
清单位置按优先级查找：.zcode-plugin/plugin.json（推荐）→ .claude-plugin/plugin.json（兼容 Claude Code）。
五种组件的写法：
组件格式与位置
命令commands/*.md，YAML frontmatter + 正文；正文用 $ARGUMENTS 接收参数
技能skills/<名>/SKILL.md，frontmatter 写清 name / description，描述越准越易被自动触发
子智能体agents/*.md，frontmatter 必填 name / description，正文即其 system prompt
Hookshooks/hooks.json，在特定事件时机自动执行；随插件启停，详见 Hooks
MCP 服务根目录 .mcp.json 或清单 mcpServers，接入外部工具，键名自动加命名空间避免冲突
最小清单只需要一个 name：
{
"name": "hello-world",
"version": "0.1.0",
"description": "我的第一个插件"
}
plugin.json 字段速查
字段必填含义
name✅插件名，须匹配 ^[a-z0-9][a-z0-9._-]{0,127}$（小写字母 / 数字开头，可含 . _ -，1–128 字符）
version版本号，缺省 0.0.0，建议语义化版本
description一句话描述，显示在插件管理界面
author作者，可写字符串或对象 { name, email, url }
homepage / repository主页与仓库地址
license许可证，如 MIT
keywords关键词数组
commands / skills / hooks / mcpServers / agents各类组件声明，可写目录路径字符串、路径数组或内联对象
dependencies依赖的其他插件，写 name@market 或同市场内裸 name
userConfig用户可配置项（见下表）
清单里写了 channels / lspServers / outputStyles / settings 这几个字段时，当前运行时仅登记、不执行，会给出诊断提示，不影响其它组件加载。
userConfig 里的每一项都会出现在插件详情弹窗的 配置 区，供用户在界面里填写：
字段含义
type类型：string / number / boolean / directory / file
title界面上显示的标题
description配置项说明
default默认值
required布尔；是否必填，界面标「必填」
sensitive布尔；敏感值，界面打码且暂不支持在界面直接填写
敏感配置（sensitive）的值可以在 MCP 声明里用 ${user_config.键} 引用。
marketplace.json 字段速查
「插件市场」是一份目录清单，告诉客户端有哪些插件可装、各自在哪。
顶层字段：
字段必填含义
name✅市场名，命名规则同插件名
description市场描述
plugins✅插件条目数组（见下表）
pluginRoot解析各条目 source 时的基准目录，相对市场根目录
allowCrossMarketplaceDependenciesOn允许跨市场依赖的市场名数组
plugins[] 每个条目：
字段必填含义
name✅插件名
source插件代码在哪。最常用是相对路径字符串，也可写对象（见下表）
description / version展示用描述与版本
category / tags分类（字符串）与标签（字符串数组），便于检索
dependencies依赖的其他插件，写 name@market 或同市场内裸 name
strict布尔；对该条目做更严格的校验
source 的几种写法：
写法含义
"./plugins/hello"最常用。相对市场根目录的子目录（插件与市场同仓库）
{ "source": "directory", "path": "/abs/path" }本地绝对路径目录
{ "source": "github", "repo": "owner/repo", "path": "subdir", "ref": "main" }从 GitHub 仓库取，可指定子目录与分支
{ "source": "git", "url": "https://...git", "path": "subdir", "ref": "..." }从任意 Git 仓库取
{ "source": "file", "path": "..." }读取一个本地清单文件
{ "source": "url", "url": "https://.../marketplace.json" }指向一个 JSON 文件的 HTTP 地址，可带 headers
{ "source": "npm", "package": "..." }从 npm 包取
命令 .md 字段速查
commands/*.md 的 frontmatter 支持以下字段：
字段必填含义
description✅命令描述（或正文非空即可）
argument-hint参数提示，如 "[topic]"
allowed-tools逗号分隔，限制该命令可用的工具
model覆盖默认模型
skills逗号分隔，自动挂载的技能
disable-noninteractive布尔；是否在非交互模式下禁用
正文里 $ARGUMENTS 代表用户传入的全部参数，$1 / $2 代表位置参数。命令名取自文件名，须匹配 ^[a-z0-9][a-z0-9_:-]{0,63}$。
技能 SKILL.md 字段速查
skills/<名>/SKILL.md 的 frontmatter 支持以下字段：
字段必填含义
name✅技能名，缺省取所在目录名
description✅触发说明，写清「什么时候用」；最长 1024 字符，越准越易被自动调用
when_to_use补充触发时机描述
license许可证
metadata对象，可放 author / version 等附加信息
其余非白名单字段（如 homepage）会被忽略，不影响加载。
完整 JSON 用例
plugin.json（全字段）
{
"name": "ios-simulator",
"version": "1.2.0",
"description": "iOS 模拟器开发循环：技能 + 命令 + MCP + 钩子",
"author": { "name": "你的名字", "email": "you@example.com", "url": "https://example.com" },
"homepage": "https://example.com/ios-simulator",
"repository": "https://github.com/your-team/ios-simulator",
"license": "MIT",
"keywords": ["ios", "simulator", "mobile"],
"commands": "commands",
"skills": ["skills", "extra-skills"],
"agents": "agents",
"hooks": "hooks/hooks.json",
"mcpServers": ".mcp.json",
"dependencies": ["skill-creator@zcode-plugins-official"],
"userConfig": {
"api_key": {
"title": "API 密钥",
"description": "访问第三方服务用",
"type": "string",
"required": true,
"sensitive": true
},
"default_device": { "title": "默认设备", "type": "string", "default": "iPhone 16" },
"max_retries": { "type": "number", "default": 3 },
"verbose": { "type": "boolean", "default": false },
"workspace_dir": { "type": "directory" },
"config_file": { "type": "file" }
}
}
commands / skills / hooks / mcpServers / agents 三种写法均可——目录字符串（如 "commands"）、路径数组（如 ["skills", "extra-skills"]）、或直接内联对象。上例分别演示了字符串、数组与文件路径。
marketplace.json（全字段 + 所有 source 写法）
{
"name": "my-market",
"description": "团队内部插件市场",
"pluginRoot": "plugins",
"allowCrossMarketplaceDependenciesOn": ["zcode-plugins-official"],
"plugins": [
{
"name": "hello-world",
"source": "./hello-world",
"description": "打招呼插件",
"version": "0.1.0",
"category": "demo",
"tags": ["starter", "demo"],
"strict": true
},
{
"name": "from-github",
"source": { "source": "github", "repo": "your-team/another", "path": "plugins/x", "ref": "main" },
"dependencies": ["hello-world", "skill-creator@zcode-plugins-official"]
},
{
"name": "from-git",
"source": { "source": "git", "url": "https://git.example.com/x.git", "path": "sub", "ref": "v1.0" }
},
{
"name": "from-dir",
"source": { "source": "directory", "path": "/abs/path/to/plugin" }
},
{
"name": "from-url",
"source": { "source": "url", "url": "https://example.com/plugin-manifest.json", "headers": { "Authorization": "Bearer xxx" } }
},
{
"name": "from-npm",
"source": { "source": "npm", "package": "@scope/plugin" }
}
]
}
设了 pluginRoot 后，相对 source（如 "./hello-world"）以它为基准解析，即 plugins/hello-world。
hooks/hooks.json
{
"hooks": {
"SessionStart": [
{
"matcher": "startup|clear|compact",
"hooks": [
{
"type": "command",
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run.sh\" start",
"async": false,
"shell": true,
"timeout": 30,
"statusMessage": "初始化中…"
}
]
}
],
"PreToolUse": [
{
"matcher": "Bash",
"hooks": [
{
"type": "process",
"command": "node",
"args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.js"],
"timeoutMs": 5000,
"statusMessage": "校验命令…"
}
]
}
],
"PostToolUse": [
{ "hooks": [ { "type": "command", "command": "echo done" } ] }
],
"Stop": [
{ "hooks": [ { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/cleanup.sh\"", "async": true } ] }
]
}
}
当前支持 SessionStart、UserPromptSubmit、PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、Stop 七个事件。每个事件下是 matcher 组数组；process 使用 argv 执行，command 使用 shell 字符串并支持 async。标准位置 hooks/hooks.json 会自动发现，不要再在 manifest 中重复指向同一文件。插件启用后 Hook 才进入新 session，完整语义见 Hooks。
.mcp.json（stdio + http + sse）
{
"mcpServers": {
"ios-simulator": {
"type": "stdio",
"command": "node",
"args": ["${CLAUDE_PLUGIN_ROOT}/dist/mcp/server.js"],
"cwd": "${CLAUDE_PROJECT_DIR}",
"env": {
"IOS_SIM_ROOT": "${CLAUDE_PLUGIN_ROOT}",
"IOS_SIM_DEVICE": "${user_config.default_device}"
},
"enabled": true,
"timeoutMs": 60000
},
"remote-http": {
"type": "http",
"url": "https://mcp.example.com/api",
"headers": { "Authorization": "Bearer ${user_config.api_key}" },
"enabled": true,
"timeoutMs": 30000
},
"remote-sse": {
"type": "sse",
"url": "https://mcp.example.com/sse",
"headers": { "X-Token": "${user_config.api_key}" }
}
}
}
type 可省略——有 command 默认 stdio，有 url 默认 http。可用模板变量：
变量含义
${CLAUDE_PLUGIN_ROOT}插件根目录，亦可写 ${ZCODE_PLUGIN_ROOT}
${CLAUDE_PLUGIN_DATA}插件数据目录
${CLAUDE_PROJECT_DIR}当前工作目录
${user_config.键}引用 userConfig 中对应配置项的值
服务键名会自动加命名空间 plugin:<插件名>:<服务名> 避免冲突。
在客户端本地测试
本地建好插件目录，再写一份 marketplace.json，plugins[].source 用相对路径指向插件目录。
打开 设置 -> 插件，点右上角 创建 -> 添加插件市场，填该目录的本地路径（本地路径需真实存在）。
在 个人 分段找到它，点 安装 并启用，在会话里触发组件验证；改完代码回到 市场源 面板刷新该市场即可。
做一个市场分发给团队
把插件放进市场仓库的 plugins/ 目录，根目录写 marketplace.json 列出条目，推到 GitHub。队友点 创建 -> 添加插件市场 填仓库地址，即可一次拿到全部插件。
自带的官方插件是最好的范例（skill-creator 最简，ios-simulator / android-emulator 最完整）。从纯技能插件起步，跑通后再加命令、Hooks、MCP。
安全提示：启用插件就是授予代码执行信任。已启用的第三方市场插件与官方插件一样，可以执行本地进程并读取继承的 Agent 环境变量。启用前请审查来源、hooks/hooks.json 和脚本，不信任时停用或卸载插件。
下一步
Hooks
事件、输入输出契约与退出码的完整开发参考。
Command
了解 ZCode Agent 的内置命令，以及如何新建自定义命令。
Skill
通过 Skill 让 Agent 掌握特定的工作方式。
MCP
为 Agent 接入外部工具能力。
On this page
插件里有什么
浏览与安装插件
添加自己的插件市场
内置插件
管理插件
配置插件
装好的插件怎么用
开发自己的插件
一个插件长什么样
plugin.json 字段速查
marketplace.json 字段速查
命令 .md 字段速查
技能 SKILL.md 字段速查
完整 JSON 用例
plugin.json（全字段）
marketplace.json（全字段 + 所有 source 写法）
hooks/hooks.json
.mcp.json（stdio + http + sse）
在客户端本地测试
做一个市场分发给团队
下一步
