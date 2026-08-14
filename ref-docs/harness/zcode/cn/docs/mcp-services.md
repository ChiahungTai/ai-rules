MCP | ZCODE Docs
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
MCP
MCP（Model Context Protocol）可以把文件系统、浏览器、记忆、数据库等外部能力接入 Agent。ZCode 会统一管理 ZCode Agent 使用的 MCP 服务器配置。
给 ZCode Agent 配好常用 MCP 后，Agent 在长任务里可以更稳定地使用项目文件、浏览器自动化、记忆等工具，配合 GLM 5.3 系列模型时也更适合处理连续、多步骤的开发任务。
列表分组
MCP 列表按来源分为两组：
已配置 MCP 服务器：你手动添加的 MCP 服务，可直接编辑、删除或启用/停用。
Plugin MCP 服务器：随插件一起安装的 MCP 服务，由对应插件统一管理。
列表中每个 MCP 都会展示名称、来源、启动方式和命令。
新建 MCP 服务器
进入 设置 -> MCP 服务器，点击右上角 新建 MCP 服务器。表单 模式适合快速填写常见 stdio 服务：
选择 作用域：用户（所有工作区可用）或 工作区（仅当前项目可用）。
填写名称，例如 memory。
类型选择 stdio（本地命令），也支持 SSE 和 HTTP 类型的远程服务。
填写命令，例如 npx，以及参数，例如 -y @modelcontextprotocol/server-memory。
如服务需要密钥或路径，再展开 环境变量（可选） 填写。
点击 添加 后回到列表，并确认开关处于启用状态。
除 stdio 本地命令外，还有两种录入方式：接入远程服务时，类型选择 HTTP 或 SSE，填写服务地址即可，需要鉴权的服务可展开 请求头（可选） 补充 Authorization 等信息；如果已有现成 JSON 配置，则切换到 完整配置 模式直接粘贴，支持 {"server-name": {...}} 和 {"mcpServers": {...}} 两种常见结构。
需要 OAuth 授权的服务
有些远程 MCP 服务（例如 Figma 的官方 MCP）不接受固定密钥，而是要求你在浏览器里授权一次。为这类服务开启 OAuth 后，剩下的交给 ZCode。
授权需要你点一下：设置 → MCP 里对应的服务行会出现 打开授权 按钮，点击后用系统浏览器打开授权页面，你确认完，ZCode 会自动重连并加载它的工具。ZCode 不会擅自弹出浏览器窗口，主动权在你。
插件自带的 MCP 服务同样支持，列表行会显示「需要授权」。
两点需要知道：这只适用于 HTTP 和 SSE 类型的远程服务，本地服务仍然通过环境变量传凭据；如果新建会话时授权一直没完成，ZCode 只会把这一个服务标记为失败，不会拖住整个会话。之后如果换了服务地址或授权范围，需要重新授权一次。
从外部 Agent 导入 MCP 服务器
如果你已经在 Claude Code、Codex CLI、OpenCode 等外部 Agent 中配置了一批 MCP 服务器，不需要在 ZCode 里逐个重建。在 MCP 服务器 页面右上角点击 导入 图标，ZCode 会自动扫描这些外部 Agent 的配置文件，把已有的 MCP 服务器集中列出，供你一次性导入。
ZCode 会从以下来源发现可导入的 MCP 服务器：
Claude Code：~/.claude/settings.json
Codex CLI：~/.codex/config.toml
OpenCode：~/.config/opencode/opencode.json
通用 .agents：~/.agents/mcp.json
操作步骤：
在 ZCode 设置中进入 MCP 服务器 页面。
点击右上角的 导入 图标，打开「导入外部 Agent MCP 服务器」弹窗。
在弹窗右上角选择导入的 作用域（全局或当前工作区）。
勾选要导入的服务器，或点击 全选；弹窗会实时显示发现的可导入数量与已选数量。
点击 导入 完成导入，服务器会出现在列表中并默认启用。
导入后的服务器会和手动添加的服务一样保存在对应作用域的 .zcode 配置文件中，可以在 ZCode 内继续编辑、启停或删除，原外部 Agent 的配置文件不会被修改。
配置文件与默认读取路径
设置面板只是入口之一。ZCode 按固定的目录约定读取 MCP 配置文件，你也可以直接手工编辑这些文件来批量管理服务：
作用域文件路径配置键
用户（所有工作区可用）~/.zcode/cli/config.jsonmcp.servers
工作区（仅当前项目可用）<项目根>/.zcode/config.jsonmcp.servers
用户 · .agents 兼容~/.agents/mcp.jsonmcpServers
工作区 · .agents 兼容<项目根>/.agents/mcp.jsonmcpServers
注意：用户级原生配置在 .zcode/cli/ 目录下，而工作区级直接在 .zcode/ 目录下，两个文件同名为 config.json 但层级不同。
ZCode 原生配置（config.json）的 MCP 部分形如：
{
"mcp": {
"servers": {
"memory": {
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-memory"],
"env": {}
}
}
}
}
.agents/mcp.json 则使用业界通用的 {"mcpServers": {...}} 结构，便于和其他支持 .agents 目录约定的 AI 工具共享同一份 MCP 配置。
读取规则与优先级
工作区优先加载：打开工作区时先读取工作区作用域的配置，再读取用户作用域，两边的服务都会出现在列表中。
同作用域内 .zcode 强优先：只要 .zcode 配置文件里读到了任何 MCP 服务，同作用域的 .agents/mcp.json 就会被整体跳过，不做合并。.agents 只在 .zcode 没有配置任何服务时才作为兜底来源生效。
启用状态记录在配置对象内：在列表里停用某个 MCP 时，ZCode 会向该服务的配置对象写入 "enable": false；没有这个字段即视为启用。
面板写入永远落在 .zcode：通过设置面板新增或编辑的服务，始终写回对应作用域的 .zcode 原生配置文件，.agents 文件不会被修改。
提示：如果你在 .agents/mcp.json 里维护了一批服务，又在设置面板里新建了一个服务，原来 .agents 里的服务会因为 .zcode 优先规则而整体失效。此时把 .agents 里的配置合并进 .zcode 配置文件即可。
工作区 MCP 会自动连接
写在项目配置里的 MCP 服务，在会话启动时会和用户级服务一样 自动连接，不需要你每次手动授权。这让团队把 MCP 配置提交进仓库后，成员克隆下来就能直接用。
方便之外有件事需要留意。打开一个项目，就等于连上了它配置里写的所有 MCP 服务，而 MCP 服务能执行命令、读写你的文件、访问网络。所以打开来路不明的仓库之前，建议先看一眼它的 .zcode/config.json，确认里面的 MCP 配置你都认得。
同名服务以你自己的配置为准，项目配置覆盖不了它。
推荐配置
下面这些推荐优先使用智谱相关 MCP，点击卡片可直达智谱官方文档查看完整说明与配置方法：
zai-mcp-server：提供视觉理解能力，让 Agent 可以分析图片、截图和界面信息。
web-search-prime：提供联网搜索能力，让 Agent 获取最新资料和外部信息。
web-reader：提供网页读取能力，让 Agent 解析网页正文、结构和关键信息。
这些服务通常需要配置智谱 API Token。团队内如果有统一 MCP 规范，建议用 用户 作用域共享通用服务，再按项目需要在 工作区 作用域补充专用服务，避免配置互相污染。
下一步
Command
把常用提示词和流程沉淀成可复用命令。
Skill
通过 Markdown 文件让 Agent 掌握特定的工作方式。
On this page
列表分组
新建 MCP 服务器
需要 OAuth 授权的服务
从外部 Agent 导入 MCP 服务器
配置文件与默认读取路径
读取规则与优先级
工作区 MCP 会自动连接
推荐配置
下一步
