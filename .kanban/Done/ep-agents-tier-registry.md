# [tag:agents] EP 追蹤：agents tier registry 與兩跳 model 解析

## 目標
agents/ registry split（shared/zcode/claude）＋ model-routing 兩跳改寫＋三顆 tier-pinned agent。

## 結算
- EP：`ai-analysis/execution-plans/_done/ep-agents-tier-registry.md`（docs mode、S1-S4 全段完成＋post-build gate 閉環）
- S1 model-routing 兩跳改寫＋13 處引用同步（殘留掃描零命中）
- S2 registry split＋頂層翻轉＋AGENTS.md 治理段（原 4 symlink 農場→08-29 午證偽修正為實檔拷貝＋cmp 同步紀律）
- S3 lite-verify／spec-miner／vision-review 三顆（glm-5.3-flash＋thoughtLevel: high）
- S4 deploy 3/3（17 neutral、bundle 94% gate）＋kanban 建卡
- ✅ 開箱驗證（2026-08-29 新 session）：ZCode spawn smoke 3/3 附證據（lite-verify 正常完成無 pin 報錯；telemetry `model_id=glm-5.3-flash`＋`agent=zcode-lite-verify`）＋CC 端清單確認（`~/.claude/agents`→`agents/claude`，僅 shared 兩顆、零 zcode 專屬檔）
- ✅ symlink 證偽修正驗證（08-29 午）：registry 改實檔拷貝後 CR session spawn code-reviewer PASS（四臂實驗閉環）＋hub telemetry 複核；**殘留＝CC 臂 spawn 未 runtime 驗證**（relay 待跑：CC session 重啟後 spawn code-reviewer）
