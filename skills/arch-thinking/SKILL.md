---
name: arch-thinking
description: Clean Architecture + DDD 設計視角 — 用分層依賴規則（domain←use case←adapter←infra）、bounded context 邊界、use case 驅動檢視整體結構。用於 spec/EP/build/review 的設計決策，自問「新東西落哪層？依賴方向對嗎？邊界清楚嗎？消費者是誰？」。觸發詞：架構設計、clean architecture、分層、bounded context、use case 驅動、DDD、SOLID、依賴方向、模組邊界。
---

# Architecture Thinking — Clean Architecture + DDD 設計視角

用 Clean Architecture + DDD 視角檢視結構的設計視角。**視角非模板** — 注入思考，不強制分層、不過度工程。頂層總綱見 [ai-development-guide.md](../../ai-development-guide.md)「架構設計紀律」。

## 三主線 + 流程注入點

### ① 依賴規則（Clean Architecture 分層）

domain ← use case ← adapter ← infra，依賴**向內**（內層不依賴外層）。

設計時自問：
- 新東西落哪層？
- 依賴方向對嗎（有無下層 import 上層）？
- 有無循環？

**流程注入**：
- spec：研究「既有分層？」（非「功能怎麼塞」）
- EP / illustrate：畫提案 city map「新東西落哪層？」
- build：遵循依賴方向
- review：查反向依賴、循環

### ② bounded context（DDD 邊界）

每個 context 邊界清楚，**不跨域直接存取內部**（`_private`）。

設計時自問：
- 這該在哪個 context？
- 有無跨域直接存取？

**流程注入**：
- spec：邊界定義（Always / Ask First / Never）
- EP / illustrate：city map 凸顯跨域存取
- review：findReferences 查跨域

### ③ use case 驅動

先問**消費者要什麼行為**，再設計結構。

設計時自問：
- 消費者是誰？
- 結構撐得起 use case 嗎？

**流程注入**：
- spec：UC 盤點
- illustrate：畫 use case flow「結構撐得起嗎」（人 gate）
- EP：段落引用 UC
- 驗證：回歸 use case 行為

## mosaic 範例（領域特定，規則通用）

- **domain**：策略訊號、風控規則（純邏輯，無 IO）
- **use case**：回測、下單、數據更新（編排 domain）
- **adapter**：NT（執行）、SJ（行情）、catalog（持久化）（接外部）
- **infra**：DB、SDK、檔案系統（外部細節）

依賴向內：domain 不依賴 use case / adapter / infra；adapter 依賴 use case interface（非反過來）。

## RC-2 邊界：bounded context vs module boundary

- **bounded context（本 skill）**：DDD 語義邊界 — context 間不跨域存取內部。檢視**整體結構**。
- **module boundary（[api-and-interface-design](../api-and-interface-design/SKILL.md)）**：介面合約邊界 — Hyrum's Law、Validate at Boundaries、合約穩定性。**設計介面**。

**分工**：設計 API / 介面 → `api-and-interface-design`；檢視整體結構 / 分層 → 本 skill。兩者互補（介面是 adapter 邊界的具體化）。

## 與既有 skill 邊界

- [debugging-and-error-recovery](../debugging-and-error-recovery/SKILL.md)：除**自己 code** 的 bug。本 skill 是**設計視角**（預防性，非除錯）。
- [source-driven-development](../source-driven-development/SKILL.md)：實作 **grounding 於文檔**。本 skill 是結構視角（非文檔查證）。
- [acceptance-evidence](../../rules/acceptance-evidence.md)：測試 / 驗收**證據階層**。本 skill 是設計層（證據階層是驗收層）。
- [api-and-interface-design](../api-and-interface-design/SKILL.md)：見上 RC-2 邊界。

## 不適用

- 除錯 → `debugging-and-error-recovery`
- 查 API 用法 / 文檔 → `source-driven-development` / `context7-mcp`
- 測試策略 → `test-driven-development` / `validation-strategy`
- 強制套四層模板（本 skill 是視角，非模板）
