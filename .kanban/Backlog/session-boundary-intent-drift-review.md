# 觀察/deferred：跨 session intent-drift review command

`acceptance-evidence.md`「B 軸人類驗收層」已落 **session-boundary review** 原則（跨 session 接續時判讀累積目標是否漂移），但**跨 session 場景目前無觸發機制** —— 全 repo 無 resume-review trigger（`/at`=usage-resume、`/handoff`=交接包裝、`/standup`=activity digest，皆非 intent-drift review）。

**現況**：原則效果限**單 session batch-ceiling 軟觸發**（`build.md` batch ceiling：累積多段 → 建議暫停跑 session-boundary review）。跨 session（開新 session 接續 EP）時，靠 LLM 自覺觸發 —— 而 resume 時正是 intent drift 風險最高的時刻，靠自覺最不可靠（與「機械 > 自述」原則矛盾）。

**deferred 決策**（EP `ep-review-assurance-uplift` DT-2，2026-07-09）：本 EP 不建新 command（scope）。待獨立 EP 設計：resume/接續時自動觸發「上一 session 累積產出 vs 原始 EP intent」的 intent-drift review（Type B 動態漂移偵測，見 acceptance-evidence「Intent Drift 的兩型」）。

**部分落地（EP-A `ep-autonomous-execution-reliability` S2，2026-07-10）**：autonomous-execution「Session 級 Recovery」已提供 **substrate + 觸發器**——resume 時 crash-only reconciliation（re-derive「git diff vs EP scope」差異報告），為本原則提供事實層 + resume 觸發點。**仍 deferred（本 card 追蹤）**：完整 intent-drift review **command**（判讀層：差異報告 → intent 是否漂移）——substrate ≠ review，review 本身仍待獨立 EP。

**來源**：solo+AI review guide（session-boundary review）+ EP `ep-review-assurance-uplift` DT-2
