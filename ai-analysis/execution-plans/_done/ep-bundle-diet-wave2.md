# EP: T2-2 bundle 減肥第二波——rule 合併／下沉／單源化

> **ep_type**: implementation（docs mode——變更全為 `.md`，無 `.py` callable 符號變更）
> **baseline**: 082b7f7（implement 階段 1 重 stamp——原始 206d967；前 session 五批〔8201987…082b7f7〕已 gate commit 屬弧外；重 stamp 時點工作樹僅本 EP 檔案，乾淨樹 gate 已過）

## 實作總覽

把非 Claude 端 always-on bundle 從 88,085 bytes（90KiB gate 的 95%）減到 ~79.7KB（gate 86%）：一條合併 rule（deep-thinking＋guide 架構段 → design-thinking）、兩條 rule 下沉 skill（model-routing、llm-output-convention）、guide↔rule 三處單源化、bundle 內自檢清單退場。

凍結決策（來源：2026-08-30 side chat T2 執行包；brainstorm 報告 §4 T2-2＋§9——`ai-analysis/reports/2026-08-29-skill-agent-rules-improvement-brainstorm.md`）：

1. **deep-thinking×架構段 合併**：新 `rules/design-thinking.md`（~2.5KB）＝思考紀律核心＋架構三視角核心（自 guide「架構設計紀律」段收編，該段瘦成 pointer）＋兩個 skill pointer；`skills/deep-thinking/SKILL.md` 承載輸出格式＋深層論證；arch-thinking skill 本體不動
2. **model-routing 下沉**：rule 留骨架（角色→tier 表＋兩跳原則）；解析表細節／thoughtLevel 但書／rate limit 並發表／classifier 段 → `skills/model-routing/SKILL.md`；引用錨點 rg 同步
3. **llm-output-convention 下沉**：細則（print tag 表、Logger 慣例、stdlib 並存）→ skill；rule 留核心原則＋Namespace＋pointer；自檢清單退場（搬入 skill）
4. **自檢清單退場**：bundle 內 2 條（deep-thinking 結尾、llm-output-convention 結尾）——理由「零獨立性驗證」（可辯護），不用「零約束力」（不可觀察）
5. **guide↔rule 單源化三處**：guide 演化性思維:18 向後相容 → edit-discipline 為源；guide 架構段 SOLID 子段 → edit-discipline 為源；guide 量化鐵律:148 數據完整性 row → quality-constraints 為源（guide 引用不重述）

帳（絕對 bytes 口徑；gate＝90KiB=92,160B、ZCode 截斷線 100KiB）：88,085B（95%）→ 目標 ≤79,700B（86%）。來源實測 deep-thinking 4,382B／model-routing 5,343B／llm-output-convention 4,401B——理論可減 ~9.6KB、餘裕 1-3KB。75KB 降級為自然機會（不硬擠）。skills 不吃 bundle 預算（下沉是淨賺）。

## UC 盤點（docs mode）

### Backlog 關聯

- **supersede 對象**：`.kanban/Backlog/bundle-layered-diet.md`（同主題 deferred 卡）——本 EP 觸發條件改為「90KiB gate 95%+ 現實壓力」已成立。**繼承其護欄**：每項搬移須驗證「on-demand 連結存在且可被觸發」，不做無痕刪除。收尾時標 superseded 並搬 `.kanban/Done/`
- **EP 追蹤卡**：本 EP 產出後於 `.kanban/Backlog/` 建卡（見收尾段）

### SYSTEM-MAP 影響

無 SYSTEM-MAP.md（元專案無此檔，正當跳過）。

### 掃描範圍

- rules/AGENTS.md manifest（rule 清單＋部署紀律）、ai-development-guide.md 全文、三條目標 rule、edit-discipline、quality-constraints
- repo-wide `rg 'deep-thinking|model-routing|llm-output-convention'`（排除 ref-docs／.git／.code-reality）＋語義反向撈（guide 段名引用：`架構設計紀律|演化性思維|量化交易專屬鐵律`）
- 基礎設施：scripts/deploy_agents.py、tests/、skills/scan-project/scripts/check_single_source.py、skills/CLAUDE.md

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| rule+skill 分層模式（rule 留核心＋pointer，深層住 skill） | ✅ | rules/AGENTS.md 尺寸 gate 段（先例：acceptance-evidence / lsp-navigation / instruction-writing / context7） | 更新 | 擴至三組新分層；先例清單收尾同步 |
| 90KiB deploy gate＋三端部署驗證 | ✅ | scripts/deploy_agents.py＋rules/AGENTS.md 部署驗證義務段 | 更新 | 每段 dry-run＋收尾三端驗證 |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| always-on bundle 尺寸治理第二波（合併／下沉／單源化，88→~79.7KB） | 📋 | 本 EP（rules/＋skills/＋ai-development-guide.md） |

## 段落 0：全域研究摘要

### 可複用基礎設施

