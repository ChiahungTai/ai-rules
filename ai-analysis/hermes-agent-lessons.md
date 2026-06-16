# Hermes Agent 經驗對 ai-rules 的啟發（天馬行空發想）

> 本文基於對 `/Users/ctai/Github/hermes-agent`（Nous Research 的 Hermes Agent）三大子系統＋架構的深度分析（見 [`hermes-agent/ai-analysis/`](../../../hermes-agent/ai-analysis/)），**自由發想**這些經驗如何啟發本 repo（`ai-rules`——使用者的 AI 協作開發規則庫）的演化。
>
> 用戶要求：「天馬行空不受限的發想」「不用省篇幅」。故本文混合**務實可落地**與**激進願景**兩種構想，每條都標明。所有 Hermes 引用附 `path:line`（來自前述分析），ai-rules 對照引用本 repo 真實檔案/命令。

---

## 0. 兩個系統的本質對照（為什麼這個借鏡有效）

| 維度 | Hermes Agent | ai-rules |
|---|---|---|
| 本質 | 一個**正在跑的**、自我改進的 agent | 一個**靜態的**規則/skill/命令庫，塑造 AI 如何協作 |
| 「自我改進」 | 自動（背景 review fork＋curator＋memory） | **人工**（`/flow-feedback` 收集 → `/flow-review` 聚合 → 人類決策 → `/spec` → `/build`） |
| 載體 | Python 程式碼（`AIAgent` 迴圈） | Markdown 規則＋slash commands＋skills |
| 時間視角 | runtime 連續演化 | 規則版本＝git commit，跳躍演化 |

**核心洞察**：ai-rules **已經有一個自我改進迴圈**（`flow-feedback` → `flow-review` → `/spec` → `/build` → `/commit`），但它是**人工驅動**的——需要人類 fire `/flow-review`、人類判讀、人類決策。Hermes 證明了同一個迴圈可以**部分自動化**（背景 review fork 自動提案、curator 自動整併、consent queue 把關）。

**所以最高層次的借鏡不是「抄某個功能」，而是問：ai-rules 這個「規則庫」本身，能不能像 Hermes 的「skill 庫」一樣，成為一個有生命週期、有遙測、有自動整併、有 provenance 的自我演化系統？**

這是本文的主軸。

---

## 1. 逐主題借鏡

### 1.1 背景審查 fork → 「自動規則審查」daemon（最高價值）

**Hermes 機制**：每 ~10 turn，fork 一個 `AIAgent`，只給 `{memory, skills}` tool 白名單，重播對話快照，被 `_SKILL_REVIEW_PROMPT`（`agent/background_review.py:45-148`）指示**主動**把使用者偏好與挫折訊號（「別再做 X」「這太冗長」）寫進 skill 而非只是 memory。它繼承 parent 的 cached system prompt 保 prefix cache（~26% 成本降低），`skip_memory=True` 防污染，工具白名單防越權（`background_review.py:470-483`）。

**ai-rules 現狀**：`/flow-feedback [摩擦描述]`（`commands/flow-feedback.md`）收集 session 摩擦 → 寫 `ai-analysis/flow-feedback/`；`/flow-review [--since]`（`commands/flow-review.md`）定期讀累積回饋、找重複摩擦、聚合 type-2 設計缺陷、**跟 user 討論**。這是 B 軸（人類判斷驅動）的設計——刻意的。

**移植構想（務實）**：在 `/flow-review` 之前加一個**自動提案層**——一個背景審查 daemon（或 `/flow-review --auto-scan` 模式），它掃描最近的 `flow-feedback/`＋近期 git diff＋近期 session 摘要，**自動產出**「type-1（時機：該用 /X 沒用）」與「type-2（設計缺陷）」的**結構化提案草稿**，寫入 `ai-analysis/flow-review/proposals/`。人類 `/flow-review` 時面對的不是原始摩擦，而是**已分類、已聚合、已附 counter-factual 的提案**。這把 Hermes「fork 自動讀+提案」的 80% 搬過來，但**保留 ai-rules 的 B 軸鐵律**——人類仍是最終決策者（對應 Hermes curator 的 consent-first，見 1.3）。

