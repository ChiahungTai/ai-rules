---
description: "USE-CASES.md 同步與品質檢查。驗證狀態-實作一致性、路徑有效性、跨引用完整性、Domain-First 合規。"
when_to_use: "Check USE-CASES.md synchronization with code and internal quality. Use when UC status may be stale, paths may have changed, or Domain-First compliance needs verification."
usage: "/uc-sync [目錄路徑] [選項]"
argument-hint: "/uc-sync [目錄路徑] [--quality] [--all] — 預設核心層檢查，--quality 加品質層，--all 全部"
allowed-tools: ["Read", "Bash"]
---

# /uc-sync — USE-CASES.md 同步與品質檢查

驗證 USE-CASES.md 的**狀態準確性**、**內部一致性**、**與程式碼的同步性**。回答「能力索引是否準確反映系統狀態？」

方法論定義見 [ai-development-guide.md](../ai-development-guide.md) 的「UC-Driven Development」章節。
狀態掃描見 [/uc-status](./uc-status.md)（進度報告），本命令專注**一致性與合規性**。

---

## 價值定位

| 命令 | 回答什麼問題 | 類比 |
|------|-------------|------|
| `/uc-status` | 「多少 UC 做完了？」 | 進度儀表板 |
| `/uc-sync` | 「UC 索引還準確嗎？」 | 健康檢查報告 |

UC 索引不準確的後果：AI agent 以為系統有某能力（實作已移除）或不知道某能力（已實作但未記錄）。

---

## 執行分層

| 層級 | 包含角度 | 參數 |
|------|---------|------|
| **核心層** | 狀態-實作一致性 + 路徑有效性 + 跨引用完整性 + Domain-First 合規 | 預設 |
| **品質層** | + 格式合規 + 重複偵測 + 章節歸位 + 消費場景欄位 | `--quality` |
| **完整層** | + 覆蓋缺口 + 過時項目 | `--all` |

### 10 個檢查角度

| # | 角度 | 層級 | 一行摘要 |
|---|------|------|---------|
| 1 | 狀態-實作一致性 | 核心 | ✅ UC 的實作路徑是否仍存在？📋 UC 是否已有程式碼？ |
| 2 | 路徑有效性 | 核心 | 專案相對路徑是否指向存在的檔案？ |
| 3 | 跨引用完整性 | 核心 | Workflow UC 引用的 Domain UC ID 是否存在？孤立 UC ID？ |
| 4 | Domain-First 合規 | 核心 | UC 放置是否符合 library 模組規則？scripts/ 下有無 USE-CASES.md？ |
| 5 | 格式合規 | 品質 | 狀態 emoji、UC ID 格式、路徑格式是否正確？ |
| 6 | 重複偵測 | 品質 | 同一行為是否在多個 USE-CASES.md 重複定義？ |
| 7 | 覆蓋缺口 | 完整 | library 模組缺少 USE-CASES.md？實作功能沒有 UC？ |
| 8 | 章節歸位 | 品質 | ✅ UC 是否仍留在「待實作」章節？ |
| 9 | 過時項目 | 完整 | 🔧/🟡 項目長期未更新？ |
| 10 | 消費場景欄位 | 品質 | ✅ UC 是否缺少「消費場景」欄位？是否仍引用 EP/SM 編號？ |

---

## 檢查角度詳細定義

### 角度 1：狀態-實作一致性（核心）

**核心原則**：UC 狀態必須反映實作的真實狀態。✅ 意味著程式碼存在且可用，📋 意味著程式碼尚不存在。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| ✅ UC 的路徑指向不存在的檔案 | Critical | `test -f <path>` |
| ✅ UC 的路徑指向存在但內容已大幅變更（語義偏移） | Important | spot-check：讀路徑檔案，確認核心 class/function 仍存在 |
| 📋 UC 已有對應程式碼（應升級為 ✅ 或 🔧） | Important | 搜尋 UC 描述中的關鍵字是否出現在 .py 檔案 |
| ❌ UC 的功能是否真的已棄用（被移除或取代） | Suggestion | 確認引用該 UC 的其他 UC 是否仍有效 |