- **rule+skill 分層先例**（結構模板）：`rules/lsp-navigation.md`（rule 核心）＋`skills/lsp-navigation/SKILL.md`（深層；frontmatter `name`＋`description` 尾帶「觸發詞：…」）——新三組 skill 照此 frontmatter 模板
- **rule→skill pointer 模式**（neutral 規範）：rule 內用 skill 名不用路徑（`見 model-routing skill（on-demand）`）——rules/ 禁 `../skills/` 跨域 ref（rules/AGENTS.md 機械檢查清單＋tests `test_purity_cross_domain_path` 把關）
- **skills→skill 連結模式**：skill 檔間用相對路徑 `[model-routing](../model-routing/SKILL.md)`
- **部署機制**：`scripts/deploy_agents.py` 掃 frontmatter auto-discover——rule 改名/新增**不需改 script**；`~/.zcode/skills` 整目錄 symlink repo `skills/`——新 skill 目錄自動可見（corrections-weekly 已實證）；Claude 端 `~/.claude/rules/` 目錄 symlink 即時反映新增/刪除

### 依賴關係與 ripple 證據（rg 機械輸出，2026-08-30 掃描）

**基礎設施零耦合**（關鍵正面證據）：`rg 'deep-thinking|model-routing|llm-output-convention|design-thinking' scripts/deploy_agents.py tests/ skills/scan-project/scripts/check_single_source.py skills/CLAUDE.md rules/_ai-behavior-constraints.md` → **0 hits**。deploy gate 測試全用合成 tmp rule（`tests/test_deploy_agents.py` 讀畢確認），rule 改名不炸 gate。

**引用面（live 檔，須逐檔同步）**：

| 引用檔:行 | 引用內容 | 歸屬段 |
|---|---|---|
| `rules/AGENTS.md:49,60,67` | manifest 三行（deep-thinking／llm-output-convention／model-routing） | S1/S3/S2 |
| `skills/arch-thinking/SKILL.md:8` | 「頂層總綱見 ai-development-guide「架構設計紀律」段」——**段收編後斷（指向 pointer 的 pointer）** | S1 |
| `skills/arch-thinking/SKILL.md:18` | `[deep-thinking](../../rules/deep-thinking.md)` 輸出格式 | S1 |
| `rules/edit-discipline.md:23` | SOLID 指標「頂層總綱見 ai-development-guide「架構設計紀律」段」——同上斷裂 | S1 |
| `skills/ep-review/SKILL.md:125`、`skills/code-review/SKILL.md:142` | 「深層思考框架見 `~/Github/ai-rules/rules/deep-thinking.md`」（review agent spawn prompt 用） | S1 |
| `skills/trading-analysis/SKILL.md:8` | 「見 deep-thinking rule」 | S1 |
| `skills/agent-workflow/SKILL.md:49,160,180,214` | 並發表/解析表 單一源指向 `rules/model-routing.md` | S2 |
| `skills/execution-plan/SKILL.md:158,303,310,312` | :158＝角色 tier 表語境（留 rule）；:303,310,312＝並發表語境（→skill） | S2 |
| `skills/review-engine/SKILL.md:138,140`、`skills/code-review/SKILL.md:56`、`skills/blueprint-bootstrap/SKILL.md:55`、`skills/illustrate/SKILL.md:75` | model-routing 並發表/tier 表引用 | S2 |
| `skills/_common/workflow-review-pattern.md:161`、`skills/_common/agent-review-cycle.md:40,50` | :40＝並發表語境（→skill）；:161/:50＝角色 tier 表語境（留 rule） | S2 |
| `agents/AGENTS.md:16,18` | pin 單一源（解析表）＋tier 詞彙定義指向 `rules/model-routing.md` | S2（⚠️ 前批 dirty 檔） |
| `ai-analysis/tours/agents-tour.md:5,57` | pins 單一源 `rules/model-routing.md` ×2 | S2 |
| `skills/commit/SKILL.md:160` | 「違反 llm-output-convention」——概念名引用，rule 名不變，**不需改** | — |
| `skills/code-review/SKILL.md:5`（when_to_use 提 deep-thinking） | 概念名＝skill 名，持續有效，**不需改** | — |

**不改清單**（歸檔快照，改了反而破壞歷史記錄）：`ai-analysis/execution-plans/_done/`、`ai-analysis/specs/_done/`、`ai-analysis/reports/`（含 brainstorm 報告）、`ai-analysis/reports/superpowers/README.md:4`。reports 的概念名引用在 skill 同名後自然有效。

**guide 段引用（語義反向撈）**：「架構設計紀律」段被 `rules/edit-discipline.md:23`＋`skills/arch-thinking/SKILL.md:8` 引用為頂層總綱——S1 收編後兩處改指 design-thinking rule。

### 類似功能既有實作

- bundle 減肥第一波：`ai-analysis/execution-plans/_done/ep-rules-bundle-desink.md`（92.1→79.7KB）——本 EP 是第二波，模式相同（壓縮＋下沉），其「明確不動清單」中 deep-thinking 當時列禁區（輸出格式模板是 08-21 審查輪特意恢復）——**本次由凍結決策 1 解除**（模板下沉 skill 非刪除，行為內容仍在、只是不吃 always-on 預算）
- tier registry EP：`ai-analysis/execution-plans/_done/ep-agents-tier-registry.md` S1 曾做 model-routing 兩跳改寫＋八檔引用同步——S2 沿用其同步模式

