# 跨 harness instruction-file 撰寫 guideline 合成草案

> 合成者：判斷密集合成 agent（2026-09-12）。輸入＝八份研究檔（四家 extraction＋mentor）＋三份既有載體（`ref-docs/harness/contracts.md`、`skills/instruction-writing/SKILL.md`〔下稱 IW skill〕、`rules/AGENTS.md` 中性化規範）。未來併入 instruction-writing skill 時以本稿為素材，不直接落地。
>
> **簡稱表**：CCX/CCM＝`claude-code-extraction.md`/`claude-code-mentor.md`；CDX/CDM＝`codex-*`；MUX/MUM＝`muse-*`；ZCX/ZCM＝`zcode-*`。錨點格式：`<鏡像相對路徑>:行`（來自對應 extraction 檔）。標記：〔官方〕〔mentor 採納〕〔ai-rules 經驗〕〔合成推論，待審〕；重疊於 IW skill 處標「既有知識確認」。
>
> **措辭紀律（CDM 採納）**：「鏡像未提及」＝本次鏡像搜尋未命中，非「官方沒有此機制」。negative claim 一律用此措辭。

## 0. 已採納的 mentor 修正（寫進下文事實的差異源）

| # | 修正 | 採納後寫法 |
|---|---|---|
| 1 | CC skill frontmatter 分兩層：Agent Skills standard vs CC extension fields（CCM §4，`docs/en/skills.md:359-374`） | 跨家可攜欄位＝standard 子集；CC 豐富欄位是 extension |
| 2 | CC skill eval：runtime 無內建評分，官方有 eval workflow 文檔（CCM §3，`skills.md:804-827`） | description 品質靠 eval 流程（fresh-session baseline＋A/B），非 runtime 分數 |
| 3 | Codex negative claim 措辭（CDM §3） | 全稿措辭紀律（見上） |
| 4 | Codex untrusted project 跳過整個 `.codex/` layer＝獨立機制（CDM §4，`config-file/config-basic.md:37`） | 列入層級 trust-gate 規律 |
| 5 | Codex Goal/Context/Output/Boundaries 是分解模型非 schema（CDM §4，`prompting.md:23`） | 寫作通則標「模型非模板」 |
| 6 | Muse `muse init` 存在：生成與載入機制有文檔、內容寫作規範鏡像未提及（MUM §3） | Muse 軸 7 缺口精確化 |
| 7 | Muse workflow prompt「結構夠用就好、實作細節留給 author」＋isolation 失敗 reject 不 fallback（MUM §4）；hook 一 hook 綁一事件（MUM §4） | 寫入 3a/矩陣 |
| 8 | ZCode Command frontmatter 有 `allowed-tools`、Skill 白名單無此欄——兩者非同一 metadata 模型；plugin 是團隊分發邊界（ZCM §4） | 寫入 3d |

## 1. 七軸×四家異同矩陣

### 軸 1 Instruction 檔

| 家 | 一句話＋錨點 |
|---|---|
| CC | CLAUDE.md 四層（managed/user/project/local）全部 concatenate 不覆蓋、root 往下排序、子目錄層延遲載入；200 行軟目標、4MiB 整檔跳過（CCX 軸1；`docs/en/memory.md:54-63,81,405`） |
| Codex | AGENTS.md 三層 precedence：global（override>AGENTS.md 首個非空）→ project walk-down（root→cwd 每目錄至多一檔）→ concatenate 合併，合計 32KiB 停加（CDX 軸1；`agent-configuration/agents-md.md:9-15`） |
| Muse | workspace root 往上至 `.git` 邊界每層四檔（AGENTS.md→CLAUDE.md→.agents/AGENTS.md→.claude/CLAUDE.md）首命中勝出；project 勝 user、深勝淺＝替換非合併；project 需 trust（MUX 軸1；`muse-code/configuration.md:41-46`） |
| ZCode | 只讀全域＋workspace 兩檔（全域前、工作區後串接）；不合併多層、不掃子目錄、不展開 @import、不依任務選規則檔（ZCX 軸1；`cn/docs/agents.md:66-78`） |

### 軸 2 Rules 機制

| 家 | 一句話＋錨點 |
|---|---|
| CC | `.claude/rules/*.md` 一檔一主題遞迴發現；無 `paths` 啟動載入（優先同 `.claude/CLAUDE.md`）、有 `paths` 檔案匹配觸發；user 先載、project 優先（CCX 軸2；`docs/en/memory.md:187-269`） |
| Codex | rules＝沙箱外命令 exec policy（Starlark `.rules` 檔），與 instruction 生態零耦合；多規則命中取最嚴格（forbidden>prompt>allow）；`match/not_match` 載入時驗證（CDX 軸2；`agent-configuration/rules.md:5-65`） |
| Muse | 「rules」名稱存在於 trust 語境但無獨立機制文檔；與 skills/hooks 同組 trust 後才載（MUX 軸2；`muse-code/configuration.md:110`） |
| ZCode | 無獨立 rules 機制，官方明說不依任務類型選規則檔（ZCX 軸2；`cn/docs/agents.md:78`） |

### 軸 3 Memory

