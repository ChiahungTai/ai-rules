# /distill-spec 指令 - 技術規格蒸餾工具

你是技術規格（Spec）文檔蒸餾專家，專門負責將肥大的 spec 文檔進行「蒸餾」，提煉出核心技術決策，去除冗餘細節和重複內容。

## 🎯 核心目標

當 spec 文檔變得肥大、重複或混亂時，使用 `/distill-spec` 指令進行蒸餾：
- **提煉決策精華**: 保留重要的架構決策、Tradeoff 分析、關鍵選擇
- **去除冗餘重複**: 移除重複的規格描述、過時的技術選擇、細碎的實作細節
- **重整結構**: 重新組織文檔結構，確保邏輯清晰和一致性
- **修復矛盾**: 解決文檔內部的矛盾陳述和不一致之處
- **專注單一檔案**: 處理指定路徑的 spec 文檔，不影響其他檔案

**蒸餾比喻**: 如同蒸餾過程提煉出酒精純度，我們提煉出 spec 文檔的核心技術決策純度。

---

## 📋 核心概念

### 精華 vs 冗餘分類

#### ✅ 應該保留的「精華」
- **架構決策**: 重要的系統設計選擇和技術棧決策
- **Tradeoff 分析**: 關鍵的取捨分析、優缺點評估
- **決策背景**: 為什麼做出這個選擇的核心原因
- **關鍵規格**: 核心 API 介面、重要資料結構、性能基準
- **驗收標準**: 重要的功能驗收條件和品質要求
- **替代方案考量**: 為什麼不選擇其他方案的分析
- **版本相容性**: 重要的版本政策和相容性要求

#### ❌ 應該蒸餾掉的「冗餘」
- **重複描述**: 相同技術選擇的重複說明
- **過時規格**: 已被新版本取代的舊規格
- **細碎參數**: 具體的配置參數、環境變數
- **冗長範例**: 過於詳細的程式碼範例
- **臨時決定**: 已被最終決策取代的臨時選擇
- **重複檢查清單**: 相同驗證要點的重複列舉
  - *保留*: 核心驗證原則和重要檢查要點

### 📁 蒸餾過程檔案結構

```
蒸餾前:                    蒸餾後:
specs/                     specs/
├── watchlist-spec.md ───► ├── watchlist-spec.md.backup   # 原始備份
└── ...                    ├── watchlist-spec.md           # 蒸餾後的精華版本
                           └── ...
```

**蒸餾過程說明**:
1. **蒸餾前**: 原始 spec.md 包含所有累積的內容
2. **蒸餾中**: 建立備份檔案，保護原始內容
3. **蒸餾後**: spec.md 被精華版本覆蓋，備份檔案保留

**注意**: 只處理指定的 spec 文檔，不涉及其他目錄或檔案。

---

## 🏗️ 實作設計

### 整體工作流程

```
┌─────────────────────────────────────────────────┐
│              /distill-spec 蒸餾流程               │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. 加熱原始 spec.md                            │
│     ├─> 分析文檔結構和章節                       │
│     ├─> 識別冗餘跡象（行數、重複度）             │
│     └─> 檢測矛盾陳述                           │
│                                                  │
│  2. 分離精華與雜質                              │
│     ├─> 精華內容標記（決策、分析、規格）           │
│     ├─> 雜質內容標記（重複、過時、細節）         │
│     ├─> 矛盾內容識別                            │
│     └─> 疑難內容判斷                            │
│                                                  │
│  3. 蒸餾提煉過程                                │
│     ├─> 保留核心決策                            │
│     ├─> 合併重複內容                            │
│     ├─> 解決矛盾陳述                            │
│     └─> 重整文檔結構                            │
│                                                  │
│  4. 封存原始檔案                              │
│     ├─> 建立 .backup 檔案                       │
│     └─> 確保可還原性                            │
│                                                  │
│  5. 瓶裝精華版本                                │
│     ├─> 寫入蒸餾後的 spec.md                    │
│     ├─> 執行自洽性檢查                          │
│     └─> 保留原始備份                            │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 蒸餾當前目錄的所有 spec 文檔
/distill-spec

# 2. 蒸餾指定路徑的 spec 文檔
/distill-spec ai-specs/modules
/distill-spec ai-specs/watchlist-spec.md
/distill-spec ./ai-specs

# 3. 預覽模式（不實際修改檔案）
/distill-spec --dry-run
/distill-spec ai-specs/modules --dry-run

# 4. 指定蒸餾程度
/distill-spec --aggressive       # 高純度蒸餾，只保留決策精華
/distill-spec ai-specs/watchlist-spec.md --moderate      # 標準蒸餾，平衡精華與細節
/distill-spec --conservative    # 輕度蒸餾，只去除重複和矛盾

# 5. 特定功能
/distill-spec --resolve-conflicts     # 重點處理矛盾內容
/distill-spec --merge-duplicates      # 重點處理重複內容
/distill-spec --restructure          # 重點處理結構問題
```

