# EP: build Agent Review loop 閉環 — clean 覆蓋正確性假設失敗 → 顯式 Correctness lens + 迭代收斂

> **ep_type**: implementation
> **docs mode**: ✅（變更全為 `.md`，無 `.py` callable）
> **EP Review Cycle 已修正**（F3-1/F3-2 Critical + F4 消費者同步 + F3-3/4 loop + F3-5 邊界 + F5 漏場景）；見末段 EP Review Findings。

## 實作總覽

**問題（EP Review F3-1 校正後的精確前提）**：不是「base 缺 Correctness」（既有設計知道正確性）。真相鏈：
1. `agent-review-cycle.md:31-32` 明文：正確性 dimension agent 被**刻意移除**（理由：舊 4 dimension agent 共享錨定，邊際遞減）+「**正確性由 clean agent 讀 code 自然覆蓋**」
2. F1 案例（`_compute_available_funds` 的 `max(fill_dates)` 跨日低估資金）證明：**「clean 自然覆蓋正確性」假設失敗** —— clean 是 code smell 視角（讀 code 覺得怪不怪），不主動質疑邊界；`max(fill_dates)` 作為 code 看起來不怪 → clean 漏
3. 所以：移除理由的「共享錨定遞減」仍成立（dimension agent 共享錨定），但「clean 覆蓋正確性」**失敗** → 需**顯式 Correctness lens**（非 dimension agent 回歸，是第三正交 perspective）

**為何 Correctness lens 不適用「共享錨定遞減」移除理由**（F3-1 論證）：三者錨定方式**不同**，非共享 ——
- ① clean：**無錨定**（純讀 code smell）
- ② UC-anchored：**錨 EP/UC**（查語意覆蓋）
- ③ Correctness：**不錨定意圖，主動質疑邊界事實**（跨日？空值？溢出？）

三種錨定方式正交 → Correctness lens 與 clean/UC 不共享錨定 → 不適用「共享錨定遞減」→ 可加入 base。

**修復（Loop engineering）**：
1. **base 補 Correctness lens**（2→3 perspective）：review 閘門覆蓋邏輯邊界
2. **修正 agent-review-cycle:31-32 舊論述**（「clean 覆蓋正確性」→ F1 證偽）：避免新 lens 與舊論述矛盾
3. **loop 迭代收斂**（apply 後 re-review）：loop 真閉環
4. **Correctness lens vs checklist 邊界**（F3-2）：lens 上移 domain；checklist（what to check）留 code-review-and-quality profile
5. **誠實邊界**（F3-5）：Correctness 對「非系統性偏誤類」邊界 bug 同 session 有效；「系統性偏誤類」（LLM 普遍弱項）同 session 也漏 → layer 2

**三主線**（arch-thinking）：① DIP（Correctness lens 上移 domain base）② bounded context（lens 歸 review-engine；checklist 留 code-review-and-quality，review-engine:23 邊界）③ use case（build loop 閉環 = lens 補 + 舊論述修 + 迭代收斂）

---

## 段落 0：研究摘要（rg 查證 + EP Review 校正）

**斷層查證（rg confirmed）**：
- `agent-review-cycle.md:31-32`：明文「正確性 dimension agent 刻意移除（共享錨定遞減）+ clean 覆蓋正確性」← F1 證偽後半
- `review-engine` base 2-perspective（①②），無 Correctness lens（rg 0 hits）
- `code-review-and-quality` ### 1 Correctness（checklist：邏輯 bugs/邊界/測試充分）—— profile，留此處（F3-2 邊界）
- `review-engine:23`：明文「不裝（留各 adapter）：維度定義（各 profile 自訂）」← Correctness **checklist** 不上移，只 **lens** 上移
- `build.md` 階段 4：review→judge→apply→ruff，**apply 後無 re-review**（一輪非迭代）

