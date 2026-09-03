---
id: AIR-17
title: 夜間收斂 cron 首跑驗證
status: To Do
assignee: []
created_date: '2026-09-03 04:34'
labels:
  - cron
  - memory-audit
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
automation-751ecce2（每日 23:40、ai-rules 池）明早驗證首跑：報告是否產出（前後 chars/bytes/條目對照＋動作清單）、_audit-state last_index_chars 是否更新、_regen-failed 狀態。異常處置：跑題/未觸發/誤刪——按 at-skill-zcode-cron-gaps 開放項判讀（runCount/lastRunAt 不可推斷）。通過即關卡
<!-- SECTION:DESCRIPTION:END -->
