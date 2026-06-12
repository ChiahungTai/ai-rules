---
description: "Worktree 分支棧 rebase：當前 branch rebase onto 指定 branch，cascade 子 worktree"
when_to_use: "Rebase current branch onto a target branch, then cascade to dependent worktree branches. Use when synchronizing multiple worktrees."
usage: "/rebase <target-branch>"
argument-hint: "/rebase main — rebase onto main"
allowed-tools:
  - Bash
  - Read
  - Edit
---

# /rebase — Worktree 分支棧 Rebase

當前 branch rebase onto 指定的 target branch，然後 cascade 依賴此 branch 的子 worktree。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 執行流程

### Phase 1：確認當前狀態 + 分叉預覽

1. **`git branch --show-current`** — 確認當前所在分支
2. **`git status --porcelain`** — 確認工作目錄 clean
3. **分叉預覽**：判斷 rebase 風險等級

```bash
git merge-base --is-ancestor HEAD <target>  # HEAD 是 target 祖先 → fast-forward
git merge-base --is-ancestor <target> HEAD  # target 是 HEAD 祖先 → up-to-date
# 兩者都不是 → diverged
git log --oneline HEAD..<target> | wc -l   # target 獨有 commit 數
git log --oneline <target>..HEAD | wc -l   # current 獨有 commit 數（將被 replay）
```

| 分叉狀態 | 風險 | 說明 |
|---------|------|------|
| fast-forward | 🟢 零風險 | HEAD 落後 target，直接快轉 |
| up-to-date | 🟢 零風險 | HEAD 已包含 target，rebase no-op |
| diverged | 🟡 可能衝突 | 雙方各有獨有 commit，N commits replay |

4. **印出確認**：`當前分支: <current>，目標: <target>，<分叉狀態>`

**不 clean** → 停下，提示用戶先 commit 或 stash。

### Phase 2：Rebase 當前 branch

```
git rebase <target-branch>
```

**基本規則**：當前 branch rebase onto 輸入的 target branch。

| 結果 | 處理 |
|------|------|
| 成功 | `✅ <current> rebase onto <target>（N commits replayed）` |
| 衝突 | **進入衝突分析流程**（見下方） |
| 空 commit（變更已包含在 target） | AI 預設建議 `git rebase --skip`（rebase 後空 commit 無語義價值），除非用戶有明確理由保留 |

### 衝突分析流程（rebase 衝突時觸發）

> ⚠️ **Rebase 中 ours/theirs 與 merge 相反**
>
> | 操作 | `<<<<<<< HEAD`（:2:） | `>>>>>>> branch`（:3:） |
> |------|----------------------|------------------------|
> | **merge** | 當前分支 | 被合併的分支 |
> | **rebase** | target 分支 | 當前分支（被 replay） |

Git index stages: `:1:` = base（共同祖先）, `:2:` = HEAD（target）, `:3:` = incoming（current branch）

#### Step 1：收集衝突資訊

- `git diff --name-only --diff-filter=U` — 列出所有衝突檔案
- 逐檔 `Read` 衝突標記區段，用 `rg -n "^<{7}|^={7}|^>{7}" <file>` 定位每個 conflict block

#### Step 2：產出衝突比對表（強制）

**每個衝突檔案必須產出以下表格**，每個 conflict block 一列。漏列 = 漏分析 = 解決不完整。

衝突類型分類：

| 衝突類型 | 定義 | 正確解法 |
|---------|------|---------|
| **獨立新增** | 雙方在同一位置加不同東西（最常見：import 衝突） | **兩者都保留** |
| **架構重構** | 一方重構結構，另一方用舊結構 | 採重構方，適配另一方邏輯 |
| **邏輯衝突** | 雙方對同一行有不同意圖 | 需用戶判斷 |
| **刪除 vs 修改** | 一方刪除，另一方修改同處 | 需用戶判斷（刪除是否過時？） |