**天馬行空（激進）**：
- **「規則違反遙測」**：Hermes 用 `.usage.json` sidecar 追蹤 skill 的 `last_used_at`（`tools/skill_usage.py`）。ai-rules 可以追蹤**每條 rule 被違反的次數**——例如 `bash-hard-rules` 的「`python -c` 加註解」若反覆觸發權限提示，那條 rule 就是「高摩擦、低效果」候選。一個「rule telemetry」累積器（掛在 Claude Code hooks 的 `pre_tool_call`？）記錄哪條 rule 最常被引用/違反/導致摩擦。**違反頻率最高的 rule 不是「執法不力」，而是「規則本身有問題」的訊號**——這是 Hermes 沒有但 ai-rules 獨有的機會（因為 ai-rules 的 rule 是給 AI 讀的，AI 的遵守/違反本身就是遙測）。
- **「反模式自動捕獲」**：背景審查不只看 flow-feedback，還掃描「連續糾正 2 次仍失敗」（`context-management.md` 的訊號）的 session，自動把這類反模式蒸餾成 candidate rule。

---

### 1.2 全 index + 模型自選 的 skill 路由 → ai-rules skill 挑選的明確化

**Hermes 機制**：🔑 **沒有 router／keyword／embedding**。所有啟用 skill 的 name＋截斷 description 注入 system prompt（按 category 分組），附**強制指令**「回覆前掃描，相關者必須 `skill_view` 載入，寧可多載」（`agent/prompt_builder.py:1356-1382`）。選擇由主模型做。漸進揭露三層：`skills_list`→`skill_view`→`skill_view(file_path)`（`tools/skills_tool.py:684/859/1171`）。

**ai-rules 現狀**：`skills/using-agent-skills/` 是 meta-skill（治理 skill 發現與呼叫）；`rules/model-routing.md` 管 subagent 模型分派；skill 數量已多（~35 個），全載入成本真實。目前靠 skill 的 `description` 欄位讓 Claude 自行判斷載入——這其實就是 Hermes 的「全 index + 模型自選」，只是 ai-rules 沒有顯式的「強制掃描指令」與「漸進揭露契約」。

**移植構想（務實）**：
- **顯式化「全 index + 強制掃描 + 漸進揭露」契約**：在 `skills/CLAUDE.md`（skill 索引）或 `using-agent-skills` 裡，明確寫出 Hermes 那段「回覆前掃描 skill index、相關者必須載入、寧可多載」的指令，並定義三層揭露（一句話 description → SKILL.md body → supporting files）。這讓 ai-rules 的 skill 挑選從「隱含慣例」升級為「顯式合約」。
- **`compact_categories` 概念**：Hermes 在 coding focus mode 把非 coding skill 降級為名稱 only（`agent/prompt_builder.py:1318-1328`）。ai-rules 可依**任務網域**動態降級——量化交易 session 時，`frontend-ui-engineering`/`browser-testing-with-devtools`/`shipping-and-launch` 降級；一般開發 session 時，`trading-analysis`/`upgrade-nt`/`upgrade-sj` 降級。名稱仍可見（保召回），但 description 不載入（省 token）。這對應 ai-rules 的「context 是有限資源」（`claude-writing.md`）。

**天馬行空（激進）**：
- **Skill description 的 token 預算化**：Hermes 把 description 在 system prompt index 截斷到 ≤60 字元（`agent/skill_utils.py:653-655`）、在 tool 輸出 ≤1024。ai-rules 可對 skill description 設顯式 token 預算，並用 `skill-cleaner`（已存在！）定期審查哪些 description 過肥。
- **Embedding 預篩作為「拒絕採用」的對照組**：Hermes 刻意不要 embedding 預篩。ai-rules 在 skill 數量破 50+ 時，可實驗性比較「全 index」vs「embedding top-K 預篩」的召回率。但 Hermes 的哲學警告：**語意預篩會錯殺「看似無關實則關鍵」的 skill**。ai-rules 的 `deep-thinking.md`（第一性原理）也反對錶面相關性判斷——所以全 index 與 ai-rules 哲學共鳴，應為預設。