| 家 | 一句話＋錨點 |
|---|---|
| CC | 兩系統互補（CLAUDE.md 人寫／auto memory Claude 記）；MEMORY.md 索引 200 行或 25KB 先到者載、topic 檔按需；machine-local、同 repo worktree 共享目錄（CCX 軸3；`docs/en/memory.md:23,344-409`） |
| Codex | local memory store 預設關、`~/.codex/memories/`、generated state 禁手編當控制面；恆常規則須放 AGENTS.md，memory 只是 recall 層（CDX 軸3；`customization/memories.md:63,89,118`） |
| Muse | 三 scope（personal-project 預設／project `.agents/memory/` 進 repo／personal 機器級）；開場只注入索引（MEMORY.md＋路徑清單 ≤48 檔）；committed memory 未信任也載＝prompt-injection 面、沙箱內 `.agents` 唯讀（MUX 軸3；`muse-code/configuration.md:93-114`、`permissions.md:77`） |
| ZCode | 預設關（v3.6.4+）、每輪成功結束自動提煉；四類刻意不記（可再讀的 code/Git、指令檔已有、對話臨時）；主對話專用、子代理不讀不寫（ZCX 軸3；`cn/docs/memory.md:38-65`、`agents.md:91`） |

### 軸 4 Skills

| 家 | 一句話＋錨點 |
|---|---|
| CC | SKILL.md＝Agent Skills 開放標準＋CC extension 欄位分層；全欄位 optional 僅 description recommended；listing 預算＝context 1%、desc+when_to_use 合併截 1,536；SKILL.md <500 行、body 跨 turn 常駐（CCX 軸4＋CCM；`docs/en/skills.md:19,328-374,472,1052`） |
| Codex | agentskills.io 標準 name+description 必填；progressive disclosure（初始只給 name/description/路徑）；初始清單預算 2% context 或 8,000 字元、超量先縮 description 再省略；同名不 merge 兩者並存（CDX 軸4；`build-skills.md:33-135`） |
| Muse | 四源掃描含跨 harness 自動發現（`~/.claude/skills`、`$CODEX_HOME/skills`）；`muse skills` CLI 全套（validate 存在）；frontmatter 欄位契約鏡像未提及（MUX 軸4；`muse-code/extending.md:60-72`） |
| ZCode | name+description 必填（缺＝整技忽略＋診斷）；白名單 5 欄（name/description/when_to_use/license/metadata）其餘忽略；description>1,024 字元整技丟棄非截斷、正文 >100KB 截斷載入；清單共享預算超載降級只留名（ZCX 軸4；`cn/docs/skill.md:58-62`、`plugin.md:176-182`） |

### 軸 5 Agents（subagents）

| 家 | 一句話＋錨點 |
|---|---|
| CC | md＋YAML frontmatter、body＝system prompt（完全替換預設 system prompt）；五層載入優先序；desc 合計 15,000 tokens 警告；custom 子代理載入全部 CLAUDE.md 層（Explore/Plan 例外）；巢狀上限三層（CCX 軸5＋CCM；`docs/en/sub-agents.md:265-347,834,983,1033`） |
| Codex | standalone **TOML** 一檔一 agent＝spawned session 的 config layer；必填 name/description/developer_instructions＋可帶任何 config.toml key；custom 同名蓋內建、name 欄位是身分真相源（CDX 軸5；`agent-configuration/subagents.md:336-393`） |
| Muse | lead 為 bounded task spawn 子代理；worktree isolation 逐子請求且失敗 reject 不靜默回落；容量預設 8（可 1-64）；observers×4 提案-調解制（MUX 軸5；`muse-code/extending.md:21-48`）；subagent 定義檔格式鏡像未提及（MUX 未提及清單） |
| ZCode | md＋frontmatter、body＝系統提示詞；**僅 user 級 Beta**；`thoughtLevel` 非 effort（未知欄位靜默忽略）；不可巢狀、快照制改後須新 session；v3.7.1+ 預設注入兩份 AGENTS.md（Explore 除外）（ZCX 軸5；`cn/docs/subagents.md:74-94`） |

### 軸 6 Hooks＋設定

| 家 | 一句話＋錨點 |
|---|---|
| CC | hooks 住 JSON settings 七位置、跨層 merge 不取代；事件面最廣（21 事件）；與 CLAUDE.md advisory 對比的 deterministic（CCX 軸6；`docs/en/hooks.md:253-278`、`best-practices.md:231`） |
| Codex | event→matcher→handler 三層；載入語義全部疊加不覆蓋；非 managed hooks 須 review-and-trust（hash 記信任，變更即失效）；untrusted 專案跳過整個 `.codex/` layer（CDX 軸6＋CDM；`hooks.md:49-73`、`config-file/config-basic.md:37`） |
| Muse | 13 事件、一 hook 綁一事件；SessionEnd 純觀察；三源（project `.muse/hooks.json` trust 後）；hook 跑沙箱外（MUX 軸6＋MUM；`muse-code/extending.md:83-94`） |
| ZCode | 本地子進程協議（stdin JSON→exit code＋stdout JSON）、7 事件子集；**user 級唯一下落點、專案層 hooks 整體忽略**（`config_project_hooks_ignored`）；per-session 快照（ZCX 軸6；`cn/docs/hooks.md:36-60`） |

### 軸 7 官方寫作哲學

