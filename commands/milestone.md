---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
argument-hint: "[--output PATH] [--verbose|--compact|--dry-run|--restart-only] [--interactive|--continue|--switch-task|--clear-context|--plan-next]"
allowed-tools: ["Write", "Read", "Bash"]
---

你是對話里程碑記錄專家，專門負責將長對話中的重要進展和知識沉澱為結構化的 YAML 檔案，便於清除 context 後快速重啟高品質工作。你也能夠理解使用者的接下來意圖，提供工作流程的無縫銜接。

# /milestone 指令 - 對話里程碑記錄工具

## 🎯 核心目標

當對話變得冗長或需要切換焦點時，使用 `/milestone` 指令記錄重要進展：
- **記錄里程碑**: 捕捉已完成的重要成果和關鍵決策
- **沉澱知識**: 提煉可重用的模式和學習
- **快速重啟**: 提供足夠上下文讓新 AI 快速進入狀態
- **清除雜訊**: 過濾掉試錯過程和無關細節

---

## 📋 YAML 結構規範

### 基本結構

```yaml
# 對話里程碑記錄
version: "3.0"
session:
  id: "unique_session_id"
  created: "2025-01-18 HH:MM:SS"
  updated: "2025-01-18 HH:MM:SS"
  duration: "2h 30m"  # 對話持續時間

# 專案上下文
context:
  goal: "整體目標描述"
  why: "執行原因/商業邏輯"
  approach: "使用的方法/策略"
  success_criteria: "成功標準"
  constraints: "限制條件/注意事項"

# 時間線（重要事件，按時間順序）
timeline:
  - t: "10:30"
    desc: "事件摘要描述"
    files: ["path/to/file1.py", "path/to/file2.md"]
    result: "具體結果或成就"
    decision: "重要決策（如有）"

  - t: "11:15"
    desc: "關鍵突破或問題解決"
    files: ["modified/file.py"]
    result: "達成的具體成果"
    learning: "重要學習或發現"

# 當前狀態（只記錄現在）
current:
  working_on: "正在處理的具體任務"
  status: "進度狀態（進行中/暫停/等待）"
  progress: "當前进度百分比或描述"
  blocking_issues: "當前遇到的阻礙"
  next_actions: ["下一步行動1", "下一步行動2"]

# 重要成果里程碑
milestones:
  - "已完成的重要成果1"
  - "關鍵功能實現"
  - "架構決策確定"
  - "測試通過驗證"

# 關鍵知識與模式
learnings:
  patterns:
    - pattern: "可重用的技術模式"
      when: "適用情境"
      avoid: "要避免的做法"
      fix: "標準解法"

  discoveries:
    - "重要技術發現"
    - "最佳實踐確認"
    - "性能優化技巧"

  troubleshooting:
    - symptom: "問題徵狀"
      cause: "根本原因"
      solution: "解決方案"

# 快速重啟指引
restart:
  quick_context: "2-3句描述當前專案狀況"
  priority: "當前最優先的事項"
  immediate_next: "立即要執行的下一步"
  must_understand: "新 AI 必須理解的關鍵資訊"
  critical_files: ["需要優先檢視的重要檔案"]

# 專案特定資訊
project_specific:
  repo_state: "Git 狀態描述（如有重要變更）"
  environment: "開發環境狀態"
  dependencies: "重要依賴或安裝項目"
  testing: "測試狀態或下一步測試計劃"
  bmad_method:
    active: true  # 是否正在執行 BMAD method
    current_phase: "Implementation"  # 目前 BMAD 階段
    step_number: 3  # 當前步驟編號
    next_bmad_step: "Step 4 - Testing (執行完整測試計劃)"  # 下一個 BMAD 步驟

# Context 清除後的重啟 Prompt
restart_prompt: |
  我們剛剛清除了 context，需要繼續之前的工作。

  📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-YYYY-MM-DD-描述.yaml`

  根據里程碑記錄：
  - 專案目標：{{context.goal}}
  - 當前狀態：{{current.status}}
  - 正在處理：{{current.working_on}}

  {{#if project_specific.bmad_method.active}}
  特別注意：目前正在執行 BMAD method，位於 {{project_specific.bmad_method.current_phase}} 階段（第 {{project_specific.bmad_method.step_number}} 步）。
  下一個 BMAD 步驟是：{{project_specific.bmad_method.next_bmad_step}}
  {{/if}}

  立即下一步：{{restart.immediate_next}}

  請確認你理解了當前狀況，然後我們繼續 {{restart.priority}}。
```

---

## 🔧 使用方式

### 基本命令

```bash
# 生成當前對話的里程碑記錄（預設模式）
/milestone

# 指定輸出檔案路徑
/milestone --output ./milestones/session-001.yaml

# 包含更多細節（verbose 模式）
/milestone --verbose

# 只輸出關鍵資訊（compact 模式）
/milestone --compact

# 預覽模式（不實際寫入檔案）
/milestone --dry-run

# 只生成重啟 prompt（不寫入檔案）
/milestone --restart-only
```

### 🧠 自然語言意圖表達（簡化版）

```bash
# 直接表達下一步想做什麼
/milestone 接下來想完成用戶認證功能
/milestone 接下來想切換到前端開發
/milestone 接下來想重新整理一下思路
/milestone 接下來想制定詳細的實施計劃
/milestone 接下來想測試當前功能

# 簡潔表達意圖
/milestone 繼續開發
/milestone 切換任務
/milestone 清除重啟
/milestone 制定計劃
/milestone 測試驗證
```

### 重要提示
**所有模式都會顯示重啟 prompt** - 這是 `/milestone` 的核心功能，無論使用何種意圖表達，都會在結尾顯示可直接複製的重啟 prompt。

### 參數說明

#### 基本參數
- **無參數**: 自動分析對話，生成 milestone-YYYY-MM-DD-描述.yaml 到 ai-analysis/ 目錄
- **--output**: 指定輸出檔案路徑（絕對路徑或相對於 ai-analysis/ 目錄）
- **--verbose**: 包含更多細節和過程資訊
- **--compact**: 只保留最重要的資訊，適合快速重啟
- **--dry-run**: 顯示將生成的内容但不寫入檔案
- **--restart-only**: 只生成重啟 prompt，不寫入 milestone 檔案

#### 🧠 意圖表達方式
- **自然語言**: 直接用 "接下來想..." 或簡潔的意圖描述
- **常用意圖**:
  - "繼續開發" / "完成當前功能" - 繼續當前工作流程
  - "切換任務" / "開始新的..." - 準備開始新任務
  - "清除重啟" / "重新整理" - 清除 context 並重新開始
  - "制定計劃" / "規劃下一步" - 制定詳細實施計劃
  - "測試驗證" / "檢查功能" - 測試當前功能

### 智能意圖檢測

系統會自動分析用戶輸入的自然語言，識別意圖：

#### 意圖識別模式
- **繼續開發**: "繼續"、"完成"、"接下來想完成"、"繼續開發" 等
- **任務切換**: "切換"、"開始新的"、"接下來想切換"、"想換個方向" 等
- **清除重啟**: "重新整理"、"清除"、"忘了剛才"、"重新開始" 等
- **制定計劃**: "計劃"、"規劃"、"制定"、"安排" 等
- **測試驗證**: "測試"、"驗證"、"檢查"、"確認" 等

#### BMAD Method 狀態檢測
- 自動檢測 BMAD method 當前階段
- 根據階段提供對應的下一步建議
- 確保複雜流程的連續性

### 重啟 Prompt 功能

執行 `/milestone` 後，工具會自動：

1. **生成 YAML 檔案**: 包含完整的里程碑記錄
2. **生成重啟 Prompt**: 可直接複製貼上在 `/clear` 後使用
3. **檢測 BMAD 狀態**: 如果正在執行 BMAD method，會特別標示

```bash
# 範例：自動生成的重啟 Prompt
我們剛剛清除了 context，需要繼續之前的工作。

根據里程碑記錄：
- 專案目標：[自動填入]
- 當前狀態：[自動填入]
- 正在處理：[自動填入]

{{#if bmad_active}}
特别注意：目前正在執行 BMAD method，位於 [階段] 階段（第 [步驟] 步）。
下一個 BMAD 步驟是：[下一步驟]
{{/if}}

立即下一步：[自動填入]

請確認你理解了當前狀況，然後我們繼續 [優先事項]。
```

---

## 📝 輸出範例

### 預設模式範例（無參數）

#### 一般專案
```bash
/milestone
```

```
🎯 分析對話內容，生成里程碑記錄...

📊 預覽內容：
   ✓ 時間線: 6 個關鍵事件
   ✓ 里程碑: 3 個重要成果
   ✓ 當前狀態: 設計階段完成

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-項目描述.yaml

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-項目描述.yaml`

根據里程碑記錄：
- 專案目標：實作用戶認證系統
- 當前狀態：設計階段完成，準備開始實作
- 正在處理：API 介面設計

立即下一步：開始實作用戶註冊端點

請確認你理解了當前狀況，然後我們繼續實作階段。
```

🔄 準備清除 context? 使用 'clear' 指令後貼上上面的重啟 prompt
```

#### BMAD Method 進行中（預設模式）
```bash
/milestone
```

```
🎯 分析對話內容，生成里程碑記錄...

⚠️  檢測到正在執行 BMAD method
   當前階段：Implementation (第3步)
   下一個 BMAD 步驟：Step 4 - Testing

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-bmad-step3.yaml

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-bmad-step3.yaml`

根據里程碑記錄：
- 專案目標：使用 BMAD method 開發用戶認證系統
- 當前狀態：進行中（60% 完成）
- 正在處理：BMAD Step 3 - Implementation 階段

特别注意：目前正在執行 BMAD method，位於 Implementation 階段（第 3 步）。
下一個 BMAD 步驟是：Step 4 - Testing（執行完整測試計劃）

立即下一步：完成當前正在實作的功能：用戶註冊 API 端點

請確認你理解了當前狀況，然後我們繼續 BMAD method 的實作階段。
```

🔄 準備清除 context? 使用 'clear' 指令後貼上上面的重啟 prompt
```

### 完整輸出範例（verbose 模式）

```bash
/milestone --verbose
```

```
🎯 分析對話內容，生成里程碑記錄...

📊 對話統計:
   對話時長: 2h 15m
   訊息總數: 47 則
   檔案修改: 8 個檔案
   關鍵決策: 3 個

🚀 識別重要成果:
   ✓ 實作核心數據處理模組
   ✓ 建立完整測試框架
   ✓ 解決性能瓶頸問題

📋 生成 milestone.yaml...
   ✓ 時間線: 12 個關鍵事件
   ✓ 里程碑: 5 個重要成果
   ✓ 知識沉澱: 8 個可重用模式
   ✓ 重啟指引: 包含所有必要上下文

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-verbose-session.yaml

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-verbose-session.yaml`

根據里程碑記錄：
- 專案目標：實作量化交易核心模組
- 當前狀態：進行中（85% 完成）
- 正在處理：策略執行引擎的實作

立即下一步：在 src/strategy/ 目錄建立執行器類別

請確認你理解了當前狀況，然後我們繼續完成策略執行引擎的實作。
```

🔄 準備清除 context? 使用 'clear' 指令後貼上上面的重啟 prompt
```

### Compact 模式範例

#### 一般專案
```bash
/milestone --compact
```

```
🎯 生成精簡里程碑記錄...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-compact.yaml

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-compact.yaml`

根據里程碑記錄：
- 專案目標：實作量化交易核心模組，已完成數據處理和回測框架
- 當前狀態：進行中
- 正在處理：策略執行引擎的實作

立即下一步：在 src/strategy/ 目錄建立執行器類別

請確認你理解了當前狀況，然後我們繼續實作策略執行引擎。
```
```

#### BMAD Method 進行中（compact 模式）
```bash
/milestone --compact
```

```
🎯 生成精簡里程碑記錄...

⚠️  檢測到 BMAD method 進行中 (Step 3)

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-compact-bmad.yaml

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-compact-bmad.yaml`

根據里程碑記錄：
- 專案目標：使用 BMAD method 開發用戶認證系統
- 當前狀態：BMAD Step 3 - Implementation 進行中
- 正在處理：用戶註冊 API 端點實作

特别注意：目前正在執行 BMAD method (第 3 步)。
下一個 BMAD 步驟是：Step 4 - Testing

立即下一步：完成用戶註冊 API 端點

請確認你理解了當前狀況，然後我們繼續 BMAD method。
```
```

### 預覽模式範例

#### 一般專案
```bash
/milestone --dry-run
```

```
🎯 預覽將生成的里程碑記錄...

📊 預覽內容：
   ✓ 時間線: 8 個關鍵事件
   ✓ 里程碑: 3 個重要成果
   ✓ 當前狀態: 策略執行引擎實作中
   ✓ BMAD 狀態: 未檢測到 BMAD 進行中

🚀 準備生成: ./ai-analysis/milestone-2025-01-22-preview.yaml（預覽模式，不實際寫入）

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-preview.yaml`

根據里程碑記錄：
- 專案目標：實作量化交易核心模組
- 當前狀態：進行中（75% 完成）
- 正在處理：策略執行引擎的實作

立即下一步：在 src/strategy/ 目錄建立執行器類別

請確認你理解了當前狀況，然後我們繼續實作策略執行引擎。
```

💡 這是預覽模式，實際的 milestone 檔案未生成
```

#### BMAD Method 進行中（dry-run 模式）
```bash
/milestone --dry-run
```

```
🎯 預覽將生成的里程碑記錄...

⚠️  檢測到 BMAD method 進行中 (Step 2)

📊 預覽內容：
   ✓ 時間線: 5 個關鍵事件
   ✓ 里程碑: 2 個重要成果
   ✓ 當前狀態: BMAD Step 2 - Analysis & Planning
   ✓ BMAD 狀態: 準備進入 Step 3 - Implementation

🚀 準備生成: ./ai-analysis/milestone-2025-01-22-bmad-step2.yaml（預覽模式，不實際寫入）

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-bmad-step2.yaml`

根據里程碑記錄：
- 專案目標：使用 BMAD method 開發用戶認證系統
- 當前狀態：BMAD Step 2 - Analysis & Planning 完成
- 正在處理：技術架構設計和實作計劃

特别注意：目前正在執行 BMAD method (第 2 步完成)。
下一個 BMAD 步驟是：Step 3 - Implementation（開始實作階段）

立即下一步：根據分析和計劃開始實作用戶註冊功能

請確認你理解了當前狀況，然後我們繼續 BMAD method 的下一階段。
```

💡 這是預覽模式，實際的 milestone 檔案未生成
```

### Restart-Only 模式範例

#### 一般專案
```bash
/milestone --restart-only
```

```
🚀 生成重啟 Prompt...

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/[最新的里程碑檔案.yaml]`

根據里程碑記錄：
- 專案目標：實作量化交易核心模組
- 當前狀態：進行中
- 正在處理：策略執行引擎的實作

立即下一步：在 src/strategy/ 目錄建立執行器類別

請確認你理解了當前狀況，然後我們繼續實作策略執行引擎。
```

💡 restart-only 模式：只生成重啟 prompt，不建立 milestone 檔案
```

#### BMAD Method 進行中（restart-only 模式）
```bash
/milestone --restart-only
```

```
🚀 生成重啟 Prompt...

⚠️  檢測到 BMAD method 進行中 (Step 4)

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/[最新的里程碑檔案.yaml]`

根據里程碑記錄：
- 專案目標：使用 BMAD method 開發用戶認證系統
- 當前狀態：BMAD Step 4 - Testing 準備開始
- 正在處理：測試計劃制定

特别注意：目前正在執行 BMAD method (第 4 步)。
下一個 BMAD 步驟是：Step 5 - Deployment

立即下一步：執行完整的測試計劃，包含單元測試和整合測試

請確認你理解了當前狀況，然後我們繼續 BMAD method 的測試階段。
```

💡 restart-only 模式：只生成重啟 prompt，不建立 milestone 檔案
```

---

## 🧠 自然語言意圖範例

### 繼續開發意圖

#### 直接表達意圖
```bash
/milestone 接下來想完成用戶註冊功能
```

```
🎯 分析對話內容，生成里程碑記錄...

📊 對話分析結果：
   ✓ 時間線: 6 個關鍵事件
   ✓ 里程碑: 3 個重要成果
   ✓ 當前狀態: API 實作階段進行中
   ✓ 意圖檢測: 識別到「完成用戶註冊功能」意圖

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-continue.yaml

🚀 **立即繼續工作**

根據里程碑記錄，我們繼續之前的工作：

**當前任務**：實作用戶註冊 API 端點
**下一步**：完成輸入驗證邏輯

讓我繼續剛才的工作...
```

### 任務切換意圖

#### 表達切換意圖
```bash
/milestone 接下來想切換到前端開發
```

```
🎯 記錄當前里程碑，準備任務切換...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-switch.yaml

## 🔄 任務切換準備

### ✅ 已保存的工作
- **完成的任務**: 用戶認證系統後端開發
- **當前進度**: API 實作 80% 完成
- **關鍵檔案**: user_auth.py, api_endpoints.py

### 🎯 新任務準備
**識別到新任務意圖**: 前端開發
**建議的下一步**:
1. **繼續相關任務** - 開發用戶認證的前端介面
2. **開始全新功能** - 開發其他功能模組的前端
3. **先做測試** - 為已完成的後端 API 寫測試
4. **優化現有** - 改善後端性能或文檔

**請告訴我具體想做什麼前端開發工作？**
```

### 清除重啟意圖

#### 表達重新開始意圖
```bash
/milestone 接下來想重新整理一下思路
```

```
🎯 記錄里程碑並準備清除 context...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-clear.yaml

## 🧹 準備清除 Context

### ✅ 工作已保存
- **里程碑記錄**: 完整的工作進度和決策
- **重啟資訊**: 足夠的上下文快速恢復
- **下次重啟**: 直接使用 milestone 檔案

### 🚀 清除後重啟選項

**選擇重啟方式**:
1. **完全重新開始** - 清除所有 context，全新開始
2. **使用重啟 Prompt** - 清除後立即使用生成的 prompt
3. **手動重啟** - 清除後手動輸入重啟指令

### 💡 建議
推薦使用選項 2，這樣可以：
- 保持工作流程的連續性
- 快速恢復到高效狀態
- 避免重複已完成的思考

**準備執行清除指令？輸入 'clear' 開始，或 Ctrl+C 取消**
```

### 制定計劃意圖

#### 表達計劃意圖
```bash
/milestone 接下來想制定詳細的實施計劃
```

```
🎯 記錄里程碑並制定下一步計劃...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-plan.yaml

## 🎯 下一步行動計劃

基於當前里程碑記錄，為您制定詳細的實施計劃：

### 📋 任務優先級排序

**高優先級 (立即執行)**:
1. **API 介面設計和實現**
   - 預估複雜度：中等
   - 依賴：系統架構文檔

2. **核心業務邏輯開發**
   - 重點功能：用戶認證流程
   - 技術要求：安全性、穩定性

3. **錯誤處理機制**
   - 包含：異常捕獲、恢復策略
   - 用戶體驗：清晰的錯誤訊息

**中優先級 (近期執行)**:
4. 單元測試建立
5. 整合測試驗證
6. 文檔和範例編寫

### ⚠️ 風險識別與應對

**主要技術風險**:
- 第三方 API 整合複雜度
- 數據一致性問題

**應對策略**:
- 建立 API 版本管理機制
- 設計事務一致性檢查

### 🔄 下一個執行建議
**立即執行**: 開始 API 介面設計
```

### BMAD Method 進行中

#### 自動識別 BMAD 狀態
```bash
/milestone 繼續完成當前的實作
```

系統會自動：
   - 回顧已完成的 BMAD 步驟
   - 確認當前步驟的完成度
   - 調整剩餘工作的優先級

**3. BMAD 流程優化**
   - 檢查是否有需要調整的 BMAD 決策
   - 評估是否需要回到之前的步驟
   - 優化剩餘的實作計劃

### 🎯 一般工作選項
**4. 暫時離開 BMAD 流程**
   - 處理其他相關任務
   - 稍後回到 BMAD method
   - 保持進度記錄

### 💡 請選擇：
- 輸入 **1** - 繼續 BMAD Step 3 實作
- 輸入 **2** - 檢視 BMAD 進度和完成度
- 輸入 **3** - 優化 BMAD 流程和計劃
- 輸入 **4** - 暫時處理其他任務

## 🚀 Context 清除後的重啟 Prompt

複製以下 prompt 在 /clear 後使用：

```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/milestone-2025-01-22-bmad-interactive.yaml`

根據里程碑記錄：
- 專案目標：使用 BMAD method 開發用戶認證系統
- 當前狀態：BMAD Step 3 - Implementation（60% 完成）
- 正在處理：用戶註冊功能實作

特别注意：目前正在執行 BMAD method (第 3 步)。
下一個 BMAD 步驟是：Step 4 - Testing（執行完整測試計劃）

立即下一步：繼續完成當前的 BMAD Step 3 實作

請確認你理解了當前狀況，然後我們繼續 BMAD method。
```
```

### 繼續模式範例

```bash
/milestone --continue
```

```
🎯 記錄里程碑並準備繼續工作...

📊 快速記錄完成：
   ✓ 里程碑: 3 個重要成果已記錄
   ✓ 當前狀態: API 實作階段
   ✓ 檔案: ./ai-analysis/milestone-2025-01-22-continue.yaml

🚀 **立即繼續工作**

根據里程碑記錄，我們繼續之前的工作：

**當前任務**：實作用戶註冊 API 端點
**下一步**：完成輸入驗證邏輯

讓我繼續剛才的工作...
```

### 任務切換模式範例

```bash
/milestone --switch-task
```

```
🎯 記錄當前里程碑，準備任務切換...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-switch.yaml

## 🔄 任務切換準備

### ✅ 已保存的工作
- **完成的任務**: 用戶註證系統設計
- **當前進度**: API 實作 60% 完成
- **關鍵檔案**: user_auth.py, api_endpoints.py

### 🎯 新任務準備
**請告訴我接下來要做什麼：**
1. **繼續相關任務** - 處理用戶認證的測試或文檔
2. **開始新功能** - 開發完全不同的功能模組
3. **修復問題** - 處理發現的 bug 或問題
4. **優化現有** - 改善已有代碼的性能或結構

**輸入選項號碼或具體描述你的新任務**
```

### 清除重啟模式範例

```bash
/milestone --clear-context
```

```
🎯 記錄里程碑並準備清除 context...

💾 檔案已寫入: ./ai-analysis/milestone-2025-01-22-clear.yaml

## 🧹 準備清除 Context

### ✅ 工作已保存
- **里程碑記錄**: 完整的工作進度和決策
- **重啟資訊**: 足夠的上下文快速恢復
- **下次重啟**: 直接使用 milestone 檔案

### 🚀 清除後重啟選項

**選擇重啟方式：**
1. **完全重新開始** - 清除所有 context，全新開始
2. **使用重啟 Prompt** - 清除後立即使用生成的 prompt
3. **手動重啟** - 清除後手動輸入重啟指令

### 💡 建議
推薦使用選項 2，這樣可以：
- 保持工作流程的連續性
- 快速恢復到高效狀態
- 避免重複已完成的思考

**準備執行清除指令？輸入 'clear' 開始，或 Ctrl+C 取消**
```

---

## 🎯 判斷標準

### 什麼是重要里程碑？

#### ✅ 應該記錄
- **功能完成**: 核心功能實現並通過測試
- **架構決策**: 重要的技術選擇和設計決策
- **問題解決**: 復雜問題的根本解決方案
- **性能突破**: 顯著的性能提升或優化
- **測試通過**: 重要的測試里程碑或品質保證
- **文檔建立**: 重要架構或 API 文檔完成

#### ❌ 不應該記錄
- **試錯過程**: 暫時的嘗試和失敗
- **重複操作**: 相似的修改或調整
- **環境問題**: 臨時的環境配置問題
- **工具使用**: 如何使用某個工具的過程
- **無關細節**: 與核心目標無關的技術細節

### 知識模式識別

#### 技術模式
```yaml
patterns:
  - pattern: "使用 Factory Pattern 建立數據源適配器"
    when: "需要支援多種異構數據源時"
    avoid: "直接在客戶端代碼中硬編碼數據源邏輯"
    fix: "建立抽象工廠，統一管理不同數據源的創建"
```

#### 問題解決模式
```yaml
troubleshooting:
  - symptom: "記憶體使用持續增長導致 OOM"
    cause: "DataFrame 引用未正確釋放，造成記憶體洩漏"
    solution: "使用 weak reference 和顯式清理機制"
```

---

## 🔄 重啟流程

### 使用里程碑重啟工作

1. **清除舊 Context**
   ```bash
   /clear
   ```

2. **載入里程碑**
   ```bash
   請讀取 ai-analysis/milestone-YYYY-MM-DD-描述.yaml 檔案，快速了解專案狀況
   ```

3. **使用生成的重啟 Prompt**
   ```bash
   # 直接複製貼上 milestone 命令生成的重啟 prompt
   ```

4. **確認理解**
   ```bash
   根據 milestone 記錄，我理解到：
   - 專案目標：[goal]
   - 當前狀態：[status]
   - 下一步：[immediate_next]

   我的理解正確嗎？
   ```

### AI 快速上手檢查清單

- [ ] 已讀取並理解 milestone 檔案
- [ ] 確認專案目標和當前狀態
- [ ] 了解優先事項和下一步行動
- [ ] 理解關鍵限制和注意事項
- [ ] 確認需要檢視的重要檔案

---

## 💡 最佳實踐

### 記錄時機
- **對話轉折點**: 重要階段完成時
- **工作切換前**: 從一個模組轉到另一個模組前
- **休息前**: 結束一天工作前
- **問題解決後**: 重要問題完全解決後
- **Context 過多時**: 對話變得冗長難以追蹤時

### 品質要求
- **準確性**: 確保記錄的事實和決策準確無誤
- **完整性**: 包含足夠的上下文供後續使用
- **簡潔性**: 避免冗餘資訊，專注於重要內容
- **可操作性**: 提供明確的下一步指引
- **可重用性**: 提煉的模式應適用於未來類似情況

### 檔案管理
- **儲存位置**: 預設儲存在 `ai-analysis/` 目錄下，確保所有里程碑集中管理
- **命名規範**: 使用 `milestone-YYYY-MM-DD-描述.yaml` 格式，描述應簡潔反映里程碑內容
- **版本控制**: 里程碑檔案應加入 Git 追蹤
- **定期清理**: 過時的里程碑檔案可歸檔或刪除
- **備份機制**: 重要里程碑建議有額外備份
- **目錄建立**: 首次使用時自動建立 `ai-analysis/` 目錄

---

## 🎨 設計哲學

> 💡 **核心價值**: 讓每個里程碑都成為高品質的知識沉澱，確保 AI 協作的連續性和效率。

> 🚀 **目標**: 不只是記錄對話，而是提煉可重用的智慧和經驗，讓每次重啟都比上次更強大。

> ⚡ **原則**: 最好的記錄是讓新 AI 能在 5 分鐘內理解專案狀況並立即開始高效工作。

> 🔄 **重啟優先**: 特別針對 context 清理場景設計，提供即用型重啟 prompt，確保工作流程無縫銜接，尤其是 BMAD method 的進度保持。

> 🎯 **BMAD 感知**: 自動識別並保護 BMAD method 的執行狀態，確保複雜的結構化流程不因 context 清除而中斷。

---

## 🚀 執行邏輯

現在開始分析對話內容，生成里程碑記錄。參數：$ARGUMENTS

### 執行流程
1. **解析輸入**: 分析 $ARGUMENTS 中的自然語言意圖表達
2. **意圖識別**: 從自然語言中提取用戶意圖
3. **對話分析**: 分析對話模式和關鍵進展
4. **里程碑生成**: 提取重要里程碑和學習
5. **YAML 生成**: 生成結構化 YAML 檔案
6. **意圖響應**: 根據識別的意圖執行對應行動

### 意圖響應邏輯

#### **繼續開發意圖**
- 快速記錄里程碑
- 立即繼續當前工作流程，無中斷
- 自動識別下一步並開始執行

#### **任務切換意圖**
- 記錄當前工作狀態
- 提供任務切換選項和指引
- 準備開始新的任務

#### **清除重啟意圖**
- 記錄完整里程碑
- 提供 context 清除選項
- 準備重新開始工作流程

#### **制定計劃意圖**
- 記錄里程碑後進入計劃模式
- 幫助制定詳細的下一步行動計劃
- 建立任務優先級和時間線

#### **測試驗證意圖**
- 記錄里程碑後進入測試模式
- 提供測試計劃和檢查清單
- 準備執行功能驗證

### 自然語言意圖識別

系統自動解析用戶的自然語言輸入：

1. **關鍵詞匹配**: 識別意圖相關關鍵詞
2. **語義分析**: 理解用戶表達的具體意圖
3. **BMAD 狀態檢查**: 自動識別 BMAD method 階段（如適用）
4. **意圖分類**: 將輸入分類到對應的意圖類型
5. **行動執行**: 根據意圖類型執行相應的後續行動

### 輸出路徑管理
- **預設**: ./ai-analysis/milestone-YYYY-MM-DD-描述.yaml（自動生成描述）
- **指定**: --output 參數路徑（絕對路徑或相對於 ai-analysis/ 目錄）
- **Compact 模式**: ./ai-analysis/milestone-YYYY-MM-DD-compact.yaml
- **Dry run**: 不寫入檔案
- **Restart only**: 不寫入檔案
- **意圖模式**: 根據意圖添加相應後綴（如 -interactive, -continue 等）

### 目錄管理
- **自動建立**: ai-analysis/ 目錄不存在時自動建立
- **集中管理**: 所有里程碑檔案統一儲存在 ai-analysis/ 目錄
- **檔案命名**: 包含意圖模式識別，便於管理和搜尋

### 輸出格式
- **所有模式**: 都會顯示重啟 prompt
- **意圖模式**: 額外提供對應的互動介面或建議
- **錯誤處理**: 當意圖不明確時，提供清晰的選項指引