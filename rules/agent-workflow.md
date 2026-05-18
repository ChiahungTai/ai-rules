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

### 何時用 `isolation: "worktree"`

- **PoC 驗證**：不確定方案是否可行，用 worktree 隔離，失敗自動清理
- **平行實作**：多個 Agent 同時修改不同檔案，避免衝突
- **風險操作**：修改核心架構或大量檔案時

### 何時不用

- **純研究**：只 Read/Grep，不修改檔案 → foreground Agent 即可
- **單檔案修改**：在主 session 直接做更簡單

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

---

## PoC → Implement 流程

```
1. Agent 跑 PoC（isolation: "worktree"）
   ├─ 失敗 → worktree 自動清理，回到主 session 討論
   └─ 成功 → 拿到 path + branch，讀取結果確認可行

2. 確認方向後實作
   ├─ 小範圍 → 主 session 直接做
   └─ 大範圍 → 再 spawn Agent 平行實作（或用 /batch）
```

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
