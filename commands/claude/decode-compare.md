---
description: "對比 doc-decode 結果與實際程式碼 — 驗證 CLAUDE.md 編碼精度"
usage: "/claude:decode-compare <模組路徑> [--redecode] [--depth A|B|C|all] [--recursive]"
argument-hint: "模組目錄路徑（如 rule_forge），必須包含 .py 實作"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /claude:decode-compare — 解碼精度驗證

你是編碼品質驗證專家，負責對比文檔解碼結果與實際程式碼，驗證 CLAUDE.md 的編碼精度（Encoder 品質）。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 核心目標

對比 `/claude:doc-decode` 生成的 pseudo code 與實際 .py 實作，量化 CLAUDE.md 的編碼效果。回答核心問題：**「只看 CLAUDE.md，LLM 能理解多少？」**

**操作模式**：
- 先內嵌執行 doc-decode 流程（只看文檔 → 生成 pseudo code）
- 再掃描實際 .py 檔案
- 逐項比對，生成差異報告

**嚴格約束**：
- **唯讀操作**：不修改任何檔案
- **引用來源**：所有差異必須標註具體程式碼位置（檔案:行號）

---

## 執行流程

### 步驟 1: DECODE — 文檔解碼

**先執行完整的 `/claude:doc-decode` 流程**，產生三層 pseudo code 作為比對基準。

流程與 `/claude:doc-decode` 完全一致：READ → DECODE → PSEUDO → VERIFY。

**重要**：此步驟**只看文檔**，尚未讀取任何 .py 檔案。生成的 pseudo code 代表「純文檔理解」。

### 步驟 2: SCAN — 掃描實際程式碼

讀取模組目錄下的 .py 檔案，提取實作事實。

```
2.1 目錄結構掃描
    fd -e py . $TARGET_DIR --max-depth 2
    fd -t d . $TARGET_DIR --max-depth 2

2.2 類別/函數定義提取
    rg "^class " -t py $TARGET_DIR
    rg "^def " -t py $TARGET_DIR

2.3 關鍵檔案深入讀取
    根據步驟 1 的 pseudo code 決定需要讀取哪些 .py
    優先讀取：engine.py, types.py, 核心演算法檔案

2.4 型別註解和 docstring 提取
    讀取 dataclass 定義、型別註解、docstring
```

### 步驟 3: COMPARE — 逐項比對

#### Level A: 架構級比對

| 比對項目 | 驗證方式 |
|---------|---------|
| 模組劃分 | 文檔描述的檔案是否存在？職責是否匹配？ |
| 數據流方向 | pseudo code 的數據流方向是否與 import 鏈一致？ |
| 依賴關係 | 文檔描述的 import 依賴是否準確？ |
| Pipeline 流程 | 步驟順序是否與實際呼叫鏈一致？ |

#### Level B: 演算法級比對

| 比對項目 | 驗證方式 |
|---------|---------|
| 函數邏輯步驟 | pseudo code 的步驟是否匹配實際函數實作？ |
| 條件判斷 | IF/ELSE 分支是否準確？ |
| 計算公式 | 公式推導是否與程式碼中的計算一致？ |
| YAML 解析流程 | 配置檔案的解析邏輯是否準確？ |
| AND/OR 邏輯 | 組合條件的評估邏輯是否正確？ |

#### Level C: 資料結構級比對

| 比對項目 | 驗證方式 |
|---------|---------|
| dataclass 欄位 | pseudo code 的欄位名稱和型別是否準確？ |
| Enum 值 | pseudo code 的 enum 值是否完整？ |
| 公式實作 | 公式推導是否與程式碼中的計算一致？ |
| YAML 格式 | 文檔描述的 YAML 結構是否與實際檔案一致？ |
| 方法簽名 | pseudo code 的方法是否存在於實際類別中？ |

#### 標記系統

| 標記 | 含義 | 判斷標準 |
|------|------|---------|
| ✅ 正確 | 完全匹配或僅有命名差異 | 核心邏輯/結構完全一致 |
| ⚠️ 部分差異 | 方向正確但細節有誤 | 主體正確，但有遺漏或多餘的步驟/欄位 |
| ❌ 理解錯誤 | 與實作相反或嚴重偏離 | 邏輯方向錯誤或結構理解反了 |
| 🔍 信息缺失 | 文檔完全未提及 | 實作中存在但文檔無對應描述 |

### 步驟 4: REPORT — 差異報告

