# agents × model 調配＋agents 協同（fleet）研究素材

> 軸：多源（ZCode telemetry db 唯讀＋agent metadata ledger＋CC transcripts＋reports＋harness 鏡像文檔）
> 日期：2026-09-10｜方法：sqlite mode=ro 查詢＋metadata.json 彙整＋rg/Read 逐字引證
> 證據檔：`.agent-tmp/spawn-desc.txt`（1785 筆 spawn 描述）、`.agent-tmp/agent-meta.txt`（1751 筆 metadata 彙整）

---

## A. 使用史——user 的實際調配模式（ZCode 端）

### A1. 總量與成長

| 指標 | 值 | 證據 |
|---|---|---|
| 14 天 Agent tool spawn | 1785 次 | sqlite part 表 `json_extract(data,'$.tool')='Agent'`，time > 08-27；全歷史幾乎相同（功能 08-24 才啟用） |
| spawn 結果 | completed 2205 / error 53 / running 2（全歷史） | 同上 `$.state.status` |
| agent ledger（metadata.json） | 1751 個 agent（08-24 起） | `~/.zcode/cli/agents/` find metadata.json 計數 |
| ledger 終態 | **completed 1603（91.5%）／failed 79（4.5%）／stopped 52（3.0%）／running 17** | agent-meta.txt 彙整 `status` 欄 |
| 日量 ramp | 13（08-24）→ 77-99（08-29~09-01）→ 158（09-02）→ **peak 255（09-07）** → 66-82（09-08~09） | agent-meta.txt `createdAt` 日期分佈 |
| spawn 涉入面 | 209 個 parent session spawn 過 agent（14 天 335 個 interactive session 的 62%） | part 表 DISTINCT session_id vs session 表 |

### A2. subagent_type 分佈（14 天 spawn 呼叫數）

| type | 次數 | 主要用途（description 語料歸類） |
|---|---|---|
| vision-review | 522（29%） | 截圖/TA 圖判讀驗收（「6533 圖」「TA 圖判讀」） |
| Explore | 374（21%） | **79%（297/374）是審查軸**——EP 審查「結構軸/正確性軸」、Review「①clean/②UC/③正確性」視角（cheap review 軸） |
| code-reviewer | 257（14%） | fresh-eyes 審 diff（132 次 fresh-eyes 呼叫） |
| lite-verify | 122（7%） | flash 獨立覆核（清單驗證） |
| general-purpose | 103（6%） | 調查 23／實作 24／其餘混合（POC、成本調查） |
| code-reviewer-primed | 84（5%） | primed 審意圖對齊（98 次 primed 呼叫） |
| muse-rescue＋muse:muse-rescue | 95（5%） | muse 家族外部委派 |
| mem-distill | 50（3%） | memory 蒸餾 |
| impl-flash／impl-lite | 35＋16 | 實作型 agent（flash pin） |
| cr-research | 33（2%） | CR 圖譜研究（flash） |
| spec-miner | 21 | 規格採礦（flash） |
| cross-verify-investigator | 18 | 單軸查證（flash） |
| delegate-rescue／codex-rescue | 15＋20 | codex/delegate bridge 委派 |
| research-flash | 6（**6 次全 failed**） | 「flash組」三路平行研究——agent type 不在 registry，從未成功 |
| 其餘 | archify-gen 4、probe 類 ~9 | 試驗/探針 |

### A3. model × agent 矩陣（model_usage 表，14 天 turn 數）

| agent | full（GLM-5.3/glm-5.3） | flash（GLM-5.3-Flash/glm-5.3-flash） | 讀法 |
|---|---|---|---|
| zcode-agent（主線） | 39451 | 6108 | 主線偶爾降 flash |
| vision-review | 0 | 1997（100% flash） | 硬 pin flash |
| impl-flash | 0 | 1138（100%） | 硬 pin flash |
| impl-lite | 0 | 825（100%） | 硬 pin flash |
| mem-distill | 0 | 1077（33 turn error≈3%） | 硬 pin flash |
| lite-verify | 0 | 1013（100%） | 硬 pin flash |
| cr-research / spec-miner / cross-verify | 0 | 762／291／193（100%） | 全 flash |
| **code-reviewer** | 4164 | 760 | **預設 full、少數 flash**（與 model-routing「lite 預設、高保護面升 full」實況不符——實際偏 full） |
| code-reviewer-primed | 973 | 217 | 偏 full |
| Explore | 4441 | 660 | 多數繼承主線（full），flash 少數 |
| muse/codex/delegate-rescue | 471 | 39 | rescue 走 full |

