# EP: Dev Process 整脊 — 補架構紀律層 + 能力下沉 + 結構前移

> **整脊隱喻**：不是縫補 5 個既有 EP（`db0a42f`），而是把 dev process 當脊柱，用 Clean Architecture + DDD 重新校正排列。**補缺失的架構紀律層 + 能力下沉到可複用 skill + 結構確認前移到 pre-EP + 受眾靠產出區分而非命令**。
>
> **本 EP 位置**：`ai-analysis/execution-plans/dev-process/`(整脊工作群組目錄,master + 衍生 EP 放此;歸檔走 `execution-plans/_done/` 統一區)。
>
> **🔴 本 EP 是綱要 EP（blueprint），不直接 /build**。整脊任務跨 10+ 段都是中型變更,單一 EP 裝不下。本 EP 是整脊全貌綱要(段落依賴 + 吸收範圍 + 風險);**每段(S0-S8)→ 衍生子 EP（在 `dev-process/`）→ /build 子 EP**（見 S8）。/build 偵測本 EP 為 blueprint 會提示衍生、不腦補(S8 建立此機制)。

## 動機（self-contained 背景）

### 根本問題：體系缺一整層「架構紀律」

scan 證實（`rg "clean code|clean architecture|SOLID|分層|依賴規則|單一職責|bounded context" rules/ skills/`)：19 rules + 30 skills 裡，clean code / clean architecture / SOLID / DDD 設計精神 **0 處顯式存在**（3 個命中全是巧合：llm-output-convention「分層」=LLM 輸出分層、code-edit-constraints「依賴方向」=library→scripts、nt-query 是 grounding 用詞）。頂層 `ai-development-guide.md` 五章節（演化性思維 / 驗證約束 / UC-Driven / 量化鐵律 / Summary）**獨缺架構設計**。

體系有四種紀律 — 驗證紀律（acceptance-evidence）、流程紀律（UC-Driven/TDD）、工具紀律（lsp/bash）、協作紀律（commit-consent）— **獨缺「架構紀律」**。這解釋了實戰觀察「架構沒有太重視，不合 clean code 精神」：不是某個命令的縫隙，是整個體系缺一整層。

### 四個結構性問題（實戰浮現）

**問題①：結構確認太晚**。現狀結構審查在 post-EP（`/arch-review --ep`，[arch-review.md](../../../commands/arch-review.md) `:262-270`），EP 已寫完、結構已貴。Clean Architecture 核心順序是「先定 use case + 邊界，再寫細節」— 結構判斷該在寫 EP **之前**。

> **時機張力實證**：本 EP 自身的 post-EP 結構審查(見 judge-review RC-1/2/3,新 skill 邊界未銳利化)正好證明問題① — 若 pre-EP 就跑 whole-picture,這些邊界問題能在寫進 EP 前抓到,不必現在補。本 EP 是「過渡期」:在 pre-EP checkpoint(S2)建立前,仍需 post-EP 補審。

**問題②：結構審查能力綁死單一命令**。`/arch-review` 的機械能力（City Map / Pattern Radar / 重用枚舉 / LSP 查證）只在它內部，`/code-review` axis 3（[code-review.md](../../../commands/code-review.md) `:106-107`）、`/ep-review`（[execution-plan.md](../../../commands/execution-plan.md) `:215-275`）、`/illustrate` 各自闕如或重造。

**問題③：`/arch-review` 與 `/illustrate` 職責重疊**。兩者都做結構圖解，能力分散。

**問題④：review 鏈冗餘（arch→judge→code→judge）**。結構審查與正確性審查分開跑、judge 評估重複。若 code review 含結構（axis 3），即可合併成精簡鏈。

**共同根因**：dev process 缺架構紀律層 + 缺可複用結構能力 + 結構確認時機滯後 + review 鏈未精簡。

### 本 EP 範圍
(a) **補架構紀律層**（多點注入，頂層為核心）、(b) 機械能力下沉為 `architecture-viewport` skill、(c) `/arch-review` 命令移除（能力分流到 `/illustrate` + `/code-review`）、(d) 結構確認前移到 pre-EP（彈性化，討論中介入）、(e) commit SYSTEM-MAP 升格顯式收尾、(f) review 鏈精簡 recipe。**吸收** `db0a42f` 的 review-pipeline / execution-plan-hardening / agent-output / commit-gate 四個 EP。

