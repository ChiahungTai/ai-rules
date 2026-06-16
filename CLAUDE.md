# ai-rules 專案

本專案管理 Claude Code 的 rules、skills、commands。

所有 rules/skills/commands 的**文件本身供 AI 消費**（AI 讀 `.md` 來執行命令）—— 寫作、審查、修改以「AI 能否正確執行」為準。readability 對 AI = 結構可機械解析、指令可遵行，**不是人類閱讀流暢度**；禁止用「人類讀者需要前置框架/會困惑」這類人類認知論證當審查發現。無需人類式證據出處、版本履歷、精確專案數字（詳見 `rules/_ai-behavior-constraints`、`rules/claude-writing`）。

> **文件受眾 ≠ 命令受眾**：文件一律給 AI 讀（執行用）；但命令的**產出**服務不同對象 —— LLM 執行鏈（機器消費）或人類 viewport（人消費）。命令的設計、審查、討論一律以「產出受眾」為頂層脊柱（見下）。

## 命令的受眾視角

> **核心心智模型**：commands 不是按生命週期階段（EP / code）分，是按**產出受眾**分。設計、審查、討論任何命令時，先問「這命令的產出給誰消費」。

### 受眾二分

| 軌道 | 消費者 | 產出形式 | 誰推動 |
|------|--------|---------|--------|
| **① LLM 執行鏈** | 機器自讀自判自修 | 工程化、self-contained（EP、findings、code） | AI 自主（人類開頭觸發） |
| **② 人類 viewport** | 人類用「大原則」判讀 | 意圖（行為 artifact + 認知誤差點）+ 結構（whole-picture 心智模型） | 人類切入（或 AI 產出、人類讀） |

兩軌道平行不交匯，服務不同讀者。`/ep-review`、`/code-review`、`/audit-test`、`/build` 內部審查、`/judge-review` 屬軌道 ①；`/deliverable-review`（交付）與 `/arch-review`（結構）是軌道 ② 的兩個命令。

### 原理：人補 LLM 的結構性 blind spot（direction >> quality）

人類 viewport 補的是 LLM 結構上做不到的兩件事 —— 都靠人的互補認知：

| LLM blind spot | 失敗 | 人類互補認知 | 命令 |
|----------------|------|-------------|------|
| 缺 whole picture → 重造既有 | 重造 enum / 模組 | 整體直覺（細節忘但感覺得到關係 / 重用） | `/arch-review` |
| 抓不準意圖 → 偏方向 | 漂亮但錯方向 | 持有 vision，判「這是我要的嗎」 | `/deliverable-review` |

**優先級：方向 >> 品質**。LLM 預期能做到 Clean Code 等級（頂多需人提點）；災難性、無法靠 polish 彌補的是方向錯 ——「程式碼架構再好也沒用，如果直接做錯方向」。所以 viewport 重度傾斜在**方向驗證**，不浪費人注意力在 code 品質（那是 `/code-review` + LLM 自身能力的事）。

> viewport 渲染的是人類**用來承載意圖 / 理解結構的 artifact**（use case / scenario / UI / 範例 / 心智模型），不是 code 結構（簽名 / 檔案樹 / drift / 覆蓋率 —— 那是 LLM 鏈的 `/code-review`、`/audit-test`）。

### 三層介入（證據獨立性遞增）

| 層 | 機制 | 獨立性 | 軸 |
|----|------|--------|-----|
| 1 | same-session LLM 自判（agent review、`/ep-review` in-pipeline、`/audit-test`） | 低 | A |
| 2 | 跨 session LLM 第二意見（開新 session 跑 `/code-review`/`/ep-review`，findings 貼回實作 LLM → `/judge-review`） | 中 | A |
| 3 | `/deliverable-review`（交付）+ `/arch-review`（結構）：人類 viewport 判讀 | 高（不同智能） | B |

理論底層（A/B 軸、L1-L6 證據階層、證據獨立性）見 `rules/acceptance-evidence.md`。本節是入口摘要，acceptance-evidence 是完整理論。

### 核心流程命令分類

| 命令 | 受眾 | 層 | 誰呼叫 |
|------|------|----|--------|
| `/spec` | LLM（人互動） | 鏈 | 人類觸發 |
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
| **`/arch-review`** | **人類（結構）** | **3** | **人類** |
| `/commit` | 人類確認 | — | 人類 |

工具/維護命令（`/standup`、`/doc-health`、`/consistency`、`/claude:*` 等）與受眾模型正交，完整索引見 `commands/CLAUDE.md`。

## 專案結構

- `rules/` — Auto-loaded 行為規範（每次 session 載入）
- `skills/` — On-demand 領域知識和工作流
- `commands/` — Slash commands（`/invoke` 時載入）；依受眾分類（見上）
- `commands/claude/_common/` — 共用子範本（`claude:*` 命令的引用單元）
- `agents/` — Custom subagent 定義（Agent tool 按需委派，跨專案可用）

## 載體選擇

> 載體維度是「**執行確定性**」（何時載入、多確定會執行），與「受眾」（產出給誰）正交。同一命令（如 `/deliverable-review`，人類受眾）可用 Rule 治理其行為、用 Agent 委派調查。

| 需求 | 用什麼 | 為什麼 |
|------|--------|--------|
| 必須每次零例外執行 | **Hook**（`.claude/settings.json`） | 確定性保證，非建議性 |
| 每次 session 都需遵守的行為規範 | **Rule**（`~/.claude/rules/`） | Auto-loaded，治理性 |
| 不需要每次載入的領域知識或工作流 | **Skill**（`.claude/skills/`） | On-demand，不消耗日常 context |
| 按需委派的專家子能力 | **Agent**（`~/.claude/agents/`） | 獨立 context，由主對話視任務委派 |

**判斷原則**：
- 如果忘了執行會造成損害 → Hook（如：commit 前跑 lint）
- 如果 AI 不知道就會犯錯 → Rule（如：用 `fd` 不用 `find`）
- 如果只在特定任務才需要 → Skill（如：Mermaid 圖表生成）
- 如果需要獨立 context 執行專家任務 → Agent（如：LSP 架構驗證）

## 寫作治理

新增 rule/skill/command 時遵守：

1. **先修剪測試**：這行知識從程式碼推導得出嗎？是 → 不寫
2. **選對載體**：Hook？Rule？Skill？按上面的分界判斷
3. **驗證附著**：rule/command 是否包含可驗證的標準？沒有驗證的規則是噪音
4. **長度預算**：CLAUDE.md 越長，AI 越容易忽略重要規則。一條規則一行能說完最好
