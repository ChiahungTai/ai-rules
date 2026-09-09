---
id: AIR-54
title: 跨池記憶主體遷移——muse project memory 一等公民＋CC/ZCode symlink＋inbox 寫入流（含 mosaic 移植）
status: To Do
assignee: []
created_date: '2026-09-09 02:47'
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