**Scope out**：`ep-deep-work-redesign`（#12/#16 自主路由，與整脊主軸弱關聯，保留獨立）、#7 的 2.4 L4 runtime 分級（acceptance-evidence）、#17 spec↔code drift（doc-health）、#13 judge-review 持久化位置、#1 import 盤點/測試隔離。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S0** | **補架構紀律層（多點注入）**：S0a 頂層指南加章節 + S0b 編輯約束擴充 + S0c architecture-thinking skill + S0d api-design 對齊 + S0e validation-strategy skill | 無 |
| S1 | 新增 `architecture-viewport` skill — 機械能力下沉 | 無 |
| S2 | `/illustrate` 擴充 + **流程彈性化**（討論中介入）+ **軟 gate** | S1 |
| S3 | `/arch-review` 移除 — 刪命令；流程位置改 `/illustrate`；修改清單全 repo | S1 + S2 |
| S4 | EP review 換 Clean Arch 視角 + **top-down 審查順序** + **agents→skills 統一**探討 | S0 |
| S5 | `/code-review` axis 3 調用 S1 + **top-down**（結構先於正確性）| S1 |
| S6 | commit SYSTEM-MAP 顯式收尾 + 子目錄 EP 歸檔路徑適應 | 無 |
| S7 | `validation-strategy` 注入 build/commit | S0 |
| **S8** | **綱要 EP / 子 EP 結構支援**(ep_type blueprint/implementation + 衍生機制 + /build 偵測)— 整脊自己暴露的 dev process gap | 無 |
| 收尾 | 索引 + 受眾模型 + **review-pipeline recipe** + **綱要 EP 完成定義** + 歸檔 4 個既有 EP | 全部 |

**段落劃分**：S0 是架構紀律層（5 子點，頂層為核心）；S1 能力下沉；S2/S3 illustrate 相關連作；S4-S7 相對獨立引用 S0/S1。

**建議 build 順序**：S0 → S1 → S2 → S3（連作）→ S4 ∥ S5 ∥ S6 ∥ S7 → 收尾。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（吸收 `db0a42f` 四個藍圖 EP + 實戰經驗）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過；S6 的 SYSTEM-MAP 收尾是給消費專案用的通用 rules）。

### 掃描範圍
- 受影響命令：`commands/arch-review.md`（移除）、`commands/illustrate.md`、`commands/execution-plan.md`、`commands/code-review.md`、`commands/commit.md`、`commands/CLAUDE.md`、`commands/build.md`、`commands/ep-review.md`、`commands/deliverable-review.md`（後三者含 `/arch-review` 引用，S3 清理）
- 受影響根文件：`CLAUDE.md`（受眾模型）、`ai-development-guide.md`（S0a 加架構章節）、`skills/CLAUDE.md`（索引）
- 受影響 rules：`rules/code-edit-constraints.md`（S0b 擴充）、`rules/acceptance-evidence.md`（含 `/arch-review` 引用，S3 清理）
- 新增 skills：`skills/architecture-viewport/`、`skills/architecture-thinking/`、`skills/validation-strategy/`
- 受影響既有 skill：`skills/api-and-interface-design/`（S0d 對齊）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 結構 viewport（City Map/Flows/Boundaries/重用） | `commands/arch-review.md` | ✅ → S3 移除；能力分流 S1(skill)+S2(illustrate)+S5(code-review axis3) |
| 圖解技術概念/架構/流程 | `commands/illustrate.md` | ✅ → S2 擴充 + 流程彈性化 + 軟 gate |
| 段落式實作計畫書（含 EP Review） | `commands/execution-plan.md` | ✅ → S4 EP Review 換 Clean Arch 視角 + top-down |
| 深層思考六軸審查 | `commands/code-review.md` | ✅ → S5 axis 3 調用 skill + top-down |
| commit（lint → UC 狀態 → 提交） | `commands/commit.md` | ✅ → S6 SYSTEM-MAP 顯式收尾 + 子目錄歸檔 |
| 開發協作指南 | `ai-development-guide.md` | ✅ → S0a 補「架構設計紀律」章節 |
| 程式碼編輯約束 | `rules/code-edit-constraints.md` | ✅ → S0b 擴充 clean code 實作原則 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 架構設計紀律（Clean Arch + DDD 精神，頂層） | 📋 | `ai-development-guide.md`（S0a） |
| Clean code 實作紀律（SOLID/單一職責/依賴向內） | 📋 | `rules/code-edit-constraints.md`（S0b） |
| Clean Architecture + DDD 設計視角（深入） | 📋 | `skills/architecture-thinking/SKILL.md`（S0c） |
| 驗證策略紀律（e2e/replay>live/不重驗 pkg） | 📋 | `skills/validation-strategy/SKILL.md`（S0e） |
| 結構機械能力（可複用） | 📋 | `skills/architecture-viewport/SKILL.md`（S1） |
| pre-EP 結構 checkpoint（彈性、軟 gate） | 📋 | `commands/illustrate.md`（S2） |
| review 鏈精簡（code review 含 arch 合併） | 📋 | 收尾 recipe |

---

