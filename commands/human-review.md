---
description: "人類 viewport — 人用 4 lens（I/O / 架構 / 大概實作 / 驗證範圍審查）判讀 EP 或 code。/human-review [--ep <EP>] [scope]"
when_to_use: "Human-facing viewport (layer 3). Renders the human-graspable view of an Execution Plan (post-EP checkpoint) or code (post-build checkpoint) using 4 lenses: I/O contracts, architecture (Clean Code), rough implementation shape, and verification-scope review. Human judges with big principles; does NOT do line-by-line correctness or run scenarios. Use when a human needs to accept what the AI produced."
usage: "/human-review [--ep <EP路徑>] [target] [base]"
argument-hint: "--ep <EP> 審 EP / 無參數審 uncommitted / commit hash 審該 commit / branch 名稱審該 branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /human-review — 人類 viewport

> **核心理念**：人類 viewport（layer 3），source-agnostic（EP 或 code）。
> 人精力有限 → 只做 4 件擅長的事：I/O、架構、大概實作、驗證範圍審查。

不是 LLM 審 code 給 human 看（那是 `/code-review`，LLM 執行鏈）；是 **AI 渲染出人類可掌握的視角，讓人用大原則判讀**。

**不做的事**（交 LLM 執行鏈）：逐行正確性（`/code-review`）、跑測試/型別/覆蓋率（`/build` + `/audit-test`）、親跑行為場景（人定範圍、LLM 執行）。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [mermaid](../skills/mermaid/SKILL.md) — MD 模式圖表（`--md` 時引用）

按需讀取：
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — LSP 輔助調查方法（Phase 2 用）

受眾模型與三層介入見 [CLAUDE.md](../CLAUDE.md)「命令的受眾視角」；理論底層見 [acceptance-evidence](../rules/acceptance-evidence.md)。

---

## 審查範圍（source mode）

| 用法 | source | 檢查點 | 人判什麼 |
|------|--------|--------|---------|
| `/human-review --ep <EP>` | EP | post-EP | 「這是我要的系統嗎？」（I/O 契約 + 架構意圖 + 驗證範圍） |
| `/human-review` | code（uncommitted） | post-build | 「實作符不符合、架構行不行、I/O 對不對」 |
| `/human-review abc1234` | code（commit） | post-build | 同上 |
| `/human-review feat/xxx` | code（branch） | post-build | 同上 |
| `/human-review feat/xxx main` | code（branch + base） | post-build | 同上 |

**Source 偵測**：第一個參數是 `--ep` → EP mode（post-EP）；`--ep` 與 target/base 互斥（同時給予報錯並提示用法）。否則第一個參數匹配 `[0-9a-f]{7,40}` → commit mode；其餘視為 branch name。

**Output 模式**：

| 旗標 | 說明 |
|------|------|
| 預設（console） | ASCII 圖表，terminal 內即時產出 + 互動 |
| `--md` | Mermaid 圖表，寫檔 `ai-analysis/reports/human-review-{scope}.md`，Phase 2 仍為 terminal 互動 |

---

## 執行模式選擇

偵測 effort level 和 max-agents（查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md)）。

**Phase 1（4 Lens 概覽）**：

| 條件 | 模式 | Agent 數量 |
|------|------|-----------|
| effort = ultracode/xhigh 且 max-agents > 1 | Workflow（4 lens 平行 agents） | ≤ max-agents |
| effort < ultracode 或 max-agents = 1 | Main LLM（序列） | 0 |

**Phase 2（互動式調查）**：永遠 Main LLM（互動需要 conversation state）。

印出確認：`[Human Review] source=EP|code, Phase 1: effort=X, workflow=Y, max=N`

---

## Phase 1: 4 Lens 概覽

> **目標**：讓 human 用「大原則」5 秒內掌握全貌，4 lens 各對應一項人擅長的判讀。依序展示。

### Lens 1: I/O（介面契約）

**人判**：介面契約 sensible 嗎（簽名、吃什麼吐什麼、介面是否合理）。

| source | 提取 | 呈現 |
|--------|------|------|
| EP | pseudo code 的函式簽名、資料流、模組公開介面 | 契約清單 |
| code | git diff 中 public 簽名（新/改的 function signature、class public API、data flow） | 契約清單 + **設計 vs 實作落差**標記 |

**code mode 提取 patterns**（match `+` lines in diff）：

| Pattern | 擷取目標 |
|---------|---------|
| `^\+(?:async\s+)?def\s+(\w+)\s*\(` | Function 簽名 |
| `^\+class\s+(\w+)` | Class public API |
| `^\+def\s+\_\_.+?\_\_.+:\s*$`（多行） | Dunder / protocol 介面 |

