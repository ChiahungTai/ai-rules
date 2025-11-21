# Claude Code Slash Commands 使用指南

## 🎯 目標讀者

**本文檔使用對象**: AI 系統 (Claude Code, KiloCode, Gemini 等)

本文檔指導 AI 如何正確使用 slash commands 進行高效開發協作。

---

## 🔧 Slash Commands 核心機制

### 📍 發現機制
Claude Code 會自動讀取以下目錄中的 `.md` 檔案作為可用的 slash commands：
- **專案層級**: `.claude/commands/` (團隊共享)
- **個人層級**: `~/.claude/commands/` (跨專案使用)

### 🎮 執行方式
```bash
/command-name [參數] [內容]
```

**AI 使用注意**: 當用戶輸入 slash command 時，AI 應使用 `SlashCommand` 工具執行，而非手動展開。

---

## 🛠️ 命令創建規範

### 📄 檔案結構
每個 slash command 都是一個 Markdown 檔案，可包含：

```markdown
---
description: "簡短描述用途"
argument-hint: "參數提示"
allowed-tools: ["Bash", "Read", "Write"]
model: "sonnet"
disable-model-invocation: false
---

命令內容或提示詞
```

### 💡 參數處理

**全體參數**:
```markdown
<!-- 使用 $ARGUMENTS 捕獲所有輸入 -->
分析以下代碼的性能問題：$ARGUMENTS
```

**位置參數**:
```markdown
<!-- 使用 $1, $2 等捕獲個別參數 -->
檔案: $1
行號: $2
問題類型: $3
```

---

## 🎯 高級功能

### 🔧 Bash 執行
```markdown
---
description: "執行系統命令"
---

!echo "執行命令: $ARGUMENTS"
!ls -la
```

### 📎 檔案引用
```markdown
---
description: "分析指定檔案"
---

請分析檔案 @$1 的內容...
```

### 🧠 思考模式
```markdown
---
description: "深度分析"
---

請深入思考 $ARGUMENTS
提供詳細的分析報告...
```

### 📂 命名空間
```
.claude/commands/
├── git/
│   ├── commit.md      -> /git:commit
│   └── push.md        -> /git:push
└── review/
    └── pr.md          -> /review:pr
```

---

## 📋 現有可用命令

### 🚀 核心命令
- `/explain` - 解釋技術概念、架構設計或流程
- `/lessons` - 提取知識精華和經驗教訓
- `/parallel-task` - 智能並行任務協調器
- `/doc-hierarchy` - 創建通用 CLAUDE.md 階層文檔生成器
- `/worktree:done` - 合併 Git Worktree 分支並清理

### 🔧 技術命令
- `/agents:config-manager` - 代理配置管理器

---

## 🎨 AI 使用最佳實踐

### ✅ 正確使用方式
1. **自動識別**: 當用戶輸入 `/command` 時，AI 應識別為 slash command
2. **工具執行**: 使用 `SlashCommand` 工具而非手動處理
3. **參數傳遞**: 將用戶輸入完整傳遞給 command
4. **結果呈現**: 清晰呈現 command 執行結果

### ❌ 避免的錯誤
- 🚫 手動展開 command 內容
- 🚫 忽略 frontmatter 配置
- 🚫 修改參數格式
- 🚫 混淆 slash command 與普通提示

### 🔄 執行流程
```
用戶輸入: /explain 某個技術概念
    ↓
AI 識別: 這是 slash command
    ↓
AI 執行: SlashCommand("/explain 某個技術概念")
    ↓
系統展開: 讀取 .claude/commands/explain.md
    ↓
替換參數: $ARGUMENTS = "某個技術概念"
    ↓
執行結果: 返回解釋內容
```

---

## 🔍 故障排除

### 常見問題
1. **Command not found**: 檢查檔案是否在 `.claude/commands/` 目錄
2. **Parameter not passed**: 確認使用 `$ARGUMENTS` 或位置參數
3. **Permission denied**: 檢查 `allowed-tools` 配置

### 調試技巧
```bash
# 列出所有可用 commands
ls .claude/commands/

# 檢查 command 語法
cat .claude/commands/your-command.md
```

---

## 📚 擴展資源

- **官方文檔**: https://code.claude.com/docs/en/slash-commands
- **Agent Skills**: 複雜工作流程請使用 Agent Skills 而非 slash commands
- **MCP 整合**: 格式為 `/mcp__<server-name>__<prompt-name>`