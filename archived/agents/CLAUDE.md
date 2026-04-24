# Claude Code Agents 開發參考

> **AI 重要提示**: 本專案採用符號連結架構將 Git 管理的 agents 整合到 Claude Code 系統中。個人層級的 `~/.claude/agents` 符號連結指向 `/Users/ctai/Github/ai-rules/agents`，實現版本控制、跨專案共享和即時更新。

## 系統架構概覽

Subagents 是獨立的 AI 執行實例，具有隔離的上下文視窗和專門化的系統提示。當主對話需要處理特定任務類型時，會自動或手動委派給適合的 agent。所有 agents 都納入 Git 版本控制管理。

### 核心特性
- **上下文隔離**: 每个 agent 維持獨立對話上下文
- **專業化處理**: 針對特定任務類型優化
- **精確工具控制**: 權限和工具的細粒度管理
- **跨會話重用**: 在不同對話中重複使用相同 agent

## Agent 配置規範

### 檔案結構
每個 agent 必須使用以下標準結構：

```yaml
---
name: agent-identifier
description: 觸發條件和用途描述
tools: Read, Write, Grep, Bash
model: sonnet
permissionMode: default
---

<系統提示內容>
```

### 必要配置參數
- `name`: Agent 識別符（用於 Task.subagent_type 調用）
- `description`: 智能選擇的觸發條件描述
- `tools`: 允許使用的工具列表（Read, Write, Grep, Bash）
- `model`: 使用的 Claude 模型（sonnet/opus/haiku/inherit）
- `permissionMode`: 檔案操作權限級別（default/acceptEdits/bypassPermissions）

### 命名規範
- 必須使用小寫字母
- 使用連字符分隔單詞
- 範例：`milestone-recorder.md`、`code-reviewer.md`

## Agent 載入機制

### 載入優先級
Claude Code 按以下優先級搜尋和載入 agents：

1. `.claude/agents/` - 專案層級（最高優先級）
2. `--agents` CLI 參數定義（中等優先級）
3. `~/.claude/agents/` - 用戶層級（最低優先級）

### Git 管理的符號連結架構

#### 架構設計
```bash
# 符號連結配置（個人層級 → Git 管理的專案層級）
~/.claude/agents -> /Users/ctai/Github/ai-rules/agents
```

#### 技術優勢
- **版本控制**: 所有 agents 納入 Git 管理
- **跨專案共享**: 個人層級符號連結使所有專案都能使用相同 agents
- **即時更新**: Git 中的修改立即生效於所有 Claude Code 實例
- **集中維護**: 避免重複配置和版本不一致問題

#### 符號連結管理
```bash
# 檢查現有連結狀況
ls -la ~/.claude/agents
readlink ~/.claude/agents

# 建立符號連結（如果不存在）
ln -sfn /Users/ctai/Github/ai-rules/agents ~/.claude/agents

# 驗證連結正確性
ls ~/.claude/agents/
```

#### 當前專案 Agents 清單
```bash
# ai-rules 專案中的自定義 agents
ls -la /Users/ctai/Github/ai-rules/agents/
```

包含以下自定義 agents：
- `milestone-recorder` (5071 bytes) - 對話里程碑記錄和重啟管理
- `context-analyzer` (4275 bytes) - 上下文和背景脈絡分析
- `structure-analyzer` (3677 bytes) - 檔案結構和依賴關係分析
- `verification-expert` (4166 bytes) - 程式碼驗證和品質測試
- `report-coordinator` (4382 bytes) - 報告整合和協調管理
- `content-analyzer` (3448 bytes) - 內容品質分析和評估
- `content-processor` (4439 bytes) - 內容蒸餾和整合處理
- `visualization-specialist` (5290 bytes) - ASCII 和 Mermaid 圖表生成

## Agent 調用介面

### 基本調用
```python
Task("任務描述", subagent_type="agent-name")
```

### 並行執行
```python
Task("安全分析", subagent_type="security-expert")
Task("效能評估", subagent_type="performance-analyzer")
Task("文檔驗證", subagent_type="doc-validator")
```

### 狀態驗證
```python
# 測試 agent 可用性
Task("功能測試", subagent_type="agent-name")

# 檔案系統檢查
ls ~/.claude/agents/
head -10 ~/.claude/agents/agent-name.md
```

## 進階執行模式

### Agent 鏈接
複雜工作流程使用多個 agents 串聯執行：

```python
# 第一階段：需求分析
Task("分析用戶需求", subagent_type="requirements-analyzer")

# 第二階段：架構設計
Task("設計系統架構", subagent_type="architecture-expert")

# 第三階段：實作開發
Task("生成實現代碼", subagent_type="code-generator")
```

### 會話恢復
使用 session ID 繼續之前的 agent 對話：

```python
Task("繼續分析", subagent_type="data-analyst", resume="session-id-123")
```

### 插件整合
來自插件的 agents 可直接調用：

```python
Task("資料庫優化", subagent_type="db-optimizer")  # 插件提供的 agent
```

## 內建 Agents 參考

