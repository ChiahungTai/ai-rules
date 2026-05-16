---
description: "每日自動化 CLAUDE.md 維護 — compare-first：先比對再決定是否重建"
when_to_use: "Automated daily CLAUDE.md maintenance: compare source-docs against .py first, only rebuild when precision drops. Runs autonomously."
usage: "/claude:daily-maintain [--full] [--max-agents N] [--dry-run] [--modules a,b,c]"
argument-hint: "/claude:daily-maintain — compare-first 自動維護，--full 全模組審計（含 Layer D 基礎設施覆蓋）"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
---

# /claude:daily-maintain — 每日自動化 CLAUDE.md 維護（Compare-First）

你是 CLAUDE.md 知識管理自動化引擎。核心目標：**讓 CLAUDE.md 保持準確且完整**。

**核心理念 — Compare-First**：decode-compare（便宜）先跑，只有精度不足時才觸發 doc-decode（昂貴）。避免對新鮮的 source-docs 做無意義的重建。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

Autonomous execution: [autonomous-execution SKILL.md](../../skills/autonomous-execution/SKILL.md) — 夜間排程的決策框架：不問問題、所有判斷記錄在 morning report、Don't-Self-Decide Boundaries。

---

## 核心目標

**CLAUDE.md 持續演化**：不是寫完就過時的靜態文檔，而是隨程式碼演化的活知識庫。

**三層資料流**：

```
CLAUDE.md（理解框架 — 知道什麼重要）+ .py（程式碼真相 — 知道實際怎麼做）
  ↓ doc-decode（雙輸入：CLAUDE.md 定優先級，.py 提供真相）
source-docs/（詳細理解中間層 — 驗證層，非消費層）
  ↓ decode-compare 驗證 + 找缺口
CLAUDE.md（壓縮知識 — 最終目標，品質是唯一指標）
```

> **關鍵認知**：LLM 使用 CLAUDE.md 協助開發和分析，不會直接讀 source-docs。source-docs 是驗證中間層，存在目的是協助判斷 CLAUDE.md 品質。因此 doc-decode 必須從 CLAUDE.md 出發（知道什麼重要），再用 .py 驗證（確認是否準確），才能產出有意義的 source-docs。

這個三層架構的**真正目的**不是產出 source-docs，而是**反向驗證 CLAUDE.md 的完整性**。decode 把 CLAUDE.md 解壓回詳細理解，compare 找出 .py 中存在但 CLAUDE.md 沒 encode 的知識缺口。source-docs 是中間產物，CLAUDE.md Gap Report 才是目標。

**成本認知**：

| 操作 | 成本 | 說明 |
|------|------|------|
| decode-compare | **便宜** | 讀 source-docs + 對 .py 做 spot check，幾分鐘 |
| doc-decode | **昂貴** | 讀 CLAUDE.md + **所有** .py，寫完整 source-docs（200-900 行/模組），含驗證迴圈，十幾分鐘 |

因此 **compare 永遠先跑**。只有 compare 發現精度不足（source-docs 與 .py 差距大）才觸發 decode。

---

## 操作模式

| 模式 | Scope | Depth | 說明 |
|------|-------|-------|------|
| **Default** | 自上次執行後有變更的模組 | A/B/C | 快速日常維護 |
| **--full** | 全部模組 | A/B/C/D（含基礎設施覆蓋） | CLAUDE.md 完整性審計 |

**Scope 差異**（處理哪些模組）：
- Default：`git log {last_hash}..HEAD` 只看變更的 .py / CLAUDE.md
- --full：強制納入全部 16 個模組

**Depth 差異**（compare 幾層）：
- Default：A（架構）+ B（演算法）+ C（資料結構）
- --full：A + B + C + **D（基礎設施覆蓋）** — 跨模組 import 分析，找可複用基礎設施遺漏

**兩者都不強制重建 source-docs**。是否重建取決於 Phase 1 compare 的精度結果。

**Use Case 對照表**：

