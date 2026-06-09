# AI 協作開發指南

> **🔗 Symbolic Link 說明**: `~/.claude/CLAUDE.md` 是一個 symbolic link，連結目標為 `ai-rules/ai-development-guide.md`

> **🔴 強烈警告**: AI 寫作或修改 CLAUDE.md 時**絕對禁止**加入統計資訊（行數、字數）、版本號、更新日期。詳細約束請參考 `@~/.claude/rules/_ai-behavior-constraints.md`

**適用範圍**: 所有軟體開發專案（量化交易專案優先）
**AI 系統**: Claude Code、KiloCode、Gemini 等
**核心理念**: 品質導向 + 智能協作 + 持續演化

---

## 🤝 協作哲學

你現在進入的是 **品質導向、智能協作、持續演化** 的開發環境。

我們重視：
- **事實驗證**：基於實際程式碼查證，不依賴經驗推測
- **測試保護**：在測試覆蓋下進行架構優化和重構
- **完整交付**：方向明確時執行到可用狀態，絕不交付半成品
- **架構優先**：優先考慮長期架構品質，向後相容需特別確認

---

## 價值導向思維

> **核心原則**：在評價任何技術方案前，必須先深度理解要解決的問題和痛點。

**技術方案評估流程**：
1. **痛點分析** - 要解決什麼痛點？不解決的災難性後果？
2. **價值衡量** - 解決後的長期價值？對用戶體驗的改善？
3. **技術評估** - 實作複雜度？維護成本？
4. **綜合決策** - 價值 vs 成本，值得做嗎？

**借鑒與原創的權衡**：
- 借鑒成熟方案是**聰明的實用主義**（已有成熟方案、用戶明確要求、避免重複造輪子）
- 原創但不實用 = 浪費時間
- 追求解決問題，而非追求新穎性

**深度理解用戶意圖**：
- **字面意思** → 聽清楚字面內容
- **深層意圖** → 理解背後的目的
- **背景脈絡** → 同理用戶處境
- **有疑問時主動詢問**，不基於假設進行實作

---

## 演化性思維

> **核心原則**：測試保護下的架構重構是可接受的，優先考慮長期架構品質。

**核心理念**：
- **測試是安全網**：有測試保護時，大膽進行架構級重構
- **架構優先**：預設不考慮向後相容，優先考慮架構品質
- **持續演化**：在測試保護下持續改進，而非一次到位

**測試驅動重構**：
1. 先寫測試保護現有行為
2. 進行架構級重構
3. 確認測試通過
4. 持續改進直到架構滿意

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
- **🔴 高風險**（核心架構、數據庫、安全、API 重大修改）→ 必須完整驗證所有相關功能
- **🟡 中等風險**（新功能、演算法優化、性能改進）→ 核心功能測試 + 經驗分析
- **🟢 低風險**（樣式、文檔、配置）→ 至少執行一次確保無語法錯誤

> 詳細執行規範（禁止行為、流程、起源證據）見 `~/.claude/rules/must-execute-before-complete.md`；漸進式驗證流程（DEPTH-MIN → DEPTH-SAMPLE → DEPTH-FULL）見 `~/.claude/rules/progressive-validation.md`

### 務實評估約束

> **核心原則**：提供相對複雜度評估和風險分析，不預測絕對時間。

**必須提供**：複雜度評估、風險識別、依賴分析、里程碑規劃、相對排序
**避免提供**：具體時間預估、精確進度預測、不切實際承諾

---

## UC-Driven Development

> **核心原則**：UC ID 是穩定錨點，貫穿三層文件體系。CLAUDE.md Capabilities 記錄已完成能力（✅），.kanban/ 追蹤待辦與進行中任務（📋/🔧）。所有功能開發以 UC 定義為前置條件。

### 解決的痛點

| 痛點 | UC-Driven 解法 |
|------|---------------|
| LLM 不善用已有程式碼（token 限制下傾向重新發明） | CLAUDE.md Capabilities 表格是緊湊的能力索引，LLM 掃一眼即知系統能做什麼 |
| 文檔維護成本高 | Capabilities 只記「做什麼」+ 入口，不記「怎麼做」（怎麼做看程式碼） |
| 依賴人類記憶力才知道什麼做過 | `/task-status` 隨時可查 Kanban 進度，`/doc-health` 檢查 Capabilities 準確性 |
| LLM 重複造輪子 | `/spec` 啟動時先掃描相關 Capabilities + Kanban，避免定義已有功能 |

