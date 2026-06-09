---
name: scan-project
description: >
  Unified project knowledge scanner. Scans Python imports (via scan_imports.py),
  CLAUDE.md Capabilities tables, and .kanban/ cards. Produces .project-snapshot.json
  for cross-artifact validation. Use before /claude:sync, /claude:daily-maintain,
  or when setting up a new project.
when_to_use: >
  Run before daily-maintain, during init, or when you need cross-artifact
  validation data. Also use when dependency graph or Capabilities registry may be stale.
argument-hint: "[--project-root PATH] [--output PATH] [--init]"
allowed-tools: Bash(uv run python *)
---

# /scan-project — 統一專案知識掃描器

掃描 Python import 依賴、CLAUDE.md Capabilities 表格、.kanban/ 卡片，產出統一 snapshot 供交叉驗證。

Schema 定義：[unified-snapshot-schema.md](reference/unified-snapshot-schema.md)

---

## 執行

```bash
# 掃描當前專案
uv run python ${CLAUDE_SKILL_DIR}/scripts/scan_project.py --project-root . --output .project-snapshot.json

# 首次建立（從零產出）
uv run python ${CLAUDE_SKILL_DIR}/scripts/scan_project.py --init --output .project-snapshot.json

# 輸出到 stdout（pipe 用）
uv run python ${CLAUDE_SKILL_DIR}/scripts/scan_project.py --project-root /path/to/project
```

## Graceful Degradation

- 如果目標專案有 `scripts/scan_imports.py`：自動 import 並擴展（dep-graph 資料完整）
- 如果沒有：dep-graph 欄位為空，Capabilities/Kanban 掃描仍正常運作
- 如果沒有 `.kanban/` 目錄：`kanban_registry` 為空，Capabilities 掃描仍正常運作
- 輸出格式 schema_version: 3（三層文件體系）

## 產出

`.project-snapshot.json` 包含：

| Section | 來源 | 說明 |
|---------|------|------|
| `modules` / `edges` / `hotspots` | scan_imports.py（如有） | Module 依賴結構 |
| `capabilities_registry` | CLAUDE.md Capabilities 表格 | 所有 ✅ UC 能力（ID、能力、入口、狀態） |
| `kanban_registry` | .kanban/ cards | 所有 Kanban 卡片（ID、lane、標題） |
| `claude_md_registry` | CLAUDE.md 解析 | 所有 CLAUDE.md 元資料（模組邊界、Capabilities 數量） |
| `cross_validation` | 機械性檢查 | X-cap-dup / X-cap-kanban-conflict / X-kanban-orphan / X6 問題 |

## 與其他命令整合

| 命令 | 如何使用本 skill |
|------|-----------------|
| `/claude:daily-maintain` | Phase 1 執行本 skill 產出 snapshot，Phase 2/3 消費 |
| `/claude:sync` | Step 0.5 載入 `.project-snapshot.json`，用於交叉驗證 |
| `/claude:init` | Phase 1.5 執行本 skill，報告 Capabilities 缺口 |
| `/doc-health` | 步驟 1 用 `capabilities_registry` + `kanban_registry` 取代自行解析 |

## 交叉驗證（機械性）

| Check | 說明 |
|-------|------|
| X-cap-dup | 同一 UC ID 出現在多個 CLAUDE.md Capabilities 表格 |
| X-cap-kanban-conflict | 同一 UC ID 同時存在 Capabilities ✅ 和 Kanban active lane |
| X-kanban-orphan | Kanban card 的 UC ID 找不到對應 Capabilities 或模組 |
| X6 | dep-graph 有模組但無 CLAUDE.md |

語義性驗證（X1 dep-graph 矛盾、X8 幽靈 Capabilities 引用）由 `/claude:sync` 和 `/doc-health` 的 LLM 判斷完成。