---

### 1.3 Consent-first suggestion queue → 規則變更治理

**Hermes 機制**：cron 的 suggestion 系統（`cron/suggestions.py`）——**任何自動化（catalog、blueprint、usage 推論）都流過同一個待確認 suggestion 佇列**，`MAX_PENDING=5`，使用者必須顯式 `accept_suggestion` 才落地，駁回以 `dedup_key` latch（`suggestions.py:18-22, 220-240`）。Curator 整併 skill 也**絕不刪除只封存**（`agent/curator.py:13`），突變前先 tar.gz 快照（`agent/curator_backup.py`）。

**ai-rules 現狀**：`commit-consent.md` 鐵律——LLM 絕不執行 git commit 除非用戶明確同意。`/commit` 展示再確認。這已經是 consent-first。但 ai-rules 的 `daily-maintain`（`commands/daily-maintain.md`）是 cron/launchd 驅動、**自動修正低風險問題＋commit**——這裡「低風險」的判定是寫死的。

**移植構想（務實）**：
- **三層風險閘門的 suggestion 化**：把 `daily-maintain` 的「自動修＋commit」改成 Hermes 式三層——🟢 低風險（lint/format/import）自動修＋commit（現狀）；🟡 中風險（rule 微調、doc 同步）寫入 suggestion 佇列等人類 `/project-review` 確認；🔴 高風險（rule 語意變更、新 rule）只產出提案草稿，連 suggestion 都不算，必須走完整 `/spec`→`/build`。這對應 ai-rules 既有的「風險分級驗證策略」（`ai-development-guide.md`），但套用到「規則變更」本身。
- **規則變更的快照與回滾**：Hermes curator 突變前 tar.gz 快照整個 skills 樹。ai-rules 的 rule 變更已有 git 兜底，但可以加一層「實驗性 rule」機制——AI 提案的 rule 先進 `.staged-rules/`，跑 N 個 session 觀察效果，再決定 merge 或丟棄。這是 Hermes「archive 不刪除」哲學的延伸。

**天馬行空（激進）**：
- **Rule 的 A/B testing**：Hermes 沒有這個（它的 skill 改了就改了）。但 ai-rules 因為是「給 AI 讀的規則」，可以對**同一條 rule 的兩個版本**做 A/B——一半 session 載入 v1、一半載入 v2，比較違反率/摩擦率/產出品質。這是 ai-rules 獨有的可能性（Hermes 的 skill 是給人用的 workflow，難 A/B；ai-rules 的 rule 是給 AI 讀的指令，天然可 A/B）。這呼應 `acceptance-evidence.md` 的「自動化對照（A/B diff）」演進方向。

---

### 1.4 Provenance + Curator → 規則生命週期管理

**Hermes 機制**：只有**背景審查 fork** 標記的 skill 才是 `agent-created`（`tools/skill_provenance.py:68`），**只有 agent-created skill 才 curator-eligible**（前景造的 skill 不被自動整併）。Curator 7 天週期：純函數狀態轉移（`active→stale(30d)→archived(90d)`，依 `.usage.json` 活動時間戳，`agent/curator.py:255`）＋ LLM fork 做 umbrella-building（合併窄 skill→class-level，反「skill 庫爆炸」，`CURATOR_REVIEW_PROMPT` `:344-483`）。

**ai-rules 現狀**：
- rules/ 已有**重疊**——`modern-cli-preference.md`、`lsp-navigation.md`、`bash-hard-rules.md` 都講工具選擇（rg/fd vs grep/find、LSP vs rg）；`code-edit-constraints.md` 與 `_ai-behavior-constraints.md` 都談 AI 行為；`quality-constraints.md` 與 `acceptance-evidence.md` 都談驗收。這正是 Hermes curator 要解決的「sprawl」。
- `skill-cleaner`（`skills/skill-cleaner/`）已存在——審查重複 skill、未用 skill、prompt-budget。這是 curator 的雛形。
- 但**沒有 provenance 標記**——無法區分「人寫核心 rule」與「AI 提案 rule」與「從失敗蒸餾 rule」。