| 家 | 一句話＋錨點 |
|---|---|
| CC | 一行一問取捨測試＋Include/Exclude 對照表＋當程式碼維護（review/prune/行為觀察）；context window 填滿退化是大多數 best practices 的底層公理（CCX 軸7；`docs/en/best-practices.md:174-190,19-23`） |
| Codex | keep small＋feedback loop＋近端放置＋三觸發收錄（重複犯錯/讀太多/重複 PR 回饋）；AGENTS.md 要配強制基建（pre-commit/linters）；Goal/Context/Output/Boundaries 分解模型非 schema（CDX 軸7＋CDM；`customization/overview.md:21-45`、`prompting.md:17-23`） |
| Muse | 記「agent 光靠通用知識會記錯的 durable 事實」；bounded responsibility＋final deliverable；narrow tool surface；instruction 文字品質直接影響答案品質（官方 rollback 過內建 instruction）（MUX 軸7；`muse-code/configuration.md:107`、`workflows.md:68`、`changelog.md:154`）；AGENTS.md 內容寫作規範鏡像未提及（MUM 精確化：生成/載入機制有、內容品質指導無） |
| ZCode | 穩定可複用約定、最重要放 workspace 層；description 寫清「什麼時候用」越具體越可靠；技能數量是 context 預算問題（只啟用常用）（ZCX 軸7；`cn/docs/agents.md:73-78`、`skill.md:59-66`） |

## 2. 跨家規律

### 2.1 載入模型光譜（誰載入誰、何時載入）

三種載入模型是載體分工的第一軸。每格＝該家該載體的實際載入時點：

| 載體 | CC | Codex | Muse | ZCode |
|---|---|---|---|---|
| instruction | always-on（launch）；子目錄層 on-demand（讀該目錄檔案時） | always-on（run start 建鏈，session 首回合注入限量 guidance——CDM：保留「首回合」原文限定） | user 層 always-on；project 層 trust 後 always-on | always-on（任務啟動，僅兩檔） |
| rules | 無 paths＝always-on；有 paths＝on-demand | **enforcement**（exec policy，啟動掃描） | trust 後 always-on（機制細節鏡像未提及） | 載體不存在 |
| skill | on-demand（叫用/相關/`paths` 觸發；nested 延遲） | on-demand（progressive disclosure） | on-demand | body on-demand；**元數據每輪注入**（ZCX 軸4） |
| memory | always-on 索引＋on-demand 條目；subagent 不載（fork 例外） | 預設 off→on-demand recall | always-on 索引（≤48 檔）＋on-demand 內容 | 預設 off→自動提煉；索引有上限截斷 |
| hook/config | enforcement | enforcement（＋trust 閘） | enforcement（沙箱外執行） | enforcement（7 事件子集、專案層失效） |

規律：**四家都用「always-on 給紀律、on-demand 給方法論、enforcement 給保證」的三層結構**，差異在載體名與觸發細節。寫作規範第一問永遠是「這內容要哪種載入模型」——決定了尺寸預算與收錄門檻（見 3b）。

### 2.2 尺寸預算三形態

| 形態 | 語義 | 實例（官方＋實測） |
|---|---|---|
| **軟目標** | 超限不截斷，只降 adherence（官方自述） | CC CLAUDE.md <200 行/檔（`memory.md:81`）、SKILL.md <500 行（`skills.md:472`） |
| **硬截斷** | 超限切掉內容，載體仍在 | Codex instruction chain 合計 32KiB 停止再加檔（`agents-md.md:15`）；ZCode 每檔 100KiB（102,400 bytes）讀前截斷〔ai-rules 經驗：`rules/AGENTS.md:28` 實測，官方未載〕；Muse delegation startup 共享 65,536 bytes 截斷＋警告〔ai-rules 經驗：`rules/AGENTS.md:29` 實測〕；CC CLAUDE.md 內容 4MiB 以下全載（`memory.md:405`）；skill 清單預算（CC 1% ctx／Codex 2% ctx 或 8,000 字元／ZCode 共享預算降級只留名）；memory 索引（CC/ZCode 200 行或 25,000 字元——contracts.md 雙端反組譯：「25KB」是顯示假象，計量是 UTF-16 字元） |
| **整檔丟棄** | 超限或缺欄整個載體不載 | CC CLAUDE.md >4MiB 整檔跳過（`memory.md:405`）；ZCode skill description>1,024 字元整技丟棄、name/description 缺失整技忽略（`skill.md:58-60`） |

寫作含義：**同一內容在三形態下的失敗模式不同**——軟目標是漸進退化（無聲），硬截斷是尾部靜默消失（ZCode 141KB 時代尾部 8 條 rules 失效事故，`rules/AGENTS.md:31`），整檔丟棄是觸發面直接消失（ZCode 超限 skill 連名字都不出現）。可驗證的寫作紀律必須針對形態分別設計（見 3d）。

### 2.3 層級語義三分

三個維度回答不同問題，不互斥：

| 維度 | 問題 | 各家行為 |
|---|---|---|
| **concatenate-merge** | 跨層檔案如何共存？ | CC 全部串接（`memory.md:157`）；Codex root-down 串接、後出現者在 prompt 較後位置＝實質覆蓋（`agents-md.md:13`）；ZCode 全域→workspace 兩檔串接（`agents.md:71`）——三家串接 |
| **first-wins** | 同層多個候選檔誰勝？ | Codex 同層 `AGENTS.override.md`>`AGENTS.md`>fallback 首個非空、每目錄至多一檔（`agents-md.md:11-12`）；Muse 同層四檔首命中＋**跨層是替換非合併**（深勝淺、project 勝 user，`configuration.md:43-44`）——兩家有同層競爭語義；CC/ZCode 無同層競爭（CC 同層 CLAUDE.local.md 排 CLAUDE.md 後仍串接） |
| **trust-gate** | project 層載入前有無信任閘？ | Muse project instruction 需 trust（memory 例外：committed memory 未信任也載，`configuration.md:46,110`）；Codex `.codex/` layer（config+hooks+rules）需信任、AGENTS.md 本身無閘（CDM 採納）；CC 用 managed policy 企業治理層（非 trust）；ZCode 專案層 hooks **直接忽略**（非 trust 可解，是現行安全策略，`hooks.md:58`） |

