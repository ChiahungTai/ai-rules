---
id: AIR-2
title: CR 消費端 cutover S4 殘留＋ai-rules 舊碼刪除
status: Done
assignee: []
created_date: '2026-09-02 13:07'
updated_date: '2026-09-02 14:02'
labels:
  - code-reality
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
code-reality 成熟後消費端切 --project ~/Github/code-reality＋刪 ai-rules code_reality/ 與 tests/（判準：rg 'uv run --project ~/Github/ai-rules' --type md 歸零，豁免 zcode-session-query）。源卡：git history code-reality-consumer-cutover-s4.md
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
實質完成：code_reality/ 已刪、tests/ 無 CR 測試；活躍文檔 uv run --project 舊引用歸零（僅剩 zcode-session-query 豁免項），reports/archive 兩命中為歷史文檔依規不動
<!-- SECTION:FINAL_SUMMARY:END -->
