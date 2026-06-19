# EP: S0 補架構紀律層(architecture-discipline)

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)(整脊綱要 S0 段展開)
> **本 EP**:master 綱要 S0 的 implementation 展開 — 補體系缺失的架構紀律層,多點注入以頂層為核心。過渡期(master S8 綱要 EP 機制未建立)手動衍生,標 parent。

## 動機（self-contained 背景）

scan 證實(`rg "clean code|clean architecture|SOLID|分層|依賴規則|單一職責|bounded context" rules/ skills/`):19 rules + 30 skills 裡 clean code / clean architecture / SOLID / DDD 設計精神 **0 處顯式存在**(3 命中皆巧合)。頂層 [ai-development-guide.md](../../../ai-development-guide.md) 五章節(演化性思維 / 驗證約束 / UC-Driven / 量化交易專屬鐵律 / Summary)**獨缺架構設計**。

體系有四種紀律(驗證 / 流程 / 工具 / 協作),獨缺**架構紀律**。靠單一 on-demand skill 不夠(不觸發不載入)→ 必須寫進**頂層 auto-load**(ai-development-guide)+ 實作 auto-load(code-edit-constraints),搭配深入 skill。故多點注入,頂層為核心。

**本 EP 範圍**(master S0 五子點):S0a 頂層指南加章節 + S0b 編輯約束擴充 + S0c architecture-thinking skill + S0d api-and-interface-design 對齊 + S0e validation-strategy skill。

**Scope out**:S1 architecture-viewport skill(master 另段)、S2-S8(master 其他段)、skill 內部 mosaic 範例的完整 domain 模型(本 EP 只放範例指標,非重造 mosaic 架構)。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S0a** | `ai-development-guide.md` 加「架構設計紀律」章節(頂層 auto-load 核心) | 無 |
| **S0b** | `code-edit-constraints.md` 擴充 clean code 實作原則(SOLID/單一職責/不洩漏/依賴向內) | 無 |
| **S0c** | 新增 `skills/architecture-thinking/SKILL.md`(深入視角,頂層指向它) | 無 |
| **S0d** | `skills/api-and-interface-design/SKILL.md` 對齊 clean arch 分層(RC-2 邊界) | 無 |
| **S0e** | 新增 `skills/validation-strategy/SKILL.md`(驗證紀律) | 無 |

5 子點獨立、可平行。建議順序 **S0a(頂層核心)→ S0b → S0c ∥ S0d ∥ S0e**。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### 掃描範圍
- [ai-development-guide.md](../../../ai-development-guide.md)(S0a 加章節)
- [rules/code-edit-constraints.md](../../../rules/code-edit-constraints.md)(S0b 擴充,:17 既有「依賴方向」)
- `skills/architecture-thinking/SKILL.md`(S0c 新)
- [skills/api-and-interface-design/SKILL.md](../../../skills/api-and-interface-design/SKILL.md)(S0d 對齊)
- `skills/validation-strategy/SKILL.md`(S0e 新)
- [skills/CLAUDE.md](../../../skills/CLAUDE.md)(收尾索引)

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 開發協作指南 | `ai-development-guide.md` | ✅ → S0a 補「架構設計紀律」章節 |
| 程式碼編輯約束 | `rules/code-edit-constraints.md` | ✅ → S0b 擴充 clean code 實作原則 |
| 穩定 API / 介面設計 | `skills/api-and-interface-design/` | ✅ → S0d 補 clean arch 分層對齊 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| Clean Architecture + DDD 設計視角(深入) | 📋 | `skills/architecture-thinking/SKILL.md`(S0c) |
| 驗證策略紀律(e2e/replay>live/不重驗 pkg) | 📋 | `skills/validation-strategy/SKILL.md`(S0e) |

---

