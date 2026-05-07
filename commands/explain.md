---
description: 解釋技術概念、架構設計或流程
usage: /explain [console|md] <主題|@目錄|@檔案1 @檔案2 ...>
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

## 🎯 核心能力

### 📝 單一主題解釋
- **概念解析**: 技術概念、架構設計、流程說明
- **視覺化圖表**: ASCII 或 Mermaid 圖表輔助理解

### 📁 批次檔案分析
- **目錄掃描**: 自動分析整個目錄結構和內容
- **智能並行**: 使用 parallel-processing skill 自動判斷並行可行性
- **智能關聯**: 自動發現檔案間的關聯性和依賴關係

## 模式說明

### 🖥️ Console 模式（預設）
- **圖表類型**: ASCII 圖表（嚴格禁止 Mermaid）
- **內容長度**: 精簡扼要
- **輸出格式**: 終端機友善
- **適用場景**: 快速理解、即時討論
- **執行要求**: 必須輸出可純文字顯示的圖表

### 📄 MD 檔案模式
- **圖表類型**: Mermaid 圖表
- **內容長度**: 詳盡完整
- **輸出格式**: 自動儲存為 Markdown 檔案
- **儲存位置**: `ai-analysis/reports/` (統一路徑規則)
- **適用場景**: 文檔記錄、深度分析、知識沉澱

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

## 🧠 智能並行決策（Skill-First 設計）

### 第一步：並行可行性分析
```bash
# 使用 parallel-processing skill 進行智能決策
skill: "parallel-processing" "分析解釋任務：$USER_TASK"

# skill 返回決策結果
{
  "recommend_parallel": true/false/user_choice,
  "reason": "基於檔案數量、複雜度、成本效益的詳細分析",
  "optimal_task_count": 3-8,
  "grouping_strategy": "按檔案類型和智能負載平衡分組"
}
```

### 第二步：執行策略選擇
```bash
# 根據 skill 決策選擇執行策略
if skill.recommend_parallel:
    execute_parallel_explain(skill.recommendations)
elif skill.recommend_parallel == "user_choice":
    ask_user_about_parallel_benefit()
else:
    execute_sequential_explain()
```

### 按檔案切分的並行策略
```
┌─────────────────────────────────────────────────────┐
│            Skill-First 智能並行架構                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  用戶輸入 ──→ Skill 分析決策                          │
│               ↓                                    │
│      ┌─────────┴─────────┐                          │
│      │                   │                          │
│  建議並行 ↓             建議序列 ↓                    │
│  ┌───────┐            ┌──────────┐                  │
│  │並行處理│            │序列處理  │                  │
│  │(最優度)│            │(高效)    │                  │
│  └──┬────┘            └────┬─────┘                  │
│     ↓                      ↓                        │
│  ┌───────┐              ┌───────┐                   │
│  │智能分組│              │單一分析│                   │
│  └──┬────┘              └───────┘                   │
│     ↓                                                 │
│  ┌─────────────────────────────────────────────┐     │
│  │Skill建議的最優Task數量 → 同時執行 → 整合結果│     │
│  └─────────────────────────────────────────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘

Skill-First 流程：
1. Task 分析 → Skill 決策
2. 智能分組 → 最優並行度
3. 執行監控 → 結果整合
4. 輸出報告
```

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

### 🎨 圖表生成規範

**Skill 使用要求**:
- **✅ 必須使用**: `skill: "mermaid"` 生成所有圖表
- **✅ 自動確保**: Dark/Light 模式相容性
- **✅ 標準化**: 統一的色彩配置和樣式
- **🚫 禁止**: 手動編寫 Mermaid 語法

**使用方式**:
```bash
# 在需要圖表時使用 skill 調用
skill: "mermaid"
# 然後描述需要的圖表類型和內容
```
### 支援的圖表類型

使用 `skill: "mermaid"` 可以生成以下專業圖表：

- **流程圖**: 業務流程、演算法流程
- **序列圖**: 系統交互、API 呼叫流程
- **類圖**: 軟體架構、類別關係
- **甘特圖**: 專案時程、里程碑規劃
- **架構圖**: 系統架構、組件關係
- **狀態圖**: 狀態轉換、生命週期

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