**移植構想（務實）**：
- **Rule provenance 標記**：每條 rule/skill 的 frontmatter 加 `provenance: human-core | ai-proposed | distilled-from-failure | community` 與 `added:` 時間。AI 提案的 rule 強制帶 provenance＋可回滾標記。這對應 ai-rules 的 `_ai-behavior-constraints.md`（「AI 禁止加統計/版本」）——那是「AI 不能寫什麼」，provenance 是「AI 寫的要怎麼追蹤」，兩者互補。
- **規則 curator**：擴充 `skill-cleaner` 或 `/project-review` 成一個定期 curator——掃描 rules/ 的重疊（機械偵測：哪些 rule 引用相同符號、講相同原則），產出「合併建議」（如 `modern-cli-preference`＋`lsp-navigation`＋`bash-hard-rules` 的工具選擇段落可否整併成一個 `tool-selection.md` umbrella＋各自專業子段）。**只建議、不自動改**（consent-first，見 1.3）。這直接對應 Hermes curator 的 umbrella-building。

**天馬行空（激進）**：
- **Rule 的 stale/archive 生命週期**：Hermes 依 `last_used_at` 把 30 天沒用的 skill 轉 stale、90 天 archived。ai-rules 的 rule 可類比——若一條 rule 90 天沒被任何 session 引用、沒出現在任何 flow-feedback，它是 stale 候選。但 ai-rules 的 rule 多半是「常設規則」（如 commit-consent），不該輕易 archive。所以這裡要謹慎——provenance=`human-core` 的 rule 豁免生命週期，只有 `ai-proposed`/`distilled-from-failure` 的規則受 stale/archive 約束。這是個精密的雙軌：**人寫規則是憲法（永久），AI 蒸餾規則是判例（可演化）**。

---

### 1.5 Byte-stable 3-tier prompt → UC-Driven 三層文件的重新框架

**Hermes 機制**：system prompt 分三層——**stable tier**（byte-stable，保 prompt cache：SOUL.md、guidance、skills index）、**context tier**（cwd 相依：AGENTS.md/CLAUDE.md）、**volatile tier**（每 session/turn 變：memory 快照、時間戳）。Ephemeral 注入（memory prefetch、`pre_llm_call` plugin context）**絕不進 cached prefix**（`agent/system_prompt.py:62-387`，`agent/conversation_loop.py:736-746`）。時間戳只用日期（不用時間）以免每日失效 cache（`:365`）。

**ai-rules 現狀**：UC-Driven Development 的**三層文件體系**（`ai-development-guide.md`）已經對應——`CLAUDE.md` Capabilities（永久）、`SYSTEM-MAP.md`（現在）、`.kanban/`（暫時）。時間視角：永久/現在/暫時。**ai-rules 已經有這個概念**，只是沒有用 prompt-cache 的視角框架。

**移植構想（務實）**：
- **用 byte-stable 視角強化 UC-Driven 的論述**：在 `ai-development-guide.md` 或 `claude-writing.md` 裡，明確點出「CLAUDE.md（stable）/ SYSTEM-MAP（context）/ .kanban（volatile）」對應 prompt cache 的三層——這給「為什麼 CLAUDE.md 不該放頻繁變動的內容」一個**機械理由**（cache 失效＝成本），而不只是「signal/noise」的審美理由。這是個論述強化，零實作成本。
- **Volatile tier 的顯式化**：ai-rules 的對話中，「當前任務狀態」（當前 EP 段落、kanban 卡片、今天日期）是 volatile。Hermes 把這些注入 user message 而非 system prompt。ai-rules 可在 `context-engineering` skill 裡點明：**當前任務狀態屬 volatile，注入位置要與永久規則分離**，避免污染 system prompt 的穩定性。

