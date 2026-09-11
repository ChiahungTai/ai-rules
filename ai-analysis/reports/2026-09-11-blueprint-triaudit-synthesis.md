# 藍圖三方大審查——歸納修正方向（codex×muse×GLM-5.3 兩輪）

> 形態：三方審查合成報告。範圍＝`bad4d67..HEAD`（09-10 04:29 起 68 commits，`git rev-list --count` 實測）＋working tree——兩天方向大調整全量。流程：三家獨立審查（r1：codex 12 條／muse 18 條／GLM 15 條）→互看輪（r2：交叉命中對照、分歧裁決、改判明說——GLM 2 條 🟡→🔴、muse 撤回 1 條自曝 2 錯、codex 2 條升降級）→本歸納。原始報告：`.agent-tmp/audit-{gpt,muse,glm}.md`＋`audit-r2-{gpt,muse,glm}.md`（7 天區——重要結論已收錄本檔）。

## 總診斷（三家總評一致）

**藍圖方向沒有走錯**——WT 過渡條款完備（3/3 正向交叉）、✅⚠️❌ 現況標記誠實（無一處把 target 偽裝 runtime）、特赦條件鏈相容、archify 退役方向正確。**最脆弱處是「決策速度 > materialization／ownership 收斂速度」**：兩天內大定案前進極快，但承載卡、live routing、consumer cutover、durable source pointer 沒有同速收斂——多數 finding 是同一失敗模式（decision→commitment→materialization 傳導鏈無機械化）的不同表面。控制面現呈「混世代」：新決策與舊 runtime 並存且無收斂點。

## 交叉命中（高置信——兩三家獨立證實）

| # | 問題 | 命中 | synthesis 最終定級 |
|---|---|---|---|
| X1 | 測試契約 v3.1 六檔落檔**無承載卡**（兩天最大定案零 delivery object；六線波次亦無槽） | 3/3 | 🔴 |
| X2 | cr-research 升 full 已裁決、**五處 live routing 仍 lite**（rule/skill×2/sync_agents/execution-plan；減量弧還把舊值重固化） | 3/3 | 🔴（主筆裁決；GPT🟡／Muse🔴／GLM🔴——severity 未全收斂，動作一致） |
| X3 | **殼 git 政策雙軌**：illustrate-html-mode 檔內矛盾（:67 全進版控 vs :68/:94/:99 渲染不進＋`git clean -Xf`）＋AIR-73 卡/synthesis 帶已被 AIR-74 推翻的 lossless-ignore 終案 | 2/3（GLM+codex 兩面合一族） | 🔴 |
| X4 | 殼 backlink 寫死 **:6420（mosaic board）**——ai-rules 是 :6422；規範源→template→兩 flagship 殼→全 repo 10 html 全錯鏈 | 2/3 | 🟡（09-11 退役改取消，修正鏈 superseded——見 §④） |
| X5 | blueprint 真相源映射指 **`.agent-tmp/`**（7 天清理區）——illupatch-synthesis 同時是 AIR-73 acceptance 考古源 | 2/3 | 🔴（主筆裁決；GPT🟡／Muse🟡／GLM🔴——severity 未全收斂，動作一致） |
| X6 | 對齊覆核 11 類觸發**無 finalization owner**（post-build 鏈無 blueprint realignment 步） | 2/3 | 🟡（優先級升） |
| X7 | AIR-71 前置 AIR-72 **只在 prose、`dependencies: []` 空** | 2/3 | 🟡 |
| X8 | AIR-72 desc ④列**已落地的 outward 特赦**（卡面 stale） | 3/3 | 🟡 |

**獨有但經複查成立**（單家抓到、另两家 r2 採納）：CDN 自包含違反（codex 🔴——殼 mermaid 走 jsdelivr，離線圖區全空白，違反「無外部 fetch」契約）；same-family oracle 前提裂縫（codex 🔴——muse 全棧形態下「EP↔實作跨家族」前提靜默失效）；mosaic 跨 repo 死鏈（`Github/Github` 雙層）；/commit 例外清單漂移（仍只列建卡/ruff 兩項）；fresh-machine runbook「新開一卡」裁決無卡；wave 三套語彙（wt-decision「現在遷 wave -1」vs 執行順序藍圖波次 1=AIR-58 vs AIR-72 卡名 wave-1）；human-summary 在 single-writer target 下無代寫者；test-gen 仍佔 model-routing 常設 full 行。

