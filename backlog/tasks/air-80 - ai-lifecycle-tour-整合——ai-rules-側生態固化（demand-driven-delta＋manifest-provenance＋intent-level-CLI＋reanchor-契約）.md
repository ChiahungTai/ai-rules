---
id: AIR-80
title: >-
  ai-lifecycle tour 整合——ai-rules 側生態固化（demand-driven delta＋manifest
  provenance＋intent-level CLI＋reanchor 契約）
status: To Do
assignee: []
created_date: '2026-09-12 06:25'
labels:
  - tours
  - integration
  - post-build
dependencies: []
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕ai-lifecycle 已定案吸收 CodeTour fork player＋demand-driven delta 觸發；ai-rules 與 code-reality 側固化七項生態變更（doctrine 修訂＋CLI patch），兩側契約才接得上。現況：接手 handoff 開工。

〔baseline：ai-rules 0d97bd7；code-reality 0d8b80f（v0.8.1）；設計源＝ai-lifecycle 00-tasks/09-12-uc7-tour-walkthrough/ep.md（定稿 7a7664a，三方收斂：user＋GLM＋codex 三輪對辯）〕

〔已決策勿重辯：①demand-driven delta——post-build hook 2 持久 delta 產點從 always 改 ask-once（收尾報告待確認清單增「delta tour：產生／略過」預設略過；未確認弧保留 snapshot pair inputs；理由＝user 實證常常產生沒在看）②manifest provenance——arcId＝materialization canonical key（cardId 僅 join 屬性、一卡可多弧）；列欄位＝{arcId, cardId, base/target commit, EP 路徑, quality: full|degraded}；materialized row 保留不刪（補 tourPath）；消費端容忍式讀取（欄缺席＝無觸發 UI）③intent-level CLI＝code-reality tour materialize <arcId>——extension 只傳意圖、CLI 自組完整 recipe（snapshot pair/EP gate/--primary 保留——重產漏旗標靜默掉落是已記錄陷阱）；含同弧重產檔名行為（覆蓋 vs 後綴）決策④delta_tour 寫 tour-level ref:<after commit>——delta 是歷史快照永不 living-reanchor（delta_tour.rs:443-527）⑤chain_tour 寫 x-codeReality.symbol＝真 SCIP symbol（現況 file+name+nearest-line 非完整 identity；chain_tour.rs:302-417/446-529）⑥tour_validate 移出 docs-only gate（現掛 post-build 階段4 僅 .md 鏈下＝純 code 變更時 tour 漂移不驗——bug；移至 general finalization）⑦消費端文件改指 ai-lifecycle（fork vsix 退役）——metadata-sync 結案 refs 附 .tours/delta/<arc>.tour、illustrate html-mode 殼連 delta tour、收尾報告 AI Tours 視圖句、tour-bootstrap 消費端段。緩議勿先做：rename/module-move alias 子系統（先量 exact-symbol miss 分佈）、player DocumentSymbol fallback（等 dogfood 統計）〕

〔驗收：7 項以 ai-rules 慣例固化（rule/skill/CLI patch——code-reality 側 cargo test 過＋ai-rules 側 rg 對齊掃描）；回 TASK-7 notes 對齊契約時點（ai-lifecycle 側追蹤卡）；單一源紀律——hook 2 ask-once 修訂輻射 implement 階段6 fallback/html-mode hook2 row/code-review 模式B 引用點〕
<!-- SECTION:DESCRIPTION:END -->
