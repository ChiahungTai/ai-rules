---
id: AIR-67
title: >-
  CR quick-wins——cr-research 角色定義修正＋symbol query 五步 ladder＋.code-reality.toml
  smoke（cr-audit R2+R4）
status: In Progress
assignee: []
created_date: '2026-09-09 21:43'
updated_date: '2026-09-12 05:20'
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

〔開工 2026-09-12〕R2 已由 5dc56cd 落地（cr-research 查詢形態修正＋miss ladder）；reviewer MCP-first 行已在 HEAD（code-reviewer.md:29／code-reviewer-primed.md:16）——原卡 R2 部分轉驗收。剩餘 scope 收斂為兩弧（codex 討論 job-mtxfv83d 定案）：弧A policy closure＝work-order §7「foreign runtime 無 LSP／MCP 面」過時斷言改 available-face 階梯（MCP→CLI→rg degraded [WARN]；禁從 role/template 宣告推定 runtime 有 MCP）＋R7 fallback 可見化（transient 才同 face 重試一次；capability 缺場記 reason 降階不盲重試；spawn auth 失敗屬 dispatch 層不混同）；弧B telemetry closure（施工序固定 collector→replay→trigger）＝cr_usage.py 演化三證據類（structured call evidence＝bridge jobs `item.completed`+`item.type=command_execution` 的 command 欄位〔正樣本 job-mtx2eakq 實證〕／output evidence＝`[SRC]`+「未 index 驗證」指紋、計數名 evidence-bearing outputs 非 CR calls／degraded marker 單獨計）→ 09-11 正樣本＋muse 基線 replay 驗收 → post-build 階段4 獨立條款「CR wiring telemetry checkpoint」（非 AIR-75 子梔——政策傳播vs行為量測不同軸；checkpoint≠effectiveness proof）＋schedule-registry #3 描述同步（CR 腿事件觸發為主）。觸及檔：skills/_common/work-order.md、skills/post-build/SKILL.md、skills/corrections-weekly/{SKILL.md,scripts/cr_usage.py}、ai-analysis/schedule-registry.md。R4（ai-rules .code-reality.toml smoke）仍在卡內待做。
<!-- SECTION:NOTES:END -->
