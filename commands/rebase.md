---
description: "Trunk-based worktree rebase：feature rebase onto trunk（慣例 main），trunk 只往前、永不被 rebase"
when_to_use: "Rebase a feature branch onto the trunk (main), optionally sync other feature worktrees onto the same trunk. Use when synchronizing worktrees around a single integration branch."
usage: "/rebase <branch> [--autostash]"
argument-hint: "<branch>（慣例 main） [--autostash]"
allowed-tools:
  - Bash
  - Read
  - Edit
---

# /rebase — Trunk-Based Worktree Rebase

Feature branch rebase onto **trunk**（慣例 `main`）。多 worktree 共用同一 `.git`，rebase 即時本地、不需 push。本命令只處理「feature onto trunk」方向 —— trunk 永不被 rebase（見鐵律）。`<branch>` arg 的角色隨當前 branch 翻轉（在 trunk 上 = feature，在 feature 上 = trunk；見 Phase 0）。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## Trunk 模型鐵律（執行前必讀）

1. **指定一條 trunk**（慣例 `main`）。Trunk 是唯一整合線。
2. **Trunk 只往前**：疊新 commit，或 fast-forward 到一條已 rebase 過 trunk 的 feature。Trunk **永遠不是 `git rebase` 的主詞**。
3. **Feature onto trunk（單向）**。Feature 之間**不直接 rebase 彼此** —— `backbone` 要 `replay` 的東西，走 trunk 中轉（replay→trunk→backbone），不 `backbone rebase replay`。
4. **讓 trunk 吸收 feature** 的正確兩步（**不是 `git rebase`**）：
   - feature 先 `rebase <trunk>`（feature 變成 trunk 的後代）
   - 在 trunk worktree：`git merge --ff-only <feature>`（fast-forward 吸收）
5. **為何 `merge --ff-only` 而非 `rebase`**：若 trunk 不是 feature 的祖先（你漏了上一步、或 trunk 自己有 feature 沒有的新 commit），`merge --ff-only` **大聲拒絕**；`git rebase` 同情況會**靜默改寫 trunk** —— trunk 已 push 時就是 force-push 災難。`--ff-only` 是安全欄杆。

> **rerere**：feature 反覆 rebase trunk 時，相同衝突自動套用前次解析。建議 `git config --global rerere.enabled true`。

---

## 執行流程

### Phase 0：arg 角色 = f(當前 branch)

**第一個動作，任何操作前。** `/rebase <branch>` 的 `<branch>` 是「另一端」——**角色由當前 branch 決定，不是固定 trunk**。第一步永遠：

```bash
git branch --show-current
```

| 當前 = | `<branch>` 是 | 操作 |
|--------|--------------|------|
| **trunk**（慣例 `main`） | feature | `git merge --ff-only <branch>`（吸收步，鐵律 4）→ 結束 |
| **feature** | trunk | 進入 Phase 1 rebase 流程 |

**當前 = trunk（吸收步）**：**不 rebase**（鐵律 2）。前置檢查：
- arg 須是 feature（≠ trunk；arg = trunk 本身 → 拒絕）。
- 工作目錄須 clean —— dirty → 停下，提示先 commit/stash（merge 路徑不適用 `--autostash`，旗標忽略；吸收步在整合線上，不 smooth over trunk dirt）。

先驗 ff —— trunk 須是 arg 祖先才能快轉：

```bash
git merge-base --is-ancestor HEAD <branch>   # exit 0 = 當前（trunk）是 arg 祖先 = ff 可能
```

- **exit 0** → `git merge --ff-only <branch>`，印 `✅ <current>: merge --ff-only <branch>`，**結束**（跳過 Phase 1-3；需同步其他 feature worktree → 另在該 worktree 跑 `/rebase main`）。
- **exit 1** → arg 尚未 rebase onto trunk；**不強制 merge**，提示「切到 `<branch>` worktree 跑 `/rebase main`（鐵律 4 step 1：feature 先 rebase onto trunk）」。

> **方向記法**：`--is-ancestor A B` =「A 是 B 祖先」。要把 `<branch>` 併進 trunk，trunk 須落後 arg → 查 `--is-ancestor <trunk> <branch>`，**不是** `<branch> <trunk>`。

