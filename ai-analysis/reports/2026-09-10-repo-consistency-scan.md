# 2026-09-10 全 repo 一致性掃描報告（三軸 flash agents＋muse/codex 顧問）

> 排程弧：`/at 02:00`（2026-09-09 21:45 排程，02:00 觸發自主執行）。掃描時點 HEAD=`b75e8a7`。本報告為分析產出（禁 commit 紅線），修復提案採不採由 user 裁決。完整 journals：`.agent-tmp/consistency-{gov,skills,ops}-journal.md`。

## ① 掃描範圍與方法

- **任務**：掃整個 repo 所有目錄（含 md），找互相矛盾、衝突、怪異之處。
- **三軸切分**（三個 registry lite agents，`glm-5.3-flash` pin，唯讀，平行背景）：
  - **A 治理軸**：`ai-development-guide.md`＋根 `AGENTS.md`/`CLAUDE.md`＋`rules/` 全部 19 檔（guide↔rule、rule↔rule 矛盾）
  - **B skills 軸**：`skills/` 62 skill 精讀＋橫向 rg 掃描（skill↔skill、skill↔rule、失效連結）
  - **C 營運軸**：`scripts/`、`agents/`、`hooks/`、`deploy/`、`tests/`、`ref-docs/harness` manifest、`backlog/`＋`ai-analysis/` 治理宣稱面（code 行為 vs 檔案宣稱、版控源完整性）
- **證據要求**：每條 finding 附矛盾雙側 path:line＋逐字節錄；查證不了標 unverified。
- **機械驗證**（營運軸實跑）：`sync_agents.py --check` exit 0、`check_report_shells.py` exit 0、LaunchAgents vs repo plist diff IDENTICAL、manifest 1072 頁存在性全掃＋sha256 抽查 23 檔、live `~/.zcode/cli/config.json` hooks 子樹逐條比對。
- **統計**：高 0｜中 13｜低 13（A：中4低7；B：中6低4；C：中3低2）。三軸間無重複 findings、無互相矛盾結論。

## ② Findings

### 中級（13 條，五群）

#### 群一：部署/載入記載 drift（治理層對「誰載入什麼」說法不一）

**G1｜非 Claude harness 家族清單三種版本**
- A 側：根 `AGENTS.md:3`「非 Claude 端：`~/.zcode/AGENTS.md` 等**四家** → guide bundle」
- B 側：`rules/AGENTS.md:10,40`「非 Claude 端（**ZCode/Codex/Muse**）」「三端」；`ai-development-guide.md:3` 同；`scripts/deploy_agents.py` targets 僅 zcode/codex/muse；且單一源 `skills/instruction-writing/SKILL.md` 又是另一套「四家 harness（Claude/ZCode/**OpenCode**/Codex）」含 `~/.config/opencode/AGENTS.md`、無 Muse
- 衝突點：「四家」無第四端部署證據；instruction-writing 的清單與部署腳本實況又不同——家族清單 drift 會誤導部署驗證範圍判斷

**G2｜claude-specific rule 帶錯置的「部署載入」boilerplate**
- A 側：`rules/bash-hard-rules.md:7`、`rules/code-edit-constraints.md:7`「各家 harness 經全域 guide 部署載入」
- B 側：`rules/AGENTS.md:69` 明列這兩檔是 claude-specific、被排除於 bundle；`deploy_agents.py:20-22` default bundle 僅 neutral
- 衝突點：兩檔宣稱的載入路徑對它們不存在（實際只經 Claude symlink auto-load）——從 neutral 檔複製的殘留

**G4｜`bundle: skip` 機制未記載＋scope 表摘要漂移**
- A 側：`rules/acceptance-evidence.md:15-21,49-51` 五條 claim 校驗規則（數字 claim／刪除死碼／silent-failure／Review 雙向／自報元資料）被 `<!-- bundle: skip -->` 剝除（`deploy_agents.py:146-149` 處理）
- B 側：`rules/AGENTS.md` 部署紀律段（:46）僅記 `harness-scope` 單一真相源，未記 skip 語法；:52 摘要未反映 skip 面
- 衝突點：機制存在但治理文檔漏記；非 Claude 端拿到的 acceptance-evidence 缺一整塊可操作規則且 scope 表無揭露

