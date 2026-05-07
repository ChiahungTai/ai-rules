---
description: "從 CLAUDE.md 文檔解碼模組理解 — 生成 pseudo code 並評估編碼品質"
usage: "/claude:doc-decode <模組路徑> [--depth A|B|C|all] [--source-aided]"
argument-hint: "模組目錄路徑（如 rule_forge）或 CLAUDE.md 檔案路徑"
allowed-tools: ["Read", "Glob", "Grep", "Write"]
---

# /claude:doc-decode — CLAUDE.md Decoder

你是模組知識的 Decoder，負責從 CLAUDE.md 及其引用文檔重建對模組的理解。預設模式**只看文檔**（不碰 .py），生成三層 pseudo code 並自我評估信心等級。加 `--source-aided` 時可讀取程式碼輔助重建完整理解文檔。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 核心目標

CLAUDE.md 是模組知識的 Encoder（壓縮表示）。本命令有兩種模式：

**預設模式（Decoder Test）**：驗證 Encoder 是否成功捕獲了本質知識，讓 LLM 能從文檔重建出八九不離十的理解。

**`--source-aided` 模式（程式碼輔助重建）**：結合文檔 + 程式碼實作，產出完整理解文檔。目標是還原程式碼的整體思考邏輯流程 — 不只是 API 列表，而是「為什麼這樣設計、怎麼串起來、關鍵決策點在哪」的完整敘事。

### 模式切換約束

| 約束 | 預設模式 | `--source-aided` |
|------|---------|-------------------|
| 讀取 .py | **禁止** | **允許**（核心價值） |
| 寫入檔案 | **禁止** | **允許**（輸出到指定目錄） |
| 輸出 | pseudo code + 信心評估 | 完整理解文檔（含程式碼段落） |
| 目的 | 測試文檔品質 | 重建完整模組理解 |

---

## 預設模式執行流程（Decoder Test）

> 以下為預設模式（不加 `--source-aided`）的流程。`--source-aided` 模式見下方獨立章節。

### 步驟 1: READ — 文檔收集

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

### 步驟 2: DECODE — 理解模組

**只基於步驟 1 收集的文檔內容，不查證程式碼。**

```
2.1 模組定位
    - 核心職責是什麼？
    - 在整個系統中扮演什麼角色？
    - 設計哲學（為什麼這樣設計）

2.2 設計決策
    - 有哪些非顯而易見的選擇？
    - 架構約束有哪些？
    - 模組邊界（不做什麼）？

2.3 數據流
    - 輸入從哪來？
    - 經過哪些轉換？
    - 最終輸出是什麼？

2.4 Actor 角色（如適用）
    - Code / LLM / Human 各自負責什麼？
```

### 步驟 3: PSEUDO — 三層 pseudo code 生成

#### Level A: 架構級

生成模組互動的結構化描述：

```
# 模組互動
[模組A] → [數據/型別] → [模組B] → [數據/型別] → [模組C]

# 數據流（從源頭到最終產物）
Source → Transform1 → Transform2 → Output

# 依賴關係
module_x imports from: common, structure
module_x imported by: engine, pipeline

# 子系統分工（如有多個子系統）
Subsystem1: 職責 → 輸出
Subsystem2: 職責 → 輸出
```

#### Level B: 演算法級

關鍵函數/流程的核心邏輯 pseudo code：

```
function key_algorithm(input):
    step 1: [描述]
    step 2: IF [條件] THEN [分支A] ELSE [分支B]
    step 3: [計算公式]
    step 4: RETURN [結果]

# Pipeline 流程
Pipeline Step 1: Input → Processing → Intermediate Output
Pipeline Step 2: Intermediate → Processing → Final Output

# YAML 解析流程
Load YAML → Parse Structure → Validate → Build Runtime Objects
```

#### Level C: 資料結構級

型別定義的 pseudo code：

```
@dataclass
class TypeName:
    field1: type          # 語義說明
    field2: type          # 語義說明

class EnumName(Enum):
    VALUE1 = "str"       # 語義說明
    VALUE2 = "str"       # 語義說明

# 公式
metric_x = (a - b) / b * 100    # 語義說明
```

### 步驟 4: VERIFY — 自我評估

```
4.1 信心等級標記
    🟢 高信心（>80%）— 文檔清楚描述，可直接重建
    🟡 中信心（50-80%）— 方向正確，細節可能偏差
    🔴 低信心（<50%）— 大量推測，很可能有誤

4.2 推測標記規範
    Pseudo code 中的具體內容分兩類：
    - **文檔記載**：直接從文檔原文推導的內容，正常呈現
    - **AI 推測**：文檔未明確說明，基於上下文猜測的內容
      → 必須用 推測: 前綴標記
      → 適用範圍：具體數值/閾值、未記載的分支邏輯、未記載的錯誤處理

    範例：
    IF up_big_pct > baseline + 推測: 0.10 AND win_rate > 推測: 0.55:

4.3 整體信心計算
    各層信心評分 → 加權平均：
    整體信心 = A層信心 × 0.4 + B層信心 × 0.4 + C層信心 × 0.2

    各層信心估算方式：
    - 盤點該層 pseudo code 中的項目
    - 每個項目判斷：🟢=90%, 🟡=65%, 🔴=30%
    - 該層信心 = 項目信心的算術平均

4.4 信息缺口識別
    文檔未提及但系統推測需要的部分：
    - 列出每個缺口
    - 標記影響層級（A/B/C）
    - 標記風險（高/中/低）

4.5 信息衝突
    文檔內部不一致的描述

4.6 編碼品質總結
    - High Signal 覆蓋率估算
    - 整體信心評分（含計算過程）
    - 改善建議
```

