---
description: "human-review 命令的 domain 層 — 判準 4(命名/設計質疑)+ 判準 5(mixed-tree scope framing)+ 編排 audit-test + 誠信 stance。被 /human-review 委託。"
when_to_use: "委託載入（by /human-review）。判準 4/5 是 human-review 獨有價值（4 分散承載、5 完全無既有），沉此 skill 避免散落 drift。"
---

# human-review — 放大鏡判準 domain 層

> 承載 `/human-review` 的**獨有判準（4/5）+ 編排 + 誠信 stance**。通用審查邏輯（severity / confidence / 審查者自證）在 [review-engine](../review-engine/SKILL.md)；測試反模式偵測在 [audit-test](../../commands/audit-test.md)；本 skill 不重造，只補 human-review 獨有部分。

## 判準 4：質疑命名/設計（AI 產出的命名/設計盲點）

AI 寫 code 時犯三類命名/設計錯誤，human-review **預設質疑**（不假設 AI 命名正確）：

### 4a 命名碰撞

符號名與既有概念碰撞，造成語義混淆。

- 機械：LSP `workspaceSymbol` 查同名候選 + 讀定義確認語義是否真相同
- 範例：domain class `CashAccount`（現金累算器）與 NT `AccountType.CASH`（帳戶類型）— 同名不同概念，讀者混淆
- 判定：同名但語義不同 → finding（建議改名或文件標明區隔）

### 4b domain 一致性（名稱反映涵蓋）

命名/設計與 domain 模型不一致 — 名稱宣稱的涵蓋範圍 ≠ 實際定義。

- 機械：讀 Protocol / 型別 / 介面定義，比對「名稱宣稱」vs「實際涵蓋」
- 範例：`RateLimiter` Protocol 只定義 sync CM，名稱卻宣稱通用 → 涵蓋缺口（消費者標註的 instance 可能是 AsyncRateLimiter，不符 Protocol）
- 判定：名稱過廣 / 過窄 → finding（建議改名 / 補定義 / 拆分）

### 4c phantom API（AI 幻覺造的符號）— **限 source 側**

docstring / 註解 / 範例引用不存在的 method / class（AI 文檔幻覺）。

- **scope**：限 **source 側** docstring 幻覺；**test 側** docstring/assert 幻覈走 [audit-test](../../commands/audit-test.md) 角度 1（幽靈斷言 / 標題不符）
- 機械：rg / LSP 確認 docstring 提及的符號真實存在（定義點 + import 鏈）
- 範例：`__init__.py` docstring 引用 `throttle_request()`（不存在的方法，AI 幻覺）
- 判定：docstring 提及符號不存在 → finding（建議修正 docstring）

> ⚠️ **查證陷阱（dogfood 教訓）**：查 phantom API **不能只查「符號在不在」**，要查「引用語意對不對」— 符號存在但 docstring 放錯 class / 宣稱錯使用場景，仍是 finding（語意誤導，見 dogfood T4：符號 `_get_historical_bars_sync` 存在，但 docstring 放 `TestAsyncThrottle` 下暗示它是 throttle 使用，實際走 acquire）。

## 判準 5：mixed-tree scope framing（完全無既有承載）

> 既有 [git-workflow-and-versioning](../git-workflow-and-versioning/SKILL.md) 講「commit 前分組」（commit 視角），但 **review 面對 mixed working tree 怎麼 framing 結論**完全無承載。本 skill 補此缺口（human-review 最大省 prompt 價值之一）。

mixed working tree = 多 session / 來源的變更混在同一 working tree。human-review 審某 scope 時，working tree 常有無關變更（其他 session、pre-existing、unstaged）。

### 5a 分組（git status）

`git status` 看所有變更，按邏輯單元分組。

### 5b 標明誰的變更

每組標「**本次審查標的**」vs「**混入的其他來源**」。

### 5c 結論 framing 對應 scope

**結論只涵蓋審查範圍**，禁下全域結論。若 working tree 有未審變更，明確標「本次結論僅覆蓋 \<X\>，\<Y\> 未審」。

- 🔴 反例：`/code-review` 審 rate_limiter 子集，下「無 Critical」全域結論，但 working tree 有 `client.py`（production concurrency）未審 → `/judge-review` 才揭露
- ✅ 正解：標「無 Critical（**僅 rate_limiter 子集**）；`client.py` 未審，需另跑」

