---
id: AIR-21
title: muse-plugin-cc bridge wait 子命令——job 輪詢機械化
status: To Do
assignee: []
created_date: '2026-09-03 22:35'
labels:
  - muse-plugin-cc
  - delegation
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
09-04 WO-1 輪詢器實證：orchestrator 手搓 show --json 解析易踩兩坑（status 巢在 job. 下；狀態詞彙 11 個，列舉終態必漏 interrupted/capped）。root fix＝bridge 加 wait <jobId> [--timeout N] [--interval N]——阻塞至終態、輸出 final JSON（含 finalText），orchestrator 零手搓解析。〔跨 repo：實作住 ~/Github/muse-plugin-cc——本卡為 handoff 載體，帶去該 repo session 做〕驗收：wait 對 running job 阻塞正確、終態即出 final JSON、timeout 到期 exit 非 0 帶當前狀態；bridge 既有 tests 過（node --test tests/xxx.test.mjs 形態）。教訓已入 memory reference_muse-code-cli-facts（bridge 段 job 輪詢陷阱）
<!-- SECTION:DESCRIPTION:END -->
