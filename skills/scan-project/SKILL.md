---
name: scan-project
description: >
  Unified project knowledge scanner. Scans Python imports (via scan_imports.py),
  CLAUDE.md Capabilities tables, and .kanban/ cards. Produces dep_graph + findings + fingerprint.
  Use before /daily-maintain or /project-review, or when setting up a new project.
when_to_use: >
  Run before daily-maintain, during init, or when you need mechanical
  cross-validation findings. Also use when dependency graph may be stale.
argument-hint: "[--project-root PATH] [--output PATH] [--init]"
allowed-tools: Bash(uv run python *)
---

# /scan-project — 統一專案知識掃描器

掃描 Python import 依賴、CLAUDE.md Capabilities 表格、.kanban/ 卡片，產出 **dep_graph + findings + fingerprint**。

Schema 定義：[unified-snapshot-schema.md](reference/unified-snapshot-schema.md)

---

## 核心設計

**scan_project.py 做機械性檢查，不產出完整 registry。LLM 需要細節時直接讀取檔案。**

三個產出：
1. **dep_graph** — AST-parsed Python import 關係（LLM 無法自行計算）
2. **findings** — 機械性交叉驗證問題（路徑、tag、重複等）
3. **fingerprint** — 輕量變化偵測（counts + hashes）

內部解析（CLAUDE.md、.kanban/）僅用於計算 findings，**不在輸出中包含 registry**。

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
- 如果沒有：dep-graph 欄位為空，findings 仍正常運作
- 如果沒有 `.kanban/` 目錄：kanban 相關 findings 不產出
- 輸出格式 schema_version: 5

## 產出

`.project-snapshot.json` 包含：

| Section | 來源 | 說明 |
|---------|------|------|
| `dep_graph.modules` | scan_imports.py（如有） | 模組依賴結構（file_count, internal_deps, fan_out 等） |
| `dep_graph.edges` | scan_imports.py（如有） | 模組間 import edges |
| `dep_graph.hotspots` | scan_imports.py（如有） | 高 fan-out imports |
| `findings` | 機械性交叉檢查 | X-cap-path / X-tag-module / X-ep-ready / X6 |
| `fingerprint` | 計數 + 雜湊 | capabilities_total, kanban_total, kanban_by_lane, hashes |

**不在輸出中的**：capabilities_registry、kanban_registry、claude_md_registry、cross_validation（v3 舊格式）。

## 與其他命令整合

| 命令 | 如何使用本 skill |
|------|-----------------|
| `/daily-maintain` | Phase 1 執行本 skill 產出 snapshot（自動模式） |
| `/project-review` | Phase 1 執行本 skill 產出 snapshot（互動模式） |
| `/claude:sync` | 可選：載入 dep_graph 用於 import 驗證 |
| `/claude:init` | 可選：執行本 skill，用 findings 報告缺口 |
| `/doc-health` | 步驟 1 消費 findings，LLM 直接讀 CLAUDE.md + .kanban/ 做品質檢查 |

## 交叉驗證（機械性）

| Check | 說明 | 嚴重度 |
|-------|------|--------|
| X-cap-path | Capabilities 入口路徑不存在（檢查 project root / package root / CLAUDE.md 目錄） | important |
| X-tag-module | Kanban 卡片 `[tag:xxx]` 不對應 mosaic_alpha/ 子目錄 | important |
| X-ep-ready | Next-Up/In-Progress 卡片引用的 EP 檔案不存在 | important |
| X6 | dep-graph 有模組（≥3 files）但無 CLAUDE.md | important |

語義性驗證（X1 dep-graph 矛盾、X8 幽靈 Capabilities 引用）由 `/claude:sync` 和 `/doc-health` 的 LLM 判斷完成。
