---
id: AIR-65
title: memory 池治理三議題裁決固化——mosaic mini-merge 後續（bytes 波次／bare hash／M2 日期閘）
status: Done
assignee: []
created_date: '2026-09-09 20:18'
updated_date: '2026-09-09 20:51'
labels: []
dependencies: []
references:
  - 'http://127.0.0.1:6421/viewer/_md-viewer.html?p=/skills/memory-audit/SKILL.md'
  - skills/memory-audit/SKILL.md
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mosaic 09-09 十卡收案群→bytes 觸頂→09-10 mini-merge 事件三議題裁決＋資產固化。裁決：①B（SKILL lite 加 bytes≥95% mini-merge 候選必列義務，維持人裁）；②A（HASH_RE 加 bare-hash 分支 letter+digit）；③A（實作 M2：DATE_RE MM-DD＋SESS_RE 硬擋）；④line21 三項皆不修（上游已具備／drift 消失／模板在位 mosaic 側驗 live），line15 四殘無相關新增繼續等。patch：hooks/block-memory-index-write.py＋skills/memory-audit/SKILL.md＋tests/test_memory_lifecycle.py（7 新測試）。詳 .agent-tmp/memory-gov-journal.md。禁 commit（user 收案時統一處理）。
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
CR 稽核三議題裁決固化完成：bare-hash 擴閘＋M2 日期/sess_ 閘＋SKILL bytes 候選義務（53a7487——hooks/block-memory-index-write.py＋memory-audit SKILL＋test_memory_lifecycle 120 行，288 tests 綠）。id 由 AIR-59 改 65（解除與 webgpt 卡撞號——f163ea3 同型處置，平行 session 發起本 session 完成 rename）。工作隨 air-52 弧 ff 進 main。
<!-- SECTION:FINAL_SUMMARY:END -->
