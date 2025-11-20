# Claude Code Agents

## 🎯 用途

這個目錄包含自定義的 Claude Code Agents，透過 symbolic link 連結到 `~/.claude/agents/`。

## 📋 使用方式

### 調用 Agents
```bash
Task("task-name", subagent_type="agent-name", description="任務描述")
```

### 並行處理
```bash
# 多個 Agents 可同時執行
Task("analysis1", subagent_type="agent1", ...)
Task("analysis2", subagent_type="agent2", ...)
```

## 🔗 連結

`~/.claude/agents` → `/Users/ctai/Github/ai-rules/agents`