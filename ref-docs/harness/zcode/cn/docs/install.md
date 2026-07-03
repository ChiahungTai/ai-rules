安装 | ZCODE Docs
开始使用
ZCode for GLM-5.2
安装
连接模型
用户反馈与支持
核心功能
ZCode Agent
目标模式（Goal）
Remote Control
任务与文件管理
Bot Channel
编辑历史对话
子智能体
Skill
MCP 服务器
Plugin
Command
使用统计
深度集成
安全操作确认
远程开发
智能体开发环境工具
帮助
快捷键表
常见问题解答 (Q&A)
开始使用复制全文
安装
下载并安装 ZCode 桌面应用，开始体验自研 ZCode Agent 驱动的端到端开发工作流。
下载
立即下载 ZCode
适用于 macOS (Apple Silicon)
v3.2.3·最新版本
其他平台
ZCODE 适用于 macOS (Intel)ZCODE 适用于 WindowsZCODE 适用于 Windows (ARM64)ZCODE Linux 内测群
支持 macOS（Apple Silicon / Intel）、Windows（x64）；Linux 版本请通过内测群获取。
安装步骤
macOSApple Silicon / Intel
1打开下载的 ZCode.dmg 安装镜像。
2将 ZCode.app 拖动到 Applications 文件夹。
3在启动台中找到 ZCode 并启动。
WindowsWindows x64
1下载 ZCode 安装程序。
2双击运行，按照安装向导完成安装。
3从开始菜单或桌面快捷方式启动 ZCode。
Linux内测版本
1在下载区加入 Linux 内测群，获取内测安装包。
2按发行版的常规方式安装，或为安装文件添加可执行权限后直接运行。
3从应用菜单或命令行启动 ZCode。
首次启动
首次启动会进入「首次启动设置」页面，完成后在左下角点击 连接使用 进入登录页面：
点击 开始使用 ZCode 直接进入。如需迁移历史数据，可选择 数据迁移向导：目前仅支持导入 Claude Code 和 旧版 ZCode 中 ZCode Agent 的对话记录，不支持其他工具；也可以先跳过，稍后在设置中继续迁移。
进入后选择一个项目目录作为工作区。
在对话框输入一句简单指令，比如让 Agent 列出当前目录的文件，确认响应正常。
如果还没有配置模型，点击左下角 连接使用 进入登录页面，引导你 连接 Z.ai、连接 BigModel 或 使用 API Key 完成接入，详见下一节 连接模型。
故障排查
macOS 提示「ZCode 已损坏，无法打开」
在终端执行以下命令解除隔离属性后重新打开：
xattr -dr com.apple.quarantine /Applications/ZCode.app
Windows 安装时被防火墙 / 杀软拦截
暂时关闭实时防护或将安装目录加入白名单后重试。
Linux 安装文件无法运行
确认已添加可执行权限（chmod +x）；部分发行版需要额外安装 fuse 依赖。
了解更多
连接模型
为 Agent 接入 GLM 模型与 Coding Plan，开启对话与编程能力。
用户反馈与支持
遇到问题时，了解如何提供有效反馈。
常见问题解答 (Q&A)
查看安装、配置与使用中的常见疑问。
On this page
下载
安装步骤
首次启动
故障排查
了解更多
