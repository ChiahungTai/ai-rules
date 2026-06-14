---
description: "POC 驅動的 EP 技術假設驗證。/ep-validate <EP路徑>"
when_to_use: "Validate high-risk technical assumptions in an Execution Plan by writing and executing POCs. Use when EP involves unverified external APIs, SDKs, concurrency models, or serialization formats."
usage: "/ep-validate <EP路徑>"
argument-hint: "<Execution Plan 檔案路徑>"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Agent"]
---

# /ep-validate — POC 驅動的 EP 技術假設驗證

EP Review 抓邏輯矛盾，EP Validate 抓跑不起來的。用 POC 驗證 EP 中的高風險技術假設。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 核心概念

> **EP Review = 靜態分析**（讀文件找矛盾）
> **EP Validate = 動態驗證**（寫程式碼跑起來確認假設）

兩者正交互補，不是取代關係。

### 與 /spec POC 的分工

`/spec` Phase 3 做可行性 POC（能不能做），`/ep-validate` 做深度 POC（效能、邊界、壓力）。

| | /spec POC | /ep-validate |
|--|-----------|-------------|
| 時機 | EP 之前 | EP 之後 |
| 深度 | 可行性驗證（能不能做） | 深度驗證（效能、邊界、壓力） |
| 範圍 | 2-3 個關鍵假設 | EP 所有段落的假設 |
| 產出 | `lab/poc_*.py`（可保留或刪除） | EP 回寫 + `lab/poc_*.py` |

`/spec` 已驗證過的假設，`/ep-validate` 可跳過或做更深入的邊界測試。

---

## 何時需要

| EP 特徵 | 需要 EP Validate？ | 說明 |
|---------|-------------------|------|
| 外部系統整合（API、SDK） | ✅ 需要 | 跨框架互動 pseudo code 看不出 |
| 新演算法 / 數學模型 | ✅ 需要 | 邊界行為難從 pseudo code 推斷 |
| 效能敏感路徑 | ✅ 需要 | 延遲假設需要實測 |
| 跨語言 / 跨進程通訊 | ✅ 需要 | 序列化、IPC 細節不跑不知道 |
| 無外部互動的變更（純重構、配置、文檔） | ❌ 不需要 | 不涉及技術風險，EP Review 足夠 |

**觸發時機**：
- 預設：EP Review → EP Validate → `/build`（靜態先、動態後）
- 例外：EP 含「致命假設」（假設錯了整個 EP 要重寫）→ 可跳過 Review 先跑 Validate

---

## 與 EP Review 的順序

**預設**：EP Review → EP Validate（靜態先、動態後）

理由：EP Review 低成本高速度，先抓邏輯問題可減少後續 POC 數量；POC 基於邏輯正確的 EP，假設清單更精確。

**例外**：EP 含致命技術假設時，先 Validate 確認技術可行，再 Review 檢查邏輯。

判斷原則：**如果你心裡有「這個假設錯了整個 EP 要重寫」的疑慮 → 先 Validate。**

---

## 執行流程

### Phase 1: 假設識別

讀取 EP，識別高風險技術假設：

1. 掃描 EP 所有段落的 Pseudo Code 和 Context
2. 找出「未經外部系統驗證」的假設（API 行為、SDK 用法、序列化格式、併發模型、效能預期等）
3. 每個假設標記風險等級

**風險等級**：

| 等級 | 定義 | POC 失敗後果 |
|------|------|-------------|
| 致命 | 假設錯了整個 EP 要重寫 | 回到 `/spec` 或 `/execution-plan` 重新規劃 |
| 高 | 假設錯了對應段落要大改 | 修正 EP 該段落 + 可能影響上下游段落 |
| 中 | 假設錯了需調整實作細節 | 微調 Pseudo Code，不影響段落結構 |

輸出 POC 清單（展示給用戶確認後再執行）：

| POC # | 假設 | 風險 | 驗證標的 | 預期結果 |
|-------|------|------|---------|---------|
| 1 | [假設描述] | 致命 | [具體驗證什麼] | [通過的定義] |

### Phase 2: POC 生成與執行

對每個假設生成 POC 並執行：

