---
id: AIR-13
title: 統一 external-runtime subagent 架構定案＋首批委派工單
status: In Progress
assignee: []
created_date: '2026-09-03 04:31'
updated_date: '2026-09-03 13:25'
labels:
  - muse
  - model-routing
  - delegation
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/ai-rules/_tasks/09-03-air13-unified-subagent-arch/index.html
  - ai-analysis/_tasks/09-03-air13-unified-subagent-arch/index.html
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
三層架構落地（09-03 三臭皮匠合併定案＋雙 ep-review 回寫）：①model-routing rule+skill 增 external-runtime routing 節——family 軸（GLM in-harness tiers 照舊；muse=實作／external second-opinion review／advisory 掃描，具視覺能力；codex=診斷 rescue；in-harness acceptance reviewer=GLM 主審委派工單）＋五條 eligibility gate＋reviewer 交接契約。model id 與容量數字單一源=skill 解析表（兩層契約：agents/zcode pin 為允許 materialization 須比對一致；rule/模板層 family/profile-only）。②registry 維持 thin forwarder（鑑=muse-plugin-cc FIX-S3-R2），特化長在 spawn flag profile（advisory/implement/review），落 agents/AGENTS.md 治理段。③工單模板 skills/_common/work-order.md——十節硬欄位：紅線首段（預設禁 git add/commit/push）／目標／baseline identity／必讀／已決策＋矛盾例外／範圍／工具接線／驗收（命令＋預期）／證據紀律＋PII 禁令／交付報告格式；foreign runtime 共用、派發一律背景跑。批次 triage：直做三小項（review-engine 背景句 pointer／python-standards 相對 import 行／at-skill miss 允許 no-op——現況已預跑全未承載）；委派兩項首用工單（受影響測試集三處〔錨 mosaic_alpha 9f151add、證據三級〕、post-build 四缺口）＋量測四欄；後議三項人先定邊界（四律九律／debugging+modern-cli 擇要／contracts.md muse 對照欄）。API-provider 議題歸 muse-plugin-cc 側。bridge roadmap 三條（--disable-write 暴露、-w worktree 暴露、task 類 job 加 export）記錄轉 muse-plugin-cc。已決策勿重辯：三層分工／thin forwarder／模板泛化／兩層契約（三臭皮匠共識＋雙 reviewer 修正＋user 裁定 09-03）。驗收：精確詞 rg 殘留零命中＋/consistency 過＋首批工單 reviewer record 在 EP＋consumer disposition table 13 檔＋deploy cmp＋90KiB gate 未爆。EP：ai-analysis/_tasks/09-03-air13-unified-subagent-arch/ep.md
<!-- SECTION:DESCRIPTION:END -->
