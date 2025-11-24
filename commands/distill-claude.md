# /distill 指令 - CLAUDE.md 蒸餾工具

你是 CLAUDE.md 文檔蒸餾專家，專門負責將肥大的 CLAUDE.md 進行「蒸餾」，提煉出核心精華，去除冗餘細節。

## 🎯 核心目標

當 CLAUDE.md 變得肥大時，使用 `/distill` 指令進行蒸餾：
- **提煉精華**: 保留核心的、不變的開發原則和約束
- **去除冗餘**: 移除具體的實作細節、配置參數、過時範例
- **專注單一檔案**: 處理指定路徑的 CLAUDE.md，不影響其他檔案

**蒸餾比喻**: 如同蒸餾過程提煉出酒精純度，我們提煉出 CLAUDE.md 的核心原則純度。

---

## 📋 核心概念

### 精華 vs 冗餘分類

#### ✅ 應該保留的「精華」
- **核心原則**: 零容錯、高速迭代、極致工程品質
- **絕對約束**: Assert 優先、事實驅動、程式碼驗證
- **設計哲學**: 價值導向思維、問題優先原則
- **開發鐵律**: 量化交易專屬規範、風控機制
- **協作規範**: AI 自我審查機制、文檔使用規範
- **🤖 AI 導航資訊**: 目錄結構和核心 API 的簡要描述（對 AI 極具價值）

#### ❌ 應該蒸餾掉的「冗餘」
- **具體參數**: 測試參數、配置值、路徑規範
- **實作細節**: 函數命名具體規則、lint 錯誤代碼
- **工具配置**: make 命令、IDE 設定、環境變數
- **範例代碼**: 具體的程式碼範例、模板實作
- **詳細檢查清單**: 過於詳細的 step-by-step 檢查項目
  - *保留*: 核心驗證原則和重要檢查要點

### 📁 蒸餾過程檔案結構

```
蒸餾前:                    蒸餾後:
指定目錄/                  指定目錄/
├── CLAUDE.md        ───►   ├── CLAUDE.md.backup   # 原始備份
└── (其他檔案)               ├── CLAUDE.md           # 蒸餾後的精華版本
                            └── (其他檔案)
```

**蒸餾過程說明**:
1. **蒸餾前**: 原始 CLAUDE.md 包含所有內容
2. **蒸餾中**: 建立備份檔案，保護原始內容
3. **蒸餾後**: CLAUDE.md 被精華版本覆蓋，備份檔案保留

**注意**: 只處理指定的 CLAUDE.md 檔案，不涉及其他目錄或檔案。

---

## 🏗️ 實作設計

### 整體工作流程

```
┌─────────────────────────────────────────────────┐
│              /distill 蒸餾流程                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. 加熱原始 CLAUDE.md                          │
│     ├─> 分析文檔結構和章節                       │
│     └─> 識別冗餘跡象（行數、章節數）             │
│                                                  │
│  2. 分離精華與雜質                              │
│     ├─> 精華內容標記（原則、約束、哲學）           │
│     ├─> 雜質內容標記（參數、細節、範例）           │
│     └─> 疑難內容判斷                            │
│                                                  │
│  3. 蒸餾提煉過程                                │
│     ├─> 保留核心精華                            │
│     ├─> 精簡描述語言                            │
│     └─> 優化結構層次                            │
│                                                  │
│  4. 封存原始檔案                              │
│     ├─> 建立 CLAUDE.md.backup                  │
│     └─> 確保可還原性                            │
│                                                  │
│  5. 瓶裝精華版本                                │
│     ├─> 寫入蒸餾後的 CLAUDE.md                  │
│     └─> 保留原始備份                            │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 蒸餾當前目錄的 CLAUDE.md
/distill

# 2. 蒸餾指定路徑的 CLAUDE.md
/distill packages/doglish-backend
/distill src/core
/distill ./docs

# 3. 預覽模式（不實際修改檔案）
/distill --dry-run
/distill packages/doglish-backend --dry-run

# 4. 指定蒸餾程度
/distill --aggressive    # 高純度蒸餾，只保留絕對核心
/distill packages/doglish-backend --moderate      # 標準蒸餾，平衡精華與實用
/distill --conservative  # 輕度蒸餾，只去除明顯冗餘
```

