# 蒸餾分類邏輯詳細規則

> 被引用自 `/distill-spec`。此文件包含蒸餾分類的完整 pseudo code 和模式列表。

---

## 內容分類模式識別

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

---

## 技術規格脈絡分析

分析 spec 文檔的設計意圖和決策背景，判斷上下文類型以調整分類策略。

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
```

---

## 增強蒸餾分餾邏輯

結合技術決策脈絡分析的內容分類邏輯。

```python
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
```

---

## 主蒸餾分餾邏輯

整合脈絡分析、矛盾檢測、增強分類、傳統關鍵詞分析的四步分類流程。

```python
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

## 四步分類流程摘要

```
classify_spec_content()
  │
  ├─ Step 1: analyze_spec_context()        → 判斷 spec_type（架構決策/API 規格/性能要求/實作細節）
  │
  ├─ Step 2: 矛盾檢測（優先級最高）         → conflict → resolve
  │
  ├─ Step 3: enhanced_classify_spec_content() → 結合上下文調整分類策略
  │
  └─ Step 4: 備用傳統關鍵詞分析             → 最後驗證
```
