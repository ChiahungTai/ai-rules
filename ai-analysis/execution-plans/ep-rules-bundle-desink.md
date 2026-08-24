# EP: rules bundle 減量——任務型下沉 skill＋去重重組＋論證壓縮

> **ep_type**: implementation（docs mode——變更全為 `.md`，無 `.py` callable 符號）

baseline: d362e242df5c7b8f7bf94de1f7486cf9a1d50c74

## 實作總覽

Bundle（18 條 neutral rules＋guide，92,091B）已撞 90KiB gate（92,160B）——A6/M3 弧的 rg glob 陷阱行想進 rules 因無空間回退（2026-08-24 首次觸發下沉決策點）。本 EP 執行系統性減量：**下沉任務型、保留行為校準、去重重組、壓縮論證**，目標釋出 ≥10KB（bundle → ~77-80KB，gate 的 84-87%）。

分類判準（既定分層原則，先例：acceptance-evidence/lsp-navigation/instruction-writing 三組 08-21 分層）：

- **always-on（保留 rule）**：每 session 需要的硬紀律＋組命令當下的行為校準（tool-discipline、fd/rg 陷阱、must-execute、outward-action-consent 等）
- **任務觸發型（下沉 skill）**：特定任務出現時才需要的知識（instruction 檔寫作、STATE.md 寫入、盤點、library 查詢、EP 規劃）
- **語意重複（重組/壓縮）**：同知識多重表示（lsp 三重表示）、可推導導航內容、非承重論證

**承重牆聲明**：下沉效果完全依賴目標 skill 的 `description` 語意匹配——任務出現時 skill 要被載入。每個下沉動作必須同步校準目標 skill description 的 trigger 詞（這是改檢索系統，非搬檔案）。

## UC 盤點（docs mode：受影響命令/rules 清單）

### 掃描範圍
`rules/*.md`（18 條 neutral bundle 成員逐條尺寸/段落量化已完成）、`ai-development-guide.md`、`skills/`（目標載體 description）、引用面 rg（見段落 0）。ai-rules 無 `.kanban/`、無 SYSTEM-MAP.md——元專案正當跳過建卡。

### 既有 UC 狀態

| 能力（載體） | 狀態 | 影響 |
|------|------|------|
| instruction 檔寫作規範（instruction-writing skill＋三條 rules） | ✅ | 更新——吸收 `_ai-behavior-constraints`＋`self-consistency` 兩條 rule 全量 |
| STATE.md 寫入程序（`skills/_common/state-md-write.md`） | ✅ | 更新——吸收 context-management 的 STATE.md 段；rule 留 pointer |
| 驗收證據深層理論（acceptance-evidence skill） | ✅ | 更新——吸收「盤點執行點雙掃」段 |
| LSP 導航深層參考（lsp-navigation skill） | ✅ | 更新——吸收 Agent Prompt 工具選擇段 |
| 驗證策略（validation-strategy skill） | ✅ | 更新——吸收 quality-constraints「整合器型變更判定」段 |
| context7 MCP 查詢 | 📋 新增 | `skills/context7/SKILL.md`（自 rules/context7.md 整檔遷入） |

無新增程式碼 UC；全部為文檔載體遷移與內容重組。

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 消費端 session 修改 AGENTS.md | instruction 檔編輯任務 | instruction-writing skill 經語意匹配載入，元資訊禁止＋六維自洽知識可達 | 新 session 抽查（S5） | instruction 檔寫作規範 |
| SM-2 | 自主 session 結束寫 STATE.md | /at、/deep-work 觸發 | state-md-write 載入（at/deep-work/handoff 已引用）——rule 縮減後 pointer 仍指得到 | rg 引用驗證 | STATE.md 寫入程序 |
| SM-3 | user 問 library/framework 用法 | 文檔查詢任務 | 新 context7 skill 載入，查詢步驟可達 | skill description trigger 詞審查 | context7 MCP 查詢 |
| SM-4 | rules 變更後部署 | `uv run python scripts/deploy_agents.py` | gate [OK]＋bundle 尺寸下降至目標區間 | 每段強制跑 | — |
| SM-5 | 引用斷鏈（下沉後殘留） | 任何檔仍 link 已刪 rule | rg 殘留 0——`rg "_ai-behavior-constraints|rules/self-consistency|rules/context7"` 命中需全部是歷史文檔（EP 歸檔/memory 免改） | 每段驗證 | — |
| SM-6 | 壓縮誤刪承重論證 | 論證壓縮段（S4） | 每刪一句套判準「此論證是否對應易被 rationalize 動搖的規則」——是則留；diff 逐行核對刪除行 | S4 逐處 | — |
| SM-7 | 新 session bundle 載入 | 部署後開新 session | sentinel 尾行 `<!-- bundle-end -->` 在場、無截斷、下沉知識可經 skill 讀取 | S5 抽查 | — |

