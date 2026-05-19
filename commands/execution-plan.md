---
description: "段落式實作計畫書生成器，基於 /spec 規格摘要生成 Self-Contained Segments。/execution-plan \"任務描述\" [PROMPT檔案]"
when_to_use: "Generate a segmented Execution Plan from a spec. Creates self-contained segments with context, pseudo code, validation strategy, and dependency anchors."
usage: "/execution-plan \"實作任務描述\" [PROMPT檔案路徑]"
argument-hint: "<實作任務描述> [可選：PROMPT檔案路徑]"
---

# /execution-plan — 段落式實作計畫書生成器

基於 `/spec` 的規格摘要，生成段落式實作計畫書。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [planning-and-task-breakdown](../skills/planning-and-task-breakdown/SKILL.md) — 依賴圖分析、垂直切片、task sizing

---

## 核心概念：Self-Contained Segment

每個段落都是**完全獨立的功能單元**，AI 只需讀取該段落就能完成實作。

特徵：Context 獨立 / 功能完整 / 驗證自足 / 執行獨立

---

## 段落設計標準

每個段落必須包含：

### 1. Context

- **背景資訊**：基於 `/spec` 規格摘要
- **依賴關係**：與其他段落的依賴和整合點
- **語義約束**：與其他段落共享的隱含假設（型別定義、命名慣例、架構決策）。無則寫「無」，有則寫「與 S{N} 共享 [具體假設]」
- **基礎設施盤點**：設計 pseudo code 前的必做步驟（讀 CLAUDE.md 可複用基礎設施 → `rg` 搜尋相關元件 → 列出可複用元件或寫「無」）
- **依賴錨點**：EP 對現有程式碼的引用錨定（格式：`function_name` → `path/to/file.py:123`）。`/build` 執行前驗證錨點，drift 時先更新 EP
- **技術選型** + **成功標準**

### 2. 核心實作要點

主要類別、關鍵方法、設計決策、整合方式

### 3. Pseudo Code

類別結構 + 方法實現 + Call Stack + 錯誤處理。檔案結構用樹狀展示（非 mermaid）。空殼 class 用詳細註解標示設計意圖。

### 4. 驗證策略

Examples 設計 + 測試計畫 + 完成檢查 + 整合測試

---

## 段落劃分原則

依賴圖分析、垂直切片、task sizing 遵循 [planning-and-task-breakdown](../skills/planning-and-task-breakdown/SKILL.md)。

EP 專屬約束：
- **語義顯式化**：段落間共享的隱含假設必須顯式標記
- **驗證自足性**：每段有獨立驗證策略

---

## 段落設計檢查清單

- [ ] 標題明確且獨立
- [ ] Context 包含所有必要背景
- [ ] Pseudo Code 具體可執行
- [ ] 驗證策略完整可執行
- [ ] 整合點清晰定義
- [ ] 語義約束已顯式標記
- [ ] 基礎設施盤點已完成
- [ ] 依賴錨點已標記

---

## Dry Run 驗證

EP 草稿完成後、寫入前，spawn Explore Agent 驗證：

1. **Call Stack 可行性**：pseudo code 每步能否跑通？
2. **Pattern Alignment（最重要）**：EP 設計假設的 usage pattern 是否與 callers 實際 pattern 一致？
3. **下游依賴發現**：有沒有 EP 沒提到的 callers？
4. **邊界條件**：空值、null、缺少欄位等

發現缺口時補強 EP 再輸出。

---

## 輸出

- **位置**：`ai-analysis/execution-plans/`
- **檔名**：從任務描述自動衍生（kebab-case）
- **結構**：實作總覽 → 段落劃分策略 → 各段落（Context → 要點 → Pseudo Code → 驗證）→ 整合策略

---

## 流程位置

```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review
```

前置：`/spec`
後續：`/ep-review` → `/verify-review` → `/build`
