---
description: "每日維護：dependency-graph + CLAUDE.md sync + USE-CASES sync 三合一"
when_to_use: "Daily maintenance routine: dependency graph update, CLAUDE.md sync, and USE-CASES sync. Use daily, after refactoring, or before standup. Supports --init for first-time dep-graph generation, --only to run specific phases."
usage: "/claude:daily-maintain [--init] [--only dep-graph|sync|uc-sync]"
argument-hint: "/claude:daily-maintain — 全部執行 | --only dep-graph | --init"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# /claude:daily-maintain — 每日維護三合一

統一的每日文檔健康檢查入口，編排三個維護階段。

---

## 三階段流程

```
Phase 1: Dependency Graph          Phase 2: CLAUDE.md Sync          Phase 3: USE-CASES Sync
─────────────────────────          ──────────────────────          ────────────────────────
scan_imports.py → JSON        →    /claude:sync --changed-since  →  /uc-sync
diff 新舊 JSON                     檢查路徑/簽名/導航有效性         驗證狀態-實作一致性
LLM 策展更新 dep-graph.md          報告或修正同步問題               Domain-First 合規
commit snapshot
```

三個階段獨立，前一階段失敗不阻塞後續。

---

## Phase 1: Dependency Graph 維護

### 步驟 1.1：掃描 import（腳本）

```bash
cd <project-root>
uv run python scripts/scan_imports.py --output .dependency-snapshot.json
```

腳本產出 JSON（modules / edges / hotspots）。

### 步驟 1.2：偵測變化

**`--init` 模式**：跳過 diff，直接進入步驟 1.3。

**維護模式**：比較新舊 JSON 的 `modules` 和 `edges`。沒變 → 報告跳過。有變 → 列出具體變更。

### 步驟 1.3：更新 dependency-graph.md（LLM 策展）

根據掃描資料更新對應段落（Mermaid graph、Direct Dependencies、Hotspots、Ripple Impact Rules 等）。

- `--init`：從零產出所有段落
- 維護模式：只更新受影響的段落，保留既有語義描述

### 步驟 1.4：Commit snapshot

`.dependency-snapshot.json` 隨程式碼一起 commit，作為下次 diff 基準。

---

## Phase 2: CLAUDE.md 同步

執行 [/claude:sync](./sync.md) `--changed-since yesterday --recursive`。

**覆蓋範圍**（由 `--recursive` 保證）：
- **Root CLAUDE.md**（專案根目錄，如 `mosaic_alpha/CLAUDE.md`）— 頂層索引、模組觸發器、全局架構描述
- **Module CLAUDE.md**（各子模組目錄）— 模組內架構、導航、設計理由

檢查：
- 導航有效性（概念 → 程式碼路徑）
- 程式碼一致性（路徑、簽名、行為描述）
- Signal/Noise ratio

低風險自動修正（路徑指向已更名檔案）直接修。其他問題先報告。

---

## Phase 3: USE-CASES 同步

執行 [/uc-sync](../uc-sync.md)。

檢查：
- 狀態-實作一致性（✅ 的 UC 路徑是否存在）
- 路徑有效性
- Domain-First 合規（UC 放在主要實作模組目錄）
- 跨引用完整性

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 依序執行 Phase 1 → 2 → 3 |
| **--init** | Phase 1 用初始生成模式（從零產出 dep-graph） |
| **--only dep-graph** | 只跑 Phase 1 |
| **--only sync** | 只跑 Phase 2 |
| **--only uc-sync** | 只跑 Phase 3 |

---

## 輸出格式

### 無任何變化

```
## Daily Maintenance Report

### Phase 1: Dependency Graph
✅ 無變化（掃描結果與上次一致）

### Phase 2: CLAUDE.md Sync
✅ 無問題（檢查 N 個檔案）

### Phase 3: USE-CASES Sync
✅ 無問題（檢查 N 個 USE-CASES.md）
```

### 有變化

```
## Daily Maintenance Report

### Phase 1: Dependency Graph
⚠️ 偵測到變更
- 新增 deps: features → data
- 新增 hotspots: services (fan_out 2→4)
- 已更新: Mermaid graph, Direct Dependencies 表

### Phase 2: CLAUDE.md Sync
⚠️ 發現 3 個問題
- data/CLAUDE.md: 路徑 data/fetchers/twse.py 已更名 → 自動修正
- features/CLAUDE.md: 缺少 features/spec_base.py 導航 → 建議新增

### Phase 3: USE-CASES Sync
✅ 無問題

### 下一步
確認更新內容後，commit 變更
```

---

## 執行約束

- **腳本先行**：Phase 1 必須先跑 scan_imports.py，禁止跳過
- **階段獨立**：前一階段失敗不阻塞後續（記錄錯誤，繼續）
- **增量更新**：維護模式只更新變化的部分，不重寫整個檔案
- **保留語義**：LLM 策展時保留既有的人工描述，只更新結構性資料
- **報告先行**：先完整報告三個階段的結果，再詢問是否執行修正

---

## 與 launchd 的配合

`run-claude-sync.sh` 已改用本命令：

```bash
claude -p "/claude:daily-maintain"
```

一次跑完三個維護階段。也可拆開執行（避免單次 session 過長）：

```bash
claude -p "/claude:daily-maintain --only dep-graph"
claude -p "/claude:daily-maintain --only sync"
claude -p "/claude:daily-maintain --only uc-sync"
```
