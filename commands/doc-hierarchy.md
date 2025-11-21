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

## 🚀 智能並行處理架構 (基於 parallel-processing skill)

### 🎯 並行處理決策引擎

在開始並行處理前，使用 **parallel-processing skill** 進行智能決策：

```bash
# Step 0: 並行可行性評估
skill: "parallel-processing" "評估分析 [directory_path] 的並行處理可行性"
```

### 🔄 智能執行流程

#### Phase 1: 準備與決策階段
```bash
# 1. 參數解析與目錄驗證
- 解析目標目錄路徑
- 驗證目錄存在性和可訪問性
- 基本統計：檔案數量、目錄層級、檔案類型

# 2. 並行處理決策 (skill 決策)
skill: "parallel-processing" "檔案數量: [count], 預估處理時間: [estimate]"
```

**Skill 決策結果**：
- ✅ **建議並行**: 檔案 ≥ 10個 且預估時間 ≥ 45秒
- ⚠️ **詢問用戶**: 5-9個檔案 或中等複雜度
- ❌ **序列處理**: 檔案少或簡單操作

#### Phase 2: 智能並行執行 (僅在 skill 建議時)
```bash
# 3. 按技能建議的並行度執行
# Skill 自動計算最優並行度 (3-8個 Task)

# 範例：Skill 建議 4 個並行任務（真正的並行執行）
Task 1: "分析 [核心模組群組]，生成 CLAUDE.md 架構文檔" &
Task 2: "分析 [API 層群組]，生成 CLAUDE.md 介面文檔" &
Task 3: "分析 [工具配置群組]，生成 CLAUDE.md 配置文檔" &
Task 4: "分析 [測試文檔群組]，生成 CLAUDE.md 測試文檔" &
wait

# 所有 Task 真正並行執行，然後整合結果創建檔案
```

#### Phase 3: 結果整合與檔案創建
```bash
# 4. 收集並行分析結果並創建 CLAUDE.md
Write: [project_root]/CLAUDE.md (總覽文檔)
Write: [subdirs]/CLAUDE.md (各模組文檔)

# 5. 驗證檔案創建成功
find [target_path] -name "CLAUDE.md" -type f
```

## 🔧 實作步驟

### 步驟 1: 初始分析與決策 (序列)
```bash
# 1. 基本目錄分析
- 解析目標目錄路徑
- 驗證目錄存在性
- 統計檔案數量和類型分布

# 2. 觸發並行處理決策
skill: "parallel-processing" "分析 [directory_path] - [file_count] 個檔案，包含 [type_distribution]"
```

### 步驟 2: Skill 決策響應
```bash
# Skill 可能的三種回應：
✅ **建議並行處理**: "檔案數量充足，預估可節省 [X]% 時間，建議使用 [N] 個並行任務"
⚠️ **詢問用戶意見**: "中等規模任務，並行處理可提升 [Y]% 效率，是否啟用？"
❌ **建議序列處理**: "規模較小，序列處理更高效"
```

### 步驟 3: 執行策略選擇
```bash
# A. 真正的並行處理模式 (Skill 建議且用戶同意)
根據 Skill 建議的並行度 [3-8] 個 Task，使用 & 符號：
Task 1: "核心業務模組分析，生成架構文檔" &
Task 2: "API/介面層分析，生成介面文檔" &
Task 3: "工具配置分析，生成配置文檔" &
Task N: "測試文檔分析，生成測試文檔" &
wait

# B. 序列處理模式 (Skill 建議或用戶選擇)
單一 Task 依序處理所有檔案
```

### 步驟 4: 結果整合與文檔生成
```bash
# 1. 收集所有 Task 分析結果
# 2. 生成階層式 CLAUDE.md 文檔
Write: [root]/CLAUDE.md (專案總覽)
Write: [subdirs]/CLAUDE.md (模組詳情)

# 3. 建立模組間匯入關係
# 4. 驗證所有檔案正確生成
```

### 步驟 5: 最終驗證
```bash
# 必須確認檔案真的存在！
find [target_path] -name "CLAUDE.md" -type f | wc -l
```

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

