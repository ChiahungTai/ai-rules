# Model Routing（subagent 模型分派）

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

subagent model 依**任務類型**決定是否降級；降級目標 = 主 session model **降一級**。

- **降級（session-1）**：verify / research / explore / render agent（查證 / 分析 / 偵測，非 review command）— 讀/分析、產 findings，不需最強推理
- **inherit session**（不降級）：impl / test-gen agent + **review command agent**（ep-review / code-review / audit-test / execution-plan EP Review / build Agent Review — 品質閘門需強度）— 寫 code/test、做品質審查

> **carve-out**：review **command** agent 預設 inherit（覆蓋早期「review→降級」通用規則 —— review command 是品質閘門需強度）；其他 review-ish agent（verify / research / explore）維持降級。完整 review 執行預設見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」。

**降級映射**（主 session → 降一級）：opus→sonnet、sonnet→haiku、haiku→haiku（已最低）

## rate limit 與並發上限（model facts 單一源 — 以 provider 現況為準，可能滯後）

| 模型 | rate limit | 並發上限 |
|------|-----------|---------|
| haiku / sonnet / opus | 10 | **3** |

> provider 帳號級事實，repo 無法驗證；改限額時**只改本表**（agent-workflow 引用此，不自帶數字，避免 provider 改限額時兩處 drift）。數字可能滯後 — 以 provider dashboard 為準。

## 套用（兩路徑都從本檔取 literal，不寫死絕對 model）

- **Workflow path**（ultracode）：script `agent({model})` 填 literal —— **review command agent = 主 session（inherit，見上方 carve-out）**；非 review command agent（explore / research / verify）= 當前 session 降一級（runtime deterministic、saved workflow 凍結）
- **Agent Tool path**（fallback）：spawn `model` param 同上（review command inherit / 非 review 降一級）

作者（Claude）依當前 session model + 任務類型（review command vs 其他）套映射、填入對的 literal。並發上限查本檔上表（單一源）。

## classifier 間歇 unavailable（harness 已知風險，與 model 分派正交）

GLM / 非 Claude harness 的 safety classifier 可能**間歇 unavailable**（spawn agent 收 note、無 findings，非主動阻擋）。這是已知服務端間歇故障，**重試 spawn 是正解**（≤ 2 次，常成功），非異常 —— 別因此直接降級主 LLM 自審（會丟失獨立 review）。完整處置（重試 / 降級 + 標記 fallback）見 [agent-workflow](../skills/agent-workflow/SKILL.md)「Auto Mode」。
