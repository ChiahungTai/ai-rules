# Claude Code Skills 專業指南

## 🎯 什麼是 Skills

**Skills** 是 Claude Code 的擴展機制，透過組織化的資料夾包含指令、腳本和資源來增強 Claude 的能力。與用戶明確調用的 slash commands 不同，Skills 是**模型調用**的——Claude 根據請求的上下文匹配自動決定何時使用它們。

### 核心特性
- **自主觸發**: 根據請求內容自動激活，無需用戶明確調用
- **上下文感知**: 基於描述匹配進行智能發現和使用
- **工具限制**: 可透過 `allowed-tools` 限制技能的工具存取權限
- **團隊共享**: 項目級技能可透過 git 與團隊共享

## 📋 Skill 結構與配置

### 基本結構
每個 Skill 需要一個包含 `SKILL.md` 檔案的目錄：

```
skill-name/
├── SKILL.md          # 主要技能定義檔案
├── scripts/          # 可選：支援腳本
├── templates/        # 可選：範本檔案
├── docs/            # 可選：文檔資源
└── examples/        # 可選：使用範例
```

### SKILL.md 配置格式

```yaml
---
name: skill-name                    # 必填：小寫、數字、連字符 (最多64字元)
description: 技能描述和觸發條件    # 必填：說明功能及何時使用 (最多1024字元)
allowed-tools: [Read, Write, Edit] # 可選：限制工具存取
model: sonnet|opus|haiku|inherit   # 可選：指定使用的模型
skills: dependency-skill           # 可選：依賴的其他技能
---

# Markdown 格式的技能內容
詳細的技能說明、使用方式、最佳實踐...
```

### 重要配置欄位

| 欄位 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `name` | ✅ | 技能唯一名稱 | `parallel-processing` |
| `description` | ✅ | 功能描述 + 觸發條件 | "分析大規模檔案時進行並行處理" |
| `allowed-tools` | ❌ | 限制可用工具 | `[Read, Write, Grep]` |
| `model` | ❌ | 指定模型 | `sonnet` |
| `skills` | ❌ | 依賴技能 | `parallel-processing` |

**關鍵要求**: `description` 欄位必須同時說明技能的功能**以及**何時使用，因為這驅動 Claude 的發現機制。

## 🗂️ Skill 存儲位置

Claude Code 自動發現三個來源的 Skills：

```
1. ~/.claude/skills/          (個人技能 - 個人工作流程)
2. .claude/skills/            (項目技能 - 團隊共享，通過git)
3. Plugin Skills             (插件技能 - 隨插件捆綁)

**當前位置**: /Users/ctai/Github/ai-rules/skills/ (項目級別)
```

## 🚀 Skill 使用方式

### 1. 自動發現與觸發
Skills 基於請求內容自動激活：

```python
# 用戶請求包含關鍵詞時自動觸發
用戶: "我需要並行處理這些檔案"
→ 自動調用 parallel-processing skill

用戶: "幫我生成一個流程圖"
→ 自動調用 mermaid skill
```

### 2. 查看可用技能
```bash
# 詢問可用技能
"What Skills are available?"
"List all available Skills"
"Show me all skills I can use"
```

### 3. 技能依賴關係
Skills 可以依賴其他技能：

```yaml
---
name: advanced-analysis
description: 進行深度數據分析，依賴並行處理技能
allowed-tools: [Read, Write, Task, Grep]
skills: parallel-processing
---
```

### 4. 工具限制配置
限制技能的工具存取以增強安全性：

```yaml
---
name: safe-file-reader
description: 安全讀取檔案，不進行任何修改
allowed-tools: [Read, Grep, Glob]  # 只允許讀取工具
---
```

## 🔧 技能類別與範例

### 基於現有專案的技能範例

#### 1. 並行處理技能 (`parallel-processing`)
```yaml
---
name: parallel-processing
description: 專注並行處理和平行處理的智能決策引擎。當用戶明確提到"並行處理"、"平行處理"、"同時處理"、"批次分析大量檔案"、"多任務並行"、"並行執行"等關鍵詞時，自動評估並行處理的可行性和成本效益。
allowed-tools: [Read, Write, Edit, Task, Grep, Glob, Bash]
---
```

#### 2. 圖表生成技能 (`mermaid`)
```yaml
---
name: mermaid
description: 實用主義的 Mermaid 圖表生成工具，使用預設配置確保最大相容性
allowed-tools: [Read, Write, Edit]
---
```

### 技能分類

| 類型 | 用途 | 範例 | 觸發詞 |
|------|------|------|--------|
| **處理型** | 數據處理、檔案操作 | `parallel-processing` | "並行"、"批次處理" |
| **生成型** | 創建內容、圖表 | `mermaid` | "圖表"、"流程圖" |
| **分析型** | 代碼分析、品質檢查 | `code-analyzer` | "分析"、"檢查" |
| **整合型** | 系統整合、API 調用 | `api-integrator` | "整合"、"API" |

