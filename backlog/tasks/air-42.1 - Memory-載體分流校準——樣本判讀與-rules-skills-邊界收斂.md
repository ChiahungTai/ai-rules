---
id: AIR-42.1
title: Memory 載體分流校準——樣本判讀與 rules skills 邊界收斂
status: In Progress
assignee: []
created_date: '2026-09-07 08:44'
updated_date: '2026-09-07 08:44'
labels:
  - memory
  - governance
dependencies:
  - AIR-40
  - AIR-41
parent_task_id: AIR-42
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：消費寫入歸因與 body Read 觀測樣本，校準 memory/rule/skill/AGENTS/backlog 分流。〔baseline：ai-rules f03d346〕〔已決策勿重辯：memory 留已確定且改變未來行動的專案/使用者事實；通用不等於 rule，專案方法也可放 skill；固化後指針僅在有額外召回價值時保留；低 Read 不直接降 rank；先 advisory 不直接清池〕〔範圍：memory-audit 寫入/收斂段、context-management pointer 與查得的直接消費端；報告含具體候選與目的地；本卡不刪改共享 memory、不部署全域 bundle，需另外具體授權〕〔驗收：用 AIR-40/41 證據抽樣給出情境/事實/行動/載體/權威來源判讀；跨檔分流一致；允許全保留；沒有新閘門〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 樣本判讀具召回情境、事實、行動與去向，未知或全保留合法
- [ ] #2 通用原則與 rule 分離、指針有條件保留、always-on 摘要精簡並同步引用
- [ ] #3 記錄 raw telemetry 誤差與索引召回盲區，不依低 Read 自動改 rank
- [ ] #4 共享 memory/部署不在本卡變更範圍；跨檔一致性與獨立 EP review 完成
<!-- AC:END -->