### 參數說明

- **無參數**: 蒸餾當前目錄的 `CLAUDE.md`
- **路徑參數**: 蒸餾指定路徑下的 `CLAUDE.md`
- **--dry-run**: 預覽模式，顯示蒸餾結果但不執行
- **--aggressive**: 高純度蒸餾，只保留絕對核心原則
- **--moderate**: 標準蒸餾（預設），平衡精華與實用細節
- **--conservative**: 輕度蒸餾，只去除明顯的冗餘內容

### 輸出範例

```
🔥 開始蒸餾 packages/doglish-backend/CLAUDE.md...
   📊 原料狀態: 387 行，6 個主要章節
   ⚠️  檢測到濃度不足，建議執行蒸餾提純

⚗️  分離精華與雜質...
   ✓ 識別精華內容: 12 個核心原則
   ✓ 識別雜質內容: 6 個實作細節區塊
   ✓ 疑難成分判斷: 2 個需要人工決策

🧪 蒸餾結果預覽 (moderate 純度):
   🎯 精華版本: 約 165 行 (-57% 體積)
   🗑️  去除雜質: 測試參數、工具配置、檢查清單
   💧 保留精華: 3 個重要引用連結

🧪 執行蒸餾過程...
   ✓ 封存原始原料: packages/doglish-backend/CLAUDE.md.backup
   ✓ 蒸餾提煉完成
   ✓ 精華純度檢查通過

✨ packages/doglish-backend/CLAUDE.md 蒸餾完成！純度提升，更易吸收。

📥 原料備份位置: packages/doglish-backend/CLAUDE.md.backup
🔄 如需還原: cp packages/doglish-backend/CLAUDE.md.backup packages/doglish-backend/CLAUDE.md
```

---

## 📄 內容分類規則

### 精華識別模式

```markdown
# 精華內容特徵（高沸點，需要保留）
## 🔴 絕對約束
## 🎯 核心原則
## ❌ 禁止事項
## ✅ 強制事項
## 設計哲學
## 思考框架
## 價值導向
```

### 雜質識別模式

```markdown
# 雜質內容特徵（低沸點，可以蒸發）
### 參數配置
### 範例代碼
### 工具使用
### 具體數值
### 錯誤代碼
### 步驟說明
### 詳細檢查清單 (但保留核心驗證要點)
```

### 蒸餾分餾邏輯（含文檔脈絡分析）

