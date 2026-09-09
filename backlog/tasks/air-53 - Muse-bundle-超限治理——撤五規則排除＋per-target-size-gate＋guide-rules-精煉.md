---
id: AIR-53
title: Muse bundle 超限治理——撤五規則排除＋per-target size gate＋guide/rules 精煉
status: To Do
assignee: []
created_date: '2026-09-09 02:09'
labels:
  - governance
  - context
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 862c2d0〕〔已決策勿重辯：①撤 MUSE_MECHANICS_EXCLUDE——五份被排除 rules（tool-discipline/symbol-query-routing/model-routing/context-management/instruction-writing）的排除理由被逐條反駁（含 Muse 通用約束；「Muse 不寫 instruction」與工單可指定編輯矛盾），恢復全部 16 份 neutral rules 常駐②deploy_agents 改 per-target size gate（Muse 65,536B／ZCode 100KiB 各自 gate）③精煉＝合併重複敘述非刪約束（Volume 單位/CA 邊界/sizing 會計/worktree ownership 全保留）——rules+guide 18 檔 205+/690-④mosaic AGENTS.md 42,887→24,327B 精煉（卡 branch 慣例段已吸收）⑤context-management checkpoint 落盤與外部工單唯讀衝突＝工單範圍限制優先。執行＝codex session 01a083ae（usage 盡），ZCode 主 session 代收尾（查證：26/26 tests 綠、bundle 38,830B 實測、loader 98,923B 截斷→無警告 codex 實證）〕〔驗收：①muse bundle ≤65,536B（實測 38,830）②deploy tests 綠③三端 bundle 新鮮度④muse flash post-build 審查（進行中）〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 bundle 38,830B＋tests 綠＋post-build muse flash 審查過
<!-- AC:END -->
