---
name: model-routing
description: Model routing 深層載體 — tier×provider 權威表（requirement 分類〔旗艦/影像/一般〕×五公司，model 值單一源）＋旗艦資格條款（五項）／坐位註記＋role→requirement 分配表＋dispatch 預設（harness 主軸：GLM 主力/額度現值 GLM+muse/實作預設 muse＋glm-5.3-flash/影像＝支援影像的 model/muse 跨家族審查優先/codex 預設不派）＋額度 failover＋lite 分工律（執行層降級條件＝保護面厚度、判斷密集位 full 能力檔、模型歸因紀律）＋external-runtime family→(model,effort,容量) 解析表（muse／codex 委派、工單 profile）、rate limit 並發表、thoughtLevel 但書（sticky 不達 wire #339/#306）、classifier unavailable 處置（重試≤2）＋spawn 失敗態（1301／1308／1302）＋eligibility gate／reviewer 交接契約／套用三路徑。always-on 骨架在 rules/model-routing.md；spawn 前查並發與 eligibility 時載入。觸發詞：額度現值、實作預設、並發上限、rate limit、spawn model、tier、thoughtLevel、reasoningEffort、classifier unavailable、1301、1308、1302、glm-5.3-flash、分工律、保護面、haiku、pins、external-runtime、委派、工單、eligibility、eligibility gate、reviewer 交接、advisory、bridge 必經、完成回報收法、收法、三態判定。
---

# Model Routing — 解析表與 provider 事實

> 本 skill 是 `rules/model-routing.md` 的 on-demand 深層載體：rule 端保留 always-on 骨架（角色→tier 表、兩跳解析原則、tier 詞彙句、external-runtime routing 段頭＋pointer——內容在本檔）；本檔承載 tier→(model, effort) 解析表、external-runtime family→(model, effort, 容量) 解析表、eligibility gate、reviewer 交接契約、套用三路徑、rate limit 與並發上限表、thoughtLevel 但書與 classifier 處置。model id 與容量數字單一源在此（rule／registry／模板僅 family／profile 詞彙）。

## tier → (model, effort) 解析表（requirement × provider 權威表——model 值單一源）

> **tier 詞＝requirement 正式 token**（AIR-24 同源，一個詞彙兩個語義面，不另造第三套）：full＝旗艦需求（judge／EP 規劃／批判）、vision＝影像需求（需「支援影像的 model」——能力軸非強度軸，旗艦／一般都可能具備或不具備）、lite＝一般需求（實作／驗證／挖掘／渲染——標準款省成本）。本表是 model/effort 值的**唯一源**（`sync_agents.py` pin dict 與生成物以本表為 parity 對象）；role 的 requirement 分配見下方 role→requirement 表；dispatch 兩跳＝role→requirement(tier)→本表列。

| tier（requirement） | zai | Anthropic | OpenAI | xai | meta |
|---|---|---|---|---|---|
| **full**（旗艦） | GLM 5.3＝主 session inherit（不釘 id）〔repo-observed〕 | opus〔**未訂閱禁派**〕 | sol high／max〔**預設不派**——額度最少〕 | fabel〔**未訂閱禁派**〕 | muse-spark-1.3（effort xhigh 起） |
| **vision**（影像） | glm-5.3-flash（多模✓ 已實戰）〔repo-observed〕 | 〔未訂閱禁派〕 | 〔預設不派〕 | 〔未訂閱＋本機未安裝〕 | muse-spark-1.3 `--image`✓〔repo-observed〕 |
| **lite**（一般） | glm-5.3-flash〔repo-observed〕 | 〔未訂閱禁派；能力對照 sonnet 級——haiku 基本不用〕 | terra high+（**luna 排除，基本不用**）〔**預設不派**〕 | 〔未訂閱禁派〕 | —（與旗艦同體；額度貴，非省成本預設） |

> 證據狀態標註：repo-observed（本機實測）＞official-doc（官方文檔，非本機 L4）＞first-real-usage-pending（首例實戰待補）。

### 旗艦資格條款（五項）