### 風險假設

| # | 假設 | 等級 | 驗證 |
|---|------|------|------|
| R1 | rule 改名/新增不需改 deploy script（frontmatter auto-discover） | ✅ 已驗證非風險 | tests 掃描 0 hits＋rules/AGENTS.md:45 明載＋test_deploy_agents.py 讀畢 |
| R2 | 下沉後細則仍 on-demand 可達 | 🔴 高（supersede 卡繼承護欄） | 每組三件套：skill description 觸發詞＋skills/CLAUDE.md 索引行＋rule 內 pointer 語義完整（不斷頭）——S1/S2/S3 驗證欄逐項檢查 |
| R3 | 尺寸帳未達 ~79.7KB | 🟡 中 | 每段 build 後 `--dry-run` 記錄數字；未達時處方＝繼續壓縮 rule 本體（encoder 原則），不是放棄目標也不是硬湊 |
| R4 | ripple 殘留（引用沒跟） | 🟡 中 | 每段 rg 殘留對帳（live 檔零殘留）＋收尾 repo-wide 複掃＋`/consistency` formal gate |
| R5 | 與前 session 五批並行 commit 衝突（同檔：agents/AGENTS.md） | 🟡 中 | implement 階段 1 硬 gate：`git status` 乾淨才開工；重 stamp baseline |
| R6 | 下沉後 spawn-time 行為退化——並發上限是每次 spawn 的行為輸入、非查閱型細節 | 🟡 中 | 消費者改指 skill 名＋S2 驗證檢查點（agent-workflow Step 2 指向可達、spawn 確認行 max 查表非憑記憶）。凍結決策不變——表在 skill 維持單源，rule 不留數字副本（兩處數字違反 agent-workflow:49「本檔不自帶數字」單源紀律） |

**死路假設嫌疑**：無（本 EP 無「宣稱被整合/觸發的既有符號」類宣告；docs mode 無 code symbol，CR 圖查詢不適用——markdown 不在 scip/graph 索引面，rg 是本 EP 的機械證據面）。

## Scenario Matrix（docs mode——觸發/預期行為為文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 部署 happy path | 每段 build 後 `deploy_agents.py --dry-run` | rules 清單正確（S1 後 design-thinking 取代 deep-thinking、仍 17 條）、尺寸遞減、gate 綠 | 無 | bundle 尺寸治理 |
| SM-2 | 非 Claude 端讀到新 bundle | 實際 deploy 後 `rg` 抽查 `~/.zcode/AGENTS.md` | 含 design-thinking section marker；舊 rule 名零殘留（除合法概念引用） | 無 | 部署驗證義務 |
| SM-3 | gate 攔截路徑 | bundle 撞 90KiB | deploy 拒絕＋fail loud（本 EP 尺寸下降方向，不應觸發；測試面已覆蓋 gate 行為） | 無 | 90KiB gate |
| SM-4 | Claude 端 symlink 反映 | rule 改名後 | `~/.claude/rules/design-thinking.md` 存在、`deep-thinking.md` 消失（目錄 symlink 即時） | 無 | 部署驗證義務 |
| SM-5 | 下沉細則 on-demand 觸發 | AI 遇「print tag 表怎麼寫／spawn 前查並發上限」 | 經 rule pointer 或 description 觸發詞載入對應 skill（段內驗兩通道）；skills/CLAUDE.md 索引隨各段結算補（第三通道） | 無 | 分層模式護欄 |
| SM-6 | 效能期待 | 收尾 dry-run | ≤~79.7KB（gate 86%）；每段數字單調遞減記錄在 EP review 區段 | 無 | bundle 尺寸治理 |

## 段落劃分原則

- 四段各自獨立可驗證（rg 殘留＋dry-run 數字），順序執行：S1 → S2 → S3 → S4
- **S4 依賴 S1**：S1 重構 guide 架構段骨架後，S4 才縮該段的 SOLID 子段（同區域兩步改，順序固定避免 Edit 衝突）
- 段落間檔案局部重疊但無同段編輯衝突（rules/AGENTS.md 三段各行；skills/code-review S1 :142／S2 :56 不同行），保守序列執行（每段後 dry-run 檢查點需要單調數字）
- 每段完成即結算（段落自足：build session 可能跨 session 接續）

---

## S1：design-thinking 合併（deep-thinking rule × guide 架構段）

### Context

**背景**：`rules/deep-thinking.md`（93 行，4,382B）與 guide「架構設計紀律」段（:120-139）分居兩處但同屬「設計決策思考紀律」——合併為單一 rule 承載核心，深層內容下沉 skill。架構段被 edit-discipline:23 與 arch-thinking:8 引用為「頂層總綱」，合併後總綱落點改為新 rule。

**UC 引用**：更新「rule+skill 分層模式」（先例清單＋一組新分層）；新增「bundle 尺寸治理第二波」主體。

