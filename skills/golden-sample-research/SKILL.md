---
name: golden-sample-research
description: golden-sample 研究方法論 — 從正樣本收割(交易所/事件幫你撈好的結果股)歸納 setup 籤名,建分類器套用全市場。研究收斂/多頭拉回/飆股 Surge/abN 等「結果股回推 setup」問題、標註 golden sample、歸納門檻、LLM 當分類器時載入。核心紀律=先歸納後演繹(反發明特徵/反過早判斷/反四分法/反 boolean OR/漸進擴大/LLM 建議非裁決)。domain 心智模型在各 domain skill(pre-attack-setup 等)。
---

# Golden-Sample 研究方法論

> **載入時機**:做「從已知結果股回推 setup 籤名 → 歸納 → 建分類器」這類研究時;LLM 當分類器掃特徵時;標註/迭代 golden sample 時。
> 本 skill 是**過程紀律**(domain 中立)。各研究的 domain 心智模型在對應 domain skill(如 [pre-attack-setup](../pre-attack-setup/SKILL.md))。

## 什麼是 golden-sample 研究

**從「已知結果的股票」回推它們發生前的 setup 籤名,歸納成分類器,再套用全市場預測**。關鍵:結果股 = 免費的正樣本收割源,不必自己掃全市場找答案。

| 研究 | 正樣本收割源(為何免費) | 歸納的 setup |
|------|----------------------|-------------|
| 攻擊前 setup | 處置股(交易所處置機制 = 大漲篩選器) | 收斂 / 多頭拉回 |
| 飆股 Surge/abN | 歷史大波段(事後全掃已知頂底) | Surge 噴出波 / abN 洗籌碼 |

## UC 鏈(研究分解)

```
UC-1 標註源收割(機械撈結果股) → UC-2 Golden(人工標 setup 型 + 細化)
   → UC-3 Pattern(歸納門檻)→ UC-4 Classifier(程式化 + 驗證)
```

- **UC-1**:從收割源機械撈出候選(處置股清單 / 歷史大波段)。門檻鬆,先求召回。
- **UC-2**:人工確認 setup 型 + 標細部特徵 → golden-samples(結構化欄位,非散文)。golden 同時扮演兩角色:**UC-1 的輸出規格**(掃描器該產出什麼)+ **UC-3 的輸入**(歸納門檻的素材)。
- **UC-3**:從 golden 統計 setup 特徵分佈 → 門檻 → 回饋 UC-1 收緊/放寬。
- **UC-4**:門檻穩定後寫分類器 + 回測驗證(召回/精確)。

迭代:`UC-1 粗掃 → UC-2 標記 → UC-3 歸納 → 收緊 → 再掃 → 收斂 → UC-4 程式化`。**不在案例不足時硬寫門檻**(C 層風險)。

> **分類 vs 分群**:UC-3/UC-4 預設「規則/LGBM 分類」(人類先標 type → 歸納門檻)。user 也探索過**分群**(k-means / 時間序列)作為替代 — 特徵自然聚攏找群心,不預設 type,但群心語義事後解讀。現行處置股研究選分類(已有 type);分群是 user 考慮過的未探索替代。

## 核心紀律:先歸納後演繹(反覆糾正出的 LLM 行為缺陷)

這些是從實際研究中反覆糾正 LLM 的行為模式 — 不是建議,是**禁令**:

1. **反發明特徵** — 只算人類指定的特徵,不自己發明新特徵。先算指定清單 → 觀察 → 才考慮加。LLM 愛自創複合指標,那是越界。
2. **反過早判斷** — 先輸出**統計表格**(特徵逐日/逐檔數值),「看就會很明顯」;不要資料還沒看就跳到分類規則。歸納先於演繹。
3. **反四分法推門檻** — 門檻數值**直接從 golden 觀察極值(min/max)**,不用 quartile 統計推估。golden 裡收斂最小的 ma3 是多少,就是門檻,不要「用四分位數估」。
4. **反 boolean OR** — 多條件用**分層/條件式門檻**(tiered),不是 OR 平鋪。例:ma5<X 不查 ma3;ma5 介於區間才加查 ma3/ma4。OR 太寬,分層才精準。
5. **漸進擴大** — 10 檔 → 50 檔 → 全量。不要一開始跑全量(基本邏輯錯就全浪費)。每階段邏輯穩定才擴大。
6. **採樣多樣性** — 抽樣要**四散**(代碼前綴、年份、產業都分散),不要都抓同類。採樣偏誤會假陽性。
7. **LLM 是建議者非裁決者** — agent 每檔提案分類 + 規則修改 → 主 session 統整 → **人類 L6 看圖拍板**。golden set 是活的,人類會 `OVERRIDE`(改型)/ `EXCLUDE`(剔除)。

## 三層程式化可行性(決定 UC-4 能走多遠)

| 層 | 性質 | 處理 |
|----|------|------|
| **A 層(機械)** | 發動點定位、轉折極值、連續性、指標 | 直接提煉 code |
| **B 層(半機械)** | 從 golden 歸納的門檻 | 門檻穩定後寫,持續迭代 |
| **C 層(天花板)** | 基本面 / 意圖 / 「真發動 vs 再次攻擊」邊界 | K 線代理 + 人工,無法全自動 |

C 層靠 LLM 判讀 + 人類 L6 — 這正是 golden-sample 研究需要 skill(domain 判讀層)而非純 code 的理由。

## 校準

- **in-sample 100% ≠ 一般化**:golden 對齊的完美記錄是 heuristic + 少數人工修正的結果。out-of-sample 驗證(time-respecting split)才算閉合。
- **單一個案 ≠ 通則**:任何從 golden 歸納的「籤名 / 指紋 / 門檻」套用新標的須重新驗證,不可當普世規則硬套。
- **正樣本收割源的 bias**:處置股 = 大漲過的股,從它們學的 setup 籤名可能有「大漲股特有」偏差。分類器套用全市場時,非大漲股的 false positive 要靠 out-of-sample loop 量測。

## 實例

- 攻擊前 setup(收斂/多頭拉回):[pre-attack-setup](../pre-attack-setup/SKILL.md) + mosaic `poc/sqz/`(POC)/ `ai-analysis/surge-abc/archived/round2-2026-07-29/design-scanner.md`(UC 鏈設計源)
- 飆股 Surge/abN:mosaic `ai-analysis/surge-abc/archived/`(golden-samples.md golden 樣本、round2-2026-07-29/design-scanner.md UC 鏈);正樣本收割源 = 歷史大波段(事後全掃)
