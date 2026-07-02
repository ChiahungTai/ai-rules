---
name: kanban-board
description: 管理 Tasks.md 看板卡片（讀取、建立、移動、回顧）。用於任務規劃、進度追蹤、每日回顧。觸發詞：看板、kanban、任務看板、卡片、card、lane、backlog、task board、我的任務、today、what's next。
---

# Kanban Board (Tasks.md)

## 概述

Tasks.md 是自架的 Markdown 任務看板。每個 lane 是一個目錄，每張 card 是一個 `.md` 檔案。LLM 透過檔案系統直接操作看板，不需要網頁 UI。

**資料位置**：專案根目錄 `.kanban/`

## Lane 結構

```
.kanban/
├── Backlog/       ← 所有想做的事，未排序（無限制）
├── Next-Up/       ← 排好優先順序，下一個要做（WIP ≤ 3）
├── In-Progress/   ← 正在做（WIP ≤ 2）
└── Done/          ← 完成歸檔（無限制）
```

> **無 Review lane**：AI 開發流程已內建 review（/build 含 Agent Review → /code-review → /commit），不需要獨立的 Review lane。In-Progress 完成後直接移至 Done。

### `.gitkeep` 規則

每個 lane 目錄**必須**包含 `.gitkeep`。Git 不追蹤空目錄，lane 清空後整個目錄會從 repo 消失，導致工具和腳本因路徑不存在而報錯。

- 所有 lane 統一加 `.gitkeep`，不假設某個 lane「不會空」
- 初始化 `.kanban/` 時，建立目錄同時建立 `.gitkeep`
- `/claude:init` 或任何建立 kanban 的流程都必須遵守

### WIP 限制（Work In Progress）

Solo 開發者同時進行太多任務會造成 context switching 損失。移動卡片前必須檢查目標 lane 的卡片數量，超過限制時提醒用戶。

### 移動卡片 = 移動檔案

lane 間的移動是檔案系統的 rename（跨目錄）：

```
Backlog/feature-X.md → Next-Up/feature-X.md
```

## 操作指南

### 讀取看板狀態

```bash
# 總覽：每個 lane 有幾張卡片
fd -e md . .kanban/ --max-depth 2 | rg -o '([^/]+)/[^/]+\.md' -r '$1' | sort | uniq -c | sort -rn

# 查看某個 lane 的所有卡片
fd -e md . .kanban/In-Progress/
```

### 建立卡片

在對應 lane 目錄下建立 `.md` 檔案，檔名即為卡片標題：

```markdown
[tag:module]

# 卡片標題（中文，與檔名相同）

## 目標
[這張卡片要完成什麼]

## 相關
- EP: [EP 路徑或編號]
- 分支: [git branch name]

## 驗收標準
- [ ] [具體可驗證的條件]

## 備註
[額外資訊]
```

**檔名規則**：
- **中文標題**：檔名使用繁體中文，保留必要的英文縮寫（如 NT、SJ、SMA、LGBM）
- **純描述性**：檔名只描述功能，不含編號 prefix
- 範例：`訂閱分級語意重構.md`（而非 `SJ-04-revised-tiered-semantics.md`）
- Tag 負責模組歸屬，檔名只負責描述功能

### 移動卡片

用 `mv` 在 lane 目錄間移動：

```bash
mv .kanban/Next-Up/feature-X.md .kanban/In-Progress/feature-X.md
```

移動後告知用戶變更內容。

### 完成卡片

移動到 `Done/` 時，在卡片末尾加上完成日期：

```markdown
## 完成紀錄
- 完成日期: YYYY-MM-DD
- commit: [commit hash]（如適用）
```

## 與現有流程的整合

### /standup 整合

每日晨間簡報時，順便回報看板狀態：

1. 列出 `In-Progress/` 和 `Next-Up/` 的卡片
2. 昨日 `Done/` 新增的卡片（用 git log 或修改時間判斷）
3. 建議今日聚焦的卡片

### /build 整合

EP 段落完成後：

1. 消費場景隨 Capabilities 寫入一併落地（build 階段 5a 結算，非暫存供 commit）
2. 全部段落完成 → build 階段 5a 結算（情境 A）移動到 `Done/` 並加完成紀錄

### deep-work 整合

自主實作模式啟動時：

1. 從 `Next-Up/` 拉第一張卡片到 `In-Progress/`
2. 實作過程中更新卡片內容（加上決策記錄）
3. 完成後移動到 `Done/`

### /execution-plan 整合

EP UC盤點完成時（自動建卡機制）：

1. 在 `Backlog/` 建立卡片
2. 卡片內記錄 EP 引用的能力描述

## 卡片與 UC 的關係

| 概念 | 追蹤維度 | 生命週期 |
|------|---------|---------|
| **Kanban Card** | 時間（現在做什麼） | 建立 → 移動 → 歸檔到 Done |
| **CLAUDE.md Capabilities** | 功能（系統能做什麼） | 📋 → 🔧 → ✅ |

**關聯方式**：卡片內用能力描述引用 Capabilities 條目，但不取代 Capabilities 的狀態追蹤。一張卡片可能涉及多個能力，一個能力也可能跨多張卡片完成。

## 每週回顧

用戶要求「看板回顧」或「kanban review」時：

1. **統計**：各 lane 卡片數量、本週完成數量
2. **Backlog 整理**：標記過時卡片（超過 30 天未動）、建議刪除或拆分
3. **優先順序**：建議 Backlog → Next-Up 的移動
4. **WIP 健康度**：In-Progress 是否堆積、Next-Up 是否過長

## 注意事項

- **不自動建立卡片**：除非用戶明確要求，或是在 `/execution-plan`、`/build` 等流程中依規則建立
- **不自動刪除卡片**：刪除前必須確認
- **Tag 管理**：LLM 建立或更新卡片時，依模組目錄掃描決定 tag（見專案 CLAUDE.md「Tag 慣例」）。用戶也可透過 Tasks.md 網頁 UI 手動管理 tag 顏色和自訂 tag
- **並行安全**：看板檔案可能同時被網頁 UI 和 LLM 修改，避免同時編輯同一張卡片
