# Agentic Design Patterns → ai-rules → mosaic_alpha 應用分析

> 本文分析 Antonio Gulli《Agentic Design Patterns — A Hands-On Guide》(482 頁,21 patterns)如何能幫助 `ai-rules`,進而幫助消費者 `mosaic_alpha` 的開發。
>
> 方法:4 平行 research agent 各讀一域(ai-rules 設計原理、mosaic 消費模型、書 Part1+2、書 Part3+ 附錄)→ 主 session arch-thinking 合成 → **2 個 grounding agent 逐一驗證每個映射/建議對照實際檔案**(初版發生 false-gap:R2/R3/R4 誤報 + Memory 虛構,已校正)。本文為 grounding 校正後版本,所有 verdict 附 path:line 證據。

---

## 1. 核心洞察(grounding 校正後)

1. **ai-rules 本身就是一個 agentic system,且已實作書中 21 個 patterns 的 ~18 個** —— 但用**不同分解軸**。書問「這段 control flow 是什麼形狀?」(Prompt Chaining / Reflection / ...);ai-rules 問「這份產出給誰消費,多確定會被執行?」(受眾 × 載體)。兩者正交、可疊加。

2. **書對 ai-rules 的價值主要是「確認設計」,而非「揭示 gap」**。grounding 證實:初版以為的 3 個高代價 gap(R2 例外路徑驗證、R3 build/commit 閘門對稱、R4 review-pipeline recipe)**全都早已實作**,且多處比書的建議更細(如「可觀測≠已修復」visible/overlap-fixed/root-cause-fixed 三區分)。ai-rules 在「AI 協作開發治理」這個 use case 下,已是書的 patterns 的高完成度實作。

3. **真正存活的 gap 很少,且多半 by-design**。grounding 後僅 **R5(agent-friendly interface)**是高價值結構性缺口;其餘真 gap(output-filtering guardrail、動態 model 校準、production telemetry)屬低優先或刻意設計取捨。

4. **→ mosaic 的鏈也收斂**:mosaic 側真正存活缺口僅 **M3(live alpha drift 監控,SYSTEM-MAP 自承 🔧)**與 **M1(例外處理 handle 層 partial)**;初版宣稱的 M5/M6 早已存在,mosaic gap #5/#6 已解決。

---

## 2. arch-thinking 視角:為什麼「書 ≠ 取代 ai-rules 設計」

### ① 依賴規則(pattern 是 domain,載體是 adapter)

```
書的 21 patterns  =  agent 設計的 domain building blocks(「形狀」知識)
ai-rules 載體     =  部署/載入機制(Hook/Rule/Skill/Command/Agent — adapter 層)
```

兩層**依賴向內**:載體(adapter)依賴 pattern(domain)的概念,但 pattern 不依賴載體。一個 pattern 可被任意載體承載 —— Reflection 可在 Skill(review-engine)、Command(/code-review)、Agent(Reviewer subagent)中實作。這解釋了為什麼 ai-rules 不需要「照書重排」:它的載體分解是對的(解決「何時載入」),書的 pattern 分解也對(解決「什麼形狀」),兩者疊加而非互斥。

### ② bounded context(三個 context,pattern 跨域複用)

| context | 關心什麼 | 邊界 |
|---------|---------|------|
| 書 | 「如何打造 robust agent」 | 通用 agent 工程知識 |
| ai-rules | 「如何治理 AI 協作開發」 | 載體 × 受眾 × 驗證階層 |
| mosaic | 「如何做穩健量化交易」 | NT/SJ/catalog、crash-only、回測可現 |

Reflection / Memory / Goal-Monitoring 這類 pattern **跨三個 context 都成立**。ai-rules 的 bounded context 紀律體現在其載體不互滲(Rule ≠ Skill ≠ Command);書的 pattern 則是跨 context 的共用 domain 語彙。

### ③ use case 驅動(消費者要什麼行為)

- ai-rules 的消費者想要「方向正確、可驗收的 AI 協作開發」→ 組裝出受眾視角 + A/B 軸 + 驗證階層。
- mosaic 的消費者想要「扣完成本後正期望、可重現、不會自我毀滅的量化交易」→ 組裝出 crash-only + HITL policy + goal-driven 風控。

