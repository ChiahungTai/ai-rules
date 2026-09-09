---
id: DRAFT-2
title: muse/grok telemetry 記錄面探測——可行則接線、不可行則揭露定案
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
目標：判定 muse 與 grok 的 session 工具呼叫記錄是否存在可解析面。線索：muse CLI 有 export/trace 子命令（~/.config/muse/ 僅 config 無 session 目錄——記錄位置待探測，可能 XDG data）；grok-build plugin（bridge 同族）runs 面有 runId 記錄、本地路徑待探測；bridge ledger（.delegate-bridge/jobs/*.jsonl）只覆蓋 bridge 派發任務非全部 session。產出：探測結論——找到結構化 tool call 記錄（file_path+時間+成敗）則另開接線卡對齊 read_codex 形態；只找到對話 transcript 無工具面則 uninstrumented 揭露定案（記錄探測證據）。bash-rg 無記錄面屬定義性盲區、不在此卡。

〔user 09-08 註記：全 draft 暫緩——等真的用再處理。**前置注意**：muse local memory 機制與 CC/ZCode 結構性不同（三 scope／`.agents/memory/` 命名空間／index 注入上限 48 檔／background observer 主動召回／untrusted 也載入）——telemetry 歸因設計以「muse 不用自家 memory、寫我們的池」為前提，若改走 muse 自家 memory 則此卡與歸因機制都要重新設計（詳 memory 條目 muse-memory-mechanism-divergence）〕
<!-- SECTION:DESCRIPTION:END -->

## Notes

<!-- SECTION:NOTES:BEGIN -->
〔AIR-54 S5 標記 2026-09-09〕**探測目標已完成**：muse session 工具呼叫記錄面＝`~/.local/share/muse/sessions/<date>/<session-id>/`（session.jsonl 含 tool call 事件流；hook 事件 `hook_run_started`/`hook_run_terminal` 也在場——09-09 hooks 實驗即以此驗證）。**歸因前提已變更**：user 註記的「若改走 muse 自家 memory 則此卡與歸因機制都要重新設計」已命中——AIR-54 落地後 muse 讀 repo `.agents/memory/` 主體（project scope）、寫經 inbox（hook 攔截代存，`.agents/memory-inbox/` 的 payload JSON 即結構化寫入記錄面）。telemetry 接線若要做，輸入源已從「探測未知」變成兩個已知面（muse session.jsonl＋inbox payload）；grok 腿仍未知。本 draft 續留（接線未承諾），探測段份已了結。
<!-- SECTION:NOTES:END -->
