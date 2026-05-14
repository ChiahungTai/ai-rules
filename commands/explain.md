---
description: "解釋技術概念、架構設計或流程。可指定 @目錄或 @檔案讓 AI 先讀再解釋，支援 console（即時）和 md（寫檔）兩種輸出模式。"
when_to_use: "Explain technical concepts, architecture, or processes. Supports console (ASCII) and md (Mermaid) output. Use with @dir or @file for code-based explanations."
usage: "/explain [console|md] <主題|@目錄|@檔案1 @檔案2 ...>"
---

# 智能解釋系統

## 🎯 輸出模式說明

### Console 模式（預設）
- **圖表類型**: ASCII 圖表（適合終端機顯示）
- **內容風格**: 精簡扼要，適合快速理解
- **適用場景**: 即時討論、快速查詢

### MD 模式
- **圖表類型**: Mermaid 圖表（使用 `skill: "mermaid"`）
- **內容風格**: 詳盡完整，適合文檔記錄
- **適用場景**: 深度分析、知識沉澱

## 核心能力

### 單一主題解釋
- **概念解析**: 技術概念、架構設計、流程說明
- **視覺化圖表**: ASCII 或 Mermaid 圖表輔助理解

### 批次檔案分析
- **目錄掃描**: 自動分析整個目錄結構和內容
- **智能並行**: 使用 parallel-processing skill 自動判斷並行可行性
- **智能關聯**: 自動發現檔案間的關聯性和依賴關係

### 深度分析
根據內容類型套用對應分析框架（論文/文章/程式碼）。詳見 [explain-deep-analysis.md](./claude/_common/explain-deep-analysis.md)。

## 使用方式

```bash
# 單一主題解釋（預設 Console 模式）
/explain 微服務架構
/explain md Kubernetes 叢集管理     # 生成: ai-analysis/reports/kubernetes-叢集管理-analysis.md

# 目錄分析（自動檢測檔案數量）
/explain @src/components/          # Console 輸出
/explain md @docs/                 # 生成: ai-analysis/reports/docs-analysis.md

# 多檔案分析（Skill 智能決策並行處理）
/explain @file1.js @file2.js @config.json
/explain md @src/ @tests/          # 生成: ai-analysis/reports/src-tests-analysis.md

# 自定義檔名
/explain md @architecture/ --output "系統架構分析.md"
/explain md @api/ --output ai-analysis/reports/api-analysis.md

# 進階分析
/explain md 深度分析整個專案架構 @src/
/explain md 論文分析：@paper1.pdf @paper2.pdf --output "論文對比分析.md"
```

更多使用範例見 [explain-examples.md](./claude/_common/explain-examples.md)。

---

## 🖥️ Console 模式規範

### 輸出原則
- **精簡為上**: 重點突出，刪除冗餘
- **ASCII 圖表**: 使用文字符號繪製
- **快速掃讀**: 3-5 個章節，每節 3-5 點
- **即時可用**: 無需額外工具檢視

### ASCII 圖表工具集
```bash
# 基本元件
┌─┐ └─┘ │ │ ├─┤ ┬─┬
│ │ │ │ │ │ │ │ │ │
└─┘ └─┘ └─┘ └─┘ ┴─┴

# 流程箭頭
→ ↓ ↑ ← ↔ ⇄
─── ⇒ ⇐ ⟷

# 標註符號
【】『』※★◆
```

### Console 範例結構
```
【核心概念】
一行定義 + ASCII 簡圖

【架構流程】
┌─┐ → ┌─┐ → ┌─┐
│A│   │B│   │C│
└─┘   └─┘   └─┘

【關鍵要點】
• 要點一：簡要說明
• 要點二：簡要說明
• 要點三：簡要說明

【實作建議】
1. 步驟一
2. 步驟二
3. 步驟三
```

---

## 📄 MD 檔案模式規範

### 輸出原則
- **詳盡完整**: 深度分析，背景脈絡
- **專業圖表**: 使用 `skill: "mermaid"` 生成 Dark/Light 模式相容圖表
- **層次結構**: 多級標題，詳細展開
- **文檔導向**: 適合長期保存和分享

### 圖表生成規範

**必須使用** `skill: "mermaid"` 生成所有圖表。禁止手動編寫 Mermaid 語法。

支援的圖表類型：流程圖、序列圖、類圖、甘特圖、架構圖、狀態圖。

### MD 範例結構
```markdown
# 主題：[主題名稱]

## 一、概念背景
### 問題定義
### 發展歷程
### 核心價值

## 二、技術架構
### 整體架構圖
skill: "mermaid"
# 生成系統整體架構圖，包含各組件關係

### 核心組件分析
#### 組件一：功能與職責
#### 組件二：介面設計
#### 組件三：資料流程

## 三、實作流程
### 階段一：規劃設計
skill: "mermaid"
# 生成開發流程時序圖

### 階段二：開發實作
### 階段三：測試部署

## 四、最佳實踐
### 設計原則
### 常見陷阱
### 優化策略

## 五、案例分析
### 成功案例
skill: "mermaid"
# 生成案例對比分析圖

### 失敗教訓
### 經驗總結
```

