# review 命令家族架構重構：review-engine domain 抽出

同一「審查」動作跨 ep-review/code-review/audit-test/execution-plan（含 build/deep-work）重複實作且不一致（drift）。套用 Clean Architecture：新增 `review-engine` skill（domain 層，通用審查邏輯唯一真相源），命令退化為薄 adapter，消除 drift。

**範圍**：新增 review-engine + 改薄 4 命令 + 收斂 execution-plan EP Review + ripple（build/deep-work/judge-review/deliverable-review/agent-review-cycle/using-agent-skills）+ 索引同步。7 段。

**關鍵設計**：
- review-engine 只裝通用 why（嚴重度/信心水準/自證/LSP）；審查模式**判定邏輯**留 workflow-review-pattern（與 schema/腳本強耦合）；多層驗證**三層鏈**留 audit-test（test 專屬）
- 收進判準：所有 review 命令都適用（只適用部分命令的不收）

**EP**：[ep-review-engine-refactor.md](../../ai-analysis/execution-plans/ep-review-engine-refactor.md)（含 EP Review 14 findings 全採納）

**來源**：對話深層思考（Clean Architecture + DDD 視角診斷 review 家族 domain 邏輯散落 adapter 層）+ EP Review 補 build/deep-work ripple（F6）
