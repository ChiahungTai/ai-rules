> **ep_type**: implementation
> **mode**: docs（變更全為 `.md` + `settings.json` JSON + `check_single_source.py` 字串常數；無 `.py` callable 符號變更）
> **來源**: `/spec` 需求摘要（arch-thinking 吸收 arch-viewport）+ 三輪深度思考

# EP: arch-thinking 吸收 arch-viewport（skill 合併）

## 實作總覽

將 `arch-viewport`（結構機械能力）併入 `arch-thinking`（設計視角），形成單一 skill「設計視角（上層）→ 結構機械（下層）」。動機：兩者幾乎總一起用、組合才有湧現價值（視角給方向 + 機械給事實）；分離只增引用負擔與漏接風險（三輪深度思考查證：真正獨立只吃單一的場景幾乎不存在，污染無受害者）。

**變更範圍**：1 個 skill 檔擴充 + 刪 1 個 skill 目錄 + ~18 處引用遷移 + `settings.json` 1 行 + `check_single_source.py` 1 行 note。

**不變**：消費端 UC（illustrate 結構 viewport / code-review axis 3 / ep-review F3 / execution-plan EP Review）行為照舊；受眾中性聲明保留；RC-2/RC-3 邊界保留。

---

## 段落 0：全域研究

### 引用清單（精確錨點，build 時直接定位）

**arch-viewport 引用（全部遷移/刪除）**：

| # | 位置 | 現況 | 遷移動作 |
|---|------|------|---------|
| V1 | `skills/arch-viewport/SKILL.md` | skill 本體（87 行） | 刪整個目錄（S3） |
| V2 | `settings.json:55` | `"Skill(arch-viewport)"` | 刪該行（S2） |
| V3 | `skills/CLAUDE.md:44` | 索引行 `arch-viewport` | 刪行；:28 arch-thinking 描述更新（S3） |
| V4 | `skills/review-engine/SKILL.md:20` | 並列 link | 改單一 arch-thinking（S1） |
| V5 | `skills/review-engine/SKILL.md:174` | 論述「arch-thinking + arch-viewport」 | 改單一（S1） |
| V6 | `skills/scan-project/scripts/check_single_source.py:58` | note 字串「共用 arch-viewport skill」 | 改 arch-thinking（S2） |
| V7 | `commands/CLAUDE.md:87` | 「調 arch-viewport skill」 | 改 arch-thinking（S1） |
| V8 | `commands/ep-review.md:20` | 並列 link | 改單一（S1） |
| V9 | `commands/ep-review.md:85` | 並列 link（視角/結構資料分工） | 改單一 + 保留分工描述「視角見 §一、機械見 §二」（S1） |
| V10 | `commands/execution-plan.md:295` | 並列 link | 改單一（S1） |
| V11 | `commands/execution-plan.md:298` | 論述「arch-thinking + arch-viewport」 | 改單一（S1） |
| V12 | `commands/code-review.md:68` | axis 表「調用 arch-viewport skill」 | 改 arch-thinking（S1） |
| V13 | `commands/code-review.md:81` | 「引用 arch-viewport + arch-thinking」（注意原文 viewport 在前） | 改單一 + 保留分工描述（S1） |
| V14 | `commands/code-review.md:107` | 「調用 arch-viewport skill」 | 改 arch-thinking（S1） |
| V15 | `commands/illustrate.md:9` | link（受眾對比） | 改 arch-thinking（S1） |
| V16 | `commands/illustrate.md:28` | link（mode A） | 改 arch-thinking（S1） |
| V17 | `commands/illustrate.md:102` | 並列 link（視角來源） | 改單一 + 保留分工描述（S1） |
| V18 | `commands/illustrate.md:132` | 能力下沉表 `arch-viewport skill` | 改 arch-thinking（S1） |
| V19 | `commands/illustrate.md:140` | 委託 link | 改 arch-thinking（S1） |
| V20 | `commands/claude/_common/illustrate-structure-viewport.md:4` | 能力來源 link（**三層路徑 `../../../skills/`**） | 改 arch-thinking，路徑 `../../../skills/arch-thinking/SKILL.md`（S1） |