**EP mode 提取**（從 EP 結構元素，非 diff）：pseudo code 段落的 `def`/`class` 簽名 + Context 的模組公開介面 + 段落間資料流（上段產出 → 下段輸入）。呈現「契約清單」讓人判 I/O 是否合理（code mode 額外標「設計 vs 實作落差」）。

**Console 輸出格式**（code mode 範例）：

```
🔌 Lens 1: I/O — 5 contracts                     2 ⚠️ 落差

Function               Signature                       Status
────────────────────── ─────────────────────────────── ────────
fetch_daily            (symbol: str, start, end) → df  ✏️ MOD  簽名加了 interval 參數（EP 無）
TradeAction            enum: BUY/SELL/HOLD             🆕 NEW  EP 寫 BUY/SELL，實作多 HOLD ⚠️
parse_response         (raw: bytes) → Quote            ✏️ MOD
```

### Lens 2: 架構（Clean Code）

**人判**：耦合/內聚、依賴方向、SRP、模組邊界、drift（重複造輪子/漏用/漂移）。

> 原 Pattern Radar 摺入此 —— dup/reuse/drift 是架構 lens 的子項（寧漏勿誤，false positive 是毒藥）。

**架構違規偵測**（code mode，從 import graph；EP mode 無 code 故跳過此子項，僅跑下方 Pattern Radar dup 偵測）：

| 違規 | 偵測 | 嚴重度 |
|------|------|--------|
| 依賴方向反向（下層 import 上層） | import graph + 分層規則 | HIGH |
| 模組邊界打破（跨域直接存取內部） | import private/`_` symbol | MEDIUM |
| 新耦合（無對應 EP 設計） | diff 新增 import 非 EP 預期 | MEDIUM |

**Pattern Radar 偵測策略**（按 ROI 排序，沿用既有信心度）：

| 類型 | 觸發條件 | 搜尋方法 | ROI |
|------|---------|---------|-----|
| Enum 重複 | diff 中有 `class X(Enum)` | LSP `workspaceSymbol` + `rg` member values | 最高 |
| Function 重複 | diff 中有 `def X()` | LSP `workspaceSymbol` + `outgoingCalls` 比對 | 高 |
| Data Structure 重複 | diff 中有 `@dataclass` / `TypedDict` | `rg` field name overlap（Jaccard） | 中 |
| Import 漏用 | diff 中有 `from X import Y` | LSP `documentSymbol` + `__all__` 比對 | 低（FP 高） |

**偵測流程**：

```
Phase A: Extract — 從 diff（code）或 EP pseudo code（EP）解析 symbols → 分類 → 提取簽名/欄位/成員值
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

**門檻**：HIGH ≥ 7 / MEDIUM 4-6 / LOW 1-3。只展示 HIGH + MEDIUM；LOW 收在 drill-down。

**LSP Degradation**（subagent worktree 中不可用時）：

| LSP 操作 | rg Fallback |
|---------|-------------|
| `workspaceSymbol` | `rg -t py "class\s+(\w+)" --no-filename -o -r '$1'` |
| `hover` | `Read` file directly |
| `findReferences` | `rg -t py "symbol_name"`（text match，可能漏 dynamic refs） |
| `documentSymbol` | `rg -t py "^\s*(class\|def)\s+" file.py` |

**Console 輸出格式**（code mode 範例）：

```
🏗️  Lens 2: 架構 — 1 違規 + 3 dup 嫌疑

⚠️ 架構違規
  data/fetcher.py imports cli.args — 下層 import 上層（依賴方向反向）

📡 Pattern Radar
🔴 HIGH
  PR-001  Enum Dup   TradeAction (fetcher.py:15)
          ↔ TradeSide (types.py:23, 12 refs)
          Evidence: same members BUY/SELL, both StrEnum, fetcher.py already imports types
🟡 MEDIUM
  PR-002  Fn Dup     _parse_response (fetcher.py:88)
          ↔ _parse_raw (parser.py:45, 5 refs)
          Evidence: same signature (str) → dict, 70% logic overlap
```

### Lens 3: 大概實作（結構形狀）

**人判**：結構形狀（大圖，非逐行）。

| source | 元件 |
|--------|------|
| EP | pseudo code 結構 + 段落依賴圖 |
| code | Diff Map（改動地圖）+ Symbol Inventory（符號清單） |

#### Diff Map（改動地圖）— code mode

**提取邏輯**：
1. `git diff --stat` → per-file (+N/-M)
2. Parse file paths → group by top-level directory
3. Import analysis → file A imports file B 且兩者都改 → dependency edge（⚠️ co-change risk）
4. Render → ASCII tree（console）or Mermaid flowchart（`--md`）

**大小自適應**：

| Size | 觸發 | 行為 |
|------|------|------|
| Small | <50 lines changed | 完整檔案樹，每檔案列 +N/-M |
| Medium | 50-500 lines | 按模組分組 + dependency flow |
| Large | >500 lines | 模組級摘要（module + file count + total +N/-M）+ drill-down |

**Console 輸出格式**（Medium 範例）：

```
🗺️  Lens 3: 大概實作 — 3 modules, 11 files     +312 -87 = +225

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
```

#### Symbol Inventory（符號清單）— code mode

**提取 patterns**（match `+` lines in diff，按順序匹配，first match wins）：

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
```