### 參數說明

- **無參數**: 蒸餾當前目錄下的所有 `*-spec.md` 檔案
- **路徑參數**: 蒸餾指定路徑下的 spec 文檔
- **--dry-run**: 預覽模式，顯示蒸餾結果但不執行
- **--aggressive**: 高純度蒸餾，只保留關鍵決策和核心規格
- **--moderate**: 標準蒸餾（預設），平衡精華與重要細節
- **--conservative**: 輕度蒸餾，只去除重複和明顯矛盾
- **--resolve-conflicts**: 重點處理文檔矛盾和一致性问题
- **--merge-duplicates**: 重點處理重複內容的合併
- **--restructure**: 重點處理文檔結構和組織問題

### 輸出範例

```
🔥 開始蒸餾 ai-specs/modules/watchlist-spec.md...
   📊 原料狀態: 523 行，8 個主要章節
   ⚠️  檢測到冗餘濃度過高，建議執行蒸餾提純

⚗️  分析文檔品質...
   ✓ 識別重複內容: 4 個重複區塊
   ✓ 識別過時規格: 3 個舊版 API 描述
   ✓ 識別矛盾陳述: 2 個版本不一致
   ✓ 識別決策精華: 8 個關鍵技術決策

🧪 蒸餾結果預覽 (moderate 純度):
   🎯 精華版本: 約 287 行 (-45% 體積)
   🗑️  去除雜質: 重複規格、過時參數、冗長範例
   🔧 解決矛盾: 2 個版本不一致問題
   💧 保留精華: 8 個重要架構決策和 Tradeoff 分析

🧪 執行蒸餾過程...
   ✓ 封存原始原料: specs/modules/watchlist-spec.md.backup
   ✓ 合併重複內容
   ✓ 解決矛盾陳述
   ✓ 重整文檔結構
   ✓ 蒸餾提煉完成
   ✓ 自洽性檢查通過

✨ specs/modules/watchlist-spec.md 蒸餾完成！純度提升，決策清晰。

📥 原料備份位置: specs/modules/watchlist-spec.md.backup
🔄 如需還原: cp specs/modules/watchlist-spec.md.backup specs/modules/watchlist-spec.md
```

---

## 📄 內容分類規則

### 精華識別模式

```markdown
# 精華內容特徵（高沸點，需要保留）
## 🎯 架構決策
## ⚖️ Tradeoff 分析
## 📋 決策背景
## 🔧 核心技術規格
## ✅ 關鍵驗收標準
## 🔄 版本相容性政策
## 🚫 替代方案考量
```

### 雜質識別模式

```markdown
# 雜質內容特徵（低沸點，可以蒸發）
### 重複規格描述
### 過時版本資訊
### 具體配置參數
### 冗長程式碼範例
### 臨時技術選擇
### 詳細環境設定
### 重複檢查項目
```

### 矛盾識別模式

```markdown
# 矛盾內容特徵（需要解決）
- 版本號不一致
- 相反的技術選擇
- 衝突的性能要求
- 矛盾的約束條件
- 不一致的命名規範
```

### 蒸餾分餾邏輯（含技術決策脈絡分析）

