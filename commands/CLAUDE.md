# Slash Commands 技術規範

> **AI 重要提示**: 本專案採用符號連結架構將 Git 管理的 slash commands 整合到 Claude Code 系統中。個人層級的 `~/.claude/commands` 符號連結指向 `/Users/ctai/Github/ai-rules/commands`，實現版本控制、跨專案共享和即時更新。

## 系統架構

Slash Commands 是 Claude Code 的可擴展命令系統，透過解析 Git 管理的 Markdown 檔案定義可執行命令。AI 系統使用 `SlashCommand` 工具執行命令，所有命令檔案都納入版本控制並通過符號連結共享。

### 核心執行機制
```python
# AI 調用 slash command 的標準方式
SlashCommand("/command-name [參數]")
```

### 發現機制優先級
Claude Code 按以下順序搜尋命令檔案：
1. **專案層級**: `.claude/commands/` (最高優先級)
2. **個人層級**: `~/.claude/commands/` (最低優先級)

### Git 管理的符號連結架構

#### 架構設計
```bash
# 符號連結配置（個人層級 → Git 管理的專案層級）
~/.claude/commands -> /Users/ctai/Github/ai-rules/commands
```

#### 技術優勢
- **版本控制**: 所有 slash commands 納入 Git 管理
- **跨專案共享**: 個人層級符號連結使所有專案都能使用相同命令
- **即時更新**: Git 中的修改立即生效於所有 Claude Code 實例
- **集中維護**: 避免重複配置和版本不一致問題

#### 建立符號連結
```bash
# 檢查現有連結狀況
ls -la ~/.claude/commands

# 建立新的符號連結（如果不存在）
ln -s /Users/ctai/Github/ai-rules/commands ~/.claude/commands

# 驗證連結正確性
readlink ~/.claude/commands
ls ~/.claude/commands/
```

#### 當前專案命令清單
```bash
# ai-rules 專案中的自定義 commands
ls -la /Users/ctai/Github/ai-rules/commands/
```

包含以下自定義命令：
- `/analysis-plan` - 技術分析計劃生成
- `/code-review` - 程式碼審查和品質檢查
- `/claude:clean` - 清理 CLAUDE.md 中不必要的元資訊
- `/claude:distill` - 蒸餾 CLAUDE.md，提煉核心精華
- `/claude:sync` - 檢查 CLAUDE.md 與程式碼的同步性
- `/commit-message` - Git 提交訊息生成
- `/design-plan` - 設計計劃制定
- `/design2prompt` - 設計轉提示詞轉換
- `/distill-spec` - 規格蒸餾和提煉
- `/doc-hierarchy` - 通用 CLAUDE.md 階層文檔生成器
- `/doc-quality-checker` - 文檔品質檢查
- `/docs-manager` - 文檔管理和整理
- `/error-diagnose` - 錯誤診斷和解決方案
- `/explain` - 技術概念、架構設計或流程解釋
- `/execution-plan` - 執行計劃和任務分解
- `/lessons` - 經驗教訓提取和知識蒸餾
- `/lint-fix` - 執行 ruff 和 mypy 檢查並自動修正問題
- `/milestone` - 對話里程碑記錄和重啟管理
- `/parallel-task` - 智能並行任務協調器
- `/story-design` - 用戶故事和功能設計
- `/worktree/*` - Git Worktree 管理命令集（子目錄結構）

### 命令載入和執行流程
```
AI 調用 SlashCommand("/command args")
    ↓
系統按優先級搜尋：
1. 專案層級：.claude/commands/command.md
2. 個人層級：~/.claude/commands/command.md
   ↓
符號連結解析：~/.claude/commands -> /Users/ctai/Github/ai-rules/commands
   ↓
實際載入：/Users/ctai/Github/ai-rules/commands/command.md
   ↓
解析 YAML frontmatter 配置
   ↓
驗證 allowed-tools 和權限
   ↓
執行命令內容，替換 $ARGUMENTS 和位置參數
   ↓
應用 disable-model-invocation 設定
   ↓
返回執行結果給 AI
```

