---
description: "人工導向代碼審查 — Human 提線索，LLM 做調查。/human-review [scope]"
when_to_use: "Human-led code review where the human points out suspicions and the LLM investigates with LSP + rg. Produces a visual Diff Map, Symbol Inventory, and Pattern Radar first, then enters interactive investigation mode. Use for spotting duplicate code, missed reuse, and architectural drift that LLM-only review misses."
usage: "/human-review [target] [base]"
argument-hint: "無參數審查 uncommitted / commit hash 審查該 commit / branch 名稱審查該 branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /human-review — 人工導向代碼審查

> **核心理念**：Human 的聯想記憶 + LLM 的精確搜尋 = 最強審查組合
> 不是 LLM 審 code 給 human 看，是 **Human 審 LLM 的盲區**。

LLM review 回答「這段 code 正確嗎？」；Human review 回答「這段 code 有沒有重新造輪子？」兩者互補。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [mermaid](../skills/mermaid/SKILL.md) — MD 模式圖表（`--md` 時引用）

按需讀取：
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — LSP 輔助調查方法（Phase 2 用）

---

## 審查範圍

| 用法 | 實際執行 | 場景 |
|------|---------|------|
| `/human-review` | `git diff` + `git diff --cached` + `git ls-files --others --exclude-standard` | Uncommitted（預設，含 untracked） |
| `/human-review abc1234` | `git diff abc1234~1 abc1234` | 單一 commit（hash 偵測） |
| `/human-review feat/xxx` | `git diff HEAD...feat/xxx` | Feature branch |
| `/human-review feat/xxx main` | `git diff main...feat/xxx` | Branch + 指定 base |

**Commit hash 偵測**：第一個參數匹配 `[0-9a-f]{7,40}` → commit mode。否則視為 branch name。

**Output 模式**：

| 旗標 | 說明 |
|------|------|
| 預設（console） | ASCII 圖表，terminal 內即時產出 + 互動 |
| `--md` | Mermaid 圖表，寫檔 `ai-analysis/reports/human-review-{scope}.md`，Phase 2 仍為 terminal 互動 |

---

## 執行模式選擇

偵測 effort level 和 max-agents（查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md)）。

**Phase 1（視覺化概覽）**：

| 條件 | 模式 | Agent 數量 |
|------|------|-----------|
| effort = ultracode/xhigh 且 max-agents > 1 | Workflow（平行 3 agents） | ≤ max-agents |
| effort < ultracode 或 max-agents = 1 | Main LLM（序列） | 0 |

**Phase 2（互動式調查）**：永遠 Main LLM（互動需要 conversation state，不能 spawn agent）。

印出確認：`[Human Review] Phase 1: effort=X, workflow=Y, max=N`

---

## Phase 1: 視覺化概覽

> **目標**：讓 human 5 秒內掌握改動全貌，觸發聯想記憶。

三個元件依序展示：Diff Map → Symbol Inventory → Pattern Radar。

### Diff Map（改動地圖）

**提取邏輯**：
1. `git diff --stat` → per-file (+N/-M)
2. Parse file paths → group by top-level directory
3. Import analysis → for each changed file, extract `import` / `from ... import`
   → if file A imports file B and both changed → dependency edge（⚠️ co-change risk）
4. Render → ASCII tree（console）or Mermaid flowchart（`--md`）

**大小自適應**：

| Size | 觸發 | Diff Map 行為 |
|------|------|--------------|
| Small | <50 lines changed | 完整檔案樹，每檔案列 +N/-M |
| Medium | 50-500 lines | 按模組分組 + dependency flow |
| Large | >500 lines | 模組級摘要（只列 module + file count + total +N/-M）+ drill-down 提示 |

**Console 輸出格式**（Medium 範例）：

```
🗺️  Diff Map — 3 modules, 11 files     +312 -87 = +225

📦 data/ (4 files) .......................... +156 -34
├── fetcher.py ......................... +89 -12
│   └─ imports: transform, indicators
├── transform.py ..................... +34 -8
└── gateway.py ...................... +22 -6  🆕

📦 tests/ (4 files) .......................... +58 -25
└── test_fetcher.py .................... +32 -11

── Internal Dependencies ───────────────────
fetcher.py ──uses──▶ transform.py  (both changed) ⚠️
fetcher.py ──uses──▶ gateway.py    (new dep)    🆕

🆕 = new file   ⚠️ = co-changed dependency
```

**MD 輸出**（`--md`）：Mermaid flowchart，遵循 [mermaid skill](../skills/mermaid/SKILL.md) 約束（3 style max、安全色、emoji-first、禁 `%%init%%`）。

### Symbol Inventory（符號清單）

**提取 patterns**（match `+` lines in diff，按表中順序匹配，**first match wins**）：