- 語料中的 4 種 model 拼寫（GLM-5.3／glm-5.3／GLM-5.3-Flash／glm-5.3-flash）＝2 個實際 model——遙測無正規化。
- 分工輪廓：**機械/驗證/視覺/研究＝flash 硬 pin；review 主鏈（fresh-eyes/primed）＝full 為主；rescue＝full**。

### A4. 平行 vs 序列

| 訊號 | 值 | 證據 |
|---|---|---|
| run_in_background=1 | 1729/1785（**96.9%**） | part 表 input.run_in_background |
| spawn 呼叫時長 | 1710 次 <5s（背景即回）；>5s 僅 20 次 | state.time.end-start |
| 同 parent 同分鐘 fan-out | 1 次/min：824（54%）｜2 次：259｜3-5 次：121｜6+ 次：6（**max 11/min**） | part 表 group by session_id, minute |
| 高峰樣態 | 09-06 14:10 11 顆（LLM 標記）、09-01 09:50 10 顆（memory 全量審計）、09-01 06:53-07:11 處置股 golden 樹 9/8/7 顆三波 | 同上 |
| 雙 review 鏈 | 53 個 session 同時跑過 fresh-eyes＋primed（writer/reviewer 分離落地） | description INTERSECT 查詢 |

**調配模式一句**：96% 背景平行 spawn＋星形收割（主線等 wait/collect），fan-out 成組（2-5 顆常態、最多 11），review 用「Explore 軸審 → fresh-eyes → primed → judge」鏈，機械驗證全 flash 化。

### A5. 失敗分類（53 次 spawn error）

| 類型 | 次 | 樣本 |
|---|---|---|
| `Agent type 'X' not found`（registry 快照缺 type） | 22 | mem-distill×4、code-reviewer×3、research-flash×6、impl-flash/muse-rescue/impl-lite/archify-gen/probes——available agents 清單隨 session 變動 |
| `Required MCP tool is not available in the parent startup snapshot` | 7 | vision-review×5（mcp__4_5v_mcp__analyze_image）、code-reviewer/primed（zread）、cr-research（CR MCP） |
| cancelled before return | 8 | general-purpose/vision-review/mem-distill/Explore |
| 5h usage limit（muse 窗口） | 5 | Explore/mem-distill `[1308]` |
| rate limit | 1+ | mem-distill `[1302]` |

- **research-flash 全滅事件**（08-30）：想跑「flash組三路平行研究」×2 輪全數 `Agent type not found`——registry 沒有該 type，改用其他 type 才動起來。
- mem-distill 是 ledger 中失敗率最高者（42 spawn 中 9 failed≈21%＋10 spawn-call error）。

### A6. CC 端對照（~/.claude/projects/）

| 指標 | 值 | 證據 |
|---|---|---|
| Task 呼叫總量 | 150（全歷史，398 jsonl 中） | `rg '"subagent_type"'` 計數 |
| 分佈 | Explore 75／general-purpose 57／**fork 10**／code-reviewer 6／muse:muse-rescue 1／Plan 1 | 同上 uniq -c |
| ZCode:CC 使用比 | ≈ 1785:150（14 天內 CC 僅少數檔案活躍） | find -mtime -14 |
| fork 用法 | mosaic-alpha S2 重構——「production 已驗證勿動，fork 只改 5 個測試檔跑綠」 | agent-a6614b1a jsonl 內容 |

- CC 端有 CC 專屬形態：**fork**（繼承完整 context 的 subagent）、subagents/ 目錄結構（`<parent-session>/subagents/agent-*.jsonl`）。
- ZCode 是 fleet 主場（12 倍量差），CC 端零星。

