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

**Lint → Format → Verify 三步流程**：

```bash
uv run ruff check --fix .    # Step 1: 自動修可修的
uv run ruff format .         # Step 2: 格式化
uv run ruff check .          # Step 3: 最終驗證（必須 0 errors）
```

如果 Step 3 仍有錯誤 → **嘗試手動修正**（不直接放棄）：

| 錯誤類型 | 自動處理策略 |
|---------|------------|
| PLC0415（局部 import） | 移至 top-level import。**禁止假設 circular import** — AI 常偷懶放在函數內，99% 不是 circular。真正循環的解法是重構目錄結構，不是局部 import |
| F841（未使用變數） | 移除或加 `_` 前綴 |
| E402（sys.path 後的 import） | 加 per-file-ignores 到 pyproject.toml |
| 其他可修問題 | 依 `/lint-fix` 指引修正 |

手動修正後仍無法通過 → 提示 `/lint-fix`，中止。

**MyPy 檢查**（可選，不阻塞 commit）：
```bash
uv run mypy .
```

### 階段 2：Git 狀態分析

`git status --porcelain` + `git diff` + `git diff --cached` + `git log --oneline -10`

深度理解：檔案層級（模組、功能區域）+ 程式碼層級（業務邏輯）+ 變更類型（feat/fix/refactor/perf/test/docs/style/chore）

### 階段 3：生成 Commit Message

**格式**：`<type>(<scope>): <description>`

**語言規範**：

| 部分 | 語言 | 範例 |
|------|------|------|
| type | 英文 | `feat`, `fix`, `refactor` |
| scope | 英文 | `data`, `commands`, `ui` |
| description | **繁體中文**（術語保留英文） | `新增 DataGateway 統一數據介面` |
| body | 繁體中文 + 英文術語 | 說明為什麼這樣改 |

### 階段 4：用戶確認

展示變更摘要 + 建議 commit message → **等待用戶明確確認**。

**遵守 `commit-consent` rule**：未收到確認絕不執行 git commit。

### 階段 5：執行 Commit

確認後 `git add` + `git commit`（含 `Co-Authored-By: Claude`）

### 階段 6：選配分支操作

- `--push`：`git push`
- `--rebase <branch>`：fetch + rebase + push
- 建立 PR：`gh pr create`

---

## 執行約束

- **遵守 `commit-consent` rule**：未經確認絕不 commit
- **lint 必須 0 errors 才 commit**（pre-existing 問題也需在此時處理：加 per-file-ignores 或直接修）
- **description 必須繁體中文**（技術術語保留英文）
- **基於實際 diff 分析**，不憑猜測
- **遵循 git log 風格**

禁止：未確認就 commit / 全英文 description / 跳過 lint / 無意義 message

---

## 流程位置

```
/build（含 Agent Review）→ [/code-review（含 commit message）] → /commit
```

前置：`/lint-fix`（lint 不通過時）、`/code-review`

**捷徑模式**：當 `/code-review` 已產生 commit message 時，跳過階段 2（Git 狀態分析），直接進入階段 1（Lint）→ 階段 4（確認）→ 階段 5（提交）。
