---
name: model-routing
description: Model routing 深層載體 — tier→(model, effort) 解析表（ZCode×GLM flash＋thoughtLevel、CC×GLM haiku 別名、CC×Anthropic）、rate limit 與並發上限表（haiku/sonnet/opus 並發 3、flash 高）、thoughtLevel 但書（sticky user reasoningLevel 不達 wire、zai-org/feedback #339/#306 已知 bug 家族）、classifier 間歇 unavailable 處置（重試 ≤2 次）。always-on 骨架（角色→tier 表、兩跳解析原則、套用路徑）在 rules/model-routing.md；spawn agent 前查並發上限、維護 zcode/ pins、診斷 thoughtLevel 行為時載入。觸發詞：並發上限、rate limit、spawn model、tier 解析、thoughtLevel、reasoningEffort、classifier unavailable、flash、haiku、pins。
---

# Model Routing — 解析表與 provider 事實

> 本 skill 是 `rules/model-routing.md` 的 on-demand 深層載體：rule 端保留 always-on 骨架（角色→tier 表、兩跳解析原則、套用路徑）；本檔承載 tier→(model, effort) 解析表、rate limit 與並發上限表、thoughtLevel 但書與 classifier 處置。

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

## rate limit 與並發上限（model facts 單一源 — 以 provider 現況為準，可能滯後）

| 模型 | rate limit | 並發上限 |
|------|-----------|---------|
| haiku / sonnet / opus | 10 | **3** |
| flash（glm-5.3-flash，lite／vision 層） | — | **高**（遠高於上列；具體數字以 provider dashboard 為準） |

> provider 帳號級事實，repo 無法驗證；改限額時**只改本表**（agent-workflow 等引用此，不自帶數字，避免 provider 改限額時兩處 drift）。數字可能滯後 — 以 provider dashboard 為準。

## classifier 間歇 unavailable（harness 已知風險，與 model 分派正交）

GLM / 非 Claude harness 的 safety classifier 可能**間歇 unavailable**（spawn agent 收 note、無 findings，非主動阻擋）。這是已知服務端間歇故障，**重試 spawn 是正解**（≤ 2 次，常成功），非異常 —— 別因此直接降級主 LLM 自審（會丟失獨立 review）。完整處置（重試 / 降級 + 標記 fallback）見 agent-workflow skill「Auto Mode」（on-demand 載入）。
