# Blueprint B 軸——工作項→實際目標檔反推矩陣

問題｜ai-rules 六條執行線的檔案觸及面（逐工作項反推，供與 A 軸交叉驗證）
軸｜工作樹檔案存在性＋內容錨點（git 工作樹＋跨 repo 工作樹；read-only，唯一寫入＝本檔）
方法｜九張卡（tasks/air-{58,60,63,67,70,68}＋completed/air-{61,62,64,69}，後四者經 triage 併弧為前三線的段二/段三）逐工作項推目標檔，fd/ls 驗存在、rg/sed 驗內容錨點；範圍源報告（consistency-scan／cr-role-audit）作 finding→檔案映射依據
日期｜2026-09-10　基線｜工作樹現況（HEAD 未逐 commit 錨定，行號為掃描當下值）

## 六線組成（併弧結構，自卡面 Final Summary/Notes 機械讀出）

| 線 | 組成 | 併弧證據 |
|---|---|---|
| AIR-58 | 本卡 S1-S4 | — |
| AIR-60 | 本卡段一＋AIR-61 段二＋AIR-62 段三 | air-60 notes「triage 併弧 09-10」；61/62 Final Summary「併入 AIR-60」 |
| AIR-63 | 本卡段一＋AIR-64 段二 | air-63 notes「升級為視圖雙件弧」；64 Final Summary「併入 AIR-63」 |
| AIR-67 | 本卡段一（R2+R4）＋段二（R1+R3）＋段三（R6+R7） | air-67 notes |
| AIR-70 | 本卡段一（13 中級＋低級）＋AIR-69 段二 | air-70 notes；69 Final Summary「併入 AIR-70」 |
| AIR-68 | 本卡（delegate-bridge repo，全範圍 S1-S5） | — |

---

## AIR-58 codex顧問化治理

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| S1 codex 角色升級（sweet spot 備註擴） | `skills/model-routing/SKILL.md` | rg『sweet spot』→ :45「codex（OpenAI）→ 預設不派…定性甜蜜點實證…state-review 的候選家族之一」；family 表 :119 codex 行 | verified |
| S1 rules 面零觸及（單一源不 materialize） | （rules/model-routing.md 不改） | rules/model-routing.md:30「現值見 model-routing skill 解析表（單一源，不在此 materialize）」 | verified |
| S2 ~/.codex/agents toml 刪除（已完成） | machine-local `~/.codex/agents/`（現空）＋tombstone `.agent-tmp/codex-agents-tombstone-0909/`（5 toml 在場） | ls 兩處實測；AC#2 已勾 | verified（repo 零檔案） |
| S3 mosaic 記憶路由段落地 | `/Users/ctai/Github/mosaic_alpha/AGENTS.md`＋同型評估 `mosaic_alpha_offline_backtesting/AGENTS.md`、`mosaic_alpha_trading_lab/AGENTS.md`（跨 repo） | 三檔 ls 全在場；參照源＝ai-rules `AGENTS.md:110`「觀察池路由」段（rg 錨點） | verified（檔案存在；卡稱 mosaic 側無 codex 路由段屬卡面宣稱，本軸未逐一 rg mosaic 檔內容） |
| S4 決策記錄歸檔（擇一） | `skills/model-routing/SKILL.md` 或 `skills/memory-audit/SKILL.md` | 兩檔 ls 在場；最終擇一未定 | verified（檔案）＋unknown（落點） |

