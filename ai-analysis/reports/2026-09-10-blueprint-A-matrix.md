# Blueprint A — 線×觸及檔案面矩陣（六線平行衝突偵測）

- 問題：ai-rules backlog 六條執行線（L1–L6）各觸及哪些檔案/目錄；同一檔被 ≥2 線觸及的重疊清單
- 軸：repo 卡面文檔（git/repo 軸——backlog 卡×9＋報告×2＋機械錨點實測）
- 日期：2026-09-10｜方法：逐卡讀 desc＋notes 萃取**明示指名**檔案；報告 findings 逐條抽 path；禁腦補——卡面沒寫的標 ❔unknown
- 觸及類型：✏️修改｜➕新增｜❌刪除｜🔍唯讀·掃描·查證｜📍pointer 指向（卡面未述修改與否）｜❔落點未指名

## 0. 證據源與出處代號

| 代號 | 源 |
|---|---|
| 58:S1 等 | `backlog/tasks/air-58 - codex顧問化治理….md` Description 段落號／AC# |
| 58:AC#1 | 同卡 Acceptance Criteria 條號 |
| 60:desc／60:notes | `backlog/tasks/air-60….md`（notes＝09-10 triage 併弧段） |
| 61:desc／62:desc／64:desc／69:desc／69:notes | `backlog/completed/air-{61,62,64,69}*.md` |
| 63:desc／63:notes／67:desc／67:notes／68:desc／70:desc／70:notes | `backlog/tasks/air-{63,67,68,70}*.md` |
| RPT:G1…／RPT:S1…／RPT:F1…／RPT 低級 | `ai-analysis/reports/2026-09-10-repo-consistency-scan.md` ② Findings（:16–133） |
| RPT:P4-1…9 | 同報告 ④ 修復建議表（:161–173） |
| CONF:§二／§四／§五 | `ai-analysis/reports/2026-09-10-carrier-placement-v2-conference.md` |
| AUDIT:R1…R8 | `ai-analysis/reports/2026-09-09-cr-role-audit.md` R 行表（:189–196，本 session 實測引文在場） |
| 實測 | 本 session 機械核驗（rg/ls/sed 逐字引文，見各列） |

每條發現標 verified（證據在場：卡面原文＋必要時機械核驗）或 unverified（卡面未指名，僅推斷——本表一律標 ❔ 不入矩陣格）。

## 1. 矩陣表

### 1a. ai-rules repo — always-on rule／guide／根文檔

