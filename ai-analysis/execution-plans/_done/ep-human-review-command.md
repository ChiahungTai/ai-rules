# EP: `/human-review` — 人工導向代碼審查命令

## 研究摘要

三個平行研究 agent 已完成調查：
1. **Pattern Radar 偵測策略** — enum/function/data structure/import 四類偵測、信心度公式、LSP+rg 操作
2. **視覺化設計** — Diff Map / Symbol Inventory / Pattern Radar 的 console ASCII + MD Mermaid 模板、大小自適應
3. **互動 UX** — 命令結構、6 種 Human 觀察類型、Phase 2 調查協議、邊界案例

## EP Review 修正記錄

> **審查者**：獨立 Explore agent（技術可行性 + Pattern Alignment + 下游依賴 + 邊界條件）

| # | 嚴重度 | 問題 | 修正狀態 | 修正位置 |
|---|--------|------|---------|---------|
| 1 | 🔴 Critical | Enum regex 被 class 先匹配到，永遠不觸發 | ✅ 已修正 | S2 Symbol Inventory 提取邏輯：改為 more-specific-first ordering（enum 在 class 之前） |
| 11 | 🔴 Critical | Subagent worktree 中 LSP 不可用，無 fallback | ✅ 已修正 | S2 Pattern Radar 偵測流程 Phase B：新增 LSP Degradation 對照表（workspaceSymbol→rg、hover→Read、findReferences→rg） |
| 3 | 🟡 Important | 信心度因子作用域未說明，可能誤加 `—` 欄位 | ✅ 已修正 | S2 Pattern Radar 信心度表格後新增「因子作用域約束」說明 |
| 7 | 🟡 Important | MD 模板提議 classDiagram 但專案無先例 | ✅ 已修正 | S2 檔案結構改為統一使用 flowchart |
| 12 | 🟡 Important | Non-Python files（.md/.yaml）未處理 | ✅ 已修正 | S4 邊界案例新增 non-Python 和 binary files 處理規則 |
| 13 | 🟡 Important | Binary files 未處理 | ✅ 已修正 | 同上 |
| DR-1 | 🟢 Dry Run | async pattern 順序未標注（與 enum 同理） | ✅ 已修正 | S2 Symbol Inventory：async 加註「必須在 function 之前」 |
| DR-2 | 🟢 Dry Run | Human 不明確終止時無 Review Summary | ✅ 已修正 | S2 Phase 1→2 過渡：新增「完成審查後說 done 或 summary 產出最終報告」提示 |

---

## UC 盤點

### Backlog 關聯
無（ai-rules 專案無 .kanban/ 目錄）

### SYSTEM-MAP 影響
無

### 掃描範圍
- `commands/code-review.md` — scope handling、effort 偵測、輸出格式
- `commands/illustrate.md` — console/md 雙模式、現有 code 優先原則
- `commands/followup-review.md` — 互動式驗證模式
- `commands/judge-review.md` — 三態決策框架
- `commands/claude/_common/workflow-review-pattern.md` — Workflow 平行 agent 協調
- `skills/mermaid/SKILL.md` — Mermaid 約束（3 style max、安全色、emoji-first）
- `skills/code-review-and-quality/SKILL.md` — LSP 輔助審查方法
- `rules/lsp-navigation.md` — LSP 操作決策樹