### 5d scope 判定 checklist（操作準則，避免落地模糊）

判定某變更屬於哪組的具體流程：

1. **本次標的** = user 明確指定的 dir/files（`/human-review <dir>` 參數）
2. **其他來源** = working tree 中不在本次標的的其他變更，進一步判定：
   - `git log --oneline -5 <file>` 看最近 commit author/timestamp — 與本次 session 不同的 author 或近期 commit = 其他 session / 來源
   - `git diff HEAD <file>` vs `git diff --cached <file>` — staged vs unstaged 區分
   - 變更內容與本次標的無邏輯關聯（不同模組/功能）= 獨立來源
3. **處理**：其他來源變更不審（不在本次 scope），但在報告結論**最後列「未審清單」**（標明檔名 + 推測來源）
4. **禁下全域結論**：即使 working tree 全綠，也只能說「本次標的（X）無 Critical」，不可說「全部無 Critical」

## 編排 audit-test（test 側）

human-review 的 test 段聚焦**判準 2（收窄：production wrapper 重複測試）**，其餘隱含覆蓋 / 反模式委外 audit-test：

| human-review test 段做（判準 2 收窄） | 委外 audit-test |
|---|---|
| **production wrapper 重複測試**（測 thin wrapper，但 wrapper 本體已被別處測；**且 wrapper 無獨立 production 入口**）| 反模式（幽靈斷言 / 同義反覆 / 空殼）— 角度 1 |
| test 與 production 脫節（docstring 語意誤導，如 dogfood T4）| 過時 / 死測試 — 角度 6 |
| —（其餘隱含覆蓋場景） | mock 健康度 / 覆蓋對稱 / 漸進驗證 |

**判準 2 收窄理由**：audit-test 角度 1（同義反覆）+ 角度 6（死測試）已覆蓋多數隱含覆蓋場景。human-review 判準 2 **真正獨有**的是「**production wrapper 重複測試**」判斷 — 測 wrapper 時要查 wrapper 是否有**獨立 production 入口**：

- 有獨立 production 入口（如 `throttle()` 被 production 直接呼叫）→ **保留**（覆蓋 production 路徑，非重複）
- 無獨立 production 入口（wrapper 只被 test 呼叫，本體已被別處測）→ **冗餘**（建議清除）

> 區分 audit-test 角度 6：角度 6 是「**動態過時**」（重構後 assertion 迎合實作）；本判準是「**production wrapper 重複**」（wrapper 無獨立入口）。兩者語義不同。

## 引用既有（判準 1/3/6，不重寫）

- **判準 1 YAGNI**：[collaboration-constraints](../../rules/collaboration-constraints.md) YAGNI check + [acceptance-evidence](../../rules/acceptance-evidence.md) filter trap
- **判準 3 嚴格不放水**：[collaboration-constraints](../../rules/collaboration-constraints.md) 反 Sycophancy + [review-engine](../review-engine/SKILL.md) 審查者自證
- **判準 6 大改動管控**：[ai-development-guide](../../ai-development-guide.md) 風險分級 + 規模分級 → EP / 直接改分流

## 誠信 stance（human-review 對 audit-test 的差異化）

human-review 不是機械列 finding（那是 audit-test），是**批判性追查**。stance：

- **read-only 偵測器**（非判官）：只產 finding + 建議，不自動改 code
- **查證必須**：inferred finding 必查證才報；未查標 `inferred ⚠️`（防 false positive）
- **撤銷透明**：查證推翻標 ❌ 保留，不刪（示範自我否證）
- **對抗性自查**：每個 finding 挑戰自己判斷（不放水，判準 3）
- **兩個查證陷阱（dogfood 實證，必記）**：
  1. **LSP-stale**：判死碼時 LSP `findReferences` 回可疑少（只 intra-file / 跨檔消失）→ 必須 rg 補（[lsp-navigation](../../rules/lsp-navigation.md) 條件式 fallback）。dogfood 實證：`throttle()` LSP 只回定義點，rg 才見 production 消費者
  2. **符號路徑**：**符號存在 ≠ 走你想當然的路徑**。看到符號被引用，別假設它走你預期的路徑 — **讀 body 確認**。dogfood 實證：`_get_historical_bars_sync` 符號存在且被 docstring 引用，初版假設它是 throttle 消費者；fresh-eyes 讀 body 才發現走 `async with`（acquire），不是 throttle