## Scenario Matrix（大型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 用戶與 LLM 討論新功能到一定程度 | 對話中、要決定方向時 | **提醒** `/illustrate` 畫提案結構（軟 gate：標註+提醒，不硬擋）→ 人判讀 → 直接 EP 或先 spec | 無 | pre-EP 結構 checkpoint |
| SM-2 | 人想看 EP/架構整體結構 | post-EP 或任意時點 | `/illustrate --ep` 渲染 city map/重用/邊界，人判讀（原 arch-review --ep 的活） | 無 | 結構 viewport |
| SM-3 | 機器審結構符合度 | `/code-review`（含 axis 3 結構） | top-down：先 axis 3 結構（調用 architecture-viewport skill）後細部正確性；產 finding | 無 | 六軸審查 |
| SM-4 | EP review agent 審 EP | `/execution-plan` EP Review | Clean Arch 視角（分層/邊界/use case）+ top-down；agent 引用 skill 統一 | 無 | 段落計畫 |
| SM-5 | commit 收尾 | `/commit` 最後一段 | 顯式三件：Capabilities + Kanban + SYSTEM-MAP | 無 | commit 顯式收尾 |
| SM-6 | 驗證策略選擇 | `/build` / `/commit` 驗證段 | e2e 優先；交易 replay >>> live；放 scripts/；不重驗 package（NT/bokeh/panel） | 無 | 驗證策略紀律 |
| SM-7 | 整脊完成反查 | `rg "/arch-review" .` | 全 repo 0 hits（流程圖/關係表/索引/受眾模型改 illustrate） | 無 | 結構 viewport 遷移 |
| SM-8 | 頂層架構精神 in context | 每次 session auto-load | `ai-development-guide.md`「架構設計紀律」章節生效（Clean Arch 分層 + DDD 邊界 + use case 驅動） | 無 | 架構設計紀律 |
| SM-9 | 實作碼遵循 clean code | `/build` 實作段 | `code-edit-constraints.md` 擴充的 SOLID/單一職責/依賴向內生效 | 無 | clean code 實作紀律 |
| SM-10 | review 鏈精簡 | 大型變更 review | `/code-review`（含 axis 3 結構）→ `/judge-review`（一次）；不再 arch→judge→code→judge 兩次 judge | 無 | review 鏈精簡 |

---

## S0: 補架構紀律層（多點注入，頂層為核心）

### Context
- **背景**：scan 證實體系 0 處 clean code 精神、頂層指南獨缺架構章節。靠單一 on-demand skill 不夠（不觸發就不載入）— 必須寫進**頂層 auto-load** 才能確保每次 session 在 context。故多點注入，以頂層為核心。
- **UC 引用**：新增「架構設計紀律」「clean code 實作紀律」「設計視角」「驗證策略紀律」
- **依賴**：無
- **語義約束**：clean code 精神是**視角/原則**（注入思考），**非架構模板**（不強制分層、不過度工程）。範例可用 mosaic（領域特定 OK），規則通用（否則違反「通用 rules 不依賴特定專案」）。
- **依賴錨點**：[ai-development-guide.md](../../../ai-development-guide.md)（五章節，無架構章節）、[code-edit-constraints.md](../../../rules/code-edit-constraints.md) `:17`（既有「依賴方向 library→scripts」，擴充點）、[api-and-interface-design/SKILL.md](../../../skills/api-and-interface-design/SKILL.md)（既有 Hyrum's Law/Validate at Boundaries，對齊點）、[acceptance-evidence.md](../../../rules/acceptance-evidence.md)（L1-L6，validation-strategy 引用）
- **成功標準**：
  - [ ] S0a：`ai-development-guide.md` 加「架構設計紀律」章節（與「驗證約束」「UC-Driven」並列）— Clean Architecture 分層依賴規則（domain←use case←adapter←infra）+ DDD bounded context + use case 驅動 + SOLID 精神總綱。**頂層 auto-load 核心**。
  - [ ] S0b：`rules/code-edit-constraints.md` 擴充 — 既有「依賴方向」之外補 clean code 實作原則：SOLID、單一職責、不洩漏實作細節、依賴向內。實作時 auto-load 生效。
  - [ ] S0c：`skills/architecture-thinking/SKILL.md`（新）— 詳細視角（三主線：依賴規則/bounded context/use case 驅動，各自在 spec/illustrate/EP/build 哪裡生效）+「視角非模板」明文 + mosaic 範例 + 與既有 skill 邊界
  - [ ] **bounded context vs module boundary 邊界明文**（RC-2）：bounded context（DDD 語義邊界）vs module boundary（介面合約,`api-and-interface-design`）— 呼叫端設計介面載 api-and-interface、檢視結構載 thinking
  - [ ] S0d：`skills/api-and-interface-design/SKILL.md` 對齊 — 既有 Hyrum's Law/Validate at Boundaries 補與 clean arch 分層對齊（邊界 = adapter 邊界）
  - [ ] S0e：`skills/validation-strategy/SKILL.md`（新）— e2e 優先 > 單元隔離；交易 replay >>> live；放 scripts/；不重驗 package（NT/bokeh/panel 主要 package，自己有測試，別重測內部）。引用 acceptance-evidence L3-L5 不重複。
  - [ ] **與 `test-driven-development` 邊界**（RC-4）：測試類型**選擇**（紀律,e2e/replay/live）vs RED/GREEN **流程**（TDD）— 層次不同,非重造 Test Classification

### 修改要點
1. **S0a `ai-development-guide.md`**：新增 `## 架構設計紀律` 章節（頂層總綱）— 三主線 + SOLID + 指向 architecture-thinking skill（深入）。簡潔（總綱非全書）。
2. **S0b `rules/code-edit-constraints.md`**：擴充實作紀律段（SOLID/單一職責/不洩漏/依賴向內）
3. **S0c `skills/architecture-thinking/SKILL.md`（新）**：三主線 + 流程注入點 + mosaic 範例 + 邊界（與 debugging/source-driven/acceptance-evidence）
4. **S0d `skills/api-and-interface-design/SKILL.md`**：補 clean arch 分層對齊段
5. **S0e `skills/validation-strategy/SKILL.md`（新）**：四紀律 + 判準 + 與 acceptance-evidence/quality-constraints 邊界

