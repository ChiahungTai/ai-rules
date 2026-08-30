---
harness-scope: neutral
---

# Model Routing（角色 → tier → model 解析）

> **載入機制**: source 在 ai-rules repo `rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide bundle 載入

subagent 的 (model, effort) 由**角色需求**決定（與主 session 開什麼模型無關），經兩跳解析：

1. **角色 → tier**（通用表——本檔單一源）
2. **tier → (model, effort)**（依 harness × 當前 provider 查解析表；ZCode 端材料化為 `agents/zcode/` 定義檔 frontmatter pins，pin 值以本檔為單一源）

## 角色 → tier

| 角色 | tier | 說明 |
|------|------|------|
| code-reviewer / code-reviewer-primed／review **command** agent | full（inherit） | 品質閘門需強度——carve-out：任何「review 順手降級」的直覺不適用 |
| impl / test-gen agent | full（inherit） | 寫 production code／等價測試設計 |
| spec-miner / lite-verify / render | lite | 機械查證（rg+Read+逐字引用）、清單驅動驗證、渲染——規則明確、read-only |
| vision-review | vision | 多模視覺驗收（Read 本地圖；remote URL 先 Bash curl 落地再 Read。白名單 MCP 全名**僅對連線中 server 合法**——未連線全名才整顆拒絕 spawn〔d32ddb0 邊界定版〕；CR plugin per-session 連線故白名單可掛） |
| research / explore | 內建 Explore 承接（要釘模型時同 lite） | — |

> tier 詞彙（full / lite / vision）單一源在此；agents/AGENTS.md 治理段與 agent 命名引用之，不自帶定義。

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

> provider 帳號級事實，repo 無法驗證；改限額時**只改本表**（agent-workflow 引用此，不自帶數字，避免 provider 改限額時兩處 drift）。數字可能滯後 — 以 provider dashboard 為準。

## 套用（三路徑都從本檔取值，不寫死絕對 model）

- **CC Workflow path**（ultracode）：script `agent({model})` 填 literal —— review command agent = inherit（full tier carve-out）；lite 類 = `haiku`（＋`effort: high`）
- **CC Agent Tool path**（fallback）：spawn `model` param 同上
- **ZCode path**：pins 釘在 `agents/zcode/` 定義檔 frontmatter（值以本檔解析表為單一源——改表 → `rg` 同步 pins，治理見 agents/AGENTS.md registry 段）

spawn 前印出確認：`[Agent] model=<依角色 tier>, max=N, current=M`（max 按該 agent 所在 tier 查上表——lite 層並發上限較寬）。

## classifier 間歇 unavailable（harness 已知風險，與 model 分派正交）

GLM / 非 Claude harness 的 safety classifier 可能**間歇 unavailable**（spawn agent 收 note、無 findings，非主動阻擋）。這是已知服務端間歇故障，**重試 spawn 是正解**（≤ 2 次，常成功），非異常 —— 別因此直接降級主 LLM 自審（會丟失獨立 review）。完整處置（重試 / 降級 + 標記 fallback）見 agent-workflow skill「Auto Mode」（on-demand 載入）。