## ⚡ 智能效能優化 (由 Skill 主導)

### 🧠 Skill-Driven 優化策略
parallel-processing skill 自動處理以下優化：

#### 1. **智能並行度計算**
```bash
# Skill 根據以下因素自動計算最優並行度：
- 檔案總數和類型分布
- 預估處理複雜度
- 系統資源可用性
- 預期加速比
```

#### 2. **動態負載平衡**
```bash
# Skill 自動分組策略：
- 按檔案類型和位置智能分組
- 確保每組工作量相近
- 避免資源閒置
```

#### 3. **成本效益分析**
```bash
# Skill 自動評估：
- 並行啟動成本 vs 預期效益
- 最小效益閾值：≥ 2.0x 加速比
- 淨效益：節省時間 > 啟動成本 × 1.5
```

### 🛡️ 統一錯誤處理
```bash
# Skill 提供的標準化錯誤處理：
- 錯誤隔離：單一 Task 失敗不影響其他
- 智能重試：自動重試失敗的 Task
- 部分成功：繼續處理其他檔案
- 統一報告：所有錯誤在最終統一彙總
```

## 🎯 智能執行範例

### 範例 1: 大型專案並行處理
**用戶輸入**: `/doc-hierarchy ./large-web-app`

**執行過程**:
```markdown
🔍 **Phase 1**: 初始分析
目錄: ./large-web-app
檔案數量: 48 個 | 類型: Python(32) + Config(8) + Docs(8)

🧠 **Phase 2**: Skill 決策
skill: "parallel-processing" "48個檔案，包含32個Python檔案，預估需要深度分析"

✅ **Skill 建議**: "檔案數量充足，預估可節省 65% 時間，建議使用 5 個並行任務"

🚀 **Phase 3**: 並行執行
Task 1: 分析 src/core/, src/models/ (核心模組)
Task 2: 分析 src/api/, src/routes/ (API層)
Task 3: 分析 src/services/, src/utils/ (服務層)
Task 4: 分析 tests/, config/ (測試配置)
Task 5: 分析 docs/, examples/ (文檔範例)

📊 **Phase 4**: 結果整合
✅ 成功分析: 46/48 檔案 (2個語法錯誤跳過)
✅ 並行效率: 3.2x 加速比
✅ CLAUDE.md 生成完成: 6 個檔案
```

### 範例 2: 中型專案詢問決策
**用戶輸入**: `/doc-hierarchy ./medium-project`

**執行過程**:
```markdown
🔍 **Phase 1**: 初始分析
目錄: ./medium-project
檔案數量: 12 個 | 類型: Python(8) + Config(4)

🧠 **Phase 2**: Skill 決策
skill: "parallel-processing" "12個檔案，中等規模任務"

⚠️ **Skill 詢問**: "中等規模任務，並行處理可提升 40% 效率，是否啟用並行處理？"

👤 **用戶選擇**: "是，啟用並行處理"

🚀 **Phase 3**: 並行執行 (3 個 Task)
Task 1: 分析核心業務檔案
Task 2: 分析配置和工具檔案
Task 3: 分析測試檔案

📊 **Phase 4**: 結果整合
✅ 成功分析: 12/12 檔案
✅ 並行效率: 1.7x 加速比
```

### 範例 3: 小型專案序列處理
**用戶輸入**: `/doc-hierarchy ./small-lib`

**執行過程**:
```markdown
🔍 **Phase 1**: 初始分析
目錄: ./small-lib
檔案數量: 4 個 | 類型: Python(3) + Config(1)

🧠 **Phase 2**: Skill 決策
skill: "parallel-processing" "4個檔案，小規模任務"

❌ **Skill 建議**: "規模較小，序列處理更高效"

🔧 **Phase 3**: 序列執行
單一 Task 依序處理所有檔案

📊 **Phase 4**: 結果整合
✅ 成功分析: 4/4 檔案
✅ 執行時間: 8 秒
```

### 輸出結構統一模式
```
project/
├── CLAUDE.md                 # 根目錄總覽
├── src/
│   └── CLAUDE.md             # 模組指南
├── tests/
│   └── CLAUDE.md             # 測試指南
└── docs/
    └── CLAUDE.md             # 文檔指南

# 執行方式記錄在每個 CLAUDE.md 頂部
# 生成方式: [並行處理 | 序列處理] + [加速比]
```

