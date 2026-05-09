---
description: "每日自動化 CLAUDE.md 維護 — 增量偵測變更、重建理解文檔、更新 CLAUDE.md、產出 morning report"
usage: "/claude:daily-maintain [--full] [--ripple] [--max-agents N] [--dry-run] [--modules a,b,c]"
argument-hint: "/claude:daily-maintain — 自動偵測模式（有 source-docs/ → incremental，無 → full）"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
permission-mode: "acceptEdits"
---

# /claude:daily-maintain — 每日自動化 CLAUDE.md 維護

你是 CLAUDE.md 知識管理自動化引擎，負責在夜間排程中增量偵測程式碼變更、重建理解文檔、更新 CLAUDE.md，並產出 morning report 供用戶起床後 review。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

Autonomous execution: [autonomous-execution SKILL.md](../../skills/autonomous-execution/SKILL.md) — 讀取此檔案以理解夜間自主執行的決策框架。

---

## 核心目標

**讓 CLAUDE.md 活著**：不是寫完就過時的靜態文檔，而是隨程式碼演化的活知識庫。

**操作模式**：

| 模式 | 觸發條件 | 行為 |
|------|---------|------|
| **Full Rebuild** | `source-docs/{module}/` 不存在，或 `--full` | 全部模組完整 decode + compare + update |
| **Daily Incremental** | `source-docs/` 已存在，有 git 變更 | 只處理受影響的模組和子系統 |

**核心約束**：
- **CLAUDE.md 是關鍵資產**：每個修改都是獨立 Edit 操作（不是整檔重寫），確保 git diff 精確到行
- **autonomous-execution 模式**：夜間執行不問問題，所有決策記錄在 morning report
- **可追蹤性**：每個 CLAUDE.md 改動都附帶 sync 或 decode-compare 的具體發現作為理由

---

## 目錄結構

```
專案目錄/
├── source-docs/                    ← 理解文檔（doc-decode 產出）
│   ├── dependency-graph.md         ← 模組依賴知識圖譜
│   ├── rule_forge/
│   │   ├── overview.md
│   │   ├── condition-system.md
│   │   └── ...
│   └── indicators/
│       └── overview.md
├── ai-analysis/
│   └── daily-report/
│       ├── 2026-05-08.md
│       └── 2026-05-09.md
└── mosaic_alpha/
    └── rule_forge/
        └── CLAUDE.md
```

---

## 執行流程（7 Phases）

### Phase 0: COMPLEXITY SCAN — 模組掃描與 Agent 分配

> **設計理念**：兩階段執行策略 — 先掃描複雜度再分配 agent。

```
0.1 模組發現
    fd -e py . mosaic_alpha/ --max-depth 2
    識別所有含 CLAUDE.md 或 .py 的模組目錄

0.2 模組分類（每個模組）
    統計：
    - .py 檔案數量
    - 核心演算法函數數量（有非 trivial 邏輯的 def）
    - 既有的 source-docs 子系統數

    分類標準：
    | 分類 | .py 數 | 核心演算法 | 子系統 |
    |------|--------|-----------|--------|
    | large | > 8 | > 15 | > 2 |
    | medium | 4-8 | 5-15 | 1-2 |
    | small | < 4 | < 5 | 0-1 |

0.3 Agent 分配策略

    分配規則：
    | 模組類型 | Agent 配額 |
    |---------|-----------|
    | large | 1 agent 專用 |
    | medium | 2 模組共用 1 agent |
    | small | 3 模組共用 1 agent |

    單 agent 最大負載：不超過 800 行核心演算法
    超出時：優先拆分 large 模組為子系統（強制子系統拆分）

    若 --max-agents N：
    - 按 N 調整分配（N=4 → 最多 4 agent 並行）
    - 多餘模組排隊等候

0.4 模式偵測

    if --full → 全部模組標記 "needs full decode"
    elif source-docs/ 不存在 → 全部模組標記 "needs full decode"
    else → 進入 Phase 0.5（增量偵測）

    輸出：Agent 分配表 + 模組處理清單
```

### Phase 0.5: CHANGE DETECTION — 增量變更偵測

> **僅 Daily Incremental 模式執行**。Full Rebuild 跳過。

