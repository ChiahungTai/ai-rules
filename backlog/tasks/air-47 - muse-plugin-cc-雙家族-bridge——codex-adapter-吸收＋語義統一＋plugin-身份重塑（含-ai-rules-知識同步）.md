---
id: AIR-47
title: muse-plugin-cc 雙家族 bridge——codex adapter 吸收＋語義統一＋plugin 身份重塑（含 ai-rules 知識同步）
status: Done
assignee: []
created_date: '2026-09-08 11:59'
updated_date: '2026-09-08 15:13'
labels:
  - bridge
  - external-runtime
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-rules/skills/model-routing/SKILL.md
  - /Users/ctai/Github/delegate-bridge/00-tasks/09-08-dual-family-bridge/ep.md
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
官方 openai-codex plugin 停更（user 09-08 觀察）→ codex 委派路徑維護真空，由自有 bridge 接管：muse-plugin-cc 升級雙家族委派入口（codex adapter 吸收＋語義統一＋plugin 身份重塑＋ai-rules 知識同步）。〔baseline：muse-plugin-cc dd2e19b；ai-rules a10f2b2〕〔已決策勿重辯：①吸收進自有 bridge（非 fork 官方 plugin）；**載體＝新 repo（2026-09-08 user 裁定，推翻原「非另開新 repo」）**；②**新 repo＋帶 history 搬遷（2026-09-08 user 裁定，推翻原 in-place rename/GitHub redirect——原理由不成立：repo 無 remote，搬遷破壞面與 plugin 身份重塑重疊）**，repo 名定案＝**delegate-bridge**（2026-09-08 user 拍板；名字描述 bridge context、家族只在 family 軸——原則③）、與雙家族能力同一 coordinated release，plugin 身份重塑（plugin 名/agent/skill 名/marketplace 重發）是 breaking 主帳；③命名原則＝名字描述 bridge context、家族只出現在 family 軸（task --family muse|codex＋per-family agent 命名）；④語義統一沉 bridge 層（timeout/resume 對外單一形），ai-rules 端拆家系判讀知識刪除；⑤官方 openai-codex plugin 退役（registry/知識引用移除，raw CLI 語義留 memory reference）；⑥決策層不動（eligibility gate/role→family 映射/「codex 額度最少預設不派」照舊）；⑦前置已滿足（09-08 落地）＝--session-id 弧完成：muse-plugin-cc a52a3d7、v0.2.6 發佈＋本地 cache repoint——bridge ≥0.2.6 暴露 task --session-id <uuid>（絕對定址，顯式值優先於 --resume-last）；⑧前置查證已過（09-08 v0.2.6 成功發佈 muse-market——發佈權實證在 user 手）〕弧形狀（開工跑 execution-plan 展开 EP）：core/adapter 抽離→codex adapter→語義統一→plugin 身份重塑＋marketplace 重發→ai-rules 知識同步（四檔＋memory 2-3 條）。〔驗收：--family muse|codex 兩家族 task/runs/show/wait 全鏈綠（既有測試不破＋codex adapter 新測試）；timeout/resume 對外單一語義；plugin 新名 marketplace 重發＋重裝可用；ai-rules 端 model-routing skill＋rules pointer＋AGENTS＋agents/AGENTS＋work-order＋memory 引用面同步完畢；官方 codex plugin 引用退役〕
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
S5 執行記錄（2026-09-08 接手 session）：前段由平行 session 完成（2dfa456＝8 檔同步主體＋raw-facts 條目），user 停該 session 後本 session 接手補缺——①活檔死名 tombstone 清除（openai-codex×3／muse-bridge.mjs×3／.muse-bridge／muse-plugin-cc，分布 AGENTS+agents+zcode-registration+model-routing SKILL）；②memory 合併：raw-facts（缺 stdin/互斥兩事實）併入較早完整的 reference_codex-cli-exec-facts（repo 指針同步）、移 _trash、索引重生成；③S2 知識補落地：export fail-loud（R8）入 SKILL.md、flag 表 codex implement 列 --write 幽靈旗標修正（bridge parseTaskArgs 無此 token）；④弧結案蒸餾：muse-plugin-cc 池 5 條終態化＋索引同步；⑤部署補課：zcode/codex bundle 重生（21:52 版落後 2dfa456，現雙家族條文 3/3 上線）；⑥ripple：.gitignore 加 .delegate-bridge/、draft-2 活路徑更新；⑦驗收：活指令面雙 rg 全清（殘留僅 ai-analysis 歸檔/ref-docs 鏡像/backlog 卡歷史）。live config pins 由 user/delegate-bridge 側先行清除（機械驗證過）。遺留觀察：delegate-bridge v1.0.0 hooks.json description 仍寫舊名（該 repo 側關賬可順手修）；muse bundle 99% gate 警告（既有）。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
雙家族知識同步＋官方 codex plugin 退役完成——S1-S5 全結：delegate-bridge v1.0.0 雙端 delegate@delegate-market、ai-rules 活面死名殘留 0、codex raw CLI 事實單條 exec-facts、muse 池弧流水蒸餾 5 條、bundle 3/3 重部署
<!-- SECTION:FINAL_SUMMARY:END -->
