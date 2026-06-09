# Unified Snapshot Schema（v3）

> JSON 合約定義：scan_project.py 產出格式，供 daily-maintain / doc-health / sync 消費。

---

## 版本策略

- `schema_version: 1` — 舊格式（scan_imports.py 產出，只含 modules/edges/hotspots）
- `schema_version: 2` — USE-CASES.md 格式（含 uc_registry/uc_edges）
- `schema_version: 3` — 三層文件格式（含 capabilities_registry/kanban_registry，無 uc_registry）
- **向前不相容**：v3 移除 `uc_registry`、`uc_edges`，新增 `capabilities_registry`、`kanban_registry`

### v2 → v3 遷移

消費端遇到 `schema_version < 3` 的 snapshot 時：
1. **刪除舊 snapshot**：`rm .project-snapshot.json`
2. **重新掃描**：執行 `/scan-project` 產出 v3 snapshot
3. 無需手動遷移——scan_project.py 只產出 v3，不支援向下相容寫入

舊欄位對應：
| v2 欄位 | v3 對應 | 說明 |
|---------|---------|------|
| `uc_registry[]` | `capabilities_registry[]` | 結構不同（v2 扁平 UC 清單 → v3 含 module/status/entry_point） |
| `uc_edges[]` | `cross_validation[]` | 語義不同（v2 UC 間依賴 → v3 機械性交叉驗證 findings） |
| (無) | `kanban_registry[]` | 新增：Kanban 卡片狀態 |
| (無) | `claude_md_registry[]` | 新增：CLAUDE.md 模組邊界資訊 |

---

## 完整結構

```json
{
  "project": "mosaic_alpha",
  "scan_timestamp": "2026-06-09T10:30:00+08:00",
  "schema_version": 3,

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
  ],

  "capabilities_registry": [
    {
      "uc_id": "D-14",
      "module": "data",
      "capability": "每日收盤完整流程 Pipeline",
      "entry_point": "CLI `daily-update` / `run_daily_update()`",
      "status": "✅",
      "source_claude_md": "mosaic_alpha/data/CLAUDE.md",
      "domain_deps": ["D-07", "D-08"],
      "downstream_consumers": ["D-18"]
    }
  ],

  "kanban_registry": [
    {
      "uc_id": "SJ-05",
      "lane": "Backlog",
      "title": "SJ 歷史資料驗證",
      "has_spec": true,
      "source_file": ".kanban/Backlog/SJ-05-sj-history-verify.md"
    }
  ],

  "claude_md_registry": [
    {
      "path": "mosaic_alpha/data/CLAUDE.md",
      "module": "data",
      "exists": true,
      "has_module_boundaries": true,
      "has_capabilities_table": true,
      "capabilities_count": 27,
      "declared_not_depend_on": ["strategies"]
    }
  ],

  "cross_validation": [
    {
      "check_id": "X-cap-dup",
      "severity": "critical",
      "detail": "UC ID D-14 appears in Capabilities of both data/CLAUDE.md and cli/CLAUDE.md",
      "uc_id": "D-14",
      "source_files": ["mosaic_alpha/data/CLAUDE.md", "mosaic_alpha/cli/CLAUDE.md"]
    },
    {
      "check_id": "X-cap-kanban-conflict",
      "severity": "critical",
      "detail": "UC ID D-18 has ✅ in Capabilities but also exists in Kanban Backlog",
      "uc_id": "D-18",
      "capabilities_source": "mosaic_alpha/data/CLAUDE.md",
      "kanban_source": ".kanban/Backlog/D-18-xxx.md"
    },
    {
      "check_id": "X-kanban-orphan",
      "severity": "important",
      "detail": "Kanban card SJ-99 has no matching Capabilities entry and no domain module",
      "uc_id": "SJ-99",
      "kanban_source": ".kanban/Backlog/SJ-99-xxx.md"
    },
    {
      "check_id": "X6",
      "severity": "important",
      "detail": "Module 'services' has files but no CLAUDE.md",
      "module": "services"
    }
  ]
}
```

---

## 欄位說明

### capabilities_registry

> 資料來源：各模組 CLAUDE.md 的 `## Capabilities` 表格

| 欄位 | 型別 | 說明 |
|------|------|------|
| `uc_id` | string | UC 唯一識別碼（如 D-14、VE-15） |
| `module` | string | 所屬模組（從 CLAUDE.md 路徑推導） |
| `capability` | string | 能力描述（Capabilities 表格「能力」欄） |
| `entry_point` | string | 入口（CLI / library function） |
| `status` | string | 狀態 emoji（✅ 或 🟢） |
| `source_claude_md` | string | 所在 CLAUDE.md 的專案相對路徑 |
| `domain_deps` | string[] | 「領域依賴」欄位中的 UC ID |
| `downstream_consumers` | string[] | 「下游消費者」欄位中的 UC ID |

### kanban_registry

> 資料來源：`.kanban/{Backlog,Next-Up,In-Progress,Review,Done}/*.md`

| 欄位 | 型別 | 說明 |
|------|------|------|
| `uc_id` | string | UC 唯一識別碼 |
| `lane` | string | Kanban lane（Backlog / Next-Up / In-Progress / Review / Done） |
| `title` | string | 卡片標題 |
| `has_spec` | bool | card 是否有 spec 連結 |
| `source_file` | string | 卡片檔案的專案相對路徑 |

### claude_md_registry

| 欄位 | 型別 | 說明 |
|------|------|------|
| `path` | string | CLAUDE.md 的專案相對路徑 |
| `module` | string | 所屬模組名稱（從路徑推導） |
| `exists` | bool | 檔案是否存在 |
| `has_module_boundaries` | bool | 是否包含 Module Boundaries 段落 |
| `has_capabilities_table` | bool | 是否包含 Capabilities 表格 |
| `capabilities_count` | int | Capabilities 表格中的 ✅ 條目數 |
| `declared_not_depend_on` | string[] | 「Does NOT depend on」段落中宣告的模組 |

### cross_validation

| 欄位 | 型別 | 說明 |
|------|------|------|
| `check_id` | string | 檢查代碼 |
| `severity` | string | critical / important / suggestion |
| `detail` | string | 人類可讀的問題描述 |
| 其餘欄位 | any | 依 check_id 而異的額外資訊 |

---

## 機械性交叉驗證清單

| check_id | 檢查邏輯 | severity |
|----------|---------|----------|
| `X-cap-dup` | 同一 UC ID 出現在多個 CLAUDE.md Capabilities 表格 | critical |
| `X-cap-kanban-conflict` | 同一 UC ID 同時存在 Capabilities ✅ 和 Kanban active lane（Backlog/Next-Up/In-Progress/Review） | critical |
| `X-kanban-orphan` | Kanban card 的 UC ID 在 Capabilities 中找不到（Done/ 除外，Done/ 是歸檔） | important |
| `X6` | dep-graph modules 中有模組但該模組目錄下無 CLAUDE.md | important |

**語義性驗證（由 LLM 判斷，不在 cross_validation 中）**：
- X1：dep-graph 矛盾（CLAUDE.md "Does NOT depend on" vs 實際 import edge）
- X8：幽靈 Capabilities 引用（SYSTEM-MAP.md 提到的 UC ID 不在 capabilities_registry，可能是過時引用）