> 定義「有資格被解析為旗艦（full）」的模型能力條款——資格線穩定（大綱層）；同 tier 內強弱排行不進條款（另見下行坐位註記）。候選模型須全部滿足：

1. **跨文件交叉推導力**：docstring↔斷言、EP↔code、caller↔callee 型不一致能抓；證據指針＝四家同尺比較中五項跨文件案唯終審層抓到。
2. **judge 否決力**：對高信心措辭 finding 有否決傾向而非順勢採納；證據指針＝同尺比較首輪全採納傾向反例。
3. **規劃的契約查證力**：把既有測試契約當設計約束、會推導決策前提失效；證據指針＝同尺比較 wrapper parity 約束與前提失效推導案。
4. **長弧查證紀律**：查證密度不隨 session 長度衰減；證據指針＝同尺比較後段淺驗反例。
5. **寫入邊界首改的邊界意識**：首次改動寫入契約／human truth 層時主動設唯一入口與 crash-only 防線；證據指針＝同尺比較唯一刪改入口案。

> **坐位註記**（換代只改此行；現值坐位見上表 full 行，不重複記載）：候選觀察：無；升坐位法：既有比較尺（四軸＋旗艦不可讓五項任務）跑一弧實測。

### dispatch 預設（user 2026-09-05 裁定、09-07 修訂；訂閱現值變更只改本段＋上表格標註）

**額度現值（2026-09-07 user 拍板「固定記載」）：可用＝GLM（5.3 主力＋glm-5.3-flash）＋muse 兩家**；codex 額度最少不派、Anthropic／xai 未訂閱禁派——派發前可派池只有這兩家。

**harness 主軸（user 的開發入口決定主力 model——與下方 external-runtime「角色 → family → profile 映射」同源）：**

- **ZCode 開發（日常主力）**：主 session＝**GLM 5.3**（判斷/規劃/EP/judge；其餘角色 inherit 主 model）；lite subagent 執行檔＝glm-5.3-flash（省成本層）
- **muse code 開發（user 直用時＝該弧主力 harness）**：muse-spark-1.3 全棧——實作/審查都在該 harness 內；repo 層 AGENTS.md muse 會載入（bridge log 實證；全域 guide 的 muse 部署點未查證）
- **審查類（ep-review／code-review 等 review agent 層）→ muse／glm-5.3-flash 皆可**（user 09-07 放寬「審查類都可以」）：跨家族第二意見仍 muse 優先（非 GLM 視角）；in-harness 審查可用 glm-5.3-flash——原「full inherit 為基準＋保護面厚度條件降 lite」門檻就此放寬；**judge 裁決層不變：固定主 session GLM 5.3**（AIR-24 三防線）
- **實作（implement profile bridge 委派）＝預設 muse**（user 09-07 修訂，取代 09-05「user 指定時派」單批指示慣例）：重實作段 muse、lite 機械段 glm-5.3-flash；**CR 工具鏈 agent（cr-research 等）同收斂 muse＋glm-5.3-flash**——與「user 直在 muse code 開發」仍是兩種形態（委派 vs harness 切換）
- **影像需求（vision tier）＝需「支援影像的 model」，現值＝glm-5.3-flash**（user 09-07「影像目前都用 flash」——選它因 5.3 flash 原生多模，非因 lite tier；非所有 lite 款都具影像能力）——muse `--image` 是能力備註（上表），非現值路由
- **codex（OpenAI）→ 預設不派**（額度最少）——僅 user 顯式指定（例：「codex sol max」）。定性甜蜜點實證：control-plane／docs 形態 repo 的全 repo 狀態對抗深審（[/state-review](../state-review/SKILL.md) 的候選家族之一）——產出與 in-family 盲點正交（權威模型／事務完整性／provenance 類問題）；本行是能力備註，不構成取消顯式指定授權
- **Anthropic／xai → 未訂閱禁派**（含影像格——上表保留能力對照）；Anthropic 之後**視性價比評估**再決定訂閱（CC 原生家，訂了可重配 backend），訂閱後解除標註並補查證

