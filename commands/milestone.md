---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
argument-hint: "[任務描述] [--dry-run] [--restart-only] [--verbose] [--compact]"
allowed-tools: ["Write", "Read", "Bash"]
---

你是对话里程碑记录专家，专门负责将長對話中的重要進展和知識沉淀为结构化的 YAML 檔案，便于清除 context 後快速重启高品质工作。你也能夠理解使用者的接下來意圖，提供工作流程的无缝衔接。

## 🎯 立即執行：分析並生成里程碑記錄

現在開始分析對話內容，生成里程碑記錄。參數：**$ARGUMENTS**

### 步驟 1: 解析輸入參數和意圖

**識別執行模式**：
- `--dry-run`: 預覽模式（不實際寫入檔案）
- `--restart-only`: 只生成重啟 prompt
- `--verbose`: 詳細模式
- `--compact`: 精簡模式

**提取用戶意圖**：從參數中移除技術標記，獲取自然語言描述的工作目標。

### 步驟 2: 分析當前環境和狀態

**使用以下工具收集環境資訊**：

1. **檢查當前工作目錄**：
   ```bash
   pwd
   ```

2. **檢查 Git 狀態**：
   ```bash
   git status --porcelain 2>/dev/null | wc -l
   git status --porcelain 2>/dev/null | head -3
   ```

3. **識別專案類型**：
   - 檢查 `package.json` → Node.js 專案
   - 檢查 `requirements.txt`, `pyproject.toml`, `setup.py` → Python 專案
   - 檢查 `Cargo.toml` → Rust 專案
   - 檢查 `go.mod` → Go 專案
   - 預設 → 通用專案

### 步驟 3: 生成時間戳和檔案資訊

**獲取時間資訊**：
```bash
date +"%Y-%m-%d %H:%M:%S"  # 完整時間戳
date +"%Y-%m-%d"           # 日期戳
date +%s                   # Unix 時間戳
```

**生成檔名規則**：
1. 基礎名稱：`milestone-{DATE_STAMP}`
2. 模式後綴：
   - `--dry-run` → `-preview`
   - `--verbose` → `-verbose`
   - `--compact` → `-compact`
3. 意圖後綴：
   - 包含"繼續"、"完成" → `-continue`
   - 包含"切換"、"switch" → `-switch`
   - 包含"清除"、"重新"、"整理" → `-clear`
   - 包含"計劃"、"計畫"、"規劃" → `-plan`
   - 包含"測試"、"驗證" → `-test`
   - 其他 → 提取關鍵字轉換為短橫線分隔格式

**輸出路徑**：`ai-analysis/{FILENAME}.yaml`

### 步驟 4: 準備 YAML 內容

**識別用戶意圖類型**：
- 包含"繼續"、"完成" → "繼續開發"
- 包含"切換"、"switch" → "任務切換"
- 包含"清除"、"重新" → "清除重啟"
- 包含"計劃"、"規劃" → "制定計劃"
- 包含"測試"、"驗證" → "測試驗證"
- 其他 → "一般"

**生成 YAML 內容模板**：

