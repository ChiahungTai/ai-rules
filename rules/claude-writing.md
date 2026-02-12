# CLAUDE.md 撰寫規範

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

> **🔴 強烈警告**: AI 寫作 CLAUDE.md 時**絕對禁止**加入統計資訊、版本號、更新日期等元資訊。詳細說明請參考 `@~/.claude/rules/_ai-behavior-constraints.md`

## 基本原則

CLAUDE.md 是給 AI 的協作指南，應專注於**核心原則**和**執行約束**，避免冗餘細節。

## 命名規範

### 檔案命名
- 專案層級: `./CLAUDE.md` 或 `./.claude/CLAUDE.md`
- 命令層級: `commands/claude/{command-name}.md`
- 符號連結: 用 `@path` 引用共用內容

### 命令命名（slash commands）
- 格式: `/{category}:{action}` 或 `/{action}`
- 範例: `/claude:clean`, `/commit-message`, `/explain`
- 使用小寫和連字線，不用底線

## 結構規範

### YAML Frontmatter
```yaml
---
description: "簡短明確的功能描述"
usage: "/command [參數] [選項]"
argument-hint: "參數提示信息"
allowed-tools: ["Read", "Write", "Edit"]
permission-mode: "acceptEdits"
---
```

### 章節組織
```markdown
# 標題

## 🎯 核心目標（可選）
簡述此檔案/命令的目的

## 核心內容
- 使用清晰層級（## → ### → ####）
- 用項目符號區分要點
- 用程式碼區塊展示範例

## 執行約束
列出必須遵守的約束條件

## 品質檢查清單（可選）
- [ ] 檢查項目 1
- [ ] 檢查項目 2
```

## 內容規範

### 應該包含
- **核心原則**: 為什麼做、不可妥協的約束
- **執行約束**: 必須遵守的規則
- **AI 導航**: 重要檔案和 API 簡要描述
- **實作範例**: 可執行的使用範例

### 應該避免
- **版本號**: `> **版本**: 2.0`
- **更新日期**: `> **更新日期**: 2025-01-01`
- **歷史變更**: `## 變歷史` 或 `## Changelog`
- **統計資訊**: `行數: 387`, `字數: 5234`
- **過時範例**: 無法實際執行的範例

### 引用語法
```markdown
# 相對路徑（相對於當前檔案）
See @./_common/recursive-discovery.md

# 絕對路徑（個人層級）
See @~/.claude/my-instructions.md

# 專案根目錄相對路徑
See @../../rules/self-consistency.md
```

## 程式碼範例規範

### 範例格式
```markdown
### 基本用法

```bash
/claude:clean
```

### 輸出範例

```
預期輸出格式
```
```

### 語言標籤選擇
- **bash**: Shell 命令、Git 操作
- **python**: Python 程式碼
- **markdown**: Markdown 格式範例
- 無語言標籤時使用純文字

## 品質標準

- **簡潔**: 避免冗餘描述，專注核心信息
- **明確**: 避免模糊詞彙（「大概」「可能」「應該」）
- **可操作**: 提供具體執行步驟和範例
- **可維護**: 結構清晰，易於更新
