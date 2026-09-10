# 02 — sp 借鑒到 ai-rules（選擇性吸收內容/手法）

> 接續 [`01-結構理解與診斷.md`](01-結構理解與診斷.md)。本檔是 **Session 結論的行動面**：不重寫整個 ai-rules 成 sp，但選擇性借鑒 sp 的「內容/手法/方法論」到 ai-rules 現有載體。
> sp fork 維護策略見本文附錄；OpenCode 退路見 [`03-OpenCode退路.md`](03-OpenCode退路.md)；決策摘要見 [`README.md`](README.md)。

---

## 核心區分：借鑒「內容/手法」，不借鑒「結構/機制」

sp 的東西分兩類，借鑒成本天差地別：

| 類型 | 舉例 | 借鑒成本 | 在「不重寫」下 |
|------|------|---------|---------------|
| **內容/手法/方法論** | skill-as-TDD 方法、file-handoff 手法、progress ledger 技巧、behavior-shaping 措辭、form-to-failure 理論 | 🟢 低 —— 吸收進 ai-rules 現有載體（rules/skills/commands） | ✅ 可借 |
| **結構/機制** | session-start bootstrap、多 harness adapter、plugin 分發、drill eval harness | 🔴 高 —— 這些是「sp 的底座」，要重寫才有 | ❌ 不借 |

**為什麼不借結構類**：session 確認不重寫整個 ai-rules（見 [`README.md` Session 結論](README.md)）。結構類機制（bootstrap/adapter/plugin/eval harness）是 sp 的底座，引進等於部分重寫，且與 ai-rules 哲學衝突（on-demand 省 context vs 強制載入；載體選擇 vs 全 skill）。借鑒只取「內容/手法」—— 可無痛吸收進 ai-rules 現有載體（rules auto-load / Skill on-demand / command / hook）。

---

## 借鑒清單（5 個內容類，按 ROI 排序）

| 優先 | 借鑒什麼 | 解 ai-rules 什麼痛點 | 載體建議 | 衝突 |
|------|---------|---------------------|---------|------|
| **P0** | **skill-as-TDD 方法論**（先跑壓力測試看 agent 失敗 → 寫 skill → 看遵守 → 堵漏洞） | ai-rules skill 品質靠事後 `/consistency` `/doc-health`，缺「前置 TDD 迴圈」 | 新建 `writing-skills` skill（on-demand，寫 skill 時載入流程）；或寫進 `skills/CLAUDE.md` 當「寫 skill 前必讀」 | 無 |
| **P0** | **progress ledger 防 compaction**（`.superpowers/sdd/progress.md` 模式：任務完成寫一行，compaction 後信任 ledger 不重做） | ai-rules 長任務（deep-work、`/build` 多段）跨 compaction 失憶，可能重做已完成段 | 引進 `/build` / `autonomous-execution` skill 機制；載體 = command/skill 步驟 | 無 |
| **P1** | **SDD file-handoff**（task-brief / report / review-package 用**檔案**交接，不 paste 進 context） | ai-rules `/build` 段落實作的 controller context 肥大問題 | 強化 `agent-workflow` + `self-contained-prompt` skill | 無（ai-rules 已有基礎） |
| **P1** | **Match the Form to the Failure**（prohibition vs recipe 理論：shaping 問題用 recipe 不用 prohibition；prohibition 在 shaping 上 backfire） | ai-rules 寫 rules/skills 時的手法精度 | 寫進 `instruction-writing.md` 或 `encoder-philosophy`（rule 載體，寫文檔時 auto-load） | 無（純理論） |
| **P2** | **behavior-shaping 措辭**（Red Flags tables、rationalization lists、「Iron Law」全大寫） | ai-rules 高違規風險 rules（`must-execute-before-complete`、`commit-consent`、`bash-hard-rules`）可更抗 rationalization | 強化既有 rules（不新建載體） | 無 |

> **來源 reference**：借鑒內容的 sp 原始出處 —— `skills/writing-skills/SKILL.md`（skill-as-TDD + Match the Form to the Failure）、`skills/subagent-driven-development/SKILL.md`（file-handoff + progress ledger + Model selection）、各 skill 的 Red Flags/rationalization tables（behavior-shaping 措辭）。

---

## 不借的（結構類，不重寫就沒有）

| sp 機制 | 為何不借 |
|--------|---------|
| **session-start bootstrap 強制載入** | ai-rules 已有 rules auto-load 等效（每 session 載入核心 rules）；強制載入跟 on-demand 省 context 衝突；不重寫就沒 bootstrap 層 |
| **多 harness adapter（tool mapping 層）** | ai-rules 已轉型 multi-harness（`deploy_agents.py` 部署 zcode/opencode/codex 三家），但**不需要 sp 的 tool mapping adapter 層**——adapter 解的是「動作詞彙翻譯成各家 tool name」，而 ai-rules 的 rule 是宣告式約束（跨 harness 讀取等價、無動作詞彙需翻譯）。這不是「scope 邊界」不借，是「**解的問題對宣告式 rule 不存在**」。機制根因與下游缺口詳 [`04-multi-harness機制對照.md`](04-multi-harness機制對照.md) §1-§2 |
| **drill eval harness（LLM verifier）** | ai-rules 的 B 軸人類 viewport 提示：eval 該是「人類 + 機械」混合，不是純 LLM verifier —— 借鑒 eval 的「前置壓力測試」精神（已併入 P0 skill-as-TDD），但不引進 drill 結構。理論詳 [`03` 附錄黃金連接點](03-OpenCode退路.md) |
| **Model selection per-task** | ai-rules `model-routing.md` 夠用；`/build` 不是 sp 的 fresh-subagent-per-task 模式 |

---

## 附錄：sp fork 維護策略（重心不在這，但保持清楚）

session 確認：sp 是 fork 參考源，**重心是 ai-rules 側借鑒，不重心改 sp**。所以 sp fork 維護採低投入策略：

| 做法 | 取捨 |
|------|------|
| **保持 upstream 純粹** | 不在 sp 加 fork-local 改 core（避免 drift 負擔）；要導航用 ai-rules 側報告（本報告 `01`）|
| **若已加 fork-local 導航 CLAUDE.md** | 可保留（自用導航）但認知：upstream 每次更新可能 drift；或退回純 upstream + 導航靠本報告 `01` |
| **upstream 貢獻** | 只挑低門檻的（如 Gemini 殘留清理）；不改 skill content（94% rejection + 需 eval 證據）|

> sp 結構債（6 個，全 upstream 歸因）詳 [`01` 結構債清單](01-結構理解與診斷.md)。這些是 upstream 的問題，fork 不必承擔修復。

---

> 接續：OpenCode 退路見 [`03-OpenCode退路.md`](03-OpenCode退路.md)；決策摘要見 [`README.md`](README.md)。