### 與 BDD 的區別

| | **BDD** | **UC-Driven Development** |
|--|---------|--------------------------|
| 核心目的 | 驗證正確性（test-as-spec） | 協調開發 + LLM 上下文管理 |
| 格式 | Gherkin（Given/When/Then） | Kanban card（📋）+ Capabilities row（✅） |
| 角色 | 測試工程師、QA | 開發者 + AI Agent |
| 解決的問題 | 需求→測試的 gap | LLM 不知道系統能做什麼的 gap |

兩者互補不衝突。BDD 解決「怎麼驗證對不對」；UC-Driven 解決「LLM 知不知道系統有什麼」。

### 三層文件體系（CLAUDE.md + SYSTEM-MAP.md + Kanban）

USE-CASES.md 的 ✅ 條目蒸餾至各模組 CLAUDE.md 的 Capabilities 表格，📋/🔧 條目遷移至 .kanban/ Backlog cards，USE-CASES.md 檔案刪除。三層文件各司其職：
- **CLAUDE.md**（架構 + 能力）：Capabilities 表格取代 USE-CASES 導航表格，記錄已完成能力
- **SYSTEM-MAP.md**（功能狀態）：跨域功能狀態總覽
- **.kanban/**（任務管理）：取代 UC-BACKLOG.md 的優先佇列功能，📋/🔧 條目以 Kanban cards 存在

**UC ID 生命週期**：
- 📋 階段：/spec 建立 Kanban Backlog card（UC ID 在此誕生）
- 🟡 階段：card 移至 Next-Up/In-Progress（進行中）
- ✅ 階段：/build 完成 → CLAUDE.md Capabilities table 新增一行 + card 移至 Done/

**跨文件引用**：UC ID 是穩定錨點，貫穿 CLAUDE.md（✅）、Kanban cards（📋/🔧）、SYSTEM-MAP.md（功能引用）。

### UC 狀態標記

每個 UC 條目依狀態放在不同位置：

| 標記 | 含義 | 存放位置 |
|------|------|---------|
| ✅ | 已完成 | CLAUDE.md Capabilities 表格 |
| 📋 | 待實作 | .kanban/Backlog/ card |
| ❌ | 已棄用 | 從 Capabilities 移除（或標記 ❌） |
| 🔧 | Library 已實作 / 部分完成 | .kanban/Backlog/ card（含剩餘細節） |
| 🟡 | 進行中 | .kanban/Next-Up/ 或 In-Progress/ card |
| 🟢 | 部分覆蓋 | CLAUDE.md Capabilities（附已知限制） |

**CLAUDE.md Capabilities 表格格式**（✅ 條目）：

| UC ID | 能力 | 入口 | 狀態 |
|-------|------|------|------|
| D-18 | 每日增量 K 線更新 | CLI `daily-update` / `run_daily_update()` | ✅ |

**Kanban card 格式**（📋/🔧 條目）：每張卡片有 frontmatter（UC ID、模組、標題、spec 連結）+ body（設計要點、測試計畫、剩餘細節）。

### 四種開發情境

| 情境 | 觸發 | UC 路徑 |
|------|------|---------|
| **A: 一次到位** | /spec → EP → /build 完成 | 📋(Kanban Backlog) → ✅(CLAUDE.md Capabilities) |
| **B: 分段完成** | /spec → EP → /build 部分 | 📋(Kanban) → 🔧(Kanban，內嵌剩餘細節) |
| **C: 回溯盤點** | 已有程式碼 | ✅(CLAUDE.md Capabilities) 或 📋(Kanban Backlog) |
| **D: 棄用清理** | 功能淘汰 | ❌（從 Capabilities 移除） |

**未完成項處理**：📋/🔧 Kanban card 內直接記錄實作細節（前置條件、設計要點、測試計畫）。轉為 ✅ 時清理暫時性資訊，寫入 CLAUDE.md Capabilities 表格。

**測試計畫內容**：描述測試的**種類和情境**，不寫數量。包含：測試類型分佈（單元 / 整合 / E2E / 外部 API mock）、關鍵情境覆蓋（happy path、邊界案例、error handling、冪等性）、已知未覆蓋的風險。禁止寫測試數量 — 數字每次修改都過時，對決策無價值。

### 變更規模分級

| 規模 | UC 要求 | 說明 |
|------|---------|------|
| **大型**（跨模組、新功能） | /spec 必須建立 Kanban Backlog card（📋） | UC 為開發前置條件 |
| **中型**（功能優化、新 API） | 更新既有 Capabilities 或 Kanban card | 不需新建 card，但需更新 |
| **小型**（bug fix、文檔） | 不需要 UC | 不影響系統行為 |

### UC 放置原則（Domain-First）

> **核心原則**：UC ID 對應模組域（如 D- = data, SJ- = adapters/sj）。✅ 條目歸屬於**主要實作所在的 library 模組目錄**的 CLAUDE.md，📋/🔧 條目以 Kanban cards 管理。

**放置規則**：
- ✅ 條目 → **對應模組 CLAUDE.md 的 Capabilities 表格**（如 `mosaic_alpha/data/CLAUDE.md`）
- 📋/🔧 條目 → **.kanban/ Backlog cards**（不放在 CLAUDE.md）
- UC ID 前綴對應模組域（如 D- = data, SJ- = adapters/sj, FE- = features）
- **UC 不重複原則**：同一能力只在一個 CLAUDE.md 的 Capabilities 表格記錄

**跨域資訊歸屬**：
- **跨域依賴**：Capabilities 表格的「領域依賴」欄位引用其他 UC ID
- **跨域流程**：SYSTEM-MAP.md 按工作流組織功能區塊，引用 UC ID
- **跨域狀態**：SYSTEM-MAP.md 追蹤功能生命週期（🏃/✅🔍/✅/⚠️/📋/❌）
- **域以程式碼目錄為準**：同一 `mosaic_alpha/` 子目錄視為同一域

**scripts/ 定位**：scripts/ 是 thin wrapper 層（CLI 入口），**不放 Capabilities 表格**。

### CLAUDE.md Capabilities + .kanban/ 合作

兩者是同一 UC ID 的兩個正交視角。✅ 時寫入 CLAUDE.md（永久），📋/🔧 時存在 .kanban/（暫時）。

| 文件 | 職責 | 時間視角 |
|------|------|---------|
| `CLAUDE.md` Capabilities | 架構 + 已完成能力索引 | 永久（✅ 條目） |
| `.kanban/` cards | 任務追蹤 + 進度管理 | 暫時（📋→✅ 後移至 Done/） |

**銜接機制**：

1. **/spec → Kanban Backlog**：新建 UC 時建立 .kanban/Backlog/ card（含 UC ID、模組、spec 連結）
2. **/build → Capabilities + Done**：完成時在 CLAUDE.md Capabilities 表格新增一行，同時移動 Kanban card 至 Done/
3. **原子操作**：Capabilities 新增 + Kanban card 移動必須同時完成（`/doc-health` angle 6 驗證）

