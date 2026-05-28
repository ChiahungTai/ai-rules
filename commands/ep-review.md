---
description: "審查 Execution Plan 合理性（完整性、規範合規、一致性、遺漏風險）。/ep-review <EP路徑>"
when_to_use: "Review an Execution Plan for completeness, rules compliance, internal consistency, and omission risks before implementation begins."
context: fork
agent: Explore
usage: "/ep-review <Execution Plan 路徑>"
argument-hint: "<Execution Plan 檔案路徑>"
allowed-tools: ["Read", "Grep", "Glob"]
---

# /ep-review — Execution Plan 合理性審查

EP 審查員，在實作前審查 Execution Plan，確保計畫書完整、合規、可執行。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — 多維度審查方法論

---

## 四維度審查

### F1: 完整性檢查

每段是否有驗收標準？檔案是否完整列出？依賴項是否遺漏？邊界情況是否考量？

### F2: Rules 合規檢查

命名是否符合 `python-standards`？是否遵守 `code-edit-constraints`？是否有違反 `_ai-behavior-constraints` 的內容？是否需要更新 CLAUDE.md？

### F3: 內部一致性檢查

段落間依賴順序合理？對同一檔案的修改矛盾？技術方案一致？語義約束（共享型別、命名慣例、架構假設）是否標記？

### F4: 遺漏風險檢查

Demo 檔案有規劃？測試有規劃？`__init__.py` 的 `__all__` 需要更新？配置檔案需修改？受影響的其他模組已列出？

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

在 EP 對應段落的 Context 末尾加入：

```markdown
> **EP Review 修正**：[修正內容描述]
```

### 回寫驗證

回寫完成後，重新讀取 EP 確認修正已入檔。未回寫的發現不得標記為「已處理」。

---

## 技術約束

- **基於實際程式碼**：必須讀取計畫書提到的檔案確認存在
- **四維度覆蓋**：必須覆蓋 F1-F4
- **審查者自證**：提出問題前必須用 Read/Grep 查證宣稱。聲稱檔案存在 → 讀它；聲稱命名衝突 → 查 import 鏈；聲稱依賴順序有問題 → 追蹤執行順序。無法查證的宣稱標注「未驗證」
- **不實作**：審查階段不自動開始實作

---

## 邊界

- **Always**：完整讀取 EP、查證現有程式碼、覆蓋四維度、輸出結構化報告
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
/spec → /execution-plan（含 EP Review）→ [/ep-review] → /build（含 Agent Review）→ /code-review
```

前置：`/execution-plan`
後續：`/judge-review` → `/build`
