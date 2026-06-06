---
description: "系統能力地圖生成器。/uc-report"
when_to_use: "Generate a top-down system capability report. Use when you need a comprehensive view of what the system can do, what's not yet implemented, and what code lacks UC coverage."
usage: "/uc-report"
argument-hint: "/uc-report — 產出 uc-report.md（含孤兒偵測）"
allowed-tools: ["Read", "Bash", "Write"]
---

# /uc-report — 系統能力地圖生成器

產出 **top-down 系統能力地圖**（`uc-report.md`），按架構層級組織所有 UC，附可點擊連結。回答「系統能做什麼？什麼還沒做？什麼程式碼沒有被記錄？」

與 [uc-status](uc-status.md)（快速聊天進度儀表板）和 [uc-sync](uc-sync.md)（健康檢查）正交。本命令產出**人類閱讀的檔案報表**，供定期審查。

方法論定義見 [ai-development-guide.md](../ai-development-guide.md) 的「UC-Driven Development」章節。

---

## 價值定位

| 命令 | 回答什麼問題 | 輸出 | 讀者 |
|------|-------------|------|------|
| `/uc-status` | 「多少 UC 做完了？」 | 聊天 | AI agent（開發中快速看） |
| `/uc-sync` | 「UC 索引還準確嗎？」 | 聊天 | AI agent（健康檢查） |
| `/uc-report` | 「系統整體功能地圖長什麼樣？」 | `uc-report.md` 檔案 | 人類（坐下來審查） |

---

## 執行流程

### 步驟 1：檢查資料來源

```bash
test -f .project-snapshot.json && echo "SNAPSHOT_OK" || echo "NO_SNAPSHOT"
```

- **有 snapshot** → 直接消費預計算資料，進入步驟 2
- **無 snapshot** → 提示用戶先跑 `/scan-project`，然後降級到直接掃描 USE-CASES.md（用 `fd` 找檔案 + `rg` 提取 title line，參照 `/uc-status` 的掃描邏輯）

### 步驟 2：讀取與解析

有 snapshot 時，`Read .project-snapshot.json`，提取：

| 資料 | 欄位 | 用途 |
|------|------|------|
| UC 條目 | `uc_registry[]` | 每個 UC 的 ID、status、title、path、source_file、cross_refs |
| UC 依賴邊 | `uc_edges[]` | source/target/type（consumed_by / domain_dep） |
| 失效 UC | `cross_validation[]` | X-path 條目（路徑指向不存在的檔案） |
| 模組清單 | `modules{}` | file_count（孤兒偵測用） |

### 步驟 3：分層組織

按 `source_file` 路徑將 UC 條目歸入 6 個架構層：

| 層級 | 路徑模式 | 模組 |
|------|---------|------|
| L5 Workflow | `*/workflows/USE-CASES.md` | workflows |
| L5 Analysis | `*/rule_forge/`, `*/watchlist/`, `*/strategies/`, `*/ui/` | rule_forge, watchlist, strategies, ui |
| L4 Assembly | `*/datasets/`, `*/model/` | datasets, model |
| L3 Compute | `*/features/`, `*/conditions/`, `*/labels/`, `*/indicators/` | features, conditions, labels, indicators |
| L2 Infrastructure | `*/data/`, `*/adapters/sj/`, `*/venues/`, `*/feed/` | data, adapters, venues, feed |
| L0-L1 Foundation | `*/common/`, `*/config/` | common, config |

**判定方式**：`source_file` 包含對應路徑片段即歸入該層。同一 `source_file` 的 UC 歸入同一層。

### 步驟 4：Workflow 展開

對每個 WF-XX 類型的 UC：

1. 從 `uc_edges` 找所有 `target == WF-XX` 的邊（即哪些 UC 被 WF-XX 消費）
2. 反向查找：從 UC 的 `downstream_consumers` 或 `cross_refs` 包含 WF-XX 的條目
3. 展開為編排流程列表，每項標注狀態和連結

### 步驟 5：待實作全景

過濾 `uc_registry` 中 status 為 📋/🔧/🟡 的條目。對每個待實作 UC：

1. 從 `uc_edges` 找哪些 WF-XX 的消費鏈包含此 UC
2. 標注「阻塞的 Workflow」（如果被 WF 引用）

### 步驟 6：失效 UC

直接使用 `cross_validation` 中 `check_id == "X-path"` 的條目。過濾掉明顯的解析問題（path 包含中文或括號等非路徑字元），只保留真實的檔案缺失。

### 步驟 7：孤兒偵測

**模組級**：

```bash
fd "USE-CASES.md" <專案 library 目錄> --type f
```

比對 `modules` 中的所有模組名 vs 有 USE-CASES.md 的目錄。有 `file_count` 但無 USE-CASES.md 的模組即為孤兒模組。

**檔案級**：

```bash
fd -e py . <專案 library 目錄> --type f
```

比對所有 `.py` 檔案 vs `uc_registry` 中的 `path` 欄位。不在任何 UC 路徑中的 `.py` 檔案列為潛在孤兒。排除 `__init__.py`、`_archive/`、`.venv/`、`scripts/`。

### 步驟 8：產出 uc-report.md

Write 到專案根目錄。格式見下方「輸出格式」。

---

## 輸出格式

