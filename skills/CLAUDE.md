# Claude Code Skills 技術規範

## 寫作原則

> **載入時機**：Skill 只在語意匹配觸發時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Skill 不支援 `@` transclusion。引用輔助檔案一律使用 `[描述](path)` markdown link
- **描述檔案內容**：讓 AI 判斷何時該跟隨 link 讀取，而非無條件載入
- **實作程式碼**：避免在 skill 中嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

## 架構

個人層級 `~/.claude/skills` 符號連結指向 `/Users/ctai/Github/ai-rules/skills`，實現 Git 版本控制、跨專案共享和即時更新。驗證：`readlink ~/.claude/skills`。

## Skill 索引

> 現有 skills 依用途分組。Skill 靠 frontmatter `description` 語意匹配自動 discovery，本索引供「一眼看全」之用，非載入機制；詳見各 `skills/<name>/SKILL.md`。
>
> **⚠ drift-prone**：手動維護的現狀清單——新增/移除/改名 skill 需同步此索引，否則與 `skills/` 目錄漂移。可定期用 `skill-cleaner` 稽核。

### 開發流程（spec → 交付）
- `spec-driven-development` — 開新專案/功能前先寫 spec（需求不明或無規格時）
- `planning-and-task-breakdown` — 把 spec/需求拆成有序可執行任務
- `incremental-implementation` — 跨多檔變更增量交付（避免一次寫一大坨）
- `test-driven-development` — TDD 驅動實作（RED → GREEN → 重構）
- `source-driven-development` — 每個實作決策 grounding 於官方文檔
- `arch-thinking` — Clean Architecture + DDD 設計視角 + 結構機械（分層依賴/bounded context/use case 驅動[含共用層外溢]；city map/dep weight/Pattern Radar/domain grounding/LSP 查證/補償邏輯盤點；視角非模板；受眾中性；與 api-and-interface-design 分工）
- `debugging-and-error-recovery` — 系統性根因除錯（非猜測）
- `external-api-investigation` — 外部 API / 整合器真實行為調查（monkey-patch dry-run、查 stub、問 domain；實證優先於讀 code 推理）
- `autonomous-execution` — 無人介入自主執行的決策 / 錯誤恢復 / 完成回報 / workspace safety / path invariants / session recovery（false-done 偵測）