書的 patterns 是「積木」;ai-rules 與 mosaic 是「為各自 use case 組裝積木的成品」。use case 決定哪些 pattern 要重、哪些要輕。

---

## 3. ai-rules 設計原理速覽(合成基底)

| 設計維度 | 本質 | 設計理由 |
|---------|------|---------|
| **載體選擇** | 按「執行確定性」分層:Hook(零例外)→ Rule(auto-load 治理)→ Skill(on-demand)→ Command(主動觸發)→ Agent(獨立 context) | 每條知識放對位置 —— 該強制的機械化、該自律的自動載入、該按需的不消耗 context |
| **受眾視角** | 命令按產出受眾分,非生命週期:① LLM 執行鏈(機器消費)② 人類 viewport(人消費) | 人類注意力是稀缺資源,集中在機器結構性做不到的事(方向判讀、whole-picture) |
| **A/B 軸** | A 機器自驗(L1-L3,天花板=AI 自洽)B 人類驗收(L4-L6,充分性來源) | AI 同寫 test+impl = 證據獨立性塌縮,綠燈只證「自洽地重複自己的錯」 |
| **UC-Driven** | Capabilities 表(✅)+ .kanban(📋/🟡)+ /commit 原子操作 | UC 是「需求→實作→驗收」索引鍵,狀態可機械追蹤 |
| **驗證階層 L1-L6** | 證據債券:不同驗證手段產生不同強度證據,覆蓋不同 bug 類別 | 根本禁令:用低層證據冒充高層驗收是核心錯誤 |
| **演化性思維** | 測試保護下大膽重構,預設不考慮向後相容 | Git 是權威版本;品質優先於相容,讓重構阻力最小 |
| **review 家族** | review-engine(唯一真相源:嚴重度/信心/執行預設)+ 薄 adapter 命令 | 消除跨命令重複定義與 drift(DIP:domain 不被 adapter 污染) |

**靈魂**:對 AI 誠實性的結構性不信任(證據獨立性塌縮)× 對人類注意力的不對稱尊重(direction >> quality)。

---

## 4. 書的 pattern 體系速覍

書的 21 patterns(結論章歸 4 類 + Part Four 生產硬化):

| 類別 | Patterns |
|------|----------|
| **Core Execution & Decomposition** | Prompt Chaining · Routing · Parallelization · Planning |
| **Interaction with External Environment** | Tool Use · RAG · MCP · A2A |
| **State & Self-Improvement** | Memory · Learning(SICA 自我改 code)· Reflection · Self-Correction |
| **Collaboration** | Multi-Agent · HITL |
| **Goal & Reliability** | Goal Setting & Monitoring · Exception Handling |
| **Production Hardening(Part Four)** | Resource-Aware · Reasoning(CoT/ToT/ReAct/MASS)· Guardrails · Evaluation & Monitoring · Prioritization · Exploration |

**作者反覆強調的 trade-off**(貫穿全書):flexibility vs predictability(Ch6)、品質 vs 成本/latency(Ch4)、自主 vs 控制(Ch6/Ch9 overseer)。**沒有 pattern 是免費的**。

**與量化交易直接相關的例子**(作者多次以 trading bot 為例):Ch11「最大化報酬守住風險容忍度」、Ch12「insufficient funds / market closed 異常」、Ch13「human-on-the-loop:人設 70/30 + 單股<5% + -10% stop,AI 即時執行」、Ch20「多訊號競合的優先序」。

---

## 5. S1:書 → ai-rules 映射(grounding 校正)

### 5.1 映射表 — 18/21 ✅ verified,1 false positive 已刪

