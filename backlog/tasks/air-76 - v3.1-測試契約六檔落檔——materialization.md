---
id: AIR-76
title: v3.1 測試契約六檔落檔——materialization
status: To Do
assignee: []
created_date: '2026-09-11 05:50'
labels:
  - governance
  - testing
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
兩天最大定案零承載收斂（tri-audit X1/X2 雙 🔴）：測試契約 v3.1（三方裁決 reports/2026-09-11-test-contract-design.md）落檔六 skill＋routing 鏈＋附帶同步面。〔baseline：ai-rules 4b0d2b7〕〔已決策勿重辯：①v3.1 終態——獨立性買 judgment boundary（challenge＋軸B review）非 every authorship；②RED provenance 三栓（receipt 落檔/sha256 digest 凍結/基線跑法）；③test-gen＝P0 最後手段不生成 registry 檔（AIR-70 答案反轉）；④cr-research 升 full 僅一角（Explore fallback 維 lite）；⑤amendment authority 四分——實作現況永遠非證據；⑥same-family precondition producer（EP author_family 欄）＋consumer（implement gate）雙端；⑦MVP 過線標準預凍結，不過線僅 S1 可跑 S2-S7 全停〕風險面：寫入契約首改（六 skill 行為控制面）＋跨文件交叉推導（TC 語彙六檔共享）。跨弧編輯面：AIR-67 同檔異面（roles tier vs 角色定義）、AIR-70 notes 收 test-gen 結論。〔驗收：①MVP 報告過線（challenge recall ≥3/4 誤報 ≤1＋routing 5/6＋attribution 5/6）或 fail-loud 回報；②九 routing 錨點全 full（rg＋roles 直驗＋Explore fallback 未誤升）；③六檔＋code-review-and-quality /consistency 全綠；④全域 rg 殘留掃清單（EP 整合策略）逐條 exit 0；⑤pytest test_sync_agents 綠＋sync_agents --map cr-research=full；⑥blueprint v3.1 節翻 ✅＋workflow ②⑤站補半句〕EP：ai-analysis/_tasks/09-11-test-contract-v31/ep.md（三方審查 22 findings 已吸收：muse 13/GLM 17/codex 5，judge 21 ✅＋1 gate 候選）。
<!-- SECTION:DESCRIPTION:END -->
