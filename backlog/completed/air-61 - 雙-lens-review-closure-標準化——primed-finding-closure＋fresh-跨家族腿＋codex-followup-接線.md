---
id: AIR-61
title: 雙 lens review closure 標準化——primed finding closure＋fresh 跨家族腿＋codex followup 接線
status: Done
assignee: []
created_date: '2026-09-09 13:20'
updated_date: '2026-09-09 23:13'
labels:
  - governance
  - skills
  - review
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 6e96e0e〕MOS-74 先例（reviewer --session-id 同 session followup 複驗優於 fresh）＋09-09 三顧問討論收斂的審查鏈標準化卡；同日 dogfood 已實證兩種接續形態（bridge --session-id durable 續寫零背景重複／SendMessage agent resume 帶輪 1 context 純記憶作答）。

〔已決策勿重辯：①雙 lens 分工——primed reviewer（同 session followup）只做逐 finding closure（closed/reopen/unverified，驗證式機械複跑）；fresh（優先跨家族）reviewer 留給「修正越出 finding scope／新問題密度高」的弧，抓 fix-induced regression／scope drift；primed 不當 final acceptance——例外條款：finding 級 closure 附驗證式可機械複跑者可為終驗②codex followup 腿接線＝工程任務非實驗（機制三件套在場：bridge task --family codex --session-id＋ledger sessionId 定址＋work-order review variant），模板改自 muse-followup-air50 形態；fallback＝現狀 user relay 零損失③量測獨立性——雙 lens A/B 判定的 judge 不得同家族單審，closure accuracy 與 drift-detection rate 分開量、判準機械可判④跨家族迴路最後一段（user 當郵差）是實測最痛點——user 09-06 曾中止 AI 派發改直跑（用腳投票實證）〕

〔驗收：①followup-review skill（或 post-build 鏈對應段）載明雙 lens 分工與 primed 邊界②一次真實 codex review 弧完成 --session-id followup 接線：state-review「派發形態現況」codex followup 從 first-real-usage-pending 改已驗證（附 bridge jobId）③下游引用面（review-engine／judge-review／post-build）rg 掃描無 drift④工單模板含授權失效條款（與恢復鏈治理卡③同步）〕
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
triage 併入 AIR-60（session 接續×review closure 治理弧段二）——user 09-10 拍板關聯合一連續做；原 desc 全文見本卡 Description。
<!-- SECTION:FINAL_SUMMARY:END -->
