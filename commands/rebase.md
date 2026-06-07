---
description: "Worktree 分支棧 rebase：當前 branch rebase onto 指定 branch，cascade 子 worktree"
when_to_use: "Rebase current branch onto a target branch, then cascade to dependent worktree branches. Use when synchronizing multiple worktrees."
usage: "/rebase <target-branch>"
argument-hint: "/rebase main — rebase onto main"
allowed-tools: ["Bash", "Read"]
---

# /rebase — Worktree 分支棧 Rebase

當前 branch rebase onto 指定的 target branch，然後 cascade 依賴此 branch 的子 worktree。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 執行流程

### Phase 1：確認當前狀態

1. **`git branch --show-current`** — 確認當前所在分支
2. **`git status --porcelain`** — 確認工作目錄 clean
3. **印出確認**：`當前分支: <current>，目標: <target-branch>`

**不 clean** → 停下，提示用戶先 commit 或 stash。

### Phase 2：Rebase 當前 branch

```
git rebase <target-branch>
```

**基本規則**：當前 branch rebase onto 輸入的 target branch。

| 結果 | 處理 |
|------|------|
| 成功 | `✅ <current> rebase onto <target>（N commits replayed）` |
| 衝突 | **停下**，印出衝突檔案清單，提示用戶手動解決。解決後 `git rebase --continue` |

### Phase 3：Cascade 子 worktree

1. **`git worktree list`** — 取得所有 worktree
2. 找出以當前分支為 parent 的子 worktree（用 `git merge-base --is-ancestor` 判斷）
3. **檢查子 worktree clean**：`git -C <path> status --porcelain`
4. **Rebase 子 worktree**：`git -C <path> rebase <current-branch>`

無子 worktree → 跳過此階段。

有多層子 worktree → 遞迴 cascade（子 rebased 後，再找子的子）。

每步 rebase 後同 Phase 2 的結果處理（成功印出 / 衝突停下）。

### Phase 4：報告

```
## Rebase Report

當前: daily-update → target: main

### 結果
✅ daily-update: rebase onto main（5 commits replayed）
✅ paper-trading: rebase onto daily-update（3 commits replayed）  [cascade]

### 總結
2/2 成功，0 衝突
```

---

## 參數

| 參數 | 說明 |
|------|------|
| **\<target-branch\>** | 要 rebase onto 的目標分支（如 main、daily-update） |

---

## 執行約束

### 強制

- 必須先確認當前分支和工作目錄狀態
- 必須當前 worktree clean 才能 rebase
- Cascade 前必須檢查子 worktree 也 clean
- 必須使用 `git -C <path>` 操作跨 worktree，禁止 `cd`
- 衝突時必須停下等用戶手動解決

### 禁止

- ❌ 自動解決衝突（rebase 衝突影響 commit history，必須人工判斷）
- ❌ `cd` 到其他 worktree 目錄
- ❌ 跳過 clean 檢查直接 rebase
- ❌ 未確認當前 branch 就開始 rebase

---

## 流程位置

```
/commit（--push / --rebase）→ /rebase <target>（同步分支棧）
```

獨立使用，通常在 commit 之後或每日開工前執行。
