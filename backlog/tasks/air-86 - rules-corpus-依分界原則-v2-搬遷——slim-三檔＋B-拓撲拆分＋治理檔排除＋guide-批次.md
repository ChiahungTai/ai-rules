---
id: AIR-86
title: rules corpus 依分界原則 v2 搬遷——slim 三檔＋B 拓撲拆分＋治理檔排除＋guide 批次
status: In Progress
assignee: []
created_date: '2026-09-13 00:38'
updated_date: '2026-09-13 05:09'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
09-13 bundle 定稿裁定（user 拍板：推薦版；與 codex 兩輪討論收斂，材料＝reports/2026-09-13-scope-boundary-memory-rules-skills/materials/codex-out.txt＋codex-bytes-out.txt）：

**形態**：bundle 收斂為「跨任務 user calibration＋首個有後果行動前不可缺的 bootstrap」，其餘內容須能說明為何不能可靠 on-demand。guide 不豁免 A/B 審查（七節骨架留、body 清理——UC-Driven 節削最多：狀態 glyph 全表＋完整 lifecycle 鏈沉 skills，−500~750B）。16 支 rule 每支留 minimal semantic closure，methodology/lookup/案例沉同名 skill；邊界維持不併檔；不設硬 byte gate（semantic form 為硬驗收，byte band 只抓漏瘦）。

**批次重排**（排序指標＝paired-carrier 完整度→semantic risk→可削 bytes；取代原 A 密度優先）：批一 acceptance-evidence＋model-routing＋design-thinking（~3.4–4.4KB 主收益＋定型可重複模板）；批二 edit-discipline＋symbol-query-routing＋quality-constraints＋must-execute；批三 guide＋collaboration＋context-management＋python-standards（python 只 A-slimming——無完整 paired carrier，AIR-85 前禁 pointer-only）；批四 tool-discipline＋outward-action-consent（高後果 calibration，最後）。

**驗收對照**＝目標態表（逐檔 final form 一行描述＋bundle band）：materials/codex-out.txt §C。推薦版 deployed 目標 19–23.5KB（AIR-85 後）/20–24KB（前）；現值 32,835B，headroom 9–14KB。

**雙量測驗收**：每檔記 semantic source size＋deployed bundle size——source sum 禁直接對 gate（deploy framing ~964B；skip-\* 區段現抵 ~1,957B；機制 deploy_agents.py:304-340）。

structure.md 引用邊表已加 bundle role 欄（bootstrap split / conditional projection eligible / reference layering）——本卡實施時對照該欄。

09-13 補充裁定：guide 新增「Session 開場導引」小節（批三 guide 範圍；codex 對齊定稿）：

**定位**：放 guide 最前段（intro 後、演化性思維前）——session 首個 substantive decision 的 routing bootstrap。邊界公式＝**guide 常駐「where am I / where do I enter / how do I continue」；skills 承載「what exactly happens after I enter」**——一句鏈（標準開發主鏈）通過 Bootstrap test 留常駐；各站執行細節/glyph/條件沉 skills（與 UC-Driven slimming 完全相容，UC 節不再偷扛導航責任）。

**三行定稿（逐字入 bundle）**：
- **先定位現在在哪**：有 STATE.md 先讀最近 session 觀察，再以 active card／board 狀態與 card notes／EP 進度節核對目前工作、已完成處與 resume point；觀察層不能取代現況來源。
- **再決定下一個入口**：標準開發主鏈為 /execution-plan → /implement → /post-build → /commit；需求釐清、審查、修復等分支及各步方法論查 skills/CLAUDE.md 索引與對應 skill。
- **需要跨 context 接續時先結算**：context 將耗盡先把進度與待辦寫回 EP／card；同一工作稍後續跑用 /at，交給另一個 session／repo／provider 用 /handoff。

**禁令**：導引不放八站名稱/glyph（防 UC 段 slim 掉的內容從此入口長回）；STATE.md 不寫成高於 board/EP 的 authority；skills/CLAUDE.md 描述為索引非 authority。材料＝materials/codex-navdesign-out.txt。

09-13 批二完成（待 commit）：ED 1,265→1,139/SQR 1,549→1,258/QC 2,341→1,797/ME 1,155→985；C1 承接 validation-strategy「crash-only 邊界」＋sqr skill 載體事實；impl drift 攔截 2 錨點→ledger 補 consumer 同步 3 筆；雙審 13/13 DELETE-OK、四檔 band 全上修（C-core 承重，C7 前例）、B2-F1 落 AIR-70；consistency 3 實質問題全處置（F1 in-batch/F2F3 隨 AIR-87）；deployed 31,427→30,296B 三端 identical；364 tests。帳本＝materials/review-ledger-air86-batch2.md。剩批三（guide＋開場導引＋collaboration/context/python）、批四（tool-discipline/outward）。
<!-- SECTION:NOTES:END -->
