# doc-decode 輸出格式與知識圖譜格式

> 供 `/claude:doc-decode` S4 (WRITE) 和 `--recursive` 知識圖譜產出使用。

---

## 子系統文檔輸出格式

每個子系統產出獨立的 Markdown 文檔，結構如下：

```markdown
# {子系統名稱} — 模組理解文檔

## 模組全貌
[一段話描述模組的核心目標和設計哲學]

## 思考流程：從輸入到輸出
[Pipeline 敘事 — 以數據的視角描述完整轉換流程]

## 核心子系統

### {子系統 1}：{一句話職責}

**設計意圖**：[為什麼需要這個子系統]

**關鍵程式碼**（逐字抄錄自 source）：

```python
# source: path/to/file.py:行號
[10-30 行從 .py 逐字抄錄的程式碼]
```

語義解釋：[這段程式碼在整體流程中做什麼、為什麼這樣寫]

**演算法邏輯**（語義描述，非逐字）：

```
[Pseudo code 或流程描述 — 這是 AI 的理解，不是實際程式碼]
```

### {子系統 2}：{一句話職責}
[同上結構]

## 型別語義
[關鍵型別的語義解釋、為什麼需要、在流程中的位置]

## 設計決策記錄
| 決策 | 選項 | 選擇 | 推斷理由 | 驗證來源 |
|------|------|------|---------|---------|
| [決策點] | [A/B/C] | [選擇] | [從程式碼推斷的理由] | [file.py:行號] |

## 與其他模組的關係
[依賴方向、數據流、整合方式]
```

### 文檔拆分規則

| 情境 | 策略 |
|------|------|
| 模組 < 10 個 .py，單一流程 | 單一文檔 `{module}.md` |
| 模組有明確子系統（如 setup + filter_tree） | 按子系統拆分 `{subsystem}.md` + 總覽 `overview.md` |
| 模組有獨立的配置系統 | 配置拆為獨立文檔 `config.md` |

### 強制子系統拆分

> **設計理念**：大模組不拆分子系統會導致 context dilution — 單一文檔塞入過多內容，每個子系統的理解深度不足。

**觸發條件**：
- 模組 .py 檔案 > 8 → **必須**拆分子系統文檔

**拆分策略**：
- 按 import 叢集分組（不是按檔案數均分）
- 識別方式：分析 .py 間的 import 依賴，找出內聚的子群組
- 每個子系統產出獨立文檔 + 總覽 `overview.md`
- `overview.md` 包含：Pipeline 敘事、子系統導航、型別語義、設計決策

**拆分範例**：
```
rule_forge/ (21 .py) → import 叢集分析 →
  ├── overview.md              (Pipeline 敘事 + 子系統導航)
  ├── condition-system.md      (condition_mapping + condition_auditor)
  ├── setup-classification.md  (setup_classifier + setup_summary + YAML)
  ├── filter-tree.md           (filter_tree + pipeline + sequential_greedy + registry)
  ├── backbone-pipeline.md     (engine + backbone_analysis + backbone_report)
  └── exploratory-analysis.md  (tag_ig_calculator + exploratory_stats + future_label)
```

---

## 知識圖譜輸出（dependency-graph.md）

> **設計理念**：模組間的依賴關係是系統知識的重要組成部分，對 ripple impact 偵測和開發者導航都有價值。

**--recursive 時自動產出**：`source-docs/dependency-graph.md`

**格式**：

```markdown
# Module Dependency Graph — {project_name}

## Direct Dependencies（import 層級）

| 模組 | 依賴 | 被依賴 |
|------|------|--------|
| rule_forge | common, indicators | analytics |
| analytics | rule_forge, features | (none) |
| indicators | common | rule_forge, features, analytics |

## Semantic Dependencies（知識層級）

| 變更類型 | 影響範圍 | 範例 |
|---------|---------|------|
| common/enums.py Enum 值變更 | 全部下游模組 | Interval 新增 "2h" |
| rule_forge/types.py 型別變更 | analytics, engine | ConditionFilter 新增欄位 |
| indicators 新增指標 | features, rule_forge | 新增 VWAP 指標 |

## Ripple Impact Rules

| 觸發 | 連鎖更新 |
|------|---------|
| types.py 變更 | 同模組全部子系統重 decode |
| common/enums.py 變更 | 所有 import 它的模組重 compare |
| YAML 定義檔變更 | 對應子系統重 decode + compare |
```

**增量更新**：`daily-maintain` 的 incremental 模式只更新受影響模組的條目，不重建整份文檔。
