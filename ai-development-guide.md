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

> 詳細執行規範（禁止行為、流程、起源證據）見 `~/.claude/rules/must-execute-before-complete.md`；漸進式驗證流程（QUICK → REPRESENTATIVE → ALL）見 `~/.claude/rules/progressive-validation.md`

### 務實評估約束

> **核心原則**：提供相對複雜度評估和風險分析，不預測絕對時間。

**必須提供**：複雜度評估、風險識別、依賴分析、里程碑規劃、相對排序
**避免提供**：具體時間預估、精確進度預測、不切實際承諾

---

## UC-Driven Development

> **核心原則**：USE-CASES.md 是開發的起點和驅動力（系統應該做到什麼），不是事後追蹤。所有功能開發以 UC 定義為前置條件。

### 解決的痛點

| 痛點 | UC-Driven 解法 |
|------|---------------|
| LLM 不善用已有程式碼（token 限制下傾向重新發明） | USE-CASES.md 是緊湊的能力索引，LLM 掃一眼即知系統能做什麼 |
| 文檔維護成本高 | UC 只記「做什麼」+ 狀態，不記「怎麼做」（怎麼做看程式碼） |
| 依賴人類記憶力才知道什麼做過 | `/uc-status` 隨時可查，不依賴記憶 |
| LLM 重複造輪子 | `/spec` 啟動時先掃描相關 UC，避免定義已有功能 |

### 與 BDD 的區別

| | **BDD** | **UC-Driven Development** |
|--|---------|--------------------------|
| 核心目的 | 驗證正確性（test-as-spec） | 協調開發 + LLM 上下文管理 |
| 格式 | Gherkin（Given/When/Then） | 自由格式 Markdown + 狀態標記 |
| 角色 | 測試工程師、QA | 開發者 + AI Agent |
| 解決的問題 | 需求→測試的 gap | LLM 不知道系統能做什麼的 gap |

兩者互補不衝突。BDD 解決「怎麼驗證對不對」；UC-Driven 解決「LLM 知不知道系統有什麼」。

### UC 狀態標記

每個 UC 條目的標題行必須以狀態 emoji 開頭，方便滾動掃描：

| 標記 | 含義 |
|------|------|
| ✅ | 已完成 |
| 📋 | 待實作 |
| ❌ | 已棄用 |
| 🔧 | Library 已實作 / 部分完成（回溯盤點或分段完成，待整合或驗證） |
| 🟡 | 進行中（正在執行或等待前置完成） |
| 🟢 | 部分覆蓋（有部分數據，已知限制） |

標題格式：`### ✅ UC-ID: 簡述 — 專案相對路徑`

實作位置必須使用**專案根目錄相對路徑**（如 `mosaic_alpha/data/fetchers/twse_api.py`、`mosaic_alpha/workflows/pipeline.py`），禁止只寫檔名。理由：USE-CASES.md 的讀者是 AI agent，裸檔名無法定位程式碼。

### 四種開發情境

| 情境 | 觸發 | UC 路徑 |
|------|------|---------|
| **A: 一次到位** | /spec → EP → /build 完成 | 📋→✅ |
| **B: 分段完成** | /spec → EP → /build 部分 | 📋→🔧（內嵌剩餘細節） |
| **C: 回溯盤點** | 已有程式碼 | ✅ 或 📋 |
| **D: 棄用清理** | 功能淘汰 | ❌ |

**未完成項處理**：📋/🔧 條目內直接記錄實作細節（前置條件、設計要點、測試計畫）。轉為 ✅ 時清理暫時性資訊（前置條件、測試計畫），保留已知限制和結果摘要。

**測試計畫內容**：描述測試的**種類和情境**，不寫數量。包含：測試類型分佈（單元 / 整合 / E2E / 外部 API mock）、關鍵情境覆蓋（happy path、邊界案例、error handling、冪等性）、已知未覆蓋的風險。禁止寫測試數量 — 數字每次修改都過時，對決策無價值。

**章節歸位**：「待實作」章節的 UC 轉為 ✅ 後，必須搬到對應的正確章節（如「一次性設定與回填」、「定期維護」等）。留在「待實作」會稀釋該區段的信號（讀者掃描待實作區期待看到真正待辦的事項）。

### 變更規模分級