**當前 = feature（rebase 步）**：arg 必須是 trunk（鐵律 3：feature 不互 rebase；在 `backbone` 上 `/rebase replay` 之類拒絕，走 trunk 中轉 replay→main→backbone）→ 進入 Phase 1。

### Phase 1：確認狀態 + 分叉預覽

> 到此必為「當前 = feature、`<branch>` = trunk」（Phase 0 已分流）。

1. **`git status --porcelain`** — 確認工作目錄狀態（clean / dirty）
2. **分叉預覽**：判斷 rebase 風險等級

```bash
git merge-base --is-ancestor HEAD <branch>   # HEAD 是 trunk 祖先 → fast-forward
git merge-base --is-ancestor <branch> HEAD    # trunk 是 HEAD 祖先 → up-to-date
# 兩者都不是 → diverged
git log --oneline HEAD..<branch> | wc -l      # trunk 獨有 commit 數
git log --oneline <branch>..HEAD | wc -l      # current 獨有 commit 數（將被 replay）
```

| 分叉狀態 | 風險 | 說明 |
|---------|------|------|
| fast-forward | 🟢 零風險 | HEAD 落後 trunk，直接快轉 |
| up-to-date | 🟢 零風險 | HEAD 已包含 trunk，rebase no-op |
| diverged | 🟡 可能衝突 | 雙方各有獨有 commit，N commits replay |

3. **印出確認**：`當前分支: <current>，trunk: <branch>，<分叉狀態>`

4. **trunk worktree HEAD vs trunk branch ref 消歧**（防誤讀 `git worktree list`）：rebase 的 base 永遠是 **trunk branch ref**（`git rev-parse <branch>`）。`git worktree list` 顯示的 trunk worktree HEAD 可能**落後** trunk branch ref（該 worktree 未 checkout 最新，或處於 detached），但那與 rebase base **無關** —— 你不在 trunk worktree 操作。若 `git worktree list` 的 trunk HEAD ≠ `git rev-parse <branch>`，提示「base 採 trunk branch ref（`<ref>`），非 trunk worktree HEAD（`<head>`）」消歧，省下釐清 stale HEAD 的 tool call。

**不 clean 的處理**：
- **預設（無 `--autostash`）** → 停下，提示用戶先 commit 或 stash。
- **帶 `--autostash`** → 不阻擋，Phase 2 改用 `git rebase --autostash`（git 自動 stash→rebase→pop）。

### Phase 2：Rebase 當前 branch

```
git rebase [--autostash] <branch>   # --autostash 僅在帶旗標時加
```

**基本規則**：當前（feature）branch rebase onto 輸入的 trunk branch。帶 `--autostash` 時，git 自動把 dirty 變更 stash、rebase 完 pop 回來。

> ⚠️ **autostash pop ≠ rebase 衝突流程**：autostash 的 `git stash pop` 發生在 rebase 完成（或衝突解完 `--continue`）之後，是獨立事件。若 pop 衝突（WIP 與 rebase 結果撞行），留下 conflict markers，需手動 Read + Edit 解 —— 不在下方「衝突分析流程」涵蓋內。帶旗標前自問 WIP 是否可能撞 trunk 改動。

| 結果 | 處理 |
|------|------|
| 成功 | `✅ <current> rebase onto <branch>（N commits replayed）` |
| 衝突 | **進入衝突分析流程**（見下方） |
| 空 commit（變更已包含在 trunk） | AI 預設建議 `git rebase --skip`（rebase 後空 commit 無語義價值），除非用戶有明確理由保留 |

### 衝突分析流程（rebase 衝突時觸發）

> ⚠️ **Rebase 中 ours/theirs 與 merge 相反**
>
> | 操作 | `<<<<<<< HEAD`（:2:） | `>>>>>>> branch`（:3:） |
> |------|----------------------|------------------------|
> | **merge** | 當前分支 | 被合併的分支 |
> | **rebase** | trunk 分支 | 當前分支（被 replay） |

Git index stages: `:1:` = base（共同祖先）, `:2:` = HEAD（trunk）, `:3:` = incoming（current branch）

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