**arch-thinking 引用（保留；並列處改單一、描述更新）**：`commands/{ep-review,execution-plan,code-review,illustrate}.md` 並列處 + `skills/review-engine/SKILL.md` 並列處 + `skills/CLAUDE.md:28` 索引 + `ai-development-guide.md:124`（單一，不動）+ `skills/api-and-interface-design/SKILL.md:34`（單一，不動）+ `commands/execution-plan.md:194/283/309`（單一，不動）。

**歷史註記（不動）**：`_done/ep-adaptive-mechanical-trigger.md:14`、`_done/ep-build-review-loop-correctness.md:28` — 歸檔 EP 歷史記錄，符合成功條件排除。

**不在遷移範圍（review 確認 positive）**：`agents/lsp-architect.md`（是 skill 引用的下游 helper，agent 本身不引用 arch-viewport skill，正確不列入）。

### 可複用基礎設施

- `~/.claude/skills` → `/Users/ctai/Github/ai-rules/skills` symlink（刪 repo 目錄即同步生效，無需另部署）
- `~/.claude/commands` → symlink（本 EP 不動 commands 目錄結構，只改內容）
- `check_single_source.py` 的 single-source invariant 機制（`skill_allowlist_coverage` L61-72 自動捕捉 settings ↔ skills 目錄對應；改 note 字串不影響邏輯）

### 風險假設

| 假設 | 風險 | 驗證 |
|------|------|------|
| 合併檔不遺失 viewport 關鍵能力 | 中（Pattern Radar 評分表、product-type 雙軌、RC-3 邊界易漏） | S0 逐項比對 viewport 原文 + 評分表逐格 checkpoint |
| 引用遷移無斷 link | 中（`_common/` 三層路徑、相對路徑層級） | S1 各引用點路徑驗證 + link 有效性 |
| settings.json 雙向 | 低（review 確認僅 L55 一處，無 deny） | S2 rg + JSON 對應 |
| 受眾中性論證基礎不崩 | 低（thinking 本身中性，三輪查證） | S0 保留聲明 + 三層次區隔 + /consistency |
| 合併檔 context 成本 | 低（thinking 83 + viewport 87 ≈ 170 行） | S0 行數 < 200 checkpoint |

---

## UC 盤點（docs mode）

**受影響命令/rules 清單**（元專案無 Capabilities 表格，docs mode 掃受影響清單）：

- `skills/arch-thinking/SKILL.md`（擴充，承載合併能力）
- `skills/arch-viewport/`（刪除）
- 消費端命令：`illustrate.md`、`code-review.md`、`ep-review.md`、`execution-plan.md`、`commands/CLAUDE.md`
- 消費端 skill：`review-engine/SKILL.md`、`skills/CLAUDE.md`、`api-and-interface-design/SKILL.md`（不動，單一引用）
- 支撐檔：`commands/claude/_common/illustrate-structure-viewport.md`
- 配置/invariant：`settings.json`、`scan-project/scripts/check_single_source.py`

**UC 變更類型**：無新 UC、無行為變更。本變更是**承載結構重組**（skill 合併 + 引用遷移），消費端 UC 行為不變。

**Kanban / SYSTEM-MAP**：元專案無 `.kanban/`、無 `SYSTEM-MAP.md` → 正當跳過（docs mode 元專案適用）。

---

