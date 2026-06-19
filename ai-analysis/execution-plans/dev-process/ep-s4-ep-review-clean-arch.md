# EP: S4 EP review 換 Clean Arch 視角 + top-down + agents→skills

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S4 段展開）
> **本 EP**: execution-plan EP Review Cycle 4 維度偏泛泛（完整性/可行性/風險/一致性），改 **Clean Architecture + use case 視角**（S0c architecture-thinking）+ **top-down 審查順序**（先結構後正確性）+ **agents→skills 統一**探討（agent 審查知識沉 skill）。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

EP Review Cycle（[execution-plan.md](../../../commands/execution-plan.md) `:215-275`）4 維度偏泛泛，缺架構紀律層視角（整脊根本問題：體系缺架構紀律層）。S0c [architecture-thinking](../../../skills/architecture-thinking/SKILL.md) skill 已建（分層依賴/bounded context/use case 驅動），EP review 該引用。**top-down**（B7）：先結構（分層/邊界）後細部正確性 — 結構錯了正確性審也白費。**agents→skills**（B12）：agent 審查知識沉 skill 統一引用，agent prompt 只組裝。

**本 EP 範圍**（master S4）：改 execution-plan.md EP Review Cycle（維度表 + Fallback + agent prompt）+ 流程位置（pre-EP illustrate checkpoint）。

**Scope out**：S5 code-review axis3（消費端，S5 子 EP）；S8 綱要 EP 機制（與本 EP 同改 execution-plan，但獨立概念，S8 子 EP）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S4a** | 維度表 + Fallback 改 Clean Arch 視角 + top-down 明文 | S0c |
| **S4b** | agent prompt 引用 skill（agents→skills 統一）+ 流程位置加 pre-EP illustrate | S4a |

2 段序列（維度表先 → agent prompt/流程位置）。

---

## UC 盤點（docs mode）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 段落式實作計畫書（含 EP Review） | `commands/execution-plan.md` | ✅ → S4 EP Review 換 Clean Arch 視角 + top-down |

---

## Scenario Matrix（中型變更，docs mode）

| SM | 情境 | 觸發 | 預期行為 | UC |
|----|------|------|---------|-----|
| SM-4 | EP review agent 審 EP | `/execution-plan` EP Review | Clean Arch 視角（分層/邊界/use case 覆蓋/兜底）+ top-down（結構先）；agent 引用 skill 統一 | 段落計畫 |

---

## S4a: 維度表 + Fallback 改 Clean Arch + top-down

### Context
- **背景**：維度表（`:229-238`）4 維度偏泛泛，改 Clean Arch + use case 視角。Fallback（`:251-266`）對應改 + top-down 明文。
- **依賴錨點**：[execution-plan.md](../../../commands/execution-plan.md) `:229-238`（維度表）、`:251-266`（Fallback）；視角來源 [architecture-thinking](../../../skills/architecture-thinking/SKILL.md)（S0c 三主線）
- **成功標準**：
  - [ ] 維度表（`:229-238`）4 維度 → Clean Arch：**分層依賴**（domain←use case←adapter←infra，依賴向內）/ **bounded context**（不跨域存取 `_private`）/ **use case 覆蓋**（消費者要什麼行為）/ **兜底路徑驗證**（EP 預見極限，實作落差）
  - [ ] Fallback（`:251-266`）四維度對應改 Clean Arch
  - [ ] **top-down 明文**：EP review 先結構（分層/邊界）後細部正確性（結構錯了正確性審白費）

### 修改要點
1. **維度表**（`:229-238`）：4 維度改 Clean Arch 四視角
2. **Fallback**（`:251-266`）：對應改 + top-down 明文

### 驗證策略（docs mode）
- **rg 閘門**：`rg "分層依賴|bounded context|use case 覆蓋|兜底路徑|top-down" commands/execution-plan.md` → 命中

---

## S4b: agent prompt 引用 skill + 流程位置 pre-EP illustrate

### Context
- **背景**：agent prompt 引用 architecture-thinking + architecture-viewport（知識沉 skill，agents→skills 統一）。流程位置（`:323-331`）加 pre-EP illustrate checkpoint（彈性軟 gate）。
- **依賴錨點**：[execution-plan.md](../../../commands/execution-plan.md) `:323-331`（流程位置）；agent prompt 段
- **成功標準**：
  - [ ] agent prompt 引用 [architecture-thinking](../../../skills/architecture-thinking/SKILL.md) + [architecture-viewport](../../../skills/architecture-viewport/SKILL.md)（agent 知識沉 skill，非內嵌）
  - [ ] **agents→skills 統一探討**明文：探討 agent 審查能力是否該統一沉 skill（非各命令內嵌），對齊 #B12
  - [ ] 流程位置（`:323-331`）加 pre-EP illustrate checkpoint（對話 → illustrate → 確認 → execution-plan，彈性軟 gate）

### 修改要點
1. **agent prompt**：引用 architecture-thinking + architecture-viewport；加 agents→skills 探討段
2. **流程位置**（`:323-331`）：加 pre-EP illustrate（彈性軟 gate）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "architecture-thinking|architecture-viewport|agents.*skills|統一.*沉|pre-EP" commands/execution-plan.md` → 命中

---

## 收尾

### 回母 EP
本 EP 完成（master S4 build+commit）後，master 綱要 S4 段標 ✅。

### 風險與緩解
- 維度表改 Clean Arch 可能讓既有 EP Review 慣性失效 → 保留 Writer/Reviewer 分離 + 適應式多 agent（既有機制），只換審查維度內容
- agents→skills 是「探討」非強制（B12 探討階段）— 標明探討，不過度工程
