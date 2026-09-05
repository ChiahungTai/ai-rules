# illustrate HTML 模式 — archify 展示級渲染（opt-in）

> /illustrate 的第三輸出模式。Console（即時）與 MD（Mermaid 沉澱，**source of record**）角色不變——HTML 是**按需渲染的展示層**，服務「一次性人類 viewport」：分享 / demo / re-onboard / drift 審查。三模式是受眾分流非取代。

## 觸發條件

- **明示**：`/illustrate html <主題或 @dir/@file>`（mode D 主題 → archify；mode B @dir → artifact 概念→載體映射；mode A/C 明示 html → city map 走 architecture 映射）；`@ep`／實作報告／`@module`／`@dir` + html 明示報告導讀 → **Report Shell**（見「html 報告殼」段）
- **增益建議**（不自動切換）：mode D 分享情境——互動搜尋 / focus / reach 追蹤 / Present 導覽對位人類 viewport 消費方式時，建議 html 並由 user 決定
- **drift compare**（opt-in）：post-build drift 審查明示要比對圖時（見下「drift compare」段）
- **永不**：Console 語境不 inline 渲染（明示 html = 切換輸出模式，檔案交付＋路徑回報）

## archify 存在性偵測與降級

偵測順序（skills 根 `~/.zcode/skills`、`~/.agents/skills`、`~/.claude/skills` 三者 symlink 同源，任一根命中即可）：

1. `<skills 根>/archify/bin/archify.mjs`（已安裝）
2. `~/Github/archify/archify/bin/archify.mjs`（repo clone）
3. 全 miss → **缺場降級**：輸出 MD Mermaid 版＋告知安裝方式，不靜默失敗

- **在場但壞**：首次偵測到後跑 `node <archify>/bin/archify.mjs doctor` 一次——doctor 失敗（node 缺 / 版本 <18 / 上游 breaking）→ 同缺場降級＋回報 doctor 診斷
- **安裝建議 clone 優先**（`git clone https://github.com/tt-a1i/archify ~/Github/archify`）；`npx skills add -g` 在本部署架構（skills 根 symlink 到 ai-rules repo）會穿 symlink 寫進 ai-rules 版本控管目錄——除非使用者明知，不建議

## 概念→載體映射（illustrate 概念軸；圖型軸判準在 diagram-selection）

mode B artifact 與 mode A/C city map 共用此映射（概念軸單一源；「sequence/stateDiagram 這類圖型用哪個載體」的判準與量化邊界見 [diagram-selection](../diagram-selection/SKILL.md)——兩軸互補不重疊）：

| illustrate 概念 | 首選載體 | 備註 |
|----------------|---------|------|
| boundary / city map | archify `architecture` 或 **HTML 塊**（層次型） | 自由排版型，authoring 成本高——層次/對照內容優先 HTML 塊 |
| data-flow | archify `dataflow` 或 mermaid `flowchart LR`（管線型） | stage/row 語意排版 vs 線性管線按複雜度選 |
| sequence | mermaid `sequenceDiagram`（殼內）或 archify `sequence` | 有通道——mermaid 一輪可成，成本最低 |
| call graph | archify `workflow`／`sequence` 或 mermaid（小圖） | **優先語意排版型** |
| class slice | **無對應** | 維持 md／表格（diagram-selection 兩層判準），不硬映射 |
| **報告殼（`@任務家/<task>/ep.md`／實作報告／@module／@dir + html）** | 按報告類型選型（見下節變體表） | Report Shell——人類 viewport 通用模式 |

> **archify 是最後手段**（user 裁示「非必要不用」——判準源見 [diagram-selection](../diagram-selection/SKILL.md)）：只有命中 archify 獨有價值（互動導航／大規模依賴網／無通道大圖的防交錯結構容器＋validate gate）才走 archify-gen 產線；規律型/小圖走 mermaid 或 HTML 塊——硬用 archify＝浪費 validate 迴圈。

## html 報告殼（Report Shell——人類 viewport 的通用模式）

> 本質：任何「AI 消費為主、人類需要快速理解」的產物（EP 計畫／實作完成報告／codebase 架構／module 現況／目錄導覽）共用同一模式——**本體層**（markdown source of record）＋**報告殼層**（順序敘事 viewport）——同源雙消費。起源實證：EP「我現在很少看了，太難理解，都給 AI 用的」。