## 段落 0：全域研究摘要（已完成——2026-08-24 稽核輪）

**尺寸事實**（`wc -c` 實測）：bundle = 18 rules 81,192B＋guide 9,875B＋包裝 ≈ 92,091B；gate 92,160B（deploy_agents.py `BUNDLE_MAX_BYTES`）；ZCode 硬截斷線 102,400B（`zcode.cjs`，靜默）。Claude-scope 三條（bash-hard-rules/model-routing/code-edit-constraints）不在此 bundle。

**逐條判定與釋出估計**（保守，pointer 行成本 120-200B/處）：

| 段落 | 標的 | 動作 | 釋出 |
|------|------|------|------|
| S1 | `_ai-behavior-constraints.md`（3,053B——三段下沉、python -c 段拆出保留）＋`self-consistency.md`（2,968B——六維下沉、single-source drift 核心留 rule）＋`context7.md`（1,046B） | 整檔下沉×1＋拆分下沉×2 | ~5.6KB |
| S2 | context-management「STATE.md 段」（1,651B）＋modern-cli「盤點執行點雙掃」段（1,294B） | 段落下沉 | ~2.6KB |
| S3 | lsp-navigation 決策樹(1,057)＋速查(1,091)＋分工(667) 合併；Agent Prompt 段(1,101)＋quality「整合器型判定」(~1,300) 下沉 | 重組＋下沉 | ~2.7KB |
| S4（可選段） | quality crash-only 論證壓縮、python-standards `__init__` 論證、llm-output 自檢清單(642)、acceptance「與既有規則的關係」 | 論證壓縮 | ~1.2KB |
| S5 | rg glob 陷阱行回補（~300B）＋全域驗證 | 回補 | −0.3KB（消耗） |

合計毛額 ~12.1KB、扣除 S5 回補 0.3KB → 淨釋出 ~11.8KB → bundle ≈80.3KB。**部分做論證**（R7）：S1-S3 ≈10.9KB 毛額已達「淨釋出 ≥10KB」目標（≈81.8KB）——S4 標可選段（08-21 誤刪前科＋R2 已移除其中一項，時間/風險考量可跳過，不影響達標）；建議仍做（本 EP 動機含語意精簡）。

**明確不動清單**（審查時勿越界）：guide（9,875B 頂層原則保守不動）、tool-discipline、must-execute-before-complete、progressive-validation、instruction-writing（rule 本體已是 pointer 形態）、edit-discipline、deep-thinking（輸出格式模板是 08-21 審查輪特意恢復的，禁止再壓）、outward-action-consent（安全規則不壓縮）、modern-cli 的 fd/rg 陷阱段＋統計禁 head 段（行為校準）。

**引用面盤點**（rg 實測起點，每段執行時重新 rg）：

- `_ai-behavior-constraints`：8 檔——`AGENTS.md`（repo）、`ai-development-guide.md`、`rules/AGENTS.md`、`rules/instruction-writing.md`、`skills/{ep-review,execution-plan,instruction-init,instruction-writing}/SKILL.md`
- `self-consistency`：3 檔——`rules/AGENTS.md`、`skills/consistency/SKILL.md`、`skills/instruction-writing/SKILL.md`
- `rules/context7`：1 檔——`skills/arch-thinking/SKILL.md`
- `state-md-write`：已接線（`skills/{at,deep-work,handoff}/SKILL.md` 引用）
- `盤點執行點`：僅 `rules/modern-cli-preference.md` 自身（無外部引用——遷移無 ripple）

