---
id: AIR-13
title: muse 特化定案＋批次一工單
status: To Do
assignee: []
created_date: '2026-09-03 04:31'
labels:
  - muse
  - model-routing
  - delegation
dependencies: []
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
D1 委派路徑入 model-routing skill 層（適用判準：可工單化＋≥30分鐘 GLM 量／治理鐵則：muse 實作者＋GLM reviewer 不可省／計費現實：訂閱 5h 窗省 context 不省 requests）；D2 registry 維持 thin forwarder 單入口、不長特化 agent（trigger 相撞前車之鑑）；D3 固化 _common/muse-work-order.md template（七節：一句話/必讀/範圍限定/勿重辯/工具接線/驗收/完成檢查話術）。D 裁決後執行批次：review-engine 背景句、post-build 四通用缺口、四律九律分拆落位、debugging＋modern-cli 擇要、python-standards 相對 import 行、受影響測試集三處（quality-constraints 機制句＋cr-query 配方＋implement 指針，9f151add 反查為回歸錨）、at-skill miss codify、contracts.md muse 對照欄。載體：muse 工單委派、GLM reviewer 驗收
<!-- SECTION:DESCRIPTION:END -->