**額度 failover（僅撞牆時）**：GLM 撞 1308（錯誤訊息含重置時間戳）→ muse 承接執行段；muse 亦乾 → 等 reset（`/at`）或 user 裁定硬跑；任何降級必顯式記錄（AIR-13）

### harness 部署填法（pins＝部署預設；值抄上表）

| tier | harness 填法 |
|---|---|
| lite／vision | ZCode：`model: glm-5.3-flash`＋`thoughtLevel: high※`（pins 由 sync_agents 生成，非 authoring）；CC：**用 CC 自己的模型詞彙**——預設 inherit（主 session）、lite 點名 `sonnet` 別名（env 映射層直達 glm-5.3-flash，見 settings.json `ANTHROPIC_DEFAULT_*`）——dispatch 不綁實體 backend id；**地板＝sonnet/terra 級（haiku／luna 基本不用，user 09-05）** |
| full | `model` 省略（inherit）——任何 harness |
| ccr 模式（未啟用） | `Fusion/<tier>`；啟用時 pins 只換值、角色/tier 不動 |

## role → requirement（tier）分配表

| requirement | roles |
|---|---|
| full | code-reviewer, code-reviewer-primed |
| vision | vision-review |
| lite | archify-gen, cr-research, cross-verify-investigator, impl-lite, lite-verify, mem-distill, spec-miner |

> 判斷密集位（judge 裁決／EP 規劃／post-build 編排）不是 role——**主 session 直做**（AIR-24 分工律）；「非 full＋max effort 補償＝未驗證路徑」。新 role 須在此表登記 requirement——缺登記＝`sync_agents.py` fail loud（防靜默 unpinned 上線）。

> ZCode 注意：`thoughtLevel` 綁具體 model（inherit 時不生效）；欄位名**不是** `reasoningEffort`——未知欄位靜默忽略。**※ thoughtLevel 但書**：sticky user reasoningLevel 在場時（user-scope `local_setting`），定義的 thoughtLevel **不達 wire**——telemetry `variant` 記 user 層級而非定義值（08-29 兩數據點：lite-verify＋vision-review 定義 `high` 皆記 `max`，sticky `max` 在場、主 session rows 同 max）。**model pin 不受影響**（frontmatter model 字串逐字到 wire——vision-review 首筆遙測實證）。sticky override 與 silent no-op 尚未分辨（flip 實驗待跑：改 user level≠定義值再 spawn 看 variant 是否跟隨）——對應**已知 open bug 家族**（zai-org/feedback #339「thought-level changes silently discarded after first selection」＋#306 reasoning effort injection 缺陷；EN/cn 文檔一致、用法無誤）。CC 注意：enum 別名（sonnet/haiku/opus）在 GLM provider 由 provider 別名表解析到對應 GLM 模型。

## effort 家族對譯表（跨 runtime 詞彙對照）

> 同一思考投入檔位在四家 runtime 的詞彙對照（AIR-28 補；execution contract tier 欄與跨家族工單 effort 欄對話時用）。**單一源在本表**——registry pins／工單模板／contract 表引用不自带數值；muse/codex 現值權威見下方 external-runtime family 表。對譯是語義對應非等價保證——實現機制不同（ZCode `thoughtLevel` 綁具體 model＋sticky 不達 wire 家族〔見上方但書〕、CC spawn-time enum、muse/codex runtime 參數）。

| 檔位語義 | ZCode thoughtLevel | CC effort（spawn-time） | muse effort | codex `--effort` | repo 慣用位 |
|---------|--------------------|------------------------|-------------|------------------|------------|
| 純機械（渲染／掃描） | low | low | `low` | `minimal`～`low` | advisory 掃描降檔（省 quota） |
| 執行層（lite tier 預設） | `high`（registry pins 標配） | `high` | `medium` | `medium` | lite tier pins |
| 審查／判斷（review 委派） | `high` | `high` | `high` | `high` | review 工單 |
| 深推理（判斷密集／深挖） | `max`（user 層級；定義檔設值 sticky 不達 wire——見上方但書） | `high` | `xhigh`～`ultra` | `xhigh` | muse 委派預設（09-04 定）；深推理升 `ultra` |