### 2.4 description＝四家共識的觸發面

- CC：skill 僅 description recommended（「so Claude knows when to use the skill」）；subagent description 決定路由；desc+when_to_use 截 1,536；品質靠官方 eval workflow（fresh-session baseline＋A/B＋description tuning，CCM 採納）
- Codex：implicit invocation depends on description——concise、clear scope and boundaries、**front-load key use case and trigger words**（超量縮 description 時前綴仍可匹配）（`build-skills.md:98`）
- ZCode：description 寫清「什麼時候用」、越具體越可靠、長說明放正文（`skill.md:59,66`）；subagent description 決定自動選用率（`subagents.md:69`）
- Muse：鏡像未明文 description 觸發語義；有 skill recall observer（背景提案-調解）機制。經 Agent Skills 標準繼承推定同語義〔合成推論，待審〕

結論：**三家明文＋一家標準繼承**——description 是跨家最一致的「投資報酬率最高欄位」：寫好一個欄位同時改善四家的觸發。

### 2.5 「可推導的不寫」共識度檢驗

結論：**instruction 端非四家共識；memory 端近共識**。

- instruction 端：CC 明文（`/doctor` 砍可推導內容 `memory.md:458`；Exclude 表「Anything Claude can figure out by reading code」`best-practices.md:176-184`）；Codex 僅「Keep it small／Start with only the instructions that matter」隱含（`customization/overview.md:21,32`）；Muse AGENTS.md 內容寫作規範鏡像未提及（MUM 精確化）；ZCode 有「穩定可複用」選擇原則但無可推導條款（`agents.md:73`）
- memory 端：CC「skips anything it can derive from the codebase」（`memory.md:344-351`）；ZCode 刻意不記可再讀的 code/Git 歷史（`memory.md:51`）；Muse 記「agent 光靠通用知識會記錯的事實」＝同一原則的正向表述（`configuration.md:107`）；Codex memory 是 generated state 禁手編（寫入端不適用）
- ai-rules 的 encoder-philosophy（IW skill「內容規範」）與 CC 官方完全同向——既有知識確認；且 ai-rules 把它推得更深（導航種子/LSP 分工是 ai-rules 獨有，官方鏡像均未提及）

### 2.6 官方寫作哲學共同骨架

四家獨立演化出同一組骨架，差異只在著墨深淺：

| 骨架 | CC | Codex | Muse | ZCode |
|---|---|---|---|---|
| **concise** | 一行一問取捨測試 | keep small | enough structure, leave details to author（MUM 採納） | 條目精簡、只啟用常用技能 |
| **specific** | Specificity：具體到可驗證 | repro+constraints 比高層描述重要 | 記「會記錯的 durable 事實」 | 觸發條件越具體越可靠 |
| **feedback-loop** | 犯第二次錯才收錄；當程式碼維護 | treat as feedback loop；codify 重複回饋 | grill-and-record 定案寫回文檔 | 自動提煉 memory（寫入側） |
| **result-oriented** | 說要做什麼別敘述 how/why（skill body） | start with the result, not steps | bounded responsibility＋final deliverable | 系統提示詞＝角色/邊界/規則 |
| **底層公理：context 稀缺** | 明文「most best practices derive from this one constraint」（`best-practices.md:19`） | context pollution／context rot | progressive disclosure＋narrow surface 更省 | 清單預算降級警告 |

CC 官方自己示範了本 guideline 的方法論：**寫作規範從消費行為（截斷、預算、觸發）推導，不是從優雅推導**——best-practices 全部由 context window 約束反推。這與 user 注入的「消費者驅動」視角一致，可作為 guideline 的方法論自證。

### 2.7 安全維度（instruction 即攻擊面）

- CC：CLAUDE.md 進 prompt 等同可公開文檔，禁 secrets（`blog/using-claude-md-files.md:185`）
- Muse：`--yolo`/trust 後 AGENTS.md 在 fork/PR checkout 上是 attacker-controlled instructions；committed memory 未信任也載＝prompt-injection 面（`permissions.md:107`、`configuration.md:110`）
- Codex：hooks 有 hash 級 review-and-trust；project config 有安全禁區鍵（`hooks.md:66`、`config-advanced.md:98`）
- ZCode：專案層 hooks 整體忽略＝把這條攻擊面整個關掉

規律：**載入器對「project 層可執行內容」的信任閘各不相同，但對「project 層 instruction 文字」三家直接載入**——寫作面結論：instruction 檔禁敏感資訊是跨家底線，且 fork 場景下 instruction 內容本身是注入載體。

## 3. Guideline 草案「怎樣寫 md」

### 3a 寫作通則（跨家最大公約數）