---

## --source-aided 模式：程式碼輔助完整重建

> 啟用條件：`/claude:doc-decode <模組路徑> --source-aided`

### 設計理念

預設模式是「閉卷考試」— 測試文檔是否足夠。`--source-aided` 是「開卷考試」— 結合文檔的理解框架 + 程式碼的實作細節，產出**完整的思考邏輯文檔**。

目標不是 API 文檔（那是程式碼本身做的事），而是**重建模組的思考流程**：設計者如何拆解問題、每個組件為什麼存在、數據如何在組件間流動、關鍵決策點的推理過程。

### 執行流程

#### S1: READ — 文檔收集

同預設模式的步驟 1（讀取 CLAUDE.md + 引用文檔）。文檔提供「理解框架」— 知道模組做什麼、為什麼這樣設計。

#### S2: SCAN — 程式碼掃描

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

#### S3: RECONSTRUCT — 重建思考流程

**這是 source-aided 的核心步驟**。不是列 API，而是用「思考流程」組織理解：

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
    預設：ai-analysis/{module_name}/source-aided-{topic}.md
    可透過 --output 參數指定

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

### 輸出格式（source-aided）

```markdown
# {模組名稱} — Source-Aided 理解文檔

## 模組全貌
[一段話描述模組的核心目標和設計哲學]

## 思考流程：從輸入到輸出
[Pipeline 敘事 — 以數據的視角描述完整轉換流程]

## 核心子系統

### {子系統 1}：{一句話職責}

**設計意圖**：[為什麼需要這個子系統]

**關鍵程式碼**（逐字抄錄自 source）：

```python
# source: path/to/file.py:行號
[10-30 行從 .py 逐字抄錄的程式碼]
```

語義解釋：[這段程式碼在整體流程中做什麼、為什麼這樣寫]

**演算法邏輯**（語義描述，非逐字）：

```
[Pseudo code 或流程描述 — 這是 AI 的理解，不是實際程式碼]
```

### {子系統 2}：{一句話職責}
[同上結構]

## 型別語義
[關鍵型別的語義解釋、為什麼需要、在流程中的位置]

## 設計決策記錄
| 決策 | 選項 | 選擇 | 推斷理由 | 驗證來源 |
|------|------|------|---------|---------|
| [決策點] | [A/B/C] | [選擇] | [從程式碼推斷的理由] | [file.py:行號] |

## 與其他模組的關係
[依賴方向、數據流、整合方式]
```

### 文檔拆分規則

| 情境 | 策略 |
|------|------|
| 模組 < 10 個 .py，單一流程 | 單一文檔 `source-aided-{module}.md` |
| 模組有明確子系統（如 setup + filter_tree） | 按子系統拆分 `source-aided-{subsystem}.md` + 總覽 `source-aided-{module}-overview.md` |
| 模組有獨立的配置系統 | 配置拆為獨立文檔 `source-aided-{module}-config.md` |

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 解碼當前目錄的 CLAUDE.md |
| **模組路徑** | 解碼指定目錄或 CLAUDE.md 檔案 |
| **--depth A** | 只生成架構級 pseudo code（預設模式專用，與 --source-aided 互斥） |
| **--depth B** | 只生成演算法級 pseudo code（預設模式專用） |
| **--depth C** | 只生成資料結構級 pseudo code（預設模式專用） |
| **--depth all** | 全部三層（預設） |
| **--source-aided** | 程式碼輔助重建模式：讀取 .py + 文檔，產出完整理解文檔（與 --depth 互斥） |
| **--output** | source-aided 輸出目錄（預設：`ai-analysis/{module_name}/`） |
| **--recursive, -r** | 遞迴處理所有子目錄的 CLAUDE.md。可與 --source-aided 組合，每個子模組獨立產出文檔 |

---

## 輸出格式

### 單模組輸出

