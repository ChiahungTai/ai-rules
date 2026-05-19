# Claude Code Skills 技術規範

## 寫作原則

> **載入時機**：Skill 只在語意匹配觸發時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Skill 不支援 `@` transclusion。引用輔助檔案一律使用 `[描述](path)` markdown link
- **描述檔案內容**：讓 AI 判斷何時該跟隨 link 讀取，而非無條件載入
- **實作程式碼**：避免在 skill 中嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

## 架構

個人層級 `~/.claude/skills` 符號連結指向 `/Users/ctai/Github/ai-rules/skills`，實現 Git 版本控制、跨專案共享和即時更新。驗證：`readlink ~/.claude/skills`。

## Frontmatter 配置

```yaml
---
name: skill-name                    # 必填：小寫、數字、連字符 (最多 64 字元)
description: 功能描述和觸發條件    # 必填：功能 + 何時使用 (最多 1024 字元)
allowed-tools:                      # 可選：限制工具存取權限
  - Read
  - Write
  - Edit
model: sonnet|opus|haiku|inherit    # 可選：指定使用的 Claude 模型
skills: dependency-skill            # 可選：依賴的其他技能
---
```

`description` 是觸發關鍵 — 必須同時說明**功能**和**觸發條件**，包含多種同義觸發詞。