| 檔案 | L1 AIR-58 | L2 AIR-67 | L3 AIR-70 | L4 AIR-60 | L5 AIR-63 | L6 AIR-68 |
|---|---|---|---|---|---|---|
| `AGENTS.md`（根） | — | — | ✏️ 段一 G1「四家」清單〔RPT:G1 :23；P4-4〕 | — | — | — |
| `ai-development-guide.md` | — | — | ✏️ 段一 G1（:3）＋低 G7（:13）＋G9（:58）〔RPT:G1/G7/G9〕 | — | — | — |
| `CLAUDE.md`（根 wrapper） | — | — | ✏️ 低 G10（:15-26 載體表判準無單一源指向）〔RPT:G10〕 | — | — | — |
| `rules/AGENTS.md` | — | — | ✏️ 段一 G1（:10,40）＋G4（:46 部署紀律段登記 bundle:skip）＋低 G5（:94）〔RPT:G1/G4/G5；P4-3〕 | — | — | — |
| `rules/model-routing.md` | — | — | ✏️ 段一 S1（:16 role 表 impl/test-gen 幽靈——**最重**）〔RPT:S1 :41；P4-1〕 | — | — | — |
| `rules/context-management.md` | — | — | ✏️ 段一 S2（:23 STATE 三方對齊）〔RPT:S2 :46；P4-7〕 | ✏️ 段一 決策①「接手 quota 中斷先讀」清單→改引用恢復序列單一源〔60:desc①；驗收①〕 | — | — |
| `rules/bash-hard-rules.md` | — | — | ✏️ 段一 G2（:7）＋低 G8 歧異帶（:15,23）〔RPT:G2/G8〕 | — | — | — |
| `rules/code-edit-constraints.md` | — | — | ✏️ 段一 G2（:7 boilerplate 殘留）〔RPT:G2 :29〕 | — | — | — |
| `rules/acceptance-evidence.md` | — | — | 🔍 段一 G4（:15-21,49-51 為被剝內容——登記面在 rules/AGENTS.md 或改剝除策略）〔RPT:G4；P4-3〕 | — | — | — |
| `rules/modern-cli-preference.md` | — | — | ✏️ 低 G5 歧異帶（:7）〔RPT:G5〕 | — | — | — |
| `rules/_ai-behavior-constraints.md` | — | — | ✏️ 低 G5 歧異帶（:7）〔RPT:G5〕 | — | — | — |
| `rules/tool-discipline.md` | — | — | ✏️ 低 G8 歧異帶（:19）〔RPT:G8〕 | — | — | — |
| `rules/symbol-query-routing.md` | — | — | ✏️ 低 G7（:30 驗證順序字面相反）〔RPT:G7〕 | — | — | — |
| `rules/edit-discipline.md` | — | — | ✏️ 段二⑥ 規範歸位——卡面僅寫「edit-discipline」無路徑；repo 內唯一同名檔（❔推定此檔）〔69:notes⑥；實測 rules/ 無第二同名〕 | — | — | — |
| `rules/instruction-writing.md` | — | — | 🔍 低 G11 查證面（:3-4 `paths:`——實測三檔帶 paths：instruction-writing/python-standards/llm-output-convention）〔RPT:G11 :104；實測 rg `^paths:`〕 | — | — | — |
| `rules/python-standards.md`／`rules/llm-output-convention.md` | — | — | 🔍 低 G11 查證面（同上三檔）〔RPT:G11〕 | — | — | — |
| `scripts/deploy_agents.py` | — | — | 🔍 段一 G1（targets＝家族清單機械源，腳本改否未定）＋G11（paths: 消費端 probe）〔RPT:G1/P4-4；RPT:G11〕 | — | — | — |

### 1b. ai-rules repo — skills