**三層結構（順序性是核心——user 實證：「兩張圖並列搞得好亂、不知道從哪看起、S1 S2 S3 那排不能點」）**：

```
報告殼（自製薄殼 index.html——非 archify）
  左 sidebar＝章節順序，點章節切主區
  主區＝該章節文字精華＋該章節該看的圖（iframe 嵌入）
      ↓ iframe
視圖素材層（archify 圖引擎——每張圖=一個視圖，檔名 diagram-<type>.html）
```

- **archify 是單視圖圖表引擎**（pan/zoom/search 是空間探索；`meta.views` guided story 也只在同圖內）——順序性敘事導覽它沒有也不該有；**殼結構/視覺/互動單一源＝template [`skills/_common/illustrate-report-shell.html`](./illustrate-report-shell.html)，建殼＝複製＋填 slot**（slot：title/badge/meta/nav/section-content/diagram/backlinks/source；首屏 active、sidebar 折疊、hash restore 自帶；預設深色，沿 golden-pretriage 裁決），入口命名 `index.html`、圖命名 `diagram-<type>.html`
- **消費單位是章節不是圖**——多圖並列無導覽＝亂（實證）；每章節只放該章該看的圖
- **首屏 active 與嵌入參數由 template 擁有**（首個含圖章節規則＋`?embed=1`＋AIR-14 實證見 template 檔頭註解三條硬約束）——建殼不重推導、不手改首屏指向
- **殼不整殼降級**：archify 缺場/壞場時用同 template degraded slot（章節敘事完整，diagram 區塊顯示待裝提示）——「降級 MD」規則適用單圖任務，不把殼一起降掉
- **殼嵌圖四形態**（同殼可混用，按圖選載體——判準見 [diagram-selection](../diagram-selection/SKILL.md)）：inline SVG（預設產物 **≤1/頁**——mmdc id 碰撞；**帶唯一 `-I <svgId>` 可多張**，見 [mermaid](../mermaid/SKILL.md) 陷阱 5）／iframe＋`diagram-*.svg` 檔（其餘 mermaid）／iframe＋`?embed=1`（archify）／HTML 塊直寫殼內（層次/對照，零渲染管線）；外框統一 frame-wrap（標題列＋↗ 全屏連結）。**無縫一體準則**：同主題（殼 dark → 圖 dark chrome）、透明底、同字體、尺寸自適應、無 iframe 痕跡（border/scrollbar/白底不出現）——mermaid 配方（mmdc `-t dark -b transparent`／CDN lazy render）見 [mermaid](../mermaid/SKILL.md) 殼內嵌段
- **md 死鏈禁例**：殼連結 `.md` 的 mermaid code block 在 file:// 不渲染＝死內容——未渲染 .md 圖集不進殼，**圖要真的出現在頁面上**（渲染產物嵌殼），不是「原始碼在另一檔」

**內容篩選通則（user 勘正：「缺漏要看是不是人類真的需要知道」）**：殼裝**判斷材料**（意圖/為什麼動機鏈、風險與降級、取捨決策、驗收判準、當前狀態、實物樣本、回源路徑），**不裝執行細節**（治理規則、AI 流程產物如 UC 盤點表、機械完整性逐項覆蓋）——後者留本體層，殼至多一句指路。**實物樣本要進殼**（如 aria baseline 真實 YAML 開頭——人類沒看過實物，機制敘述等於空談）。

**殼生成分工（三 tier——AIR-28；registry 對號查 agents/AGENTS.md execution contract 表）**：

1. **archify-gen（lite 產線）**：JSON IR 撰寫＋archify validate showcase 迴圈＋diagram 渲染——機械產線，**事實由呼叫端給定**（agent 不自產宣稱）。**只接 archify 圖**——mermaid（mmdc 機械 CLI）與 HTML 塊由主 session/lite 直接產，不經 archify-gen
2. **篩選敘事（full 主 session）**：殼的章節篩選與敘事＝判斷密集（「缺漏是不是人類真的需要知道」是判斷題）——不派 lite
3. **vision-review（vision 驗收）**：渲染 PNG 逐張 verdict（圖互 clip／CJK 誤讀／美感底線）——驗收收法見該 agent 定義；契約（三段式/分批上限/全樣本錨定）見 [diagram-selection](../diagram-selection/SKILL.md) 共性段

