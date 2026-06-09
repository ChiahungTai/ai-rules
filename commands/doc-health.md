---
description: "Capabilities + Kanban 健康檢查。12 角度驗證文件準確性，--report 產出完整能力地圖。"
when_to_use: "Check documentation accuracy after /build, before /commit, or during daily maintenance. Use --report for full capability map, --sync-system-map to align SYSTEM-MAP.md with Capabilities status."
usage: "/doc-health [--quality] [--all] [--report] [--sync-system-map]"
argument-hint: "[--quality] [--all] [--report] [--sync-system-map]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# /doc-health — Capabilities + Kanban 健康檢查

> **角色**：documentation 的 lint layer — 檢查所有文件的準確性，回答「文件準確嗎？有沒有過時、斷裂、遺漏？系統整體能力地圖長什麼樣？」

---

## 使用模式

```
/doc-health              → 聊天報告（快速，核心 5 角度）
/doc-health --quality    → 加品質層（格式、CLAUDE.md 品質、消費場景、測試覆蓋）
/doc-health --all        → 全部 12 角度
/doc-health --report     → 產出 doc-health-report.md 檔案（含完整能力地圖）
/doc-health --sync-system-map → 用 Capabilities 狀態同步 SYSTEM-MAP.md
```

---

## 12 個檢查角度

| # | 角度 | 層級 | 一行摘要 | 資料來源 |
|---|------|------|---------|---------|
| 1 | Capabilities-Code 一致性 | 核心 | Capabilities 入口路徑指向的程式碼還存在？核心 class/function 仍存在？ | CLAUDE.md + .py |
| 2 | 路徑有效性 | 核心 | 入口路徑格式正確、檔案存在、不指向 scripts/？ | CLAUDE.md |
| 3 | 跨引用完整性 | 核心 | CLAUDE.md 間的 UC ID 引用、Kanban ↔ CLAUDE.md 的 UC ID 引用都有效？ | CLAUDE.md + .kanban/ |
| 4 | Domain-First 合規 | 核心 | Capabilities 在正確模組的 CLAUDE.md？UC ID 前綴與模組目錄一致？ | CLAUDE.md |
| 5 | 格式合規 | 品質 | Capabilities 表格格式（UC ID、狀態 emoji、路徑格式）正確？ | CLAUDE.md |
| 6 | Kanban-Capabilities 同步 | 核心 | Done/ lane 的卡片都有對應 Capabilities？反之亦然？同一 UC ID 不同時出現在 Capabilities ✅ 和 Kanban active？ | CLAUDE.md + .kanban/ |
| 7 | 覆蓋缺口 | 完整 | library 模組有 .py 但無 CLAUDE.md Capabilities 表格？ | CLAUDE.md + .py |
| 8 | 過時項目 | 完整 | Kanban Backlog 卡片超過 30 天未更新？In-Progress 超過 14 天？ | .kanban/ |
| 9 | 消費場景 | 品質 | Capabilities 行有消費場景資訊？ | CLAUDE.md |
| 10 | Test Coverage | 品質 | Capabilities 對應的程式碼有測試保護？ | CLAUDE.md + tests/ |
| 11 | SYSTEM-MAP 一致性 | 完整 | SYSTEM-MAP 功能狀態與底層 Capabilities + Kanban 一致？ | SYSTEM-MAP.md + CLAUDE.md + .kanban/ |
| 12 | CLAUDE.md 品質 | 品質 | Signal/noise ratio 合理？導航指引有效？無可推導內容？ | CLAUDE.md |

### 角度 6「Kanban-Capabilities 同步」的具體檢查邏輯

這是 Kanban↔CLAUDE.md 的核心同步機制。/build 完成時的原子操作是：（1）CLAUDE.md Capabilities 加一行 +（2）Kanban 卡片移到 Done/。本角度驗證這個原子操作是否完整：

- **正向檢查**：Done/ lane 中每張有 UC ID 的卡片，該 UC ID 是否出現在某個 CLAUDE.md Capabilities 表格中？
- **反向檢查**：每個 CLAUDE.md Capabilities ✅ 條目，其 UC ID 是否曾經存在於 Done/ lane（或從未經過 Kanban，如回溯盤點的 ✅）？
- **衝突檢查**：同一 UC ID 不應同時存在於 Capabilities ✅ 和 Kanban active lanes（Backlog/Next-Up/In-Progress/Review）
- **重複檢查**：同一 UC ID 不應出現在多個 CLAUDE.md Capabilities 表格（UC 不重複原則：同一能力只在一個模組 CLAUDE.md 記錄）
- **遺漏檢查**：Kanban active lanes 中的卡片，其 UC ID 前綴是否與對應模組的 Capabilities 存在性一致？