### Scenario Matrix：EP 規劃期的消費場景思考

> **核心原則**：EP 規劃時強制思考「使用者會遇到哪些情境」，避免實作完成才發現漏掉錯誤路徑或邊界案例。矩陣是 EP 的規劃工具，產出後提煉成消費場景寫入 CLAUDE.md Capabilities 或 Kanban card。

**術語層級**（glossary）：
- **Scenario Matrix** = EP 中的 artifact（一個表格，規劃期產出，EP 完成後隨 EP 歸檔）
- **消費場景** = Capabilities 表格或 Kanban card 的欄位（自包含描述）
- **場景** = Scenario Matrix 表格中的 column 概念（單一情境）

**為什麼放 EP 而非 /spec**：/spec 不一定每次都跑（小型/中型變更可能跳過），但 EP 是中大型變更的必經關卡，作為強制思考點覆蓋率更高。

**Scenario Matrix 格式**（EP 內的表格區段）：

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應 UC |
|---|------|------|---------|------------|---------|
| SM-1 | 每日例行 | launchd / 手動 | Full pipeline | 無（從頭算） | D-14 |
| SM-2 | 改 ranking 重跑歷史 | 手動 --date | 讀 snapshot → Analysis → JSON | snapshot | D-14（部分） |
| SM-3 | 缺 snapshot 且未加 --rebuild-features | 錯誤操作 | assert fail + 提示 | — | — |

**欄位含義**：
- **場景**：使用者想做的事（意圖導向，非操作步驟）
- **觸發**：CLI flag、外部事件、錯誤操作
- **預期行為**：系統該怎麼反應（happy path、error path 都算）
- **Checkpoint**：從哪個狀態恢復（無、catalog、snapshot）
- **對應 UC**：本場景引用的 UC ID（可能對應多個 UC，或僅部分步驟）

