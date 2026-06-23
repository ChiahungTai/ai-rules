---
description: "審查 Execution Plan 合理性（完整性、規範合規、一致性、遺漏風險、場景覆蓋）。/ep-review <EP路徑>"
when_to_use: "Review an Execution Plan for completeness, rules compliance, internal consistency, omission risks, and scenario coverage before implementation begins."
context: fork
agent: Explore
usage: "/ep-review <Execution Plan 路徑>"
argument-hint: "<Execution Plan 檔案路徑>"
allowed-tools: ["Read", "Grep", "Glob", "Agent", "Workflow"]
---

# /ep-review — Execution Plan 合理性審查

EP 審查員，在實作前審查 Execution Plan，確保計畫書完整、合規、可執行。

> **受眾**：LLM 執行鏈命令（layer 1 同 session 自判 / layer 2 跨 session），產出回寫 EP 餵回產 EP 的 LLM，**不給人看**。EP 的人類 viewport 是 `/deliverable-review --ep`（layer 3 方向）+ `/illustrate --ep`（layer 3 結構 viewport）。見 [CLAUDE.md](../CLAUDE.md)「命令的受眾視角」。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [review-engine](../skills/review-engine/SKILL.md) — 通用審查邏輯（嚴重度/信心水準/審查者自證/LSP 查證/審查模式判定規則/多層驗證）
- [arch-thinking](../skills/arch-thinking/SKILL.md) + [arch-viewport](../skills/arch-viewport/SKILL.md) — 架構視角 + 結構機械（F3 用）
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — code 審查方法論

Workflow 執行協調：[workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)（模式判定見 review-engine；本檔定義「審 EP profile」F1-F5 維度）

---

## 審查模式選擇

review 執行預設（force 獨立 / max-agents / model inherit）見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」—— 本命令僅定義 EP 特有 profile（F1-F5）+ 產出（回寫 EP）。模式判定規則（effort/max-agents → Workflow/Agent Tool/Main LLM）見 [review-engine](../skills/review-engine/SKILL.md)；啟用 F1-F5 五維度（下表），Workflow 執行細節（schema/腳本）見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md)。

**Workflow 模式**（判定條件見 [review-engine](../skills/review-engine/SKILL.md)）：

使用 Workflow tool，參照 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md) 腳本骨架。

| Workflow Phase | 說明 | Agent 數量 |
|----------------|------|-----------|
| Review | 平行 spawn 維度 agents | ≤ max-agents |
| Verify | must-fix findings → 1 verifier/finding | findings 數 |

**啟用維度**：

| 維度 Agent | 審查項目 | 優先級 |
|-----------|---------|--------|
| F1 完整性 | 驗收標準、檔案清單、依賴項、邊界情況 | P0 |
| F2 合規 | 命名、code-edit-constraints、CLAUDE.md | P0 |
| F3 一致性 | 段落依賴順序、檔案修改矛盾、語義約束 | P1 |
| F4 遺漏 | Demo、測試、__all__、配置、受影響模組 | P2 |
| F5 場景覆蓋 | Scenario Matrix 是否涵蓋 happy path、錯誤操作、邊界、效能期待差異 | P2 |

啟用維度數 > max-agents → 從低優先級（P2 起）合併至前一個 agent（不丟棄任何維度）。

每個 Review agent prompt 包含：
- EP 完整內容
- 該維度的檢查項目清單（F1-F5 各自定義）
- 計畫書提到的檔案路徑（必讀）
- 方法論引用（code-review-and-quality）
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）
- schema: DimensionVerdict（定義在 workflow-review-pattern.md）

Workflow 完成後回傳 `{confirmed, stats}` → Main LLM 合成 5 個 DimensionVerdict → 執行回寫（回寫原則見下方）。

印出確認：`[EP Review Mode] effort=ultracode, workflow=true, max=N`

**Agent Tool 模式**（Fallback；review 執行預設 force 獨立、不走 Main LLM —— 見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」；判定條件同見 review-engine）：

