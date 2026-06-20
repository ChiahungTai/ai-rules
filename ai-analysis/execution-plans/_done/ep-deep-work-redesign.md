# EP: deep-work 解耦 — 自主執行模式 vs 無人值守 + 非 build 任務模式

## 動機（self-contained 背景）

`/deep-work` 把兩個正交概念綁死，導致兩類真實摩擦（來源：兩筆 flow-feedback）：

**綁定①：自主執行模式 ≡ 無人值守**。[commands/deep-work.md](../../commands/deep-work.md) `:11` 開宗「用戶已離開」、`:27-33`「前置：進入 auto-mode（強制）」— 非 auto-mode 就印警告並停。但「自主執行」（genius engineer：不問、自決、完整交付）與「無人值守」（auto-mode 防 prompt 卡死）是兩件事：
- 在場也可以「不微管、要 AI 自主跑完」（① 開、② 可關）— user 原話「deep work 有時候只是我不想管你好好做事，因為你是天才工程師」（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-18-deep-work-auto-mode-gate.md`）
- 離開才必須 auto（② 開，否則 prompt 卡死無人 flow）

現狀把 ① 等同 ② → 在場下 `/deep-work` 被 auto-mode gate 擋，浪費 turn 處理矛盾（同上 feedback 的 session 摘要：開頭 flag auto-mode 前置、警告無人值守卡權限）。

**綁定②：deep-work 階段 build 導向**。`:37-45` dispatch「ARGUMENTS = 非 /build → 用 deep-work 自己的階段」；但自有階段（`:49-94`：實作/驗證/`pytest`/demo/`/audit-test`）是 build 導向。對規劃鏈任務（`/deep-work /execution-plan`、`/spec`、`/ep-review`）語意錯位 — 規劃的「實作」= 寫 EP/POC、「驗證」= EP Review agent 審，不是 pytest。user 原話「Deep work 有時候不會只處理 build, 所以要小心這件事」（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-18-nt-margin-deep-work-design.md`，type-2）。

**本 EP 範圍**：解耦 ①②（S1）+ 非 build 任務模式（S2）。不動 build 階段本身（build 是委派標的，非 deep-work 自有）。`autonomous-execution` skill 同步：auto-mode 是「無人值守的權限策略」非「自主執行的前提」。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | deep-work 解耦：自主執行（永遠）+ auto-mode 降為 heads-up（非 gate） | 無 |
| S2 | 非 build 任務模式：dispatch 到該命令自有流程，deep-work 只疊行為模式 | S1 |

**段落劃分**：S1 是核心解耦（行為模式 vs 權限策略），單獨可用 — 即使不做 S2，S1 讓在場 `/deep-work` 不再被擋。S2 處理非 build 的階段錯位，疊在 S1 之上。兩者獨立驗收。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（本 EP 源自兩筆 flow-feedback，非 kanban 卡）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過：ai-rules 自身無跨域功能狀態總覽）。

### 掃描範圍
- [commands/deep-work.md](../../commands/deep-work.md)、[skills/autonomous-execution/SKILL.md](../../skills/autonomous-execution/SKILL.md)（受影響）
- [commands/build.md](../../commands/build.md)（委派標的，確認不動）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 自主實作（用戶離開時的完整交付） | `commands/deep-work.md` | ✅ → S1 重構（解耦自主/無人）+ S2 補非 build 模式 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 在場自主執行（genius engineer，不微管） | 📋 | `commands/deep-work.md` S1（auto-mode heads-up 非 gate） |
| 非 build 任務的自主執行（規劃/審查鏈） | 📋 | `commands/deep-work.md` S2（dispatch 非 build 命令自有流程） |

---