#### EP mode 結構形狀

pseudo code 結構 + 段落依賴圖（哪些段依賴哪些段），讓人一眼看見「這 EP 拆成幾塊、怎麼接」。

### Lens 4: 驗證範圍審查

**人判**：該驗哪些（domain edge / error path / 效能，涵蓋了嗎）。**人審範圍，不親跑。**

> 與 `/audit-test` 的區別：audit-test 審**測試品質**（反模式、mock 健康度）；本 lens 審**驗證範圍是否完整**（該驗的有沒有列）。人用領域直覺補 AI 的邊界盲區。

**素材**：

| source | 素材 | 人判 |
|--------|------|------|
| EP | EP Scenario Matrix | 該驗的場景都列了嗎（domain edge / error path 涵蓋） |
| code | git diff 測試檔案（`test_*.py`）+ 測試名稱（若有 EP SM 則對照） | 該驗的 edge 有沒有實際測到 |

> SM 無「場景類型」欄位；AI 逐 row 讀「觸發」+「預期行為」自行分類 happy / error / boundary / perf。code mode 無 EP SM → 只從測試名稱判 domain edge 覆蓋。

**檢查項**：

| 檢查 | 嚴重度 | 判斷 |
|------|--------|------|
| 該領域關鍵 edge 未列場景 | HIGH | domain edge（除權息、跨日、缺前置條件等）SM 沒覆蓋 |
| error path 缺場景 | MEDIUM | 只有 happy path，無錯誤/失敗場景 |
| 效能期待差異未列 | LOW | 效能敏感場景無對應 SM entry |
| 「該驗但沒列」的場景 | HIGH | 人依領域直覺判斷遺漏（AI 常漏的邊界） |

**Console 輸出格式**：

```
🛡️  Lens 4: 驗證範圍 — 3 files 涵蓋 8 場景     2 ⚠️ 缺口

SM 場景涵蓋: happy ✅ / error ✅ / boundary ⚠️ 缺跨日 / perf — 

⚠️ 缺口
  - 除權息當日下單：SM 無對應場景（domain edge，該領域高風險）
  - 連線中斷重試：SM 無 error path 場景

💡 這是「該驗什麼」的範圍審查。補進 EP Scenario Matrix 後，跑驗證是 LLM 鏈（/audit-test + /build）的事。
```

### Phase 1 → Phase 2 過渡

展示完 4 lens 後，印出（兩 mode 皆可用：`contracts` / `verify-scope` / `explain` / `deep` / 自然語言；`drill` / `symbols` / `focus` 為 code mode 專用）：

```
──────────────────────────────────────────────────
💬 Phase 1 完成。你現在可以：

  drill <module>      — 檔案級 detail（大型 diff）
  symbols <path>      — 完整 symbol table
  dup-detail          — 所有架構相似匹配（含 LOW confidence）
  contracts           — 完整 I/O 契約清單
  verify-scope        — 完整驗證範圍審查
  deep <PR-XXX>       — 深入分析某個架構嫌疑
  focus <file>        — 只看影響該檔案的條目
  explain <symbol>    — 解釋某 symbol 的功能和連結

  或直接用自然語言描述可疑處。
  完成審查後說 done 或 summary 產出最終報告。
──────────────────────────────────────────────────
```

---

## Phase 2: 互動式調查

> **核心理念**：Human 提線索（模糊記憶），LLM 做精確查證（LSP + rg）。

### 7 種 Human 觀察類型 → 對應 Lens

| Type | Human 說什麼 | 對應 Lens | LLM 調查工具 |
|------|------------|-----------|-------------|
| 🔍 Suspicion | 「L45 看起來不對」「retry 邏輯怪怪的」 | I/O / 大概實作 | `Read` + LSP `hover`/`findReferences` + `rg` |
| 📖 Understanding | 「這個 ChainMap 在幹嘛？」 | I/O / 大概實作 | LSP `goToDefinition` + `incomingCalls`/`outgoingCalls` |
| 🔗 Impact | 「這改動影響 demo 嗎？」 | 架構 | LSP `findReferences` + `rg` 搜 `demo_*.py`, `lab/`, `examples/` |
| 🔄 Consistency | 「error handling 跟其他地方一致嗎？」 | 架構 | `rg` 搜 pattern across codebase + `Read` 2-3 代表實作 |
| 🛡️ Coverage | 「除權息驗了嗎？」「該驗的 edge 有沒有測？」 | 驗證範圍 | `rg` 測試名稱 + EP SM 對照（code mode）；Read EP SM（EP mode） |
| 🤿 Deep Dive | 「深入看 error handling」 | 跨 lens | Full sub-graph：`Read` + LSP `incomingCalls` + `outgoingCalls` |
| 💬 Free-form | 任意問題 | 自動分類 | 自動分類到上述類型（含驗證範圍），或直接回答 |