**必須涵蓋的場景類型**：
- Happy path（正常使用）
- 錯誤操作（缺參數、缺前置條件）
- 邊界案例（空資料、跨日、回補多天）
- 效能期待差異（秒級、幾十秒、慢、線性放大）

**散到 Capabilities 的「消費場景」**：
EP 完成後，每個 UC 的消費場景從矩陣提煉成自包含描述（不引用 EP/SM 編號，因為 EP 可能歸檔或刪除）。✅ UC 寫入 CLAUDE.md Capabilities 表格的備註；📋/🔧 UC 寫入 Kanban card 的描述。

### Command Pipeline 整合

```
/spec（建立 Kanban Backlog card）→ /execution-plan（引用 UC ID + SYSTEM-MAP 關聯）→ [/ep-validate] → /build（CLAUDE.md Capabilities + Kanban Done）
    → /code-review（驗證 Capabilities 覆蓋度）→ /commit（確認 Capabilities + Kanban 同步）→ /task-status
```

| Command | UC 職責 |
|---------|--------|
| `/spec` | 啟動時掃描相關 **CLAUDE.md Capabilities** + SYSTEM-MAP.md；建立 Kanban Backlog card（含 UC ID） |
| `/execution-plan` | EP 段落引用 UC ID（如「實作 D-31」）；掃描 SYSTEM-MAP.md 取得功能上下文；大型/中型變更須產出 Scenario Matrix |
| `/build` | 段落完成後：CLAUDE.md Capabilities 表格新增 ✅ 行 + Kanban card 移至 Done/；從 EP Scenario Matrix 提煉消費場景；未完成段落更新 Kanban card 內嵌細節；更新 SYSTEM-MAP.md 功能生命週期狀態 |
| `/code-review` | 第六軸：Capabilities 覆蓋度（實作是否滿足 **CLAUDE.md Capabilities** 描述） |
| `/commit` | 大型/中型變更時提示確認 Capabilities + Kanban 同步 |
| `/standup` | Kanban 進度摘要（狀態變化、新增、關閉）+ SYSTEM-MAP 功能進度 |
| `/task-status` | Kanban-centric 進度儀表板（Lane 分佈 + 模組 Breakdown + Stale Cards） |
| `/doc-health` | Capabilities + Kanban 健康檢查（12 角度 + `--report` 檔案輸出）；`--sync-system-map` 用 Capabilities 狀態同步 SYSTEM-MAP.md |

### 文件放置