## AIR-60 session 接續恢復鏈（＋61 段二＋62 段三）

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| rehydration 三份局部版（合併觸及面） | ①`skills/at/SKILL.md` ②`rules/context-management.md` ③`skills/handoff/SKILL.md`＋`skills/self-contained-prompt/SKILL.md` | ①:116「## Resume 後的行為」②:18「接手 quota 中斷先讀」③handoff:53-55 自稱薄 adapter、schema 十欄實際定義在 self-contained-prompt——第三份局部版實體在 self-contained-prompt | verified |
| rehydration 單一源落點 | 未指定（新寫法住哪檔卡面未定） | 卡文僅「合併為一條…三處改引用」 | unknown |
| at Phase 0 結算改序 | `skills/at/SKILL.md` | 檔在場（:116 錨點同上） | verified |
| 授權失效條款三處 | `skills/at/SKILL.md`＋`skills/_common/work-order.md`＋`skills/model-routing/SKILL.md`「session 定向接續」節 | model-routing:163 節標題 rg 錨點；work-order.md rg『授權\|PENDING』零命中＝條款現況未落地（符合 To Do） | verified |
| 段二 雙 lens 分工載明 | `skills/followup-review/SKILL.md`（或 `skills/post-build/SKILL.md` 對應段） | 兩檔 ls 在場 | verified |
| 段二 codex followup 接線現況翻轉 | `skills/state-review/SKILL.md` | :21「**派發形態現況**…codex 腿本弧為 user-relay…first-real-usage-pending」 | verified |
| 段二 下游引用面防 drift（rg 掃） | `skills/review-engine/SKILL.md`＋`skills/judge-review/SKILL.md`＋`skills/post-build/SKILL.md` | 三檔 ls 在場（可能零改動） | verified |
| 段三 receipt 生成器＋測試 | 新檔，位置未指定 | 卡面無路徑 | unknown |
| 段三 resume 讀 receipt | 段一單一源檔（隨 unknown 落點） | 同上 | unknown |
| 段三 implement 斷點格式同步 | `skills/implement/SKILL.md` | 檔在場（:279 錨點） | verified |

## AIR-63 pending 讀取覆層（＋64 段二）

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| S1 _pending.md 生成器 | `skills/memory-audit/scripts/generate_pending.py`（**新檔**） | 父目錄 ls 在場（現含 generate_index.py＋memory_telemetry.py）；generate_pending.py 不存在 | verified（目標面確立） |
| S2 MEMORY.md 固定 pointer | `skills/memory-audit/scripts/generate_index.py`（:185 `render_b_form`）→ 產物 `.agents/memory/MEMORY.md` | rg render_b_form :185,:335 verified；MEMORY.md 在場（投影禁手寫） | verified |
| S3 豁免（夜波異常篩＋daily-maintain） | `skills/memory-audit/SKILL.md`（T4-1 三 allow 訊號＝:72）＋`skills/daily-maintain/SKILL.md` Phase 0（:45） | 兩錨點 rg verified | verified |
| S3 AIDetector 豁免 | AIDetector 本體位置不明 | rg 全 repo 僅 air-63 卡文命中；hooks/muse_memory_inbox.sh、.muse/hooks.json 無 aidetector 字樣——推測 machine-local muse 端，本軸無法驗 | unknown |
| S4 pool gitignore＋觸發接線 | `.agents/memory/` 池級 gitignore（machine-local pool git）＋接線點 | 池目錄在場（8 條目＋投影驗證見 AIR-70 段二） | verified（池）＋unknown（接線點：卡載「SessionStart 接線另議」） |
| S5 測試 | 新檔，位置未指定 | 卡面無路徑 | unknown |
| draft-5 殼清除 | 找不到 draft-5 檔 | fd ai-analysis＋.agent-tmp 零命中（7d 清理已過期或他處） | unknown（washed-out 候選） |
| 段二 web-brief 雙軌（卡明示只改兩檔） | `skills/self-contained-prompt/SKILL.md`＋`skills/handoff/SKILL.md` | 兩檔 ls 在場；rg『web-ask\|web-tell』零命中＝未實作（符合 To Do）；負面範圍：agent-review-cycle 不動 | verified |