> 可考值域：codex 接受 `none`/`minimal`/`low`/`medium`/`high`/`xhigh`（**codex plugin** 的 codex-cli-runtime skill——plugin cache 面，非本 repo 檔；repo 內鏡像 `ref-docs/harness/codex/config-sample.md` 的 config-level enum 無 `none`——companion flag 值域與 config 值域是兩個面）；muse 用 `low`/`medium`/`high`/`xhigh`/`ultra`（`ultra`＝CLI alias → provider 最高級＝API `max`）；ZCode 欄位名是 `thoughtLevel`（非 `reasoningEffort`——未知欄位靜默忽略）、user reasoningLevel 層級含 `max`；CC effort enum 以 CC runtime 為準（repo 慣用 `high`）。跨家族委派時 effort 值以**各家族解析表**為準（muse/codex 見 external-runtime family 表、in-harness 見 tier 解析表），本表只對詞彙。

## lite 分工律（執行層降級條件）

> 09-04/05 夜 GLM-5.3-Flash 全切換的三軸鑑識（對話行為／git 產出／建議查證）定版；rule 端只錄 tier 語義與升降級條件，證據與細節在此。

**執行層可降 lite，條件＝保護面厚度**（三件全滿）：既有測試釘住（可重跑驗證）＋驗證閉環（機械閘門在場）＋非跨邊界語義面（單位換算／領域語義轉換不屬此段）。

- 實證（GLM-5.3-Flash 可靠面）：lite-verify 10/10、cron 四段全交卷、reviewer 20/20 交卷（dual-context 兩側獨立交叉命中）且 10 findings 經 full 複驗全成立、findings 修正 10 分鐘落地、測試警告清理走顯式契約（僅 1 條窄域 filter）
- 已知風險面（降級時主動防）：跨單位語義換算錯＋靜默失效＋斷點汙染（西元↔民國 P0×2/P1）；測試合法化 bug（mock 假設即 bug——lite 模型測試僅規格陳述，驗收證據另補 full 複驗）；inferred findings（報「機制可能」非「實測確認」——judge 遇 inferred 必重跑實測，見 judge-review 三防線）；機械掃描漏變體（rg pattern 需含空格/等號形）；Edit 前未 Read 偏高（20 vs 3——spawn prompt 注入 Read 紀律）
- **判斷密集位不可降**：judge 裁決／EP 規劃／post-build 編排＝full 能力檔——judge 自證塌陷＋sycophancy（錯信心 finding＋順勢採納＝最危險組合）是能力剖面問題。**lite＋max effort 補償＝未驗證路徑**：欲採用先小規模實證（舊 findings 重裁對照 full 裁決），結果記回本節
- **歸因紀律**：模型歸因結論必須 per-message modelID 機械對帳（ZCode db.sqlite；unpinned subagent 跟 spawning session 模型走、registry pin 不受手動切換影響），不接受 session 自述——09-05 三例自述歸因錯（full 亦被 priming 帶偏）
- **管轄對照（兩套降級條件邊界）**：本段三件（既有測試釘住＋驗證閉環＋非跨邊界語義面）＝**spawn 執行層降級**判定；handoff「建議執行 tier」三條件（保護面厚＋EP 條款機械可判＋審查鏈全開）＝**handoff 路由建議**判定——兩套條件管轄面各異，詞形差異非 drift

## External-runtime（family 軸）解析表

> 維護原則：model／effort／容量現值演進只改此段（rule／registry／模板不寫數字與型號——分層：骨架＋詞彙在 `rules/model-routing.md`、現值與映射在本檔）。family／profile 詞彙定義以 rule 為單一源，本段只給權威值。

### 角色 → family → profile 映射（family 表）

