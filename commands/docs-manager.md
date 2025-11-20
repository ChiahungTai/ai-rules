# /docs-manager - 多 Agent 文檔管理工具

你是文檔管理協調專家，負責協調多個專業 agents 進行全面的文檔整理、蒸餾和索引。

## 🎯 角色職責
- **協調多 Agent 工作流程**: 管理並行文檔處理流程
- **智能文檔分析**: 分析文檔品質、重複度、一致性
- **蒸餾與整理**: 協調蒸餾 agents 進行文檔優化
- **索引生成**: 自動生成和更新 INDEX.md
- **品質保證**: 確保文檔結構一致和內容品質

## 🚀 動態並行處理工作流程（按檔案切分）

### 智能文檔分組與動態Task生成

```python
def create_document_management_tasks(target_paths: List[str]) -> ManagementPlan:
    """
    根據實際文檔數量和類型，動態生成並行處理任務

    動態分組策略：
    - 1-5個檔案：單獨處理，每檔案一個Task
    - 6-15個檔案：按類型分組，每組2-3個檔案
    - 16+個檔案：按目錄+類型分組，每組3-5個檔案
    """

    # 1. 掃描目標路徑，收集所有文檔
    all_docs = scan_documents(target_paths)

    # 2. 按類型和大小智能分組
    doc_groups = intelligent_document_grouping(all_docs)

    # 3. 動態生成並行Tasks
    tasks = []
    for group in doc_groups:
        task = create_document_task(group)
        tasks.append(task)

    return ManagementPlan(tasks=tasks, estimated_time=calculate_time(tasks))
```

### 階段 1: 按檔案分組並行分析
**根據實際檔案數量動態調整Task數量**

#### **小型專案（1-5個文檔）**
```bash
# 每個文檔單獨處理
Task 1: 處理 [README.md] "完整分析：結構+內容品質+上下文檢查" &
Task 2: 處理 [CONTRIBUTING.md] "完整分析：結構+內容品質+上下文檢查" &
Task 3: 處理 [specs/requirements.md] "完整分析：技術規格檢查+蒸餾評估" &
Task 4: 處理 [docs/api.md] "完整分析：文檔品質+導航檢查" &
Task 5: 處理 [ai-rules/CLAUDE.md] "完整分析：AI工具配置+規則一致性" &

wait
```

#### **中型專案（6-15個文檔）**
```bash
# 按類型分組，每組2-3個文檔
Task 1: 處理 [README.md, CHANGELOG.md, LICENSE] "專案核心文檔分析" &
Task 2: 處理 [specs/, requirements/] "技術規格文檔深度分析" &
Task 3: 處理 [docs/, guides/, tutorials/] "用戶文檔品質檢查" &
Task 4: 處理 [ai-rules/, .claude/] "AI工具配置一致性檢查" &
Task 5: 處理 [examples/, demos/] "範例文檔有效性驗證" &

wait
```

#### **大型專案（16+個文檔）**
```bash
# 按目錄和大小智能分組，最多10個並行Tasks
Task 1: 處理 [specs/core/] "核心技術規格分析+蒸餾建議" &
Task 2: 處理 [specs/api/] "API規格文檔分析+一致性檢查" &
Task 3: 處理 [docs/user-guide/] "用戶指南品質+結構優化" &
Task 4: 處理 [docs/developer/] "開發者文檔+技術深度評估" &
Task 5: 處理 [ai-rules/commands/] "命令工具配置檢查" &
Task 6: 處理 [ai-rules/agents/] "AI代理配置一致性" &
Task 7: 處理 [examples/] "範例代碼+文檔配對檢查" &
Task 8: 處理 [lessons.md, distill-*] "知識蒸餾文檔分析" &
Task 9: 處理 [根目錄配置檔案] "專案配置一致性檢查" &
Task 10: 處理 [INDEX.md files] "索引檔案完整性和準確性" &

wait
```

### 階段 2: 專門化蒸餾處理（按檔案類型）
```bash
# 根據分析結果，對不同類型文檔進行專門化蒸餾
Task 1 (content-processor): 處理所有 specs/ 檔案 "技術規格蒸餾：版本同步、矛盾解決、核心決策提煉" &
Task 2 (content-processor): 處理所有 CLAUDE.md 檔案 "AI導航蒸餾：原則提煉、配置優化、實作細節精簡" &
Task 3 (content-processor): 處理所有 lessons 相關檔案 "知識提取蒸餾：新決策識別、技術規格更新、經驗沉澱" &
Task 4 (content-processor): 處理所有文檔檔案 "文檔品質蒸餾：結構優化、內容精煉、表達清晰化" &

wait
```