| Pattern | ai-rules 實作(載體) | verdict | 證據 | gap |
|---------|---------------------|---------|------|-----|
| **Prompt Chaining** | `/spec→/execution-plan→/build→/commit` UC 生命週期(Command) | ✅ | `commands/CLAUDE.md` 流程圖;`build.md:298`;`commit.md:195` | — |
| **Routing** | skill `description` 語意匹配 + 命令 dispatch | ✅(實作) | `skills/CLAUDE.md`;`using-agent-skills/SKILL.md:3,12-37` | 🔶 無專職「clarification sub-agent」路由器,但 clarification 行為散布存在(`using-agent-skills:57-67`) |
| **Parallelization** | `/build --max-agents`、worktree isolation | ✅ | `build.md:88,94-103`;`agent-workflow/SKILL.md:128,138-144` | — |
| **Reflection** | Writer-Reviewer 分離、`/code-review`、`/judge-review` | ✅ | `review-engine/SKILL.md:3,112-114,171`;`judge-review.md:2,40,91` | — |
| **Tool Use** | MCP + LSP + rg/fd + git 包成 tools | ✅ | `nt-query/SKILL.md:3,50,53`;`external-api-investigation/SKILL.md:3,8,46` | — |
| **Planning** | `/execution-plan` Self-Contained Segments | ✅ | `execution-plan.md:3,48,52`(simple 邊界=不過度規劃) | — |
| **Multi-Agent** | agent-workflow、worktree、force-獨立 review | ✅ | `agent-workflow/SKILL.md`;`review-engine/SKILL.md:171` | — |
| **Memory** | CLAUDE.md(長期語意)+ .kanban(任務態)+ flow-feedback(情節) | ✅(已刪虛構項) | `commands/flow-feedback.md:2` | ⚪ 無 vector 語意檢索(刻意,結構 recall 已足) |
| **Learning(SICA)** | `/flow-feedback→/flow-review→rules 演化`(人類把關版) | ✅ | `flow-feedback.md:2,15,36-39`;`flow-review.md:2,3,11,29` | ⚪ 無自主自我修改(刻意人類把關) |
| **MCP** | api-and-interface-design + source-driven-development | 🔶 partial | `api-and-interface-design/SKILL.md`(Hyrum's Law、Validate at Boundaries) | ❌ **agent-friendly interface 未涵蓋(= R5)**:Validate-at-Boundaries(邊界驗證)≠ agent-friendly(回 Markdown 非 PDF、filter/sort) |
| **Goal Setting & Monitoring** | `/deliverable-review`、`/audit-test` | ✅ | `deliverable-review.md:3,137,177-180`(認知誤差點) | — |
| **Exception Handling** | crash-only + arch-thinking 補償邏輯盤點 | ✅ | `arch-thinking/SKILL.md:125-135`(補償 pair) | ✅ EP 例外路徑驗證已實作(= R2,非 gap) |
| **HITL** | `/deliverable-review`、`/illustrate`、commit-consent | ✅ | `rules/commit-consent.md:9,37`;`deliverable-review.md` | — |
| **RAG** | `/sync-sources`、`/doc-health` | ✅ | `sync-sources.md:2,3,11,18,25,29` | — |
| **Resource-Aware** | model-routing.md(研究 agent 降級、並發 3) | ✅ | `rules/model-routing.md:5-12,16-20` | 🟢 無動態校準 / Critique Agent(靜態 tier) |
| **Reasoning** | deep-thinking + `/judge-review` | ✅ | `rules/deep-thinking.md:9,47-48,133-134` | — |
| **Guardrails** | rules-reminder、hooks、review-engine 嚴重度 | ✅(實作) | `rules-reminder/SKILL.md`;`hooks/block-python-c-comment.py`;`settings.json:314-324` | 🟢 無 output-filtering(僅 input-side PreToolUse) |
| **Evaluation & Monitoring** | `/audit-test`、validation-strategy、acceptance-evidence L1-L6 | ✅ | `acceptance-evidence.md:28-39,76-77` | 🟢 無 production-telemetry(dev-time 框架,by-design) |
| **Prioritization** | kanban lanes、findings risk matrix | ✅ | `maintain/SKILL.md:5`;`kanban-board/SKILL.md` | — |
| **Exploration** | idea-refine、`/spec` | ✅(deep-research 非自有) | `idea-refine/SKILL.md:3`;`spec.md` | ⚪ 探索偏輕(刻意);deep-research 是 plugin 命令非 ai-rules 自有 |
| **A2A** | agent 靠主 session 編排 | ✅ | `agents/`;skill `description`=自描述供 routing | ⚪ 單 harness N/A(刻意) |

### 5.2 已是 ai-rules「結構機械」的 pattern(比書的 prompt 層更強)

- **Reflection** → Writer-Reviewer「force-獨立 context + 3-perspective + 信心水準 enum」機械化(`review-engine`)。
- **Compensating pair(Exception Handling 進階)** → arch-thinking 反向 rg 補償訊號 + 兩處 docstring 矛盾指紋,把「B 抵消 A 的 bug」非引用關係變成可偵測結構(`arch-thinking/SKILL.md:125-135`)。
- **Evaluation drift** → `/sync-sources` 把「single-source invariant 沒被 drift」變成機械檢查(`sync-sources.md:25-35`)。

---

## 6. S1 強化建議(grounding 校正後)

> 初版 R2/R3/R4 經 grounding 確認**早已實作**(false gap)。本節僅留**通過 grounding 的真 gap**。

### ✅ 已實作(初版誤報為 gap,書確認設計)

- **R2** EP 例外路徑驗證:`/ep-review.md:112` + `/execution-plan.md:320`(含 visible/overlap-fixed/root-cause-fixed 三區分)+ `/build.md:48` 階段 0 硬掃。三層強制,比書 Ch12 更細。
- **R3** build/commit mypy 對稱:`/build.md:126,281` 每段 ruff+mypy+pytest,與 `/commit` 對稱。
- **R4** review-pipeline recipe:`commands/CLAUDE.md`「review-pipeline recipe」完整段落。

### 🔴 R5(唯一高價值真 gap):agent-friendly interface 成獨立設計關注

- 書 Ch10 MCP 最強警告:介面須 agent-friendly(回 Markdown 非 PDF、filter/sort、分頁),否則再好 pattern 也救不了。
- grounding:`rg "agent.friendly|markdown.*pdf|filter.*sort"` 全 ai-rules 0 hits;`api-and-interface-design/SKILL.md` 只涵蓋 Hyrum's Law / Validate at Boundaries / 穩定 API,**完全不涵蓋** agent 消費友善性;`code-review.md:68` 六軸無此軸。
- **落地**:已在 `api-and-interface-design/SKILL.md` 補「Agent-Friendly Interfaces」段落(本 session)。

### 🟢 真但低優先 / by-design

- **output-filtering guardrail**:`settings.json` 僅 PreToolUse(input-side),無 PostToolUse/Stop(output-side)。低優先。
- **Resource-Aware 動態校準 / Critique Agent**:model-routing 是靜態 tier,無動態校準。低優先。
- **Evaluation production-telemetry**:ai-rules 是 dev-time 框架,無 agent run runtime 監控。by-design。
- **R6 progress-stagnation overseer**:autonomous-execution 只偵測連續失敗,無進度停滯。低優先。

### ⚪ 刻意不落地(over-engineering)

- vector DB 語意檢索(結構 recall 已足)、A2A 協定(單 harness)、SICA 全自主自我修改(刻意人類把關)、永久嵌入 mapping 表到命令(留本文件即可)。

### ❌ 初版 false positive(已刪)

- §5.1 Memory row 初版宣稱「`memory/` 系統 + MEMORY.md 索引 = 教科書級 long-term store」—— **虛構**:ai-rules 無 `memory/` 目錄、無 MEMORY.md 檔(混淆自 mosaic / 全域 `~/.claude/.../memory/`)。Memory 載體實為 CLAUDE.md + .kanban + flow-feedback。

---

## 7. S2:→ mosaic_alpha(grounding 校正後)

### 7.1 mosaic 消費模型

- **單向 symlink 注入**:`~/.claude/{CLAUDE.md, skills, commands, rules, agents}` 全 symlink 到 ai-rules → mosaic 100% 倚賴 ai-rules,無本地 skills/commands。
- **mosaic 是 primary consumer / 共同設計者**:ai-rules 領域範例直接釘 mosaic(`ai-development-guide.md:122`);nt-query / trading-analysis / validation-strategy / upgrade-nt/sj 是純 quant 特化 skill。
- **生產級消費**:7 個 launchd plist 把 ai-rules commands cron 化。
- **3 worktree 共用 skills**:main / offline_backtesting / trading_lab 同一 symlink,單一源零 drift。

### 7.2 交易 pattern 直射(grounding 校正 —— 多數已存在)

| 書 pattern(trading 例子) | mosaic 現況(grounding) | verdict |
|---|---|---|
| Goal Setting(Ch11) | daily_loss 5% circuit breaker + BidAsk 緊急出場 + preflight 啟動閘,碎片化存在;封裝成顯式 goal-state framework 是認知/文件工作 | 🔶 M4 partial |
| Exception(Ch12) | detect ✅(NT OMS event 進 cache)+ recover ✅(live `reconciliation=True` broker truth);**handle 層缺**(策略無 `on_order_rejected`,paper optimistic-overlay 脫鉤) | 🔶 M1 partial |
| HITL(Ch13) | policy `frozen=True` config + Order.tags reason 有;缺顯式「execution 偏離 policy」deviation alert | 🔶 M2 partial |
| Evaluation drift(Ch19) | **回測強、live drift 監控無** —— `SYSTEM-MAP.md:226` **自承** 🔧「Live vs Backtest 一致性驗證 未自動化」 | ❌ M3 real |
| Resource-Aware(Ch16) | launchd 三階段(Backbone/Modern/Intraday)+ 3 worktree 已內化 fast/slow path | ✅ M5 已有 |
| Exploration+Learning(Ch21+Ch9) | AlphaForge(HITL 規則樹 + IG + sequential greedy)+ walkforward(expanding window)已 extensively 有 | ✅ M6 已有 |
| A2A | in-process(TradingHost 聚合)良好,非必要 | ⚪ M7 N/A |
| mosaic gap #5 NT source-first | nt-query SKILL.md 已 docs-first GATE 修復 | ✅ 已解決 |
| mosaic gap #6 scan-project false positive | 紀錄在 `_archive/`(2026-06-05),現況 skip 邏輯已避開 | ✅ 已解決 |

### 7.3 mosaic 真正存活強化點(僅 2)

- **🔴 M3 live alpha drift / regime drift 監控**:真實缺口(mosaic 自承)。中型。lever 既有 `session_exporter`(trades/equity parquet)+ `compute_backtest_metrics`,加 offline 比對腳本起步。定義 drift metric(sharpe/IC vs backtest baseline)+ 監控窗口 + 觸發動作。
- **🔶 M1 例外處理 handle 層**:加 strategy `on_order_rejected(self, event)` callback,清 optimistic overlay + log + 評估 re-submit/標記 signal dead。小-中。連動 R2(已實作,新 EP 寫例外處理會被強制驗證 handle path 經過失敗點)。
- M2(deviation alert)、M4(goal-state framework 封裝)= 認知/文件工作,走 `/illustrate` 非 code。
- M5/M6 ✅ 已有;gap #5/#6 ✅ 已解決。

---

## 8. chain(grounding 校正後)

```
書(21 patterns)─提供詞彙 + 完整性檢查→
ai-rules(已實作 ~18/21,受眾×載體分解)
  ├ 多數 pattern ✅ 已實作(書確認設計)
  ├ R2/R3/R4 = 初版 false gap(早已實作,多處比書更細)
  └ 唯一高價值真 gap:R5 agent-friendly interface → 已落地 api-and-interface-design
       ↓ symlink 自動惠及
mosaic_alpha(primary consumer,共同設計者)
  ├ M5/M6 ✅ 已有(launchd fast/slow、AlphaForge + walkforward)
  ├ gap #5/#6 ✅ 已解決
  └ 真正存活:M3(live alpha drift,🔴 真缺口)+ M1 handle 層(🔶 partial)
       → mosaic session 工程
```

**書的價值不是「找到一堆 gap」,而是**:(a) 確認 ai-rules/mosaic 已成熟;(b) 命名既有實作使其可推理;(c) 指出少數真 gap(R5、M3)。

---

## 9. 下一步(grounding 校正後)

| 項目 | 狀態 | 動作 |
|---|---|---|
| **R5** agent-friendly interface | ✅ 本 session 已落地(`api-and-interface-design/SKILL.md`) | 待 /commit |
| R2/R3/R4 | ✅ 早已實作(false gap) | 無 |
| **M3** live alpha drift | 🔴 真缺口(mosaic 側,自承) | mosaic session:`/spec` → `/execution-plan` |
| **M1** 例外 handle 層 | 🔶 partial(mosaic 側) | mosaic session:連動既有 R2 EP 驗證 |
| R6 / output-filtering / 動態校準 / telemetry | 🟢 真但低 / by-design | kanban card 或暫不動 |

**核心結論**:ai-rules 與 mosaic 在書的 pattern 體系下都已高度成熟;書主要的作用是**確認與命名**,而非揭示大量 gap。真正值得動的:ai-rules 側 **R5(已落地)**、mosaic 側 **M3(待 mosaic session)**。

---

## 10. 第一手精讀補強(全 21 章 + 前言親讀;書本理論錨點 ↔ ai-rules)

> 主 session 逐章第一手精讀(非 agent 轉述)後的補強。**結論:書多次用更 crisp 的語言,把 ai-rules 已落地機制背後的原理講出來 —— 印證多於教新。** 無 major flattening 校正(agent 報告準確);本節補的是「理論錨點」。

### 10.1 最深共振:Context Engineering(書)↔ ai-rules 全系統
書(Ch1 末 + Appendix A)把 **Context Engineering 提升為獨立紀律,位於 prompt engineering 之上**:「output 品質取決於 context 豐富度,非模型架構」;context 分層 = system prompt + 外部資料(retrieved docs + tool outputs)+ implicit data(user identity/history/env)。**這正是 ai-rules 的靈魂載體** —— `context-engineering` skill + `claude-writing.md` Encoder Philosophy(CLAUDE.md = 概念壓縮表示)+ 載體選擇(context 何時載入)。ai-rules 本質上就是一個 context-engineering 系統,書把這個隱含定位說清楚了。(Appendix A「Pydantic parse-don't-validate at boundaries」= api-and-interface-design Validate-at-Boundaries 的 cousin。)

### 10.2 AI "Contract" 4-pillar(Ch19)↔ Execution Plan —— 高價值新映射
書提「agent → advanced contractor」演化,4 pillar 與 ai-rules EP 流程**幾近一一對應**:

| 書 pillar | ai-rules 對應 |
|---|---|
| Formalized Contract(可驗證 deliverable + scope,單一真相源) | `/execution-plan`(驗收 criteria + Self-Contained Segments + EP 是 build 唯一真相) |
| Dynamic Negotiation(agent 先 flag 歧義/風險再執行) | `/spec`(需求釐清)+ EP Review 兜底假設路徑驗證(R2) |
| Quality-Focused Iterative Execution(對 contract criteria 自我驗證:gen→test→score→submit) | `/build`(TDD RED/GREEN + Agent Review loop + judge-review) |
| Hierarchical Subcontracts(大任務拆子 contract) | `ep_type: blueprint`(綱要 EP → 衍生子 EP) |

**意義**:EP 不只是「實作計畫」,在書的框架下它是 **formalized contract**(模糊任務→可驗證/可協商/可階層化的契約)—— 比「計畫書」更精準的定位。

### 10.3 Ch11 Goal/Monitor caveat = ai-rules 核心論題的獨立確認
書:「**same LLM 寫 code 又 judging quality → harder time discovering wrong direction**」「LLM may incorrectly assess as successful / hallucinate」。**這正是 ai-rules `acceptance-evidence.md` 核心論題「證據獨立性塌縮」**(AI 同寫 test+impl = 綠燈只證自洽地重複自己的錯)—— **書獨立講出同一洞見**,是 ai-rules 靈魂(A/B 軸、L1-L6、Writer-Reviewer)的理論背書。書解法 = 分離 Producer/Reviewer/Test-writer 多 agent = ai-rules Writer-Reviewer force-獨立 + `/audit-test`。

### 10.4 Ch18 "Engineering Reliable Agents":古典 SE 原則套到 agent
書明言「treat agents as complex software, apply proven SE disciplines」:
- **checkpoint/rollback**(transactional commit/rollback)↔ ai-rules commit-consent(原子操作)+ UC 原子性
- **modularity / separation of concerns**(專業小 agent 非 monolithic)↔ bounded context + 載體分離(Rule≠Skill≠Command)
- **observability via structured logging**(捕 chain-of-thought/tool calls/confidence)↔ `llm-output-convention`([FAIL]/[OK] tag + Logger)+ `/audit-test`
- **principle of least privilege**(最小權限、blast radius)↔ 權限分層(global vs project settings)+ scan-project

### 10.5 trajectory evaluation(Ch19)↔ acceptance-evidence L6 + audit-test
書:「traditional tests 不足;agent 機率性運作,須評 final output **and** trajectory(步驟序列)」,比較法 exact/in-order/any-order match、precision/recall。= ai-rules acceptance-evidence「評估 trajectory 非僅 endpoint」(L6 人類觀察)+ `/audit-test`(測試品質 = 步驟是否真測該行為)。

### 10.6 其他 crisp 錨點(充實 §5 mapping)
- **Planning「does the how need to be discovered, or already known?」**(Ch6)= ai-rules simple 邊界(不過度規劃小改)的精準判準
- **Reflection Producer-Critic 不同 system prompt 防 self-review 認知偏差**(Ch4)= Writer-Reviewer force-獨立的書本原型;+ Reflection 與 Memory 協同使 reflection cumulative(無 memory 自足、有 memory 累積)= flow-feedback→flow-review
- **Memory short-term(context,even long-context 只是放大、仍 ephemeral)vs long-term(3 型:semantic/episodic/procedural)**(Ch8)= ai-rules memory/(semantic)+ flow-feedback(episodic)+ rules/skills(procedural via flow-review);「long-context ≠ long-term」精準區分
- **SICA async overseer 偵測 loops/stagnation**(Ch9)= R6 的書本原型(confirmation)
- **HITL「human-on-the-loop」**(Ch13):人設 policy、AI 即時執行(trading 70/30、<5%、-10% stop)= mosaic 設計 + M2
- **Exception detect/handle/recover 3-layer + trading「insufficient funds/market closed→log,不重試 invalid,notify」**(Ch12)= M1 直射
- **MCP agent-friendly 反模式**(Ch10 逐字):「agents do NOT magically replace deterministic workflows; they require STRONGER deterministic support」「回 PDF 對不能 parse 的 agent 無用→應回 Markdown」= R5 落地的直接根基
- **Marco Argenti(Goldman CIO)**:static map vs GPS、交易/風控失誤代價、「messy systems + agents = disaster,須先 clean APIs / enterprise-as-software」= mosaic crash-only + R5 + 交易 stakes 的業界重量級背書
- **Agent Level 0-3**(前言:raw LLM → tool/RAG → strategic+context-eng → multi-agent)= ai-rules 落在 Level 2-3 的定位框

### 10.7 精讀範圍聲明(誠實)
- **第一手親讀**:全 21 章 + 前言(Introduction / What makes an agent / 5 hypotheses / Level 0-3)+ Appendix A 核心概念段 = 書的概念主體(~75%)
- **依賴 agent 報告(精讀中確認準確、無 flattening)**:Appendix A prompting 技術尾部、Appendix B-F(framework survey/CLI agents,參考性質)、Conclusion(4 類 + pattern 組合)、Glossary、Index —— 參考/查詢性質,邊際補強價值低

---

## 附:方法論教訓

本分析的初版發生 **completeness bias**(捏造 false gap):mosaic-consumer agent 讀了 `_done/`(**已歸檔=已解決**)flow-feedback 卻報告成 gap,合成時未回頭查實際檔案就列建議 → R2/R3/R4 誤報 + Memory 虛構。**教訓**:建議新增規則/記錄/覆蓋前,必須先 grounding(查實際檔案是否存在,附 path:line);`_done/`/`_archive/` 的摩擦 = 已解決,非 gap。本文件 §5-§7 的所有 verdict 已附 path:line 證據。