| 角色 | family | profile | 備註 |
|------|--------|---------|------|
| 實作（implementation） | muse | implement | 主力 implementation loop 承接 |
| external second-opinion review | muse | review | 獨立第二意見，與 in-harness 驗收審查職責分離（見下） |
| in-harness acceptance reviewer | GLM | — | 驗收委派工單的主審（Writer/Reviewer 分離的 in-harness 側） |
| 診斷 rescue | codex | implement | ad-hoc 選項（想到再用、低頻）；context 小＋消耗快禁大工單 |
| advisory 掃描 | muse | advisory | 唯讀掃描、盤點 |
| 機械驗證／探索 | GLM | lite | 機械查證、探索（沿用 tier→lite 路由） |
| 視覺驗收 | GLM | vision | 預設路由；muse 具視覺能力為跨家族備選 |
| 架構級 EP（blueprint） | muse | implement | 使用者會話在場裁決為 eligibility 前提（gate 第六條）；無 user 在場不放行 |

> 兩種 review 邊界：external second-opinion review（跨家族獨立視角）與 in-harness acceptance reviewer（GLM 主審、把關工單結案）職責分離，前者補視角、後者定結論。容量不足的家族禁派大工單——現值見下表，rule 不寫數字與型號。重大架構／風控／會計 diff 的跨家族 review＝**軟提醒非硬閘**（額度現實：muse/codex 額度吃緊時派不動）——額度允許時至少一側跨家族；不足時顯式記錄降級（in-harness full 雙 context 承接），禁靜默略過。

### family → (model, effort, 容量現值)

| family | model | effort | 容量現值 | 備註 |
|--------|-------|--------|----------|------|
| muse | `muse-spark-1.3` | `xhigh`（user 09-04 定；純機械掃描 advisory 可降 `low`/`medium` 省 quota）；深推理可升 `ultra`（CLI alias → provider 最高級＝API `max`，限 1.3 Standard tier；reasoning tokens 佔 output 比例更大，留意輸出上限截斷） | 長 context（以 provider dashboard 為準） | 具視覺輸入 `--image`，跨家族備選；advisory／implement／review 共用此 family；bridge 端預設 pin 與本表對齊（muse-plugin-cc 弧維護），`--model`／`--effort` passthrough 僅供臨時 override |
| codex | `gpt-5.6-sol` | `high` | 約 258K（user 09-05 實值；以 provider 為準）——額度最少故預設不派（見 dispatch 預設段）；大 context 任務仍優先 muse | ad-hoc 選項（僅 user 顯式指定）；companion `--model` 可傳（內建 `spark` 別名），不傳落 `~/.codex/config.toml` 預設（本機已 pin 同值） |
| GLM（in-harness） | 見 tier 表 | 見 tier 表 | 高（遠高於 200K 級，見 provider dashboard） | 沿用 tier→lite／vision 路由，不經 external-runtime 派發；in-harness acceptance reviewer 屬此 |

> 容量為「需現況查證」性質，隨 model 世代更新只改本表。

### eligibility gate（六條，逐條判）

> 任一不過 → 主 session 直做；「≥30 分鐘」僅提醒信號非機械判準。

1. **決策凍結**：工單目標、範圍與驗收已凍結，無待決設計選擇
2. **條款客觀化**：驗收條款為機械可判（命令＋預期結果），非主觀描述
3. **單一 writer 無待決**：單一 writer 可獨立完成，無需主 session 中途決策或協調多 writer
4. **主價值＝承接 implementation loop**：主價值在承接完整實作迴圈，而非零碎問答或探測
5. **環境可啟動**：目標 runtime 環境可啟動（bridge setup 綠、binary 在場），非環境阻塞
6. **使用者會話在場裁決**：架構級 EP（blueprint）委派須有使用者會話在場裁決——無在場證據面為零，不放行