### 角度 2：路徑有效性（核心）

**核心原則**：每個 UC 標題行的路徑必須指向專案中存在的檔案。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| 路徑不存在（檔案被刪除或改名） | Critical | `test -f <path>` |
| 路徑只有檔名無目錄（違反專案相對路徑規則） | Important | 正則匹配：路徑不含 `/` |
| 路徑指向 scripts/（違反 Domain-First） | Important | 正則匹配：路徑以 `scripts/` 開頭 |

### 角度 3：跨引用完整性（核心）

**核心原則**：Workflow UC 引用的 Domain UC ID 必須存在，UC ID 不應孤立。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| Workflow UC 引用的 Domain UC ID 不存在 | Critical | 全文搜尋 UC ID |
| Domain UC 的「下游消費者」引用的 WF-XX 不存在 | Important | 全文搜尋 WF ID |
| UC ID 被引用但從未定義（懸空引用） | Important | 比對引用集 vs 定義集 |
| 同一 UC ID 在多個 USE-CASES.md 重複定義 | Critical | 全域 UC ID 唯一性檢查 |

### 角度 4：Domain-First 合規（核心）

**核心原則**：USE-CASES.md 必須放在 library 模組目錄，不在 scripts/。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| scripts/ 下存在 USE-CASES.md | Critical | `fd "USE-CASES.md" scripts/` |
| Workflow UC 不在 `workflows/` 目錄的 USE-CASES.md 中 | Important | 檢查 WF-XX UC 所在的 USE-CASES.md 路徑 |
| 跨域 UC 誤歸為 Domain UC（「跨領域依賴」引用 ≥ 2 個不同模組但不在 workflows/ 下） | Important | 檢查「跨領域依賴」欄位引用的模組數量 vs 所在目錄 |
| Domain UC 的 ID prefix 與所在目錄不匹配（如 D-XX 在 backtesting/ 下） | Suggestion | 比對 ID prefix 與目錄名 |

**Pipeline vs Workflow 語義判定**（域以程式碼目錄為準，見 guide「Pipeline vs Workflow 區分」）：
- UC 的「編排流程」步驟引用 ≥ 2 個不同模組的 UC ID → 應為 Workflow UC
- Consumer Domain UC（有跨域「領域依賴」但主要邏輯在一個模組）→ 仍為 Domain UC，不算誤歸

### 角度 5：格式合規（品質）

| 檢查項 | 嚴重程度 |
|--------|---------|
| 標題行缺少狀態 emoji 開頭 | Important |
| UC ID 格式不合規（非 `前綴-數字`） | Important |
| 標題行缺少路徑（無 `—` 分隔符） | Important |
| 混用新舊格式（同一 USE-CASES.md 內） | Important |
| 🔧/🟡 標記但缺少說明細節 | Suggestion |

### 角度 6：重複偵測（品質）

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| 不同 UC ID 但描述相似度極高（可能是重複定義） | Important | 比對描述文字 |
| 同一檔案路徑出現在多個 UC 條目 | Important | 搜尋路徑重複 |

### 角度 7：覆蓋缺口（完整）

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| library 模組目錄缺少 USE-CASES.md | Important | `fd` 掃描 library 目錄，比對是否有 USE-CASES.md |
| `.py` 檔案中有公開 class/function 但無對應 UC | Suggestion | 掃描 library 目錄的 .py 檔案 vs UC 條目 |

### 角度 8：章節歸位（品質）

| 檢查項 | 嚴重程度 |
|--------|---------|
| ✅ UC 仍留在「待實作」/「Todo」章節（應搬到正確章節） | Important |
| 「待實作」章節為空但仍存在（可移除） | Suggestion |

