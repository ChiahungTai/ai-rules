---
id: AIR-40
title: memory 寫入歸因可視化——週期 top 寫入 session×條目（telemetry 歸因、零新機制）
status: To Do
assignee: []
created_date: '2026-09-07 07:56'
labels:
  - memory
  - governance
dependencies: []
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：用現成遙測產出 memory 寫入歸因報告——每週（或每波）列 top 寫入 session × 條目 × chars，點名 ad-hoc subagent 繞 hook 大寫入，把 subagent 合規率從黑盒變可量測。〔baseline：ai-rules 339e2c9〕〔已決策勿重辯：①零新機制——不加 hook、不加寫入閘門、不改 PreToolUse（AIR-9／desc-loop 兩次否決重申）；②搭既有週期腿——corrections-weekly 週六班次或夜波/standup 擇一落點，提案時定；③只量測不攔截——輸出是報告（advisory），處置走人工；④寫入者判定鍵＝條目 frontmatter originSessionId sess_subagent_ 前綴為主、db.sqlite part 表 Edit file_path 交叉為輔；⑤主 session／mem-distill 合規寫入不列為問題（只列事實）；⑥規模初判 standard（方法＋腳本＋文檔），開工階段 1 確認是否升 EP〕〔驗收：①腳本對 ai-rules 池跑出本週 top 寫入排行，與 --check inflow 增量對得上（誤差說明）；②至少一例 ad-hoc subagent 繞 hook 寫入被點名（含 session＋條目＋chars）；③落點確定且首跑報告產出；④全程零新增寫入閘門（rg 證 hooks/ 無新增攔截）〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 腳本跑出本週 top 寫入排行，與 inflow 增量對帳一致
- [ ] #2 至少一例 subagent 繞 hook 寫入被點名
- [ ] #3 落點確定＋首跑報告產出
- [ ] #4 零新增寫入閘門
<!-- AC:END -->