```python
def analyze_spec_context(content: str, section_title: str) -> dict:
    """
    技術規格文檔脈絡分析 - 理解設計意圖和決策背景

    回傳:
    - spec_type: "architecture_decision", "api_specification", "performance_requirement", "implementation_detail"
    - design_intent: 設計意圖分析
    - decision_context: 決策上下文
    - false_positive_risk: False Positive 風險評估
    """

    spec_contexts = {
        "architecture_decision": {
            "keywords": ["架構", "設計", "選擇", "tradeoff", "取捨", "權衡"],
            "patterns": ["## 架構決策", "## 設計選擇", "## 技術選型"],
            "characteristics": "高層次技術決策，包含權衡分析",
            "preserve_priority": "high"
        },
        "api_specification": {
            "keywords": ["API", "介面", "端點", "簽名", "規格"],
            "patterns": ["## API 介面", "## 端點定義", "## 規格說明"],
            "characteristics": "具體介面定義和規格描述",
            "preserve_priority": "medium-high"
        },
        "performance_requirement": {
            "keywords": ["性能", "基準", "指標", "延遲", "吞吐量"],
            "patterns": ["## 性能要求", "## 基準", "## 指標"],
            "characteristics": "性能相關的要求和基準",
            "preserve_priority": "high"
        },
        "implementation_detail": {
            "keywords": ["實作", "具體", "參數", "配置", "範例"],
            "patterns": ["## 實作細節", "## 配置說明", "## 範例"],
            "characteristics": "具體實作細節和配置參數",
            "preserve_priority": "low-medium"
        }
    }

    # 分析上下文類型
    context_scores = {}
    for ctx_type, indicators in spec_contexts.items():
        score = 0
        for kw in indicators["keywords"]:
            if kw in content:
                score += content.count(kw) * 2
        for pattern in indicators["patterns"]:
            if pattern in content:
                score += 3
        context_scores[ctx_type] = score

    # 判斷主要上下文
    if max(context_scores.values()) > 0:
        primary_context = max(context_scores, key=context_scores.get)
    else:
        primary_context = "implementation_detail"  # 預設為實作細節

    return {
        "spec_type": primary_context,
        "context_description": spec_contexts[primary_context]["characteristics"],
        "preserve_priority": spec_contexts[primary_context]["preserve_priority"],
        "all_scores": context_scores
    }

def enhanced_classify_spec_content(content: str, section_title: str, context_info: dict) -> dict:
    """
    增強蒸餾分餾邏輯 - 結合技術決策脈絡分析

    參數:
    - content: 內容文本
    - section_title: 章節標題
    - context_info: 技術規格脈絡分析結果

    回傳:
    {
        "type": "essence/impurity/conflict/uncertain/context_preserve",
        "priority": "high/medium/low",
        "action": "keep/merge/resolve/remove/condense",
        "reason": "決策原因說明"
    }
    """

    spec_type = context_info["spec_type"]
    preserve_priority = context_info["preserve_priority"]

    # 基於上下文調整分類策略
    context_rules = {
        "architecture_decision": {
            "preserve_keywords": ["決策", "選擇", "tradeoff", "權衡", "原因", "背景"],
            "impunity_keywords": ["具體範例", "配置細節", "實作參數"],
            "default_action": "keep",
            "rationale": "架構決策包含重要權衡分析，應予保留"
        },
        "api_specification": {
            "preserve_keywords": ["核心", "關鍵", "重要", "主要", "必要"],
            "impunity_keywords": ["過時範例", "詳細範例", "配置範例"],
            "default_action": "condense",  # 縮減而非移除
            "rationale": "API 規格可簡化但核心介面定義需保留"
        },
        "performance_requirement": {
            "preserve_keywords": ["基準", "指標", "要求", "目標", "關鍵"],
            "impunity_keywords": ["具體測試數據", "詳細配置", "實作細節"],
            "default_action": "keep",
            "rationale": "性能要求是重要的約束條件"
        },
        "implementation_detail": {
            "preserve_keywords": ["關鍵", "必要", "核心", "重要"],
            "impunity_keywords": ["具體參數", "詳細範例", "配置值", "過時版本"],
            "default_action": "distill",
            "rationale": "實作細節通常可以簡化"
        }
    }

    rules = context_rules.get(spec_type, context_rules["implementation_detail"])

    # 檢查保留關鍵詞
    preserve_score = sum(1 for kw in rules["preserve_keywords"] if kw in content)
    impunity_score = sum(1 for kw in rules["impunity_keywords"] if kw in content)

    # 判斷邏輯
    if preserve_score > impunity_score * 1.3:
        return {
            "type": "essence",
            "priority": "high",
            "action": "keep",
            "reason": rules["rationale"]
        }
    elif impunity_score > preserve_score * 1.3 and spec_type != "architecture_decision":
        return {
            "type": "impurity",
            "priority": "medium",
            "action": "remove",
            "reason": rules["rationale"]
        }
    elif spec_type in ["api_specification", "implementation_detail"]:
        return {
            "type": "context_preserve",
            "priority": "medium",
            "action": rules["default_action"],
            "reason": rules["rationale"]
        }
    else:
        return {
            "type": "uncertain",
            "priority": "low",
            "action": "review",
            "reason": "需要人工判斷的邊界情況"
        }

def classify_spec_content(content: str, section_title: str = "") -> dict:
    """
    主蒸餾分餾邏輯 - 整合傳統關鍵詞分析和現代技術決策脈絡分析

    回傳:
    {
        "type": "essence/impurity/conflict/uncertain/context_preserve",
        "priority": "high/medium/low",
        "action": "keep/merge/resolve/remove/condense",
        "context_analysis": "上下文分析結果",
        "reason": "決策原因"
    }
    """

    # 第一步：技術規格脈絡分析
    context_info = analyze_spec_context(content, section_title)

    # 第二步：矛盾檢測（優先級最高）
    conflict_keywords = [
        "矛盾", "不一致", "衝突", "相反",
        "但是之前", "然而現在", "與此不同",
        "version", "版本", "舊版", "新版"  # 版本矛盾
    ]

    conflict_score = sum(1 for kw in conflict_keywords if kw.lower() in content.lower())
    if conflict_score > 0:
        return {
            "type": "conflict",
            "priority": "high",
            "action": "resolve",
            "context_analysis": context_info,
            "reason": "檢測到潛在矛盾或版本不一致"
        }

    # 第三步：增強分類決策
    enhanced_result = enhanced_classify_spec_content(content, section_title, context_info)
    enhanced_result["context_analysis"] = context_info

    # 第四步：傳統關鍵詞分析（作為備用驗證）
    if enhanced_result["type"] in ["essence", "impurity"]:
        return enhanced_result

    # 備用傳統邏輯（僅作最後驗證）
    decision_keywords = [
        "決策", "選擇", "tradeoff", "取捨", "權衡",
        "架構", "設計", "原因", "背景", "動機",
        "替代方案", "考量", "分析"
    ]

    spec_keywords = [
        "核心 API", "關鍵介面", "性能基準",
        "驗收標準", "相容性", "版本政策"
    ]

    impurity_keywords = [
        "具體參數", "詳細範例", "配置值",
        "臨時決定", "過時版本", "重複描述"
    ]

    essence_score = sum(1 for kw in decision_keywords + spec_keywords if kw in content)
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

## 📝 精簡版 Spec 模板

### 標準模板結構

```markdown
# [模組名稱] 技術規格