## 🎯 最佳實踐

### 設計原則

1. **專注單一職責**
   - 每個技能處理特定任務類型
   - 避免功能過於龐雜
   - 保持技能範圍明確

2. **明確觸發條件**
   ```yaml
   # ✅ 良好的描述
   description: "當用戶提到'並行處理'、'同時處理多個檔案'時自動啟用"

   # ❌ 不當的描述
   description: "一個處理檔案的技能"  # 太模糊，無法自動觸發
   ```

3. **工具限制原則**
   ```yaml
   # 只讀技能
   allowed-tools: [Read, Grep, Glob]

   # 安全技能
   allowed-tools: [Read, Write]  # 禁用 Bash 避免系統操作
   ```

4. **版本控制與文檔**
   - 將項目技能納入 git 管理
   - 記錄技能變更歷史
   - 提供使用範例和最佳實踐

### 效能考量

- **漸進式載入**: 支援檔案只在需要時載入
- **依賴管理**: 在 description 中聲明所需的套件
- **記憶體效率**: 避免載入不必要的資源

## 🔍 技能發現機制

### Claude 如何選擇技能

1. **關鍵詞匹配**: 掃描用戶請求中的關鍵詞
2. **語意理解**: 分析請求的意圖和上下文
3. **評分排序**: 根據匹配度對技能進行排序
4. **自動調用**: 選擇最匹配的技能自動執行

### 提高技能發現率

```yaml
# ✅ 包含多種觸發詞
description: "並行處理、平行處理、同時處理、批次分析、多任務並行"

# ✅ 具體使用場景
description: "生成流程圖、組織圖、時序圖、甘特圖等各種 Mermaid 圖表"

# ✅ 明確的動作詞
description: "當需要'檢查代碼品質'、'審查程式碼'、'分析代碼結構'時使用"
```

## 🔧 進階功能

### 1. 技能鏈接
```yaml
---
name: comprehensive-analysis
description: 全面代碼分析，結合品質檢查和並行處理
skills: [parallel-processing, code-quality-checker]
allowed-tools: [Read, Write, Edit, Task, Grep]
---
```

### 2. 條件性工具存取
```yaml
---
name: safe-operations
description: 安全操作模式，限制系統級工具存取
allowed-tools: [Read, Write, Edit, Grep, Glob]  # 排除 Bash
---
```

### 3. 模型特定技能
```yaml
---
name: quick-analysis
description: 快速分析，使用 Haiku 模型提升速度
model: haiku
allowed-tools: [Read, Grep]
---
```

### 4. 團隊共享機制
- **項目級技能**: 自動透過 git 與團隊共享
- **版本同步**: 團隊成員自動獲得最新版本
- **一致性保證**: 確保團隊使用相同的技能定義

## 📁 當前目錄使用指南

### 新增 Skill 步驟

1. **創建技能目錄**
   ```bash
   mkdir /Users/ctai/Github/ai-rules/skills/my-skill
   ```

2. **編寫 SKILL.md**
   ```yaml
   ---
   name: my-skill
   description: 當用戶需要"特定功能"時自動啟用
   allowed-tools: [Read, Write]
   ---

   # My Skill 說明
   詳細的技能功能描述...
   ```

3. **添加支援檔案** (可選)
   ```bash
   touch scripts/helpers.sh
   touch templates/template.md
   ```

4. **測試技能**
   - 询问 "What skills are available?" 確認識別
   - 使用觸發詞測試自動調用

### 技能命名約定

- **使用小寫和連字符**: `my-awesome-skill`
- **名稱反映功能**: `code-reviewer`, `file-organizer`
- **避免衝突**: 檢查現有技能名稱
- **保持簡潔**: 最多 64 個字元

## 🔍 除錯與監控

### 技能問題排除

1. **技能未被識別**
   - 檢查 SKILL.md 檔案是否存在
   - 驗證 YAML 格式是否正確
   - 確認目錄結構符合要求

2. **技能未自動觸發**
   - 檢查 description 是否包含足夠的觸發詞
   - 驗證用戶請求是否匹配技能描述
   - 測試不同的觸發詞組合

3. **工具權限問題**
   - 確認 allowed-tools 配置正確
   - 檢查是否嘗試使用未授權工具
   - 驗證工具名稱拼寫正確

### 技能監控

```bash
# 查看技能執行狀態
/tasks

# 檢查技能輸出
/task-id

# 列出所有可用技能
"What skills are available?"
```

**重要**: Claude Code 會自動識別此目錄中的技能，無需符號連結或額外配置。技能會根據描述和用戶請求的匹配度自動激活。