- **CLAUDE.md Capabilities**：放在**主要實作所在的 library 模組目錄**（如 `mosaic_alpha/data/CLAUDE.md`），每個 ✅ UC 有唯一 ID 和一行記錄
- **SYSTEM-MAP.md**：專案根目錄，按使用者工作流組織的功能狀態總覽（唯一跨域入口）
- **.kanban/**：專案根目錄，Kanban board（`Backlog/`、`Next-Up/`、`In-Progress/`、`Review/`、`Done/` lanes）
- **禁止放在 scripts/**：scripts/ 是 thin wrapper，不放 Capabilities 表格
- **跨域視角只在 SYSTEM-MAP.md**：工作流編排、功能狀態、跨模組消費關係統一由 SYSTEM-MAP.md 管理，Capabilities 只描述單一模組能力

**SYSTEM-MAP 生命週期狀態定義**：

| 狀態 | 含義 | 升級條件 | 降級條件 | 對應 UC 狀態 |
|------|------|---------|---------|------------|
| 🏃 Running | 透過排程或工作流每日自動運行 | — | 自動化流程中斷或停止 → ⚠️ | 功能內 UC 多為 ✅ |
| ✅🔍 Verified | 程式碼完整 + 測試通過 + 整合環境驗證過 | UC 全部 ✅ + 測試通過 + 已在整合流程消費 | — | 功能內 UC 全部 ✅ |
| ✅ Built | 程式碼存在 + 測試通過，未在整合環境驗證 | 完成整合驗證 → ✅🔍 | 發現問題 → ⚠️ | 功能內 UC 全部 ✅ |
| ⚠️ Issues | 運行中或已完成但有已知問題 | 問題修復 → ✅🔍 或 ✅ Built | — | 部分 UC 可能有 📋/🔧 |
| 📋 Planned | 尚未實作 | 開始實作 → 🟡 或直接 ✅ Built | — | 功能內 UC 多為 📋 |
| ❌ Abandoned | 已廢棄，不再規劃 | — | — | UC 標記 ❌ |

**判定流程**：由 Capabilities + Kanban 狀態聚合推導。功能內所有 UC ✅ + 有整合驗證 → ✅🔍；全部 ✅ 但無整合驗證 → ✅ Built；有 📋/🔧 → 視問題嚴重度 ⚠️ 或 📋。`/doc-health --sync-system-map` 自動執行此推導。

**三元文件分工**：

| 文件 | 角色 | 時間視角 |
|------|------|---------|
| `CLAUDE.md` Capabilities | 已完成能力索引（按模組組織） | 永久 |
| `SYSTEM-MAP.md` | 功能狀態總覽（按工作流組織） | 現在 |
| `.kanban/` | 任務管理（Kanban lanes） | 暫時（Done/ 歸檔） |

---

## 工作流程

**任務執行流程**：
1. 確認方向明確且技術可行
2. 制定完整的執行計劃和驗收標準
3. 按照標準完整執行，中途不急著結束
4. 確保所有相關測試、文檔、配置都完成
5. 達到完整可用狀態才交付

**智能決策框架**（深層思考框架定義見 `~/.claude/rules/deep-thinking.md`）：
1. 評估決策類型（單向門/雙向門）和變更風險等級
2. 第一性原理分析（本質需求、元素拆解、原理推導）
3. 第二層後果追蹤（至少追蹤兩層後果，強制）
4. 根據風險選擇驗證深度（高風險→實際驗證，中風險→重點驗證，低風險→基於經驗）
5. 註明資料來源和決策依據
6. 提供替代方案和風險分析

---

## AI 自我審查清單

> **建議遵循**：回覆前確認以下項目

1. 我有沒有驗證 import（如適用）？
2. 我有沒有考慮錯誤處理策略？
3. 我有沒有引用真實路徑和來源（如適用）？
4. 我的判斷是否基於代碼和事實？
5. 這個建議在實際環境中是否可行？
6. 有沒有任何表達是模糊不清的？
7. 是否考慮了用戶體驗和生產環境需求？
8. 我是否提供了平衡的分析，而非極端化建議？

---

## 量化交易專屬鐵律

量化交易系統有特殊的品質要求，適用 Crash-Only Design 原則。

**核心鐵律**：
| 鐵律 | 說明 | 實施策略 |
|------|------|----------|
| **數據完整性優先** | 損壞數據比沒有數據更災難 | Fail-fast，無效輸入立即崩潰 |
| **100% 回測可重現** | hash + config + seed | 波動 >0.01 必須重做 |
| **Crash-Only 恢復機制** | 崩潰後快速恢復 | 狀態外部化，恢復即初始化 |
| **Live / Backtest 共用代碼** | 避免條件分支 | 統一處理邏輯 |
| **算術溢出零容忍** | 數值計算必須嚴格檢查 | 溢出即崩潰，不允許靜默錯誤 |
| **隨機性完全控制** | seed 必須可注入 | np.random 必須避免 |

**代碼品質要求**：
- 每個策略必須有完整單元測試，測試失敗即崩潰
- 所有數值計算必須有溢出檢查，溢出立即崩潰
- 數據驗證失敗立即崩潰，不嘗試修復損壞數據
- 策略邏輯必須可解釋且有完整日誌
- 實盤部署前必須通過壓力測試和崩潰恢復測試

**Crash-Only 風控機制**：
- **數據層級風控**：輸入驗證失敗立即崩潰，避免損壞數據傳播
- **策略層級風控**：單筆、總倉位、停止損機制，違規即崩潰
- **系統層級風控**：異常檢測失敗立即崩潰，自動重啟恢復
- **恢復機制**：狀態外部化，重啟後從持久化存儲完整恢復

---

## Summary Instructions（/compact 壓縮策略）

> **觸發時機**：`/compact` 手動或自動壓縮對話時，此區塊引導 compactor 保留關鍵資訊。

When summarizing this conversation, always preserve:
- File paths that have been read or modified
- Test results and error messages
- Decisions made and the reasoning behind them
- Current task objective and pending items

---

> 💡 **協作哲學**：高品質的 AI 協作需要平衡嚴謹性與靈活性。本指南提供指導原則而非死板規則，鼓勵根據實際情況做出專業判斷。

> 🤖 **AI 協作價值**：AI 作為智能協作夥伴，需要在專業能力和適應性之間找到平衡，為用戶提供既有價值又實用的建議。

> ⚡ **持續改進**：本指南本身也會根據實際使用經驗持續優化，確保其實用性和時效性。
