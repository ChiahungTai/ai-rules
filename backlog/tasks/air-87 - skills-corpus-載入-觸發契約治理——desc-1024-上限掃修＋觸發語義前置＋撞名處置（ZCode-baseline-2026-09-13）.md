---
id: AIR-87
title: skills-corpus 載入/觸發契約治理——desc 1024 上限掃修＋觸發語義前置＋撞名處置（ZCode baseline 2026-09-13）
status: To Do
assignee: []
created_date: '2026-09-13 04:50'
labels: []
dependencies: []
ordinal: 73000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 目標一句話
把 ZCode skills 盤查（ai-analysis/reports/2026-09-13-zcode-skills-baseline/report.md）發現的系統性載入/觸發契約問題收斂：desc 長度上限系統掃修、觸發語義前置、同名撞名、frontmatter 變異。

## baseline
ai-rules main @ 開卡 commit。材料源＝baseline 報告（97 active：repo 79＋plugin 18；ZCode 官方載入規則實證）＋model-routing desc hotfix（root cause 案例：raw desc 1,198>1024 被 drop——已先行修復 776 chars 觸發前置，2026-09-13，隨本卡 commit 入庫）。

## 已決策（勿重辯）
- ZCode 載入契約（官方文檔 zcode-guide/diagnosing-skills 實證）：扁平 key:value 解析；desc 缺失或 raw 行 >1024 chars → 整支 drop；觸發呈現只取 desc 前 ~250 chars——「觸發詞尾掛」模式對 ZCode 無效，語義必須前置
- 兩種解析器量測差異：完整 YAML 會剝 # 註解、ZCode flat parser 不剝——長度以 raw 行為準；desc 一律引號化
- model-routing hotfix 已先行（獨立於本卡，root cause 定案材料）

## 範圍項
1. 全 79 支 repo skill desc 機械掃（raw 長度/引號/# 陷阱/block scalar）＋修復
2. 觸發語義前置改寫（前 250 chars 承載 when-to-use）——高流量 skills 優先（memory-audit/implement/execution-plan/kanban-board 等）
3. code-reality 同名撞名處置（repo 15,361B vs plugin 19,532B，內容不同，載入序 user>plugin 實際生效 repo 版）
4. mermaid 0700 權限、plugin cache 孤兒（110 vs active 18）清理裁定
5. 跨 harness desc 消費差異文檔化（CC 全文 vs ZCode 250 截斷）——instruction-writing skill 增補
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 desc 契約機械掃 script 入庫可重跑；79 支全綠（raw≤1024、引號一致、無 # 陷阱）
- [ ] #2 觸發語義前置：高流量 skills 前 250 chars 承載 when-to-use
- [ ] #3 撞名/權限/孤兒處置各有裁定記錄落卡
- [ ] #4 跨 session 載入驗證：新 ZCode session skill 清單含 model-routing（hotfix 舉證）＋抽樣舉證
<!-- AC:END -->
