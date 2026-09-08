---
id: AIR-50
title: 開發流程契約修復＋反饋固化——codex 六斷點＋mosaic MOS-74 四條
status: To Do
assignee: []
created_date: '2026-09-08 22:02'
updated_date: '2026-09-08 22:02'
labels:
  - docs
  - skills
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-rules/_tasks/09-09-skill-contract-fixes/ep.md
  - ai-analysis/_tasks/09-09-skill-contract-fixes/ep.md
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules ac6cccf〕〔已決策勿重辯：A線①保留七 skill 入口不合併；修序先交接→再分流→最後減法②PB3 結案時點採收斂後單一發布（post-build hook 2／implement 6 fallback；5a 只到 🟡 Built）——guide/implement/metadata-sync/illustrate-html-mode/kanban-board 五處起同步③findings 帳本 caller 單一指定；無 EP fallback＝.review（judge-review 不再貶抑）④.md 分流以路徑判行為控制面（skills/rules/agents/commands）走 code-review docs-mode⑤EP 定稿 gate＝三背景 agents（transcript 考古／修法 dry-run／ZCode 專攻）遺漏吸收；B線⑥bridge 直跑範式定案（agent 轉發退役——timeout 約束從未存在）；resume 鏈 review→judge→修正→同 session followup 獨立記載⑦Finding 驗證式欄＋external reviewer 工單要素（followup 零摩擦關鍵）⑧長命令背景跑通則入 tool-discipline＋三層反模式案例⑨固化分層：操作事實留 memory、機制進 ai-rules（mosaic 側已改寫，承接不重做）⑩tour_validate 中文目錄 bug 移交 code-reality repo——本弧只重現實證＋移交，不跨 repo 寫入〕〔驗收：①SM-1~9 場景 rg 可驗②「結案兩步」全 repo 同詞單一時點③sync-sources 全綠＋guide 部署同步（deploy_agents）④model-routing 無 agent 轉發殘留、有直跑＋resume 鏈＋驗證式要素⑤tool-discipline 通則＋案例在場⑥tour_validate 重現實證＋移交指針在場（或 code-reality 側修復 PASS）⑦codex checkpoint＋mosaic 反饋佇列已搬 durable（任務 references/）〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A 線六斷點＋B 線四條反饋固化落地：SM-1~9 rg 可驗、五處結案時點同步、sync-sources/部署全綠、暫存證據搬 durable
<!-- AC:END -->