#### 群二：文件引用已改組的實體（章節/角色遷移後引用沒清）

**S1｜rules 引用的 `impl`/`test-gen` role 在 registry 已不存在**
- A 側：`rules/model-routing.md:16` role 表「impl / test-gen｜full 基準，機械段依同條件降 lite…」
- B 側：`skills/model-routing/SKILL.md:64` full 角色表為空（judge/EP 規劃是主 session 職責非 role）；`agents/roles/` 僅 `impl-lite.md`；`sync_agents.py` pins 亦無 impl/test-gen
- 衝突點：always-on rule 的 role 表指向已不存在的 role（impl-lite lite 化重組未回同步）——session 依 rule 嘗試 spawn `impl` 會落空。**（評註：分級最接近「高」的邊界案例）**

**S2｜STATE.md 寫入端三方不一致**
- A 側：`skills/_common/state-md-write.md:3`「`/at`、`/handoff`、`/deep-work` 在 session 結束寫 STATE.md 時引用此處」
- B 側：`rules/context-management.md:23`「由 at/deep-work 觸發」（無 handoff）；`skills/handoff/SKILL.md:31`「STATE.md…非 `/at`/`/handoff` 替代」且全檔無 STATE 寫入步驟
- 衝突點：範本宣稱 handoff 是寫入消費端，handoff 自身否認、rule 也只列兩家——三處對「誰寫 STATE」說法分歧

**S3｜commit 流程圖違反自家 canonical flow 單一源宣告**
- A 側：`skills/code-review/SKILL.md:223`「canonical review flow（詳細）以本檔為單一源——其他命令畫 flow 須引用此處、不重畫」
- B 側：`skills/commit/SKILL.md:203` 自畫 flow「`/implement（含 Agent Review）→ [/code-review（含 commit message）] → /commit`」（漏 `/execution-plan`、`/post-build`，code-review 未置於 post-build 內）
- 衝突點：commit 重畫了 flow 且與 canonical（code-review:234）不一致——正是宣告要防的 flow drift

**S5｜implement 引用已刪的 commit 階段 3**
- A 側：`skills/implement/SKILL.md:279`「（原 commit 階段 3 的 consistency 職責併入此）」
- B 側：`skills/commit/SKILL.md` 階段編號實測＝1, 2, 2.5–2.8, 4, 5, 6, 7（無階段 3）
- 衝突點：stale cross-ref 成對（職責已遷移至 commit:190 與 implement 5d，引用文字沒清）

#### 群三：退役殘留（功能/檔案已退役，死引用沒清）

**S4｜usage-ping 內部殘留已退役語音指令**
- A 側：`skills/usage-ping/SKILL.md:20`「**無語音**（user 09-09 定案…）：無排程確認 say、無 sentinel 召回」
- B 側：同檔 :30 表格欄「無 UI 邊界時的保底 / 語音後接力」＋:118「聽到語音後再跑一次＝手動接力下一輪」
- 衝突點：語音已全面退役，「聽到語音後再跑」是永不觸發的死指令，與同檔 09-09 定案矛盾（註：ebf269e 去語音 commit 殘留）

**S6｜instruction-writing 斷連結**
- A 側：`skills/instruction-writing/SKILL.md:151`「詳細 benchmark 數據和架構探索教訓見 [lessons_learnt.md](lessons_learnt.md)」
- B 側：`fd lessons_learnt` 全 repo 0 hits——檔案不存在
- 衝突點：相對路徑（基底 skills/instruction-writing/）無解析目標

#### 群四：版控源/同步完整性破口

**F1｜deploy/launchd/ 版控源不完整——cleanup plist 無 repo 副本**
- A 側：`skills/acceptance-evidence/SKILL.md:20`「launchd plist（現值＝`~/Library/LaunchAgents/`，repo 內 `deploy/launchd/` 只是源）」
- B 側：`deploy/launchd/` 僅 `com.ai-rules.backlog-browser.plist`；`com.ai-rules.backlog-cleanup`（LaunchAgents 已驗在場、23:50、腳本路徑正確）repo 內無版控副本
- 衝突點：「deploy/launchd/ 只是源」對 cleanup 不成立——LaunchAgents 端遺失/換機時無法從 repo 重建