### A7. metadata ledger 能力（~/.zcode/cli/agents/<parent>/agent_<id>/metadata.json）

每 agent 記錄：profileId、profileSnapshot（含 tools 白名單）、prompt 全文、status、totalDurationMs、totalTokens、usage（inputTokens/cacheReadTokens 細分）、childSessionId、parentToolUseId。樣本：Explore review agent 跑 370s、1.26M tokens（1.23M cache-read）——單顆 agent 成本可機械量測，但**從未有人彙整過**。

---

## B. 既有報告清單（ai-analysis/reports/，含 fleet 覆蓋判定）

| 報告 | 一句核心結論 | 協同/fleet 覆蓋 |
|---|---|---|
| `_done/superpowers/04-multi-harness機制對照.md` | 宣告式 rule 跨 harness 零翻譯故單層足夠；真缺口在下游消費側（skills/commands Claude-only、載入語意未驗證） | ❌ 無 agent 協作（僅觸及 sp 的 subagent dispatch 跨 harness 翻譯問題） |
| `_done/review-orchestration-圖解說明.md` | review 執行層集中 review-engine；spawn/另開 session 雙路徑；agent 預設 2-perspective（clean+UC）；spawn 失敗階梯 429→serialize→降級標記 | 🟡 有 spawn 編排與失敗階梯，但同 family 單 LLM、星形收割、無 agent 間通訊 |
| `_done/2026-08-29-skill-agent-rules-improvement-brainstorm.md` | 「工具在場、紀律在檔、接線不在生產路徑」；v1 經魔鬼代言人對抗後修訂 | 🟡 方法論上實證「三平行調查 agents＋flash lite-verify 獨立覆核＋魔鬼代言人」模式，無機制沉澱 |
| `_done/2026-09-01-cr-adoption-token-impact.md`＋`09-03-remeasure` | CR 導入 prompts/tokens 前後對比（db.sqlite 量測腳本可重用） | ❌（但證明 db 量測方法可復用於 fleet 成本量測） |
| `_done/cross-harness-commands-skills-deployment.md` | commands 跨 harness 無共用路徑，部署待決策 | ❌ |
| `_done/archify-pilot-report.md` | archify 渲染 pilot 成本/品閘結算（archify-gen agent 的來源） | ❌ |
| `2026-09-08-codex-agents-md-usage-and-insights.md` | Codex AGENTS.md 用法忠實整理＋arch-thinking 洞見 | ❌ 單 agent 指令層 |
| `2026-09-08-codex-philosophy-instruction-layering.md` | Codex 哲學＝小主檔＋引用＋skills＋memory＋MCP 五層互補；muse 64KiB 截斷已於 09-08 調 knob 根治 | ❌ |
| `2026-09-09-cr-role-audit.md` | CR 全流程角色稽核＋三顧問建議 | ✅ **完整 fleet 實證**：主 GLM-5.3 建基線 → 4 顆 flash cr-research 平行掃（mosaic 全 wt＋ai-rules＋zcode/muse 對話）→ 3 顧問（muse／GLM-5.3 general-purpose／codex web high）→ 綜合提案 |
| `2026-09-10-repo-consistency-scan.md` | 全 repo 一致性掃描（HEAD b75e8a7） | ✅ 同模式第二次實證：三軸 flash agents 平行（唯讀背景）＋muse/codex 顧問 |
| `2026-09-10-carrier-placement-v2-conference.md` | 載體選擇 v2 三方會議裁決書 | ✅ **跨 family 對抗式會議**：GLM 5.3 主導 × muse × codex 兩輪 bridge 接續，出現 round-2 立場互換→主導裁決收斂 |
| `2026-09-10-wt-workflow-decision.md` | WT 工作流裁決：primary=control plane、card WT=execution plane、1卡=1branch=1WT | 🟡 三方顧問模式（GLM×muse×codex＋業界查證） |
| `2026-09-10-wt-research-synthesis.md` | 兩份 WT 研究（ai-rules 側/mosaic 側）judge 對照融合 | 🟡 「judge 融合」角色實證（GLM 5.3 對照兩份外部研究） |
| `2026-09-10-blueprint-A-matrix.md`／`B-matrix` | 六線×檔案觸及面衝突矩陣（雙軸交叉驗證） | ❌ |
| `2026-09-10-holistic-design-review.md` | 八站斷點＋強化定案（④實作站 wrapper 直呼化等） | 間接（③⑥站 relay/session 接續是協同前提） |
| `2026-09-10-dryrun-uc67.md` | fresh machine/onboarding 紙上 dry run 斷點走查 | ❌ |