| 規模 | UC 要求 | 說明 |
|------|---------|------|
| **大型**（跨模組、新功能） | /spec 必須定義新 UC（📋） | UC 為開發前置條件 |
| **中型**（功能優化、新 API） | 更新既有 UC 描述或狀態 | 不需新建 UC，但需更新 |
| **小型**（bug fix、文檔） | 不需要 UC | 不影響系統行為 |

### UC 放置原則（Domain-First）

> **核心原則**：USE-CASES.md 放在**主要實作所在的 library 模組目錄**，不放在使用者入口層（如 scripts/）。理由：USE-CASES.md 的核心消費者是 AI agent，AI agent 在 library 層工作時需要直接看到能力索引。

**UC 分類**：

| 層級 | 定義 | 歸屬 |
|------|------|------|
| **Domain UC** | 單一 library 模組的能力描述 | 該 library 模組的 `USE-CASES.md` |
| **Workflow UC** | 跨 library 模組的端到端流程 | `workflows/USE-CASES.md`（編排層） |
| **Consumer Domain UC** | Domain UC + 跨域依賴（主要邏輯在一個模組，但引用其他模組） | 主要 library 模組的 `USE-CASES.md`，標記「領域依賴」 |

**判定流程**（按順序判斷，命中即停止）：

1. UC 的主要邏輯跨越多個模組？→ **Workflow UC** → `workflows/USE-CASES.md`
2. UC 有跨域依賴但主要邏輯在一個模組？→ **Consumer Domain UC** → 主要 library 模組，標記「領域依賴」
3. UC 的主要邏輯在一個模組內？→ **Domain UC** → 主要 library 模組的 USE-CASES.md

**Domain UC 格式**（每個 UC 描述單一領域的能力）：

```markdown
### ✅ D-18: 每日增量 K 線更新 — mosaic_alpha/data/daily_update/coordinator.py

- **能力**: 從 TWSE/TPEX API 增量更新日 K 線至 Catalog
- **入口**: CLI `daily-update` / library `run_daily_update()`
- **消費場景**: 每日例行全量更新、回補多天（逐日呼叫）
- **領域依賴**: calendar（交易日判斷）、fetchers（API 取得）
- **下游消費者**: WF-01（每日工作流）
```

**Workflow UC 格式**（引用 Domain UC，不重複描述）：

```markdown
### ✅ WF-01: 每日工作流 — mosaic_alpha/workflows/pipeline.py

- **編排流程**:
  1. DataPhase: D-31（DailyClosePipeline）→ 數據更新
  2. FeaturePhase: DS-01（MLDataset 組裝）→ 特徵計算
  3. AnalysisPhase: W-01/W-02（可插拔 WatchlistMethod）→ 選股排名
  4. PersistPhase: 結果持久化
- **消費場景**: 每日例行全 pipeline、改 ranking 用 --date 重跑歷史、改 Feature 用 --rebuild-features 重算
- **跨領域依賴**: D-31, DS-01, W-01, W-02
- **觸發**: Launchd 15:30（收盤後）
```

**跨域依賴處理**：
- Domain UC 的跨域依賴用「領域依賴」欄位標記（引用其他 UC ID）
- Workflow UC 的步驟引用 Domain UC ID（不重複描述能力細節）
- UC 不重複原則：同一行為只在一個 USE-CASES.md 定義

**Pipeline vs Workflow 區分**：
- **Pipeline** = 域內步驟編排（步驟全在同一 domain）。UC 放在該 domain 的 USE-CASES.md
- **Workflow** = 跨域流程編排（步驟跨越多個 domain）。UC 放在 `workflows/USE-CASES.md`
- 技術上可共用 Pipeline 基類（如 `common/pipeline.py:Pipeline`），區別在語意層面
- **域以程式碼目錄為準**：同一 `mosaic_alpha/` 子目錄視為同一域，不以外部系統邊界為準

**scripts/ 定位**：scripts/ 是 thin wrapper 層（CLI 入口），**不放 USE-CASES.md**。scripts/ 的 CLAUDE.md 作為導航索引，指向 library 模組的 USE-CASES.md。

### CLAUDE.md 與 USE-CASES.md 合作

兩者是同一領域的兩個正交視角，放在同一個模組目錄下讓 AI 在同一 context 中同時看到。