1. 生成 `lab/poc_<描述性名稱>.py`（遵循下方 POC 檔案規範）
2. `uv run python lab/poc_<描述性名稱>.py` 執行
3. 記錄結果（✅ 通過 / ❌ 假設錯誤 / ⚠️ 部分通過 + 具體發現）

**POC 設計原則**：
- 每個 POC 聚焦**一個假設**
- 包含 happy path + 至少一個邊界案例
- 必須可獨立執行（不依賴其他 POC 的結果）
- POC 之間可共用外部資源（如 Redis），但邏輯不耦合

### Phase 3: 結果回報與 EP 更新

**回報格式**：

| POC # | 假設 | 結果 | 關鍵發現 |
|-------|------|------|---------|
| 1 | [假設] | ✅ 通過 | [具體發現] |
| 2 | [假設] | ❌ 假設錯誤 | [哪裡錯了 + 正確行為] |

**EP 回寫**（回寫原則同 [ep-review.md](./ep-review.md)）：

在 EP review 區段用 Finding Record 表格(同 ep-review,欄位定義見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)),「問題」欄填 POC 驗證結果:

```
## EP Validate Findings

| ID | 嚴重度 | EP 段落 | 問題(POC 結果) | 建議 | 狀態 |
|----|--------|---------|----------------|------|------|
| 1 | 🔴 | S1 | POC#1 ❌ 假設錯誤 | 修正設計 | implemented |
| 2 | ⚠️ | S2 | POC#2 部分通過 | 調整段落 | needs-confirmation |
```

✅ 通過 → `verified`;❌ 錯誤 → `implemented`(回寫修正)+ 必要時標「需重新 Review」;⚠️ 部分通過 → `needs-confirmation`。

**致命假設被推翻** → 提示用戶：EP 需要大幅修正，建議重新跑 `/execution-plan` 或 `/spec`。

---

## POC 檔案規範

**放置位置**：`lab/poc_<描述性名稱>.py`

**命名慣例**：
- `poc_tick_to_bar.py`（Tick 聚合邏輯驗證）
- `poc_sj_subscription.py`（SJ 訂閱回調驗證）
- `poc_nt_redis_writer.py`（NT + Redis 寫入驗證）

**檔頭格式**：

```python
"""POC: [假設描述]

驗證: [具體驗證標的]
EP 段落: S{N}
風險: [致命/高/中]
"""
```

**生命週期**：
- 驗證期間：保留為活文件（技術決策的證據，可追溯「為什麼這樣設計」）
- 生產化後：由使用者決定何時刪除或歸檔

---

## 輸出格式

```markdown
## 🔬 EP Validate 結果

**EP**: [路徑] | **POC**: [N]（✅ [X] / ❌ [Y] / ⚠️ [Z]）

### POC 清單
| POC | 檔案 | 假設 | 結果 | 關鍵發現 |
|-----|------|------|------|---------|

### EP 回寫紀錄
[段落 + 修正摘要]

### 建議
[可直接 /build / 需修正 EP 後重新 Review / 需重新規劃]
```

---

## 執行約束

- **每個 POC 必須實際執行**（`uv run`），不憑靜態分析宣稱驗證通過（遵守 `must-execute-before-complete` rule）
- **POC 失敗不中止**：繼續驗證其他假設，最後統一回報
- **不生產化**：POC 只驗證假設，不直接成為生產程式碼（生產化在 `/build` 階段，可參考 POC 設計但需遵循生產標準）
- **遵守 [rules-reminder](../skills/rules-reminder/SKILL.md)**：`uv run` 前綴、`rg`/`fd` 取代 `grep`/`find`

---

## 流程位置

```
/spec → /execution-plan（含 EP Review）
  → [/ep-validate]（可選，高技術風險時）
  → /build
```

前置：`/execution-plan`（或手動撰寫的 EP）
後續：`/build`（基於驗證後的 EP）

---

## 語音通知

遵循 `voice-notification` skill：
- **開始**：`say -v Meijia -r 180 "開始 EP 技術驗證"`
- **完成**：`say -v Meijia -r 180 "前輩！技術驗證完成，請看結果～"`
