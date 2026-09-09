---
id: AIR-70
title: 一致性掃描修復弧——13 中級全修＋低級順手批次（09-10 scan-report 承接）
status: To Do
assignee: []
created_date: '2026-09-09 22:40'
labels:
  - governance
  - consistency
dependencies: []
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
09-10 02:00 三軸掃描報告（ai-analysis/reports/2026-09-10-repo-consistency-scan.md）user 拍板全修。範圍：中級 13 條（五群：G1 部署家族清單三版本/G2 claude-specific boilerplate/G4 bundle-skip 未記載/S1 impl-test-gen role 幽靈〔最重〕/S2 STATE.md 三方/S3 commit flow 重畫/S4 usage-ping 語音殘留/S5 階段3 stale ref/S6 斷連結/F1 cleanup plist 無版控副本/F4 mosaic twin 缺 loud-fail〔次重，跨 repo〕/F3 README 必查路徑撲空＋低級順手批次：共識 trivial G10/S7/S9/F2/F5/G7，歧異帶 G5/G8/G9/S8/S10 併入判讀，G6 不修〔誤報〕）。⚠️ 掃描時點 b75e8a7——AIR-52 修正迴圈＋AIR-66 瘦身已動部分檔案（usage-ping/rules 面），執行前逐條 rg 重驗現況，已被修掉的標 washed-out。修法方向照報告 Phase 4 表（序 1-9），F4 跨 repo（mosaic twin 同步）依跨 repo 慣例；第四軸結構性建議（部署渲染/runtime 消費對等）不入本弧，另行評估。驗收：13+順手逐條附 rg/sha 證據＋post-build（docs-mode 為主）＋G11 先查證（Claude loader paths: 消費——probe 後裁）。素材：報告全文＋兩顧問裁決段＋journals .agent-tmp/consistency-*-journal.md。
<!-- SECTION:DESCRIPTION:END -->
