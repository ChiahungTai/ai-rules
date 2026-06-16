# dogfood 縫隙：docs mode EP 的 ripple 漏掃（ep-poc-scripts-lifecycle 執行發現）

> 來源：以 docs mode 執行 `ep-poc-scripts-lifecycle.md`（S6 dogfood /execution-plan）時，實作層發現 EP 未涵蓋的 ripple。兩者皆為 type-2（/execution-plan docs mode 的設計缺陷），已於本次 build 當場修正，記錄供 /flow-review。

## 縫隙 1：宣稱「共用規範」的第三個檔頭檔未被 ripple 掃到

- **情境**：EP S3 統一 POC 檔頭格式（聯集 template：EP 段落 / 風險 / 來源）於 `spec.md` + `ep-validate.md`。但 `skills/spec-driven-development/SKILL.md` 也有一個 POC 檔頭，且**檔內明文宣稱「與 /spec 和 /ep-validate 共用規範」**——第三個檔頭欄位卻分歧（缺 EP 段落、風險寫 [高] 非 [致命/高/中]）。
- **為何漏**：EP 的 ripple 清單（S3/S5）逐檔列舉，未用「宣稱共用規範」這個語義線索反向撈所有自稱共用的檔頭。LLM 寫 EP 時逐檔想到、漏了第三處。
- **type-2 建議**：/execution-plan 處理「格式統一」類變更時，ripple 步驟應加一條機械掃描——`rg "共用規範|與.*共用"` 撈所有自稱共用的檔頭/段落，逐一比對是否真的與權威源一致。語義線索（自稱共用）比檔名枚舉更不易漏。
- **本次處置**：已對齊 spec-driven-development SKILL.md 檔頭至聯集 template（記為 EP 偏差，實作層裁量）。

## 縫隙 2：術語改名時，段落定義源（execution-plan.md）未進 ripple 範圍

- **情境**：S4 把 `build.md`/`deep-work.md` 的「Examples 盤點/驗證」改名「POC/demo」。但 `execution-plan.md` 的「### 4. 驗證策略」段（定義 EP 段落該寫什麼驗證）仍寫「Examples 設計」——這是 build 盤點的**上游定義源**，改名後下游（build）改了、上游（execution-plan）沒改，未來產生的新 EP 會繼續寫「Examples」。
- **為何漏**：EP 把 ripple 限在「直接引用舊詞的檔案」，沒意識到 execution-plan.md 是**產生這些詞的源頭**。改下游不改上游 = 術語會從上游再生。
- **type-2 建議**：/execution-plan 處理「跨命令術語改名」時，ripple 必須包含**定義該術語的源頭命令**（execution-plan.md 定義段落元素、commit.md 定義 commit 階段…），不只消費端。判定：哪個命令的文檔**描述這個概念的規範**（而非只是使用它）→ 必改。
- **本次處置**：已改 execution-plan.md:142,193「Examples」→「POC/demo」（Agent Review Finding 3 採納）。

## 共通根因

兩縫隙同一根因：**EP 的 ripple 靠「逐檔枚舉」，缺「語義反向撈」**。枚舉漏率高（人/LLM 想不到的檔案就漏）；語義線索（「自稱共用」「定義源」）機械可掃、覆蓋更全。docs mode 的驗證策略（rg 殘留）只驗「目標詞歸零」，不驗「相關概念是否還有漏網檔案」——這是 docs mode 驗證的盲區。