單一 Explore agent 做所有 5 維度（ep-review 特有配置，非 code-review 的 2-perspective）。印出確認：`[EP Review Mode] effort=standard, workflow=false`

---

## 五維度審查

### F1: 完整性檢查

每段是否有驗收標準？檔案是否完整列出？依賴項是否遺漏？邊界情況是否考量？Use LSP goToDefinition to verify file paths mentioned in EP actually contain the referenced symbols.

### F2: Rules 合規檢查

命名是否符合 `python-standards`？是否遵守 `code-edit-constraints`？是否有違反 `_ai-behavior-constraints` 的內容？是否需要更新 CLAUDE.md？

### F3: 一致性 + 架構視角檢查（承接 execution-plan 維度①②④）

- **段落一致性**：段落間依賴順序合理？對同一檔案的修改矛盾？技術方案一致？
- **語義約束**（共享型別、命名慣例、架構假設）是否標記？drift 檢查
- **依賴錨點 drift**：EP 對現有 code 的雙向錨定（定義端 + 消費端）是否 drift — 用 LSP `goToDefinition`/`findReferences` 驗證
- **分層依賴**（承接 execution-plan ①）：domain←use case←adapter←infra 依賴向內？有循環？— 視角見 [arch-thinking](../skills/arch-thinking/SKILL.md)，結構資料見 [arch-viewport](../skills/arch-viewport/SKILL.md)
- **bounded context**（承接 ②）：跨域存取 `_private`？邊界清楚？職責單一？

### F4: 遺漏風險檢查

Demo 檔案有規劃？測試有規劃？`__init__.py` 的 `__all__` 需要更新？配置檔案需修改？受影響的其他模組已列出？

### F5: 場景覆蓾度檢查

大型/中型變更必須有 Scenario Matrix。檢查：
- 場景是否涵蓋 happy path、錯誤操作、邊界案例、效能期待差異？
- 每個場景的「觸發 → 預期行為」是否具體可驗證？
- Checkpoint 語義是否與程式碼中的實際 checkpoint 對齊（snapshot / catalog / 無）？
- 矩陣中的「對應 UC」是否與 EP 段落的 UC 引用一致？
- 是否遺漏明顯的使用者情境（如回補多天、跨日、缺前置條件）？

小型變更（bug fix）跳過此維度。

### 「審 EP profile」維度映射表（與 execution-plan EP Review 共用，零失落）

execution-plan EP Review Cycle 的四維度 ↔ 本命令 F1-F5 對應（execution-plan 引用此 profile，不再自帶維度 — 見 S6）：

| execution-plan 維度 | 本命令歸屬 |
|---------------------|-----------|
| ①分層依賴（domain←use case←adapter←infra 向內？循環？） | F3 |
| ②bounded context（跨域 `_private`？） | F3 |
| ③use case 覆蓋（EP 撐得起 use case？） | F5 場景覆蓋 |
| ④兜底路徑驗證（複合） | 拆解 → 實作落差預見（深層思考）+ 語義約束 drift（F3）+ 依賴錨點 drift（F3）+ **兜底假設路徑驗證**（F3：EP 宣稱「X 段暴露/處理 Y」→ 驗證 X 的 code path 真經過 Y，追 call chain 附 path:line；不經過標「未驗證」非「handled」，Y 另開調查）+ Rules 合規（F2）+ 遺漏（F4）+ 內部一致性（F3） |

### 深層思考（第一性原理 + 第二層思考）

F1-F5 檢查「有沒有漏」，深層思考檢查「方向對不對」。
- **本質需求追問**：每段的核心目的？是否有更簡單的實現路徑？
- **技術方案驗證**：EP 選擇的方案是否基於對現有程式碼的正確理解？讀取相關檔案確認
- **實作落差預見**（承接 execution-plan 兜底④）：EP pseudo code 看起來對，接起來才發現的邊界/副作用/組件互動 — EP 預見極限，標記給 build 注意
- **連鎖後果追蹤**：EP 中的設計決策會導致什麼下游影響？至少追蹤兩層
- **如果錯了**：最壞情境？可以逆轉嗎？逆轉成本？

