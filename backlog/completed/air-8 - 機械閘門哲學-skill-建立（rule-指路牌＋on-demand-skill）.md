---
id: AIR-8
title: 機械閘門哲學 skill 建立（rule 指路牌＋on-demand skill）
status: Done
assignee: []
created_date: '2026-09-02 13:07'
updated_date: '2026-09-02 14:23'
labels:
  - meta
dependencies: []
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
原則散落 9 檔無定義源（flow-review 2026-06-17 hybrid 裁決）：rules/ 加指路牌＋建 skills/mechanical-gate-philosophy（L1-L6 階層＋機械/viewport/prompt 決策樹＋反模式）；建成時回收 acceptance-evidence Runtime Invariant 等三處引用為 canonical。docs mode。源卡：git history mechanical-gate-philosophy-hybrid.md
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
裁決縮小（2026-09-02 arch-thinking 復審）：不建新 skill mechanical-gate-philosophy——L1-L6 階層與 A/B 軸已由 acceptance-evidence rule+skill 雙層承載（reference 分層晚於 06-17 原裁決落地），散落程度已大幅收斂。真實殘餘缺口僅「載體決策樹」（hook 純機械/單入口/立即危害 → rule always-on 硬紀律 → skill on-demand 方法論 → prompt/LLM 語義判斷）一小段。做法改為：併入 instruction-writing skill（載體選擇是寫作治理核心決策，AGENTS.md 治理第 2 點展開）＋hook-vs-llm 分工原則從 memory 固化進 repo 資產；不建獨立 skill、不動 acceptance-evidence 三處引用
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
縮小方案落地：載體決策樹（hook 三判準缺一即退 LLM 流程＋假確定性論證＋對照組）已併 instruction-writing skill 新段；AGENTS.md 寫作治理第 2 點展開為四載體判準＋指路；hook-vs-llm 分工原則自 memory 固化進 repo 資產。未建獨立 mechanical-gate-philosophy skill（acceptance-evidence reference 分層已收斂原散落）
<!-- SECTION:FINAL_SUMMARY:END -->