| Pattern | 擷取目標 | 排序要求 |
|---------|---------|---------|
| `^\+class\s+(\w+)\(.*(?:Enum\|StrEnum\|IntEnum\|Flag\|IntFlag)` | Enum class | 必須在 class 之前 |
| `^\+class\s+(\w+)` | Class | — |
| `^\+async\s+def\s+(\w+)\s*\(` | Async function | 必須在 function 之前 |
| `^\+def\s+(\w+)\s*\(` | Function | — |
| `^\+([A-Z_][A-Z0-9_]+)\s*=` | Module-level constant | 注意：也匹配 singleton（如 `LOGGER = ...`），標 INFO 即可 |

**狀態判定**：NEW（僅 +lines）/ MODIFIED（+ 和 - 都有）/ DELETED（僅 -lines）/ RENAMED（同檔同區 deleted+new pair）

**跨 Repo 相似搜尋**：每個 NEW symbol → `LSP workspaceSymbol(name)` + `rg -t py` fallback

**大小自適應**：Small 全顯示 / Medium 按模組分組 + top 10 / Large 只顯示摘要計數 + drill-down

**Console 輸出格式**：

```
📋 Symbol Inventory                                     8 symbols

Symbol                Type     Location                  Status
────────────────────── ──────── ──────────────────────── ──────────
TradeAction           enum     data/fetcher.py:15        🆕 NEW
TradeAction.BUY       member   data/fetcher.py:16        🆕 NEW
_fetch_daily          func     data/fetcher.py:42        ✏️ MOD
MAX_RETRIES           const    data/fetcher.py:8         🆕 NEW

Cross-Reference: Similar Existing Symbols
TradeAction  ↔ TradeSide (types.py:23)    ⚠️ 語義可能重複
```

### Pattern Radar（模式雷達）

> **核心理念**：自動偵測「可能重複/漏用」的嫌疑清單，觸發 human 的聯想記憶。寧漏勿誤——false positive 是毒藥。

**四類偵測策略**（按 ROI 排序）：

| 類型 | 觸發條件 | 搜尋方法 | ROI |
|------|---------|---------|-----|
| Enum 重複 | diff 中有 `class X(Enum)` | LSP `workspaceSymbol` + `rg` member values | 最高 |
| Function 重複 | diff 中有 `def X()` | LSP `workspaceSymbol` + `outgoingCalls` 比對 | 高 |
| Data Structure 重複 | diff 中有 `@dataclass` / `TypedDict` | `rg` field name overlap（Jaccard similarity） | 中 |
| Import 漏用 | diff 中有 `from X import Y` | LSP `documentSymbol` + `__all__` 比對 | 低（FP 高） |

**偵測流程**：

```
Phase A: Extract — 從 diff 解析新 symbols → 分類 → 提取簽名/欄位/成員值
Phase B: Search  — LSP workspaceSymbol + rg 平行搜尋（⚠️ subagent worktree 中 LSP 不可用，降級為 rg-only）
Phase C: Score   — 計算信心度 → 過濾（只展示 ≥ MEDIUM）→ 排序（信心度 desc → 類型 ROI）
Phase D: Verify  — HIGH findings 用 LSP findReferences 確認 existing symbol 確實被使用（非 dead code）
```

**信心度公式**（加權加總，只計算對應類別標有數值的因子，`—` 表示不適用）：

| 因子 | Enum | Function | Data Struct | Import |
|------|------|----------|-------------|--------|
| 名稱相似 | +3 | +5 | +3 | — |
| 值/簽名重疊 | +4 | +4 | +6 | — |
| Import 路徑已通 | +3 | — | +3 | +4 |
| 呼叫圖重疊 | — | +4 | — | — |
| 欄位重疊 >60% | — | — | +5 | — |
| diff 重實作已有功能 | — | — | — | +6 |

**門檻**：HIGH ≥ 7 / MEDIUM 4-6 / LOW 1-3。只展示 HIGH + MEDIUM；LOW 收在 `dup-detail` drill-down。

**LSP Degradation**（subagent worktree 中不可用時）：

| LSP 操作 | rg Fallback |
|---------|-------------|
| `workspaceSymbol` | `rg -t py "class\s+(\w+)" --no-filename -o -r '$1'` |
| `hover` | `Read` file directly |
| `findReferences` | `rg -t py "symbol_name"`（text match，可能漏 dynamic refs） |
| `documentSymbol` | `rg -t py "^\s*(class\|def)\s+" file.py` |

**Console 輸出格式**：

```
📡 Pattern Radar                                      3 suspects

🔴 HIGH
  PR-001  Enum Dup   TradeAction (fetcher.py:15)
          ↔ TradeSide (types.py:23, 12 refs)
          Evidence: same members BUY/SELL, both StrEnum, fetcher.py already imports types

🟡 MEDIUM
  PR-002  Fn Dup     _parse_response (fetcher.py:88)
          ↔ _parse_raw (parser.py:45, 5 refs)
          Evidence: same signature (str) → dict, 70% logic overlap

🟢 LOW (in dup-detail)
  PR-003  Import     from . import config — config.get_db_url() not imported

💡 這是自動偵測的嫌疑清單。你可能注意到我們漏掉的 —— 直接說，我來查證。
```

