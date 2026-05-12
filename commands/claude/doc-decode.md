---
description: "從 CLAUDE.md + 程式碼重建模組理解文檔，產出完整思考邏輯文檔（source-docs/）"
when_to_use: "Reconstruct module understanding documents from CLAUDE.md + code, producing source-docs/ with pipeline narratives, code verbatims, and design decisions."
usage: |
  /claude:doc-decode [模組路徑]
  /claude:doc-decode rule_forge
  /claude:doc-decode rule_forge --output source-docs/rule_forge
  /claude:doc-decode --recursive
  /claude:doc-decode rule_forge --subsystem trend,oscillator
argument-hint: "/claude:doc-decode [模組路徑] [--recursive] [--subsystem LIST] — 模組目錄路徑（如 rule_forge）或 CLAUDE.md 檔案路徑"
allowed-tools: ["Read", "Glob", "Grep", "Write"]
---

# /claude:doc-decode — CLAUDE.md Decoder

你是模組知識的 Decoder，負責從 CLAUDE.md 及其引用文檔，結合程式碼實作，重建對模組的完整理解。

目標不是 API 文檔（那是程式碼本身做的事），而是**重建模組的思考流程**：設計者如何拆解問題、每個組件為什麼存在、數據如何在組件間流動、關鍵決策點的推理過程。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 核心目標

CLAUDE.md 是模組知識的 Encoder（壓縮表示）。本命令結合文檔 + 程式碼實作，產出完整理解文檔 — 還原程式碼的整體思考邏輯流程：不只是 API 列表，而是「為什麼這樣設計、怎麼串起來、關鍵決策點在哪」的完整敘事。

---

## 執行流程

### S1: READ — 文檔收集

```
1.1 定位目標 CLAUDE.md
    - $ARGUMENTS 非空 → 解析為路徑（目錄或檔案）
    - $ARGUMENTS 為空 → 當前目錄的 CLAUDE.md

1.2 讀取主 CLAUDE.md

1.3 追蹤引用鏈
    - @ 展開的文檔（CLAUDE.md 中的 @path 語法）
    - markdown link 引用的文檔（[描述](path)）
    - .yaml 配置檔案（如 setup_definitions.yaml, condition_mappings.yaml）

1.4 建立文檔清單
    列出所有已讀取的文檔及其職責
```

文檔提供「理解框架」— 知道模組做什麼、為什麼這樣設計。

### S2: SCAN — 程式碼掃描

```
2.1 模組結構掃描
    - Glob 掃描所有 .py 檔案
    - 識別 class / function 定義
    - 提取型別註解和 docstring

2.2 關鍵檔案深讀
    - 從 CLAUDE.md 的模組結構中識別核心檔案
    - 讀取核心檔案的完整實作
    - 追蹤 import 鏈（讀取被引用的關鍵模組）

2.3 配置檔讀取
    - .yaml 定義檔（如 setup_definitions.yaml）
    - .toml 配置
    - __init__.py 的公開 API 導出

2.4 建立程式碼知識圖譜（附已讀追蹤）
    - 哪些 class 在哪個檔案
    - 哪些 function 被誰呼叫
    - 數據型別在模組間如何傳遞

    已讀追蹤表（在 context 中維護，不寫入最終文檔）：
    | 檔案 | 已讀行數 | 核心演算法 | 讀取狀態 |
    |------|---------|-----------|---------|
    | core.py | 1-200 | evaluate, _check | ✅ |
    | builder.py | (未讀) | build_recursive | ❌ 需讀取 |

    未讀取的核心檔案 → 必須在 S3 開始前完成讀取。
    若 S3 途中發現遺漏 → 按 fallback 規則先 Read 再寫入。
```

### S3: RECONSTRUCT — 重建思考流程

**這是核心步驟**。不是列 API，而是用「思考流程」組織理解：

**⚠️ 前置步驟：覆蓋清單（Coverage Checklist）**

在開始寫任何文檔前，必須先建立覆蓋清單：

```
3.0 覆蓋清單（S2 完成後、S3.1 開始前）

    對每個子系統：
    1. 列出該子系統的所有核心 .py 檔案
    2. 列出每個 .py 中的 class 和 public method
    3. 標記哪些是「核心演算法」（有非 trivial 邏輯的函數）
    4. 預估需要多少程式碼段落才能覆蓋（目標 ≥ 6 段/子系統）

    輸出格式（在 context 中維護，不寫入最終文檔）：

    子系統: {name}
    ├── file_a.py
    │   ├── ClassA.__init__        → 設計意圖
    │   ├── ClassA.core_method()   → 核心演算法 ✅ (需程式碼段落)
    │   └── ClassA.helper()        → 輔助邏輯
    ├── file_b.py
    │   ├── function_x()           → 核心演算法 ✅ (需程式碼段落)
    │   └── function_y()           → 輔助邏輯
    預估程式碼段落: N 段 (必須 ≥ 6)
    狀態: ❌ 未覆蓋 / ✅ 已覆蓋

    此清單在 S3 進行中持續更新，
    S3.5 驗證時對照清單確認 100% 覆蓋。
```

