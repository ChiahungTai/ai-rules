---
description: 創建通用 CLAUDE.md 階層文檔生成器
usage: /doc-hierarchy [directory_path] [options]
---

# CLAUDE.md 階層文檔生成器

## ⚠️ 重要警告：執行陷阱

### ❌ 危險的誤解（最容易犯的錯誤）
- **Task 回報「完成」= 檔案已存在** ❌
- **記憶體中的分析結果 = 檔案系統內容** ❌
- **並行執行完成 = 所有檔案已創建** ❌

### ✅ 正確的理解
- **Task 工具只負責分析，在記憶體中工作** ✅
- **必須使用 Write 工具才能創建檔案** ✅
- **必須手動驗證檔案真的存在** ✅

### 🎯 關鍵執行原則
1. **責任分離**: Task 分析 + Write 寫入 + Bash 驗證
2. **三階段執行**: 分析 → 寫入 → 驗證
3. **強制確認**: 每個階段都要驗證結果

## 🚀 功能描述

基於 Claude Code 記憶體系統（https://code.claude.com/docs/en/memory）的自動載入特性，自動分析程式碼目錄並生成完整的 CLAUDE.md 階層文檔體系，讓 AI 快速理解程式碼架構並精確定位相關程式碼。

### 🧠 記憶體系統核心原理

