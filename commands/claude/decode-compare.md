---
description: "對比文檔理解與實際程式碼，驗證精確度"
when_to_use: "Compare source-docs/ documentation against actual Python code to verify encoding precision. Supports --quick scan and full three-level comparison."
usage: "/claude:decode-compare <路徑> [--quick] [--redecode] [--subsystem NAME] [--recursive]"
argument-hint: "/claude:decode-compare <輸出目錄> [--quick] [--redecode] [--subsystem NAME] [--recursive] — --quick 為輕量驗證（rg/fd），預設為完整三層比對"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Write"]
---

# /claude:decode-compare — 解碼精度驗證

對比 source-docs/ 與實際 .py 實作，量化理解文檔的精度。回答：**「source-docs 的描述與實際程式碼有多一致？」**

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)
遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 操作模式

| 模式 | 觸發 | 做法 | 成本 |
|------|------|------|------|
| **Quick Scan** | `--quick` | rg/fd 抽查引用完整性（秒級） | 極低 |
| **Full Compare** | 預設 | 讀取 .py 逐項三層比對（分鐘級） | 高 |

Quick Scan 用於 FRESH 模組的日常巡檢；Full Compare 用於 STALE 模組或首次驗證。

**嚴格約束**：
- **原始碼唯讀**：不修改任何 .py 檔案
- **引用來源**：所有差異必須標註具體程式碼位置（檔案:行號）

---

## 執行流程

### 步驟 0: PATH RESOLVE — 路徑解析

自動偵測輸入路徑類型：
- 含 .md（且無 .py）→ 輸出目錄 → 從目錄名推導模組路徑 → 進入 SCAN
- 含 .py → 錯誤：只接受 source-docs/ 目錄
- 若帶 --redecode → 先執行 doc-decode 重建，再比對
- 若帶 --subsystem → 只比對指定子系統的 .py

### 步驟 0.5: QUICK SCAN（--quick 模式）

只用 rg/fd 抽查 source-docs 的引用是否仍指向真實程式碼：
1. 檔案引用驗證：提取 .py 檔名 → fd 確認存在
2. Class/Type 引用驗證：提取 PascalCase 名稱 → rg 確認 class 定義存在
3. 行號有效性抽樣：提取 file:line → wc -l 確認不超過檔案總行數

結果判定：全部 ✅ → 引用完整 | ❌ ≤ 2 → 針對性修正 | ❌ > 2 → 觸發 Full Compare

### 步驟 1: SCAN — 掃描實際程式碼

讀取模組目錄下的 .py，提取實作事實（目錄結構、class/function 定義、型別註解、docstring）。

### 步驟 2: COMPARE — 逐項比對

#### 三層比對

| 層級 | 比對項目 |
|------|---------|
| **A 架構** | 模組劃分、數據流方向、依賴關係、Pipeline 流程 |
| **B 演算法** | 函數邏輯步驟、條件判斷、計算公式、YAML 解析、AND/OR 邏輯 |
| **C 資料結構** | dataclass 欄位、Enum 值、方法簽名 |

#### 標記系統

| 標記 | 含義 |
|------|------|
| ✅ | 完全匹配或僅有命名差異 |
| ⚠️ | 方向正確但細節有誤 |
| ❌ | 與實作相反或嚴重偏離 |
| 🔍 | 文檔完全未提及 |

### 步驟 3: REPORT — 差異報告

精度計算：`(✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%`

精度門檻：≥ 90% ✅ | 70-89% 🟡 | < 70% 🔴 需更新 CLAUDE.md

### 步驟 4: ACTION — 產出可執行的 CLAUDE.md 修改

**設計理念**：將 High Signal 差異轉化為可直接 copy-paste 的 CLAUDE.md 修改文字。Low Noise 項目不產出 ACTION。

#### Signal/Noise 過濾

| 差異類型 | 信號等級 | 處理方式 |
|---------|---------|---------|
| 架構級設計決策缺失（🔍 A 級） | High Signal | 產出新增段落 |
| 演算法行為描述不準確（⚠️ B 級） | High Signal | 產出修正文字 |
| 導航缺口（概念無程式碼指引） | High Signal | 產出導航補充 |
| 流程描述不完整 | Medium Signal | 產出補充文字 |
| 資料結構細節差異（⚠️ C 級） | Low Noise | 跳過（從程式碼可推導） |

**排序**：導航缺口 > 設計決策 > 行為描述 > Low Noise（不產出）

---

## 參數

| 參數 | 說明 |
|------|------|
| **輸出目錄** | 必填，要比對的 source-docs/ 目錄 |
| **--quick** | Quick Scan：只用 rg/fd 驗證引用完整性 |
| **--redecode** | 先執行 doc-decode 重建，再比對 |
| **--subsystem** | 只比對指定子系統 |
| **--recursive, -r** | 遞迴處理所有子目錄 |
| **--max-agents N** | 平行 agent 上限（預設 4） |

---

## 比對公平性約束

- **寬鬆認定**：命名差異（如 `range_pct` vs `amplitude_pct`）不算錯誤
- **抽象容忍**：文檔省略的實作細節不算信息缺失
- **推導合理**：從文檔可合理推導出的理解算 ✅

遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 與其他 Command 的關係

| Command | 職責 | 關係 |
|---------|------|------|
| `/claude:doc-decode` | 文檔 + 程式碼 → source-docs | 前置：產出比對基準 |
| `/claude:decode-compare` | source-docs vs 實作比對 | 本命令 |
| `/claude:sync` | 文檔↔程式碼同步性 | 互補：sync 檢查「是否一致」，compare 檢查「理解是否準確」 |

> **驗證哲學**: CLAUDE.md 的價值在於傳達「從程式碼猜不到的知識」。本命令量化這個傳達效果。
