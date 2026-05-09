---
description: "每日自動化 CLAUDE.md 維護 — 掃描、修正、重建、驗證、產出 morning report"
usage: "/claude:daily-maintain [--full] [--max-agents N] [--dry-run] [--modules a,b,c]"
argument-hint: "/claude:daily-maintain — 自動掃描修正全部模組，--full 強制全部重建 source-docs"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
permission-mode: "acceptEdits"
---

# /claude:daily-maintain — 每日自動化 CLAUDE.md 維護

你是 CLAUDE.md 知識管理自動化引擎。核心目標：**讓 CLAUDE.md 保持準確**。透過 source-docs 中間層驗證文檔品質，自動修正過時描述，產出 morning report 供用戶 review。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

Autonomous execution: [autonomous-execution SKILL.md](../../skills/autonomous-execution/SKILL.md) — 讀取此檔案以理解夜間自主執行的決策框架。

---

## 核心目標

**讓 CLAUDE.md 活著**：不是寫完就過時的靜態文檔，而是隨程式碼演化的活知識庫。

**三層資料流**：

```
.py（程式碼真相）
  ↓ doc-decode
source-docs/（詳細理解中間層）
  ↓ decode-compare 驗證 + 找缺口
CLAUDE.md（壓縮知識 — 最終目標）
```

**操作模式**：

| 模式 | 觸發條件 | 行為 |
|------|---------|------|
| **Default** | 預設（無參數） | 掃描全部模組 → 定向修正（source-docs + CLAUDE.md）→ 重建過時模組 → morning report |
| **Full Rebuild** | `--full` | 全部模組強制重建 source-docs + Full Compare + update |

**Use Case 對照表**：

| # | 場景 | 判斷方式 | 該做什麼 |
|---|------|---------|---------|
| UC1 | 全新專案，無 source-docs | source-docs/ 不存在 | Full doc-decode → verify → CLAUDE.md |
| UC2 | 每日跑，有 .py 變更 | source-docs 過時 | 自動重建受影響 source-docs → verify → CLAUDE.md |
| UC3 | source-docs 剛建好 | source-docs 新鮮 | 定向修正（不重建）→ verify → CLAUDE.md |
| UC4 | 沒有任何變更 | 全部新鮮 + 無新 commits | 全部跳過，只更新 .last-run |
| UC5 | 大重構後 | `--full` | 全部模組重建 source-docs |
| UC6 | .py 被刪除 | git diff 偵測 | 清理 source-docs 引用 → verify → CLAUDE.md |
| UC7 | 手動改了 CLAUDE.md | 只有 CLAUDE.md diff | 定向修正 source-docs（反向同步） |

**核心約束**：
- **CLAUDE.md 是關鍵資產**：每個修改都是獨立 Edit 操作（不是整檔重寫），確保 git diff 精確到行
- **autonomous-execution 模式**：夜間執行不問問題，所有決策記錄在 morning report
- **可追蹤性**：每個 CLAUDE.md 改動都附帶 decode-compare 的具體發現作為理由

---

## 目錄結構

```
專案目錄/
├── source-docs/                    ← 理解文檔（doc-decode 產出）
│   ├── .last-run                   ← 上次執行時間戳
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

### Phase 0: SCAN — 模組掃描 + 新鮮度檢查 + 決策樹

> **設計理念**：先判斷每個模組需要做什麼，再分配 agent。避免對新鮮的 source-docs 做無意義的重建。

```
0.1 模組發現
    fd -e py . mosaic_alpha/ --max-depth 2
    識別所有含 CLAUDE.md 或 .py 的模組目錄

0.2 新鮮度檢查（每個有 source-docs 的模組）

    對每個模組，比較 source-docs 和 .py 的最後修改時間。
    使用 epoch timestamp（%at）確保數值比較可靠，避免 ISO 字串比較問題。

    source_doc_ts = git log -1 --format="%at" -- "source-docs/mosaic_alpha/{module}/"
    py_ts = git log -1 --format="%at" -- "mosaic_alpha/{module}/"

    注意：必須只看 .py 檔案（不含 CLAUDE.md），否則文檔 commit 會干擾判斷。

    if source_doc_ts >= py_ts → FRESH（source-docs 比 .py 新）
    else → STALE（source-docs 比 .py 舊，需要重建）

    commit 級別比較即可，不需要行級別精確。

