# CLAUDE.md 撰寫規範

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

> **🔴 強烈警告**: AI 寫作 CLAUDE.md 時**絕對禁止**加入統計資訊、版本號、更新日期等元資訊。詳細說明請參考 `@~/.claude/rules/_ai-behavior-constraints.md`

## 基本原則

CLAUDE.md 是給 AI 的協作指南，應專注於**核心原則**和**執行約束**，避免冗餘細節。

## 命名規範

### 檔案命名
- 專案層級: `./CLAUDE.md` 或 `./.claude/CLAUDE.md`
- 命令層級: `commands/claude/{command-name}.md`
- 符號連結: 用 `@path` 引用共用內容

### 命令命名（slash commands）
- 格式: `/{category}:{action}` 或 `/{action}`
- 範例: `/claude:clean`, `/commit-message`, `/explain`
- 使用小寫和連字線，不用底線

## 結構規範

### YAML Frontmatter
```yaml
---
description: "簡短明確的功能描述"
usage: "/command [參數] [選項]"
argument-hint: "參數提示信息"
allowed-tools: ["Read", "Write", "Edit"]
permission-mode: "acceptEdits"
---
```

### 章節組織
```markdown
# 標題

## 🎯 核心目標（可選）
簡述此檔案/命令的目的

## 核心內容
- 使用清晰層級（## → ### → ####）
- 用項目符號區分要點
- 用程式碼區塊展示範例

## 執行約束
列出必須遵守的約束條件

## 品質檢查清單（可選）
- [ ] 檢查項目 1
- [ ] 檢查項目 2
```

## 內容規範

> **核心理念**: CLAUDE.md 是模組知識的 Encoder（壓縮表示）。品質標準是 Signal/Noise ratio — 保留從程式碼猜不到的知識，移除可推導的內容。詳細框架見 `commands/claude/_common/encoder-philosophy.md`。

### 應該包含（High Signal）
- **導航指引**: 每個關鍵概念必須附帶 `file.py:ClassOrFunction` 指引，讓 LLM 能從概念直接定位到程式碼（判斷：文檔引入了概念但 LLM 不知道去哪裡找 → 導航缺口）
- **設計理由**: 為什麼這樣做而非那樣做
- **架構約束**: 不可妥協的設計限制
- **非顯而易見的選擇**: 看起來反直覺但有意義的決策
- **模組邊界**: 這個模組不做什麼
- **失敗教訓**: 從實際 debugging 經驗得到的規則
- **執行約束**: 必須遵守的規則
- **型別關係**: 相似型別的用途區別和使用場景（判斷：兩個型別名字相似但職責不同 → 它們的區別是 High Signal）
- **Pipeline 編排**: 多步驟流程的順序和數據銜接點（判斷：從單一函數看不到的全局流程 → High Signal）
- **慣例映射**: 專案特定的約定和語義映射（判斷：名稱推導不出語義 → High Signal）
- **可複用基礎設施**: 其他模組可能會複用的 utilities、base classes、protocols（判斷：如果另一個模組的 EP 設計新功能時會想複用 → 值得記錄。格式：`path/to/file.py` — 用途簡述）

### 應該避免（Low Noise）
- **可推導內容**: API 簽名、參數表、欄位列表（從程式碼可直接推導）
- **完整範例**: 超過 5 行的程式碼範例（精簡為一句話 + 源碼引用）
- **元資訊**: 版本號、更新日期、統計資訊、Changelog
- **過時範例**: 無法實際執行的範例

### 引用語法（依檔案類型選擇）

#### CLAUDE.md / rules/ — `@` 自動展開
`@` 是 CLAUDE.md 專用的 transclusion 機制，啟動時自動展開內容。
```markdown
# 相對路徑（相對於當前檔案）
@docs/architecture.md

# 絕對路徑（個人層級）
@~/.claude/rules/_ai-behavior-constraints.md

# 專案根目錄相對路徑
@../../rules/self-consistency.md
```

#### Skill / Command — markdown link 按需讀取
Skills 不支持 `@` transclusion。使用 markdown link 讓 Claude 知道何時讀取 supporting files。
```markdown
# 相對路徑（相對於 SKILL.md 所在目錄）
Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

# 引用其他 command
參考: [clean.md](./clean.md)
```
描述檔案內容讓 Claude 判斷何時讀取，而非無條件載入。

#### CLAUDE.md — 長文件按需指引（不用 `@`）
當目標檔案太長或 signal/noise 比例不佳，不值得 `@` 全載，但 AI 需要知道它的存在時，使用 markdown link + 內容描述。
```markdown
# 偶爾才需要的背景知識（debug 時才查）
詳細 benchmark 數據和架構探索教訓見 [lessons_learnt.md](lessons_learnt.md)
```

**選擇判斷**：context 是有限資源，只載入每次對話都需要的內容。

| 條件 | 語法 | 理由 |
|------|------|------|
| 每次對話都可能需要 + 內容精簡 | `@path` | 強制載入確保 AI 始終知道 |
| 偶爾才需要 / 情境觸發 | `[描述](path)` | AI 按需讀取；描述越明確，觸發越準確 |

## 程式碼範例規範

### 範例格式
```markdown
### 基本用法

```bash
/claude:clean
```

### 輸出範例

```
預期輸出格式
```
```

### 語言標籤選擇
- **bash**: Shell 命令、Git 操作
- **python**: Python 程式碼
- **markdown**: Markdown 格式範例
- 無語言標籤時使用純文字

## 導航優先原則

> **核心理念**: CLAUDE.md 的首要價值是讓 LLM 從「概念」定位到「程式碼」。導航失敗 = 理解失敗，LLM 找不到程式碼就無法正確工作。

### 概念→程式碼映射

每個 CLAUDE.md 引入的關鍵概念（設計決策、核心演算法、資料結構）都必須附帶導航指引：

```markdown
✅ 有導航：CLAUDE.md 提到「台灣證券分類器」→ 指向 security_type_classifier.py:TWSecurityClassifier
❌ 無導航：CLAUDE.md 提到「證券分類」→ 只有檔案名，不知道核心 class 是什麼
```

### 導航語法

```markdown
- **設計決策描述** → `file.py:ClassName` 或 `file.py:function_name()`
```

箭頭 `→` 後接具體的檔案路徑和 class/function 名稱。避免只寫檔案名不寫 class/function。

### 導航覆蓋範圍

| 內容類型 | 導航要求 |
|---------|---------|
| 關鍵設計決策 | 必須附帶 `→ file.py:Class` |
| 模組職責表 | 每列至少有檔案名，核心職責附 class 名 |
| 跨模組依賴 | 具體到 `module.ClassName`，不只寫模組名 |
| Pipeline 步驟 | 每個步驟指向入口 function |
| 資料流描述 | 標注產出型別和下游消費者 |

### 導航 Decoder Test（自檢）

寫完 CLAUDE.md 後，不查源碼，嘗試回答：
1. 「我要修改 X 的邏輯，打開哪個檔案？」→ 能定位到具體檔案名？
2. 「Y 這個概念在哪裡實作？」→ 能指向檔案 + class 或 function 名？
3. 「Z 的上游資料從哪來？」→ 能追蹤到上游步驟和產出型別？

任一問題無法回答 → 補充導航指引。

## 品質標準

- **導航優先**: 每個關鍵概念都有程式碼位置指引
- **簡潔**: 避免冗餘描述，專注核心信息
- **明確**: 避免模糊詞彙（「大概」「可能」「應該」）
- **可操作**: 提供具體執行步驟和範例
- **可維護**: 結構清晰，易於更新
