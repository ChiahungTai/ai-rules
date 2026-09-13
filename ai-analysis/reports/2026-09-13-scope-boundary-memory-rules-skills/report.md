# Scope 分界定稿：memory / rules-bundle / skills——研究報告（2026-09-13）

> 任務源起：user deep-work 派工——「最重要的是要分清楚 scope，哪些放 memory、哪些是 rules（user level AGENTS.md，因為會透過 bundle）…哪些要放 skills，我的直接是用觸發的，然後現在模型能力越來越強 rules 不應該放太多 common 工程共識，應該是放一些特殊規範」＋mid-flight steering「CC 的 rules 機制可能是解掉 bundle agents.md 一直很難減少的關鍵」。分工：flash 腿取證、codex 共析與評斷、GLM-5.3 主 session 整合與終審 judge。
>
> 管線：四 spec-miner/lite-verify 腿（CC 逆向／四家對照／rules 19 檔標註／memory 池盤點）→ codex webgpt-high 共析 r1（六挑戰三測試）→ probe 腿（user-level `paths:` L4 實證）→ codex r2 followup（§四四修＋回填條文草稿）→ 主 session judge（五項機械複核全過）。材料十檔在本目錄 `materials/`。

## 一、結論一覽

1. **rule 資格公式（定稿建議）**：層級相容 ∩「首個有後果的決策前必須在場」∩（經驗證的模型校準需求 ∪ user 特殊裁定 ∪ trigger-bootstrap 必要資訊）。「模型已知／通用共識」只產生 **delete candidate**（user 北極星正式化——不升格硬反條件，防模型代際誤殺）。
2. **residency 三測試**：Bootstrap／First-consequential-action／Portfolio-duplication（定義見 §三）。
3. **條件載入層（steering 落地）**：CC 原生 `paths:`（Read 匹配檔 lazy 注入）**probe 實證成立**；跨 harness 投影採**三軸分離**——`harness-scope:`＝誰消費、`paths:`＝CC 何時載、新顯式 marker（如 `bundle-mode: pointer`）＝非 CC 怎麼投影；**`paths:` 不單獨作非 CC 排除訊號**（單欄位單語義）。
4. **corpus 實況**：rules 19 檔中 A 共識密度僅 ~10%（排序 heuristic 非 metric）——slimming 主戰場＝design-thinking／edit-discipline／python-standards 三檔＋B 拓撲檔「核心留、細節沉」第二批；memory 池（239 條）與 rules 是條文↔事故證據縱深互補，形態健康。
5. **回填歸屬**：判準回填併 AIR-70（連 09-10 未落的層級閘首句一起，單一源 memory-audit 載體統一定義表；diff 見 §六）；corpus 實際搬遷＋條件載入層 vertical slice 另開弧（判準修訂與搬遷不混驗收）。

## 二、機制事實基礎（五腿精華）

### 2.1 四家 bundle/skills/memory 消費（腿 2；細節 materials/leg2）

- **instruction bundle＝always-on 全量**是跨 harness portable baseline：CC launch concatenate（4MiB 整檔 skip 為唯一硬限）、Codex run-start 建鏈（instruction budget 有界；32KiB 語義兩處官方描述未調和，unverified）、Muse wins 替換、ZCode 兩檔全載（100KiB 讀前截斷實測）——rule 每字都吃開場 token。
- **skills 真 on-demand**：CC/Codex/Muse 三家 listing（name+desc）常駐、body 選中才載；**ZCode 半例外**——元數據每輪注入共享固定預算，超載降級只留名、自動觸發率下降（治理對象＝enabled surface，非 skill 總數）。
- **path-scoped rule 中間層只有 CC 原生**；memory 四家都有原生機制但寫入拓撲各異（CC/ZCode 開放寫入、Codex generated 禁手編、Muse 沙箱唯讀＋官方缺口）；CC/ZCode subagent 都讀不到主對話 memory（委派工單必須自含）。

### 2.2 Claude Code 2.1.263 逆向＋實證（腿 1＋腿 5）

- `~/.claude/rules/` 是**官方** user-level rules 機制（recursive `.md`、symlink 官方支援、user-scope import 免批准）；CC **不原生讀 AGENTS.md**（`@AGENTS.md` wrapper＝官方建議模式）。
- **user-level `paths:` 條件載入＝成立（L4 probe）**：實驗組 Read 匹配檔→`load_reason:"path_glob_match"` attachment 注入（Read 回傳後、下一 model turn 前）；對照組零事件。binary `conditionalRule:!1`＝eager 掃描旗標非能力缺席。
- 邊界三條：①**Cowork desktop 跳過指向 working dir 外的 symlink**（本機兩條部署 symlink 都中——Cowork 場景整組失效，終端/IDE 不受影響）；②probe 只證 **Read** 觸發——新建檔首個動作是 Write 時 rule 不會載（python-standards 既有 `paths:` 在 CC 已有此 latent 洞）；③CC 無 bundle 截斷線（超裁＝adherence 無聲退化）。
- 附帶：CC live 認證在 `~/.claude/settings.json` 的 `.env`（非 Keychain——Keychain 條目已過期殘留）；`rules/AGENTS.md`（治理檔）被 CC 不限檔名掃描當行為規範載——**受眾錯置**。