## Scenario Matrix（docs mode，文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 合併檔被觸發 | 結構設計/審查/重造偵測查詢 | 單一 skill 同時載入視角+機械 | 無 | 結構審查（不變） |
| SM-2 | 引用遷移 | build 改 V4~V20 引用點 | 並列 → 單一；相對路徑指向 arch-thinking；`_common/` 三層路徑正確 | S1 rg 排除 `skills/CLAUDE.md`（歸 S3）= 0 | — |
| SM-3 | settings.json 雙向 | 合併完成 | 刪 `Skill(arch-viewport)`；`Skill(arch-thinking)` 保留；allowlist ↔ 目錄一一對應 | rg settings.json + ls skills/ | — |
| SM-4 | invariant 演化 | `check_single_source.py:58` | note 文字 arch-viewport → arch-thinking；layer 3 自標受眾邏輯不變 | `/sync-sources` 通過 | — |
| SM-5 | 殘留檢查 | rg 全 repo | `arch-viewport` 0 hits（排除 `_done/` 歷史註記） | `rg "arch-viewport" repo` | — |
| SM-6 | symlink 同步 | 刪 repo 內 arch-viewport/ | `~/.claude/skills/arch-viewport` 同步消失 | `ls ~/.claude/skills/` 無 arch-viewport | — |
| SM-7 | 受眾中性保留 | illustrate（人）/ code-review（機器）調用 | 合併檔仍明文「不決定受眾」+ 三層次區隔（受眾中性 / skill 邊界 / 不做） | `/consistency` arch-thinking | — |
| SM-8 | 輕量單一面向場景 | execution-plan 測試計畫（只要視角）、總綱導入 | 合併檔較大但順帶載機械無害（三輪查證：無獨立單一受害者） | 合併行數 < 200 | — |

---

## 段落劃分原則

垂直切片，依賴序：S0（合併檔）→ S1（引用指向新檔）→ S2（配置/invariant）→ S3（刪舊 + 全域驗證）。S1 依賴 S0（引用要對應合併後結構）；S3 依賴 S1（引用全遷移完才能刪目錄，否則斷 link）。

---

## S0：合併檔撰寫（arch-thinking SKILL.md 擴充）

### Context
- **UC 引用**：承載「結構審查能力（視角+機械）」，消費端 UC 行為不變
- **依賴**：無前置段落；本段是後續引用遷移的目標
- **語義約束**：與 S1 共享「合併後結構 = 視角（§一）→ 機械（§二）」；與 S3 共享「舊 arch-viewport 目錄刪除後，所有能力由 arch-thinking 承載」
- **基礎設施盤點**：`skills/arch-thinking/SKILL.md`（現 83 行）、`skills/arch-viewport/SKILL.md`（現 87 行，待吸收）
- **依賴錨點**：`arch-thinking` skill 目錄 `skills/arch-thinking/`（定義端）；消費見 V4~V20
- **成功標準**：合併檔含 viewport 全部關鍵能力（評分表逐格）；受眾中性聲明保留 + 三層次區隔；行數 < 200；/consistency 通過

### 修改要點（docs mode，不寫 pseudo code）

合併後 `arch-thinking/SKILL.md` 大綱結構：

```
# Architecture Thinking — Clean Architecture + DDD 視角 + 結構機械
[一句話：設計視角（怎麼判斷）+ 結構機械（怎麼查證），單一 skill 承載]

## 受眾中性（頂部，適用整個 skill）
[從 viewport L8 搬入頂部：機械能力不決定受眾，由消費命令（illustrate 人 / code-review 機器）決定]

## 一、設計視角（原 arch-thinking 三主線 — 人類/LLM 思考提示層）
### ① 依賴規則（Clean Architecture 分層）
### ② bounded context（DDD 邊界）
### ③ use case 驅動
### mosaic 範例
### RC-2 邊界（bounded context vs module boundary）

## 二、結構機械（原 arch-viewport，吸收 — agent 可執行工具層）
[段首標示：本段為 agent 可執行的機械能力（枚舉/查證/LSP 操作），與上層設計視角（人類/LLM 思考提示）層次不同，消費端按受眾取用]
### product-type 雙軌（code: scan-project dep_graph + lsp-architect / docs: rg；含 docs 排除細節：dep_graph 不適用但 code↔doc findings 仍可借）
### City Map 資料生成（dep weight / 反向耦合 flag；含 lean/heavy/consumer 數範例 + 反向耦合觸發範例）
### Pattern Radar（重用枚舉：三類 + 5 因子加權矩陣逐格保留 + 門檻 + lifecycle）
### domain grounding（RC-3 邊界）
### LSP 查證（call chain；保留對 rules/lsp-navigation.md 引用「本 skill 用 LSP 非重造決策樹」）

## 三、流程注入點（spec/EP/build/review 各階段怎麼用）
[只保留 thinking 原 3 主線 × 4 階段的流程注入結構；補充「機械能力在各階段如何被調用」（如 review 同時用視角查反向依賴 + 機械 LSP findReferences）。viewport「不做」不併入此段]

## 與既有 skill 邊界
[source-driven-development 整合為單條：同時涵蓋「thinking 結構視角非文檔查證」+「viewport domain grounding 是審查時 grounding 非實作 grounding」；其餘 debugging/acceptance-evidence/api-and-interface + RC-3 邊界保留]

## 不適用 / 不做
[合併兩者：thinking「不適用」（除錯/查 API/測試策略/強制套四層）+ viewport「不做」（渲染心智模型→illustrate / 產 finding→code-review / 決定受眾→消費命令）]
```

