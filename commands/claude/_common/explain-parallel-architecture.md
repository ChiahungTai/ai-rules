# Explain 平行處理架構與檔案分組邏輯

> **引用情境**: 當 `/explain` 需要處理 >= 5 個檔案時，參考此文件決定平行處理策略和檔案分組方式。

---

## Skill-First 平行處理架構

### 決策流程

```
用戶輸入 ──→ Skill 分析決策
              ↓
     ┌─────────┴─────────┐
     │                   │
 建議並行 ↓            建議序列 ↓
 ┌───────┐            ┌──────────┐
 │並行處理│            │序列處理  │
 └──┬────┘            └────┬─────┘
    ↓                      ↓
 ┌───────┐              ┌───────┐
 │智能分組│              │單一分析│
 └──┬────┘              └───────┘
    ↓
 ┌─────────────────────────────────────┐
 │Skill 建議的最優 Task 數量            │
 │→ 同時執行 → 整合結果                │
 └─────────────────────────────────────┘
```

### 第一步：Skill 可行性分析

```bash
skill: "parallel-processing" "分析解釋任務：$USER_TASK"

# skill 返回決策結果
{
  "recommend_parallel": true/false/user_choice,
  "reason": "基於檔案數量、複雜度、成本效益的詳細分析",
  "optimal_task_count": 3-8,
  "grouping_strategy": "按檔案類型和智能負載平衡分組"
}
```

### 第二步：執行策略選擇

```bash
if skill.recommend_parallel:
    execute_parallel_explain(skill.recommendations)
elif skill.recommend_parallel == "user_choice":
    ask_user_about_parallel_benefit()
else:
    execute_sequential_explain()
```

---

## 動態平行執行策略

當 Skill 建議平行處理時，按以下策略分配 Task：

```bash
# 使用 Skill 建議的最優並行度和分組策略
tasks = create_skill_optimized_groups(skill.grouping_strategy)

# 同時發起多個整合型 Task
Task 1 (content-analyzer):  完整分析 [檔案組1]（內容+結構+上下文）
Task 2 (structure-analyzer): 完整分析 [檔案組2]（架構+關聯+邏輯）
Task 3 (context-analyzer):   完整分析 [檔案組3]（背景+歷史+依賴）

# 最終整合
Task (report-coordinator): 整合所有結果，生成統一解釋報告
```

### Skill-First 優勢

- **智能決策**：基於成本效益分析，避免無效平行
- **最優分組**：Skill 提供最優的檔案分組策略
- **動態調整**：根據實際檔案特性和複雜度調整

---

## 視覺化處理階段

### 階段 2：根據模式生成圖表

```bash
Task (visualization-specialist): 根據 Console 或 MD 模式生成對應圖表
- Console 模式：ASCII 流程圖、架構圖，終端機友善
- MD 模式：skill: "mermaid" 生成專業圖表
  - 流程圖、類圖、時序圖、架構圖
  - 確保 Dark/Light 模式相容
```

### 階段 3：結果整合

```bash
Task (report-coordinator): 整合分析結果，生成完整的分析報告
```

---

## 智能檔案分組策略

```python
def group_files_for_analysis(file_paths):
    """智能分組檔案以進行最適化平行處理"""
    groups = {
        'config': [],      # 配置檔案
        'code': [],        # 程式碼檔案
        'docs': [],        # 文檔檔案
        'tests': [],       # 測試檔案
        'data': []         # 資料檔案
    }

    for path in file_paths:
        if any(config in path for config in ['package.json', 'tsconfig', 'yaml']):
            groups['config'].append(path)
        elif any(code in path for code in ['.py', '.js', '.ts', '.java']):
            groups['code'].append(path)
        elif any(doc in path for doc in ['.md', '.txt', '.pdf']):
            groups['docs'].append(path)
        elif 'test' in path:
            groups['tests'].append(path)
        else:
            groups['data'].append(path)

    return [g for g in groups.values() if g]  # 過濾空群組
```

### 分組原則

- **同類檔案同組**：相同類型的檔案放同一 Task 分析，提高上下文連貫性
- **依賴檔案同組**：有 import/引用關係的檔案盡量同組
- **負載平衡**：各組檔案數量和複雜度盡量均衡
