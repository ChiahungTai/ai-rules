---
id: AIR-52
title: 治理同步弧——排程解綁＋registry 外部依賴反查＋跨 repo 消費端檢查＋memory B 形態跟進
status: To Do
assignee: []
created_date: '2026-09-09 01:35'
labels:
  - governance
  - doc-sync
dependencies: []
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 78c2f06〕standup 誤刪事件（09-09：ai-rules 端盤點看不見 mosaic 23:20 任務依賴——skill 已從 f7e60dc^ 恢復）暴露排程綁定型 doc-drift；同日 memory B 形態審查抓 23:40 cron prompt gate 數字過時（A 形態 22,500/21,000/190——B 形態下波段收斂流入觸發失能）。四段：S1 排程解綁 15 處（audit-test×4/daily-maintain×3/standup×3/maintain×1/skills-CLAUDE×1/kanban-board×1/cr-query×2）——行為契約留、時刻/系統名去；S2 schedule-registry.md 增「外部依賴反查表」A1-A5（mosaic 23:20→daily-maintain/standup/audit-test；23:20 夜間看照→memory-audit 等〔prompt 未證實〕；launchd backlog-cleanup 雙 plist→kanban-board/scripts/backlog_precheck.sh；ai-rules 三 cron→memory-audit/corrections-weekly；report-server→ai-analysis/report-assets）；S3 消費端檢查清單補跨 repo 掃描（歸屬候選：acceptance-evidence 雙掃段路徑集擴充——launchd plists＋目標 workspace memory＋消費端 repo deploy/）；S4 memory B 形態跟進（CronUpdate 23:40 prompt 改動態 gate 口徑＋cross-verify memory 軸/commit 2.8 掃描面補 _inventory.md 檢索語義）。〔已決策勿重辯：①排程事實住排程系統＋registry、skill 只寫行為契約（user 09-09「這種定時任務不應該綁定在 Skill」）②mosaic README 排程表不動（排程表本該記載）③恢復配套已就地改寫「由排程載體整合」（時刻字樣不回填）④B 形態 gate 口徑單一源＝generator 輸出行，cron prompt 不硬編數字〕〔驗收：①15 處改寫後 skills/ 內排程字樣僅行為契約語義（rg '23:20|nightly-sequence|com\.mosaic' 驗證）②registry 反查表 A1-A5 與 plist/腳本實況對帳通過③23:40 prompt 引用動態 gate（無硬編數字）④mosaic 23:20 連續兩晚正常產出（昨日活動節在場）⑤memory 審查其餘面（kanban-board 蒸餾第三動/corrections-weekly telemetry/instruction-init B 形態蓋章）已確認跟上，無需變更〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 S1-S4 全落地＋驗收五項機械驗證通過
<!-- AC:END -->
