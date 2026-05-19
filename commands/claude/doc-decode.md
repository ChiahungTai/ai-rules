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

從 CLAUDE.md 及其引用文檔，結合程式碼實作，重建模組的完整理解。目標不是 API 文檔，而是**重建模組的思考流程**：設計者如何拆解問題、每個組件為什麼存在、數據如何在組件間流動。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)
遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 執行流程

### S1: READ — 文檔收集

定位目標 CLAUDE.md → 讀取主文檔 → 追蹤引用鏈（`@` 展開、markdown link、.yaml 配置）。文檔提供「理解框架」— 知道模組做什麼、為什麼這樣設計。

### S2: SCAN — 程式碼掃描

Glob 掃描所有 .py → 識別 class/function 定義 → 深讀核心檔案 → 追蹤 import 鏈 → 建立程式碼知識圖譜（含已讀追蹤表）。未讀取的核心檔案必須在 S3 前完成。

### S3: RECONSTRUCT — 重建思考流程

**這是核心步驟**。不是列 API，而是用「思考流程」組織理解：

1. **覆蓋清單（強制前置）**：列出每個子系統的所有 class/public method，標記核心演算法（有非 trivial 邏輯的函數），預估程式碼段落數（≥ 6/子系統）
2. **Pipeline 敘事**：從使用者視角描述完整流程
3. **關鍵演算法深潛**：逐字抄錄（**verbatim 約束** — 程式碼必須從 .py 原樣複製，不可改寫或虛構）+ 語義解釋
4. **型別語義重建**：為什麼需要這個型別、在流程中的位置、相似型別的區別
5. **設計決策記錄**：從程式碼推斷設計意圖

#### ⚠️ 逐字抄錄約束（強制）

程式碼段落必須從 .py 逐字抄錄（verbatim），禁止改寫或虛構。「看起來合理」不等於「實際如此」。

錯誤模式：
- ❌ 「AI 覺得合理的寫法」— 用概念理解代替程式碼觀察
- ❌ 「簡化後的 pseudo code 偽裝成實際程式碼」
- ❌ 「從文檔描述反向推導實作」
- ✅ Read .py → 逐字複製 → 加語義解釋（解釋可改寫，程式碼不能）

#### S3.5: VERIFY — 程式碼段落交叉驗證

攔截「合理化虛構」— 對每個嵌入的程式碼段落：
1. **逐字驗證**：重新 Read 對應行，確認文檔程式碼與檔案一致
2. **簽名驗證**：函數名、參數名/順序/型別、回傳型別必須一致
3. **邏輯驗證**：語義解釋的行為描述必須與程式碼一致

### S4: WRITE — 輸出文檔

- 單一模組 → 單一文檔；多子系統 → 按子系統拆分
- 輸入 `--output source-docs/rule_forge` → 寫入 `source-docs/rule_forge/{subsystem}.md`
- 程式碼段落：每段 10-30 行，附 `# source: path/to/file.py:行號`
- 區分**逐字段落**（標記 source:）和**語義描述**（標記為流程描述）

輸出格式：[doc-decode-output-formats.md](./_common/doc-decode-output-formats.md)

---

## --subsystem 模式：子系統級增量重建

**啟用**：`/claude:doc-decode <模組> --subsystem <子系統列表> --output <既有 source-docs/>`

只重建指定子系統，跳過未指定的（完全不被觸及），最後輕量 Edit 更新 overview.md（不重寫）。若 overview.md 不存在 → 降級為全模組重建。

---

## 量化深度標準 — 比例化（強制）

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

「核心演算法」定義：有非 trivial 邏輯的函數（排除 getter/setter/property/re-export）

每個子系統文檔：逐字程式碼段落 ≥ 最低段落數、總行數 ≥ 最低行數、核心函數覆蓋 100%、.py 檔案覆蓋 ≥ 80%

**未達標**：回到 S2 補讀 → S3 補充 → S3.5 驗證。禁止以「已足夠」為由跳過。

---

## Agent 分配策略（--recursive 時強制）

| 模組類型 | .py 數 | Agent 配額 |
|---------|--------|-----------|
| large (> 8 .py) | > 8 | 1 agent 專用 |
| medium (4-8 .py) | 4-8 | 2 模組 / 1 agent |
| small (< 4 .py) | < 4 | 3 模組 / 1 agent |

單 agent 最大負載：800 行核心演算法。預設平行上限：4 agent。禁止將多個 large 模組分配給同一 agent。

--recursive 兩階段：Phase 1 COMPLEXITY SCAN（分類）→ Phase 2 DECODE（平行執行 → 產出 dependency-graph.md）

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 解碼當前目錄的 CLAUDE.md |
| **模組路徑** | 解碼指定目錄或 CLAUDE.md 檔案 |
| **--output** | 輸出目錄（預設 `source-docs/`） |
| **--recursive, -r** | 遞迴處理所有子目錄 |
| **--subsystem** | 只重建指定子系統（逗號分隔），需搭配 `--output` |
| **--max-agents N** | 平行 agent 上限（預設 4） |

---

## 執行約束

- **不修改原始碼**：只讀取 .py
- **覆蓋清單**：S3 前必須建立，S3.5 對照確認 100% 覆蓋
- **引用追蹤深度**：最多 2 層

---

## 與其他 Command 的關係

| Command | 關係 |
|---------|------|
| `/claude:decode-compare` | 後續：驗證 doc-decode 產出的精度 |
| `/claude:sync` | 互補：sync 檢查「是否一致」，doc-decode 重建「完整理解」 |
| `/claude:clean` | 前置：先清理再 decode |
| `/claude:distill` | 前置：先蒸餾再 decode |

> **推薦工作流**: `/claude:clean` → `/claude:distill` → `/claude:sync` → `/claude:doc-decode` → `/claude:decode-compare`
