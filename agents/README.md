# agents/ — Custom Subagent Definitions

Custom subagents for Claude Code, stored as Markdown with YAML frontmatter.

**載入位置**：`~/.claude/agents` → symlink → `/Users/ctai/Github/ai-rules/agents/`（全域，跨專案可用）

---

## Agent 定義格式

```yaml
---
name: agent-name          # 必填：小寫 + 連字號
description: ...          # 必填：觸發條件描述（Claude Code 據此決定何時委派）
model: inherit            # 選填：sonnet / opus / haiku / inherit（省略 = sonnet）
---

System prompt body...
```

**`tools:` 欄位**：省略 = 繼承主對話全部工具（含 LSP plugin、MCP）。除非需要限制工具，否則不要加此欄位。

---

## Agent 清單

| Agent | 用途 | 搭配 Rules |
|-------|------|-----------|
| `lsp-architect` | 架構驗證、型別追蹤、呼叫鏈分析 | `rules/lsp-navigation.md` |
| `nt-type-auditor` | NautilusTrader Cython 邊界型別審計 | `rules/lsp-navigation.md` |

---

## 設計原則

- **System prompt 是行為控制的核心**：rules 是全域規範（auto-loaded），agent system prompt 是按需載入的專家指令
- **單一職責**：每個 agent 只做一類事（lsp-architect = 通用語義導航，nt-type-auditor = NT 特化）
- **與 rules 的分工**：rules/lsp-navigation.md 提供 LSP 決策樹（全域），agent system prompt 提供任務導向的強制 LSP 工作流
