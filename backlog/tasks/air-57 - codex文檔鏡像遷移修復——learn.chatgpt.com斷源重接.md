---
id: AIR-57
title: codex文檔鏡像遷移修復——learn.chatgpt.com斷源重接
status: Done
assignee: []
created_date: '2026-09-09 21:45'
updated_date: '2026-09-09 23:05'
labels:
  - ref-docs
  - codex
  - crawl
dependencies: []
references:
  - .review/air-57.md
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
上游整站搬遷：developers.openai.com/codex/* → learn.chatgpt.com/docs/*（308 redirect），URL 重組為區段巢狀（agent-configuration/、customization/、config-file/…）。crawl.py discover_codex 的 regex 只匹配舊域名 → 09-09 重跑 discovery 0 頁、95 個磁碟檔全孤兒、manifest 被寫壞成 codex:0 pages（該次已 git checkout 還原；磁碟檔未動）。最後成功爬抓＝09-04。

修復內容：
1. crawl.py 遷移：CODEX_LLM 改 learn.chatgpt.com/docs/llms.txt；regex 改 `learn\.chatgpt\.com/docs/[^)]+\.md`；路徑剝離適配（`/docs/agent-configuration/rules.md` → `agent-configuration/rules.md`）。
2. 舊 95 檔平面路徑 → 新巢狀路徑遷移對映（抽查已知：rules.md→agent-configuration/rules.md、memories.md→customization/memories.md、guides/agents-md.md→agent-configuration/agents-md.md）；舊檔刪除前逐檔確認新位置在索引內。
3. 全量 re-mirror＋manifest 重建；驗證：孤兒歸零、抽查 3 頁 sha256 與線上一致。

範圍界定：
- 新 docs/llms.txt 是 ChatGPT+Codex 合併文檔集（~158 md links，含 app/windows 等 ChatGPT 面）——沿用舊行為整集入鏡像（舊 95 頁本就含 ChatGPT app 頁）。
- 輔助官方源（不取代逐頁鏡像）：learn.chatgpt.com/docs/llms-full.txt（1.8MB 單檔全量匯出）、learn.chatgpt.com/docs/codex-manual.md（2.3MB 濃縮手冊）、developers.openai.com/learn/codex（HTML learning hub）。use-cases/llms.txt 官方索引自帶 404 死鏈（已實測），卡內註記勿踩。
- 內容 drift 已抽查（09-09）：agents-md.md/rules.md 零機制變動；memories.md 有實質更新（Chronicle 退役 404 → Computer History＝customization/computer-history.md；文檔新增 ChatGPT-web-memory vs 本地 codex local-memory-store 分流敘述）——re-mirror 後 rg "chronicle" 掃 repo 引用面（contracts.md、04 報告等）同步。
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 crawl.py --source codex discovery 命中 learn.chatgpt.com 全集，孤兒歸零
- [x] #2 manifest codex 頁數>0 且與磁碟檔一致；舊平面路徑檔已遷移/清理
- [x] #3 抽查 3 頁（memories/agents-md/rules）sha256 與線上一致
- [x] #4 repo 內 chronicle 引用面掃描並同步
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔開工 handoff 09-10 CC〕①branch：git checkout -b air-57（自 main，WT 現乾淨）。②入口：uv run python ref-docs/harness/crawl.py --source codex（discover+sha256 增量+manifest 單一工具，AGENTS.md 記載）。③現場：09-09 寫壞的 manifest 已 git checkout 還原（HEAD 乾淨）；95 個舊平面檔在磁碟未動——遷移步驟 2 的素材。④陷阱重申（卡內已記）：use-cases/llms.txt 官方自帶 404 勿踩；llms-full.txt/codex-manual.md 輔助源不取代逐頁鏡像。⑤chronicle 掃描面：ref-docs/harness/contracts.md＋ai-analysis/reports/superpowers/04 報告＋rg 全 repo。⑥驗收四條 AC 逐項附機械證據（sha256 抽查用 shasum -a 256 對線上 curl）。⑦收斂：post-build（docs-mode——crawl.py 是 .py，code 鏈跑 ruff+pytest 面）＋結案兩步＋蒸餾。

build baseline: 4f8e1e6（air-57 branch 起點；09-10 impl session 補記）

〔AC 證據 09-10〕#1 `[OK] codex: 148 pages (ok=148)`（remirror2.out），FAIL/WARN/孤兒 0 命中；148=llms.txt 全集（loose 148==canonicalize 後 148——?surface= query 形態 2 頁〔developer-commands/developer-settings〕由 regex `(?:\?[^)]*)?`＋`url.split("?",1)[0]` canonicalize 收入）。#2 三向對帳 page_count=148==pages==disk 且路徑集合相等；55 舊檔刪除（49 路徑變更＋6 outside-scope：community/plugins/guides×2/videos/docs root——308 redirect Location 逐檔實測為據，.agent-tmp/migration-verdict.json）＋11 空目錄清除；basename 猜測不可靠（5+ 處與 redirect 實測不符），對映判定以 redirect 為權威。#3 三頁 local==online(norm)==manifest 全 MATCH（2036fdd5…/4a81af9e…/ff6c8477…）。#4 rg chronicle 全 repo（排除鏡像目錄）僅本卡自述命中；contracts.md/04 報告零字面引用（卡預掃面經查無）；活文檔同步=README.md codex 列＋model-routing SKILL.md L81 config-file/ 路徑，殘留掃描歸零；ai-analysis 歷史報告引用舊路徑屬歸檔歷史不動。

〔實作分工〕crawl.py 遷移＋regex 修補＝impl-lite(flash) TDD×2 段（RED→GREEN，6 passed）；對映判定/網路驗證/judge＝主 session。review=post-build codex+muse 跨家族雙審（bridge task 工單）。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
codex 鏡像斷源重接完成：crawl.py 遷移 learn.chatgpt.com/docs（含 ?surface= canonicalize）＋95→148 頁 re-mirror（55 舊檔按 308 redirect 實測對映清理）＋manifest 重建；AC×4 機械證據＋lite-verify 10/10＋muse/codex 跨家族雙審（無 Critical；2 findings 順手修）；289 tests passed
<!-- SECTION:FINAL_SUMMARY:END -->

<!-- SECTION:FINAL_SUMMARY:END -->