| 檔案 | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| `skills/model-routing/SKILL.md` | ✏️ S1 codex 段 sweet spot 備註（AC#1）；❔AC#4 S4 決策記錄「model-routing/memory-audit 擇一」〔58:S1/AC#1/AC#4；實測 codex row :45、「session 定向接續」節 :163 在場〕 | — | 📍 段二① pointer 源（「model-routing 收法段是源」——條目刪正文留 pointer；skill 本體改否卡面未述）〔69:notes①〕 | ✏️ 段一 驗收③「session 定向接續」節加授權失效條款〔60:desc③驗收〕 | — | — |
| `skills/instruction-writing/SKILL.md` | — | — | ✏️ 段一 G1（家族清單第三版本）＋S6（:151 斷連結 lessons_learnt.md）〔RPT:G1 :24；RPT:S6 :67；P4-4/P4-9〕 | — | — | — |
| `skills/_common/state-md-write.md` | — | — | ✏️ 段一 S2（:3 刪 handoff 宣稱＋:34 同檔自打處——P4-7 修點）〔RPT:S2 :46；RPT:③ :151；P4-7〕 | — | — | — |
| `skills/_common/work-order.md` | — | ✏️ 段三 R6（:61 過時假議修正＋capability-aware 注入塊「工單/spawn prompt 注入塊」）〔67:notes 段三；AUDIT:R6；實測 :61 行在場〕 | ✏️ 段二⑦ 合約段一句＋留事故〔69:notes⑦〕 | ✏️ 段一 授權失效條款（驗收③「work-order 範本」）＋段二④ 工單模板同步〔60:desc③驗收；61:desc驗收④〕 | — | — |
| `skills/handoff/SKILL.md` | — | — | 🔍 段一 S2 基準側（:31——P4-7「以 handoff 自述為準」，本體未列修點）〔RPT:S2 :46；P4-7〕 | ✏️ 段一 決策① schema 欄序→改引用恢復序列單一源〔60:desc①驗收①〕 | ✏️ 件二 web 軌改寫 web-brief 雙軌（本地軌零變更）〔64:desc①⑤〕 | — |
| `skills/at/SKILL.md` | — | — | — | ✏️ 段一 決策①②③（「Resume 後的行為」1-4 改引用＋Phase 0 先結算＋resume prompt 授權失效條款）〔60:desc①②③；驗收②〕 | — | — |
| `skills/commit/SKILL.md` | — | — | ✏️ 段一 S3（:203 不再重畫 flow）＋低 S7（:38 ruff verify typo）〔RPT:S3 :51；RPT:S7 :106；P4-5〕 | — | — | — |
| `skills/usage-ping/SKILL.md` | — | — | ✏️ 段一 S4（:20,:30,:118 語音殘留）〔RPT:S4 :63；P4-6〕 | — | — | — |
| `skills/implement/SKILL.md` | — | — | ✏️ 段一 S5（:279 stale ref「commit 階段 3」）〔RPT:S5 :56；P4-9〕 | — | — | — |
| `skills/scan-project/SKILL.md` | — | — | ✏️ 低 S9（:57 `${CLAUDE_SKILL_DIR}` 無 ZCode fallback）〔RPT:S9 :110〕 | — | — | — |
| `skills/doc-health/SKILL.md` | — | — | ✏️ 低 S8 歧異帶（:36 SYSTEM-MAP 雙寫入 owner）〔RPT:S8 :108〕 | — | — | — |
| `skills/metadata-sync/SKILL.md` | — | — | ✏️ 低 S8 歧異帶（:3）〔RPT:S8〕 | — | — | — |
| `skills/rules-reminder/SKILL.md` | — | — | ✏️ 低 S10（:3 description「Claude Code rules」措辭——實測字串在本檔 :3）〔RPT:S10 :112；實測 rg〕 | — | — | — |
| `skills/kanban-board/SKILL.md` | — | — | ✏️ 段二④ 建卡段（worktree 直進 main 分流規範搬入）＋⑤ 卡操作段（id 對時一句）〔69:notes④⑤；CONF:§四〕 | — | — | — |
| `skills/instruction-clean/SKILL.md` | — | — | ✏️ 段二⑥ skill-deletion-consumer-scan 規範歸位〔69:notes⑥〕 | — | — | — |
| `skills/debugging-and-error-recovery/SKILL.md` | — | — | ✏️ 段二⑧ diagnose-installed-vs-source-first 規範歸位＋留事故〔69:notes⑧〕 | — | — | — |
| `skills/memory-audit/SKILL.md` | ❔ AC#4 S4 決策記錄歸檔「擇一」候選〔58:AC#4〕 | — | ✏️ 段二 A「載體統一定義表」兩處修補（層級閘首句＋誤置表 A/B；實測表在 :136）＋C 全量 audit 層 3 修正面〔70:notes 段二；69:notesA；CONF:§二〕 | — | ❔ 件一「canonical>pending 優先序有文字」落點卡面未指名〔63:AC#1〕 | — |
| `skills/memory-audit/scripts/generate_pending.py` | — | — | — | — | ➕ 件一 S1 生成器〔63:notes S1〕 | — |
| `skills/memory-audit/scripts/generate_index.py` | — | — | — | — | ✏️ 件一 S2 render_b_form＋routing 行→MEMORY.md 固定 pointer〔63:notes S2；實測檔案在場〕 | — |
| `skills/daily-maintain/SKILL.md` | — | — | — | — | ✏️ 件一 S3 Phase0 加 `_pending.md` refresh 為合法自產物〔63:notes S3〕 | — |
| `skills/self-contained-prompt/SKILL.md` | — | — | — | — | ✏️ 件二 web 軌改寫〔64:desc⑤「只改 self-contained-prompt＋handoff 兩檔」〕 | — |
| `skills/agent-review-cycle/SKILL.md` | — | — | — | — | 明示**不動**（負範圍）〔64:desc⑤〕 | — |
| `skills/followup-review/SKILL.md` | — | — | — | ✏️ 段二 雙 lens 分工＋primed 邊界——「或 post-build 鏈對應段」❔二擇一〔61:desc驗收①〕 | — | — |
| `skills/post-build/SKILL.md` | — | — | — | 🔍 段二 驗收③ 下游引用面掃描（修改❔）〔61:desc驗收③〕 | — | — |
| `skills/state-review/SKILL.md` | — | — | — | ✏️ 段二「派發形態現況」codex followup first-real-usage-pending→已驗證〔61:desc驗收②〕 | — | — |
| `skills/review-engine/SKILL.md` | — | ✏️ 段二 R1 negative-claim gate 語義化條文〔67:notes 段二；AUDIT:R1〕 | — | 🔍 段二 驗收③ 下游引用面掃描（修改❔）〔61:desc驗收③〕 | — | — |
| `skills/judge-review/SKILL.md` | — | ✏️ 段二 R1（驗證式承載 negative verdict 語義）〔67:notes 段二；AUDIT:R1〕 | — | 🔍 段二 驗收③ 下游引用面掃描（修改❔）〔61:desc驗收③〕 | — | — |
| `skills/execution-plan/SKILL.md` | — | ✏️ 段二 R1（claim 四欄結構觸發面）＋R3 落點❔（卡面僅述「EP 同層 references/research.md」機制，修改端檔案未指名）〔67:notes 段二；AUDIT:R3〕 | — | — | — | — |
| `skills/cr-query/SKILL.md` | — | ✏️ 段一 R2 五步 ladder 三檔同步〔67:desc R2；AUDIT:R2〕 | — | — | — | — |
| `skills/symbol-query-routing/SKILL.md` | — | ✏️ 段一 R2 三檔同步〔67:desc R2；AUDIT:R2〕 | — | — | — | — |
| `agents/roles/cr-research.md` | — | ✏️ 段一 R2 第一刀（:23 角色定義教錯 module-path query）〔67:desc R2；AUDIT:R2「第一刀修 :23」〕 | — | — | — | — |
| `.code-reality.toml`（repo 根） | — | ➕ 段一 R4＋smoke 驗證〔67:desc R4；實測現缺場（ls 無此檔）＝新增〕 | — | — | — | — |
| 恢復序列單一源（新落點） | — | — | — | ➕❔ 段一 決策①「合併為一條寫死的恢復序列單一源」——落點檔案卡面未指名〔60:desc①〕 | — | — |
| segment receipt 生成器＋測試 | — | — | — | ➕❔ 段三 機械欄生成 script（落點未指名；「生成器有測試」）〔62:desc①②；驗收①〕 | — | — |
| `ai-analysis/README.md` | — | — | ✏️ 段一 F3（:28 必查路徑撲空＋:21,:27）〔RPT:F3 :87；P4-9〕 | — | — | — |
| `ai-analysis/schedule-registry.md` | — | — | ✏️ 低 F5（:25 port 6421→6422）〔RPT:F5 :116〕 | — | — | — |
| `deploy/launchd/com.ai-rules.backlog-cleanup.plist` | — | — | ➕ 段一 F1 版控副本（LaunchAgents 在場、repo 缺——實測 deploy/launchd/ 僅 browser plist）〔RPT:F1 :75；P4-8；實測〕 | — | — | — |
| `deploy/scripts/run-backlog-cleanup.sh` | — | — | 🔍 段一 F4 條款源側（:7,:18-19,:27——修改面在 mosaic twin）〔RPT:F4 :79；P4-2〕 | — | — | — |
| `hooks/zcode-registration.json` | — | — | ✏️ 低 F2（:6 維護條款＋:78 版號 1.0.0→現役漂移）〔RPT:F2 :114〕 | — | — | — |