**天馬行空（激進）**：
- **Cache-aware 的 CLAUDE.md 結構**：既然 `@path` transclusion 是「啟動時自動展開」，展開後的 CLAUDE.md 內容若頻繁變動會持續重算。ai-rules 可設計一個「CLAUDE.md fingerprint」——追蹤哪些 `@path` 引用的檔案最近變動，提示「這會使 cache 失效」。這是 Hermes 沒有但對 ai-rules（重度依賴 `@` transclusion）有價值的。
- **`/compact` 前的 volatile 萃取**：見 1.6。

---

### 1.6 `on_pre_compress` hook → Context 壓縮前的訊號萃取

**Hermes 機制**：`MemoryManager.on_pre_compress`（`agent/memory_manager.py:746`）讓 memory provider 在 context 壓縮**丟棄舊訊息之前**萃取洞察——「防訊號被摘要丟掉」。Honcho 用這個 hook 在壓縮前把重要 context 存走。

**ai-rules 現狀**：`context-management.md` 談 `/compact` 策略與 Summary Instructions（CLAUDE.md 裡有專門段落引導 compactor 保留什麼）。`acceptance-evidence.md` 點出「重構後必須重新確認證據有效」。但沒有「壓縮前自動萃取」的主動機制。

**移植構想（務實）**：
- **`/compact` 前的自動 flow-feedback 萃取**：在 `/compact` 觸發時（或 deep-work/build 長任務中途），自動掃描「即將被壓縮掉的 context」裡的**摩擦訊號**（連續糾正、權限提示卡關、同類錯誤重複），自動寫一筆 flow-feedback。這把「快要被遺忘的教訓」在壓縮前搶救下來。對應 Hermes `on_pre_compress` 的精神。
- **這可做成 Claude Code hook**（`SessionStart`/`PreCompact` 若支援）：壓縮前觸發一個輕量萃取腳本。

**天馬行空（激進）**：
- **「記憶搶救」daemon**：不只壓縮前，任何「context 即將丟失」的時刻（session 結束、`/clear`、context window 接近滿）都觸發萃取。這是 ai-rules 把 Hermes 的「學習迴圈」主動化的具體著力點——ai-rules 的 session 本身就是學習素材，但太多教訓隨 context 消失。

---

### 1.7 帶外子系統不擾動主流程 → 主 session 保護（共鳴點，非移植）

**Hermes 機制**：curator 完全在對話迴圈外（`agent/curator.py:1-22` docstring 明說），fork 自己的 `platform="curator"` agent。cron 每 job 全新 agent、`skip_memory=True` 防污染。背景 review fork 也 `skip_memory=True`（`background_review.py:384-398`）。理由：自我改進/排程**絕不能擾動**使用者的主 session cache、預算、memory representation。

**ai-rules 現狀**：`context-management.md`「研究用 subagent，結果摘要回主 session」、`model-routing.md`「review/verify/research/explore agent 降級，避免 bottleneck」——**ai-rules 已經有完全相同的哲學**。`acceptance-evidence.md` 進一步點出「同家族 LLM 共享系統性偏誤，quorum 對共同盲點無效」——這是對「獨立 context ≠ 獨立智能」的深刻認識。

**這條是共鳴而非移植**：ai-rules 在這裡**比 Hermes 更深刻**。Hermes 的 background review fork 用同一個模型，有 acceptance-evidence 點出的盲點；ai-rules 的 acceptance-evidence 已經識破這點。**借鏡方向反而是：把 acceptance-evidence 的 A/B 雙軸理論，反向寫成給 Hermes 式系統看的設計指引**——即「任何自我改進迴圈，其 A 軸（機器自驗）天花板是 AI 自洽，必須有 B 軸（人類驗收）兜底」。這強化了 1.1 的「保留人類決策」設計。

**天馬行空**：ai-rules 可發展一套「自我改進系統的安全檢查表」——任何自動 rule/skill 變更機制上線前，必須通過：provenance 標記、consent queue、可回滾、B 軸人類 viewport、acceptance-evidence 階層標示。這是把 ai-rules 既有的品質理論，**套用到「自我改進機制」這個新標的**。

---

### 1.8 NL-via-LLM + deterministic 驗證層 → EP/spec 的機械驗證