**依賴關係**：無前置段。S4 依賴本段（guide 架構段重構）。

**語義約束**：與 S4 共享「guide 引用不重述」原則——本段只收編三主線＋視角非模板，SOLID 子段（:130-132）本段**原樣保留**由 S4 處理。

**基礎設施盤點**：lsp-navigation 分層先例（rule 核心＋skill 深層＋description 觸發詞）；`規則：rule 內 pointer 用 skill 名不用路徑`。

**依賴錨點**（定義端／消費端，rg 已驗）：
- `rules/deep-thinking.md`（定義端，刪除）← 消費：arch-thinking:18、ep-review:125、code-review:142、trading-analysis:8、rules/AGENTS.md:49
- guide `## 架構設計紀律`（:120 定義端，重構）← 消費：edit-discipline:23、arch-thinking:8

### 修改要點

1. **建 `rules/design-thinking.md`**（frontmatter `harness-scope: neutral`＋載入機制注記；目標 ~2.5KB）：
   - 核心原則：兩層思考強制（第一性原理＋第二層思考）＋「本質正確但後果災難」一句例（Tesla）
   - 思維框架要點：步驟 1-6 摘要＋**步驟 5-6 強制**＋需要更深入分析的信號（框架圖與 7 問清單 → skill）
   - 決策分級：單向門／雙向門表（原樣保留）
   - **架構三視角**（自 guide 收編）：依賴規則／bounded context／use case 驅動三主線＋各自自問句；視角非模板句＋mosaic 領域映射範例（標「範例領域特定」；深入視角見 arch-thinking skill）
   - 程式碼查證一句核心（查證細則 → skill）
   - 觸發情境（精簡保留）
   - Pointer：輸出格式模板＋深層論證（思維框架圖、關鍵問題 7 問、程式碼查證細則）見 deep-thinking skill（on-demand）
2. **建 `skills/deep-thinking/SKILL.md`**：frontmatter `name: deep-thinking`＋description（觸發詞：深層思考、第一性原理、第二層思考、單向門、雙向門、決策分析、深層思考分析、輸出格式）；body 承載：輸出格式模板（原 rule「輸出格式」段全文）、思維框架圖（ASCII 圖）、關鍵問題清單全文（0-7 共 8 條——含第 0 問「讀者是誰」，必須在任何分析之前先回答）、程式碼查證與連鎖後果細則、執行自檢清單（自 bundle 退場、skill 收編）
3. **刪 `rules/deep-thinking.md`**
4. **guide 架構段瘦身**（:120-139）：保留段標＋核心原則句（視角非模板）＋一行指向 design-thinking rule（三主線、視角非模板子段 :134-136〔含 mosaic 範例〕、決策思考核心已收編）＋SOLID 子段原樣留（S4）＋尾段 arch-thinking 深入視角 pointer 保留
5. **引用同步**（rg 逐檔）：
   - `skills/arch-thinking/SKILL.md:8`：頂層總綱 → `[design-thinking rule](../../rules/design-thinking.md)`（skill→rule 相對路徑慣例）
   - `skills/arch-thinking/SKILL.md:18`：`[deep-thinking](../../rules/deep-thinking.md)` → `[deep-thinking skill](../deep-thinking/SKILL.md)`（輸出格式在 skill）
   - `rules/edit-discipline.md:23`：括號注「頂層總綱見 ai-development-guide「架構設計紀律」段」→「頂層總綱見 design-thinking rule」
   - `skills/ep-review/SKILL.md:125`、`skills/code-review/SKILL.md:142`：絕對路徑改 `~/Github/ai-rules/skills/deep-thinking/SKILL.md`（跨專案 review agent 讀取指引——維持絕對路徑形態，相對路徑在非 ai-rules cwd 不可解析）
   - `skills/trading-analysis/SKILL.md:8`：「見 deep-thinking rule」→「見 design-thinking rule／deep-thinking skill」
   - `rules/AGENTS.md:49`：row 改 `design-thinking`，說明「決策與架構設計思考核心（兩層思考＋三視角；輸出格式在 deep-thinking skill）」
   - 概念名通則：中文「深層思考」「深層思考分析」「第一性原理」等概念名引用（judge-review 等各處）在 skill 同名後語義持續有效，不需改

### 驗證策略

- rg 殘留：`rg -n 'deep-thinking\.md' --glob '!ai-analysis/**' rules/ skills/ agents/ ai-development-guide.md` → **0 hits**（manifest row 描述與 skill 相對連結 `../deep-thinking/SKILL.md` 均不含 `deep-thinking.md` 連續字串；bundle 內 deploy 自動 marker 隨改名歸零）
- `rg -n '架構設計紀律' rules/ skills/` → 僅歷史/描述性提及，無「總綱見 guide 段」句
- `uv run python scripts/deploy_agents.py --dry-run`：17 rules 含 design-thinking、尺寸低於 88,085（記錄數字）
- 實際 deploy＋`uv run pytest tests/` 全綠
- 護欄三件套檢查：deep-thinking skill description 觸發詞在場；索引行**隨本段結算補**（skills/CLAUDE.md 加 deep-thinking 行——注明 rule 端為 design-thinking）；rule pointer 語義完整（讀者知道輸出格式去哪找）

