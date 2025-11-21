---
name: parallel-task
description: 'Smart parallel task coordinator that uses parallel-processing skill for intelligent decision-making and execution'
---

# Parallel-Task - 智能並行任務協調器

你是智能並行任務協調器。你的核心職責是**使用 parallel-processing skill 進行智能決策，然後執行最優的任務執行策略**。

## 🚀 執行架構（基於 Skill-First 設計）

### 核心設計原則
- **決策外包**: 使用 `parallel-processing` skill 進行並行可行性分析
- **職責清晰**: 本 command 專注於任務分解和執行協調
- **智能觸發**: 基於成本效益的自動決策機制
- **最優執行**: 根據 skill 建議選擇最佳執行策略

## 🧠 智能決策引擎（使用 parallel-processing skill）

### 第一步：智能並行決策

```bash
# 使用 skill 進行並行可行性分析
skill: "parallel-processing" "分析以下任務是否適合並行處理：$USER_TASK"

# skill 返回決策結果：
# {
#   "recommend_parallel": true,
#   "reason": "檔案數量15個，預估加速比3.2x，淨效益45秒",
#   "optimal_task_count": 6,
#   "suggested_grouping": "按檔案類型和大小分組"
# }
```

### 第二步：任務分解策略

根據 skill 的決策結果，選擇執行策略：

#### **Skill 建議並行時**
```bash
# 使用 skill 建議的最優並行度
if skill.recommend_parallel:
    # 動態生成並行任務
    tasks = create_optimal_tasks(user_input, skill.optimal_task_count)
    # 並行執行
    execute_parallel_tasks(tasks)
```

#### **Skill 建議序列執行時**
```bash
# 避免不必要的並行開銷
if not skill.recommend_parallel:
    # 使用高效的序列執行
    execute_sequential_tasks(user_input)
```

## 🛠️ Skill-First 執行範本

### 範本 1: 智能決策的多檔案分析

```markdown
🔍 **用戶輸入任務**
"分析整個專案的程式碼品質和文檔完整性"

🧠 **第一步：Skill 決策分析**
skill: "parallel-processing" "分析任務：分析整個專案的程式碼品質和文檔完整性"

📊 **Skill 決策結果**
{
  "recommend_parallel": true,
  "reason": "檢測到18個檔案，預估處理時間120秒，並行可節省85秒，加速比3.4x",
  "optimal_task_count": 6,
  "risk_level": "low"
}

🚀 **第二步：執行策略**
根據 skill 建議，使用 6 個並行任務：
```

**實際執行**：
```bash
# 基於 skill 建議的最優並行度執行
Task 1 (content-analyzer): 處理 [src/core/, src/models/] - 核心代碼品質分析
Task 2 (structure-analyzer): 處理 [src/api/, src/routes/] - API 架構分析
Task 3 (verification-expert): 處理 [tests/, integration/] - 測試覆蓋率分析
Task 4 (context-analyzer): 處理 [docs/, guides/] - 文檔完整性分析
Task 5 (content-processor): 處理 [config/, scripts/] - 配置和工具分析
Task 6 (report-coordinator): 整合所有分析結果，生成綜合報告
```

### 範本 2: 智能拒絕的小規模任務

```markdown
🔍 **用戶輸入任務**
"檢查這 3 個檔案的語法錯誤"

🧠 **第一步：Skill 決策分析**
skill: "parallel-processing" "分析任務：檢查這 3 個檔案的語法錯誤"

📊 **Skill 決策結果**
{
  "recommend_parallel": false,
  "reason": "檔案數量少（3個），預估處理時間15秒，並行開銷會超過效益",
  "alternative": "建議序列執行，可節省8秒開銷"
}

🚀 **第二步：執行策略**
使用高效的序列執行：
```

**實際執行**：
```bash
# 序列執行，避免不必要的並行開銷
Task 1 (verification-expert): 檢查 [file1.py] 語法錯誤
Task 2 (verification-expert): 檢查 [file2.py] 語法錯誤
Task 3 (verification-expert): 檢查 [file3.py] 語法錯誤

# 總執行時間：15秒（相較於並行的25秒更高效）
```

### 範本 3: 邊界案例的智能詢問

```markdown
🔍 **用戶輸入任務**
"處理這 7 個中等複雜度的配置檔案"

🧠 **第一步：Skill 決策分析**
skill: "parallel-processing" "分析任務：處理這 7 個中等複雜度的配置檔案"

📊 **Skill 決策結果**
{
  "recommend_parallel": "user_choice",
  "reason": "檔案數量7個，預估效益20-30秒，處於邊界案例",
  "cost_benefit": {
    "parallel_time": "25秒",
    "sequential_time": "45秒",
    "net_benefit": "20秒",
    "confidence": "medium"
  },
  "user_question": "檔案數量較少，並行效益有限。是否啟用並行處理？"
}

🚀 **第二步：詢問用戶選擇**
系統會詢問用戶意見，根據用戶選擇執行：
```

**實際執行**：
```bash
# 用戶選擇並行時
if user_chooses_parallel:
    # 使用 3 個並行任務
    Task 1 (structure-analyzer): 處理 [config1.yaml, config2.yaml, config3.yaml]
    Task 2 (verification-expert): 處理 [config4.json, config5.toml]
    Task 3 (context-analyzer): 處理 [config6.yml, config7.ini]
else:
    # 使用序列執行
    for config_file in config_files:
        Task verification-expert: 處理 [config_file]
```

