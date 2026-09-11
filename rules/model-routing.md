---
harness-scope: neutral
---

# Model Routing（角色 → tier → model 解析）

subagent 的 model/effort 由角色需求決定，不依主 session 模型。兩跳：本檔 role→tier，再查 **model-routing skill** 的 harness×provider 權威表；model 值只在 skill，ZCode pins 由 sync_agents 材料化。

tier 是 requirement 能力檔：full＝旗艦、vision＝影像、lite＝一般；旗艦資格、升降級、坐位與歸因見 skill。

## 角色 → tier

| 角色 | tier 與約束 |
|---|---|
| code-reviewer / primed / review command agent | lite 預設（user 拍板：findings 生產層已實證；判斷集中 judge）；僅高保護面/跨邊界語義升 full，禁順手升級 |
| impl / test-gen | full 基準；機械段依 skill 條件降 lite。lite test 只算規格陳述，須另補獨立驗收 |
| judge-review / execution-plan / post-build 編排 | full，不可條件降級；自證塌陷/sycophancy 非 effort 可補，lite＋max 全面採用前先小規模對照 full 實證（一次性事前驗證，不作逐任務降級理由） |
| spec-miner / lite-verify / cross-verify-investigator / render / cron 機械段 | lite；read-only 查證，缺源標 unverified、不腦補 |
| mem-distill | lite 寫入型；只在 prompt 清單內 Read→Write；hook 不攔 subagent，靠 prompt 守範圍 |
| vision-review | vision；本地 Read、remote 先落地；MCP 白名單只列已連線 server，CR per-session 可掛 |
| research / explore | 內建 Explore 繼承主模型，釘 lite 可選非必要；全域研究用 registry cr-research（**v3.1 已裁升 full**，落檔隨 AIR-76）＋CR 白名單 |
| harness 內建 general-purpose / Explore | 無 pin、繼承主模型；機械/lite 工作派對應 registry，禁假設內建預設便宜 |

review/impl 的 ZCode registry 與 CC 別名釘選依 skill 解析表；本 rule 不維護 model 值。

## external-runtime routing（family 軸）

family＝GLM/muse/codex；profile＝implement/review/advisory。tier/family/profile 詞彙由本檔定義，其他載體只引用。外部 runtime 由 caller 背景 Bash 直呼 bridge，禁 subagent wrapper；需接續的 background job 必掛 `wait <jobId>`。

codex `chatgpt-web` 池（webgpt）專責 review／規劃，禁大型實作／大 payload 單發——單則訊息上限遠小於窗口，超限單發 turn-0 即死（4 筆 ledger 實證見 skill webgpt 專節）；**僅段落級評估確認可完成才派**（派發前提，非例外條款）。額度池分帳（`wham/usage` 看不見 web 池）與五類固定失敗態的處置見 skill。

委派、收法、定向接續/fork 時必載 **model-routing skill**：role→family→profile、eligibility、reviewer handoff、bridge 必經 `task --family muse|codex`、resume/fork、rate limit/classifier failure 與 lite 分工都在其中。external-runtime policy 不擴充 tier/pin；工單禁再委派時不得因載入 routing 自行 spawn。