---

## S2：model-routing 下沉（解析表/並發表/但書 → skill）

### Context

**背景**：`rules/model-routing.md`（5,343B）承載 churn 最快的 provider 事實（rate limit 表自承可能滯後、thoughtLevel bug 遙測數據點）——佔 always-on 預算。骨架留 rule（每次 spawn 都需要的角色→tier 判斷），provider 級細節下沉。

**UC 引用**：更新「rule+skill 分層模式」＋「兩跳解析單一源」（ep-agents-tier-registry 建立的 UC——**單一源位置從 rule 檔內表移到 skill 檔**，rule 仍是「兩跳原則＋角色→tier 表」的源）。

**依賴關係**：無前置段。⚠️ 觸碰 `agents/AGENTS.md`（前批 ① dirty 檔）——**本段必須在乾淨樹上執行**（implement 階段 1 gate）。

**語義約束**：與 agents/AGENTS.md 共享「pin 值單一源」語義——下沉後 pins 值的源＝skill 解析表；tier **詞彙**定義仍在 rule（agents/AGENTS.md:18 引用詞彙不引用表）。

**依賴錨點**：`rules/model-routing.md`（定義端，瘦身）← 消費 12 檔（研究表格 S2 區塊），全部 rg 已列。

### 修改要點

1. **`rules/model-routing.md` → 骨架**（~1.5KB）：
   - 保留：兩跳解析原則、角色→tier 表（全文）、tier 詞彙單一源句、套用三路徑（三行摘要）、spawn 前確認行、載入機制注記
   - Pointer：tier→(model, effort) 解析表、rate limit 與並發上限表、thoughtLevel 但書（#339/#306 已知 bug 家族）、classifier 間歇 unavailable 處置——見 model-routing skill（on-demand）
   - **自指句隨遷**：保留段內「pin 值以本檔為單一源」（:12）與「值以本檔解析表為單一源」（:52）改指 model-routing skill 解析表——原文照抄即「rule 宣稱自己是表的家但表已不在」的自相矛盾
2. **建 `skills/model-routing/SKILL.md`**：frontmatter `name: model-routing`＋description（觸發詞：spawn agent model、tier 解析、並發上限、rate limit、thoughtLevel、reasoningEffort、classifier unavailable、flash、haiku）；body 承載：tier→(model,effort) 解析表全文、thoughtLevel 但書段（含 #339/#306）、rate limit 與並發上限表＋「改限額只改本表」單源句、CC/GLM enum 別名細節、classifier 間歇段全文
3. **引用同步——A/B 兩類**（引用語境決定改不改；B 類改了反而斷鏈）：
   - **A 類（並發表／解析表／classifier 語境 → 改指 model-routing skill**；skill 檔間連結 `../model-routing/SKILL.md`）：`skills/agent-workflow/SKILL.md` :49,160,214（並發表）＋:180（classifier）；`skills/execution-plan/SKILL.md` :303,310,312；`skills/review-engine/SKILL.md:138`；`skills/code-review/SKILL.md:56`；`skills/blueprint-bootstrap/SKILL.md:55`；`skills/_common/agent-review-cycle.md:40`；`agents/AGENTS.md:16`（pin 單一源 → skill 解析表）；`rules/AGENTS.md:67` row 說明（「兩跳解析＋並發表」→「兩跳解析骨架（解析表/並發表在 model-routing skill）」）；`ai-analysis/tours/agents-tour.md:5,57`（單一源落點）
   - **B 類（角色→tier 表／tier 詞彙語境 → 留 rule 不動**，該表仍在 rule，改指 skill 反而斷鏈）：`skills/execution-plan/SKILL.md:158`；`skills/review-engine/SKILL.md:140`；`skills/illustrate/SKILL.md:75`；`skills/_common/workflow-review-pattern.md:161`；`skills/_common/agent-review-cycle.md:50`；`agents/AGENTS.md:18`（tier 詞彙定義仍在 rule）

### 驗證策略

- rg 殘留（兩類對帳）：`rg -n 'rules/model-routing\.md' rules/ skills/ agents/ ai-analysis/tours/` → 僅 **B 類語境**（角色 tier 表／tier 詞彙）與 rule 自身／manifest row 名；**A 類語境零殘留**
- `rg -n '並發表|並發上限' skills/agent-workflow/ skills/execution-plan/ skills/_common/ skills/review-engine/` → 措辭指向 skill 而非 rule 檔
- R6 檢查點：agent-workflow Step 2（:49）指向可達（skill 經 symlink 讀得到）、spawn 確認行 `max=N` 的 N 查表非憑記憶
- dry-run 尺寸記錄（預期較 S1 後再降 ~3KB）；deploy＋pytest 全綠
- 護欄：model-routing skill description 觸發詞含「並發上限/rate limit」（spawn-time 查表可達）；索引行隨本段結算補（skills/CLAUDE.md 加 model-routing 行）
- agents/zcode/ pins 檔內註解不含路徑（rg 已驗）→ 無需動

