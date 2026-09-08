# AI 協作開發指南

> **🔗 部署說明**: 本檔是 harness-neutral source，部署到各 harness 全域位置（Claude `~/.claude/CLAUDE.md` symbolic link → 本檔；ZCode `~/.zcode/AGENTS.md`；Codex `~/.codex/AGENTS.md`；Muse Code `~/.config/muse/AGENTS.md`）。專案層雙檔模式（AGENTS.md source；Claude 端另有 CLAUDE.md wrapper）見 [instruction-writing.md](rules/instruction-writing.md)。

> **🔴 強烈警告**: AI 撰寫或修改 instruction 檔（AGENTS.md source；Claude 端另有 CLAUDE.md wrapper）時**絕對禁止**加入統計資訊（行數、字數）、版本號、更新日期。詳細約束（❌ 行為表、自檢清單）見 instruction-writing skill「元資訊禁止行為」章

**適用範圍**: 所有軟體開發專案（量化交易專案優先）
**AI 系統**: Claude Code、KiloCode、Gemini 等
**核心理念**: 品質導向 + 智能協作 + 持續演化

---

## 演化性思維

> **核心原則**：測試保護下的架構重構是可接受的，預設不考慮向後相容。

- 有測試保護時，大膽進行架構級重構
- 向後相容確認時機見 [edit-discipline.md](rules/edit-discipline.md)（rule 為源，此處不重述）
- 持續演化（測試 → 重構 → 確認），而非一次到位

---

## 驗證約束

### 風險分級驗證策略

> **核心原則**：每次修改程式碼後必須執行驗證，驗證深度根據風險調整。

**統一驗證流程**：
1. 修改程式碼
2. 強制執行一次修改的程式碼（除非純註解/文檔）
3. 快速檢查語法和 import
4. 評估變更風險等級
5. 根據風險執行對應驗證深度

**風險分級標準**：
- **🔴 高風險**（核心架構 — 含跨 context 共用 domain service / 會計總量 / 風控 sizing 路徑、數據庫、安全、API 重大修改）→ 必須完整驗證所有相關功能
- **🟡 中等風險**（新功能、演算法優化、性能改進）→ 核心功能測試 + 經驗分析
- **🟢 低風險**（樣式、文檔、配置）→ 至少執行一次確保無語法錯誤

> 詳細執行規範見 [must-execute-before-complete.md](rules/must-execute-before-complete.md)；漸進式驗證（DEPTH-MIN→FULL）見 [quality-constraints.md](rules/quality-constraints.md)

### 務實評估約束

> **核心原則**：提供相對複雜度評估和風險分析，不預測絕對時間。

**必須提供**：複雜度評估、風險識別、依賴分析、里程碑規劃、相對排序
**避免提供**：具體時間預估、精確進度預測、不切實際承諾

---

## UC-Driven Development

> **核心原則**：AGENTS.md Capabilities 記錄已完成能力（✅），backlog board（`backlog/`，Backlog.md——機制單一源見 kanban-board skill）追蹤待辦與進行中任務（📋/🔧）。所有功能開發以 UC（Use Case）定義為前置條件。能力描述和入口路徑是索引鍵。

### 文檔體系

`AGENTS.md`（source；Claude 端另有 CLAUDE.md wrapper）每次 session auto-load；`architecture.md` / `SYSTEM-MAP.md` / `dependency-graph.md` 內容大，用 markdown link on-demand 讀（**不 `@` transclude**，避免撂爆 instruction 檔 — 機制見 [instruction-writing.md](rules/instruction-writing.md)「長文件按需指引」）：

| 文件 | 角色 | 時間視角 |
|------|------|---------|
| `AGENTS.md` / `CLAUDE.md` | 導航 + 已完成能力索引（what / where） | 永久 |
| `architecture.md` | 設計決策 / whole-picture（why）— 有此檔才適用 | 永久 |
| `SYSTEM-MAP.md` | 跨域功能狀態總覽（status） | 現在 |
| `dependency-graph.md` | 跨模組依賴 / ripple 風險地圖 — 有此檔才適用（per-repo opt-in，人工策展；機械依賴/ripple 查詢由 code-reality graph 承擔） | 現在 |
| `backlog/` | 任務追蹤（Backlog.md board——承諾池；機制單一源見 kanban-board skill） | 暫時（結案兩步後卡留 Done 欄；`task complete` 搬 `completed/` 延後到清理批次） |

**UC 生命週期**：📋（execution-plan → `backlog task create`，建卡即 commit——跨 WT id 防撞）→ 🟡（build 階段 1 → `task edit -s "In Progress"`＋開工雙 ref）→ ✅（build 階段 5a → Capabilities＋結案兩步：`-s Done --final-summary` → `--ref` 換 `done/` URL，卡留 Done 欄；UC 完成情境）

### UC 狀態標記

| 標記 | 含義 | 存放位置 |
|------|------|---------|
| ✅ | 已完成 | AGENTS.md Capabilities 表格（Claude 端 CLAUDE.md wrapper 同步） |
| 📋 | 待實作 | backlog To Do 卡（或 drafts——未承諾想法） |
| ❌ | 已棄用 | 從 Capabilities 移除 |
| 🔧 | 部分完成 | backlog To Do 卡 |
| 🟡 | 進行中 | backlog In Progress 卡 |
| 🟢 | 部分覆蓋 | AGENTS.md Capabilities（附限制；Claude 端 CLAUDE.md wrapper 同步） |

**Capabilities 表格格式**：`| 能力 | 入口 | 狀態 |`（每行一個 ✅ UC，入口含 CLI + 函式路徑）

### 放置原則（Domain-First）

