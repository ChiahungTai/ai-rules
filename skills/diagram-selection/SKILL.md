---
name: diagram-selection
description: "畫圖前選載體的判準與跨載體共性慣例——mermaid／HTML 塊圖／archify／表格／domain 渲染器。觸發詞：選圖、畫圖工具、圖表選型、何時用 archify、mermaid vs archify、載體選擇、report shell 補圖、換形態、vision 判讀契約、圖表渲染管線。判準四問（邊有無通道／交錯度／是否圖論問題／成本軸）＋vision 三段式契約＋渲染/判讀分離。"
when_to_use: "任何要畫圖的時刻——/illustrate 選輸出模式、EP/殼規劃期圖型分派、report shell 補圖、vision 批量判讀派發前。archify 是最後手段（user 裁示），選型預設 mermaid／HTML 塊。"
---

# Diagram Selection — 畫圖載體選型與產線共性

> **職責邊界**：本 skill 管「**用什麼載體畫**」（選型判準＋跨載體共性慣例）。「畫什麼 artifact」（boundary/sequence/call-graph 等 SA/SD 語義）歸 illustrate [artifact menu](../_common/illustrate-artifact-menu.md)；「怎麼嵌進殼」歸 [illustrate-html-mode](../_common/illustrate-html-mode.md)；各載體實作配方在各自 skill/role（見文末指針）。

## 判準四問（順序回答）

1. **邊有沒有結構化通道？** 時間軸（sequence）、線性管線（flowchart LR）、狀態轉移（stateDiagram）、層次/泳道柵格（layer/lanes）是天然通道——邊沿通道走零交錯。有通道 → mermaid 一次可成（層次柵格通道只有 archify 結構容器提供——互動/規模需要時才走，見下「最後手段」段）。
2. **交錯度多高？** 自由 node-link（邊要自己找路、交錯不可避免）是 auto-layout 死穴——user 判決錨：「如果圖的物件線條要交錯太複雜，不好用」。決策流程的**分支匯流是臨界**（分支少 mermaid 勉強、再多換載體）。
3. **是不是圖論問題？** 層次對照、前後比較、分類學——內容本質沒有 edge routing 需求 → **HTML 塊（div/flex/grid）或表格**，不是圖的東西別硬畫圖。
4. **成本軸**：mermaid 宣告式 1 輪；archify LLM 產線高一至兩個數量級（~10 輪量級/圖、單圖十分鐘級、時間絕大多數耗在 LLM 生成——鑑識錨：AIR-30 任務弧材料）；domain 資料圖機械渲染秒級。小圖的資訊密度撐不起 LLM 產線成本。

## 載體對照（實證版）

| 載體 | 適用 | 邊界/實證 |
|------|------|----------|
| mermaid `sequenceDiagram` | 呼叫鏈/互動序/雙路徑 | **最強形態**（`alt/loop/note` 承載分支；隱藏容器渲染免疫）；1 輪 |
| mermaid `stateDiagram-v2` | lifecycle/狀態機 | 5 狀態/8 邊/label ≤20 字是餘裕上限；self-loop 表 idempotent 自然；1 輪 |
| mermaid `erDiagram` | 實體關係 | 實體 ≤6、關係邊為鍵語義時清楚；1 輪 |
| mermaid `flowchart LR` | 管線/單向流程 | 單向無分支零交叉，資訊密度與布局成本最低；1 輪 |
| mermaid `flowchart TB` 自由 | 小型組件圖 | ≤8 節點勉強（永遠殘留小 crossing）；畫前先問能否換形態；~3 輪 |
| **HTML 塊圖**（殼內 div/flex/grid） | 層次架構/多分支決策/前後對照 | 零渲染管線、殼原生一體；「不是圖論問題」的結構首選；色彩語義可承載（如 rose=痛點/green=改善） |
| **表格** | 分類學/型別對照 | class 圖第一層答案：型別｜職責｜依賴比繼承圖好讀好維護 |
| **archify** | 見下「最後手段」段 | 無通道大圖＋互動導航才值回成本 |
| **domain 渲染器**（如 mosaic kchart） | 真實資料綁定圖（K 棒/行情） | 機械渲染（秒級、確定性、與 token 脫鉤）＋LLM 只在判讀端——複用單位是「圖形契約」lib＋領域薄殼，不是成品圖 |
| **刪邊/降文字記載** | 交錯度超標的取捨 | 第三選項（不是只有換工具/硬畫二選一）——取捨顯式記錄在圖備註/卡，事實不丟 |

**class 圖兩層判準**：先問是不是圖論問題（型別對照→表格）；真是繼承網且需要圖→archify（mermaid classDiagram 實證難用——多向交錯無通道可救）。

