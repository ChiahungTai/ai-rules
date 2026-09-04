---
name: model-routing
description: Model routing 深層載體 — tier→(model,effort) 解析表（ZCode×GLM flash、CC×GLM haiku、CC×Anthropic）＋flash 分工律（執行層降級條件＝保護面厚度、判斷密集位 full 能力檔、模型歸因紀律）＋external-runtime family→(model,effort,容量) 解析表（muse／codex 委派、工單 profile）、rate limit 並發表、thoughtLevel 但書（sticky 不達 wire #339/#306）、classifier unavailable 處置（重試≤2）＋spawn 失敗態（1301／1308／1302）＋eligibility gate／reviewer 交接契約／套用三路徑。always-on 骨架在 rules/model-routing.md；spawn 前查並發與 eligibility 時載入。觸發詞：並發上限、rate limit、spawn model、tier、thoughtLevel、reasoningEffort、classifier unavailable、1301、1308、1302、flash、分工律、保護面、haiku、pins、external-runtime、委派、工單、eligibility、eligibility gate、reviewer 交接、advisory、bridge 必經。
---

# Model Routing — 解析表與 provider 事實

> 本 skill 是 `rules/model-routing.md` 的 on-demand 深層載體：rule 端保留 always-on 骨架（角色→tier 表、兩跳解析原則、tier 詞彙句、external-runtime routing 段頭＋pointer——內容在本檔）；本檔承載 tier→(model, effort) 解析表、external-runtime family→(model, effort, 容量) 解析表、eligibility gate、reviewer 交接契約、套用三路徑、rate limit 與並發上限表、thoughtLevel 但書與 classifier 處置。model id 與容量數字單一源在此（rule／registry／模板僅 family／profile 詞彙）。

## tier → (model, effort) 解析表

| tier | harness × provider | agent 定義填法 | 備註 |
|------|-------------------|---------------|------|
| lite | ZCode × GLM | `model: glm-5.3-flash`＋`thoughtLevel: high※` | flash＝5.3 世代輕量層（多模）；effort 配 high——max 耗時耗 token 增益有限 |
| lite | CC × GLM | spawn-time `model: haiku`（＋`effort: high`） | CC enum 是 tier 別名——GLM provider 的對應表直達 flash |
| lite | CC × Anthropic | `model: haiku`＋`effort: high` | 原生 haiku |
| lite | ccr 模式（未啟用） | `Fusion/lite` | direct-first 常態（ccr 會斷 ZCode usage 顯示）；啟用時 pins 只換值、角色/tier 不動 |
| full | 任何 | `model` 省略（inherit） | — |
| vision | ZCode × GLM | `model: glm-5.3-flash`＋`thoughtLevel: high※` | 原生多模已實戰驗證（逐字忠實度高＋像素取樣驗證行為；與 4.6V 對比大致平手——判斷面需更強時升 full） |

> ZCode 注意：`thoughtLevel` 綁具體 model（inherit 時不生效）；欄位名**不是** `reasoningEffort`——未知欄位靜默忽略。**※ thoughtLevel 但書**：sticky user reasoningLevel 在場時（user-scope `local_setting`），定義的 thoughtLevel **不達 wire**——telemetry `variant` 記 user 層級而非定義值（08-29 兩數據點：lite-verify＋vision-review 定義 `high` 皆記 `max`，sticky `max` 在場、主 session rows 同 max）。**model pin 不受影響**（frontmatter model 字串逐字到 wire——vision-review 首筆遙測實證）。sticky override 與 silent no-op 尚未分辨（flip 實驗待跑：改 user level≠定義值再 spawn 看 variant 是否跟隨）——對應**已知 open bug 家族**（zai-org/feedback #339「thought-level changes silently discarded after first selection」＋#306 reasoning effort injection 缺陷；EN/cn 文檔一致、用法無誤）。CC 注意：enum 別名（sonnet/haiku/opus）在 GLM provider 由 provider 別名表解析到對應 GLM 模型。

## flash 分工律（執行層降級條件）

