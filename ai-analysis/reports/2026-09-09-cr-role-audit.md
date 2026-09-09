# code-reality 全流程角色稽核——質性「可用未用」情境盤點＋三顧問建議

> 排程執行（2026-09-09 23:00，origin：user `/at 23:00` 原話——「仔細檢查 code reality 在整個開發流程中扮演的角色, mosaic_alpha 所有wt + ai riiles, zcode muse的對話紀錄都要看，是否有可以用但是沒有用到的時候…然後問 muse, 5.3, codex web gpt high 的建議，看看能不能將所有開發流程都妥善利用」）。
> 方法：主 session（GLM-5.3）建基線 → 四個 flash agents（cr-research 型，glm-5.3-flash）平行掃描 → 報告 → 三顧問（muse／GLM-5.3 general-purpose／codex chatgpt-web/high）→ 綜合提案。
> 狀態：✅ 完成（2026-09-10 00:0x 收斂——四 agents＋三顧問全交卷，§5 終稿落盤；中間產物 `.agent-tmp/cr-audit-*`、顧問全文 `.agent-tmp/cr-audit-advisor-*.out`）。

## 1. 角色基線（治理檔定義的 CR 角色＋既有量化）

### 1.1 CR 是什麼（定義源：skills/code-reality/SKILL.md）

符號/圖譜工具鏈，住獨立 repo `~/Github/code-reality`（Rust carrier），消費形態 `code-reality <tool> --repo <repo-root>`（CLI）或 ZCode plugin MCP（21 工具）。雙源分治：plugin skill＝工具事實真相源；ai-rules skill＝生態操作真相源（何時跑、接線、紀律）。

**治理接線的時點表**（skill「何時跑」段）：

| 時點 | 工具 | 消費者 |
|------|------|--------|
| 新 repo／缺 graph.db | `build` | 任何 graph 面消費的前置 |
| implement 階段 1 | `snapshot --label <ep>` | delta_tour 的 before 基準 |
| 弧模式（code 已 commit） | `delta_tour <a> <b> --ep` | code-review 模式 B primed／post-build／implement 階段 6／debrief |
| hub symbol 波及盤點 | `hub_refs`（hazard 安全網） | debrief 第 5 段；「可刪」判斷前必跑 |
| graph_audit 缺差對照 | `scip_refs` | callers 真相源 |
| EP 規劃期 | `project`（投影圖 orchestrator） | execution-plan 段落 0（EP 作者）＋ep-review F3（判讀） |

**規則層路由**（rules/symbol-query-routing.md）：符號/引用/呼叫鏈/消費者/依賴查詢 cr-first；任務啟動 gate（涉及引用/fan-in/邊界查詢第一步確認 CR 在場）；rename/改簽名前必查全呼叫點；測試集機械反查（quality-constraints：impact_radius/scip_refs --callers，不憑目錄直覺）。

### 1.2 承諾點地圖（提及 CR 的 workflow 載體，rg 盤點 2026-09-09）

核心定義：code-reality／cr-query／symbol-query-routing（rule+skill）。接線消費者：post-build、execution-plan、implement、code-review、ep-review、review-engine、cross-verify、handoff、debrief、smell-detector、corrections-weekly（cr_usage.py 健檢）、daily-maintain、maintain、arch-thinking、blueprint-bootstrap、tour-bootstrap、scan-project、_common/illustrate-artifact-menu、work-order。Agent registry：cr-research（段落 0 研究）、spec-miner、lite-verify、cross-verify-investigator、code-reviewer(-primed)、vision-review 白名單掛 CR MCP。

### 1.3 既有量化結論（本次定位＝質性互補）

- **2026-09-01**（token-impact 報告）：EP2 換軌後 1.5 天觀察窗**滲透零**——「條文在場、行為不在場」；implement 用量不降反升（其 hotspot 在批次化/Read 紀律非符號查證）；判定「省 token」價值主張不成立，重新定位為「結構證據品質」。修正方向：升級①＝research agent 掛 CR MCP 白名單（把接線放進工具可見域，不是 prose）。
- **2026-09-03**（remeasure 報告）：**升級①生效**——cr-research ×5 spawn（4 次正牌 EP 段落 0）、結構查詢 16 次、EP fresh input −36%（342K→220K）、滲透率 2/10=20%。殘餘問題＝**引用落地斷鏈**（查詢結果進 EP 但 `[SRC]` 引用全遺失）。三建議：①research.md 落檔（機械可驗收）②implement review spawn 改 cr-research 優先③用量面不動。
- **corrections-weekly CR 健檢**（週六 cron）：cr_usage.py 定期量測滲透指標。

> 本次差異定位：前兩份是「量」；本報告收「質」——具體哪些決策時點該用未用、什麼情境跳過、正面案例長什麼樣，以及 muse 側（無 MCP、只有 CLI＋64KiB rules 截斷風險）的結構性疑問。

## 2. 四路掃描發現（Agents A/B/C1/C2——✅ 全數已收）

### 2.1 Agent A：mosaic_alpha 三 WT（✅ 已收——done EP 39 全掃深讀 12＋卡 82＋git log；三 WT 目前同 HEAD 1ba946f，CR setup：WT1 08-29、WT2/3 09-03——**09-03 前的弧客觀上無 CR 可用**）

