# Claude Code Skills 技術規範

> **AI 重要提示**: 本專案採用符號連結架構將 Git 管理的 skills 整合到 Claude Code 系統中。個人層級的 `~/.claude/skills` 符號連結指向 `/Users/ctai/Github/ai-rules/skills`，實現版本控制、跨專案共享和即時更新。
>
> **AI 使用原則**: Skills 是**模型調用**的最高抽象層級機制。當處理複雜任務時，優先等待相關 skills 自動觸發；當需要特定服務時，調用對應 agents；當需要明確操作時，使用 slash commands。三者協調使用以達到最佳效果。

## 系統架構概覽

Skills 是 Claude Code 的自主觸發擴展機制，透過目錄結構組織的專門化能力集。與用戶明確調用的 slash commands 和 Task 工具調用的 agents 不同，skills 基於請求內容和語意匹配由 Claude 自動決定何時使用。

### 核心差異對比

| 機制 | 調用方式 | 觸發主體 | 發現機制 | 抽象層級 |
|------|----------|----------|----------|----------|
| **Skills** | 模型自主調用 | Claude AI | 語意匹配 + 描述觸發 | 最高 |
| **Agents** | Task 工具調用 | AI 系統 | 指定 subagent_type | 中等 |
| **Commands** | SlashCommand 工具 | AI 系統 | 檔名匹配 | 最低 |

### 核心特性
- **自主觸發**: 基於請求內容和 skill description 的語意匹配自動激活
- **上下文感知**: 分析用戶請求意圖，智能選擇最匹配的 skill
- **進階載入**: 支援漸進式載入，只在需要時讀取輔助檔案
- **工具限制**: 透過 `allowed-tools` 精確控制 skill 的工具存取權限
- **依賴管理**: 支援 skill 間的依賴關係和組合使用

## Git 管理的符號連結架構

### 架構設計
```bash
# 符號連結配置（個人層級 → Git 管理的專案層級）
~/.claude/skills -> /Users/ctai/Github/ai-rules/skills
```

### 技術優勢
- **版本控制**: 所有 skills 納入 Git 管理
- **跨專案共享**: 個人層級符號連結使所有專案都能使用相同 skills
- **即時更新**: Git 中的修改立即生效於所有 Claude Code 實例
- **集中維護**: 避免重複配置和版本不一致問題

### 符號連結管理
```bash
# 檢查現有連結狀況
ls -la ~/.claude/skills
readlink ~/.claude/skills

# 建立符號連結（如果不存在）
ln -sfn /Users/ctai/Github/ai-rules/skills ~/.claude/skills

# 驗證連結正確性
ls ~/.claude/skills/
```

## Skill 發現和載入機制

### 發現優先級（符號連結架構）
Claude Code 按以下優先級搜尋和載入 skills：
1. **專案層級**: `.claude/skills/` (最高優先級，團隊共享)
2. **個人層級**: `~/.claude/skills/` (中等優先級，指向 Git 管理目錄)
3. **插件層級**: Plugin skills (最低優先級，隨插件捆綁)

**符號連結影響**：由於 `~/.claude/skills -> /Users/ctai/Github/ai-rules/skills`，個人層級實際載入的是 Git 管理的技能集，實現了跨專案共享。

### 自動觸發流程
```
用戶發出請求
    ↓
Claude 分析請求意圖和關鍵詞
    ↓ 掃描可用 skills 的 description
語意匹配和評分
    ↓ 選擇最匹配的 skill
自動載入並執行 skill
    ↓ 返回執行結果
```

### 語意匹配機制
Claude 使用以下策略進行 skill 匹配：
- **關鍵詞匹配**: 掃描 description 中的觸發詞
- **語意理解**: 分析請求的上下文和意圖
- **評分排序**: 根據匹配度對 skills 進行排序
- **自動選擇**: 選擇最高分的 skill 自動執行

## Skill 檔案結構標準

### 必要目錄結構
每個 skill 必須使用以下標準結構：

```
skill-name/
├── SKILL.md           # 必要：主要技能定義檔案
├── reference.md       # 可選：技術參考資料
├── examples.md        # 可選：使用範例
├── scripts/           # 可選：支援腳本
│   └── helper.py
├── templates/         # 可選：範本檔案
│   └── template.md
└── docs/             # 可選：詳細文檔
    └── technical.md
```

### 進階載入機制
- **漸進式載入**: 只在需要時讀取輔助檔案
- **上下文效率**: 管理記憶體使用和上下文長度
- **路徑規範**: 輔助檔案必須使用 Unix 風格路徑（正斜杠）

## Frontmatter 配置標準

### 必要配置參數
```yaml
---
name: skill-name                    # 必填：小寫、數字、連字符 (最多64字元)
description: 技能描述和觸發條件    # 必填：功能描述 + 何時使用 (最多1024字元)
allowed-tools: [Read, Write, Edit] # 可選：限制工具存取權限
model: sonnet|opus|haiku|inherit   # 可選：指定使用的 Claude 模型
skills: dependency-skill           # 可選：依賴的其他技能
---
```

