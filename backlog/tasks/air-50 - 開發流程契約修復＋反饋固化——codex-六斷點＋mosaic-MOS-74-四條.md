---
id: AIR-50
title: 開發流程契約修復＋反饋固化——codex 六斷點＋mosaic MOS-74 四條
status: To Do
assignee: []
created_date: '2026-09-08 22:02'
updated_date: '2026-09-08 23:08'
labels:
  - docs
  - skills
dependencies: []
references:
  - 'http://127.0.0.1:6421/ai-rules/_tasks/09-09-skill-contract-fixes/index.html'
  - ai-analysis/_tasks/09-09-skill-contract-fixes/index.html
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules ba386cb〕〔已決策勿重辯：A線①保留七 skill 入口不合併；修序先交接→再分流→最後減法②PB3 結案時點採收斂後單一發布（post-build hook 2／implement 6 fallback；5a 只到 🟡 Built）——guide 等全引用面同步（EP Review F1 補五消費端：flow-review/skills CLAUDE.md/blueprint-bootstrap/maintain/context-management）③findings 帳本＝.review 正典化為工作帳本（EP review 區段＝規劃期）；caller 指定可覆寫④.md 分流以**語義判準**判行為控制面（塑造 LLM 行為之檔——AGENTS.md 家族/rules/skills/agents/commands/hooks/settings/guide；路徑降 hint＋純修飾輕量快道）走 code-review docs-mode⑤EP 定稿 gate＝三背景 agents 遺漏吸收＋EP Review（已完成——零 Critical、F1-F6 全處置）；B線⑥bridge 直跑範式定案（agent 轉發退役——timeout 約束從未存在；外部 runtime 承載者＝背景 Bash，禁 subagent wrapper）；resume 鏈 review→judge→修正→同 session followup 獨立記載⑦Finding 驗證式欄＋external reviewer 工單要素（followup 零摩擦關鍵）⑧長命令背景跑通則入 tool-discipline＋三層反模式案例⑨固化分層：操作事實留 memory、機制進 ai-rules（mosaic 側已改寫，承接不重做）⑩tour_validate 重現實測**不重現**（現行版中文目錄掃描正常、205 tours）——降級結案，repro 紀錄留任務 references/；C線⑪AIR-48 剩餘併入同弧（S9）——本卡結案時同步結 AIR-48〕〔驗收：①SM-1~10 場景 rg 可驗②「結案兩步」全 repo 同詞單一時點（含 F1 五消費端）③sync-sources 全綠＋guide 部署同步（deploy_agents）④model-routing 無 agent 轉發殘留、有直跑＋resume 鏈＋驗證式要素⑤tool-discipline 通則＋案例在場⑥AIR-48 P4 dogfood 收尾＋定義表 wrapper 條目＋P5 裁決點彙整⑦暫存證據已搬 durable（任務 references/）〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A 線六斷點＋B 線反饋固化＋C 線 AIR-48 剩餘落地：SM-1~10 rg 可驗、結案時點全消費端同步、sync-sources/部署全綠、AIR-48 同弧結案
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
【09-09】user 裁定 AIR-48 剩餘併入本弧（S9：P4 dogfood 窗口至 09-10＋P5 裁決點＋memory-audit 統一定義表補 wrapper 誤置條目）——本卡結案時同步結 AIR-48；air-50 branch 已重建快進至 main（開工 checkout 依新 git 慣例）
<!-- SECTION:NOTES:END -->