**計數**：可用未用 8（2 強/2 中/4 弱-parity）｜正面 9｜不可用/形態坑 6。

**類 1「可用未用」（全部附現場 CR 對照）**：
1. **（強）adj-temporal-contract（09-07）「唯一 caller」錯誤**——EP 宣稱 `ExDividendGateway.get_by_code` 唯一 caller＝adjustment.py；R1（🔴）事後被抓 market_intel.py:96＋scan_capital_increase_events.py:114 皆走此介面——**CR 現場對照＝8 callers（production 3＋tests 5），一次 5 秒查詢即見全部漏項**；靠額外一輪 review 才擋下，且是對外 gateway 簽名變更。
2. **（中-結構性）MOS-74 reexport-waves**——消費者枚舉全 rg-alternation；卡面自證「MOS-57 普查實證單 pattern 會漏」——**明知 rg 會漏仍以多 pattern rg 為方法**（CR refs 機械涵蓋全部 import 形態）。
3. **（中）MOS-73**——EP 開工條款「以 CR refs/callers 加掃描補齊實際 callers」，實際記錄「caller inventory（rg 全 repo）」——**prescribe CR 但執行 rg**（review 輪有真用）。
4. **弱/parity（誠實列）**：MOS-83 rename checklist（CR 對照與 rg 集合一致）、daily-window `load_features` 檢查（同集合）、mos-82 零消費者宣稱（CR 對照＝0 callers，宣稱正確但證據形態未載）——**符號名唯一時 rg 與 CR 等效**，方法違反 CR-first 條款但無價值損失。工具邊界反例：module 常數/deploy shell scripts＝CR 盲區，rg 正確。

**類 2 正面（9 條 top）**：**mos79——CR 發現卡 desc 漏列的活躍消費者 experiment_mtm_equity.py、直接改變 S1 工作範圍**；mos78 專章「依賴關係與消費者（CR callers/closure/impact_radius）」作風險表驗證證據；mos223 research journal 混合紀律典範（CR 面＋盲區都明文＋`[SRC]`）；mos80「新檔無 inbound——CR 缺場以 rg 補」誠實降級；**資料面常態化**——chain_tour/tour_validate 接進 post-build gate、三 WT snapshots 21+12+9 枚。

**類 3 不可用/形態坑（6）**：tour_validate 相對路徑 bug 完整閉環（`--repo .` exit 1 零匹配→17 個真錨債未被驗出→v0.6.8 根修）；mos-4 delta_tour 跨世代 phantom 刪檔（v0.6.3 修）；09-05 spawn captcha＋Explore fallback 併發上限（誠實降級紀錄）；09-03 前 WT2/3 literally 無 CR；heal/panic 摩擦；**查詢形態摩擦（本調查現場重現）——module-path 與 display 形態都查無 DEF、僅 bare name／`Class.method` 有效，6 連敗後第 7 查才命中；MCP 首查觸發 index heal 71.1s**。

**Index 狀態**：三 WT graph.db 35.9-37.9MB 全新鮮（@HEAD，09-09 22:2x refresh）；`.code-reality.toml` 全在場（WT1 含 hazard_registry×2）——**mosaic 側資料面健康，對比 ai-rules 側 toml 缺場**。

**A 總括**：**CR 滲透與「接進自動化/流程角色」強相關，與「查詢者自由裁量」弱相關**——資料面因接進 gate 採用近乎常態；符號面晚至 09-08/09 才在 spawn cr-research 的研究弧出現，同週 rename/衛生弧仍 rg。成因：(a) 查詢形態摩擦（首次使用成本高）、(b) 早期信任侵蝕（captcha/heal/相對路徑 bug 落在習慣養成窗口）、(c) rg 對唯一符號名確實等效、缺乏「不用會出事」的即時回饋——**唯一強反例都發生在負面宣稱場景（「X 不走此介面」「零消費者」），正是 rg 蓋不住的「證明不存在」型查詢**。制度面最有效槓桿＝把「零消費者/唯一 caller 宣稱」變成 gate 條件（如 tour_validate 之於錨），而非依賴段落 0 自覺。
### 2.2 Agent B：ai-rules repo＋承諾 vs 兌現（✅ 已收）

**承諾面**：19 個 workflow 載體全掃（17 skill＋work-order＋rule 層），30+ 接線語義行。EP 段落 0（cr-research spawn＋工具清單＋「每個 ripple 宣稱附 `[SRC]` 工具輸出引用」）、implement 階段 1 snapshot「一律跑」、review-engine「CR 接線查證段硬性必含」、post-build hook 2 持久版 delta tour、debrief hub_refs、corrections-weekly cr_usage 健檢——承諾網完整且密集。

**類 1「可用未用」3 條**：
1. **AIR-32 量測窗（歷史最大洞，已修）**——review-flavored spawn prompt 含 CR 指引 0/66；code-reviewer 族有白名單仍僅 ~4/40 實際呼叫；handoff 續跑弧 4 件跳過 snapshot（`backlog/tasks/air-32….md:24`）。
2. **AIR-55/56 hooks python 變更零 CR 痕跡（現場對照：CR 其實可答）**——兩卡驗證全走 pytest；CR `callers is_pool_entry` 現場回 1 callers（`hooks/memory_hook_common.py:56`，`[SRC] @ b75e8a7`）。部分正當：接線本體是 settings.json（CR 盲區）。
3. **air-48 弧缺 baseline snapshot**——snapshots 有 air-49/50/52/29 label、air-48 無（implement:79「一律跑」個案未兌現）。