### 參數技術規範

#### `name` 欄位
- **格式**: 小寫字母、數字、連字符
- **長度**: 最多 64 字元
- **範例**: `parallel-processing`, `code-analyzer`, `data-visualizer`

#### `description` 欄位（關鍵）
- **雙重功能**: 必須同時說明**功能**和**觸發條件**
- **關鍵詞**: 包含多種觸發詞和同義詞
- **使用場景**: 明確說明適用的具體場景
- **長度**: 最多 1024 字元

#### `allowed-tools` 欄位
```yaml
# 唯讀技能
allowed-tools: [Read, Grep, Glob]

# 安全技能（禁用系統操作）
allowed-tools: [Read, Write, Edit, Grep, Glob]  # 不包含 Bash

# 完整技能
allowed-tools: [Read, Write, Edit, Task, Grep, Glob, Bash]
```

#### 依賴關係
```yaml
# 單一依賴
skills: parallel-processing

# 多重依賴
skills: [parallel-processing, mermaid, code-analyzer]
```

## 當前專案 Skills 參考

> **AI 使用指南**: 以下是本專案中可自動觸發的 3 個核心 skills，所有 skills 都透過符號連結架構實現 Git 版本控制和跨專案共享。

### 並行處理和分析技能 (`parallel-processing`)
- **檔案大小**: 15567 bytes
- **觸發詞**: "並行處理", "平行處理", "同時處理", "批次分析", "多任務並行", "並行執行"
- **核心功能**:
  - 智能並行決策和成本效益分析
  - 大規模檔案分析優化
  - 真正的並行執行（`&` 和 `wait`）
  - 結果智能整合
- **適用場景**: 大規模檔案分析、多文檔品質檢查、程式碼批量審查
- **工具權限**: 完整工具集 `[Read, Write, Edit, Task, Grep, Glob, Bash]`

### 批判性思维分析技能 (`critical-thinking`)
- **檔案大小**: 10893 bytes
- **觸發詞**: "批判性思考", "第一性原理", "驗證建議", "分析設計決策", "技術評估"
- **核心功能**:
  - 基於第一性原理的技術建議驗證
  - 設計決策的深度分析
  - 外部 AI 建議的批判性評估
  - 可行性和風險識別
- **適用場景**: 技術選型評估、架構決策分析、外部建議驗證
- **工具權限**: 分析工具集 `[Read, Grep, WebFetch]`

### 視覺化圖表生成技能 (`mermaid`)
- **檔案大小**: 11766 bytes
- **觸發詞**: "圖表生成", "流程圖", "組織圖", "時序圖", "視覺化", "mermaid"
- **核心功能**:
  - 實用主義的 Mermaid 圖表生成
  - Dark/Light 模式相容性
  - 多種圖表類型支援
  - 最小干擾的視覺設計
- **適用場景**: 技術文檔圖表、流程視覺化、系統架構圖
- **工具權限**: 生成工具集 `[Read, Write, Edit]`

## AI 使用 Skills 的最佳實踐

### 有效觸發策略
```python
# 明確請求，包含觸發詞
"請並行處理這些檔案的品質檢查"
# → 自動觸發 parallel-processing skill

# 具體的使用場景描述
"我需要生成一個系統架構的時序圖"
# → 自動觸發 mermaid skill

# 批判性分析請求
"請用第一性原理分析這個技術選型"
# → 自動觸發 critical-thinking skill
```

### 技能組合使用
```python
# 複雜任務可能自動組合多個 skills
"請並行分析這些程式碼並生成視覺化報告"
# → 可能同時觸發: parallel-processing + mermaid

# 深度技術評估
"請批判性分析這個架構設計的成本效益"
# → 可能同時觸發: critical-thinking + parallel-processing
```

### 查詢可用 Skills
```python
# 查詢當前環境中的可用 skills
"What skills are available?"
"List all available skills"
"Show me all skills I can use"
```

## AI 實務使用指導

### 使用策略優先級

#### 1. Skills 優先（自動觸發）
當請求包含以下特徵時，優先等待 skills 自動觸發：
- 複雜分析和處理任務
- 需要專門領域知識
- 大規模檔案處理
- 批次操作需求

#### 2. Agents 輔助（Task 調用）
當需要以下功能時，考慮調用 agents：
- 需要隔離上下文的複雜分析
- 多階段處理工作流程
- 專門化代理服務

#### 3. Commands 明確調用（SlashCommand）
當需要以下功能時，使用 slash commands：
- 明確的系統維護操作
- 用戶指定的工具執行
- 標準化的重複任務

### AI 決策流程
```python
# AI 內部決策樹
用戶請求 → 分析複雜度
    ↓ 簡單任務
直接處理
    ↓ 複雜任務
檢查觸發詞匹配
    ↓ 匹配 skill
等待自動觸發
    ↓ 不匹配 skill
考慮調用 agent 或 command
```

### 協調使用模式

