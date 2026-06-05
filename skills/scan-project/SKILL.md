---
name: scan-project
description: >
  Unified project knowledge scanner. Scans Python imports (via scan_imports.py),
  USE-CASES.md entries, and CLAUDE.md metadata. Produces .project-snapshot.json
  for cross-artifact validation. Use before /claude:sync, /claude:daily-maintain,
  or when setting up a new project.
when_to_use: >
  Run before daily-maintain, during init, or when you need cross-artifact
  validation data. Also use when dependency graph or UC registry may be stale.
argument-hint: "[--project-root PATH] [--output PATH] [--init]"
allowed-tools: Bash(uv run python *)
---

# /scan-project — 統一專案知識掃描器

掃描 Python import 依賴、USE-CASES.md 條目、CLAUDE.md 元資料，產出統一 snapshot 供交叉驗證。

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
- 如果沒有：dep-graph 欄位為空，UC/CLAUDE.md 掃描仍正常運作
- 輸出格式是 scan_imports.py 的 strict superset（schema_version: 2）

## 產出

`.project-snapshot.json` 包含：

| Section | 來源 | 說明 |
|---------|------|------|
| `modules` / `edges` / `hotspots` | scan_imports.py（如有） | Module 依賴結構 |
| `uc_registry` | USE-CASES.md 解析 | 所有 UC 條目（ID、狀態、路徑、交叉引用） |
| `claude_md_registry` | CLAUDE.md 解析 | 所有 CLAUDE.md 元資料（模組邊界、UC 引用） |
| `uc_edges` | 從 uc_registry 推導 | UC→UC 依賴邊 |
| `cross_validation` | 機械性檢查 | X-path / X6 / X7 / X-unique 問題 |

## 與其他命令整合

| 命令 | 如何使用本 skill |
|------|-----------------|
| `/claude:daily-maintain` | Phase 1 執行本 skill 產出 snapshot，Phase 2/3 消費 |
| `/claude:sync` | Step 0.5 載入 `.project-snapshot.json`，用於交叉驗證 |
| `/claude:init` | Phase 1.5 執行本 skill，報告 UC 缺口 |
| `/uc-sync` | 步驟 1 用 `uc_registry` 取代自行解析 |

## 交叉驗證（機械性）

| Check | 說明 |
|-------|------|
| X-path | UC 的 code_path 對應的檔案/目錄不存在 |
| X6 | dep-graph 有模組但無 CLAUDE.md |
| X7 | UC cross-reference 指向不存在的 UC ID |
| X-unique | 同一 UC ID 在多個 USE-CASES.md 定義 |

語義性驗證（X1 dep-graph 矛盾、X8 幽靈 UC 引用）由 `/claude:sync` 和 `/uc-sync` 的 LLM 判斷完成。