### General-purpose Agent
- **技術規格**: 複雜多步驟任務，廣泛研究和分析
- **工具集**: Read, Write, Grep, Glob, Bash
- **適用場景**: 代碼重構、多檔案分析、跨專案整合

### Explore Agent
- **技術規格**: 快速代碼庫探索，唯讀模式優化
- **工具集**: Read, Glob, Grep
- **適用場景**: 結構探索、資訊搜索、文檔分析

### Plan Agent
- **技術規格**: 計畫模式下的代碼庫研究
- **工具集**: Read, Glob, Grep, Bash
- **觸發條件**: 進入 plan 模式時自動啟動
- **適用場景**: 功能設計、架構分析、實作規劃

### Test-generator Agent
- **技術規格**: 自動測試用例生成
- **觸發條件**: 程式碼修改後自動觸發
- **適用場景**: 單元測試、集成測試、覆蓋率提升

### Skills-based Agents
- **parallel-processing**: 智能並行決策和成本效益分析
- **content-analyzer**: 內容品質分析和評估
- **visualization-specialist**: ASCII 和 Mermaid 圖表生成

### 本專案 Agents 技術規格

> **AI 使用指南**: 以下是本專案中可立即使用的 8 個自定義 agents，所有 agents 都透過符號連結架構實現 Git 版本控制和跨專案共享。

#### 核心分析 Agents
- **milestone-recorder** (5071 bytes) - 對話里程碑記錄和重啟管理
  - 專門處理對話狀態保存、重啟指引生成
  - 支援多種執行模式：`--dry-run`, `--restart-only`, `--verbose`

- **context-analyzer** (4275 bytes) - 上下文和背景脈絡分析
  - 深度分析對話歷史和項目背景
  - 識別關鍵決策點和技術選型

#### 結構化處理 Agents
- **structure-analyzer** (3677 bytes) - 檔案結構和依賴關係分析
  - 程式碼架構分析和模組關係圖譜
  - 依賴性檢測和重構建議

- **verification-expert** (4166 bytes) - 程式碼驗證和品質測試
  - 程式碼品質評估和最佳實踐檢查
  - 安全性掃描和效能分析

#### 內容處理 Agents
- **content-analyzer** (3448 bytes) - 內容品質分析和評估
  - 文檔品質評分和改進建議
  - 內容一致性檢查

- **content-processor** (4439 bytes) - 內容蒸餾和整合處理
  - 技術文檔蒸餾和知識提取
  - 多源資訊整合和結構化

#### 協調和可視化 Agents
- **report-coordinator** (4382 bytes) - 報告整合和協調管理
  - 多來源報告整合和優先級排序
  - 跨 agent 結果協調

- **visualization-specialist** (5290 bytes) - ASCII 和 Mermaid 圖表生成
  - 技術圖表生成和視覺化處理
  - 支援 Dark/Light 模式相容性

## Agent 開發規範

### 設計原則
1. **單一職責**: 每個 agent 專注特定任務領域
2. **明確指令**: 系統提示包含詳細執行步驟
3. **工具最小化**: 只開放必要工具，提高安全性
4. **動態響應**: 避免硬編碼，根據輸入適應輸出

### 系統提示設計標準

#### 結構化模式
```markdown
<專家角色定義和職責範圍>

## 執行步驟
### 1. <具體步驟名稱>
- 詳細操作說明和命令語法
- 處理邏輯和決策規則

### 2. <後續步驟名稱>
- 延續處理流程

## 關鍵約束
- **禁止事項**: 明確列出不允許的操作
- **必要要求**: 必須遵守的核心原則

## 輸出規範
- 格式要求：指定輸出格式和結構
- 內容要求：必須包含的資訊要素
- 品質標準：完整性和準確性要求
```

#### 動態內容生成約束
```markdown
## 關鍵執行約束
**嚴格禁止硬編碼輸出內容！**必須根據實際輸入動態生成。

### 動態生成流程
1. 解析輸入參數和上下文
2. 檢查系統環境狀態
3. 識別關鍵詞和用戶意圖
4. 生成對應的具體建議
5. 適應輸出格式要求
```

### 效能最佳實踐
- **提示長度**: 保持 < 2000 字元以提高響應速度
- **工具調用優化**: 批次處理相似操作，減少調用次數
- **上下文管理**: 避免不必要的重複分析和資源浪費

## 故障排除與驗證

### 常見故障模式

#### 無回應狀況
- **症狀**: Task 執行後無任何輸出
- **可能原因**:
  - 系統提示過於複雜 (>2000 字元)
  - YAML frontmatter 語法錯誤
  - 包含未定義的函數或引用
- **解決方案**: 簡化系統提示、驗證 YAML 語法、移除複雜代碼範例

#### 載入失敗
- **症狀**: `Agent type 'xxx' not found`
- **診斷檢查**:
  ```bash
  # 檢查符號連結狀態
  ls -la ~/.claude/agents
  readlink ~/.claude/agents

  # 檢查 Git 管理的實際目錄
  ls -la /Users/ctai/Github/ai-rules/agents/

  # 檔案存在驗證
  ls /Users/ctai/Github/ai-rules/agents/agent-name.md

  # 命名規範檢查（小寫+連字符）
  # ✅ 正確: milestone-recorder.md
  # ❌ 錯誤: MilestoneRecorder.md

  # YAML 格式驗證
  head -10 /Users/ctai/Github/ai-rules/agents/agent-name.md
  ```

