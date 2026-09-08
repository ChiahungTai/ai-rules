---
id: DRAFT-1
title: memory telemetry codex 源接線——sessions rollout JSONL reader
status: Draft
assignee: []
created_date: '2026-09-08 01:45'
labels:
  - memory
  - governance
  - telemetry
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：writes/reads 歸因覆蓋 codex 面（uninstrumented 移除 codex）。可行性：~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl 在場且含 tool call 事件（09-07/08 弧考古已解過 response_item 格式）。範圍：memory_telemetry.py 新 read_codex() adapter 對齊 read_clauude 契約（status 配對/time_source/三源 coverage）；codex 工具形態研究（shell/apply_patch 呼叫怎麼抽 file_path+成敗+時間）。驗收：codex session 對 memory 條目的寫/讀出現在歸因與觀測報告；fixture 覆蓋 codex 格式配對失敗形態。
<!-- SECTION:DESCRIPTION:END -->