0.3 變更偵測（.py + CLAUDE.md）

    0.3.1 讀取上次執行時間
        從 source-docs/.last-run 讀取

        Fallback 鏈（.last-run 不存在時）：
        1. 當日 commits → git log --since="YYYY-MM-DD 00:00:00"
           - 有當日 commits → 使用當日第一筆 commit 時間戳作為 LAST_RUN
           - 記錄「首次執行（偵測到 N 筆當日 commits）」
        2. 無當日 commits → 報告「首次執行，無當日變更」
           → 只執行 Phase 3（Morning Report）+ 寫入 .last-run
           → 不觸發 Phase 1-2

    0.3.2 Git 變更偵測（.py + CLAUDE.md）
        git log --since="$LAST_RUN" --name-only --pretty=format:
        過濾 .py 和 CLAUDE.md，分類變更

        變更分類：

        | 變更類型 | 判斷方式 | 處理策略 |
        |---------|---------|---------|
        | .py 修改 | git diff 中有 ± 行 | 子系統級重建 |
        | .py 刪除 | git diff 中只有 - 行 | 清理 source-docs 殘留引用 |
        | .py 新增 | git diff 中只有 + 行 | 全模組重建 |
        | CLAUDE.md 修改 | 路徑匹配 CLAUDE.md | 定向修正 source-docs（反向同步） |

        映射規則（.py → 模組）：
        mosaic_alpha/rule_forge/engine.py → rule_forge
        mosaic_alpha/common/enums.py → common

    0.3.3 .py 修改 — 子系統級偵測
        對每個受影響模組：
        - 讀 source-docs/{module}/overview.md 的子系統清單
        - 比對 git 變更的 .py 屬於哪個子系統
        - 標記需要重建的子系統

    0.3.4 .py 刪除 — source-docs 殘留清理
        對每個被刪除的 .py：
        rg "source:.*{deleted_file}" source-docs/{module}/
        → 移除對應的程式碼段落（獨立 Edit，git diff 精確到行）
        → 若某子系統文件的所有 source 段落都來自已刪除檔案 → 標記過時

    0.3.5 .py 新增 — 全模組重建
        新增 .py 改變模組結構（import 圖可能改變）
        → 該模組標記 "needs full decode"（不做子系統級判斷）

    0.3.6 CLAUDE.md 修改 — 反向同步
        當模組只有 CLAUDE.md 變更、無 .py 變更時：
        - 標記為 "claude-md-only change"
        - 不觸發 doc-decode（.py 沒變，逐字抄錄段落仍正確）
        - 改用定向修正：讀 CLAUDE.md diff → 更新 source-docs 對應段落
          - 設計決策新增/修正 → 更新 source-docs 的「設計決策記錄」段落
          - 描述修正 → 更新 source-docs 中對應描述
          - 結構重組（少見）→ 降級為全模組重建

    0.3.7 source-docs dirty 偵測
        git diff --name-only source-docs/
        → 有 uncommitted changes 的檔案 → 跳過處理，記入 morning report 提醒

0.4 決策樹

    if --full → 全部模組標記 "needs full decode"（不管新鮮度，全部重建 source-docs）

    else:（預設 — 全自動）
      對每個模組，根據新鮮度自動選擇處理方式：

      | 新鮮度 | 處理方式 |
      |--------|---------|
      | 過時（source-docs 比 .py 舊） | 重建 source-docs（doc-decode）→ Full Compare |
      | 新鮮（source-docs 比 .py 新） | 定向修正（Quick Scan + sync）→ 不重建 |
      | 無 source-docs | Full doc-decode → Full Compare |
      | Quick Scan 發現引用斷裂 | 定向 Edit 修正 source-docs（不重建） |
      | Sync 發現 CLAUDE.md 過時 | 定向 Edit 修正 CLAUDE.md |

