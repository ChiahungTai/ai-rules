---
id: AIR-17
title: 夜間收斂 cron 首跑驗證
status: In Progress
assignee: []
created_date: '2026-09-03 04:34'
updated_date: '2026-09-03 22:45'
labels:
  - cron
  - memory-audit
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
automation-751ecce2（每日 23:40、ai-rules 池）明早驗證首跑：報告是否產出（前後 chars/bytes/條目對照＋動作清單）、_audit-state last_index_chars 是否更新、_regen-failed 狀態。異常處置：跑題/未觸發/誤刪——按 at-skill-zcode-cron-gaps 開放項判讀（runCount/lastRunAt 不可推斷）。通過即關卡
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
排程盤點整併已完成（09-03 午）：fed036ff 週日 23:30→23:00（錯開每晚收斂貼背）＋移除寫死 gate 值改動態讀＋補姊妹弧 ≥93% 觸發提示＋審計獨立註記；usage-ping 9/3 completed 殘留已刪（釋放 20-cap）。現存三排程：23:40 每晚收斂（寫手）/23:00 週日治理（審計）/23:10 週六糾正週報。剩：今晚 23:40 首跑驗證。

mosaic 側整併落地（09-03 午後）：收斂波節併入 nightly-watch automation-13dfeb9c（每晚 23:50、不新增排程）；首版誤判兩池（ZCode 路徑 vs Claude 池），readlink 覆核證 symlink 單池後 CronUpdate 定版（單池、desc 門檻 100、波段觸發 chars>21,000、弧線預警 8,000×7d——對齊 919c108 基線）。首跑驗證範圍加一：今晚 23:50 mosaic nightly-watch——報告應含「## 🧹 收斂波」節、_regen-failed 不應殘留、輕掃/波段動作列報告。
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-09-03 22:45
---
【handoff 09-04】任務＝AIR-17 夜間收斂修訂版首跑驗證。接手方式二選一：(A) 已過 09-05 00:05 → 直接執行下方清單；(B) 未到 → CronCreate one-shot（cron='5 0 5 9 *', recurring=false, title='AIR-17 夜間收斂首跑驗證'）prompt 用下方清單全文（排程 session 自足）。背景：23:40 收斂 cron 五腿（①輕掃 24h-mtime desc>100 trim ②弧線軟預警 >8,000chars×7d report-only ③波段收斂 gate FAIL/_regen-failed/chars>21,000→sweep+成功後 rm marker ④L5 清淤 .agent-tmp/.at-contexts>7d、.review>30d ⑤報告 append ai-analysis/nightly-convergence.log self-trim 300K→200K），今晚 09-04 23:40 是修訂版首跑。清單（每項附命令+輸出證據）：1. tail -80 ai-analysis/nightly-convergence.log→09-04 深夜標頭+報告在場 2. fd -H _regen-failed <memory池>/→零命中 3. wc -l/-c MEMORY.md→記錄現值（上限 200 行/25,000 chars，超限紅燈）4. ls -lt .agent-tmp/ | head -20→只清點不刪 5. ls -lt .review/→同 6. log 宣稱的 trim/merge 抽查 2-3 條目 desc 長度對帳（Claim→Evidence）。產出：全過→bash skills/kanban-board/scripts/backlog_precheck.sh（exit 1=停）→過才結案兩步（-s Done --final-summary '夜間收斂修訂版首跑驗證全過——五腿證據齊、marker 零殘留、log 落盤'）；有不過→--append-notes 記錄不結案。紅線：禁 git commit/push/stage；禁改 memory 條目內容（收斂是 cron 的事你只驗證）；禁改 rules/skills/EP；禁刪 .agent-tmp。〔平台事實：本任務原擬由 09-04 session 直接 CronCreate，被擋——隸屬排程的 session 不能巢狀建排程，須乾淨 session 建〕
---
<!-- COMMENTS:END -->
