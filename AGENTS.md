# ai-rules 專案

> 本檔是 **ai-rules 專案指令**（開本 repo 時讀）。**全域開發指南**（演化/驗證/UC-Driven/架構/量化鐵律）是另一份獨立檔 `ai-development-guide.md`，經各 harness 全域位置載入——非 Claude 端：`~/.zcode/AGENTS.md` 等三家 → guide bundle；Claude 端：`~/.claude/CLAUDE.md` symlink → guide + `~/.claude/rules/` auto-load（不走 bundle）——非本檔。

本專案管理 AI coding agent 的 rules、skills、commands（跨 harness：Claude Code / ZCode / OpenCode / Codex）。

所有 rules/skills/commands 的**文件本身供 AI 消費**（AI 讀 `.md` 來執行命令）—— 寫作、審查、修改以「AI 能否正確執行」為準。readability 對 AI = 結構可機械解析、指令可遵行，**不是人類閱讀流暢度**；禁止用「人類讀者需要前置框架/會困惑」這類人類認知論證當審查發現。無需人類式證據出處、版本履歷、精確專案數字（詳見 instruction-writing skill、`rules/instruction-writing.md`）。

> **文件受眾 ≠ 命令受眾**：文件一律給 AI 讀（執行用）；但命令的**產出**服務不同對象 —— LLM 執行鏈（機器消費）或人類 viewport（人消費）。命令的設計、審查、討論一律以「產出受眾」為頂層脊柱（見下）。

## 消費端 context（know your customer）

> ai-rules 的 rules/skills/commands 部署到每個消費端專案、直接塑造其 session 行為——**設計決策 downstream 影響所有消費端**。設計/修改任何 command/skill/rule 前，先對照本段：它在消費端的真實工作情境下仍合理嗎？

**消費端畫像**：
- **solo developer + AI agent**（非團隊、無 CI）——一人與 AI 協作；沒有 code review 文化、沒有 CI 自動把關
- **工作單元 = 一 EP = 一 session**——一次 session 推進一個 Execution Plan；context 是稀缺資源
- **model 會退化**——長 session 後 LLM 行為變怪；消費端實務是「不硬撐：結算 EP 進度 → 開新 session 接續」（接續：`/at`、`/handoff`、EP 段落自足）
- **context 節奏**：`/compact` 分佈在 EP 各階段；command 必須在 compact 壓力下仍可接續
- **git 多軌**：多 worktree + 單一 trunk，feature 單向 rebase onto trunk（並行開發軌；軌名各專案自訂）
- **review 模式**：Writer/Reviewer 平行 session 分離（同 LLM 自審有 bias → 開新 session 審）

**設計含義**（設計 command/skill 時核對）：
- **自足**：段落自包含、進度可結算可接續（消費端會 compact、跨 session）
- **不依賴外部服務**：預設無 CI、無團隊 review——需人類判讀的走 viewport 命令（`/debrief`、`/illustrate`、`/smell-detector`），不假設 CI
- **git 認知**：涉及 git 的 command 尊重 worktree+trunk（不交互 rebase、trunk 永不被 rebase）
- **review 鏈**：review command 支援「產出 finding → 跨 session 貼回 → `/judge-review`」多 session 鏈
- **自主性**：自主 command（`/deep-work`、cron 排程）假設人類不在場——紅線/黃線分級 + 完成報告

## 命令的受眾視角

> **核心心智模型**：commands 不是按生命週期階段（EP / code）分，是按**產出受眾**分。設計、審查、討論任何命令時，先問「這命令的產出給誰消費」。

### 受眾二分

| 軌道 | 消費者 | 產出形式 | 誰推動 |
|------|--------|---------|--------|
| **① LLM 執行鏈** | 機器自讀自判自修 | 工程化、self-contained（EP、findings、code） | AI 自主（人類開頭觸發） |
| **② 人類 viewport** | 人類用「大原則」判讀 | 意圖（行為 artifact + 認知誤差點）+ 結構（whole-picture 心智模型） | 人類切入（或 AI 產出、人類讀） |

兩軌道平行不交匯，服務不同讀者。`/ep-review`、`/code-review`、`/audit-test`、`/implement` 內部審查、`/judge-review` 屬軌道 ①；`/debrief`（改動理解）、`/illustrate`（結構 viewport）、`/smell-detector`（壞味道：zoom 放大鏡 / baseline 盤點）是軌道 ② 的命令。**一檔兩受眾必然產生 token 牆——單檔單受眾**（失敗實證：/human-review 三度重建又棄）。

### 原理：人補 LLM 的結構性 blind spot（direction >> quality）

人類 viewport 補的是 LLM 結構上做不到的兩件事 —— 都靠人的互補認知：