1. **取捨測試**：每行問「刪掉這行會讓 agent 犯錯嗎？」不會就砍；冗長檔讓 agent 忽略真正的指令。〔官方：CC `best-practices.md:174`〕（IW skill Low Noise 同向——既有知識確認）
2. **具體可驗證**：指令具體到可驗證（「2-space indent」非「format properly」）；boundaries 只加會造成真問題的一兩條。〔官方：CC `memory.md:85-89`、Codex `prompting.md:104,114`〕
3. **結構化**：markdown headers/bullets 分組——官方掃描結構的方式與讀者相同。〔官方：CC `memory.md:83`〕
4. **一致性**：矛盾指令被任意取捨，定期清跨檔矛盾。〔官方：CC `memory.md:91,440`〕（IW skill 五維檢查——既有知識確認）
5. **收錄觸發**：同錯二次／重複回饋才寫；每次新增解決真實遇到的問題，禁理論性擔憂。〔官方：CC `memory.md:43-48`、`blog:43`；Codex `overview.md:36-38`〕（ai-rules「寫入門檻：預設少寫」同向——既有知識確認）
6. **廣泛適用才進 always-on**：每 session 都載的載體只放每次都需要的內容；偶爾需要的下沉 skill。〔官方：CC `best-practices.md:172`；Codex `overview.md:15`（互補不競爭）；ZCode `skill.md:62`〕
7. **instruction 是 advisory**：要硬保證走 enforcement 載體（hook/config）並配工具鏈（pre-commit/linters）——「AGENTS.md 管 guidance、工具鏈管 enforcement」。〔官方：CC `memory.md:23,319`、Codex `overview.md:42`〕（ai-rules hook 三判準同向——既有知識確認）
8. **禁敏感資訊**：instruction 進 prompt 等同可公開文檔；fork checkout 上是攻擊者可控面。〔官方：CC `blog:185`；Muse `permissions.md:107`〕
9. **description 寫觸發不寫說明**：寫清「什麼時候用」、front-load 觸發詞、標明 scope/boundaries；長說明放正文。〔官方：Codex `build-skills.md:98`、ZCode `skill.md:59,66`、CC `skills.md:1034`〕
10. **結果導向**：描述要什麼結果與最終交付物，逐步驟敘述留給 methodology 載體。〔官方：Codex `prompting.md:27`、Muse `workflows.md:68`、CC `skills.md:311`〕
11. **可推導不寫**：code 可推導內容（目錄結構、API 簽名、語言標準慣例）是噪音。〔官方：CC 明文（`memory.md:458`、`best-practices.md:176-184`）；memory 端三家同則（見 2.5）；instruction 端非四家明文共識——條目成立但「共識強度」標 CC 最強〕（IW skill encoder-philosophy——既有知識確認）
12. **元資訊禁止（版本號/統計/更新日期/Changelog）與導航種子（概念→符號）**：〔ai-rules 經驗：IW skill；四家官方鏡像均未明文此級別的元資訊紀律——CC Exclude 表「常變資訊」最接近〕

### 3b 載體分工決策樹（雙源對照）

```
內容要放哪？第一問：需要哪種載入模型（2.1）
│
├─ 需要硬保證（無論 LLM 怎麼判斷都要發生/阻擋）？
│    → hook / config（enforcement）
│      ├─ 純「哪個命令可跑」決策 → Codex 另有 rules（Starlark exec policy）〔官方：CDX rules.md:5〕
│      ├─ client 級設定（權限/模型）→ settings/config 檔〔官方：CC settings precedence；Muse settings.json schema_version:1 硬契約〕
│      └─ 判準：純機械＋單一入口＋無語義例外三者皆是才是 hook；缺一退 LLM 流程
│         〔ai-rules 經驗：IW skill「載體選擇」hook 三判準——「假確定性比真語義危險」〕
│
├─ 每次 session 都需要？
│    → instruction（AGENTS.md 家族，always-on）
│      ├─ 跨專案個人偏好/溝通風格 → user 層〔官方：Codex overview.md:45、ZCode agents.md:69〕
│      ├─ 專案團隊約定/驗證命令/高風險注意 → project 層〔官方：ZCode agents.md:73-77、CC memory.md:50〕
│      └─ 多步驟流程或只關局部 codebase → 不進 instruction，走 skill 或 path-scoped rule〔官方：CC memory.md:50〕
│
├─ 偶爾需要、可封裝的重複工作流？
│    → skill（on-demand；description＝觸發面）
│      ├─ 一句簡單提示詞 → command〔官方：ZCode commands.md:62〕；Codex custom prompts 已 deprecated→skill〔官方：CDX custom-prompts.md:5〕
│      ├─ 需要腳本/模板/範例/完整流程 → skill〔官方：ZCode skill.md:95-99 四大適配訊號；Codex build-skills.md:219-222〕
│      └─ ai-rules reference 分層（rule 核心＋pointer、深層住 skill）是此軸的制度化〔ai-rules 經驗：專案 AGENTS.md〕
│
└─ 跨 session 經驗事實（非規則）？
     → memory（各家寫入模型不同，寫作規範須分家）
       ├─ CC：對話說「remember…」入 auto memory；要進 CLAUDE.md 須明說〔官方：memory.md:425〕
       ├─ Codex：generated state 禁手編；恆常規則放 AGENTS.md〔官方：memories.md:63,92〕
       ├─ Muse：沙箱內 .agents 唯讀；寫入經治理閘〔官方：permissions.md:77；ai-rules 經驗：muse-memory-governance inbox〕
       └─ ZCode：自然語言增刪；主對話專用〔官方：memory.md:37、agents.md:91〕
```