### 1c. memory 池（ai-rules 主體 `.agents/memory/`）

| 對象 | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| `feedback_bridge-job-completion-no-push.md` | — | — | ✏️ 段二① 規範正文刪＋留事故＋pointer〔69:notes①；CONF:§四；實測條目在場〕 | — | — | — |
| `reference_backlog-cli-entry.md` | — | — | ❌ 段二② 整條刪〔69:notes②〕 | — | — | — |
| `global-vs-project-permissions.md` | — | — | ✏️ 段二③ 重寫為 project 現況條（mixed 輕處置）〔69:notes③；CONF:§四〕 | — | — | — |
| `feedback_cross-session-commit-on-active-branch.md` | — | — | ✏️ 段二④ 規範搬出、留事故證據〔69:notes④〕 | — | — | — |
| `feedback_backlog-card-edit-precheck.md` | — | — | ✏️ 段二⑤ 補一句進 kanban 後留 AIR-26 事故〔69:notes⑤〕 | — | — | — |
| `feedback_skill-deletion-consumer-scan.md` | — | — | ❌ 段二⑥ 規範歸位後刪（與 zcode-skill-usage-audit 重複）〔69:notes⑥〕 | — | — | — |
| `project_zcode-skill-usage-audit-0909.md` | — | — | ✏️ 段二⑥ 併入事故證據〔69:notes⑥；實測條目在場〕 | — | — | — |
| `feedback_work-order-contract-point-to-source.md` | — | — | ✏️ 段二⑦ 合約句進 work-order.md 後留事故〔69:notes⑦〕 | — | — | — |
| `feedback_diagnose-installed-vs-source-first.md` | — | — | ✏️ 段二⑧ 規範進 debugging skill 後留事故〔69:notes⑧〕 | — | — | — |
| 池全量條目（C 段 full audit） | — | — | 🔍→✏️ 段二 C ai-rules 主體 162 條（desc 用語；實測目錄 177 檔含索引等非條目）＋mosaic 池全量——advisory→user 核可→修正〔69:desc；70:notes 段二 C；CONF:§三〕 | — | — | — |
| `MEMORY.md`（投影） | — | — | （間接：段二條目刪改後投影再生——卡面未逐字；投影機制衍生） | — | ✏️ 件一 S2 固定 pointer 一行（經 generate_index.py）〔63:notes S2〕 | — |
| 池級 gitignore | — | — | — | — | ✏️ 件一 S4（「池級 gitignore，provisional 不入歷史」——確切檔名卡面未逐字）〔63:notes 三拍板②〕 | — |
| draft-5 殼／draft-1/2（telemetry 源接線） | — | — | ❔ 段二「draft-1/2 併入本段」落點未指名〔70:notes 段二〕 | — | ❔ 件一「draft-5 殼同步清除」路徑未指名〔63:notes 併弧段〕 | — |
| T4-1 三 allow 訊號／AIDetector 豁免 | — | — | — | — | ❔ 件一 S3 豁免落點檔案未指名（daily-maintain 之外）〔63:notes S3；AC#1〕 | — |