### 既有 UC 狀態
| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| LLM 代碼審查 | ✅ | commands/code-review.md | 不受影響 | /human-review 與 /code-review 互補 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| Human-led code review with Pattern Radar + Interactive Investigation | 📋 | commands/human-review.md |

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | Review uncommitted | `/human-review` | Diff Map + Symbol Inventory + Pattern Radar → interactive | 無 | Human Review 全流程 |
| SM-2 | Review specific commit | `/human-review abc1234` | 偵測 commit hash → `git diff abc~1 abc` → same pipeline | 該 commit 的 diff | Human Review 全流程 |
| SM-3 | Review branch | `/human-review feat/xxx main` | Branch diff → same pipeline | base branch ancestor | Human Review 全流程 |
| SM-4 | Empty diff | Clean working tree | Helpful error + scope suggestions | — | — |
| SM-5 | Large diff (>500 lines) | 大型 branch diff | Module-level summary + drill-down prompts | — | Human Review (大型) |
| SM-6 | Pattern Radar clean | 小而乾淨的 diff | "Clean" report listing what was scanned | — | — |
| SM-7 | Human spots duplicate enum | Phase 2 互動 | LLM → LSP workspaceSymbol + rg → 確認/否認 + 影響範圍 | Phase 1 output | Interactive Investigation |
| SM-8 | Human asks impact | 「這改動影響 demo 嗎？」 | LLM → LSP findReferences + rg 搜 demo/lab → caller chain | — | Interactive Investigation |
| SM-9 | Human says done | `done` / `summary` | Final Review Summary（confirmed findings + false alarms + action items） | — | — |
| SM-10 | Merge commit | `/human-review abc1234` 為 merge | 提示雙 parent，預設用 parent 1，可切換 | parent 選擇 | — |
| SM-11 | Human asks consistency | 「error handling 跟其他地方一致嗎？」 | LLM → rg 搜 pattern → Read 代表實作 → 比對 | — | Interactive Investigation |

消費場景（提煉自矩陣，供 Capabilities 使用）：
- **視覺化改動總覽**：`/human-review` 自動產出 Diff Map + Symbol Inventory + Pattern Radar，human 5 秒內掌握改動全貌
- **互動式盲區調查**：Human 指出可疑處（重複、漏用、不一致），LLM 用 LSP+rg 精確查證並回報
- **多 scope 審查**：支援 uncommitted / commit hash / branch，與 /code-review 語法一致

---

## 段落劃分原則

- **S1** 是檔案骨架，後續段落在此基礎上擴展
- **S2** 和 **S3** 可平行實作（Phase 1 vs Phase 2），但共享 scope 變數
- **S4** 是收尾，依賴 S1-S3 全部完成
- 語義約束：Phase 1 的 Pattern Radar 輸出格式必須與 Phase 2 的調查入口點一致（suspect ID 跨 phase 引用）

---

## S1: Command Foundation + Scope Handling

### Context

建立命令檔案骨架：YAML frontmatter、scope 解析、執行模式選擇、Phase 概覽。

**UC 引用**：實作「Human-led code review with Pattern Radar + Interactive Investigation」

**依賴關係**：
- 無外部依賴（第一個段落）
- 後續 S2/S3/S4 在此骨架上擴展

**語義約束**：
- 與 S2/S3 共享：scope 類型（uncommitted/commit/branch）決定 diff 取得方式
- 與 S2/S3 共享：effort level 決定 Phase 1 用 Workflow 或 Main LLM

**基礎設施盤點**：
- `commands/code-review.md` — YAML frontmatter 格式、scope handling table
- `commands/illustrate.md` — console/md 雙模式設計
- `commands/claude/_common/workflow-review-pattern.md` — Workflow schema（DimensionVerdict）

**依賴錨點**：
- scope handling table → 定義 `commands/code-review.md:審查範圍` / 消費 `S2 Phase 1` + `S3 Phase 2`
- effort detection → 定義 `commands/code-review.md:審查模式選擇` / 消費 `S2 Workflow agents`
- frontmatter format → 定義 `commands/CLAUDE.md` / 消費 `S1` 自己

**技術選型**：單一 Markdown 命令檔案，無需新 skill

**成功標準**：檔案可以被 `/human-review` 正確載入，frontmatter 符合 commands/CLAUDE.md 規範

### 核心實作要點

1. **YAML Frontmatter**
   - `description`: 「人工導向代碼審查 — Human 提線索，LLM 做調查。/human-review [scope]」
   - `when_to_use`: 英文說明觸發場景
   - `usage`: `/human-review [target] [base]`
   - `argument-hint`: 無參數審查 uncommitted / commit hash 審查該 commit / branch 名稱審查該 branch
   - `allowed-tools`: Read, Grep, Glob, Bash, Agent, Workflow

2. **Scope Handling**
   - 三種 scope，與 /code-review 完全對齊
   - Commit hash 偵測：匹配 `[0-9a-f]{7,40}` → commit mode
   - 否則視為 branch name