**Hermes 機制**：排程不寫 NL→cron parser，**讓 LLM 在對話裡產生結構化 schedule 字串**（`tools/cronjob_tools.py:465`）。但排程表達仍經 `parse_schedule`（`cron/jobs.py:289`）＋ `croniter` **機械驗證**。建立時掃 prompt injection（`tools/cronjob_tools.py:213`）、runtime 再掃一次（`cron/scheduler.py:1236`）。

**ai-rules 現狀**：`/spec`、`/execution-plan` 已經是 LLM 產出結構化文件（UC、EP）。`/ep-review`、`/ep-validate` 是**機械＋判讀驗證層**。這又是共鳴——ai-rules 已經採用「LLM 產結構＋機械驗證」哲學。

**移植構想（務實）**：
- **「LLM 產 + dry-run 驗證」模式的顯式命名**：把這個模式（Hermes cron 與 ai-rules EP 共用）提煉成一個顯式的設計原則，寫進 `api-and-interface-design` 或 `planning-and-task-breakdown` skill。原則：「**把語意判斷交給 LLM，但把契約驗證交給機械**——LLM 決定 `0 9 * * *`，croniter 驗證下 5 個 fire 時間；LLM 寫 EP pseudo-code，POC/ep-validate 驗證可行性」。
- **回顯式驗證**：Hermes cron 可改進點之一是「LLM 產 schedule 後，croniter dry-run 下 N 個 fire 時間回顯給使用者確認」（排程分析 02 的可改善點 2）。ai-rules 的 EP 已有 Scenario Matrix（`execution-plan.md`）——可強化「EP 產出後，機械展開所有 scenario 的觸發/預期，回顯給人類確認」（這正是 `deliverable-review` 元件 D 的方向，`acceptance-evidence.md` 已點出）。

---

### 1.9 Plugin hook 生命週期 → Claude Code hooks 的系統化運用

**Hermes 機制**：`hermes_cli/plugins.py:128` 的 `VALID_HOOKS` 涵蓋 tool/LLM/session/subagent/gateway/approval 生命週期（`pre_tool_call`/`post_tool_call`/`pre_llm_call`/`on_session_start`/...）。核心在適當點 `invoke_hook`。

**ai-rules 現狀**：ai-rules 跑在 Claude Code 上，Claude Code 有自己的 hooks（`settings.json`）。`update-config` skill（`skills/` 列表）碰 hooks。但 ai-rules 對 hooks 的運用**零散**——沒有系統化的「用 hook 實現帶外自動化」對照表。

**移植構想（務實）**：
- **「Hook 點位 → ai-rules 自動化」對照表**：整理一份「Claude Code hook X 可實現 ai-rules 自動化 Y」的對照。例如：`SessionStart` → 自動 `/standup`；`PreCompact` → 自動 flow-feedback 萃取（1.6）；`PostToolUse`（若 commit）→ 自動 `/audit-test`；`Stop` → 自動語音通知（`voice-notification`）。把 Hermes 的「plugin hook 是擴充點」思維，落地成 ai-rules 的 hook 配置指南。這對應 ai-rules 的 `fewer-permission-prompts` 與 `update-config`，但層次更高——不只是減少權限提示，而是**用 hook 把帶外自動化接上主流程**。

**天馬行空（激進）**：
- **ai-rules 專屬 hook pack**：發布一組推薦的 `settings.json` hook 配置（對應 ai-rules 的命令體系），一鍵安裝。這讓 ai-rules 從「被動規則庫」升級為「主動作業系統」——規則定義「應該怎麼做」，hook 確保「自動在對的時機做」。這是 Hermes「plugin 生態」的 ai-rules 版。

---

### 1.10 Trajectory 壓縮 → 典範蒸餾（離線學習）

**Hermes 機制**：`trajectory_compressor.py` 是**離線**資料集壓縮器，把完成的 trajectory 壓縮成訓練資料給下一世代模型（`trajectory_compressor.py:1-31`）。**不是 runtime 迴圈**。

