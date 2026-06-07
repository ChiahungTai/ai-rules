---
description: "Worktree 分支棧 rebase：偵測線性分支棧並逐層 rebase 到最新。--sync-main 同步更新 main"
when_to_use: "Rebase all worktree branches in a linear branch stack to keep them up to date. Use when synchronizing multiple worktrees. Add --sync-main to also fetch and fast-forward main from origin."
usage: "/rebase [--sync-main]"
argument-hint: "/rebase — rebase branch stack | /rebase --sync-main — 同步 origin/main 後 rebase"
allowed-tools: ["Bash", "Read"]
---

# /rebase — Worktree 分支棧 Rebase

偵測專案的線性分支棧，從底層往上逐層 rebase，讓所有 worktree branch 保持最新。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 執行流程

### Phase 1：偵測分支棧

1. **`git worktree list`** — 取得所有 worktree 路徑 + 當前分支
2. **`git merge-base --is-ancestor <A> <B>`** — 判斷分支間的 ancestor 關係，組建線性棧
3. **印出偵測結果**，讓用戶確認棧順序：

```
分支棧偵測：
  main → daily-update → paper-trading

Worktree 對應：
  /path/to/main-repo/         → daily-update
  /path/to/worktree/          → paper-trading
```

**偵測失敗**（非線性、無法判斷 ancestor）→ 停下，提示用戶確認分支關係。

### Phase 2：前置檢查

1. 每個 worktree 執行 `git -C <path> status --porcelain`
2. **不 clean** → 停下，列出有未提交變更的 worktree，提示用戶先 commit 或 stash
3. `--sync-main` 時確認 `git remote` 有 origin

### Phase 3：同步 main（僅 `--sync-main`）

1. **`git fetch origin`** — 拉取遠端最新
2. **`git fetch origin main:main`** — fast-forward local main 到 origin/main
   - 不需 checkout，不影響任何 worktree 的工作目錄
   - 非 fast-forward（local main 有 diverge）→ 停下報錯，提示用戶手動處理
3. 印出結果：`✅ main: fast-forward to origin/main（+N commits）`

### Phase 4：逐層 Rebase

從分支棧的**底層往上**，每個 worktree branch rebase 到其 parent：

```
git -C <worktree-A-path> rebase main           # daily-update onto main
git -C <worktree-B-path> rebase daily-update    # paper-trading onto daily-update
```

**遵守工作目錄紀律**：使用 `git -C <path>` 而非 `cd`。Worktree 屬同一 repo，`git -C` 可安全跨 worktree 操作。

每步 rebase 後：

| 結果 | 處理 |
|------|------|
| 成功 | `✅ <branch> rebase onto <parent>（N commits replayed）` |
| 衝突 | **停下**，印出衝突檔案清單，提示用戶手動解決。解決後用 `git -C <path> rebase --continue` 或重新執行 `/rebase` |
| 失敗 | 停下，印出錯誤訊息 |

### Phase 5：報告

```
## Rebase Report

### 分支棧
main → daily-update → paper-trading

### 結果
✅ main: fast-forward to origin/main（+3 commits）        [--sync-main only]
✅ daily-update: rebase onto main（5 commits replayed）
✅ paper-trading: rebase onto daily-update（3 commits replayed）

### 總結
3/3 成功，0 衝突
```

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 偵測分支棧，逐層 rebase |
| **--sync-main** | 先 fetch origin + fast-forward main，再逐層 rebase |

---

## 執行約束

### 強制

- 必須先偵測分支棧並確認
- 必須所有 worktree clean 才能 rebase
- 必須使用 `git -C <path>` 操作跨 worktree，禁止 `cd`
- 衝突時必須停下等用戶手動解決

### 禁止

- ❌ 自動解決衝突（rebase 衝突影響 commit history，必須人工判斷）
- ❌ `cd` 到其他 worktree 目錄
- ❌ 跳過 clean 檢查直接 rebase

---

## 流程位置

```
/commit（--push / --rebase）→ /rebase（同步分支棧）
```

獨立使用，通常在 commit 之後或每日開工前執行。
