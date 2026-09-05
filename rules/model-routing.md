---
harness-scope: neutral
---

# Model Routing（角色 → tier → model 解析）

> **載入機制**: source 在 ai-rules repo `rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide bundle 載入

subagent 的 (model, effort) 由**角色需求**決定（與主 session 開什麼模型無關），經兩跳解析：

1. **角色 → tier**（通用表——本檔單一源；tier 詞＝requirement 正式 token：full＝旗艦需求／vision＝影像需求／lite＝隨意需求，中文語義標籤，與 skill 權威表對齊行同詞彙）
2. **tier → (model, effort)**（依 harness × 當前 provider 查解析表——在 model-routing skill 的 tier×provider 權威表，model 值唯一源；ZCode 端材料化為 `agents/zcode/` 定義檔 frontmatter pins〔部署預設，由 sync_agents 生成〕，pin 值以該表為單一源）

> **tier 是能力檔語義，非模型綁定**——哪個具體模型夠格坐哪個 tier，單一源在 skill 解析表（provider 演進只改該表）；本檔只錄角色需要的能力檔與升降級條件（分工律證據與條款見 skill「flash 分工律」）。

## 角色 → tier

| 角色 | tier | 說明 |
|------|------|------|
| code-reviewer / code-reviewer-primed／review **command** agent | full（inherit）為基準；**條件式降 lite** | 品質閘門需強度。降級條件＝**保護面厚度**（既有測試釘住＋驗證閉環＋非跨邊界語義面）；條件不滿足時「review 順手降級」直覺不適用 |
| impl / test-gen agent | full（inherit）為基準；機械段條件式降 lite（條件同 review） | 寫 production code／等價測試設計；降級附加約束＝lite 模型測試僅規格陳述非驗收證據（mock 假設即 bug），驗收證據另補 |
| judge 裁決（judge-review）／EP 規劃（execution-plan）／post-build 編排 | **full 能力檔（不可條件降級）** | 判斷密集位——judge 自證塌陷＋sycophancy 是能力剖面問題非努力不足；lite＋max effort 補償＝未驗證路徑（採用前先小規模實證，紀錄回 skill） |
| spec-miner / lite-verify / cross-verify-investigator / render／cron 機械段（automation session 選 lite 模型） | lite | 機械查證（rg+Read+逐字引用）、清單驅動驗證、單軸多源查證（軸＝prompt 參數；源缺場回報 unverified 不腦補）、渲染、排程收斂/watch——規則明確、read-only |
| mem-distill | lite（寫入型） | memory 條目蒸餾——規則明確的語義壓縮（清單內 Read→Write 全覆寫）；hook 不攔 subagent 寫入，上限＝prompt 紀律（registry `agents/zcode/`） |
| vision-review | vision | 多模視覺驗收（Read 本地圖；remote URL 先 Bash curl 落地再 Read。白名單 MCP 全名**僅對連線中 server 合法**——未連線全名才整顆拒絕 spawn〔d32ddb0 邊界定版〕；CR plugin per-session 連線故白名單可掛） |
| research / explore | 內建 Explore 承接（要釘模型時同 lite）；EP 段落 0 全域研究＝registry `cr-research`（ZCode：lite pin＋CR MCP 白名單） | — |

> tier 詞彙（full / lite / vision）與 family／profile 詞彙（GLM／muse／codex；implement／review／advisory 等）單一源在此；agents/AGENTS.md 治理段、工單模板與 agent 命名引用之，不自帶定義。

## external-runtime routing（family 軸）

> **定位**：external-runtime routing policy（family 軸），非 tier→model 映射擴充、非 registry pin。

角色→family→profile 映射、eligibility gate 五條、reviewer 交接契約、bridge 必經（muse 委派唯一入口）、完成回報收法（push 化決策樹）、套用（三路徑）——見 model-routing skill（`skills/model-routing/SKILL.md` on-demand；觸發詞：external-runtime、eligibility、reviewer 交接、bridge 必經、委派、收法）。

> tier→(model, effort) 解析表、flash 分工律（執行層降級條件＋風險面＋歸因紀律）、external-runtime family 解析表、thoughtLevel 但書、rate limit 與並發上限表、classifier 處置＋spawn 失敗態辨識——見 model-routing skill。