**F4｜twin cleanup 腳本同步條款已破（mosaic 側缺 loud-fail 預檢）**
- A 側：`deploy/scripts/run-backlog-cleanup.sh:7`「twin: mosaic_alpha/deploy/scripts/run-backlog-cleanup.sh 同邏輯副本——修改須同步」＋:18-19 環境預檢 loud-fail exit 1＋:27 worktree 空列舉檢查
- B 側：diff mosaic twin——環境預檢與 worktree 空檢兩段不存在；precheck 缺場時進迴圈逐卡記 `[不可清-跳過]`
- 衝突點：ai-rules 側新增的 loud-fail 保護未同步到 twin——mosaic 端退化成 ai-rules 註解明言要避免的「靜默 no-op 與誤計 skip」形態。**（評註：分級最接近「高」的邊界案例——mosaic 端清板保護實際弱化）**

#### 群五：治理條款指向缺場/錯置

**F3｜README「必查」去重條款指向缺場檔案**
- A 側：`ai-analysis/README.md:28`「`backlog task create` 前必 `backlog search`＋查 `ai-analysis/_inbox/pending-decisions.md`（與同域 `open-items.md`）」；:21/:27 提 `ai-analysis/_projects/<線>/tasks/…`
- B 側：`ls` 實測 `_inbox` 與 `_projects` 均不存在
- 衝突點：「必查」條款指名的路徑撲空——若屬 lazy-create 慣例應註記，否則每次去重前置必 miss

### 低級（13 條）

**G5｜載入機制註記重複**：`rules/AGENTS.md:94`「neutral rule 不需每檔重複」vs `rules/modern-cli-preference.md:7`、`rules/_ai-behavior-constraints.md:7` 仍帶完整註記——規範與自身實踐不一致。

**G6｜連續失敗閾值不一**：`rules/context-management.md:9`「連續糾正**兩次**仍失敗就換 prompt」vs `rules/code-edit-constraints.md:63`「連續 **3 次**同類錯誤 → 停下」（情境不同，術語噪音級）。

**G7｜驗證順序字面相反**：`ai-development-guide.md:13`「必須實際執行，**再**檢查語法/import」vs `rules/symbol-query-routing.md:30`「Edit→ruff→check_file→mypy→pytest」。

**G8｜`python -c` 同行 `#` 可否**：`rules/tool-discipline.md:19`「不寫**換行後** # 註解」vs `rules/bash-hard-rules.md:15,23`「禁止寫註解」含單行（pointer 已部分緩解）。

**G9｜backlog_precheck.sh 路徑寫法歧義**：`ai-development-guide.md:58`「kanban-board 的 `scripts/backlog_precheck.sh`」——實際在 `skills/kanban-board/scripts/`，與 guide 自己 `scripts/`（repo 根）語義易混。

**G10｜CLAUDE.md 載體表自立一套判準**：`CLAUDE.md:15-26` 自帶需求→載體表＋「忘了執行會造成損害 → Hook」啟發式，無指向單一源（instruction-writing「載體選擇」＋memory-audit 統一定義表）宣告。

**G11｜rules frontmatter `paths:` 欄位消費端未記載**：`rules/instruction-writing.md:3-4` 等三檔帶 `paths:`，`deploy_agents.py` 不消費（rg 0 命中），治理文檔未記載其消費端。

**S7｜commit 內「ruff verify」非存在子命令**：`skills/commit/SKILL.md:38`「ruff format 後同時跑 ruff verify 和 mypy」——Step 3 實為 `ruff check .`，疑 typo。

**S8｜SYSTEM-MAP 狀態雙寫入路徑無協調**：`skills/doc-health/SKILL.md:36` `--sync-system-map` vs `skills/metadata-sync/SKILL.md:3` 生命週期宣稱——誰是狀態更新 owner 無交叉宣示。

