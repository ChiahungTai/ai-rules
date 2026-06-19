# EP: S8 綱要 EP / 子 EP 結構機制（ep_type）+ task #8

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S8 段展開 — **整脊自身暴露的 dev process gap**）
> **ep_type**: implementation（本 EP 建機制本身,雖描述 blueprint 概念；欄位機械掃描避免自指誤判）
> **本 EP**: dev process 支援大型任務的**綱要 EP（blueprint）+ 子 EP（implementation）**結構。加 `ep_type`；`/build` 偵測 blueprint → 提示衍生（修「自行補上」腦補災難路徑）；子 EP 繼承；觸發條件；commit 歸檔。**task #8**：觸發條件 N 定值。

## 動機（self-contained 背景）

本 master EP 是首個**綱要 EP 實例** — 整脊跨 10+ 段都是中型變更，單一 EP 裝不下。但 grep 證實 `/build`、`/execution-plan` **0 處**「綱要/master/衍生/子 EP/nested」概念。`/build` 階段 0 對段落缺 Pseudo Code 的處置是「自行補上/自行推斷」（[build.md](../../../commands/build.md) `:44-45`）— 直接 build 綱要 EP 會把藍圖段落當實作段落，**build LLM 腦補淺版**（如架構章節寫淺），品質塌。需補 dev process 支援大型任務的綱要 + 子 EP 結構。

## 範圍
- **S8a**：[execution-plan.md](../../../commands/execution-plan.md) 加 `ep_type`（blueprint/implementation）+ 綱要 EP 結構（段落表 + 衍生子 EP 標記）+ 衍生機制（子 EP 繼承 master 脈絡）+ 觸發條件
- **S8b**：[build.md](../../../commands/build.md) 階段 0 偵測 `ep_type`（blueprint → 不直接 build，提示衍生，修 `:44-45` 腦補）+ [commit.md](../../../commands/commit.md) 綱要 EP 歸檔（子 EP 全完成才歸檔 master）+ [commands/CLAUDE.md](../../../commands/CLAUDE.md) `/execution-plan` description 補 ep_type

## task #8 決策：觸發條件 N
**綱要 EP 觸發**：任務含 **≥ 5 段都是中型變更**（每段本身需完整 EP 規劃深度：Context + 修改要點 + 驗證策略 + Scenario Matrix），單一 EP 裝不下 → 綱要 EP。N=5 為建議值（視任務複雜度調整，**避免過度工程** — 小型/單一中型任務用 implementation EP）。本整脊（10 段）是典型綱要 EP 實例。

## 依賴
無（獨立；與 S4 同改 execution-plan，S4 已完成）

---

## S8a: execution-plan ep_type 概念 + 綱要 EP 結構

### 成功標準
- [ ] **ep_type**（blueprint 綱要 / implementation 實作，預設 implementation）：frontmatter 或 EP 標頭欄位
- [ ] **綱要 EP 結構**：段落是藍圖層級（描述要做什麼 + 依賴 + 吸收範圍）+ 每段標「→ 衍生子 EP（路徑）」；**不含可實作 Pseudo Code**
- [ ] **衍生機制**：子 EP 標 `parent: <master EP 路徑>` + 繼承該段 Context/依賴/吸收範圍；子 EP 是完整 implementation EP，可獨立 /build
- [ ] **觸發條件文檔**：何時用綱要 EP（≥ 5 段中型變更）vs implementation（小型/單一中型）— 避免過度工程

### 驗證
- `rg "ep_type|blueprint|綱要 EP|衍生子 EP|implementation" commands/execution-plan.md`

---

## S8b: build 偵測 + commit 歸檔 + description

### 成功標準
- [ ] **build 階段 0 偵測** `ep_type`：blueprint → **不直接 build**，提示「逐段衍生子 EP」（列段落 + 建議子 EP 路徑 + build 順序）；implementation → 正常逐段（修 `:44-45`「自行補上」腦補災難路徑）
- [ ] **commit 綱要 EP 歸檔**：master EP 在所有子 EP build+commit 後才歸檔（commit 階段 3 EP 歸檔邏輯）
- [ ] **commands/CLAUDE.md** `/execution-plan` description 補「ep_type（blueprint/implementation）」

### 驗證
- `rg "ep_type|blueprint|不直接.*build|衍生子 EP" commands/build.md commands/commit.md commands/CLAUDE.md`

---

## 收尾
- 回母 EP：S8 build+commit 後，master S8 段標 ✅；**task #8 關閉**（觸發條件 N=5 定值）
- 風險：ep_type 是新概念 → 觸發條件明確（≥ 5 段中型）避免小型任務硬拆（過度工程）；過渡期靠標記 + 人工衍生（本整脊自身就是過渡期實例）
