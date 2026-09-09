---
id: AIR-65
title: memory 池治理三議題裁決固化——mosaic mini-merge 後續（bytes 波次／bare hash／M2 日期閘）
status: In Progress
assignee: []
created_date: '2026-09-09 20:18'
labels: []
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mosaic 09-09 十卡收案群→bytes 觸頂→09-10 mini-merge 事件三議題裁決＋資產固化。裁決：①B（SKILL lite 加 bytes≥95% mini-merge 候選必列義務，維持人裁）；②A（HASH_RE 加 bare-hash 分支 letter+digit）；③A（實作 M2：DATE_RE MM-DD＋SESS_RE 硬擋）；④line21 三項皆不修（上游已具備／drift 消失／模板在位 mosaic 側驗 live），line15 四殘無相關新增繼續等。patch：hooks/block-memory-index-write.py＋skills/memory-audit/SKILL.md＋tests/test_memory_lifecycle.py（7 新測試）。詳 .agent-tmp/memory-gov-journal.md。禁 commit（user 收案時統一處理）。
<!-- SECTION:DESCRIPTION:END -->