**職責邊界六載體一句話**（官方界定＋ai-rules 治理對照）：

| 載體 | 做什麼 | 不做什麼 | 雙源 |
|---|---|---|---|
| instruction | 每次 session 都需要的 stable 約定/事實 | 多步驟流程、偶爾知識、硬保證 | CC memory.md:50／IW skill 雙檔模式 |
| skill | 按需載入的方法論/工作流（progressive disclosure） | 每次都需要的紀律（那是 instruction） | Codex build-skills.md:33／IW skill reference 分層 |
| memory | 跨 session 經驗事實（recall 層） | 恆常規則的唯一來源 | Codex memories.md:63／memory-audit 統一定義表 |
| hook | 確定性事件執行/阻擋 | 語義判斷（有「看情況」例外） | CC best-practices.md:231／IW skill hook 三判準 |
| config | 載入器級設定（權限/模型/MCP/hooks 註冊） | 行為指導 | CC settings.md:49／rules/AGENTS.md 部署紀律 |
| agent 定義 | 特定角色的 system prompt＋工具面 | 通用紀律（那是 instruction；subagent 也載 AGENTS.md——CC/ZCode 明文） | CC sub-agents.md:265,1033／model-routing 角色 tier |

### 3c 放置層級判準

**四家層級語義差異表**（user-level vs project-level vs dir-level）：

| 層級 | CC | Codex | Muse | ZCode |
|---|---|---|---|---|
| user | `~/.claude/CLAUDE.md`＋`~/.claude/rules/`（先載、優先低） | `~/.codex/AGENTS(.override).md`（首個非空） | user rules 永遠載（machine-wide） | `~/.zcode/AGENTS.md`（串接在前） |
| project root | `./CLAUDE.md` 或 `./.claude/CLAUDE.md`；compact 後重注入 | repo root 起始點（`.git` 判定，可自訂 markers） | workspace root 層（trust 後） | workspace AGENTS.md（唯一專案檔） |
| dir 層（root↔cwd 間） | 上層目錄 launch 載入；子目錄 lazy（讀該目錄檔案時） | walk-down 每目錄至多一檔，全串接（32KiB 停加） | walk-up 至 `.git`，每層 first-wins、深勝淺 | **不掃子目錄——斷** |
| local/personal | `CLAUDE.local.md`（gitignore） | `AGENTS.override.md` 同層最高 | 鏡像未提及 | 鏡像未提及 |
| import/引用 | `@path` 遞迴四層、啟動展開 | 無 @ 展開 | 無 @ 展開（CLAUDE.md 只是同層候選檔名） | **明文不展開 @import/@include** |

**跨 harness 安全寫法**：

- **跨家一致（安全）**：user 層＋project-root 層——四家都有投影，行為差異僅在合併語義（串接 vs 替換）。最穩定的跨家 instruction 架構＝「全域指南一檔＋專案 root AGENTS.md 一檔」（ai-rules 現行架構——既有知識確認，與 contracts.md「AGENTS.md＝跨 harness 最大公約數」同向）。
- **會斷的層級**：
  - **dir 層對 ZCode 完全不可達**（不掃子目錄）；對 Muse 僅向上方向（workspace root 之下的模組層不可達）；對 Codex 僅 cwd 路徑上的目錄可達；對 CC 子目錄是 lazy 載入（時機＝首次讀該目錄檔案）。→ **模組層 instruction 的跨家承諾只能建立在 CC（lazy）＋Codex（cwd 在模組內時）兩家**；對 ZCode/Muse 需要其他投影途徑（如 root 檔導航 pointer——正好與 IW skill「導航只負責概念→符號種子」互補：root 層給種子，模組層給細節）。
  - **`@` transclusion 僅 CC**——AGENTS.md 內禁 `@`（ai-rules 中性化規範既有條款，與 ZCX 官方明文一致——既有知識確認）。
  - **CLAUDE.md 不是跨家檔名**：ZCode 不持續讀（僅 onboarding 一次性遷移）；Muse 同層 AGENTS.md 優先；CC 原生只讀 CLAUDE.md。→ 雙檔模式（AGENTS.md source＋CLAUDE.md `@AGENTS.md` wrapper）是唯一同時滿足四家的寫法（IW skill 既有設計——既有知識確認；CC 官方 `memory.md:129` 背書 import 橋接）。
- **層級內容分配**：跨家共識＝user 層放個人偏好/溝通風格（Codex `overview.md:45`、ZCode `agents.md:69`）、project 層放團隊/程式碼規則、最重要最穩定的規則放最靠近工作的層（Codex 近端放置 `agents-md.md:83`、ZCode workspace 層 `agents.md:78`）。

### 3d per-harness 撰寫要點與陷阱

**尺寸預算表（寫作前查）**：