## 當前專案 Commands 參考

> **AI 使用指南**: 以下是本專案中可立即使用的 22+ 個自定義 slash commands，所有命令都透過符號連結架構實現 Git 版本控制和跨專案共享。

### CLAUDE.md 專用命令
- `/claude:clean` - 清理 CLAUDE.md 元資訊（版本、日期等）
- `/claude:distill` - 蒸餾精簡 CLAUDE.md，提煉核心精華
- `/claude:sync` - 檢查 CLAUDE.md 與程式碼同步性（支援 --clean, --all）

### 核心系統命令
- `/explain` - 技術概念、架構設計或流程解釋
- `/milestone` - 對話里程碑記錄和重啟管理
- `/parallel-task` - 智能並行任務協調器
- `/doc-hierarchy` - 通用 CLAUDE.md 階層文檔生成器

### 開發流程命令
- `/analysis-plan` - 技術分析計劃生成
- `/code-review` - 程式碼審查和品質檢查
- `/design-plan` - 軟體設計計劃制定
- `/execution-plan` - 執行計劃和任務分解
- `/lint-fix` - ruff 和 mypy 自動修正

### Git 工作流程命令
- `/commit-message` - Git 提交訊息生成
- `/worktree:create` - 建立新的 Git Worktree
- `/worktree:status` - 列出所有 Git Worktrees 狀態
- `/worktree:cleanup` - 智能清理 Git Worktrees
- `/worktree:done` - 合併 Git Worktree 分支並清理

### 文檔管理命令
- `/doc-quality-checker` - 文檔品質檢查
- `/docs-manager` - 文檔管理和整理
- `/distill-spec` - 規格蒸餾和提煉

### 錯誤處理和診斷
- `/error-diagnose` - 錯誤診斷和解決方案
- `/lessons` - 經驗教訓提取和知識蒸餾

### 設計和規劃工具
- `/story-design` - 用戶故事和功能設計
- `/design2prompt` - 設計轉提示詞轉換

### Claude Code 內建命令參考
- `/agents:config-manager` - Agent 配置管理器
- MCP 整合命令：`/mcp__server-name__prompt-name`

## 基本語法規範

### AI 調用語法
```python
# 標準命令調用
SlashCommand("/command-name [參數]")

# 帶選項的命令調用
SlashCommand("/command --option value")

# 命名空間命令
SlashCommand("/git:commit 'commit message'")
SlashCommand("/mcp__server__prompt [args]")
```

### 參數替換機制
```markdown
---
description: "參數處理範例"
---

# 完整參數捕獲 ($ARGUMENTS)
處理用戶輸入：$ARGUMENTS

# 位置參數 ($1, $2, $3...)
檔案：$1
行號：$2
操作：$3
```

### 命名空間技術規範
- **層級結構**: `/category:command` (如 `/git:commit`)
- **MCP 整合**: `/mcp__server-name__prompt-name`
- **巢狀結構**: 支援多層級命名空間

## Frontmatter 配置標準

### 必要配置參數
```yaml
---
description: "簡短明確的功能描述"
usage: "/command [參數] [選項]"
argument-hint: "參數提示信息"
allowed-tools: ["Bash", "Read", "Write"]
model: "sonnet"
disable-model-invocation: false
---
```

### 完整配置範例
```yaml
---
description: "執行程式碼性能分析和優化建議"
usage: "/performance [檔案路徑] [分析類型]"
argument-hint: "檔案路徑和可選的分析類型"
allowed-tools: ["Read", "Grep", "Bash"]
model: "sonnet"
disable-model-invocation: false
permission-mode: "default"
---
```

### 參數詳細說明

- `description`: 命令功能的簡潔描述，用於命令列表顯示
- `usage`: 命令使用語法範例
- `argument-hint`: 參數提示信息，指導用戶輸入格式
- `allowed-tools`: 該命令允許使用的工具列表
- `model`: 執行時使用的 Claude 模型 (sonnet/opus/haiku)
- `disable-model-invocation`: 是否禁用模型調用
- `permission-mode`: 檔案操作權限級別 (default/acceptEdits/bypassPermissions)

