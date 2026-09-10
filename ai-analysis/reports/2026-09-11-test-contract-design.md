# 測試契約×驗證分工——裁決記錄（v3.1：契約層＋判讀邊界獨立＋provenance 三栓）

> 形態：正式裁決記錄（architecture decision record）。參與：主 session（GLM-5.3）＋muse（xhigh）＋codex（chatgpt-web/high）**三輪**遞迴諮詢（每輪 user 挑戰→修訂→兩家 session resume 複驗）。bridge jobs：`mtw29l54/mtw29l7v`（r1）→`mtw2l446/mtw2l46l`（r2）→`mtw3fpc1/mtw3fpea`（r3）。諮詢 prompt 全文：`.agent-tmp/test-*-consult.md`（7 天區，結論以本檔為準）。人類 viewport：`ai-analysis/test-contract/index.html`（已進版控）。

## 1. 問題起源

user 提案：workflow 支援「不同家族寫實作 vs 寫測試」的分離模式，或在 EP 先加測試規劃段落。動機＝acceptance-evidence 核心焦慮：「AI 同寫 test＋impl 共享理解，綠燈只證明自洽」。

## 2. user 三輪挑戰（每輪重構設計）

1. **「我其實只要有路徑就可以看了」**（另弧，見 viewport report）——本弧的 r1 收斂：契約先、分離後。
2. **r2 挑戰**：測試規劃是 top-level 段落放實作段落**前面**（文件順序＝時間順序）＋implement 流程拆段換 model 的路由設計。
3. **r3 兩刀**：
   - **刀一**：TC 在 EP 凍結後，EP 作者（GLM）↔ 實作者（Muse）**本來就跨家族**——oracle 獨立性已在 EP 層兌現；第三家族寫 RED 塌縮成「把 assert 公式搬進 pytest」（codex 自己 r1 的零增量邏輯對任何翻譯者成立）。
   - **刀二**：「先審 test」若只審「忠實翻譯 TC」是機械軸；review 層該做**架構面**——這次 diff 的整體測試邏輯作為系統守不守得住。

## 3. v3.1 終態（兩家 r3 同向同意＋六處必改後定案）

**設計原則（codex r3 定調）**：Family separation 放在 **judgment boundary**，不放在 every authorship boundary——獨立性買在「審規格」（challenge）與「審結構」（review），不買在「把 oracle 抄成 pytest」。

```
EP（GLM full）：凍結 TC ——oracle 層獨立（在實作段落前面）
  ↓ 高風險/P0：pre-RED challenge（跨家族 advisory·fresh·blind derive→reveal＋completeness）
  ↓ oracle 錯→judge/人類→EP amendment（實作前最便宜）
實作家族（單一 model·context 連續）：照凍結 TC 寫 RED
  ↓ RED 三 gate 當場驗：STRUCT_OK／SEM_OK／BEFORE_GREEN＋contract-test digest 凍結
  ↓ GREEN（frozen contract test 唯讀）→ REFACTOR
  ↓ 撞牆→mutation authority gate（想改哪側 truth→有沒有 authority；TC oracle→停 GREEN→amendment）
audit-test（軸A 機械）：predicate 對帳／mock↔evidence class／oracle 圓形依賴／
  RED receipt＋digest／基線跑法／fixture provenance／路徑覆蓋反查
code-review（軸B 架構面·跨 session dual-context）：拓撲 vs blast radius／層級平衡／
  符號≠路徑／evidence fidelity／shared dependency／耦合面（翻譯忠實度不歸它）
judge-review＋修正迴圈（現行）
```

**RED provenance 三栓**（r3 共識核心——v3 用 cache 友善換了污染，三栓是補償）：① RED receipt（TC-ID＋baseline 身份＋test digest＋failing predicate，**落檔存證非中途 commit**）；② gate 過後 contract-test digest 凍結（GREEN 不得靜默改 frozen test）；③ 基線跑法（新測試在 pre-change baseline 上必須紅——在 baseline 綠＝vacuous/test-after 劇場化，直接退回）。

