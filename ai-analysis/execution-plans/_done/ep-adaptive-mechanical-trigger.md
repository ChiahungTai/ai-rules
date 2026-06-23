# EP: build 階段 4 adaptive extra agent 觸發機械化

> **ep_type**: implementation
> **docs mode**: ✅（變更全為 `.md`：review-engine / build / agent-review-cycle，無 `.py` callable 符號）

## 實作總覽

把 review-engine adaptive「>2 配置」從**語義 opt-in**（LLM 判「高風險/大變更」）改為**機械觸發 + 分層正確**：

- **domain**（review-engine）：定義通用「段落風險特徵 → extra agent」映射框架（DIP — 不寫死消費命令特有名詞）
- **adapter**（build）：把**既有兩個機械信號**（階段 0 整合器 IO 觸發 / 階段 2 路徑覆蓋簽名偵測）映射到通用特徵 → 觸發 extra；階段 6 加 layer 旗標
- **複用非新造（範圍已界定）**：build adapter **只接線既有兩信號**（IO + 簽名），不新造偵測。跨模組 ripple 在段落 scope 看不全（layer 1 天花板），交 **layer 旗標導向 layer 2 code-review**（全貌 findReferences），不在 build 新造跨模組偵測

**三主線**（arch-thinking 已檢視）：① 依賴 `build → review-engine`（review-engine 不依賴 build，DIP；domain 零消費命令特有名詞）② bounded context（review-engine 擁通用風險特徵 domain；build 特有名詞是 adapter 翻譯）③ use case（機械觸發不靠 LLM 感覺）

---

## UC 盤點（元專案 — 受影響命令/rules 清單）

ai-rules 元專案無 library Capabilities 表格。受影響：

| 檔案 | 角色 | 段 |
|------|------|----|
| `skills/review-engine/SKILL.md` | adaptive domain（**S1 改**） | 點 5（:143） |
| `commands/build.md` | 消費 adaptive（**S2 改**） | 階段 0/2/4/6 |
| `commands/claude/_common/agent-review-cycle.md` | >2 配置執行範本（**S3 同步**） | :49-51 |

**消費者確認（不受影響 — 用 dimension profile 非 2-perspective，EP Review rg 實證）**：`code-review`（六軸）、`ep-review`（F1-F5）、`execution-plan` EP Review（五維度）— review-engine 點 4 明文「code-review 六軸、ep-review F1-F5 等以維度 profile 分配 agent，非此 clean/UC 2-perspective」。EP Review rg 確認三檔無 `>2 配置`/`opt-in`/`adaptive` 引用。