0.5 Agent 分配

    簡化策略：將需要處理的模組平分給 --max-agents 個 agent。
    預設 max-agents = 4。

    分配原則：
    - Quick Scan 模組全部在主線程執行（輕量，不需要 agent）
    - CLAUDE.md sync 模組（Phase 0.6）分配給 agent（每模組 3-5 min，可並行）
    - Full Compare 模組分配給 agent（每模組 10-20 min，需要並行）
    - 需要 full decode 的模組（較重）分配到不同 agent
    - 單 agent 一次處理 1-3 個模組

    輸出：Agent 分配表 + 每個模組的決策（skip / quick / rebuild / full-compare）
```

### Phase 0.5: QUICK SCAN — source-docs 引用完整性（預設執行）

> **預設執行**。用 rg/fd 抽查 source-docs 的引用是否仍指向真實程式碼。

```
0.5.1 檔案引用驗證
    從 source-docs 提取所有引用的 .py 檔名：
    rg -o "source: ([\w/]+\.py):\d" source-docs/{module}/ --no-filename -r '$1' | sort -u

    對每個檔名，用 fd 確認存在：
    fd "^{filename}$" mosaic_alpha/ --max-depth 4

0.5.2 Class/Type 引用驗證
    從 source-docs 提取 PascalCase 名稱：
    rg -o "\x60([A-Z][A-Za-z]+)\x60.*\x60([\w/]+\.py):(\d+)\x60" \
       source-docs/{module}/ --no-filename -r '$1' | sort -u

    對每個名稱，用 rg 確認 class 定義存在：
    rg "class {Name}" mosaic_alpha/ -l

0.5.3 結果判定
    全部 ✅ → 引用完整，記錄在 morning report
    有 ❌ → 定向 Edit 修正 source-docs（引用斷裂直接修）
    ❌ 數量多 → 標記模組為需要重建（進 Phase 1）
```

### Phase 0.6: CLAUDE.md SYNC — commit 驅動語義驗證（預設執行）

> **預設執行**。用 sync --changed-since 只檢查今天 commit 涉及的 CLAUDE.md，抓語義過時和導航缺口。

```
0.6.1 取得變更範圍

    讀取 source-docs/.last-run 取得上次執行時間（LAST_RUN）。
    Fallback：當日第一筆 commit 時間。

    git log --since="$LAST_RUN" --name-only --pretty=format:
    過濾 .py 和 CLAUDE.md，映射到模組目錄。

0.6.2 執行 sync --changed-since

    對每個受影響的模組目錄，執行 sync 核心層：
    - 角度一：導航有效性（概念→程式碼連結、導航 Decoder Test）
    - 角度二：程式碼一致性（檔案路徑、class/function、語義 spot-check）
    - 角度七：Signal/Noise Ratio

    不執行品質層（--quality）或完整層（--all），保持輕量。

0.6.3 收集 ACTION items

    sync 產出的 Sync Summary ACTION 供 Phase 3 消費：
    - 導航缺口 → 自動補充 CLAUDE.md
    - 語義不準確 → 自動修正 CLAUDE.md
    - Low Noise 項 → 跳過

    無變更的模組 → 跳過 sync，記錄在 morning report
```

### Phase 1: FIX & REBUILD — 定向修正 + 重建過時 source-docs

> **自動處理所有模組**。過時模組重建 source-docs，新鮮模組只做定向修正。

```
1.0 變更類型分流

    根據 Phase 0 的決策，每個模組走不同路徑：

    | Phase 0 決策 | Phase 1 處理方式 |
    |-------------|-----------------|
    | needs full decode（無 source-docs / .py 新增） | doc-decode 全模組 |
    | needs subsystem rebuild（.py 修改） | doc-decode --subsystem {列表} |
    | needs cleanup（.py 刪除） | 清理引用（已在 Phase 0.3.4 完成） |
    | claude-md-only（反向同步） | 定向修正 source-docs（見 1.4） |
    | skip / verify-only | 跳過 |

1.1 啟動 Agent Pool
    按 --max-agents N 啟動 N 個 agent