**ai-rules 現狀**：ai-rules 不訓練模型。但 ai-rules 累積「成功的 EP→build→commit 軌跡」與「失敗/修正軌跡」。`flow-feedback`/`flow-review` 處理失敗側。

**移植構想（務實）**：
- **成功軌跡的「典範蒸餾」**：補 `flow-feedback`（收失敗）的對稱物——「成功蒸餾」。定期掃描成功的 `/build` 軌跡（尤其那些一次過、零 review 修正的），萃取出「為什麼這次順」的可遷移模式，寫成 candidate skill 或 `lessons-learnt` 性質的文件。Hermes 的 `SKILLS_GUIDANCE`（`agent/prompt_builder.py:172-179`）說「完成複雜任務後存成 skill」——ai-rules 可有 `/distill-win` 或在 `/commit` 時提示「這次很順，值得蒸餾嗎？」

**天馬行空（激進）**：
- **ai-rules 的「訓練資料」就是它自己**：Hermes 用 trajectory 訓練下一世代「模型」。ai-rules 沒有模型可訓，但它的「下一世代」是**它自己的 rule/skill 庫**。每次成功的協作模式蒸餾成 skill，就是 ai-rules 的「自我訓練」。這把 Hermes 的 trajectory 概念，轉化為 ai-rules 的「rule 庫演化驅動力」——**ai-rules 的 git history 就是它的訓練資料集**，而 curator（1.4）就是它的「訓練迴圈」。

---

## 2. 統合願景：ai-rules 2.0 — 一個自我改進的 AI 協作作業系統

把上述 10 條收斂成一個願景：

**現狀的 ai-rules** 是一個**靜態的、人工維護的**規則/skill/命令庫。它的自我改進靠人類（`/flow-review`）。

**願景的 ai-rules 2.0** 是一個**有生命週期的、部分自我改進的**作業系統，分三層：

1. **感知層（telemetry）**：rule 違反率、skill 引用率、權限提示頻率、flow-feedback 累積、成功/失敗軌跡——全部被動收集（掛 Claude Code hooks）。
2. **反思層（background review + curator）**：定期 daemon 掃描感知層，自動產出**結構化提案**（type-1 時機建議、type-2 設計缺陷、rule 合併建議、stale rule 候選、成功典範）。產出進 **consent queue**，不自動落地。
3. **治理層（consent + provenance + B-axis）**：人類 `/flow-review`/`/project-review` 判讀提案，決定落地。落地的變更帶 provenance（`ai-proposed` 標記）、可回滾、受生命週期約束（非 human-core 的可 stale/archive）。人類是 B 軸兜底，acceptance-evidence 階層標示每條 rule 的證據強度。

這對應 Hermes 的三迴圈（背景 review / curator / memory），但**關鍵差異在 B 軸**：ai-rules 的 acceptance-evidence 理論保證了「自我改進不會退化為 AI 自我強化錯誤」——這是 ai-rules 比 Hermes 更成熟的地方，也是 ai-rules 2.0 的護城河。

**這個願景的天馬行空之處**：ai-rules 不再只是「給 AI 讀的規則」，而是一個**會觀察自己被如何使用、會反思、會提案、會在人類監督下演化**的系統。它把 Hermes 的 self-improving 哲學，從「agent 自己變強」轉移到「協作規則自己變好」——而後者的影響面（每一個用 ai-rules 的 session）遠大於前者。

---

## 3. 風險與節制（acceptance-evidence 的警告）

本 repo 的 `acceptance-evidence.md` 是本文的**內建剎車**。它警告：

