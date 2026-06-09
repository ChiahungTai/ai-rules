---
description: "Kanban-centric 進度儀表板。顯示 Capabilities 完成率、Kanban lane 分佈、模組 Breakdown、過時卡片。"
usage: "/task-status [路徑]"
argument-hint: "[專案根目錄路徑，預設當前目錄]"
---

# /task-status — Kanban-centric 進度儀表板

> **角色**：Kanban 的 view layer — 把 Kanban lanes + CLAUDE.md Capabilities 翻譯成人可讀的進度表。回答「做到哪了？完成率多少？有沒有過時的卡片？」

---

## 掃描流程

| 步驟 | 操作 | 指令 |
|------|------|------|
| 1 | 定位所有模組 CLAUDE.md | `fd "CLAUDE.md" mosaic_alpha/ --type f --full-path` |
| 2 | 定位所有 Kanban 卡片 | `fd "." .kanban/ --type f --extension md` |
| 3 | 解析 Capabilities 表格 | 從每個 CLAUDE.md 提取 `## Capabilities` 下的表格行 |
| 4 | 解析 Kanban 卡片 | 從每張卡片提取 UC ID 欄位和所在 lane |
| 5 | 聚合統計 | 按模組計算 ✅/📋/🟡 數量 + Kanban lane 分佈 |
| 6 | 計算完成率 | 見下方公式 |
| 7 | 偵測過時卡片 | Backlog > 30 天、In-Progress > 14 天 |
| 8 | 產出 Dashboard | 見下方格式 |

### Snapshot 消費（步驟 1.5）

如果 `.project-snapshot.json` 存在且 < 24 小時：
- 直接使用 `capabilities_registry` 取代步驟 3
- 直接使用 `kanban_registry` 取代步驟 4
- 否則重新掃描

---

## Capabilities 表格解析

- 搜尋 `## Capabilities` 標題
- 讀取下方 markdown table（`| UC ID | 能力 | 入口 | 狀態 |`）
- 提取每行的 UC ID 和狀態 emoji

## Kanban 卡片解析

- 讀取每張 .kanban/{lane}/*.md 卡片
- 從 frontmatter 或 `## 相關` 段落提取 UC ID
- 從檔案路徑判斷 lane（`.kanban/Backlog/` → 📋，`.kanban/Next-Up/` → 🟡 等）
- **容錯**：lane 目錄不存在時視為 0 張卡片（不報錯）
- Done/ lane 的卡片不計入統計（已完成 → 已在 Capabilities 表格中）

---

## 完成率公式

```
done = count(Capabilities ✅) + count(Capabilities ✅🔍) + count(Capabilities 🏃)
pending = count(Kanban Backlog) + count(Kanban Next-Up) + count(Kanban In-Progress) + count(Kanban Review)
rate = done / (done + pending)
```

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
| Review | X |
| Done | XXX |

### Module Breakdown
| 模組 | ✅ Capabilities | 📋 Backlog | 🟡 Active | 完成率 |
|------|----------------|-----------|----------|--------|
| data/ | 27 | 0 | 0 | 100% |
| watchlist/ | 3 | 4 | 0 | 43% |
| ... | ... | ... | ... | ... |
| **Total** | **146** | **31** | **0** | **82%** |

### ⚠️ Stale Cards
- .kanban/Backlog/SJ-05-xxx.md — XX days unchanged
- .kanban/In-Progress/FE-12-xxx.md — XX days unchanged

### SYSTEM-MAP Summary
（如果 SYSTEM-MAP.md 存在，附上功能狀態摘要）
```

---

## 掃描路徑

`mosaic_alpha/**/CLAUDE.md`（遞迴 glob，涵蓋 nested 目錄如 `adapters/sj/CLAUDE.md`）

---

## 執行約束

- 容錯：無 .kanban/ 目錄時只顯示 Capabilities 統計，不報錯
- 容錯：無 `## Capabilities` 的 CLAUDE.md 跳過，不報錯
- 過時閾值：Backlog 30 天、In-Progress 14 天、Next-Up 7 天