### 驗證策略（docs mode）
- **rg 閘門**：`rg "架構設計紀律|分層依賴|bounded context|use case 驅動" ai-development-guide.md` → 命中
- **rg 閘門**：`rg "SOLID|單一職責|依賴向內|不洩漏" rules/code-edit-constraints.md` → 命中
- **rg 閘門**：`rg "視角非模板|三主線" skills/architecture-thinking/SKILL.md` → 命中
- **rg 閘門**：`rg "e2e|replay.*live|不重驗" skills/validation-strategy/SKILL.md` → 命中
- **`/consistency`**：跑五檔（確認與既有 rules/skill 邊界不衝突）
- **模擬（SM-8/SM-9）**：給「新功能」→ 確認頂層架構精神 + 實作 clean code 生效

---

## S1: architecture-viewport skill（機械能力下沉）

### Context
- **背景**：`/arch-review` 機械能力綁死命令內部，下沉為 skill 讓四消費端共用。**skill 只給機械能力，不決定受眾**。
- **UC 引用**：新增「結構機械能力」
- **依賴**：無
- **語義約束**：**能力下沉、受眾保留** — skill 是列舉+查證機械能力，不渲染心智模型（illustrate 人 viewport 職責）、不產 finding 格式（code-review 機器職責）。A/B 軸靠消費命令產出形式區分。
- **依賴錨點**：能力來源 [arch-review.md](../../../commands/arch-review.md) `:83-164`（City Map 元件 A + 重用枚舉元件 D + Pattern Radar + 信心度）、`:185-206`（Phase 2 查證分工）。吸收 `ep-review-pipeline-grounding` 的 dep weight（`:83-97`）、reuse lifecycle、domain grounding（#17）。
- **成功標準**：
  - [ ] `skills/architecture-viewport/SKILL.md`：City Map 渲染（節點 + 依賴方向 + **dep weight** lean/heavy + 消費者數）、Pattern Radar（Enum/Fn/DataStruct + Jaccard + 信心度）、重用 lifecycle（實作後 re-review）、LSP 查證、**domain grounding**（外部框架語意強制查 stub/source 附 path:line）
  - [ ] 明文「機械能力，不決定受眾；消費命令決定產出給人/機器」
  - [ ] 與 `lsp-navigation`、`scan-project` 邊界（RC-1 銳利化）：**code 場景複用 scan-project dep_graph**（不重造 AST);**docs 場景 scan-project 不適用**（.py only）→ 自己 rg 跨檔畫命令/skill 拓樸
  - [ ] **domain grounding 獨立邊界**（RC-3）：review/結構審查時 grounding;與 `source-driven-development`（實作 grounding）/ `external-api-investigation`（runtime 調查）/ `nt-query`（能力查詢）區分,非第四個過載

### 修改要點
1. **`skills/architecture-viewport/SKILL.md`（新）**：從 arch-review.md `:83-206` 抽出機械能力重組。章節：City Map（含 dep weight）/ Pattern Radar / 重用 lifecycle / LSP 查證 / domain grounding / 機械分工（scan-project 枚舉 primary、lsp-architect 驗證 secondary）。開頭明文「機械能力，不決定受眾」。

### 驗證策略（docs mode）
- **rg 閘門**：`rg "dep weight|lean|heavy|Pattern Radar|Jaccard|domain grounding|不決定受眾" skills/architecture-viewport/SKILL.md` → 命中
- **跨檔一致**：skill 機械能力與 arch-review.md `:83-206` 對應
- **`/consistency`**：跑 skill 檔
- **模擬**：給「重型 helper 抽進 lean 廣用模組」→ 確認 dep weight flag 反向耦合（吸收 #14）

---

## S2: /illustrate 擴充 + 流程彈性化 + 軟 gate