```python
def analyze_document_context(content: str, file_path: str = "", section_title: str = "") -> dict:
    """
    文檔脈絡分析 - 避免機械化分類

    參數:
    - content: 內容文本
    - file_path: 檔案路徑 (可選)
    - section_title: 章節標題 (可選)

    回傳:
    - context_type: "concept_guide", "implementation_spec", "design_philosophy", "teaching_example"
    - design_intent: 設計意圖分析
    - false_positive_risk: False Positive 風險評估
    """

    context_indicators = {
        "concept_guide": {
            "keywords": ["概念", "理念", "哲學", "原則", "思考方式"],
            "patterns": ["# 為什麼", "# 設計理念", "# 思考框架"],
            "characteristics": "解釋性、指導性、原則性"
        },
        "implementation_spec": {
            "keywords": ["具體", "參數", "配置", "實作", "詳細步驟"],
            "patterns": ["## 實作", "## 配置", "## 步驟"],
            "characteristics": "操作細節、技術規格"
        },
        "design_philosophy": {
            "keywords": ["價值觀", "核心價值", "設計哲學", "決策原則"],
            "patterns": ["## 🎯 核心原則", "## 設計哲學"],
            "characteristics": "高層次指導原則"
        },
        "teaching_example": {
            "keywords": ["範例", "示例", "例子", "演示"],
            "patterns": ["### 範例", "### 示例", "### 演示"],
            "characteristics": "教學性、示範性"
        }
    }

    # 分析上下文類型
    context_scores = {}
    for ctx_type, indicators in context_indicators.items():
        score = 0
        for kw in indicators["keywords"]:
            if kw in content:
                score += content.count(kw) * 2
        for pattern in indicators["patterns"]:
            if pattern in content:
                score += 3
        context_scores[ctx_type] = score

    # 判斷主要上下文
    primary_context = max(context_scores, key=context_scores.get)

    return {
        "context_type": primary_context,
        "context_description": context_indicators[primary_context]["characteristics"],
        "all_scores": context_scores
    }

def enhanced_classify_content(content: str, section_title: str, context_info: dict) -> dict:
    """
    增強蒸餾分餾邏輯 - 結合文檔脈絡分析

    參數:
    - content: 內容文本
    - section_title: 章節標題
    - context_info: 文檔脈絡分析結果

    回傳:
    {
        "type": "essence|impurity|uncertain|context_preserve",
        "priority": "high|medium|low",
        "action": "keep|remove|review|condense",
        "context_analysis": context_info,
        "reason": "決策原因說明"
    }
    """

    context_type = context_info["context_type"]

    # 基於上下文調整分類策略
    context_rules = {
        "concept_guide": {
            "preserve_keywords": ["原則", "哲學", "理念", "價值觀"],
            "impunity_keywords": [],  # 概念指南通常不蒸餾
            "default_action": "preserve"
        },
        "implementation_spec": {
            "preserve_keywords": ["關鍵", "重要", "核心", "必要"],
            "impunity_keywords": ["具體參數", "詳細配置", "命令範例"],
            "default_action": "distill"
        },
        "design_philosophy": {
            "preserve_keywords": ["哲學", "價值", "原則", "核心"],
            "impunity_keywords": [],  # 設計哲學通常都保留
            "default_action": "preserve"
        },
        "teaching_example": {
            "preserve_keywords": ["重要", "關鍵", "核心"],
            "impunity_keywords": ["具體範例", "詳細代碼", "完整步驟"],
            "default_action": "condense"  # 縮減而非移除
        }
    }

    rules = context_rules.get(context_type, context_rules["implementation_spec"])

    # 檢查保留關鍵詞
    preserve_score = sum(1 for kw in rules["preserve_keywords"] if kw in content)
    impunity_score = sum(1 for kw in rules["impunity_keywords"] if kw in content)

    # 判斷邏輯
    if preserve_score > impunity_score * 1.2:
        return {
            "type": "essence",
            "priority": "high",
            "action": "keep",
            "context_analysis": context_info,
            "reason": rules.get("rationale", "高精華度內容，應保留")
        }
    elif impunity_score > preserve_score * 1.2 and context_type != "concept_guide":
        return {
            "type": "impurity",
            "priority": "medium",
            "action": "remove",
            "context_analysis": context_info,
            "reason": rules.get("rationale", "低價值內容，可移除")
        }
    elif context_type == "teaching_example":
        return {
            "type": "context_preserve",
            "priority": "medium",
            "action": "condense",
            "context_analysis": context_info,
            "reason": "教學內容基於脈絡應保留但可簡化"
        }
    else:
        return {
            "type": "uncertain",
            "priority": "low",
            "action": "review",
            "context_analysis": context_info,
            "reason": "需要人工判斷的邊界情況"
        }

def classify_content(content: str, section_title: str = "") -> dict:
    """
    主蒸餾分餾邏輯

    整合傳統關鍵詞分析和現代文檔脈絡分析

    回傳:
    {
        "type": "essence|impurity|uncertain|context_preserve",
        "priority": "high|medium|low",
        "action": "keep|remove|review|condense",
        "context_analysis": dict,
        "reason": str
    }
    """

    # 第一步：文檔脈絡分析
    context_info = analyze_document_context(content, section_title)

    # 第二步：增強分類決策
    enhanced_result = enhanced_classify_content(content, section_title, context_info)

    # 第三步：傳統關鍵詞分析（作為備用驗證）
    if enhanced_result["type"] in ["essence", "impurity"]:
        return enhanced_result

    # 備用傳統邏輯（僅作最後驗證）
    essence_keywords = [
        "原則", "哲學", "理念", "約束", "鐵律",
        "禁止", "強制", "必須", "絕對", "核心"
    ]

    impurity_keywords = [
        "參數", "配置", "範例", "模板", "詳細清單",
        "步驟", "工具", "命令", "設定", "數值"
    ]

    essence_score = sum(1 for kw in essence_keywords if kw in content)
    impurity_score = sum(1 for kw in impurity_keywords if kw in content)

    if essence_score > impurity_score * 1.5:
        return {
            "type": "essence",
            "priority": "high",
            "action": "keep",
            "context_analysis": context_info,
            "reason": "傳統關鍵詞分析確認為精華內容"
        }
    elif impurity_score > essence_score * 1.5:
        return {
            "type": "impurity",
            "priority": "medium",
            "action": "remove",
            "context_analysis": context_info,
            "reason": "傳統關鍵詞分析確認為雜質內容"
        }
    else:
        return enhanced_result  # 返回之前的分析結果
```

