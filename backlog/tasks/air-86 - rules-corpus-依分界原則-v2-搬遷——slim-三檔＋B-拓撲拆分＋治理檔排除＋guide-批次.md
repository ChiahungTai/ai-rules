---
id: AIR-86
title: rules corpus 依分界原則 v2 搬遷——slim 三檔＋B 拓撲拆分＋治理檔排除＋guide 批次
status: To Do
assignee: []
created_date: '2026-09-13 00:38'
labels: []
dependencies: []
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 目標一句話
依 2026-09-13 scope 分界 v2 判準（rule 資格公式＋residency 三測試；reports/2026-09-13-scope-boundary-memory-rules-skills/report.md）對 rules 19 檔＋ai-development-guide.md 逐條搬遷。

## baseline
ai-rules main @（AIR-85 建卡 commit）。材料源＝report.md §四＋materials/draft-v0-dispositions.md（逐檔裁定 v1 已套 bootstrap test）＋materials/leg3-rules-tagging.md（形態標註）。

## 已決策（勿重辯）
- A 共識＝delete candidate：逐條文判不逐檔判（A 殼 C 核拆分）；刪除者與初判者分離（writer 標 candidate、獨立 reviewer 複核）；純教學 A 直接刪不降 skill
- slim 三檔：design-thinking（刪純共識論述、留 C 兩層強制＋模板 pointer；不套 path-scoping——codex 駁回）、edit-discipline（SOLID 壓一行）、python-standards（禁舊 typing 壓一行、留反主流裁定＋re-export 案例；Write-without-Read 洞一併處置——補配對 skill 或縮 paths 適用面）
- B 拓撲兩檔拆分：model-routing（留兩跳/native-ID/tier 骨架；委派/resume/rate-limit 細節收 skill）、symbol-query-routing（留啟動 gate＋禁 0-hit 斷言；工具細節收 skill）
- rules/AGENTS.md 排除出 bundle（治理文件第五類——harness-scope 標記；CC 端不再被當行為規範載）
- C 大宗 12 檔留；modern-cli-preference 列首次校準 re-audit 清單（rg/fd 模型多已自覺——C 代際衰減活例，事件觸發非日曆）
- guide 同標準、批次二（本次僅納入判準宣示與量測，逐條搬遷可再分）
- 判準依 AIR-70 回填後的 memory-audit 載體表為準（先回填後搬遷，順序勿倒）

## 驗收
- 每檔搬遷附 A 殼刪除清單（diff 舉證）＋bootstrap 指針在場宣告
- deploy 全端綠＋bundle bytes 前後量測（三高 A 檔＋B 拆分檔）
- 刪除候選經獨立複核（reviewer 記錄）——writer 不得自刪自核
- /consistency＋check_single_source 全綠
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 slim 三檔 diff＋A 殼清單舉證
- [ ] #2 B 拓撲兩檔核心/細節拆分落地
- [ ] #3 rules/AGENTS.md 排除出 bundle（CC 端驗證）
- [ ] #4 獨立複核記錄＋consistency/deploy 全綠
<!-- AC:END -->