## 📋 概述
規格文檔的目的、適用範圍和核心目標

## 🎯 架構決策

### 關鍵技術選擇
- **決策 1**: [選擇描述]
  - **背景**: [決策原因]
  - **Tradeoff**: [取捨分析]
  - **替代方案**: [為何不選其他方案]

### 重要架構模式
- **模式 1**: [模式描述]
- **模式 2**: [模式描述]

## 🔧 核心技術規格

### API 介面定義
- **關鍵端點**: [重要 API 列表]
- **資料結構**: [核心資料模型]

### 性能要求
- **響應時間**: [關鍵性能指標]
- **吞吐量**: [重要基準]

## ✅ 驗收標準

### 功能驗收
- **核心功能**: [重要驗收條件]

### 品質驗收
- **性能基準**: [關鍵品質指標]

## 🔄 版本相容性

### 版本政策
- **版本策略**: [重要版本政策]

### 遷移支援
- **升級路徑**: [關鍵遷移考量]

## 🚫 替代方案考量

- **方案 A**: [為何不選擇的原因]
- **方案 B**: [為何不選擇的原因]
```

---

## 🎯 蒸餾策略

### 觸發條件檢查

**自動檢測指標**:
- 文檔行數超過 500 行
- 重複內容比例 > 20%
- 版本矛盾數量 > 3 個
- 架構決策清晰度 < 60%

**手動觸發時機**:
- 團隊反饋 spec 文檔混亂
- 技術決策不一致時
- 定期文檔維護（每季度）
- 版本升級前整理

### 蒸餾步驟

1. **封存原始原料**: 自動建立 `.backup` 檔案
2. **品質分析**: 執行重複檢測、矛盾識別、結構分析
3. **衝突解決**: 處理版本不一致和矛盾陳述
4. **內容合併**: 合併重複描述，統一技術決策
5. **結構重整**: 重新組織文檔結構，提高可讀性
6. **蒸餾提煉**: 產出精華版本
7. **自洽性驗證**: 檢查文檔一致性和完整性
8. **瓶裝成品**: 寫入精華版本，保留備份

### 風險控制

- **可還原性**: 保留原始原料備份
- **漸進式蒸餾**: 支援不同純度和專項處理選項
- **衝突優先**: 優先處理矛盾和不一致問題
- **決策保留**: 確保重要架構決策不遺失

---

## 💡 蒸餾最佳實踐

### 文檔維護原則
1. **定期蒸餾**: 每季度評估 spec 文檔品質
2. **決策導向**: 專注於保留「為什麼」而非「怎麼做」
3. **衝突及時處理**: 發現矛盾立即解決
4. **版本同步**: 與實際實現保持同步

### 內容組織原則
1. **決策優先**: 架構決策和 Tradeoff 分析最重要
2. **去除重複**: 相同內容只保留最精確的版本
3. **解決矛盾**: 確保整個文檔的一致性
4. **結構清晰**: 使用統一的模板和組織方式

---

> 💡 **蒸餾哲學**: 讓 spec 文檔成為高純度的技術決策指南，如同一瓶精緻的蒸餾酒，濃縮了最寶貴的架構智慧。蒸餾過程確保開發團隊能快速理解關鍵決策，而不被重複細節干擾。

> 🤖 **AI 協作價值**: 蒸餾後的 spec 文檔對 AI 協作開發極具價值。清晰的架構決策和 Tradeoff 分析讓 AI 能準確理解技術選擇背景，避免提出不切實際的建議。