**消費者同步清單（EP Review F4 補列，逐檔非數字）**：review-engine（base domain）/ agent-review-cycle（base 執行範本 + :31-32 舊論述）/ build（階段 4 loop）/ code-review-and-quality（### 1 邊界）/ code-review.md（:66 第三處定義）/ **deep-work.md:98**（引用 2-perspective）/ **audit-test.md:15**（base 鏡像描述）/ **workflow-review-pattern.md:255**（導覽）/ **sync-sources.md**（需新增 base perspective invariant）/ ep-review.md:66（邊界對比文字）

**風險假設**：無 runtime（docs mode）；行為假設「LLM 照新 base spawn Correctness + loop 迭代」待 L6 真實 build 驗證。

---

## UC 盤點（元專案 — 受影響清單，逐檔）

| 檔案 | 角色 | 段 | 同步類型 |
|------|------|----|---------|
| `skills/review-engine/SKILL.md` | base domain（**S1**） | 點 4 base + :23 邊界 | lens 補 + 邊界明文 |
| `commands/claude/_common/agent-review-cycle.md` | base 範本 + 舊論述（**S1+S2**） | :15-16/:31-32/:42 | base 3 + **修正 :31-32 clean 覆蓋論述** |
| `commands/build.md` | 階段 4 loop（**S2+S3**） | :152/:167/:176/:180-194/:196-204 | base 3 + loop 迭代 |
| `skills/code-review-and-quality/SKILL.md` | Correctness checklist（**S4**） | ### 1 | checklist 留（邊界），lens 引用 review-engine |
| `commands/code-review.md` | :66 第三處定義（**S4**） | :66 | 改引用（避免三定義） |
| `commands/deep-work.md` | 引用 2-perspective（**S2**） | :98 | 對齊 3-perspective |
| `commands/audit-test.md` | base 鏡像描述（**S2**） | :15 | 對齊描述 |
| `commands/claude/_common/workflow-review-pattern.md` | 導覽（**S2**） | :255 | 對齊導覽 |
| `commands/sync-sources.md` | 需新增 invariant（**收尾**） | — | 新增 base perspective invariant |
| `commands/ep-review.md` | 邊界對比文字（**S2**） | :66 | 對比文字更新 |