---

## 執行流程

| 步驟 | 名稱 | 觸發 |
|------|------|------|
| 1 | 定位 CLAUDE.md + .kanban/ | 預設 |
| 1.5 | Snapshot 消費 | `.project-snapshot.json` 存在時 |
| 2 | 解析 Capabilities 表格 + Kanban 卡片 | 預設 |
| 3 | 驗證路徑有效性 | 預設（角度 2） |
| 4 | 驗證 Capabilities-Code 一致性 | 預設（角度 1） |
| 5 | 驗證跨引用完整性 | 預設（角度 3） |
| 6 | 驗證 Domain-First 合規 | 預設（角度 4） |
| 7 | 驗證 Kanban-Capabilities 同步 | 預設（角度 6） |
| 8 | 格式合規 | `--quality`（角度 5） |
| 9 | 消費場景檢查 | `--quality`（角度 9） |
| 10 | Test Coverage | `--quality`（角度 10） |
| 11 | CLAUDE.md 品質 | `--quality`（角度 12） |
| 12 | 覆蓋缺口 | `--all`（角度 7） |
| 13 | 過時項目 | `--all`（角度 8） |
| 14 | SYSTEM-MAP 一致性 | `--all`（角度 11） |
| 15 | 產出報告 | 預設（聊天）或 `--report`（檔案） |

### Snapshot 消費（步驟 1.5）

如果 `.project-snapshot.json` 存在且 < 24 小時：
- 直接使用 `capabilities_registry` 取代步驟 2 的 Capabilities 解析
- 直接使用 `kanban_registry` 取代步驟 2 的 Kanban 解析
- 直接使用 `cross_validation` 的 findings 作為機械性檢查基礎
- 否則自行掃描

**check_id → 角度映射**（消費 snapshot cross_validation 時使用）：

| check_id | 對應角度 | 說明 |
|----------|---------|------|
| `X-cap-dup` | 角度 6 | 同一 UC ID 出現在多個 CLAUDE.md Capabilities |
| `X-cap-kanban-conflict` | 角度 6 | UC ID 同時在 Capabilities ✅ 和 Kanban active |
| `X-kanban-orphan` | 角度 3 | Kanban 卡片 UC ID 不在任何 Capabilities |
| `X6` | 角度 7 | 模組有 .py 但無 CLAUDE.md |

---

## Capabilities 表格解析

- 掃描 `{project_root}/**/CLAUDE.md`（遞迴 glob）
- 搜尋 `## Capabilities` 標題
- 讀取下方 markdown table（`| UC ID | 能力 | 入口 | 狀態 |`）
- 提取每行的 UC ID、能力描述、入口、狀態
- 不存在 `## Capabilities` 的 CLAUDE.md 跳過（不報錯）

## Kanban 掃描邏輯

- 掃描 `.kanban/{Backlog,Next-Up,In-Progress,Review,Done}/*.md`
- **容錯**：lane 目錄不存在時跳過，不報錯
- 提取每張卡片的 UC ID 和所在 lane

---

## 各角度驗證邏輯

### 角度 1：Capabilities-Code 一致性（核心）

對每個 Capabilities ✅ 條目：
1. 解析入口路徑（如 `CLI daily-update / run_daily_update()`）
2. 確認檔案存在
3. `rg` 確認核心 class/function 名稱仍存在
4. ❌ 失敗 → critical

### 角度 2：路徑有效性（核心）

對每個 Capabilities 條目的入口路徑：
1. 格式正確（不以 scripts/ 開頭）
2. 檔案/目錄存在
3. ❌ 失敗 → critical

### 角度 3：跨引用完整性（核心）

1. 收集所有 Capabilities UC ID 和 Kanban 卡片 UC ID
2. CLAUDE.md 內引用的 UC ID 是否都存在於某個 Capabilities 表格？
3. Kanban 卡片的 UC ID 是否都存在於某個 Capabilities 表格或 Backlog？
4. ❌ 孤立 UC ID → critical

### 角度 4：Domain-First 合規（核心）

