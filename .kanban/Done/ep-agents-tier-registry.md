# [tag:agents] EP 追蹤：agents tier registry 與兩跳 model 解析

## 目標
agents/ registry split（shared/zcode/claude）＋ model-routing 兩跳改寫＋三顆 tier-pinned agent。

## 結算
- EP：`ai-analysis/execution-plans/_done/ep-agents-tier-registry.md`（docs mode、S1-S4 全段完成＋post-build gate 閉環）
- S1 model-routing 兩跳改寫＋13 處引用同步（殘留掃描零命中）
- S2 registry split＋頂層翻轉＋AGENTS.md 治理段（原 4 symlink 農場→08-29 午證偽修正為實檔拷貝＋cmp 同步紀律）
- S3 lite-verify／spec-miner／vision-review 三顆（glm-5.3-flash＋thoughtLevel: high）
- S4 deploy 3/3（17 neutral、bundle 94% gate）＋kanban 建卡
- ✅ 開箱驗證（2026-08-29 新 session）：ZCode spawn smoke 3/3 附證據（lite-verify 正常完成無 pin 報錯；telemetry `model_id=glm-5.3-flash`＋`agent=zcode-lite-verify`）＋CC 端清單確認（`~/.claude/agents`→`agents/claude`，僅 shared 兩顆、零 zcode 專屬檔）
- ✅ symlink 證偽修正驗證（08-29 午）：registry 改實檔拷貝後 CR session spawn code-reviewer PASS（四臂實驗閉環）＋hub telemetry 複核；**殘留＝CC 臂 spawn 未 runtime 驗證**（relay 待跑：CC session 重啟後 spawn code-reviewer）
- ✅ 實戰驗證（08-29 午後 mosaic session，lite-verify 代跑）：flash 視覺過關——6533 七 panel 標題逐字（含 `PS12>60` 寫死 quirk＝真讀像素證據）、處置股 TA 圖（收斂/多頭拉回真實案例）6 SMA 標籤+顏色全對、像素取樣 RGB 與生成碼逐 byte 一致；vs 4.6V（`mcp__4_5v_mcp__analyze_image`）互有勝負：flash 蠟燭色規約兩圖皆對（4.6V 一圖答反自相矛盾）、4.6V 型態絕對標籤 2/2 較乾淨。⚠️ 附帶發現：vision-review tools 白名單含 MCP 工具時，parent session 啟動快照缺該工具即整顆拒 spawn（`Required MCP tool is not available in the parent startup snapshot`，定義啟動時快取、session 內改白名單實測無效）→ **修法建議：白名單拔 MCP 工具**（flash 原生多模；遠端圖 Bash curl→Read 可達），新 session 復跑 vision-review 本體驗證；品質弱點紀錄：小蠟燭目視色向、fontsize 6 密集刻度末端易誤讀
- ✅ 修法閉環（08-29 下午 d32ddb0 後新 session 復跑）：vision-review 本體 spawn 成功（metadata profileSnapshot 驗 `tools:[Read,Bash]` 新定義直達）、兩張 TA 圖**全部對上**——標題逐字（全形括號/破折號/波浪號）、6 SMA 標籤＋色映射全對、紅漲綠跌、型態雙對（1236 收斂/1529 多頭拉回）、處置虛線 ~78%＋註記日期對；真讀鐵證＝x 軸 13 刻度逐個讀出與生成碼 `step=115//12` 機械一致、個別蠟燭開收誠實標「無法辨識」；**人設紀律生效**：全程僅 2 tool call（兩次 Read）零腳本，對比 lite-verify 人設跑視覺寫像素掃描卡死（人設差異實證）。flash vs 4.6V 對決定案：型態 2/2 平手、色向 flash 2/2 勝（4.6V 1236 答反跨圖矛盾）→ 弧線建議**通過（附但書）**。telemetry 首筆 `zcode-vision-review`：`model_id=glm-5.3-flash`（frontmatter 原字串直達 wire；對比主 session 解析後 `GLM-5.3`）＋**variant=max 第二數據點**（定義 `thoughtLevel: high` 仍記 max，與 lite-verify 上輪一致）——相關性查明：`local_setting` user-scope sticky `model/reasoningLevel={"level":"max"}` 在場、主 session rows 同 max → 判讀＝sticky user 設定蓋過定義 thoughtLevel（與主 session config→local_setting 同 precedence 鏈）**或** silent no-op，flip 實驗（暫改 user reasoningLevel≠max 再 spawn 看 variant 是否跟隨）未跑無法分辨。**反饋待固化（ai-rules session）**：`rules/model-routing.md:37`「thoughtLevel 綁具體 model 即生效」宣稱補但書——「sticky user reasoningLevel 在場時定義 thoughtLevel 不達 wire（08-29 兩數據點）；model pin 不受影響（model_id 逐字到 wire）」，tier 表 L30/L35 的 `＋thoughtLevel: high` 註記同款但書
- ✅ 反饋已固化（08-29 傍晚）：model-routing ※但書落地（ZCode 注意段＋L30/L35 兩 cell 標※）＋bundle 重部署。**flip 實驗裁定＝排，併入下個新 session 驗證批**（與 cr-query 改名卡的 SM-4 清單檢查同批；協議：user 暫改 reasoningLevel≠max（如 medium）→ spawn lite-verify 小任務 → telemetry variant：跟隨 user＝sticky override、仍 high＝field 生效、仍 max＝第三形態）；實務含義先落地＝user 跑 max 時 lite agents 實際吃 max（社群警告的浪費面真實存在）——在 flip 分辨前，省 token 對策靠 user 層不靠定義層