## ⚡ Skill-Driven 並行處理架構

### 動態並行執行策略（基於 Skill 建議）
```bash
# 第一步：Skill 決策分析
skill: "parallel-processing" "分析解釋任務的並行可行性"

# 第二步：基於 Skill 建議的執行
if skill.recommend_parallel:
    # 使用 Skill 建議的最優並行度和分組策略
    tasks = create_skill_optimized_groups(skill.grouping_strategy)

    # 同時發起多個整合型 Task
    Task 1 (content-analyzer): 完整分析 [檔案組1]（內容+結構+上下文）
    Task 2 (structure-analyzer): 完整分析 [檔案組2]（架構+關聯+邏輯）
    Task 3 (context-analyzer): 完整分析 [檔案組3]（背景+歷史+依賴）

    # 最終整合
    Task report-coordinator: 整合所有結果，生成統一解釋報告
else:
    # 高效序列處理
    execute_sequential_analysis()
```

**Skill-First 優勢**：
- **智能決策**：基於成本效益分析，避免無效並行
- **最優分組**：Skill 提供最優的檔案分組策略
- **動態調整**：根據實際檔案特性和複雜度調整

### 🎯 模式區分約束

#### Console 模式（預設）
**輸出要求**：
- **圖表類型**: 純文字 ASCII 圖表
- **內容風格**: 精簡扼要，重點突出
- **適用場景**: 快速理解、即時討論

#### MD 模式
**輸出要求**：
- **圖表類型**: 使用 `skill: "mermaid"` 生成專業圖表
- **內容風格**: 詳盡完整，適合長期保存
- **適用場景**: 文檔記錄、深度分析、知識沉澱

**🎯 關鍵區別**：
- Console 模式：適合終端機快速瀏覽
- MD 模式：適合專業文檔和分享

#### 階段 2: 視覺化處理
```bash
# 根據輸出模式自動生成對應圖表
Task (visualization-specialist): 根據 Console 或 MD 模式生成對應圖表
- Console 模式：生成 ASCII 流程圖、架構圖，創建終端機友善圖表
- MD 模式：使用 skill: "mermaid" 生成專業圖表
  - 流程圖、類圖、時序圖、架構圖
  - 自動使用高對比度配色 (#111827, #475569)
  - 確保 WCAG 可讀性標準
```

#### 階段 3: 結果整合
```bash
# 整合所有分析結果和視覺化輸出
Task (report-coordinator): 整合分析結果，生成完整的分析報告
```

### 智能檔案分組策略

```python
def group_files_for_analysis(file_paths):
    """智能分組檔案以進行最適化平行處理"""
    groups = {
        'config': [],      # 配置檔案
        'code': [],        # 程式碼檔案
        'docs': [],        # 文檔檔案
        'tests': [],       # 測試檔案
        'data': []         # 資料檔案
    }

    for path in file_paths:
        if any(config in path for config in ['package.json', 'tsconfig', 'yaml']):
            groups['config'].append(path)
        elif any(code in path for code in ['.py', '.js', '.ts', '.java']):
            groups['code'].append(path)
        elif any(doc in path for doc in ['.md', '.txt', '.pdf']):
            groups['docs'].append(path)
        elif 'test' in path:
            groups['tests'].append(path)
        else:
            groups['data'].append(path)

    return [g for g in groups.values() if g]  # 過濾空群組
```

---

## 執行邏輯

> 🔧 **搜尋約束**：`fd` 取代 `find`、`rg` 取代 `grep`。詳見 `modern-cli-preference.md`（已自動載入）

### 簡化決策流程
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
# 系統自動執行步驟：
1. 解析用戶輸入 → 主題 or 檔案/目錄
2. 檢測 md 參數 → 圖表類型決策
3. 計算檔案數量 → 處理模式決策
4. 自動啟動對應的處理流程
5. 🚨 嚴格執行模式規範：
   - Console 模式：強制使用 ASCII 圖表
   - MD 模式：強制使用 Mermaid 圖表
