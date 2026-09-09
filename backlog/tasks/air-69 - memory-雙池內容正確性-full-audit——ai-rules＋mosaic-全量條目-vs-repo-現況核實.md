---
id: AIR-69
title: memory 雙池內容正確性 full audit——ai-rules＋mosaic 全量條目 vs repo 現況核實
status: To Do
assignee: []
created_date: '2026-09-09 22:16'
updated_date: '2026-09-09 23:09'
labels:
  - governance
  - memory
dependencies: []
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
動機（09-10 兩實例）：①ai-rules feedback_dual-family-review-dispatch:44 教『spawn delegate-rescue 轉發』錯誤形態（記憶層主動強化錯誤模式——wrapper 是最大 spawn 單型的記憶源，已修）②mosaic project-memory-audit-advisory-only desc 稱『AIR-54 S6 主體進 repo』但 S6 未收斂（宣稱漂移）。內容正確性漂移是常態不是零星。範圍＝memory-audit skill 層 2『內容核實 vs repo』全量形態（full audit——非 lite 增量抽核）：ai-rules 主體 162 條＋mosaic 池全量，逐條 load-bearing claims 對照 repo/規則現況，過時/教錯/宣稱漂移列清單→advisory 報告→user 核可後修正（層 3 分工：登錄舉證、核可後執行）。排序硬依賴：mosaic 側等 AIR-54 S6 收斂後跑（池遷移改實體，舊池 audit 會作廢）；ai-rules 側可先跑。執行形態：full audit 弧（大規模語義工作授權層）＋歸因投影（memory_telemetry attribution）輔助。素材：09-10 掃描三報告 .agent-tmp/subagent-usage-*.md。
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔AIR-54 收尾審查移交——對帳清單 09-10（post-build 三路：flash fresh/primed＋codex bridge job-mtuou4f1-wt7hfk）〕①memory_pack 120 行索引/單條 8KB 數值現駐 skills/memory-audit/SKILL.md「Inbox 消費」節＋池 reference_muse-code-cli-facts——muse 升版兩處須同步重驗；②8KB 單位語義（bytes vs chars）未實測——判讀 8K-12K 治理政策前先以修剪樣本釘住（draft-4 待辦 4 已註記）；③23:40 cron prompt「path contract 五條」vs SKILL 列①-⑥（⑥ edit 專屬）計數措辭——下次修 cron prompt 時對齊，勿為此單獨重放；④同節名「Inbox 消費」跨池掛不同波次載體（mosaic 23:20 看照波 vs ai-rules 23:40 夜波——部署自由非錯，對帳一次即可）。素材：draft-4 修訂版（本日）。

〔CC 09-10 擴充——三方會議裁決承接（ai-analysis/reports/2026-09-10-carrier-placement-v2-conference.md）＋user 拍板全修〕排序依賴解除：S6 已由 mos-88 收斂，兩側均可跑。本弧新增三段：〔A 判準落地〕memory-audit 統一定義表兩處修補——層級閘首句（裁決書§二定版條文逐字）＋誤置表 A/B 兩行；零 bundle 增量硬約束（deployed 36,773B 不增，只刪改指針）；同 commit 完成＋rg 驗零殘留正文（原子性條件）。〔B 先鋒批次 8 條已裁（user 09-10 拍板照辦）〕①bridge-job-completion-no-push→規範正文刪（model-routing 收法段是源），留事故證據＋pointer ②backlog-cli-entry→整條刪 ③global-vs-project-permissions→重寫為 project 現況條（mixed 輕處置）④cross-session-commit-on-active-branch→規範搬 kanban SKILL 建卡段（worktree 直進 main 分流——含今天 user 拍板的 skill 歸屬）＋memory 留事故證據 ⑤backlog-card-edit-precheck→kanban SKILL 卡操作段補 id 對時一句＋留 AIR-26 事故 ⑥skill-deletion-consumer-scan→規範進 instruction-clean/edit-discipline＋事故併入 zcode-skill-usage-audit 後刪（與其重複）⑦work-order-contract-point-to-source→work-order.md 合約段一句＋留事故 ⑧diagnose-installed-vs-source-first→debugging-and-error-recovery skill＋留事故。淨效果：池瘦 ~8-9K chars＋六規範各歸正源。〔C 全量 audit 照原 desc 續跑〕雙向掃描（裁決書§三 forward/reverse lane regex candidate-only）＋歸因投影輔助。執行形態：主 session full。
<!-- SECTION:NOTES:END -->