```
0.5.1 讀取上次執行時間
    從 source-docs/.last-run 讀取（無則用 git log -1 --format=%ci）

0.5.2 Git 變更偵測
    git log --since="$LAST_RUN" --name-only --pretty=format:
    過濾 .py 檔案，映射到所屬模組

    映射規則：
    mosaic_alpha/rule_forge/engine.py → rule_forge
    mosaic_alpha/common/enums.py → common
    mosaic_alpha/rule_forge/types.py → rule_forge

0.5.3 比對既有 source-docs
    對每個受影響模組：
    - 讀 source-docs/{module}/overview.md 的子系統清單
    - 比對 git 變更的 .py 屬於哪個子系統
    - 標記需要重建的子系統

    輸出：受影響模組清單 + 受影響子系統清單
```

### Phase 0.7: RIPPLE ANALYSIS — 連鎖影響偵測（--ripple 模式）

> **僅 --ripple 模式執行**。需要 `source-docs/dependency-graph.md` 存在。

```
0.7.1 讀取 dependency-graph.md
    取得 Semantic Dependencies 表和 Ripple Impact Rules

0.7.2 逐檔精細分析

    對每個 git 變更的 .py：
    git diff HEAD~{n}..HEAD -- {file_path}

    讀取 diff 內容，分類變更類型：

    | 變更類型 | 判斷方式 | 影響等級 | Ripple 範圍 |
    |---------|---------|---------|------------|
    | 新增 class/function | +^class / +^def | 低 | 僅同模組 |
    | 新增 import 行 | +^from / +^import | 中 | 被 import 的模組 |
    | 修改函數 signature | -def... → +def... 參數不同 | 高 | 所有 import 此函數的模組 |
    | 修改 dataclass 欄位 | class 內 +- 欄位 | 高 | 同上 |
    | 修改 Enum 值 | enum class 內 +- 成員 | 高 | 所有使用此 Enum 的模組 |
    | 修改演算法邏輯 | 函數內部改動但 signature 不變 | 中 | 同模組子系統 |
    | 刪除 class/function | -^class / -^def | 極高 | 全部下游 |
    | YAML 定義變更 | +/-.yaml 內容 | 中 | 對應子系統 |

0.7.3 交叉比對 dependency graph
    對每個 HIGH/極高 影響的變更：
    - 查詢 dependency-graph.md 的「被依賴」欄
    - 將受影響的下游模組加入處理清單

0.7.4 產出 ripple 報告
    ```
    Ripple Impact Analysis:
    rule_forge/types.py — ConditionFilter 新增欄位 [HIGH]
      → analytics (imports ConditionFilter) [新增至處理清單]
      → engine (imports ConditionFilter) [新增至處理清單]
    common/enums.py — Interval 新增 "2h" [HIGH]
      → indicators (uses Interval) [新增至處理清單]
      → features (uses Interval) [新增至處理清單]
      → datasets (uses Interval) [新增至處理清單]
    ```

    輸出：擴展後的受影響模組清單（嵌入 morning report）
```

### Phase 1: SYNC — 同步性檢查

```
1.1 對每個受影響模組執行 sync 邏輯（帶 --changed-since $LAST_RUN）
    讀取 CLAUDE.md + 對應 .py
    9 角度檢查（code consistency, coverage, metadata, distillation, internal quality, signal/noise, reference syntax, consumer chain, navigation effectiveness）

1.2 收集不一致
    每項標記：
    - type: outdated_description / missing_reference / metadata / ...
    - location: CLAUDE.md:行號
    - detail: 具體差異
    - confidence: high / medium
    - source: file.py:行號（程式碼證據）

1.3 輸出 Sync Report（兩層）
    Layer 1: 完整報告（人類可讀，嵌入 morning report）
    Layer 2: Sync Summary（結論摘要，供 Phase 4 消費）
```

### Phase 2: DOC-DECODE — 理解文檔重建

> **核心步驟**。按 Phase 0 分配啟動 parallel agents。

```
2.1 啟動 Agent Pool
    按 --max-agents N 啟動 N 個 agent

    Agent 分配策略：
    | 模組類型 | Agent 配額 | 內部策略 |
    |---------|-----------|---------|
    | large | 1 agent 專用 | 內部拆子系統，逐系統 decode |
    | medium | 2 模組/agent | 一次 decode 整個模組 |
    | small | 3 模組/agent | 一次 decode 整個模組 |

2.2 每個 Agent 執行 doc-decode --source-aided 邏輯

    遵循 doc-decode.md 的完整流程（S1→S2→S3）。
    品質標準見執行約束（比例化深度標準、強制子系統拆分、覆蓋清單）。

2.3 寫入 source-docs/
    模組文檔 → source-docs/{module}/
    知識圖譜 → source-docs/dependency-graph.md（僅 --full 時重建）

2.4 更新 .last-run
    寫入 source-docs/.last-run = 當前時間戳
```