## 參數處理機制

### 參數捕獲和替換
```markdown
---
description: "參數處理技術範例"
---

# $ARGUMENTS 捕獲完整用戶輸入
用戶輸入內容：$ARGUMENTS

# $1, $2, $3 位置參數處理
第一參數：$1
第二參數：$2
第三參數：$3

# 參數組合使用
分析檔案 $1 的第 $2 行，執行 $3 操作
```

### 參數驗證技術
```markdown
---
description: "參數驗證和錯誤處理"
allowed-tools: ["Bash"]
---

# Bash 參數驗證
if [ -z "$1" ]; then
    echo "錯誤：缺少必要參數"
    exit 1
fi

# 參數格式檢查
if [[ ! "$1" =~ ^[a-zA-Z0-9_\-\.]+$ ]]; then
    echo "錯誤：參數格式無效"
    exit 1
fi

echo "參數驗證通過：$1"
```

### 條件參數處理
```markdown
---
description: "條件式參數處理"
---

# 根據參數執行不同邏輯
case "$1" in
    --dry-run)
        echo "預覽模式：$2"
        # 預覽邏輯
        ;;
    --verbose)
        echo "詳細模式：處理 $2"
        # 詳細處理邏輯
        ;;
    --force)
        echo "強制模式：$2"
        # 強制執行邏輯
        ;;
    *)
        echo "標準模式：$1"
        # 預設處理邏輯
        ;;
esac
```

## 工具調用與執行模式

### 工具權限配置
```yaml
---
# 唯讀權限
allowed-tools: ["Read"]

# 檔案操作權限
allowed-tools: ["Read", "Write", "Edit"]

# 開發權限
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep"]
permission-mode: "acceptEdits"

# 完整系統權限
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Task"]
permission-mode: "bypassPermissions"
---
```

### Bash 執行技術
```markdown
---
description: "系統命令執行"
allowed-tools: ["Bash"]
---

# 直接命令執行
echo "處理參數：$1"

# 條件式命令執行
if [ -f "$1" ]; then
    echo "檔案存在：$1"
    ls -la "$1"
else
    echo "檔案不存在：$1"
fi

# 管道和重定向
grep -n "error" "$1" | head -10
```

### 檔案操作技術
```markdown
---
description: "檔案內容分析和處理"
allowed-tools: ["Read", "Write"]
---

# 檔案內容讀取和分析
# AI 會自動使用 Read 工具處理檔案引用
請分析檔案 $1 的以下方面：
1. 程式碼結構和架構
2. 潛在的效能問題
3. 安全性考量
4. 改進建議
```

### 模型調用控制
```yaml
---
# 禁用模型調用 - 純工具執行
disable-model-invocation: true

# 啟用模型調用 - 允許 AI 處理
disable-model-invocation: false

# 預設值（通常為 false）
# disable-model-invocation: false
---
```

## 與 Agents 整合

### Agent 調用技術
```markdown
---
description: "觸發專門 Agent 處理"
allowed-tools: ["Task"]
---

# 單一 Agent 調用
Task("分析以下程式碼：$ARGUMENTS", subagent_type="code-reviewer")

# 指定模型調用
Task("複雜分析任務", subagent_type="data-analyst", model="sonnet")
```

### 並行 Agent 協調
```markdown
---
description: "多 Agent 並行分析"
allowed-tools: ["Task"]
---

# 同時啟動多個 Agent（AI 會並行執行）
Task("安全漏洞分析", subagent_type="security-expert")
Task("效能瓶頸識別", subagent_type="performance-analyzer")
Task("程式碼品質評估", subagent_type="code-reviewer")
Task("文檔完整性檢查", subagent_type="doc-validator")
```

