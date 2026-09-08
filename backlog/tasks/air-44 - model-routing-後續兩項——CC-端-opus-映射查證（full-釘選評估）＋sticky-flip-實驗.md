---
id: AIR-44
title: model-routing 後續兩項——CC 端 opus 映射查證（full 釘選評估）＋sticky flip 實驗
status: To Do
assignee: []
created_date: '2026-09-08 01:42'
labels:
  - governance
dependencies: []
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 508f4a9〕〔已決策勿重辯：①來源＝AIR-43 EP 後續項（done/09-08-model-vocab-governance）弧外登記，AIR-43 已全弧閉環②CC 查證方法＝CC session spawn 後 transcript rg '"model"' 實測 opus 別名→GLM 映射（agent-workflow Step 1 表 :57 仍列 glm-5-turbo 舊值＋缺 glm-5.3 列，未查證前 CC 端維持 inherit 不釘）③sticky flip＝SKILL.md:68 既有待跑項——AIR-43 S3 已得數據點（variant=max、定義 high 不達 wire、全 agent 一致 max），flip 實驗分辨 sticky override vs silent no-op（改 user reasoningLevel≠定義值再 spawn 看 variant 跟隨否）〕〔驗收：agent-workflow Step 1 表更新為實測值或標註未查證；flip 結果（override/no-op 判定）回寫 SKILL.md:68 但書段＋platform-facts〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CC 映射表實測更新；flip 判定回寫但書段
<!-- AC:END -->