1.2 子系統增量重建
    對 .py 修改的模組，傳遞 Phase 0 的受影響子系統清單：
    doc-decode {module} --output source-docs/{module}/ --subsystem {子系統列表}

    遵循 doc-decode.md 的 --subsystem 模式流程（S1→S2→S3 + overview 輕量同步）。
    未指定的子系統文檔不被觸及。

1.3 全模組重建
    對 .py 新增或無 source-docs 的模組，執行完整 doc-decode：
    doc-decode {module} --output source-docs/{module}/

1.4 CLAUDE.md 反向同步（UC7）
    當模組只有 CLAUDE.md 變更、無 .py 變更時：

    1.4.1 讀取 CLAUDE.md diff
        git diff HEAD~{n}..HEAD -- {module}/CLAUDE.md

    1.4.2 分類變更
        | 變更類型 | 處理方式 |
        |---------|---------|
        | 新增設計決策段落 | 新增到 source-docs 的「設計決策記錄」段落 |
        | 修正描述 | 更新 source-docs 中對應描述 |
        | 刪除內容 | 從 source-docs 移除對應內容 |
        | 結構重組（章節大幅調整） | 降級為全模組重建（跑 1.3） |

    1.4.3 執行定向修正
        對每項變更：Read source-docs 對應檔案 → Edit 精確替換

    不讀取 .py（逐字抄錄段落仍正確）。
    品質標準：只修正 CLAUDE.md 變更對應的段落，不改其他內容。

1.5 寫入 .last-run
    寫入 source-docs/.last-run = 當前時間戳
```

---

### Phase 2: VERIFY — decode-compare 驗證

> **核心步驟**。驗證所有有 source-docs 的模組，產出 CLAUDE.md 的 ACTION items。這是 daily-maintain 產出 CLAUDE.md 更新建議的主要來源。

```
2.0 驗證範圍

    對所有有 source-docs 的模組執行驗證（不限於 Phase 1 重建的模組）。
    根據模組新鮮度選擇驗證深度：

    | 模組狀態 | 驗證方式 | 理由 |
    |---------|---------|------|
    | 已重建（Phase 1 doc-decode） | decode-compare（Full Compare） | 需確認重建品質 |
    | 已新建（首次 doc-decode） | decode-compare（Full Compare） | 首次驗證 |
    | 未重建（FRESH） | 跳過 | Phase 0.5 Quick Scan + Phase 0.6 sync 已驗證 |

2.1 未重建模組 → 跳過驗證

    Phase 0.5 Quick Scan + Phase 0.6 sync 已驗證，不需要 Full Compare。
    Phase 0.5 發現的引用斷裂已在 Phase 1 定向修正。
    直接記錄在 morning report 即可。

2.2 Full Compare（已重建/已新建模組）

    執行 decode-compare（預設模式）：
    - 讀取 source-docs/{module}/ 的所有 .md
    - 比對對應 .py 實作
    - 三層比對（A 架構 / B 演算法 / C 資料結構）
    - 標記每項為 ✅ 正確 / ⚠️ 部分差異 / ❌ 理解錯誤 / 🔍 信息缺失