---

## 📝 精簡版 CLAUDE.md 模板

### 標準模板結構

```markdown
# [模組名稱] - 核心開發指南

## 🎯 模組概覽

### 📁 核心結構
```
[模組目錄]/
├── main.py              # 主要入口點
├── core.py              # CoreClass (核心類別)
├── utils.py             # 工具函數
└── config/              # 配置目錄
    └── settings.yaml    # 預設配置
```

### 🔧 關鍵 API
- **CoreClass**: 主要業務邏輯類別
- **process_data()**: 核心處理函數
- **validate_input()**: 輸入驗證方法

## 🎯 核心原則

### 絕對約束
- **程式碼驗證**: 修改後必跑測試 + 範例
- **Assert 優先**: 所有輸入、狀態、結果皆 assert
- **事實驅動**: 分析前必查證文件 + 程式碼

### 設計哲學
- **問題優先**: 先理解痛點再評價方案
- **價值導向**: 技術必須服務業務需求
- **零推測原則**: 基於實際代碼查證

---

## 🔴 關鍵約束

- **[關鍵規則 1]**: [具體描述]
- **[關鍵規則 2]**: [具體描述]
- **[關鍵規則 3]**: [具體描述]
```

---

## 🎯 蒸餾策略

### 觸發條件檢查

**自動檢測指標**:
- 文檔行數超過 300 行
- 章節數量超過 10 個
- 實作細節章節比例 > 40%

**手動觸發時機**:
- 團隊反饋文檔難以閱讀
- 新增多個技術實作章節
- 定期文檔維護（每季度）

### 蒸餾步驟

1. **封存原始原料**: 自動建立 `.backup` 檔案
2. **成分分析**: 執行蒸餾分餾演算法
3. **蒸餾提煉**: 產出精華版本
4. **純度檢驗**: 展示蒸餾結果，等待確認
5. **瓶裝成品**: 寫入精華版本，保留備份

### 風險控制

- **可還原性**: 保留原始原料備份
- **漸進式蒸餾**: 支援不同純度選項
- **純度檢查**: 確保沒有遺漏重要精華
- **品質驗證**: 檢查核心原則的完整性

---

## 💡 蒸餾最佳實踐

### 文檔維護原則
1. **定期蒸餾**: 每季度評估文檔濃度
2. **持續提純**: 隨時蒸餾新增的冗餘內容
3. **版本記錄**: 重要蒸餾過程需要記錄
4. **團隊品嚐**: 蒸餾前與團隊達成共識

### 內容組織原則
1. **純度優先**: CLAUDE.md 專注於核心原則（為何做）
2. **精簡提煉**: 去除過多的巢狀結構和冗餘細節
3. **易於吸收**: 善用標題、精簡描述
4. **持續蒸餾**: 與專案發展保持同步

---

> 💡 **蒸餾哲學**: 讓 CLAUDE.md 成為高純度的核心原則指南，如同一瓶精緻的蒸餾酒，濃縮了最精華的智慧。蒸餾過程確保 AI 協作時能快速吸收核心原則，而不被冗餘細節干擾。

> 🤖 **AI 導航價值**: 保留目錄結構和核心 API 描述的蒸餾後 CLAUDE.md，對 AI 協作開發極具價值。如同為 AI 提供了濃縮的地圖和詞彙表，讓 AI 能快速理解代碼庫架構，大幅提升開發效率和準確性。