```
3.1 Pipeline 敘事
    從使用者的視角描述完整流程：
    「我是一根 K 線數據，我經過了哪些轉換，最終變成了什麼」

3.2 關鍵演算法深潛（逐字抄錄約束）

    ⚠️ 程式碼段落必須從 .py 逐字抄錄（verbatim），禁止改寫或虛構。
    「看起來合理」不等於「實際如此」— 概念理解再強也不能替代程式碼觀察。

    對每個核心演算法/流程：
    - 它解決什麼問題（設計意圖）
    - 怎麼解決（演算法邏輯）
    - 逐字程式碼段落（10-30 行，用 Read 工具從 .py 抄錄）
    - 邊界情況的處理（防禦性設計）

    錯誤模式警示（必須避免）：
    ❌ 「AI 覺得合理的寫法」— 用概念理解代替程式碼觀察
    ❌ 「簡化後的 pseudo code 偽裝成實際程式碼」— 看起來像真的但其實是編造
    ❌ 「從文檔描述反向推導實作」— 文檔說概念，AI 自行填補實作細節
    ✅ Read .py → 逐字複製 → 加語義解釋（解釋可以改寫，程式碼不能）

3.3 型別語義重建
    不是列出 dataclass 欄位，而是解釋：
    - 為什麼需要這個型別
    - 它在流程中的哪個位置被創建和消費
    - 相似型別的區別（如 SignalDirection vs TradeDirection）

3.4 設計決策記錄
    從程式碼中推斷設計意圖：
    - 為什麼用 AND/OR 而不是單一條件
    - 為什麼 YAML-driven 而不是 hard-code
    - 為什麼拆分成這些子模組
```

#### S3.5: VERIFY — 程式碼段落交叉驗證

> **防線目的**: 攔截「合理化虛構」— AI 用概念理解覆蓋程式碼觀察的常見失敗模式。

```
在寫入文檔前，對每個嵌入的程式碼段落執行三項驗證：

3.5.1 逐字驗證
    每個標記為「source: file.py:行號」的程式碼段落，
    重新 Read 該檔案的對應行，確認文檔中的程式碼與檔案內容一致。
    如有不一致 → 以 .py 內容為準修正文檔。

3.5.2 簽名驗證
    文檔中出現的函數簽名（def/class），
    必須與 .py 中的實際簽名一致：
    - 函數名稱正確
    - 參數名稱和順序正確
    - 參數型別正確
    - 回傳型別正確
    如有模糊 → 重新 Read 確認。

3.5.3 邏輯驗證
    語義解釋中的行為描述（如「每步重新計算」「不重新計算」），
    必須與程式碼實際行為一致。
    如無法從已讀程式碼確認 → 標記為「推測:」。

    常見邏輯驗證失敗模式：
    - 文檔說「不重新計算」但程式碼有遞迴呼叫 → 需重新 Read 確認
    - 文檔描述的執行路徑與 if/else 分支不符 → 需重新 Read 確認
    - 文檔的演算法複雜度推測與實際迴圈結構不符 → 需重新 Read 確認
```

#### S4: WRITE — 輸出文檔

```
4.1 確定輸出結構
    單一模組 → 單一文檔
    多子系統 → 按子系統拆分（每個子系統有獨立思考流程）

4.2 寫入目標目錄
    檔案放在 --output 指定的目錄內，用簡潔檔名：
    - --output source-docs/rule_forge → 寫入 source-docs/rule_forge/{subsystem}.md
    - 預設目錄：source-docs/{module_name}/
    - 檔名使用 flat 命名（路徑分隔符用底線）：adapters_sj.md, common_rate_limiter.md
    檔名範例：condition-system.md, filter-tree.md, setup-classification.md, engine-analysis.md, overview.md

4.3 程式碼段落嵌入規則（逐字抄錄）
    - 每段 10-30 行，聚焦單一邏輯
    - 保留原始縮排
    - 標註來源：# source: path/to/file.py:行號
    - **逐字抄錄**：程式碼必須從 .py 原樣複製，不可改寫
    - 嵌入後用一段話解釋「這段程式碼在整體流程中的角色」
    - 區分兩種程式碼區塊：
      - **逐字段落**（標記 source: file:行號）= 從 .py 抄錄的鐵證
      - **語義描述**（標記為「流程描述」或 pseudo code）= AI 的理解和解釋

4.4 撰寫品質
    - 用繁體中文 + 英文術語
    - 遵循 signal/noise 框架（不寫可推導內容）
    - 程式碼段落必須附帶語義解釋
    - 不加統計資訊、版本號、日期
```