### 1d. 跨 repo／外部路徑

| 對象 | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| `~/Github/mosaic_alpha/AGENTS.md` | ➕✏️ S3 觀察池路由段（依賴 AIR-54 移植後形態；AC#3）〔58:S3/AC#3；實測檔案在場〕 | — | — | — | — | — |
| `mosaic_alpha_offline_backtesting`／`mosaic_alpha_trading_lab`（AGENTS.md❔） | 🔍❔ S3「同型一併評估」——評估對象，改動面未定〔58:S3〕 | — | — | — | — | — |
| `~/Github/mosaic_alpha/deploy/scripts/run-backlog-cleanup.sh` | — | — | ✏️ 段一 F4 twin 同步（環境 loud-fail＋worktree 空檢兩段；或升級機制單一源）〔RPT:F4 :80；P4-2；實測在場〕 | — | — | — |
| mosaic 池條目（mosaic_alpha `.agents/memory/`） | — | — | 🔍→✏️ 段二 C 全量 audit（前置 AIR-54 S6——已由 mos-88 收斂，依賴解除）〔69:desc/notes〕 | — | — | — |
| `~/.codex/agents/*.toml`（ai-rules 二 toml） | ❌ S2 **已執行**（AC#2 [x]；tombstone `.agent-tmp/codex-agents-tombstone-0909/`）——剩餘工無觸及〔58:S2/AC#2〕 | — | — | — | — | — |
| `~/.codex/config.toml` | ✏️ S4 附帶**已完成**（09-09，backup config.toml.bak-advisor-0909）〔58:S4〕 | — | — | — | — | — |
| `~/Github/delegate-bridge/plugins/delegate/agents/delegate-rescue.md` | — | — | — | — | — | ✏️ S1 fail-loud＋deprecated 句→❌ S4 刪除〔68:desc S1/S4；實測檔案在場（卡面路徑「agents/delegate-rescue.md」＝plugin 根相對）〕 |
| `~/Github/delegate-bridge/plugins/delegate/commands/delegate.md` | — | — | — | — | — | ✏️ S2 :56 spawn subagent_type→caller 背景 Bash 直呼〔68:desc S2；實測 :56 逐字在場〕 |
| `~/Github/delegate-bridge/plugins/delegate/skills/delegate-runtime/` | — | — | — | — | — | ✏️ S3 改寫（agent 內部契約→caller 直呼契約）〔68:desc S3；實測目錄在場〕 |
| `~/Github/delegate-bridge/plugins/delegate/AGENTS.md` | — | — | — | — | — | ✏️ S4 :13〔68:desc S4；實測 :13 逐字在場〕 |
| `~/Github/delegate-bridge/AGENTS.md`（repo 根） | — | — | — | — | — | ✏️ S4 :70,:78〔68:desc S4；實測兩行逐字在場〕 |
| `~/Github/delegate-bridge/reference/AGENTS.md` | — | — | — | — | — | ✏️ S4 :25〔68:desc S4；實測 :25 逐字在場〕 |
| `~/Github/delegate-bridge/tests/s3s4.test.mjs` | — | — | — | — | — | ✏️ S4 :546,:601（S3 contract 釘住 agent 檔案）〔68:desc S4；實測檔案在場〕 |
| `~/Github/delegate-bridge/dist/`＋marketplace 版號 | — | — | — | — | — | ✏️❔ S5 重打包＋版號（確切檔名未指名）〔68:desc S5〕 |
| `~/Github/delegate-bridge/00-tasks/`（EP） | — | — | — | — | — | ➕ EP 建其處（AIR-47 跨 repo 卡慣例）〔68:desc 範圍段〕 |

