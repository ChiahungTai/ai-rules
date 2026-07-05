# ai-rules 專案

> 本檔是 **ai-rules 專案指令**（開本 repo 時讀）。**全域開發指南**（演化/驗證/UC-Driven/架構/量化鐵律）是另一份獨立檔 `ai-development-guide.md`，經各 harness 全域位置載入（`~/.claude/CLAUDE.md`、`~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md` → `ai-development-guide.md`），非本檔。

本專案管理 AI coding agent 的 rules、skills、commands（跨 harness：Claude Code / ZCode / OpenCode）。

所有 rules/skills/commands 的**文件本身供 AI 消費**（AI 讀 `.md` 來執行命令）—— 寫作、審查、修改以「AI 能否正確執行」為準。readability 對 AI = 結構可機械解析、指令可遵行，**不是人類閱讀流暢度**；禁止用「人類讀者需要前置框架/會困惑」這類人類認知論證當審查發現。無需人類式證據出處、版本履歷、精確專案數字（詳見 `rules/_ai-behavior-constraints.md`、`rules/instruction-writing.md`）。

> **文件受眾 ≠ 命令受眾**：文件一律給 AI 讀（執行用）；但命令的**產出**服務不同對象 —— LLM 執行鏈（機器消費）或人類 viewport（人消費）。命令的設計、審查、討論一律以「產出受眾」為頂層脊柱（見下）。

## 命令的受眾視角

> **核心心智模型**：commands 不是按生命週期階段（EP / code）分，是按**產出受眾**分。設計、審查、討論任何命令時，先問「這命令的產出給誰消費」。

### 受眾二分

| 軌道 | 消費者 | 產出形式 | 誰推動 |
|------|--------|---------|--------|
| **① LLM 執行鏈** | 機器自讀自判自修 | 工程化、self-contained（EP、findings、code） | AI 自主（人類開頭觸發） |
| **② 人類 viewport** | 人類用「大原則」判讀 | 意圖（行為 artifact + 認知誤差點）+ 結構（whole-picture 心智模型） | 人類切入（或 AI 產出、人類讀） |

兩軌道平行不交匯，服務不同讀者。`/ep-review`、`/code-review`、`/audit-test`、`/build` 內部審查、`/judge-review` 屬軌道 ①；`/deliverable-review`（交付）與 `/illustrate`（結構 viewport）是軌道 ② 的兩個命令。

### 原理：人補 LLM 的結構性 blind spot（direction >> quality）

人類 viewport 補的是 LLM 結構上做不到的兩件事 —— 都靠人的互補認知：

| LLM blind spot | 失敗 | 人類互補認知 | 命令 |
|----------------|------|-------------|------|
| 缺 whole picture → 重造既有 | 重造 enum / 模組 | 整體直覺（細節忘但感覺得到關係 / 重用） | `/illustrate`（結構 viewport） |
| 抓不準意圖 → 偏方向 | 漂亮但錯方向 | 持有 vision，判「這是我要的嗎」 | `/deliverable-review` |

**優先級：方向 >> 品質**。LLM 預期能做到 Clean Code 等級（頂多需人提點）；災難性、無法靠 polish 彌補的是方向錯 ——「程式碼架構再好也沒用，如果直接做錯方向」。所以 viewport 重度傾斜在**方向驗證**，不浪費人注意力在 code 品質（那是 `/code-review` + LLM 自身能力的事）。

> viewport 渲染的是人類**用來承載意圖 / 理解結構的 artifact**（use case / scenario / UI / 範例 / 心智模型），不是 code 結構（簽名 / 檔案樹 / drift / 覆蓋率 —— 那是 LLM 鏈的 `/code-review`、`/audit-test`）。

### 三層介入（證據獨立性遞增）

| 層 | 機制 | 獨立性 | 軸 |
|----|------|--------|-----|
| 1 | same-session LLM 自判（agent review、`/ep-review` in-pipeline、`/audit-test`） | 低 | A |
| 2 | 跨 session LLM 第二意見（開新 session 跑 `/code-review`/`/ep-review`，findings 貼回實作 LLM → `/judge-review`） | 中 | A |
| 3 | `/deliverable-review`（交付）+ `/illustrate`（結構 viewport）：人類 viewport 判讀 | 高（不同智能） | B |

理論底層（A/B 軸、L1-L6 證據階層、證據獨立性）見 `rules/acceptance-evidence.md`。本節是入口摘要，acceptance-evidence 是完整理論。

### 核心流程命令分類

| 命令 | 受眾 | 層 | 誰呼叫 |
|------|------|----|--------|
| `/spec` | LLM（人互動·需求釐清） | 鏈 | 人類觸發 |
| `/execution-plan` | LLM | 鏈 | 人類觸發 |
| `/ep-review` | LLM | 1（同 session 自判）/ 2（跨 session） | AI-self / 人類（跨 session） |
| `/ep-validate` | LLM | 鏈 | AI-self |
| `/build` | LLM | 鏈 | 人類觸發 |
| `/audit-test` | LLM | 1 | AI-self |
| `/code-review` | LLM | 1 / 2（跨 session） | LLM / 人類（跨 session） |
| `/judge-review` | LLM | 鏈 | AI-self |
| `/followup-review` | LLM | 2（Review LLM 驗收實作 LLM） | LLM / 人類觸發 |
| `/fix-test` `/lint-fix` | LLM | 鏈（修復） | AI-self |
| **`/deliverable-review`** | **人類（交付）** | **3** | **人類** |
| **`/illustrate`** | **人類（結構 viewport）** | **3** | **人類** |
| `/commit` | 人類確認 | — | 人類 |
| `/metadata-sync` | LLM | 1 | 人類 / AI-self |

工具/維護命令（`/standup`、`/doc-health`、`/consistency`、`/instruction:*` 等）與受眾模型正交，完整索引見 `commands/CLAUDE.md`。

## 專案結構

- `rules/` — 行為規範（載入機制因 harness 而異；Claude 端 auto-load，見 CLAUDE.md）
- `skills/` — 領域知識和工作流（on-demand；SKILL.md 開放標準，跨 harness 可攜）
- `commands/` — 命令工作流（invocation 因 harness 而異；Claude 端為 slash command，見 CLAUDE.md）
- `commands/instruction/_common/` — 共用子範本（`instruction:*` 命令的引用單元）
- `hooks/` — Hook 實作腳本（**Claude 專屬**：ZCode 3.2.5 實測 configuration-file 與 plugin hooks 對 native ZCode Agent 皆無效，見 [`zai-org/feedback#32`](https://github.com/zai-org/feedback/issues/32) P2 open；OpenCode/Codex 機制待考。Claude 端 hook 全綁 `~/.claude/settings.json` 的 PreToolUse/Stop/Notification 事件）
- `ref-docs/` — 參考文檔（外部書籍 PDF + 衍生分析）；PDF 受版權不 commit（`.gitignore` `ref-docs/*.pdf`）

## 寫作治理

新增 rule/skill/command 時遵守：

1. **先修剪測試**：這行知識從程式碼推導得出嗎？是 → 不寫
2. **選對載體**：Hook？Rule？Skill？按上面的分界判斷
3. **驗證附著**：rule/command 是否包含可驗證的標準？沒有驗證的規則是噪音
4. **長度預算**：CLAUDE.md 越長，AI 越容易忽略重要規則。一條規則一行能說完最好