**frontmatter description**：合併兩組觸發詞 — 視角詞（架構設計/clean architecture/分層/bounded context/use case 驅動/DDD/SOLID/依賴方向）+ 機械詞（city map/dep weight/lean-heavy/Pattern Radar/重用枚舉/Jaccard/domain grounding/結構查證/**結構 viewport**/**反向耦合**/LSP 查證）。「結構 viewport」「反向耦合」是 viewport 原文 frontmatter 既有的觸發訊號，必須保留；「LSP 查證」沿用原文用語（非新增「LSP call chain」）。

**關鍵保留（逐項比對 viewport 原文 87 行，不可遺漏）**：
- **product-type 雙軌表**（code: scan-project dep_graph + lsp-architect / docs: rg）+ **docs 場景排除細節**：scan-project 的 code↔doc findings（掃 CLAUDE.md Capabilities）在 docs 場景仍可用，只有 dep_graph（.py AST）不適用 docs
- **Pattern Radar**：三類（Enum/Function/Data Structure）+ **5 因子加權矩陣逐格保留**（名稱相似/值簽名重疊/Import 路徑/呼叫圖重疊/欄位重疊>60% Jaccard，viewport L51-58）+ 門檻（HIGH≥7/MED 4-6/LOW 1-3）+ 重用 lifecycle（RC 實作後重跑查落點）
- **domain grounding**（未 grounding 標 `open` 非 `verified`）+ RC-3 邊界（與 source-driven/external-api-investigation/nt-query 四路區分）
- **LSP 查證表**（findReferences/incomingCalls/outgoingCalls）+ 機械分工（枚舉 primary / lsp-architect 驗證 secondary）+ 對 `rules/lsp-navigation.md` 引用（本 skill 用 LSP 非重造決策樹）
- **反向耦合 flag**（heavy symbol → lean 廣用模組 = anti-pattern）+ **資料範例**（catalog_utils lean 12 consumers / dataframe_utils heavy 3 consumers / polars helper 觸發反向耦合，viewport L34-37）
- **City Map 節點標註**（依賴方向 A─uses─▶B / dep weight lean-heavy / 消費者數）

### 驗證策略（docs mode）
- **逐項比對**：S0 完成後對照 viewport 原文 87 行逐段確認無遺漏
- **Pattern Radar 評分表逐格 checkpoint**：5 因子加權矩陣（viewport L51-58）逐格保留，非只搬門檻數字
- **行數 checkpoint**：合併後 SKILL.md < 200 行（SM-8）；超過則評估是否精簡
- **/consistency**：跑 `arch-thinking/SKILL.md` 自洽性（章節結構、交叉引用、前後邏輯）
- **導航有效性**：合併檔內所有 `[...](path)` link 指向存在檔案（含 `rules/lsp-navigation.md`）
- **受眾中性**：確認「不決定受眾」聲明存在於頂部且適用整個 skill；三層次（受眾中性 / 與既有 skill 邊界 / 不適用不做）無內容重疊

---

## S1：引用遷移（commands/ + skills/ 內 arch-viewport → arch-thinking）