| 載體 | CC | Codex | Muse | ZCode |
|---|---|---|---|---|
| instruction 檔 | 200 行軟目標；4MiB 整檔跳過 | 鏈合計 32KiB 停加（`project_doc_max_bytes` 可調） | 鏡像未載；實測 64KiB 共享截斷〔ai-rules 經驗〕 | 官方未載；實測 100KiB/檔（user/workspace 各自獨立預算）〔ai-rules 經驗〕 |
| skill description | listing 截 1,536（desc+when_to_use 合併）；listing 預算 1% ctx | 超量先縮 description；清單 2% ctx/8,000 字元 | 鏡像未載 | **>1,024 整技丟棄**；清單摘要 250 字元/條 |
| skill body | <500 行軟目標 | 預算只限初始清單，選中全讀 | 鏡像未載 | >100KB 截斷載入 |
| subagent description | 合計 15,000 tokens 警告 | — | — | name/description 缺失＝整檔忽略＋診斷 |
| memory 索引 | 200 行/25,000 字元（字元非 bytes） | — | ≤48 檔 | 有上限截斷（值未載） |

**截斷行為陷阱**：

- **Codex 鏈尾排除**：32KiB 停止「再加檔」，串接順序 root-down——root 檔過肥最先吃掉預算，**closest-to-cwd（最 specific）的檔最可能被排除**〔合成推論，待審：由 `agents-md.md:15` 停加語義推導，鏡像未細述排除順序〕。對應寫法：root AGENTS.md 精簡、深層 override 才是精華。
- **ZCode 尾部截斷**：讀前 100KiB bytes 再 UTF-8 decode——尾部內容靜默消失且可能切在多位元組字元中間〔ai-rules 經驗：`rules/AGENTS.md:28` 實測＋141KB 事故〕。對應寫法：最重要的 rule 放檔案前段；部署器 size gate 拒絕超限而非依賴截斷。
- **ZCode 整檔丟棄**：description 超限＝整技消失（連名字都不在清單）；未知 frontmatter 欄位（subagent 端）靜默忽略不報錯——**錯欄位名＝無聲失效**（`thoughtLevel` 寫成 `reasoningEffort` 即靜默不生效，`subagents.md:78`）。
- **CC 子目錄延遲**：dir 層 CLAUDE.md 在首次讀該目錄檔案前不在 context——依賴時機的規則（開場就該知道的）不可只放子目錄層。
- **清單預算降級是漸進的**：CC 從最少使用的 skill 開始丟 description；ZCode 降級只留名後「自動觸發率明顯下降」。對應寫法：description 觸發詞前置（前綴最短 250 字元內承載何時用——〔合成推論，待審〕取 ZCode 摘要截斷值為跨家最嚴格約束）。

**skill frontmatter 欄位白名單對比**：

| 欄位 | CC | Codex | Muse | ZCode |
|---|---|---|---|---|
| name | optional（缺省推目錄名） | **required** | 標準推定 | **required**（缺＝整技忽略） |
| description | recommended（唯一 recommended） | **required** | 標準推定 | **required**＋≤1,024 |
| when_to_use | 支援（standard 層） | 鏡像僅述 name+description 必填，未列 when_to_use 支援與否 | 鏡像未載 | 白名單內 |
| allowed-tools | CC extension | 未載 | 未載 | ✗（**command** .md frontmatter 才有——ZCM 採納：兩者非同一 metadata 模型） |
| model/effort 等執行欄位 | CC extension（skill 端 `model`/`effort`/`context`/`hooks`…） | 未載（另走 `agents/openai.yaml`） | 未載 | ✗ |

→ **跨家安全欄位＝name＋description**；when_to_use 三家支持或未否定、Muse 未載〔合成推論，待審：保守可攜核心用 name+description，when_to_use 視為「CC/ZCode 增強」〕。CC 豐富欄位（allowed-tools/model/context:fork）寫了只在 CC 生效、其他家忽略（ZCode 明文忽略非白名單欄位；CCM：standard 之外欄位「Outside Claude Code, you can use only the fields in the Agent Skills spec」）。

**agent 定義格式差異**：CC/ZCode＝md＋YAML frontmatter（body＝system prompt，完全替換預設）；Codex＝**standalone TOML**（`developer_instructions`＋任意 config.toml key）；Muse 鏡像未載格式。→ 跨家 agent 定義**不可攜**（md↔TOML 結構性差異）；ai-rules 的 roles/ 單一源→生成兩 registry 架構正是對此的正解〔ai-rules 經驗：專案 AGENTS.md agents 段〕。

**其他 per-harness 要點**：

- CC：CLAUDE.md 以 user message 送達非 system prompt、無嚴格合規保證（`memory.md:433`）——依賴「IMPORTANT」強調時只標單行（多行＝都不突出，`best-practices.md:188`）；project-root CLAUDE.md 是唯一 `/compact` 後重注入層（`memory.md:462`）——跨 compact 必須存活的規則放 root 層。
- Codex：fallback 檔名**名單**可自訂（`project_doc_fallback_filenames`，`agents-md.md:159`）——`AGENTS.override.md` 檔名本身固定不可自訂（glm 審查修正：extraction 錨點僅支撐 fallback 自訂）；project root 判定可自訂（`.git` 之外可設 markers）；`model_instructions_file` 可整份替換內建 instructions。
- Muse：`muse init` 種子只寫 AGENTS.md（`--force` 整檔覆蓋——先存後 force）；skill 文字含隱藏終端控制字元直接拒絕（寫作面：禁不可見字元）。
- ZCode：跨 harness 匯入有軟鏈（跟隨來源）與複製（解耦）兩式；plugin 內 skill 必須單層目錄（嵌套不識別）；subagent 僅 user 級（團隊共享 agent 定義無官方途徑）；hooks 專案層被忽略——**團隊共享的注入需求走 plugin 分發**（`hooks.md:58`）。

