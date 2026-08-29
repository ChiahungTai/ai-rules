# [tag:agents] EP 追蹤：agents tier registry 與兩跳 model 解析

## 目標
agents/ registry split（shared/zcode/claude）＋ model-routing 兩跳改寫＋三顆 tier-pinned agent。

## 結算
- EP：`ai-analysis/execution-plans/_done/ep-agents-tier-registry.md`（docs mode、S1-S4 全段完成＋post-build gate 閉環）
- S1 model-routing 兩跳改寫＋13 處引用同步（殘留掃描零命中）
- S2 registry split＋4 symlink＋頂層翻轉＋AGENTS.md 治理段
- S3 lite-verify／spec-miner／vision-review 三顆（glm-5.3-flash＋thoughtLevel: high）
- S4 deploy 3/3（17 neutral、bundle 94% gate）＋kanban 建卡
- ⚠️ 待新 session 驗證：ZCode spawn smoke（registry 快照）＋CC 端清單確認