**類 2 正面 6 條（top）**：09-03-air13 CR×rg 交叉驗證（rg 6 檔 vs impact_radius 15 test 檔、擋歷史漏網）；`[SRC]` 引用首次落地 done 歸檔（09-09-skill-contract-fixes/agent-b-report.md:66）；AIR-32 修復後 handoff snapshot 首次實戰（air-50/52 實落）；AIR-33 cr-demand 迴路閉合（三缺口→v0.6.4 修復）；in-flight pilot-pool 4 檔帶 `[SRC]`。

**類 3 不可用/形態坑 5 條**：WT 缺 scip index 的誠實降級（09-07-memory-governance/ep.md:38）；**`.code-reality.toml` 缺場→delta_tour EP 宣稱對照整段退化（今日實證：`.agent-tmp/2026-09-09-ep.tour`「未比對——profile 未載入」）**；`--repo` 相對路徑 bug（v0.6.8 根修）；callers 符號須 bare-name（module-path 查無 DEF，現場雙向重現）；AIR-33 三缺口史。

**09-03 三建議落地狀態**：①research.md 落檔——**未 codified**（execution-plan skill 無產出條文；done EP 僅 1 個 research.md 且是建議前舊形態；實踐 partial＝in-flight EP 自覺做了）；②implement review spawn 改 cr-research——**未照字面、被 AIR-32 替代**（review-engine「硬性必含」範本路線）；③cr_usage 常態健檢——**載體在場、迴路實質斷線**（cron＋腳本在，但月檔 corrections-*.md 全 git 史零 commit、09-05 週六無可見產出）。

**Index 狀態**：graph.db 909KB 在場（09-09 18:33，落後 HEAD 約 4h；首查 auto-heal 2.5s 自癒至 HEAD）；snapshots 7 枚；`.tours/delta/` 空＋manifest 不存在（**持久版 delta_tour 承諾自設立以來零落產**）；`.code-reality.toml` 缺場（最單一可修斷點）。

**覆蓋**：19 載體＋done EP 25/25＋backlog 全掃＋git log -80；docs-mode 正當缺席約 18-19/25 EP。

**B 總括**：**斷點不在查詢行為，在量測與落檔迴路**——①toml 缺場使 delta_tour 核心價值（EP 宣稱對照）在 ai-rules 自身從未完整發生過一次；②CR 滲透健檢零產出（無人量測狀態）；③research.md 條文缺席＝下個 EP 仍會再斷。修復成本序：toml（一行）→ research.md 條文（09-03 已論證機械可驗收）→ 查 cron 為何無產出。
### 2.3 Agent C1：ZCode 對話紀錄（✅ 已收——真 DB `~/.zcode/cli/db/db.sqlite` 2.4GB，唯讀）

**量化底盤（08-19 後）**：CR MCP 全呼叫 callers 112／refs 104／impact_radius 35／snapshot 32＋CLI（scip_refs 67/graph_query 50/build 34…）。**週趨勢上升**：08/19-25＝0 → 08/26-09/01＝112（33 sessions）→ 09/02-09/08＝178（54 sessions）→ 09/09 單日＝91（16 sessions）。

**意圖時刻歸因**（942 sessions、2,389 個「找引用/消費者/呼叫點/零 caller」時刻，±15min 工具窗）：**CR 近傍 175（7.3%）／rg 近傍 2,110（88.3%）／兩者皆無 4.4%**——rg 近傍非全不當（字串鍵/YAML 本該 rg），此為支配度非錯誤率。

**類 1「可用未用」top 5**：
1. `sess_364996c2`（MOS-83 rename 衛生批 09-09）：六符號 rename 前用 rg 迴圈＋AST——「rename 前必查 cr refs/callers」成文規則整段跳過（CRnear=False）。
2. `sess_740807c3`（MOS-29 09-04）：「零 production 消費者→刪除路線成立」決策全建立在 rg 文字掃描（全 session 零 CR）。
3. `sess_8d139bba`（08-25）：rg 消費者盤點漏抓 `ui/trading_dashboard.py`、靠 lint 補上——rg 失敗模式實錄。
4. `sess_2e6cdf11`（08-30）：「`create_all_buttons` 零外部消費者」YAGNI flag 事後勘誤——實被 `FloatingControls.from_behaviors()`（dynamic_chart.py:477）內部呼叫，**假零消費者差點刪碼**。
5. `sess_8a20c5bd`（MOS-73 09-08）：呼叫點上下文用 `sed -n` 直讀（dict-key 部分 rg 正當，誠實界線）。

**類 2 正面**：cr-research 24 sessions 用 CR（market_thresholds refs/callers/impact_radius 全套）；**引用落地已改善——22/24 尾端帶 `[SRC]`、`done/09-03-mos10-sj-data-resilience/ep.md` 實際含 `[SRC]`（09-03 報告時 0 檔——最後一哩修復在 mosaic 側已發生）**；主 session 混合模式出現（MOS-57 明確派 cr-research 查 labels↔datasets 斷環）。