**分歧裁定亮點**：muse「review 須 committed revision」被 codex 否決（code-review 預設就是 uncommitted 審查——處方會破壞既有契約，僅保留 identity 補強）；KPI 18=4+7+7 逐行自洽（GLM 驗證通過、muse 自曝誤報）；archify「退役乾淨」🟢 被 GLM🔴A1 證偽——muse 撤回並留教訓：**退役驗收的 rg 只掃產線名不掃舊政策句＝詞彙零命中≠政策零殘留**。

## 修正方向（合併排序——六項）

### ① v3.1 materialization 卡【最高優先，工作量：大】
建「測試契約落檔」卡，scope 至少：六檔＋研究鏈（cr-research **五處一次原子切 full** 含 sync_agents 重生成＋test-gen 移出常設 full 行改 P0 註記）＋EP 加 same-family precondition（author family≠implement family，不成立強制 challenge 或明示 degraded）＋八站②⑤主表補 challenge 半句＋`skills/CLAUDE.md` 五命令索引同步＋`/commit` 例外清單改 pointer 委託＋seeded MVP。跨弧編輯面（AIR-67、bundle 減量 working tree）在卡內宣告。**止血項即刻做**：rules/model-routing.md 研究行加「（v3.1 已裁升 full，落檔隨卡）」一行，防新 EP 段落 0 繼續錯派。

### ② AIR-73 開工前重基＋殼政策統一【第二，工作量：中大】
清掉所有 AIR-74 前舊政策殘留：illustrate-html-mode :68/:94/:99 重寫（渲染全進版控、刪 `git clean -Xf` 重生情境、illustrate SKILL "Regenerate shells" 改 diagrams-only）；AIR-73 卡 desc 重基（synthesis 的 lossless-ignore 終案已過時——引用處改指 AIR-74 後新政策）；**acceptance 擴成 consumer cutover**（builder＋execution-plan hook1＋post-build hook2＋html-mode＋onboarding regeneration 同弧切換＋一條真 EP→hook1→hook2 E2E——否則 builder 綠燈＝false green）；workflow ② 站補「AIR-73 前 legacy 手填」括號。

### ③ CDN×自包含契約二選一裁決【第三，工作量：小～中】
要嘛 mermaid runtime 本地化/inline（自包含契約成立、離線可看），要嘛撤銷「無外部 fetch」宣稱（file: 直開依賴網路）——不能兩者並存。傾向本地化（契約是 viewport 架構的根基）。

### ④ 視覺/導航最後一公里【第四，工作量：小】
backlink 條關閉（09-11 board server 退役改走取消——6420→6422 修正鏈無需執行）＋mosaic 死鏈修路徑＋illupatch-synthesis **固化進 reports/**（AIR-73 開工前必做——acceptance 考古源）＋「四小項」兩批同名改單一 pending-materialization 表（逐項 owner／已落／未落）。

### ⑤ blueprint 治理機械化（治本）【第五，工作量：中】
post-build/metadata-sync 加輕量 **realignment trigger detector**（arc diff 命中 11 類 source 時要求 blueprint 對齊才結算）——11 觸發從「希望有人記得」變機械閘。本項解釋並預防本輪大量 mixed-generation drift 的共同根因。

### ⑥ 執行系卡面衛生【第六，工作量：小（多為一行級）】
AIR-71 `dependencies` 補 AIR-72；AIR-72 desc ④標「已由 4b1fd7b 落地，本卡驗 single-writer 相容」；wave 語彙消歧（明定 AIR-72 相對六線位置）；human-summary 代寫 owner 補進 control-plane transaction；fresh-machine runbook 裁決落實（補卡或正式取消）；觀察池路由補進 workflow viewport 節一小段。

## 建議執行順序

即刻（本 session 或下一條）：①止血行＋④小修鏈（死鏈/固化；backlink 已關閉見④）＋⑥卡面衛生——全是小改。
建卡開工：① v3.1 materialization（先於一切 wave）→ ② AIR-73 重基後才可開工。
裁決項（user）：③ CDN 二選一；fresh-machine 卡去留；wave 語彙定名。