3. **執行模式選擇**
   - Phase 1: effort = ultracode/xhigh + max-agents > 1 → Workflow（平行 3 agents）
   - Phase 1: effort < ultracode → Main LLM（序列）
   - Phase 2: 永遠 Main LLM（互動需要 conversation state）
   - 印出確認：`[Human Review] Phase 1: effort=X, workflow=Y, max=N`

4. **Phase 概覽**
   - Phase 1: 自動產出視覺化概覽（Diff Map + Symbol Inventory + Pattern Radar）
   - Phase 2: 互動式調查（Human 指揮，LLM 偵查）

### Pseudo Code

```markdown
---
description: "人工導向代碼審查 — Human 提線索，LLM 做調查。/human-review [scope]"
when_to_use: "Human-led code review ..."
usage: "/human-review [target] [base]"
argument-hint: "..."
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /human-review — 人工導向代碼審查

> 核心理念：Human 的聯想記憶 + LLM 的精確搜尋 = 最強審查組合
> 不是 LLM 審 code 給 human 看，是 Human 審 LLM 的盲區。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [mermaid](../skills/mermaid/SKILL.md) — MD 模式圖表（`--md` 時引用）

按需讀取：
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — LSP 輔助調查方法

## 審查範圍

| 用法 | 實際執行 | 場景 |
|------|---------|------|
| `/human-review` | `git diff` + `git diff --cached` + `git ls-files --others --exclude-standard` | Uncommitted（預設） |
| `/human-review abc1234` | `git diff abc1234~1 abc1234` | 單一 commit（hash 偵測） |
| `/human-review feat/xxx` | `git diff HEAD...feat/xxx` | Feature branch |
| `/human-review feat/xxx main` | `git diff main...feat/xxx` | Branch + base |

**Commit hash 偵測**：第一個參數匹配 `[0-9a-f]{7,40}` → commit mode。否則視為 branch name。

**Output 模式**：
| 旗標 | 說明 |
|------|------|
| 預設（console） | ASCII 圖表，terminal 內即時產出 |
| `--md` | Mermaid 圖表，寫檔 `ai-analysis/reports/human-review-{scope}.md` |

## 執行模式選擇

偵測 effort level 和 max-agents（查 agent-workflow 並發表）。

**Phase 1（視覺化概覽）**：

| 條件 | 模式 | Agent 數量 |
|------|------|-----------|
| effort = ultracode/xhigh 且 max-agents > 1 | Workflow（平行 3 agents） | ≤ max-agents |
| effort < ultracode 或 max-agents = 1 | Main LLM（序列） | 0 |

**Phase 2（互動式調查）**：永遠 Main LLM（互動需要 conversation state）

印出確認：`[Human Review] Phase 1: effort=X, workflow=Y, max=N`

## 兩階段流程

### Phase 1: 視覺化概覽（LLM 自動產出，Human 看）
[→ S2 詳細定義]

### Phase 2: 互動式調查（Human 指揮，LLM 偵查）
[→ S3 詳細定義]
```

### 驗證策略

- Read 完成的檔案，確認 frontmatter 符合 `commands/CLAUDE.md` 規範
- 確認 scope handling 與 `/code-review` 一致
- 確認 commit hash 偵測邏輯正確
- 確認 Phase 1/Phase 2 概覽清晰

---

## S2: Phase 1 — Visual Overview + Pattern Radar

### Context

Phase 1 的核心：三個視覺化元件（Diff Map、Symbol Inventory、Pattern Radar）+ 大小自適應。

**UC 引用**：實作「視覺化改動總覽」（SM-1/2/3/5/6）

**依賴關係**：
- 依賴 S1（scope handling、執行模式）
- 被依賴於 S3（Phase 2 的調查入口點是 Pattern Radar 的 suspect ID）

**語義約束**：
- 與 S3 共享：Pattern Radar 的 suspect ID 格式（PR-001、PR-002...）在 Phase 2 被引用
- 與 S3 共享：Symbol Inventory 的 symbol name 在 Phase 2 的調查中被引用

**基礎設施盤點**：
- `skills/mermaid/SKILL.md` — Mermaid 約束（3 style max、安全色 #10b981/#ef4444/#f59e0b/#3b82f6、emoji-first、禁 %%init%%）
- `rules/lsp-navigation.md` — LSP 操作（workspaceSymbol、findReferences、hover、documentSymbol）
- `commands/claude/_common/workflow-review-pattern.md` — DimensionVerdict schema