### 2.3 corpus 與池現況（腿 3＋腿 4）

- rules/ 19 檔（勘誤：非 20）：主要形態 **C 校準 12 檔、B 特殊 6 檔、A 1 檔**；A 密度 top：design-thinking ~60%、edit-discipline ~35%、python-standards ~25%。三檔已帶 `paths:`（instruction-writing `**/*.md`、llm-output-convention 與 python-standards `**/*.py`）。
- 池 239 條（feedback 136/reference 67/project 36）：與 rules 19 檔的主題重疊全呈「條文↔事故證據＋user 原話」縱深互補（條目常自陳「條文已落 rules/xxx」）；must-execute 重疊最薄、llm-output-convention 無同題條目。
- 尺寸：bundle 現值 32,835B；最緊 target 為 Muse（09-10 時距 gate 僅 91B，現 ~4KB headroom）。

## 三、分界原則 v2（定稿建議）

### 3.1 決策流

**Scope gate（層級硬閘，09-10 定版：「repo 名替換掉後規則仍成立」＝user-level；user-level 知識不得以 project-only 載體為權威源）→ residency 三測試 → 載體。**

### 3.2 rule 資格公式＋三測試

> **rule 資格 ＝ 層級相容 ∩「首個有後果的決策前必須在場」∩（經驗證的模型校準需求 ∪ user 特殊裁定 ∪ trigger-bootstrap 必要資訊）**

- **Bootstrap test**：body 下沉 skill 後，模型不知道其內容仍能可靠知道何時載對應 skill？不能→最小 bootstrap 留 rule。
- **First consequential action test**：等 on-demand 載入時首個不可忽略行為（commit／選錯 model／rg 誤判零消費者）是否已可能發生？是→核心提前常駐。
- **Portfolio duplication test**：同一約束已由 harness system prompt／hook／repo AGENTS／可靠 skill trigger 承載？是→user-level rule 是重複 token 稅，退出。

### 3.3 形態→處置映射（A/B/C/D＋第五類）

| 形態 | 處置 |
|---|---|
| A 共識 | **delete candidate**——逐條文判不逐檔判（A 殼 C 核拆分）；刪除者與初判者分離（writer 標 candidate、獨立 reviewer 查現役 model families 反覆失敗證據）；有 observed violation／user override／pre-trigger necessity 重分類 C/B。**純教學 A 直接刪**（降 skill 仍付 catalog 稅＋trigger 競爭） |
| C 校準 | 三路：留 rule（跨任務且先於 routing 生效：skill 觸發/授權邊界/驗收宣稱面）／降 skill（有清楚 task trigger 且首個有害行為前可載）／移 hook（純機械＋單入口＋無語義例外）。**衰減治理＝事件觸發 re-audit**（主力 family 換代／harness 改版／bundle 逼近 gate／事故長期消失＋無 rule probe 穩定／條文被修改時）——非日曆 sunset |
| B 特殊 | **bootstrap core 留 rule＋lookup body 下沉 skill**（判準：模型不知道這行還知道何時載 skill 嗎）；經驗事實（事故/偏好/user 原話）依三物進 memory |
| D 機械 | 機械性≠residency（軸分離）——D 只說明易成 hook/config/recipe；是否常駐另判 |
| 治理文件（受眾≠模型） | **不進 bundle**（harness-scope 排除部署；rules/AGENTS.md 首例） |

### 3.4 條件載入層（三軸分離設計）

| 欄位 | 唯一語義 |
|---|---|
| `harness-scope:` | **誰**消費（neutral/claude-specific/meta） |
| `paths:` | **CC 何時**載 native rule body（Read path match——probe 實證） |
| 新顯式 marker（如 `bundle-mode: pointer`，名稱實施時裁） | **非 CC 如何 materialize**（full body／bootstrap pointer）——explicit opt-in，處理序：harness-scope → target eligibility → projection mode；`claude-specific+paths` 與 `meta` 不生成 pointer |

- **bootstrap pointer＝作者寫語義＋deploy 只投影**：pointer trigger 句由作者明寫在 source（同一真相源），deploy 機械驗（target skill 存在、該 harness 可達/enabled）＋原樣 materialize＋body 排除；**fail closed**（找不到 skill/pointer/target 即 deploy 失敗，禁靜默抽 body——防「bundle 變小但規範消失」false green）。
- **新 `paths:` ＝ CC 行為變更**：只有既有 `paths:` 檔「CC 行為不變」成立；新增 path-scoping 須以 Read-trigger 時點重跑 bootstrap／first-consequential-action 測試。
- **候選裁定**（r2）：`instruction-writing`＝golden pilot（有 paths＋配對 skill＋guide 已有 bootstrap 句）；`llm-output-convention` 第二；`python-standards` 現況**不過 gate**（無配對 skill＋Write-without-Read 洞）——先補 retrieval carrier；`design-thinking(**/*.md)` **駁回**（applicability 是決策型非檔案型，違 trigger congruence——維持 minimal always-on core＋deep-thinking skill）。