| LLM blind spot | 失敗 | 人類互補認知 | 命令 |
|----------------|------|-------------|------|
| 缺 whole picture → 重造既有 | 重造 enum / 模組 | 整體直覺（細節忘但感覺得到關係 / 重用） | `/illustrate`（結構 viewport） |
| 抓不準意圖 → 偏方向 | 漂亮但錯方向 | 持有 vision，判「這是我要的嗎」 | `/debrief` |

**優先級：方向 >> 品質**。LLM 預期能做到 Clean Code 等級（頂多需人提點）；災難性、無法靠 polish 彌補的是方向錯 ——「程式碼架構再好也沒用，如果直接做錯方向」。所以 viewport 重度傾斜在**方向驗證**，不浪費人注意力在 code 品質（那是 `/code-review` + LLM 自身能力的事）。

> viewport 渲染的是人類**用來承載意圖 / 理解結構的 artifact**（use case / scenario / UI / 範例 / 心智模型），不是 code 結構（簽名 / 檔案樹 / drift / 覆蓋率 —— 那是 LLM 鏈的 `/code-review`、`/audit-test`）。

### 三層介入（證據獨立性遞增）

| 層 | 機制 | 獨立性 | 軸 |
|----|------|--------|-----|
| 1 | same-session LLM 自判（agent review、`/ep-review` in-pipeline、`/audit-test`） | 低 | A |
| 2 | 跨 session LLM 第二意見（開新 session 跑 `/code-review`/`/ep-review`，findings 貼回實作 LLM → `/judge-review`） | 中 | A |
| 3 | `/debrief`（改動理解+驗證證據）+ `/illustrate`（結構 viewport）+ `/smell-detector`（壞味道：zoom 放大鏡/baseline 盤點）：人類 viewport 判讀 | 高（不同智能） | B |

理論底層（A/B 軸、L1-L6 證據階層、證據獨立性、Claim→Evidence→Trust）見 `rules/acceptance-evidence.md`（always-on 核心）；深層理論（Runtime Invariant Assurance、Intent Drift Type A/B、filter trap、B 軸演進）見 acceptance-evidence skill（on-demand）。本節是入口摘要。

### 核心流程命令分類

| 命令 | 受眾 | 層 | 誰呼叫 |
|------|------|----|--------|
| `/spec` | LLM（人互動·需求釐清） | 鏈 | 人類觸發 |
| `/execution-plan` | LLM | 鏈 | 人類觸發 |
| `/ep-review` | LLM | 1（同 session 自判）/ 2（跨 session） | AI-self / 人類（跨 session） |
| `/ep-validate` | LLM | 鏈 | AI-self |
| `/implement` | LLM | 鏈 | 人類觸發 |
| `/post-build` | LLM | 鏈（build 後收尾鏈編排） | 人類觸發 |
| `/audit-test` | LLM | 1 | AI-self |
| `/code-review` | LLM | 1 / 2（跨 session） | LLM / 人類（跨 session） |
| `/judge-review` | LLM | 鏈 | AI-self |
| `/followup-review` | LLM | 2（Review LLM 驗收實作 LLM） | LLM / 人類觸發 |
| `/fix-test` `/lint-fix` | LLM | 鏈（修復） | AI-self |
| **`/debrief`** | **人類（改動理解簡報）** | **3** | **人類** |
| **`/illustrate`** | **人類（結構 viewport）** | **3** | **人類** |
| **`/smell-detector`** | **人類（壞味道偵測）** | **3** | **人類** |
| `/commit` | 人類確認 | — | 人類 |
| `/metadata-sync` | LLM | 1 | 人類 / AI-self |

工具/維護命令（`/doc-health`、`/consistency`、`/instruction-*` 等）與受眾模型正交，完整索引見 `skills/CLAUDE.md`。

## 專案結構