### Context
- **背景**：`/illustrate` 加 city map/call stack/對話式 drill（吸收 arch-review 職責 A）。**流程彈性化**：illustrate 不是固定流程節點，是「討論到一定程度時的結構催化劑」— 用戶與 LLM 對話討論 → 提醒用 illustrate 畫提案結構 → 人判讀 → 直接 EP 或先 spec。**EP 是必備起點，spec 是可選前置**。
- **UC 引用**：更新「圖解」+ 新增「pre-EP 結構 checkpoint（彈性、軟 gate）」
- **依賴**：S1（illustrate 調用 architecture-viewport skill）
- **語義約束**：illustrate 成為**人類 viewport 結構探索載體**（B 軸）+ 通用圖解。**軟 gate**（F4）：pre-EP 是標註+提醒，不硬擋（保留前移價值又不卡流程）。對齊用戶「illustrate 是討論中催化劑，非固定節點」。
- **依賴錨點**：[illustrate.md](../../../commands/illustrate.md) `:18-22`（核心能力）、`:24-46`（現有程式碼優先）、`:79-89`（決策流程）；搬入 [arch-review.md](../../../commands/arch-review.md) `:166-181`（drill 指令）、`:185-206`（Phase 2 互動式）；流程圖 [commands/CLAUDE.md](../../../commands/CLAUDE.md) `:20-25`
- **成功標準**：
  - [ ] illustrate 加：city map（調用 S1，含 dep weight）、call stack（重要節點呼叫鏈）、對話式 drill（`city/flow/reuse/verify/boundary`）
  - [ ] **pre-EP checkpoint（彈性）**：流程非剛性「spec→illustrate→ep」，而是「對話討論 →〔提醒〕illustrate 結構化提案 → 確認 → EP（spec 可選前置）」。EP 必備、spec 可選。
  - [ ] **軟 gate 明文**：pre-EP 標註+提醒，不硬擋（避免流程摩擦；前移價值靠提醒而非強制）
  - [ ] 流程圖更新（[commands/CLAUDE.md](../../../commands/CLAUDE.md) `:20-25`）：對話 → illustrate（提醒）→ 確認 → execution-plan

