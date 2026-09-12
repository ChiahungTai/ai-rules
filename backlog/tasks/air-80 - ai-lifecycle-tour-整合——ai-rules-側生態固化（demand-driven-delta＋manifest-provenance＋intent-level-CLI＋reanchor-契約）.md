---
id: AIR-80
title: >-
  ai-lifecycle tour 整合——ai-rules 側生態固化（demand-driven delta＋manifest
  provenance＋intent-level CLI＋reanchor 契約）
status: Done
assignee: []
created_date: '2026-09-12 06:25'
updated_date: '2026-09-12 07:33'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔09-12 結算〕七項全落地：①post-build hook2 ask-once（輻射 implement 階段6 fallback/code-review 模式B/tour-bootstrap/html-mode hook2 row）；②manifest provenance（tour-bootstrap 契約節＋code-reality [[delta_arc]] rows）；③tour materialize <arcId> intent-level CLI（code-reality 6ec95f5——snapshot pair sha8 fail-loud 解析、同 arcId 覆蓋同 tourPath）；④delta_tour tour-level ref=<after commit>；⑤chain_tour x-codeReality.symbol（真 SCIP symbol 三錨點帶出）；⑥tour_validate 移出 docs-only（post-build 新「Tour corpus gate」general finalization 節）；⑦消費端改指 ai-lifecycle（tour-bootstrap vsix 退役/post-build 報告 AI Tours 句/html-mode 殼連結+refs 附 delta tour）。驗證：code-reality cargo test 全 workspace 綠＋live smoke（air-78 弧 32 steps materialize、ref 帶全 sha、manifest row 齊）；ai-rules 殘留掃描＝舊「持久版單一產點/裝 vsix/階段4步驟3」引用全同步。緩議兩項如卡面（alias 子系統/fallback 統計）。

〔09-12 codex 審回寫（job-mty0ythj：1🔴5🟡1ℹ️ NO-GO→全採納修正）〕🔴C1 ask-once 斷鏈＝兩階段契約（tour register 持久化 pending row→materialize 補 tourPath；略過路徑 row 在場＝ai-lifecycle 可觸發；register/註冊形 materialize 立即 dump、失敗不抹 row）；C2 EP 雙語義＝FS 絕對（claims）/tour 錨 repo-relative 分離（repo-外 EP 不作 step anchor）；C3 7碼 short sha＝rev-parse --verify 解析成 full sha 再查 snapshot；C4 stale gate 進 materialize 本體（_meta.stale 非空 fail-loud）；C5 dogfood 弧身分錯（beb86429..11fd0d73 實跨 AIR-79+80）＝產物收回；C6 run() e2e 兩條入 s8（register→materialize 全鏈＋stale rejection＋overwrite＋7碼註冊）；C7 delta row＝tool-owned full replace 契約明寫（tour-bootstrap）。cargo 全綠。修訂後 post-build ask-once 段＝register+materialize 兩步。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
ai-lifecycle tour 整合 ai-rules 側七項固化——demand-driven delta（hook2 ask-once）、manifest provenance（arcId canonical）、tour materialize intent-level CLI、delta_tour ref、chain_tour x-codeReality.symbol、tour_validate 去 docs-only、消費端指 ai-lifecycle；cargo 全綠＋live smoke（32-step 首個 materialize）；code-reality 側 6ec95f5
<!-- SECTION:FINAL_SUMMARY:END -->
