# Execution Plan - Skill Frontmatter 優化

> **🎯 核心目的**: 降低每個命令從啟動到完成的 **prompt 次數**（來回對話輪數），同時**維持或提升產出品質**。
>
> 每一個 Claude 停下來問問題、猜錯方向、或遺忘指令的點，都是一次額外 prompt。好的 skill 設計把這些決策點提前編碼進去，讓任務變成可預測的執行路徑。

## 實作總覽

- **基於**: `/verify-review` 評估結果（四家 AI 建議，經官方文檔交叉驗證）
- **段落策略**: 4 個 Self-Contained Segment，按「降低 prompt 的 ROI」排列
- **品質保證**: 每段完成後驗證 skill 仍可正常觸發和執行

### 變更範圍

| 段落 | 目標 | 降低 Prompt 機制 | 修改檔案數 | 風險 |
|------|------|-----------------|-----------|------|
| S1 | `when_to_use` frontmatter 新增 | 更精準路由 → 少 1-2 輪「找錯 skill」 | ~15 | 低 |
| S2 | 長 Skill 重構為 Supporting Files | 更好的 context 管理 → 少 2-3 輪「遺忘指令」 | ~5 | 中 |
| S3 | `context: fork` 隔離執行 | 主對話 context 乾淨 → 品質提升 | ~3 | 中 |
| S4 | `permission-mode` 清理 + CLAUDE.md 文檔更新 | 移除無效欄位 → 減少混淆 | ~9 | 低 |

### 官方文檔依據

所有變更基於 `code.claude.com/docs/en/skills` 的 Frontmatter Reference 表（2026-05 查證）：

| 使用欄位 | 官方說明 | 降低 Prompt 機制 |
|---------|----------|-----------------|
| `when_to_use` | "Additional context for when Claude should invoke the skill" — 與 description 合併計入 1,536 字元上限 | 路由精準化 |
| `context: fork` | "Set to `fork` to run in a forked subagent context" | Context 隔離 |
| `agent` | "Which subagent type to use when `context: fork` is set" | 指定執行環境 |

---

## 段落 1: `when_to_use` Frontmatter 新增

### Context

**背景**: 當前 22 個 skill 的 description 偏簡潔，Claude 在自動路由時可能無法精準匹配。官方的 `when_to_use` 欄位可補充觸發情境描述，讓 Claude 第一次就選對 skill。

**降低 Prompt 機制**: 若 Claude 選錯 skill（或沒選到任何 skill），用戶需要手動修正或重述需求 = +1-2 輪 prompt。精準路由直接消除這個浪費。

**語義約束**: 與 S3 共享「description + when_to_use 合併 1,536 字元上限」的約束。

**依賴錨點**: 無（純新增 frontmatter 欄位）

**成功標準**:
- [ ] 所有 22 個 skill 的 frontmatter 含 `when_to_use`
- [ ] description + when_to_use 合併長度 < 1,536 字元
- [ ] Skill 仍可正常觸發

### 核心實作要點

#### `when_to_use` 完整新增計畫

基於對每個 skill 完整內容的深度分析，以下是精確的 when_to_use 文本：

