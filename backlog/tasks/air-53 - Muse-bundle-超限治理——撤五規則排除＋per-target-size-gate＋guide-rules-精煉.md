---
id: AIR-53
title: Muse bundle 超限治理——撤五規則排除＋per-target size gate＋guide/rules 精煉
status: Done
assignee: []
created_date: '2026-09-09 02:09'
updated_date: '2026-09-09 03:28'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
【post-build 審查（muse ultra→runtime gate 降 xhigh；job job-mtth0nsn-yscfae）】1 Important＋2 Suggestion。F1（Important）edit-discipline SOLID 列舉被精煉成裸詞——OCP/子型替換/ISP rules/ 零殘留＝刪除非合併（違卡決策③）——已修（列舉補回，審查者建議形態）。F2（Sugg）muse bundle 38,830/40,960＝94.8% gate、餘量 ~2KB——設計如此（global-only 留專案空間），bundle-watch 跟蹤、撞線前先精煉。F3（Sugg）VARIANT_LABEL_SUFFIX 不可達＋tests 零覆蓋——baseline 同樣零覆蓋非回歸，保留作未來鉤子不補測。約束保全 A/B/C 對照（outward 紅線/正確性 gate/crash-only）：20 保留條款、約束刪除 0。驗收 6 條全過（uv 與 ~/.config 被 sandbox 擋→.venv 直跑＋同源碼重建 byte 對帳，muse 如實揭露）。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
撤 MUSE_MECHANICS_EXCLUDE 五規則恢復常駐＋deploy_agents per-target size gate（Muse 65,536B/ZCode 100KiB）＋guide/rules 18 檔精煉（205+/690- 合併非刪）——muse bundle 51,180→38,830B 無截斷、26/26 tests 綠、post-build 審查三 findings 處置完（f84fe59＋2a794a7）
<!-- SECTION:FINAL_SUMMARY:END -->