### Context
- **UC 引用**：消費端引用從「兩個 skill」收斂為「一個」，UC 行為不變
- **依賴**：S0（合併檔結構已定，引用才能正確指向 §一/§二）
- **語義約束**：與 S0 共享合併結構（§一 視角 / §二 機械）；並列處的「視角+機械」分工語意以「視角見 §一、機械見 §二」描述保留（非塌縮為「同 skill 內」）
- **基礎設施盤點**：V4~V20 共 17 處引用點（排除 V1 本體、V2 settings、V3 索引、V6 invariant，這些歸 S2/S3）
- **依賴錨點**：見段落 0 引用清單 V4~V20
- **範圍邊界**：S1 **只改 V4~V20**；`skills/CLAUDE.md:44` 索引行歸 S3（S1 rg 驗證須排除此檔，否則誤報殘留）
- **成功標準**：`rg "arch-viewport"` 於 `commands/`+`skills/`（**排除 `skills/arch-viewport/` 本體、`skills/CLAUDE.md`（歸 S3）、`_done/`**）= 0

### 修改要點

**相對路徑層級（三種深度，不可混淆）**：
- `commands/xxx.md` → `../skills/arch-thinking/SKILL.md`（一層 `../` 進 skills/）
- `skills/xxx/SKILL.md` → `../arch-thinking/SKILL.md`（一層 `../` 同層）
- `commands/claude/_common/xxx.md`（V20）→ **`../../../skills/arch-thinking/SKILL.md`**（三層 `../../../`，比 commands/ 多兩層）⚠️ 機械套用 `../skills/` 會斷 link

**並列引用 → 單一**（保留「視角+機械」分工描述，指向合併檔 §一/§二）：
- V4 `review-engine:20`：`[arch-thinking] / [arch-viewport]` → `[arch-thinking]`（單一 skill 含視角+機械）
- V5 `review-engine:174`：論述改「依賴 arch-thinking（視角+機械）」
- V8 `ep-review:20`：`[arch-thinking] + [arch-viewport]` → `[arch-thinking]`
- V9 `ep-review:85`：並列分工 → 單一，描述「視角與結構機械同 skill（視角見 §一、機械見 §二）」
- V10 `execution-plan:295`、V11 `execution-plan:298`：並列/論述 → 單一
- V13 `code-review:81`（注意原文「arch-viewport + arch-thinking」viewport 在前）：「引用 arch-viewport + arch-thinking」→ 「引用 arch-thinking（視角+機械）」
- V17 `illustrate:102`：並列 → 單一 + 保留分工描述

**單一 arch-viewport 引用 → arch-thinking**（依相對路徑層級改）：
- V7 `commands/CLAUDE.md:87`、V12 `code-review:68`、V14 `code-review:107`、V15 `illustrate:9`、V16 `illustrate:28`、V18 `illustrate:132`、V19 `illustrate:140`、V20 `illustrate-structure-viewport.md:4`（三層路徑）

**能力下沉表更新**（V18 `illustrate:132`）：`arch-viewport skill` → `arch-thinking skill`，「跨 illustrate/code-review/ep-review 共用」語意保留。

### 驗證策略（docs mode）
- **rg 殘留**：`rg "arch-viewport" commands/ skills/`（**排除 `skills/arch-viewport/` 本體、`skills/CLAUDE.md`（L44 歸 S3）、`_done/`**）= 0
- **link 有效性**：遷移後每個 `[arch-thinking](path)` 路徑正確（commands/ 一層、skills/ 同層、`_common/` 三層，分別驗證）
- **V20 三層路徑重點查**：`illustrate-structure-viewport.md` 的 link 必須是 `../../../skills/arch-thinking/SKILL.md`
- **語意保留**：抽查 ep-review:85、code-review:81、illustrate:102，確認「視角見 §一、機械見 §二」分工描述未丟失
- **/consistency**：受影響命令檔（illustrate/code-review/ep-review/execution-plan）

---

## S2：配置 + invariant 同步

### Context
- **UC 引用**：配置層同步（非 UC 變更）
- **依賴**：獨立於 S0/S1（配置不依賴檔案內容），但邏輯上在刪目錄前完成
- **語義約束**：settings.json 雙向（allowlist ↔ 目錄一一對應）；invariant 邏輯不變只改文字
- **基礎設施盤點**：`settings.json` permission allowlist、`check_single_source.py` invariant 規則
- **依賴錨點**：`settings.json:54-55`、`check_single_source.py:56-59`
- **成功標準**：settings.json 無 `Skill(arch-viewport)`；`/sync-sources` 通過