| Skill | description (現有) | when_to_use (新增) | 合併字元 |
|-------|-------------------|-------------------|---------|
| `code-review` | 第一性原理代碼審查 — 未 commit 的 code，多找相關程式碼確認實作合理性 | Review uncommitted code changes before committing. Use after /build or after writing new code to validate correctness, architecture, and security. | ~280 |
| `consistency` | 文檔品質檢查器（自洽性、矛盾性、順序、自包含、精準度）。/consistency <文檔路徑> | Check a single Markdown document for internal quality: self-consistency, contradictions, ordering, self-containedness, accuracy, and signal/noise ratio. | ~290 |
| `lint-fix` | 執行 ruff 和 mypy 檢查並自動修正問題 | Run ruff format, ruff check --fix, and mypy on Python files. Use after writing or modifying Python code to enforce style and type conventions. | ~245 |
| `commit-message` | 分析 git 變更生成 commit message。自動偵測 staged/unstaged/diff，產出 conventional commits 格式建議。 | Generate a conventional commit message from current git changes. Use when you have uncommitted changes and are ready to commit. | ~310 |
| `rules-reminder` | 快速提醒 LLM 最常忘記的規則 — 避免權限提示卡關 | Remind the LLM of rules most frequently violated: no # in python -c, use rg/fd not grep/find, always uv run, no sed for code, split pipe commands. | ~295 |
| `followup-review` | 審查者回頭驗收實作結果，確認修改合理性和不修改的合理性。/followup-review [審查報告]（無參數則從 git 變更推斷） | Verify that code changes from a previous review were implemented correctly. Use after /verify-review decisions have been applied. | ~340 |
| `ep-review` | 審查 Execution Plan 合理性（完整性、規範合規、一致性、遺漏風險）。/ep-review <EP路徑> | Review an Execution Plan for completeness, rules compliance, internal consistency, and omission risks before implementation begins. | ~280 |
| `batch-task` | Sequential batch task processor - processes subtasks one at a time to avoid rate limits | Process multiple subtasks sequentially (one agent at a time) to avoid rate limits. Use when you need batch processing but parallel execution is not feasible. | ~295 |
| `ui-collab` | UI-LLM 協作模式 — 啟動 UI 並監控操作日誌 | Launch the Backbone Trajectory Viewer UI and monitor [ACTION] logs so the LLM can understand user UI interactions in real time. | ~265 |
| `deep-work` | 深度工作模式 - 用戶離開時的自主實作引擎，AI 全力發揮、慢慢思考、完整交付 | Autonomous implementation mode for when the user is away. Full-power, self-directed execution with deep thinking, error self-healing, and complete delivery. | ~310 |
| `verify-review` | 評估其他 AI 的審查建議，基於第一性原理決定是否採納。/verify-review <ai1: 建議 [ai2: 建議]> | Evaluate AI review suggestions using first-principles reasoning against actual code. Decide adopt/reject/needs-confirmation before making changes. | ~305 |
| `spec` | 結構化需求討論（User Story 挖掘、假設浮出、技術選型、邊界定義），為 EP 做準備。/spec [需求描述] | Structure a feature requirement into a spec document with User Story, assumptions, tech choices, and boundaries. Use before /execution-plan. | ~300 |
| `execution-plan` | 段落式實作計畫書生成器，基於 /spec 規格摘要生成 Self-Contained Segments。/execution-plan "任務描述" [PROMPT檔案] | Generate a segmented Execution Plan from a spec. Creates self-contained segments with context, pseudo code, validation strategy, and dependency anchors. | ~320 |
| `build` | 基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號] | Implement an Execution Plan segment-by-segment using TDD. Use after /ep-review and /verify-review. Supports parallel agents with --max-agents. | ~315 |
| `distill-spec` | 蒸餾肥大的 spec 文檔 — 提煉核心技術決策，去除冗餘和重複，產出精簡版 spec。 | Distill a bloated spec document by extracting core technical decisions, removing redundancy and contradictions, producing a condensed version. | ~280 |
| `claude/clean` | 清理 Markdown 文檔中不必要的元資訊（版本號、日期、統計、Changelog） | Remove unnecessary metadata (version numbers, dates, statistics, changelogs) and low-signal content from CLAUDE.md files. Use to improve signal/noise ratio. | ~290 |
| `claude/distill` | 蒸餾 Markdown 文檔，提煉核心精華，移除可推導內容 | Distill CLAUDE.md files by separating signal from noise: keep design rationale and constraints, remove API signatures and derivable content. | ~275 |
| `claude/decode-compare` | 對比文檔理解與實際程式碼，驗證精確度 | Compare source-docs/ documentation against actual Python code to verify encoding precision. Supports --quick scan and full three-level comparison. | ~280 |
| `claude/doc-decode` | 從 CLAUDE.md + 程式碼重建模組理解文檔，產出完整思考邏輯文檔（source-docs/） | Reconstruct module understanding documents from CLAUDE.md + code, producing source-docs/ with pipeline narratives, code verbatims, and design decisions. | ~295 |
| `claude/sync` | 檢查 Markdown 文檔與程式碼同步性及內部品質 | Check CLAUDE.md synchronization with code: navigation validity, code consistency, signal/noise ratio. Supports --recursive, --changed-since, --quality. | ~280 |
| `claude/daily-maintain` | 每日自動化 CLAUDE.md 維護 — 掃描、修正、重建、驗證、產出 morning report | Automated daily CLAUDE.md maintenance: scan modules, fix stale docs, rebuild source-docs, verify accuracy, produce morning report. Runs autonomously. | ~300 |
| `explain` | 解釋技術概念、架構設計或流程。可指定 @目錄或 @檔案讓 AI 先讀再解釋，支援 console（即時）和 md（寫檔）兩種輸出模式。 | Explain technical concepts, architecture, or processes. Supports console (ASCII) and md (Mermaid) output. Use with @dir or @file for code-based explanations. | ~330 |