- **.kanban/**：ai-rules 元專案 kanban 用於自身開發追蹤；掃描確認是否建 EP 追蹤卡
- **SYSTEM-MAP**：ai-rules 無，跳過（正當跳過）

### Scenario Matrix（docs mode 文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 段落含外部整合（IO） | build 階段 0 整合器標記（:63） | 觸發 adversarial extra agent | base ①+② + adversarial | review adaptive |
| SM-2 | 段落改公開簽名/新注入點 | build 階段 2 路徑覆蓋觸發（:132） | 觸發 architecture+consumer extra | base + arch+consumer | review adaptive |
| SM-3 | 小段落無特徵命中 | 無特徵 | base 2-perspective，**不 spawn extra**（避免浪費） | base ①+② | review adaptive |
| SM-4 | 段落 UC 數 >6（EP 本身 UC 清單） | EP UC 盤點計數 | 觸發 UC-split extra | base + UC-split | review adaptive |
| SM-5 | review-engine adaptive 改 | S1 改點 5 | 消費者同步（agent-review-cycle） | rg 0 殘留舊措辭 | 同步 |
| SM-6 | 跨模組 / 公開簽名變更 / 整合器段落 commit 前 | build 階段 6 偵測（**新增**偵測分支） | 輸出 layer 旗標「⚠️ 本 build 僅 layer 1，建議跑跨 session /code-review（layer 2）」 | 階段 6 旗標 | layer 提示 |
| SM-7 | 多特徵同時命中 + max-agents cap 不足 | 如同段落命中外部整合+公開簽名，max-agents=3（base 佔 2，僅 1 extra 額度） | 依優先序（architecture > adversarial/edge > consumer-perspective，見 review-engine 點 5）取最高，其餘特徵觸發但被 cap 截斷 → 輸出截斷提示 | 優先序 + cap | review adaptive |

---

## 段落劃分原則

依賴圖：**S1**（domain 框架）→ **S2**（build adapter）+ **S3**（消費者同步）並行 → 收尾。**並行前提**：S1 特徵清單 + 映射已定稿（S2/S3 依賴 S1 最終措辭；實作時依依賴錨點 drift check）。

**語義約束**（S1/S2/S3 共享）：
- **通用風險特徵**（review-engine domain 定義，單一源）：`外部整合` / `公開簽名變更` / `跨模組` / `UC 數 >6`
- **特徵→agent 映射**（review-engine 單一源）：外部整合→adversarial、公開簽名變更→architecture+consumer、跨模組→architecture、UC>6→UC-split
- **build adapter 範圍（僅接線既有兩信號）**：IO 觸發→外部整合、簽名偵測→公開簽名變更。**跨模組特徵在 build 無 adapter**（build 無既有跨模組偵測；跨模組 ripple 交 SM-6 layer 旗標導向 layer 2，不在 build 新造偵測）。UC>6 由 EP UC 清單驅動（非 build diff）
- **依賴方向**：build→review-engine（adapter 提供 build 信號翻譯成通用特徵；review-engine domain **不列消費命令特有名詞**）

---

## S1: review-engine adaptive domain 框架

### Context
- **背景**：`skills/review-engine/SKILL.md:143` 點 5「>2 配置」當前措辭「opt-in，高風險 / 大變更」靠 LLM 語義判斷，會漏（低估風險的段落不升級 extra agent）
- **UC 引用**：更新 review-engine adaptive 行為（語義 opt-in → 機械特徵觸發框架）
- **依賴**：S1 是基礎，S2/S3 依賴
- **語義約束**：見段落劃分原則（通用特徵 + 映射 + 依賴方向；domain 零消費命令特有名詞）
- **基礎設施盤點**：review-engine/SKILL.md adaptive 段（既有，:128-150）；agent-review-cycle.md（執行範本，:51 引用單一源）
- **依賴錨點**：
  - `>2 配置` 點 5 → 定義 `skills/review-engine/SKILL.md:143` / 消費 `commands/claude/_common/agent-review-cycle.md:51`、`commands/build.md:152`
  - adaptive 段標題 → `skills/review-engine/SKILL.md`（`## review 執行預設`，rg 機械定位；行號可能 drift，以標題文字為準）
- **成功標準**：點 5 定義通用框架（特徵→agent 映射），特徵是 review 通用概念，不寫死消費命令名詞；消費命令提供特徵偵測（adapter）

### 修改要點（docs mode，無 Pseudo Code）
1. **`skills/review-engine/SKILL.md:143` 點 5 重寫**：
   - 「opt-in，高風險 / 大變更」→ 「**消費命令提供段落風險特徵 → 映射 extra agent**（機械觸發，非 LLM 語義判）」
   - 定義**通用風險特徵清單**：`外部整合` / `公開簽名變更` / `跨模組` / `UC 數 >6`
   - 定義**特徵→agent 映射**（單一源）：外部整合→adversarial、公開簽名變更→architecture+consumer、跨模組→architecture、UC>6→UC-split
   - **明文 DIP（純抽象，不舉消費命令例）**：「特徵偵測由消費命令提供（adapter）；review-engine 只定義映射框架（domain），**不列消費命令特有名詞**（如不寫 build 的整合器/路徑覆蓋）」— 用泛化詞，零 adapter 名詞進 domain
   - **保留**：base ① clean + ② UC-anchored、max-agents cap、extra 優先序到 cap、絕不複製 lens（多樣性 > 數量）
2. **`skills/review-engine/SKILL.md:3` description**：description 現含「review 執行預設單一源（... / 視角 / ...）」；「視角」涵蓋 2-perspective vs dimension profile 分配。若 S1 改 adaptive 觸發（屬「視角分配」邊界），實作層判斷是否需同步「視角」措辭 — 標記供判斷

### 驗證策略（docs mode）
- **rg 殘留**：`rg "opt-in|高風險 / 大變更" skills/review-engine/SKILL.md` → 點 5 不再用 opt-in 為主觸發措辭
- **跨檔一致**：消費者（agent-review-cycle:51、build:152）引用新框架，無 drift
- **導航有效性**：`rg "外部整合|公開簽名變更|跨模組" commands/build.md commands/claude/_common/agent-review-cycle.md` → 消費端引用的特徵名存在於 domain（S1 定義）
- `/consistency skills/review-engine/SKILL.md`
- `/sync-sources`：review-engine adaptive 單一源（定義源 vs 消費者引用一致）
- **DIP 純度**：`rg "整合器|路徑覆蓋" skills/review-engine/SKILL.md` → 0 hits（domain 零消費命令特有名詞）

---

## S2: build adapter 接線（階段 4 映射 + 階段 6 layer 旗標）

### Context
- **背景**：`commands/build.md` 階段 4（:149-184）消費 review-engine adaptive。加「build 機械信號 → review-engine 通用特徵」映射接線。階段 6（:220-222）加 layer 旗標
- **UC 引用**：更新 build Agent Review 行為（機械觸發 extra）+ 階段 6 layer 提示
- **依賴**：S1（review-engine 框架定義後才能接線）
- **語義約束**：見段落劃分原則；映射用 review-engine 通用特徵名（build 不自創特徵名，只翻譯自己的信號）；**只接線 IO+簽名兩既有信號，不新造跨模組偵測**
- **基礎設施盤點**：build 階段 0 整合器（:57-65）、階段 2 路徑覆蓋（:132）、階段 4（:149-184，含 Step1 max-agents / Step2 審查模式 / judge-review / Apply Changes）、階段 6（:220-222 完成報告，現僅靜態輸出清單）
- **依賴錨點**：
  - 整合器 IO 觸發 → 定義 `commands/build.md:63` / 消費 S2 階段 4 映射
  - 路徑覆蓋新簽名偵測 → 定義 `commands/build.md:132` / 消費 S2 階段 4 映射
  - 階段 4 adaptive 引用 → `commands/build.md:152`
  - 階段 6 完成報告輸出 → `commands/build.md:222`（輸出清單內加 layer 旗標）
- **成功標準**：階段 4 有映射表（build IO+簽名→通用特徵→agent，**不含跨模組**）；階段 6 有 layer 旗標（新增非取代）；只接線既有兩信號

### 修改要點
1. **`commands/build.md` 階段 4 加獨立子段「#### adaptive 觸發映射」**（位置：Step 2 選擇審查模式 之後、judge-review 之前；不與既有 Step 衝突）：
   - 映射表「build 機械信號 → review-engine 通用特徵 → extra agent」：
     - 階段 0 整合器標記（:63 IO 觸發）→ `外部整合` 特徵 → adversarial agent
     - 階段 2 路徑覆蓋觸發（:132 新簽名/注入點）→ `公開簽名變更` 特徵 → architecture+consumer agent
   - **明文範圍**：只接線上述**兩個既有信號**（IO + 簽名）；**跨模組特徵在 build 無 adapter**（無既有偵測，不新造；跨模組 ripple 交階段 6 layer 旗標導向 layer 2）；UC>6 由 EP UC 清單驅動（非 build diff）
   - **明文 DIP**：build 是 adapter（提供特徵偵測 + 翻譯），review-engine 是 domain（定義映射）；build 階段 4 引用 review-engine 通用特徵名
   - **明文 cap**：extra 受 max-agents cap + 優先序（architecture > adversarial/edge > consumer-perspective，見 review-engine 點 5）；多特徵命中 + cap 不足時取優先序最高，截斷其餘並輸出截斷提示（SM-7）
2. **`commands/build.md` 階段 6 完成報告輸出（:222 輸出清單內）加硬性 layer 旗標**：
   - **偵測條件**（階段 6 **新增**偵測分支，非既有）：跨模組（`git diff --name-only` 模組目錄計數 ≥2）或 公開簽名變更（路徑覆蓋觸發）或 整合器段落
   - 命中 → 輸出「⚠️ 本 build 僅 layer 1（AI 自洽天花板），此變更建議跑**跨 session /code-review**（layer 2）抓全貌漣漪 / 同 session 盲點」
   - **`:255` 軟提醒保留不動**（涵蓋 deliverable-review/illustrate/code-review 三建議，非只 code-review）— layer 旗標是**新增**硬性 code-review 導向旗標，不取代 :255
3. 確認 **base ①+② 不變**；extra 依映射 + max-agents cap + 優先序

### 驗證策略（docs mode）
- **rg 殘留**：`rg "adaptive 觸發映射|layer 旗標|建議跑.*code-review" commands/build.md` → 子段 + 旗標存在
- **跨檔一致**：階段 4 映射用 review-engine 通用特徵名（`外部整合`/`公開簽名變更`），非把 build 特有名詞塞進 review-engine
- **導航有效性**：階段 4 映射引用的 review-engine 特徵名存在於 review-engine domain（S1 定義）
- `/consistency commands/build.md`

---

## S3: 消費者同步（agent-review-cycle >2 配置）

### Context
- **背景**：`commands/claude/_common/agent-review-cycle.md:49-51`（>2 配置）是 build 階段 4 的 Agent Tool 執行範本，引用 review-engine 單一源。S1 改框架後確認同步
- **UC 引用**：更新 agent-review-cycle >2 配置（對齊 review-engine 新框架）
- **依賴**：S1
- **語義約束**：agent-review-cycle 引用 review-engine 單一源，不自創映射
- **基礎設施盤點**：agent-review-cycle.md:49-51（既有，純引用單一源）
- **依賴錨點**：
  - `>2 配置` → 定義 `commands/claude/_common/agent-review-cycle.md:51`（引用 review-engine）/ 消費 build 階段 4
- **成功標準**：agent-review-cycle >2 配置措辭與 review-engine 新框架一致；無 drift

### 修改要點
1. **`commands/claude/_common/agent-review-cycle.md:49-51` 同步**：
   - :49 標題「>2 配置（opt-in，高風險 / 大變更）」→ 對齊 review-engine 新措辭（機械特徵觸發）
   - :51 規則描述：保持純引用 review-engine 單一源（review-engine 點 5 改為特徵→agent 映射，agent-review-cycle 同步反映引用；**不自創映射定義**，避免雙定義 drift）
2. **確認其他消費者不受影響**（EP Review rg 實證）：code-review（六軸 dimension）/ep-review（F1-F5）/execution-plan（五維度）用 dimension profile，非 2-perspective >2 配置

### 驗證策略（docs mode）
- **rg 殘留**：`rg "opt-in|高風險 / 大變更" commands/claude/_common/agent-review-cycle.md`
- **消費者確認 rg**（EP 修改要點 2 點名，補入驗證策略）：`rg "opt-in|>2 配置" commands/code-review.md commands/ep-review.md commands/execution-plan.md` → 0 hits（確認消費者不受影響）
- **跨檔一致**：agent-review-cycle 與 review-engine 點 5 措辭一致（單一源）
- **導航有效性**：agent-review-cycle 引用的特徵名/映射存在於 review-engine domain
- `/consistency commands/claude/_common/agent-review-cycle.md`

---

## 整合策略

- S1 定義框架 → S2（build 接線：映射表 + layer 旗標）+ S3（agent-review-cycle 同步）並行（前提：S1 特徵清單+映射定稿）
- **整合驗證**：全鏈 `rg` review-engine adaptive 點 5 新措辭 → build（:152）/agent-review-cycle（:51）一致引用；layer 旗標在 build 階段 6（:222 輸出清單）；`:255` 軟提醒保留
- `/sync-sources`：review-engine adaptive 單一源機械驗證（定義源 vs 消費者引用一致）

## 收尾步驟（docs mode）

1. **CLAUDE.md Capabilities + Kanban**：元專案無 library Capabilities；ai-rules 自身 `.kanban/` 掃描確認是否建 EP 追蹤卡（本次為流程增強，無新外部 UC）；跳過或建追蹤卡
2. **SYSTEM-MAP**：ai-rules 無，跳過
3. **CLAUDE.md 更新（查證後多為空操作）**：`rg "adaptive|opt-in|>2 配置|觸發" commands/CLAUDE.md skills/CLAUDE.md` 確認 — EP Review rg 實證三處 CLAUDE.md 皆無 adaptive 文字 → **條件不成立 → 跳過**（S1 修改要點 2 的 description :3「視角」邊界由實作層判斷，預設不同步除非觸及）
4. **/audit-test**：docs mode 無 `.py` 測試，跳過
5. **docs mode 收尾替代**：受影響命令行為已反映 + `commands/CLAUDE.md` 命令索引同步（查證空操作）+ `/sync-sources`（review-engine adaptive 單一源）+ `/consistency`（review-engine / build / agent-review-cycle）

