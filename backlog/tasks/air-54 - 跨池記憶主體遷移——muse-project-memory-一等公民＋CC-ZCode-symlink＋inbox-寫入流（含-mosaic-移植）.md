---
id: AIR-54
title: 跨池記憶主體遷移——muse project memory 一等公民＋CC/ZCode symlink＋inbox 寫入流（含 mosaic 移植）
status: In Progress
assignee: []
created_date: '2026-09-09 02:47'
updated_date: '2026-09-09 11:02'
labels:
  - memory
  - governance
  - cross-harness
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-rules/ai-analysis/_tasks/09-09-memory-spine-migration/ep.md
  - ai-analysis/_tasks/09-09-memory-spine-migration/ep.md
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：09-09 實驗鏈全驗——muse project scope 注入（14 檔 copy 投影實測：MEMORY.md 全文＋清單列 13 檔）、hooks deny 契約（hookSpecificOutput/permissionDecision，擋 add_memory 實證）、add_memory 裸寫（純 content 零 frontmatter 不動 index）、memory 機制拒 symlink（read_memory 報錯）；材料＝.agent-tmp/muse-hooks-findings.md＋poc_muse_projection.py〕目標：記憶主體遷至 <repo>/.agents/memory/（muse project memory），CC 端 ~/.claude/projects/<encoded>/memory 換目錄 symlink 透明讀寫，ZCode 既有鏈雙跳；muse 從唯讀消費者升一等公民（CP 最高 runtime 零適配），寫入流走 inbox（hook 導流→CC/ZCode consolidation 補 frontmatter＋六問）。〔已決策勿重辯：①主體＝project scope repo 內＋gitignore（非 personal_project——路徑文檔化合約、不怕 muse 重置私有資料；user 09-09）②寫入流＝inbox 先行（「先 inbox 看看」，直寫主體留後議）③一張卡含 mosaic 移植④與 AIR-48 平行推進——muse 品質閘引用其三判準（純機械/單入口/無語義例外）⑤copy 投影過渡形態遷移完成即退役⑥AGENTS.md「Muse memory 唯讀」段隨弧改寫（muse 成受約束寫入者）〕〔驗收：①三端等距驗證——CC/ZCode 開場經 symlink 載入主體如常、muse read_memory project scope 可讀 ②池 git 歷史連續（.git 搬家後夜間收斂波正常跑）③治理路徑全同步（generator/Stop hook/夜間 cron/telemetry——rg 掃描舊路徑零殘留）④muse hooks 品質閘＋inbox 流落地可跑 ⑤mosaic 多 worktree 解法落地（owning 線實體＋其餘 symlink）⑥過渡投影退役＋AGENTS.md/條目/文檔同步〕
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔開工 handoff 09-09 晚——AIR-50 閉環後 center 交接〕排序拍板不變（51✓→53✓→50✓→**54 開工**→52）。baseline：8c4fa14（main HEAD；最後一顆 86e0602 已 push、8c4fa14 待 push）。開工起手式：checkout -b air-54（自 main）→ task edit air-54 -s In Progress → 開工雙 ref → code-reality snapshot --label air-54（勿跳——handoff 續跑弧 4/4 漏這步實證）→ 讀 EP 進 /implement。EP＝本任務家 ep.md（167b87d 定稿——獨立 context review 16 findings 全 apply；S0 段已砍〔user 討論定案〕、S1 手術程序＝mv＋側備份＋併發 guard、S3 hook 絕對路徑、SM 擴至 14 場景）。已決策勿重辯：①Muse 在本 repo 只讀不寫（禁 add_memory/edit_memory——共用池寫入由 ZCode/CC 側）；②memory spine 住 ~/.agents/memory-spine/（plain md＋frontmatter，條目 ai-rules 側寫入、各池 generator 認養 routing 行段）；③過渡形態：.agents/ 投影由冪等腳本 .agent-tmp/poc_muse_projection.py 刷新（結案蒸餾後手動重跑）；④23:40 cron 動檔順序 54 先改路徑 52 後改口徑。在飛事項：AIR-50 審計弧的 muse 跨家族 review 腿背景執行中（bridge job——findings 回來若有採納項由現 session 修正補 commit，不阻塞 54 開工）；hook live 觸發驗證＝下個 CC session 的 hook log（memory-hook-events.jsonl 首筆）。tier：主弧 GLM in-harness。workspace：ai-rules 主 WT（main）。卡歸屬：AIR-54 本 repo board。