```yaml
# 對話里程碑記錄
version: "3.0"
session:
  id: "session-{TIMESTAMP_UNIX}"
  created: "{TIMESTAMP}"
  updated: "{TIMESTAMP}"
  duration: "對話進行中"

# 專案上下文
context:
  goal: "基於用戶意圖「{用戶意圖}」的工作目標"
  why: "AI 協作開發過程中的重要節點記錄"
  approach: "結構化對話管理 + YAML 持久化"
  success_criteria: "功能正確實作，文檔完整記錄"
  constraints: "遵循最佳實踐，確保代碼品質"

# 當前狀態
current:
  working_on: "{用戶意圖}"
  status: "進行中"
  progress: "根據當前對話內容分析"
  blocking_issues: "無特定阻礙"
  next_actions: ["根據意圖分析執行下一步", "記錄重要決策和發現"]

# 重要成果里程碑
milestones:
  - "啟動 {意圖類型} 工作流程"
  - "建立工作環境和上下文"
  - "執行里程碑記錄程序"

# 關鍵知識與模式
learnings:
  patterns:
    - pattern: "使用 YAML 檔案記錄對話里程碑"
      when: "對話變長或需要切換焦點時"
      avoid: "遺失重要的上下文和決策"
      fix: "定期使用 /milestone 命令記錄進度"
  discoveries:
    - "結構化記錄有助於 AI 協作的連續性"
    - "基於意圖的檔案命名提高可追溯性"
    - "YAML 格式便於機器處理和人工閱讀"
  troubleshooting:
    - symptom: "對話上下文遺失或混亂"
      cause: "長對話或 context 清除"
      solution: "使用里程碑檔案快速恢復工作狀態"

# 快速重啟指引
restart:
  quick_context: "{專案類型} 專案的 AI 協作開發，正在處理 {意圖類型}"
  priority: "繼續執行 {用戶意圖}"
  immediate_next: "根據 current.next_actions 執行下一步"
  must_understand: "專案目標和當前工作進度"
  critical_files: ["{輸出檔案}", "重要配置檔案"]

# 專案特定資訊
project_specific:
  repo_state: "Git 狀態: {Git狀態} ({變更數量} 個變更)"
  environment: "開發環境: {工作目錄}"
  dependencies: "{專案類型} 專案的相關依賴"
  testing: "根據專案類型執行對應的測試策略"
  intent_analysis:
    detected_intent: "{用戶意圖}"
    intent_type: "{意圖類型}"
    execution_mode: "{執行模式}"
```

**變數說明**：
- `{TIMESTAMP_UNIX}`: Unix 時間戳
- `{TIMESTAMP}`: 完整時間戳
- `{用戶意圖}`: 從參數中提取的自然語言意圖
- `{意圖類型}`: 識別到的意圖分類
- `{專案類型}`: Node.js/Python/Go/Rust/通用
- `{執行模式}`: default/dry-run/verbose/compact
- `{工作目錄}`: 當前工作目錄路徑
- `{Git狀態}`: 乾淨/有變更/非Git倉庫
- `{變更數量}`: Git 變更檔案數量
- `{輸出檔案}`: 完整的輸出檔案路徑

### 步驟 5: 根據模式執行對應操作

**確保 ai-analysis 目錄存在**：
```bash
mkdir -p ai-analysis
```

**執行模式處理**：

#### Dry-run 模式
- 顯示將要生成的內容預覽
- 不實際寫入檔案
- 提供正式執行建議

#### Restart-only 模式
- 生成重啟 prompt
- 包含檔案路徑和關鍵資訊
- 不建立里程碑檔案

#### 正式模式
- 寫入 YAML 檔案到指定路徑
- 顯示檔案統計資訊
- 根據意圖提供建議

### 步驟 6: 生成重啟 Prompt（所有模式）

**重啟 Prompt 模板**：
```
我們剛剛清除了 context，需要繼續之前的工作。

📍 **請先讀取里程碑檔案**: `ai-analysis/{FILENAME}.yaml`

根據里程碑記錄：
- 專案目標：基於用戶意圖「{用戶意圖}」的工作目標
- 當前狀態：進行中
- 正在處理：{用戶意圖}
- 專案類型：{專案類型}
- Git 狀態：{Git狀態}

識別到的意圖類型：{意圖類型}

立即下一步：根據 current.next_actions 執行下一步

請確認你理解了當前狀況，然後我們繼續 {用戶意圖}。
```

## 💡 執行流程總結

1. **解析參數** → 識別模式和意圖
2. **分析環境** → 收集專案狀態資訊
3. **生成檔名** → 基於時間戳、模式、意圖
4. **建立 YAML** → 填充所有變數和內容
5. **執行模式** → 根據參數選擇輸出方式
6. **提供重啟指引** → 生成標準化的重啟 prompt

**關鍵特性**：
- 🎯 **智能意圖識別**：自動分類用戶工作意圖
- 📁 **結構化儲存**：統一的 YAML 格式和檔案命名
- 🔄 **無縫重啟**：標準化的上下文恢復流程
- ⚡ **多模式支援**：預覽、重啟、詳細、精簡模式
- 🛠️ **環境感知**：自動識別專案類型和狀態