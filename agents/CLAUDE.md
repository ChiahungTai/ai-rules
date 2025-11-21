# Claude Code Agents

## 🎯 用途

這個目錄包含自定義的 Claude Code Agents。Claude Code 會自動讀取此目錄中的 agent 配置檔案作為可用的專門代理。

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

## 📁 目錄結構

直接在此目錄中新增 agent 配置檔案即可創建新的專門代理。

**重要**: 不需要創建符號連結，Claude Code 會自動識別此目錄中的檔案。