```markdown
## Doc Decode Report — {module_name}

**來源文檔**: CLAUDE.md + N 個引用文檔
**文檔清單**: [列出所有讀取的文檔及其職責]
**整體信心**: 🟢/🟡/🔴 (X%)

---

### 模組定位

[一段話描述核心職責和設計哲學]

### Level A: 架構級 [信心: 🟢/🟡/🔴]

#### 模組互動
[結構化描述或 ASCII 圖]

#### 數據流
[從源頭到最終產物的流程]

#### 依賴關係
[import 依賴和數據依賴]

### Level B: 演算法級 [信心: 🟢/🟡/🔴]

#### {關鍵函數/流程 1}
```
pseudo code
```

#### {關鍵函數/流程 2}
```
pseudo code
```

### Level C: 資料結構級 [信心: 🟢/🟡/🔴]

#### {型別定義 1}
```
pseudo dataclass/enum
```

#### {公式}
```
metric = formula
```

---

### 信息缺口

| 缺口 | 影響層級 | 推測內容 | 風險 |
|------|---------|---------|------|
| [文檔未提及的部分] | A/B/C | [基於上下文的推測] | 高/中/低 |

### 信息衝突（如有）

| 位置 A | 位置 B | 衝突描述 |
|--------|--------|---------|
| [文檔:段落] | [文檔:段落] | [矛盾說明] |

### 編碼品質評估

- **High Signal 覆蓋率**: X%（設計理由、架構約束、非顯而易見的選擇、模組邊界、失敗教訓）
- **信息缺口數**: N 個
- **整體評價**: [一段話總結]
- **建議**: [具體的改善方向]

### 信心計算過程

| 層級 | 項目數 | 🟢 | 🟡 | 🔴 | 層信心 |
|------|--------|----|----|----|--------|
| A 架構 | N | X | Y | Z | X% |
| B 演算法 | N | X | Y | Z | X% |
| C 資料結構 | N | X | Y | Z | X% |

**整體信心** = A×0.4 + B×0.4 + C×0.2 = X%
```

### 遞迴模式輸出

遞迴輸出格式: [recursive-output.md](./_common/recursive-output.md)

---

## 執行約束

### 預設模式約束（不加 --source-aided）
- **只讀文檔類型**: .md、.yaml、.toml（配置檔）
- **禁止讀取**: .py、.pyx、.pxd、.json（除非是文檔引用的配置）
- **引用追蹤深度**: 最多 2 層（CLAUDE.md → 直接引用 → 間接引用）
- **唯讀操作**: 不修改任何檔案（Write 工具僅供 --source-aided 模式使用，預設模式下禁止呼叫）
- **Pseudo code 品質**: 必須有足夠細節讓人判斷正確性
- **公式**: 必須寫出完整推導
- **型別定義**: 必須包含欄位語義

### --source-aided 模式約束
- **可讀取**: .md、.yaml、.toml、.py（程式碼輔助理解）
- **程式碼段落嵌入**: 每段 10-30 行，附 source 路徑標註
- **不修改原始碼**: 只讀取 .py，不修改任何 .py 檔案
- **輸出**: 只寫入 `ai-analysis/` 或 `--output` 指定目錄

### 共用約束
- 信心等級必須基於實際理解程度
- 推測的內容必須明確標記為「推測」（含 pseudo code 中的數值/閾值）
- 不確定時寧可標記為 🔴 也不要虛報 🟢
- 信息缺口必須如實列出，不能假裝知道

---

## 與其他 Command 的關係

| Command | 職責 | 關係 |
|---------|------|------|
| `/claude:doc-decode` | 只看文檔 → pseudo code | 本命令（Decoder Test） |
| `/claude:doc-decode --source-aided` | 文檔 + 程式碼 → 完整理解文檔 | 本命令的輔助模式（程式碼輔助重建） |
| `/claude:decode-compare` | 文檔理解 vs 實作比對 | 後續步驟：用本命令的 pseudo code 比對 .py |
| `/claude:sync` | 文檔↔程式碼同步性 | 互補：sync 檢查「是否一致」，doc-decode 檢查「是否可理解」 |
| `/claude:clean` | 清理元資訊 | 前置：先清理再 decode，避免 noise 干擾 |
| `/claude:distill` | 蒸餾 signal/noise | 前置：先蒸餾再 decode，提高 decode 品質 |
| `/consistency` | 文檔內部品質 | 前置：先確保文檔自洽再做 decode |

> **定位**: `/claude:sync` 回答「文檔和程式碼是否同步」，`/claude:doc-decode` 回答「文檔的知識是否足夠讓人理解系統」。

> **推薦工作流**: `/claude:clean`（清理 noise）→ `/claude:distill`（蒸餾 signal）→ `/claude:sync`（靜態一致性）→ `/claude:doc-decode`（理解度測試）→ `/claude:decode-compare`（精度驗證）

---

## 使用範例

```bash
# 解碼當前目錄的 CLAUDE.md
/claude:doc-decode

# 解碼指定模組
/claude:doc-decode mosaic_alpha/rule_forge

# 只生成演算法級 pseudo code
/claude:doc-decode rule_forge --depth B

# 程式碼輔助重建 — 結合文檔 + .py 產出完整理解文檔
/claude:doc-decode rule_forge --source-aided

# 指定輸出目錄
/claude:doc-decode rule_forge --source-aided --output ai-analysis/rule_forge

# 遞迴解碼所有子模組
/claude:doc-decode --recursive
```

---

> **Decoder 哲學**: CLAUDE.md 的終極品質標準是 Decoder Test — 如果一個 LLM 只看文檔就能重建出八九不離十的理解，說明 Encoder 成功捕獲了本質知識。本命令是這個標準的系統化執行工具。

> **誠實優先**: 信心評估的價值在於真實反映理解程度。虛報信心比承認不了解更危險 — 它會掩蓋文檔的真正缺口。