**caller 端事實清單義務（archify 委派前）**：清單自帶**幾何分類**（主線/分支/消費＋標註哪些邊跨圖、哪些垂直相鄰——agent 才能守「single main path + side branches from nearest node」）；起手規格一句（3 lanes 起手×零堆疊×5-6 節點/lane、短 sublabel（code identifiers 保留、去 CJK 裝飾詞）、fromCol/toCol 按 phase 帶切乾淨禁重疊）——**事前預防 spec 過重**，非只靠 >4 輪止損；archify-gen 無權刪 caller 給的事實，長文案由 caller 自己收進 cards。

**機械底稿（數據宣稱唯一來源）**：殼中一切**數據宣稱**（數字、狀態、覆蓋率、時間）只從機械底稿帶入、禁止敘事層自填——底稿＝**delta_tour 輸出／archify JSON IR／validate rounds ledger／命令輸出原文**（防 lite 產線的文檔宣稱漂移弱面——flash 分工律，model-routing skill）。

**確定性再生 diff**：同一底稿重跑 archify-gen → JSON IR diff 應為空——再生等價被 diff 釘住（測試保護的等價物）；diff 非空＝底稿或產線漂移，先查因再交付。

**報告類型的敘事骨架變體**（殼固定、骨架變）：

| 報告類型 | 敘事骨架 | archify 視圖選型 |
|---------|---------|------------------|
| EP 計畫導讀（任務家 `<task>/ep.md`） | 為什麼（動機鏈）→資產與命運→推進與驗收→各段細節→風險降級→決策記錄 | workflow（主：gate/exception）＋architecture（輔） |
| 實作完成報告（implement 完成報告/debrief） | 意圖→做了什麼→**驗證證據**（命令+exit code）→認知誤差點/待確認 | workflow（流程變更時）＋architecture 前後對照（drift compare） |
| codebase 架構報告 | 分層地圖→資料流→熱點與風險區 | architecture＋dataflow |
| module 現況（`@module`／AGENTS.md 域） | 職責→Capabilities 精華→依賴與邊界 | architecture（局部視圖） |
| 目錄導覽（`@dir`） | 這裡有什麼→入口→慣例 | architecture（目錄級） |

**產物位置分流（user 裁決「開心目錄」——一弧一殼、隨生命週期生長）**：

- **流程性 brief（EP 計畫導讀＋實作完成結果）→ 任務家（task home）下 `MM-DD-<task-name>/`**（目錄名**無年份、無 ep-/impl- 前綴**——活躍弧停留短；完結弧 task 目錄**整目錄**搬同家歸檔層——repo 慣例探測 `done/` 扁平或 `_done/<YYYY>/` 年分層，皆無建 `done/`；年份僅由年分層形態承接；歸檔目錄判定單一源見 [metadata-sync](../metadata-sync/SKILL.md) EP 歸檔項）。**任務家探測（2026-09-02 三池重構定案，各 skill 放置規則共用本源）**：`<repo>/ai-analysis/_tasks/` 在場 → 雜項任務家＝它（**線任務另居 `ai-analysis/_projects/<線>/tasks/`**——session 從線 context 來時；完成→同線 `done/`）；否則 repo-root `00-tasks/`（`00-` 前綴 VSCode/`ls` 排最前）。spec（`spec.md`）與 EP 本體（`ep.md`）同 task 目錄——一弧全生命檔案同處。殼目錄內 JSON IR 沿用 `<主題>.<type>.json` 命名（與 arch-report 同慣例）。與 debrief（文字簡報）/delta tour（行級走讀）三層互補：殼=high-level 圖形、debrief=模組/檔案文字、tour=行級；殼實作章節吸收日常判斷材料（做了什麼/證據/誤差點），debrief 為深度選配（模組/檔案級深挖）
- **按需性視覺產物（codebase 架構/module 現況/目錄導覽 illustrate）→ `arch-report/<主題>/`**（現狀不變）
- git 慣例**同一原則、條目隨任務家**：投影源頭進 git（任務家＝自製殼 `index.html`＋JSON IR＋`ep.md`/`spec.md`；arch-report＝JSON IR＋visual-check receipt）、archify 渲染產物不進（`diagram-*.html` 與 arch-report 的 `index.html` 是渲染產物；gitignore 條目隨任務家路徑——如 `ai-analysis/{_tasks,_projects}/**/diagram-*.html` 或 `00-tasks/**/diagram-*.html`）。⚠ **任務家殼 `index.html` 是手寫殼、非 JSON 可再生**——gitignore 條目只排除 `**/diagram-*.html`；排過寬（`**/*.html`）會連殼一起 ignore（規格↔實作分歧實證：殼蒸發死鏈）

