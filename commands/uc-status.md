---
description: "USE-CASES 跨領域狀態掃描。/uc-status [路徑]"
when_to_use: "Check USE-CASES completion status across the project. Use for project-wide progress overview."
usage: "/uc-status [路徑]"
argument-hint: "/uc-status — 掃描專案根目錄；/uc-status mosaic_alpha/data — 掃描單一領域"
allowed-tools: ["Read", "Bash"]
---

# /uc-status — USE-CASES 跨領域狀態掃描

USE-CASES 全局進度報告。掃描 library 模組目錄下所有 USE-CASES.md，產出跨領域完成度儀表板。

方法論定義見 [ai-development-guide.md](../ai-development-guide.md) 的「UC-Driven Development」章節。

---

## 執行流程

### 步驟 1：定位掃描範圍

**指定路徑** → 掃描該目錄及其子目錄。
**未指定** → 掃描專案根目錄下所有子目錄。

```bash
fd "USE-CASES.md" <掃描根目錄> --type f
```

排除 `_archive/`、`node_modules/`、`.venv/`、`scripts/`。

### 步驟 2：解析 USE-CASES.md

對每個 USE-CASES.md，提取 title line 的狀態標記。

**兩種標記格式**（向下相容）：
- 標準格式（✅）：`### ✅ D-01: title — [`file.py`](/path/to/file.py)`（markdown link，href 為 `/` 開頭的專案根目錄相對路徑）
- 標準格式（📋）：`### 📋 D-01: title — path/to/dir/`（純文字，尚未實作）
- 舊格式：`### B-01: title 🔧 library`（狀態在後）

**狀態分類**：

| 狀態 | 含義 | 分類 |
|------|------|------|
| ✅ | 已完成 | done |
| 📋 | 待實作 | todo |
| ❌ | 已棄用 | deprecated |
| 🔧 | Library 已實作 / 部分完成 | library |
| 🟡 | 進行中 | in_progress |
| 🟢 | 部分覆蓋（已知限制） | partial |

統計每個領域的 done / todo / deprecated / library / in_progress / partial 數量。

**完成率計算**：`✅ / (✅ + 📋 + 🔧 + 🟡 + 🟢)`，❌ 不計入分母。

### 步驟 3：一致性檢查

1. **格式不一致**：同一 USE-CASES.md 內混用新舊格式
2. **📋 無實作細節**：標記 📋 但缺少前置條件或主要流程描述

### 步驟 4：產出報告

---

## 輸出格式

```markdown
## UC Status Dashboard

### 總覽

| 領域 | ✅ Done | 📋 Todo | ❌ Deprecated | 🔧 Library | 🟡 WIP | 🟢 Partial | ⚠️ Untested | 完成率 |
|------|---------|---------|---------------|------------|--------|------------|-------------|--------|
| data (D) | 25 | 2 | 0 | 2 | 0 | 3 | 8 | 83% |
| backtesting (B) | 2 | 0 | 0 | 8 | 0 | 0 | 0 | 20% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **Total** | **XX** | **XX** | **XX** | **XX** | **XX** | **XX** | **XX** | **XX%** |

> ⚠️ Untested = ✅ UC 中無對應 test 檔案（啟發式偵測：目錄匹配 + 檔名匹配）。UC 標記 `testing: N/A` 不計入。

### 📋 待實作 / 🔧 進行中項目

| UC ID | 領域 | 描述 | 狀態 |
|-------|------|------|------|
| D-31 | data | DailyUpdate Pipeline 化 | 📋 |
| D-36 | data | 同步已發行股數 | 🔧 |
| ... | ... | ... | ... |

### ⚠️ 一致性問題

- [ ] 格式不一致: XXX/USE-CASES.md 混用新舊標記格式
- [ ] 📋 無實作細節: D-XX 標記 📋 但缺少描述

### 建議下一步

- [ ] {基於 📋 項目的優先序建議}
- [ ] {基於一致性問題的修正建議}
- [ ] 執行 `/uc-report --sync-system-map` 同步 SYSTEM-MAP.md

### 功能級別摘要（SYSTEM-MAP.md）

如果專案根目錄存在 `SYSTEM-MAP.md`，附加以下摘要：

```markdown
### SYSTEM-MAP 功能概覽

| 狀態 | 數量 |
|------|------|
| 🏃 Running | X |
| ✅🔍 Verified | X |
| ✅ Built | X |
| ⚠️ Issues | X |
| 📋 Planned | X |
| ❌ Abandoned | X |

**⚠️ 需關注**: [列出標記 ⚠️ 的功能及其問題]
```
```

---

## 執行約束

- **只讀不寫**：本命令只掃描和報告，不自動修改任何檔案
- **快速掃描**：用 `rg` 提取 title line，不完整讀取每個 USE-CASES.md
- **排除目錄**：`_archive/`、`node_modules/`、`.venv/`
- **繁體中文輸出**：報告使用繁體中文 + 英文術語

---

## 與其他 Command 的協作

| 時機 | 建議動作 |
|------|---------|
| /spec 完成 | 執行 /uc-status 確認新 UC 已加入 |
| /build 段落完成 | 執行 /uc-status 確認狀態更新 |
| 每日 /standup | 搭配 /uc-status 檢視整體進度 |
