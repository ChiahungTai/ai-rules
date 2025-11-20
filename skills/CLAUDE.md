# Claude Code Skills

## 🎯 用途

這個目錄包含自定義的 Claude Code Skills，透過 symbolic link 連結到 `~/.claude/skills/`。

## 📋 使用方式

### 調用 Skills
```bash
skill: "skill-name"
"技能調用描述"
```

### 在 Agents 中使用
```bash
allowed-tools: [Read, Write, Edit, "skill:skill-name"]
```

## 🔗 連結

`~/.claude/skills` → `/Users/ctai/Github/ai-rules/skills`