**殼生命週期掛點（自動產生雙掛點＋fallback）**——修「掛弧後（commit 後）的產物在 session context 耗盡時必死」：掛點全落在 commit **前**的穩定點。**backlog 卡同步與主動顯示隨掛點聯動**（命令合約＝[kanban-board](../kanban-board/SKILL.md)；「顯示」走 report server URL——與卡上連結同一條，server 未開 fallback `open <絕對路徑>`）。

| 掛點 | 時機 | 殼 | backlog 卡同步 | 主動顯示 |
|------|------|-----|---------------|---------|
| **hook 1** | EP 定稿（[execution-plan](../execution-plan/SKILL.md) 定稿交付） | **建殼骨架**＋計畫章節，badge 📋——骨架＝零渲染管線內容（HTML 塊/表格可），**mermaid/archify 圖不於 hook 1 產**，diagram 槽留 degraded 待裝＋殼頭標「圖待 hook 2 裝」（砍掉 hook 1 計畫圖在 hook 2 實作大改後的重投影成本）；殼頭部聲明 EP 路徑＋task integration baseline＋projection source（未 commit 用本體 content SHA；post-build/code-review 弧模式跨 session 可從殼讀） | `task edit <id> --ref "<殼URL>,<相對路徑>"`（**開工雙 ref 合約**——殼未建前的過渡 URL 指 md preview，建殼後更新） | **`open <殼URL>`**——殼建好即彈出（提前預覽骨架） |
| **badge 推進** | [implement](../implement/SKILL.md) 階段 5a 結算 | 情境 A（全項結算）→ ✅；情境 B（中間段）→ 🟡 | 卡不動（仍 In Progress） | 不主動開——board portal 隨時點同一 URL |
| **hook 2** | **post-build 完成**（commit 前最後穩定點；程序載體＝[post-build](../post-build/SKILL.md) 階段 5） | 同一殼長**實作章節**：做了什麼／驗證證據／delta 前後對照／認知誤差點＋回源連結——反映修正迴圈後**最終態**；**並產圖一次**——依 [diagram-selection](../diagram-selection/SKILL.md) 選型補 degraded 槽（hook 1 未產的渲染管線圖在此一次產）；badge ✅；並產**持久版 delta tour**（落 `.tours/delta/` 進 git） | **結案兩步＋弧結案蒸餾第三動**：`-s Done --final-summary` → `--ref` 換 `done/` 新 URL（任務目錄遷 done/ 後；卡留 Done 欄）；本弧 memory 條目蒸餾終態 facts | **`open <殼URL>`**——終態殼彈出 |
| **fallback** | 無 post-build 弧（user 直接 `/commit`、弧終止）→ implement 階段 6 | hook 2 同款產出由 implement 階段 6 承接 | 同 hook 2 | 同 hook 2 |

**共通必備**：狀態 badge（📋 計畫／🟡 進行中／✅ 完成——與全域 UC 狀態標記同符號語義）；計畫 vs 既有顯式區分（計畫物 tag「S<N> 計畫中」——並列無區分＝誤導）；回源連結（本體檔案路徑＋baseline commit）；**board 反向連結**（repo 有 backlog board 時，殼頭部 nav 加 `http://127.0.0.1:6420`——best-effort）；**EP（.md）http 連結形態**（:6421 掛載帶 route 前綴——ai-rules=`/ai-rules/`、URL **不含** `ai-analysis/` 段；.md 連結一律 viewer 形態 `/viewer/_md-viewer.html?p=/<route>/<repo 相對路徑>`，raw 直連會被週日卡 ref lint 旗標）——精確合約見 kanban-board 雙 ref 行；狀態隨本體結算更新、本體歸檔殼隨之（殼服務本體生命期）

