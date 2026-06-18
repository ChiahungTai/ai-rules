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
- `debugging-and-error-recovery` — 系統性根因除錯（非猜測）
- `external-api-investigation` — 外部 API / 整合器真實行為調查（monkey-patch dry-run、查 stub、問 domain；實證優先於讀 code 推理）
- `autonomous-execution` — 無人介入自主執行的決策 / 錯誤恢復 / 完成回報

### 品質與審查
- `code-review-and-quality` — 合併前多軸 code review
- `code-simplification` — 不改行為的重構簡化
- `security-and-hardening` — 未信任輸入 / 外部整合的安全強化
- `performance-optimization` — 效能瓶頸 profiling 與優化
- `python-type-gap` — 第三方套件型別缺口的四層策略

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
- `scan-project` — 統一專案知識掃描（imports + Capabilities + kanban → dep_graph / findings）
- `context-engineering` — session 起始 / 品質退化 / 任務切換時的 context 與 rules 設置
- `agent-workflow` — Agent 派發 / worktree 隔離 / 並發控制 / Writer-Reviewer
- `skill-cleaner` — 稽核 skill：重複 / 未用 / prompt-budget / compact

### 工具與查詢
- `context7-mcp` — library / framework / API 文檔查詢（context7 MCP）
- `nt-query` — NautilusTrader 能力 / 實作查詢（docs-first + LSP-on-Cython-stubs）
- `mermaid` — pragmatism-first Mermaid 圖表生成
- `rules-reminder` — 常被違反的 Bash 規則（rg/fd、無 `#`、`uv run`、無 `$` 展開）
- `voice-notification` — 任務完成 macOS `say` 通知（三模式）
- `idea-refine` — 結構化發散 / 收斂的想法精煉
- `using-agent-skills` — skill 發現與呼叫的 meta-skill

### UI / 協作
- `frontend-ui-engineering` — Panel/Bokeh 互動 dashboard / 視覺化
- `browser-testing-with-devtools` — 真實瀏覽器 DevTools 測試
- `ui-collab` — 互動式 UI 的 LLM 協作模式（`[ACTION]` 操作日誌）

### 領域特定
- `trading-analysis` — 股票 / 市場走勢三層分析（經典 TA → 量化 → 第二層思考）

## Frontmatter 配置

```yaml
---
name: skill-name                    # 必填：小寫、數字、連字符 (最多 64 字元)
description: 功能描述和觸發條件    # 必填：功能 + 何時使用 (最多 1024 字元)
allowed-tools:                      # 可選：限制工具存取權限
  - Read
  - Write
  - Edit
model: sonnet|opus|haiku|inherit    # 可選：指定使用的 Claude 模型
skills: dependency-skill            # 可選：依賴的其他技能
---
```

`description` 是觸發關鍵 — 必須同時說明**功能**和**觸發條件**，包含多種同義觸發詞。
