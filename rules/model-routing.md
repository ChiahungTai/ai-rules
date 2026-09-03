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

> tier 詞彙（full / lite / vision）與 family／profile 詞彙（GLM／muse／codex；implement／review／advisory 等）單一源在此；agents/AGENTS.md 治理段、工單模板與 agent 命名引用之，不自帶定義。

## external-runtime routing（family 軸）

> **定位**：external-runtime routing policy（family 軸），非 tier→model 映射擴充、非 registry pin。family／profile 詞彙單一源見本檔 tier 詞彙句，agents/AGENTS.md 與工單模板引用之。工單模板見 `skills/_common/work-order.md`。

### family 表（角色 → family → profile → 備註）

| 角色 | family | profile | 備註 |
|------|--------|---------|------|
| 實作（implementation） | muse | implement | 主力 implementation loop 承接 |
| external second-opinion review | muse | review | 獨立第二意見，與 in-harness 驗收審查職責分離（見下） |
| in-harness acceptance reviewer | GLM | — | 驗收委派工單的主審（Writer/Reviewer 分離的 in-harness 側） |
| 診斷 rescue | codex | implement | 環境診斷與救援 |
| advisory 掃描 | muse | advisory | 唯讀掃描、盤點 |
| 機械驗證／探索 | GLM | lite | 機械查證、探索（沿用 tier→lite 路由） |
| 視覺驗收 | GLM | vision | 預設路由；muse 具視覺能力為跨家族備選 |

> 兩種 review 邊界：external second-opinion review（跨家族獨立視角）與 in-harness acceptance reviewer（GLM 主審、把關工單結案）職責分離，前者補視角、後者定結論。容量不足的家族禁派大工單——現值見解析表（`skills/model-routing/SKILL.md`），rule 不寫數字與型號。

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

## 套用（三路徑都從解析表取值，不寫死絕對 model）

- **CC Workflow path**（ultracode）：script `agent({model})` 填 literal —— review command agent = inherit（full tier carve-out）；lite 類填 lite tier 對應值（查 skill 解析表）
- **CC Agent Tool path**（fallback）：spawn `model` param 同上
- **ZCode path**：pins 釘在 `agents/zcode/` 定義檔 frontmatter（治理見 agents/AGENTS.md registry 段）

spawn 前印出確認：`[Agent] model=<依角色 tier>, max=N, current=M`（max 查 skill 並發表——lite 層較寬）。

> tier→(model, effort) 解析表、external-runtime family 解析表、thoughtLevel 但書（#339/#306）、rate limit 與並發上限表、classifier 間歇 unavailable 處置＋spawn 失敗三態辨識（classifier 重試／1301 內容攔改寫 prompt／1308 額度窗口）——見 model-routing skill（on-demand；觸發詞：並發上限、rate limit、thoughtLevel、classifier unavailable、1301、1308、spawn model、external-runtime）。