> 09-04/05 夜 GLM-5.3-Flash 全切換的三軸鑑識（對話行為／git 產出／建議查證）定版；rule 端只錄 tier 語義與升降級條件，證據與細節在此。

**執行層可降 lite，條件＝保護面厚度**（三件全滿）：既有測試釘住（可重跑驗證）＋驗證閉環（機械閘門在場）＋非跨邊界語義面（單位換算／領域語義轉換不屬此段）。

- 實證（flash 可靠面）：lite-verify 10/10、cron 四段全交卷、reviewer 20/20 交卷（dual-context 兩側獨立交叉命中）且 10 findings 經 full 複驗全成立、findings 修正 10 分鐘落地、測試警告清理走顯式契約（僅 1 條窄域 filter）
- 已知風險面（降級時主動防）：跨單位語義換算錯＋靜默失效＋斷點汙染（西元↔民國 P0×2/P1）；測試合法化 bug（mock 假設即 bug——lite 模型測試僅規格陳述，驗收證據另補 full 複驗）；inferred findings（報「機制可能」非「實測確認」——judge 遇 inferred 必重跑實測，見 judge-review 三防線）；機械掃描漏變體（rg pattern 需含空格/等號形）；Edit 前未 Read 偏高（20 vs 3——spawn prompt 注入 Read 紀律）
- **判斷密集位不可降**：judge 裁決／EP 規劃／post-build 編排＝full 能力檔——judge 自證塌陷＋sycophancy（錯信心 finding＋順勢採納＝最危險組合）是能力剖面問題。**lite＋max effort 補償＝未驗證路徑**：欲採用先小規模實證（舊 findings 重裁對照 full 裁決），結果記回本節
- **歸因紀律**：模型歸因結論必須 per-message modelID 機械對帳（ZCode db.sqlite；unpinned subagent 跟 spawning session 模型走、registry pin 不受手動切換影響），不接受 session 自述——09-05 三例自述歸因錯（full 亦被 priming 帶偏）

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

> 兩種 review 邊界：external second-opinion review（跨家族獨立視角）與 in-harness acceptance reviewer（GLM 主審、把關工單結案）職責分離，前者補視角、後者定結論。容量不足的家族禁派大工單——現值見下表，rule 不寫數字與型號。重大架構／風控／會計 diff 的跨家族 review＝**軟提醒非硬閘**（額度現實：muse/codex 額度吃緊時派不動）——額度允許時至少一側跨家族；不足時顯式記錄降級（in-harness full 雙 context 承接），禁靜默略過。

### family → (model, effort, 容量現值)

| family | model | effort | 容量現值 | 備註 |
|--------|-------|--------|----------|------|
| muse | `muse-spark-1.3` | `xhigh`（user 09-04 定；純機械掃描 advisory 可降 `low`/`medium` 省 quota）；深推理可升 `ultra`（CLI alias → provider 最高級＝API `max`，限 1.3 Standard tier；reasoning tokens 佔 output 比例更大，留意輸出上限截斷） | 長 context（以 provider dashboard 為準） | 具視覺輸入 `--image`，跨家族備選；advisory／implement／review 共用此 family；bridge 端預設 pin 與本表對齊（muse-plugin-cc 弧維護），`--model`／`--effort` passthrough 僅供臨時 override |
| codex | `gpt-5.6-sol` | `high` | 約 200K（以 provider 為準，禁大工單；大 context 任務改派 muse） | ad-hoc 選項（想到再用、低頻）；context 小＋消耗快禁大工單（見上角色映射表）；companion `--model` 可傳（內建 `spark` 別名），不傳落 `~/.codex/config.toml` 預設（本機已 pin 同值） |
| GLM（in-harness） | 見 tier 表 | 見 tier 表 | 高（遠高於 200K 級，見 provider dashboard） | 沿用 tier→lite／vision 路由，不經 external-runtime 派發；in-harness acceptance reviewer 屬此 |

> 容量為「需現況查證」性質，隨 model 世代更新只改本表。

### eligibility gate（五條，逐條判）

