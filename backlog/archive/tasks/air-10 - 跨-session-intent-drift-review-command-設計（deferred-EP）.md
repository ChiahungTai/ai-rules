---
id: AIR-10
title: 跨 session intent-drift review command 設計（deferred EP）
status: To Do
assignee: []
created_date: '2026-09-02 13:07'
labels:
  - meta
dependencies: []
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
session-boundary review 原則已落（acceptance-evidence）但跨 session 無觸發機制；substrate 已有（autonomous-execution resume 時 crash-only reconciliation），缺判讀層 command（差異報告→intent 是否漂移，Type B）。源卡：git history session-boundary-intent-drift-review.md
<!-- SECTION:DESCRIPTION:END -->
