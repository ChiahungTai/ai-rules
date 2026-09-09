---
id: AIR-54
title: 跨池記憶主體遷移——muse project memory 一等公民＋CC/ZCode symlink＋inbox 寫入流（含 mosaic 移植）
status: To Do
assignee: []
created_date: '2026-09-09 02:47'
updated_date: '2026-09-09 06:24'
labels:
  - memory
  - governance
  - cross-harness
dependencies: []
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：09-09 實驗鏈全驗——muse project scope 注入（14 檔 copy 投影實測：MEMORY.md 全文＋清單列 13 檔）、hooks deny 契約（hookSpecificOutput/permissionDecision，擋 add_memory 實證）、add_memory 裸寫（純 content 零 frontmatter 不動 index）、memory 機制拒 symlink（read_memory 報錯）；材料＝.agent-tmp/muse-hooks-findings.md＋poc_muse_projection.py〕目標：記憶主體遷至 <repo>/.agents/memory/（muse project memory），CC 端 ~/.claude/projects/<encoded>/memory 換目錄 symlink 透明讀寫，ZCode 既有鏈雙跳；muse 從唯讀消費者升一等公民（CP 最高 runtime 零適配），寫入流走 inbox（hook 導流→CC/ZCode consolidation 補 frontmatter＋六問）。〔已決策勿重辯：①主體＝project scope repo 內＋gitignore（非 personal_project——路徑文檔化合約、不怕 muse 重置私有資料；user 09-09）②寫入流＝inbox 先行（「先 inbox 看看」，直寫主體留後議）③一張卡含 mosaic 移植④與 AIR-48 平行推進——muse 品質閘引用其三判準（純機械/單入口/無語義例外）⑤copy 投影過渡形態遷移完成即退役⑥AGENTS.md「Muse memory 唯讀」段隨弧改寫（muse 成受約束寫入者）〕〔驗收：①三端等距驗證——CC/ZCode 開場經 symlink 載入主體如常、muse read_memory project scope 可讀 ②池 git 歷史連續（.git 搬家後夜間收斂波正常跑）③治理路徑全同步（generator/Stop hook/夜間 cron/telemetry——rg 掃描舊路徑零殘留）④muse hooks 品質閘＋inbox 流落地可跑 ⑤mosaic 多 worktree 解法落地（owning 線實體＋其餘 symlink）⑥過渡投影退役＋AGENTS.md/條目/文檔同步〕
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔開工 handoff 09-09 晚——AIR-50 閉環後 center 交接〕排序拍板不變（51✓→53✓→50✓→**54 開工**→52）。baseline：8c4fa14（main HEAD；最後一顆 86e0602 已 push、8c4fa14 待 push）。開工起手式：checkout -b air-54（自 main）→ task edit air-54 -s In Progress → 開工雙 ref → code-reality snapshot --label air-54（勿跳——handoff 續跑弧 4/4 漏這步實證）→ 讀 EP 進 /implement。EP＝本任務家 ep.md（167b87d 定稿——獨立 context review 16 findings 全 apply；S0 段已砍〔user 討論定案〕、S1 手術程序＝mv＋側備份＋併發 guard、S3 hook 絕對路徑、SM 擴至 14 場景）。已決策勿重辯：①Muse 在本 repo 只讀不寫（禁 add_memory/edit_memory——共用池寫入由 ZCode/CC 側）；②memory spine 住 ~/.agents/memory-spine/（plain md＋frontmatter，條目 ai-rules 側寫入、各池 generator 認養 routing 行段）；③過渡形態：.agents/ 投影由冪等腳本 .agent-tmp/poc_muse_projection.py 刷新（結案蒸餾後手動重跑）；④23:40 cron 動檔順序 54 先改路徑 52 後改口徑。在飛事項：AIR-50 審計弧的 muse 跨家族 review 腿背景執行中（bridge job——findings 回來若有採納項由現 session 修正補 commit，不阻塞 54 開工）；hook live 觸發驗證＝下個 CC session 的 hook log（memory-hook-events.jsonl 首筆）。tier：主弧 GLM in-harness。workspace：ai-rules 主 WT（main）。卡歸屬：AIR-54 本 repo board。

〔開工 handoff 09-09 command center〕S1-S5 本 session（S6 mosaic 後延另 handoff）。baseline d430b0f。前置檢查：AIR-50 muse 跨家族補審是否收斂（未收斂→先做只讀盤點、勿進 S1 手術）。起手式：checkout -b air-54 → In Progress → 開工雙 ref → code-reality snapshot --label air-54。S1 手術時序避 23:40±30min；whole-rename＋側備份＋E2E 矩陣全綠才刪 .bak（EP 內程序自足）。muse bridge task ×3 驗證點（S1 read_memory／S3 攔截實測／recall sentinel）。勿重辯：主體 project scope／inbox 流／WAL light／CAS v1／mosaic 直寫廢止。收尾含整體記憶機制審視（含 ZCode）——EP 收尾步驟 6。
<!-- SECTION:NOTES:END -->
