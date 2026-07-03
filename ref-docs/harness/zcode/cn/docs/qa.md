常见问题解答 (Q&A) | ZCODE Docs
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
帮助复制全文
常见问题解答 (Q&A)
在这里，我们汇总了关于 ZCode 的产品定位、费用说明以及在使用过程中可能遇到的技术问题的解答。
1. ZCode 的产品定位是什么？
ZCode 是一个全新的智能体开发环境（Agentic Development Environment，ADE），与传统 IDE 不同，ZCode 不以手动编写代码为核心，而是让 AI Agent 成为开发的主角——您只需用自然语言描述需求，Agent 即可驱动从编码、调试到预览的完整开发流程。
ADE 平台：围绕自研 ZCode Agent 内置文件管理、终端、Git 提交及实时浏览器预览，通过自然语言指令驱动 Agent 完成全生命周期开发任务。
全上下文感知：Agent 能够深入理解项目结构、文件内容以及 UI 视觉元素，无需记忆复杂的命令行参数。
当前重点：围绕自研 ZCode Agent 强化长任务执行和稳定性，把工作区、工具、模型、权限和 Review 串成连续的开发流程。
2. ZCode 免费吗？
ZCode 工具本身完全免费。但作为开发者，您需要准备自己的 API Key 或模型服务套餐。目前支持以下接入方式：
智谱系列：GLM Coding Plan 编程套餐、智谱开放平台模型资源包/充值余额、智谱 Z.ai。
模型服务：ZCode Agent 可使用已接入的模型服务和套餐。
企业模型通道：团队统一维护、供 ZCode Agent 稳定调用的模型通道。
自托管服务：团队批准的私有化模型服务或专有网络模型资源。
3. 我的终端已配置好 GLM API，还需要在 ZCode 重新配置吗？
需要。终端环境变量和 ZCode 桌面端的模型配置是两套独立入口，配置不会自动同步。您可以选择以下任一方式：
快速连接：在欢迎页面或个人头像处连接 BigModel/Z.ai 账号，若账户内有可用套餐将自动连接。
手动管理：通过模型选择器底部的「管理模型」进入 模型设置，手动添加 Base URL 和 API Key。
4. Connect 之后一直 Loading？
如果模型服务连接一直处于 Loading，请优先检查：
网络环境：确保当前网络可以访问对应模型服务。
账号权限：确保登录账号或 API Key 拥有可用额度和模型访问权限。
5. 使用 @ 添加上下文时，为什么只能选择文件，不能选择文件夹？
当前输入框中的 @ 选择器用于快速选择单个文件，也可以选择技能和智能体，但不会列出文件夹。如果需要把整个文件夹作为上下文提供给 Agent，可以直接将文件夹拖拽到输入框中。
支持的方式包括：
从 ZCode 左侧文件树中拖拽文件夹到输入框。
从 Finder、资源管理器等系统文件管理器中拖拽文件夹到输入框。
拖入后，ZCode 会把该文件夹作为上下文引用，Agent 可以围绕目录结构和其中的文件继续分析或执行任务。
6. GLM Coding Plan、Anthropic 端点、OpenAI 通用端点有什么区别？
智谱 BigModel 与 Z.ai 在 API Key 模式下提供 三类端点（详见 连接模型 → 智谱 / Z.ai API 端点说明）：
端点典型地址（BigModel）何时使用
Coding Plan 专用https://open.bigmodel.cn/api/coding/paas/v4已购 GLM Coding Plan，用 API Key 接入 Coding 场景
OpenAI 通用https://open.bigmodel.cn/api/paas/v4开放平台模型资源包 / 充值余额，走 OpenAI 兼容协议
Anthropichttps://open.bigmodel.cn/api/anthropic同上资源包 / 余额，走 Anthropic 协议（ZCode 默认）
常见误区：
买了 Coding Plan，却把 OpenAI 地址填成通用端点 /api/paas/v4 → 无法正常消耗编程套餐额度。
只有资源包 / 余额，却填了 Coding 端点 /api/coding/paas/v4 → Coding 端点仅限 Coding 场景，不适用于通用 API。
通过 「编程套餐」账号授权（非 API Key）连接时，无需手动填端点，ZCode 会自动路由。
海外 Z.ai 请将地址中的域名替换为 api.z.ai，路径规则相同。
On this page
1. ZCode 的产品定位是什么？
2. ZCode 免费吗？
3. 我的终端已配置好 GLM API，还需要在 ZCode 重新配置吗？
4. Connect 之后一直 Loading？
5. 使用 `@` 添加上下文时，为什么只能选择文件，不能选择文件夹？
6. GLM Coding Plan、Anthropic 端点、OpenAI 通用端点有什么区别？