```markdown
# System Capability Report — {project}

> 產出命令：`/uc-report` ｜ 資料來源：`.project-snapshot.json`
> 掃描時間：{scan_timestamp}

---

## 總覽

| 層級 | ✅ | 📋 | 🔧 | 🟡 | ❌ | 總計 | 完成率 |
|------|----|----|----|----|----|----|--------|
| L5 Workflow | X | X | X | X | X | XX | XX% |
| L5 Analysis | X | X | X | X | X | XX | XX% |
| L4 Assembly | X | X | X | X | X | XX | XX% |
| L3 Compute | X | X | X | X | X | XX | XX% |
| L2 Infrastructure | X | X | X | X | X | XX | XX% |
| L0-L1 Foundation | X | X | X | X | X | XX | XX% |
| **Total** | **XX** | **XX** | **XX** | **XX** | **XX** | **XX** | **XX%** |

> 完成率 = ✅ / (✅ + 📋 + 🔧 + 🟡 + 🟢)，❌ 不計入分母。

---

## L5 Workflow Layer

### WF-01: DailyWorkflow — ✅

- **編排流程**:
  1. D-14 DailyClose — ✅ → [USE-CASES.md](mosaic_alpha/data/USE-CASES.md)
  2. RF-03 FilterTree — ✅ → [USE-CASES.md](mosaic_alpha/rule_forge/USE-CASES.md)
  3. W-01 NaiveWatchlist — ✅ → [USE-CASES.md](mosaic_alpha/watchlist/USE-CASES.md)
  4. W-02 MLWatchlist — ✅ → [USE-CASES.md](mosaic_alpha/watchlist/USE-CASES.md)

→ [USE-CASES.md](mosaic_alpha/workflows/USE-CASES.md)

### WF-02: LiveTrading — 📋
...（同上展開格式）

---

## L5 Analysis Layer

| UC ID | 名稱 | 狀態 | 實作路徑 | USE-CASES |
|-------|------|------|---------|-----------|
| RF-03 | FilterTree | ✅ | rule_forge/... | [USE-CASES.md](mosaic_alpha/rule_forge/USE-CASES.md) |
| RF-04 | BackboneAnalysis | ✅ | rule_forge/... | [USE-CASES.md](mosaic_alpha/rule_forge/USE-CASES.md) |
| W-01 | NaiveWatchlist | ✅ | watchlist/... | [USE-CASES.md](mosaic_alpha/watchlist/USE-CASES.md) |
| ... | ... | ... | ... | ... |

---

## L4 Assembly Layer

| UC ID | 名稱 | 狀態 | 實作路徑 | USE-CASES |
|-------|------|------|---------|-----------|
| DS-01 | ... | ✅ | datasets/... | [USE-CASES.md](...) |
| ... | ... | ... | ... | ... |

---

## L3 Compute Layer
（同上表格格式）

---

## L2 Infrastructure Layer
（同上表格格式）

---

## L0-L1 Foundation Layer
（同上表格格式）

---

## 📋 待實作全景

| UC ID | 領域 | 名稱 | 狀態 | 阻塞的 Workflow |
|-------|------|------|------|----------------|
| WF-03 | workflows | PaperTrading | 📋 | — |
| W-03 | watchlist | MLWatchlist V2 | 📋 | WF-01（部分） |
| SJ-08 | adapters/sj | Tiered Subscription | 📋 | WF-02 |

---

## ⚠️ 失效 UC（路徑指向不存在檔案）

| UC ID | 預期路徑 | 問題 |
|-------|---------|------|
| SJ-09 | mosaic_alpha/adapters/sj/hub.py | 檔案不存在 |
| ... | ... | ... |

（無問題時顯示「無失效 UC ✅」）

---

## 🔍 孤兒程式碼偵測

### 模組級（有 .py 但無 USE-CASES.md）

| 目錄 | .py 檔案數 | 說明 |
|------|-----------|------|
| mosaic_alpha/cli/ | 4 | 入口層，Domain-First 不需 USE-CASES.md |
| ... | ... | ... |

### 檔案級（不在任何 UC 路徑中的 .py）

| 檔案 | 可能需要 UC？ |
|------|-------------|
| data/fetchers/twse_api.py | 是 — 核心數據源 |
| ... | ... |

（無孤兒時顯示「無孤兒程式碼 ✅」）
```

---

## 連結格式

使用**專案相對路徑**的 markdown link：`[USE-CASES.md](mosaic_alpha/data/USE-CASES.md)`

- GitHub 上：直接可點擊
- VSCode 中：直接可點擊（cmd+click）
- 統一從專案根目錄算相對路徑

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 產出 uc-report.md（含總覽 + 層級 + 待實作 + 失效 UC） |
| **--orphans** | 額外包含孤兒程式碼偵測（模組級 + 檔案級） |

---

## 執行約束

- **產出位置**：`uc-report.md` 放專案根目錄
- **資料來源**：`.project-snapshot.json` 優先；無 snapshot 時降級到直接掃描
- **snapshot 時效**：`scan_timestamp` 超過 24 小時時，提示用戶先跑 `/scan-project`
- **只寫一個檔案**：本命令只 Write `uc-report.md`，不修改任何其他檔案
- **繁體中文輸出**：報告使用繁體中文 + 英文術語
- **排除目錄**：`_archive/`、`node_modules/`、`.venv/`、`scripts/`

---

## 與其他 Command 的協作

| 命令 | 與 /uc-report 的關係 |
|------|---------------------|
| `/uc-status` | 快速進度看板（聊天）；`/uc-report` 是詳細版（檔案） |
| `/uc-sync` | 健康檢查（聊天）；`/uc-report` 產出含失效 UC 段落 |
| `/scan-project` | 產出 `/uc-report` 所需的 `.project-snapshot.json` |
| `/claude:daily-maintain` | 可在 Phase 4 後追加 `/uc-report` 產出報表 |
| `/standup` | 晨間可搭配 `/uc-report` 審查整體狀態 |

> **工作流**: `/scan-project`（更新 snapshot）→ `/uc-report`（產出報表）→ 人類審查 → 針對問題跑 `/uc-sync`
