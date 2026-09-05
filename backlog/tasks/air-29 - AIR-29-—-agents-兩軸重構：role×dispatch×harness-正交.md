---
id: AIR-29
title: AIR-29 — agents 兩軸重構：role×dispatch×harness 正交
status: To Do
assignee: []
created_date: '2026-09-05 05:46'
labels:
  - meta
  - agents
  - ep-ready
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
registry 兩軸正交：roles/ 單一源（目標→做法→skills，零 model/harness 字樣）＋sync_agents.py 生成式投影（zcode pins＝部署預設）＋dispatch matrix 兩軸（harness 怎樣用／model 按任務選——執行檔 flash≈terra≈sol-high≈sonnet≈muse-spark、判斷檔 opus≈fabel≈sol-max+）＋external 工單 role 段引用。role 集合不動（10 role UC 已驗證），修的是部署面可達性（CC 8/10 不可達、external 無檔面）。〔baseline c83ddf4；spec+ep 在 ai-analysis/_tasks/09-05-agents-two-axis-refactor/；驗收＝CC L4 逐名啟動 10 檔＋--check 綠＋12 命令檔零改動〕
<!-- SECTION:DESCRIPTION:END -->