**類 3 不可用**：**cr-research spawn 死於 auth（captcha verify failed）→重試靜默漂移成 Explore（rg 型）**——供應鏈脆弱＋降級無人回頭；callers tool_timeout×4；「查無 DEF」110 宗（bare-name/路徑混寫的符號形式摩擦）。

**缺口模式（C1 歸納）**：
1. **CR 停在段落 0，進不了 build 的手**——research 股用 CR；implement 主體（impl-flash 33 sessions）CR＝0；「查消費者」時刻 88% 走 rg 反射。
2. **fallback 已制度化**——spawn 失敗→「主 session fallback，已標記」的 rg 路徑順滑到不觸發重試。
3. **rg 可信域錯位**——字串鍵掃描 rg 正當；「零消費者→刪」verdict 需要 transitive symbol 邊（兩個實證誤判都落在這錯位）。
4. **符號形式紀律弱**——查無 DEF 高頻，摩擦推人回 rg。

**Agent 型態對照（工具可見域假說——成立）**：cr-research 23/32（72%）用 CR、171 次結構查詢；主 session 12%；code-reviewer 5%／primed 4%；**Explore 475／general-purpose 159／vision-review 502／impl-flash 33／spec-miner 17 sessions 全部 0**——非白名單 agent 千餘 sessions 零 CR。

**覆蓋**：942 sessions 意圖掃描＋深讀 13 主/股 sessions＋cr-research 24＋1 條 spawn 鏈（21 children）；限制：±15min 近傍歸因是啟發式、查無 DEF 後重試行為 unverified。
### 2.4 Agent C2：muse 對話紀錄（✅ 已收——408 sessions 全淺掃＋14 深掃，窗口 09-02~09-09＝muse 歷史全長）

**滲透率：CR 任何形態 5/408 session（1.2%）——CLI 4＋MCP 1；rg/grep 169/408（41%）＋muse 內建 `search` 工具第三替代路徑。**

**正面案例（5 個，全部 prompt 注入驅動、零例 rules 自發）**：impact_radius on `scripts/deploy_agents.py`（spawn prompt 逐字注入「結構查證用 CLI：code-reality callers/impact_radius…」）；mosaic `pre_swing_profiler.py` impact_radius（工單紅線「只准 git show／rg／ls／code-reality 查詢面」）；唯一一次 CR MCP 實呼＝`snapshot label:mos65-build-before`（09-07）——同 batch 照樣 rg。**最純樣本**：09-02 user 親問「你這邊知道有 code reality可以用嗎」——muse 事前不知 CR 存在。

**「可用未用」主流形態**：接手 EP 的 507 工具呼叫 session 全程 search/grep/rg 零 CR；40MB 分類器討論 session（981 工具呼叫）rg 連發零 CR；impact_radius 成功後的驗收腿仍以 rg 反查為準——**CR 未成為預設信任源**。

**規則面結構證據（64KiB 截斷在場且靜默）**：`context_block_diagnostic` 機械指紋——**134/408（33%）session rules 可證被切**（69 個落 65533-65536、65 個恰 32000＝09-08 深夜 untrusted 自動化批次）；32000 cap 恰好切掉 bundle 尾段的 CR 路由規則（tool-discipline@byte 36165、code-reality 路由@34080-34305）；**無任何 truncation 警語**——model 無從自察。**前提翻案**：muse 自 09-05 已掛 CR MCP（settings.json `mcpServers.code-reality`；09-03 起 session catalog 已列全套工具）——「muse 無 CR MCP」過時。

**瓶頸歸因（證據強度序）**：①**規則沒載（主因）**——33% 截斷＋早期 bundle 根本未含 CR 路由＋正面案例全靠外部注入；②**不是工具不可見**——binary 在場（0.6.8+5938aee）、MCP 在場、10 次 CLI 呼叫全成功；③**習慣慣性（次要）**——rules 完整載入的 session（bytes=55244 未觸界）仍走 rg/search。

**限制**：未深掃 ~394 session 只有命令面統計；65535 叢集的 global/project 串接組成為推斷（unverified）；muse `search` 工具用量未精確計數。中間產物：`.agent-tmp/c2-scan.py`、`c2-scan-results/`（408 檔）、`c2-transcripts/`（14 檔）。

## 3. 缺口模式分類（四路交叉綜合）

**模式一：接線形態決定滲透——自動化 gate ＞ agent 白名單 ＞ prose 條文 ＞ 自覺。** 資料面（snapshot/tour_validate/chain_tour）接進 post-build gate 與文檔弧→近乎常態（三 WT 42 枚快照）；符號面靠 cr-research 白名單（72% sessions 用 CR、171 次查詢）與段落 0 注入；主 session 意圖時刻僅 7.3% 用 CR；非白名單 agents（Explore/general-purpose/impl-flash…千餘 sessions）＝0；muse 側 1.2% 且零 rules 自發、全靠工單/spawn prompt/user 親問注入。**遞移律：離「工具可見域＋流程必經點」越遠，行為越退回 rg 反射。**