```
4.1 精度總覽（按層級統計）
4.2 詳細差異清單（每項含程式碼引用）
4.3 編碼改善建議（優先級排序）
4.4 整體評價
```

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **模組路徑** | 必填，要比對的模組目錄 |
| **--redecode** | 強制重新執行 decode（不復用之前的理解） |
| **--depth A** | 只比對架構級 |
| **--depth B** | 只比對演算法級 |
| **--depth C** | 只比對資料結構級 |
| **--depth all** | 全部三層（預設） |
| **--recursive, -r** | 遞迴處理所有子目錄的 CLAUDE.md |

---

## 輸出格式

```markdown
## Decode Compare Report — {module_name}

**比對基準**: doc-decode pseudo code（來自 CLAUDE.md + N 個引用文檔）
**比對目標**: N 個 .py 檔案
**掃描檔案**: [列出實際讀取的 .py 檔案]

---

### 精度總覽

| 層級 | ✅ 正確 | ⚠️ 部分差異 | ❌ 理解錯誤 | 🔍 信息缺失 | 精度 |
|------|---------|------------|------------|------------|------|
| A 架構 | X | Y | Z | W | X% |
| B 演算法 | X | Y | Z | W | X% |
| C 資料結構 | X | Y | Z | W | X% |
| **總計** | **X** | **Y** | **Z** | **W** | **X%** |

**精度計算**: (✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%

---

### Level A: 架構級差異

#### ✅ 正確
- **[項目]**: 說明（來源: file.py:行號）

#### ⚠️ 部分差異
- **[項目]**: 預期 X，實際 Y（來源: file.py:行號）

#### ❌ 理解錯誤
- **[項目]**: 預期 X，實際 Y（來源: file.py:行號）

#### 🔍 信息缺失
- **[項目]**: 實作中有 X，文檔未提及（來源: file.py:行號）

### Level B: 演算法級差異
[格式同上]

### Level C: 資料結構級差異
[格式同上]

---

### 編碼改善建議

| 優先級 | 改善項目 | 影響層級 | 影響項數 | 建議動作 |
|--------|---------|---------|---------|---------|
| 🔴 | [高影響缺口] | A/B/C | N | [具體建議：在 CLAUDE.md 的哪裡加入什麼] |
| 🟡 | [中影響缺口] | A/B/C | N | [具體建議] |
| 🟢 | [低影響缺口] | A/B/C | N | [具體建議] |

### 整體評價

- **架構理解**: [一段話評價]
- **演算法理解**: [一段話評價]
- **資料結構理解**: [一段話評價]
- **CLAUDE.md 編碼品質**: [一段話總結 — 文檔是否成功捕獲了本質知識]
- **最大收穫**: [這次比對發現的最重要發現]
```

---

## 執行約束

### 比對公平性約束
- **寬鬆認定**：命名差異（如 `range_pct` vs `amplitude_pct`）不算錯誤，只要語義一致
- **抽象容忍**：pseudo code 省略的實作細節不算信息缺失，只標記文檔完全未提及的概念
- **推導合理**：從文檔可合理推導出的理解算 ✅，不需要文檔逐字描述

### 引用來源約束
- 所有差異必須標註程式碼引用（`檔案路徑:行號`）
- 正確項目引用文檔來源（`文檔名:段落`）
- 改善建議必須具體到 CLAUDE.md 的哪個章節

### 遞迴處理約束
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

遞迴輸出格式: [recursive-output.md](./_common/recursive-output.md)

---

## 使用範例

```bash
# 對比 rule_forge 模組
/claude:decode-compare mosaic_alpha/rule_forge

# 只比對演算法級
/claude:decode-compare rule_forge --depth B

# 強制重新 decode（不復用之前的理解）
/claude:decode-compare rule_forge --redecode

# 遞迴比對所有子模組
/claude:decode-compare --recursive
```

---

## 與其他 Command 的關係

| Command | 職責 | 關係 |
|---------|------|------|
| `/claude:doc-decode` | 只看文檔 → pseudo code | 本命令的步驟 1 |
| `/claude:decode-compare` | 文檔理解 vs 實作比對 | 本命令（完整流程） |
| `/claude:sync` | 文檔↔程式碼同步性 | 互補：sync 檢查「是否一致」，compare 檢查「理解是否準確」 |
| `/consistency` | 文檔內部品質 | 前置：先確保文檔自洽再做 compare |

> **定位**: `/claude:sync` 回答「文檔和程式碼是否同步」，`/claude:decode-compare` 回答「文檔的知識是否足夠讓人理解系統」。

---

> **驗證哲學**: CLAUDE.md 的價值不在於記錄每個 API 簽名，而在於傳達「從程式碼猜不到的知識」。本命令量化這個傳達效果 — 如果架構級理解 90%+ 正確，說明 Encoder 成功；如果演算法級有大面積 ❌，說明文檔需要補充關鍵邏輯。