## 換形態設計招（比換工具有效）

1. **組件圖 → sequence**：多數「組件關係」真實問題是「執行時誰呼叫誰」＝時序，畫成 sequence 立刻有通道
2. **自由 flowchart → 分層**：節點按依賴方向分 layer/subgraph——archify architecture 的本質
3. **class 圖 → 表格**：繼承/組合列欄位
4. **低價值邊先砍**：backward/交叉邊移除、語義沉到 sublabel 或 cards，比硬繞 via 便宜

## archify 使用前提（最後手段——user 裁示「非必要不用」）

只有命中**獨有價值**才上：①互動導航（pan/zoom/search/focus、節點護照、點擊回源）②大規模依賴網 ③無通道大圖需要防交錯結構容器（layer/lanes 柵格）＋validate 佈局 gate。命中 → 走 [illustrate-html-mode](../_common/illustrate-html-mode.md) 委派產線（含止損分層與輪數 guard）；未命中 → 上面對照表選輕載體。**規律型圖硬用 archify＝浪費 validate 迴圈**（AIR-29 實證）。

## 跨載體共性慣例池（三弧同構：archify 線/kchart 線/事件分析線各自獨立收斂）

**vision 判讀契約（三段式）**——派 vision-review 判讀圖時 prompt 必含：①逐張結構化輸出（一行固定欄位）②**誠實段**（目視分不出來明說、無從判斷不腦補）③跨案觀察段。配套：**每 agent ≤10-15 張**（超過 token 爆炸）；**抽樣錨定全樣本**——只看輸家（或贏家）子集的 vision 結論是倖存者偏差，會被全樣本數字反駁；產出要能**回數字驗證**（機械綠/parse OK ≠ 渲染 OK ≠ 佈局可讀——vision 是後兩層唯一防線）。

**盲判＝Writer/Reviewer 分離**——既有結論/人標不進判讀包（防引導偏差；分歧＝浮出候選非缺陷）；渲染端可機制化（如 `--blind` 撤結論欄）。預期描述須 code＋文檔**雙源核對**（文檔 drift 會直接污染判讀 prompt）。

**self-contained 圖**——給 agent 的圖把關鍵數值/週期宣告燒進圖題（agent 不用回查表；OCR 不可靠所以 caller prompt 自帶 header 重複宣告）；事件錨點直接標在圖上。

**渲染/判讀分離**——畫圖走機械 code path（確定、秒級、可批次、與 token 脫鉤），LLM 只放消費端（判讀）；一次渲染多方消費（agent 判讀＋人審圖牆）攤薄判讀成本。工具演化靠 code commit＋review，非逐圖 LLM 迴圈。

**fail-visible 批次**——單案渲染 FAIL 不拖垮批次；manifest 逐案增量記（中斷續跑）；無圖有降級路徑（標「無輔助」可判讀）。

**契約 lib 化＋領域薄殼**——複用單位是「圖形契約」（標記原語＋匯出管線）不是成品圖；新研究線只寫同款薄殼，lib 不隨領域演化。暫存 code 有「.agent-tmp 先暫存→正式化上抽 repo」生命週期。

**人類板設計**——圖牆/殼為人類瀏覽設計：正反分頁、按家族分組、worst-first、每卡自帶 gate 數值、iframe lazy loading。人類目檢是最後一道（會抓到 AI 數字分析的盲區）。

**載體限制顯式登記**——渲染端已知限制（避讓缺失/座標裁切/合成事件釘不住）寫進 instruction 檔方法論限制段，不是每次重踩。

**git policy**——源進 git、渲染產物不進、一命令再生（條目詳 [illustrate-html-mode](../_common/illustrate-html-mode.md) git 段，單一源）。

## 邊界與指針（配方不重述）

| 要做什麼 | 去哪 |
|---------|------|
| mermaid 渲染配方（style 規範/mmdc 管線/殼內嵌 lazy render） | [mermaid](../mermaid/SKILL.md) |
| 殼整合（嵌圖形態/hook 時間點/輪數 guard/重生） | [illustrate-html-mode](../_common/illustrate-html-mode.md) |
| archify 產線紀律（validate 迴圈/止損/author 期前移） | [archify-gen](../../agents/roles/archify-gen.md) role |
| UI 驗收編排（三鏈/截圖量測/盲判 spawn/pytest 沉澱） | [ui-visual-verify](../ui-visual-verify/SKILL.md) |
| domain 判讀契約實例（K 線三證據層/七項清單） | [kbar-form-analysis](../kbar-form-analysis/SKILL.md) |