### --subsystem 模式：子系統級增量重建

> **啟用條件**：`/claude:doc-decode <模組路徑> --subsystem <子系統列表>`

**設計理念**：daily-maintain Phase 0.5 已識別受影響的子系統。只重建變更的子系統，跳過未變更的子系統，大幅節省 context 和 token。

**觸發條件**：
- 必須搭配 `--output`（指向既有 source-docs/ 目錄）
- 子系統列表逗號分隔：`--subsystem trend,oscillator`

**執行流程**：

```
1. 讀取 --output 目錄的既有子系統清單
   （從 overview.md 或目錄結構推導）

2. 對每個指定子系統執行 S1→S2→S3（同標準流程）
   - S1: 讀取 CLAUDE.md + 引用文檔
   - S2: 只讀取該子系統相關的 .py（不讀其他子系統的 .py）
   - S3: 重建該子系統的理解文檔
   - S3.5: 交叉驗證

3. 跳過未指定的子系統（保留既有 source-docs 不動）

4. Overview 輕量同步
   讀取每個受影響子系統文檔的 summary 段落
   比對 overview.md 中的對應段落
   → 有差異則 Edit 更新（不改寫整份 overview.md）
   不重新讀 .py（summary 來源於子系統文檔，非程式碼直接提取）
```

**約束**：
- 跳過的子系統文檔**完全不被觸及**（不讀、不改）
- Overview 同步是增量 Edit，不是全量重寫
- 若 overview.md 不存在或格式異常 → 降級為全模組重建

**輸出**：
```
[subsystem-mode] Rebuilding 2/5 subsystems for rule_forge
  ✅ trend.md (重建)
  ✅ oscillator.md (重建)
  ⏭️ condition-system.md (跳過)
  ⏭️ filter-tree.md (跳過)
  ⏭️ backbone-pipeline.md (跳過)
  ✅ overview.md (輕量同步, 2 處更新)
```

### 輸出格式

輸出格式和知識圖譜格式：[doc-decode-output-formats.md](./_common/doc-decode-output-formats.md)

### 量化深度標準 — 比例化（強制）

> **核心原則**：不同複雜度的模組需要不同的深度門檻。固定標準對小模組太鬆、對大模組太嚴。

**比例化公式**：

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

**「核心演算法」定義**：有非 trivial 邏輯的函數（排除簡單 getter/setter/property/re-export）

**範例**：
| 模組 | 核心演算法 | 子系統 | 最低行數 | 最低段落 |
|------|-----------|--------|---------|---------|
| small (3 .py) | 4 | 0 | max(200, 120) = 200 | max(6, 3) = 6 |
| medium (6 .py) | 10 | 1 | max(200, 350) = 350 | max(6, 8) = 8 |
| large (21 .py) | 20 | 6 | max(200, 900) = 900 | max(6, 16) = 16 |

**每個子系統文檔的最低標準**：

| 指標 | 最低要求 | 說明 |
|------|---------|------|
| 逐字程式碼段落 | ≥ 最低段落數（公式計算） | 每段 10-30 行，覆蓋該子系統的核心演算法 |
| 總行數 | ≥ 最低行數（公式計算） | 含程式碼段落、語義解釋、型別語義、設計決策 |
| 核心函數/方法覆蓋 | 100% | S3 覆蓋清單中的每個項目都有對應的程式碼段落或語義描述 |
| .py 檔案覆蓋 | ≥ 80% | 子系統內的核心 .py 檔案至少有一段程式碼段落被引用 |

**未達標時的處理**：
1. 回到 S2（SCAN）補讀未覆蓋的 .py 檔案
2. 回到 S3（RECONSTRUCT）補充缺少的程式碼段落
3. 重新執行 S3.5（VERIFY）驗證新增內容
4. 禁止以「已足夠」為由跳過未達標的子系統

### Agent 分配策略（--recursive 時強制）

> **設計理念**：當一次處理多個模組時，context dilution 導致品質下降。合理分配確保每個 agent 有足夠 context 完成高品質輸出。

**分配規則**：

| 模組類型 | .py 數 | 核心演算法 | Agent 配額 |
|---------|--------|-----------|-----------|
| large | > 8 | > 15 | 1 agent 專用 |
| medium | 4-8 | 5-15 | 2 模組 / 1 agent |
| small | < 4 | < 5 | 3 模組 / 1 agent |