#### Skill + Agent 組合
```python
# 先觸發 skill 進行初步處理
"請並行分析這些程式碼的效能問題"
# → 觸發 parallel-processing skill

# 再調用 agent 進行深度分析
Task("基於分析結果進行詳細的代碼審查", subagent_type="code-reviewer")
```

#### Skill + Command 輔助
```python
# Skill 自動觸發主要處理
"請批判性分析這個架構設計"
# → 觸發 critical-thinking skill

# Command 輔助後續操作
SlashCommand("/milestone 記錄架構分析決策")
```

### 觸發優化建議

#### 提高 Skill 觸發率
1. **明確使用觸發詞**：在請求中包含 skill 的關鍵詞
2. **描述具體場景**：明確說明需要的處理類型
3. **避免模糊表達**：使用精準的技術術語

#### 觸發詞優化範例
```python
# ❌ 模糊表達（可能不觸發）
"看看這些檔案"

# ✅ 明確觸發（高概率觸發）
"請並行處理這些檔案進行分析"
"請批次檢查這些文檔的品質"
"請同時處理多個檔案的性能分析"
```

## 故障排除與驗證

### 常見故障模式

#### Skill 未被識別
**症狀**: skill 不會自動觸發
**診斷步驟**:
```bash
# 檢查符號連結狀態
ls -la ~/.claude/skills
readlink ~/.claude/skills

# 檢查 Git 管理的實際目錄
ls -la /Users/ctai/Github/ai-rules/skills/

# 檢查 skill 目錄結構
ls -la /Users/ctai/Github/ai-rules/skills/skill-name/
```

**解決方案**:
- **符號連結問題**: 重建符號連結 `ln -sfn /Users/ctai/Github/ai-rules/skills ~/.claude/skills`
- **目錄結構**: 確保包含 `SKILL.md` 檔案
- **YAML 語法**: 驗證 frontmatter 格式正確性

#### Skill 未自動觸發
**症狀**: skill 存在但不會自動激活
**診斷檢查**:
```markdown
# 檢查 description 的觸發詞
是否包含足夠的關鍵詞和同義詞？

# 檢查觸發條件描述
是否明確說明何時使用這個 skill？

# 測試不同的請求表達
"並行處理檔案" vs "批次分析文檔" vs "同時處理多個任務"
```

**解決方案**:
- **優化 description**: 增加更多觸發詞和使用場景
- **測試表達方式**: 嘗試不同的請求表達
- **檢查語意匹配**: 確保請求內容與 skill 描述匹配

#### 工具權限限制
**症狀**: skill 執行時權限被拒絕
**技術修正**:
```yaml
# 檢查 allowed-tools 配置
allowed-tools: [Read, Write, Edit, Grep, Glob]  # 確保包含必要工具

# 如需系統操作，添加 Bash
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
```

### AI 驗證測試流程

#### 基本功能驗證
```python
# 查詢可用 skills
"What skills are available?"

# 測試觸發詞
"請並行處理這些檔案"  # 應觸發 parallel-processing
"生成一個流程圖"        # 應觸發 mermaid
"批判性分析這個建議"   # 應觸發 critical-thinking
```

#### 符號連結驗證
```markdown
# AI 自檢查清單（符號連結架構）
1. 確認符號連結有效：readlink ~/.claude/skills
2. 驗證實際技能存在：ls /Users/ctai/Github/ai-rules/skills/
3. 檢查技能載入狀態："What skills are available?"
4. 確認 Git 追蹤狀態：git status /Users/ctai/Github/ai-rules/skills/
```

## 開發檢查清單

### Skill 結構驗證
- [x] 符合標準目錄結構
- [x] 包含必要的 `SKILL.md` 檔案
- [x] YAML frontmatter 語法正確
- [x] `name` 符合命名規範
- [x] 符號連結指向正確的 Git 管理路徑

### Description 優化驗證
- [x] 同時說明功能和觸發條件
- [x] 包含多種觸發詞和同義詞
- [x] 明確描述適用場景
- [x] 長度在 1024 字元以內
- [x] 語意表達清晰準確

### 技術規範驗證
- [x] `allowed-tools` 配置合理且必要
- [x] 依賴關係宣告正確
- [x] 模型指定符合需求
- [x] 輔助檔案路徑使用正斜杠格式
- [x] 支援漸進式載入機制

### AI 友好性驗證
- [x] 技術術語精準無歧義
- [x] 觸發機制清晰可預測
- [x] 與其他 skills 無衝突
- [x] 與 agents/commands 協調良好
- [x] 整體設計符合 AI 使用模式

### 符號連結架構驗證
- [x] 符號連結有效且指向正確目標：`~/.claude/skills -> /Users/ctai/Github/ai-rules/skills`
- [x] Git 管理的 skills 可正常載入並被 Claude 識別
- [x] 修改即時生效於所有 Claude Code 實例
- [x] 與 agents/commands 符號連結架構完全一致
- [x] 跨專案共享機制正常運作