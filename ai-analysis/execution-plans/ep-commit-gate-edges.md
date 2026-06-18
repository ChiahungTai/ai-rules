# EP: commit 閘門邊界精修 — stage3 觸發條件 + pre-existing lint 分流

## 動機（self-contained 背景）

`/commit` 兩個閘門的觸發/處置條件不夠精確，用粗略判準導致摩擦：

**閘門①：階段 3 觸發於「規模」而非「新 UC」**（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-16-dashboard-streaming-debug.md` §2.5，#5e）。[commit.md](../../commands/commit.md) `:130`「階段 3：Capabilities + Kanban 狀態更新（**大型/中型變更**）」— 觸發於變更規模。但跨模組大型 **bug fix 到既有 capability**（如 dashboard streaming：ui+trading+strategies，但本質修「BarBridgeActor live K-line streaming」既有 ✅ 能力）兩者都不適用：不新增 UC、不搬 Done（修既有能力非新功能）。AI 得自行推理「這是 bug fix 非 new UC → 跳過」。與 [ai-development-guide](../../ai-development-guide.md) 變更規模分級矛盾（小型 bug fix 本就不需 UC，但 stage3 沒對齊這條）。

**閘門②：階段 1 pre-existing lint 無分流判準**（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-18-multi-session-review-chain-and-lint-scoping.md` 摩擦 B，#15B）。[commit.md](../../commands/commit.md) `:186`「pre-existing 問題也需在此時處理：加 per-file-ignores / type: ignore 或直接修」— 全處理，與 [code-edit-constraints](../../rules/code-edit-constraints.md)「不混合範疇」直接衝突。現狀要嘛全修（混合範疇）、要嘛全卡（commit 推不動）。#15B 實證：build commit 遇 5 個 pre-existing mypy errors（trading unused-ignore ×3 + lab demo ×2），build 沒碰這些模組，糾結是否該在此 commit 修。

**共同根因**：兩個閘門用「規模 / 全處理」粗略判準，缺「是否新 UC」「順手 vs 另開」的精確分流。

**本 EP 範圍**：S1 stage3 觸發條件改「新 UC」、S2 pre-existing lint 分流。純 commit.md 改動。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | 階段 3 觸發條件從「規模」改「是否新 UC」 | 無 |
| S2 | 階段 1 pre-existing lint 分流判準（順手修 vs 另 `/lint-fix`） | 無 |

兩段獨立、各自可驗收，同屬 commit 閘門邊界。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（本 EP 源自 #5e + #15B）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過）。

### 掃描範圍
- [commands/commit.md](../../commands/commit.md)（`:130` 階段 3、`:186` pre-existing lint）— 兩段都在此檔

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| commit（lint 閘門 → UC 狀態確認 → message → 提交） | `commands/commit.md` | ✅ → S1 精修 stage3 觸發、S2 補 pre-existing 分流 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| bug fix 到既有 capability 的 commit（跳過 stage3） | 📋 | `commands/commit.md` 階段 3（S1） |
| pre-existing lint 分流（順手 vs 另 `/lint-fix`） | 📋 | `commands/commit.md:186`（S2） |

---

## Scenario Matrix（中型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 跨模組 large bug fix（修既有 capability） | 變更 large 但無新 UC | **跳過** stage3（不盤點 Capabilities/Kanban/Done） | 無 | bug-fix commit |
| SM-2 | 新功能 / 新 UC | 變更含新 UC | 執行 stage3（Capabilities ✅ + Kanban Done + EP 歸檔） | 無 | commit（既有） |
| SM-3 | pre-existing lint 無風險 ≤3 行同型別 | unused-ignore 移除、ns-preserve 標註精確化 | **順手修**，本 commit 含，message 標「pre-existing lint 清理」 | 無 | pre-existing 分流 |
| SM-4 | pre-existing lint 跨模組/複雜/需設計判斷 | lab demo Iterator→Generator 要改邏輯 | **標記另 `/lint-fix`**，不卡本次 commit，commit 後提示 | 無 | pre-existing 分流 |

---

## S1: 階段 3 觸發條件從「規模」改「新 UC」