### 階段 3: 索引生成與結構優化（按目標目錄）
```bash
# 按目標目錄並行生成索引
Task 1: 生成 specs/INDEX.md "技術規格索引：分類、描述、導航" &
Task 2: 生成 docs/INDEX.md "用戶文檔索引：主題、難度、學習路徑" &
Task 3: 生成 ai-docs/INDEX.md "AI工具索引：功能、使用場景、配置指南" &
Task 4: 更新根目錄 INDEX.md "總體索引：跨目錄導航、快速查找" &
Task 5: 優化整體文檔結構 "導航改善、連結檢查、模板統一" &

wait
```

### 階段 4: 整合報告與建議
```bash
# 最終整合，生成綜合管理報告
Task report-coordinator "整合所有分析和處理結果，生成文檔健康報告、維護建議、優化路線圖"
```

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 完整文檔管理流程（推薦）
/docs-manager

# 2. 處理指定目錄
/docs-manager specs/
/docs-manager docs/
/docs-manager ./project-root

# 3. 預覽模式（不實際修改）
/docs-manager --dry-run
/docs-manager specs/ --dry-run

# 4. 專項模式
/docs-manager --distill-only      # 只執行蒸餾，不生成索引
/docs-manager --index-only        # 只生成索引，不蒸餾
/docs-manager --analysis-only     # 只分析，不執行任何修改
/docs-manager --rebuild-index     # 強制重建所有索引

# 5. 特定處理模式
/docs-manager --resolve-conflicts    # 重點處理矛盾內容
/docs-manager --merge-duplicates     # 重點處理重複內容
/docs-manager --update-lessons       # 重點更新 lessons
```

### 參數說明

- **無參數**: 處理當前目錄下的 specs/ 和 docs/
- **路徑參數**: 處理指定路徑下的文檔
- **--dry-run**: 預覽模式，顯示計畫但不執行
- **--distill-only**: 只執行蒸餾流程，不更新索引
- **--index-only**: 只更新 INDEX.md，不進行蒸餾
- **--analysis-only**: 只分析現況，生成報告
- **--rebuild-index**: 強制重建所有 INDEX.md
- **--resolve-conflicts**: 優先處理矛盾內容
- **--merge-duplicates**: 優先處理重複內容
- **--update-lessons**: 優先執行 lessons 更新

### 輸出範例

```bash
# 完整流程範例
🚀 啟動文檔管理流程...

📊 階段 1: 文檔現況分析
📋 Task structure-analyzer - 文檔掃描: 發現 18 個文檔，3 個目錄
🔍 Task content-analyzer - 品質評估: 檢測到 4 個重複區塊，2 個矛盾
🎯 Task context-analyzer - 決策分析: 識別 8 個關鍵架構決策

⚗️ 階段 2: 蒸餾與清理
🔧 Task content-processor - Spec 蒸馏: 處理 specs/modules/ (5 個檔案)
   ✓蒸餾完成: -32% 體積，解決 2 個矛盾
🎓 Task content-processor - Claude.md 蒸馏: 處理 3 個 CLAUDE.md
   ✓蒸餾完成: -28% 體積，提煉核心原則
📚 Task content-processor - Lessons 提取: 分析 1000+ 則對話
   ✓新決策: 2 個重要架構選擇
   ✓新規格: 5 項技術要求

📋 階段 3: 索引生成與整理
🗂️ Task content-processor - INDEX 生成: 建立 ai-docs/INDEX.md
   ✓索引條目: 18 個文檔，4 個分類
🔗 Task structure-analyzer - 結構優化: 改善導航和連結
   ✓優化完成: 統一模板，改善連結

✅ 文檔管理完成！
📊 處理統計:
   • 蒸餾文檔: 8 個
   • 解決矛盾: 4 個
   • 合併重複: 6 個
   • 索引條目: 18 個
   • 體積減少: -30%

💾 備份已建立，可在需要時還原。
```

---

## 📋 生成 INDEX.md 結構

### 標準 INDEX.md 模板

```markdown
# [目錄名稱] - 文檔索引

## 📊 概況
- **文檔總數**: [數量] 個
- **最後更新**: [更新時間]
- **主要類型**: 技術規格、設計文檔、API 文檔

## 🔧 技術規格文檔

### 架構與設計
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]

### API 與介面
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]

### 部署與運維
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]

## 📚 BMAD 開發流程文檔

### 開發規範
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]

### 設計決策
- **[檔案名稱]**: [簡短描述，3-10 字] - [檔案大小]

## 🔄 文檔維護

### 自動維護
- 本索引由 `/docs-manager` 自動生成
- 最後更新: [更新時間]