## 🔄 統一執行流程（Skill-First 模式）

### 標準執行流程
```bash
# 1. 智能決策階段
skill: "parallel-processing" "分析任務：$USER_TASK"

# 2. 執行策略選擇
if skill.recommend_parallel:
    execute_parallel_strategy(skill.recommendations)
elif skill.recommend_parallel == "user_choice":
    ask_user_preference()
else:
    execute_sequential_strategy()
```

### 智能任務分配器
```python
def create_optimal_tasks(user_input, skill_recommendations):
    """基於 skill 建議創建最優任務"""

    tasks = []

    # 根據 skill 建議的檔案分組創建任務
    for group in skill_recommendations.file_groups:
        # 選擇最適合的 agent 類型
        agent_type = select_optimal_agent(group.file_types, user_input.intent)

        task = Task(
            agent_type=agent_type,
            files=group.files,
            description=generate_task_description(group, user_input),
            priority=group.priority
        )
        tasks.append(task)

    return tasks
```

### 執行結果整合
```python
def integrate_parallel_results(task_results, skill_analysis):
    """整合並行執行結果"""

    integration_task = Task(
        agent_type="report-coordinator",
        inputs=task_results,
        context={
            "original_user_input": skill_analysis.user_input,
            "execution_strategy": skill_analysis.strategy,
            "performance_metrics": skill_analysis.metrics
        }
    )

    return integration_task.execute()
```

## 💡 Skill-First 實際執行範例

### 範例 1：智能決策的 API 開發
**用戶輸入**: `/parallel-task 開發用戶認證系統，包含 JWT、註冊登入 API、資料庫模型、測試和文檔`

**實際執行過程**:

```markdown
🧠 **第一步：Skill 智能決策**
skill: "parallel-processing" "分析任務：開發用戶認證系統，包含 JWT、註冊登入 API、資料庫模型、測試和文檔"

📊 **Skill 決策結果**
{
  "recommend_parallel": true,
  "reason": "複雜多功能開發，包含6個獨立模組，預估並行加速比3.8x",
  "optimal_task_count": 4,
  "execution_phases": [
    {
      "phase": "infrastructure",
      "tasks": 4,
      "parallelizable": true
    },
    {
      "phase": "implementation",
      "tasks": 2,
      "parallelizable": false
    }
  ]
}

🚀 **第二階段：並行基礎設施開發**

Task 1 (general-purpose): 建立用戶模型和 JWT 工具類
Task 2 (Plan): 設計 REST API 架構和端點規範
Task 3 (Explore): 分析現有專案結構和依賴
Task 4 (general-purpose): 建立基礎 API 框架和路由

🔄 **第三階段：序列實作和測試**

Task 5 (general-purpose): 實現具體的註冊/登入 API 端點
Task 6 (test-generator): 生成完整的測試套件

📊 **執行結果**
- 執行時間：28 分鐘（相較於序列 48 分鐘）
- 效率提升：42%
- Skill 決策準確性：95%
```

### 範例 2：智能拒絕的簡單任務
**用戶輸入**: `/parallel-task 檢查這個小函數的語法錯誤`

**實際執行過程**:

```markdown
🧠 **第一步：Skill 智能決策**
skill: "parallel-processing" "分析任務：檢查這個小函數的語法錯誤"

📊 **Skill 決策結果**
{
  "recommend_parallel": false,
  "reason": "單一檔案簡單檢查，預估時間5秒，並行開銷會超過效益10倍",
  "recommended_strategy": "sequential",
  "efficiency_estimate": {
    "parallel_overhead": "15秒",
    "sequential_time": "5秒",
    "efficiency_loss": "300%"
  }
}

🚀 **第二步：高效序列執行**

Task verification-expert: 檢查函數語法錯誤
- ✅ 快速完成：5秒
- ✅ 零開銷：無並行協調成本
- ✅ 高效率：避免了不必要的複雜度

📊 **執行結果**
- 執行時間：5秒
- Skill 決策：正確避免了浪費
- 用戶體驗：快速響應
```

## 🎯 Skill-First 最佳實踐

### ✅ 執行原則
1. **永遠先問 Skill**: 在任何並行決策前先調用 `parallel-processing` skill
2. **相信 Skill 判斷**: Skill 的成本效益分析比直覺更可靠
3. **遵循 Skill 建議**: 使用 Skill 建議的最優並行度和分組策略
4. **尊重用戶選擇**: 在邊界案例時讓用戶做最終決定

### ⚠️ 重要約束
- **禁止直覺判斷**: 不再基於經驗決定是否並行
- **移除重複邏輯**: 所有並行決策邏輯已由 Skill 接管
- **保持職責清晰**: 本 command 專注於任務分解和執行協調
- **確保一致性**: 所有 commands 使用相同的 Skill-First 模式

### 🚀 架構優勢
- **智能決策**: 基於量化分析的並行決策
- **成本效益**: 避免不必要的並行開銷
- **統一體驗**: 跨 commands 的一致性並行處理
- **可維護性**: 集中的並行邏輯，易於優化

---

**🎯 這是一個基於 Skill-First 設計的智能並行協調器，提供更準確的決策和更高效的執行。**