---
id: AIR-42
title: Memory 知識治理改善——寫入歸因、讀取觀測與載體分流
status: To Do
assignee: []
created_date: '2026-09-07 08:44'
labels:
  - memory
  - governance
dependencies: []
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：以可信 telemetry 改善 memory 的知識分流，讓下次情境能召回已確定事實與約束。〔baseline：ai-rules f03d346〕〔已決策勿重辯：做過哪些事由 backlog/git 承載；沿用 AIR-40/41；不加 hook 或寫入閘門；母卡只協調與驗收，不重複子卡實作；順序 AIR-40→AIR-41→內容分流子卡；AIR-39 已完成作既有基線〕〔驗收：子卡 EP 與證據可追溯、首跑量測有覆蓋限制、分流樣本判讀可全部保留、不以刪除量或違規數驗收〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 子卡與 EP 完整連結，依賴無循環
- [ ] #2 寫入、讀取與分流首輪證據分開陳述；未知不冒充零
- [ ] #3 不增加寫入閘門，結案依子卡行為驗收而非計畫存在
<!-- AC:END -->