### Agent 結果整合
```markdown
---
description: "分階段 Agent 處理流程"
allowed-tools: ["Task"]
---

# 第一階段：數據收集和分析
Task("收集和分析 $1 的技術債務", subagent_type="debt-analyzer")

# 第二階段：基於分析結果的優化建議
# AI 會根據第一階段結果自動調整第二階段任務
Task("基於技術債務分析提供重構建議", subagent_type="architect-expert")
```

### 與 Skills 協調策略
```markdown
---
description: "Commands 與 Skills 協調使用"
---

# 簡單任務：使用 slash commands
/parallel-task "基礎程式碼審查和測試"

# 複雜決策：使用 Skills
# AI 會自動判斷何時使用 Skill 而非 Command
skill: parallel-processing

# 混合使用：Command 觸發，Skill 處理
Trigger complex analysis workflow...
```

### MCP 整合技術
```markdown
---
description: "MCP 伺服器整合"
allowed-tools: ["Task"]  # 如果 MCP 服務作為 Agent 提供
---

# MCP 伺服器命令調用
# 格式：/mcp__server-name__prompt-name
# 系統會自動路由到對應的 MCP 服務

# 在命令中引用 MCP 結果
分析來自 MCP 資料庫的查詢結果：$ARGUMENTS
```

## 高級功能

### 條件執行邏輯
```markdown
---
description: "條件分支處理"
---

# 檢查檔案是否存在
if [ -f "$1" ]; then
    echo "檔案存在，執行分析..."
    # 分析邏輯
else
    echo "檔案不存在，建立新檔案..."
    # 建立邏輯
fi
```

### 迴圈處理機制
```markdown
---
description: "批次檔案處理"
---

for file in $1/*.py; do
    echo "處理檔案: $file"
    # 個別檔案處理邏輯
done
```

### 錯誤處理機制
```markdown
---
description: "錯誤處理和恢復"
---

set -e  # 遇到錯誤立即退出

trap 'echo "命令執行失敗，正在清理..."; cleanup_function' ERR

# 主要執行邏輯
main_function "$@"

echo "命令執行成功完成"
```

### 狀態管理機制
```markdown
---
description: "執行狀態跟蹤"
---

# 狀態檔案管理
STATE_FILE="/tmp/.command_state"

# 記錄執行狀態
echo "STARTED: $(date)" > $STATE_FILE

# 執行主要邏輯
main_logic "$@"

# 更新完成狀態
echo "COMPLETED: $(date)" >> $STATE_FILE
```

## 故障排除與驗證

### 常見故障模式

#### Command 載入失敗
**症狀**: `Command not found` 錯誤
**診斷步驟**:
```bash
# 檢查符號連結狀態
ls -la ~/.claude/commands
readlink ~/.claude/commands

# 檢查 Git 管理的實際目錄
ls -la /Users/ctai/Github/ai-rules/commands/

# 檢查特定命令檔案
ls /Users/ctai/Github/ai-rules/commands/your-command.md
cat /Users/ctai/Github/ai-rules/commands/your-command.md

# 驗證 YAML 語法
head -20 /Users/ctai/Github/ai-rules/commands/your-command.md
```

**解決方案**:
- **符號連結問題**：重建符號連結 `ln -sfn /Users/ctai/Github/ai-rules/commands ~/.claude/commands`
- **檔案權限**：確保檔案可讀 `chmod 644 /Users/ctai/Github/ai-rules/commands/your-command.md`
- **YAML 語法**：驗證 frontmatter 格式正確性
- **檔案編碼**：確保為 UTF-8 編碼

#### 符號連結相關問題
**症狀**: 命令存在但無法載入，或載入舊版本
**診斷步驟**:
```bash
# 檢查連結是否有效
test -L ~/.claude/commands && echo "符號連結存在" || echo "符號連結缺失"

# 檢查連結目標是否存在
test -d /Users/ctai/Github/ai-rules/commands && echo "目標目錄存在" || echo "目標目錄不存在"

# 檢查連結是否正確
if [ "$(readlink ~/.claude/commands)" = "/Users/ctai/Github/ai-rules/commands" ]; then
    echo "符號連結正確"
else
    echo "符號連結錯誤，需要重建"
fi
```

