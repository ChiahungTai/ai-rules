---
id: AIR-17
title: 夜間收斂 cron 首跑驗證
status: In Progress
assignee: []
created_date: '2026-09-03 04:34'
updated_date: '2026-09-04 05:51'
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

【接手 09-04 08:15｜路徑 B】one-shot 驗證排程已建：automation-8d9c2fea（09-05 00:05，cron '5 0 5 9 *'，prompt=驗證清單全文自足）。跑前基線：nightly-convergence.log 不存在（報告腿修訂版首寫）、_audit-state last_index_chars=17769、ai-rules 池（Claude 實體路徑，ZCode 端 symlink 單池）零 _regen-failed、CronList 確認 automation-751ecce2 在場（runCount=1＝09-03 舊版、nextRun 09-04 23:40 修訂版首跑）。mosaic 側首跑驗證已先行通過：09-03 23:50 nightly-watch 報告（mosaic_alpha/ai-analysis/_inbox/nightly-watch-20260903.md）含「## 🧹 收斂波」節、①6 條 desc 修剪、③波段未觸發列報；三池 fd _regen-failed 零命中。修正註記：handoff 清單「結案前跑 backlog_precheck.sh」對 In Progress 卡固定 exit 1（腳本 L35-36）＝死鎖，kanban-board skill 明文結案兩步不需 precheck——one-shot 改跑等價跨線檢查 git log --all --not HEAD --grep AIR-17（非空=停手不結案）。

09-04 09:00 首跑驗證（mosaic workspace one-shot 驗證腿）——B PASS／A FAIL，未關卡。B（mosaic nightly-watch 23:50）PASS：報告 ai-analysis/_inbox/nightly-watch-20260903.md（23:55 生成、commit 31b3084b）含收斂波三節——①desc>100 修剪 6 條（索引 13,926→13,851 chars）、②弧線軟預警 31 條（頭號 disposition-marking-campaign 145KB）、③波段未觸發🟢；_regen-failed 不存在；_audit-state last_lite_audit=20260903＋last_index_chars 已更新。A（ai-rules 23:40 automation-751ecce2）FAIL＝未觸發（零產物）：①池 _audit-state.md mtime=09-03 08:13（白天治理輪所寫，last_index_chars 17769 非夜跑更新）；②昨夜 23:30-00:59 時窗池零檔案變動（find 空）；③repo fd 12h 掃描無收斂報告、_inbox 空；④睡眠假說排除——host 在線（mosaic 23:50 十分鐘後正常觸發落地）。歸因（open，mosaic workspace 看不到對方 automation 狀態，不猜）：dispatch 撞並行 session 被吞（ai-rules 昨夜～今晨活躍——bundle 減量弧 ae3bc28/e2c302f 正是對 mosaic 23:55 報告 95.1% 警戒的反應，09-04-rules-bundle-diet ep.md mtime 06:28）／automation 已停用或刪除／觸發即靜默失敗。建議：ai-rules 側自查 automation-751ecce2 在場與否（CronList）；卡等 23:40 首次成功跑過再關（通過即關卡不變）。

勘正（09-04 09:0x，mosaic 驗證腿讀卡後撤回前則）：前則「A FAIL＝未觸發」判定撤回——本卡 08:15 路徑 B 註記已證 runCount=1＝09-03 23:40 舊版有觸發；零產物與修訂版前無報告腿一致（nightly-convergence.log 係修訂版首寫），非 dispatch 被吞/停用。09-03 23:40 舊版跑不在本卡驗證範圍（卡上驗證項按修訂版行為定義）；真正首跑＝09-04 23:40 修訂版，驗證腿＝ai-rules 側 automation-8d9c2fea（09-05 00:05，五腿清單自足）。mosaic workspace one-shot（automation-d348ea38，已 fire 完成退場）任務結束：B（mosaic 23:50）PASS 證據保留於前則；卡維持 In Progress 等 09-05 00:05 驗證。另：本 one-shot prompt 原載「結案前跑 backlog_precheck.sh」有死鎖陷阱（In Progress 卡固定 exit 1，08:15 註記已證）——幸未走到該路徑，勘正後以 git log --all --not HEAD --grep AIR-17 等價檢查為準。
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-09-03 22:45
---
【handoff 09-04】任務＝AIR-17 夜間收斂修訂版首跑驗證。接手方式二選一：(A) 已過 09-05 00:05 → 直接執行下方清單；(B) 未到 → CronCreate one-shot（cron='5 0 5 9 *', recurring=false, title='AIR-17 夜間收斂首跑驗證'）prompt 用下方清單全文（排程 session 自足）。背景：23:40 收斂 cron 五腿（①輕掃 24h-mtime desc>100 trim ②弧線軟預警 >8,000chars×7d report-only ③波段收斂 gate FAIL/_regen-failed/chars>21,000→sweep+成功後 rm marker ④L5 清淤 .agent-tmp/.at-contexts>7d、.review>30d ⑤報告 append ai-analysis/nightly-convergence.log self-trim 300K→200K），今晚 09-04 23:40 是修訂版首跑。清單（每項附命令+輸出證據）：1. tail -80 ai-analysis/nightly-convergence.log→09-04 深夜標頭+報告在場 2. fd -H _regen-failed <memory池>/→零命中 3. wc -l/-c MEMORY.md→記錄現值（上限 200 行/25,000 chars，超限紅燈）4. ls -lt .agent-tmp/ | head -20→只清點不刪 5. ls -lt .review/→同 6. log 宣稱的 trim/merge 抽查 2-3 條目 desc 長度對帳（Claim→Evidence）。產出：全過→bash skills/kanban-board/scripts/backlog_precheck.sh（exit 1=停）→過才結案兩步（-s Done --final-summary '夜間收斂修訂版首跑驗證全過——五腿證據齊、marker 零殘留、log 落盤'）；有不過→--append-notes 記錄不結案。紅線：禁 git commit/push/stage；禁改 memory 條目內容（收斂是 cron 的事你只驗證）；禁改 rules/skills/EP；禁刪 .agent-tmp。〔平台事實：本任務原擬由 09-04 session 直接 CronCreate，被擋——隸屬排程的 session 不能巢狀建排程，須乾淨 session 建〕
---
<!-- COMMENTS:END -->