2.3 計算精度（僅 Full Compare）

    精度 = (✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%

    按層級統計：
    | 層級 | ✅ | ⚠️ | ❌ | 🔍 | 精度 |
    |------|----|----|----|----|------|
    | A 架構 | | | | | X% |
    | B 演算法 | | | | | X% |
    | C 資料結構 | | | | | X% |

2.4 精度門檻判斷（僅 Full Compare）

    精度 ≥ 90% → ✅ 品質優良，無需動作
    精度 70-89% → 🟡 可接受，建議改善
    精度 < 70% → 🔴 需要更新 CLAUDE.md

    全部 ❌ 和 🔍 → 標記具體改善建議
    每項附帶：
    - 影響層級（A/B/C）
    - 程式碼引用（file.py:行號）
    - 建議動作（在 CLAUDE.md 的哪裡加入什麼）

2.5 產出 ACTION items（Signal/Noise 過濾）

    遵循 decode-compare §步驟 4 的 ACTION 格式：

    | 信號等級 | 處理方式 | 說明 |
    |---------|---------|------|
    | High Signal | 自動套用（Phase 3 處理） | 設計理由缺失、導航缺口、行為描述錯誤 |
    | Medium Signal | 標記 ⚠️ 建議修改（morning report） | 語義修正、流程描述補充 |
    | Low Noise | 跳過 | API 簽名、參數值（從程式碼可推導） |

    ACTION 格式：
    ```
    ACTION N: [操作類型] [優先級]
    目標位置: CLAUDE.md [章節/行號]
    操作: [新增/修改]
    [可直接貼入的 CLAUDE.md 修改文字]
    信號等級: High/Medium | 驗證來源: file.py:行號
    ```

    輸出：ACTION items 清單（供 Phase 3 消費）
```

---

### Phase 3: UPDATE + REPORT — CLAUDE.md 更新 + 日報

> **CLAUDE.md 是最終目標**。根據 Phase 2 的 ACTION items 更新 CLAUDE.md，然後產出 morning report。

```
3.1 CLAUDE.md 更新

    3.1.1 合併 ACTION items
        來源：Phase 2 的 decode-compare 發現
        分類：High Signal（自動套用）+ Medium Signal（建議）

    3.1.2 修改分類（安全邊界）

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

    3.1.3 逐項執行 Edit
        對每個 ✅ 項目：
        - Read CLAUDE.md 取得當前內容
        - Edit 精確替換（不是整檔重寫）
        - 記錄修改理由（來自 Phase 2 的哪個 ACTION）

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
    - 術語一致性
    - 章節結構
    - 引用完整性
    - 前後邏輯
    - 格式規範

    格式問題直接修正。
    邏輯問題標記 ⚠️。

3.3 Morning Report

    3.3.1 寫入 ai-analysis/daily-report/{YYYY-MM-DD}.md
    3.3.2 同時 print 到對話（精簡版）

    3.3.3 問題分類（⚠️ 未解決問題）

        每個未解決問題必須標注修復方式：

        | 修復方式 | 適用情境 | 實際動作 |
        |---------|---------|---------|
        | CLAUDE.md 定向修正 | 導航缺口、過時描述 | 直接 Edit CLAUDE.md |
        | source-docs 定向修正 | 引用斷裂、已刪除檔案引用 | 直接 Edit source-docs |
        | 自動重建 | 過時模組需要完整重建 | 下次執行時自動處理（doc-decode） |
        | --full | 大重構後 | 全部重建 |

        ⚠️ 大部分 source-docs 問題用定向 Edit 即可，不需要 --full。
        只有 .py 大量變更導致 source-docs 大面積過時時才需要 --full。
```

#### Morning Report 格式

```markdown
# Morning Report — {YYYY-MM-DD}

**執行模式**: Default / Full Rebuild
**執行時間**: {start} → {end}（耗時 {duration}）
**處理模組**: N 個（{模組列表}）

---

## 決策摘要

| 模組 | 處理方式 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|---------|
| rule_forge | 重建 source-docs | 7 files rebuilt | Full Compare: 87% | 5 edits |
| indicators | 定向修正 | skip | Quick Scan: ✅ | — |
| common | 跳過（無變更） | skip | Quick Scan: ✅ | — |

## CLAUDE.md 變更摘要

### ✅ 自動修改（{N} 項）

| 模組 | CLAUDE.md 位置 | 修改類型 | 來源 | 修改摘要 |
|------|---------------|---------|------|---------|
| rule_forge | :45 | 過時描述更新 | compare:engine.py:122 | Pipeline v2 描述更新 |
| rule_forge | :78 | 補充型別關係 | compare:types.py:56 | ConditionFilter vs ObservationFilter 區別 |

### ⚠️ 建議修改（{N} 項）— 需要您確認

| # | 模組 | CLAUDE.md 位置 | 建議 | 理由 | 來源 |
|---|------|---------------|------|------|------|
| 1 | rule_forge | (新增) | 新增「FilterTree 的 sequential greedy 設計理由」 | decode-compare 發現此為非顯而易見的設計決策 | compare:sequential_greedy.py:45 |

## Phase 2: Decode-Compare 精度報告

{每個模組的精度總覽表}

## Decoder Test 結果

| 模組 | 職責 | 設計決策 | 約束 | 邊界 | 通過 |
|------|------|---------|------|------|------|
| rule_forge | ✅ | ✅ | ✅ | ✅ | ✅ |
| indicators | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |

## ⚠️ 未解決問題

| # | 問題 | 嚴重性 | 修復方式 | 建議動作 |
|---|------|--------|---------|---------|
| 1 | indicators source-docs 引用不存在的 ATDDef | 低 | source-docs 定向修正 | 移除引用（Edit） |
| 2 | adapters source-docs 引用已刪除的 .py | 低 | source-docs 定向修正 | 移除引用（Edit） |
| 3 | datasets CLAUDE.md 缺少 ExportConfig 導航 | 低 | CLAUDE.md 定向修正 | 補充導航（Edit） |
| 4 | 4 個過時模組 source-docs 需要重建 | 中 | 自動重建 | 下次 .py 變更時自動處理 |

**修復方式分類**：
- **CLAUDE.md 定向修正**：導航缺口、過時描述 → 直接 Edit，不需要任何模式
- **source-docs 定向修正**：引用斷裂、已刪除檔案 → 直接 Edit source-docs，不需要重建
- **自動重建**：過時模組需要完整重建 source-docs（doc-decode）
- **--full**：大重構後全部打掉重練

## 下次建議

- {根據本次發現的改善建議}
- ⚠️ 不要對所有問題一律建議 --full：
  - 大部分 source-docs 問題 → 定向 Edit 即可
  - 只有 source-docs 大面積過時（.py 大量變更後）才需要 --full
```

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 全自動：掃描 + 定向修正 + 重建過時模組 → morning report |
| **--full** | 強制全部重建 source-docs（大重構後使用） |
| **--max-agents N** | 平行 agent 上限（預設 4，避免 rate limit） |
| **--dry-run** | 只產出 Phase 0 計劃，不實際執行 |
| **--modules a,b,c** | 只處理指定模組（除錯用） |

---

## 與其他 Command 的關係

| Command | 在 daily-maintain 中的角色 |
|---------|--------------------------|
| `/claude:decode-compare --quick` | Phase 0.5：Quick Scan source-docs 引用完整性（rg/fd） |
| `/claude:sync --changed-since` | Phase 0.6：CLAUDE.md 語義驗證（commit 驅動） |
| `/claude:doc-decode` | Phase 1：重建過時模組的 source-docs |
| `/claude:decode-compare` | Phase 2：Full Compare 完整三層比對（重建後的模組） |
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
- **執行前確認 working tree clean**：確保可 rollback
- **修改理由追蹤**：每個 Edit 附帶 decode-compare 的具體發現
- **Decoder Test 驗證**：修改後自動驗證品質

### 比例化深度標準

每個子系統文檔必須達到：

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

未達標 → 回到 Phase 1 補讀，禁止以「已足夠」為由跳過。

### 強制子系統拆分

```
觸發條件：模組 .py > 8
拆分策略：按 import 叢集分組（不是按檔案數均分）
輸出：每個子系統獨立文檔 + overview.md
```

---

## 使用範例

```bash
# 每日：全自動掃描 + 修正（預設，約 30-60 min）
/claude:daily-maintain

# 大重構後：全部重建 source-docs
/claude:daily-maintain --full

# 只重建特定模組的 source-docs
/claude:daily-maintain --full --modules rule_forge

# 只看計劃不執行
/claude:daily-maintain --dry-run

# 只處理特定模組
/claude:daily-maintain --modules rule_forge,indicators
```

---

## 與 /loop 排程整合

```bash
# 每日：全自動（預設）
/loop /claude:daily-maintain

用戶起床後：
1. 查看 ai-analysis/daily-report/{date}.md
2. git diff 檢查 CLAUDE.md 變更
3. 確認 ⚠️ 建議修改項目
```

---

> **維護哲學**: CLAUDE.md 的價值在於持續演化。daily-maintain 是一站式維護引擎：掃描全部模組 → 定向修正小問題（Edit）→ 自動重建過時模組（doc-decode）→ Full Compare 驗證品質 → morning report。一個指令搞定，不需要額外跑其他模式。大重構後才需要 `--full` 強制全部重建。