根據 [Claude Code Memory System 文檔](https://code.claude.com/docs/en/memory)，該系統具有以下核心特性：

#### 自動載入機制
- ✅ **啟動時自動讀取**：所有 `CLAUDE.md` 檔案在 Claude Code 啟動時自動載入到上下文中
- ✅ **遞歸查找**：從當前工作目錄開始，向上遞歸查找記憶體檔案
- ✅ **階層優先**：子目錄的記憶體檔案優先於父目錄，支援細粒度的上下文控制

#### 匯入系統
- ✅ **模組化引用**：使用 `@path/to/import` 語法匯入其他記憶體檔案
- ✅ **相對路徑**：支援相對路徑引用，便於建立模組化的知識體系
- ✅ **避免重複**：透過匯入機制避免知識重複，維護單一真實來源

#### 上下文管理
- ✅ **智能合併**：系統會智能合併多個記憶體檔案的內容
- ✅ **衝突解決**：當有多個相同路徑的記憶體檔案時，子目錄優先
- ✅ **動態更新**：記憶體檔案修改後會在下一次對話中生效

### 🎯 本工具設計理念

本工具充分利用上述記憶體系統特性，實現：

1. **自動化知識提取**：掃描程式碼庫，自動生成結構化的 CLAUDE.md 檔案
2. **階層式組織**：建立根目錄總覽 + 子目錄詳情的知識階層
3. **精確定位**：提供檔案和行數的精確引用，便於 AI 快速定位相關程式碼
4. **模組化匯入**：使用 `@path` 語法建立模組間的知識關聯

## 📋 語法與參數

```bash
/doc-hierarchy [directory_path]
```

### 參數定義

- **directory_path**: 目標目錄（預設：當前目錄 `.`）

## 🎯 核心功能

### 1. 目錄結構分析
- 遞歸掃描目錄樹
- 識別架構模式（MVC、分層、微服務等）
- 評估模組重要性

### 2. 程式碼內容深度分析
- AST 解析提取類別/函數定義
- 計算複雜度和行數
- 識別設計模式
- 提取配置參數和關鍵常數

### 3. CLAUDE.md 自動生成
- 根目錄：整體架構總覽 + 模組匯入
- 子目錄：詳細實作指南 + 檔案分析
- 精確行數引用（如：connection.py:44-60）
- 使用 @path 語法建立匯入關係

### 4. 智能重要性評估
- 🔴 高複雜度：>500行 或 核心功能
- 🟡 中複雜度：200-500行 或 重要功能
- 🟢 低複雜度：<200行 或 輔助功能

## 🏗️ 輸出模板

### 根目錄 CLAUDE.md 模板

```markdown
# [ProjectName] 總體架構指南

## 專案概覽
[專案核心功能和設計理念描述]

## 架構模式
[識別出的架構模式]

## 核心模組匯入
@[module1]/CLAUDE.md
@[module2]/CLAUDE.md

## 快速定位指南

### 按功能查找
- [功能1]: [檔案]:[行數]
- [功能2]: [檔案]:[行數]

### 按重要性查找
- 🔴 高優先級: [關鍵檔案列表]
- 🟡 中優先級: [重要檔案列表]
- 🟢 低優先級: [輔助檔案列表]
```

### 子目錄 CLAUDE.md 模板 (AI 友善格式)

```markdown
# [ModuleName] 模組指南

## 核心功能
[模組主要職責和用途]

## 關鍵函數與類別

### [檔案名] - 重要函數
#### src/core/models.py:45-67 - User class
用戶資料模型，包含基本資料和認證方法。支援密碼hash儲存。
屬性: username, email, password_hash, created_at。
方法: authenticate(), update_profile(), is_active()。
依賴: datetime, bcrypt 模組。

#### src/core/models.py:89-123 - authenticate_user()
用戶認證函數，驗證密碼並返回用戶物件。
參數: username(str), password(str)。返回: User物件或None。
關鍵邏輯: bcrypt密碼比對 → 帳號狀態檢查 → 最後登入更新。
相關: User.authenticate(), refresh_token()。

### [檔案名] - 工具函數
#### src/utils/helpers.py:23-45 - format_currency()
金額格式化工具，支援多國幣別顯示。
參數: amount(Decimal), currency(str)。返回: 格式化字串。
特殊邏輯: 處理負數顯示，千分位分隔，幣別符號。

## 模組關係
- 依賴: utils/helpers.py, database/connection.py
- 被依賴: api/endpoints.py, services/payment.py
- 子模組: @[子目錄]/CLAUDE.md

## 測試覆蓋
- 整體覆蓋率: 87%
- 關鍵測試: test_models.py, test_authentication.py
```

## 🚀 並行處理架構 (基於 parallel-task.md 原則)

### 🎯 工具責任分工（關鍵區別）

```bash
# 📋 工具職責明確分工
Task 工具:    分析、提取、組織（記憶體中）     ← 不創建檔案！
Write 工具:   寫入、保存、創建（檔案系統）   ← 唯一創建檔案的方式！
Bash 工具:    驗證、確認、檢查（確保存在）   ← 確認檔案真的存在
```

### 🔄 真實執行流程（基於實測驗證）

#### Wave 1: 準備階段 (序列執行)
```bash
Task 0: 參數解析與目錄掃描
- 解析命令列參數與驗證
- 遞歸掃描目標目錄結構
- 智能檔案分組 (按類型/大小/位置)
- 輸出: 檔案清單 + 分組策略
```

#### Wave 2: 並行分析階段（記憶體中，不創建檔案）
```bash
# ⚠️ 重要：此階段不創建任何檔案！
# 按檔案切分原則，同時發起多個 Task 工具調用
Task 1 (content-analyzer): 分析 src/core/ 模組，回傳結構化結果
Task 2 (structure-analyzer): 分析 src/api/ 模組，回傳結構化結果
Task 3 (content-processor): 分析 src/services/ 模組，回傳結構化結果
Task 4 (verification-expert): 分析 tests/ 目錄，回傳結構化結果
Task 5 (context-analyzer): 分析 config/, utils/ 模組，回傳結構化結果

# 注意：所有 Task 都在記憶體中工作，不會創建任何檔案！
```

#### Wave 3: 檔案寫入階段（關鍵步驟，必須手動執行）
```bash
# 🔥 關鍵：必須使用 Write 工具創建檔案
# 根據 Wave 2 的分析結果，手動使用 Write 工具生成檔案
Write: /path/to/project/CLAUDE.md (根目錄總覽)
Write: /path/to/project/src/CLAUDE.md (src 模組指南)
Write: /path/to/project/src/core/CLAUDE.md (core 實作指南)
Write: /path/to/project/src/api/CLAUDE.md (api 實作指南)
Write: /path/to/project/tests/CLAUDE.md (測試指南)
```

#### Wave 4: 驗證確認階段（確保檔案真的存在）
```bash
# 🔍 關鍵：必須確認檔案真的存在
# 確保檔案真的存在的重要步驟
find /target/path -name "CLAUDE.md" -type f | wc -l

# 檢查生成的檔案數量和大小
ls -la /target/path/*/CLAUDE.md

# 驗證檔案內容正確性
head -20 /target/path/CLAUDE.md
```

### 🎯 並行分組策略

#### 智能檔案分組演算法
```python
def intelligent_file_grouping(files: List[str], max_groups: int = 10) -> List[FileGroup]:
    """
    基於 parallel-task.md 的按檔案切分原則
    """

    # 1. 按類型和位置預分組
    type_groups = {
        'core': [],      # 核心業務邏輯
        'api': [],       # API/路由檔案
        'config': [],    # 配置/設定檔案
        'utils': [],     # 工具/輔助函數
        'tests': [],     # 測試檔案
        'docs': []       # 文檔/範例檔案
    }

    # 2. 檔案分類
    for file_path in files:
        group_type = classify_file_type(file_path)
        type_groups[group_type].append(file_path)

    # 3. 動態負載平衡 - 確保每組工作量相近
    balanced_groups = balance_workload(type_groups, max_groups)

    return balanced_groups
```

#### 分組範例 (中型專案)
```markdown
🔍 **檔案分析結果**
檢測到 45 個目標檔案，智能分組為 6 組並行處理：

- 組1: [src/core/*.py] - 核心業務邏輯 (8檔案, ~2000行)
- 組2: [src/api/**/*.py] - REST API 層 (7檔案, ~1800行)
- 組3: [src/services/*.py] - 服務層邏輯 (6檔案, ~1500行)
- 組4: [config/, utils/] - 配置工具 (5檔案, ~800行)
- 組5: [tests/**/*.py] - 測試套件 (10檔案, ~2200行)
- 組6: [docs/, examples/] - 文檔範例 (9檔案, ~1200行)

🚀 **啟動並行執行**
```

## 🔧 並行實作步驟

### 步驟 1: 參數解析與驗證 (序列)
1. 解析命令列參數
2. 驗證目錄存在性
3. 設定預設值與選項衝突處理
4. **並行度評估**: 根據檔案數量決定 Task 數量

### 步驟 2: 智能目錄掃描與分組 (序列)
1. 遞歸掃描指定目錄
2. 過濾排除的目錄和檔案類型
3. **智能分組**: 按類型、大小、位置平衡分配
4. 建立檔案樹結構和依賴關係預分析

### 步驟 3: 並行程式碼內容分析 (完全並行)
```bash
# 同時發起多個獨立 Task 工具調用
Task 1 (content-analyzer):
完整分析 [核心業務檔案群組]，包含 AST 解析、複雜度計算、設計模式識別

Task 2 (structure-analyzer):
完整分析 [API 層檔案群組]，專注架構層次和端點組織

Task 3 (content-processor):
完整分析 [服務層檔案群組]，處理業務邏輯和數據流

Task 4 (verification-expert):
完整分析 [測試檔案群組]，評估測試覆蓋率和測試品質

Task 5 (context-analyzer):
完整分析 [配置工具檔案群組]，分析配置邏輯和工具函數

Task 6 (context-analyzer):
完整分析 [文檔範例檔案群組]，評估文檔完整性和範例有效性

# 所有 Task 無依賴關係，可真正並行執行
```

### 步驟 4: 並行重要性評估 (組內並行)
1. **各組內部評估**: 每個 Task 獨立計算所屬檔案的重要性分數
2. **並行評估指标**:
   - 行數權重 (30%) + 類別/函數數量 (25%) + 複雜度 (25%) + 架構重要性 (20%)
   - 識別各組內的高優先級模組
3. **組間依賴分析**: 等待所有組完成後進行跨組依賴評估

### 步驟 5: 整合文檔生成 (序列)
1. 收集所有並行分析結果
2. **跨模整合**: 建立完整的依賴關係圖
3. 生成根目錄 CLAUDE.md (整體架構總覽)
4. 生成子目錄 CLAUDE.md (詳細實作指南)
5. 建立 @path 匯入關係鏈
6. 執行安全性檢查和最終驗證

## 🔍 演算法設計

### 重要性評估演算法

```python
def calculate_importance(file_path):
    score = 0

    # 行數權重 (30%)
    line_count = count_lines(file_path)
    score += (line_count / 1000) * 0.3

    # 類別/函數數量 (25%)
    entities = count_entities(file_path)
    score += (entities / 50) * 0.25

    # 複雜度評分 (25%)
    complexity = calculate_complexity(file_path)
    score += (complexity / 100) * 0.25

    # 架構重要性 (20%)
    arch_importance = assess_arch_importance(file_path)
    score += arch_importance * 0.2

    return min(score, 1.0)
```

### 架構模式識別

```python
def detect_architecture_pattern(directory_structure):
    patterns = {
        'MVC': ['controllers', 'views', 'models'],
        'Layered': ['controllers', 'services', 'repositories'],
        'Microservices': ['services', 'api', 'gateway'],
        'Component': ['components', 'utils', 'hooks'],
        'Modular': ['modules', 'core', 'shared']
    }

    detected = []
    for pattern, keywords in patterns.items():
        if all(keyword in directory_structure for keyword in keywords):
            detected.append(pattern)

    return detected
```

## 🔒 安全性檢查

### 敏感檔案過濾
- 過濾敏感檔案（.env, .key, passwords）
- 檢測敏感資訊模式
- 保護智慧財產權

### 錯誤處理
- 無效檔案跳過
- 權限不足處理
- 編碼問題處理

## 📊 使用範例

```bash
# 分析當前目錄
/doc-hierarchy .

# 分析特定目錄
/doc-hierarchy ./src
```

## ⚡ 並行效能優化

### 🚀 核心並行優化策略
1. **智能並行處理**: 基於檔案數量動態調整並行度 (3-10 Tasks)
2. **負載平衡分組**: 確保每個 Task 工作量相近，避免資源浪費
3. **無衝突並行**: 所有分析任務皆為純讀取操作，安全並行
4. **快取機制**: 避免重複分析相同檔案結構
5. **增量更新**: 支援只處理變更檔案，大型專案快速更新


### 🔧 深度限制與記憶體管理
1. **智能深度控制**: 根據專案複雜度動態調整分析深度
2. **記憶體最佳化**: 大型專案分批並行處理，避免記憶體溢出
3. **資源監控**: 實時監控 CPU 和記憶體使用率，動態調整並行度

### 🛡️ 錯誤處理策略
- **檔案衝突檢測**: 自動檢測並避免檔案操作衝突
- **錯誤隔離**: 單一 Task 失敗不影響其他並行任務
- **繼續處理**: 大部分錯誤跳過失敗檔案，繼續分析其他檔案
- **最終報告**: 所有錯誤和跳過的檔案在最後統一報告

## 🎯 並行執行範例

### 範例 1: 一般專案並行分析
**用戶輸入**: `/doc-hierarchy ./my-web-app`

**並行執行過程**:
```markdown
🔍 **Wave 1**: 目錄掃描與檔案分組
檔案數量: 42 個 | 並行度: 6 個 Tasks

🚀 **Wave 2**: 6 個並行 Task 同時執行

Task 1 (content-analyzer): 分析 src/core/ 模組
Task 2 (structure-analyzer): 分析 src/api/ 模組
Task 3 (content-processor): 分析 src/services/ 模組
Task 4 (verification-expert): 分析 tests/ 目錄
Task 5 (context-analyzer): 分析 config/, utils/ 模組
Task 6 (context-analyzer): 分析 docs/, examples/ 目錄

📊 **執行完成**
✅ 成功分析: 40/42 檔案
❌ 跳過檔案: 2 個 (語法錯誤)
✅ 根目錄 CLAUDE.md 生成完成
✅ 子目錄 CLAUDE.md 生成完成
```

### 預期並行輸出結構
```
project/
├── CLAUDE.md                 # 根目錄總覽 (並行整合結果)
├── src/
│   ├── CLAUDE.md             # src 模組指南 (並行分析結果)
│   ├── controllers/
│   │   └── CLAUDE.md         # controllers 實作指南
│   ├── services/
│   │   └── CLAUDE.md         # services 實作指南
│   └── models/
│       └── CLAUDE.md         # models 實作指南
├── tests/
│   └── CLAUDE.md             # 測試指南 (並行驗證結果)
└── docs/
    └── CLAUDE.md             # 文檔指南 (並行分析結果)

並行執行日誌: .doc-hierarchy-parallel.log
```

## 🔧 執行檢查清單（確保成功）

### ✅ 執行前檢查
```markdown
- [ ] 了解 Task 只在記憶體中工作，不會創建檔案
- [ ] 準備好使用 Write 工具來創建檔案
- [ ] 明確目標檔案路徑和命名規則
- [ ] 確認有足夠的磁碟空間和權限
```

### ✅ 執行中檢查
```markdown
- [ ] Wave 1 完成：目錄掃描和檔案分組正確
- [ ] Wave 2 完成：所有 Task 回報分析結果
- [ ] Wave 3 完成：使用 Write 工具逐個寫入檔案
- [ ] 每個檔案寫入後確認成功（無錯誤訊息）
```

### ✅ 執行後檢查（關鍵驗證）
```markdown
- [ ] 使用 find 確認檔案存在：
  ```bash
  find /target/path -name "CLAUDE.md" -type f | wc -l
  ```
- [ ] 使用 ls 檢查檔案大小合理：
  ```bash
  ls -la /target/path/*/CLAUDE.md
  ```
- [ ] 使用 head 確認內容格式正確：
  ```bash
  head -20 /target/path/CLAUDE.md
  ```
- [ ] 檢查檔案數量：1(根目錄) + N(子目錄) = N+1
```

### 🚨 常見錯誤與解決方案

#### 錯誤 1: Task 完成但找不到檔案
**原因**: 忘記使用 Write 工具
**解決**: 回到 Wave 3，使用 Write 工具創建檔案

#### 錯誤 2: 檔案存在但內容空白
**原因**: Write 工具內容參數錯誤
**解決**: 檢查 Write 工具的內容參數，確保包含 Task 分析結果

#### 錯誤 3: 檔案數量不正確
**原因**: 漏掉某些子目錄的 CLAUDE.md
**解決**: 檢查每個子目錄，確保都有對應的 CLAUDE.md

### Task 分配策略
```bash
# 按檔案類型和模組智能分配
content-analyzer: 處理程式碼檔案 (.py, .js, .ts)
structure-analyzer: 處理架構相關檔案
context-analyzer: 處理文檔和配置檔案
verification-expert: 處理測試檔案
content-processor: 處理範例和工具檔案

# 同時發起多個 Task，無依賴關係
```

### 錯誤處理方式
```markdown
📊 最終執行報告
✅ 成功分析: 40/42 檔案
❌ 跳過檔案:
   - config/settings.yaml (語法錯誤)
   - src/broken.py (檔案損壞)

💡 建議修復錯誤檔案後重新執行以獲得完整文檔
```

### 關鍵原則
- **正確性優先**: 確保架構分析準確
- **錯誤隔離**: 單一檔案錯誤不影響其他分析
- **品質一致**: 無論並行或序列，輸出品質相同
- **驗證強制**: 每個階段都要驗證結果

---

*💡 這個工具專注於正確的架構分析，讓 AI 能快速理解任何程式碼庫的結構和定位。*