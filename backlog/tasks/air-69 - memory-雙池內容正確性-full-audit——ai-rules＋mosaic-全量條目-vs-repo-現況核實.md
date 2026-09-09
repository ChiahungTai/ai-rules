---
id: AIR-69
title: memory 雙池內容正確性 full audit——ai-rules＋mosaic 全量條目 vs repo 現況核實
status: To Do
assignee: []
created_date: '2026-09-09 22:16'
labels:
  - governance
  - memory
dependencies: []
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
動機（09-10 兩實例）：①ai-rules feedback_dual-family-review-dispatch:44 教『spawn delegate-rescue 轉發』錯誤形態（記憶層主動強化錯誤模式——wrapper 是最大 spawn 單型的記憶源，已修）②mosaic project-memory-audit-advisory-only desc 稱『AIR-54 S6 主體進 repo』但 S6 未收斂（宣稱漂移）。內容正確性漂移是常態不是零星。範圍＝memory-audit skill 層 2『內容核實 vs repo』全量形態（full audit——非 lite 增量抽核）：ai-rules 主體 162 條＋mosaic 池全量，逐條 load-bearing claims 對照 repo/規則現況，過時/教錯/宣稱漂移列清單→advisory 報告→user 核可後修正（層 3 分工：登錄舉證、核可後執行）。排序硬依賴：mosaic 側等 AIR-54 S6 收斂後跑（池遷移改實體，舊池 audit 會作廢）；ai-rules 側可先跑。執行形態：full audit 弧（大規模語義工作授權層）＋歸因投影（memory_telemetry attribution）輔助。素材：09-10 掃描三報告 .agent-tmp/subagent-usage-*.md。
<!-- SECTION:DESCRIPTION:END -->