- spawn prompt 舉例的「model-vocab／flash 分工／dual-family」**報告檔名無命中**（rg `model.vocab|flash 分工` 無 report 檔）——該類知識現居 `rules/model-routing.md`＋`skills/model-routing/SKILL.md`（非 report 軸），B 軸內如實標記。

---

## C. 兩家 harness 的 fleet 機制對照

### Claude Code（ref-docs/harness/claude-code/docs/en/）

四層平行形態（`agents.md`「Run agents in parallel」總表）＋配套機制：

1. **Subagents**（`sub-agents.md`）：md＋YAML frontmatter（name/description/tools/model）定義檔，放 `.claude/agents/`（project）或 `~/.claude/agents/`（user）。description 驅動自動委派（合計 >15k tokens 啟動警告，細節下沉 system prompt）。內建 Explore/Plan（read-only、跳過 CLAUDE.md）＋general-purpose；Explore 自 v2.1.198 繼承主線 model（capped at Opus）。
2. **model 解析序**（`sub-agents.md`「Choose a model」）：per-invocation `model` 參數 > 定義檔 frontmatter（`inherit`＝主線）> `CLAUDE_CODE_SUBAGENT_MODEL` env > 主線 model；`_FORCE=1` 可壓過全部。組織 `availableModels` allowlist 擋掉時做 family 內替代或回退繼承。
3. **協同限制**：巢狀深度上限 3 層（子 agent 也能 spawn）；同 session 並行上限 20（`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`）；常見模式＝隔離高輸出量作業／平行研究／chain subagents（前顆產出傳後顆）。
4. **Agent teams**（`agent-teams.md`，實驗性 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）：lead＋teammates 完全獨立 session，**共享 task list＋teammate 直接互訊**（非星形）；teammate model 指定序＝spawn prompt 指名 > subagent 定義檔 > env > lead model；用途＝平行 review、competiting hypotheses 除錯、跨層協調；缺點=token 倍增、檔案衝突要靠分工不靠 worktree。
5. **Dynamic workflows**（`workflows.md`）：腳本跑大量 subagent 並**交叉驗證 findings**（codebase-wide audit、500-file migration、跨源研究）——計畫住在腳本而非 LLM turn 判斷。配套：worktrees（平行 session 檔案隔離）、cross-session messaging（同機/跨機 session 互傳）、`/batch`（大變更拆 5-30 個 worktree-isolated subagent 各開 PR）、fork（`/subtask` 繼承全 context 的 subagent）。

### Codex（ref-docs/harness/codex/）

1. **Subagent workflow**（`agent-configuration/subagents.md`）：平行 spawn＋主線等全部結果後合併回應；動機明文＝context pollution/rot（主線只留需求/決策/結論）；觸發＝明示要求或 AGENTS.md/skill 指示（Ultra 才主動委派）。
2. **模型分級**（同檔「Choosing models and reasoning」）：gpt-5.6（模糊多步重活）／gpt-5.6-terra（快掃、read-heavy 平行 worker）／gpt-5.6-luna（窄範圍高量輕任務）＋`model_reasoning_effort` 七檔（ultra/max/xhigh/high/medium/low）——reviewer 建議 high、掃描建議 medium。
3. **全域 config**（`config-file/config-reference.md`:692-704 佐證）：`[agents]` 表＝`enabled`／`max_concurrent_threads_per_session`／`default_subagent_model`／`default_subagent_reasoning_effort`／`interrupt_message`。
4. **Custom agent＝TOML 檔**（`~/.codex/agents/` 或 `.codex/agents/`）：必填 name/description/developer_instructions，可帶 model/effort/**sandbox_mode（可 read-only）**/mcp_servers/skills.config；內建 default/worker/explorer；解析序＝spawn 明示 > `[agents]` default > parent 繼承。
5. **編排守則**：read-heavy 先行（exploration/tests/triage/summarization）、write-heavy 平行謹慎（衝突＋協調成本）；sandbox/permission 繼承 parent turn；`/agent` 檢視切換 thread、可口語 steer/stop。官方兩個 pipeline 範例：`pr_explorer→reviewer→docs_researcher`（PR 審查）、`code_mapper→browser_debugger→ui_fixer`（UI 除錯）。