### 修改要點

- **settings.json**：刪 L55 `"Skill(arch-viewport)"`（保留 L54 `"Skill(arch-thinking)"`）。雙向：順向（allowlist 條目對應存在目錄）✓ arch-thinking 保留；反向（arch-thinking 目錄有對應 permission）✓。review 確認 settings.json 僅 L55 一處 arch-viewport，無 deny section。
- **check_single_source.py:58**：note 字串「共用 arch-viewport skill 的消歧對稱」→「共用 arch-thinking skill 的消歧對稱」。**invariant 邏輯不變**：`audience_self_declare`（L56 `must_contain_any` = layer 3/人類 viewport/B 軸/受眾，不含 arch-viewport）+ `skill_allowlist_coverage`（L61-72，自動捕捉 settings↔skills 目錄對應，刪除後兩端同步不誤報）。

### 驗證策略（docs mode）
- **settings.json 雙向**：`rg "arch-viewport" settings.json` = 0；`rg "Skill\(arch-thinking\)" settings.json` = 1；JSON 合法（`jq . settings.json`）
- **invariant**：執行 `/sync-sources` 通過；確認 `must_contain_any` 與 `skill_allowlist_coverage` 邏輯未受文字改動影響

---

## S3：刪除舊目錄 + 收尾驗證

### Context
- **UC 引用**：完成承載轉移（舊目錄移除，能力全歸 arch-thinking）
- **依賴**：S1（所有引用遷移完才刪，否則斷 link）、S2（配置已同步）
- **語義約束**：乾淨刪除，不留 redirect/alias（ai-rules 不考慮向後相容）
- **基礎設施盤點**：`skills/arch-viewport/` 目錄、`skills/CLAUDE.md` 索引、`commands/CLAUDE.md` 索引
- **依賴錨點**：`skills/arch-viewport/`（刪除目標）、`skills/CLAUDE.md:28,44`、`commands/CLAUDE.md:87`
- **成功標準**：`arch-viewport` 目錄消失（repo + symlink 同步）；全域 rg 殘留 = 0；索引同步

### 修改要點

- **刪除** `skills/arch-viewport/` 整個目錄
- **skills/CLAUDE.md 索引**：刪 L44 `arch-viewport` 行；L28 `arch-thinking` 描述更新為「設計視角 + 結構機械（合併；含 city map/dep weight/Pattern Radar/domain grounding/LSP；受眾中性）」
- **commands/CLAUDE.md**：L87 已於 S1 改 arch-thinking，此處複查

### 驗證策略（docs mode）
- **symlink 同步**：`ls ~/.claude/skills/` 無 arch-viewport（symlink 自動反映 repo 刪除）
- **全域 rg 殘留**：`rg "arch-viewport" /Users/ctai/Github/ai-rules`（排除 `_done/` 歷史註記、history/project jsonl）= 0
- **索引同步**：`skills/CLAUDE.md` 索引與實際 `skills/` 目錄一致（無 arch-viewport 條目、arch-thinking 描述正確）
- **/consistency**：`skills/CLAUDE.md`、`commands/CLAUDE.md`

---

## 整合策略

- 段落依賴序嚴格：S0 → S1 → S2 → S3。S3 刪目錄前必須確認 S1 引用全遷移（含 V20 三層路徑）、S2 配置同步，否則產生斷 link / 懸掛 permission
- 每段完成跑該段 rg 驗證；S3 跑全域 rg 作為最終閘門
- 合併檔（S0）是資訊完整性高風險段 — Pattern Radar 評分表（逐格）/ product-type 雙軌 docs 細節 / RC-3 是最易漏點

---

## 收尾步驟（docs mode）

1. **CLAUDE.md Capabilities + Kanban**：跳過（元專案無 Capabilities 表格、無 .kanban/）
2. **SYSTEM-MAP.md**：跳過（元專案無 SYSTEM-MAP.md）
3. **CLAUDE.md 更新**：
   - `skills/CLAUDE.md` 索引同步（S3 已含）
   - `commands/CLAUDE.md` 命令索引 description 同步（S1 已含 L87）
   - 受影響命令（illustrate/code-review/ep-review/execution-plan）行為描述反映「單一 arch-thinking skill（視角 §一 + 機械 §二）」（S1 已含）