---

## EP Review Findings

> EP Review Cycle（3 Explore agent · F1-F5 維度 · top-down）findings + judge 決策。修正已寫入 EP 段落。

| ID | 嚴重度 | 檔案:行 | 問題 | 決策 | 處置 |
|----|--------|---------|------|------|------|
| F3-1/F-7/F5-1 | Critical | EP S2 映射表 / SM-3 | 「跨模組 diff≥2 模組」在 build.md 無既有偵測，與「複用非新造」核心宣稱矛盾 | ✅ 採納 | build adapter 移除跨模組（只接 IO+簽名）；跨模組交 SM-6 layer 旗標導向 layer 2；domain 保留跨模組通用特徵（未來消費者可用） |
| F-5/F3-2/F5-3 | Important | EP S2 / SM-6 | layer 旗標 vs `:255` 軟提醒（涵蓋 deliverable/illustrate/code-review）取代關係模糊 | ✅ 採納 | layer 旗標**新增**非取代；`:255` 保留不動；S2 修改要點 2 明文 |
| F-4 | Important | EP S2 階段 4 | 映射表插入子段未釘死（階段 4 多子段） | ✅ 採納 | 新增獨立子段「#### adaptive 觸發映射」（Step 2 後、judge 前） |
| F5-2 | Important | EP SM | 漏 cap 不足降級 + 多特徵優先序場景 | ✅ 採納 | 補 SM-7；S2 映射表補 cap + 優先序明文 |
| F4-2 | Important | EP S3 驗證策略 | 漏自己點名的消費者確認 rg | ✅ 採納 | S3 驗證策略補消費者確認 rg |
| F3-3 | Suggestion | EP S1:75 | domain 語境舉 build 特有名詞（破 DIP 純度） | ✅ 採納 | S1 改純抽象（零 adapter 名詞）；S1 驗證補 DIP 純度 rg |
| F-3/F4-3 | Suggestion | EP 收尾 3 | CLAUDE.md 更新空操作未明示 | ✅ 採納 | 收尾 3 明文「查證條件不成立→跳過」 |
| F-6 | Suggestion | EP 語義約束 | UC>6 缺 adapter 對應說明 | ✅ 採納 | 語義約束 + SM-4 補「UC>6 由 EP UC 清單驅動」 |
| F4-1 | Suggestion | EP S1/S3 驗證 | 缺導航有效性 | ✅ 採納 | S1/S3 驗證補導航有效性 rg |
| F3-4 | Suggestion | EP S1 錨點 | 段標題 :128 半漂移 | ✅ 採納 | 改標題文字錨點（rg 定位，不依行號） |
| F-9 | Suggestion | EP 整合策略 | S2/S3 並行前提 | ✅ 採納 | 段落劃分原則補「並行前提：S1 定稿」 |
| F-1/F-2/F-8/F3-5 | — | — | 通過查證紀錄（錨點全驗證 / 消費者不受影響實證 / 驗證策略完整 / DIP 方向正確） | — | 無需動作 |