深層思考框架見 `~/.claude/rules/deep-thinking.md`

---

## 回寫原則

> **核心原則**：EP 是 `/build` 的唯一真相來源。審查發現不在 EP 裡 = 不存在。

> **適用範圍**：回寫由主 LLM 執行（非 Explore agent）。在 `/execution-plan` 流程中由主 LLM 自動完成；獨立 `/ep-review` 時，回寫紀錄供用戶參考手動套用至 EP。

build 可能由不同 LLM session 執行，無法存取審查報告。因此：

- **🔴 必須修正** → 審查結論前必須回寫 EP（修正段落內容或新增約束）
- **🟡 建議討論且被採納** → 回寫 EP（作為段落補充說明或新段落）
- **🟡 建議討論但未確認** → 回寫 EP（標記 `⚠️ 待確認：[說明]`），不留在報告裡等 build 自己看
- **禁止「build 再改」**：任何需要 build 執行的變更，必須寫入 EP 的對應段落。審查報告只記錄「已回寫什麼」，不代替 EP 承載實作指令

### 回寫格式

在 EP 開頭(研究摘要之後、UC 盤點之前)加 review 區段,用 Finding Record 表格(欄位定義見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md))。EP 場景「檔案:行」欄填「EP 段落」(如 S2):

```
## EP Review Findings

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| 1 | 🔴 必須修正 | S2 | ... | ... | implemented |
| 2 | 🟡 建議 | S3 | ... | ... | needs-confirmation |
```

回寫後:🔴 / 🟡-採納 → `implemented`(修正已入 EP);🟡-未確認 → `needs-confirmation`。

### 回寫驗證

回寫完成後，重新讀取 EP 確認修正已入檔。未回寫的發現不得標記為「已處理」。

---

## 技術約束

- **基於實際程式碼**：必須讀取計畫書提到的檔案確認存在
- **五維度覆蓋**：必須覆蓋 F1-F5
- **審查者自證**：提出問題前必須用 Read/Grep 查證宣稱。聲稱檔案存在 → 讀它；聲稱命名衝突 → 查 import 鏈；聲稱依賴順序有問題 → 追蹤執行順序。無法查證的宣稱標注「未驗證」
- **不實作**：審查階段不自動開始實作

---

## 邊界

- **Always**：完整讀取 EP、查證現有程式碼、覆蓋五維度、輸出結構化報告
- **Ask First**：重大架構問題時是否停止審查、格式不符標準時是否要求修正
- **Never**：不自動實作、不基於推測、不跳過維度

---

## 審查報告格式

```markdown
## 🔍 Execution Plan 審查報告

**檔案**: [計畫書路徑]
**段落數**: [N] 個

### ⚠️ 需要確認的問題

**🔴 必須修正**：[問題 + 修正方式]
**🟡 建議討論**：[問題 + 替代方案]
**ℹ️ 提醒事項**：[已處理項目說明]

### 📝 EP 回寫紀錄

列出已回寫至 EP 的修正（段落 + 修正摘要），供用戶快速確認。

### 審查結論
[可直接執行 / 有條件執行 / 需修正後重新審查]
```

---

## 流程位置

> **內建整合**：EP Review Cycle 已整合至 `/execution-plan`。獨立使用適用於手動修改 EP 後重新審查。

```
/spec（純輔助·需求釐清，可選）→ /execution-plan（含 EP Review）→ [/ep-validate] → /build（含 Agent Review）→ /code-review
```

前置：`/execution-plan`
後續：`/build`（→ `/code-review` → `/judge-review` → `/commit`；canonical review flow 見 [code-review.md](./code-review.md)）