| Block | 行號 | HEAD（<branch>）加/改 | Incoming（<current>）加/改 | 衝突類型 | 建議 |
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

### Phase 3：同步其他 feature worktree（onto trunk）

Trunk 模型沒有 parent-child stack；多個 feature worktree 共用同一 `.git`，可選擇一併 rebase onto 同一 trunk。**只 rebase 非 trunk 的 feature worktree**（trunk 永不被 rebase，鐵律 2）。

1. **`git worktree list`** — 取得所有 worktree
2. 對每個**非 trunk** 的 feature worktree：先 `git -C <path> status --porcelain` 確認狀態
3. **Rebase onto trunk**：`git -C <path> rebase [--autostash] <branch>`（不是 rebase 彼此，鐵律 3）；dirty 處理同 Phase 1（預設停下問 / `--autostash` 自動 stash）

無其他 feature worktree → 跳過此階段。

每步 rebase 後同 Phase 2 的結果處理（成功印出 / 衝突停下）。

> 要讓 feature 的工作**進 trunk**：Phase 2/3 只是把 feature rebase 到 trunk 之上（feature 變 trunk 後代）；最後在 trunk worktree 跑 `git merge --ff-only <feature>` 才真正推進 trunk（鐵律 4）。

### Phase 4：報告

```
## Rebase Report

當前: replay → trunk: main

### 結果
✅ replay: rebase onto main（5 commits replayed）
✅ backbone: rebase onto main（3 commits replayed）  [Phase 3 同步其他 feature]

### 總結
2/2 成功，0 衝突
```

---

## 參數

| 參數 | 說明 |
|------|------|
| **\<branch\>** | 「另一端」分支，**角色由當前 branch 決定**（見 Phase 0）：當前 = trunk → `<branch>` 是 feature；當前 = feature → `<branch>` 是 trunk |
| **--autostash** | dirty 工作目錄時自動 stash→rebase→pop（預設停下問；**僅 rebase 路徑**）。帶旗標 = 你知道有 WIP、要保留、且準備好處理 pop 衝突 |

**對比例子**：
- 在 `main`（trunk）上 `/rebase replay` → `<branch>` = `replay`（feature）→ `git merge --ff-only replay`（吸收步）
- 在 `replay`（feature）上 `/rebase main` → `<branch>` = `main`（trunk）→ `git rebase main`

---

## 執行約束

### 強制

- 必須先確認當前分支和工作目錄狀態
- 必須當前 worktree clean 才能 rebase（帶 `--autostash` 例外：dirty 由 git 自動 stash/pop）
- 同步其他 feature worktree 前，每個必須先確認狀態（同 `--autostash` 例外）
- 必須使用 `git -C <path>` 操作跨 worktree，禁止 `cd`
- 衝突時必須分析雙方變更意圖，提出解決方案，等用戶確認後才執行
- 未經用戶確認不得執行 `git rebase --continue`

### 禁止

- ❌ **`git checkout --theirs` / `git checkout --ours`** — 這是核彈級操作，直接丟棄一方所有變更。必須逐衝突 Read + Edit 精確解決
- ❌ 未經用戶確認就解決衝突並 continue rebase
- ❌ `cd` 到其他 worktree 目錄
- ❌ 跳過 clean 檢查直接 rebase
- ❌ **未先 `git branch --show-current` 分流 arg 角色就動作**（本命令最常見誤判：假設 arg 一律是 trunk）
- ❌ **當前 = trunk 卻跑 `git rebase`**（鐵律 2；trunk 用 `merge --ff-only` 吸收）

---

## 回復機制

Rebase 完成但用戶不滿意結果時，用 reflog 回復：

```bash
git reflog show <branch> --format="%h %gD: %gs" | head -10
# 找到 rebase 前的 commit（通常是 "rebase (finish)" 之前的條目）
git reset --hard <pre-rebase-commit>
```

⚠️ 如果 branch 已 push 過，回復後需要 `git push --force-with-lease` 同步 remote。同步多個 feature worktree 時，被 push 過的每個都需要 force push。

---

## 流程位置

```
/commit（--push / --rebase）→ /rebase <branch>（feature onto trunk，可選同步其他 feature）
```

獨立使用，通常在 commit 之後或每日開工前執行。