**S9｜scan-project 腳本路徑缺 ZCode 變體**：`skills/scan-project/SKILL.md:57` 用 `${CLAUDE_SKILL_DIR}` 無 ZCode fallback（兄弟 skill standup:27 有處理）——ZCode 跑會得空值路徑。

**S10｜rules-reminder 描述措辭未隨跨 harness 部署更新**：description「Enforces the most frequently violated **Claude Code** rules」——ZCode 端讀到別家 harness 名。

**F2｜zcode-registration delegate 條目版號漂移**：`hooks/zcode-registration.json:6` 自帶維護條款「plugin 升級時同步更新」＋:78 指 delegate **1.0.0**——現役 plugin 已是 **1.0.1**（舊 cache 在場故引用未斷）。

**F5｜schedule-registry browser 服務行 port 語境錯置**：`ai-analysis/schedule-registry.md:25`「backlog-browser…（`http://127.0.0.1:6421`）」——:6421 是 report-server；browser 實際 `--port 6422`（`run-backlog-browser.sh:2`），同表 A5 行的分開表述才是正確形態。

### 已驗證排除（假陽性，三軸合計）

- 90KiB vs 100KiB：`deploy_agents.py:132` 刻意低於 ZCode 截斷線，兩處宣稱一致
- 引用存在性全數通過：cr-research registry、illustrate-html-mode、`check_single_source.py`＋`deploy_bundle_freshness`、`scip_refs --callers`、memory 三條目、memory-spine/index.md、delegate-bridge/docs、四個全域 symlink
- `rules/AGENTS.md:134-151` 自檢 grep 實跑乾淨；`_ai-behavior-constraints.md:15` 確認是指標非內容禁令
- post-build 鏈序（code-review→judge-review→修正→consistency→metadata-sync）三處一致；finding status 枚舉單一源一致；起手式五步、建卡即 commit、結案兩步跨檔一致
- 79 個 skill name 與目錄名全數一致；skills 宣稱的腳本全數存在
- `sync_agents --check` exit 0（roles↔registry 同步）；LaunchAgents browser plist vs repo IDENTICAL；manifest 1072 頁全在場
- 語音 sentinel 路徑三方一致；usage-ping 退役在 hook 端已同步

### Unverified（本機無法查證，不下結論）

- `rules/model-routing.md:20`「未連線全名會拒絕 spawn」；Muse 65,536 bytes 截斷 runtime 行為
- Claude rules loader 是否消費 frontmatter `paths:`（G11 關鍵未知數）
- `~/.zcode/cli/config.json` 與 registration 範本子樹全等性（C 軸已逐條比對 hooks 子樹，無漂移發現）
- upgrade-sj/nt-query 對外部 repo 的路徑宣稱；corrections-weekly 絕對路徑跨機可攜性
- ZCode CronList 3 條 automationId 與 mosaic 23:20 cron prompt 本體（跨 workspace）

## ③ 顧問裁決與歧異（Phase 3）

兩顧問皆經 bridge 完成唯讀 advisory（muse＝muse-spark-1.3/xhigh，jobId `job-mtuf9gyq-z2rnkw`；codex＝chatgpt-web/high，jobId `job-mtuf9h0z-mg99gg`；全文 `.agent-tmp/consistency-consult-{muse,codex}.out`）。

### 共識

- **中級 13 條兩家全數判「真矛盾需修」**（零否決；五群全數成立）。
- **S1 與 F4 一致標為最重**——與本報告「接近高」邊界案例標註吻合。
- **G11 一致「先查證再裁」**：Claude loader 是否消費 `paths:` 未證實，不硬判。
- **盲區本質收斂**：三軸都是 producer artifacts 靜態比對，掃不到「源自洽、但 consumer 沒照預期吃」。muse 提「部署渲染對等軸」（diff repo 源 vs 各 harness 實際載入產物：bundle 生成、symlink 解析、live hooks、截斷後實字）；codex 提「Harness Runtime Consumption 軸」（disposable session probe：實際載入哪些 rule、優先級、role 能否 spawn、hook 是否觸發）——同一主題的靜態面與動態面。

### 歧異