## AIR-67 CR quick-wins（三段）

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| R2 角色定義修正 | `agents/roles/cr-research.md`（:23「查詢形態」bullet＝教錯點） | sed :20-26 實讀，:23「symbol 用 module path（pkg.mod.Symbol）」原文在場 | verified |
| R2 三檔同步 | ＋`skills/cr-query/SKILL.md`＋`skills/symbol-query-routing/SKILL.md` | 兩檔在場 | verified |
| R2 registry 生成物連動 | `agents/zcode/cr-research.md`＋`agents/claude/cr-research.md`（sync_agents.py 重跑同步） | fd 兩生成物在場；roles/ 改必須重跑 `scripts/sync_agents.py` | **verified（連動面，見下特別標註）** |
| R4 `.code-reality.toml` | repo root `.code-reality.toml`（**新檔**） | ls 確認現不存在 | verified（目標面確立） |
| R1 negative-claim gate | `skills/review-engine/SKILL.md`（claim 條文 :59-61、:169 negative verdict 條款部分已在）＋`skills/execution-plan/SKILL.md`＋`skills/judge-review/SKILL.md` | 三檔在場；review-engine:169 已有「negative verdict 永遠不可用 rg」句（R1 是擴 claim 四欄 gate） | verified |
| R3 research.md 載體 | `skills/execution-plan/SKILL.md`（段落 0 條文；per-EP 產物 `references/research.md`） | rg『research.md』於 execution-plan 零命中＝未落地 | verified |
| R6 capability-aware 注入 | `skills/_common/work-order.md`（:61 過時假議原文在場） | sed :58-64，「external runtime 接線（foreign runtime 無 LSP／MCP 面）…CLI 缺場＝rg degraded」＝待修 provider hardcode | verified |
| R7 spawn auth 失敗回報 | `agents/roles/cr-research.md`（→ registry 連動同 R2） | roles 檔在場 | verified＋連動 |
| 範圍源（read-only） | `ai-analysis/reports/2026-09-09-cr-role-audit.md`（R 行表 :189-196） | 實讀 verified | verified |

## AIR-70 一致性掃描修復（段一）——13 中級逐條