- **.kanban/**：建 EP 追蹤卡；**SYSTEM-MAP**：無，跳過

### Scenario Matrix（docs mode；EP Review F5 補漏場景）

| # | 場景 | 觸發 | 預期行為 | Checkpoint |
|---|------|------|---------|------------|
| SM-1 | 非系統性偏誤邊界 bug（F1 類：跨日/空值/溢出，非 LLM 普遍弱項） | Correctness lens 質疑邊界 | build loop **抓到** | base ③ Correctness |
| SM-2 | apply 修正引入新問題 / 舊 finding 沒修對 | apply 後 re-review | loop 迭代收斂（F5-M3） | S3 loop |
| SM-3 | **系統性偏誤**邊界 bug（LLM 普遍弱項） | — | Correctness 同 session **也漏** → layer 旗標導向 layer 2（F3-5） | layer 旗標 |
| SM-4 | Correctness 定義 drift（三處→單一源） | lens 上移 + checklist 留 + :66 改引用 | 無雙/三定義 | S4 |
| SM-5 | base 3 + max-agents=3（預設） | base 佔滿 | Correctness always；extra 不觸發（除非 -a 4+） | 優先序 |
| SM-6 | **base 3 + max-agents<3 降級**（-a 1/2） | cap < base 數 | 降級策略：Correctness 優先保留 > clean > UC（F5-M2） | 降級序 |
| SM-7 | **loop 達迭代上限（3 輪）未收斂** | re-review 仍有 finding | 硬性處置：標 ⚠️ + 阻止 Capabilities 升級 + layer 旗標導向 layer 2（F5-M1） | S3 上限 |

---

## 段落劃分原則

依賴圖：**S1**（base 補 lens + 修正舊論述 + 邊界）→ **S2**（base 3 傳播所有消費者）+ **S3**（loop 迭代）並行 → **S4**（code-review 對齊 + checklist 邊界）→ 收尾。

**語義約束**：
- **Correctness lens 定義**（review-engine domain）：邊界正確性**視角**（質疑邊界事實：跨日/空值/溢出）—— **lens 非 checklist**（checklist 留 code-review-and-quality，review-engine:23 邊界）
- **三正交 perspective**（錨定方式不同，非共享）：① clean 無錨定(smell) / ② UC 錨 EP(coverage) / ③ Correctness 主動質疑邊界(correctness)
- **loop 收斂定義**：review → judge → apply → **re-review（同 base 3）→ 若有 finding 再 judge→apply**，直到 pass 或達上限（3 輪）
- **pass 判定者**（F3-3）：re-review 後**再 invoke /judge-review**（非主 LLM 自判，保 Writer/Reviewer 分離）
- **降級序**（F5-M2）：max-agents < 3 時，保留序 Correctness > clean > UC
- **系統性偏誤邊界**（F3-5）：Correctness 對非系統性偏誤同 session 有效；系統性偏誤（LLM 普遍弱項）需 layer 2

---

## S1: review-engine base 補 Correctness lens + 修正 agent-review-cycle 舊論述 + 邊界

### Context
- **背景**（F3-1 校正前提）：agent-review-cycle:31-32 明文「正確性 dimension agent 移除 + clean 覆蓋」。F1 證明 clean 覆蓋失敗。需顯式 Correctness **lens**（非 dimension agent 回歸）+ 修正舊論述
- **依賴**：S1 基礎，S2/S3/S4 依賴
- **語義約束**：見段落劃分原則（lens vs checklist 邊界 + 三正交 + 論證）
- **依賴錨點**：review-engine 點 4 base（:138）/ :23 邊界（不裝維度定義）/ agent-review-cycle :31-32（舊論述）
- **成功標準**：base 3-perspective（+ ③ Correctness lens）+ :31-32 舊論述修正 + :23 邊界明文（lens 上移 / checklist 留）

### 修改要點（docs mode）
1. **`review-engine` 點 4**：2→3 perspective
   - + ③ Correctness lens（邊界正確性視角：質疑邊界事實，主動查跨日/空值/溢出；不錨定意圖）
   - 論證（F3-1）：三者錨定方式不同（clean 無錨 / UC 錨 EP / Correctness 質疑邊界）→ 正交 → 不適用「共享錨定遞減」移除理由
   - 明文：Correctness 對**非系統性偏誤**邊界 bug 同 session 有效；**系統性偏誤**（LLM 普遍弱項）同 session 也漏 → layer 2（F3-5）
2. **`review-engine:23` 邊界明文**：Correctness **lens**（視角，執行預設）屬 domain 可裝；Correctness **checklist**（what to check：null/boundary/error path）屬 profile，留 code-review-and-quality（F3-2）
3. **`agent-review-cycle.md:31-32` 修正舊論述**：刪/改「正確性由 clean 自然覆蓋」（F1 證偽）→ 改「正確性由 ③ Correctness lens 顯式覆蓋（clean 是 smell 視角，不主動質疑邊界）」；保留「共享錨定遞減」對 dimension agent 的論述（仍成立）
4. **點 5 對齊**：base 恆 ①+②+③（3）；extra 在 max-agents>3；Correctness 是 base（always-on）**不進入 extra 優先序**

### 驗證策略
- rg：`rg "3-perspective|③ Correctness" skills/review-engine/SKILL.md` → base 3
- rg 舊論述：`rg "clean.*覆蓋正確性|clean 自然覆蓋" commands/claude/_common/agent-review-cycle.md` → 已修正
- DIP/邊界：lens 在 domain，checklist 留 code-review-and-quality
- /sync-sources：base perspective 單一源

---

## S2: base 3 傳播所有消費者（含 EP Review F4 補列）

### Context
- **背景**：S1 base 改 3-perspective 後，所有引用 base/2-perspective 的消費者同步。EP Review F4 補列 deep-work/audit-test/workflow-review-pattern/ep-review（原 EP 漏）
- **依賴**：S1
- **依賴錨點**：agent-review-cycle :15-16/:42、build :152/:167/:176/:180-194、deep-work :98、audit-test :15、workflow-review-pattern :255、ep-review :66
- **成功標準**：所有消費者 2-perspective → 3-perspective 對齊；build.md cap 提示 base 佔 2→3

### 修改要點
1. **`agent-review-cycle.md`**：base 3（:15-16 加 ③ Correctness prompt）；max-agents≥3 base 3；max-agents<3 降級序（Correctness>clean>UC，SM-6）
2. **`build.md` 階段 4**：:152/:167/:176 對齊 base 3；:180-194 adaptive 映射 base 佔 2→3；:194 cap 截斷提示 base 佔 2→3
3. **`deep-work.md:98`**：2-perspective → 3-perspective（deep-work 是用戶不在場唯一閘門，base 缺 Correctness 損害更大）
4. **`audit-test.md:15`**：base 鏡像描述 2→3（audit-test 自身不走 perspective，但描述範圍對齊）
5. **`workflow-review-pattern.md:255`**：導覽 2→3
6. **`ep-review.md:66`**：邊界對比文字更新

### 驗證策略
- rg 殘留：`rg "2-perspective|預設 2 agent" commands/ skills/` → 僅歸檔 EP/歷史文件
- 跨檔一致：所有活躍消費者 base 3
- /consistency 各消費者

---

## S3: build 階段 4 loop 迭代收斂（EP Review F3-3/4 + F5-M1 補）

### Context
- **背景**：build 階段 4 現狀 review→judge→apply→ruff→階段 5，**apply 後無 re-review**。Loop engineering 要閉環
- **依賴**：S1（base 補 lens 後 re-review 有意義）
- **語義約束**：見段落劃分原則（loop 收斂 + pass 判定者 + 達上限處置 + 降級序）
- **依賴錨點**：build :202（ruff 後）/ :204（階段 5 邊界）/ :242（layer 旗標）
- **成功標準**：階段 4 apply 後 re-review loop（pass 判定 = judge-review，非主 LLM 自判）；達上限硬性處置

### 修改要點
1. **`build.md` 階段 4 加「loop 迭代收斂」**（:202 ruff 後、:204 階段 5 前）：
   - apply 後 **re-review（同 base 3-perspective）**
   - **pass 判定**（F3-3）：re-review findings **再 invoke /judge-review**（非主 LLM 自判，保 Writer/Reviewer 分離）
   - 有 ✅ 採納 finding → 再 apply → re-review（迭代）
   - **收斂**：judge-review 無新 ✅ 採納（pass）或**達上限 3 輪**
2. **達上限硬性處置**（F3-4 + F5-M1）：
   - 標 ⚠️「loop 未收斂（達 3 輪上限）」
   - **阻止 Capabilities/Kanban 升級**（build.md:222 升級條件加「loop 須收斂」）
   - **layer 旗標導向 layer 2**（:242 條件加「loop 未收斂」）
3. 明文 Loop engineering 框架：階段 4 = self-correcting loop（非一輪）

### 驗證策略
- rg：`rg "re-review|loop 迭代|loop 未收斂" commands/build.md`
- 邊界：達上限硬性處置（阻止升級 + layer 2）

---

## S4: code-review 對齊 + Correctness lens/checklist 邊界（F3-2 + F4-5）

### Context
- **背景**：Correctness lens 上移 review-engine；checklist 留 code-review-and-quality（:23 邊界）。code-review.md:66 是第三處自包含定義（F4-5），改引用
- **依賴**：S1
- **成功標準**：Correctness 定義單一源（review-engine lens + code-review-and-quality checklist，邊界清楚）；code-review:66 改引用

### 修改要點
1. **`code-review-and-quality/SKILL.md` ### 1**：Correctness **checklist**（null/boundary/error path，what to check）**留此處**（profile，:23 邊界）；加一句「Correctness **lens**（視角）定義見 review-engine base 點 4 ③」
2. **`code-review.md:66`**：自包含定義 → 改引用（「Correctness lens 見 review-engine；checklist 見 code-review-and-quality ### 1」），消除第三處定義（F4-5）
3. **layer 2 邊界明文**（build 階段 6 + review-engine）：build loop（內，補 lens 後閉環非系統性偏誤邊界 bug）vs layer 2 code-review（外，系統性偏誤 + 同 session 盲點）

### 驗證策略
- rg：Correctness 定義單一源（review-engine lens + code-review-and-quality checklist）；code-review:66 引用非自包含
- /sync-sources：Correctness lens 單一源

---

## 整合策略

- S1（base lens + 舊論述 + 邊界）→ S2（消費者傳播）+ S3（loop 迭代）並行 → S4（code-review 邊界）→ 收尾
- 整合驗證：全鏈 base 3 + 舊論述修正 + loop 迭代 + lens/checklist 邊界 + 消費者同步
- /sync-sources（新增 base perspective invariant）+ /consistency

## 收尾步驟（docs mode）

1. **sync-sources 新增 invariant**（F4-3）：加「review-engine base perspective」invariant（定義源 review-engine 點 4 ↔ 消費者引用一致），讓 /sync-sources 機械驗證 base 3-perspective
2. **CLAUDE.md**：查證空操作（rg commands/CLAUDE.md skills/CLAUDE.md 無 perspective/base → 跳過）
3. **/audit-test**：docs mode 無 .py，跳過
4. **docs mode 收尾**：受影響命令行為反映 + /sync-sources（base perspective invariant）+ /consistency（review-engine / agent-review-cycle / build / code-review-and-quality / code-review / deep-work / audit-test / workflow-review-pattern）