1. UC ID 前綴是否與 CLAUDE.md 所在模組目錄一致？（D- 應在 data/CLAUDE.md）
2. ❌ 不一致 → important

### 角度 5：格式合規（品質）

1. Capabilities 表格有正確的 4 欄（UC ID / 能力 / 入口 / 狀態）
2. UC ID 格式正確（大寫前綴-數字）
3. 狀態欄有 emoji
4. 💡 不合規 → suggestion

### 角度 7：覆蓋缺口（完整）

1. 列出所有有 .py 但無 CLAUDE.md Capabilities 表格的 library 模組
2. 🟡 缺口 → important

### 角度 8：過時項目（完整）

1. Backlog 卡片 > 30 天未修改 → important
2. In-Progress 卡片 > 14 天未修改 → important
3. Next-Up 卡片 > 7 天未修改 → suggestion

### 角度 9：消費場景（品質）

1. Capabilities 行是否有消費場景資訊（下游消費者欄位或描述中提及消費端）
2. 💡 缺少 → suggestion

### 角度 10：Test Coverage（品質）

1. Capabilities 對應的程式碼是否有 `tests/` 下對應的測試檔案
2. 💡 無測試 → suggestion

### 角度 11：SYSTEM-MAP 一致性（完整）

1. 讀取 SYSTEM-MAP.md（如果存在）
2. 對每個功能區塊，檢查其引用的 UC ID 是否都存在於 Capabilities 或 Kanban
3. 檢查功能狀態是否與底層 UC 狀態一致
4. `--sync-system-map`：自動用 Capabilities + Kanban 狀態推導功能狀態並更新

### 角度 12：CLAUDE.md 品質（品質）

遵循 [claude-writing.md](../rules/claude-writing.md) 和 [encoder-philosophy.md](../commands/claude/_common/encoder-philosophy.md) 品質標準：
1. Signal/noise ratio（無可推導內容、無 API 簽名、無統計資訊）
2. 導航有效性（每個關鍵概念有 `file.py:Class` 指引）
3. 💡 不合格 → suggestion

---

## 聊天報告格式

```markdown
## Doc Health Report

### 總覽

| 模組 | Capabilities | ✅ | 📋 | Kanban sync | 路徑 | 引用 | 健康度 |
|------|-------------|---|---|------------|------|------|--------|
| data/CLAUDE.md | 27 | 27 | 0 | ✅ | 0 | 0 | 100% |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 🔴 Critical（必須修正）
- [ ] ...

### 🟡 Important（建議修正）
- [ ] ...

### 💡 Suggestion（可以改善）
- [ ] ...

### Summary
- total_capabilities: XX
- total_kanban_cards: XX
- kanban_sync_ok: XX/XX
- critical: X / important: X / suggestion: X
- health_avg: XX%
- needs_action: true/false
```

**健康度評分**：每個模組 CLAUDE.md 產出一個健康度（pass/total × 100%）。門檻：≥90% ✅、70-89% ⚠️、<70% ❌。

---

## `--report` 檔案產出

`--report` flag 產出 `doc-health-report.md`，包含：
- 健康度總覽表格（同聊天報告）
- 🔴/🟡/💡 問題清單
- **系統能力地圖**：按模組組織所有 Capabilities，含可點擊連結
- **孤兒偵測**：有 .py 但無 Capabilities 的模組
- **未驗證 Capabilities**：✅ 條目但對應程式碼缺測試

---

## `--sync-system-map` 同步邏輯

1. 讀取 SYSTEM-MAP.md
2. 對每個功能區塊，聚合其引用的 UC ID 狀態：
   - 全部 ✅ + 有整合驗證 → ✅🔍
   - 全部 ✅ 但無整合驗證 → ✅ Built
   - 有 📋/🔧 → 視嚴重度 ⚠️ 或 📋
3. 更新 SYSTEM-MAP.md 中功能的生命週期狀態
4. 報告變更項目

---

## 執行約束

- **容錯**：無 .kanban/ 目錄時只驗 Capabilities，不報錯
- **容錯**：無 SYSTEM-MAP.md 時跳過角度 11，不報錯
- **容錯**：無 `## Capabilities` 的 CLAUDE.md 跳過，不報錯
- `--report` 產出覆蓋既有 `doc-health-report.md`（不備份）
- `--sync-system-map` 修改 SYSTEM-MAP.md 前展示 diff 待確認