## 🔧 執行檢查清單（確保成功）

### ✅ 執行前檢查
```markdown
- [ ] 確認目標目錄存在且可訪問
- [ ] 了解 parallel-processing skill 決策機制
- [ ] 準備好響應 skill 的並行處理建議
- [ ] 確認有足夠的磁碟空間和寫入權限
```

### ✅ Skill 決策階段檢查
```markdown
- [ ] Phase 1 完成：目錄掃描和檔案統計正確
- [ ] Skill 決策獲取：收到並行處理建議
- [ ] 用戶回應：確認採納或拒絕並行處理建議
- [ ] 執行策略確定：並行或序列處理路線明確
```

### ✅ 執行中檢查
```markdown
# 並行處理模式：
- [ ] 所有 Task 並行啟動成功
- [ ] 各 Task 回報分析結果
- [ ] 結果整合無錯誤

# 序列處理模式：
- [ ] 單一 Task 完成所有檔案分析
- [ ] 分析結果結構化正確
```

### ✅ 執行後檢查（關鍵驗證）
```markdown
- [ ] 使用 Write 工具創建所有 CLAUDE.md 檔案
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

### 🚨 常見情況與處理方式

#### 情況 1: Skill 建議並行但用戶選擇序列
**處理方式**: 使用單一 Task 依序處理所有檔案
**優點**: 執行流程簡單，資源使用穩定
**缺點**: 處理時間較長

#### 情況 2: Skill 建議序列但用戶希望並行
**處理方式**: 可強制啟用並行，但效率可能不佳
**注意**: 小規模任務並行可能反而更慢

#### 情況 3: 並行執行中部分 Task 失敗
**處理方式**: Skill 自動錯誤隔離，繼續處理其他檔案
**結果**: 部分成功，最終報告會標註失敗檔案

#### 情況 4: 檔案寫入失敗
**原因**: 記憶體中的分析結果未正確傳遞給 Write 工具
**解決**: 檢查 Write 工具參數，確保包含完整的分析結果

### 📊 執行報告範本
```markdown
## doc-hierarchy 執行報告

### 基本資訊
- 目標目錄: [directory_path]
- 檔案總數: [count] 個
- Skill 決策: [並行處理 | 序列處理 | 詢問用戶]
- 執行策略: [用戶選擇的策略]

### 執行結果
- ✅ 成功分析: [成功數量]/[總數量] 檔案
- ❌ 跳過檔案: [失敗數量] 個 (列出原因)
- 🚀 效能提升: [加速比]x (並行處理時)
- ⏱️ 執行時間: [總時間] 秒

### 輸出檔案
- 根目錄 CLAUDE.md: ✅ 生成成功
- 子目錄 CLAUDE.md: [數量] 個 ✅ 生成成功
```

### 🎯 關鍵成功原則
- **Skill 主導**: 相信 parallel-processing skill 的智能決策
- **正確性優先**: 確保架構分析準確性比速度更重要
- **靈活應對**: 根據 skill 建議和實際情況選擇執行策略
- **強制驗證**: 每個階段都要確認檔案真的存在且內容正確

---

## 🎯 總結

doc-hierarchy 命令現在採用 **skill-first** 設計理念，將複雜的並行處理邏輯交由專門的 **parallel-processing skill** 處理：

### 核心優勢
- **智能決策**: 自動評估是否需要並行處理
- **成本效益**: 只有在效益顯著時才啟用並行
- **簡化邏輯**: 移除複雜的手動並行分組
- **統一標準**: 使用標準化的 skill 介面

### 執行流程
1. **初始分析** → **Skill 決策** → **用戶確認** → **執行** → **驗證**
2. 所有並行處理細節由 skill 自動處理
3. 保持原有的階層文檔生成功能

*💡 這個工具專注於正確的架構分析，讓 AI 能快速理解任何程式碼庫的結構和定位。並行處理由 parallel-processing skill 智能決策，確保最佳效能。*