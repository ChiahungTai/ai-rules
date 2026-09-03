---
id: AIR-15
title: memory 寫入原則微調（P1/P2）
status: In Progress
assignee: []
created_date: '2026-09-03 04:31'
updated_date: '2026-09-03 04:42'
labels:
  - governance
  - memory
  - temp-areas
dependencies: []
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
memory 寫入原則微調（裁決即做）：P1 hook DESC_LIMIT 120→100（對齊紀律值；generator TRUNCATE_DESC＋tests cross-layer 錨同步）建議做；P2 弧線條目軟預警（夜間 cron 加腿：單檔>8,000 chars 且 mtime 活躍列報告不擋——禁加段的軟執行）建議做。微執行不建工單
<!-- SECTION:DESCRIPTION:END -->