**雙向一致性（html ↔ md——user 勘正：「同一個 md 每個人理解都不一樣，AI 跟人有理解差異正常，但是大方向不要錯」）**：

- **分級而非逐字**——零差異不可能也不追求；分兩級：
  - **大方向（硬，不可錯）**：目的與動機、範圍邊界（做什麼/不做什麼）、段落劃分與順序、驗收判準的語義（gate 過關條件）、風險的有無與等級、關鍵數字的數量級——判準句：「**拿殼給人看形成的大方向預期，vs 拿本體給 AI 實作產出的結果——兩者對得上嗎**」；對不上＝投影失真（這才是 bug）
  - **細節（軟，容忍理解差異）**：語氣/詳略/例子選擇/口語化改寫——不逐字逐句核對
- **殼是投影非平行創作**——殼想說本體沒有的東西 → **先改本體再投影**（發現順序顛倒是警訊：本體缺該內容）；禁止殼內出現本體沒有的**大方向級主張**（新決策/新範圍/新風險等級）
- **投影鎖定與 stale 標記**：殼頭部將 task integration baseline 與 projection source **分欄聲明**；projection source 已 commit 時用包含本體的 revision，未 commit 時用本體 content SHA（不可拿早於本體的 integration baseline 冒充）。本體修訂（review 修訂/段落結算/狀態變化）→ 殼**同步重投影**並只更新 projection source（大方向級變更必同步；純文字潤飾可不動）。同步義務與「測試斷言變更→驗收規格同步」「code 變更→Capabilities 同步」同一模式（single source of truth 的投影紀律）
- **提煉篩選≠語義漂移**：篩選通則（判斷材料 vs 執行細節）授權「刪」不授權「改」——刪掉的內容一個指路連結回本體即可
- **archify authoring invariants 以其 SKILL.md 為準全文適用**（visual_preset/subtitle 預設省略、labelAt/via 診斷驅動單控制修復——實證：違反前兩條者多花修復輪次）

## Authoring 紀律（委派，不重述）

渲染端全紀律以 archify 自帶 SKILL.md 為準——**檔案位置隨偵測結果**（skills 安裝：`<skills 根>/archify/SKILL.md`；clone：`~/Github/archify/archify/SKILL.md`，schemas/ 與 examples/ 同目錄）。bounded path 摘要：type router → 讀 schema+example → author JSON → `validate --quality showcase` → repair → `deliver` → `visual-check`；label 保留、repair 順序。illustrate 側補充：

- **grounding 事實先產**：讀 code（arch-thinking §二機械）→ 結構事實 → JSON IR 從事實作者化（非直接跳 archify）
- **證據附著**：節點帶 `sources`（repo 相對路徑 + line）；私有 repo 帶 `meta.repository`（GitHub origin + 當下 revision SHA），render 時以 `--repo-root` 本地 git 驗證
- **與 archify standalone 的分工**（觸發詞重疊的裁決）：illustrate 是「讀 code → grounding 結構事實 → 受眾/生命週期管理」的入口，archify skill 在場時 illustrate 仍走自己的委派流程；archify standalone 適合 raw 渲染請求（既有 JSON 渲染、Mermaid beautify、無 grounding 需求的 plain-language 圖）——不競爭，分流

## 輪數 guard（止損分層——本段為閾值與 ledger 規格單一源，archify-gen role 以 pointer 引用）

口徑＝**validate 呼叫輪數**（每次 candidate 修改後的 validate 記 1 輪，含 containment 修復）：

