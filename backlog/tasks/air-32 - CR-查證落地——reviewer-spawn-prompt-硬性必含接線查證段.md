---
id: AIR-32
title: CR 查證落地——reviewer spawn prompt 硬性必含接線查證段
status: To Do
assignee: []
created_date: '2026-09-06 05:45'
labels:
  - governance
  - skills
dependencies: []
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules ce49f85〕3 天量測（09-04～06，ZCode db.sqlite）：review 鏈 CR 查詢面近乎缺席——review-flavored Explore spawn prompt 含 CR CLI 指引 0/66；code-reviewer 族有 MCP 白名單＋定義指引仍僅 ~4/40 實際呼叫；handoff 續跑弧 4 件跳過階段 1 snapshot。〔已決策勿重辯：①根因＝處方在 skill 註記層、spawn prompt 沒帶（cr-research 對照組實證 prompt 明示才被執行）②解法＝範本層硬性必含——review-engine「spawn prompt 工具紀律」CR 段為單一源（含 MCP/CLI 兩形態命令），agent-review-cycle／workflow-review-pattern／code-review 模板掛必含行 ③不動 agents/roles 定義檔（dry run 後視需要 follow-up）〕〔驗收：四範本檔含硬性必含行＋指向單一源；dry run——照新範本組一隻模擬 spawn prompt、其中 CLI 命令（scip_refs callers）實跑通過；rg 殘留掃描無舊式重複定義〕
<!-- SECTION:DESCRIPTION:END -->
