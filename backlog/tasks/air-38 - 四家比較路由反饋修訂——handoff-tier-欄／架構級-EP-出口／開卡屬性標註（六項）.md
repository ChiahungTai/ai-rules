---
id: AIR-38
title: 四家比較路由反饋修訂——handoff tier 欄／架構級 EP 出口／開卡屬性標註（六項）
status: To Do
assignee: []
created_date: '2026-09-07 04:53'
labels:
  - skills
dependencies: []
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
基於 mosaic 0906/07 四家模型比較修訂 ai-rules 三處路由（handoff 建議執行 tier 欄、external-runtime 架構級 EP 角色行、開卡風險屬性標註）＋flash off-peak 但書＋自報元資料不可信 claim 類型＋單一源掃描〔baseline：ai-rules 50230b3〕〔已決策勿重辯：①路由詞彙一律「旗艦/一般」tier 抽象（user 拍板）——模型名只在 tier→(model,effort) 解析層，family 軸（muse/codex）是第二軸非 tier 降級；②tier 詞彙體系（full/lite/vision requirement token）不動——只在 handoff/開卡/external-runtime 三處擴充出口；③四家比較結論已定案不重推，證據自包含於任務家 spec（不需讀 mosaic repo）；④實作排在 AIR-37 之後（execution-plan SKILL 同檔並行避撞）〕〔驗收：①六項 A-F 逐項落地或記錄不採納理由；②F 的 rg 掃描證據（改動定義的引用面清單）；③tier 詞彙一致性——旗艦/一般（tier 層）vs 模型名（解析層）不混用〕
<!-- SECTION:DESCRIPTION:END -->