所有合併字元數均遠低於 1,536 上限（最高 ~340 字元）。

#### 不新增 `paths` 的理由

深度分析後決定**不為任何 skill 新增 `paths`**。原因：
- `paths` 只限制 Claude **自動觸發**的場景
- 絕大多數 skill 由用戶手動 `/name` 調用，`paths` 不影響手動調用
- `lint-fix` 和 `consistency` 的 description 已足夠明確（提及 "ruff/mypy" 和 "文檔品質"），Claude 不太可能在非匹配場景誤觸發
- 加 `paths` 反而可能阻止有用的自動觸發（例如 Claude 在修改 Python 時自動建議跑 lint）

### 程式碼框架

以 `code-review.md` 為例：

```yaml
---
description: "第一性原理代碼審查 — 未 commit 的 code，多找相關程式碼確認實作合理性"
when_to_use: "Review uncommitted code changes before committing. Use after /build or after writing new code to validate correctness, architecture, and security."
usage: "/code-review [選項]"
argument-hint: "[可選：指定檔案或範圍]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---
```

### 驗證策略

1. 修改完成後，在 Claude Code 中輸入相關觸發詞（如 "review my code"），確認 `code-review` 被自動載入
2. 輸入 "check this doc"，確認 `consistency` 被載入而非其他 skill
3. 用 `rg -o 'description:.*' commands/` 手動加總各 skill 的 description + when_to_use 字元數，確認均 < 1,536

---

## 段落 2: 長 Skill 重構為 Supporting Files

### Context

**背景**: 官方建議 SKILL.md 保持 **500 行以內**。超長 skill 的問題：
1. 每次調用都載入全部內容 → 佔用 context window → Claude 遺忘前面的對話 → 需要額外 prompt 重述
2. 詳細參考資料和工作流混合在一起 → Claude 分不清哪些是指令、哪些是參考 → 輸出品質下降

**降低 Prompt 機制**: Skill 內容越精簡，Claude 越能抓住重點。詳細參考資料按需載入，避免一次性灌入導致指令被稀釋。這直接減少 Claude 「忘了要做什麼」而需要用戶重述的 prompt。

**語義約束**: SKILL.md 中引用 supporting files 使用 markdown link `[描述](path)`。Commands 不支援 `@` transclusion。

**依賴錨點**:
- `claude/_common/encoder-philosophy.md` — 已存在，被 `sync.md`、`consistency.md` 等引用
- `claude/_common/recursive-*.md` — 已存在，被 `sync.md`、`clean.md` 等引用

**成功標準**:
- [ ] 所有超過 500 行的 skill 精簡至 500 行以內
- [ ] Supporting files 被 SKILL.md 正確引用
- [ ] 調用 skill 後功能不受影響

### 核心實作要點

#### 重構原則

**保留在 SKILL.md**: workflow checklist（做什麼、步驟順序、成功標準）
**移到 Supporting Files**: 詳細檢查標準、輸出格式模板、實作 pseudo code、範例

#### 各 Skill 重構計畫（基於逐行分析）

##### `sync.md` (993 → 目標 ~400)

最大的重構目標。深度分析識別出三個可移出區塊：

```
commands/claude/
├── sync.md                              # 核心流程 + 引用（精簡後 ~400 行）
└── _common/
    ├── sync-check-angles.md             # 9 個檢查角度的完整定義（~200 行）
    │                                    # 來源: 原 sync.md:58-261
    ├── sync-output-templates.md         # 6 組輸出格式模板（~330 行）
    │                                    # 來源: 原 sync.md:545-875
    └── sync-implementation-steps.md     # 步驟 1-10 的詳細實作（~220 行）
                                         # 來源: 原 sync.md:325-541
```

SKILL.md 保留（~400 行）：
- 核心身份 + 文檔類型判斷（:9-42）
- 執行層級概覽表（:46-56）
- 檢查角度的名稱 + 一行摘要 + supporting file 引用（取代 :58-261 的詳細定義）
- Content Change Assessment（:168-203，因為是決策規則非參考資料）
- Command Interface（:264-322）
- 步驟名稱 + 引用（取代 :325-541 的詳細 pseudo code）
- 執行約束 + 品質檢查表（:884-980）
- 既有的 _common 引用不變

