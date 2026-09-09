---
id: AIR-66
title: >-
  muse user bundle 36KiB 自限——guide/三肥段瘦身＋MUSE_USER_BUDGET 部署 gate（×cr-audit
  R8/R5 合流）
status: To Do
assignee: []
created_date: '2026-09-09 21:43'
labels:
  - governance
  - bundle
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User 09-10 拍板方案甲：ai-rules 部署的 muse user 層自限 36,864B（現 40,092B——09-09 AIR-53 精煉 mosaic 專案層到貼線 292B、mos-80 +333B 後串接全額 65,577 超 64KiB 線 41B，尾段規則截斷）。範圍：①瘦身 ≥3.2KB——guide+header 6,386B→~4.5KB＋tool-discipline(3,938B)/quality-constraints(3,613B)/collaboration-constraints(3,323B) 三肥段語義壓縮（深層已有 skill 可承接者下沉）；②scripts/deploy_agents.py 加 MUSE_USER_BUDGET=36,864 硬 gate（獨立於 BUNDLE_MAX_BYTES=90KB 共用 gate——只看 user 層不看專案層是本次炸鍋結構破口；超線拒部署）；③合流 cr-audit R8 承諾網掃除（reports/2026-09-09-cr-role-audit.md R8：19 載體零使用掛名刪或降按需參見——瘦身與掃除同面一次做）＋R5 量測換軌（事件觸發主形態＋KPI 換 negative-claim 覆蓋率，併 corrections-weekly 治理腿）。驗收：部署後 ~/.config/muse/AGENTS.md ≤36,864B＋四部署檔 cmp 一致＋24 tests 綠＋mosaic 串接全額 65,536-framing 復歸線內（user 40K 內＋mosaic 24,660＋825 ≤ 65,536 留 ≥3.2KB 緩衝）。
<!-- SECTION:DESCRIPTION:END -->