- **>4 輪不收斂＝caller spec 過重**——停手回報 caller 改 spec 重跑（減 lanes/去堆疊/砍 sublabel/次要事實沉 cards），不是 agent 不努力（實證：spec 瘦身後首輪收斂全綠 vs 過重 spec 十數輪空轉）
- **單圖止損 12 輪** / **session 總預算 18 輪**（多圖請求合併計）——超限 → **降級輸出 MD Mermaid 版**＋回報殘留診斷（subject/evidence）——不接受半成品 HTML 交付（正當出口不是失敗）
- 「兩連續輪無改善即停」引用 archify 自帶止損
- **validate rounds ledger**：archify-gen 每輪 validate 把摘要（輪次/checks/errors/warnings/變更處）append `<主題>.rounds.md`——與 candidate 同目錄、隨 JSON IR 進 git、屬機械底稿源。成本觀測面：沒有 ledger，逐輪數字只能靠 db session 鑑識事後撈（git 只有終態 receipt）

## 產物生命週期

- **輸出位置**：`arch-report/<主題>/`（**repo root 層級**——結構理解視覺產物是人類瀏覽優先的渲染產物，與任務家（`ai-analysis/` 下的活躍工作面——收**流程**產物 ep/spec/殼）角色不同，故維持 root 不進 `ai-analysis/`；html 報告殼的分流放置見上「產物位置分流」）——**每次 html 任務（主題）一個子目錄**，入口 HTML 命名 **`index.html`**（靜態伺服器慣例——`python -m http.server`/GitHub Pages 開目錄即入圖）；JSON IR 用自描述名 `<主題>.<type>.json` 並存（每圖約 8 檔）；`--output <path>` 自訂路徑尊崇（track 與否使用者決定）
- **目錄即索引**：不建 index——kebab 檔名＋JSON `meta.title` 自描述；手維護 index 是 drift-prone 清單（同 skills/CLAUDE.md 索引教訓），量大再考慮機械投影生成（YAGNI）
- **git 分工（⚖️ 源進 git、產物不進、一命令再生——單一源，per-repo 可覆蓋）**：**JSON IR＋`.mmd` 源＋visual-check receipt 進 git**（源=機器可讀結構快照＋再生源頭——`.mmd` 與 JSON IR 對位，任務家與 `arch-report/` 兩場景同規）；**渲染產物不進**（archify HTML 每顆 ~720KB 內嵌 viewer runtime，git 比例 175:1；mermaid `diagram-*.svg` 同理）——本地在盤、分享時複製出檔、fresh clone 用源＋一命令再生；排除規則（`.gitignore` 條目）：`arch-report/` 下 `**/*.html`、`**/*.svg`、`**/*.visual-check.*.png`；任務家（`ai-analysis/_tasks/` 與 `_projects/` 同款）`**/diagram-*.html`、`**/diagram-*.svg`、`**/diagram-*.png`、`**/diagram-*.visual-check.*.png`——`.mmd` 源不受任何條目影響（進 git）
- **html→md 雙輸出**：同主題先 html 後要 md 沉澱 → 從同一 grounding 事實再渲染 Mermaid（非 JSON 機械轉譯）；md 是 source of record

## 重生（regeneration）

**觸發**：user 說「**重生 arch-report**」／「**重生報告殼**」（全量）或「重生 `<主題>`」（單目錄）；fresh clone 後；`git clean -Xf arch-report/` 之後。

**程序**（對每個含 JSON IR 的報告目錄——`arch-report/<主題>/` 與任務家 `*/` 殼目錄〔`ai-analysis/_tasks/`、`ai-analysis/_projects/*/tasks/`、`00-tasks/`——存在者〕）：

1. 圖型 = JSON 檔名後綴（`.architecture` / `.workflow` / `.sequence` / `.dataflow` / `.lifecycle`）；mermaid 圖 = `.mmd` 源
2. `deliver <type> <主題>.<type>.json <目錄>/index.html`——JSON 含 `meta.repository`（證據圖）者加 `--repo-root <repo根>`；mermaid：`npx -y @mermaid-js/mermaid-cli -i diagram-<name>.mmd -o diagram-<name>.svg -t dark -b transparent`；archify 路徑依上方存在性偵測
3. 驗收態（可選）：`visual-check <目錄>/index.html`（需要 Chrome；產 receipt＋截圖＋contact sheet）
4. 確定性保證：同源 → 逐位元組相同產物（sha256 可驗）；重生後指紋對不上 = 源或工具版本變了，如實回報

缺場/壞場：報告哪些目錄待裝 archify，不靜默跳過。

