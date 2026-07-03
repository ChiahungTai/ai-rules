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

## /judge-review 評估（2026-06-17 dry-run dogfood）

> 以「hermes 自我進化系統 §5 行動 1（自我改進安全檢查表：新建顯式 rule + 統一『機械閘門 > LLM 自覺』散落術語）」為 dry-run 標的，實際跑 docs mode ripple + rg 殘留驗證。純 .md、無 .py callable 變更 → docs mode 成立。

**Dry-run 實證（實際 rg，非推測）**：

| 查證 | 結果 | 證明的盲區 |
|---|---|---|
| `rg -l "機械閘門\|LLM 自覺"` | 9 檔跨 4 目錄（rules/、commands/、commands/instruction/_common/、ai-analysis/） | 逐檔枚舉漏 `_common/`（被引用的共用範本）+ ai-analysis/（非權威處）|
| `_common/workflow-review-pattern.md:112` | 引用「機械閘門」但非定義 | _common/ 是「逐檔枚舉必漏」典型（被引用方，非主動方）|
| 定義源 | `review-commit-workflow-mismatch.md:8`（ai-analysis/ 摩擦文件，非 rules/）| 縫隙 2 真實：定義源在非顯眼處 |
| `rg -l "共用規範\|與.*共用"` | 12 檔自稱共用 | 語義反向撈的目標群真實存在 |
| `agent-review-cycle.md:23` 用「機械**軸**」 | rg near-miss / 概念邊界模糊 | 語義撈需人工判讀，且「相關概念」難精確 |

**決策**：

| 子建議 | 決策 | 理由 |
|---|---|---|
| (A) ripple 加語義反向撈 | ✅ 採納（限定觸發） | 核心哲學自我套用（見下）；dry-run 證實 9 檔散落、12 檔自稱共用。**限定**：僅「格式統一/術語統一/共用規範」類 docs EP 觸發，非所有 docs EP（防過度工程）|
| (B) 術語改名 ripple 必含定義源 | ✅ 採納 | dry-run 證實定義源在 ai-analysis/ 非顯眼處；判定準則清晰（「描述規範」非「僅使用」→ 必改）|
| (C) rg 殘留驗證加同義詞盤點 | ⚠️ 部分採納 | 概念成立（「機械軸」near-miss 實證），但獨立步驟= over-engineering；**併入 (A)** 同一 rg（同義詞盤點不另起步驟）|

**採納的最強理由（第一性原理）**：本 type-2 不是外來意見，是 ai-rules 核心哲學**「機械閘門 > LLM 自覺」**（`review-commit-workflow-mismatch.md:8`）對 ripple 步驟的自我套用——ripple 靠 LLM「想到」= 自覺（會漏）；語義反向撈 = 機械閘門（rg 強制掃）。採納 = 治理原則貫穿自身命令寫作；拒絕 = 在 ripple 點上自相矛盾地「靠 LLM 自覺」。

**第二層後果 / 誠實限制**：
- 語義反向撈**降低漏率，不消除漏率**——pattern 本身會漏同義表述（「遵循 template」「對齊 spec」不用「共用」字眼）、會 near-miss（「機械軸」≠「機械閘門」）。是「機械補人類遺忘」，非 100% 覆蓋。
- 過度觸發 → EP 負擔膨脹 → 違反 `acceptance-evidence.md`「避免過度工程」內建約束 → 故三子建議都限定觸發條件。

**狀態**：`needs-confirmation`（type-2 正常路徑為 /flow-review 人類討論 → /spec → /build）。本評估為 /flow-review 的現成輸入；實際改 `execution-plan.md` docs mode 段（加觸發條件 + 語義撈步驟）由後續 /build 執行。