**解決方案**:
- **符號連結問題**：重建符號連結 `ln -sfn /Users/ctai/Github/ai-rules/agents ~/.claude/agents`
- **檔案權限**：確保檔案可讀 `chmod 644 /Users/ctai/Github/ai-rules/agents/agent-name.md`
- **YAML 語法**：驗證 frontmatter 格式正確性
- **檔案編碼**：確保為 UTF-8 編碼

#### 符號連結相關問題
- **症狀**: Agent 存在但無法載入，或載入舊版本
- **診斷步驟**:
  ```bash
  # 檢查連結是否有效
  test -L ~/.claude/agents && echo "符號連結存在" || echo "符號連結缺失"

  # 檢查連結目標是否存在
  test -d /Users/ctai/Github/ai-rules/agents && echo "目標目錄存在" || echo "目標目錄不存在"

  # 檢查連結是否正確
  if [ "$(readlink ~/.claude/agents)" = "/Users/ctai/Github/ai-rules/agents" ]; then
      echo "符號連結正確"
  else
      echo "符號連結錯誤，需要重建"
  fi
  ```

**解決方案**:
  ```bash
  # 移除舊連結並重建正確連結
  rm -f ~/.claude/agents
  ln -s /Users/ctai/Github/ai-rules/agents ~/.claude/agents

  # 驗證重建結果
  ls -la ~/.claude/agents
  ls ~/.claude/agents/ | head -5
  ```

#### 權限限制問題
- **症狀**: 無法執行檔案操作
- **技術修正**:
  ```yaml
  permissionMode: acceptEdits
  tools: Read, Write, Bash
  ```

#### 硬編碼輸出
- **症狀**: Agent 輸出固定重複內容
- **系統提示修正**:
  ```markdown
  ## 核心執行約束
  **絕對禁止硬編碼輸出！**必須根據輸入動態生成響應。
  ```

### 驗證測試流程
```python
# 基本功能驗證
Task("基本功能測試", subagent_type="agent-name")

# 參數處理測試
Task("參數測試: --dry-run 驗證模式", subagent_type="agent-name")

# 系統檔案驗證
bash -c "head -20 ~/.claude/agents/agent-name.md"
```

## 開發檢查清單

### 配置驗證
- [ ] YAML frontmatter 語法完全正確
- [ ] `name` 使用小寫連字符，無特殊符號
- [ ] `tools` 清單必要且無冗餘
- [ ] `description` 清楚描述觸發條件
- [ ] 符號連結指向正確的 Git 管理路徑

### 系統提示驗證
- [ ] 執行步驟明確且可操作
- [ ] 包含關鍵約束和禁止事項
- [ ] 總長度控制在 2000 字元以內
- [ ] 動態生成要求明確且強制
- [ ] 輸出格式要求具體

### 功能測試
- [ ] 基本功能運行正常
- [ ] 無任何硬編碼輸出
- [ ] 錯誤處理機制完善
- [ ] 邊界情況處理正確

### 系統整合驗證
```bash
# 符號連結狀態檢查
readlink ~/.claude/agents
test -L ~/.claude/agents && echo "符號連結正確" || echo "符號連結異常"

# Agent 載入驗證
ls ~/.claude/agents/ && echo "Agents 載入成功" || echo "載入失敗"

# 實際檔案存在性驗證
ls /Users/ctai/Github/ai-rules/agents/ && echo "Git 管理目錄存在" || echo "Git 目錄異常"

# 語法一致性驗證（檢查實際檔案）
find /Users/ctai/Github/ai-rules/agents/ -name "*.md" -exec echo "檢查: {}" \; -exec head -15 {} \;

# Git 追蹤狀態檢查
git status /Users/ctai/Github/ai-rules/agents/
```

### AI 開發檢查清單（符號連結架構）

#### 配置驗證
- [x] YAML frontmatter 語法完全正確
- [x] `name` 使用小寫連字符，無特殊符號
- [x] `tools` 清單必要且無冗餘
- [x] `description` 清楚描述觸發條件
- [x] 符號連結指向正確的 Git 管理路徑

#### 系統提示驗證
- [x] 執行步驟明確且可操作
- [x] 包含關鍵約束和禁止事項
- [x] 總長度控制在 2000 字元以內
- [x] 動態生成要求明確且強制
- [x] 輸出格式要求具體

#### 功能測試
- [x] 基本功能運行正常
- [x] 無任何硬編碼輸出
- [x] 錯誤處理機制完善
- [x] 邊界情況處理正確

#### 符號連結架構驗證
- [x] 符號連結有效且指向正確目標
- [x] Git 管理的 agents 可正常載入
- [x] 修改即時生效於所有專案
- [x] 與 commands 符號連結架構一致