**模式二：價值集中在「證明不存在」型查詢（負面宣稱）。** 全部強案例都是負面宣稱場景：「唯一 caller」（8 vs 1，靠 review 才抓到）、「零消費者→刪/YAGNI」（create_all_buttons 假零消費者差點刪碼、MOSAIC_DISPLAY_TZ rg 漏抓靠 lint 補）、「rg 單 pattern 會漏仍用 rg」（MOS-74）。符號名唯一時 rg≡CR（parity 案無價值損失）——**CR 的不可替代性＝transitive symbol 邊上的 negative verdict**。

**模式三：fallback 已制度化＋供應鏈脆弱。** cr-research spawn 死於 auth captcha→重試靜默漂移成 Explore（rg 型）→「主 session fallback，已標記」順滑到無人回頭重試；「查無 DEF」110 宗（符號形式摩擦）持續把人推回 rg；MCP 首查 heal 71s。**降級路徑太順＝滲透天花板。**

**模式四：符號形式紀律是第一哩摩擦。** 有效形態僅 bare name／`Class.method`；上層 instruction 導引的 module-path 形態與口語 display 形態都查無 DEF（兩側 agents 獨立現場重現）；查無 DEF 後正確形式的重試行為未制度化。

**模式五：量測與落檢迴路斷線（承諾網＞行為網）。** corrections-weekly CR 健檢零產出（滲透趨勢無人量測）；research.md＋`[SRC]` 落檔未 codified（mosaic 側 done EP 已實踐、ai-rules 側靠自覺）；ai-rules `.code-reality.toml` 缺場→delta_tour EP 宣稱對照（核心價值）在自家從未完整發生、持久版 `.tours/delta/` 零落產。

**模式六：muse 側結構性截斷。** 33% session rules 被靜默截斷（32000 untrusted cap 恰切 CR 路由段；無警語＝model 無從自察）；CR MCP 09-05 起在場但 1/408 使用；規則完整載入的 session 仍走 rg——**截斷是主因、慣性是次因、工具從來不是瓶頸**。

**跨模式總括**：CR 的問題不是能力也不是承諾網不足，是**行為接線的「最後一哩」**——承諾已過剩（19 載體 30+ 接線行），兌現集中在「被接進必經路徑」的少數形態（post-build gate、cr-research 白名單、工單注入）；其餘全靠自覺，而自覺已被證明不可靠（7.3% vs 88.3%）。

## 4. 三顧問建議（muse／GLM-5.3／codex chatgpt-web/high；工單：`.agent-tmp/cr-audit-advisor-workorder.md`；全文存 `.agent-tmp/cr-audit-advisor-{muse,codex}.out`）

### 4.1 muse（muse-spark-1.3，effort high，job-mtu91smu，✅ 已收）

**核心論點**：CR 的問題不是「接線不夠多」（19 載體已過剩），是「**必經點太少、自覺點太多**」——新增接線只允許 gate／白名單／工單注入三形態，新增 prose 條文一律拒絕；接線只鎖「證明不存在」型查詢點。

**逐階段**：spec 不接（例外：spec 含改簽名/刪符號字樣→附一句指向 EP 段落 0 核驗）；EP 段落 0 保持 cr-research＋codify research.md＋`project` 只用於新符號 EP＋開工前置檢查（toml 在場？graph 新鮮？缺則誠實降級）；**implement build 主體不接（impl-flash 0% 是正確分工——stale index vs LSP 即時面），只設兩個負面宣稱 gate：rename/改簽名前必跑 refs/callers、刪除/YAGNI verdict 前必跑 hub_refs**＋snapshot「一律跑」降為「有 code diff 才跑」；review 收窄「硬性必含」為雙觸發（負面宣稱→獨立 CR 對照；弧模式→delta_tour）＋**不擴白名單到 code-reviewer（5% yield 已證偽）改 spawn-prompt 注入**；post-build 補 ai-rules toml＋持久版 tour 落檔強制化；consistency 只做引用完整性機械檢查（[SRC] 在場、符號形式）不跑 live；viewport 維持現狀。橫切：符號形式一行紀律、fallback 重試紀律、量測迴路修復或刪除。

**CP 值 top 5**：①負面宣稱 gate（唯一有強反例的形態，~5 秒/次擋刪碼與簽名事故）②ai-rules toml＋持久版 tour（一行成本解鎖自家從未 firing 的核心價值）③research.md codify（mosaic 已自發實踐只差條文）④muse 工單注入片段（繞過截斷與慣性雙障礙，不付 bundle 手術費）⑤fallback 重試＋符號形式一行（兩行成本削「推回 rg 的力」）。**刻意不進榜**：project 常態化、runtime_edges/boundary、reviewer 白名單擴張、Explore/general-purpose/impl-flash 白名單（千餘 sessions 零 CR 是正確分工不是缺口）。

**反過度工程**：rg 就夠——parity 查詢（符號名全域唯一）、md/docs-mode/shell/YAML/字串鍵（CR 盲區）、working-tree 編輯中查詢（LSP 領域）、型別查詢（lsp-bridge）、新檔無 inbound 小弧。該降級/刪除——cr-first 加 **parity 例外 clause**（`[rg-parity]` 標籤，否則條文教人撒謊）；snapshot 改有 diff 才跑；review-engine 硬性必含收窄為雙觸發＋誠實標籤（兌現率 10% 是債不是資產）；**19 載體大掃除**（保留 gate 點，刪 maintain/daily-maintain/blueprint-bootstrap/scan-project/illustrate-artifact-menu 零使用證據的掛名接線——每行無人執行的「必」都在訓練模型忽略規則）；corrections-weekly 二選一（修到真產出或刪接線——殭屍 cron 最貴）。