| finding | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| G1 家族清單三版本 | `AGENTS.md`:3＋`rules/AGENTS.md`:10,40＋`ai-development-guide.md`:3＋`skills/instruction-writing/SKILL.md`:22,24,33＋`scripts/deploy_agents.py`（targets :105-112 僅 zcode/codex/muse） | 五檔逐一 rg/sed：四家 vs 三端 vs 四家含 OpenCode 無 Muse——三版本字樣全數在場 | verified |
| G2 claude-specific boilerplate | `rules/bash-hard-rules.md`:7＋`rules/code-edit-constraints.md`:7 | 兩檔 :7「各家 harness 經全域 guide 部署載入」原文在場 | verified |
| G4 bundle-skip 未記載 | `rules/AGENTS.md` 部署紀律段（:46,:52） | 檔在場（錨點沿掃描報告） | verified |
| S1 impl/test-gen role 幽靈 | `rules/model-routing.md`:16 | :16「\| impl / test-gen \| full 基準…」原文在場；`agents/roles/` ls 10 檔——無 impl.md/test-gen.md（僅 impl-lite.md），幽靈屬實 | verified |
| S2 STATE.md 三方 | `skills/_common/state-md-write.md`:3,:34＋`rules/context-management.md`:23＋`skills/handoff/SKILL.md`:31 | 三錨點 sed 實讀全在場（handoff:31「STATE.md 非交接選項…非 /at//handoff 替代」） | verified |
| S3 commit flow 重畫 | `skills/commit/SKILL.md`:203（改引用 code-review:223 canonical） | :203 flow 原文在場 | verified |
| S4 usage-ping 語音殘留 | `skills/usage-ping/SKILL.md`:30,118 | rg『語音』：:20 定案句、:30 表欄「無 UI 邊界時的保底 / 語音後接力」、:118「聽到語音後再跑一次」——殘留現況仍在（未被 AIR-66 洗掉） | verified |
| S5 implement stale ref | `skills/implement/SKILL.md`:279 | :279「（原 commit 階段 3 的 consistency 職責併入此）」原文在場（行號與報告一致） | verified |
| S6 斷連結 | `skills/instruction-writing/SKILL.md`:151 | :151 `[lessons_learnt.md](lessons_learnt.md)`；fd lessons_learnt 全 repo 0 hits | verified |
| F1 cleanup plist 無版控副本 | `deploy/launchd/com.ai-rules.backlog-cleanup.plist`（**新檔**；源 `~/Library/LaunchAgents/com.ai-rules.backlog-cleanup.plist`） | ls：deploy/launchd/ 僅 browser.plist；LaunchAgents 源在場 | verified（目標面確立） |
| F4 mosaic twin 缺 loud-fail | `/Users/ctai/Github/mosaic_alpha/deploy/scripts/run-backlog-cleanup.sh`（跨 repo）＋ai-rules 側 `deploy/scripts/run-backlog-cleanup.sh`:7,18-19（twin 條款＋loud-fail 段） | twin 檔在場（**注意：路徑是 mosaic_alpha 下底線**）；ai-rules 側 :7 twin 條款、:18-19 環境預檢原文在場 | verified |
| F3 README 必查路徑撲空 | `ai-analysis/README.md`:21,27,28 | 檔在場（錨點沿掃描報告；_inbox/_projects 缺場屬報告已驗事實，本軸未重驗目錄） | verified |
| 低級 G10 | `CLAUDE.md`:15-26 | 檔在場 | verified |
| 低級 S7 | `skills/commit/SKILL.md`:38 | rg『ruff verify』:38 原文在場 | verified |
| 低級 S9 | `skills/scan-project/SKILL.md`:57（對照 standup:26-27 有 ZCode fallback） | 兩錨點 rg verified | verified |
| 低級 F2 | `hooks/zcode-registration.json`:78 | :78 delegate/**1.0.0** 殘留 rg verified | verified |
| 低級 F5 | `ai-analysis/schedule-registry.md`:25＋`deploy/scripts/run-backlog-browser.sh`:3,6 | :6 `--port 6422` verified（registry :25 6421 錯置沿報告） | verified |
| 低級 G7 | `ai-development-guide.md`:13 vs `rules/symbol-query-routing.md`:30 | 兩檔在場 | verified |
| 歧異帶（併入判讀，可修可不修） | G5→`rules/AGENTS.md`:94＋`rules/modern-cli-preference.md`:7＋`rules/_ai-behavior-constraints.md`:7；G8→`rules/tool-discipline.md`:19＋`rules/bash-hard-rules.md`:15,23；G9→`ai-development-guide.md`:58；S8→`skills/doc-health/SKILL.md`:36＋`skills/metadata-sync/SKILL.md`:3；S10→`skills/rules-reminder/SKILL.md`:3 | S10 description :3「most frequently violated **Claude Code** rules」rg verified；其餘檔在場、錨點沿報告 | verified（檔案）／修否未定 |
| G6 不修（負面範圍） | （`rules/context-management.md`:9 vs `rules/code-edit-constraints.md`:63） | — | verified（不觸及） |
| G11 先查證 | `rules/instruction-writing.md`:3-4（`paths:` 欄）；修否依 Claude loader probe | sed :1-5 paths: 欄在場 | verified |

## AIR-70 段二（AIR-69 內容：定義表 v2＋先鋒 8 條＋全量 audit）

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| 統一定義表 v2 兩處修補 | `skills/memory-audit/SKILL.md`（誤置表 :157-159；層級閘首句） | rg『誤置』:157,159 verified | verified |
| ① bridge-job-completion-no-push | 池條目 `feedback_bridge-job-completion-no-push.md`（正文刪）＋規範源 `skills/model-routing/SKILL.md`:187「### 完成回報收法」 | fd 條目在場；收法節 :187 rg verified | verified |
| ② backlog-cli-entry | `reference_backlog-cli-entry.md`（整條刪） | fd 在場 | verified |
| ③ global-vs-project-permissions | `global-vs-project-permissions.md`（池內重寫） | fd 在場（無 prefix 裸名） | verified |
| ④ cross-session-commit-on-active-branch | `feedback_cross-session-commit-on-active-branch.md`＋規範搬 `skills/kanban-board/SKILL.md` 建卡段 | fd 條目在場；skill 在場 | verified |
| ⑤ backlog-card-edit-precheck | `feedback_backlog-card-edit-precheck.md`＋`skills/kanban-board/SKILL.md` 卡操作段 | fd＋ls verified | verified |
| ⑥ skill-deletion-consumer-scan | `feedback_skill-deletion-consumer-scan.md`＋`skills/instruction-clean/SKILL.md`＋`rules/edit-discipline.md`；事故併 `project_zcode-skill-usage-audit-0909.md` 後刪 | 四檔 fd 全在場 | verified |
| ⑦ work-order-contract-point-to-source | `feedback_work-order-contract-point-to-source.md`＋`skills/_common/work-order.md` | fd＋ls verified | verified |
| ⑧ diagnose-installed-vs-source-first | `feedback_diagnose-installed-vs-source-first.md`＋`skills/debugging-and-error-recovery/SKILL.md` | fd＋ls verified | verified |
| 投影 regen | `.agents/memory/_inventory.md`＋`MEMORY.md`（generate_index.py） | 兩投影檔 ls 在場 | verified |
| C 全量 audit（雙池） | ai-rules `.agents/memory/` 全量＋mosaic 池 `/Users/ctai/Github/mosaic_alpha/.agents/memory/`（含 `_inventory.md`） | 兩池目錄 ls 在場 | verified |
| 歸因投影 | `skills/memory-audit/scripts/memory_telemetry.py` | ls 在場 | verified |
| 裁決書源（read-only） | `ai-analysis/reports/2026-09-10-carrier-placement-v2-conference.md` | 在場 | verified |

## AIR-68 delegate-rescue 退役（跨 repo：delegate-bridge）

| 工作項 | 目標檔 | 證據＋錨點 | 判定 |
|---|---|---|---|
| S1 過渡防護 | `/Users/ctai/Github/delegate-bridge/plugins/delegate/agents/delegate-rescue.md` | ls 在場 | verified |
| S2 /delegate 命令重寫 | `plugins/delegate/commands/delegate.md`:56 | :56「Invoke the `delegate-rescue` agent via the `Agent` tool (`subagent_type: "delegate-rescue…`」原文在場 | verified |
| S3 delegate-runtime skill 改寫 | `plugins/delegate/skills/delegate-runtime/SKILL.md` | ls 在場 | verified |
| S4 agent 刪除＋文檔同步 | 上agent檔（刪）＋`plugins/delegate/AGENTS.md`:13＋`AGENTS.md`:70,78＋`reference/AGENTS.md`:25 | 四錨點 sed/rg 實讀：:13 thin forwarder 句、:70,78 delegate-rescue 字樣、:25 codex-rescue S3 contract 行——全在場 | verified |
| S4 測試同步 | `tests/s3s4.test.mjs`:546,601 | rg delegate-rescue 兩行 verified（:546 agent 檔路徑釘住、:601 dist 內容表） | verified |
| S5 dist 重打包＋版號 | `dist/`（重打包；`scripts/package-marketplace.mjs`）＋`package.json` | 三者 ls 在場 | verified |
| EP 家 | `00-tasks/` | ls 在場 | verified |
| **跨 repo 零重疊驗證** | ai-rules 側 rg『delegate-rescue』（排除 .agent-tmp/ai-analysis/backlog）→ **僅 `AGENTS.md`:107 一處**（「delegate-rescue` 委派」消費形態描述） | rg 實跑 | verified——正式範圍（bridge repo）與 ai-rules 零重疊；但 AGENTS.md:107 是「rg 零殘留」驗收若全域跑時的命中點（卡明示 ai-rules 側不併弧、rule promotion 掛 AIR-66） |

---

## 重疊清單（多線共同觸及檔）

| 檔 | 觸及線 |
|---|---|
| `skills/_common/work-order.md` | AIR-60（授權失效條款）＋AIR-67 R6（capability-aware 注入）＋AIR-70 段二⑦（work-order-contract 搬入）——**三線同檔，併弧/排序需協調** |
| `skills/model-routing/SKILL.md` | AIR-58 S1/S4＋AIR-60（定向接續節授權條款）＋AIR-61（下游引用面 rg）＋AIR-70 段二①（收法段為規範源） |
| `skills/at/SKILL.md` | AIR-60 段一（rehydration＋Phase 0＋resume prompt）——單線多工作項 |
| `skills/execution-plan/SKILL.md` | AIR-67 R1＋R3 |
| `skills/review-engine/SKILL.md`＋`skills/judge-review/SKILL.md`＋`skills/post-build/SKILL.md` | AIR-61 下游引用面（可能零改動） |
| `skills/handoff/SKILL.md` | AIR-60（rehydration 第三局部版/schema）＋AIR-64 段二（web-brief） |
| `skills/self-contained-prompt/SKILL.md` | AIR-60（schema 十欄實體）＋AIR-64 段二 |
| `skills/kanban-board/SKILL.md` | AIR-70 段二④⑤（兩條搬入） |
| `agents/roles/cr-research.md` | AIR-67 R2＋R7（同檔兩工作項） |
| `skills/commit/SKILL.md` | AIR-70 S3＋S7（同檔兩 finding） |
| `skills/memory-audit/SKILL.md` | AIR-58 S4（候選落點）＋AIR-63 S3（T4-1 豁免）＋AIR-70 段二（定義表 v2） |
| `AGENTS.md`（根） | AIR-70 G1＋（AIR-68 驗收殘留命中點 :107，非改動範圍） |
| 跨 repo：`mosaic_alpha` | AIR-58 S3（AGENTS.md）＋AIR-70 F4（cleanup twin）＋AIR-70 段二 C（memory 池 audit） |

## registry 生成物連動面（特別標註）

- **`agents/roles/*` 是 authoring 單一源；`agents/zcode/`、`agents/claude/` 是 `scripts/sync_agents.py` 生成物**。AIR-67 對 `agents/roles/cr-research.md` 的 R2＋R7 改動，必須重跑 sync_agents.py，否則 `agents/zcode/cr-research.md`＋`agents/claude/cr-research.md` 兩生成物 drift（fd 驗：兩生成物現與 roles 同步在場）。
- AIR-68 刪 `delegate-bridge/plugins/delegate/agents/delegate-rescue.md` 屬 bridge repo 自身 registry，**不经 ai-rules sync_agents**（跨 repo 零連動——ai-rules agents/roles 無 delegate-rescue.md，ls 驗）。
- rules/ 面改動（AIR-60 context-management、AIR-70 G1/G2/G4/S1/S2）觸發 `deploy_agents.py` bundle 重建（machine-local ~/.zcode、~/.codex、~/.config/muse AGENTS.md）——AIR-60 驗收④明列此同步。

## unknown 清單

1. AIR-60 rehydration 單一源落點檔（卡未指定；三處引用改寫的錨點檔隨之未定）
2. AIR-62 segment receipt 生成器＋測試的新檔路徑
3. AIR-63 AIDetector 本體位置（rg 全 repo 僅卡文命中；推測 machine-local muse 端，無法驗）
4. AIR-63 S4 觸發接線點（卡載「SessionStart 接線另議」）＋S5 測試路徑
5. AIR-63 draft-5 殼位置（fd 零命中——已過期清理或他處；washed-out 候選）
6. AIR-58 S4 決策記錄歸檔最終擇一（model-routing vs memory-audit）
7. AIR-70 段一 washed-out 風險面：卡自載「AIR-52＋AIR-66 已動 usage-ping/rules 面，執行前逐條 rg 重驗」——本軸重驗 S4/S5 殘留仍在場，其餘 finding 未逐條重驗 washed-out（沿掃描報告時點 b75e8a7）
8. AIR-67 R4 smoke 產物、AIR-70 G11 Claude loader probe 結果——依賴未來執行，非本軸可驗

## 軸級結論

- 六線的 repo 內觸及面共約 **40 個現存檔＋5 個確立的新檔**（generate_pending.py、.code-reality.toml、cleanup plist 版控副本、receipt 生成器＋測試〔路徑未定〕）；跨 repo 面＝delegate-bridge（AIR-68 九處）＋mosaic_alpha 三 repo（AIR-58 S3＋AIR-70 F4＋段二池 audit）。
- 全部逐項宣稱均附 fd/ls/rg/sed 機械證據；「未實作」項以目標錨點缺場反向確立（web-ask 零命中、research.md 零命中、work-order 授權條款零命中、.code-reality.toml 不存在）。
- 最大協調風險點＝`skills/_common/work-order.md` 三線同檔＋`skills/model-routing/SKILL.md` 四線觸及；registry 連動（roles→zcode/claude）僅 AIR-67 一線觸發。
- 與 spawn 範例的差異修正：AIR-70 段二「六個規範目標檔」實數＝6 檔成立（model-routing、kanban-board、instruction-clean＋edit-discipline〔⑥雙檔〕、work-order、debugging-and-error-recovery——嚴格數 6 個檔案路徑、7 個規範落點因⑥雙檔）；AIR-70 F4 mosaic twin 路徑是 `mosaic_alpha`（下底線）非 `mosaic-alpha`。