### 調查協議模板

每次調查回報格式：

```
### [Investigation N]: [Title]

**Type**: Suspicion / Understanding / Impact / Consistency / Deep Dive
**Lens**: I/O / 架構 / 大概實作 / 驗證範圍
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
- Source: EP <path> / code (uncommitted / commit abc / branch feat/xxx vs main)
- Checkpoint: post-EP / post-build
- Lens 覆蓋: I/O | 架構 | 大概實作 | 驗證範圍

### 4 Lens Findings
| Lens | Severity | File:Line / EP 段 | Description | Action |
|------|----------|------------------|-------------|--------|
| I/O | Important | ... | TradeAction 多 HOLD（EP 無） | 確認是否 intended |
| 架構 | Important | fetcher.py:5 | import cli.args 反向依賴 | 重構 |
| 驗證範圍 | High | SM 缺除權息 edge | 該驗未列 | 補 SM 場景 |

### False Alarms (confirmed safe)
| # | File:Line | Initial Suspicion | Why Safe |
|---|-----------|------------------|----------|

### Items for Discussion
| # | Topic | Question |
|---|-------|----------|

### Recommended Next Steps
1. Fix confirmed findings
2. 補 EP Scenario Matrix 缺口（驗證範圍 lens 發現）
3. `/code-review` for automated six-axis analysis（LLM 執行鏈）
4. `/commit` when ready
```

---

## 邊界案例處理

| 案例 | 處理方式 |
|------|---------|
| EP mode 但無 Scenario Matrix | Lens 4 標「EP 無 SM，無法審驗證範圍」+ 建議補 SM |
| Empty diff（code mode） | 印出 "No changes found" + scope suggestions |
| New file（code mode，無 before state） | Symbol Inventory 全標 NEW，架構 lens 掃全檔（非 diff-only） |
| Merge commit | 提示雙 parent，預設用 parent 1（`git diff abc^1 abc`），可切換 parent 2 |
| Large diff (>500 lines) | Phase 1 只產出模組級摘要 + drill-down 提示 |
| 架構 lens clean | "Clean" report 列出掃描了哪些 pattern（不是空白輸出） |
| Non-Python files（.md/.yaml/.toml/.json） | Diff Map 照常列出，標注 `[non-Python, skipped]`；其他 lens 跳過 |
| Binary files | Diff Map 列出並標注 `[binary]`；其他 lens 跳過 |

---

## 與其他命令的關係

human-review 是**唯一的人類 viewport（layer 3）**。`/code-review`、`/ep-review`、`/audit-test` 是 LLM 執行鏈命令（layer 1/2），產出給機器消費，不是人類 viewport。

| | `/ep-review` `/code-review`（LLM 鏈） | `/human-review`（人類 viewport） |
|--|---------------------------------------|----------------------------------|
| **受眾** | LLM（產出回寫 EP / apply changes） | 人類 |
| **回答什麼** | 「code 正確嗎？」「EP 合規嗎？」（機器自判） | 「這是我要的系統嗎？架構行不行？」（人大原則） |
| **scope** | 完整正確性 / 合規 | 4 lens（I/O + 架構 + 大概實作 + 驗證範圍） |

**跨 session 第二意見（layer 2）**：開新 session 跑 `/code-review`/`/ep-review`，findings 貼回實作 LLM → `/judge-review`。這是 A 軸內的獨立性提升，與人類 viewport（B 軸）互補。

**推薦順序**：

```
post-EP：/human-review --ep（人判「這是我要的系統嗎」）
post-build：/human-review（人判 4 lens）→ /code-review（LLM 系統審查）→ /commit
```

---

## 流程位置

```
/spec → /execution-plan（含 EP Review, LLM 自判）
          ↓ post-EP checkpoint
        /human-review --ep（layer 3，人類 viewport）
          ↓
        /build（含 Agent Review + /audit-test, LLM 鏈）
          ↓ post-build checkpoint
        /human-review（layer 3）→ /code-review（layer 1/2, LLM）→ /commit
```

後續：確認 findings → `/code-review`（如尚未跑）→ `/commit`
