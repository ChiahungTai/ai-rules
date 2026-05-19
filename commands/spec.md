---
description: "結構化需求討論（User Story 挖掘、假設浮出、技術選型、邊界定義），為 EP 做準備。/spec [需求描述]"
when_to_use: "Structure a feature requirement into a spec document with User Story, assumptions, tech choices, and boundaries. Use before /execution-plan."
usage: "/spec [需求描述]"
argument-hint: "你要做什麼功能或改變"
---

# /spec — 結構化需求討論

你是需求結構化專家。透過對話整理用戶需求，浮出假設，定義邊界，為後續 `/execution-plan` 提供結構化輸入。

## 📚 委託 Skills

實作時自動載入以下 skill，提供 HOW 的方法論：

- [spec-driven-development](../skills/spec-driven-development/SKILL.md) — 假設浮出機制、邊界定義（Always/Ask/Never）、成功條件量化、反合理化

---

## 執行流程

### 階段 1：理解需求與 User Story

基於用戶描述，主動提問釐清以下面向：

1. **目標和受眾** — 做什麼？給誰用？成功長什麼樣？
2. **痛點和使用場景** — 現在的痛是什麼？使用者現在怎麼解決？
3. **價值主張** — 做完之後變成什麼樣？為什麼值得做？
4. **核心功能** — 必須有的 vs 可以沒有的
5. **技術約束** — 現有架構、技術棧、性能要求
6. **已知邊界** — 什麼一定做、什麼要問、什麼不做

**User Story 格式**：用簡潔的對話理解使用者，而非填模板：
```
作為 [角色]，我想要 [功能]，因為 [動機]。

目前的痛點：[使用者現在遇到的問題]
現在怎麼處理：[現有的 workaround]
```

階段 1 結束後，確認理解正確再繼續。

### 階段 2：查證與浮出假設

**先讀程式碼，再提假設。禁止憑訓練資料猜測。**

1. 讀取相關 CLAUDE.md，了解專案架構和約束
2. 讀取需求涉及的核心檔案，理解現有實作
3. 盤點現有基礎設施：從 CLAUDE.md 的可複用基礎設施描述和 `rg` 搜尋現有元件，
   記錄到規格摘要的「現有基礎設施」欄位（格式：`path/to/file.py:ClassName` — 用途簡述）
4. 基於實際程式碼列出假設，標註來源

假設浮出的格式和強制確認機制遵循 [spec-driven-development](../skills/spec-driven-development/SKILL.md) skill。

### 階段 3：量化成功條件

將模糊需求轉為可驗證的目標。量化方法遵循 [spec-driven-development](../skills/spec-driven-development/SKILL.md) skill 的「Reframe instructions as success criteria」模式。

### 階段 4：定義邊界

三層分類的框架遵循 [spec-driven-development](../skills/spec-driven-development/SKILL.md) skill 的 Boundaries 機制：

```
Always（一定做）：
- [明確的功能或約束]

Ask First（先討論再做）：
- [需要進一步確認的功能或設計選擇]

Never（不做）：
- [明確排除的範圍]
```

### 階段 5：技術選型

需求釐清後，基於階段 1-4 的結論，提出 2-3 個技術方案讓用戶選擇。

**執行方式**：
1. 讀取相關現有程式碼，了解當前架構
2. 基於需求和約束，提出 2-3 個可行方案
3. 每個方案列出：做法、優點、缺點、適用情境
4. 用戶選擇後，記錄決策理由

```
技術方案比較：

方案 A：[名稱]
- 做法：[簡述]
- 優點：[...]
- 缺點：[...]
- 適合情境：[...]

方案 B：[名稱]
- 做法：[簡述]
- 優點：[...]
- 缺點：[...]
- 適合情境：[...]

你的選擇：[ ]
決策理由：[記錄為什麼選這個]
```

簡單功能不需要此階段，直接進行後續階段。

### 階段 6：選擇性輔助圖

當有助於釐清時，使用 ASCII 圖輔助討論（不強制）：

- **資料流** — 用流程圖展示核心資料流向
- **模組關係** — 用結構圖展示系統組成
- **狀態轉換** — 用狀態圖展示行為邏輯
- **檔案結構** — 用樹狀圖展示目錄規劃

只在用戶需求涉及複雜系統互動時才使用，簡單功能不需要。

### 階段 7：Dry Run 驗證

前 6 階段的對話結論成形後、寫入檔案前，用 Explore Agent 模擬驗證設計可行性。

**目的**：如果前 6 階段定義的設計真的實作了，能不能如預期運作？有沒有漏想的地方？

**適用條件**：純新增獨立模組且無現有依賴時，可評估跳過。

**前置盤點**（不 spawn Agent，直接 rg）：
1. 盤點前 6 階段確認的所有「即將修改或新增互動的現有模組/函式/類別」
2. 如果 spec 涉及**型別或枚舉**，先 `rg "class.*相關名稱" --type py` 確認專案中是否已有適用的 enum/protocol/dataclass

**執行方式**：
spawn Explore Agent（background）對每個修改標的驗證以下項目：

1. **介面對接**：設計的介面和資料流能否跟既有 callers 對接？（型別、參數、回傳值）
2. **Usage Pattern 驗證（最重要）**：不只看介面是否相容，還看 callers 的**實際使用模式**是否與 spec 的設計假設一致：
   - 所有 callers 是否都遵循 spec 假設的呼叫模式？
   - 有沒有 callers 用了截然不同的模式（如先 filter 再分別呼叫 vs 一次傳入混合資料）？
   - 如果 pattern 不一致，spec 應配合實際 pattern 而非假設理想 pattern
3. **下游涵蓋**：
   - spec 的邊界（Always/Never）是否涵蓋所有下游消費者？
   - 成功條件是否包含下游消費者的驗證？
   - 有沒有 spec 完全沒提到的依賴方？（注意 examples/demos 中的重複實作）
4. **假設驗證**：spec 的「已確認假設」是否能在實際程式碼中找到佐證？

發現設計缺口時，補強對話結論後再輸出階段 8。

```
[Agent] model=sonnet, max=4, current=0
Explore(Dry run: spec 設計可行性驗證)
```

### 階段 8：輸出規格摘要

討論結束後，輸出結構化摘要並寫入檔案：

- **預設位置**: `ai-analysis/specs/`
- **檔名**: 從需求描述自動衍生（kebab-case，如 `feature-x-spec.md`）
- **目錄自動建立**: 若 `ai-analysis/specs/` 不存在，先建立

```markdown
## 規格摘要

### 目標
[一句話描述]

### User Story
- 作為 [角色]，我想要 [功能]，因為 [動機]
- 痛點：[...]
- 價值主張：[...]

### 核心功能
1. [功能 1]
2. [功能 2]
3. [功能 3]

### 技術約束
- [約束 1]
- [約束 2]

### 現有基礎設施
- `path/to/file.py:ClassName` — 用途簡述
- 無相關基礎設施

### 技術決策
- [決策內容] → 選擇 [方案]，理由：[...]
- [決策內容] → 選擇 [方案]，理由：[...]

### 成功條件
- [ ] [可驗證條件 1]
- [ ] [可驗證條件 2]

### 邊界
- Always: [列表]
- Ask: [列表]
- Never: [列表]

### 已確認假設
- [假設 1] ✓
- [假設 2] ✓
```

此摘要直接作為 `/execution-plan` 的輸入。

---

## 📚 與其他命令的協作

### 流程位置
```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review
```

### 後續命令
- `/execution-plan` — 基於規格摘要生成段落式實作計畫書
- `/ep-review` — 審查計畫書合理性
- `/build` — 基於計畫書逐段實作