## Code Review Findings（layer 2, post-build judge）

> build 階段 6 layer 旗標命中（跨模組：skills/ + commands/）→ 跑獨立 /code-review（layer 2）→ /judge-review 評估。決策如下；實作已落地（followup verified — F1/F2/F3 全部通過，未引入新問題）。

| ID | 嚴重度 | 檔案:行 | 問題（查證 confirmed） | 決策 | 處置 |
|----|--------|---------|----------------------|------|------|
| F1 | Important | EP :43（SM-7）/ :113（S2） | EP 優先序 `adversarial > architecture > consumer` 過時 — build Agent Review 還原 agent type 後，真相源 review-engine:143 + build.md:192 已是 `architecture > adversarial/edge > consumer-perspective`，但 EP 未同步 | ✅ 採納 | EP SM-7 + S2 的優先序改 `architecture > adversarial`，與真相源統一（一行×2） |
| F2 | Suggestion | review-engine:143 | domain 含「（build 無既有偵測）」消費命令名，與同句 DIP 宣稱「不列消費命令特有名詞」輕微矛盾；build.md:188 已自述跨模組無 adapter，去掉不損失資訊 | ✅ 採納（已落地） | 去括號 build 狀態，改「`跨模組` 映射目前無 adapter 接線，保留供未來消費命令」 |
| F3 | Suggestion | build.md:182（映射表標題） | 表格標題「build 既有機械信號」涵蓋三行，但第三行 UC>6 標「半機械」、:188 範圍段歸「+UC 計數」非機械 — 定性不一致 | ✅ 採納 | 表格標題「build 既有機械信號」→「build 既有信號」（去「機械」，涵蓋三行含半機械 UC） |