### 品質與審查
- `review-engine` — review 命令家族通用審查邏輯 domain 真相源（嚴重度/信心水準/審查者自證/LSP 查證/審查模式判定/Writer-Reviewer 分離/多層驗證/**review 執行預設單一源**：force 獨立 / max-agents / model / 視角 / spawn-vs-session）；ep-review/code-review/audit-test/execution-plan EP Review/build Agent Review 共用
- `code-review-and-quality` — code 六軸審查 profile（what to check）；通用邏輯見 review-engine
- `code-simplification` — 不改行為的重構簡化
- `security-and-hardening` — 未信任輸入 / 外部整合的安全強化
- `performance-optimization` — 效能瓶頸 profiling 與優化
- `python-type-gap` — 第三方套件型別缺口的四層策略
- `validation-strategy` — 驗證策略紀律（e2e 優先/交易 replay>live/放 scripts//不重驗 package；與 TDD 流程分工）

### 架構與演進
- `api-and-interface-design` — 穩定 API / 模組邊界 / 公開介面設計
- `deprecation-and-migration` — 舊系統 / API 棄用與遷移
- `documentation-and-adrs` — 架構決策與文檔記錄（ADR）
- `ci-cd-and-automation` — CI/CD pipeline 與品質閘門
- `shipping-and-launch` — 上線前檢查 / 監控 / 漸進部署 / 回滾

### 專案維運
- `git-workflow-and-versioning` — git commit / branch / 衝突 / 平行流
- `kanban-board` — Tasks.md 看板卡片管理（讀 / 建 / 移動 / 回顧）
- `maintain` — `/daily-maintain`（自動）與 `/project-review`（互動）共用的 4-phase 維護核心（勿直接呼叫）
- `metadata-sync` — metadata finalization 單一真相源（Capabilities/Kanban/SYSTEM-MAP/arch/EP/flow-feedback 狀態結算；兩 mode）；被 `/build`、`/metadata-sync` 共用 invoke
- `scan-project` — 統一專案知識掃描（imports + Capabilities + kanban → dep_graph / findings）
- `standup` — 每日晨間簡報昨日活動 digest（跨 worktree session 聚合 + commit/kanban/SYSTEM-MAP transition；nightly-sequence op4 整合）
- `context-engineering` — session 起始 / 品質退化 / 任務切換時的 context 與 rules 設置
- `agent-workflow` — Agent 派發 / worktree 隔離 / 並發控制 / 委派框架（delegation）/ side-discovery / Writer-Reviewer
- `self-contained-prompt` — 交接 prompt 設計原則（接手方三層 / schema / 決策脈絡 / drift / 機密）；/handoff 與 agent-review-cycle 共用
- `skill-cleaner` — 稽核 skill：重複 / 未用 / prompt-budget / compact
- `dependency-upgrade-watch` — 偵測 nautilus_trader / shioaji 版本漂移，主動建議 /upgrade-nt|/upgrade-sj（碰 pyproject.toml 時 auto-load）

### 工具與查詢
- `context7-mcp` — library / framework / API 文檔查詢（context7 MCP）
- `nt-query` — NautilusTrader 能力 / 實作 / 用法合約查詢（docs-first + LSP-on-Cython-stubs + designer intent）
- `mermaid` — pragmatism-first Mermaid 圖表生成
- `rules-reminder` — 常被違反的 Bash 規則（rg/fd、無 `#`、`uv run`、無 `$` 展開）
- `voice-notification` — 三通道語音通知（系統召回 / 進度提醒 / 完成通知）
- `idea-refine` — 結構化發散 / 收斂的想法精煉
- `using-agent-skills` — skill 發現與呼叫的 meta-skill

### UI / 協作
- `frontend-ui-engineering` — Panel/Bokeh 互動 dashboard / 視覺化
- `browser-testing-with-devtools` — 真實瀏覽器 DevTools 測試
- `ui-collab` — 互動式 UI 的 LLM 協作模式（`[ACTION]` 操作日誌）

### 領域特定
- `trading-analysis` — 股票 / 市場走勢三層分析（經典 TA → 量化 → 第二層思考）

## Frontmatter 配置

> **上限真相源**：`description + when_to_use` 合計截斷 **1536 字元**（對齊 `skill-cleaner.ts` 的 `MAX_DESCRIPTION_CHARS`；可用 `maxSkillDescriptionChars` 覆寫）。skill 清單預算由 settings 的 `skillListingBudgetFraction` 控制（預設 context 的 1%，溢出時最少 invoke 的 skill 描述先丟）。

```yaml
---
name: skill-name                    # 顯示名稱；預設取目錄名
description: 功能 + 何時使用 + 觸發詞    # auto-discovery 唯一依據，見下方寫法
when_to_use: 觸發短語 / 範例請求       # 附加到 description，計入 1536 上限
paths: ["**/*.py"]                   # glob 限制 auto-load（只在此檔被碰時載入 body）
allowed-tools: [Bash(uv pip *)]      # skill 作用時預批准工具（免每次權限提示）
disallowed-tools: [AskUserQuestion]  # 作用時移除工具（自主 loop 用）
disable-model-invocation: true      # 純人類觸發 → 不進 listing（見決策原則，預設不設）
user-invocable: false               # 背景知識 → 從 / 選單隱藏（仍可被 model invoke）
context: fork                       # 在 subagent 隔離執行（配 agent:；無對話歷史）
agent: Explore                      # context: fork 時的 subagent 型別
model: opus|sonnet|haiku|inherit    # 作用時覆寫模型（下個 prompt 恢復）
effort: medium                      # 作用時覆寫 effort
---
```

### 欄位決策原則

- **`disable-model-invocation` 預設不設** —— AI 在自主流程（deep-work、EP→build→commit 鏈）會高頻自動 invoke dev-loop 命令；設了會打斷既有工作流（transcript 實證：execution-plan/spec/build/commit 等在自主流程被 AI 高頻自動 invoke）。consent（如 commit-consent）已在 skill 層確保，**不需**在 invocation 層再加。只有「transcript 實證 AI 不會想 invoke」的純人類工具命令才考慮設 —— 依據 transcript 非受眾表
- **`paths`** 限縮 auto-load 範圍 —— 領域特化 skill（查特定套件、特定副檔名）用 glob 避免跨專案誤觸發；注意 paths 只擋 body auto-load，**description 仍在 listing**
- **`context: fork`** 隔離長任務 —— 適合 self-contained 任務（無對話歷史依賴），用 `agent:` 選 subagent 型別
- **`allowed-tools` vs settings 權限**：`allowed-tools` 是 skill 作用時的預批准；基礎權限仍由 settings.json 管理
- **`user-invocable: false`** 用於背景知識（不該被人類 `/invoke`）；`disable-model-invocation: true` 用於人類專屬 workflow（不該被 AI 自動觸發）

### description 寫法

`description` 是 auto-discovery 唯一依據，清單截斷時**從尾部丟**：

- **觸發詞前置** —— 「何時使用 + 同義觸發詞」放前面，功能描述放後；截斷時保住觸發詞
- **涵蓋多種說法** —— 使用者實際會打的詞（中英文同義詞都列）
- **< 1536 字元**（含 when_to_use）