- `rules/` — 行為規範的 **always-on 核心**（載入機制因 harness 而異；部署紀律 + scope 分類 + 截斷線/尺寸 gate 見 `rules/AGENTS.md`——非 Claude 端是單檔 bundle，受 harness 截斷線約束（ZCode 實測 100KiB 硬編碼），rule 只放每次 session 都需要的內容）
- `skills/` — 領域知識和工作流 skills（on-demand；SKILL.md 開放標準，跨 harness 可攜；Claude 端 `/name` slash 與 Skill tool 皆可觸發，工作流 skills 索引見 `skills/CLAUDE.md`）。**reference skill 分層**：on-demand 級 rule 內容下沉至此——rule 留 always-on 核心＋pointer，深層住 `skills/<同名>/SKILL.md` 經全域 symlink 四 harness 按需可讀；這是控制 bundle 尺寸的既定模式（先例：acceptance-evidence / lsp-navigation / instruction-writing）
- `skills/_common/` — 共用子範本（跨 skill 引用單元，非 skill；`instruction-*` 等使用）
- `hooks/` — Hook 實作腳本（跨 Claude/ZCode 單一來源。hooks 無目錄載入點，**不能 symlink**——兩家 config 以絕對路徑引用本目錄腳本：Claude `~/.claude/settings.json`；ZCode 3.7.7+ user-level hooks，註冊範本 `hooks/zcode-registration.json`——**範本內容是 `~/.zcode/cli/config.json` `hooks:` 鍵下的子樹值，merge 進去而非整檔覆蓋**（整檔覆蓋會毀掉 config 的 mcp/plugins 區塊）、`notification.sh` 不移植。詳細實測與 ZCode 限制（事件子集、專案層忽略、per-session 快照）見 [04 報告 §7 修訂](ai-analysis/reports/superpowers/04-multi-harness機制對照.md)）
- `agents/` — 跨 harness subagent 定義（registry 結構：`shared/` 內容切片＋`zcode/`／`claude/` per-harness registry 視圖，`~/.zcode/agents`→`agents/zcode/`、`~/.claude/agents`→`agents/claude/`；tier-pinned 家族〔lite-verify/spec-miner/vision-review/cr-research〕、欄位相容策略與 ZCode Beta 限制見 [agents/AGENTS.md](agents/AGENTS.md)）
- `ref-docs/` — 參考文檔（外部書籍 PDF + 衍生分析）；PDF 受版權不 commit（`.gitignore` `ref-docs/*.pdf`）。`ref-docs/harness/` 是五家 harness 官方文檔鏡像（claude-code/opencode/zcode/codex/meta〔Muse Code〕）+ `contracts.md` 對照分析——**更新鏡像用既有工具 `ref-docs/harness/crawl.py`**（`uv run python ref-docs/harness/crawl.py [--source zcode]`，discover + sha256 增量寫入 + manifest 維護；不要手動逐頁鏡像）
- code-reality 工具鏈 — meta 層工具，**住獨立 repo `~/Github/code-reality`（Rust carrier，非本 repo 目錄）**；消費形態 `code-reality <tool> --repo <repo-root>`（binary 安裝與存在性偵測真相源見 skill）；工具用法/時點真相源 [skills/code-reality/SKILL.md](skills/code-reality/SKILL.md)；repo 知識歸各 repo 的 `.code-reality.toml` profile
- muse-plugin-cc — Muse Code 委派 plugin（ZCode/CC 雙端 marketplace 發佈），**住獨立 repo `~/Github/muse-plugin-cc`（非本 repo 目錄）**；消費形態 plugin agent（`muse-rescue` 委派、`muse:muse-runtime` skills）；計費鐵則＝純訂閱 5h 窗口（無 API key 面）、預設模型 pin `muse-spark-1.2`；CLI 事實真相源 [memory reference_muse-code-cli-facts]、委派細節真相源 repo `docs/`
- **Muse memory 唯讀**：`muse` 在本 repo **只讀不寫**——可用 `read_memory`（三 scope）與 `read_file` fallback 到 CC 實體池 `~/.claude/projects/-Users-ctai-Github-ai-rules/memory/`，**禁 `add_memory`/`edit_memory`**；需固化事實由 ZCode/CC 側寫入（見 `cross-harness-memory-symlink`）

## 寫作治理

新增 rule/skill/command 時遵守：

1. **先修剪測試**：這行知識從程式碼推導得出嗎？是 → 不寫
2. **選對載體**：Hook？Rule？Skill？Prompt/LLM 流程？判準——hook＝純機械＋單一入口＋無語義例外**三者皆是**（缺一即退 LLM 流程，假確定性比真語義危險）；rule＝每次 session 都需要的硬紀律（always-on 預算稀缺）；skill＝on-demand 方法論（理論深掘、失敗案例群、撰寫規範細則＝reference 分層）；語義判斷（有「看情況」例外）＝prompt/LLM 流程。完整決策樹與對照組見 instruction-writing skill「載體決策樹」；`deploy_agents.py` 的 90KiB gate 撞線時以此為處方
3. **驗證附著**：rule/command 是否包含可驗證的標準？沒有驗證的規則是噪音
4. **長度預算**：CLAUDE.md 越長，AI 越容易忽略重要規則。一條規則一行能說完最好
5. **部署同步**：編輯 `rules/` 後的部署與驗證紀律見 [rules/AGENTS.md](rules/AGENTS.md)「部署紀律」（含 `/sync-sources` 機械新鮮度檢查）