**依賴錨點**：
- Mermaid 約束 → 定義 `skills/mermaid/SKILL.md` / 消費 `S2 MD 模式輸出`
- LSP workspaceSymbol → 定義 `rules/lsp-navigation.md` / 消費 `S2 Pattern Radar 偵測`
- rg patterns → 定義 `rules/modern-cli-preference.md` / 消費 `S2 Symbol extraction`

**技術選型**：
- Console 用 ASCII box drawing characters（╔═╗║╚╝─├┤）
- MD 用 Mermaid flowchart + classDiagram
- Pattern Radar 偵測：LSP workspaceSymbol 為主、rg 為輔

**成功標準**：Phase 1 輸出能讓 human 5 秒內掌握改動全貌

### 核心實作要點

1. **Diff Map（改動地圖）**
   - 按模組分組的檔案樹 + 改動行數（+N/-M）
   - Internal Dependencies（import 分析）
   - 大小自適應：
     - Small (<50 lines)：完整檔案樹
     - Medium (50-500)：按模組分組 + dependency flow
     - Large (>500)：模組級摘要 + drill-down 提示
   - Console：ASCII tree
   - MD：Mermaid flowchart

2. **Symbol Inventory（符號清單）**
   - 從 diff 提取 symbols：class、def、async def、enum、constant（ALL_CAPS）
   - 狀態判定：NEW / MODIFIED / DELETED / RENAMED
   - 跨 Repo 相似搜尋：LSP workspaceSymbol + rg
   - 大小自適應：small 全顯示 / medium 按模組分組 / large 只顯示摘要 + drill-down

3. **Pattern Radar（模式雷達）**
   - 四類偵測策略（按 ROI 排序）：

   | 類型 | 觸發 | 搜尋方法 | ROI |
   |------|------|---------|-----|
   | Enum 重複 | diff 中有 `class X(Enum)` | LSP workspaceSymbol + rg member values | 最高 |
   | Function 重複 | diff 中有 `def X()` | LSP workspaceSymbol + outgoingCalls | 高 |
   | Data Structure 重複 | diff 中有 `@dataclass` / `TypedDict` | rg field name overlap (Jaccard) | 中 |
   | Import 漏用 | diff 中有 `from X import Y` | LSP documentSymbol + `__all__` | 低（FP 高） |

   - 信心度公式（加權）：

   | 因子 | Enum | Function | Data Struct | Import |
   |------|------|----------|-------------|--------|
   | 名稱相似 | +3 | +5 | +3 | — |
   | 值/簽名重疊 | +4 | +4 | +6 | — |
   | Import 路徑已通 | +3 | — | +3 | +4 |
   | 呼叫圖重疊 | — | +4 | — | — |
   | 欄位重疊 >60% | — | — | +5 | — |
   | diff 重實作已有功能 | — | — | — | +6 |

   - 門檻：HIGH ≥ 7 / MEDIUM 4-6 / LOW 1-3
   - 只展示 HIGH + MEDIUM；LOW 收在 `dup-detail` drill-down
   - **因子作用域約束**：`—` 欄位表示「該因子不適用於該類別」，計算時只加總對應類別標有數值的因子

4. **Phase 1 → Phase 2 過渡**
   - 展示完三個元件後，印出互動邀請
   - 列出可用指令（drill / symbols / dup-detail / deep / focus / explain）
   - 明確提示終止方式：`完成審查後說 done 或 summary 產出最終報告`
   - 等待 human 輸入

### Pseudo Code

#### Diff Map 提取邏輯

```
Step 1: git diff --stat → per-file (+N/-M)
Step 2: Parse file paths → group by top-level directory
Step 3: Import analysis → for each changed file, extract imports
        → if file A imports file B and both changed → dependency edge (⚠️)
Step 4: Render → ASCII tree (console) or Mermaid flowchart (--md)
```

#### Symbol Inventory 提取邏輯