〔開工 handoff 09-09 command center〕S1-S5 本 session（S6 mosaic 後延另 handoff）。baseline d430b0f。前置檢查：AIR-50 muse 跨家族補審是否收斂（未收斂→先做只讀盤點、勿進 S1 手術）。起手式：checkout -b air-54 → In Progress → 開工雙 ref → code-reality snapshot --label air-54。S1 手術時序避 23:40±30min；whole-rename＋側備份＋E2E 矩陣全綠才刪 .bak（EP 內程序自足）。muse bridge task ×3 驗證點（S1 read_memory／S3 攔截實測／recall sentinel）。勿重辯：主體 project scope／inbox 流／WAL light／CAS v1／mosaic 直寫廢止。收尾含整體記憶機制審視（含 ZCode）——EP 收尾步驟 6。

〔Muse 續跑 09-09 15:00-15:30——ZCode sess_c6f260d0 停於 Desc gate 後無活動〕recall sentinel 綠（自然腿 _inventory 定位→讀 body＋顯式腿 read_memory 逐字一致，一等公民 gate 關閉）；收尾5 tests/test_muse_memory_inbox.py 新增 3 tests 綠（同族 18 綠）；收尾6 drafts/draft-4 落地（三端鏈路總圖＋ZCode 待辦＋P1-P4）；收尾1/4 零改驗畢；S5 舊敘述 rg 零殘留。待：今晚首波驗證→刪 .bak；post-build 鏈＋commit 待 user 確認。

〔T3 終審返修 09-09 16:00 Muse〕7 findings 裁決 6✅1⚠️全落地：T3-1 hook lexical gate＋測試檔 7 綠（同族 90 綠）；T3-2/3 contract 文字硬化（lstat＋尾slash＋inbox 回歸樣本）；T3-4 Phase0 第二檢查＋P5 執行者缺口（dirty-sensor live 未驗、daily-maintain 無排程——judge 比原文深一層）；T3-5 sentinel 重做（canary 2.3GB/483/tool_usage＋telemetry oracle PASS＋快照缺席 negative control）；T3-6 行為釘測試；T3-7 大小寫註記（池全ASCII）。EP 補第三輪紀錄＋draft-4 補 P5。待：今晚首波、P5 拍板、commit 確認。

〔T3 複審返修 Muse〕T3-1b：alias/secret.md 中間段穿透反例成立（舊邏輯覆現確認）→hook 補 intermediate 逐段 lstat＋2 測試（alias 反例＋nested 正例），測試檔 9 綠、同族全綠；T3-2/3/5/6/7 複審關閉；T3-4 維持開放＝P5 已知殘餘。EP/draft-4 同步。待：今晚首波、P5、commit 確認。

〔T4 接合處審查返修 Muse〕2 findings 全✅：T4-1 異常篩移到流入快照提交前（三 allow＋quarantine 停波；驗證待首波）；T4-2 合約收緊池根 basename＋hook 跳過 slash enrichment（T3-1b walk 移除更簡）＋nested 測試翻轉；ruff PLC0415 修畢（93 綠、ruff/diff-check 綠）。EP 補第四輪。待：今晚首波、P5、commit 確認。

〔註記更正〕前兩則註記有兩處已過時：①daily-maintain 執行者歸屬改為未驗證（skill 記 23:20 vs registry 無此條，AIR-52 解綁處理中）——前稱無排程執行者收回；②T3-1b walk 已被 T4-2 slash 規則取代移除。Phase0 注記與 draft-4 P5 已同步修正口徑。

〔多機支援 Muse〕clone 支援落地（未 commit）：setup-memory-symlinks.sh（命名規則雙實測＋dry-run＋bak）＋verify-memory-topology.sh（只讀＋smoke）＋MULTI-MACHINE.md runbook＋5 測試（98 綠同族）；深層限制＝雙池無同步、主機模型。commit 包再擴大，待你那句。

〔收尾補記 09-09〕draft-4/draft-5 出處：muse session（09-09 下午）順產——draft-4＝EP 收尾步驟 6 的審視產出、draft-5＝pending 讀取覆層設計定案（user 09-09 拍板「只做設計不寫程式」，AIR-57 建卡承接——5a6ce2e 建卡 commit 落 air-54 branch 為 muse 越界〔建卡紀律應在 owning 線〕，隨收尾 merge 進 main、message 已帶正確 id，歷史交 git log）；air-58 為獨立任務卡（非本弧）。post-build 三視角（primed/fresh/codex）22 findings 裁決全 apply——帳本 .review/air-54.md；VP3 recall sentinel 結論＝僅 explicit 過＝召回面受限（EP 風險 7 已補記）。

〔VP3 更正 09-09〕前則「僅 explicit 過＝召回面受限」為單腿結論——與 muse 15:00 工具鏈腿（_inventory.md 直讀→定位→讀 body，綠）合成後正解：一等公民 gate 關閉（observer 工具鏈召回可達）＋直達注入限清單內（深度記錄）。EP 風險 7 已更新。
<!-- SECTION:NOTES:END -->
