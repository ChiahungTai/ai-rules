---
id: AIR-9
title: memory 條目重複機械防護評估（池衛生）
status: Done
assignee: []
created_date: '2026-09-02 13:07'
updated_date: '2026-09-02 14:12'
labels:
  - skills
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
同主題重複條目僅 prose 紀律（寫入四問 rg 查重），generator 對合法 frontmatter 來者不拒——評估機械防護（寫入前 hook 查重／audit near-dup 偵測）。YAGNI 檢驗：先量測兩池 near-dup 現況再建。源卡：git history memory-entry-dup-guard.md
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
評估完成，裁定不建機械防護。量測已被 memory 治理弧（08-30~09-02 五波）隱含完成：(1) near-dup 靠寫入四問 prose 紀律＋週期 audit cluster merge 收斂——每次索引超限都收斂回 gate 內（09-02 收斂波合併已完結 project-* cluster）；(2) 機械防護最大盲區＝subagent 寫入不觸發 PreToolUse hook（兩次實證：16,154 chars Write 落地、disposition-marking 一日 11.8K→39.7K）——hook 查重擋不到真實膨脹源，邊際價值低；(3) full audit 98/102 條核實零推翻。維持 prose＋audit 層
<!-- SECTION:FINAL_SUMMARY:END -->
