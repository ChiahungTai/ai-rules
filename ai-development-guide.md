# AI 協作開發指南

跨專案、harness-neutral 的協作規範，量化交易優先。Claude 全域檔 symlink 至本 guide，rules 另行 auto-load；ZCode/Codex/Muse 由 `scripts/deploy_agents.py` 將 guide + neutral rules 部署為全域 AGENTS.md。專案指令另放各 repo 的 AGENTS.md；Claude 端以 CLAUDE.md wrapper 載入。

修改 instruction 檔前載入 instruction-writing skill；禁止加入行數、字數、版本號、更新日期、Changelog。雙檔與按需引用規範見 [instruction-writing.md](rules/instruction-writing.md)。

## 演化性思維

在測試保護下優先架構品質、正確性與清晰度，持續測試→重構→確認；預設不保留向後相容。需確認的外部整合、數據流程、部署等情境見 [edit-discipline.md](rules/edit-discipline.md)。

## 驗證約束

修改後必須實際執行，再檢查語法/import，依風險完成驗證；純文檔/註解等例外見 [must-execute-before-complete.md](rules/must-execute-before-complete.md)。驗證順序與消費端要求見 [quality-constraints.md](rules/quality-constraints.md)。

### 風險分級標準

| 風險 | 範圍 | 驗證深度 |
|---|---|---|
| 高 | 核心架構、跨 context 共用 domain service、會計總量、風控 sizing、數據庫、安全、API 重大修改 | 完整驗證所有相關功能 |
| 中 | 新功能、演算法/性能優化 | 核心功能測試＋經驗分析 |
| 低 | 樣式、文檔、配置 | 至少確認語法；執行例外依上述 rule |

評估須提供相對複雜度、風險、依賴、里程碑與排序；不預測絕對耗時或精確進度。

## UC-Driven Development

功能開發先定義 Use Case。AGENTS.md Capabilities 是已完成能力索引，backlog 是待辦/進行中承諾池；操作命令、refs、precheck 的單一源為 kanban-board skill。

### 文檔體系

| 載體 | 職責 |
|---|---|
| AGENTS.md（Claude 端 CLAUDE.md wrapper） | 自動載入的導航與已完成能力 what/where |
| architecture.md（若有） | 設計決策與 whole-picture why |
| SYSTEM-MAP.md | 跨域功能當前狀態 |
| dependency-graph.md（per-repo opt-in） | 人工策展依賴/ripple 地圖；機械查詢由 code-reality 承擔 |
| backlog/ | Backlog.md 任務卡；Done 留板，清理批次才 `task complete` 搬 completed/ |

長文件用 Markdown link 按需讀，不用 Claude `@` 全量 transclude。

### UC 狀態與放置

- ✅ 已完成：主要實作模組的 AGENTS.md Capabilities；同一 UC 只記一處。表格 `| 能力 | 入口 | 狀態 |`，入口含 CLI＋函式路徑。
- 🟢 部分覆蓋：Capabilities 附限制；❌ 棄用：移出 Capabilities。
- 📋 待辦、🔧 部分完成：backlog To Do；🟡 進行中：In Progress；未承諾想法用 drafts。
- scripts/ 是人類 demo 入口（基於 library，可用 typer），不放 Capabilities。Claude 端 wrapper 隨 source 同步。

### 變更規模分級

大型跨模組/新功能：execution-plan 建卡；中型優化：更新既有能力或卡；小型 bug fix/文檔免 UC，結構性修復依 execution-plan simple 邊界判定。

### 銜接機制

1. execution-plan 盤點 UC，`backlog task create` 含 labels、EP 連結，建卡即 commit 以免跨 WT id 碰撞。
2. build 階段 1：`task edit <id> -s "In Progress"`＋開工雙 ref；無 backlog/ 可跳過。階段 5a：完成 UC 的 Capabilities、`-s Done --final-summary` → `--ref` 換 done/ URL，卡留 Done 欄；EP 歸檔任務家 done/（位置見 illustrate-html-mode）。
3. post-build 在 commit 前執行 code-review → judge-review → 修正迴圈 → consistency → metadata-sync（詳 post-build skill），止步 commit 前。
4. commit 一次納入 code＋finalization，保證同 commit；commit 本身只處理 git 提交。
5. **任何 session 對卡做事（含 automation、結案、歸檔），第一動必須設 In Progress**，供平行 session 看見；任何 `task complete`／`archive`／清板前必跑 kanban-board 的 `scripts/backlog_precheck.sh`，exit 1 停手。

## Solo + AI 開發工作流

一人＋AI、無團隊/CI；一 EP＝一 session。EP 段落須自包含、可結算接續；compact 分布於規劃後與 build 段落間。model 退化不硬撐：先結算 EP，再開新 session（handoff 接續、at 處理 usage）。Writer/Reviewer 分離，review 支援跨 session findings 貼回判讀。專案另定 worktree/trunk 變體。

## 架構設計紀律

spec/EP/implement/review 的設計決策用 Clean Architecture＋DDD 視角，不強制模板或過度分層。兩層思考、依賴方向、bounded context、use case 驅動見 [design-thinking.md](rules/design-thinking.md)；SOLID 與編輯約束見 [edit-discipline.md](rules/edit-discipline.md)。整體結構深入用 arch-thinking skill，介面合約用 api-and-interface-design skill。

## 量化交易專屬鐵律

- 數據完整性優先：損壞比缺失更危險，無效資料/溢出立即失敗，禁靜默傳播；Crash-Only 適用範圍見 [quality-constraints.md](rules/quality-constraints.md)。
- 回測必須完全可重現（hash＋config＋seed），波動 >0.01 必須重做。
- 狀態外部化，崩潰後恢復即初始化；Live/Backtest 共用邏輯，避免模式分支。
- 隨機 seed 必須可注入，避免 np.random。

## Summary Instructions（壓縮策略）

壓縮對話必保留：已讀/改路徑、測試結果與錯誤、決策及理由、目標與待辦、已提交未執行的命令/skill、待確認提案、背景/中斷工作（中斷執行會隨原歷史消失）。數字/比例從實際枚舉推導或逐字複製，禁止憑記憶改寫。