**風險假設**：

- 【高】skill 語意匹配能在任務出現時載入下沉內容——驗證：S5 新 session 抽查＋每個目標 skill description trigger 詞審查（「修改 AGENTS.md / instruction 檔」「STATE.md」「文檔自洽」「library 文檔」等字面任務詞要在 description 內）
- 【高】壓縮不誤刪承重論證（08-21 壓縮輪有誤刪 5 處、審查才救回的前科）——驗證：S4 判準＋逐行 diff
- 【中】引用面完整——驗證：每段 rg 殘留掃＋語義反向撈（`rg "共用規範|與.*共用"` 類同義表述）

**部署事實**（R6 回寫）：`~/.claude/rules`、`~/.claude/skills`、`~/.zcode/skills`、`~/.agents/skills` 皆 symlink 直指本 repo——刪 rule 檔即同步改變 Claude 端 always-on 面（無殘留副本 drift 風險），下沉知識對 mosaic/NT 等消費端 session 經 skills symlink 可達性成立；deploy_agents.py 以 harness-scope 動態掃 `rules/*.md`，無硬編碼清單——刪檔安全。

## EP Review Findings

審查輪 2026-08-24（獨立 Explore agent，五維度＋深層思考；自證含 12 rules 原文＋5 目標 skill＋deploy_agents.py＋引用面 rg 覆核＋symlink 驗證）。結論：有條件執行→修正後全數回寫，可開工。

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| R1 | 🔴 必須修正 | S1 | `_ai-behavior-constraints` 實含**四段**——「python -c 禁註解」是跨任務 bash 行為校準非 instruction 寫作知識，整檔下沉＝高頻知識退出 always-on | 該段保留（併 tool-discipline），其餘三段下沉；錨點列四段明示拆分 | implemented |
| R2 | 🟡 建議 | S4-#5 | collaboration「Agent 派發」段實測不含並發/模型細節（在 agent-workflow skill）、內容多屬保留清單——重疊前提不成立 | S4-#5 移除 | implemented |
| R3 | 🟡 建議 | S2 | context-management 的 STATE.md 段**非連續**（Memory 寫入紀律段插在中間）——連續抽取會誤搬 | 錨點明示非連續抽取 | implemented |
| R4 | 🟡 建議 | S1 | `rules/AGENTS.md` 清單表（:55/:56/:68 鄰域）**確定**列有三條標的 rule，非「若提及」 | S1 改確定動作：清單表三行同步 | implemented |
| R5 | 🟡 建議 | S1 | self-consistency 的 single-source drift 段適用範圍含 code 定義源（review-engine 共通邏輯）非僅 .md——純下沉漏 code 場景 | 六維檢查下沉；rule 端留 single-source drift 核心句＋pointer | implemented |
| R6 | ℹ️ 提醒 | S5 | Claude 端 `~/.claude/rules` symlink 載入面變化未寫入 EP | S5 補 Claude 端驗證步 | implemented |
| R7 | ℹ️ 提醒 | 全域 | 五段全做 vs 部分做無論證（S1-S3 已達標） | 總覽補論證＋S4 標可選段 | implemented |
| R8 | ℹ️ 提醒 | — | 產出方向合規驗證通過（S3/S4 先後互動正確處理）；無需修改 | — | noted |
| R9 | ℹ️ 提醒 | S3 | lsp-navigation skill 的 description 現有表述列舉 rule 端內容（決策樹/工具速查）——合併刪減後需同步改 | S3 要點補 description 修正 | implemented |

## 段落劃分原則

- 五段各自獨立 commit（每段：修改 → rg 殘留 → deploy gate → consistency 變更檔 → commit）
- 風險升序排列（S1 純遷移低風險 → S4 壓縮最高風險）；S5 依賴 S1-S4 的釋出空間
- 段落間無程式碼依賴；S3 的 lsp 重組與 S1 的 lsp-navigation skill 吸收動作同檔不同段——S1 先行（skill 檔案先建好段落結構），S3 再寫入重組內容

---

