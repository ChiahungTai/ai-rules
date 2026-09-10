---
id: AIR-74
title: 退役 archify 產線：報告殼全走手寫＋codegen，index.html 一律進版控
status: In Progress
assignee: []
created_date: '2026-09-11 06:40'
updated_date: '2026-09-10 22:46'
labels:
  - governance
  - shell-pipeline
dependencies: []
references:
  - 'http://127.0.0.1:6421/ai-rules/reports/2026-09-11-test-contract-design.md'
  - ai-analysis/reports/2026-09-11-test-contract-design.md
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕
把沒有人在用的 archify 圖表產線（會產出 720KB 肥大 HTML 的那套）整組拔掉：報告殼以後只有「手寫殼」和未來的 codegen 投影兩種，所有 index.html 都進版控、不再被 gitignore 排除。對你的影響：看產物就是開檔案點開，clone 下來殼都在，不會再有「本地才看得到」的頁面。現況：repo 內 19 個殼全手寫、零 archify 渲染產物在庫——拔的是死代碼不是功能。

〔baseline〕ai-rules main cb75342（2026-09-11）

〔已決策勿重辯〕user 09-11 拍板「拔掉 archify」——證據：fd -I 補掃證實 ignored 區僅 3 個 archify 歷史目錄（archify-integration-flow／illustrate-html-mode-flow／rules-deployment，渲染產物＋visual-check 截圖）；lite-verify 19/19 在庫 html 全手寫殼（12-71KB，零 ≥500KB archify 肥檔）；殼的未來＝AIR-73 codegen 投影非 archify 渲染。移除面八項：①illustrate-html-mode 刪 archify 段（偵測／deliver 重生／archify-gen tier／JSON IR 慣例——.mmd 源保留餵 mermaid）＋放置學改寫（arch-report 退役→authored 殼進 ai-analysis committed home）②illustrate SKILL HTML 模式改「殼＋mermaid srcdoc」、刪 archify 降級分支③diagram-selection 刪 archify 列（mermaid／HTML 塊二擇）④agents 治理鏈：roles/archify-gen.md 刪→sync_agents.py（pin dict line 31 移除）重生成→model-routing skill lite 角色表移除→agents/AGENTS.md dispatch matrix 行 48＋registry 表行 67 移除⑤.gitignore 50-54 arch-report 區塊移除（先清遺留再放寬；任務家 diagram-*.html 條目＝mermaid 渲染慣例、不動）⑥遺留：3 個 archify 歷史目錄本地刪除（歷史已由 done 任務家承載）；arch-report/ 清空後目錄移除（test-family-routing 已於 cb75342 遷 ai-analysis/test-contract/）⑦blueprint 連動：s9 放置表「按需結構視覺→arch-report」列改寫、workflow viewport 節放置表同步⑧部署：skills 走 symlink 即時傳播（mosaic 消費端殼試驗走手寫 v2 非 archify，低風險）；視覺驗收（visual-check/vision）慣例獨立於 archify、保留。

〔驗收〕
- `rg -i "archify" skills/ agents/ scripts/ .gitignore` 零命中（歸檔歷史 ai-analysis/{_tasks,archive,flow-feedback} 不動）
- `sync_agents.py` 重新生成後 registry 無 archify-gen（兩端）；model-routing 角色→requirement 表無此列
- `fd -I -e html .`（尊重 gitignore 態）＝ `fd -e html .`（no-ignore 態）——兩態一致＝無 html 再被 ignore
- 全 repo `git status` 乾淨、arch-report/ 目錄不存在、289 tests passed（pre-commit gate）
- blueprint index s9/s10 與 workflow 放置表無 arch-report 殘留指標
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
（待開工補）
<!-- SECTION:NOTES:END -->