---

## S3：llm-output-convention 下沉＋自檢清單退場

### Context

**背景**：`rules/llm-output-convention.md`（4,401B）細則（tag 表、Logger 慣例、stdlib 並存）是查閱型內容非每次必載；結尾自檢清單與慣例段重複（第一波 desink EP 已標記可壓）。

**UC 引用**：更新「rule+skill 分層模式」。commit skill 的概念引用（:160）不動（rule 名不變）。

**依賴關係**：無前置段、無檔案重疊。

**依賴錨點**：`rules/llm-output-convention.md`（定義端，瘦身）← 概念消費：commit:160（名字引用，不動）、rules/AGENTS.md:60（manifest row）。

### 修改要點

1. **`rules/llm-output-convention.md` → 核心**（~1.6KB）：
   - 保留：核心原則（print 當索引 Logger 當資料庫＋state transition 定義）、決策規則一句、單檔 vs 分檔一句、Namespace 原則（module-path 反查鍵——保留全文，這是行為強制）、print/Logger 各一行摘要（tag 語意與 prefix 閉環概念）、scope 注記、frontmatter `paths: "**/*.py"`
   - Pointer：print tag 全表、`[LOG]`/`[ACTION]`/`[progress]` 細則、Logger level/prefix 細則、stdlib 與框架 Logger 並存、遷移注意——見 llm-output-convention skill（on-demand）
   - **刪「執行自檢清單」段**（退場；內容收編入 skill）
2. **建 `skills/llm-output-convention/SKILL.md`**：frontmatter `name: llm-output-convention`＋description（觸發詞：print tag、[OK]、[LOG]、[progress]、Logger prefix、action_name、log level、namespace、module-path、addHandler、lastResort）；body 承載：print tag 表＋細則三條、Logger 慣例（prefix/level/閉環）、stdlib 並存三條、遷移注意、自檢清單（收編）
3. `rules/AGENTS.md:60` row 說明（「print/Logger 雙通道」→「print/Logger 雙通道核心（tag 表/細則在 llm-output-convention skill）」）

### 驗證策略

- rg 對帳：`rg -n 'llm-output-convention' rules/ skills/` → 引用語義不變（名字持續有效）、無路徑斷鏈
- bundle 內自檢清單退場驗證：dry-run 輸出不含「執行自檢清單」（S1 的 deep-thinking 清單同時已退場）→ `rg -c '執行自檢清單' ~/.zcode/AGENTS.md`（deploy 後）＝ 0
- dry-run 尺寸記錄；deploy＋pytest 全綠
- 護欄：skill description 觸發詞覆蓋「print tag」「Logger prefix」；索引行隨本段結算補（skills/CLAUDE.md 加 llm-output-convention 行）

---

## S4：guide↔rule 單源化三處

### Context

**背景**：guide 三處內容與 rules 重複定義（兩處真理）。單源化：rule 為源，guide 引用不重述——guide 是每個 harness 都載的骨架，重複內容是雙倍維護面。

**UC 引用**：無新 UC（治理品質項）。

**依賴關係**：**依賴 S1**（架構段骨架已重構，SOLID 子段在重構後的段內縮）。

**語義約束**：與 S1 共享 guide 架構段；「guide 引用不重述」原則＝保留一句語意錨＋指向源，不整段複製。

**依賴錨點**：guide :15-19（演化性思維）↔ `rules/edit-discipline.md:60-66`（向後相容確認機制，源）；guide :130-132（SOLID 精神）↔ `rules/edit-discipline.md:20-23`（SRP/DIP/SOLID 指標，源）；guide :146-148（鐵律表首 row 數據完整性）↔ `rules/quality-constraints.md:21-36`（數據完整性優先 Crash-Only，源）。

### 修改要點

1. **guide:15-19 演化性思維**：保留核心原則句（測試保護下重構可接受）＋「持續演化」句；:18 向後相容 bullet 縮為「向後相容確認時機見 edit-discipline rule」一句（源：edit-discipline 向後相容確認機制段——四條清單不重述）
2. **guide SOLID 精神子段**（S1 重構後的架構段內）：縮為一句「SOLID 精神實作時遵循，指標細則見 edit-discipline rule」（五項縮寫的中文展開屬可推導通用知識，不重述；edit-discipline:20-23 有縮寫列舉與 SRP/DIP 細則）
3. **guide 量化鐵律表首 row**：「數據完整性優先」row 的說明/實施策略 cell 縮為語意錨一句＋「fail-fast 與崩潰策略見 quality-constraints rule」（表其餘 5 row 不動——無對應 rule 源）
4. **edit-discipline:23 括號注**（S1 已改過一次）：確認指向閉環——SOLID 頂層總綱此時落點為 design-thinking rule（視角）＋自身（指標細節），無循環指向

### 驗證策略

