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

〔已決策勿重辯〕user 09-11 拍板「拔掉 archify」＋「任務家 diagram-* 條目整段也拔」——證據：fd -I 補掃證實 ignored 區僅 3 個 archify 歷史目錄（archify-integration-flow／illustrate-html-mode-flow／rules-deployment，渲染產物＋visual-check 截圖）；lite-verify 19/19 在庫 html 全手寫殼（12-71KB，零 ≥500KB archify 肥檔）；任務家被擋的 diagram-*.html 主體＝720KB×5 archify 遺物（mermaid srcdoc 形態不產 diagram 檔）；svg 渲染 8 檔共 130KB（無 bloat 顧慮）；殼的未來＝AIR-73 codegen 投影非 archify 渲染。移除面：①illustrate-html-mode 全文重寫（刪偵測/deliver 重生/archify-gen tier/JSON IR 慣例/輪數 guard/drift compare/Authoring 紀律與教訓——.mmd 源保留餵 mermaid；放置學改寫＝按需視覺/決策 viewport→ai-analysis/<域>/）②illustrate SKILL HTML 模式改「殼＋mermaid srcdoc」③diagram-selection 刪 archify 列④agents 治理鏈：roles/archify-gen 刪→sync_agents pin dict 移除→registry 重生成→model-routing lite 表＋agents/AGENTS.md dispatch/registry 行移除⑤.gitignore：arch-report 區塊＋任務家 diagram-* 八條**整段拔除**——殼/.mmd/mermaid 渲染全進版控⑥遺物處置：3 個 archify 目錄（含 tracked JSON IR 檔——隨慣例退役刪）＋720KB 渲染 html×5＋visual-check html×3＋png×12 本地刪；svg×5 tracked 收編⑦blueprint s9/s10 放置表改寫＋theme 修復（td code/.note/chip.warn 硬編碼→light-dark token，對齊 MOS-22.3 reference；test-contract 同步修＋一處 border 色 typo）⑧部署：skills symlink 即時傳播；vision 驗收慣例獨立保留。

〔驗收〕
- `rg -i "archify" skills/ agents/ scripts/ .gitignore` 零命中（歸檔歷史 ai-analysis/{_tasks,archive,flow-feedback} 不動）
- `sync_agents.py --map` 兩 registry 無 archify-gen；model-routing 角色→requirement 表無此列
- fd 兩態一致：`fd -e html` ＝ `fd -I -e html`（20=20）、`fd -e svg` ＝ `fd -I -e svg`（5=5）——無 html/svg 再被 ignore；arch-report/ 不存在
- blueprint/test-contract 殼淺色態無硬編碼深底（td code/.note 用 var token）；殼 zoom/ESC/圖面點擊放大 Playwright 實測過
- 全 repo `git status` 乾淨（svg 收編與 JSON IR 刪除入 commit）、289 tests passed（pre-commit gate）
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
（待開工補）
<!-- SECTION:NOTES:END -->