---

## 智能內容調整

### 內容深度差異

| 層次 | Console 模式 | MD 模式 |
|------|-------------|---------|
| **概念介紹** | 1-2 句話定義 | 完整背景脈絡 |
| **技術細節** | 重點特色 | 完整技術規格 |
| **流程說明** | 主要步驟 | 詳細執行流程 |
| **案例分析** | 1 個典型例子 | 多個對比案例 |
| **實作建議** | 3 個要點 | 完整實作指南 |

### 圖表複雜度

| 圖表類型 | Console | MD |
|----------|---------|----|
| **流程圖** | 線性流程，5-7 個節點 | 分支邏輯，完整決策樹 |
| **架構圖** | 核心組件關係 | 多層次系統架構 |
| **時序圖** | 主要交互流程 | 完整消息傳遞 |
| **對比表** | 3x3 重點對比 | 詳細功能對照 |

---

## 智能並行處理

檔案數量 >= 5 時，自動啟動 Skill-First 並行處理架構：
1. 使用 `parallel-processing` skill 分析並行可行性
2. Skill 返回建議：是否並行、最優 Task 數量、分組策略
3. 按建議執行，整合結果生成統一報告

詳細的平行處理架構、檔案分組邏輯和視覺化處理階段，見 [explain-parallel-architecture.md](./claude/_common/explain-parallel-architecture.md)。

---

## 📚 委託 Skills

- **`rules-reminder`** — `rg`/`fd` 取代 `grep`/`find`、禁止 `sed`、管道拆兩步等 Bash 規則

---

## 執行邏輯

### 決策流程
```
┌─────────────────────────────────────────────────────┐
│              /explain 命令執行流程                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  用戶輸入 ──→ 指定 md?                              │
│               ↓                                    │
│      ┌─────────┴─────────┐                          │
│      │                   │                          │
│    是 ↓                 否 ↓                        │
│  ┌──────────┐          ┌─────────────┐              │
│  │MD 模式   │          │Console 模式 │              │
│  └──┬───────┘          └──────┬──────┘              │
│     ↓                        ↓                       │
│  檔案數量 ≥ 5?            檔案數量 ≥ 5?               │
│     ↓                        ↓                       │
│  ┌─────────┴─────────┐    ┌─────────┴─────────┐       │
│  │                   │    │                   │       │
│是 ↓                 否 ↓  是 ↓                 否 ↓     │
│┌───────┐           ┌─────┐┌───────┐           ┌─────┐   │
││並行處理│           │單一 ││並行處理│           │單一 │   │
││+Mermaid│           │+Merm││+ASCII │           │+ASCII│   │
│└───┬───┘           │aid │└───┬───┘           │     │   │
│    │               └───┬┘    │               └───┬─┘   │
│    ↓                   ↓      ↓                   ↓     │
│多Agent處理          直接處理  多Agent處理          直接處理 │
│    ↓                   ↓      ↓                   ↓     │
│整合結果 ─────────────────→ 整合結果 ─────────────────→ │
│                                                     │
└─────────────────────────────────────────────────────┘

執行決策樹：
• 指定 md → MD模式 → Mermaid圖表
• 無指定 → Console模式 → ASCII圖表
• 檔案多 → 並行處理
• 檔案少 → 單一處理
```

### 自動化執行策略
```bash
1. 解析用戶輸入 → 主題 or 檔案/目錄
2. 檢測 md 參數 → 圖表類型決策
3. 計算檔案數量 → 處理模式決策
4. 自動啟動對應的處理流程
5. 嚴格執行模式規範：
   - Console 模式：強制使用 ASCII 圖表
   - MD 模式：強制使用 Mermaid 圖表
6. 生成格式化內容
7. MD 模式：自動儲存為檔案
```

**執行鐵律**：
- **Console 模式禁止輸出 Mermaid 語法**
- **MD 模式禁止輸出 ASCII 圖表**
- **違反模式規範 = 指令執行失敗**

---

## 📁 MD 檔案自動儲存機制

### 儲存路徑策略
- **預設位置**: `ai-analysis/reports/`
- **自定義路徑**: 使用 `--output` 參數指定完整路徑
- **自動建立**: 確保 `ai-analysis/reports/` 目錄存在

