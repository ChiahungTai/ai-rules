---
description: "結構化需求討論（User Story 挖掘、假設浮出、技術選型、邊界定義），為 EP 做準備。/spec [需求描述]"
when_to_use: "Structure a feature requirement into a spec document with User Story, assumptions, tech choices, and boundaries. Use before /execution-plan."
usage: "/spec [需求描述]"
argument-hint: "你要做什麼功能或改變"
---

# /spec — 結構化需求討論

需求結構化專家。透過對話整理用戶需求，浮出假設，定義邊界，為 `/execution-plan` 提供結構化輸入。

委託 Skills：
- [spec-driven-development](../skills/spec-driven-development/SKILL.md) — 假設浮出、邊界定義、成功條件量化

---

## 執行流程

### 階段 1：理解需求與 User Story

主動提問釐清：目標和受眾、痛點和使用場景、價值主張、核心功能、技術約束、已知邊界。

User Story 格式：
```
作為 [角色]，我想要 [功能]，因為 [動機]。
目前的痛點：[問題]
現在怎麼處理：[workaround]
```

### 階段 2：查證與浮出假設

**先讀程式碼，再提假設。禁止憑訓練資料猜測。**

1. 讀取相關 CLAUDE.md + 核心檔案
2. 盤點現有基礎設施（CLAUDE.md 的可複用基礎設施 + `rg` 搜尋）
3. 基於實際程式碼列出假設，標註來源

假設浮出格式和強制確認遵循 [spec-driven-development](../skills/spec-driven-development/SKILL.md)。

### 階段 3：量化成功條件

將模糊需求轉為可驗證的目標。

### 階段 4：定義邊界

```
Always（一定做）：[列表]
Ask First（先討論再做）：[列表]
Never（不做）：[列表]
```

### 階段 5：技術選型

需求釐清後，提出 2-3 個技術方案（做法、優缺點、適用情境），用戶選擇並記錄決策理由。簡單功能可跳過。

### 階段 6：選擇性輔助圖

複雜系統互動時使用 ASCII 圖（資料流、模組關係、狀態轉換、檔案結構），簡單功能不需要。

### 階段 7：Dry Run 驗證

結論成形後、寫入前，spawn Explore Agent 驗證：
1. **介面對接**：設計能否跟既有 callers 對接
2. **Usage Pattern 驗證**（最重要）：callers 的實際使用模式是否與 spec 假設一致
3. **下游涵蓋**：邊界是否涵蓋所有下游消費者
4. **假設驗證**：已確認假設能否在程式碼中找到佐證

純新增獨立模組且無現有依賴時可跳過。

### 階段 8：輸出規格摘要

寫入 `ai-analysis/specs/{feature-name}-spec.md`：

```markdown
## 規格摘要
### 目標 / User Story / 核心功能 / 技術約束
### 現有基礎設施
- `path/to/file.py:ClassName` — 用途簡述
### 技術決策 / 成功條件 / 邊界 / 已確認假設
```

此摘要直接作為 `/execution-plan` 的輸入。

---

## 流程位置

```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review
```