**muse 不同意報告四處**：①「CR 停在段落 0 進不了 build 的手」不是缺口（該守的是 build 手邊界上的 gate，不是手內查詢——推 CR 入 build 手付 heal 延遲＋stale 誤導雙稅）；②09-03 建議②被 AIR-32 替代是正確演化非遺憾；③模式六因果修正——截斷是必要非充分條件（規則完整 session 仍走 rg），muse 策略**注入優先、bundle 手術次之**；④模式五升級——量測迴路斷線是「承諾網＞行為網」的**總根因**，讓行為可見的投資排序高於任何新查詢接線。

### 4.2 GLM-5.3（內建 general-purpose 繼承旗艦，fresh context，✅ 已收——獨立抽查報告 claims 5/5 成立）

**核心判斷**：與 §3 跨模式總括一致——問題不是承諾網不足，是行為接線最後一哩。軸線＝**把接線放到「工具可見域＋流程必經點」，強制域收窄到 CR 不可替代處（負面宣稱），其餘場景合法化 rg**。接線效力譜系（模式一）：**機械 gate＞spawn prompt 明示（72%）＞agent 白名單（修復前 5%）＞prose 條文（7.3%）＞rules 自發（muse 1.2%）**。

**逐階段（差異亮點）**：spec 不接，但 **spec-miner spawn prompt 加一行**（17 sessions 零用——白名單無 prompt 明示＝無效裝飾）；EP 保留 cr-research＋research.md 落檔（EP 同層 `references/research.md`）＋spawn prompt 加 fallback 紀律與符號形態提示；implement——**階段 1 snapshot 機械化**（handoff 模板加驗證命令：接力 session 首動 `ls .code-reality/snapshots/` 確認 label）＋**rename gate 觸發源用 delta_tour 機械改名清單**（tour 已列改名——改名非零→EP 須附 CR callers 證據，被 diff 逼問而非自覺）；review——**負面宣稱 gate 落 review-engine 單一源一行**（「唯一 caller／零消費者／不走此介面」型宣稱必附 `[SRC]`，缺→Critical finding）＋judge-review 驗證式類型表加此型；post-build toml 一行＋查 `.tours/delta/` 落檔斷點（無消費者則刪承諾）；**consistency/docs-mode 明文排除 CR**（symbol-query-routing 加「md 治理面＝rg 域」）；viewport 維持（token 牆風險零正面案例）；muse 注入不重排 bundle。

**CP 值 top 5**：①ai-rules toml（一行解鎖承諾網最大未兌現項，今日「未比對」鐵證）②負面宣稱證據 gate（cost 近零、唯一精準覆蓋全部已知事故場景——把 CR 使用從「全面期許」收斂為「定向觸發」）③research.md 落檔（白名單已證明、斷的是落檔——讓 `[SRC]` 機械可驗收）④**量測迴路改事件觸發**（兩次有決策影響力的量測〔09-01/09-03〕都事件驅動；週 cron 零產出證明 solo 環境消化不了週期報告——改「每次 wiring 變更後跑一次 cr_usage、數字附卡」，cron 降 optional）⑤符號形態紀律單一源修正（110 宗查無 DEF 是第一哩摩擦主體）。第 6 候選：handoff snapshot 機械驗證。

**反過度工程**：不接——md 治理面（consistency/doc-health/metadata-sync/docs-mode）、字串鍵/config/YAML/module 常數/deploy shell、**implement 機械主體（三個強事故全在宣稱生產/驗收兩端，零例在機械執行段）**、illustrate/smell-detector、**白名單擴散停止**（不加新白名單 agent——修既有的 prompt）、muse bundle 為 CR 重排（規則完整載入仍走 rg——重排救「看得到」救不了「會去做」）。降級/刪除——corrections-weekly cron→事件觸發；`.tours/delta/` 查消費者否則刪；**cr-first 強制域收窄三類**（負面宣稱／rename 簽名變更／測試集機械反查）＋**唯一名符號 parity 查詢明文「rg 等效不強制」**（把 88%-rg-多數無損的現實合法化）；`project` 設觀察窗（零正面案例）；muse 側期待改寫為注入形態。

**不同意報告三處**：①B 總括「查 cron 為何無產出（修 cron 為主）」→應**事件觸發為主**（修好 cron 只會產出每週一份沒人讀的數字）；②A 總括「負面宣稱 gate 如 tour_validate 之於錨」——**形態比擬誤導**：tour_validate 是純機械 shell gate，負面宣稱偵測是語義判斷（grep「唯一/零」必誤報），正確載體＝review-engine 條文＋judge 驗證式（LLM 鏈 gate——符合自家 hook doctrine）；③C1 缺口 1「進不了 build 的手」隱含處方（讓 implement 主體用 CR）——**應重新表述為「不需要進 build 的手」**（與 impl 反射對撞的 context 成本遠大於收益）。

### 4.3 codex（chatgpt-web/high，bridge task，job-mtu91sp6，✅ 已收——全文存 `.agent-tmp/cr-audit-advisor-codex.out`）

