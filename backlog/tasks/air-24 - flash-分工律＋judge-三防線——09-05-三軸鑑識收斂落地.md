---
id: AIR-24
title: flash 分工律＋judge 三防線——09-05 三軸鑑識收斂落地
status: Done
assignee: []
created_date: '2026-09-04 23:10'
updated_date: '2026-09-04 23:12'
labels:
  - model-routing
  - agents
dependencies: []
references:
  - 'http://127.0.0.1:6421/ai-rules/skills/model-routing/SKILL.md'
  - skills/model-routing/SKILL.md
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
09-04/05 夜 GLM-5.3-Flash 全切換三軸鑑識（對話/git/建議查證）的設計收斂落地。〔baseline：ai-rules aba8f1f〕〔已決策勿重辯：①tier＝能力檔語義非模型綁定——具體型號坐哪 tier 單一源在 model-routing skill 解析表；②執行層（review/impl 機械段/lite-verify/cron）條件式降 lite，條件＝保護面厚度三件（既有測試釘住＋驗證閉環＋非跨邊界語義面）；③judge 裁決/EP 規劃/post-build 編排＝full 能力檔不可降——lite＋max effort 補償＝未驗證路徑先小規模實證；④跨家族 review＝軟提醒非硬閘（額度現實）；⑤模型歸因必須 per-message modelID 機械對帳不接受自述〕〔驗收：①rules/model-routing.md tier 表改寫＋能力檔語義句；②skill 新增 flash 分工律節（實證＋風險面＋歸因紀律）；③judge-review 三防線＋機械化補償；④lite-verify EP 驗證策略覆蓋率項＋post-build 階段 3 接線＋implement 每情境結算條款；⑤1302 補 spawn 三態表（帳號級框架）；⑥deploy_agents.py 3/3 綠〕
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
三軸鑑識收斂落地：tier 能力檔語義＋條件式降級入 rule、flash 分工律/1302/跨家族軟提醒入 skill、judge 三防線、lite-verify EP 覆蓋率＋接線、deploy 3/3 綠
<!-- SECTION:FINAL_SUMMARY:END -->
