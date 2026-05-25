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