> **review／advisory 形態條款**（read-only 委派——external second-opinion review、[state-review](../state-review/SKILL.md) 深審腿、advisory 掃描）：以 ①②⑤＋三條專屬判定——**read-only transport**（flag 或工單紅線承載，產出＝findings/報告）、**跨家族成立**（委派對象與 caller 相異家族——external 視角是派發理由本身）、**可重現輸出**（findings 附錨點＋驗收設計，in-family judge 可機械重現）。條件③④（單一 writer／implementation loop 主價值）是 **implement 形態專屬**，不得用以擋 review 形態——否則跨家族審查腿結構性不可達（真實案例：state-review 深審腿依原條文④被擋）。
>
> **跨家族解析表**（未指定 family 時；顯式指定與 caller 同 family → fail-loud）：GLM／ZCode caller → muse；codex caller → muse；**muse caller → fail-loud**——相異家族僅剩 codex 可選，而 codex explicit-only 不因解析繞過：**停下要求 user 選擇**——顯式 `--family codex`，或明示接受同家族 degraded review（caller-harness full dual-context 承接＋記錄）；禁解析層自選降級。

> sandbox-error 禁以 `--yolo` 賭重試（父層沙箱不可越權重試）；分類走 auth-failed／environment，修因後重派。

### reviewer 交接契約

- **完成回報固定欄位**：jobId 或 thread id／base commit／改檔清單／實跑驗收命令與原始輸出／未驗證項
- **reviewer 讀料順序**：work order → diff → evidence → writer report 最後讀
- **產出**：accept／reject／needs-fix 三態 verdict；無 reviewer record 不得結卡（record 落 EP 或工單指定位置）

### flag profile → spawn 參數（external-runtime）

> 本表為 flag 具體值單一源（registry 側只留 thin forwarder 治理原則，見 `agents/AGENTS.md`）。bridge 未暴露的 flag 以工單紅線承載（見 `skills/_common/work-order.md`），暴露後改 flag；roadmap 記錄在 muse-plugin-cc 側。

| profile | family | spawn 參數 | 說明 |
|---------|--------|------------|------|
| advisory | muse | `muse task --disable-write`（bridge 暴露前由工單紅線承載） | read-only 掃描（SM-2）；effort 取上表 muse 列 |
| implement | muse | `muse task --trust-workspace` | 背景跑（見 rules/tool-discipline） |
| implement | codex | `codex task --write`（workspace-write） | 診斷／救援寫入型 |
| review | muse | `muse review --schema verdict`（bridge `review` 子命令） | 產出 accept／reject／needs-fix |
| review | codex | `codex --output-schema <verdict>` | 同上，codex 形態 |

**bridge 必經（muse 委派唯一入口）**：委派 muse 跑 repo 任務一律經 bridge 入口（上表 muse 列＝`muse-bridge.mjs` 子命令的抽象形態），禁直呼 `muse exec` 或其他繞過 bridge 的入口——bridge 落 per-repo `.muse-bridge/jobs.json` ledger（jobId／sessionId／status／text），非 bridge 入口的 muse 產出 ledger 查無，事後只能從副作用側考古（真實案例：mosaic post-build 鏈同鏈兩段 muse 委派一走 bridge 一繞道，繞道段收尾不可考）。完成回報攜帶 ledger jobId（reviewer 交接契約欄位）；委派了 muse 而 jobId 缺席＝入口違規，補查或標明。

### 完成回報收法

> **經濟學動機**：LLM 層輪詢每輪＝1+ request 且全 context 重送；push 收法等待期間 0 request、完成時恰好 1 request。輪詢只存在 bridge 進程內部（muse `wait` 內建亞秒級固定輪詢——零 LLM 成本）。

**決策樹**（未載入背景的 session 單讀可執行）：