### 修改要點
1. **`commands/illustrate.md` 核心能力**（`:18-22`）：加 city map/call stack/對話式 drill/結構 viewport（調用 S1）
2. **新增「pre-EP checkpoint（彈性 + 軟 gate）」段**：討論中介入（非線性 spec→illustrate→ep）+ 軟 gate 明文 + 引用 architecture-thinking（S0c）
3. **決策流程**（`:79-89`）：加「結構 viewport / pre-EP」分支
4. **supporting files**：可能新增 `illustrate-structure-viewport.md`（含從 arch-review 搬來的 drill 指令）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "city map|call stack|對話式|drill|pre-EP|軟 gate|討論.*催化" commands/illustrate.md` → 命中
- **跨檔一致**：illustrate 流程與 commands/CLAUDE.md 流程圖一致
- **`/consistency`**：跑 `commands/illustrate.md`
- **模擬（SM-1）**：給「對話討論新功能」→ 確認提醒 illustrate、軟 gate（不硬擋）、EP 必備 spec 可選

---

## S3: /arch-review 移除 + 流程位置遷移

### Context
- **背景**：能力已落地 S1（skill）+ S2（illustrate 吸收人 viewport）+ S5（code-review axis 3 吸收機器）。移除命令避免三處重複。post-EP/post-build 流程位置（[arch-review.md](../../../commands/arch-review.md) `:262-270`）改 `/illustrate`。
- **UC 引用**：移除「結構 viewport」命令入口（能力遷移）
- **依賴**：S1 + S2
- **語義約束**：**受眾靠產出區分不靠命令** — 人 viewport 結構判讀全程保留（載體換 illustrate，在 pre-EP/post-EP/post-build）。移除的是命令，不是能力。
- **依賴錨點**：刪 [arch-review.md](../../../commands/arch-review.md)；流程位置 `:262-270`、關係表 `:249-258` 遷移；[CLAUDE.md](../../../CLAUDE.md)（根）受眾模型、[commands/CLAUDE.md](../../../commands/CLAUDE.md) `:18-37`
- **成功標準**：
  - [ ] 刪除 `commands/arch-review.md`
  - [ ] **`rg "/arch-review" .` 全 repo → 0 殘留**（SM-7）。清理清單（F2 補全）：`commands/CLAUDE.md`、`commands/build.md`、`commands/ep-review.md`、`commands/deliverable-review.md`、`commands/execution-plan.md`、`commands/code-review.md`、`commands/commit.md`、`rules/acceptance-evidence.md`、`CLAUDE.md`（根）、memory `b-axis-human-acceptance-roadmap.md`
  - [ ] CLAUDE.md 受眾模型三層介入表：layer 3 結構軸 `/arch-review` → `/illustrate`
  - [ ] commands/CLAUDE.md 移除 `/arch-review`；`/illustrate` description 補「結構 viewport，三時點」
  - [ ] post-EP 配對：`/deliverable-review --ep`（方向）+ `/illustrate --ep`（結構）
  - [ ] `lsp-architect` agent（`agents/lsp-architect.md`，不引用 arch-review）保留 — 是 architecture-viewport skill 的查證 helper

### 修改要點
1. **刪 `commands/arch-review.md`**
2. **`commands/CLAUDE.md`**：流程圖 `:20-25`、命令索引移除 arch-review、illustrate description 擴充
3. **`CLAUDE.md`（根）**：受眾模型三層介入表 + 命令分類表，arch-review → illustrate
4. **rg 掃全 repo**：凡 `/arch-review` 引用改 `/illustrate`（清單見成功標準）
5. **memory**：`b-axis-human-acceptance-roadmap.md` 同步

### 驗證策略（docs mode）
- **rg 閘門**：`rg "/arch-review" .`（全 repo 含 memory）→ 0 hits（SM-7）
- **`/consistency`**：跑 CLAUDE.md / commands/CLAUDE.md（確認無斷引用）

---

## S4: EP review 換 Clean Arch 視角 + top-down + agents→skills

### Context
- **背景**：execution-plan EP Review Cycle（[execution-plan.md](../../../commands/execution-plan.md) `:215-275`）4 維度偏泛泛，改 Clean Arch + use case 視角（S0c architecture-thinking）。**top-down 審查順序**（B7）：先結構（分層/邊界）後細部正確性。**agents→skills 統一**（B12）：探討 agent 審查知識沉到 skill 統一引用，agent prompt 只組裝。兜底假設（#13）由 pre-EP illustrate 前置承擔。
- **UC 引用**：更新「段落式實作計畫書（含 EP Review）」
- **依賴**：S0c（architecture-thinking 視角）
- **語義約束**：保留 Writer/Reviewer 分離 + 適應式多 agent（既有機制），只換審查維度內容 + 加 top-down 順序。agent 知識沉 skill（DRY）。
- **依賴錨點**：[execution-plan.md](../../../commands/execution-plan.md) `:215-275`（EP Review Cycle）、`:229-238`（維度表）、`:251-266`（Fallback）、`:323-331`（流程位置 pre-EP）
- **成功標準**：
  - [ ] 維度表（`:229-238`）改 Clean Arch 視角：分層依賴 / bounded context / use case 覆蓋 / 兜底路徑驗證
  - [ ] **top-down 明文**：EP review 先結構（分層/邊界）後細部正確性
  - [ ] **agents→skills 統一探討**：agent prompt 引用 architecture-thinking + architecture-viewport（知識沉 skill）；探討 agent 能力是否該統一沉 skill（非各命令內嵌）
  - [ ] pre-EP checkpoint 寫入流程位置（`:323-331`）：對話 → illustrate → 確認 → execution-plan

### 修改要點
1. **`commands/execution-plan.md:229-238`**：4 維度改 Clean Arch 視角
2. **`:251-266` Fallback**：四維度改 Clean Arch 對應 + top-down 明文
3. **`:323-331` 流程位置**：加 pre-EP illustrate（彈性、軟 gate）
4. **agent prompt**：引用 architecture-thinking + architecture-viewport；加「agents→skills 統一」探討段

### 驗證策略（docs mode）
- **rg 閘門**：`rg "分層依賴|bounded context|use case 覆蓋|top-down|agents.*skills|統一.*引用" commands/execution-plan.md` → 命中
- **`/consistency`**：跑 `commands/execution-plan.md`
- **模擬（SM-4）**：給 EP → 確認 review 用 Clean Arch 視角 + top-down

---

## S5: /code-review axis 3 調用 architecture-viewport skill + top-down

### Context
- **背景**：`/code-review` axis 3（[code-review.md](../../../commands/code-review.md) `:106-107`）吸收原 arch-review 職責 B（機器結構符合度）。調用 S1 skill。**top-down**（B7）：axis 3 結構先於其他軸的正確性 — 先審結構（分層/邊界/重用），後審邏輯正確性。**review 鏈合併**（B5/SM-10）：code review 含結構（axis 3），故不再分開 arch review + judge，judge 跑一次。
- **UC 引用**：更新「六軸審查」
- **依賴**：S1
- **語義約束**：axis 3 仍**機器產 finding**（A 軸），調用 skill 取能力但產出形式不變。top-down 是審查順序（結構先），不改軸定義。
- **依賴錨點**：[code-review.md](../../../commands/code-review.md) `:63-73`（軸表，Architecture `:67`）、`:106-107`（axis 3）、`:128`（審查者自證）
- **成功標準**：
  - [ ] axis 3 調用 architecture-viewport skill（city map/dep weight/重用/LSP 查證）
  - [ ] **top-down 明文**：六軸審查結構（axis 3）先於細部正確性（Correctness 等）
  - [ ] 明文「axis 3 與 illustrate 用同一 skill，axis 3 產機器 finding（A 軸）、illustrate 渲染給人（B 軸）」
  - [ ] **review 鏈合併**：code review 含結構 → judge 一次（流程位置段反映）

### 修改要點
1. **`commands/code-review.md:106-107` axis 3**：補「調用 architecture-viewport skill」+ 受眾明文 + top-down
2. **`:63-73` 軸 agent prompt**：Architecture 軸引用 architecture-viewport + architecture-thinking
3. **流程位置段**：反映 review 鏈合併（code review 含 arch → judge 一次）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "architecture-viewport|top-down|axis 3.*skill|review 鏈|judge.*一次" commands/code-review.md` → 命中
- **`/consistency`**：跑 `commands/code-review.md`
- **模擬（SM-3/SM-10）**：給 diff → 確認 axis 3 調用 skill + top-down + judge 一次

---

## S6: commit SYSTEM-MAP 顯式收尾 + 子目錄 EP 歸檔