### Phase 3: DECODE-COMPARE — 精度驗證

```
3.1 對每個重建的模組執行 decode-compare 邏輯
    讀取 source-docs/{module}/ 的 pseudo code
    比對對應 .py 實作

3.2 計算精度
    精度 = (✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%

    按層級統計：
    | 層級 | ✅ | ⚠️ | ❌ | 🔍 | 精度 |
    |------|----|----|----|----|------|
    | A 架構 | | | | | X% |
    | B 演算法 | | | | | X% |
    | C 資料結構 | | | | | X% |

3.3 識別 CLAUDE.md 改善點（遵循 decode-compare §精度門檻自動標記）
    精度 ≥ 90% → ✅ 品質優良，無需動作
    精度 70-89% → 🟡 可接受，建議改善
    精度 < 70% → 🔴 需要更新 CLAUDE.md
    全部 ❌ 和 🔍 → 標記具體改善建議
    每項附帶：
    - 影響層級（A/B/C）
    - 程式碼引用（file.py:行號）
    - 建議動作（在 CLAUDE.md 的哪裡加入什麼）
```

### Phase 4: CLAUDE.md UPDATE — 知識更新

> **核心安全機制**：每個修改都是獨立 Edit 操作，git diff 精確到行。

```
4.1 合併改善來源
    Phase 1（sync 不一致）+ Phase 3（decode-compare 缺口）
    → 統一改善清單

4.2 修改分類（安全邊界）

    ✅ 可以自動修改：
    - 修正過時描述（程式碼已變更但描述未更新）
    - 補充型別關係（相似型別的用途區別）
    - 修正引用語法（@ vs [描述](path)）
    - 更新 pipeline 編排描述
    - 移除可推導內容（API 簽名、參數表）
    - 更新模組職責描述（與實際 .py 對齊）

    ⚠️ 只建議不自動修改（標記在 morning report）：
    - 新增「設計理由」段落
    - 新增「失敗教訓」規則
    - 刪除現有「原則」或「約束」段落
    - 修改架構約束描述
    - 任何涉及「為什麼這樣做」的內容

4.3 逐項執行 Edit
    對每個 ✅ 項目：
    - Read CLAUDE.md 取得當前內容
    - Edit 精確替換（不是整檔重寫）
    - 記錄修改理由（來自哪個 phase 的哪個發現）

4.4 Decoder Test 驗證
    修改完成後，對每個更新的 CLAUDE.md 執行 dry run Decoder Test：
    1. 這個模組的核心職責是什麼？
    2. 關鍵的設計決策和理由是什麼？
    3. 有哪些不可妥協的約束？
    4. 模組邊界在哪裡（不做什麼）？
    全部通過 → 完成
    有失敗 → 標記 ⚠️，記錄在 morning report
```

### Phase 5: CONSISTENCY CHECK — 自洽性驗證

```
5.1 對每個更新的 CLAUDE.md 執行 /consistency 邏輯
    - 術語一致性
    - 章節結構
    - 引用完整性
    - 前後邏輯
    - 格式規範

5.2 修正發現的問題
    格式問題可以直接修正
    邏輯問題標記 ⚠️
```

### Phase 6: MORNING REPORT — 日報產出

```
6.1 寫入 ai-analysis/daily-report/{YYYY-MM-DD}.md
6.2 同時 print 到對話（精簡版）

報告格式：
```

