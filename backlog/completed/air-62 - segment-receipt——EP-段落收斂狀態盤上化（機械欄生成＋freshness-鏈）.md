---
id: AIR-62
title: segment receipt——EP 段落收斂狀態盤上化（機械欄生成＋freshness 鏈）
status: Done
assignee: []
created_date: '2026-09-09 13:20'
updated_date: '2026-09-09 23:13'
labels:
  - governance
  - skills
  - workflow
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 6e96e0e〕跨 quota 接力時 EP 段落收斂狀態（RED/GREEN、loop 輪數、懸掛項）是記憶體狀態——撞 5h window 後下一個 session 從 git log 猜「這段算做完沒」（/implement 無段落級斷點格式；09-09 與 09-07 兩次事故都是未結算狀態撞牆）。

〔已決策勿重辯：①前置依賴——「session 接續恢復鏈治理」卡（rehydration 單一源合併）完成後才開工；receipt 是恢復序列的一環、不是第六個獨立落盤層②欄位分級——git 可推導欄（baseline HEAD／diff digest／pytest exit＋計數／review loop 輪數）全部機械生成（script），LLM 只寫判斷欄並標註——解「receipt 最被需要時（session 末、model 最退化）寫作品質最低」的寫入者悖論③freshness 語義——receipt 鏈式版本（parent receipt＋baseline HEAD），供 resume 判「世界是否已分叉」而非還原 snapshot④完成度真相仍是 Git＋EP re-derive；receipt 只是 transcript cache 的 validity token，不是第二真相源〕

〔驗收：①段落收斂時機械產出 segment receipt（git 可推導欄零 LLM 手寫；生成器有測試）②resume 流程（單一源恢復序列）讀 receipt 判段落完成度，不從 git log 反推③與恢復序列單一源接線一致（不另立讀取路徑）④implement skill 對應段同步（斷點格式寫進階段文件）〕
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
triage 併入 AIR-60（段三 segment receipt）——user 09-10 拍板；原 desc 見本卡。
<!-- SECTION:FINAL_SUMMARY:END -->