```
Trigger patterns (match +lines in diff, **more-specific-first ordering**):
  enum:     ^\+class\s+(\w+)\(.*(?:Enum|StrEnum|IntEnum|Flag|IntFlag)  ← 必須在 class 之前
  class:    ^\+class\s+(\w+)
  async:    ^\+async\s+def\s+(\w+)\s*\(  ← 必須在 function 之前
  function: ^\+def\s+(\w+)\s*\(
  constant: ^\+([A-Z_][A-Z0-9_]+)\s*=  ← 僅 module-level（^ 錨點排除 class 內部）
  注意：constant 會匹配 LOGGER = logging.getLogger() 等 singleton，在 Symbol Inventory 中標為 INFO 即可

Status detection:
  NEW: symbol only in +lines (no matching -line)
  MODIFIED: symbol name in both + and - lines
  DELETED: symbol only in -lines
  RENAMED: deleted + new pair in same file/region

Cross-reference search:
  For each NEW symbol → LSP workspaceSymbol(name)
  + rg -t py "class\s+({name}|{stemmed_name})" for fallback
```

#### Pattern Radar 偵測流程

```
Phase A: Extract (pure text)
  → Parse diff for new symbols → classify by category
  → Extract signatures / field names / member values

Phase B: Search (LSP + rg, parallel)
  → For each new symbol: LSP workspaceSymbol(name)
  → For each new symbol: rg for name/value similarity
  → For imports: LSP documentSymbol on imported modules
  ⚠️ LSP Degradation（subagent worktree 中 LSP 不可用）：
    workspaceSymbol → rg -t py "class\s+(\w+)" --no-filename -o -r '$1'
    hover → Read file directly
    findReferences → rg -t py "symbol_name"（text match，可能漏 dynamic refs）
    documentSymbol → rg -t py "^\s*(class|def)\s+" file.py

Phase C: Score (computation)
  → Compute confidence per finding
  → Filter: only report ≥ MEDIUM in main output
  → Sort: confidence desc, then category priority

Phase D: Verify (LSP, targeted)
  → For HIGH findings: LSP findReferences on existing symbol
  → Confirm existing symbol is used (not dead code itself)
  → Downgrade if existing has 0 references
```

#### 檔案結構（command 檔案內的 section）

```
commands/human-review.md
  ├── frontmatter (S1)
  ├── 審查範圍 (S1)
  ├── 執行模式選擇 (S1)
  ├── Phase 1: 視覺化概覽
  │   ├── Diff Map
  │   │   ├── 提取邏輯
  │   │   ├── Console 模板（ASCII tree，3 sizes）
  │   │   └── MD 模板（Mermaid flowchart）
  │   ├── Symbol Inventory
  │   │   ├── 提取 patterns
  │   │   ├── Console 模板（表格，3 sizes）
  │   │   └── MD 模板（Markdown tables + Mermaid flowchart；注意：專案無 classDiagram 先例，統一用 flowchart）
  │   ├── Pattern Radar
  │   │   ├── 偵測策略（4 types + confidence scoring）
  │   │   ├── Console 模板（🔴🟡🟢 分級列表）
  │   │   └── MD 模板（table + Mermaid impact flow）
  │   └── Phase 1 → Phase 2 過渡
  └── Phase 2: 互動式調查 [→ S3]
```

### 驗證策略

- Read 完成的 section，確認 Mermaid 符合 skill 約束（3 style、安全色、emoji-first）
- 確認 Diff Map 的 ASCII 模板在不同 terminal 寬度下可讀
- 確認 Symbol Inventory 的 regex patterns 可正確提取 Python symbols
- 確認 Pattern Radar 的信心度公式一致且門檻合理
- 確認大小自適應邏輯完整（small/medium/large 三級）

---

## S3: Phase 2 — Interactive Investigation Protocol

### Context

Phase 2 的核心：6 種 Human 觀察類型、對應的 LLM 調查協議、Session 狀態追蹤、最終 Review Summary。

**UC 引用**：實作「互動式盲區調查」（SM-7/8/9/11）

**依賴關係**：
- 依賴 S1（scope handling）
- 依賴 S2（Phase 1 的 Pattern Radar suspect ID、Symbol Inventory symbol name）

**語義約束**：
- 與 S2 共享：suspect ID 格式（PR-001）和 symbol name 在 Phase 2 被引用
- 與 S4 共享：Review Summary 格式

**基礎設施盤點**：
- `commands/followup-review.md` — 互動式驗證模式（兩種 mode 的參考）
- `commands/judge-review.md` — 三態決策（adopt/reject/needs-confirmation）
- `skills/code-review-and-quality/SKILL.md` — LSP 輔助審查（findReferences、incomingCalls）