### 3.5 guide 同標準

guide（ai-development-guide.md）就是 user-level instruction surface——判準本次明確涵蓋；19 rules 與 guide 的逐條量測分兩個 implementation batch。

## 四、rules 19 檔逐檔裁定建議

- **slim 三檔**（A 主戰場）：design-thinking（刪純共識論述、留 C「至少兩層連鎖後果」＋模板 pointer）、edit-discipline（SOLID 展開壓一行、留 C 核）、python-standards（禁舊 typing 壓一行、留 C 反主流裁定＋re-export 禁令＋案例）。
- **B 拓撲兩檔拆分**（第二批）：model-routing（留兩跳規則/native-ID 詞彙/tier 骨架；委派/resume/rate-limit 細節收 skill）、symbol-query-routing（留啟動 gate＋「禁 0-hit 斷言零消費者」；SCIP/pyrefly/LSP 細節收 skill）。
- **C 大宗 12 檔＋其餘**：留（rule 核心收件人）；modern-cli-preference 列**首次校準 re-audit 清單**（rg/fd 模型多已自覺——C 代際衰減活例）。
- **rules/AGENTS.md**：排除出 bundle（治理文件第五類首例）。
- 詳表：materials/draft-v0-dispositions.md（已套 bootstrap test v1）。

## 五、實施歸屬

1. **AIR-70 段二擴充**：判準回填（§六 diff）＋層級閘首句＋desc 觸發面修訂——單一源 memory-audit 載體統一定義表。
2. **corpus 弧（新）**：19 檔＋guide 依新判準逐條搬遷（slim 三檔＋B 拆分兩檔＋rules/AGENTS.md 排除＋guide 批次二）。
3. **條件載入層 vertical slice（新，小卡規模）**：instruction-writing pilot——`bundle-mode` marker 定名＋deploy 消費＋fail-closed 驗證＋bundle 前後量測。
4. **現況立即可做的觀察項**：python-standards 既有 `paths:` 在 CC 的 Write-without-Read 洞（新建 .py 首 Write 不觸發）——corpus 弧一併處置（補 skill 或縮 paths 適用面）。

## 六、AIR-70 回填條文（diff-able 定版建議——codex r2 草擬、judge 採納）

**A. 載體統一定義表開頭段（替換現行 L138）**：插入層級閘首句（09-10 定版原文）為首段；次段保留三處合一說明（「北極星分層」字樣簡化為分層列舉、「常駐-按需」改「residency」）；新增三段——rule 資格公式（§3.2）、「模型已知／共識只產生 delete candidate」句、residency 三測試（①Bootstrap ②First consequential action ③Portfolio duplication）、條件載入層段（`paths:`＝CC runtime 條件不單獨作非 CC 排除訊號；projection 須顯式 opt-in，細則見 instruction-writing skill；新增 path-scoping 重跑兩測試）。

**B. 表格 rule/skill 兩列（替換現行 L142-143）**：
- rule 列職責改「通過 rule 資格公式、須在首個有後果決策前生效的**最小核心／bootstrap**」；稀缺層改「portable baseline＝開場常駐最貴；可安全延後的 body 下沉 skill；CC 可另用 `paths:` 原生條件載入」；寫入預設補「三測試；common/known 只作 delete candidate 不逐檔自動刪」。
- skill 列寫入預設改「**desc＝implicit routing 面；亦可由 rule/bootstrap pointer explicit 觸發**」（修「唯一觸發面」過窄）。

**C. 一行流（替換現行 L154）**：「先套層級硬閘→…→user-level 方法論套 residency 三測試：首個有後果決策前必須在場且屬 verified calibration／user 裁定／trigger-bootstrap→最小 rule；有可靠 trigger 且首個有害行為前可載→skill；CC 檔案讀取型條件內容依條件載入層處置→…」。

（逐字 diff 全文見 materials/codex-followup-out.txt §C；hook 判準列 L155 不動——D 與 residency 已解耦，現行三判準仍是合理 hook gate。）

## 七、失敗與限制記錄

- codex followup 首派撞 webgpt **browser turns 併發上限**（本弧第四個新簽名，已落 DRAFT-6）；90 秒釋放窗後重試成功。
- 腿 3 百分比＝排序 heuristic（人工形態估計，非 clause-weighted metric）；codex 32KiB 語義 unverified；probe 絕對/相對路徑匹配未設對照（不過度宣稱）。
- 腿 1 unverified 殘項：user-level rules 引入版本、SKILL.md 大小 skip byte 值（binary 常數混淆）。
- 腿 4 盤點期間池新流入 1 條（本 session auto-memory 提煉，索引落後 1 筆待 generator）。

## 八、judge 簽收

五項機械複核全過（三檔 `paths:` 清單、python-standards frontmatter、deploy_agents.py 三函數在場、guide bootstrap 句 L5、memory-audit L143 條文）。codex r1 六挑戰、r2 四修正全採納，無否決項；兩處 codex 表述已降格處理（32KiB→unverified、腿 3 百分比→heuristic）。v2＝定稿建議，等 user 確認方向後由 AIR-70 弧實施回填。
