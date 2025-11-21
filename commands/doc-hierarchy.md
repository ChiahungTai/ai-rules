---
description: 創建通用 CLAUDE.md 階層文檔生成器
usage: /doc-hierarchy [directory_path] [options]
---

# CLAUDE.md 階層文檔生成器

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
/doc-hierarchy [directory_path] [options]
```

### 參數定義

- **directory_path**: 目標目錄（預設：當前目錄 `.`）
- **--depth N**: 分析深度（預設：3）
- **--include "ext1,ext2"**: 包含檔案類型（預設：py,js,ts,rs,go,java,cpp）
- **--exclude "dir1,dir2"**: 排除目錄（預設：pycache,node_modules,.git）
- **--force**: 強制覆蓋現有 CLAUDE.md
- **--dry-run**: 預覽模式
- **--verbose**: 詳細輸出

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

### 子目錄 CLAUDE.md 模板

```markdown
# [ModuleName] 實作指南

## 核心職責
[模組主要職責描述]

## 關鍵檔案分析

### [檔案名] [★重要性]
- **行數**: ~[行數] 行
- **關鍵類別/函數**: [重要項目]
- **核心功能**: [主要功能描述]
- **重要行數**: [行數範圍] ([功能說明])
- **依賴**: [相關模組]

## 子模組匯入
@[子目錄]/CLAUDE.md
```

## 🔧 實作步驟

### 步驟 1: 參數解析與驗證
1. 解析命令列參數
2. 驗證目錄存在性
3. 設定預設值
4. 處理選項衝突

### 步驟 2: 目錄結構掃描
1. 遞歸掃描指定目錄
2. 過濾排除的目錄
3. 收集符合副檔名的檔案
4. 建立檔案樹結構

### 步驟 3: 程式碼內容分析
1. 根據副檔名選擇解析器
2. 提取類別、函數、變數定義
3. 計算複雜度指標
4. 識別設計模式

### 步驟 4: 重要性評估
1. 計算檔案重要性分數
2. 排序檔案優先級
3. 識別核心模組
4. 建立依賴關係圖

### 步驟 5: 文檔生成
1. 生成根目錄 CLAUDE.md
2. 生成子目錄 CLAUDE.md
3. 建立匯入關係
4. 安全性檢查

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
# 基本使用 - 分析當前目錄
/doc-hierarchy .

# 分析特定目錄，深度 4 層
/doc-hierarchy ./src --depth 4

# 預覽模式，不實際建立檔案
/doc-hierarchy . --dry-run --verbose

# 自訂檔案類型，排除測試目錄
/doc-hierarchy . --include "py,js,ts" --exclude "tests,node_modules"

# 強制覆蓋現有文檔
/doc-hierarchy . --force

# 詳細輸出模式
/doc-hierarchy ./my-project --verbose --depth 5
```

## ⚡ 效能優化

1. **並行處理**: 多檔案並行分析
2. **快取機制**: 避免重複分析
3. **增量更新**: 只處理變更檔案
4. **深度限制**: 防止過深遞歸
5. **記憶體管理**: 大型專案分批處理

## 🎯 輸出範例

執行後將在目標目錄和子目錄中生成對應的 CLAUDE.md 檔案，建立完整的文檔階層體系。

### 預期目錄結構
```
project/
├── CLAUDE.md                 # 根目錄總覽
├── src/
│   ├── CLAUDE.md             # src 模組指南
│   ├── controllers/
│   │   └── CLAUDE.md         # controllers 實作指南
│   ├── services/
│   │   └── CLAUDE.md         # services 實作指南
│   └── models/
│       └── CLAUDE.md         # models 實作指南
├── tests/
│   └── CLAUDE.md             # 測試指南
└── docs/
    └── CLAUDE.md             # 文檔指南
```

---

*💡 這個工具將成為 AI 協作開發的基礎設施，讓任何複雜的程式碼庫都能快速建立起 AI 友善的理解介面，大幅提升 AI 與開發者的協作效率。*