> 任一不過 → 主 session 直做；「≥30 分鐘」僅提醒信號非機械判準。

1. **決策凍結**：工單目標、範圍與驗收已凍結，無待決設計選擇
2. **條款客觀化**：驗收條款為機械可判（命令＋預期結果），非主觀描述
3. **單一 writer 無待決**：單一 writer 可獨立完成，無需主 session 中途決策或協調多 writer
4. **主價值＝承接 implementation loop**：主價值在承接完整實作迴圈，而非零碎問答或探測
5. **環境可啟動**：目標 runtime 環境可啟動（bridge setup 綠、binary 在場），非環境阻塞

> sandbox-error 禁以 `--yolo` 賭重試（父層沙箱不可越權重試）；分類走 auth-failed／environment，修因後重派。

### reviewer 交接契約

- **完成回報固定欄位**：jobId 或 thread id／base commit／改檔清單／實跑驗收命令與原始輸出／未驗證項
- **reviewer 讀料順序**：work order → diff → evidence → writer report 最後讀
- **產出**：accept／reject／needs-fix 三態 verdict；無 reviewer record 不得結卡（record 落 EP 或工單指定位置）

### flag profile → spawn 參數（external-runtime）

> 本表為 flag 具體值單一源；`agents/AGENTS.md` 的 flag profile 表只寫形態並引用此處。bridge 未暴露的 flag 以工單紅線承載（見 `skills/_common/work-order.md`），暴露後改 flag；roadmap 記錄在 muse-plugin-cc 側。

| profile | family | spawn 參數 | 說明 |
|---------|--------|------------|------|
| advisory | muse | `muse task --disable-write`（bridge 暴露前由工單紅線承載） | read-only 掃描（SM-2）；effort 取上表 muse 列 |
| implement | muse | `muse task --trust-workspace` | 背景跑（見 rules/tool-discipline） |
| implement | codex | `codex task --write`（workspace-write） | 診斷／救援寫入型 |
| review | muse | `muse review --schema verdict`（bridge `review` 子命令） | 產出 accept／reject／needs-fix |
| review | codex | `codex --output-schema <verdict>` | 同上，codex 形態 |

**bridge 必經（muse 委派唯一入口）**：委派 muse 跑 repo 任務一律經 bridge 入口（上表 muse 列＝`muse-bridge.mjs` 子命令的抽象形態），禁直呼 `muse exec` 或其他繞過 bridge 的入口——bridge 落 per-repo `.muse-bridge/jobs.json` ledger（jobId／sessionId／status／text），非 bridge 入口的 muse 產出 ledger 查無，事後只能從副作用側考古（真實案例：mosaic post-build 鏈同鏈兩段 muse 委派一走 bridge 一繞道，繞道段收尾不可考）。完成回報攜帶 ledger jobId（reviewer 交接契約欄位）；委派了 muse 而 jobId 缺席＝入口違規，補查或標明。

> 工單模板見 `skills/_common/work-order.md`（foreign runtime 共用；prompt 為任務本文，禁含委派語言）。

### 套用（三路徑都從解析表取值，不寫死絕對 model）

- **CC Workflow path**（ultracode）：script `agent({model})` 填 literal —— review command agent = inherit（full 為基準；保護面厚度條件成立時降 lite）；lite 類填 lite tier 對應值（查本檔解析表）
- **CC Agent Tool path**（fallback）：spawn `model` param 同上
- **ZCode path**：pins 釘在 `agents/zcode/` 定義檔 frontmatter（治理見 agents/AGENTS.md registry 段）

spawn 前印出確認：`[Agent] model=<依角色 tier>, max=N, current=M`（max 查本檔並發表——lite 層較寬）。

## rate limit 與並發上限（model facts 單一源 — 以 provider 現況為準，可能滯後）

| 模型 | rate limit | 並發上限 |
|------|-----------|---------|
| haiku / sonnet / opus | 10 | **3** |
| flash（glm-5.3-flash，lite／vision 層） | — | **高**（遠高於上列；具體數字以 provider dashboard 為準） |

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
