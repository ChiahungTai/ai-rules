---
harness-scope: neutral
---

# Model Routing（角色 → tier → model 解析）

subagent 的 model/effort 由角色需求決定，不依主 session 模型。兩跳：本檔角色→tier，再依 harness×provider 查 **model-routing skill** tier×provider 權威表（model 值唯一源；ZCode 由 sync_agents 材料化部署 pins）。

tier＝requirement 能力檔，非模型綁定：full＝旗艦、vision＝影像、lite＝一般。旗艦五項資格、坐位註記、升降級與歸因細則見該 skill。

## 角色 → tier

| 角色 | tier 與約束 |
|---|---|
| code-reviewer / code-reviewer-primed / review command agent | lite 預設（user 09-09——審查 findings 生產層跨層品質已實證，判斷價值集中 judge 裁決層）；高保護面／跨邊界語義面才升 full，禁順手升級 |
| impl / test-gen | full 基準，機械段依同條件降 lite；lite test 僅規格陳述，不是獨立驗收證據，須另補 |
| judge-review / execution-plan / post-build 編排 | full，不可條件降級；判斷/自證塌陷/sycophancy 非 effort 可補，lite＋max 須另先小規模實證並記 skill |
| spec-miner / lite-verify / cross-verify-investigator / render / cron 機械段 | lite，rg＋Read 逐字查證/清單驗證/單軸多源/渲染/watch；read-only、缺源標 unverified 不腦補 |
| mem-distill | lite 寫入型，清單內 Read→Write 蒸餾；hook 不攔 subagent，靠 prompt 範圍紀律 |
| vision-review | vision；Read 本地圖，remote 先 curl 落地；MCP 白名單只可列已連線 server，未連線全名會拒絕 spawn，CR per-session 連線可掛 |
| research / explore | 內建 Explore 繼承主模型；釘 lite 可選非必要。EP 段落 0 全域研究用 registry cr-research（ZCode lite＋CR 白名單） |
| harness 內建 general-purpose / Explore | 無 pin、繼承主模型（ZCode 設定可釘、清空恢復）。機械/lite 工作須派對應 registry，禁誤以內建預設便宜 |

review/impl 的 ZCode registry 與 CC opus 別名釘選依 skill 解析表；不可在此另維護 model 值。

## external-runtime routing（family 軸）

family＝GLM/muse/codex；profile＝implement/review/advisory。tier、family、profile 詞彙由本檔定義，agents 治理與工單引用，不重定義。外部 runtime 委派＝caller 背景 Bash 直呼 bridge，禁 subagent wrapper 承載；需接續的 background job 必掛 wait <jobId>。

委派、收法、定向接續/fork 時載入 **model-routing skill**（角色→family→profile、eligibility、reviewer 交接契約、bridge 必經 `task --family muse|codex`、resume/fork 守衛；rate limit/classifier 失敗態/lite 分工律等亦同）。external-runtime policy 不擴充 tier 表或 registry pin。工單禁止再委派時遵守工單，不能因載入 routing 而自行 spawn。
