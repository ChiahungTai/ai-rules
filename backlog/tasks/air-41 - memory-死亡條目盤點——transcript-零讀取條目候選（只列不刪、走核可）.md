---
id: AIR-41
title: Memory body Read 觀測——覆蓋限定候選與用途判讀
parent_task_id: AIR-42
status: In Progress
assignee: []
created_date: '2026-09-07 07:56'
updated_date: '2026-09-07 08:45'
labels:
  - memory
  - governance
dependencies:
  - AIR-40
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：找出可觀測窗內沒有成功明確 body Read 的現存條目，供內容判讀。〔baseline：ai-rules f03d346；依賴 AIR-40 collector 合約〕
〔已決策勿重辯：雙源 ZCode DB+CC JSONL；Read 指工具成功讀條目本體，索引注入/rg/shell 不算本指標，但明列盲區；工作/維護/未知用途分欄，不能把 audit 讀取當使用；90 天是請求窗，不是保留期證明；缺源/解析失敗/已移除 worktree/rename 不確定/其他 harness 缺席都需 coverage 說明；rank hot、近30天mtime、活躍弧豁免，owner未知則 HOLD；零 Read 不推無用、不自動 cold；只報告，不刪改 memory；允許零候選與全部保留〕
〔驗收：真實雙源首跑帶 coverage、失敗與未知；資料不足時仍交付 observed-window 報告但不得稱90天從未讀；fixture 覆蓋 result join/partial Read/clone/dedup/豁免/rename/維護用途；候選人工抽驗可全部保留；memory-audit 接既有證據，不新增常駐排程〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 雙源首跑呈現requested/observed/unknown覆蓋，缺失不冒充零
- [ ] #2 成功 body Read 與工作/維護/未知用途分離，失敗與 unmatched 不算命中
- [ ] #3 hot、近30天mtime、活躍owner豁免；owner或歷史身分不明則HOLD
- [ ] #4 零候選或全部保留合法；無強制刪除、處置或降rank
- [ ] #5 memory-audit 觸發段與索引同步，消費 AIR-40 已驗證 reader 合約
<!-- AC:END -->