**依賴錨點**：
- 6 observation types → 定義 `S3` / 消費 `S2 Pattern Radar output` + `S2 Symbol Inventory`
- LSP operations → 定義 `rules/lsp-navigation.md` / 消費 `S3 調查協議`
- Review Summary → 定義 `S3` / 消費 `S4` (edge case handling)

**技術選型**：Main LLM 直接執行（不 spawn agent，需要 conversation state）

**成功標準**：Human 能用自然語言指出可疑處，LLM 在 1-2 輪內完成調查並回報

### 核心實作要點

1. **6 種 Human 觀察類型**

| Type | Human 說什麼 | LLM 調查工具 | 回報格式 |
|------|------------|-------------|---------|
| 🔍 Suspicion | 「L45 看起來不對」 | Read + LSP hover/findReferences + rg | Finding + Evidence + Impact + Recommendation |
| 📖 Understanding | 「這在幹嘛？」 | LSP goToDefinition + incomingCalls/outgoingCalls | What + How + Why + Connections |
| 🔗 Impact | 「這影響 demo 嗎？」 | LSP findReferences + rg 搜 demo/lab | Connection Found/None + Call Chain + Affected Consumers |
| 🔄 Consistency | 「error handling 一致嗎？」 | rg 搜 pattern + Read 2-3 代表實作 | Current vs Norm (N examples) + Verdict |
| 🤿 Deep Dive | 「深入看 X」 | Full sub-graph (Read + incomingCalls + outgoingCalls) | Extended Finding |
| 💬 Free-form | 任意問題 | 自動分類或直接回答 + LSP/rg | 依分類 |

2. **LLM 調查工具箱（對應觀察類型）**

| 觀察類型 | LSP 操作 | rg 操作 |
|---------|---------|--------|
| Suspicion | hover → findReferences → goToDefinition | 搜相似 pattern |
| Understanding | goToDefinition → hover → incomingCalls → outgoingCalls | 搜 docstring / usage |
| Impact | findReferences → incomingCalls | rg 搜 demo_*.py, lab/, examples/ |
| Consistency | — | rg 搜 pattern across codebase |
| Deep Dive | incomingCalls + outgoingCalls (full sub-graph) | rg + Read (complete files) |

3. **Session 狀態追蹤**
   - 每次調查後更新 running tally：
   ```
   ---
   Investigations: 4 | Findings: 2 confirmed, 1 false alarm, 1 needs discussion
   Action items: 2
   ---
   ```

4. **終止信號**

| Signal | 行為 |
|--------|------|
| `done` / `summary` / `that's all` / `looks good` | 產出 Final Review Summary |
| `skip`（Phase 2 開始時） | 跳過 Phase 2，只輸出 Phase 1 |

5. **Final Review Summary**
   - Review Context（scope、files、investigations count）
   - Confirmed Findings（severity + file:line + description + action）
   - False Alarms（initial suspicion + why safe）
   - Items for Discussion（open questions）
   - Recommended Next Steps（/code-review → fix → /commit）

### Pseudo Code

#### 調查協議模板

```
### [Investigation N]: [Title]

**Type**: Suspicion / Understanding / Impact / Consistency / Deep Dive
**Scope**: [files and symbols investigated]
**Tools used**: Read, LSP (hover/findReferences/goToDefinition), rg

**Finding**: [one-line verdict]

**Details**:
[Evidence and reasoning]

**Recommendation**: [actionable item or "no action needed"]
```

#### Phase 2 → Phase 1 drill-down 指令

```
Human 可用的互動指令：
  drill <module>      — File-level detail for a module（大型 diff）
  symbols <path>      — Full symbol table for a file
  dup-detail          — All similarity matches with scores（含 LOW confidence）
  deep <suspect#>     — Deep analysis of a Pattern Radar suspect
  focus <file>        — 只看影響該檔案的條目
  explain <symbol>    — 解釋某 symbol 的功能和連結

或直接用自然語言描述可疑處。
```

#### Final Review Summary 模板