### Context
- **背景**：commit 收尾現「Capabilities + Kanban（大型/中型）」+「SYSTEM-MAP（如果存在）」。SYSTEM-MAP 升格**顯式三件**。**子目錄 EP 歸檔**（F3）：EP 可能在 `dev-process/` 子目錄，歸檔跨目錄 mv 到 `execution-plans/_done/`（統一歸檔區，不另開子目錄 _done/）。
- **UC 引用**：新增「commit 顯式收尾三件」
- **依賴**：無
- **語義約束**：⚠️ ai-rules 元專案無 SYSTEM-MAP.md。S6 是給**消費專案**用（rules 寫「有就顯式更新」，元專案正當跳過）。`execution-plans/_done/` 是所有 EP 統一歸檔區，子目錄 EP 跨目錄 mv 過去（不改 _done/ 設計、不另開子目錄 _done/）。
- **依賴錨點**：[commit.md](../../../commands/commit.md) 階段 3（Capabilities + Kanban）+ 階段 6（EP 歸檔 mv）；[execution-plan.md](../../../commands/execution-plan.md) `:291-296`（收尾步驟 2 SYSTEM-MAP）
- **成功標準**：
  - [ ] commit 階段 3 改「顯式收尾三件」：Capabilities ✅ + Kanban Done + SYSTEM-MAP 狀態更新（原子操作）
  - [ ] SYSTEM-MAP 從「如果存在」改「消費專案有就顯式更新；ai-rules 元專案正當跳過」
  - [ ] **子目錄 EP 歸檔**：commit 階段 6 / execution-plan 收尾補「EP 可能在子目錄（如 dev-process/），歸檔 mv 到 `execution-plans/_done/`（跨目錄，_done/ 統一）」
  - [ ] 對齊 ai-development-guide 三層文件體系

