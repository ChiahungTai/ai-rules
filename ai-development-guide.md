# AI 協作開發指南

> **🔗 Symbolic Link 說明**: `~/.claude/CLAUDE.md` 是一個 symbolic link，連結目標為 `ai-rules/ai-development-guide.md`

> **🔴 強烈警告**: AI 寫作或修改 CLAUDE.md 時**絕對禁止**加入統計資訊（行數、字數）、版本號、更新日期。詳細約束請參考 `@~/.claude/rules/_ai-behavior-constraints.md`

**適用範圍**: 所有軟體開發專案（量化交易專案優先）
**AI 系統**: Claude Code、KiloCode、Gemini 等
**核心理念**: 品質導向 + 智能協作 + 持續演化

---

## 演化性思維

> **核心原則**：測試保護下的架構重構是可接受的，預設不考慮向後相容。

- 有測試保護時，大膽進行架構級重構
- 向後相容只在影響外部系統整合、已有生產數據、部署環境時需確認
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

> 詳細執行規範見 `~/.claude/rules/must-execute-before-complete.md`；漸進式驗證見 `~/.claude/rules/progressive-validation.md`

### 務實評估約束

> **核心原則**：提供相對複雜度評估和風險分析，不預測絕對時間。

**必須提供**：複雜度評估、風險識別、依賴分析、里程碑規劃、相對排序
**避免提供**：具體時間預估、精確進度預測、不切實際承諾

---

## UC-Driven Development

> **核心原則**：CLAUDE.md Capabilities 記錄已完成能力（✅），.kanban/ 追蹤待辦與進行中任務（📋/🔧）。所有功能開發以 UC（Use Case）定義為前置條件。能力描述和入口路徑是索引鍵。

### 文檔體系

`CLAUDE.md` 每次 session auto-load；`architecture.md` / `SYSTEM-MAP.md` / `dependency-graph.md` 內容大，用 markdown link on-demand 讀（**不 `@` transclude**，避免撂爆 CLAUDE.md — 機制見 [instruction-writing.md](~/.claude/rules/instruction-writing.md)「長文件按需指引」）：

| 文件 | 角色 | 時間視角 |
|------|------|---------|
| `CLAUDE.md` | 導航 + 已完成能力索引（what / where） | 永久 |
| `architecture.md` | 設計決策 / whole-picture（why）— 有此檔才適用 | 永久 |
| `SYSTEM-MAP.md` | 跨域功能狀態總覽（status） | 現在 |
| `dependency-graph.md` | 跨模組依賴 / ripple 風險地圖 — maintain Phase 1.3 維護（非 /consistency 範圍） | 現在 |
| `.kanban/` | 任務追蹤（Kanban lanes） | 暫時（Done/ 歸檔） |

**UC 生命週期**：📋（/execution-plan → Backlog card，UC盤點自動建卡）→ 🟡（/build → InProgress）→ ✅（/build 階段 5a → Capabilities + Done，UC 完成情境）

### UC 狀態標記

| 標記 | 含義 | 存放位置 |
|------|------|---------|
| ✅ | 已完成 | CLAUDE.md Capabilities 表格 |
| 📋 | 待實作 | .kanban/Backlog/ card |
| ❌ | 已棄用 | 從 Capabilities 移除 |
| 🔧 | 部分完成 | .kanban/Backlog/ card |
| 🟡 | 進行中 | .kanban/Next-Up/ 或 In-Progress/ |
| 🟢 | 部分覆蓋 | CLAUDE.md Capabilities（附限制） |

**Capabilities 表格格式**：`| 能力 | 入口 | 狀態 |`（每行一個 ✅ UC，入口含 CLI + 函式路徑）

### 放置原則（Domain-First）