## S1：拆分下沉×2＋整檔下沉×1——_ai-behavior-constraints＋self-consistency＋context7

### Context

三條 rule 的**多數內容**是任務觸發型（非 always-on）：`_ai-behavior-constraints` 的元資訊禁止知識（只在寫/改 instruction 檔時相關，且開頭警告與 guide 頭部重複）；`self-consistency` 的文檔自洽六維檢查（只在編輯 `.md` instruction 檔時觸發）；`context7`（MCP 工具查詢步驟——只在 library 文檔問題時觸發）。**兩處例外保留 rule 端**（R1/R5 回寫）：①「Bash python -c 禁止寫註解」段是跨任務行為校準（任何 coding session 組 `python -c` 都可能踩）→ 併入 tool-discipline.md（其 Python 命令執行段）；②single-source drift 的核心紀律適用範圍含 **code 定義源**（review-engine 共通邏輯等），非僅 .md → rule 端留核心句＋pointer。先例：instruction-writing rule 本身已是 pointer 形態。

依賴：無段落間依賴（S3 會在 lsp-navigation skill 上疊代，先建殼）。
語義約束：與 S5 共享——回補的 rg glob 陷阱行進 modern-cli，不進本段目標 skills。

錨點（段落標題錨，非行號——docstring 增刪會讓行號位移）：

- 源：`rules/_ai-behavior-constraints.md` **四段**——「🔴 強烈警告：AI 禁止行為」表／「🔴 Bash 強烈警告：python -c 禁止寫註解」（**拆出，併 tool-discipline**）／「執行約束」／「自檢清單」（後三段下沉）
- 源：`rules/self-consistency.md`——「核心檢查原則」＋五檢查項＋快速自檢清單（下沉）；其中「single-source drift 防護（修改紀律）」子段的核心句（「改定義源→強制 `rg "<單一關鍵詞>"` 掃所有引用，逐檔同步」）**留 rule**
- 源：`rules/context7.md` 全檔（四步流程）
- 目標：`skills/instruction-writing/SKILL.md`（新增兩章：「元資訊禁止」（吸收 behavior-constraints 三段，含 ❌/✅ 表）＋「六維自洽檢查」（吸收 self-consistency 全量含 single-source drift 細節——rg alternation 陷阱、案例））；`skills/context7/SKILL.md`（新建，frontmatter description 含 trigger 詞：library/framework/SDK/API/文檔查詢/Context7 MCP）

### 修改要點（docs mode——無 pseudo code）

1. 下沉內容遷入 instruction-writing skill 對應章節（語義保持，編排可調適 skill 體例；**禁止趁機精簡**——本段是純遷移，壓縮屬 S4 且此三檔不在 S4 清單）
2. python -c 段遷入 `rules/tool-discipline.md` 的 Python 命令執行段之後（同檔主題群聚）
3. 刪除 `rules/self-consistency.md`、`rules/context7.md`；`rules/_ai-behavior-constraints.md` 縮為：single-source drift 核心句＋兩行 pointer（元資訊禁止／六維自洽→instruction-writing skill）——**檔名保留**（被 8 檔引用，整檔刪除的引用面成本大於縮檔；檔頭 harness-scope 等 frontmatter 保留）
4. `rules/instruction-writing.md` pointer 行同步（涵蓋元資訊禁止與六維檢查指向）
5. 引用面遷移（rg 實測 8+3+1 檔，逐一改指向 skill）：`ai-development-guide.md` 頭部警告 link、repo `AGENTS.md`、`skills/{ep-review,execution-plan,instruction-init,consistency,arch-thinking}` 的 rule 引用改 `../instruction-writing/SKILL.md` 或 `../context7/SKILL.md`
6. **`rules/AGENTS.md` 清單表確定動作**（R4）：三行同步——self-consistency/context7 標已下沉（或移除 row 視該表語義——「部署清單」表的 row 對應檔案存在性；_ai-behavior-constraints 檔名保留故 row 保留）
7. `skills/CLAUDE.md` 索引加 context7 skill 行；instruction-writing skill 索引行描述同步
8. instruction-writing skill frontmatter description 補 trigger 詞（「修改 instruction 檔／AGENTS.md／元資訊清理／文檔自洽／single-source drift」）