6. 生成格式化內容
7. MD 模式：自動儲存為檔案
```

**🚨 執行鐵律**：
- **Console 模式禁止輸出 Mermaid 語法**
- **MD 模式禁止輸出 ASCII 圖表**
- **違反模式規範 = 指令執行失敗**

**使用者只需**: 選擇 `console` 或 `md`，其餘全自動！

---

## 📁 MD 檔案自動儲存機制

### 儲存路徑策略
```bash
# 統一儲存路徑：
- 預設位置：ai-analysis/reports/
- 自定義路徑：使用 --output 參數指定完整路徑
- 自動建立：確保 ai-analysis/reports/ 目錄存在
```

### 檔名生成規則
```python
def generate_filename(topic, files=None):
    """智能生成檔案名稱"""
    if files:
        # 多檔案分析
        if len(files) == 1:
            if files[0].startswith('@'):
                # 目錄分析
                dirname = files[0].strip('@').split('/')[-1]
                return f"{dirname}-分析報告.md"
            else:
                # 單檔案分析
                filename = files[0].split('/')[-1].split('.')[0]
                return f"{filename}-檔案分析.md"
        else:
            # 多檔案混合分析
            first_dir = files[0].strip('@').split('/')[-1] if '@' in files[0] else 'mixed'
            return f"{first_dir}-架構分析.md"
    else:
        # 主題分析
        return f"{topic.replace(' ', '-')}-解釋說明.md"
```

### 檔案儲存範例
```bash
# 實際使用範例
/explain md 微服務架構
→ 儲存: ./analysis/微服務架構-解釋說明.md

/explain md @src/
→ 儲存: ./analysis/src-分析報告.md

/explain md @src/ @tests/
→ 儲存: ./analysis/src-架構分析.md

/explain md @architecture/ --output "系統架構分析.md"
→ 儲存: ./docs/generated/系統架構分析.md
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
```bash
# 防止覆蓋重要檔案：
- 檢查目標檔案是否存在
- 存在時添加時間戳記：檔名_YYYYMMDD_HHMMSS.md
- 提供覆蓋確認選項
```

---

## 深度分析模式

根據不同類型內容，在視覺化解釋基礎上增加對應的深度分析：

### 📄 論文分析模式

#### 學術結構分析
- **研究問題**：問題定義、動機、假設
- **方法論**：實驗設計、數據來源、評估指標
- **核心貢獻**：創新點、理論突破、實用價值

#### 技術深度探討
- **算法原理**：數學公式、推導過程、複雜度分析
- **實驗設計**：對照組設定、參數調整、統計方法
- **結果驗證**：數據解讀、統計顯著性、局限性

#### 影響力評估
- **學術脈絡**：前人研究、理論基礎、發展脈絡
- **實際應用**：產業應用、實作可行性、商業價值
- **未來方向**：研究缺口、擴展可能、後續工作

### 📝 文章分析模式

#### 論述結構分析
- **核心論點**：主要觀點、支撐論據、邏輯脈絡
- **資訊架構**：章節安排、資訊層次、重點分布
- **說服策略**：修辭技巧、證據類型、目標受眾

#### 內容深度探討
- **事實查證**：數據來源、統計方法、可信度評估
- **觀點比較**：不同立場、爭議點、平衡性分析
- **背景脈絡**：時代背景、相關事件、影響因素

#### 價值判斷
- **實用性**：可操作性、適用範圍、實施難度
- **創新性**：新穎觀點、獨特見解、突破性思考
- **影響力**：社會影響、政策意涵、長期效應

### 💻 程式碼分析模式

#### 技術實作層面
- **代碼架構分析**：關鍵類別、方法、設計模式
- **性能考量**：時間/空間複雜度、瓶頸分析
- **技術選型依據**：框架選擇理由、技術棧權衡

#### 實作細節探討
- **關鍵算法**：核心邏輯的偽代碼或實際代碼
- **數據結構設計**：儲存格式、索引策略
- **錯誤處理策略**：異常情況、容錯機制

#### 系統整合分析
- **模組間依賴**：介面定義、數據傳遞
- **擴展性設計**：未來需求、架構彈性
- **測試策略**：單元測試、整合測試重點