## 2. 重疊清單（同一檔案被 ≥2 線觸及）

| # | 檔案 | 線×段 | 衝突性質 | 序列建議依據 |
|---|---|---|---|---|
| O1 | `skills/_common/work-order.md` | **L2 段三**（R6 :61＋注入塊）× **L3 段二⑦**（合約段一句）× **L4 段一＋段二**（授權失效條款×2 處） | **三線同檔修改**——最廣重疊；四處改動落不同段（:61 過時假議／合約段／範本條款），行級可能不撞但同檔併發＋語義同域（工單契約） | 無線間卡面協調；建議排 L4 段一→L3 段二→L2 段三 串行或同窗合併 |
| O2 | `skills/handoff/SKILL.md` | **L4 段一**（schema 欄序→單一源引用）× **L5 件二**（web 軌 web-brief 改寫）× L3 段一 S2（基準側🔍，P4-7 以其自述為準、本體未列修點） | **兩線實改＋一線參照**——L4 改 schema 欄序、L5 改 web 軌，同檔不同軌（本地軌 vs web 軌）；64:desc⑤「本地軌 schema 不動」與 L4 段一本地軌 schema 改引用**互為約束** | 兩卡互未提對方；AIR-64 僅聲明「兩檔自洽無 drift」內部驗收。建議 L5 件二在 L4 段一落地後接手，避免引用改寫與 web 改寫對撞 |
| O3 | `rules/context-management.md` | **L3 段一 S2**（:23 STATE 三方對齊）× **L4 段一**（「接手 quota 中斷先讀」清單→單一源引用） | **兩線同檔修改＋語義纏繞**——S2 修「誰寫 STATE」，L4 段一 at Phase 0 結算含 STATE.md 觀察；兩改動都在 session 接續語義域 | 無線間協調；建議 L4 段一先行（其恢復序列單一源正是 S2 對齊的上游語義），或同窗合併判讀 |
| O4 | `skills/model-routing/SKILL.md` | **L1 S1＋AC#4❔**（codex sweet spot＋決策記錄擇一）× **L4 段一**（「session 定向接續」節授權失效條款）× **L3 段二①📍**（pointer 源——本體改否未述） | 兩線確定改（不同節：codex row :45 vs :163 定向接續節）＋一線 pointer；行級不撞、同檔併發 | 無線間協調；弱衝突（不同節），串行即可 |
| O5 | `skills/review-engine/SKILL.md`＋`skills/judge-review/SKILL.md` | **L2 段二**（R1 語義化 gate 修改）× **L4 段二**（驗收③ 下游引用面 rg 掃描——🔍修改❔） | 修改×掃描：L2 改定義源後、L4 的「無 drift」驗收掃描時點決定結果有效性；若 L4 段二先掃、L2 後改，L4 驗收作廢 | 建議 L2 段二先於 L4 段二收斂（或 L4 驗收在 L2 後重跑） |
| O6 | `skills/implement/SKILL.md` | **L3 段一 S5**（:279 stale ref 一行清理）× **L4 段三**（斷點格式寫進階段文件——同檔段落級修改） | 兩線同檔：L3 刪 :279 stale 引用，L4 段三加斷點格式段；區位不同、L3 先清 L4 再加較乾淨 | 無線間協調；建議 L3 段一先行 |
| O7 | `MEMORY.md`／投影鏈（`generate_index.py`） | **L3 段二 B/C**（8 條目刪改→投影再生——卡面未逐字）× **L5 件一 S2**（render_b_form 改＋pointer 行） | 同產物檔＋同生成器：L5 改生成器、L3 改條目源——執行序決定 pointer 行與條目刪改是否一次投影收斂 | 63:notes 已有同類先例（與 AIR-54「同 skill 檔避免同檔併發」）；建議同窗合併或 L5 件一先行 |
| O8 | `skills/memory-audit/SKILL.md` | **L3 段二 A**（定義表兩處修補——確定）× **L1 AC#4❔**（決策記錄歸檔擇一候選）× **L5 件一❔**（優先序文字落點未指名） | 一線確定改＋兩線可能；兩個 ❔ 落點若都選此檔則三線同檔 | 58:AC#4、63:AC#1 均未指名——執行前先拍板落點即可消解 |

