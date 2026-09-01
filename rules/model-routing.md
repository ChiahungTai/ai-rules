---
harness-scope: neutral
---

# Model Routing（角色 → tier → model 解析）

> **載入機制**: source 在 ai-rules repo `rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide bundle 載入

subagent 的 (model, effort) 由**角色需求**決定（與主 session 開什麼模型無關），經兩跳解析：

1. **角色 → tier**（通用表——本檔單一源）
2. **tier → (model, effort)**（依 harness × 當前 provider 查解析表——在 model-routing skill；ZCode 端材料化為 `agents/zcode/` 定義檔 frontmatter pins，pin 值以 model-routing skill 解析表為單一源）

## 角色 → tier

| 角色 | tier | 說明 |
|------|------|------|
| code-reviewer / code-reviewer-primed／review **command** agent | full（inherit） | 品質閘門需強度——carve-out：任何「review 順手降級」的直覺不適用 |
| impl / test-gen agent | full（inherit） | 寫 production code／等價測試設計 |
| spec-miner / lite-verify / render | lite | 機械查證（rg+Read+逐字引用）、清單驅動驗證、渲染——規則明確、read-only |
| mem-distill | lite（寫入型） | memory 條目蒸餾——規則明確的語義壓縮（清單內 Read→Write 全覆寫）；hook 不攔 subagent 寫入，上限＝prompt 紀律（registry `agents/zcode/`） |
| vision-review | vision | 多模視覺驗收（Read 本地圖；remote URL 先 Bash curl 落地再 Read。白名單 MCP 全名**僅對連線中 server 合法**——未連線全名才整顆拒絕 spawn〔d32ddb0 邊界定版〕；CR plugin per-session 連線故白名單可掛） |
| research / explore | 內建 Explore 承接（要釘模型時同 lite）；EP 段落 0 全域研究＝registry `cr-research`（ZCode：lite pin＋CR MCP 白名單） | — |

> tier 詞彙（full / lite / vision）單一源在此；agents/AGENTS.md 治理段與 agent 命名引用之，不自帶定義。

## 套用（三路徑都從解析表取值，不寫死絕對 model）

- **CC Workflow path**（ultracode）：script `agent({model})` 填 literal —— review command agent = inherit（full tier carve-out）；lite 類填 lite tier 對應值（查 skill 解析表）
- **CC Agent Tool path**（fallback）：spawn `model` param 同上
- **ZCode path**：pins 釘在 `agents/zcode/` 定義檔 frontmatter（治理見 agents/AGENTS.md registry 段）

spawn 前印出確認：`[Agent] model=<依角色 tier>, max=N, current=M`（max 查 skill 並發表——lite 層較寬）。

> tier→(model, effort) 解析表、thoughtLevel 但書（#339/#306）、rate limit 與並發上限表、classifier 間歇 unavailable 處置＋spawn 失敗三態辨識（classifier 重試／1301 內容攔改寫 prompt／1308 額度窗口）——見 model-routing skill（on-demand；觸發詞：並發上限、rate limit、thoughtLevel、classifier unavailable、1301、1308、spawn model）。