## Scenario Matrix（中型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 在場下 `/deep-work /build` | user 在場、非 auto-mode | 直接跑（委派 build 階段 0-6），prompt 浮現讓 user 順手批；**不 gate、不停** | 無 | 自主實作 / 在場自主 |
| SM-2 | 離開下 `/deep-work` | user 離開、非 auto-mode | heads-up：「你會離開嗎？離開請 auto-mode 或 `/at` 排程接續，否則 prompt 卡」— 提示非阻擋 | 無 | 自主實作 |
| SM-3 | `/deep-work /execution-plan`（規劃鏈） | ARGUMENTS = 非 /build 的命令 | dispatch 到該命令自有流程；deep-work 只疊「自主+不問+完整交付」行為，**不套 build 導向階段**（pytest/demo/audit-test） | 無 | 非 build 自主 |
| SM-4 | `/deep-work /build`（既有） | ARGUMENTS = /build | 委派 build（不變） | 無 | 自主實作 |
| SM-5 | `/deep-work` 裸任務描述（非命令） | ARGUMENTS = 任意描述 | 用 deep-work 自有階段（深度理解→實作→驗證）— 保留（裸任務通常是實作） | 無 | 自主實作 |

---

## S1: 解耦自主執行 vs 無人值守

### Context
- **背景**：`:27-33` 把 auto-mode 當 deep-work 前置 hard gate。但自主執行（行為）與無人值守（權限）正交。解耦後：自主執行 mode 永遠開（deep-work 本質）；auto-mode 是「離開時的權限策略」，在場可忽略。
- **UC 引用**：更新既有「自主實作」+ 新增「在場自主執行」
- **依賴**：無
- **語義約束**：與 S2 共享「deep-work = 行為模式（mode），非流程骨架（procedure）」— 此原則 `:39` 已有，S1 強化其與 auto-mode 解耦
- **依賴錨點**：`commands/deep-work.md:27-33`（auto-mode 前置段）、`:11`（「用戶已離開」開宗）
- **成功標準**：
  - [ ] `:11` 開宗改為「自主執行 mode（不問、自決、完整交付）」，移除「用戶已離開」的等同
  - [ ] `:27-33` auto-mode 段從「強制 gate」改為「heads-up」：在場可忽略、離開才需 auto-mode（或 `/at` 排程接續）
  - [ ] 移除「非 auto-mode → 印警告並停下」的 hard stop；改「非 auto-mode → 提示（在場可忽略；離開建議 auto-mode 或 `/at`）」
  - [ ] `skills/autonomous-execution/SKILL.md` 同步：auto-mode 是「無人值守的權限策略」非「自主執行的前提」（`:8` "when user should not be disturbed" 框架擴展涵蓋「在場但不打擾」）

### 修改要點
1. **`commands/deep-work.md:11` 開宗**：「自主實作引擎。**自主執行 mode：不問、自決、完整交付。** 至於 permission — 在場你會看到 prompt、離開才需 auto-mode。」（移除「用戶已離開」預設）
2. **`:27-33` auto-mode 段**重構為 heads-up：
   - 標題「前置：auto-mode（heads-up，非 gate）」
   - 在場：忽略 auto-mode，prompt 浮現讓 user 批
   - 離開：需 auto-mode（`claude --permission-mode auto`）或 `/at` 排程接續，否則 prompt 卡死
   - 移除「不靜默降級成互動模式硬跑」的停機邏輯（在場本就是互動 + 自主）