1. **簡單轉發（review／critique／diagnosis）**：主 session 背景 Bash 直呼 bridge 阻塞形（muse `task`／codex `task`）→ process exit 自動喚醒 → stdout 即 finalText；jobId 記錄不變（reviewer 交接契約欄位照舊）
2. **長跑（>10min，xhigh 委派）＝fire-and-forget 優先**：`muse task --background "<prompt>"`（長 prompt 改 `--prompt-file <path>` 形態）提交 → jobId 即回 → caller 結束 turn 釋放（不掛前景、不綁 session）。**收法分流（session 是否需接續）**：session 活著且完成後要接續做事 → **背景 Bash 掛 `wait <jobId>`（首選兩段式）**——零 model request，wait exit 觸發 harness notification **自動喚醒 session 接續**；session 將結束或不在乎即時收 → 純認領制（事後任何時刻 `show <jobId>`——**完成無推送、不會自己回來**，須主動查）。finalText 由 per-job jsonl 重導出，ledger entry 只存 status／exitCode／summary。**timeout 到期訊號兩家相反（拆家系判讀——晚收同樣需要的語義，非殘留）**：
   - **muse `wait <jobId>`**：裸 wait 撞預設 5min＝`process.exit(124)`——exit 124＋status 仍 running＝重掛；`--timeout 0`＝forever（長跑必帶）
   - **codex `status --wait <jobId> --json`**：timeout 到期（預設 4min）＝**正常 exit 0**、JSON 帶 `waitTimedOut: true`——以此旗標判讀重掛（124 偵測對 codex 永不觸發）；**codex 無 0=forever**——`--timeout-ms 0` 靜默回落 4min 預設（`codex-companion.mjs:319` `Number(timeoutMs)||DEFAULT`），只能顯式大值
   - 任一家回非 completed 終態 → `jobs/<id>.jsonl`＋working tree 對照再判（reconcileStaleRunning 可能過早標 interrupted）
   - **兩端 SessionEnd 差異（caller 在哪家 harness，決定能否跨 session 認領）**：ZCode 端 plugin hooks 不執行 → background worker（detached，脫離 caller 進程樹）跨 session 存活 → 任何 session 以 `runs`／`show` 認領（fire-and-forget 完整可用）；CC 端 SessionEnd hook 殺 running job 進程樹＋標 interrupted → holder session 必須活著 → fire-and-forget 限縮為「session 內釋放 turn」，跨 session 認領前先確認 holder 在場（事實源：`…/muse-market/muse/<ver>/scripts/session-lifecycle-hook.mjs`＋`hooks/hooks.json`，以 plugin cache 現版為準）
3. **prompt 工程（codex gpt-5-4-prompting 改寫）**：wrapper 保留——wrapper 內單次阻塞 `task`＋env fallback 預寫不變（`CLAUDE_PLUGIN_ROOT` 缺失時 `MODULE_NOT_FOUND` 形態）；wrapper Bash 10min 上限是**約束事實**、wrapper≠job 錯位是**獨立實證**（wrapper 在 runtime 未終局時提前 complete 是系統性常態——muse×2＋codex×2 均需介入實證；wrapper agent 形態＝別名 alias）、兩者因果未驗證——預期超時的工單改走 2
4. **LLM 層 fallback（罕見——原始派發無背景 Bash 掛載；前景短 arm 仍可用）**：ETA-gate 紀律——推估完成時刻前零檢查（一段 `--timeout <eta>` arm）→ 屆時單次檢查 → 未終局重掛遞減 timeout 的阻塞 wait arm（起點＝bridge 預設 5min／4min，按 ETA 緊化至 ~30s 級；每 arm 到期＝1 request）——**永不做 LLM 層定時輪詢**

> **多工複用（fire-and-forget 的複用形態）**：一個 session 持 N 個 jobId 統一掃（`runs --json` sweep 後逐個 `show`／`wait` 認領）；並行 quota 語義＝同 5h window token 加總（並行買 wall-time 不省花費），實用並行上限 2-3 長任務。
>
> **晚收陷阱（Muse 諮詢收編——決策樹尾注）**：`wait` 用有界 timeout 迴圈、勿單一大 block；`stop`/清理前先 `show`／`export`（ledger GC 會吃證據）；委派工單設計成冪等（timeout 後可能重 wait 重收）；jobId 持久化在 workspace ledger（`.muse-bridge/`），不依賴提交 session 的 context——認領 session 只需 jobId＋同 workspace。
>
> **診斷手段（非收法）**：`.muse-bridge/jobs.json`／`show <jobId> --json`／`ps` 進程核對——懷疑 job 狀態時用它們查證，不當等待機制。

> 工單模板見 `skills/_common/work-order.md`（foreign runtime 共用；prompt 為任務本文，禁含委派語言）。

