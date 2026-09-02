---
id: AIR-6
title: CRG hook 殘留：matcher no-op 修復（死碼已清）
status: Done
assignee: []
created_date: '2026-09-02 13:07'
updated_date: '2026-09-02 14:03'
labels:
  - hooks
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
①require-crg hook 死碼已隨 20f81ad 清除；②剩 live ZCode PreToolUse matcher mcp__code-review-graph__ 對現行 CR plugin 工具名（mcp__plugin_code-reality_*）不命中＝靜默 no-op——決策：刪 matcher 或改指 CR plugin 名（查 cr-query skill 是否需 repo_root 防護）。源卡：git history crg-hook-cleanup.md
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
已完成：CRG matcher 已自 ZCode config.json 與 Claude settings.json 清除、hooks/ 無殘留（09-01 hook 殘留清完）——靜默 no-op 問題不復存在
<!-- SECTION:FINAL_SUMMARY:END -->