### 驗證策略（docs mode）

- rg 殘留：`rg -l "rules/self-consistency|rules/context7" rules/ skills/ ai-development-guide.md AGENTS.md` → 0 hits（歷史 EP/memory 免改；`_ai-behavior-constraints` 檔名保留故其引用不需清）
- 內容存活：skill 內 `rg "絕對禁止|Decoder Test|單一關鍵詞|resolve-library-id"` 命中；tool-discipline 內 `rg "python -c"` 命中；rule 端 `rg "single-source"` 核心句在場
- `uv run python scripts/deploy_agents.py` → [OK] 且尺寸下降 ~5.6KB（92.1→~86.5KB）
- `/consistency skills/instruction-writing/SKILL.md`＋`skills/context7/SKILL.md`＋`rules/tool-discipline.md`
- CJK 損壞防護：遷移後 `rg "脀|讂"`（形似異體字）0 hits

---

## S2：段落下沉×2——STATE.md 段＋盤點雙掃段

### Context

`context-management.md` 的「STATE.md（Last session 觀察層）」段（1,651B）內容（職責矩陣/邊界/生命週期/路徑/觸發）只在 at/deep-work/handoff 觸發的寫入程序中需要——載體 `skills/_common/state-md-write.md` 已存在且已被三 skill 引用。`modern-cli-preference.md` 的「盤點執行點：間接層與直呼層雙掃」段（1,294B）是盤點任務（CI/入口/影響域）時才需要——語義歸屬 acceptance-evidence skill（完整性盤點家族，同 skill 已有 consumers 41 誤寫 20 案例）。

依賴：無。
語義約束：context-management 保留的「Session 管理」（糾正策略/context 保護）與「Memory 寫入紀律」不動——只遷 STATE.md 段。

錨點：

- 源：`rules/context-management.md`「## STATE.md（Last session 觀察層）」——**非連續抽取**（R3）：該 `##` 段內「職責矩陣/邊界/Open failures」為前半；**「## Memory 寫入紀律（cluster-first）」是獨立 `##` 段、插在中間、保留原位不動**；STATE.md 的「生命週期/路徑/觸發」在 Memory 段之後（同 `##` STATE.md 段的尾部）——跨段取出尾部三小節，勿整塊連續搬
- 源：`rules/modern-cli-preference.md`「## 盤點執行點：間接層與直呼層雙掃」整段（含雙掃表＋反例——連續，可直接搬）
- 目標：`skills/_common/state-md-write.md`（併入職責矩陣等——注意該檔現有「寫入步驟」結構，遷入內容編排融入）；`skills/acceptance-evidence/SKILL.md`（新增「盤點執行點雙掃」章）

### 修改要點

1. 兩段內容遷入目標 skill（純遷移，禁止精簡）
2. 源 rule 各留一行 pointer：「STATE.md 寫入紀律與職責邊界見 skills/_common/state-md-write.md（寫入由 at/deep-work 觸發）」；「盤點執行點雙掃見 acceptance-evidence skill」
3. `skills/context-management` 相關引用面：`rg "STATE.md" rules/ skills/`——rule 內僅剩 pointer；at/deep-work/handoff 對 state-md-write 的引用已存在無需動
4. acceptance-evidence skill description 補 trigger 詞（「盤點執行點／誰呼叫／影響域／CI 執行點」）

### 驗證策略

- 內容存活：`rg "觀察層|職責矩陣|kanban Backlog" skills/_common/state-md-write.md`＋`rg "間接層|直呼層|build.yml" skills/acceptance-evidence/SKILL.md` 命中
- 殘留：`rg "STATE.md" rules/context-management.md` 僅 pointer 行；`rg "盤點執行點" rules/` 僅 pointer
- deploy → [OK]（~86.5→~83.9KB）
- consistency 兩目標 skill 檔

---

## S3：lsp-navigation 去重重組＋兩段下沉

### Context