### Context
- **背景**：`:130` 觸發於「大型/中型變更」。但 bug fix 到既有 capability（即使跨模組 large）不新增 UC、不搬 Done。#5e 實證：dashboard streaming 跨 ui+trading+strategies，本質修既有 ✅ 能力，AI 得自行推理跳過 stage3。與 ai-development-guide「小型 bug fix 不需 UC」矛盾。
- **UC 引用**：新增「bug fix 到既有 capability 的 commit」
- **依賴**：無
- **語義約束**：觸發判準是「**是否新 UC**」（語義）非「規模」（機械）— bug fix 即使 large 也跳過；新 UC 即使 medium 也執行
- **依賴錨點**：`commands/commit.md:130`（階段 3 標題與觸發條件）
- **成功標準**：
  - [ ] `:130` 觸發條件從「大型/中型變更」改「**是否新 UC**」：新 UC → 執行；bug fix 到既有 capability（即使 large）→ 跳過
  - [ ] 補判準：如何判斷「新 UC vs 既有 capability fix」— 新增 public capability / 新 UC ID → 新 UC；修既有能力行為（含跨模組）→ bug fix
  - [ ] 對齊 ai-development-guide 變更規模分級（小型 bug fix 不需 UC）

### 修改要點
1. **`commands/commit.md:130` 階段 3 標題/觸發**：「Capabilities + Kanban 狀態更新（**新 UC 變更**）」+ 判準段：「新 UC（新增 capability / 新 UC ID）→ 執行；bug fix 到既有 capability（即使跨模組 large）→ 跳過（不新增 UC、不搬 Done）」
2. 對齊引用 ai-development-guide 變更規模分級

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "大型/中型變更|新 UC 變更|是否新 UC" commands/commit.md` → 舊詞 0 hits、新詞命中
- **`/consistency`**：跑 `commands/commit.md`
- **模擬（SM-1）**：給「跨模組 large、修既有 ✅ capability」→ 確認跳過 stage3
- **模擬（SM-2）**：給「新功能新 UC」→ 確認執行 stage3

---

## S2: 階段 1 pre-existing lint 分流判準

### Context
- **背景**：`:186`「pre-existing 問題也需在此時處理」全處理，與 code-edit-constraints「不混合範疇」衝突。#15B 實證：5 個 pre-existing mypy（build 沒碰的模組），糾結是否該在此 commit 修。
- **UC 引用**：新增「pre-existing lint 分流」
- **依賴**：無
- **語義約束**：分流判準 = 「無風險 + ≤3 行 + 同型別」→ 順手修；「跨模組/複雜/需設計判斷」→ 另 `/lint-fix`
- **依賴錨點**：`commands/commit.md:186`（pre-existing lint 處置段）
- **成功標準**：
  - [ ] `:186` 加分流判準：
    - **順手修**：pre-existing 若「無風險 + ≤3 行 + 同型別問題」（unused-ignore 移除、標註精確化）→ 本 commit 含，message 標「pre-existing lint 清理」
    - **另 `/lint-fix`**：pre-existing 若「跨模組/複雜/需設計判斷」（lab demo Iterator→Generator 改邏輯）→ 標記不卡本次，commit 後提示 `/lint-fix`
  - [ ] 解與 code-edit-constraints「不混合範疇」的衝突（順手修限無風險同型別，非混合）

### 修改要點
1. **`commands/commit.md:186`** pre-existing 處置段：加分流判準（順手修 vs 另 `/lint-fix`）+ 判準表
2. 順手修的「message 標 pre-existing lint 清理」納入階段 5 message 生成

### 驗證策略（docs mode）
- **rg 閘門**：`rg "順手修|另.*lint-fix|pre-existing.*分流|≤3 行" commands/commit.md` → 命中
- **`/consistency`**：跑 `commands/commit.md`（確認與 code-edit-constraints「不混合範疇」不再衝突）
- **模擬（SM-3）**：給「unused-ignore ×3」→ 確認順手修 + message 標
- **模擬（SM-4）**：給「lab demo Iterator→Generator」→ 確認標另 `/lint-fix`、不卡 commit

---

## 收尾

- **受影響命令行為已反映**：commit stage3 觸發 + pre-existing 分流 — `commands/CLAUDE.md` 命令索引 `/commit` description 同步（補「stage3 觸發於新 UC；pre-existing lint 分流」）。
- **Scope out**：不動 build 階段的 lint/mypy（build 已每段跑 mypy，見 [build.md](../../commands/build.md) `:117`）；不動 `/lint-fix` 命令本身（它是 pre-existing 的承接者，非改動標的）。
- **與 code-edit-constraints 對齊**：S2 順手修限「無風險 + 同型別」，不構成「混合範疇」（混合是指不同功能變更交織，非同型別 lint 清理）— `/consistency` 驗證此對齊。
