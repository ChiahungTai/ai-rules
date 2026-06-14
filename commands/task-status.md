---
description: "進度儀表板。直接讀取 .kanban/ 目錄和 CLAUDE.md Capabilities，產出進度報告。"
usage: "/task-status [路徑]"
argument-hint: "[專案根目錄路徑，預設當前目錄]"
---

# /task-status — 進度儀表板

> **角色**：Kanban 的 view layer — 把 .kanban/ 目錄結構 + CLAUDE.md Capabilities 翻譯成人可讀的進度表。回答「做到哪了？完成率多少？有沒有過時的卡片？」

---

## 核心哲學

**直接讀取檔案系統，不需要 snapshot registry。**

| 資料來源 | 讀取方式 | 說明 |
|---------|---------|------|
| .kanban/ 目錄 | `fd` + `Read` | Lane = 目錄，Card = .md 檔案，檔名 = title |
| CLAUDE.md | `fd` + `Read` | `## Capabilities` 表格的 ✅ 條目 |
| scan fingerprint | `.project-snapshot.json` | 僅用於判斷是否需要重新掃描（可選） |

---

## 掃描流程

| 步驟 | 操作 | 方式 |
|------|------|------|
| 1 | 列出 Kanban lanes | 讀取 .kanban/ 下的子目錄（Backlog, Next-Up, In-Progress, Done） |
| 2 | 列出每個 lane 的卡片 | `fd -e md . .kanban/{lane}/`，提取檔名（= title）和 line 1 的 `[tag:module]` |
| 3 | 讀取 Capabilities | `fd "CLAUDE.md" <package>/ --type f`，解析 `## Capabilities` 表格的 ✅ 數量 |
| 4 | 偵測過時卡片 | 檔案 mtime：Backlog > 30 天、In-Progress > 14 天、Next-Up > 7 天 |
| 5 | 聚合統計 | 按模組（tag）聚合 Kanban 卡片 + 按 CLAUDE.md 模組聚合 ✅ |
| 6 | 產出 Dashboard | 見下方格式 |

### Snapshot 輔助（可選）

如果 `.project-snapshot.json` 存在且 < 24 小時：
- 使用 `fingerprint` 的 counts 快速呈現總數
- 仍需直接讀取 .kanban/ 以取得卡片標題和過時偵測

---

## Kanban 掃描邏輯

**Kanban 是純檔案系統**（Tasks.md Docker UI 的後端）：

| 概念 | 對應 | 範例 |
|------|------|------|
| Lane | `.kanban/` 子目錄 | `.kanban/Backlog/` |
| Card | `.md` 檔案 | `.kanban/Backlog/<card_title>.md` |
| Title | 檔案 stem | `<card_title>` |
| Tag | Line 1 的 `[tag:xxx]` | `[tag:indicators]` |
| Content | 檔案剩餘內容 | Markdown body |

**Lanes**：`Backlog`、`Next-Up`、`In-Progress`、`Done`

**Tag → 模組歸屬**：Card 的 `[tag:xxx]` 對應 `<package>/xxx/`，用於 Module Breakdown 統計。

**容錯**：lane 目錄不存在時視為 0 張卡片（不報錯）。Done/ 不計入 pending 統計。

## Capabilities 解析

- 掃描 `{project_root}/**/CLAUDE.md`
- 搜尋 `## Capabilities` 標題下的 markdown table
- 計算每個模組的 ✅ 條目數
- 模組 = CLAUDE.md 所在目錄名

---

## 完成率公式

```
done = count(Capabilities ✅)
pending = count(Kanban Active Lanes: Backlog + Next-Up + In-Progress)
rate = done / (done + pending)
```

Done/ 不計入 pending（已完成 → 已在 Capabilities 中）。

---

## 輸出格式

```markdown
## Task Status Dashboard

### Kanban Overview

| Lane | 數量 |
|------|------|
| Backlog | XX |
| Next-Up | X |
| In-Progress | X |
| Done | XXX |

### Module Breakdown

| 模組 | ✅ Capabilities | 📋 Kanban (by tag) | 完成率 |
|------|----------------|-------------------|--------|
| data/ | 27 | 2 | 93% |
| watchlist/ | 3 | 4 | 43% |
| ... | ... | ... | ... |
| **Total** | **146** | **66** | — |

### 🟡 Active Work（Next-Up / In-Progress）
- .kanban/Next-Up/卡片標題.md [tag:xxx]
- .kanban/In-Progress/卡片標題.md [tag:xxx]

### ⚠️ Stale Cards
- .kanban/Backlog/卡片標題.md — XX days unchanged
```

---

## 執行約束

- 容錯：無 .kanban/ 目錄時只顯示 Capabilities 統計，不報錯
- 容錯：無 `## Capabilities` 的 CLAUDE.md 跳過，不報錯
- 過時閾值：Backlog 30 天、In-Progress 14 天、Next-Up 7 天
- 掃描路徑：`<package>/**/CLAUDE.md`（遞迴 glob）