### 角度 9：過時項目（完整）

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| 🔧 標記超過 30 天未更新（可能被遺忘） | Suggestion | `git log -p --since="30 days ago" -- "**/USE-CASES.md"` |
| 🟡 標記超過 14 天未更新（可能卡住） | Suggestion | 同上，14 天閾值 |

### 角度 10：消費場景欄位（品質）

**核心原則**：✅ UC 應有「消費場景」欄位（由 `/build` 從 EP Scenario Matrix 提煉），欄位內容必須自包含，不引用 EP/SM 編號（EP 可能歸檔或刪除）。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| ✅ UC 缺少「消費場景」欄位 | Suggestion | 解析 UC 條目，檢查是否含 `- **消費場景**:` 行 |
| 「消費場景」內容仍引用 SM-N 編號 | Important | 正則匹配 `SM-\d+` |
| 「消費場景」內容仍引用 EP 編號或檔名 | Important | 正則匹配 `ep-|EP-\d+|execution-plan` |
| 「消費場景」描述與程式碼行為偏移 | Suggestion | spot-check：欄位描述的情境是否仍存在於程式碼 |

---

## 執行流程

| 步驟 | 名稱 | 觸發 |
|------|------|------|
| 1 | 定位 USE-CASES.md | 預設 |
| 2 | 解析所有 UC 條目 | 預設 |
| 3 | 驗證路徑有效性 | 預設（角度 2） |
| 4 | 驗證狀態-實作一致性 | 預設（角度 1） |
| 5 | 驗證跨引用完整性 | 預設（角度 3） |
| 6 | 驗證 Domain-First 合規 | 預設（角度 4） |
| 7 | 格式合規檢查 | `--quality`（角度 5） |
| 8 | 重複偵測 | `--quality`（角度 6） |
| 9 | 章節歸位檢查 | `--quality`（角度 8） |
| 10 | 消費場景欄位檢查 | `--quality`（角度 10） |
| 11 | 覆蓋缺口掃描 | `--all`（角度 7） |
| 12 | 過時項目掃描 | `--all`（角度 9） |
| 13 | 產出報告 | 預設 |

### 步驟 1：定位 USE-CASES.md

**指定路徑** → 掃描該目錄及其子目錄。
**未指定** → 掃描專案根目錄下所有子目錄。

```bash
fd "USE-CASES.md" <掃描根目錄> --type f
```

排除 `_archive/`、`node_modules/`、`.venv/`、`scripts/`。

### 步驟 2：解析所有 UC 條目

完整讀取每個 USE-CASES.md，提取：
- UC ID、狀態 emoji、描述、路徑（從標題行）
- 跨引用（從「跨領域依賴」、「下游消費者」欄位）
- 所在章節（是否在「待實作」區塊內）

### 步驟 3：驗證路徑有效性

對每個 UC 條目的路徑：
1. `test -f <專案根目錄>/<路徑>` — 檔案是否存在
2. 檢查路徑格式（是否為專案相對路徑、是否指向 scripts/）

### 步驟 4：驗證狀態-實作一致性

對 ✅ UC：spot-check 路徑指向的檔案，確認核心 class/function 仍存在。
對 📋 UC：搜尋描述中的關鍵字是否已出現在 .py 檔案中。

### 步驟 5：驗證跨引用完整性

1. 收集所有 Workflow UC 的「跨領域依賴」欄位中的 UC ID
2. 收集所有 Domain UC 的「下游消費者」欄位中的 UC ID
3. 比對引用集 vs 定義集，找出懸空引用和孤立定義

### 步驟 6：驗證 Domain-First 合規

1. 檢查 WF-XX 類型的 UC 是否在 `workflows/USE-CASES.md` 中
2. 確認掃描範圍內無 scripts/ 下的 USE-CASES.md

### 步驟 10：覆蓋缺口掃描

