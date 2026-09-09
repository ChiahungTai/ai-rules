---
id: AIR-56
title: memory mutation dirty sensor（CC側hook）——PostToolUse＋FileChanged薄傳感
status: Done
assignee: []
created_date: '2026-09-09 04:54'
updated_date: '2026-09-09 05:31'
labels:
  - memory
  - hooks
dependencies: []
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
P5裁決②實作（AIR-48定稿）。範圍：CC側新增memory-write-sensor（PostToolUse Edit|Write成功才記actor證據）＋memory-dirty-sensor（FileChanged當mutation反證；session_id是watcher非writer，只做dirty bit）。只emit raw event，由collector normalize後併入(b)投影；不另起歸因系統。覆蓋邊界：ZCode僅PreToolUse/Stop，此卡不管ZCode側（維持b+hash）。驗收：ABA/same-content改寫可被dirty event抓到；誤報（watcher非writer）有標註。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PostToolUse成功寫入才記actor
- [ ] #2 FileChanged只做dirty不指派writer
- [ ] #3 事件併入collector既有normalize
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
CC hook雙sensor落地：PostToolUse actor證據＋FileChanged dirty；collector merge/enrich/dirty旗；live接線未驗證（hash腿兜底）；全倉263綠
<!-- SECTION:FINAL_SUMMARY:END -->
