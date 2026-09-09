---
id: AIR-68
title: delegate-rescue wrapper 退役——/delegate 命令直呼化＋agent 刪除（取代性已驗證）
status: To Do
assignee: []
created_date: '2026-09-09 22:14'
labels:
  - governance
  - bridge
dependencies: []
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
09-10 bridge 回收斷鏈事故（wrapper 派 codex advisory 未收）→二輪雙顧問（muse＋codex）＋三面掃描（ZCode db 49 spawn/CC 零/ledger 99 jobs）＋3 POC 定案：wrapper 全功能面有直呼等價物且全面更優（主 session 背景 Bash 直呼——零 GLM 開銷＋exit 自動喚醒通知，POC-1 閉環實證；flag 正規化本就是 caller 責任；>2KB prompt-file bridge 自動；收法直呼更強）。user 拍板：功能可取代即退役。範圍（delegate-bridge repo，EP 建其 00-tasks/——AIR-47 跨 repo 卡慣例）：S1 過渡防護（wrapper prompt fail-loud＋description deprecated 句）；S2 /delegate 命令重寫（commands/delegate.md:56 spawn subagent_type 形態→caller 背景 Bash 直呼 bridge，--background/--wait 映射 Bash run_in_background/wait）；S3 delegate-runtime skill 改寫（agent 內部契約→caller 直呼契約）；S4 刪 agents/delegate-rescue.md＋文檔同步（plugins/delegate/AGENTS.md:13、repo AGENTS.md:70,78、reference/AGENTS.md:25）＋tests/s3s4.test.mjs:546,601（S3 contract 釘住 agent 檔案）；S5 dist 重打包＋marketplace 版號。驗收：rg delegate-rescue 零殘留（歸檔 EP 除外）＋bridge repo tests 綠＋/delegate 直呼形態實測＋CC/ZCode plugin 升級後 agent 清單無殘影。ai-rules 側不併弧（rule promotion 一行已掛 AIR-66）。素材：.agent-tmp/subagent-usage-{zcode,cc,bridge-rules}.md＋bridge-*-wait-*-out.txt（兩輪顧問全文）。
<!-- SECTION:DESCRIPTION:END -->