**核心判斷**：不要把目標設成「CR 全流程都要用」——**CR 定位＝「結構性宣稱的證據服務」**：workflow 要說「誰依賴誰/影響到哪/只有這個 caller/沒人用/可以刪」就必須進 CR；字串/Markdown/config/runtime behavior 無天然優勢。

**逐階段（差異亮點）**：spec 條件式 spec-miner（依賴「重用/誰在用/刪路徑安全/跨 context」才 spawn，非固定 gate）；EP——research.md＝code EP 機械證據載體（structural claims＋query＋`[SRC]`＋degraded 標記）；**EP negative claim 建 semantic gate（regex 找嫌疑句只負責 routing、不負責驗收——claim 要有結構語義：claim type/symbol/evidence/verdict，靠措辭會漏「沒有其他地方會用到」）**；implement 起點＝每 code EP 一次 baseline snapshot＋rename/delete/signature/cross-module 第一次 edit 前 callers/impact preflight；implement 中途＝working-tree 真相交 LSP；implement agent＝窄白名單＋明確 trigger（或高風險前派短 cr-research preflight）；**review 降級 review-engine「每個新增/修改 callable 至少 callers 一次」（超出證據支持——改 trigger-based：public/interface/rename/delete/cross-module/negative claim 才必跑）**；post-build＝一份 persistent delta_tour 全 downstream 復用（禁重算）；**consistency 100% 不接**（單文件自洽是 Read+rg 域）；debrief consume 不重做；illustrate 只 mode B/C/drift；**smell-detector 最值得接的是 YAGNI/dead-code verdict（callers→hub_refs --hazard→rg complement 三步）**。

**前置修復（codex 認為比一切條文有價值）**：**symbol query shape 五步 ladder**——①`Class.method`/bare name②not found→去 module/file/display prefix 重試③仍無→LSP/rg 找 canonical spelling④CR 再查⑤還是無→`[WARN]` degraded、**不准把 query miss 翻譯成 0 consumers**。殺手證據：**`agents/roles/cr-research.md:23` 角色定義本身教 module-path 形態**（正是查無 DEF 大宗來源）。muse 側：**capability-aware injection**（MCP first→CLI fallback→[WARN] degraded；work-order.md:61 的「foreign runtime 無 LSP/MCP 面」是過時假設，應改 runtime capability detection 而非 provider hardcode）。

**CP 值 top 5**：①negative-verdict gate（所有強失敗案例集中處、用很少 queries 擋最貴的 structural mistakes）②**symbol query shape＋自動 retry（成本近零、可能比任何新接點都有效）**③ai-rules toml profile（**非「隨便一行」——module prefix/claims extraction 須 smoke 驗證，錯 profile 產生更危險的自信假陰性**；典型 sunk infrastructure unlock）④research.md evidence carrier（同一 evidence 被 EP/review/followup/debrief 重用反而省 context）⑤external-runtime capability-aware injection（不先解 bundle 架構就能讓 code 工單進 CR 路徑）。**corrections-weekly 排五項後＋metric 換掉**：penetration % 只當健康診斷非 KPI（否則 agent 在不需 CR 的任務亂 call 就達標）——改量 `negative_structural_claims_with_CR / all_negative_structural_claims`、rename/delete preflight 覆蓋率、not-found→retry 成功率、silent fallback 數、evidence downstream 重用數。

**砍得比報告更狠**：md/rules/skill prose 搜尋→rg；consistency 100% 不接；docs-mode 不 snapshot/build/delta_tour；YAML/JSON/shell/字串鍵→rg；一次性 script→rg（僅其呼叫的 production symbol 改簽名/唯一 consumer 判定才進 CR）；單檔 local rename→LSP；formatting/readability smell→不要；runtime behavior/reflection/plugin registry→CR 只當候選結構證據非 verdict；每 edit 重建 index→不要；所有 EP 跑 project→只留 cross-module/integrator。

**codex 不同意報告三處**：①P1 的「掃字樣＋鄰近 `[SRC]` 就算過」——**文字 regex 可找候選 claim 但不能成 correctness gate**（「沒有其他地方會用到」就逃掉），claim 須有結構語義（claim type/symbol/evidence/verdict 四欄形態）；②P6 的「muse 工單標準化＝CLI 形態」——C2 已證 MCP 在場，正確抽象是 **capability-aware MCP-first、CLI fallback**，非固化即將 stale 的 harness 特例；③P8 補刀——**「唯一 symbol 名 rg parity」只適用 positive lookup，exhaustive negative verdict 永遠不可用 rg**（「我找到 3 個」vs「世界上只有這 3 個」是兩種證明責任）。

**codex 總 invariant（一句話壓縮全部）**：**「任何需要宣稱 structural completeness/absence 的決策，必須有結構證據；文字存在性問題用 rg，live type/working-tree 用 LSP，runtime correctness 用執行證據。」**——承諾網縮小反而更容易兌現。

## 5. 綜合提案：流程 × CR 接入（終稿——三家顧問收斂＋主 session 修訂）

### 5.1 三家全共識（無異議，直接可採）

