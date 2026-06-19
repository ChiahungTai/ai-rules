# EP: S7 validation-strategy 注入 build/execution-plan 驗證段

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S7 段展開）
> **本 EP**: S0e [validation-strategy](../../../skills/validation-strategy/SKILL.md) skill（e2e 優先 / 交易 replay>>>live / 放 scripts/ / 不重驗 package）注入 build/execution-plan 驗證段，讓測試類型選擇有紀律依據。對齊 acceptance-evidence L3-L5 + quality-constraints 消費端驗證。過渡期手動衍生，標 parent。

## 動機
S0e validation-strategy skill 已建（四紀律）。但 build/execution-plan 驗證段未引用 — 測試類型選擇（e2e vs 單元、replay vs live、放哪、不驗什麼）缺紀律依據。注入 = 「引用 skill 決策樹」非複製內容。

## 範圍
- **S7a**：build.md 驗證段引用 validation-strategy（決定測試類型：e2e 優先、交易 replay、放 scripts/）
- **execution-plan.md 驗證策略段**（`:140-149`）：引用 validation-strategy + architecture-thinking；EP 段落「驗證策略」範本補「交易優先 replay;不重驗 package（NT/bokeh/panel）」

## 依賴
S0e（validation-strategy，已完成 ✅）

---

## S7a: build + execution-plan 驗證段注入

### 成功標準
- [ ] build 驗證段（階段 2/3）引用 [validation-strategy](../../../skills/validation-strategy/SKILL.md)（決定測試類型：e2e 優先、交易 replay >>> live、放 scripts/、不重驗 package）
- [ ] execution-plan 驗證策略段引用 validation-strategy + architecture-thinking
- [ ] EP 段落「驗證策略」範本補「交易優先 replay;不重驗 package（NT/bokeh/panel）」

### 驗證
- `rg "validation-strategy|replay.*live|不重驗" commands/build.md commands/execution-plan.md`

---

## 收尾
- 回母 EP：S7 build+commit 後，master S7 段標 ✅
- 風險：注入是引用非複製 — 標明引流 skill，避免內容重複