比對表格式：

```markdown
### <file> 衝突比對

| Block | 行號 | HEAD（<target>）加/改 | Incoming（<current>）加/改 | 衝突類型 | 建議 |
|-------|------|----------------------|--------------------------|---------|------|
| 1 | 36-41 | `import SubscriptionGroup` | `import RankedStock, RankingSnapshot` | 獨立新增 | 保留兩者 |
| 2 | 140-150 | `_resolved_subscriptions` + 多行註解 | `_watchlist_data: WatchlistData` | 架構重構 | 採 incoming + 遷移 HEAD 端 `_resolved_subscriptions` 用法至新介面 |
```

#### Step 3：等用戶確認

逐衝突或批次確認。用戶可：
- 接受建議
- 指定不同方案
- 要求看更多細節（如完整 conflict block 內容）
- **`abort`** — 放棄 rebase（`git rebase --abort`，完整回到 rebase 前狀態，不需 reflog）

#### Step 4：執行解決 + 驗證

1. `Edit` 精確寫入解決內容（逐 block，非整檔覆寫）
2. `git add <file>`
3. **驗證**：確認 resolved file 包含比對表中標註「保留兩者」的雙方內容
   - 在 resolved file 中 `rg` 搜尋比對表列出的 HEAD 端和 incoming 端識別符
   - 發現漏失 → 修正後再 continue

4. 確認無漏失後 `git rebase --continue`
5. 如有後續 commit 衝突，重複 Step 1-4

### Phase 2.5：Post-Rebase 語義驗證

Rebase 成功後（無衝突或衝突已解決），檢查**非衝突區域**的語義一致性。

**為什麼需要**：Git 三方合併只標記「同一行的不同修改」。如果一方將 X 改名為 Y 且與另一方衝突（同行），衝突會被標記。但如果檔案另一處也引用 X 但該行沒被另一方修改 → git 認為「無衝突」auto-merge 保留舊名 X → runtime crash。

**驗證步驟**：

1. 識別 incoming commits（`git diff ORIG_HEAD..HEAD`，rebase 後 `ORIG_HEAD` 自動指向 rebase 前的 tip）中涉及的**識別符改名**（如 `futures_codes → futures_watchlist`、class 刪除、函數簽名變更）
2. `rg` 搜尋被改名/刪除的舊識別符在**整個 codebase**（不限衝突檔案）中是否還有殘留引用
3. 特別關注：import 改名、dataclass 欄位改名、函數簽名改名 — 這些會波及 git 認為「無衝突」auto-merge 的檔案
4. 發現殘留 → 視同衝突，Read + 分析 + 用戶確認 + Edit 修正

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
- 衝突時必須分析雙方變更意圖，提出解決方案，等用戶確認後才執行
- 未經用戶確認不得執行 `git rebase --continue`

### 禁止

- ❌ **`git checkout --theirs` / `git checkout --ours`** — 這是核彈級操作，直接丟棄一方所有變更。必須逐衝突 Read + Edit 精確解決
- ❌ 未經用戶確認就解決衝突並 continue rebase
- ❌ `cd` 到其他 worktree 目錄
- ❌ 跳過 clean 檢查直接 rebase
- ❌ 未確認當前 branch 就開始 rebase

---

## 回復機制

Rebase 完成但用戶不滿意結果時，用 reflog 回復：

```bash
git reflog show <branch> --format="%h %gD: %gs" | head -10
# 找到 rebase 前的 commit（通常是 "rebase (finish)" 之前的條目）
git reset --hard <pre-rebase-commit>
```

⚠️ 如果 branch 已 push 過，回復後需要 `git push --force-with-lease` 同步 remote。cascade 多個 worktree 時每個都需要 force push。

---

## 流程位置

```
/commit（--push / --rebase）→ /rebase <target>（同步分支棧）
```

獨立使用，通常在 commit 之後或每日開工前執行。