```markdown
## Human Review Summary

### Review Context
- Scope: [uncommitted / commit abc / branch feat/xxx vs main]
- Files: N | Symbols: M | Pattern Radar suspects: K
- Investigations: L

### Confirmed Findings
| # | Severity | File:Line | Description | Action |
|---|----------|-----------|-------------|--------|
| 1 | Important | ... | ... | ... |

### False Alarms (confirmed safe)
| # | File:Line | Initial Suspicion | Why Safe |
|---|-----------|------------------|----------|

### Items for Discussion
| # | Topic | Question |
|---|-------|----------|

### Recommended Next Steps
1. Fix confirmed findings
2. `/code-review` for automated six-axis analysis
3. `/commit` when ready
```

### 驗證策略

- 確認 6 種觀察類型各有完整的 LSP + rg 工具映射
- 確認 Session 追蹤格式在多次調查後仍然可讀
- 確認 Final Review Summary 格式可獨立消費（不依賴 Phase 1/2 的上下文）
- 確認終止信號覆蓋所有合理的人類表達方式

---

## S4: Edge Cases + Integration + Assembly

### Context

收尾：邊界案例、與 /code-review 的關係、檔案完整性檢查。

**UC 引用**：補充（SM-4 empty diff、SM-10 merge commit）

**依賴關係**：
- 依賴 S1（scope handling）、S2（Phase 1）、S3（Phase 2）

**語義約束**：無新增

**基礎設施盤點**：
- `commands/code-review.md` — 審查流程定位

**依賴錨點**：
- Edge case handling → 定義 `S4` / 消費 `S1 scope logic`

**成功標準**：完整命令檔案通過 `/consistency` 檢查

### 核心實作要點

1. **邊界案例**

   | 案例 | 處理方式 |
   |------|---------|
   | Empty diff | 印出 "No changes found" + scope suggestions |
   | New file（無 before state） | Symbol Inventory 全標 NEW，Pattern Radar 掃全檔 |
   | Merge commit | 提示雙 parent，預設 parent 1，可切換 |
   | Large diff (>500 lines) | Phase 1 只產出模組級摘要 + drill-down 提示 |
   | Pattern Radar clean | "Clean" report listing what was scanned |
   | Ambiguous scope (hash vs branch) | 提示兩種可能，讓 human 選 |
   | Non-Python files（.md/.yaml/.toml/.json） | Diff Map 照常列出；Symbol Inventory / Pattern Radar **跳過**（regex 僅匹配 Python），在 Diff Map 中標注 `[non-Python, skipped]` |
   | Binary files | Diff Map 列出並標注 `[binary]`；Symbol Inventory / Pattern Radar 跳過 |

2. **與 /code-review 的關係**

   ```
   推薦順序：
   複雜變更：/human-review（human 找盲區）→ /code-review（LLM 系統審查）→ /commit
   常規變更：/code-review（LLM 自動審查）→ fix → /human-review（human 驗證）→ /commit
   ```

   兩者獨立，可自由組合。

3. **流程位置**

   ```
   /spec → /execution-plan → /build → /code-review 或 /human-review → /commit
   ```

4. **檔案完整性檢查**
   - frontmatter 符合 commands/CLAUDE.md 規範
   - scope handling 與 /code-review 一致
   - Mermaid 圖表符合 mermaid skill 約束
   - 無矛盾或重複描述

### Pseudo Code

（邊界案例的處理模板已嵌入 S2/S3 的對應 section）

### 驗證策略

- 對完成檔案執行 `/consistency commands/human-review.md`
- 交叉比對 /code-review 的 scope handling 語法是否一致
- 確認 frontmatter 格式正確
- 確認所有 cross-reference links 有效

---

## 整合策略

- S1 建立檔案骨架 → S2/S3 可平行擴展各自 section → S4 收尾
- S2 和 S3 共享 suspect ID 和 symbol name 格式，必須在 S1 中定義
- 最終產出：`commands/human-review.md`（單一檔案，無需新 skill）

## 收尾步驟

1. CLAUDE.md 更新：ai-rules 專案的 CLAUDE.md 加入 `/human-review` 的說明
2. 無 Capabilities/Kanban 更新（ai-rules 專案不用 UC-Driven）
3. 無 SYSTEM-MAP 更新
4. 完整性檢查：`/consistency commands/human-review.md`
