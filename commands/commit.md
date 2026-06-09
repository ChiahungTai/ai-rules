---
description: "Commit 入口：lint 閘門 → 分析變更 → 生成 message → 確認後提交"
when_to_use: "Commit current changes after lint check, message generation, and user confirmation. Supports push, rebase, and PR creation after commit."
usage: "/commit [--push] [--rebase <branch>]"
argument-hint: "可選 --push 自動推送，--rebase <branch> rebase 後推送"
allowed-tools: ["Bash", "Read"]
---

# /commit — Commit 入口

Git Commit 工作流入口，從 lint 閘門到提交完成。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 執行流程

### 階段 1：Lint 閘門

**Ruff + MyPy 雙軌閘門**（兩者都必須通過才 commit）：

```bash
# Track A: Ruff（格式 + lint）
uv run ruff check --fix .    # Step 1: 自動修可修的
uv run ruff format .         # Step 2: 格式化
uv run ruff check .          # Step 3: 最終驗證（必須 0 errors）

# Track B: MyPy（型別檢查）
uv run mypy .                # 必須 0 errors
```

**執行順序**：Step 1 → Step 2 → **並行** Step 3 + MyPy（ruff format 後同時跑 ruff verify 和 mypy，省時間）。

Ruff 或 MyPy 有錯誤 → **嘗試手動修正**（不直接放棄）：

| 錯誤類型 | 自動處理策略 |
|---------|------------|
| PLC0415（局部 import） | 移至 top-level import。**禁止假設 circular import** — AI 常偷懶放在函數內，99% 不是 circular。真正循環的解法是重構目錄結構，不是局部 import |
| F841（未使用變數） | 移除或加 `_` 前綴 |
| E402（sys.path 後的 import） | 加 per-file-ignores 到 pyproject.toml |
| MyPy 第三方套件型別缺口 | 依 [python-type-gap](../skills/python-type-gap/SKILL.md) 四層策略處理 |
| 其他可修問題 | 依 `/lint-fix` 指引修正 |

手動修正後仍無法通過 → 提示 `/lint-fix`，中止。

### 階段 2：Git 狀態分析

`git status --porcelain` + `git diff` + `git diff --cached` + `git log --oneline -10`

深度理解：檔案層級（模組、功能區域）+ 程式碼層級（業務邏輯）+ 變更類型（feat/fix/refactor/perf/test/docs/style/chore）

### 階段 2.5：引用同步掃描

**當變更包含 `rules/`、`skills/`、`commands/` 下的 .md 檔案時執行，否則跳過。**

目的：修改 A 後，掃描是否有 B/C/D 引用了 A 但沒同步更新。

掃描範圍（按變更檔案類型）：

| 變更檔案 | 掃描目標 | 搜尋方式 |
|---------|---------|---------|
| `commands/*.md` | `commands/CLAUDE.md` 索引 | `rg "command名" commands/CLAUDE.md` |
| `commands/claude/*.md` | `commands/CLAUDE.md` 索引 + 引用此命令的其他 .md | `rg "命令名或檔名" rules/ skills/ commands/` |
| `skills/*/SKILL.md` | `skills/CLAUDE.md` 索引 + 引用此 skill 的 commands | `rg "skill名" commands/ rules/` |
| `rules/*.md` | 引用此 rule 的 commands 和 skills | `rg "rule名或檔名" commands/ skills/` |
| `ai-development-guide.md` | 所有引用 guide 定義的 commands（如 UC 狀態 emoji） | `rg "具體定義文字" commands/` |

輸出：列出需檢查的檔案（不是要求全部更新，是提醒檢查是否需要更新）。用戶在階段 5 確認時一併判斷。

### 階段 3：Capabilities + Kanban 狀態更新（大型/中型變更）

**大型/中型變更時執行，小型變更跳過。**

> **核心原則**：Capabilities 更新 + Kanban 卡片搬移 + EP 歸檔是「metadata finalization」，只在用戶確認 commit 時才執行。不在 `/build` 執行（build 可能不 commit）。

1. 識別變更涉及的 library 模組目錄
2. 檢查該模組 CLAUDE.md Capabilities 表格和 .kanban/ 卡片：是否有 UC 狀態需要更新？
3. 在 commit message 展示後，提示用戶確認以下操作：
   - **Capabilities 更新**：在對應模組 CLAUDE.md 的 `## Capabilities` 表格新增 ✅ 行
   - **Kanban 卡片搬移**：已完成 UC 的卡片從 active lane 移至 Done/
   - **消費場景寫入**：從 `/build` 提煉的消費場景寫入 Capabilities 備註或 Kanban card
   - **原子操作**：Capabilities 新增 + Kanban 卡片移動必須同時完成
4. 用戶確認後，在 commit 前**執行上述操作**（修改 CLAUDE.md + mv 卡片）
5. **EP 歸檔檢查**：如果本次 commit 是 EP 的最後一個段落（所有段落都已 commit），提醒用戶：
   - 「EP 所有段落已 commit，建議歸檔：`mv ai-analysis/execution-plans/ep-xxx.md ai-analysis/execution-plans/_done/`」
   - 歸檔為手動操作，不自動執行

### 階段 4：生成 Commit Message

**格式**：`<type>(<scope>): <description>`

**語言規範**：

| 部分 | 語言 | 範例 |
|------|------|------|
| type | 英文 | `feat`, `fix`, `refactor` |
| scope | 英文 | `data`, `commands`, `ui` |
| description | **繁體中文**（術語保留英文） | `新增 DataGateway 統一數據介面` |
| body | 繁體中文 + 英文術語 | 說明為什麼這樣改 |

### 階段 5：用戶確認

展示變更摘要 + 建議 commit message + Capabilities/Kanban 狀態提醒（如適用）→ **等待用戶明確確認**。

**遵守 `commit-consent` rule**：未收到確認絕不執行 git commit。

### 階段 6：執行 Commit

確認後 `git add` + `git commit`（含 `Co-Authored-By: Claude`）

### 階段 7：選配分支操作

- `--push`：`git push`
- `--rebase <branch>`：fetch + rebase + push
- 建立 PR：`gh pr create`

---

## 執行約束

- **遵守 `commit-consent` rule**：未經確認絕不 commit
- **ruff + mypy 必須雙通過才 commit**（pre-existing 問題也需在此時處理：加 per-file-ignores / type: ignore 或直接修）
- **description 必須繁體中文**（技術術語保留英文）
- **基於實際 diff 分析**，不憑猜測
- **遵循 git log 風格**

禁止：未確認就 commit / 全英文 description / 跳過 ruff 或 mypy / 無意義 message

---

## 流程位置

```
/build（含 Agent Review）→ [/code-review（含 commit message）] → /commit
```

前置：`/lint-fix`（lint 不通過時）、`/code-review`

**捷徑模式**：當 `/code-review` 已產生 commit message 時，跳過階段 2（Git 狀態分析，含 2.5 引用同步掃描）和階段 3（Capabilities + Kanban 狀態確認），直接進入階段 1（Lint）→ 階段 5（確認）→ 階段 6（提交）。