| 文件 | 職責 | 視角 |
|------|------|------|
| `CLAUDE.md` | 架構知識（怎麼做的 + 為什麼） | 縱切面 |
| `USE-CASES.md` | 能力索引（能做什麼 + 做了沒） | 橫切面 |

**銜接機制**：

1. **CLAUDE.md → USE-CASES.md 導航**：每個模組的 CLAUDE.md 包含「USE-CASES 導航」段落（UC ID → 實作位置對照表），讓 AI 從架構視角跳到能力視角
2. **USE-CASES.md → CLAUDE.md 引用**：UC 條目的實作路徑指向 CLAUDE.md 記錄的模組
3. **模組觸發器**：Root CLAUDE.md 的「模組觸發器」同時觸發 CLAUDE.md 和 USE-CASES.md

### Scenario Matrix：EP 規劃期的消費場景思考

> **核心原則**：EP 規劃時強制思考「使用者會遇到哪些情境」，避免實作完成才發現漏掉錯誤路徑或邊界案例。矩陣是 EP 的規劃工具，產出後提煉成 UC 的「消費場景」欄位。

**術語層級**（glossary）：
- **Scenario Matrix** = EP 中的 artifact（一個表格，規劃期產出，EP 完成後隨 EP 歸檔）
- **消費場景** = UC 的欄位名（自包含描述，永久保留在 USE-CASES.md）
- **場景** = Scenario Matrix 表格中的 column 概念（單一情境，如「每日例行」「錯誤操作」）

**為什麼放 EP 而非 /spec**：/spec 不一定每次都跑（小型/中型變更可能跳過），但 EP 是中大型變更的必經關卡，作為強制思考點覆蓋率更高。

**Scenario Matrix 格式**（EP 內的表格區段）：

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應 UC |
|---|------|------|---------|------------|---------|
| SM-1 | 每日例行 | launchd / 手動 | Full pipeline | 無（從頭算） | WF-01 |
| SM-2 | 改 ranking 重跑歷史 | 手動 --date | 讀 snapshot → Analysis → JSON | snapshot | WF-01（部分） |
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

**散到 UC 的「消費場景」欄位**：
EP 完成後，每個 UC 的「消費場景」欄位從矩陣提煉自包含描述（不引用 EP/SM 編號，因為 EP 可能歸檔或刪除）。例：SM-1/SM-2 → WF-01 的「消費場景」寫成「每日例行全 pipeline、改 ranking 用 --date 重跑歷史」。

### Command Pipeline 整合

```
/spec（含 UC 📋 定義）→ /execution-plan（引用 UC ID）→ [/ep-validate] → /build（更新 UC 狀態）
    → /code-review（驗證 UC 覆蓋度）→ /commit（確認 UC 狀態更新）→ /uc-status
```

| Command | UC 職責 |
|---------|--------|
| `/spec` | 啟動時掃描相關 **library 模組**的 USE-CASES.md；定義新 UC 或更新既有 UC |
| `/execution-plan` | EP 段落引用 UC ID（如「實作 D-31」）；大型/中型變更須產出 Scenario Matrix |
| `/build` | 段落完成後更新**同模組** USE-CASES.md 狀態（📋→✅）；從 EP Scenario Matrix 提煉「消費場景」寫入 UC；未完成段落內嵌細節 |
| `/code-review` | 第六軸：UC 覆蓋度（實作是否滿足 **library 模組目錄** USE-CASES.md 的 UC 描述） |
| `/commit` | 大型/中型變更時提示確認 UC 狀態更新 |
| `/standup` | UC 進度摘要（狀態變化、新增、關閉） |
| `/uc-status` | 全局進度掃描（掃描 **library 模組目錄**下所有 USE-CASES.md） |

### 文件放置

- `USE-CASES.md`：放在**主要實作所在的 library 模組目錄**（如 `mosaic_alpha/data/USE-CASES.md`），每個 UC 有唯一 ID
- `workflows/USE-CASES.md`：跨域 Workflow UC 的歸宿（如 `mosaic_alpha/workflows/USE-CASES.md`）
- **禁止放在 scripts/**：scripts/ 是 thin wrapper，不放 USE-CASES.md
- 全局進度：`/uc-status` 掃描 library 目錄下所有 USE-CASES.md

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