1. **定位重述**：CR＝「**結構性宣稱的證據服務**」（三家同詞）——目標不是全流程都用 CR，是「誰依賴誰/影響到哪/唯一 caller/沒人用/可刪」這類宣稱必有結構證據。
2. **總 invariant（codex 版）**：宣稱 structural completeness/absence 的決策必須有結構證據；文字存在性→rg；live type/working-tree→LSP；runtime correctness→執行證據。
3. **implement 機械主體不接 CR**（三家一致修正 C1 缺口 1 的解讀——「不需要進 build 的手」）；守兩個邊界 gate：rename/改簽名前、刪除/YAGNI verdict 前。
4. **muse 側注入、不重排 bundle**（截斷是必要非充分條件；5/5 正面案例皆注入驅動）。
5. **rg 合法域明文化**：md 治理面/docs-mode/字串鍵/YAML/shell/一次性腳本/單檔 local rename（LSP 域）——「rg 就夠」清單三家高度重疊。

### 5.2 修訂後提案（初稿 P1-P8 經顧問批判的終版）

| # | 提案（初稿→修訂） | 形態與要點 |
|---|------|---------|
| R1 | **負面宣稱證據 gate**（P1 修訂——codex 否決 regex-gate 形態） | 驗收載體＝review-engine 單一源條文＋judge-review 驗證式（**語義判斷不可 shell 化**——glm53：tour_validate 比擬誤導）；claim **結構語義化**（claim type/symbol/evidence/verdict 四欄；regex 只 routing 不驗收——否則「沒有其他地方會用到」就逃掉）；觸發面＝EP＋review＋implement 邊界（rename/delete/signature/public API）；**negative verdict 永遠不可用 rg**（rg parity 例外只適用 positive lookup——「我找到 3 個」≠「世界上只有這 3 個」） |
| R2 | **symbol query shape 五步 ladder**（P2 升級） | ①`Class.method`/bare name→②去 prefix 重試→③LSP/rg 找 canonical spelling→④CR 再查→⑤`[WARN]` degraded＋**禁把 query miss 翻譯成 0 consumers**。**第一刀修 `agents/roles/cr-research.md:23`（角色定義本身教錯 module-path 形態）**＋cr-query＋symbol-query-routing 同步（定義源改動→rg 掃引用防 drift） |
| R3 | **research.md evidence carrier**（P3，三家全同意） | code EP 段落 0 產出 EP 同層 `references/research.md`（structural claims＋query＋`[SRC]`＋degraded 標記），EP 正文只摘要；機械可驗收（fd＋rg） |
| R4 | **ai-rules 補 `.code-reality.toml`**（P4＋codex 警告） | 非隨便一行——module prefix/claims extraction 須 **smoke 驗證**（錯 profile 產生更危險的自信假陰性）；解鎖 delta_tour EP 宣稱對照＋持久版 tour（典型 sunk infrastructure unlock） |
| R5 | **量測迴路換軌**（P5 修訂——glm53 事件觸發＋codex KPI 換軌合流） | 主形態＝事件觸發（wiring 變更後跑、數字附卡；cron 降 optional 或刪——兩次有影響力的量測都是事件驅動）；**KPI 從 penetration % 換成 negative-claim CR 覆蓋率／rename-delete preflight 覆蓋率／retry 成功率／silent fallback 數**（penetration 只當健康診斷——否則 agent 在不需 CR 的任務亂 call 就達標） |
| R6 | **capability-aware injection**（P6 修訂——codex 否決 CLI-hardcode） | 工單/spawn prompt 注入塊：結構查詢 trigger 清單＋**MCP first→CLI fallback→`[WARN]` degraded**；修 `skills/_common/work-order.md:61` 過時假設（provider hardcode→runtime capability detection） |
| R7 | **fallback 可見化**（P7 保留） | cr-research spawn auth 失敗→回報「CR 未遂」＋重試一次，禁靜默漂移 Explore 吸收（降級路徑太順＝滲透天花板） |
| R8 | **承諾網大掃除**（P8 擴大） | review-engine「每 callable callers 一次」降級 trigger-based；implement snapshot 改「有 code diff 才跑」（docs-mode 免）；19 載體零使用掛名接線刪或降「按需參見」（每行無人執行的「必」都在訓練模型忽略規則）；consistency 100% 不接；`project` 設觀察窗；smell-detector 只接 YAGNI/dead-code verdict（callers→hub_refs --hazard→rg complement 三步）；spec-miner 白名單補 prompt 明示／條件 spawn；handoff snapshot 機械驗證（`ls snapshots/` 確認 label）；delta_tour 機械改名清單作 rename gate 觸發源（被 diff 逼問而非自覺） |

### 5.3 優先序（三家 CP 值交集＋主 session 裁定）

- **即刻（一行級，半小時內）**：R2（含 cr-research.md 角色定義修正——它在教錯）→ R4（toml＋smoke）。
- **短期（一卡內）**：R1（gate 語義化——牽 review-engine/execution-plan/judge 三檔）→ R3（research.md 條文）→ R6（work-order 注入塊）→ R7。
- **中期**：R5（量測換軌）→ R8（承諾網掃除——建議與 bundle 減量弧合併評估）。

### 5.4 落點建議（本報告＝提案，採納與否 user 裁）

建議拆四卡：①**quick-wins**（R2+R4）②**negative-claim gate**（R1+R3，牽三檔）③**外部 runtime 注入**（R6+R7）④**承諾網掃除**（R8＋R5 併入 corrections-weekly 治理，與 bundle 瘦身弧合併）。