- 三處 rg 對帳（有效 before/after 對照——縮前 guide:18 各 1 hit）：`rg -n '已有生產數據|向後相容只在' ai-development-guide.md` → 0 hits；`rg -n 'SRP（單一職責）' ai-development-guide.md` → 0 hits
- 源完整性：edit-discipline／quality-constraints 對應段內容完整（未被誤刪）——`rg -n '向後相容確認機制|數據完整性優先' rules/` 命中且段落在
- dry-run 尺寸記錄（小幅下降）；deploy＋pytest 全綠
- 斷 ref 檢測：deploy 內建 check_broken_refs 過（guide 引用 rule 皆 neutral，無死鏈）

---

## 整合策略

- **順序**：S1 → S2 → S3 → S4（S4 依賴 S1；其餘序列為 dry-run 單調數字檢查點）
- **每段結算**：修改 → rg 殘留 → dry-run（記錄尺寸）→ 實際 deploy → `uv run pytest tests/` → 段落完成標記寫回 EP
- **尺寸數字記錄**：每段 dry-run 後把 bytes 寫進 EP review 區段（追蹤表），收尾對帳總帳（88,085 → 最終值，目標 ≤~79.7KB）
- **baseline 弧邊界**：本 EP 任務弧＝baseline（implement 階段 1 重 stamp）→ 收尾 commit；五批前批 commit 在弧外
- **commit 切分**：一段一 commit（四段四 commit＋收尾併入 S4 或獨立）——commit gate 由用戶逐次確認（outward-action-consent）

## 收尾步驟（S4 後、commit 前必做）

1. **supersede 結算**：`.kanban/Backlog/bundle-layered-diet.md` 標 `superseded by ep-bundle-diet-wave2`（檔頭一行）→ 搬 `.kanban/Done/`；EP 追蹤卡搬 In-Progress→Done（隨本 EP commit）
2. **skills/CLAUDE.md 索引覆核**：三行 reference skill 條目已隨各段結算補（deep-thinking 行注明 rule 端為 design-thinking），格式照 acceptance-evidence／lsp-navigation 先例（skills/CLAUDE.md:121/:148）；此處僅覆核三行齊全
3. **rules/AGENTS.md 先例清單**：尺寸 gate 段「先例：acceptance-evidence / lsp-navigation / instruction-writing / context7 四組」→ 追加三組（七組）
4. **三端部署驗證**（部署驗證義務）：`shasum` 比 deployed 三檔一致；`rg` 抽查 `~/.zcode/AGENTS.md` 含 design-thinking marker、不含 deep-thinking rule 段；`ls ~/.claude/rules/design-thinking.md` 存在＋`deep-thinking.md` 不存在
5. **formal gates**：`uv run python skills/scan-project/scripts/check_single_source.py`（invariants 全綠——含 deploy_bundle_freshness）；`/consistency`（formal gate 不可跳；forked 撞 guard 時獨立 agent 六維度等價替代）
6. **repo-wide 複掃**：`rg -n 'deep-thinking\.md' --glob '!ai-analysis/**' --glob '!ref-docs/**'` 與 `rg -n 'rules/model-routing\.md' rules/ skills/ agents/` → 零殘留對帳
7. **`/audit-test`**：本 EP 無新增測試——docs mode 跳過（正當跳過：無測試變更），以 dry-run/pytest/invariants 替代

## EP Review Findings（三 agent：結構／完整性遺漏／合規兜底——2026-08-30，總評皆「需修後 build」，凍結決策未動搖）

| id | severity | 摘要 | decision | status |
|----|----------|------|----------|--------|
| A-F1 | 🔴 | S2 同步清單 A/B 兩類拆分——B 類 5 處角色→tier 表引用**留 rule 不動**（改指 skill 即斷鏈），驗證標準隨改 | ✅ | implemented |
| A-F2／B8 | 🟡 | S1 rg 殘留預期改 **0 hits**（原預期描述誤導） | ✅ | implemented |
| A-F3／B5 | 🟡 | skills/CLAUDE.md 索引行隨各段結算補（跨 session 護欄），收尾僅覆核 | ✅ | implemented |
| A-F4 | 🟡 | R6 升🟡中＋S2 檢查點（僅採選項 c；a 違凍結決策 2、b 製造兩處數字違「本檔不自帶數字」單源紀律——❌） | ✅/❌ | implemented |
| A-F5 | 🟢 | ep-review:125／code-review:142 維持**絕對路徑**形態改指 `~/Github/ai-rules/skills/deep-thinking/SKILL.md`（跨專案 agent 讀取指引；與 C-F1 衝突按語境裁決） | ✅ | implemented |
| A-F6／C-F8 | 🟡 | guide 視角非模板子段（:134-136）＋mosaic 範例隨三主線收編 design-thinking rule（標「範例領域特定」，precedent：quality-constraints mosaic 實例） | ✅ | implemented |
| A-F7／C-F7 | 🟢 | 關鍵問題實為 0-7 共 **8 問**（含第 0 問「讀者是誰」強制前置）全下沉 | ✅ | implemented |
| A-F8／C-F5 | 🟢 | model-routing :12/:52「以本檔為單一源」自指句隨遷改指 skill | ✅ | implemented |
| A-F9／C-F4／B7 | 🟡 | S4 驗證 pattern 失準（對 guide 永遠 0 hits）——改「已有生產數據｜向後相容只在」有效對照 | ✅ | implemented |
| B1 | 🟡 | execution-plan:303（「查 agent-workflow 並發表」）漏列——補入 A 類 | ✅ | implemented |
| B2 | 🟡 | agent-review-cycle:40 漏列＋S2 驗證命令範圍補 `skills/_common/` | ✅ | implemented |
| B4 | 🟢 | 概念名通則（「深層思考」等中文名引用不需改）入 S1 | ✅ | implemented |
| B6 | 🟢 | 絕對 bytes 口徑＋來源尺寸實測值（4,382/5,343/4,401B）＋鐵律表「5 row」修正 | ✅ | implemented |
| C-F1 | 🟡 | skill↔skill／skill→rule 連結用相對路徑慣例（arch-thinking:8/:18 兩處） | ✅ | implemented |
| C-F2 | 🟢 | 索引先例行號 :121/:148（off-by-one 修正） | ✅ | implemented |
| C-F3 | 🟢 | deep-thinking 索引行注明 rule 端＝design-thinking | ✅ | implemented |
| C-F6 | 🟢 | S4 SOLID 措辭改「五項縮寫展開屬可推導通用知識不重述」 | ✅ | implemented |

