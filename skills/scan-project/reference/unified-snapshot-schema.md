# Unified Snapshot Schema（v5）

> JSON 合約定義：scan_project.py 產出格式，供 daily-maintain / doc-health / sync 消費。

---

## 版本策略

- `schema_version: 1` — 舊格式（scan_imports.py 產出，只含 modules/edges/hotspots）
- `schema_version: 2` — USE-CASES.md 格式（含 uc_registry/uc_edges）
- `schema_version: 3` — 三層文件格式（含 capabilities_registry/kanban_registry/claude_md_registry/cross_validation）
- `schema_version: 5` — 精簡格式（dep_graph/findings/fingerprint，不含 registry）
- **向前不相容**：v5 移除所有 registry，改為 findings + fingerprint

### v3 → v5 遷移

消費端遇到 `schema_version < 5` 的 snapshot 時：
1. **刪除舊 snapshot**：`rm .project-snapshot.json`
2. **重新掃描**：執行 `/scan-project` 產出 v5 snapshot
3. 無需手動遷移——scan_project.py 只產出 v5，不支援向下相容寫入

舊欄位對應：

| v3 欄位 | v5 對應 | 說明 |
|---------|---------|------|
| `capabilities_registry` | —（移除） | LLM 直接讀 CLAUDE.md |
| `kanban_registry` | —（移除） | LLM 直接讀 .kanban/ |
| `claude_md_registry` | —（移除） | LLM 直接讀 CLAUDE.md |
| `cross_validation` | `findings` | 重新命名，更新 check IDs |
| `modules/edges/hotspots` | `dep_graph.modules/edges/hotspots` | 移至 dep_graph 子物件 |
| (無) | `fingerprint` | 新增：變化偵測用 counts + hashes |

---

## 完整結構

```json
{
  "project": "mosaic_alpha",
  "scan_timestamp": "2026-06-09T10:30:00+08:00",
  "schema_version": 5,

  "dep_graph": {
    "modules": {
      "mod_name": {
        "file_count": 88,
        "internal_deps": { "target_mod": ["import_path1"] },
        "external_deps": { "pandas": ["pandas.DataFrame"] },
        "imported_by": ["consumer_mod1"],
        "fan_out": 17
      }
    },
    "edges": [
      { "source": "mod_a", "target": "mod_b", "weight": 3, "imports": ["path1", "path2"] }
    ],
    "hotspots": [
      { "import_path": "mosaic_alpha.common.enums", "imported_by": ["data", "features"], "fan_out": 5 }
    ]
  },

  "findings": [
    {
      "check_id": "X-cap-path",
      "severity": "important",
      "detail": "Capabilities entry path 'runner.py' does not exist (in mosaic_alpha/data/CLAUDE.md)",
      "source_claude_md": "mosaic_alpha/data/CLAUDE.md"
    },
    {
      "check_id": "X-tag-module",
      "severity": "important",
      "detail": "Card '騰落線指標' has tag 'nonexistent' which does not match any mosaic_alpha/ subdirectory",
      "kanban_source": ".kanban/Backlog/騰落線指標.md"
    },
    {
      "check_id": "X-ep-ready",
      "severity": "important",
      "detail": "Card '重構 Pipeline' in Next-Up references EP 'ep-refactor-pipeline.md' but file not found",
      "kanban_source": ".kanban/Next-Up/重構Pipeline.md"
    },
    {
      "check_id": "X6",
      "severity": "important",
      "detail": "Module 'services' has 12 files but no CLAUDE.md",
      "module": "services"
    }
  ],

  "fingerprint": {
    "capabilities_total": 151,
    "capabilities_hash": "c647a67bf05a",
    "kanban_total": 66,
    "kanban_by_lane": { "Backlog": 63, "Next-Up": 2, "Done": 1 },
    "kanban_hash": "0b84e82352fd",
    "claude_md_total": 71
  }
}
```

---

## 欄位說明

### dep_graph

| 欄位 | 型別 | 說明 |
|------|------|------|
| `modules` | dict | 模組依賴結構（key = module name） |
| `edges` | array | 模組間 import edges |
| `hotspots` | array | 高 fan-out imports |

如果專案沒有 `scripts/scan_imports.py`，三個欄位皆為空（`{}`、`[]`、`[]`）。

### findings

機械性交叉驗證問題。LLM 不需要重複這些檢查，直接消費即可。

| 欄位 | 型別 | 說明 |
|------|------|------|
| `check_id` | string | 檢查代碼 |
| `severity` | string | critical / important |
| `detail` | string | 人類可讀的問題描述 |
| 其餘欄位 | any | 依 check_id 而異 |

### fingerprint

輕量變化偵測。用於 daily-maintain Phase 1 的 diff。

| 欄位 | 型別 | 說明 |
|------|------|------|
| `capabilities_total` | int | 所有 CLAUDE.md Capabilities ✅ 條目總數 |
| `capabilities_hash` | string | sorted capability:module:status 的 MD5 前 12 碼 |
| `kanban_total` | int | .kanban/ 卡片總數 |
| `kanban_by_lane` | dict | 各 lane 卡片數 |
| `kanban_hash` | string | sorted title:lane:tags 的 MD5 前 12 碼 |
| `claude_md_total` | int | CLAUDE.md 檔案總數 |

---

## 機械性交叉驗證清單

| check_id | 檢查邏輯 | severity |
|----------|---------|----------|
| `X-cap-path` | Capabilities 入口路徑不存在（檢查 project root / package root / CLAUDE.md 目錄三個候選位置） | important |
| `X-tag-module` | Kanban 卡片的 `[tag:xxx]` 不對應 `mosaic_alpha/` 子目錄 | important |
| `X-ep-ready` | Next-Up/In-Progress 卡片引用的 EP 檔案在 ai-analysis/ 等目錄找不到 | important |
| `X6` | dep-graph modules 中有模組（≥3 files）但該模組目錄下無 CLAUDE.md | important |

**語義性驗證（由 LLM 判斷，不在 findings 中）**：
- X1：dep-graph 矛盾（CLAUDE.md "Does NOT depend on" vs 實際 import edge）
- X8：幽靈 Capabilities 引用（SYSTEM-MAP.md 提到的能力不在 Capabilities 表格中）
