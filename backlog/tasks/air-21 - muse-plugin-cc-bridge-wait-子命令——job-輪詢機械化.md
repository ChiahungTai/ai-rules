---
id: AIR-21
title: muse-plugin-cc bridge wait 子命令——job 輪詢機械化
status: Done
assignee: []
created_date: '2026-09-03 22:35'
updated_date: '2026-09-05 01:25'
labels:
  - muse-plugin-cc
  - delegation
dependencies: []
references:
  - 'file:///Users/ctai/Github/muse-plugin-cc/scripts/muse-bridge.mjs'
  - ~/Github/muse-plugin-cc/scripts/muse-bridge.mjs
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
root fix（bridge wait 子命令）已於 0.2.4 落地（muse-bridge.mjs:1706）。09-05 L4 行為驗收通過：steps-1 探針 job（job-mtnp784d-upbyzi）實測——短 wait（timeout 1500ms）撞 running job＝exit 124、長 wait 阻塞至終局＝exit 0＋final JSON（status completed）；bridge 既有 tests 全綠（node --test tests/bridge.test.mjs，fail 0）。殘餘＝wait 自身零測試覆蓋（tests/ 無 wait 命中）——已記 memory reference_muse-code-cli-facts，補測試帶 muse-plugin-cc repo session 執行（該 repo 無 backlog）。--interval 構想經 AIR-26 裁定 YAGNI（interval 面無增益；timeout 面由 AIR-26 收法紀律承接）。〔消費弧：AIR-26 done/09-05-external-runtime-push-collection〕
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
wait 已落地＋L4 行為驗收全過（124/阻塞/final JSON 三路徑實測）＋既有 tests 綠；測試債務（wait 零覆蓋）記 memory，補測試歸 muse-plugin-cc repo session
<!-- SECTION:FINAL_SUMMARY:END -->