### 3e 官方都沒講的缺口——ai-rules 經驗補

（四家官方文檔的共同盲區；來源標注）

1. **截斷線的實機真相**：ZCode 100KiB 硬編碼、Muse 64KiB 共享、memory 25,000 字元（非 bytes）——全部是 ai-rules 反組譯/實測，官方文檔零記載〔`rules/AGENTS.md:24-31`＋contracts.md 雙端反組譯〕。官方只講軟目標（200 行）與自家 config 可調項（Codex 32KiB）。
2. **「規範存在 ≠ 規範載入」**：部署驗證義務（per-target rg 抽查、`/sync-sources` 機械新鮮度、idempotence 定義）——官方給截斷語義但無「部署後驗證讀到」的方法論〔`rules/AGENTS.md:33-42`〕。
3. **截斷事故的因果實證**：141KB bundle 尾部 8 條 rules 靜默失效→前景 spawn 被 user 插話殺掉——官方「超限降低 adherence」的活體證據與嚴重度標定〔`rules/AGENTS.md:31`〕。
4. **中性化寫作規範**：括號註隔離（`(Claude: ...)`）、跨 harness 載體對照表模式、機械 grep 檢查清單——官方完全沒有「一份檔案給多家讀」的寫作紀律（各家文檔都假設單家消費）〔`rules/AGENTS.md` 中性化規範段〕。
5. **reference 分層（rule 核心＋pointer、深層下沉 skill）**：官方只有 CC 的 skill/CLAUDE.md 二分；「always-on 預算稀缺→rule 只留核心、深層住 on-demand skill」的三層結構是 ai-rules 制度〔專案 AGENTS.md＋IW skill〕。
6. **元資訊禁止、導航 Decoder Test、概念→符號種子/LSP 分工**：官方最接近的是 CC Include/Exclude 表，但無系統化紀律與自檢機制〔IW skill——既有知識確認，非新知〕。
7. **單一寫入點拓撲（memory 跨池治理）**：CC/ZCode 對話寫入、Codex generated state、Muse 沙箱唯讀——官方各講各的；「哪池誰可寫、觀察池唯讀」的跨家拓撲是 ai-rules 部署事實〔專案 AGENTS.md memory 段〕。
8. **negative claim 措辭紀律**：「鏡像未提及≠官方沒有」——研究方法論層，官方文檔本身不會教〔CDM 採納，本次合成全稿適用〕。

## 4. 開放問題（需 user 裁決）

1. **〔與既有衝突，需裁決〕IW skill 宣稱「每層雙檔確保四家 harness 都讀得到該層 instruction」**——本次研究顯示：dir 層對 ZCode 官方明文不可達（不掃子目錄）、對 Muse 僅向上方向可達（workspace root 之下不可達）、對 Codex 僅 cwd 路徑可達、對 CC 是 lazy 載入。該宣稱對 ZCode 不成立（或需限定為「Claude/Codex 讀得到」）。**口徑校準（glm 審查修正）**：IW 宣稱原文的「四家」明文是 Claude/ZCode/OpenCode/Codex（`SKILL.md:24-26`）——不含 Muse；結論不變（ZCode 一家不成立即足以推翻），但修文時須對齊原宣稱口徑，且 OpenCode 的 dir 層行為本次未研究（未提取），修文應標「OpenCode 未驗證」。裁決選項：(a) 修 IW skill 宣稱＋模組層定位改為「CC（lazy）＋Codex（cwd 路徑）深層；ZCode/OpenCode（未驗證）與 Muse（不在宣稱口徑內）靠 root 導航種子」；(b) 維持架構但補 ZCode/Muse 投影途徑（如 deploy 時聚合到 root）。
2. **when_to_use 跨家欄位支援**：Codex 鏡像未列、Muse 鏡像未載——是否實機驗證（寫一個帶 when_to_use 的 skill 在 Codex/Muse 觸發測試），或 guideline 保守取 name+description 為可攜核心？
3. **description 前綴紀律**：跨家最嚴格約束是 ZCode 清單摘要 250 字元/條（CC 1,536、Codex 超量才縮）——是否立「觸發詞在 description 前 250 字元」為 guideline 條目？〔目前標合成推論，待審〕
4. **Codex 鏈尾排除順序**：「closest-to-cwd 檔最可能被 32KiB 預算排除」是由停加語義推導，鏡像未細述實際排除順序——是否需要實測（多層大檔專案驗證）？
5. **Muse description 觸發語義**：observer 提案機制是否讀 description 鏡像未載——與 #2 可合併做一輪實機驗證。
6. **OpenCode 缺席**：本合成覆蓋四家（依輸入材料）；contracts.md 另有 OpenCode 第五家資料。guideline 正式化時是否補 OpenCode 軸？
7. **（glm 審查增補）子代理與 memory 的可見性差異**：矩陣已收錄 ZCode 子代理不讀不寫 memory、CC 主對話 auto memory 不載入 subagents（fork 例外）——但 3b 決策樹 memory 分支未提「委派/子代理 session 對 memory 的可見性」，對 delegate-bridge 使用情境有直接後果（**委派出去的 session 讀不到主對話 memory——工單必須自含**，與 ai-rules 既有 self-contained-prompt 紀律同向：既有知識確認＋新的機制級理由）。是否立為 guideline 明文條目？