**第三家族寫手＝P0 最後手段**（非高風險預設）：啟用條件預寫死——MVP 證明 challenge＋review 擋不住 fixture fidelity 級穿透才啟用。

**amendment 語義**：EP 可改、TC baseline 凍結；改 TC 走 amendment（old/new oracle＋reason＋independent evidence＋authority）。authority 四分：invariant/reference truth 可證偽→judge；新 integration evidence→judge；**user intent／product policy→人類**；來源矛盾→人類。「實作現況」永遠不是改契約的證據。deviation log（前線提案）與 amendment（判決）兩份分離。

## 4. 附帶裁決：研究層升級（同弧）

user 裁定：**探索/研究不派 flash**——EP 段落 0 全域研究（可複用盤點＋**風險假設識別**）是判斷密集位；淺研究「自信但薄」→EP 重造既有/漏致命假設，研究省的 token 遠小於錯 EP 的重工。`cr-research` 升 **full**（機械子腿——逐字引用、CR 查詢執行——仍可 flash 承接，但作為 full 研究者的下游查詢）。編輯鏈：roles authoring→sync_agents 重新生成→model-routing 兩處表→execution-plan 段落 0 措辭。

## 5. 修改面（六檔＋研究鏈——建卡走 execution-plan）

| # | 檔 | 動什麼 |
|---|---|---|
| 1 | execution-plan | top-level 測試規劃段（TC 格式含 predicate-ID 拆分／凍結語義／amendment 附錄 authority 四分）＋§4 退化自足抄本；**段落 0 研究措辭升 full** |
| 2 | implement | RED receipt＋三 gate 當場驗＋digest 凍結（兩行——防劇場化唯一排序栓） |
| 3 | code-review | 軸B 測試架構面六項（含 evidence fidelity／shared dependency 兩新增；翻譯忠實度明寫不歸它） |
| 4 | audit-test | 軸A 機械對帳擴充七項（含 oracle 圓形依賴／基線跑法／fixture provenance） |
| 5 | fix-test | mutation authority gate 互掛＋Type B/E＝TC escalation signal |
| 6 | model-routing＋agents registry | test-gen＝P0 最後手段（啟用條件預寫死）；**cr-research 升 full**（研究鏈） |

## 6. MVP（seeded fault-injection，~3 agent call——卡內第一步）

歷史高風險段＋迷你 TC；Lane A：4 clean＋4 oracle mutant 考 challenge（blind-derive protocol）；Lane B：六類 test 架構 mutant 考 audit＋review。量 recall＋誤報＋**attribution accuracy**（防「每題建議再確認」假 recall）＋**defect routing correctness**（機械→audit／結構→review／oracle→challenge 各司其職）。過線標準預凍結（例 challenge ≥3/4 且誤報 ≤1）。誠實邊界：量已知壞樣靈敏度非 production 有效性；個位數樣本只判 discriminating power。

## 7. AIR-70 關係

`impl/test-gen` 幽靈角色的答案**反轉**：test-gen 不必成為常設角色——test 獨立性由 oracle 層（EP）＋review 層（軸B）分擔；僅以「P0 最後手段＋預寫死啟用條件」入 lifecycle 表。AIR-70 一致性修復照舊範圍結案，本弧結論 materialize 回其一項。

## 8. dispatch 經濟學（cache 顧慮入規則）

resume（`--session-id`／agentId）當「下一步需要它自己做過的事」（同任務迭代／amendment 後 re-run／reviewer 複查）；fresh 當「需要策展最小輸入」（首次挑戰／獨立性任務／平行／session 已污染／累積 context 遠大於重送包——127K 續卷警示）。總原則一句：**下一步需要的是「它做過的事」就 resume；需要的是「策展輸入」就 fresh。**

## 9. 誠實聲明

三方全屬 A 軸靜態推理（結構推論＋repo 引證），未經 pilot 實證；「跨家族寫測試比 review 難」是任務結構推論非本 repo 實證（v3.1 後此風險已邊緣化——常態路徑不再跨家族寫測試）；challenge blind-derive protocol 是設計推論未跑過；MVP 過線不代表 production 有效。
