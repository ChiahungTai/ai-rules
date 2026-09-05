---
id: AIR-27
title: >-
  generator errs 路徑 CC 化——frontmatter 違規時跳過壞條目照寫索引＋exit 1
  列名壞檔（現況拒寫＝一個壞條目擋全部合法條目投影；AIR-25 fresh-eyes review F1 後議，注意動
  test_regen_failure_marker 觸發路徑）
status: Done
assignee: []
created_date: '2026-09-05 01:09'
updated_date: '2026-09-05 01:20'
labels: []
dependencies: []
references:
  - 'http://127.0.0.1:6421/ai-rules/skills/memory-audit/scripts/generate_index.py'
  - skills/memory-audit/scripts/generate_index.py
---

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
errs 路徑 CC 化落地——壞條目跳過、合法條目照常投影＋exit 1 列名；42 測試綠（反轉 1＋新增 guard 1）、池 cmp 綠
<!-- SECTION:FINAL_SUMMARY:END -->
