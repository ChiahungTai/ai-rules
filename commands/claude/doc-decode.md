---
description: "從 CLAUDE.md 文檔解碼模組理解 — 生成 pseudo code 並評估編碼品質"
usage: "/claude:doc-decode <模組路徑> [--depth A|B|C|all]"
argument-hint: "模組目錄路徑（如 rule_forge）或 CLAUDE.md 檔案路徑"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /claude:doc-decode — CLAUDE.md Decoder

你是模組知識的 Decoder，負責從 CLAUDE.md 及其引用文檔重建對模組的理解。**只看文檔，不碰 .py 檔案**。生成三層 pseudo code 並自我評估信心等級。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

## 核心目標

CLAUDE.md 是模組知識的 Encoder（壓縮表示）。本命令執行 **Decoder Test** — 驗證 Encoder 是否成功捕獲了本質知識，讓 LLM 能從文檔重建出八九不離十的理解。

**嚴格約束**：
- **只讀文檔**：只讀 CLAUDE.md、.md 引用文檔、.yaml 配置。**禁止讀取 .py 檔案**
- **唯讀操作**：不修改任何檔案
- **誠實評估**：信心等級必須反映真實理解程度，不虛報

---

## 執行流程

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

4.2 信息缺口識別
    文檔未提及但系統推測需要的部分：
    - 列出每個缺口
    - 標記影響層級（A/B/C）
    - 標記風險（高/中/低）

4.3 信息衝突
    文檔內部不一致的描述

4.4 編碼品質總結
    - High Signal 覆蓋率估算
    - 整體信心評分
    - 改善建議
```

---

## 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 解碼當前目錄的 CLAUDE.md |
| **模組路徑** | 解碼指定目錄或 CLAUDE.md 檔案 |
| **--depth A** | 只生成架構級 pseudo code |
| **--depth B** | 只生成演算法級 pseudo code |
| **--depth C** | 只生成資料結構級 pseudo code |
| **--depth all** | 全部三層（預設） |
| **--recursive, -r** | 遞迴處理所有子目錄的 CLAUDE.md |

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
```

### 遞迴模式輸出

遞迴輸出格式: [recursive-output.md](./_common/recursive-output.md)

---

## 執行約束

### 文檔範圍約束
- **只讀文檔類型**: .md、.yaml、.toml（配置檔）
- **禁止讀取**: .py、.pyx、.pxd、.json（除非是文檔引用的配置）
- **引用追蹤深度**: 最多 2 層（CLAUDE.md → 直接引用 → 間接引用）

### 評估誠實約束
- 信心等級必須基於實際理解程度
- 推測的內容必須明確標記為「推測」
- 不確定時寧可標記為 🔴 也不要虛報 🟢
- 信息缺口必須如實列出，不能假裝知道

### 品質約束
- Pseudo code 必須有足夠細節讓人判斷正確性
- 公式必須寫出完整推導
- 型別定義必須包含欄位語義

---

## 與其他 Command 的關係

| Command | 職責 | 關係 |
|---------|------|------|
| `/claude:doc-decode` | 只看文檔 → pseudo code | 本命令（Decoder Test） |
| `/claude:decode-compare` | 文檔理解 vs 實作比對 | 後續步驟：用本命令的 pseudo code 比對 .py |
| `/claude:sync` | 文檔↔程式碼同步性 | 互補：sync 檢查「是否一致」，doc-decode 檢查「是否可理解」 |
| `/claude:clean` | 清理元資訊 | 前置：先清理再 decode，避免 noise 干擾 |
| `/claude:distill` | 蒸餾 signal/noise | 前置：先蒸餾再 decode，提高 decode 品質 |
| `/consistency` | 文檔內部品質 | 前置：先確保文檔自洽再做 decode |

> **定位**: `/claude:sync` 回答「文檔和程式碼是否同步」，`/claude:doc-decode` 回答「文檔的知識是否足夠讓人理解系統」。

---

## 使用範例

```bash
# 解碼當前目錄的 CLAUDE.md
/claude:doc-decode

# 解碼指定模組
/claude:doc-decode mosaic_alpha/rule_forge

# 只生成演算法級 pseudo code
/claude:doc-decode rule_forge --depth B

# 遞迴解碼所有子模組
/claude:doc-decode --recursive
```

---

> **Decoder 哲學**: CLAUDE.md 的終極品質標準是 Decoder Test — 如果一個 LLM 只看文檔就能重建出八九不離十的理解，說明 Encoder 成功捕獲了本質知識。本命令是這個標準的系統化執行工具。

> **誠實優先**: 信心評估的價值在於真實反映理解程度。虛報信心比承認不了解更危險 — 它會掩蓋文檔的真正缺口。
