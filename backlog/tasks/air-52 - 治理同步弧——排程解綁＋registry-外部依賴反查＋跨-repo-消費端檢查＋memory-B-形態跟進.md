---
id: AIR-52
title: 治理同步弧——排程解綁＋registry 外部依賴反查＋跨 repo 消費端檢查＋memory B 形態跟進
status: In Progress
assignee: []
created_date: '2026-09-09 01:35'
updated_date: '2026-09-09 13:12'
labels:
  - governance
  - doc-sync
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-analysis/schedule-registry.md
  - ai-analysis/schedule-registry.md
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔開工 handoff 09-09 command center〕S1-S3 可即跑（純文檔面，與今晚首波零衝突）；**S4 的 CronUpdate 必須等今晚 23:40 首波完成後**（波前/波中禁改 cron prompt），且基於現行 prompt（路徑欄已被 AIR-54 S2 改指 .agents/memory——CronList 讀現版勿按卡 desc 舊想像）。P5 watchdog 歸屬（daily-maintain 記 23:20 vs registry 無此條）＝S1 解綁範圍一併處置。schedule-registry.md 已被 AIR-54 動過（夜波 scope）——S2 增表對帳現版。branch air-52 自 main 開（air-54/59 未 merge，重疊檔 merge 時 git 自然處理）。起手式：checkout -b air-52 → In Progress（已是）→ 雙 ref → snapshot --label air-52。

〔S1-S3 done 09-09 air-52 session〕S1 17 處落地（卡列 15＋同類隨掃補 2：post-build「夜間 23:40 掃腿」／corrections-weekly「每週六 23:10」）；驗收① rg '23:20|nightly-sequence|com\.mosaic' skills/ 全清、寬掃 23:[0-9]{2} 亦清。S2 反查表 A1-A5 已入 registry（對帳：A3 雙 plist＋cleanup 腳本 precheck 接線、A4 CronList、A5 服務 plist 已核；A1/A2 記載面＝memory reference_periodic-task-landscape——23:20 automationId 在 mosaic workspace 不可直驗，表內標 provenance）。S3 acceptance-evidence 雙掃段路徑集擴充落地。consistency gate 已跑（六維過）。

〔P5 改寫移今晚（段落未進 main）〕Phase 0 段只在 air-59（63a8a19）——air-52 branch 無該文字可改；air-59→main merge＋air-52 rebase 後，將 63a8a19 版 daily-maintain Phase 0 的「**執行者歸屬未驗證（fail-loud）**：本檔 when_to_use／§配合記「ZCode 每日 23:20」…」整段替換為：「**執行者歸屬（解綁後口徑）**：時刻/載體等排程事實住排程系統＋ai-rules ai-analysis/schedule-registry.md「外部依賴反查表」，本 skill 只寫行為契約、不綁時刻/系統名。自動獨立執行的成立條件＝反查表記載的排程載體常態在跑 daily-maintain；無此記載時結案口徑＝git anomaly detector exists; automatic independent execution pending（此時雙故障偵測＝夜波自檢＋人工，不得宣稱自動雙故障偵測）」。

〔S4 今晚首波後（時序硬約束：23:40 首波完成、log 落盤前禁 CronUpdate）〕①CronList 讀現行 prompt（AIR-54 已改路徑欄指 .agents/memory——勿回退）②gate 口徑動態化：移除硬編 22,500/21,000/190/24,000，改「動態讀 GATE_CHARS/GATE_BYTES/GATE_LINES（rg skills/memory-audit/scripts/generate_index.py）＋--check 輸出行」，形態仿週日治理 prompt 段 2 層 1；逼近線改 gate 百分比口徑③cross-verify memory 軸／commit 2.8 掃描面補 _inventory.md 檢索語義（B 形態 routing：MEMORY.md 只是 resident 投影，全量條目住 _inventory.md）④P5 改寫落地（上方文案）⑤收斂後結案兩步＋弧結案蒸餾＋post-build 鏈。

〔今晚 rebase 注意〕air-59→main ff 後 air-52 rebase：①registry「更新時點」行預期一行 conflict（air-54 前綴 2026-09-09 註記 vs 本弧尾注）——解法＝兩則並存②AIR-54 未提交 registry 條 4（一次性驗證 cron automation-d64fd994 記帳行）備份於 .agent-tmp/air-54-registry-row4-pending.{diff,full.md}＋README——歸 AIR-54 收尾 session 在 owning branch 重放，非本弧範圍。

〔command center 補充 09-09 晚〕①S2 反查表建議擴欄「新架構職責註記」（AIR-54 落地後每條排程的職責變化／保留裁決——user 點名要掃排程必要性，此表為機械載體，不另開弧）。②順手項×2：draft-3 檔殼收尾（已被 AIR-53 承接落地，drafts/ 清除）；corrections-weekly SKILL:35 的 --pool 舊路徑示例改指 .agents/memory/（介面路徑經 symlink 仍通＝口徑債非斷線，S2 同檔順手）。③情報：夜波 cron prompt 已被 AIR-54 S4 更新（新路徑+inbox+bundle），S4 只剩 step 1 的 A 形態硬編數字（22,500/190→動態 gate 口徑）。
<!-- SECTION:NOTES:END -->