lsp-navigation（8,839B）三段——「決策樹」（1,057B）、「LSP 工具速查」（1,091B）、「與 rg/fd 的分工」（667B）——是**同一映射（查什麼 → 用什麼工具）的三重表示**，合併為單一速查表。「Agent Prompt 工具選擇」段（1,101B）只在 spawn 符號查詢 agent 時需要 → 下沉 lsp-navigation skill。quality-constraints「整合器型變更判定」段（Fail Loud 段內，~1,300B）是 EP 規劃時才需要 → 下沉 validation-strategy skill（語義契合：驗證策略）。

依賴：S1 已建立 instruction-writing skill 章節結構（無直接依賴，但同為 skill 檔案疊代，序位在後降低 Edit 衝突）。
語義約束：合併後的單一表**必須涵蓋三表示的全部分支**——決策樹的每個葉節點、速查表的每個 operation、分工表的每個查詢類型都要在新表可查到（這是等價重組非壓縮；遺漏任何分支＝語義損失）。

錨點：

- 源：`rules/lsp-navigation.md`「## 決策樹」「## LSP 工具速查」「## 與 rg/fd 的分工」「## Agent Prompt 工具選擇」四段標題
- 源：`rules/quality-constraints.md`「### 整合器型變更判定」＋「兩層整合測試」表（同屬 Fail Loud 段內的子結構）
- 目標：`skills/lsp-navigation/SKILL.md`（Agent Prompt 段遷入）；`skills/validation-strategy/SKILL.md`（整合器型判定遷入）

### 修改要點

1. 三表示合併：以「LSP 工具速查」表為骨架，補入決策樹獨有分支（註解/字串/config→rg；檔案→fd；Markdown/YAML→rg；被刪的三個 `^` 錨定樹狀分支語義）與分工表獨有欄（降級欄），刪決策樹樹狀圖與分工表
2. Agent Prompt 段整段遷入 lsp skill（含 audit-test/judge-review 工具指定模板）
3. 整合器型判定段遷入 validation-strategy skill；quality-constraints 留一行 pointer（「整合器型變更判定與兩層整合測試見 validation-strategy skill」）
4. lsp-navigation rule 的「反例速覽」與「Tool Discovery 強制 step」**不動**（行為校準）
5. lsp skill＋validation-strategy skill description 同步：**補 trigger 詞**（「spawn agent 工具指定」「整合器型變更／真實邊界整合測試」）＋**修正現有表述**（R9——lsp skill description 列舉 rule 端內容「決策樹、工具速查」，合併後分工表/決策樹不復存在於 rule，列舉文字要對齊合併後實況）

### 驗證策略

- 等價重組驗證（本段核心）：合併前逐表示列出分支清單（決策樹葉節點/速查 operations/分工行），合併後逐一核對在新表可查——列成 EP review 附表
- 殘留：`rg "Agent Prompt|整合器型" rules/lsp-navigation.md rules/quality-constraints.md` 僅 pointer
- 內容存活：`rg "goToImplementation|judge-review 符號查證|mock 循環論證" skills/lsp-navigation/SKILL.md skills/validation-strategy/SKILL.md` 命中
- deploy → [OK]（~83.9→~81.2KB）
- consistency 兩 rule＋兩 skill

---

## S4：論證壓縮×4（可選段——最高風險，08-21 誤刪前科）

### Context

四處內容屬「非承重論證或重複」：可壓縮（S4-#5 collaboration 已移除——R2：重疊前提經 rg 驗證不成立，段落內容幾乎全屬保留清單）。**判準（每刪一句前套用）**：此論證是否對應「易被 rationalize 動搖的規則」？是 → 保留論證；否 → 可壓。對照 08-21 前科（壓縮誤刪 deep-thinking 輸出格式模板等 5 處，審查才救回）。本段標**可選**：S1-S3 已達 ≥10KB 釋出目標，時間/風險考量可跳過（R7）。

錨點（段落標題）：