**使用場景**：
- 📄 **論文**: 學術研究分析、技術文獻理解
- 📝 **文章**: 商業報告分析、政策文件解讀
- 💻 **程式碼**: 代碼審查、架構重構、技術選型

---

## 🎯 實際使用範例

### 範例 1: 單一概念解釋
```bash
# Console 模式 - 快速理解
/explain Docker 容器化

【核心概念】
Docker 將應用程式打包成輕量級、可移植的容器
┌─────────┐    ┌──────────┐    ┌─────────┐
│ 應用程式 │ →  │ Docker   │ →  │ 容器運行│
│ + 依賴   │    │ 打包     │    │ 任何環境│
└─────────┘    └──────────┘    └─────────┘

【關鍵優勢】
• 環境一致性：開發、測試、生產環境完全相同
• 快速部署：秒級啟動，資源占用少
• 版本管理：映像檔版本控制，易於回滾
```

### 範例 2: 目錄智能分析
```bash
# 分析整個專案結構（檔案數量 >= 5 時自動並行處理）
/explain @src/ @config/ @docs/

# 系統檢測到 15+ 檔案 → 自動啟動多個 Tasks 並行處理：

#### 🔍 結構分析結果
**Task structure-analyzer** 發現 3 層架構：
```
┌─────────────┐
│  Presentation│ ← @src/components/
└─────────────┘
       ↓
┌─────────────┐
│   Business  │ ← @src/services/
└─────────────┘
       ↓
┌─────────────┐
│    Data     │ ← @src/models/
└─────────────┘
```

#### 🔍 內容分析結果
**Task content-analyzer** 識別核心服務：
- AuthService：JWT 認證機制
- PaymentService：第三方支付整合
- NotificationService：郵件/簡訊通知

#### 🔍 上下文分析結果
**Task context-analyzer** 分析 Git 歷史：
- 2 個月前從 monolithic 重構為 microservices
- 最近活躍開發：PaymentService 功能擴充
```

### 範例 3: MD 檔案深度分析
```bash
# 生成完整技術文檔
/explain md @architecture/ @database-schema.sql

# 輸出完整 Markdown 報告：

# 系統架構分析報告

## 一、整體架構概覽
```
┌─────────────────────────────────────────────────────┐
│                  系統架構圖                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐                                │
│  │ Frontend Layer  │                                │
│  │ ┌─────────────┐ │                                │
│  │ │React Components│ │                                │
│  │ └─────────────┘ │                                │
│  │ ┌─────────────┐ │                                │
│  │ │ Redux Store │ │                                │
│  │ └─────────────┘ │                                │
│  └─────────┬───────┘                                │
│            │                                        │
│            ↓                                        │
│  ┌─────────────────┐                                │
│  │ Backend Layer   │                                │
│  │ ┌─────────────┐ │                                │
│  │ │Express.js API│ │                                │
│  │ └─────────────┘ │                                │
│  │ ┌─────────────┐ │                                │
│  │ │ Auth Service│ │                                │
│  │ └─────────────┘ │                                │
│  │ ┌─────────────┐ │                                │
│  │ │Business Logic│ │                                │
│  │ └─────────────┘ │                                │
│  └─────┬───────────┘                                │
│        │                                          │
│        ↓                                          │
│  ┌─────────────────┐                                │
│  │   Data Layer    │                                │
│  │ ┌─────────────┐ │                                │
│  │ │ PostgreSQL  │ │                                │
│  │ └─────────────┘ │                                │
│  │ ┌─────────────┐ │                                │
│  │ │ Redis Cache │ │                                │
│  │ └─────────────┘ │                                │
│  └─────────────────┘                                │
│                                                     │
│數據流向：                                          │
│React → API → Auth → PostgreSQL                     │
│State → API → Business → PostgreSQL                  │
│                   Business → Redis                   │
└─────────────────────────────────────────────────────┘
```

## 二、資料庫設計分析
### 2.1 核心表結構
...

[完整報告約 2000 字，包含詳細的圖表和建議]
```

---

## 🚀 進階使用技巧

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

# CI/CD Pipeline（自動生成分析報告）
claude -p "/explain md @build-errors/"