##### `explain.md` (853 → 目標 ~420)

第二大重構目標。平行處理架構重複出現兩次（:70-129 和 :278-368）：

```
commands/
├── explain.md                           # 核心流程 + 引用（精簡後 ~420 行）
└── claude/_common/
    ├── explain-parallel-architecture.md # 平行處理架構 + 檔案分組邏輯（~130 行）
    │                                    # 來源: 原 :70-129 + :278-368（去重後）
    ├── explain-deep-analysis.md         # 深度分析框架（~60 行）
    │                                    # 來源: 原 :520-580
    └── explain-examples.md              # 3 個完整使用範例（~120 行）
                                         # 來源: 原 :583-700
```

SKILL.md 保留（~420 行）：
- 核心能力 + 模式概覽（:6-68）
- Console/MD 模式規格（:131-275）
- 執行邏輯決策流程（:370-434）
- MD 自動存檔機制（:437-517）— 保留因為是核心功能
- 進階提示 + 最佳實踐（:702-760）
- 平行處理改為引用 supporting file

##### `distill-spec.md` (564 → 目標 ~300)

**最高壓縮比（~47%）**。230 行的 Python 分類 pseudo code 是最大可移出區塊：

```
commands/
├── distill-spec.md                      # 核心流程 + 分類摘要（精簡後 ~300 行）
└── claude/_common/
    └── distill-spec-classification.md   # 分類邏輯 pseudo code + 模式列表（~270 行）
                                         # 來源: 原 :179-451
```

SKILL.md 保留（~300 行）：
- 核心身份 + Essence vs Impurity 分類概念（:8-62）
- 實作設計概覽（:64-102）
- Command Interface（:104-177）
- Concise Spec Template（:453-507）
- 蒸餾策略（:509-543）
- 分類只保留 4 型摘要表 + supporting file 引用

##### `daily-maintain.md` (713 → 目標 ~580)

**最低壓縮比（~18%）**。此 skill 本身是 workflow 文檔，大部分內容是各 Phase 的執行步驟，不適合大量移出：

```
commands/claude/
├── daily-maintain.md                    # 核心流程（精簡後 ~580 行）
└── _common/
    └── morning-report-template.md       # Morning report 格式模板（~70 行）
                                         # 來源: 原 :539-605
```

##### `doc-decode.md` (522 → 目標 ~420)

小幅精簡：

```
commands/claude/
├── doc-decode.md                        # 核心流程（精簡後 ~420 行）
└── _common/
    └── doc-decode-output-formats.md     # 輸出格式 + 知識圖譜格式（~90 行）
                                         # 來源: 原 :266-311 + :415-451
```

#### Supporting Files 引用語法

```markdown
## 詳細檢查標準

9 個檢查角度的完整定義和判斷標準：[sync-check-angles.md](./_common/sync-check-angles.md)

輸出格式模板（single-file, recursive, post-clean 等）：[sync-output-templates.md](./_common/sync-output-templates.md)
```

### 驗證策略

1. 每個 skill 重構後，調用一次完整流程確認功能正常
2. 確認 Claude 在需要時讀取了 supporting files（從對話中可觀察）
3. 確認 SKILL.md 行數 < 500（daily-maintain 例外，允許 ~580）
4. 對比重構前後的產出品質

---

## 段落 3: `context: fork` 隔離執行

### Context

**背景**: 部分 read-only 分析 skill 會大量讀取檔案，中間步驟佔用主對話 context window。使用 `context: fork` 讓 skill 在獨立 subagent context 執行，只將摘要結果返回主對話。

**降低 Prompt 機制**: Fork 不直接減少 prompt 次數，但保持主 context 乾淨 → Claude 不會因為 context 被中間步驟塞滿而遺忘後續指令 → **品質提升**，間接減少重做。

**語義約束**: 僅 **read-only 任務型 skill** 適合 fork。需要互動或編輯檔案的 skill 不適合。

**依賴錨點**: 無

**注意事項**: GitHub Issue #17283 曾報告 Skill tool 調用時 fork 不生效（已關閉）。需測試。

