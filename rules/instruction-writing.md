---
harness-scope: neutral
paths:
  - "**/*.md"
---

# Instruction File 撰寫規範

> **🔴 強烈警告**: AI 寫作 instruction file 時**絕對禁止**加入統計資訊、版本號、更新日期等元資訊。詳細說明請參考 [_ai-behavior-constraints.md](_ai-behavior-constraints.md)

## 基本原則

instruction file 是給 AI 的協作指南，應專注於**核心原則**和**執行約束**，避免冗餘細節。

## 命名規範

### 檔案命名（instruction file 雙檔模式）

> **雙檔模式（root + 每個模組層）**：每層都是 `AGENTS.md`（source）+ `CLAUDE.md`（`@AGENTS.md` wrapper）。多 harness——AGENTS.md 三家都讀、CLAUDE.md 是 Claude 專屬（Claude 不 native 讀 AGENTS.md，靠 CLAUDE.md `@AGENTS.md` wrapper 拉進 session）。標準優先：中立內容進 AGENTS.md，Claude 專屬進 CLAUDE.md。**每層雙檔確保三家 harness 都讀得到該層 instruction**——只有 root 雙檔時，其他 harness（ZCode/OpenCode/Codex）讀不到模組層。

- **`AGENTS.md`**（source, harness-neutral）：**專案指令**的中立原則層——三家 harness（Claude/ZCode/OpenCode）開本專案時都讀。body **禁 Claude 專屬散文**（hooks、`paths:`、`/build` workflow）——其他 harness 讀到是斷裂噪音；frontmatter 欄位可容忍（harness 自動忽略不懂的）

> **⚠️ 全域指南 ≠ 專案 AGENTS.md**：跨專案共用的全域開發指南（如 ai-rules 的 `ai-development-guide.md`）是**獨立檔**，部署到各 harness 全域位置（`~/.claude/CLAUDE.md`、`~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`、`~/.codex/AGENTS.md` → 該檔），**不是專案 root AGENTS.md**。專案 AGENTS.md = 開該專案時讀的專案指令；全域指南 = 所有專案都載入的跨專案規範。兩者各司其職——混為一檔 → 專案失去自己的指令 + 全域指南被專案內容污染。
- **`CLAUDE.md`**（thin wrapper, Claude 專屬）：開頭 `@AGENTS.md`（把中立規則拉進 Claude session）+ Claude 專屬段（hooks 機制、slash command workflow、repo 結構導航）。只 Claude 讀
- 專案層級：root `AGENTS.md`（source）+ `CLAUDE.md`（`@AGENTS.md` wrapper）；或 `./.claude/CLAUDE.md`
- 模組層級：每個重要模組目錄 `AGENTS.md`（source）+ `CLAUDE.md`（`@AGENTS.md` thin wrapper，通常只一行 `@AGENTS.md`——模組層少有 Claude 專屬機制，wrapper 用途是讓 Claude 讀到模組 AGENTS.md）
- 命令層級：`commands/instruction/{command-name}.md`
- 符號連結：`@path` 引用（**僅 CLAUDE.md 展開**；AGENTS.md 不展開 `@`——見下方）

> **`@` transclusion 是 Claude Code 專用**：CLAUDE.md 啟動時自動展開 `@path`；AGENTS.md（與 ZCode/OpenCode）**不展開 `@`**。所以 AGENTS.md 內**不可用 `@`** 拉內容——中立內容直接寫在 AGENTS.md，Claude 專屬才放 CLAUDE.md 用 `@`。

### 命令命名（Claude 端 slash commands）
- 格式: `/{category}:{action}` 或 `/{action}`
- 範例: `/instruction:clean`, `/commit-message`, `/illustrate`
- 使用小寫和連字線，不用底線

<!-- bundle: skip-start -->
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

> skill 完整 frontmatter 欄位（`when_to_use` / `paths` / `disable-model-invocation` / `context:fork` / `allowed-tools` 等）與決策原則見 [skills/CLAUDE.md](../skills/CLAUDE.md)（單一真相源，此處不重複）。

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

<!-- bundle: skip-end -->
## 內容規範

> **核心理念**: instruction file 是模組知識的 Encoder（壓縮表示）。品質標準是 Signal/Noise ratio — 保留從程式碼猜不到的知識，移除可推導的內容。詳細框架見 encoder-philosophy.md（Claude: `commands/instruction/_common/encoder-philosophy.md`）。

