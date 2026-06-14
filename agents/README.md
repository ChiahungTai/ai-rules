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
| `lsp-architect` | 架構驗證、型別追蹤、呼叫鏈分析 | `rules/lsp-navigation.md` + `bash-hard-rules.md` |
| `nt-type-auditor` | NautilusTrader Cython 邊界型別審計 | `rules/lsp-navigation.md` + `bash-hard-rules.md` |

---

## 設計原則

- **System prompt 是行為控制的核心**：rules 是全域規範（auto-loaded），agent system prompt 是按需載入的專家指令
- **單一職責**：每個 agent 只做一類事（lsp-architect = 通用語義導航，nt-type-auditor = NT 特化）
- **與 rules 的分工**：rules/lsp-navigation.md 提供 LSP 決策樹（全域），agent system prompt 提供任務導向的強制 LSP 工作流
- **Tool priority 以 rules 為 source of truth**：agent system prompt 內嵌的 tool priority 是方便副本，權威版本在 `rules/bash-hard-rules.md`。更新 rules 時檢查 agents 是否需要同步

---

## 檔案寫入紀律（Autonomous-friendliness）

> **核心原則**：agent 失敗成本不對稱 —— 跑很久才在末端權限失敗，前面 context 全浪費。寫檔遵循三層。

1. **禁 /tmp** —— 產出絕不寫 /tmp（易丟、不可追溯、session 中斷即消失）；寫在自己當前工作目錄（repo/worktree）內
2. **寫不進指定路徑（跨 repo / worktree 隔離）→ 回報「環境限制：我寫不進 X」，不自行妥協到 /tmp**；交回主 session 決定（spawn 端回收責任見 `rules/collaboration-constraints.md`「Agent 派發與產出回收」）
3. **暫時產物**（中間分析、草稿、POC 輸出）→ 集中到 repo 內暫存區，依模式處置：
   - **互動模式**：完成時列出清單詢問保留／刪除
   - **autonomous / deep-work**：集中到 `.agent-tmp/`（repo 內，權限預期 allow；**各專案須將 `.agent-tmp/` 加入 `.gitignore`**），最終報告列出清單，使用者事後處理（逐一確認會卡死 autonomous flow）

### 注入責任

此三條對「會寫檔的 agent」下指令，但 **agent 不自動載入 README**（subagent 只載自己的 system prompt）。**spawn 會寫檔的 agent 時，主 session 須將此三條寫入紀律注入 agent prompt**。enforcement（spawn 端）視角見 `rules/collaboration-constraints.md`「Agent 派發與產出回收」。

### 為什麼

/tmp 是 agent 寫不進目標時的危險第一反應 —— 即使主 session 事後補救，session 中斷在補救前就丟（autonomous 場景尤甚）。
