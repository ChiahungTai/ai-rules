---
description: "USE-CASES / GAPS 跨領域狀態掃描。/uc-status [路徑]"
when_to_use: "Check USE-CASES completion status and GAPS progress across the project. Use for project-wide progress overview."
usage: "/uc-status [路徑]"
argument-hint: "/uc-status — 掃描專案根目錄；/uc-status scripts/data_management — 掃描單一領域"
allowed-tools: ["Read", "Bash"]
---

# /uc-status — USE-CASES 跨領域狀態掃描

USE-CASES / GAPS 全局進度報告。掃描所有 USE-CASES.md 和 GAPS.md，產出跨領域完成度儀表板。

方法論定義見 [ai-development-guide.md](../ai-development-guide.md) 的「UC → GAPS 開發方法論」章節。

---

## 執行流程

### 步驟 1：定位掃描範圍

**指定路徑** → 掃描該目錄及其子目錄。
**未指定** → 掃描專案根目錄下所有子目錄。

```bash
fd "USE-CASES.md" <掃描根目錄> --type f
fd "GAPS.md" <掃描根目錄> --type f
```

排除 `_archive/`、`node_modules/`、`.venv/`。

### 步驟 2：解析 USE-CASES.md

對每個 USE-CASES.md，提取 title line 的狀態標記。

**兩種標記格式**（向下相容）：
- 標準格式：`### ✅ D-01: title — path/file.py`（狀態在前，路徑為專案相對路徑）
- 舊格式：`### B-01: title 🔧 library`（狀態在後）

**狀態分類**：

| 狀態 | 含義 | 分類 |
|------|------|------|
| ✅ | 已完成 | done |
| 📋 | 待實作 | todo |
| ❌ | 已棄用 | deprecated |
| 🔧 | library 實作 | library |

統計每個領域的 done / todo / deprecated / library 數量。

### 步驟 3：解析 GAPS.md

對每個 GAPS.md，提取：
- GAP ID 和標題
- 狀態（🔴 🟡 🟢 ✅ ❌ 📋）
- 對應 UC ID（從「對應 UC」欄位）
- 是否有孤立的 GAP（找不到對應 UC）

### 步驟 4：一致性檢查

1. **孤立 GAP**：GAP 引用了不存在的 UC ID
2. **📋 UC 無 GAP**：標記 📋 但沒有對應 GAP 追蹤（情境 A 不需要 GAP，但情境 B/C 的 📋 應有 GAP）
3. **格式不一致**：同一 USE-CASES.md 內混用新舊格式

### 步驟 5：產出報告

---

## 輸出格式

```markdown
## UC Status Dashboard

### 總覽

| 領域 | ✅ Done | 📋 Todo | ❌ Deprecated | 🔧 Library | 完成率 |
|------|---------|---------|---------------|------------|--------|
| data_management (D) | 25 | 2 | 0 | 0 | 93% |
| backtesting (B) | 2 | 0 | 0 | 8 | 20% |
| ... | ... | ... | ... | ... | ... |
| **Total** | **XX** | **XX** | **XX** | **XX** | **XX%** |

### 📋 待實作項目

| UC ID | 領域 | 描述 | 有 GAP 追蹤 |
|-------|------|------|-------------|
| D-31 | data_management | DailyUpdate Pipeline 化 | ✅ GAP-A01 |
| ... | ... | ... | ❌ 無 GAP |

### GAPS 進度

| Gap ID | 狀態 | 描述 | 對應 UC |
|--------|------|------|---------|
| GAP-A01 | 📋 待建 | DailyUpdate Pipeline | D-31 |
| GAP-R02 | 🟡 進行中 | financial_stmt 回填 | D-03 |
| ... | ... | ... | ... |

### ⚠️ 一致性問題

- [ ] 孤立 GAP: GAP-XXX 引用了不存在的 UC YYY
- [ ] 📋 無 GAP 追蹤: D-XX 標記 📋 但沒有對應 GAP
- [ ] 格式不一致: XXX/USE-CASES.md 混用新舊標記格式

### 建議下一步

- [ ] {基於 📋 項目的優先序建議}
- [ ] {基於一致性問題的修正建議}
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
| 發現 📋 無 GAP | 手動在 GAPS.md 補上追蹤項 |