**MD 輸出**（`--md`）：Markdown 表格 + Mermaid impact flowchart。

### Phase 1 → Phase 2 過渡

展示完三個元件後，印出：

```
──────────────────────────────────────────────────
💬 Phase 1 完成。你現在可以：

  drill <module>      — 檔案級 detail（大型 diff）
  symbols <path>      — 完整 symbol table
  dup-detail          — 所有相似匹配（含 LOW confidence）
  deep <PR-XXX>       — 深入分析某個 Pattern Radar 嫌疑
  focus <file>        — 只看影響該檔案的條目
  explain <symbol>    — 解釋某 symbol 的功能和連結

  或直接用自然語言描述可疑處。
  完成審查後說 done 或 summary 產出最終報告。
──────────────────────────────────────────────────
```

---

## Phase 2: 互動式調查

> **核心理念**：Human 提線索（模糊記憶），LLM 做精確查證（LSP + rg）。

### 6 種 Human 觀察類型

| Type | Human 說什麼 | LLM 調查工具 |
|------|------------|-------------|
| 🔍 Suspicion | 「L45 看起來不對」「這個 retry 邏輯怪怪的」 | `Read` + LSP `hover`/`findReferences` + `rg` 搜相似 pattern |
| 📖 Understanding | 「這個 ChainMap 在幹嘛？」 | LSP `goToDefinition` + `incomingCalls`/`outgoingCalls` |
| 🔗 Impact | 「這改動影響 demo 嗎？」 | LSP `findReferences` + `rg` 搜 `demo_*.py`, `lab/`, `examples/` |
| 🔄 Consistency | 「error handling 跟其他地方一致嗎？」 | `rg` 搜 pattern across codebase + `Read` 2-3 代表實作 |
| 🤿 Deep Dive | 「深入看 error handling」 | Full sub-graph：`Read` + LSP `incomingCalls` + `outgoingCalls` |
| 💬 Free-form | 任意問題 | 自動分類到上述類型，或直接回答 |

### 調查協議模板

每次調查回報格式：

```
### [Investigation N]: [Title]

**Type**: Suspicion / Understanding / Impact / Consistency / Deep Dive
**Scope**: [files and symbols investigated]
**Tools used**: Read, LSP (hover/findReferences/goToDefinition), rg

**Finding**: [one-line verdict]

**Details**:
[Evidence and reasoning — 引用具體 file:line]

**Recommendation**: [actionable item or "no action needed"]
```

### Session 狀態追蹤

每次調查後更新 running tally：

```
---
Investigations: 4 | Findings: 2 confirmed, 1 false alarm, 1 needs discussion
Action items: 2
---
```

### 終止信號

| Signal | 行為 |
|--------|------|
| `done` / `summary` / `that's all` / `looks good` | 產出 Final Review Summary |
| `skip`（Phase 2 開始時） | 跳過 Phase 2，只輸出 Phase 1 |

### Final Review Summary

```
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

---

## 邊界案例處理

| 案例 | 處理方式 |
|------|---------|
| Empty diff | 印出 "No changes found" + scope suggestions（`/human-review feat/xxx` 或 `/human-review abc1234`） |
| New file（無 before state） | Symbol Inventory 全標 NEW，Pattern Radar 掃全檔（非 diff-only） |
| Merge commit | 提示雙 parent，預設用 parent 1（`git diff abc^1 abc`），可切換 parent 2 |
| Large diff (>500 lines) | Phase 1 只產出模組級摘要 + drill-down 提示，不展開完整列表 |
| Pattern Radar clean | "Clean" report 列出掃描了哪些 pattern（不是空白輸出） |
| Ambiguous scope（hash vs branch） | 提示兩種可能，讓 human 選 |
| Non-Python files（.md/.yaml/.toml/.json） | Diff Map 照常列出，標注 `[non-Python, skipped]`；Symbol Inventory / Pattern Radar 跳過 |
| Binary files | Diff Map 列出並標注 `[binary]`；Symbol Inventory / Pattern Radar 跳過 |

---

## 與 /code-review 的關係

兩者獨立，可自由組合。互補不衝突：

| | `/code-review` | `/human-review` |
|--|---------------|-----------------|
| **Driver** | LLM（自主） | Human（互動） |
| **回答什麼** | 「code 正確嗎？」 | 「code 有沒有重複造輪子？」 |
| **輸出** | 分類 findings + commit message | 調查報告 + review summary |
| **適合** | 系統化品質閘門 | Domain expert 導向的深度審查 |

**推薦順序**：

```
複雜變更：/human-review（human 找盲區）→ /code-review（LLM 系統審查）→ /commit
常規變更：/code-review（LLM 自動審查）→ fix → /human-review（human 驗證）→ /commit
```

---

## 流程位置

```
/spec → /execution-plan → [/ep-validate] → /build → /code-review 或 /human-review → /commit
```

後續：確認 findings → `/code-review`（如尚未跑）→ `/commit`