**單 agent 最大負載**：不超過 800 行核心演算法

**預設平行上限**：4 個 agent（避免 rate limit）。可透過 `--max-agents N` 調整。分配規則計算出的 agent 數量若超過上限，多出的模組排隊等 agent 空出後再啟動。

**超出容量時的處理**：
1. 優先拆分 large 模組為子系統（強制子系統拆分）
2. 拆分後重新分配
3. 禁止將多個 large 模組分配給同一 agent

**--recursive 兩階段執行策略**：

```
Phase 1: COMPLEXITY SCAN
  掃描所有模組的 .py 數量和核心演算法數量
  分類為 large / medium / small
  按 Agent 分配規則計算需要的 agent 數量

Phase 2: DECODE
  啟動分配好的 agent pool
  每個 agent 處理分配到的模組
  全部完成後產出 dependency-graph.md（知識圖譜）
```

### 知識圖譜輸出（dependency-graph.md）

格式詳見 [doc-decode-output-formats.md](./_common/doc-decode-output-formats.md) 的「知識圖譜輸出」段落。`--recursive` 時自動產出 `source-docs/dependency-graph.md`。增量更新：`daily-maintain` 的 incremental 模式只更新受影響模組的條目，不重建整份文檔。

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 解碼當前目錄的 CLAUDE.md |
| **模組路徑** | 解碼指定目錄或 CLAUDE.md 檔案 |
| **--output** | 輸出目錄（預設 `source-docs/`） |
| **--recursive, -r** | 遞迴處理所有子目錄的 CLAUDE.md，每個子模組獨立產出文檔 |
| **--subsystem** | 只重建指定子系統（逗號分隔，如 `--subsystem trend,oscillator`），跳過其他子系統。需搭配 `--output` 指向既有 source-docs/ 目錄 |
| **--max-agents N** | 平行 agent 上限（預設 4，避免 rate limit） |

---

## 輸出格式

### 遞迴模式輸出

遞迴輸出格式: [recursive-output.md](./_common/recursive-output.md)

---

## 執行約束

- **可讀取**: .md、.yaml、.toml、.py（程式碼輔助理解）
- **程式碼段落嵌入**: 每段 10-30 行，附 source 路徑標註
- **不修改原始碼**: 只讀取 .py，不修改任何 .py 檔案
- **輸出**: 寫入 `source-docs/`（或 `--output` 指定目錄），flat 命名
- **覆蓋清單**: S3 開始前必須建立（§3.0），S3.5 時對照確認 100% 覆蓋
- **量化深度**: 每個子系統文檔必須達到最低標準（§量化深度標準）
- **引用追蹤深度**: 最多 2 層（CLAUDE.md → 直接引用 → 間接引用）

---

## 與其他 Command 的關係

| Command | 職責 | 關係 |
|---------|------|------|
| `/claude:doc-decode` | 文檔 + 程式碼 → 完整理解文檔 | 本命令 |
| `/claude:decode-compare` | source-docs 理解 vs 實作比對 | 後續步驟：驗證 doc-decode 產出的精度 |
| `/claude:sync` | 文檔↔程式碼同步性 | 互補：sync 檢查「是否一致」，doc-decode 重建「完整理解」 |
| `/claude:clean` | 清理元資訊 | 前置：先清理再 decode，避免 noise 干擾 |
| `/claude:distill` | 蒸餾 signal/noise | 前置：先蒸餾再 decode，提高 decode 品質 |
| `/consistency` | 文檔內部品質 | 前置：先確保文檔自洽再做 decode |

> **定位**: `/claude:sync` 回答「文檔和程式碼是否同步」，`/claude:doc-decode` 回答「從文檔 + 程式碼重建完整模組理解」。

> **推薦工作流**: `/claude:clean`（清理 noise）→ `/claude:distill`（蒸餾 signal）→ `/claude:sync`（靜態一致性）→ `/claude:doc-decode`（重建理解）→ `/claude:decode-compare`（精度驗證）

---

## 使用範例

```bash
# 解碼當前目錄的 CLAUDE.md → source-docs/{module}/
/claude:doc-decode

# 解碼指定模組 → source-docs/rule_forge/
/claude:doc-decode rule_forge

# 指定輸出目錄
/claude:doc-decode rule_forge --output source-docs/rule_forge

# 遞迴解碼所有子模組 → source-docs/*/
/claude:doc-decode --recursive

# 子系統增量重建
/claude:doc-decode rule_forge --subsystem trend,oscillator
```
