---
id: AIR-78
title: bridge glm 委派檔位規則入 model-routing——派工必帶 --model，禁裸委派防靜默落 flash
status: To Do
assignee: []
created_date: '2026-09-11 23:38'
labels:
  - model-routing
  - bridge
  - governance
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕把「bridge 派工給 glm 家族必須明確指定模型檔位（lite 用 sonnet、旗艦用 opus）」寫進 model-routing skill——裸委派會靜默落到 flash 版且帳本查不出實際檔位。設計已與 codex 聯合定案，等 M1 瘦身弧落地後開工。

〔baseline：ai-rules 93b5c5a〕
〔已決策勿重辯：①落點＝skill external-runtime family 表加 glm row＋3 行 glm 專節（倣 webgpt 模式）；rules/ 零改動（M1 下沉後 rule 只剩詞彙＋必載條款，family enum 已含 GLM）②檔位語義：sonnet→flash 別名、opus→GLM-5.3 旗艦；lite 派 --model sonnet、full-tier 派 --model opus；裸委派禁止作為 routing contract（09-12 實測落 flash＋ledger effectiveModel null 無證明力）——delegate-bridge d4 default pin 落地前連 lite 都要顯式 --model（codex 收緊：provenance 論證）③審計語義：以 dispatch/requested model flag 為 authoritative evidence；carrier effectiveModel 現不具證明力④唯讀 carrier v1（寫入走 muse）＋--effort/--steps/--yolo 不適用——放專節不放表（表不塞肥）⑤resume/fork 定向接續表不加 glm row（session identity 連續性未證）——專節明寫 resume/fork semantics unverified; do not infer continuation support from muse/codex⑥in-harness 對照句寫條件式：「若 in-harness full dispatch 會繼承 Flash，則 full-tier GLM 工作改走 bridge --model opus」——AIR-76 落地後條件自然失效不留歷史特例⑦時序：嚴格兩弧兩 commit——M1 下沉弧完整落地並 re-read post-M1 skill 實際形態後才開工（root cause 不同：M1 收斂既有真相、本弧新增 family runtime contract，acceptance boundary 與 review identity 不同）⑧arc home 依當下已部署 task topology（legacy 頂層），AIR-77 遷移時搬——不提前走 YYYY-MM/（script depth 假設未翻轉＝false-green 風險：script 成功退出卻沒掃到新弧）；不在本弧順手修 scanner（第三 root cause 不混弧）。源工單＝delegate-bridge f821ca7 跨 repo 交接〕
〔驗收：①family 表 glm row＋專節在場②三 invariant 機械可驗——full 派單必產 --model opus、lite 必產 --model sonnet、unsupported flags 零送出（instruction 層能控制且能獨立驗證者；ledger effectiveModel != null 不屬本弧驗收——那是 delegate-bridge d4 責任邊界）③enum 反查：掃 muse/codex/--family/family switch/generic bridge command builder 暗含二值（只有兩家）假設處逐檔處置——agents/ 零改動須由反查證明而非 glm 零命中證明④rg -i family glm 每個委派指引點帶檔位語義；instruction sync/deploy 完成〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 family 表 glm row＋3 行專節落地（值域／檔位政策／審計語義／resume-fork unverified 句）
- [ ] #2 三 invariant 機械驗證：full→--model opus、lite→--model sonnet、unsupported flags 零送出
- [ ] #3 enum 反查完成（muse/codex/--family 二值假設全掃）；agents/ 零改由反查證明
- [ ] #4 時序證據：M1 弧 commit 在前＋post-M1 skill 形態 re-read 記錄
<!-- AC:END -->