1. `rules/quality-constraints.md`「### 誤用警告：crash-only 不是『graceful 不修』的藉口」——保留禁則三句與 mosaic ReplayHost 實例一句，壓縮論證展開（~600B→~250B）
2. `rules/python-standards.md`「### 補充論證：Facade Pattern 為何不適用內部專案」——禁令本體不動；論證壓為兩句（內部專案消費者場景＋`_internal` 模式出口）（~500B→~200B）
3. `rules/llm-output-convention.md`「## 執行自檢清單」——與慣例段重複，壓為一行指回（~642B→~120B）
4. `rules/acceptance-evidence.md`「## 與既有規則的關係」——對應表壓為兩行散文（導航性內容）（~500B→~180B）

### 修改要點

每處：Read 全文 → 套判準逐句標記留/壓 → 重寫 → `git diff` 逐行核對刪除行（確認無誤刪判準為「是」的論證）→ CJK rg 驗證。

### 驗證策略

- 判準對照表：每處壓縮在 commit message 附「刪除論證清單＋各條為何非承重」
- 禁區驗證：`rg "Tesla|生產地獄" rules/deep-thinking.md` 仍在（不動清單抽樣）；`rg "兩層整合測試" rules/quality-constraints.md` 已遷 S3（本段不碰）
- deploy → [OK]（S4 執行：~81.2→~80.0KB；跳過 S4 則止於 ~81.2KB）
- consistency 四檔

---

## S5：回補＋全域驗證收尾

### Context

依賴 S1-S4 釋出的空間。回補 A6/M3 弧因 gate 回退的 rg glob 陷阱行；執行跨 session 驗證（skill 語意匹配承重牆的最終檢驗）＋文檔收尾。

### 修改要點

1. `rules/modern-cli-preference.md` fd/rg 陷阱段加行（內容定稿）：「**rg `-g` glob 錨定路徑 arg 形態**：`-g '!dir/**'` 對絕對路徑 root arg 靜默失效——要生效用 cwd＋arg `.` 或 `!**/dir/**`（hazard runner 實案：mock 全繞過、真 rg 測試才抓到）」
2. `rules/AGENTS.md` 部署紀律段：若提及被下沉 rule 名，同步（rg 檢查）
3. 新 session 抽查（開新 ZCode session）：bundle 尾行 sentinel 在場、`rg "bundle-end"` 於 system context 可見、下沉知識（instruction-writing skill 的元資訊禁止章）經 skill 清單可達
4. 最終 deploy：達標判準＝**淨釋出 ≥10KB**（S1-S3 路徑 bundle ≈81.8KB；S4 執行路徑 ≈80.3KB）——尺寸記錄進收尾報告

### 驗證策略

- deploy [OK]＋尺寸記錄進收尾報告
- 新 session 抽查結果（SM-7）記錄；失敗（skill 不可達/截斷）→ 修正 description 或回滾該下沉項
- **Claude 端驗證**（R6）：`ls ~/.claude/rules/` 確認被刪 rule 檔已不在（symlink 直指 repo，應自動成立——驗證而非假設）；`ls ~/.claude/skills/context7/` 確認新 skill 對 Claude 端可達
- `/consistency` 對本段變更檔

---

## 整合策略

- 每段獨立 commit（message 帶該段釋出 bytes）；段間無 code 依賴，可跨 session 接續（EP 段落自足）
- 全域 invariant：每段後 bundle 必須 gate [OK]（禁止「先多刪後回補」的中間超標態被 commit）
- **前置條件**：A6/M3 弧（scip_refs＋hazard 收編，16 檔）須先 commit——本 EP 變更集與之近乎不相交（僅 `skills/CLAUDE.md` 疊代），實作 session 開工前 `git status` 確認 working tree 乾淨，不乾淨先停下回報
- 實作 session 為新 session（ai-rules session 單一寫入者慣例）；build 走 `/implement` docs mode 分支

## 收尾步驟（docs mode）

1. ~~Capabilities/Kanban~~：元專案跳過——改為「受影響 rules/skills 行為已反映＋`skills/CLAUDE.md` 索引同步（context7 新行＋instruction-writing 描述更新）」
2. `/consistency` 對全部變更 `.md` 最終輪
3. `/sync-sources`（bundle 新鮮度＋single-source invariant 機械檢查——本 EP 大量動定義源，必跑）
4. 收尾報告：各段釋出 bytes 累計、最終 bundle 尺寸、新 session 抽查結果、殘留項清單