| # | 場景 | 判斷方式 | 該做什麼 |
|---|------|---------|---------|
| UC1 | 全新專案，無 source-docs | source-docs/ 不存在 | doc-decode（Phase 2）→ compare → CLAUDE.md |
| UC2 | 每日跑，有 .py 變更 | git log 偵測 | compare（Phase 1）→ 精度不足才 decode（Phase 2）|
| UC3 | source-docs 剛建好 | compare 全部 ✅ | 跳過 decode → CLAUDE.md 無需更新，只更新 .last-run |
| UC4 | 沒有任何變更 | git log 無新 commit | 全部跳過，只更新 .last-run |
| UC5 | 大重構後 / 需審計 | `--full` | 全模組 compare（含 Layer D）→ 條件 decode |
| UC6 | .py 被刪除 | git diff 偵測 | 清理 source-docs 引用 → compare |
| UC7 | 手動改了 CLAUDE.md | git log 偵測 | compare → 決定是否需要 decode |

**核心約束**：
- **CLAUDE.md 是關鍵資產**：每個修改都是獨立 Edit 操作（不是整檔重寫），確保 git diff 精確到行
- **autonomous-execution 模式**：夜間執行不問問題，所有決策記錄在 morning report
- **可追蹤性**：每個 CLAUDE.md 改動都附帶 compare 的具體發現作為理由

---

## 目錄結構

```
專案目錄/
├── source-docs/                    ← 理解文檔（doc-decode 產出）
│   ├── .last-run                   ← 上次執行時的 HEAD commit hash
│   ├── dependency-graph.md         ← 模組依賴知識圖譜
│   ├── rule_forge/
│   │   ├── overview.md
│   │   ├── condition-system.md
│   │   └── ...
│   └── indicators/
│       └── overview.md
├── ai-analysis/
│   └── daily-report/
│       └── 2026-05-09.md
└── mosaic_alpha/
    └── rule_forge/
        └── CLAUDE.md
```

---

## 執行流程

```
Phase 0: SCAN ─── 範圍偵測（哪些模組需要處理）
Phase 1: COMPARE ─ decode-compare（便宜，永遠先跑）
Phase 2: DECODE ── doc-decode（昂貴，精度不足時才觸發）
Phase 3: UPDATE ── CLAUDE.md 更新 + Morning Report
```

### Phase 0: SCAN — 範圍偵測

> **設計理念**：精確判斷哪些模組需要處理。用 commit hash（不是 wall clock）避免偵測到自己的文檔 commit。