### 應該包含（High Signal）
- **導航指引（概念→符號）**: 每個關鍵概念必須附帶 symbol name 指引（如 `ClassName` 或 `function_name()`），讓 LLM 能從概念定位到符號、再由 LSP 解析到位置。檔案路徑（`file.py:`）為選用 fallback（判斷：文檔引入了概念但 LLM 不知道對應哪個符號 → 導航缺口）
- **設計理由（預設精煉一句）**: 為什麼這樣做而非那樣做 —— 一句 why 即可（防 LLM 不懂而亂改）。**例外**：規則易被 LLM/社群慣例動搖（LLM 會 rationalize 違規，如「加統計無妨」）→ 整段反駁論證是防亂改的疫苗而非贅述，段落標 `補充論證`/`第一性原理`，先承認反方價值再反駁（範例見 `python-standards.md` Facade Pattern 段）
- **架構約束**: 不可妥協的設計限制
- **非顯而易見的選擇**: 看起來反直覺但有意義的決策
- **模組邊界**: 這個模組不做什麼
- **失敗教訓**: 從實際 debugging 經驗得到的規則
- **執行約束**: 必須遵守的規則
- **型別關係**: 相似型別的用途區別和使用場景（判斷：兩個型別名字相似但職責不同 → 它們的區別是 High Signal）
- **Pipeline 編排**: 多步驟流程的順序和數據銜接點（判斷：從單一函數看不到的全局流程 → High Signal）
- **慣例映射**: 專案特定的約定和語義映射（判斷：名稱推導不出語義 → High Signal）
- **可複用基礎設施**: 其他模組可能會複用的 utilities、base classes、protocols（判斷：如果另一個模組的 EP 設計新功能時會想複用 → 值得記錄）。格式：`ClassName`（或 `file.py:ClassName` 作為消歧 / LSP 不可用時的 fallback）— 用途簡述
- **負空間指導**: 「不要做什麼」— LLM 無法自行推導不做的事（如「API 內部函數之間不要加驗證」）
- **行為校準**: 判斷尺度 — LLM 不會自行產生的校準原則（如「拒絕≠錯誤」）

<!-- bundle: skip-start -->
#### 可複用基礎設施段落規範

**段落結構**（放置位置：Navigation Table 之後、Core API 之前）：
```markdown
## 可複用基礎設施

**{誰應該看這裡}。{一句話 scope}。**

- `ClassName`（或 `file.py:ClassName` 作為 fallback）— 一句話用途
```

**跨模組標記**（讓消費端 agent 知道「這不是本模組獨佔的」）：
- `**X 也繼承**` — 定義在此，但其他模組也使用（如 `**conditions 也繼承**`）
- `**跨模組 Protocol**` — 其他模組可以去實作的介面
- `繼承 other_module/path.py:Class` — 原始定義在他處，本模組是消費端

**Runtime API 存取模式**：當模組的核心工廠/入口回傳的物件有重要的下游 API 時（如 `create_backtest_engine()` 回傳的 BacktestEngine 的 post-run 提取方法），在「可複用基礎設施」之後以簡短表格記錄常用存取模式。判斷：工廠函式的回傳值在 2+ 個消費端被以相同模式使用 → 值得記錄。

**頂層索引**（專案根 AGENTS.md）：精選 8-12 項高頻使用項 + 子模組連結，不重複子模組的完整列表。格式：`- module.Class — 用途 → [module](module/AGENTS.md)`（連模組 AGENTS.md source；`Class` 路徑選用，LSP 可解析）

<!-- bundle: skip-end -->
### 應該避免（Low Noise）
- **可推導內容**: API 簽名、參數表、欄位列表（從程式碼可直接推導）
- **完整範例**: 超過 5 行的程式碼範例（精簡為一句話 + 源碼引用）
- **元資訊**: 版本號、更新日期、統計資訊、Changelog
- **過時範例**: 無法實際執行的範例
- **專案特定事實**: 真實專案符號/路徑/數字（如 `myproject.common.enums.MyEnum`）—— 泛用 rules/commands 教 pattern，用 `<placeholder>`（`<package>`、`<EnumClass>` 等）。例子釘死專案現狀 → 該專案一改就 drift、其他專案讀無關。專案特定工具（upgrade-* 等）例外
- **重複描述（反模式是重複，不是集中）**: 集中清單（Symbol Map / Index 段落）與 per-concept 種子重複描述同概念 —— 寫兩遍浪費 token 且易 drift。集中段落（如「可複用基礎設施」）只用於跨模組共用 symbol（distinct purpose），不可與 per-concept 種子重複

