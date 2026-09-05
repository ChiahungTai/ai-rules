# Flow Feedback — 2026-09-05 — 過期收法派發：session 記憶 ≠ 治理檔

## 摩擦（發現來源）
> AIR-28 弧 flash session 派 codex 用了過期收法「wrapper resume-to-poll」——codex wrapper 依 thin forwarder 契約明確拒絕（禁 poll/status/result），派發失敗。來源：sess_3380ab28 handoff。

## session 摘要
AIR-26（4b1950d，同日較早）已把收法條文精確改寫為 push（agents/AGENTS.md dispatch face＋model-routing skill「完成回報收法」）。事故 session 在撞號調查時**看過 4b1950d 的 commit 標題**，派發時仍用 session 記憶裡的舊詞——條文無錯，錯在「知道有改版」≠「重讀再派發」；且 memory desc 舊教義（同步回報開場）開場載入持續灌輸舊模式。

## type-1 建議（時機）
- **派發 external runtime 當下重讀治理檔收法節** → 已落地：model-routing skill「套用」段首行防護（禁用 session 記憶／memory desc 派發）
  - counter-factual：若該防護行在事發前在場，派發前重讀就會看到 push 決策樹，不會送出 resume-to-poll

## type-2 建議（設計）
- **memory desc 是開場載入的過期源**：desc 重抄行為內容＝內容演進時 desc 自動過期且每 session 開場灌輸——已修正（desc 換 doctrine 指針形）；開放問題留 flow-review：「**派發前重讀治理檔**」要不要從 model-routing 通用化到其他快速演進治理域（收法之外：hooks 註冊面、bundle 紀律、agent registry——哪些域值得同款防護行？）

## 處置記錄
- memory `reference_external-runtime-delegation-family`：desc＋完成回報模型段改 push doctrine、事故教訓入條目（發送端 session 完成）；索引已 regen
- model-routing skill 套用段防護行（本弧完成）
- 本檔直接歸檔 _done/（可行動項均已落地；僅通用化開放問題留 flow-review 撿）

## tags
`model-routing` `external-runtime` `收法` `知識過期` `memory-desc` `flow-review`