### 手動維護指南
- 新增文檔時，確保遵循命名規範
- 重大更新後，執行 `/docs-manager --rebuild-index`
```

---

## 📝 INDEX.md 生成規則

### 檔案分類邏輯

```python
def classify_document(filename: str, content: str) -> str:
    """文檔分類邏輯"""

    # 技術規格類型
    spec_keywords = ["spec", "api", "interface", "endpoint", "schema"]
    if any(kw in filename.lower() for kw in spec_keywords):
        return "tech_spec"

    # 架構設計類型
    arch_keywords = ["architecture", "design", "pattern", "system"]
    if any(kw in filename.lower() or kw in content.lower() for kw in arch_keywords):
        return "architecture"

    # 部署運維類型
    deploy_keywords = ["deployment", "config", "env", "infrastructure"]
    if any(kw in filename.lower() or kw in content.lower() for kw in deploy_keywords):
        return "deployment"

    # BMAD 流程類型
    bmad_keywords = ["bmad", "workflow", "process", "guideline"]
    if any(kw in filename.lower() or kw in content.lower() for kw in bmad_keywords):
        return "bmad_process"

    return "general"

def generate_description(filename: str, content: str) -> str:
    """生成 3-10 字的檔案描述"""

    # 讀取前幾行和標題
    lines = content.split('\n')[:10]
    headings = [line.strip('# ').strip() for line in lines if line.startswith('#')]

    if headings:
        # 使用第一個標題作為基礎
        base_desc = headings[0]
    else:
        # 從檔案名推斷
        base_desc = filename.replace('-', ' ').replace('_', ' ').replace('.md', '')

    # 提取關鍵詞
    keywords = []
    if 'API' in content or 'api' in content.lower():
        keywords.append('API文檔')
    if '設計' in content or 'design' in content.lower():
        keywords.append('設計規格')
    if '架構' in content or 'architecture' in content.lower():
        keywords.append('架構文檔')

    # 組合描述
    if keywords:
        return f"{base_desc} - {keywords[0]}"
    else:
        return base_desc[:10]  # 限制長度
```

---

## 🎯 執行順序與邏輯

### 推薦執行順序

```bash
# 開發到一段落時執行
/docs-manager

# 完整的執行順序邏輯：
# 1. distill-spec.md 清理 Specs
# 2. distill-claude.md 清理 CLAUDE.md
# 3. lessons.md 提取新知識
# 4. 整理 INDEX.md 現況
# 5. 每個文檔在 INDEX.md 中的簡要說明
```

### 智能決策邏輯

```python
def determine_processing_priority(doc_stats: dict) -> list:
    """決定處理優先順序"""

    priorities = []

    # 1. 高重複度和矛盾內容優先處理
    high_conflict_docs = [
        doc for doc, stats in doc_stats.items()
        if stats['conflict_score'] > 0.7
    ]
    priorities.extend(high_conflict_docs)

    # 2. 過時文檔優先蒸餾
    outdated_docs = [
        doc for doc, stats in doc_stats.items()
        if stats['days_since_update'] > 30
    ]
    priorities.extend(outdated_docs)

    # 3. 大型文檔優先蒸餾
    large_docs = [
        doc for doc, stats in doc_stats.items()
        if stats['line_count'] > 500
    ]
    priorities.extend(large_docs)

    # 4. 核心規格文檔
    core_specs = [
        doc for doc in doc_stats.keys()
        if 'spec' in doc or 'api' in doc
    ]
    priorities.extend(core_specs)

    return list(set(priorities))  # 去重
```

---

## 🔍 風險控制與恢復

### 備份機制
- **自動備份**: 所有修改前建立 .backup 檔案
- **版本記錄**: 記錄每次執行的操作摘要
- **回滾支援**: 提供一鍵還原功能

### 安全措施
- **預覽模式**: --dry-run 可預覽所有操作
- **確認機制**: 重大修改前需要使用者確認
- **品質檢查**: 操作後自動驗證文檔一致性

---

## 💡 使用建議

### 定期維護時機
1. **功能開發完成後**: 執行完整流程
2. **版本發布前**: 重點執行蒸餾和索引
3. **季度整理**: 執行完整文檔管理
4. **團隊交接**: 生成完整文檔現況報告

### 最佳實踐
1. **循序漸進**: 從分析開始，再執行修改
2. **定期執行**: 避免文檔積累過多問題
3. **團隊協作**: 執行前與團隊達成共識
4. **版本控制**: 重要操作前提交現狀

---

> 💡 **文檔管理哲學**: 讓文檔成為真正的知識資產，而不是技術負債。透過系統化的管理流程，確保文檔始終保持高品質、一致性和可用性，支持團隊的高效協作。

> 🤖 **AI 協作價值**: 整理後的文檔對 AI 協作開發極具價值。清晰的索引、蒸餾的精華、一致的結構，讓 AI 能快速理解專案狀況，提供更準確的技術建議和實作指導。