---
id: AIR-67
title: >-
  CR quick-wins——cr-research 角色定義修正＋symbol query 五步 ladder＋.code-reality.toml
  smoke（cr-audit R2+R4）
status: To Do
assignee: []
created_date: '2026-09-09 21:43'
updated_date: '2026-09-09 23:13'
labels:
  - cr
  - governance
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
cr-audit（reports/2026-09-09-cr-role-audit.md）即刻項半小時級。R2：agents/roles/cr-research.md:23 角色定義教錯 module-path query 形態（Class.method/bare name 才對）——修角色定義＋cr-query＋symbol-query-routing 三檔同步（定義源改動 rg 掃引用防 drift）＋五步 ladder 落地（①Class.method/bare→②去 prefix 重試→③LSP/rg 找 canonical→④CR 再查→⑤[WARN] degraded＋禁把 query miss 翻譯成 0 consumers）。R4：ai-rules 補 .code-reality.toml（module prefix/claims extraction）——必須 smoke 驗證（錯 profile 產生更危險自信假陰性）；解鎖 delta_tour EP 宣稱對照＋持久版 tour。驗收：rg 舊形態零殘留＋smoke 產出附卡＋三檔一致性。
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔triage 併弧 09-10——升級為 CR 治理總弧（三段連續做）〕段二＝cr-audit R1+R3（negative-claim gate：R1 語義化 gate 牽 review-engine/execution-plan/judge 三檔——claim 四欄結構/negative verdict 永不可用 rg；R3 research.md evidence 載體——EP 同層 references/research.md 機械可驗收）；段三＝R6+R7（外部 runtime 注入：work-order.md:61 過時假議修正＋capability-aware 注入塊 MCP-first→CLI fallback→WARN degraded；fallback 可見化：spawn auth 失敗回報 CR 未遂＋重試一次禁靜默漂移）。提案全文：ai-analysis/reports/2026-09-09-cr-role-audit.md R 行表（:189-196）。
<!-- SECTION:NOTES:END -->
