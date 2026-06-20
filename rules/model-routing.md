# Model Routing（subagent 模型分派）

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

subagent model 依**任務類型**決定是否降級；降級目標 = 主 session model **降一級**。

- **降級（session-1）**：review / verify / research / explore / render agent — 讀/分析、產 findings，不需最強推理
- **inherit session**（不降級）：impl / test-gen agent — 寫 code/test，需強度

**降級映射**（主 session → 降一級）：opus→sonnet、sonnet→haiku、haiku→haiku（已最低）

> 例外：opus session（rate limit 1）的 impl agent 也降一級避 bottleneck（見 [agent-workflow](../skills/agent-workflow/SKILL.md) 並發表）。

## 套用（兩路徑都從本檔取 literal，不寫死絕對 model）

- **Workflow path**（ultracode）：script `agent({model})` 填「當前 session 降一級」literal（runtime deterministic、saved workflow 凍結）
- **Agent Tool path**（fallback）：spawn `model` param 同上

作者（Claude）依當前 session model 套降級映射、填入對的 literal。並發上限（rate-limit）見 agent-workflow 並發表，與本檔 model 分派正交。

## classifier 間歇 unavailable（harness 已知風險，與 model 分派正交）

GLM / 非 Claude harness 的 safety classifier 可能**間歇 unavailable**（spawn agent 收 note、無 findings，非主動阻擋）。這是已知服務端間歇故障，**重試 spawn 是正解**（≤ 2 次，常成功），非異常 —— 別因此直接降級主 LLM 自審（會丟失獨立 review）。完整處置（重試 / 降級 + 標記 fallback）見 [agent-workflow](../skills/agent-workflow/SKILL.md)「Auto Mode」。