- ✅ → **主要實作模組的 CLAUDE.md**（如 `mosaic_alpha/data/CLAUDE.md`）
- 📋/🔧 → **.kanban/Backlog/** cards
- **UC 不重複**：同一能力只在一個 CLAUDE.md 記錄
- **scripts/ 不放 Capabilities**：scripts/ 是 demo 給老闆的呈現入口（基於 library 重寫，可用 typer），不放 Capabilities

### 變更規模分級

| 規模 | UC 要求 |
|------|---------|
| **大型**（跨模組、新功能） | /execution-plan 自動建立 Kanban Backlog card |
| **中型**（功能優化） | 更新既有 Capabilities 或 Kanban card |
| **小型**（bug fix、文檔；結構性修復除外 — 見 [execution-plan](commands/execution-plan.md) simple 邊界） | 不需要 UC |

### 銜接機制

1. **/execution-plan → Backlog**：UC盤點自動建立 .kanban/Backlog/ card（含模組、EP 連結）
2. **/build → InProgress + 結算**：階段 1 搬 Backlog cards 至 In-Progress/（暫時狀態）；階段 5a 結算 UC 完成情境——新增 Capabilities ✅ 行 + 搬 Done/ + EP 歸檔（working tree，隨 commit 帶走）
3. **/commit → 純 git 提交**：finalization 已在 build 階段 5a 結算（working tree），commit 一次帶走 code + finalization（**同 commit** 保證，git add 納入 finalization 檔）

---

## 架構設計紀律

> **核心原則**：所有設計決策（spec/EP/build/review）用 Clean Architecture + DDD 視角檢視。是**視角非模板**（注入思考，不強制分層、不過度工程）— 補體系缺失的架構紀律層。

### 三主線

- **依賴規則（Clean Architecture 分層）**：domain ← use case ← adapter ← infra，依賴**向內**（內層不依賴外層）。設計時自問「新東西落哪層？依賴方向對嗎？有無循環？」
- **bounded context（DDD 邊界）**：每個 context 邊界清楚，**不跨域直接存取內部**（`_private`）。設計時自問「這該在哪個 context？有無跨域存取？」
- **use case 驅動**：先問**消費者要什麼行為**（use case），再設計結構（與 UC-Driven 呼應）。設計時自問「消費者是誰？結構撐得起 use case 嗎？」

### SOLID 精神

SRP（單一職責）/ OCP（擴展開放）/ LSP（子型替換）/ ISP（介面隔離）/ DIP（依賴反轉）— 實作時遵循，詳見 `~/.claude/rules/code-edit-constraints.md`。

### 視角非模板

本紀律是**設計視角**（檢視結構方向），非強制分層模板 — 不要求每個專案套四層。原則通用，範例領域特定（mosaic：domain=策略訊號 / use case=回測下單 / adapter=NT·SJ·catalog / infra）。

> 深入視角（三主線在 spec/illustrate/EP/build 各自怎麼用）見 [arch-thinking](skills/arch-thinking/SKILL.md) skill（與 [api-and-interface-design](skills/api-and-interface-design/SKILL.md) 邊界：本視角檢視整體結構，api-and-interface 設計介面合約）。

---

## 量化交易專屬鐵律

量化交易系統有特殊的品質要求，適用 Crash-Only Design 原則。

| 鐵律 | 說明 | 實施策略 |
|------|------|----------|
| **數據完整性優先** | 損壞數據比沒有數據更災難 | Fail-fast，無效輸入立即崩潰 |
| **100% 回測可重現** | hash + config + seed | 波動 >0.01 必須重做 |
| **Crash-Only 恢復機制** | 崩潰後快速恢復 | 狀態外部化，恢復即初始化 |
| **Live / Backtest 共用代碼** | 避免條件分支 | 統一處理邏輯 |
| **算術溢出零容忍** | 數值計算必須嚴格檢查 | 溢出即崩潰，不允許靜默錯誤 |
| **隨機性完全控制** | seed 必須可注入 | np.random 必須避免 |

---

## Summary Instructions（/compact 壓縮策略）

> **觸發時機**：`/compact` 手動或自動壓縮對話時，此區塊引導 compactor 保留關鍵資訊。

When summarizing this conversation, always preserve:
- File paths that have been read or modified
- Test results and error messages
- Decisions made and the reasoning behind them
- Current task objective and pending items
