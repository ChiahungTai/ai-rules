---
description: "文件健康檢查。消費 scan findings + LLM 直接讀取驗證文件準確性。"
when_to_use: "Check documentation accuracy after /build, before /commit, or during daily maintenance. Use --report for full report, --sync-system-map to align SYSTEM-MAP.md."
usage: "/doc-health [--quality] [--all] [--report] [--sync-system-map]"
argument-hint: "[--quality] [--all] [--report] [--sync-system-map]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# /doc-health — 文件健康檢查

> **角色**：documentation 的 lint layer — 檢查所有文件的準確性，回答「文件準確嗎？有沒有過時、斷裂、遺漏？」

---

## 核心哲學

**scan_project.py 做機械性檢查，LLM 做判斷性檢查。不依賴 snapshot registry。**

| 檢查類型 | 負責者 | 資料來源 |
|---------|--------|---------|
| 機械性（路徑、tag、重複） | scan_project.py → `findings` | `.project-snapshot.json` |
| 判斷性（品質、導航、覆蓋） | LLM 直接讀取 | CLAUDE.md + .kanban/ |

LLM 需要細節時，直接 Read CLAUDE.md 和 .kanban/ 檔案，不依賴中間 registry。

---

## 使用模式

```
/doc-health              → 聊天報告（scan findings + 核心品質檢查）
/doc-health --quality    → 加品質層（CLAUDE.md signal/noise + 導航有效性）
/doc-health --all        → 全部檢查（含過時卡片、SYSTEM-MAP 同步）
/doc-health --report     → 產出 doc-health-report.md 檔案
/doc-health --sync-system-map → 用 Capabilities 狀態同步 SYSTEM-MAP.md
```

---

## 執行流程

| 步驟 | 名稱 | 觸發 | 說明 |
|------|------|------|------|
| 1 | 消費 Scan Findings | 預設 | 讀 `.project-snapshot.json` 的 `findings`，按嚴重度呈現 |
| 2 | Capabilities 品質 | 預設 | LLM 直接讀 CLAUDE.md，檢查表格格式 + 入口有效性 |
| 3 | CLAUDE.md 品質 | --quality | LLM 評估 signal/noise + 導航有效性 |
| 4 | 過時卡片 | --all | 讀 .kanban/ 檔案 mtime，標記長期未動卡片 |
| 5 | SYSTEM-MAP 同步 | --all / --sync-system-map | LLM 讀 SYSTEM-MAP.md + Capabilities，比對狀態 |
| 6 | 產出報告 | 預設（聊天）或 --report（檔案） | — |

### 步驟 1：消費 Scan Findings

如果 `.project-snapshot.json` 存在且 < 24 小時：
- 直接呈現 `findings` 陣列中的機械性問題
- 按嚴重度分類：critical / important

如果不存在或過期：
- 告知用戶執行 `uv run python scan_project.py --project-root . --output .project-snapshot.json`
- 或降級為純 LLM 直接讀取模式

**Scan findings 類型**：

| check_id | 說明 | 嚴重度 |
|----------|------|--------|
| X-cap-dup | 同一 UC ID 出現在多個 CLAUDE.md Capabilities | critical |
| X-cap-path | Capabilities 入口路徑不存在 | important |
| X-tag-module | Kanban 卡片 tag 不對應 mosaic_alpha/ 子目錄 | important |
| X-ep-ready | Next-Up/In-Progress 卡片引用的 EP 檔案不存在 | important |
| X6 | 模組有 .py 但無 CLAUDE.md | important |

### 步驟 2：Capabilities 品質（預設）

LLM 直接讀取 CLAUDE.md 的 `## Capabilities` 表格：

- **表格格式**：4 欄（UC ID / 能力 / 入口 / 狀態）完整、狀態 emoji 正確
- **入口有效性**：CLI 命令格式合理、路徑指向存在（scan 的 X-cap-path 已做路徑檢查，此處補充 CLI 命令等判斷）
- **模組覆蓋**：主要模組都有 Capabilities 表格（scan 的 X6 已做機械性檢查）

### 步驟 3：CLAUDE.md 品質（--quality）

遵循 [claude-writing.md](../rules/claude-writing.md) 品質標準：

- **Signal/Noise**：無可推導內容（API 簽名、參數表）、無統計/版本/日期
- **導航有效性**：每個關鍵概念有 `file.py:Class` 指引（導航 Decoder Test）
- **消費場景**：Capabilities 行有下游消費者資訊

### 步驟 4：過時卡片（--all）

讀取 .kanban/ 下每張卡片的檔案修改時間：
- Backlog > 30 天 → important
- In-Progress > 14 天 → important
- Next-Up > 7 天 → suggestion

### 步驟 5：SYSTEM-MAP 同步（--all / --sync-system-map）

1. 讀取 SYSTEM-MAP.md（如果存在）
2. 對每個功能區塊，從 CLAUDE.md Capabilities 讀取 UC ID 狀態
3. 比對功能生命週期狀態是否一致
4. `--sync-system-map`：自動推導並更新 SYSTEM-MAP.md（展示 diff 待確認）

生命週期推導規則：

| 條件 | 狀態 |
|------|------|
| 功能內 UC 全部 ✅ + 有整合驗證 | ✅🔍 Verified |
| 全部 ✅ 但無整合驗證 | ✅ Built |
| 有 📋/🔧 | ⚠️ Issues 或 📋 Planned |

---

## 聊天報告格式

```markdown
## Doc Health Report

### Scan Findings（機械性檢查）

| check_id | 嚴重度 | 說明 | 來源 |
|----------|--------|------|------|
| X-cap-path | important | ... | data/CLAUDE.md |

### 🔴 Critical（必須修正）
- [ ] ...

### 🟡 Important（建議修正）
- [ ] ...

### 💡 Suggestion（可以改善）
- [ ] ...

### Summary
- scan_findings: X (critical: X, important: X)
- quality_issues: X
- needs_action: true/false
```

---

## `--report` 檔案產出

`--report` flag 產出 `doc-health-report.md`，包含：
- 健康度總覽表格
- 🔴/🟡/💡 問題清單（scan findings + 品質檢查）
- **系統能力地圖**：按模組組織所有 Capabilities，含可點擊連結

---

## 執行約束

- **容錯**：無 `.project-snapshot.json` 時降級為純 LLM 檢查，不報錯
- **容錯**：無 .kanban/ 目錄時只檢查 Capabilities，不報錯
- **容錯**：無 SYSTEM-MAP.md 時跳過步驟 5，不報錯
- **容錯**：無 `## Capabilities` 的 CLAUDE.md 跳過，不報錯
- `--report` 產出覆蓋既有 `doc-health-report.md`（不備份）
- `--sync-system-map` 修改 SYSTEM-MAP.md 前展示 diff 待確認