### 修改要點
1. **`commands/commit.md` 階段 3**：標題改「顯式收尾三件」；SYSTEM-MAP 升格 + 適用對象明文
2. **`commands/commit.md` 階段 6 / `commands/execution-plan.md:291-296`**：補子目錄 EP 歸檔路徑（跨目錄 mv 到 execution-plans/_done/）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "顯式收尾|三件|子目錄.*歸檔|跨目錄|_done" commands/commit.md commands/execution-plan.md` → 命中
- **`/consistency`**：跑 commit.md（確認與 execution-plan 收尾一致）

---

## S7: validation-strategy 落地注入

### Context
- **背景**：S0e 的 `validation-strategy` skill 注入 build/commit 驗證段。對齊 acceptance-evidence L3-L5 + quality-constraints 消費端驗證。
- **UC 引用**：更新「驗證策略紀律」落點
- **依賴**：S0e
- **語義約束**：注入是「引用 skill 決策樹」非複製內容。
- **依賴錨點**：[build.md](../../../commands/build.md) 驗證段；[execution-plan.md](../../../commands/execution-plan.md) `:140-149`（驗證策略段）；[spec.md](../../../commands/spec.md) `:81-91`（風險分級 POC）
- **成功標準**：
  - [ ] build 驗證段引用 validation-strategy（決定測試類型：e2e 優先、交易 replay、放 scripts/）
  - [ ] execution-plan 驗證策略段（`:140-149`）引用 validation-strategy + architecture-thinking
  - [ ] EP 段落「驗證策略」範本補「交易優先 replay；不重驗 package（NT/bokeh/panel）」

### 修改要點
1. **`commands/build.md` 驗證段**：引用 validation-strategy
2. **`commands/execution-plan.md:140-149`**：引用 validation-strategy
3. **EP 段落驗證策略範本**：補 replay>live / 不重驗 pkg

### 驗證策略（docs mode）
- **rg 閘門**：`rg "validation-strategy|replay.*live|不重驗" commands/build.md commands/execution-plan.md` → 命中
- **`/consistency`**：跑兩檔

---

## S8: 綱要 EP / 子 EP 結構支援（dev process 巢狀 EP）

### Context
- **背景**：本 master EP 是首個綱要 EP 實例 — 整脊跨 10+ 段都是中型變更,單一 EP 裝不下。但 grep 證實 `/build`、`/execution-plan` **0 處**「綱要/master/衍生/子 EP/nested」概念。`/build` 階段 0 對段落缺 Pseudo Code 的處置是「自行補上/自行推斷」（[build.md](../../../commands/build.md) `:44-45`）— 直接 build 綱要 EP 會把藍圖段落當實作段落,**build LLM 腦補淺版**（如 S0a 架構章節寫淺）,整脊品質塌。需補 dev process 支援大型任務的綱要 + 子 EP 結構。
- **UC 引用**：新增「綱要 EP（blueprint）/ 實作 EP（implementation）類型」+「衍生子 EP 機制」
- **依賴**：無（獨立;與 S4 同改 `/execution-plan`）
- **語義約束**：**綱要 EP 觸發條件明確**（任務 ≥ N 段都是中型變更,每段本身需完整 EP 規劃深度）— 避免小型任務硬拆（過度工程）。**遞迴止境**：S8 建立機制,本身用傳統 implementation EP 衍生做（機制建立前是過渡期,靠標記 + 人工衍生）;機制建立後未來綱要 EP 有正式支援。
- **依賴錨點**：[build.md](../../../commands/build.md) `:44-45`（階段 0 段落結構快檢 + 「自行補上」處置）、[execution-plan.md](../../../commands/execution-plan.md)（段落設計標準 + EP 類型落點）、[commit.md](../../../commands/commit.md)（EP 歸檔）
- **成功標準**：
  - [ ] **EP 類型**：`/execution-plan` 加 `ep_type`（blueprint 綱要 / implementation 實作,預設）。綱要 EP 段落是藍圖層級（描述要做什麼 + 依賴 + 吸收）+ 每段標「→ 衍生子 EP（路徑）」;不含可實作 Pseudo Code
  - [ ] **/build 階段 0 偵測**：掃 `ep_type` — blueprint → **不直接 build**,提示「逐段衍生子 EP」（列段落 + 建議子 EP 路徑 + build 順序）;implementation → 正常逐段實作。直接修「自行補上腦補」災難路徑
  - [ ] **子 EP 繼承**：衍生時標 `parent: <master EP 路徑>` + 繼承該段 Context/依賴/吸收範圍;子 EP 是完整 implementation EP（Context + 修改要點 + 驗證策略 + Scenario Matrix）,可獨立 /build
  - [ ] **觸發條件文檔**：何時用綱要 EP（任務 ≥ N 段都是中型變更）vs implementation（小型/單一中型）— 避免過度工程
  - [ ] **/commit 歸檔**：綱要 EP 在所有子 EP build + commit 後才歸檔 master

### 修改要點
1. **`/execution-plan`**：加 `ep_type` 概念 + 綱要 EP 結構（段落表 + 衍生子 EP 標記）+ 衍生機制（子 EP 繼承 master 脈絡）+ 觸發條件
2. **`/build` 階段 0**：加 `ep_type` 偵測,blueprint → 提示衍生（修 `:44-45` 「自行補上」災難路徑）
3. **`/commit`**：綱要 EP 歸檔邏輯（子 EP 全完成才歸檔 master）
4. **`commands/CLAUDE.md`**：`/execution-plan` description 補「ep_type（blueprint/implementation）」

### 驗證策略（docs mode）
- **rg 閘門**：`rg "ep_type|blueprint|綱要 EP|衍生子 EP|不直接.*build" commands/execution-plan.md commands/build.md` → 命中
- **`/consistency`**：跑兩檔
- **模擬**：給綱要 EP（blueprint）→ 確認 /build 提示衍生非腦補;給 implementation EP → 正常 build

---

## 收尾

### review-pipeline recipe（#B5，精簡鏈）
在 [commands/CLAUDE.md](../../../commands/CLAUDE.md) 核心流程段補「變更類型 → review 序列」recipe（code review 含 arch 合併，judge 一次）：
- **討論/規劃期**：`/illustrate`（結構，人 viewport，可多次；pre-EP 軟 gate 提醒）
- **review 期**：post-build 可選 `/illustrate`（漂移檢查 + 重造盲點，人 viewport B 軸 — 不礙流程,懷疑結構漂移/重造既有時才用）→ `/code-review`（六軸，含 axis 3 結構 = arch 吸收，top-down，A 軸機器）→ `/judge-review`（評估 findings，**一次**）
- **不再** arch→judge→code→judge 兩次 judge

### 受影響索引同步
- `commands/CLAUDE.md`：流程圖（pre-EP illustrate 彈性 checkpoint）、命令索引（移除 arch-review、擴充 illustrate）、review-pipeline recipe
- `skills/CLAUDE.md`：索引新增 architecture-viewport / architecture-thinking / validation-strategy（開發流程 + 架構與演進段）
- `CLAUDE.md`（根）：受眾模型三層介入表 layer 3（arch-review → illustrate）、命令分類表、受眾視角說明（能力下沉受眾保留）

### 綱要 EP 完成定義（S8 機制）
本 EP 是綱要 EP（blueprint），**不直接 /build**。完成定義 = 所有衍生子 EP（S0-S8 各一,在 `dev-process/`）build + commit + 歸檔。master EP 在最後一個子 EP 完成後歸檔 `execution-plans/_done/`。過渡期（S8 機制未建立前）：靠本 EP 標記 + 人工逐段衍生。

### 5 個既有 EP（`db0a42f`）處置
本 EP 吸收 review-pipeline / execution-plan-hardening / agent-output / commit-gate 四個；build 完成後歸檔 `execution-plans/_done/`（從 root 跨目錄 mv）。`ep-deep-work-redesign` **scope out 保留獨立**。

### 風險與緩解
- S3 移除 `/arch-review` 破壞肌肉記憶/文檔引用 → rg 全清（SM-7）+ illustrate description 標「原 arch-review 能力」
- S0 多點注入可能散落難維護 → 以頂層 `ai-development-guide.md` 為核心總綱，skill 是深入載體（單一真相源）
- S2 illustrate 職責變廣 → 模式/參數區分（`@ep`/`@dir`/主題），對話式引導
- master EP 跨 10+ 檔案 → 段落獨立驗收（每段 rg 閘門 + /consistency）；build 順序 S0→S1→S2→S3→S4∥S5∥S6∥S7→收尾

### 路徑備註（F1 修正）
本 EP 在 `ai-analysis/execution-plans/dev-process/`（深 3 層），所有 repo 檔案引用用 `../../../`（如 `../../../commands/`、`../../../CLAUDE.md`）。build 時新增引用須用此深度。