## drift compare（post-build，opt-in）

- 僅 `architecture` 型：`compare architecture <base.json> <head.json> <output.html> --json`
- base/head JSON 由 drift spine 事實作者化（SEED git diff → GENERATE graph facts → 兩時點各作者化一份）；機械 receipt（added/removed/changed/moved/rerouted）與 drift 5 signal class 的 no-severity 原則同構
- guard：compare 任務（base/head/delta 各自 validate）計入 session 總預算**合併計**
- 產物一次性：base/head/delta 審完即棄，不 track

## Authoring 教訓（踩過的坑）

- **viewBox 縮放物理**：1440px viewport 下 viewer 給圖 ~930px；字級投影 = 930/viewBox寬 × 原字級，最小字級需 ≥6px——**viewBox 寧窄勿寬**（scale 大 → 字大 → 全部文字過門檻）；高度受頁高預算限制
- **CJK sublabel 是字級殺手**：中文每字 2× 寬，sublabel 帶 CJK 易縮到字級下限——優先縮文字（去 CJK/去裝飾詞），再縮 viewBox 寬
- **低價值邊先砍再繞**：backward 邊/交叉邊引發穿點與 label 衝突——依 archify 紀律移除並沉到卡片，比硬繞 via 便宜且語意更清楚；**刪邊取捨顯式記錄**在圖備註/cards（事實不丟、圖不爛——平面性與語義完整性衝突時，「降級為文字記載」是第三選項，不是只有硬塞/換工具二選一）
- **卡片行高參與頁高預算**：cards item 過長 wrap 推高頁面——item 單行為原則
- **dataflow 座標系先讀 renderer 常數再 author**：stage/row 座標是 renderer 固定值（`render-dataflow.mjs` layout 常數段：stageX=leftX+k×colGap、rowYs/nodeW/nodeH 寫死）——via/labelAt 是絕對座標，盲猜座標每輪 validate 都在錯地方修（真實案例：2026-09-01 golden-data-pipeline 作者未讀常數，多輪修復耗在錯座標系，含一次整圖按錯誤欄寬重排全廢）
- **dataflow viewBox 寬 930 是 readability 分水嶺**：寬 >930 → scale <1 → sublabel/tag 的 preferred 7px 投影 <7px；而 stages 有最小寬（5 stages＝1068）**超過 930**——此約束下 sublabel/tag 必須短到 fitted=preferred（7px→6.09px 壓線過）；任何被壓到 minimum 6px 的字即 readability fail。CJK sublabel 縮文字是首要手段
- **via 首尾段必須垂直於節點邊**：fromSide bottom → 首段 vertical 向下；via[0] 直接放側向座標會連環觸發 diagonal-segment 與 endpoint-side-direction——正確形態從錨點同軸出發再轉走廊（`[[315,230],[395,230],...]` 而非 `[[395,186],...]`）
- **跨 ≥3 stage 的長邊在 stage 佈局幾乎必死結**：起訖欄中間的橫向走廊（他邊的底部/頂部繞行）與長邊的垂直穿越段不可調和（真實案例：mosaic `arch-report/golden-data-pipeline/`——csv→rebuild2 長邊砍掉、語義沉到 rebuild2 sublabel「同源 CSV 重算」——一次解掉 5 條連鎖 constraint）
- **visual-check containment（viewport-overflow）對 dataflow 頁面是基線 fail**：官方 example 同樣 fail（header＋圖＋cards 在 1440×900 必垂直滾）——**交付標準＝validate showcase 全綠＋readability（最小投影字 ≥6px）**；containment fail 如實回報為 viewer 基線行為，非 authoring 缺陷。連帶：viewBox 高度有下限（最後 row 底 + stageBottomPad）——為頁高壓高度會觸發 readable-area fail
- **containment ≠ readability，readability 是底線**：縱向組成超一屏是組成事實（多節點＋cards 本來就垂直滾；殼內 iframe 可捲，containment 只在獨立全屏無捲動預期場景致命）；**禁為 containment 硬壓字級**——layout 緊緻重構設停手線（兩輪無改善即停）；回報紀律：validate/deliver exit 0＋containment fail 如實並列，不宣稱視覺全過