### 同線序列依賴（卡面明示）

- **L2**：段一（R2+R4）→段二（R1+R3）→段三（R6+R7）——卡面「三段連續做」〔67:notes〕
- **L3**：段一收斂後**無縫接段二**——卡面「兩段共用 kanban SKILL 等重疊面避免並行」〔70:notes〕；段一執行前逐條 rg 重驗（掃描時點 b75e8a7，AIR-52/AIR-66 已動部分檔案→washed-out 標記）〔70:desc ⚠️〕
- **L4**：段一（rehydration 單一源）→段二（雙 lens closure；AIR-61④「與恢復鏈治理卡③同步」）→段三（segment receipt；AIR-62 desc①「rehydration 單一源合併完成後才開工」——**段內硬前置**）〔60:notes；61:desc；62:desc①〕
- **L5**：件一×件二「檔案面不同可內部平行，一卡連續做收斂」〔63:notes〕；件一排序依賴「AIR-54 合併進 main 後自 main 開工（同 skill 檔避免同檔併發）」——卡面原文寫「開 air-57」（號碼與本卡 63 不一致，照錄）〔63:notes〕
- **L1**：S3 依賴 AIR-54 mosaic 移植先落地〔58:S3〕——AIR-69 notes 記載「S6 已由 mos-88 收斂」〔69:notes〕，依賴狀態以 AIR-54 卡現況為準（本軸未再核 AIR-54 卡）
- **L6**：S1（過渡防護）→S4（刪同一檔 delegate-rescue.md）——同線同檔先改後刪〔68:desc S1/S4〕