<!-- bundle: skip-start -->
### 引用語法（依檔案類型選擇）


#### CLAUDE.md / rules/ — `@` 自動展開
`@` 是 CLAUDE.md 專用的 transclusion 機制，啟動時自動展開內容。
```markdown
# 相對路徑（相對於當前檔案）
@docs/architecture.md

# 絕對路徑（個人層級）
@~/Github/ai-rules/rules/_ai-behavior-constraints.md

# 專案根目錄相對路徑
@../../rules/self-consistency.md
```

#### Skill / Command — markdown link 按需讀取
Skills 不支持 `@` transclusion。使用 markdown link 讓 AI agent 知道何時讀取 supporting files。
```markdown
# 相對路徑（相對於 SKILL.md 所在目錄）
Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

# 引用其他 command
參考: [clean.md](./clean.md)
```
描述檔案內容讓 AI agent 判斷何時讀取，而非無條件載入。

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
/instruction:clean
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

<!-- bundle: skip-end -->
## 導航優先原則

> **核心理念**：instruction file 的導航職責是提供「概念→符號」的種子；符號→位置的機械查找由 LSP 接手。文檔寫作精力應放在語義知識（設計理由、約束、失敗教訓），而非檔案路徑表。

<!-- bundle: skip-start -->
### 導航的兩個子類（LSP 時代）

| 子類 | 內容 | 誰負責 | 說明 |
|------|------|--------|------|
| **導航-A：概念→符號** | 「台股除權息調整」→ `backward_adjust()` | **instruction file（不可約）** | LSP `workspaceSymbol` 要先有名子才能搜；概念是人類用語，符號是程式碼用語，這對應只能人寫 |
| **導航-B：符號→位置/簽名/引用** | `backward_adjust()` → 哪個檔案、簽名、誰呼叫 | **LSP（可推導）** | `goToDefinition` / `hover` / `findReferences` / `incomingCalls`，live 且 100% 準確 |

**LSP 時代原則**：instruction file 只需給導航-A（概念→symbol name）；導航-B 交給 LSP。檔案路徑不再是要求。LSP 工具決策樹與分工見 `lsp-navigation.md`（rules/ source；載入機制見各檔開頭）。

### 概念→符號映射（導航-A）

每個 instruction file 引入的關鍵概念（設計決策、核心演算法、資料結構）都必須附帶 symbol name 種子：

```markdown
✅ 有種子：instruction file 提到「台灣證券分類器」→ 指向 `TWSecurityClassifier`（檔案由 LSP 解析）
❌ 無種子：instruction file 提到「證券分類」→ 只有概念，不知道核心符號是什麼
```

### 導航語法

```markdown
- **設計決策描述** → `ClassName` 或 `function_name()`
```

**檔案路徑（`file.py:`）何時仍要寫**：
- LSP 不可用情境（subagent worktree、Cython `.so`、無語言伺服器的語言）→ 路徑是唯一 fallback
- 符號名有歧義（同名多處、或 `workspaceSymbol` 回傳多個候選）→ 路徑消歧
- 其餘情況路徑選用，不要求

> ⚠️ **LSP 依賴護欄**：導航-A 依賴 LSP 可用。LSP 失效（stub 未同步等）是真實且反覆發生的失敗。**跨模組入口、或被多處引用的核心符號**（`findReferences` hits 高）附帶檔案路徑作 fallback，別假設 LSP 永遠可用。

### 導航覆蓋範圍

| 內容類型 | 導航要求 |
|---------|---------|
| 關鍵設計決策 | 必須附帶 symbol name（→ `Class` 或 `func()`） |
| 模組職責表 | 每列至少有 symbol name；核心職責附 class 名 |
| 跨模組依賴 | 具體到 `module.ClassName`，不只寫模組名 |
| Pipeline 步驟 | 每個步驟指向入口 symbol |
| 資料流描述 | 標注產出型別和下游消費者 |

### 種子深度：推進到可執行單元