---

## EP Review Findings

> EP Review Cycle（3 Explore agent · F1-F5 + Clean Arch top-down + loop 閉環驗證）。Critical 6（F3-1/F3-2 阻塞 + F4-1/2/3 + F5-M1）。全採納，已寫入 EP。

| ID | 嚴重度 | 問題 | 決策 | 處置 |
|----|--------|------|------|------|
| F3-1 | Critical（阻塞） | 既有設計 :31-32 明文正確性 agent 刻意移除 + clean 覆蓋；EP「base 缺」不精確 | ✅ 採納 | 前提重寫（clean 覆蓋假設失敗）+ 論證 lens 正交 + S1 修正 :31-32 |
| F3-2 | Critical | lens vs checklist 邊界混淆（review-engine:23） | ✅ 採納 | S1+S4 區分：lens 上移 / checklist 留 |
| F4-1 | Critical | 漏列 deep-work:98 | ✅ 採納 | S2 補列 |
| F4-2 | Critical | 漏列 audit-test:15 鏡像 | ✅ 採納 | S2 補列 |
| F4-3 | Critical | sync-sources 需新增 invariant | ✅ 採納 | 收尾新增 |
| F5-M1 | Critical | loop 達上限未收斂無 scenario | ✅ 採納 | SM-7 + S3 硬性處置 |
| F4-4 | Important | 漏列 workflow-review-pattern:255 | ✅ 採納 | S2 補列 |
| F4-5 | Important | code-review:66 第三處定義 | ✅ 採納 | S4 改引用 |
| F3-3 | Important | loop pass 判定者未定義 | ✅ 採納 | S3：再 judge-review |
| F3-4 | Important | 達上限硬性處置未定義 | ✅ 採納 | S3：⚠️ + 阻止升級 + layer 2 |
| F3-5 | Important | 同 session 盲點 vs 系統性偏誤張力 | ✅ 採納 | S1：區分非系統性/系統性偏誤 |
| F5-M2 | Important | base3 + max-agents<3 降級 | ✅ 採納 | SM-6 + S2 降級序 |
| F5-M3 | Important | re-review 發現舊 finding 沒修對 | ✅ 採納 | SM-2 涵蓋 |
| F-1/F3-7 | Important/Suggestion | 「17 檔」數字不準 | ✅ 採納 | 改描述性 + 逐檔清單 |
| F3-6/F3-8/F-6/F-7/F5-M4/F4-7 | Suggestion | 用語精確 / F1 path:line / glm 用語 / docs mode loop | ✅ 採納 | 各段微調 |