- **第一優先**：muse 排 S1＞F4（always-on rule 每次 spawn 相關 session 都撞）；codex 排 F4＞S1（自主 cleanup 的 runtime silent-degrade 是真實安全面）。判準差異：誤導頻率 vs 故事後果。
- **低級 13 條分類**：兩家一致「真 trivial」＝G10、S7、S9、F2、F5；codex 另納 G7。muse 多判 G5、S8、S10 為真 trivial；codex 判 G5、G8、G9、S8、S10 為噪音/誤報；G6 僅 muse 明判誤報。此帶屬「修不修皆可」，可整批順手或全略。
- codex 補充證據：S2 在 `skills/_common/state-md-write.md:3` 與同檔 `:34` 亦自相矛盾（範本內部不一致加一處）。

### 可信度註記

兩顧問獨立收斂於「13 條全真矛盾」；findings 本身已有雙側機械證據支撐，顧問工作是分類與排序判斷，主 session 未逐條覆核顧問結論。codex 輸出前段有 websocket/MCP transport 錯誤行（codex 端啟動噪音；job completed exit 0、產出完整，不影響裁決）。

## ④ 修復建議優先序（Phase 4——提案性質，採不採 user 裁；本弧不執行修復）

綜合兩顧問排序＋主 session 判斷（判準：改變 AI session 行為者優先、always-on 面優先於文件噪音）：

| 序 | ID | 修法方向 | 修點 |
|---|----|---------|------|
| 1 | S1 | `rules/model-routing.md:16` role 表刪 `impl`/`test-gen` 或改指 `impl-lite`，依現役 registry 重寫 impl 責任邊界（impl-lite／主 session／external-runtime） | 單檔小修，always-on 面 |
| 2 | F4 | ai-rules 側預檢兩段（環境 loud-fail＋worktree 空檢）同步進 mosaic twin；或把 twin 條款升級為機械同步/單一源 | 跨 repo（mosaic 側）——建議開卡承接 |
| 3 | G4 | `rules/AGENTS.md` 部署紀律段登記 `bundle: skip` 語法＋被剝內容清單；或取消剝除改「短核心＋pointer 到 skill」 | 治理登記，單檔 |
| 4 | G1 | 家族清單立單一源（以 `deploy_agents.py` targets 為機械源），根 AGENTS.md／rules／instruction-writing 他處只引用不列舉 | 3-4 檔對齊 |
| 5 | S3 | `commit/SKILL.md:203` 不再重畫 flow，改引用 code-review canonical（防 session 從 implement 直跳 commit、跳過 post-build） | 單檔小修 |
| 6 | S4 | 清 usage-ping 語音殘欄（:30、:118，ebf269e 去語音殘留） | 單檔 |
| 7 | S2 | STATE.md 寫入端以 handoff 自述為準收斂三方（`_common/state-md-write.md:3` 刪 handoff 宣稱、rule 對齊），一併修同檔 :34 自打處 | 2-3 檔 |
| 8 | F1 | `com.ai-rules.backlog-cleanup.plist` 補進 `deploy/launchd/` 版控源 | 單檔新增 |
| 9 | F5／F3／S5／S6 | port 語境 6421→6422；`_inbox`/`_projects` 補 lazy-create 註記或修路徑；implement:279 stale ref；instruction-writing:151 斷連結 | 單行批次 |

**低級 13 條**：共識真 trivial（G10、S7、S9、F2、F5；codex 另納 G7）建議順手批次；歧異帶（G5、G8、G9、S8、S10）可全略或挑修；G6 不修（muse 判誤報）；G11 先跑查證（Claude loader `paths:` 消費行為——可併入下述第四軸 probe）。

**結構性建議（兩顧問收斂，提案）**：長期加「部署渲染／runtime 消費對等」第四軸——靜態面 diff repo 源 vs 各 harness 實際載入產物（bundle 生成檔、symlink 解析、live hooks 子樹、截斷後實字、frontmatter 消費）；動態面 disposable session probe（rule 載入／優先級／role spawn／hook 觸發）。G4、G11 與本次 unverified 堆積正屬此軸；可作為 /consistency 或獨立腳本的擴充方向，另行開卡評估。

