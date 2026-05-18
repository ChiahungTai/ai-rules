# Agent 與 Worktree 使用規範

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 核心原則

**Agent 是工具不是預設。** 依任務複雜度分級使用，由模型自適應控制並發上限。

---

## 並發控制：自適應模型偵測

### Step 1：偵測自身模型

從系統提示詞的 model 資訊判斷當前 GLM 模型：

| 系統提示詞中的模型 ID | 對應模型 | GLM 模型 |
|---------------------|---------|---------|
| `claude-haiku-*` / `glm-4.7` | haiku | glm-4.7 |
| `claude-sonnet-*` / `glm-5.1` | sonnet | glm-5.1 |
| `claude-opus-*` / `glm-5-turbo` | opus | glm-5-turbo |

### Step 2：查表決定 Agent 策略

偵測到自身 GLM 模型後，查下表決定 Agent 模型和並發上限：

| 主 session GLM 模型 | Agent 模型 | 並發上限 | 說明 |
|--------------------|-----------|---------|------|
| `glm-4.7` (haiku) | haiku | **1** | rate limit 2，保守用 1 |
| `glm-5.1` (sonnet) | sonnet | **4** | rate limit 10，安全用 4 |
| `glm-5-turbo` (opus) | **sonnet**（降級） | **1** | rate limit 1，Agent 降級避開 bottleneck |

**spawn Agent 前必須印出確認**：

```
[Agent] model=sonnet, max=4, current=0
```

這行確認讓使用者知道即將用哪個模型開幾個 Agent。

---

## 任務分級

| 場景 | Agent 使用 | 說明 |
|------|-----------|------|
| 簡單修改（1-2 檔案） | 不用 Agent | 主 session 直接做更快 |
| 研究探索 | 1 個 foreground Agent（`Explore` 類型） | 只需 Read/Grep，不需要 worktree |
| 技術驗證 PoC | 1 個 Agent + `isolation: "worktree"` | 失敗自動清理，零污染 |
| 中型實作（3-8 檔案） | 1-N 個 Agent + worktree | 按模型並發上限控制 |
| 大型改動（20+ 檔案） | `/batch` 命令 | 自動拆分 5-30 單元，每單元獨立 worktree |

---

## Worktree 隔離

### Pre-flight 檢查（spawn 前）

**Worktree 基於 committed state 建立，看不到 uncommitted changes。**

spawn Agent 前必須確認：

1. **Uncommitted dependency check**：
   - Agent 任務是否依賴目前工作區的 uncommitted changes？
   - 是 → **先 commit**（WIP 也可），再 spawn Agent
   - 否 → 直接 spawn

2. **Branch check**：
   - 當前 branch 是否是 Agent 任務的正確 base？
   - 不是 → 先 commit + checkout 到正確 branch，或從正確 branch 建立 feature branch

3. **多 Agent 協作**：
   - 先把前置工作 commit 到 feature branch
   - 再從該 branch spawn 多個 Agent（每個 Agent 都能看到前置工作的成果）

```
典型流程：
1. 在 tagging branch 開發 S1、S2（uncommitted）
2. git checkout -b feat/wave-scalars tagging
3. git commit（commit S2 成果）
4. spawn Agent A + B（從 feat/wave-scalars，都看得到 S2）
```

### 失敗 Agent Cleanup

Agent 失敗後可能留下 orphaned worktrees 和 branches：

```bash
# 列出所有 worktrees
git worktree list

# 清理失敗的 worktrees
git worktree remove <worktree-path> --force

# 刪除對應 branches
git branch -D <worktree-branch>
```

### 成功 Agent 的 Worktree 處理

Agent 完成後，worktree 會由系統自動處理：
- **Agent 未修改檔案** → worktree 自動清理
- **Agent 有修改** → worktree 保留，主 session 讀取結果後手動清理（`git worktree remove`）
- **Agent 因路徑問題編輯了主 worktree** → worktree 為空會被自動清理，但變更已在主 worktree 中

### 何時用 `isolation: "worktree"`

- **PoC 驗證**：不確定方案是否可行，用 worktree 隔離，失敗自動清理
- **平行實作**：多個 Agent 同時修改不同檔案，避免衝突
- **風險操作**：修改核心架構或大量檔案時