```
0.1 模組發現
    fd -e py . mosaic_alpha/ --max-depth 2
    識別所有含 CLAUDE.md 或 .py 的模組目錄

0.2 讀取 .last-run（commit hash）

    從 source-docs/.last-run 讀取上次的 HEAD commit hash。

    Fallback 鏈（.last-run 不存在或格式不符時）：
    1. 嘗試解析為 commit hash → git rev-parse --verify "{value}"
    2. 失敗 → 視為首次執行，使用空字串（git log 從頭開始）
    3. 記錄「首次執行」到 morning report

    .last-run 格式（單行）：
    <40-char-sha>

    為什麼用 commit hash 而非 wall clock timestamp：
    - Wall clock 會偵測到自己的文檔 commit（在 run 開始後、commit 在 .last-run 寫入前）
    - Commit hash 精確標記「處理到哪裡」
    - git log {hash}..HEAD 是標準「找新 commit」語法
    - 代價：下次 run 會 re-compare 自己的文檔 commit（便宜，可接受）

0.3 變更偵測

    git log {last_hash}..HEAD --name-only --pretty=format:
    過濾 .py 和 CLAUDE.md，映射到模組目錄。

    映射規則（.py → 模組）：
    mosaic_alpha/rule_forge/engine.py → rule_forge
    mosaic_alpha/common/enums.py → common

    變更分類：

    | 變更類型 | 判斷方式 | Phase 1 處理 |
    |---------|---------|-------------|
    | .py 修改 | git diff 中有 ± 行 | 納入 compare |
    | .py 刪除 | git diff 中只有 - 行 | 清理引用 + 納入 compare |
    | .py 新增 | git diff 中只有 + 行 | 納入 compare（可能觸發 decode） |
    | CLAUDE.md 修改 | 路徑匹配 CLAUDE.md | 納入 compare |

0.4 .py 刪除 — source-docs 殘留清理
    對每個被刪除的 .py：
    rg "source:.*{deleted_file}" source-docs/{module}/
    → 移除對應的程式碼段落（獨立 Edit）
    → 若某子系統文件的所有 source 段落都來自已刪除檔案 → 標記需要 decode

0.5 CLAUDE.md 變更語義映射
    當模組有 CLAUDE.md 變更時（不論是否同時有 .py 變更）：

    git diff {last_hash}..HEAD -- {module}/CLAUDE.md
    對每個變更段落，識別語義類別：
    - 渲染描述變更、圖層映射變更、型別/參數變更
    - 設計決策新增/修正、模組結構變更

    映射到 source-docs 子系統：
    rg "{關鍵詞}" source-docs/{module}/ -l
    → 找到對應 → 該子系統納入 compare 重點

    核心邏輯：CLAUDE.md 變更是 source-docs 過時的領先指標。
    不直接決定 decode（交給 Phase 1 compare 判斷精度）。

0.6 source-docs dirty 偵測
    git diff --name-only source-docs/
    → 有 uncommitted changes → 跳過處理，記入 morning report 提醒

0.7 範圍判定

    | 模式 | in-scope 模組 |
    |------|-------------|
    | Default | 0.3 偵測到 .py 或 CLAUDE.md 變更的模組 + 無 source-docs 的模組 |
    | --full | 全部模組（強制納入，不論是否有變更） |

    無變更（Default + in-scope 為空）→ 跳到 Phase 3 只產出 minimal report

0.8 Agent 分配

    將 in-scope 模組平分給 --max-agents 個 agent（預設 4）。
    Compare（Phase 1）每模組 3-5 min，可並行。
    Decode（Phase 2）每模組 10-20 min，分配到不同 agent。

    ⚠️ 所有 Agent prompt 開頭必須加上 /rules-reminder 的六條規則摘要：
    `#` 是毒藥、`rg/fd` 取代 `grep/find`、`uv run` 是王道、`sed` 是地雷、管道拆兩步、繁體中文
```

---

### Phase 1: COMPARE — decode-compare（便宜，永遠先跑）

> **核心步驟**。對所有 in-scope 模組執行 decode-compare，產出精度報告和 ACTION items。精度決定是否需要 Phase 2 decode。

```
1.0 Quick Scan — 引用完整性（秒級）

    對每個 in-scope 模組：

    1.0.1 檔案引用驗證
        rg -o "source: ([\w/]+\.py):\d" source-docs/{module}/ --no-filename -r '$1' | sort -u
        對每個檔名，fd 確認存在。

    1.0.2 Class/Type 引用驗證
        rg -o "`([A-Z][A-Za-z]+)`.*`([\w/]+\.py):(\d+)`" source-docs/{module}/ --no-filename | sort -u
        對每個名稱，rg "class {Name}" 確認定義存在。

    1.0.3 CLAUDE.md 語義驗證（commit 驅動）
        對 in-scope 模組中 CLAUDE.md 有變更的模組，執行 sync 核心層：
        - 導航有效性：CLAUDE.md 引入的概念 → file.py:Class 指引是否存在
        - 程式碼一致性：CLAUDE.md 的檔案路徑、class/function 名稱是否仍正確
        - Signal/Noise Ratio：CLAUDE.md 是否包含可推導內容（API 簽名、參數表）

        發現問題 → 產出 ACTION items（導航缺口、語義不準確）
        保持輕量，不做品質層（--quality）或完整層（--all）。

    1.0.4 Quick Scan 結果
        全部 ✅ → 引用完整 + CLAUDE.md 同步
        有 ❌ → 定向 Edit 修正（獨立操作，記錄在 morning report）
        ❌ 數量多 → 標記模組為 needs decode（精度必然低）