# 定期專案分析（自動儲存到 analysis/ 目錄）
/explain md @src/ @docs/ --output "每週架構分析.md"
```

### 結果儲存與分享
```bash
# MD 模式自動儲存（預設行為）
/explain md @project/
→ 自動儲存: ./analysis/project-架構分析.md

# 自定義儲存路徑
/explain md @architecture/ --output "./docs/架構說明.md"
/explain md @api/ --output "./reports/2024-Q1-接口分析.md"

# 批次分析管理
/explain md @frontend/ --output "前端架構分析.md"
/explain md @backend/ --output "後端架構分析.md"
/explain md @database/ --output "資料庫設計分析.md"
```

### 檔案管理最佳實踐
```bash
# 建立分析報告目錄結構
mkdir -p ./analysis ./docs/generated ./reports

# 定期清理舊報告
find ./analysis -name "*.md" -mtime +30 -delete

# 報告版本控制
git add ./analysis/          # 將重要分析加入版本控制
git add ./docs/generated/     # 文檔加入版本控制
git commit -m "docs: 更新專案分析報告"
```

---

## ⚠️ 最佳實踐與限制

### ✅ 最佳實踐
1. **明確範圍**: 指定具體檔案或目錄，避免過廣
2. **批次處理**: 一次處理相關檔案，提高效率
3. **定期分析**: 建立定期程式碼審查流程
4. **結果記錄**: 保存重要分析結果供未來參考

### ⚠️ 注意事項
- **檔案大小**: 單次建議不超過 50 個檔案
- **處理時間**: 大型專案可能需要 1-3 分鐘
- **記憶體使用**: 複雜分析會消耗較多資源
- **網路依賴**: 某些分析可能需要外部查詢

### 🔄 故障排除
```bash
# 檢查檔案數量和平行處理狀態
/explain --status @project/

# 強制重新分析
/explain --refresh @project/

# 除錯模式
/explain --debug @problematic-file.py

# 查看檔案統計
/explain --stats @src/

# 檢查儲存路徑和檔案狀態
/explain --check-storage

# 強制覆蓋已存在的檔案
/explain md @project/ --force

# 預覽即將生成的檔名
/explain md @src/ --preview-filename

# 🚨 模式檢查（新增）
/explain --mode-check              # 檢查當前輸出是否符合模式規範
/explain --validate-console         # 驗證 Console 模式輸出（必須無 Mermaid）
/explain --validate-md             # 驗證 MD 模式輸出（必須有 Mermaid）
```

### 🚨 模式違規檢測
當發現 Console 模式輸出 Mermaid 時：
1. **立即終止執行**
2. **顯示錯誤訊息**: `❌ Console 模式不允許輸出 Mermaid 圖表`
3. **提供修正建議**:
   - 使用 `/explain md <內容>` 改為 MD 模式
   - 重新生成純 ASCII 圖表
4. **記錄違規事件**: 防止再次發生

**自我檢查清單**：
- [ ] Console 模式輸出是否包含任何 ````mermaid` 語法？
- [ ] 所有圖表是否為純文字 ASCII 格式？
- [ ] 在純文字終端機中是否能正確顯示？
- [ ] MD 模式是否正確使用 Mermaid 語法？
- [ ] 色彩配置是否符合 Dark/Light 模式約束？

### 檔案儲存問題解決
```bash
# 無法寫入檔案時
1. 檢查目錄權限: ls -la ./analysis/
2. 手動建立目錄: mkdir -p ./analysis ./docs/generated
3. 檢查磁碟空間: df -h

# 檔名衝突問題
- 系統自動添加時間戳記
- 使用 --force 強制覆蓋
- 使用 --output 自定義檔名

# 路徑問題
- 使用絕對路徑: /explain md @src/ --output "/full/path/report.md"
- 檢查路徑是否存在: mkdir -p ./custom/path/
```

---

## 📊 效能指標

### 並行處理效能
- **小型專案** (< 10 檔案): 5-10 秒
- **中型專案** (10-50 檔案): 10-30 秒
- **大型專案** (50+ 檔案): 30-120 秒

### 資源使用
- **記憶體峰值**: ~200MB (大型專案)
- **CPU 使用**: 短暫高峰，多核心並行
- **網路頻寬**: 最小化，僅必要時使用

