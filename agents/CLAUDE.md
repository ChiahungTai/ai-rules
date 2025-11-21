# Claude Code Agents 專業指南

## 🎯 什麼是 Subagents

**Subagents** 是專門化的 AI 助理，具有獨立的上下文視窗、客製化系統提示和受控的工具存取權限。它們是 Claude Code 生態系統中的核心組件，專門處理特定類型任務。

### 核心價值
- **上下文保護**: 每個 subagent 獨立運作，避免主要對話上下文污染
- **專業專精**: 針對特定領域微調，成功率更高
- **可重複使用**: 跨專案使用並可與團隊共享
- **彈性權限**: 不同工具存取等級，確保安全性

## 📋 Agent 配置結構

### 檔案格式
每個 agent 使用 Markdown 格式，包含 YAML 前置元數據：

```markdown
---
name: agent-name
description: 何時調用此 agent
tools: Read, Write, Grep, Bash
model: sonnet|opus|haiku|inherit
permissionMode: default|acceptEdits|bypassPermissions
skills: skill1, skill2
---

系統提示內容和詳細指令...
```

### 配置欄位說明

| 欄位 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `name` | ✅ | Agent 唯一識別名稱 | `code-reviewer` |
| `description` | ✅ | 觸發條件說明 | "代碼審查和品質檢查" |
| `tools` | ❌ | 可用工具列表 | `Read, Write, Grep, Bash` |
| `model` | ❌ | 使用的模型 | `sonnet` (預設繼承) |
| `permissionMode` | ❌ | 權限模式 | `default` |
| `skills` | ❌ | 特殊技能 | `parallel-processing` |

## 🗂️ Agent 存儲位置

Claude Code 按優先級順序讀取 agents：

```
1. .claude/agents/           (專案層級 - 最高優先級)
2. --agents flag 參數        (CLI 定義 - 中等優先級)
3. ~/.claude/agents/          (用戶層級 - 最低優先級)
```

**當前位置**: `/Users/ctai/Github/ai-rules/agents/` (專案層級)

## 🚀 Agent 使用方式

### 1. 自動委派
Claude 根據任務描述和 agent 欄位自動選擇最適合的 agent：

```python
# Claude 自動選擇適合的 agent
Task("analyze codebase structure", subagent_type="code-analyzer")
```

### 2. 明確調用
直接指定使用特定的 agent：

```python
# 明確指定 agent
Task("review recent changes", subagent_type="code-reviewer")
```

### 3. 並行處理
多個 agents 可同時執行複雜任務：

```python
# 並行執行多個 agents
Task("security analysis", subagent_type="security-expert")
Task("performance review", subagent_type="performance-analyzer")
Task("documentation check", subagent_type="doc-validator")
```

### 4. 交互式管理
使用 `/agents` 指令進行綜合管理：

```bash
/agents                    # 列出所有可用 agents
/agents config agent-name  # 查看特定 agent 配置
```

## 🔧 進階功能

### Agent 鏈接
複雜工作流程可使用多個 agents 鏈接：

```python
# 第一階段：代碼分析
Task("analyze requirements", subagent_type="requirements-analyzer")

# 第二階段：實作規劃
Task("create implementation plan", subagent_type="planning-expert")

# 第三階段：代碼生成
Task("generate code", subagent_type="code-generator")
```

### 可恢復 Agents
使用 agent ID 繼續之前的對話：

```python
Task("continue analysis", subagent_type="data-analyst", resume="agent-session-123")
```

### 整合插件 Agents
來自插件的 agents 會與自定義 agents 一起顯示：

```python
# 插件提供的 agent 也可直接調用
Task("optimize database", subagent_type="db-optimizer")  # 來自 database-plugin
```

## 📊 內建 Agents

### Plan Agent
專門用於 plan 模式的代碼庫研究：
- **工具**: Read, Glob, Grep, Bash
- **用途**: 代碼庫探索和架構分析
- **觸發**: 進入 plan 模式時自動啟動

## 🎯 最佳實踐

### 設計原則
1. **開始使用 Claude 生成的 agents**: 獲得最佳起點
2. **專注單一職責**: 每個 agent 處理特定任務類型
3. **詳細提示**: 提供具體指令和範例
4. **限制工具**: 只開放必要功能
5. **版本控制**: 將專案 agents 納入 git 管理

### 效能考量
- **上下文保護**: 有助於長時間對話維持效能
- **啟動延遲**: 每次調用需要重新收集上下文
- **記憶體管理**: 獨立上下文避免主對話膨脹

### 範例 Agent 配置

```markdown
---
name: code-reviewer
description: 對代碼變更進行全面審查，包含安全性、效能和最佳實踐檢查
tools: Read, Grep, Bash, Write
model: sonnet
permissionMode: default
skills: parallel-processing
---

你是代碼審查專家，負責對變更進行全面分析...

任務流程：
1. 分析變更範圍和影響
2. 檢查程式碼品質和安全性
3. 驗證最佳實踐遵循
4. 提供具體改進建議
```

## 🔍 除錯與監控

### Agent 狀態檢查
```bash
# 檢查 agent 執行狀態
/tasks

# 查看特定 agent 輸出
/task-id
```

### 常見問題
- **找不到 agent**: 檢查檔案路徑和命名
- **權限不足**: 確認 `permissionMode` 設定
- **工具缺失**: 驗證 `tools` 欄位配置

## 📁 當前目錄使用指南

### 新增 Agent
1. 在此目錄創建 `.md` 檔案
2. 配置 YAML 前置元數據
3. 編寫詳細系統提示
4. 測試 agent 功能

### 檔案命名約定
- 使用小寫字母和連字符: `security-analyzer.md`
- 名稱反映功能: `code-reviewer.md`
- 避免特殊字元和空格

**重要**: Claude Code 會自動識別此目錄中的檔案，無需創建符號連結或額外配置。