1.1 Full Compare — source-docs vs .py（分鐘級）

    執行 decode-compare（預設模式）：

    | 模式 | 比對層級 | 說明 |
    |------|---------|------|
    | Default | A/B/C | 架構 + 演算法 + 資料結構 |
    | --full | A/B/C/D | 上述 + 基礎設施覆蓋（跨模組 import 分析）|

    A/B/C 三層比對（所有模式）：
    - 讀取 source-docs/{module}/ 的所有 .md
    - 比對對應 .py 實作
    - A 架構：模組結構、職責劃分、依賴關係
    - B 演算法：核心邏輯、計算流程、邊界處理
    - C 資料結構：型別定義、資料模型、序列化
    - 標記每項為 ✅ 正確 / ⚠️ 部分差異 / ❌ 理解錯誤 / 🔍 信息缺失

    Layer D 基礎設施覆蓋（--full 專用）：
    - 跨模組 import 分析：rg "from {module}(\.\w+)? import" mosaic_alpha/ -t py
    - 建立「實際被複用」清單（2+ 模組 import → 可複用基礎設施）
    - 比對 CLAUDE.md 的「可複用基礎設施」段落
    - 找出遺漏項：被 import 但 CLAUDE.md 沒記錄

1.2 計算精度

    A/B/C 三層精度：
    精度 = (✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%

    Layer D 精度（--full）：
    基礎設施覆蓋率 = 已記錄 / 實際被複用 × 100%

    按層級統計：
    | 層級 | ✅ | ⚠️ | ❌ | 🔍 | 精度 |
    |------|----|----|----|----|------|
    | A 架構 | | | | | X% |
    | B 演算法 | | | | | X% |
    | C 資料結構 | | | | | X% |
    | D 基礎設施（--full）| | | | | X% |

1.3 精度門檻 → 決定是否觸發 Phase 2

    | 精度 | 判定 | 動作 |
    |------|------|------|
    | ≥ 90% | ✅ 品質優良 | 不需要 decode，直接進 Phase 3 |
    | 70-89% | 🟡 可接受 | 標記建議改善，不觸發 decode |
    | < 70% | 🔴 需要重建 | 標記 needs decode，進 Phase 2 |
    | 無 source-docs | N/A | 強制進 Phase 2（首次 decode）|

    全部 ❌ 和 🔍 → 標記具體改善建議，附帶：
    - 影響層級（A/B/C/D）
    - 程式碼引用（file.py:行號）
    - 建議動作（在 CLAUDE.md 的哪裡加入什麼）

1.4 產出 ACTION items（Signal/Noise 過濾）

    | 信號等級 | 處理方式 | 說明 |
    |---------|---------|------|
    | High Signal | 自動套用（Phase 3 處理） | 導航缺口、行為描述錯誤、基礎設施遺漏 |
    | Medium Signal | 標記 ⚠️ 建議修改（morning report） | 語義修正、流程描述補充 |
    | Low Noise | 跳過 | API 簽名、參數值（從程式碼可推導） |

    ACTION 格式：
    ACTION N: [操作類型] [優先級]
    目標位置: CLAUDE.md [章節/行號]
    操作: [新增/修改]
    [可直接貼入的 CLAUDE.md 修改文字]
    信號等級: High/Medium | 驗證來源: file.py:行號

1.5 --full 專用：Gap Report

    當 --full 模式執行時，Phase 1 額外產出 CLAUDE.md Gap Report：

    1.5.1 知識缺口（來自 compare 的 🔍 信息缺失）
        .py 中存在的重要知識，但 CLAUDE.md 沒 encode：
        - 缺少的設計理由、架構約束、型別關係、Pipeline 編排、慣例映射

    1.5.2 基礎設施缺口（來自 Layer D）
        被 2+ 個模組使用但 CLAUDE.md 未記錄的 class/function：
        - 遺漏項、過時標記、缺少跨模組標記

    1.5.3 Gap Report 格式

        ## CLAUDE.md Gap Report — {module}

        ### 知識缺口（{N} 項）
        | 缺口類型 | 遺漏內容 | 來源 | 建議動作 |
        |---------|---------|------|---------|

        ### 基礎設施缺口（{N} 項）
        | 遺漏項 | 被使用次數 | 使用模組 | 建議動作 |
        |--------|----------|---------|---------|

        ### 精度摘要
        | 層級 | ✅ | ⚠️ | ❌ | 🔍 | 精度 |
        |------|----|----|----|----|------|
```

---

### Phase 2: DECODE — doc-decode（昂貴，條件觸發）

> **只有 Phase 1 精度 < 70% 或無 source-docs 時才執行**。這是最昂貴的操作，讀取 CLAUDE.md + 所有 .py，產出完整 source-docs。

```
2.0 觸發條件（Phase 1 判定）

    | 條件 | 動作 |
    |------|------|
    | 精度 ≥ 70% | 跳過 decode（Phase 1 的 ACTION items 已足夠） |
    | 精度 < 70% | 觸發 decode（source-docs 嚴重過時） |
    | 無 source-docs | 觸發 decode（首次建立） |
    | Quick Scan 大量引用斷裂 | 觸發 decode（結構性問題） |

2.1 CLAUDE.md 優先原則（強制）

    ⚠️ doc-decode 的輸入是 CLAUDE.md + .py，不是只有 .py。
    CLAUDE.md 提供「理解框架」（知道什麼重要），.py 提供「程式碼真相」（知道實際怎麼做）。

    每個 Phase 2 agent 啟動時，必須依序執行：

    S1: READ CLAUDE.md（強制第一步）
        1. 讀取目標模組的 CLAUDE.md
        2. 追蹤 @ 引用和 markdown link 引用的文檔
        3. 提取「理解框架」：
           - 模組定位和核心職責
           - 關鍵設計決策（為什麼這樣做）
           - 不可妥協的約束
           - CLAUDE.md 標注為重要的 class/function（導航目標）
        4. 提取「可複用基礎設施」清單：
           - CLAUDE.md 的「可複用基礎設施」段落列出的 class/function
           - 跨模組標記（**X 也繼承**、**跨模組 Protocol**）
        5. 建立記錄優先級清單：
           - CLAUDE.md 提到的設計決策 → source-docs 必須有完整支撐
           - CLAUDE.md 的導航指引 → source-docs 必須覆蓋對應 .py
           - CLAUDE.md 的可複用基礎設施 → source-docs 必須覆蓋
           - CLAUDE.md 未提及的 → source-docs 可選記錄

    S2: SCAN .py
        讀取全部 .py 檔案（不是只有變更的），比對 CLAUDE.md 的理解框架。

        S2a（--full 專用）：跨模組 import 分析
            搜尋其他模組中 import 本模組的 class/function：
            rg "from {module}(\.\w+)? import" mosaic_alpha/ -t py --no-filename -o

            建立「實際被複用」清單：
            - 出現在 2+ 個模組的 import → 確認為可複用基礎設施
            - 與 S1 提取的 CLAUDE.md 清單比對 → 找出遺漏

    S3: RECONSTRUCT source-docs
        基於 CLAUDE.md 的理解框架 + .py 的程式碼真相，更新 source-docs。

    Agent Prompt 模板：
    ┌────────────────────────────────────────────────────────────┐
    │ 1. 【強制】先讀取 {module}/CLAUDE.md 建立理解框架          │
    │    - 模組定位、設計決策、約束、導航目標                     │
    │    - 追蹤 @ 引用和 markdown link                           │
    │    - 提取「可複用基礎設施」清單和跨模組標記                 │
    │ 2. 讀取全部 .py 檔案                                       │
    │    - (--full) 執行跨模組 import 分析                       │
    │ 3. 讀取現有 source-docs                                    │
    │ 4. 以 CLAUDE.md 為優先級指引，更新 source-docs             │
    │ 5. Edit 更新 source-docs（不是整檔重寫）                   │
    └────────────────────────────────────────────────────────────┘

2.2 啟動 Agent Pool
    按 --max-agents N 啟動 N 個 agent，每個遵循 §2.1 模板。

2.3 decode 後驗證
    對每個 decoded 模組執行 decode-compare（A/B/C 三層），確認重建品質。
    精度仍 < 70% → 標記 ⚠️ 記錄在 morning report（不重試 decode）。

2.4 更新 ACTION items
    基於 decode 後的 compare 結果，更新 ACTION items。
```

---

### Phase 3: UPDATE + REPORT — CLAUDE.md 更新 + 日報

> **CLAUDE.md 是最終目標**。根據 Phase 1/2 的 ACTION items 更新 CLAUDE.md，產出 morning report，寫入 .last-run。

```
3.1 CLAUDE.md 更新

    3.1.1 合併 ACTION items
        來源：Phase 1 compare（+ Phase 2 decode 後驗證）
        分類：High Signal（自動套用）+ Medium Signal（建議）

    3.1.2 修改分類（安全邊界）

        ✅ 可以自動修改：
        - 修正過時描述（程式碼已變更但描述未更新）
        - 補充型別關係（相似型別的用途區別）
        - 修正引用語法（@ vs [描述](path)）
        - 更新 pipeline 編排描述
        - 移除可推導內容（API 簽名、參數表）
        - 更新模組職責描述（與實際 .py 對齊）
        - 補充「可複用基礎設施」遺漏項（Layer D 發現的缺口，加一句話描述）
        - 補充跨模組標記（**X 也繼承**、**跨模組 Protocol**）

        ⚠️ 只建議不自動修改（標記在 morning report）：
        - 新增「設計理由」段落
        - 新增「失敗教訓」規則
        - 刪除現有「原則」或「約束」段落
        - 修改架構約束描述
        - 任何涉及「為什麼這樣做」的內容

    3.1.3 逐項執行 Edit
        對每個 ✅ 項目：
        - Read CLAUDE.md 取得當前內容
        - Edit 精確替換（不是整檔重寫）
        - 記錄修改理由（來自 Phase 1/2 的哪個 ACTION）

    3.1.4 Decoder Test 驗證
        修改完成後，對每個更新的 CLAUDE.md 執行 dry run Decoder Test：
        1. 這個模組的核心職責是什麼？
        2. 關鍵的設計決策和理由是什麼？
        3. 有哪些不可妥協的約束？
        4. 模組邊界在哪裡（不做什麼）？
        全部通過 → 完成
        有失敗 → 標記 ⚠️，記錄在 morning report

3.2 一致性檢查

    對每個更新的 CLAUDE.md：
    - 術語一致性、章節結構、引用完整性、前後邏輯、格式規範
    - 格式問題直接修正，邏輯問題標記 ⚠️。

3.3 Morning Report

    3.3.1 寫入 ai-analysis/daily-report/{YYYY-MM-DD}.md
    3.3.2 同時 print 到對話（精簡版）

    3.3.3 問題分類（⚠️ 未解決問題）

        每個未解決問題必須標注修復方式：

        | 修復方式 | 適用情境 | 實際動作 |
        |---------|---------|---------|
        | CLAUDE.md 定向修正 | 導航缺口、過時描述 | 直接 Edit CLAUDE.md |
        | source-docs 定向修正 | 引用斷裂、已刪除檔案引用 | 直接 Edit source-docs |
        | 自動 decode | 精度 < 70% | 下次執行時 Phase 2 自動處理 |
        | --full | 大重構後 | 全部重建 |

    3.3.4 --full 專用：Gap Report 摘要
        當 --full 模式執行時，morning report 必須包含：
        1. 各模組的 Gap Report 摘要（知識缺口 + 基礎設施缺口）
        2. 整體 CLAUDE.md 覆蓋度評分（各層級精度）
        3. 建議的 CLAUDE.md 更新項目（含優先級）
        4. 跨模組重複造輪子風險

    3.3.5 耗時記錄
        記錄各 Phase 的執行時間：
        - Phase 0 SCAN: Xs
        - Phase 1 COMPARE: Xs（每模組）
        - Phase 2 DECODE: Xs（每模組，若觸發）
        - Phase 3 UPDATE + REPORT: Xs
        - **總計**: Xs

3.4 寫入 .last-run

    寫入 source-docs/.last-run = 當前 HEAD commit hash（不是 wall clock）。

    git rev-parse HEAD > source-docs/.last-run

    為什麼在最後寫入：
    - 確保所有處理（包括 CLAUDE.md commit）都完成
    - 下次 run 的 git log {hash}..HEAD 不會漏掉任何 commit
    - 即使 run 過程中產生了文檔 commit，下次 compare 也是便宜操作
```

#### Morning Report 格式

Morning report 格式模板：[morning-report-template.md](./_common/morning-report-template.md)

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | Compare-first：掃描變更模組 → compare → 條件 decode → morning report |
| **--full** | 全模組 compare（A/B/C/D）→ 條件 decode → Gap Report → morning report |
| **--max-agents N** | 平行 agent 上限（預設 4） |
| **--dry-run** | 只產出 Phase 0 計劃，不實際執行 |
| **--modules a,b,c** | 只處理指定模組（除錯用） |

---

## 與其他 Command 的關係

| Command | 在 daily-maintain 中的角色 |
|---------|--------------------------|
| `/claude:decode-compare` | Phase 1：compare source-docs vs .py（便宜，永遠先跑） |
| `/claude:doc-decode` | Phase 2：重建 source-docs（昂貴，精度不足時才觸發） |
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
  - compare 精度 < 50% → 重試一次 compare
  - decode 後驗證仍 < 70% → 標記 ⚠️，不重試 decode
  - 連續 3 次失敗 → 標記 ⚠️，繼續下一個模組
- **Completion Report**：即 morning report

### 安全機制

- **每個 CLAUDE.md 修改都是獨立 Edit**：git diff 精確到行
- **執行前確認 working tree clean**：確保可 rollback
- **修改理由追蹤**：每個 Edit 附帶 compare 的具體發現
- **Decoder Test 驗證**：修改後自動驗證品質

### 比例化深度標準

每個子系統文檔必須達到：

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

未達標 → 回到 Phase 2 補讀，禁止以「已足夠」為由跳過。

### 強制子系統拆分

```
觸發條件：模組 .py > 8
拆分策略：按 import 叢集分組（不是按檔案數均分）
輸出：每個子系統獨立文檔 + overview.md
```

---

## 使用範例

```bash
# 每日：compare-first 自動維護（預設，5-15 min 無變更 / 30-60 min 有變更）
/claude:daily-maintain

# CLAUDE.md 完整性審計（全模組 A/B/C/D，含基礎設施覆蓋）
/claude:daily-maintain --full

# 只審計特定模組
/claude:daily-maintain --full --modules rule_forge

# 只看計劃不執行
/claude:daily-maintain --dry-run
```

---

## 與 /loop 排程整合

```bash
# 每日：compare-first（預設）
/loop /claude:daily-maintain

用戶起床後：
1. 查看 ai-analysis/daily-report/{date}.md
2. git diff 檢查 CLAUDE.md 變更
3. 確認 ⚠️ 建議修改項目
```

---

> **維護哲學**: Compare-First。先跑便宜的 decode-compare 確認現狀，只有精度不足才觸發昂貴的 doc-decode 重建。Default 處理變更模組（A/B/C），--full 處理全部模組（A/B/C/D + Gap Report）。兩者都不強制重建 — 交給精度門檻決定。`.last-run` 記錄 commit hash 不是 wall clock，精確標記處理進度。
