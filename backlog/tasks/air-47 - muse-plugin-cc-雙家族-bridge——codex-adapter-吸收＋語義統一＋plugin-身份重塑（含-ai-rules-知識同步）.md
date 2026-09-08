---
id: AIR-47
title: muse-plugin-cc 雙家族 bridge——codex adapter 吸收＋語義統一＋plugin 身份重塑（含 ai-rules 知識同步）
status: To Do
assignee: []
created_date: '2026-09-08 11:59'
updated_date: '2026-09-08 12:08'
labels:
  - bridge
  - external-runtime
dependencies: []
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
官方 openai-codex plugin 停更（user 09-08 觀察）→ codex 委派路徑維護真空，由自有 bridge 接管：muse-plugin-cc 升級雙家族委派入口（codex adapter 吸收＋語義統一＋plugin 身份重塑＋ai-rules 知識同步）。〔baseline：muse-plugin-cc dd2e19b；ai-rules a10f2b2〕〔已決策勿重辯：①吸收進自有 bridge（非 fork 官方 plugin、非另開新 repo）；②repo 改名＝in-place rename（GitHub redirect 保 history）、與雙家族能力同一 coordinated release，plugin 身份重塑（plugin 名/agent/skill 名/marketplace 重發）是 breaking 主帳；③命名原則＝名字描述 bridge context、家族只出現在 family 軸（task --family muse|codex＋per-family agent 命名）；④語義統一沉 bridge 層（timeout/resume 對外單一形），ai-rules 端拆家系判讀知識刪除；⑤官方 openai-codex plugin 退役（registry/知識引用移除，raw CLI 語義留 memory reference）；⑥決策層不動（eligibility gate/role→family 映射/「codex 額度最少預設不派」照舊）；⑦前置已滿足（09-08 落地）＝--session-id 弧完成：muse-plugin-cc a52a3d7、v0.2.6 發佈＋本地 cache repoint——bridge ≥0.2.6 暴露 task --session-id <uuid>（絕對定址，顯式值優先於 --resume-last）；⑧前置查證已過（09-08 v0.2.6 成功發佈 muse-market——發佈權實證在 user 手）〕弧形狀（開工跑 execution-plan 展开 EP）：core/adapter 抽離→codex adapter→語義統一→plugin 身份重塑＋marketplace 重發→ai-rules 知識同步（四檔＋memory 2-3 條）。〔驗收：--family muse|codex 兩家族 task/runs/show/wait 全鏈綠（既有測試不破＋codex adapter 新測試）；timeout/resume 對外單一語義；plugin 新名 marketplace 重發＋重裝可用；ai-rules 端 model-routing skill＋rules pointer＋AGENTS＋agents/AGENTS＋work-order＋memory 引用面同步完畢；官方 codex plugin 引用退役〕
<!-- SECTION:DESCRIPTION:END -->
