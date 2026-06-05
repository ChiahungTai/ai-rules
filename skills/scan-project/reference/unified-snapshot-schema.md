# Unified Snapshot Schema（v2）

> JSON 合約定義：scan_project.py 產出格式，供 daily-maintain / sync / uc-sync 消費。

---

## 版本策略

- `schema_version: 1` — 舊格式（scan_imports.py 產出，只含 modules/edges/hotspots）
- `schema_version: 2` — 新格式（scan_project.py 產出，含 UC/CLAUDE.md/cross_validation）
- **向後相容**：v2 是 v1 的 strict superset，舊欄位不變

---

## 完整結構

```json
{
  "project": "mosaic_alpha",
  "scan_timestamp": "2026-06-05T10:30:00+08:00",
  "schema_version": 2,

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

  "uc_registry": [
    {
      "uc_id": "D-14",
      "status": "✅",
      "title": "每日收盤完整流程 Pipeline",
      "path": "mosaic_alpha/data/daily_close/",
      "source_file": "mosaic_alpha/data/USE-CASES.md",
      "section": "每日收盤更新",
      "line_number": 42,
      "cross_refs": ["WF-01"],
      "domain_deps": ["D-07", "D-08"],
      "downstream_consumers": ["WF-01"]
    }
  ],

  "claude_md_registry": [
    {
      "path": "mosaic_alpha/data/CLAUDE.md",
      "module": "data",
      "exists": true,
      "has_module_boundaries": true,
      "referenced_uc_ids": ["D-08", "D-14"],
      "declared_not_depend_on": ["strategies"]
    }
  ],

  "uc_edges": [
    {
      "source": "WF-01",
      "target": "D-14",
      "type": "orchestrates",
      "source_file": "mosaic_alpha/workflows/USE-CASES.md"
    },
    {
      "source": "D-14",
      "target": "D-07",
      "type": "domain_dep",
      "source_file": "mosaic_alpha/data/USE-CASES.md"
    }
  ],

  "cross_validation": [
    {
      "check_id": "X-path",
      "severity": "critical",
      "detail": "UC D-15 path mosaic_alpha/data/fetchers/industry.py does not exist",
      "uc_id": "D-15",
      "path": "mosaic_alpha/data/fetchers/industry.py"
    },
    {
      "check_id": "X6",
      "severity": "important",
      "detail": "Module 'services' has files but no CLAUDE.md",
      "module": "services"
    },
    {
      "check_id": "X7",
      "severity": "critical",
      "detail": "UC TE-01 cross-references SE-01 which does not exist",
      "source_uc": "TE-01",
      "broken_ref": "SE-01"
    },
    {
      "check_id": "X-unique",
      "severity": "critical",
      "detail": "UC ID D-07 defined in multiple files: data/USE-CASES.md, cli/USE-CASES-data.md",
      "uc_id": "D-07",
      "source_files": ["data/USE-CASES.md", "cli/USE-CASES-data.md"]
    }
  ]
}
```

---

## 欄位說明

### uc_registry

| 欄位 | 型別 | 說明 |
|------|------|------|
| `uc_id` | string | UC 唯一識別碼（如 D-14、WF-01） |
| `status` | string | 狀態 emoji（✅📋🔧❌🟡🟢） |
| `title` | string | UC 標題（標題行中冒號後的文字） |
| `path` | string | 實作路徑（標題行中 — 後的文字），可能為空 |
| `source_file` | string | 所在 USE-CASES.md 的專案相對路徑 |
| `section` | string | 所在章節（最近的 ## 標題） |
| `line_number` | int | 在 source_file 中的行號 |
| `cross_refs` | string[] | 所有引用的其他 UC ID（合併 domain_deps + downstream_consumers + 編排流程中的引用） |
| `domain_deps` | string[] | 「跨領域依賴」或「領域依賴」欄位中的 UC ID |
| `downstream_consumers` | string[] | 「下游消費者」欄位中的 UC ID |

### claude_md_registry

| 欄位 | 型別 | 說明 |
|------|------|------|
| `path` | string | CLAUDE.md 的專案相對路徑 |
| `module` | string | 所屬模組名稱（從路徑推導） |
| `exists` | bool | 檔案是否存在 |
| `has_module_boundaries` | bool | 是否包含 Module Boundaries 段落 |
| `referenced_uc_ids` | string[] | 內容中引用的所有 UC ID |
| `declared_not_depend_on` | string[] | 「Does NOT depend on」段落中宣告的模組 |

### uc_edges

| 欄位 | 型別 | 說明 |
|------|------|------|
| `source` | string | 依賴方 UC ID |
| `target` | string | 被依賴方 UC ID |
| `type` | string | 關係類型：`orchestrates`（WF→D）、`domain_dep`（D→D）、`consumed_by`（反向引用） |
| `source_file` | string | 定義此關係的 USE-CASES.md |

### cross_validation

| 欄位 | 型別 | 說明 |
|------|------|------|
| `check_id` | string | 檢查代碼（X-path / X6 / X7 / X-unique） |
| `severity` | string | critical / important / suggestion |
| `detail` | string | 人類可讀的問題描述 |
| 其餘欄位 | any | 依 check_id 而異的額外資訊 |

---

## 機械性交叉驗證清單

| check_id | 檢查邏輯 | severity |
|----------|---------|----------|
| `X-path` | UC 的 path 欄位對應的檔案/目錄不存在 | critical |
| `X6` | dep-graph modules 中有模組但該模組目錄下無 CLAUDE.md | important |
| `X7` | UC cross_refs 中引用的 UC ID 不存在於任何 uc_registry | critical |
| `X-unique` | 同一 UC ID 在多個 USE-CASES.md 中定義 | critical |

**語義性驗證（由 LLM 判斷，不在 cross_validation 中）**：
- X1：dep-graph 矛盾（CLAUDE.md "Does NOT depend on" vs 實際 import edge）
- X8：幽靈 UC 引用（CLAUDE.md 提到的 UC ID 不在 uc_registry，可能是 archive 或過時引用）