## Scenario Matrix（中型變更,docs mode — 觸發/預期行為為文檔語境:rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 每次 session auto-load | 頂層 ai-development-guide 載入 | 「架構設計紀律」章節在 context — Clean Arch 分層 + DDD 邊界 + use case 驅動 + SOLID 精神 | 無 | 開發協作指南 |
| SM-2 | 實作碼寫作 | `/build` 實作段 | code-edit-constraints 的 SOLID/單一職責/依賴向內生效 | 無 | 程式碼編輯約束 |
| SM-3 | spec/EP/build 設計決策 | 設計時需架構視角 | architecture-thinking skill 載入(三主線注入點) | 無 | 設計視角 |
| SM-4 | 驗證策略選擇 | `/build`/`/commit` 驗證段 | validation-strategy:e2e 優先 / replay>live / scripts/ / 不重驗 pkg | 無 | 驗證策略紀律 |
| SM-5 | 設計介面 vs 檢視結構 | 設計 API / 檢視整體 | api-and-interface-design(介面合約)vs architecture-thinking(分層視角)邊界清晰,呼叫端知載哪個(RC-2) | 無 | 介面設計 / 設計視角 |

---

## S0a: ai-development-guide.md 加「架構設計紀律」章節(頂層核心)

### Context
- **背景**:頂層指南 5 章節獨缺架構。補一章「架構設計紀律」(與「驗證約束」「UC-Driven」並列),讓 clean code/clean arch/DDD 精神每次 session auto-load 在 context。這是多點注入的核心(單一真相源總綱)。
- **UC 引用**:更新「開發協作指南」
- **依賴**:無
- **語義約束**:**總綱非全書** — 章節簡潔(三主線 + SOLID + 指向 architecture-thinking skill 深入),不把 clean code 全書塞進頂層(頂層要精簡,噪音容忍度低)。「視角非模板」明文(不強制分層)。
- **依賴錨點**:[ai-development-guide.md](../../../ai-development-guide.md) 五章節(演化性思維 / 驗證約束 / UC-Driven / 量化鐵律 / Summary);新章節建議插在「UC-Driven Development」之後(架構是 UC 的結構支撐)
- **成功標準**:
  - [ ] 新章節 `## 架構設計紀律`(在 UC-Driven 後、量化鐵律前)
  - [ ] 三主線:依賴規則(domain←use case←adapter←infra,依賴向內)+ bounded context(DDD 邊界、不跨域存取內部)+ use case 驅動(先問消費者要什麼行為)
  - [ ] SOLID 精神一句(SRP/OCP/LSP/ISP/DIP 指標,非逐條展開)
  - [ ] 「視角非模板」明文 + 指向 [architecture-thinking](../../../skills/architecture-thinking/SKILL.md) 深入
  - [ ] 範例用 mosaic(domain=策略訊號 / use case=回測下單 / adapter=NT·SJ·catalog / infra)— 領域範例,規則通用

### 修改要點
1. `ai-development-guide.md` 在 UC-Driven 章後加 `## 架構設計紀律`:三主線 + SOLID 指標 + 視角非模板 + 指向 skill + mosaic 範例

### 驗證策略（docs mode）
- **rg 閘門**:`rg "架構設計紀律|依賴規則|bounded context|use case 驅動|視角非模板" ai-development-guide.md` → 命中
- **`/consistency`**:跑 ai-development-guide.md(章節編號連續、與既有章節風格一致)
- **模擬(SM-1)**:給「session 起始」→ 確認架構章節 auto-load 在 context

---

## S0b: code-edit-constraints.md 擴充 clean code 實作原則

### Context
- **背景**:code-edit-constraints 是 auto-load 編輯約束,實作時就在 context。既有「依賴方向(library→scripts)」(`:17`)是分層雛形。擴充 clean code 實作原則,讓實作碼遵循 SOLID/單一職責/不洩漏/依賴向內。
- **UC 引用**:更新「程式碼編輯約束」
- **依賴**:無
- **語義約束**:實作紀律(非設計視角 — 那是 S0a/thinking)。聚焦「寫碼時遵循什麼」,與既有「優先編輯現有檔案」「品質優先」等條目並列。
- **依賴錨點**:[code-edit-constraints.md](../../../rules/code-edit-constraints.md) `:17`(「依賴方向:import 必須遵循依賴層級 library → scripts」— 擴充點)
- **成功標準**:
  - [ ] 擴充實作紀律段(在「依賴方向」附近):
    - **單一職責**:一個 class/function 一個改變理由(改 A 不該碰 B)
    - **依賴向內**:高層不依賴低層細節(dependency inversion,interface 在內層)
    - **不洩漏實作細節**:公開介面不暴露內部資料結構/型別
    - **SOLID 指標**:簡述 SRP/OCP/LSP/ISP/DIP 在實作的體現(非逐條展開)
  - [ ] 與 S0a 頂層章節呼應(頂層總綱、這裡實作落地)