**入口類**導航種子必須指向**可執行單元**（function 或 method），不可停在 config / dataclass / 裸 class —— 這些不是執行入口：停在 class 讓 LLM 多一步 `documentSymbol` 才找到執行處；停在 config 則誤把配置當入口。（單純型別引用——「這個 class 在哪」——裸 class 仍是有效種子；本規則僅限**入口類**：會被導航來執行任務者。）

- **class 入口附主要 method**：寫 `ClassName.method_name()` 而非只 `ClassName`
- **config / dataclass 概念推進到 consumer**：概念核心若是 config，種子指向讀取它的 executor function，別讓 config 單獨當入口

**判準**：自問「LLM 拿這個種子能直接執行任務，還是還要再找一層？」要再找 → 種子不夠深。

> 命名慣例（`run_*` / `apply_*` = executor，`*Config` / `*Factor` = config）已承擔角色消歧，**不需額外標註角色標籤**；種子深度是對「種子指向哪裡」的結構要求，不是對符號貼標籤。

### 標準段落標題（機械識別）

> **核心原則**：每類導航內容用唯一標準標題，讓 `rg` / sync 能機械識別「所有導航表」「所有檔案結構」。模組依規模選用子集，**不強制全有**（小模組省略避免過度結構化）。

| 標題 | 內容 | 形式 / 適用 |
|------|------|--------|
| `## 模組定位` | 一句話職責 + 邊界（不做什麼） | 必有 |
| `## 模組導航` | 概念→符號種子（導航-A）。符號多→表（`Class/Function` \| `檔案` \| 職責）；符號少→描述性文字即可，不必強制表格 | 有公開符號 |
| `## 可複用基礎設施` | 跨模組共用 symbol（格式見上方「可複用基礎設施段落規範」） | 有跨模組消費者 |
| `## 模組檔案結構` | 目錄樹（`檔案:symbol`） | 檔案數多到值得展示組織 |
| `## Capabilities` | UC 能力表（能力 \| 入口 \| 狀態） | 有已完成 UC |
| `## 核心 API` | import 範例 | 有公開 API |

**內容要求 vs 形式選擇**：導航-A 種子是**內容要求**（每個關鍵概念都要有 symbol 種子，由角度一 audit 驗證）。**形式**依符號數量選擇：**內嵌種子（概念旁直接附 symbol）為預設** —— 不另開段落，最少 token 達全覆蓋；少量符號用描述性文字，不強制建表。

**大模組 selectivity 靠分組結構，不靠編排格式**：symbol 多時，關鍵不是「內嵌 vs 集中表格」，是用 **### 類別小標題**（如 `### 均線 / 動量 / 波動率 / 量能`）把長清單分組 —— 線性掃描降為「定位分組 + 小範圍掃描」，幾乎不增加 token。

**禁止標題變體**：導航表統一「模組導航」，**禁止** "Navigation" / "導航" / "Navigation Table" 等變體 — 多種標題讓 `rg "模組導航"` 漏掉其他寫法，是 LSP 時代 audit/sync 的機械識別障礙。

**設計決策類**：同義的「關鍵設計決策」/「核心設計決策」/「設計決策」統一為 `## 設計決策`；語義不同的「設計理由」(why) /「設計約束」(constraint) /「設計原則」(principle) 保留，不合併。

### 導航 Decoder Test（自檢）

寫完 instruction file 後，不查源碼，嘗試回答：
1. 「我要修改 X 的邏輯，核心符號是什麼？」→ 能給出 class/function 名？（檔案路徑由 LSP `workspaceSymbol` / `goToDefinition` 解析即可）
2. 「Y 這個概念在哪裡實作？」→ 能指向 symbol name？
3. 「Z 的上游資料從哪來？」→ 能追蹤到上游步驟和產出型別？

**機械驗證**：文檔提到的 symbol，用 `workspaceSymbol "<name>"` 確認可解析 —— 比 `test -f file.py` 更準（直接驗證符號存在且 LSP 找得到）。

任一問題無法回答 → 補充導航指引。

<!-- bundle: skip-end -->
## 品質標準

- **導航優先**: 每個關鍵概念都有 symbol 種子（位置由 LSP 解析）
- **簡潔**: 避免冗餘描述，專注核心信息
- **明確**: 避免模糊詞彙（「大概」「可能」「應該」）
- **可操作**: 提供具體執行步驟和範例
- **可維護**: 結構清晰，易於更新