**解決方案**:
```bash
# 移除舊連結並重建正確連結
rm -f ~/.claude/commands
ln -s /Users/ctai/Github/ai-rules/commands ~/.claude/commands

# 驗證重建結果
ls -la ~/.claude/commands
ls ~/.claude/commands/ | head -5
```

#### 參數傳遞失敗
**症狀**: 參數無法正確傳遞或替換
**診斷步驟**:
```bash
# 測試參數捕獲
/test-command "測試參數內容"

# 檢查位置參數
/test-command arg1 arg2 arg3
```

**解決方案**:
- 使用 `$ARGUMENTS` 捕獲完整參數
- 驗證位置參數語法 (`$1`, `$2` 等)
- 檢查參數中的特殊字符轉義

#### 工具權限限制
**症狀**: `Permission denied` 或工具調用失敗
**診斷步驟**:
```yaml
# 檢查 allowed-tools 配置
allowed-tools: ["Read", "Write"]  # 確保包含必要工具

# 檢查 permission-mode 設定
permission-mode: "acceptEdits"  # 必要時提升權限
```

#### Frontmatter 語法錯誤
**症狀**: 命令檔案無法正確解析
**常見錯誤**:
```yaml
# ❌ 錯誤：缺少結束標記
---
description: "測試命令"
allowed-tools: ["Read"]

# ❌ 錯誤：引號不匹配
description: "未閉合的引號

# ✅ 正確：完整格式
---
description: "正確的命令格式"
allowed-tools: ["Read", "Write"]
---
```

### AI 驗證測試流程

#### 命令載入驗證
```python
# AI 檢查命令可用性
SlashCommand("/test-command --verify")

# 驗證參數傳遞
SlashCommand("/test-command '參數測試'")
SlashCommand("/test-command arg1 arg2 arg3")

# 測試錯誤處理
SlashCommand("/test-command")  # 無參數測試
```

#### 系統整合驗證
```markdown
# AI 自檢查清單（符號連結架構）
1. 確認符號連結有效：readlink ~/.claude/commands
2. 驗證實際檔案存在：ls /Users/ctai/Github/ai-rules/commands/
3. 檢查命令檔案權限：stat /Users/ctai/Github/ai-rules/commands/your-command.md
4. 驗證 YAML frontmatter 語法正確性
5. 檢查 allowed-tools 配置與功能匹配
6. 測試參數替換機制
7. 驗證與現有 commands 無命名衝突
8. 確認 Git 追蹤狀態：git status /Users/ctai/Github/ai-rules/commands/
```

#### 效能和可靠性測試
```python
# 大型參數處理測試
large_content = "測試內容" * 1000
SlashCommand(f"/test-command '{large_content}'")

# 並行執行測試（AI 自動並行）
SlashCommand("/test-command 'concurrent-test-1'")
SlashCommand("/test-command 'concurrent-test-2'")
```

### AI 開發檢查清單

#### 命令結構驗證
- [x] YAML frontmatter 語法完全正確
- [x] 必要配置參數完整且準確
- [x] 命令描述對 AI 清晰明確
- [x] 參數提示信息對 AI 有用

#### 功能完整性驗證
- [x] 參數捕獲和替換機制正確
- [x] 工具調用權限配置合理
- [x] 錯誤處理機制完善
- [x] 邊界情況處理妥當

#### 系統整合驗證
- [x] 與現有 slash commands 無衝突
- [x] 命名空間使用符合規範
- [x] 與 Agents/Skills 協調機制清晰
- [x] MCP 整合技術正確實施

#### AI 友好性驗證
- [x] 技術術語精準無歧義
- [x] 範例程式碼可直接執行
- [x] 錯誤訊息對 AI 清晰
- [x] 整體設計符合 AI 使用模式