- ✅ → **主要實作模組的 AGENTS.md**（如 `mosaic_alpha/data/AGENTS.md`，Claude 端 CLAUDE.md wrapper 同步）
- 📋/🔧 → **backlog To Do 卡**（`backlog/`）
- **UC 不重複**：同一能力只在一個 instruction 檔記錄
- **scripts/ 不放 Capabilities**：scripts/ 是 demo 給老闆的呈現入口（基於 library 重寫，可用 typer），不放 Capabilities

### 變更規模分級

| 規模 | UC 要求 |
|------|---------|
| **大型**（跨模組、新功能） | execution-plan 自動建立 Kanban Backlog card |
| **中型**（功能優化） | 更新既有 Capabilities 或 Kanban card |
| **小型**（bug fix、文檔；結構性修復除外 — 見 execution-plan simple 邊界，Claude: `skills/execution-plan/SKILL.md`） | 不需要 UC |

### 銜接機制

1. **execution-plan → backlog**：UC盤點自動 `backlog task create` 建卡（含 labels、EP 連結；建卡即 commit——命令合約見 kanban-board skill）
2. **build → 進行中＋結算**：階段 1 `backlog task edit <id> -s "In Progress"`（無 `backlog/` 容錯跳過）；階段 5a 結算 UC 完成情境——新增 Capabilities ✅ 行 + backlog 結案兩步（`-s Done --final-summary` → `--ref` 換 `done/` 新 URL，卡留 Done 欄）+ EP 歸檔（任務家 done/，放置學見 illustrate-html-mode「產物位置分流」）（working tree，隨 commit 帶走）
3. **post-build（收尾鏈）**：build 完成、commit 之前——code-review → judge-review → 修正迴圈 → consistency → metadata-sync，止步於 commit 前（詳見 post-build skill）
4. **commit → 純 git 提交**：finalization 已在 build 階段 5a 結算（working tree），commit 一次帶走 code + finalization（**同 commit** 保證，git add 納入 finalization 檔）
5. **卡動作約束（任何 session——含 automation 衍生／監控迴路等不載 build-chain skill 者）**：要對 backlog 卡做事（含結案、歸檔），第一個動作＝`task edit <id> -s "In Progress"`（讓平行 session 可見）；任何 `task complete`／`archive`／清板前必跑 kanban-board skill 的 `scripts/backlog_precheck.sh`（exit 1 = 停手）

---

## Solo + AI 開發工作流

> **核心原則**：一人與 AI 協作（非團隊、無 CI）。工作單元與 session 緊綁，context 稀缺——流程要在這現實下成立。

- **一 EP = 一 session**：一次 session 推進一個 Execution Plan；跨 session 接續靠 EP 段落自足 + 進度結算（段落自包含、可結算可接續）。
- **model 退化就換 session，不硬撐**：長 session 後 LLM 行為變怪 → **結算 EP 進度 → 開新 session 接續**（跨 session：`/handoff`；usage 用盡：`/at`）。累積失敗嘗試比乾淨 context 更糟。
- **`/compact` 節奏**：對話壓縮分佈 EP 各階段（規劃後、逐段 build 間）；命令在 compact 壓力下仍可接續。
- **Writer/Reviewer 分離**：審查自己剛寫的 code 有 bias → 開新/跨 session 審查；review 命令支援「產出 finding → 跨 session 貼回 → 判讀」鏈。

> 消費端共通工作流。專案特定變體（如多 worktree + trunk 模型）由各專案自訂。

---

## 架構設計紀律

> **核心原則**：所有設計決策（spec/EP/implement/review）用 Clean Architecture + DDD 視角檢視。是**視角非模板**（注入思考，不強制分層、不過度工程）— 補體系缺失的架構紀律層。

三主線（依賴規則／bounded context／use case 驅動）、決策分級與兩層思考核心見 [design-thinking.md](rules/design-thinking.md)（rule 為源，此處不重述）。

### SOLID 精神

SOLID 精神實作時遵循，指標細則見 [edit-discipline.md](rules/edit-discipline.md)（rule 為源；五項縮寫展開屬可推導通用知識，不重述）。

> 深入視角（三主線在 spec/illustrate/EP/implement 各自怎麼用）見 arch-thinking skill（與 api-and-interface-design skill 邊界：本視角檢視整體結構，api-and-interface 設計介面合約；跨 harness skill 機制各家不同，路徑從略）。

---

## 量化交易專屬鐵律

量化交易系統有特殊的品質要求，適用 Crash-Only Design 原則。

| 鐵律 | 說明 | 實施策略 |
|------|------|----------|
| **數據完整性優先** | 損壞數據比沒有數據更災難 | Fail-fast（崩潰策略與完整細則見 [quality-constraints.md](rules/quality-constraints.md)）|
| **100% 回測可重現** | hash + config + seed | 波動 >0.01 必須重做 |
| **Crash-Only 恢復機制** | 崩潰後快速恢復 | 狀態外部化，恢復即初始化 |
| **Live / Backtest 共用代碼** | 避免條件分支 | 統一處理邏輯 |
| **算術溢出零容忍** | 數值計算必須嚴格檢查 | 溢出即崩潰，不允許靜默錯誤 |
| **隨機性完全控制** | seed 必須可注入 | np.random 必須避免 |

---

## Summary Instructions（壓縮策略）

> 對話壓縮（`/compact`）觸發時引導 compactor 保留關鍵資訊。

When summarizing this conversation, always preserve:
- File paths that have been read or modified
- Test results and error messages
- Decisions made and the reasoning behind them
- Current task objective and pending items
- Suspended actions: commands/skill invocations submitted but unexecuted, proposals awaiting user confirmation, running background tasks (interrupted executions — unlike pending plans, they vanish with the raw history)
- Counts/ratios: derive from your own enumeration or copy verbatim; never rewrite numbers from memory