掃描 library 模組目錄（如 `mosaic_alpha/` 下的子目錄），識別：
- 有 `.py` 檔案但缺少 `USE-CASES.md` 的目錄
- 有 `USE-CASES.md` 但目錄下無 `.py` 檔案（可能已清空）

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 核心層檢查所有 USE-CASES.md |
| **目錄路徑** | 只檢查指定目錄下的 USE-CASES.md |
| **--quality** | 品質層（+ 格式合規 + 重複偵測 + 章節歸位） |
| **--all** | 完整層（10 個角度全部檢查） |
| **--dry-run** | 預覽模式：只報告，不建議修改 |

---

## 輸出格式

### 健康度評分

每個 USE-CASES.md 產出一個健康度評分：

```
健康度 = (通過檢查數 / 總檢查數) × 100%
```

| 評分 | 意義 |
|------|------|
| ≥ 90% | ✅ 健康 |
| 70-89% | ⚠️ 需注意 |
| < 70% | ❌ 需修正 |

### 報告模板

```markdown
## UC Sync Report

### 總覽

| USE-CASES.md | UC 數 | ✅ | 📋 | 🔧 | 路徑問題 | 引用問題 | 格式問題 | 健康度 |
|-------------|-------|----|----|----|---------|---------|---------|--------|
| data/USE-CASES.md | 32 | 25 | 2 | 2 | 1 | 0 | 0 | 96% |
| workflows/USE-CASES.md | 5 | 4 | 1 | 0 | 0 | 1 | 0 | 85% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 🔴 Critical（必須修正）

- [ ] **路徑失效**: D-15「XX 功能」路徑 `data/old_module.py` 已不存在
- [ ] **跨引用斷裂**: WF-01 引用 D-99，但 D-99 不存在於任何 USE-CASES.md

### 🟡 Important（建議修正）

- [ ] **狀態過時**: 📋 D-31 已有實作程式碼，建議升級為 ✅ 或 🔧
- [ ] **Domain-First 違規**: WF-02 定義在 data/USE-CASES.md，應移至 workflows/USE-CASES.md
- [ ] **章節未歸位**: ✅ D-18 仍在「待實作」章節，應搬到「定期維護」

### 💡 Suggestion（可以改善）

- [ ] **覆蓋缺口**: mosaic_alpha/indicators/ 目錄缺少 USE-CASES.md
- [ ] **格式不統一**: D-22 標題缺少路徑（無 — 分隔）

### Sync Summary（結構化結論）

- total_uc: XX
- critical: X
- important: X
- suggestion: X
- health_avg: XX%
- needs_action: true/false
```

---

## 執行約束

- **只讀不寫**：本命令只檢查和報告，不自動修改任何檔案
- **實際驗證**：必須開啟程式碼檔案確認路徑和狀態，不猜測
- **引用來源**：報告問題時標註具體位置（USE-CASES.md:行號）
- **繁體中文輸出**：報告使用繁體中文 + 英文術語

---

## 與其他 Command 的協作

| 命令 | 與 /uc-sync 的關係 |
|------|-------------------|
| `/uc-status` | 互補：status 看進度，sync 看健康。建議 `/uc-status` 後接 `/uc-sync` |
| `/spec` | 定義新 UC 後，用 `/uc-sync --quality` 驗證格式合規 |
| `/build` | 段落完成更新 UC 狀態後，用 `/uc-sync` 驗證狀態準確性 |
| `/code-review` | 第六軸 UC Coverage 驗證覆蓋度；`/uc-sync` 驗證索引品質 |
| `/commit` | 大型變更後建議跑 `/uc-sync` 確認未引入路徑斷裂 |
| `/claude:sync` | CLAUDE.md 同步；`/uc-sync` USE-CASES.md 同步。兩者正交 |

> **工作流**: `/uc-status`（進度）→ `/uc-sync`（健康）→ 修正發現的問題 → `/uc-status`（確認）
