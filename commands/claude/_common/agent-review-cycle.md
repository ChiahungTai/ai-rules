# Agent Review Cycle — Agent Tool 審查範本（2-perspective）

> **載入時機**：非 ultracode 路徑（effort < ultracode 或 max-agents = 1）。ultracode 路徑用 Workflow，見 [workflow-review-pattern.md](./workflow-review-pattern.md)。

Writer/Reviewer 分離的品質閘門 — 用獨立 Agent context 審查，避免主 LLM 審自己的 code。agent 類型一律 `Explore`（read-only by design）。

---

## 核心設計：2-perspective review（固定兩 agent）

**觀察**：同樣讀 diff、同樣方法論的多個 agent **共享 writer 的 blind spot** — 都被同一份 context（diff / EP / 維度 checklist）錨定。**兩個異質 perspective 的 agent，覆蓋比多個同錨定的 agent 更廣**（多樣性 > 數量）。

| Agent | context | 審什麼 | 補的 blind spot |
|-------|---------|--------|----------------|
| **① Intent-anchored** | UC / EP Scenario Matrix + impl diff | 逐 UC 檢驗「impl 滿足嗎？漏了什麼意圖？偏離 EP 嗎？」 | 意圖偏差（build 偏離 plan） |
| **② Fresh** | **只有 impl diff，無 UC / 無 EP / 無意圖提示** | 「這 code 自身看哪裡怪 / 冗餘 / 缺 / 可疑 / 過度設計？」 | 正交盲區（writer 沒意識到的問題） |

> **② Fresh agent 刻意不給任何提示** — 它讀 code 的自身 merits，不被「這應該是做 X」的框架綁住，能挖出 intent agent 會 rationalize 掉的問題（「UC 說 X，所以這段一定是為 X」）。**新鮮 context 的價值就在無錨定 → 正交發現**。

### 為什麼固定 2 個（不再 adaptive 多維度 agent）

- **多樣性 > 數量**：舊設計的 4 個 dimension agent（正確性 / 架構 / 測試覆蓋 / EP 合規）共享錨定，邊際覆蓋遞減。2 個異質 perspective（intent + fresh）正交覆蓋更廣。
- **機械軸不靠 agent**：測試路徑覆蓋（新參數 `rg "<param>=" tests/`）是 `/build` 階段 2 硬閘門 + 階段 5d `/audit-test`，不靠 review agent 重複。正確性 / 架構由 fresh agent 讀 code 自然覆蓋；EP 合規由 intent agent 覆蓋。

---

## 自適應：max-agents

偵測 effort level 和 max-agents（見 [agent-workflow 並發表](../../../skills/agent-workflow/SKILL.md)）。

| 條件 | 模式 |
|------|------|
| max-agents ≥ 2 | **① Intent + ② Fresh** 兩 agent（預設） |
| max-agents = 1 | 單一 agent：intent-loaded + 明示「同時 fresh-eye 找 intent 之外的問題」（降級 2-in-1） |

印出確認：`[Review Agent] max=N, mode=2-perspective | single`

> review agent 模型（如 haiku）由 agent-workflow 並發表統一配置，spawn 時依表設定（模型配置議題見後續 task）。

---

## Agent Prompt

**兩 agent 共含**：
- `git diff` 範圍（所有產出的變更）
- 相關檔案路徑（必讀）
- [code-review-and-quality](../../../skills/code-review-and-quality/SKILL.md) 方法論
- rules-reminder 六條規則摘要（Agent 看不到 auto-loaded rules）

**① Intent-anchored 額外**：UC / EP 場景清單 + 「逐 UC 檢驗 impl 滿足度，標漏掉的意圖與 EP 偏離」

**② Fresh 額外**：明示「**不給任何 intent 提示，純讀 code 自身評估** — 哪裡怪、冗餘、缺、可疑、過度設計」

---

## 結果交接

兩 agent findings 合併 → 主 LLM invoke `/judge-review`（✅ / ❌ / ⚠️）→ apply ✅ 採納清單 → `ruff check --fix && ruff format`。

findings 若需持久化（跨 session / `.review/` / EP 回寫），用 [workflow-review-pattern.md](./workflow-review-pattern.md) 的 Finding Record 格式（跨命令追蹤標準）。

---

## 與 Workflow 路徑的關係

Workflow（ultracode）和 Agent Tool（本檔）**共存**，分支點在 effort level 偵測：

- effort = ultracode/xhigh 且 max-agents > 1 → [Workflow](./workflow-review-pattern.md)（schema + adversarial verify）
- 其餘 → 本檔（2-perspective）

兩路徑 findings 交接一致（同交主 LLM `/judge-review`）。