### 何時不用

- **純研究**：只 Read/Grep，不修改檔案 → foreground Agent 即可
- **單檔案修改**：在主 session 直接做更簡單
- **Agent 需要修改主 worktree 已有檔案**：isolation 產生副本需手動合併。改動少時直接不用 isolation 更簡單

### Agent spawn 範例

```
# 偵測自身模型：系統提示詞 "You are powered by the model glm-5.1" → sonnet
# 查表 → Agent 模型 = sonnet, 並發上限 = 4
# 印出確認
[Agent] model=sonnet, max=4, current=0

Agent({
  description: "PoC: 驗證 X 方案",
  prompt: "...",
  isolation: "worktree",
  run_in_background: true,
  model: "sonnet"
})
```

**關鍵約束**：`model` 參數必須是查表結果。主 session 是 opus 時 Agent 降為 sonnet，主 session 是 haiku 時 Agent 用 haiku。

### Prompt 路徑紀律

**Agent 在 worktree 中，CWD 是 worktree 目錄。Prompt 中必須用相對路徑，不要用主 worktree 的絕對路徑。**

```
# ❌ 錯誤：給主 worktree 的絕對路徑 → Agent 會編輯主 worktree 而非 worktree
prompt: "修改 /Users/ctai/Github/project/src/main.py"

# ✅ 正確：用相對路徑 → Agent 在自己的 CWD 中操作
prompt: "修改 src/main.py"
```

如果 prompt 中必須引用主 worktree 的檔案（只讀不寫），在 prompt 中標註絕對路徑為「只讀參考，用 Read 讀取」。

---

## PoC → Implement 流程

```
1. Agent 跑 PoC（isolation: "worktree"）
   ├─ 失敗 → worktree 自動清理，回到主 session 討論
   └─ 成功 → 拿到 path + branch，讀取結果確認可行

2. 審查 Agent 產出（不要假設 Agent 寫的程式碼是正確的）
   ├─ 跑測試驗證
   ├─ 檢查測試是否真的觸發了被測路徑（常見問題：mock/default 資料讓測試走了 happy path）
   ├─ /code-review 審查品質
   └─ 修正 Agent 的設計瑕疵（常見：邊界條件、錯誤處理、命名）

3. 確認方向後實作
   ├─ 小範圍 → 主 session 直接做
   └─ 大範圍 → 再 spawn Agent 平行實作（或用 /batch）
```

**Agent 產出品質預期**：核心邏輯通常正確（~80%），但細節（邊界條件、錯誤處理、命名）常需主 session 修正。任務越明確、spec 越清楚，Agent 效率越好。

---

## `/build` 整合

`/build --max-agents N` 的 N 受模型並發上限限制：

```
用戶傳入 --max-agents 8
查表: glm-5.1 → max=4
→ 實際使用 max-agents=4, model=sonnet
```

未傳入 `--max-agents` 時，預設使用查表的並發上限。

---

## 自檢清單

spawn Agent 前確認：
- [ ] 已偵測自身模型（從系統提示詞）
- [ ] 已查表確認 Agent 模型和並發上限
- [ ] 已印出 `[Agent] model=X, max=N, current=M` 確認
- [ ] 當前運行中的 Agent 數量未超過上限
- [ ] 任務確實需要 Agent（非簡單修改或純研究）
- [ ] 需要修改檔案的 Agent 是否需要 `isolation: "worktree"`
- [ ] Agent prompt 包含足夠的 context（Agent 看不到主對話歷史）
- [ ] Agent prompt 包含 `/rules-reminder` 指引（Agent 看不到 auto-loaded rules）
- [ ] Agent prompt 使用相對路徑（不用主 worktree 的絕對路徑，避免編輯錯目標）
- [ ] Uncommitted changes：Agent 是否需要看到？需要 → 先 commit
- [ ] Branch：當前 branch 是否正確？不正確 → 先 checkout
- [ ] 失敗 Agent 留下的 worktrees/branches 已清理（`git worktree list` 確認）
- [ ] Agent 產出 commit 前需用戶確認（參見 commit-consent.md）