1. **證據獨立性塌縮**：AI 自己跑 background review、自己提案 rule 修改、自己驗證——這是「AI 同時寫實作與測試」的極致版。**最危險的不是提案太弱，而是提案與驗證共享同一個錯誤前提**（`acceptance-evidence.md` 核心原則）。所以 1.1 的自動提案層，**絕不能**也自動驗證自己——必須有獨立的人類 viewport（B 軸）。
2. **AI 自我改進的固有風險**（01-self-improvement 可改善點 1）：Hermes 的背景 review fork 自己決定寫什麼，沒有獨立品質閘門——錯誤偏好會持久化並在每個 session 重讀。ai-rules 2.0 必須避免這點——**provenance=`ai-proposed` 的 rule 強制帶 expiry + 定期 review**，不能成為新的「靜默錯誤來源」。
3. **過度工程**：Hermes 是生產級 agent，需要這些機制。ai-rules 是個人規則庫，**感知層的複雜度必須與收益匹配**——`acceptance-evidence.md`「避免過度工程是內建約束」。1.1 的 daemon、1.4 的 curator 都可能是 over-engineering，若沒有足夠的 rule 數量/摩擦頻率支撐。
4. **隱私**：1.6 的「context 萃取」、1.1 的「session 掃描」涉及對話內容分析。需明確邊界（只萃取結構化訊號，不持久化原始對話）。

**底線**：ai-rules 2.0 的自我改進，**A 軸（機器提案）可以自動化，B 軸（人類判斷）絕不能自動化**。這是 ai-rules 既有的鐵律（commit-consent、acceptance-evidence），也是它優於「全自動 Hermes」的根本原因。

---

## 4. 優先級建議（若要落地，先做什麼）

依「價值 / 實作成本 / 與既有哲學契合度」排序：

| 優先 | 構想 | 為什麼先 | 對應 Hermes |
|---|---|---|---|
| 🥇 P0 | **1.5 byte-stable 視角強化 UC-Driven 論述** | 零實作、純論述強化，立刻提升 CLAUDE.md 維護的自覺 | system prompt 3-tier |
| 🥇 P0 | **1.2 skill 挑選契約顯式化 + compact_categories** | 直接改善當前 ~35 skill 的 token 成本，與 context-engineering 共鳴 | 全 index + 模型自選 + compact_categories |
| 🥈 P1 | **1.4 rule provenance 標記** | 低成本（frontmatter），為所有後續自動化鋪路（沒有 provenance 就沒有安全的 curator） | skill_provenance |
| 🥈 P1 | **1.8 「LLM 產 + 機械驗證」原則顯式化** | 把既有的 EP/spec/cron 共用模式命名，提升跨命令一致性 | cron NL-via-LLM + croniter |
| 🥉 P2 | **1.3 三層風險閘門（daily-maintain suggestion 化）** | 中等成本，但直接降低自動 commit 的風險 | consent-first suggestion queue |
| 🥉 P2 | **1.1 + 1.6 自動 flow-feedback 萃取（on_pre_compress / session end）** | 中等成本，需 Claude Code hook 支援；是「感知層」的第一塊 | background review + on_pre_compress |
| ⏳ P3 | **1.4 rule curator（合併建議）** | 等 provenance（P1）落地後；依賴 rule 數量成長到值得整併 | curator umbrella-building |
| ⏳ P3 | **1.9 hook pack 系統化** | 等 hook 點位對照表成熟 | plugin hook lifecycle |
| 🔮 願景 | **1.10 成功典範蒸餾 / ai-rules 2.0 三層** | 長期，需感知+反思+治理三層都成熟 | trajectory + 三迴圈 |

---

## 5. 一句話總結

Hermes 證明了「自我改進、排程、skill 路由」可以工程化；ai-rules 已經有對應的人工版（`flow-review`、`/at`、`using-agent-skills`）。**最值得借鏡的不是任何單一功能，而是把 ai-rules 從「靜態規則庫」升級為「有 provenance、有遙測、有 consent queue、有人類 B 軸兜底的自我演化系統」——而 ai-rules 既有的 acceptance-evidence 理論，正是這個升級的安全護欄，是它優於全自動 Hermes 的根本。**

---

*本文為發想文件，非實作承諾。所有 Hermes 引用來自 [`hermes-agent/ai-analysis/`](../../../hermes-agent/ai-analysis/) 的深度分析（01-04）。落地任何構想前，應先走 ai-rules 自己的 `/spec` → `/execution-plan` → `/build` 流程，並以 acceptance-evidence 階層標示證據強度——用 ai-rules 的規則，改善 ai-rules 自己。*