4. **/audit-test**：跳過（docs mode 無測試）；改為**全域 rg 殘留 + /consistency 受影響檔**作為品質閘門（S3 已含）

---

## EP Review 區段（Finding Record）

**Review 模式**：2 agent 並發（Review-1 設計合理性 opus inherit / Review-2 引用 drift sonnet 降級），top-down。

| ID | 維度 | 嚴重度 | 信心 | 決定 | 修正落點 |
|----|------|--------|------|------|---------|
| R1-F1 | frontmatter 觸發詞漏「結構 viewport/反向耦合」 | Important | confirmed | ✅採納 | S0 description 補回兩詞、LSP 用語校正 |
| R1-F2 | Pattern Radar 評分表僅標題式 | Important | evidence | ✅採納 | S0 關鍵保留 + 驗證策略加「5 因子逐格 checkpoint」 |
| R1-F3 | product-type 雙軌 docs 細節 | Suggestion | evidence | ✅採納 | S0 關鍵保留補 docs 排除細節 |
| R1-F4 | 保留 viewport 資料範例 | Suggestion | evidence | ✅採納 | S0 關鍵保留補 catalog_utils 範例 |
| R1-F5 | 流程注入 vs「不做」錯置 | Important | confirmed | ✅採納 | S0 大綱「不做」移入「不適用/不做」段 |
| R1-F6 | 受眾中性與邊界段重複風險 | Important | confirmed | ✅採納 | S0 受眾中性三層次區隔 + SM-7 |
| R1-F7 | source-driven 邊界兩處重複 | Important | confirmed | ✅採納 | S0 邊界段整合為單條 |
| R1-F8 | lsp-navigation.md 引用 | Suggestion | confirmed | ✅採納 | S0 關鍵保留補外部引用 |
| R1-F9 | 思考提示 vs 工具分工層次 | Important | evidence | ✅採納 | S0 §二段首層次標示 |
| R1-F10 | 消費端引用分工塌縮 | Critical→Important | confirmed | ✅採納(降級) | S1 並列處保留「§一/§二」描述；降級理由：合併目的本就是一起用，整檔載入是預期，不致功能錯誤 |
| R1-F11 | 合併檔 context 成本 | Suggestion | inferred | ✅部分採納 | S0 加行數<200 checkpoint；SM-8 判斷維持 |
| R2-F4 | V20 `_common/` 三層路徑 | Important | confirmed | ✅採納 | S1 相對路徑層級三種深度明列 |
| R2-F5/F9 | S1 rg 驗證未排除 CLAUDE.md:44 | Suggestion | evidence | ✅採納 | S1 範圍邊界 + 成功標準 + 驗證排除 skills/CLAUDE.md |
| R2-F6 | code-review:81 排序相反 | Suggestion | confirmed | ⚠️知悉 | 不動 EP；S1 逐行列舉已正確標註原文排序 |
| R2-F1/F2/F3/F7/F8 | 引用清單完整/settings 乾淨/invariant 不變/語義撈無漏/lsp-architect 不遷移 | positive | confirmed | ✅確認 | 無需動作 |

**無不採納項**。所有實質 finding 已整合進 S0/S1 段落（build LLM 直接可見）+ 本 Finding Record（追溯）。

### 獨立 /code-review（layer 2，build 後）決策

| ID | 維度 | 嚴重度 | 信心 | 決定 | 修正落點 |
|----|------|--------|------|------|---------|
| CR-S1 | L14 §五 備註只涵蓋「場景排除」，漏「不做=職責邊界」 | Suggestion | evidence | ✅採納 | L14 §五 描述改「場景排除（不適用）+ 職責邊界（不做）」 |

**觀察（非 finding，已確認良性）**：`settings.json` 在 `.gitignore:32`（未入版控），S2 本機已改（刪 `Skill(arch-viewport)`）但不進 commit；最終狀態 invariant checker 雙向通過，非遺漏。其他環境各自刪除，`check_single_source.py` 會 flag。
