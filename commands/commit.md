---
description: "Commit 入口：lint 閘門 → 分析變更 → 生成 message → 確認後提交"
when_to_use: "Commit current changes after lint check, message generation, and user confirmation. Supports push, rebase, and PR creation after commit."
usage: "/commit [--push] [--rebase <branch>]"
argument-hint: "可選 --push 自動推送，--rebase <branch> rebase 後推送"
allowed-tools: ["Bash", "Read"]
---

# /commit — Commit 入口

你是 Git Commit 工作流入口，負責從 lint 閘門到提交完成的完整流程。

## 🎯 核心目標

**「Lint 閘門 → 分析變更 → 生成 message → 用戶確認 → 提交」**

## 📚 委託 Skills

- [rules-reminder](../skills/rules-reminder/SKILL.md) — `rg`/`fd` 取代 `grep`/`find`、禁止 `sed`、管道拆兩步等 Bash 規則

---

## 📋 執行流程

### 階段 1：Lint 閘門（快速 pass/fail）

```bash
uv run ruff check --fix .
uv run mypy .
```

- **通過** → 繼續階段 2
- **不通過** → 提示用戶先跑 `/lint-fix` 修正，中止流程

### 階段 2：Git 狀態分析

```bash
git status --porcelain
git diff --cached
git diff
git log --oneline -10
```

深度理解變更：
- **檔案層級**：識別修改的模組、功能區域
- **程式碼層級**：理解變更的業務邏輯
- **變更類型識別**：feat / fix / refactor / perf / test / docs / style / chore

### 階段 3：生成 Commit Message

#### 格式標準

```
<type>(<scope>): <description>

<body>

<footer>
```

#### 語言規範

| 部分 | 語言 | 範例 |
|------|------|------|
| **type** | 英文 | `feat`, `fix`, `refactor` |
| **scope** | 英文 | `data`, `commands`, `ui` |
| **description** | **繁體中文**（術語保留英文） | `新增 DataGateway 統一數據介面` |
| **body** | 繁體中文 + 英文術語 | 說明為什麼這樣改 |

#### 範例

```
feat(data): 新增 DataGateway 統一數據介面

實作新的數據網關架構，統一多個數據源
- 新增 DataGateway 基礎類別
- 實作數據源 adapter

fix(pipeline): 修復數據流水線記憶體洩漏問題

解決長時間運行時記憶體持續增長的問題
- 修正 DataFrame 引用未正確釋放

refactor(tests): 清理過時測試工具，簡化測試配置
```

### 階段 4：用戶確認

展示以下資訊，**等待用戶明確確認**：

```markdown
## Commit 預覽

### 變更摘要
[列出主要變更]

### 建議 Commit Message
[生成的 message]

---
確認 commit？(commit / 確認 / OK / 取消)
```

**遵守 `commit-consent` rule**：未收到確認絕不執行 git commit。

### 階段 5：執行 Commit

收到確認後：

```bash
git add [相關檔案]
git commit -m "$(cat <<'EOF'
生成的 commit message

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

### 階段 6：選配分支操作

commit 完成後，根據參數或用戶意願：

#### `--push`：推送到遠端

```bash
git push
```

#### `--rebase <branch>`：rebase 後推送

```bash
git fetch origin <branch>
git rebase origin/<branch>
git push
```

#### 建立 PR（如有需要）

```bash
gh pr create --title "..." --body "..."
```

---

## 🔧 執行約束

### 必須遵守

- **遵守 `commit-consent` rule**：未經用戶確認絕不 commit
- **lint 閘門不通過不 commit**：引導用戶先跑 `/lint-fix`
- **description 必須使用繁體中文**：技術術語保留英文（中英交雜是正確的）
- **深度分析優先**：基於實際 diff 內容，不憑猜測
- **遵循專案 commit 風格**：參考 git log 歷史

### 禁止行為

- ❌ 未經用戶確認就執行 git commit
- ❌ 使用全英文 description
- ❌ 跳過 lint 閘門直接 commit
- ❌ commit message 只寫 "update"、"fix" 等無意義描述

---

## 📚 與其他命令的協作

### 流程位置
```
/build → /code-review → /commit
```

### 前置命令
- `/lint-fix` — lint 閘門不通過時的修正工具
- `/code-review` — commit 前的程式碼審查