3. **`skills/autonomous-execution/SKILL.md:8`**：「Methodology for autonomous implementation — full self-directed execution whether the user is present-but-hands-off or away. All questions deferred to a completion report; permission strategy (auto-mode) is orthogonal, needed only when away.」

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "強制|用戶已離開|不靜默降級" commands/deep-work.md` → 0 hits（舊 gate 語言清除）
- **rg 鍘門**：`rg "heads-up|自主執行 mode|在場" commands/deep-work.md` → 命中（新框架）
- **跨檔一致**：`skills/autonomous-execution/SKILL.md` 的 auto-mode 框架與 deep-work 一致（兩處都「auto-mode = 離開權限策略，非自主前提」）
- **`/consistency`**：跑 `commands/deep-work.md` 自洽性
- **模擬（SM-1）**：給 AI「在場、非 auto-mode、/deep-work /build」情境 → 確認直接跑、不停、不警告擋
- **模擬（SM-2）**：給「離開、非 auto-mode」→ 確認 heads-up 提示 auto-mode/`/at`，但不 hard stop

---

## S2: 非 build 任務模式（規劃/審查鏈 dispatch）

### Context
- **背景**：`:37-45` dispatch「非 /build → 用 deep-work 自己的階段（`:49-94`）」。但自有階段（實作/驗證/pytest/demo/`/audit-test`）是 build 導向。對規劃鏈（`/execution-plan`、`/spec`、`/ep-review`、`/ep-validate`）語意錯位 — 規劃的「實作」= 寫 EP/POC、「驗證」= EP Review agent 審，不是 pytest。
- **UC 引用**：新增「非 build 任務的自主執行」
- **依賴**：S1（行為模式 vs 流程骨架的解耦框架）
- **語義約束**：deep-work 對非 build 命令「只疊加行為模式（自主+不問+完整交付+錯誤自癒+語音通知），不疊 build 導向階段」— 命令的自有流程是 procedure，deep-work 是 mode
- **依賴錨點**：`commands/deep-work.md:37-45`（dispatch 段）、`:49-94`（自有階段）
- **成功標準**：
  - [ ] dispatch 段新增第三類：「ARGUMENTS = 其他 `/命令`（`/execution-plan`、`/spec`、`/ep-review`、`/ep-validate` 等規劃/審查命令）→ dispatch 到該命令自有流程；deep-work 只疊行為模式，**不執行**自有階段 1-5（pytest/demo/audit-test 不適用規劃鏈）」
  - [ ] 自有階段段（`:49`）標註「僅適用 ARGUMENTS = 裸任務描述（非命令）」— 避免 build 導向階段被誤套到規劃鏈
  - [ ] 規劃鏈的「驗證」對應：`/execution-plan` 的 EP Review、`/ep-validate` 的 POC — 由該命令流程自帶，非 deep-work 階段 4 pytest

### 修改要點
1. **`:37-45` dispatch 段**擴充三類：
   - ARGUMENTS = `/build <EP>` → 委派 build（既有，不變）
   - ARGUMENTS = 其他 `/命令`（規劃/審查：`/execution-plan`、`/spec`、`/ep-review`、`/ep-validate`、`/code-review` 等）→ **dispatch 到該命令自有流程**；deep-work 疊加「自主+不問+完整交付+錯誤自癒+語音通知」行為；**跳過自有階段 1-5**（build 導向，不適用）
   - ARGUMENTS = 裸任務描述 → 用自有階段（既有）
2. **`:49` 自有階段段**加註：「以下階段僅適用 ARGUMENTS = 裸任務描述（非 /命令）。/build 委派 build；其他 /命令 dispatch 到該命令流程。」
3. **階段 4 驗證、階段 5d `/audit-test`**：標註「build/實作任務適用；規劃鏈任務的驗證由該命令自帶（如 EP Review）」

### 驗證策略（docs mode）
- **rg 閘門**：`rg "dispatch 到該命令|規劃鏈|跳過自有階段" commands/deep-work.md` → 命中
- **跨檔一致**：dispatch 的命令清單與 [commands/CLAUDE.md](../../commands/CLAUDE.md) 核心流程命令一致
- **`/consistency`**：跑 `commands/deep-work.md`
- **模擬（SM-3）**：給「/deep-work /execution-plan」→ 確認 dispatch 到 execution-plan 流程（含 EP Review），**不**跑 deep-work 階段 4 pytest
- **模擬反模式（SM-4）**：給「/deep-work /build」→ 確認仍委派 build（既有行為不破壞）

---

## 收尾

- **受影響命令行為已反映**：`/deep-work` 解耦（自主 vs 無人）+ 非 build 模式 — `commands/CLAUDE.md` 命令索引 description 同步（`/deep-work` 補「在場/離開皆可，非 build 任務 dispatch 該命令流程」）。
- **Scope out（明確不在本 EP）**：不動 `commands/build.md`（build 是委派標的）；不動 agent-workflow 的 auto-mode classifier 機制本身（只改 deep-work 如何對待它）；不動 `/at`（已是「離開接續」的正交機制，S1 引用它而非改它）。
- **風險與緩解**：S1 移除 hard stop 後，若用戶真離開又沒開 auto-mode，deep-work 會卡在 prompt。緩解：heads-up 明確提示 auto-mode/`/at`；且 `/at` 是既有的「離開接續」正解。SM-2 驗證 heads-up 不 silent。