**成功標準**:
- [ ] 目標 skill 的 frontmatter 含 `context: fork` + `agent`
- [ ] 調用時確認啟動 subagent
- [ ] 主對話 context 不含中間步驟

### 核心實作要點

#### Fork 適用性判斷（基於深度分析修正）

經逐行分析每個 skill 的內容後，fork 候選必須同時滿足：
1. **Read-only** — 不需要 Edit/Write 權限
2. **非互動** — 不需要與用戶對話
3. **返回摘要即可** — 中間步驟結果不需留在主對話
4. **任務型** — 有明確的「分析 X → 產出報告」指令

| Skill | Read-only | 非互動 | 返回摘要 | 任務型 | 決策 |
|-------|-----------|--------|---------|--------|------|
| `consistency` | ✅ | ✅ | ✅ | ✅ | ✅ **Fork** |
| `ep-review` | ✅ | ✅ | ✅ | ✅ | ✅ **Fork** |
| `decode-compare` | ❌ 有 Write | ✅ | ✅ | ✅ | ❌ 不 Fork |
| `code-review` | ✅ | ❌ 用戶可能追問 | ❌ 結果供後續修改 | ✅ | ❌ 不 Fork |
| `sync` | ❌ 有 Edit | ❌ 可能互動 | ❌ | ✅ | ❌ 不 Fork |
| `build` | ❌ 大量 Edit | ❌ 動態決策 | ❌ | ✅ | ❌ 不 Fork |
| `deep-work` | ❌ Edit | ❌ | ❌ | ✅ | ❌ 不 Fork |
| `explain` | ✅ | ❌ 互動問答 | ❌ | ❌ | ❌ 不 Fork |

#### 最終 Fork 候選

| Skill | agent | 理由 |
|-------|-------|------|
| `consistency` | `Explore` | 純讀取 + 品質分析，返回報告。135 行輕量，但 fork 避免中間分析佔用 context |
| `ep-review` | `Explore` | 讀取 EP + 相關程式碼，返回審查結果 |

### 程式碼框架

以 `consistency.md` 為例：

```yaml
---
description: "文檔品質檢查器（自洽性、矛盾性、順序、自包含、精準度）。/consistency <文檔路徑>"
when_to_use: "Check a single Markdown document for internal quality: self-consistency, contradictions, ordering, self-containedness, accuracy, and signal/noise ratio."
context: fork
agent: Explore
usage: "/consistency <文檔路徑>"
argument-hint: "要檢查的文檔路徑（單一檔案）"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---
```

### 驗證策略

1. 調用 `/consistency some-file.md`，觀察是否啟動 subagent
2. 確認結果摘要返回主對話
3. 確認主對話 context 中不包含中間步驟的詳細內容
4. 若 fork 不生效（Issue #17283），回退為不加 fork — 不影響功能，只影響 context 隔離

**回退觸發條件**: 調用 `/consistency` 或 `/ep-review` 時，若 Claude 直接在主對話中產出結果（未啟動 subagent），即為 fork 不生效。回退方式：移除 `context: fork` 和 `agent` 欄位。

---

## 段落 4: `permission-mode` 清理 + CLAUDE.md 文檔更新

### Context

**背景**: 7 個 skill 使用了 `permission-mode` 欄位，但該欄位**不在官方 Frontmatter Reference 表中**。若無效，則佔用 context 且造成混淆。同時更新 `commands/CLAUDE.md` 反映所有新增的 frontmatter 欄位。

**降低 Prompt 機制**: 移除無效欄位 → 減少 Claude 對欄位用途的混淆 → 輸出更精準。文檔更新 → 未來新增 skill 時少走彎路。

**語義約束**: 無

**依賴錨點**:
- `commands/CLAUDE.md:194` — Frontmatter 配置標準段（含 permission-mode）
- `commands/CLAUDE.md:221` — 參數詳細說明段（含 permission-mode）

**成功標準**:
- [ ] 確認 `permission-mode` 的有效性
- [ ] 無效則移除所有 `permission-mode` 行
- [ ] `commands/CLAUDE.md` 反映官方支援的所有 frontmatter 欄位

### 核心實作要點

#### 步驟 1: 驗證 `permission-mode`

使用含 `permission-mode: "acceptEdits"` 的 skill（如 `lint-fix`）執行 Edit 操作，觀察是否需要手動批准。若仍需手動批准 → 欄位無效。

