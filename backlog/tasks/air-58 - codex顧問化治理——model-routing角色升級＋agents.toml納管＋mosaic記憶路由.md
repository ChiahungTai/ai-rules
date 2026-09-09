---
id: AIR-58
title: codex顧問化治理——model-routing角色升級＋agents.toml納管＋mosaic記憶路由
status: To Do
assignee: []
created_date: '2026-09-09 21:45'
updated_date: '2026-09-09 21:45'
labels:
  - codex
  - model-routing
  - memory
  - agents-registry
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
09-09 查核定調 codex＝超強力顧問（規劃/審查五角色：spec、execution-plan、ep-review、code-review、judge-review）。基建已實證 90% 在位（rollout 解剖：bundle 40,092B 全載 sentinel 在場、skills 經 ~/.agents/skills symlink 進 codex USER scope、$skill-link 調用實測成功、memory 三層注入健康）；bundle 砍 rules 已裁決不砍（AIR-53 前例：角色約束歸工單不歸 bundle；codex 自身 memory 記有「直接修好」使用模式，實作守則在場是保護面非死重）。

本卡收斂三個治理缺口＋一個決策記錄：

S1 model-routing codex 角色升級：現值「額度最少、預設不派、僅 user 顯式指定」，sweet spot 備註只有 state-review。user 09-09 定調：webgpt model 導入後額度改觀「可能可以多用了，不過還要再確認，才剛開始用」——先擴 sweet spot 備註為「規劃/審查弧跨家族第二意見候選（webgpt 觀察期）」；dispatch 預設翻轉（預設不派→顧問角色可派）等 webgpt 穩定度確認後另行拍板，本卡不翻。webgpt 現值快照：model=chatgpt-web/medium、bridge openai_base_url=127.0.0.1:17841（codex-chatgpt-web 管理）。

S2 ~/.codex/agents/*.toml 治理：現況五檔——code-reviewer/code-reviewer-primed 是 08-18 手動複本（內容仍合當前方法論，但不在 sync_agents.py 管線＝drift 風險）；codebase-memory/scout/auditor 是 codebase-memory-mcp 自帶三層查證 agents（Scout/Verify/Auditor tier、read-only graph 面，非 ai-rules 物，不動）。決策：ai-rules 二 toml 納入 sync_agents.py codex 面（roles/ 單一源生成 codex registry——需查 codex subagents 的 toml 欄位契約，ref-docs/harness/codex/subagents.md）或刪除；CBM 三個排除在治理外。

S3 mosaic 記憶路由修復（user 09-09 拍板「這要修」）：mosaic_alpha AGENTS.md 無任何 codex/觀察池路由——zcode/CC 側教訓不會流進 mosaic 場的 codex。telemetry 證據：CC 側 09-09 仍在寫 mosaic 池（~/.claude/projects/-Users-ctai-Github-mosaic-alpha/memory/，project-consistency-sweep、project-arch-tours-drift-audit 等）——教訓在累積、codex 看不到。修法：mosaic AGENTS.md 補觀察池路由段（codex 唯讀 CC 池＋zcode 池＋spine ~/.agents/memory-spine/），照 ai-rules repo AGENTS.md「觀察池路由」先例寫法；跨 repo 寫入由 mosaic 側 session 或本卡明示 cross-repo 段落執行。mosaic_alpha_offline_backtesting / mosaic_alpha_trading_lab 同型一併評估。

S4 決策記錄（無改動）：bridge 工單饋入 codex memory 生成＝保留。評估：符合 memory 原則——codex 官方 pipeline 自帶寫入端紀律等價物（extract/consolidation 雙模型、max_unused_days decay、secrets redact、rate-limit gate、idle-wait），memory_summary 實證品質良好（AIR-50/MOS 知識可用）；退場 knob 供日後翻案：thread 級 /memories、memories.disable_on_external_context=true（bridge 工單有用 MCP 面）。附帶已完成（09-09 本弧）：~/.codex/config.toml 過時註解 79KB→40KB 修正（backup config.toml.bak-advisor-0909）。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 model-routing skill codex 段 sweet spot 備註擴為規劃/審查弧候選（webgpt 觀察期語意）；dispatch 預設不變
- [ ] #2 agents/*.toml 決策落地：ai-rules 二 toml 納 sync 管線（codex 面生成）或刪除，drift 面歸零
- [ ] #3 mosaic 側 AGENTS.md 觀察池路由段落地，codex session 實測讀得到池
- [ ] #4 S4 決策與 knob 記錄歸檔（卡或 model-routing/memory-audit 引用面擇一）
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
<!-- SECTION:FINAL_SUMMARY:END -->