### 修改要點
1. `code-edit-constraints.md` 在「依賴方向」段(`:17` 附近)擴充 clean code 實作原則(單一職責/依賴向內/不洩漏/SOLID 指標)

### 驗證策略（docs mode）
- **rg 閘門**:`rg "單一職責|依賴向內|不洩漏|SOLID" rules/code-edit-constraints.md` → 命中
- **`/consistency`**:跑 code-edit-constraints.md
- **模擬(SM-2)**:給「實作新 class」→ 確認遵循單一職責/依賴向內

---

## S0c: 新增 architecture-thinking skill(深入視角)

### Context
- **背景**:頂層 S0a 是總綱(精簡),深入視角(三主線在 spec/illustrate/EP/build 各自怎麼用 + 範例 + 邊界)放 on-demand skill。頂層指向它,需要深入時載入。
- **UC 引用**:新增「Clean Architecture + DDD 設計視角」
- **依賴**:無
- **語義約束**:**視角非模板**明文(注入思考,不強制分層、不過度工程)。規則通用、範例 mosaic。RC-2 邊界明文(bounded context vs module boundary)。
- **依賴錨點**:無(新檔)。參考 [debugging-and-error-recovery/SKILL.md](../../../skills/debugging-and-error-recovery/SKILL.md)(方法論 skill 範式)、[source-driven-development/SKILL.md](../../../skills/source-driven-development/SKILL.md)、[acceptance-evidence.md](../../../rules/acceptance-evidence.md)(邊界)
- **成功標準**:
  - [ ] `skills/architecture-thinking/SKILL.md`(新):
    - 三主線(依賴規則 / bounded context / use case 驅動),各自在 spec / illustrate / EP / build / review 哪裡生效
    - 「視角非模板」明文 + mosaic 範例(domain=策略訊號 / use case=回測下單 / adapter=NT·SJ·catalog / infra)
    - **RC-2 邊界明文**:bounded context(DDD 語義邊界)vs module boundary(介面合約,`api-and-interface-design`)— 設計介面載 api-and-interface、檢視結構載 thinking
    - 與既有 skill 邊界(debugging 除自己 code / source-driven grounding 於文檔 / acceptance-evidence 證據階層)
  - [ ] frontmatter `description` 含觸發詞(架構設計、clean architecture、分層、bounded context、use case 驅動、DDD)

### 修改要點
1. `skills/architecture-thinking/SKILL.md`(新):三主線 + 流程注入點 + 視角非模板 + RC-2 邊界 + mosaic 範例 + 既有 skill 邊界

### 驗證策略（docs mode）
- **rg 閘門**:`rg "視角非模板|三主線|bounded context.*module boundary|依賴規則" skills/architecture-thinking/SKILL.md` → 命中
- **`/consistency`**:跑 skill 檔
- **模擬(SM-3/SM-5)**:給「設計新功能」→ 確認 thinking 視角注入;給「設計 API vs 檢視結構」→ 確認 RC-2 邊界(載對 skill)

---

## S0d: api-and-interface-design 對齊 clean arch 分層(RC-2)

### Context
- **背景**:api-and-interface-design 已有 Hyrum's Law / Validate at Boundaries / Prefer Addition / Error Semantics(介面合約設計)。補與 clean arch 分層的對齊 — 邊界 = adapter 邊界(介面在內層,實作在外層)。這是 RC-2 邊界的另一端(讓 api-design 也標示與 thinking 的分工)。
- **UC 引用**:更新「穩定 API / 介面設計」
- **依賴**:無
- **語義約束**:對齊非重造 — 既有 Hyrum's Law 等不動,只補「邊界 = clean arch adapter 邊界」的視角連結。
- **依賴錨點**:[api-and-interface-design/SKILL.md](../../../skills/api-and-interface-design/SKILL.md) `:18`(「Validate at Boundaries」— 對齊點)
- **成功標準**:
  - [ ] 補一段「邊界 = clean arch adapter 邊界」:介面在內層(use case 定義 port)、實作在外層(adapter 實作) — 依賴向內
  - [ ] RC-2 邊界明文:本 skill = 介面合約設計(設計時);architecture-thinking = 分層視角檢視(檢視時)— 兩者互補

