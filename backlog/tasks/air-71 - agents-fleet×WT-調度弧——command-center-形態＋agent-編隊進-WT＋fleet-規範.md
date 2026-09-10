---
id: AIR-71
title: agents fleet×WT 調度弧——command center 形態＋agent 編隊進 WT＋fleet 規範
status: To Do
assignee: []
created_date: '2026-09-10 01:50'
labels:
  - governance
  - agents
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User 09-10 願景：一個 command center session 一次控制多卡（各卡對應 WT、每 WT 兩三個 agents 協同）——user 不再當 WT 間搬運工（mosaic 三 WT 痛點：context 經 user 轉譯）。分層：L0 user（一個 viewport）→L1 調度層（CC session：wt-open/close 呼叫者＋agent 編隊＋跨卡對帳，不寫 code——即本日 CC 形態的泛化）→L2 執行層（每卡一 WT，卡內 writer＋reviewers×2＋judge 編隊）→L3 shared（board control plane＋memory symlink＋bridge ledger）。範圍三段：〔A 調度層設計〕agents 進 WT 的機制（bridge cwd 參數／絕對路徑守則升級為主形態／worker session——對照 mosaic B 研究的三案）＋agents 共享黑板（.agent-tmp/<卡>/ 落盤近似 CC agent teams 的 teammate 互訊——ZCode 無原生）＋CC context 預算（產出落盤只收 verdict——bridge 收法泛化）。〔B fleet 規範〕並行度成文上限（實測 max 11/min 無規範）＋成組慣例（fan-out 1-5 顆實態）＋失敗階梯擴充（registry 缺 type 22 次＋MCP 快照缺工具 7 次——現階梯只覆蓋 review 429）＋fleet 成本量測腿（metadata.json totalTokens 機械彙整——flash 硬 pin 是否真省零數據）＋stopped 52 顆回收慣例。〔C routing drift 查證〕review 主鏈實況 full 為主（4164 vs 760 turns）vs model-routing reviewer-lite 預設（user 09-09）——查因（規則未被遵守還是實務反轉需回改規則）＋ZCode:CC 12 倍量差分工成文＋wait<jobId>與 childSessionId 兩套接續機制對帳。素材：.agent-tmp/research-agents-fleet.md（1785 spawns 實態＋CC agent teams/workflows＋codex subagents 機制對照＋16 報告盤點）。前置：AIR-72（wave-1 基建——wt-open/close 是調度層的手）。產出：blueprint workflow.md 調度層節＋agent-workflow skill 擴充＋規範落 rules/skills＋muse/codex 顧問討論定案。
<!-- SECTION:DESCRIPTION:END -->
