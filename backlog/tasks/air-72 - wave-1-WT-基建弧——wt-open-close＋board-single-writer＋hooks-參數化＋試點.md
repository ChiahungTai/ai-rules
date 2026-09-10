---
id: AIR-72
title: wave-1 WT 基建弧——wt-open/close＋board single-writer＋hooks 參數化＋試點
status: To Do
assignee: []
created_date: '2026-09-10 01:50'
labels:
  - governance
  - wt
dependencies: []
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Blueprint workflow.md『待建基建』清單全部（ai-analysis/blueprint/workflow.md 定案）：①scripts/wt-open.sh（只接已存在 card——lock→驗卡→worktree add 自 owning 線→池/inbox symlink 兩條→muse hooks 重跑或參數化〔二選一〕→{toplevel,branch,card,baseline} 驗證→回報 cwd 啟動 session）＋wt-close.sh（lock→preflight→rebase/ff-only 既有收斂→board finalization→worktree remove→釋鎖）。②board single-writer：check_active_branches false→true＋卡 metadata（status/ref/id allocation）只有 board-control 可寫＋跨 WT max-id 預掃（補 untracked/staged 盲區）＋kanban SKILL 條款。③muse hooks 路徑參數化（.muse/hooks.json 絕對路徑半殘修——WT 內寫得到讀不到）。④outward 特赦裁定（metadata commit 擴展——user 裁）。⑤AGENTS.md git 慣例 WT 版（過渡條款收斂：primary checkout 模式→control/execution plane）。⑥試點一卡驗證（外卡落點歸零/撞號預掃/relay 新鮮度三項即驗）＋ephemeral WT fast-path（免卡小修）。融合定案吸收（reports/2026-09-10-wt-research-synthesis.md §六）：identity contract（owning_line/base/task/branch/WT path 落盤）＋scratch 三條件 materialize（①main 被卡佔用②review 期間 main 續推進③污染性測試）＋per-WT stale state 檢查位（.code-reality index/bridge ledger/backlog 副本）＋錯峰聲明落 card desc 欄位。驗收：試點卡全流程（wt-open→工作→wt-close→board Done）機械證據＋verify-memory-topology 在 card WT 通過＋blueprint workflow.md ❌TODO 標記升級。
<!-- SECTION:DESCRIPTION:END -->