### 修改要點
1. `api-and-interface-design/SKILL.md` 在「Validate at Boundaries」(`:18`)附近補 clean arch adapter 邊界對齊段 + RC-2 邊界

### 驗證策略（docs mode）
- **rg 閘門**:`rg "adapter 邊界|clean arch|依賴向內|architecture-thinking" skills/api-and-interface-design/SKILL.md` → 命中
- **`/consistency`**:跑 skill 檔

---

## S0e: 新增 validation-strategy skill(驗證紀律)

### Context
- **背景**:實戰驗證紀律(e2e 優先、交易 replay>live、放 scripts/、不重驗 package)散在 acceptance-evidence/quality-constraints。獨立 skill 讓 build/commit 驗證段引用。對齊 acceptance-evidence L3-L5 + quality-constraints 消費端驗證。
- **UC 引用**:新增「驗證策略紀律」
- **依賴**:無
- **語義約束**:引用 acceptance-evidence L3-L5 / quality-constraints 不重複(紀律載體,非證據階層重述)。RC-4 邊界(測試類型選擇 vs TDD 流程)。
- **依賴錨點**:[acceptance-evidence.md](../../../rules/acceptance-evidence.md)(L3-L5)、[quality-constraints.md](../../../rules/quality-constraints.md)(消費端驗證)、[test-driven-development/SKILL.md](../../../skills/test-driven-development/SKILL.md)(Test Classification,RC-4 邊界)
- **成功標準**:
  - [ ] `skills/validation-strategy/SKILL.md`(新):
    - 四紀律:e2e 優先 > 單元隔離;交易 replay >>> live(replay 可重現、live 不可控);放 `scripts/`;不重驗 package(NT/bokeh/panel 主要 package,自己有測試,別重測內部 — 只驗 public API 行為)
    - 判準:何時 e2e vs 單元、何時 replay vs live
    - RC-4 邊界:測試類型**選擇**(紀律)vs RED/GREEN **流程**(TDD)— 層次不同,非重造 Test Classification
    - 與 acceptance-evidence L3-L5 / quality-constraints 邊界(引用不重複)
  - [ ] frontmatter `description` 含觸發詞(e2e、replay、驗證策略、測試類型、不重驗 package)

### 修改要點
1. `skills/validation-strategy/SKILL.md`(新):四紀律 + 判準 + RC-4 邊界 + acceptance-evidence/quality-constraints 邊界

### 驗證策略（docs mode）
- **rg 閘門**:`rg "e2e|replay.*live|不重驗|scripts/|測試類型.*選擇" skills/validation-strategy/SKILL.md` → 命中
- **`/consistency`**:跑 skill 檔
- **模擬(SM-4)**:給「交易功能驗證」→ 確認選 replay 非 live、放 scripts/、不重驗 NT 內部

---

## 收尾

### 受影響索引同步
- [skills/CLAUDE.md](../../../skills/CLAUDE.md):索引新增 `architecture-thinking`(開發流程段,spec/EP/build 設計視角)+ `validation-strategy`(品質與審查段,驗證紀律)
- `ai-development-guide.md` 新章節指向 architecture-thinking(S0a→S0c 連結)
- code-edit-constraints(S0b)與頂層章節(S0a)呼應

### 風險與緩解
- S0 多點注入可能散落難維護 → **S0a 頂層為單一真相源總綱**,skill 是深入載體;頂層改、skill 跟(單向)
- S0c/scope thinking 過重(變模板)→「視角非模板」明文 + 範例 mosaic 但規則通用
- RC-2/RC-4 邊界在 S0c/S0d/S0e 三處寫,可能不一致 → /consistency 驗證三處邊界描述一致

### 回母 EP
本 EP 完成(master S0 build+commit)後,master 綱要 S0 段標 ✅。master 整脊完成 = 所有子 EP(S0-S8)完成。