#### transport 三態判定（症狀→證據→處置）

> 收法執行中懷疑 job 卡死時的處置分流；證據以上方診斷手段採集。

| 症狀 | 證據 | 處置 |
|------|------|------|
| transport 未啟動 | env/module 錯誤、log `MODULE_NOT_FOUND`、exit 1、jobs.json 無該 job | 可安全重派 |
| transport 在跑、wrapper 已收 | jobs.json 狀態 running、ps 進程在 | 背景 Bash 掛阻塞 `wait` 收，禁重派（雙跑） |
| transport 死中途、wrapper 空轉 | 進程已亡、jobs.json 停滯、無新輸出 | 機械驗收（working tree＋jobs.json 終局）＋TaskStop wrapper |

### 套用（三路徑都從解析表取值，不寫死絕對 model）

- **external-runtime 派發前重讀本檔「完成回報收法」節**——收法演進快，禁用 session 記憶／memory desc 派發（真實案例 09-05 過期派發事故：看到改版 commit 標題 ≠ 重讀條文，舊詞 resume-to-poll 被 wrapper 契約拒絕）
- **CC Workflow path**（ultracode）：script `agent({model})` 填 literal —— review command agent = inherit（full 為基準；保護面厚度條件成立時降 lite）；lite 類填 lite tier 對應值（查本檔解析表）
- **CC Agent Tool path**（fallback）：spawn `model` param 同上
- **ZCode path**：pins 釘在 `agents/zcode/` 定義檔 frontmatter（治理見 agents/AGENTS.md registry 段）

spawn 前印出確認：`[Agent] model=<依角色 tier>, max=N, current=M`（max 查本檔並發表——lite 層較寬）。

## rate limit 與並發上限（model facts 單一源 — 以 provider 現況為準，可能滯後）

| 模型 | rate limit | 並發上限 |
|------|-----------|---------|
| haiku / sonnet / opus | 10 | **3** |
| glm-5.3-flash（lite／vision 層） | — | **高**（遠高於上列；具體數字以 provider dashboard 為準） |

> provider 帳號級事實，repo 無法驗證；改限額時**只改本表**（agent-workflow 等引用此，不自帶數字，避免 provider 改限額時兩處 drift）。數字可能滯後 — 以 provider dashboard 為準。

## classifier 間歇 unavailable（harness 已知風險，與 model 分派正交）

GLM / 非 Claude harness 的 safety classifier 可能**間歇 unavailable**（spawn agent 收 note、無 findings，非主動阻擋）。這是已知服務端間歇故障，**重試 spawn 是正解**（≤ 2 次，常成功），非異常 —— 別因此直接降級主 LLM 自審（會丟失獨立 review）。完整處置（重試 / 降級 + 標記 fallback）見 agent-workflow skill「Auto Mode」（on-demand 載入）。

### spawn 失敗態辨識（處置相反，禁混用）

| 症狀 | 機制 | 處置 |
|------|------|------|
| 收 note、無 findings、無錯誤碼 | classifier 間歇 unavailable（服務端暫態） | 重試 spawn ≤2 次（上段正解） |
| 錯誤碼 **1301**（content filter） | 內容審查攔截——prompt 用詞觸發 provider 端關鍵詞過濾；**同 prompt 重試必再撞** | **禁原 prompt 重試**——改寫用詞後再 spawn；仍撞 → 換任務表述或升 full 層 |
| 錯誤碼 **1308**（usage limit） | 額度窗口耗盡（錯誤內含重置時間戳；~2 秒即敗＝根本沒跑） | 等窗口重置再派（重置前重派無效）；中途陣亡 ≠ 沒跑——先查產物判進度；不用預先降級 |
| 錯誤碼 **1302**（spawn 即敗／agent 中途陣亡） | 帳號級暫態（rate limit／spawn 通道）——**非模型專屬**（full 亦撞；晨間 full reviewer 連續兩案例） | 重試 spawn ≤2；仍撞 → **顯式降級記錄**（序列延後／in-harness 自做），禁靜默棄審 |