#### 步驟 2: 清理（若無效）

移除以下 7 個檔案的 `permission-mode` 行：

| 檔案 | 當前值 |
|------|--------|
| `build.md` | `"acceptEdits"` |
| `deep-work.md` | `"acceptEdits"` |
| `lint-fix.md` | `"acceptEdits"` |
| `claude/clean.md` | `"acceptEdits"` |
| `claude/daily-maintain.md` | `"acceptEdits"` |
| `claude/distill.md` | `"acceptEdits"` |
| `claude/sync.md` | `"acceptEdits"` |

同時更新 `commands/CLAUDE.md`，將 `permission-mode` 從文檔中移除。

#### 步驟 3: 更新 CLAUDE.md Frontmatter 文檔

更新 `commands/CLAUDE.md` 的 Frontmatter 配置標準段，新增官方支援欄位文檔：

**新增**：`when_to_use`、`context`、`agent`、`effort`、`hooks`、`shell`、`user-invocable`

**移除**（若驗證無效）：`permission-mode`

CLAUDE.md 中 permission-mode 的 6 處引用（逐項處理）：
- `:217` — Frontmatter YAML 範例中的 `permission-mode: "acceptEdits"` 行 → 刪除該行
- `:229` — 參數說明中的 `permission-mode` 條目 → 刪除該條目
- `:313` — `/lint-fix` 範例中的 `permission-mode` → 刪除
- `:317` — `/deep-work` 範例中的 `permission-mode` → 刪除
- `:596` — 文檔範例程式碼中的 `permission-mode` → 刪除
- `:597` — 文檔範例程式碼中的 `permission-mode` → 刪除

### 驗證策略

1. 測試 `permission-mode` 前後對比
2. 用 `/consistency commands/CLAUDE.md` 驗證更新後文檔品質

---

## 整合策略

### 段落間依賴

```
S1 (when_to_use)              ← 可獨立執行，ROI 最高
S2 (supporting files 重構)    ← 可與 S1 平行，ROI 次高
S3 (context: fork)            ← 依賴 S1（frontmatter 改完再測 fork）
S4 (清理 + 文檔)              ← 最後執行（彙總所有變更）
```

推薦執行順序：**S1 → S2 → S3 → S4**（S1/S2 可平行）

### 語義約束映射

| 約束 | 涉及段落 | 說明 |
|------|----------|------|
| description + when_to_use < 1,536 字元 | S1 | 所有新增 when_to_use 都已確認 < 340 字元 |
| Supporting files 用 markdown link | S2 | Commands 不支援 `@` transclusion |
| 僅 read-only 任務型 skill 用 fork | S3 | 2 個候選均為 read-only 分析 |

### 依賴錨點 drift check

`/build` 執行 S4 前驗證：
- `commands/CLAUDE.md:194` — Frontmatter 配置標準段
- `commands/CLAUDE.md:221` — 參數詳細說明段

### 品質保證

- [ ] 所有 22 個 skill 含 `when_to_use`
- [ ] 5 個長 skill 精簡至 500 行以內（daily-maintain 允許 ~580）
- [ ] 2 個 read-only skill 含 `context: fork` + `agent`
- [ ] `commands/CLAUDE.md` 反映官方 frontmatter 欄位
- [ ] Git commit 按段落分開

---

> **🎯 目標回顧**: 本 EP 的每一個段落都直接服務於「降低 prompt 次數，同時維持或提升產出品質」這個核心目標：
>
> | 段落 | 降低 Prompt 機制 | 品質影響 |
> |------|-----------------|---------|
> | S1 `when_to_use` | 精準路由 → 少 1-2 輪找錯 skill | 正面：正確的 skill 做正確的事 |
> | S2 Supporting Files | 精簡 context → 少 2-3 輪遺忘指令 | 正面：指令不被參考資料稀釋 |
> | S3 `context: fork` | 主 context 乾淨 → 品質提升 | 正面：分析結果更聚焦 |
> | S4 清理 + 文檔 | 移除無效欄位 → 減少混淆 | 正面：文檔與實際一致 |
>
> **不做的事**（避免降低品質的風險）：
> - 不對互動型 skill 加 fork（`build`、`code-review`、`explain`）
> - 不加 `paths` 限制（避免阻止有用的自動觸發）
> - 不盲目採用 ChatGPT/Gemini 的 agent OS 架構（已驗證不適用）