### 兩家對照速記

| 維度 | CC | Codex |
|---|---|---|
| 最小單位 | subagent（md 定義檔） | custom agent（TOML 定義檔） |
| model 指定 | frontmatter/per-invocation/env 四級序 | agent 檔/[agents] default/parent 三級序 |
| agent 間通訊 | agent teams 直接互訊＋共享 task list；cross-session messaging | 無（主線合併收割；thread 可檢視/steer 但不互訊） |
| 並行上限 | 20（env 可調）；深度 3 | `max_concurrent_threads_per_session`（可調） |
| 結果合流 | 主線收割／workflows 交叉驗證 | 主線等待合併 |
| 執行隔離 | worktrees（agent view 自動） | sandbox_mode per-agent（read-only 可釘） |

---

## 缺口——現有材料沒回答的

**已有答案**（討論時不必重查）：
- ZCode 端 registry×model 現況全景＋失敗分類（本檔 A）——「什麼任務配什麼 agent×model」有實測數據
- review 鏈編排（review-engine 雙路徑＋2-perspective＋失敗階梯）
- 跨 family 顧問/會議模式三次成功實證（cr-role-audit、consistency-scan、carrier conference/wt decision）＋bridge 直呼慣例
- 兩家 harness fleet 原生機制圖譜（本檔 C）

**真空**（agents×model＋協同討論的未答面）：
1. **無統一 fleet 機制設計**：平行掃＋顧問合成＋雙 review 散在個別報告作為一次性方法，無成文的協同慣例（誰 spawn、成組怎麼切軸、結果合流格式、衝突裁決權）——review 鏈是唯一有 SKILL 沉澱的子集。
2. **並行度/成組無規範**：兩家 harness 都有並行上限 knob，user 實測 max 11/min 但無自己的上限與 token 預算規則；model-routing 定義角色→tier 卻無「一個弧該開幾顆、何時 fan-out vs 序列」的規範。
3. **失敗階梯覆蓋不全**：429→serialize→降級只寫給 review spawn；實測兩大新興失敗——registry 快照缺 type（22 次）與 MCP 啟動快照缺工具（7 次，即 agents/AGENTS.md「CR plugin 啟動快照」陷阱的通用化）——無通用 fallback 處方。
4. **agent 間直接通訊零使用**：CC agent teams/cross-session messaging、codex thread steering 從未出現在 user 的遙測裡——全部是星形收割拓撲；「teammate 互辯」（carrier conference 那種）目前靠 bridge 人肉接線，不是 harness 原生。
5. **fleet 成本/效益零量測**：metadata.json 的 totalTokens/durationMs 可機械彙整但無人做過；cr-adoption 證明 db 量測方法可復用——「flash 硬 pin 是否真省／full review 是否真值」無數據。
6. **stopped（52 顆）回收慣例未定義**：背景 spawn 後 session 中斷/取消時的殘留處置（含 running 17 顆的狀態歸屬）。
7. **ZCode:CC 12 倍量差的 harness 分工未成文**：為何 ZCode 成為 fleet 主場、CC 端 fork（繼承 context）形態何時該用——model-routing skill 只寫 registry pin 不寫 harness 選擇。
8. **resumable agent 接續未整合**：model-routing 的 `wait <jobId>`（bridge 背景 job）與 ZCode background agent 的 childSessionId 接續是兩套機制，中斷後「誰欠誰一個 findings」無對帳方法。