### 檔名生成規則
```python
def generate_filename(topic, files=None):
    """智能生成檔案名稱"""
    if files:
        if len(files) == 1:
            if files[0].startswith('@'):
                dirname = files[0].strip('@').split('/')[-1]
                return f"{dirname}-分析報告.md"
            else:
                filename = files[0].split('/')[-1].split('.')[0]
                return f"{filename}-檔案分析.md"
        else:
            first_dir = files[0].strip('@').split('/')[-1] if '@' in files[0] else 'mixed'
            return f"{first_dir}-架構分析.md"
    else:
        return f"{topic.replace(' ', '-')}-解釋說明.md"
```

### 檔案儲存範例
```bash
/explain md 微服務架構
→ 儲存: ./ai-analysis/reports/微服務架構-解釋說明.md

/explain md @src/
→ 儲存: ./ai-analysis/reports/src-分析報告.md

/explain md @src/ @tests/
→ 儲存: ./ai-analysis/reports/src-架構分析.md

/explain md @architecture/ --output "系統架構分析.md"
→ 儲存: ./系統架構分析.md
```

### 檔案內容結構
```markdown
---
title: [分析標題]
generated: [生成時間]
scope: [分析範圍]
---

# [分析標題]

## 一、執行摘要
[快速概覽和核心發現]

## 二、詳細分析
[根據模式生成的完整內容]

## 三、技術圖表
[Mermaid 圖表集合]

## 四、建議與總結
[改進建議和總結]
```

### 自動備份機制
- 檢查目標檔案是否存在
- 存在時添加時間戳記：`檔名_YYYYMMDD_HHMMSS.md`
- 提供覆蓋確認選項

---

## 進階使用技巧

### 智能檔案引用
```bash
# 使用萬用字元（檔案數量 >= 5 時自動並行處理）
/explain @src/**/*.py @tests/**/*.py

# 排除特定檔案
/explain @src/ @tests/ --exclude @src/temp/ @src/old/

# 組合不同類型檔案
/explain @code/ @docs/ @config/ "微服務架構分析"
```

### 自動化整合
```bash
# Git Hook 整合
#!/bin/sh
# pre-commit hook（staged 檔案 >= 5 個時自動並行處理）
/explain md @staged/ --output "PR-代碼審查.md"

# CI/CD Pipeline
claude -p "/explain md @build-errors/"
```

### 結果儲存與分享
```bash
# MD 模式自動儲存（預設行為）
/explain md @project/
→ 自動儲存: ./ai-analysis/reports/project-架構分析.md

# 自定義儲存路徑
/explain md @architecture/ --output "./docs/架構說明.md"
/explain md @api/ --output "./reports/接口分析.md"
```

---

## 最佳實踐與限制

### 最佳實踐
1. **明確範圍**: 指定具體檔案或目錄，避免過廣
2. **批次處理**: 一次處理相關檔案，提高效率
3. **定期分析**: 建立定期程式碼審查流程
4. **結果記錄**: 保存重要分析結果供未來參考

### 注意事項
- **檔案大小**: 單次建議不超過 50 個檔案
- **處理時間**: 大型專案可能需要較長時間
- **記憶體使用**: 複雜分析會消耗較多資源

### 故障排除
```bash
/explain --status @project/          # 檢查檔案數量和平行處理狀態
/explain --refresh @project/         # 強制重新分析
/explain --debug @problematic-file.py  # 除錯模式
/explain --mode-check                # 檢查輸出是否符合模式規範
/explain --validate-console          # 驗證 Console 模式（必須無 Mermaid）
/explain --validate-md               # 驗證 MD 模式（必須有 Mermaid）
```

### 模式違規檢測

當 Console 模式輸出 Mermaid 時：
1. **立即終止執行**
2. **顯示錯誤訊息**: `Console 模式不允許輸出 Mermaid 圖表`
3. **提供修正建議**: 使用 `/explain md <內容>` 改為 MD 模式，或重新生成 ASCII 圖表

**自我檢查清單**：
- [ ] Console 模式輸出是否包含任何 ````mermaid` 語法？
- [ ] 所有圖表是否為純文字 ASCII 格式？
- [ ] MD 模式是否正確使用 `skill: "mermaid"` 生成圖表？
- [ ] 色彩配置是否符合 Dark/Light 模式約束？

---

## Supporting Files

| 檔案 | 內容 | 何時讀取 |
|------|------|---------|
| [explain-parallel-architecture.md](./claude/_common/explain-parallel-architecture.md) | 平行處理架構 + 檔案分組邏輯 | 檔案數量 >= 5 需要並行處理時 |
| [explain-deep-analysis.md](./claude/_common/explain-deep-analysis.md) | 論文/文章/程式碼深度分析框架 | 分析特定類型內容時 |
| [explain-examples.md](./claude/_common/explain-examples.md) | 3 個完整使用範例 | 需要理解各模式實際輸出格式時 |