```markdown
# Morning Report — {YYYY-MM-DD}

**執行模式**: Daily Incremental / Full Rebuild
**執行時間**: {start} → {end}（耗時 {duration}）
**處理模組**: N 個（{模組列表}）

---

## 處理摘要

| 模組 | 類型 | Phase 1 Sync | Phase 2 Decode | Phase 3 精度 | Phase 4 更新 |
|------|------|-------------|---------------|-------------|-------------|
| rule_forge | large | 3 issues | 6 files | 87% | 5 edits |
| indicators | medium | 1 issue | 2 files | 92% | 2 edits |

## CLAUDE.md 變更摘要

### ✅ 自動修改（{N} 項）

| 模組 | CLAUDE.md 位置 | 修改類型 | 來源 | 修改摘要 |
|------|---------------|---------|------|---------|
| rule_forge | :45 | 過時描述更新 | sync:rule_forge/engine.py:122 | Pipeline v2 描述更新 |
| rule_forge | :78 | 補充型別關係 | compare:types.py:56 | ConditionFilter vs ObservationFilter 區別 |

### ⚠️ 建議修改（{N} 項）— 需要您確認

| # | 模組 | CLAUDE.md 位置 | 建議 | 理由 | 來源 |
|---|------|---------------|------|------|------|
| 1 | rule_forge | (新增) | 新增「FilterTree 的 sequential greedy 設計理由」 | decode-compare 發現此為非顯而易見的設計決策 | compare:sequential_greedy.py:45 |

## Ripple Impact（--ripple 模式）

{Phase 0.7 的 ripple 報告}

## Phase 1: Sync 詳細發現

{Phase 1 的完整報告}

## Phase 3: Decode-Compare 精度報告

{每個模組的精度總覽表}

## Decoder Test 結果

| 模組 | 職責 | 設計決策 | 約束 | 邊界 | 通過 |
|------|------|---------|------|------|------|
| rule_forge | ✅ | ✅ | ✅ | ✅ | ✅ |
| indicators | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |

## ⚠️ 未解決問題

| # | 問題 | 嚴重性 | 建議動作 |
|---|------|--------|---------|
| 1 | indicators CLAUDE.md 缺少 overflow 檢查的約束描述 | 中 | 手動補充設計理由 |

## 下次建議

- {根據本次發現的改善建議}
```

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 自動偵測模式：有 source-docs/ → incremental，無 → full |
| **--full** | 強制全部重建（忽略 source-docs/ 狀態） |
| **--ripple** | 啟用連鎖影響偵測（需要 dependency-graph.md） |
| **--max-agents N** | 平行 agent 上限（預設 4，避免 rate limit） |
| **--dry-run** | 只產出 Phase 0 計劃，不實際執行 |
| **--modules a,b,c** | 只處理指定模組（除錯用） |

---

## 與其他 Command 的關係

| Command | 在 daily-maintain 中的角色 |
|---------|--------------------------|
| `/claude:sync` | Phase 1：偵測文檔-程式碼不一致 |
| `/claude:doc-decode --source-aided` | Phase 2：重建理解文檔 |
| `/claude:decode-compare` | Phase 3：驗證編碼精度 |
| `/consistency` | Phase 5：驗證 CLAUDE.md 自洽性 |
| `/claude:clean` | **不屬於 daily workflow** — 特殊處理工具 |
| `/claude:distill` | **不屬於 daily workflow** — 特殊處理工具 |

---

## 執行約束

### autonomous-execution 模式

本命令預設以 autonomous-execution 模式運行（夜間排程）：

- **不問問題**：所有決策記錄在 morning report
- **Don't-Self-Decide Boundaries**：
  - 不刪除 CLAUDE.md 的任何「原則」或「約束」段落
  - 不新增「設計理由」段落（只建議）
  - 不修改架構約束描述
- **Error Self-Healing**：
  - decode-compare 精度 < 50% → 重試一次
  - 連續 3 次失敗 → 標記 ⚠️，繼續下一個模組
- **Completion Report**：即 morning report

### 安全機制

- **每個 CLAUDE.md 修改都是獨立 Edit**：git diff 精確到行
- **執行前 git stash 或 commit**：確保可 rollback
- **修改理由追蹤**：每個 Edit 附帶 sync/compare 的具體發現
- **Decoder Test 驗證**：修改後自動驗證品質

### 比例化深度標準

每個子系統文檔必須達到：

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

未達標 → 回到 S2 補讀，禁止以「已足夠」為由跳過。

### 強制子系統拆分

```
觸發條件：模組 .py > 8
拆分策略：按 import 叢集分組（不是按檔案數均分）
輸出：每個子系統獨立文檔 + overview.md
```

### Agent 分配策略

```
large 模組（>8 .py）：1 agent 專用
medium 模組（4-8 .py）：2 模組/agent
small 模組（<4 .py）：3 模組/agent
單 agent 最大負載：800 行核心演算法
```

---

## 使用範例

```bash
/claude:daily-maintain
/claude:daily-maintain --full
/claude:daily-maintain --ripple --max-agents 6
/claude:daily-maintain --dry-run
/claude:daily-maintain --modules rule_forge,indicators
```

---

## 與 /loop 排程整合

```bash
/loop /claude:daily-maintain --ripple

排程建議：每日凌晨 1:00 執行
用戶起床後：
1. 查看 ai-analysis/daily-report/{date}.md
2. git diff 檢查 CLAUDE.md 變更
3. 確認 ⚠️ 建議修改項目
```

---

> **維護哲學**: CLAUDE.md 的價值在於持續演化。daily-maintain 不是「一次寫完」的工具，而是「每天保持最新」的知識管理系統。品質由比例化標準保證，安全由 git diff + morning report 保證，效率由增量偵測 + parallel agents 保證。