## 3. 無法從卡面判斷（unknown 彙總）

| 項 | 線 | 卡面缺口 |
|---|---|---|
| 恢復序列單一源落點檔案 | L4 段一 | 60:desc①「合併為一條…單一源」未指名新檔或併入現有三檔之一 |
| segment receipt 生成器＋測試落點 | L4 段三 | 62:desc②「機械生成（script）」未指名路徑 |
| followup-review skill「或 post-build 鏈對應段」二擇一 | L4 段二 | 61:desc驗收① 兩案並列未拍板 |
| L4 段二 review-engine/judge-review/post-build 僅驗收掃描、是否修改未述 | L4 段二 | 61:desc驗收③ |
| AC#4 決策記錄「卡或 model-routing/memory-audit 擇一」 | L1 | 58:AC#4 |
| S3 mosaic 兩 sibling repo「同型一併評估」改動面 | L1 | 58:S3 |
| R3 修改端檔案（機制＝EP 同層 references/research.md） | L2 段二 | 67:notes／AUDIT:R3 只述機制 |
| R6 capability-aware 注入塊落點（「工單/spawn prompt 注入塊」） | L2 段三 | 67:notes／AUDIT:R6 未指名檔案 |
| R7 spawn auth 失敗可見化的修改端檔案 | L2 段三 | 67:notes 未指名 |
| ⑥「edit-discipline」確切檔案 | L3 段二 | 69:notes⑥ 無路徑（repo 唯一同名＝rules/edit-discipline.md，推定待確認） |
| draft-1/2（telemetry 源接線）落點 | L3 段二 | 70:notes |
| 「canonical>pending 優先序有文字」落點 | L5 件一 | 63:AC#1 |
| T4-1 三 allow 訊號／AIDetector 豁免落點 | L5 件一 | 63:notes S3 |
| 池級 gitignore 確切檔名；觸發接線（夜波 refresh 段）落點 | L5 件一 | 63:notes 三拍板①② |
| S5 測試檔落點 | L5 件一 | 63:notes S5 |
| draft-5 殼路徑 | L5 件一 | 63:notes |
| bridge dist／marketplace 版號檔 | L6 S5 | 68:desc S5 |
| G11 Claude loader 是否消費 `paths:` | L3 段一 | RPT 報告明列 unverified——70:desc「G11 先查證」承接 |

## 4. 軸級結論

1. 六線檔案面已全數從卡面＋兩份報告萃取，逐格附出處；**memory 條目×8 全部實測在場**（`.agents/memory/`），bridge repo 六個卡面錨點（delegate-rescue.md／delegate.md:56／AGENTS.md:70,78／reference/AGENTS.md:25／tests/s3s4.test.mjs）全部實測逐字在場；`.code-reality.toml` 實測缺場（＝R4 新增）。
2. **真跨線檔案衝突（需排程協調）**：O1 `skills/_common/work-order.md`（三線）、O2 `skills/handoff/SKILL.md`（L4×L5 實改＋L3 參照）、O3 `rules/context-management.md`（L3×L4，語義纏繞最深）。
3. **弱衝突（不同節/修改×掃描）**：O4 model-routing SKILL、O5 review-engine＋judge-review、O6 implement、O7 MEMORY.md 投影鏈、O8 memory-audit SKILL（含兩個 ❔ 落點）。
4. skills／rules 同名分家注意：`rules/model-routing.md`（L3 段一 S1）與 `skills/model-routing/SKILL.md`（L1/L4/L3 段二）是**不同檔**；`rules/symbol-query-routing.md`（L3 低 G7）與 `skills/symbol-query-routing/SKILL.md`（L2 段一）同理——矩陣已分行，勿誤判重疊。
5. 段一執行前 washed-out 重驗（70:desc ⚠️）與 G11 先查證是 L3 段一的內建前置；本矩陣路徑以報告掃描時點 b75e8a7 記載為準，執行時以當時 rg 為準。