採納 17／不採納 2（A-F4 選項 a、b）／需確認 0。三 agent 對 EP 研究質量的正面核實：引用面行號逐一抽查全數命中、基礎設施零耦合宣告屬實、S1/S4 切分邊界可行、帳目可行有餘裕。

## 尺寸追蹤（dry-run 實測）

| 檢查點 | bytes | Δ |
|--------|-------|---|
| baseline | 88,085 | — |
| S1 後 | 86,388 | −1,697 |
| S2 後 | 83,661 | −2,727 |
| S3 後 | 81,524 | −2,137 |
| S4 後 | 81,540 | +16（單源化以指針換重述，淨平） |
| 壓縮輪後 | 81,030 | −510（機械冗餘壓縮：三 rule 重複表述＋guide 指針行） |
| 修復輪後（真 final） | **81,144** | +114（F1 vision cell 逐字還原 HEAD 版——恢復〔d32ddb0 邊界定版〕標記與 CR plugin 例外句） |

**總帳：88,085 → 81,144B（−6,941B，gate 95%→88%）。未達 ≤79,700B 目標（差 1,444B）**——根因：三個 rule 骨架合計超 EP 規格 ~2KB（凍結決策指定的內容分配全數保留：8 問清單、mosaic 範例、自問句、Namespace 全文等）。進一步壓縮需砍內容（違反「不做無痕刪除」護欄）或擴大到 EP 範圍外 rule——留用戶決策（accept 81KB／授權內容級刪減／後續 EP）。

## Build Review Findings（3-perspective：clean／UC-anchored／Correctness——apply 迴圈）

| id | severity | 摘要 | decision | status |
|----|----------|------|----------|--------|
| F1（三視角同中） | 🔴 | model-routing:21 vision-review cell 語義回退至 d32ddb0 舊版。根因：S2 骨架化的首讀在五批 commit 前、staleness 擋下後 re-Read 只覆蓋 :1-15 未含 :21（擋下的正是 8201987 的 cell 更新）——逐字還原 HEAD 版（含〔d32ddb0 邊界定版〕標記與 CR plugin 例外句） | ✅ | implemented（`git show 082b7f7` 逐字對照還原） |
| U-2 | 🟡 | settings.json `skill_allowlist_coverage` 缺三新 Skill 條目（important×3） | ✅ | implemented（補三行） |
| Cl-2 | 🟡 | rules/AGENTS.md:29 先例四組→七組＋:69 下沉摘要句補三組（＝EP 收尾步驟 3） | ✅ | implemented |
| Cl-4 | 🟢 | design-thinking pointer 枚舉補「執行自檢清單」 | ✅ | implemented |
| Cl-1 | 🟡 | ref-docs/Agentic-Design-Patterns-應用分析.md:109 舊路徑改遷移註記 | ✅ | implemented |
| C-2 | 🟢 | 觸發情境註解級壓縮（資訊架構括號）——可接受 | ❌ | — |
| C-3 | 🟢 | llm-output pointer 觸發詞含 namespace（Namespace 實在 rule）——冗餘無害 | ❌ | — |
| U-4 | 🟢 | A-F8 :52 句採刪除而非隨遷——同步職責由 agents/AGENTS.md:16 承載，意圖已達 | 記錄 | — |

**re-review 替代說明**（loop 收斂證據，明示非靜默跳過）：本輪 5 項採納全為機械可驗證修正——F1 為 `git show` 逐字還原（零新語義）、其餘為枚舉／allow-list／註記補行；以 invariants 全綠＋deploy/pytest＋rg 對帳作為 re-review 等價證據，不 spawn 第二輪 agent。
