# AI 協作開發指南

跨專案、harness-neutral 協作規範，量化交易優先；Claude 用 symlink＋auto-load，其餘由 `deploy_agents.py` 打包到全域位置。專案指令放各 repo AGENTS.md。

改 instruction 前載 instruction-writing skill；禁行數/字數/版本號/日期/Changelog。雙檔與引用規範見 [instruction-writing.md](rules/instruction-writing.md)。

## 演化性思維

測試保護下優先架構品質/正確性/清晰度，持續測試→重構→確認；預設不保留向後相容。需確認情境見 [edit-discipline.md](rules/edit-discipline.md)。

## 驗證約束

修改後須實跑，再查語法/import 並依風險驗證；純文檔/註解例外見 [must-execute-before-complete.md](rules/must-execute-before-complete.md)，順序/消費端要求見 [quality-constraints.md](rules/quality-constraints.md)。

| 風險 | 範圍 | 驗證深度 |
|---|---|---|
| 高 | 核心架構、跨 context domain service、會計/風控總量與 sizing、數據庫、安全、重大 API | 完整驗證相關功能 |
| 中 | 新功能、演算法/性能優化 | 核心功能測試＋經驗分析 |
| 低 | 樣式、文檔、配置 | 至少確認語法；執行例外依上述 rule |

評估提供相對複雜度、風險、依賴、里程碑與排序；不預測絕對耗時或精確進度。

## UC-Driven Development

功能先定義 Use Case。AGENTS.md Capabilities＝已完成能力索引，backlog＝承諾池；操作/refs/precheck 單一源為 kanban-board skill。

文檔：AGENTS.md（Claude 以 CLAUDE.md wrapper）＝導航/完成能力 what/where；architecture.md＝why；SYSTEM-MAP.md＝跨域現狀；dependency-graph.md＝人工依賴/ripple 地圖（機械查詢交 code-reality）；backlog/＝任務卡。長文按需 link，禁全量 transclude。

UC 狀態：✅→主要實作模組 Capabilities（同一 UC 一處，`能力|入口|狀態`，入口含 CLI＋函式）；🟢→附限制；❌→移出；📋/🔧→backlog To Do；🟡→In Progress；未承諾→drafts。scripts/ 是人類 demo，不放 Capabilities。

規模：大型跨模組/新功能→execution-plan 建卡；中型→更新既有能力/卡；純 refactor 跨檔/模組/架構描述亦按大型/中型，僅單檔小 tweak 算小型。小 bug/doc 免 UC；碰單位邊界/除權息/時區/會計/風控即非 simple，至少列受影響 invariant＋驗證式（silent-corruption 例外）。

銜接：execution-plan 建卡即 commit 防 id 撞→implement 開工設 In Progress、完成寫 Capabilities（✅ 只在收斂後結案兩步）→post-build：code-review→judge-review→修正→consistency→metadata-sync（停 commit 前）→一次 commit code＋finalization。任何 session 動卡第一動設 In Progress；結案/清板前跑 kanban-board precheck，exit 1 停手。

## Solo + AI 開發工作流

一人＋AI、無團隊/CI；一 EP＝一 session。段落須自含、可結算接續；compact 分布於規劃後/build 段間。model 退化就先結算再 handoff 新 session；Writer/Reviewer 分離，review 支援跨 session findings 回貼。

## 架構設計紀律

spec/EP/implement/review 用 Clean Architecture＋DDD 視角，不強制模板/過度分層；兩層思考、依賴方向、bounded context、use case 見 [design-thinking.md](rules/design-thinking.md)，SOLID/編輯見 [edit-discipline.md](rules/edit-discipline.md)；深入用 arch-thinking，介面用 api-and-interface-design skill。

## 量化交易專屬鐵律

- 數據完整性優先：損壞比缺失更危險，無效資料/溢出立即失敗，禁靜默傳播；Crash-Only 適用範圍見 [quality-constraints.md](rules/quality-constraints.md)。
- 回測完全可重現（hash＋config＋seed），波動 >0.01 必須重做。
- 狀態外部化；Live/Backtest 共用邏輯，避免模式分支。
- 隨機 seed 必須可注入，避免 np.random。

## Summary Instructions

壓縮對話必保留：已讀/改路徑、測試結果/錯誤、決策/理由、目標/待辦、已提交未執行命令/skill、待確認提案、背景/中斷工作。數字/比例須實際枚舉或逐字複製，禁憑記憶改寫。
