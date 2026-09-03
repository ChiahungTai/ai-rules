---
status: draft
labels: [governance, bundle-diet, memory-audit]
---

# rules audit × bundle 減量聯合弧

## 目標

`rules/`（always-on bundle 成員）的使用度／價值盤點——類比 08-31 skills Tier A 盤點（使用度普查＋零引用刪除候選）對 rules 版。與 memory-audit 同框架設計、**觸發時同一治理班次一起跑**（一次清兩池：rules bundle＋memory 池）。

## 觸發條件（user 2026-09-03 定調「到時候一起做」）

bundle 逼近硬 gate——建議線：`deploy_agents.py` 輸出 ≥93% gate（90KiB 線）。現況 83,113B＝90%（WARN 區、緩漲中）。

## 範圍草案

- **使用度腿**：每條 rule 的 inbound 引用（skills/commands 對它的 pointer 數）＋git 活躍度＋session 實際依賴證據（哪些 rule 的內容真的在消費端被讀）
- **價值腿**：always-on 預算的正當性——每條 rule 是否仍「每次 session 都需要」（rule 定義）；可降級為 skill on-demand 的候選（reference 分層既有先例：acceptance-evidence/lsp-navigation）
- **合併腿**：內容重疊的 rule 對（如 edit-discipline × design-thinking 的 SOLID 段邊界）
- **聯合執行**：與該週 memory full/lite audit 同班次——報告合併、收斂動作（rule 減量＋memory 蒸餾）一次落地

## 預估量級

小弧（1 session）：盤點機械腿＋advisory 清單＋user 裁決＋執行。先例：bundle-diet-wave2（88KB→81KB）、Tier A skills 盤點（8 刪）。
