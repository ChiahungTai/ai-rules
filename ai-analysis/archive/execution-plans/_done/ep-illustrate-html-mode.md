# EP: illustrate html 輸出模式 — archify 展示級渲染整合

> **ep_type**: implementation（docs mode — 變更全為 `.md`，無 `.py` callable 變更）

baseline: 009e4a6c2f13913a791167eeb51e5f561c00cca1

## 實作總覽

`/illustrate` 新增第三輸出模式 **HTML（opt-in）**：委派外部 archify 渲染引擎（agent 產 typed JSON IR → 確定性編譯自包含互動 HTML），服務「一次性人類 viewport」情境（分享/demo/re-onboard/drift 審查）。Console（即時討論）與 MD（Mermaid 知識沉澱，**維持 source of record**）角色不變——三者是受眾分流非取代。

證據基礎：archify pilot（`ai-analysis/reports/archify-pilot-report.md`）——四圖型全走通 showcase validate + visual-check；vision agent 驗收裁定「有條件價值」，條件即本 EP 的設計約束：

| # | 驗收條件 | 本 EP 落點 |
|---|---------|-----------|
| 1 | opt-in 觸發，非預設 | S1（決策流程＋執行鐵律） |
| 2 | repair 輪數上限 guard（>6 降級 Mermaid＋回報） | S2 |
| 3 | AI 判斷增益（mode D/drift 情境才建議，非四型全上） | S1 |
| 4 | Mermaid 維持 source of record；HTML 按需渲染＋生命週期約定 | S1/S2 |

## EP Review Findings

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| D-01/F1-01 | 🔴 必須修正 | S0/S2/SM-3 | guard=6 使映射表主目標（architecture 7/dataflow 12/workflow 12 輪）常態降級——與 pilot 證據矛盾；計數口徑未定義；「39 輪」應為 37 | 口徑精確化＋數值重校 | implemented |
| F1-02 | 🟡 建議 | 掃描範圍 | illustrate-*.md 實為 6 檔非 5 檔 | 計數修正 | implemented |
| F1-03 | 🟡 建議 | 收尾 | pilot 產物 untracked 處置未交代、.gitignore 無 HTML 規則 | 收尾清單補產物處置＋.gitignore 規則 | implemented |
| F1-04 | ℹ️ 提醒 | S1 | illustrate-examples.md 補 html 範例是對稱動作 | S3 加一項 | implemented |
| F2-01 | 🟡 建議 | S2 | 要點文案自帶輪數統計，照抄落地違反元資訊禁令 | 明示統計留 EP/report、skill 檔只寫 guard 值＋定性理由 | implemented |
| F3-01 | 🟡 建議 | S1 | mode B + html 路由斷層（映射表全是 mode B 語彙，決策流程無 html 分支） | S1 決策流程補 mode B html 分支 | implemented |
| F3-02 | 🟡 建議 | S1/SM-6 | 「Console 永不觸發」未編入鐵律且字面推不出 | 鐵律明寫 html 是寫檔模式、Console 語境明示 = 切換模式非 inline | implemented |
| F3-03 | 🟡 建議 | S2/SM-2 | archify skill description 觸發詞與 illustrate 完全重疊，安裝後競爭路由 | S2 加分工聲明（illustrate=grounding/受眾/路由入口；archify standalone=raw 渲染） | implemented |
| F3-04 | 🟡 建議 | S2 | 偵測順序前兩項同物理位置（三根 symlink 同源）；npx skills add -g 會穿 symlink 寫進 ai-rules repo | 偵測改「skills 任一根→clone」；安裝建議 clone 優先＋symlink 警告 | implemented |
| F4-01 | 🟡 建議 | SM | 缺「在場但壞」場景（node 缺/版本舊/breaking）；偵測只查存在性 | SM-8 補＋偵測程序加首跑 doctor | implemented |
| F4-02 | 🟡 建議 | S2 | guard 單圖口徑，多圖請求仍可吃爆 session | 補 per-session 總預算 | implemented |
| F5-01/F5-02/F5-03 | 🟡/ℹ️ | SM | 缺 html→md 雙輸出、drift compare guard 口徑與產物處置、--output 互動 | SM 補三列＋S2 對應條款 | implemented |
| D-02 | ✅ 提醒 | 總覽 | 與 archify standalone 的分工應明示 | 併 F3-03 | implemented |

**guard 設計定案（D-01 修正）**：口徑＝**validate 呼叫輪數**（每次 candidate 修改後的 validate 記 1 輪，含 containment 修復）；**單圖上限 12 輪**（涵蓋 pilot 全部實測案例 7/12/12/6——不是常規預期而是止損線）；**per-session 總預算 18 輪**（多圖請求）；**無改善即停**引用 archify SKILL.md 自帶止損（兩連續輪未降錯誤數即停——illustrate guard 與之互補）。skill 檔只寫 guard 值與定性理由，輪數統計留 EP/report（元資訊禁令）。

## UC 盤點（docs mode：受影響命令/rules 清單）

### Backlog 關聯
- 自動建卡：`[tag:skills] illustrate html 輸出模式（archify 整合）`（本 EP 追蹤卡）——建於 `.kanban/Backlog/illustrate-html-mode-archify.md`

### SYSTEM-MAP 影響
- 無 SYSTEM-MAP.md（ai-rules 為元專案，正當跳過）

### 掃描範圍
- `skills/illustrate/SKILL.md`（主變更）、`skills/_common/illustrate-*.md`（6 檔：analysis / artifact-menu / deep-analysis / examples / parallel-architecture / structure-viewport）、`skills/CLAUDE.md`（工作流索引 L53）、`skills/mermaid/SKILL.md`（對照，不動）、外部 `~/Github/archify/archify/SKILL.md`（authoring 權威，不動不重述）

### 既有 UC 狀態
| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| /illustrate 圖解（console/md） | ✅ | skills/CLAUDE.md 索引 | 更新 | description 加 html 模式 |
| mode B artifact menu（5 artifact） | ✅ | illustrate-artifact-menu.md | 更新 | 加 html 類型映射 pointer |
| drift overlay（drift spine） | ✅ | illustrate-artifact-menu.md | 更新 | RENDER 段加 html compare 選項 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| /illustrate html 輸出（archify 展示級互動圖，opt-in＋降級 guard） | 📋 | `skills/illustrate/SKILL.md` + `skills/_common/illustrate-html-mode.md` |

## Scenario Matrix（docs mode：文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 明示 html | `/illustrate html <主題或 @dir>` | 走 archify 委派流程（偵測→類型映射→authoring→deliver） | 無 | html 輸出 |
| SM-2 | archify 缺場 | 偵測順序全 miss（無 skill 安裝、無 repo clone） | 降級輸出 MD Mermaid＋明確告知缺場與安裝方式，**不靜默失敗** | 降級即恢復點 | html 輸出 |
| SM-3 | repair 輪數爆炸 | 單圖 validate 輪數 > 12，或 session 累計 > 18，或兩連續輪無改善（archify 自帶止損） | 停止修復、降級 Mermaid 版、回報殘留診斷（subject/evidence） | 降級即恢復點 | html 輸出 |
| SM-4 | mode D 分享情境 | `/illustrate md <主題>` 且使用者意圖是分享/展示 | **建議** html（增益判斷：互動搜尋/focus/Present 對位），不自動切換 | 無 | html 輸出 |
| SM-5 | post-build drift 審查 | 使用者在 drift checkpoint 明示要比對圖 | html compare（僅 architecture 型；base/head JSON 由 drift spine 事實作者化） | 無 | drift overlay |
| SM-6 | Console 即時討論 | 無 param 或 console 模式 | **永不觸發 archify**（鐵律：Console 禁 Mermaid 語法延伸——禁重渲染引擎） | 無 | 既有鐵律 |
| SM-7 | 產物生命週期 | html 產出後 | JSON IR 與 HTML 同目錄並存（JSON=再生源頭，tracked）；HTML/截圖 sidecar 依 .gitignore 規則不進 repo 常駐層 | 無 | html 輸出 |
| SM-8 | 在場但壞 | archify 在場但 `doctor` 失敗（node 缺/版本 <18/上游 breaking） | 同缺場降級路徑（MD Mermaid＋回報 doctor 診斷）；首次使用先跑 doctor 一次 | 降級即恢復點 | html 輸出 |
| SM-9 | html 後要 md | 同主題先 html 後要求 md 沉澱 | 從同一 grounding 事實再渲染 Mermaid（非 JSON 機械轉譯）；md 是 source of record | 無 | html 輸出 |
| SM-10 | drift compare 口徑 | compare 任務（base/head/delta 各自 validate） | 計入 session 總預算合併計（非每圖獨立 12 輪）；base/head/delta 產物一次性——審完即棄不 track | 無 | drift overlay |
| SM-11 | --output 自訂路徑 | user 明示 `--output <path>` | 尊崇自訂路徑；track 與否由使用者決定（預設規則只約束預設路徑） | 無 | html 輸出 |

## 段落 0：全域研究摘要

研究已由 pilot 超額完成（39 輪 validate 實測 + schema 全讀 + CLI 表面實測），證據：`ai-analysis/reports/archify-pilot-report.md`。關鍵事實（自足摘錄）：

- **可複用基礎設施**：archify skill 自帶 authoring contract（bounded path：type router → 讀 schema+example → author JSON → validate showcase → repair → deliver → visual-check；自帶止損「兩連續輪無改善即停」），**不重述、只委派**（單一源紀律）。CLI 穩定面：`render / validate / deliver / compare architecture / visual-check / doctor`（v2.16.0 實測）。
- **存在性**：archify 未安裝於任何 harness skills 根；repo clone 在 `~/Github/archify/archify`（doctor 全綠、Node ≥18 即免裝）。注意：`~/.zcode/skills`、`~/.claude/skills`、`~/.agents/skills` 三根 symlink 同源 ai-rules/skills——skills 目錄安裝會穿 symlink 寫進 ai-rules repo（F3-04）。
- **authoring 成本實測**（validate 呼叫輪數，總計 37 輪）：sequence（y 排序）6 輪、workflow（lane/col）12 輪、architecture（自由 pos）7 輪、dataflow 12 輪——guard 值設計見 EP Review Findings 表（單圖 12 止損＋session 18 預算，涵蓋全部實測）。
- **驗證閘門誠實**：visual-check 抓到初版 4/4 overflow，修復迴圈收斂——品質閘門可信。
- **風險假設**（皆已實測消除）：①本地可跑（doctor 全綠 ✅）②私有 repo 可用 repository evidence（mosaic 有 GitHub origin ✅）③CJK 字級會觸發 6px 門檻（已量化，寫進 S2 教訓 ✅）。無致命等級殘留。
- **外部依賴 drift 風險**：archify 上游移動快（v2.16 今日發版）——整合只耦合穩定命令面 + 存在性偵測，不內嵌 schema 細節。

## 段落 1：illustrate SKILL.md 輸出模式擴充

### Context
- **UC 引用**：實作「/illustrate html 輸出（archify 展示級互動圖，opt-in＋降級 guard）」
- **依賴**：S2（illustrate-html-mode.md 承載細節，本段只做路由與鐵律）；S3 索引同步依賴本段定案的模式名
- **語義約束**：與 S2/S3 共享「模式名 = `html`（小寫）」「降級目標 = MD Mermaid」
- **基礎設施盤點**：既有輸出模式表（SKILL.md L14-21）、執行鐵律（L21）、使用方式（L50-58）、決策流程（L101-117）、Supporting Files 表（L154-163）——全部既有結構擴充，無新骨架
- **修改要點**（docs mode，替代 Pseudo Code）：
  1. frontmatter `description`/`when_to_use`：`console/md` → `console/md/html` 三模式（html = archify 委派）
  2. 輸出模式表加列：`| **HTML**（opt-in） | archify 互動圖（委派 [illustrate-html-mode.md](../_common/illustrate-html-mode.md)） | 展示級（互動搜尋/focus/Present） | 分享 / demo / re-onboard / drift 審查 |`
  3. 執行鐵律擴充：加「HTML 是**寫檔模式**——僅明示 `html` 或增益判斷時觸發；Console 語境明示 html = 切換輸出模式（檔案交付＋路徑回報），永不 inline 渲染；archify 缺場/壞場或 guard 超限 → 降級 MD Mermaid 並回報（細節見 illustrate-html-mode.md）」
  4. 使用方式範例加一行：`/illustrate html @src/components/   # HTML 模式 → archify（缺場降級）`
  5. 決策流程：mode D 行補「（md 沉澱；分享情境建議 html——增益判斷）」；mode B 行補 html 分支（`html+@dir/@file → B`：artifact menu 選型後走 html 類型映射，class slice 除外）；輸入判斷線索加 `主題+html→D（archify）` 與 `@dir+html→B（映射）`
  6. Supporting Files 表加 `illustrate-html-mode.md` 行（何時讀取：html 模式觸發/mode D 增益判斷/drift compare）
- **成功標準**：SKILL.md 讀者（AI）能從本體判斷何時進 html 模式、去哪讀細節；鐵律三模式完備

### 驗證策略（文檔驗證）
- rg 對齊：`rg -n "html" skills/illustrate/SKILL.md` 命中模式表/鐵律/範例/流程/Supporting Files 五處
- 導航有效：`illustrate-html-mode.md` 連結指向 S2 產出檔案
- 元資訊禁令合規（無統計/版本號/日期——instruction-writing skill 約束）

## 段落 2：illustrate-html-mode.md 新檔（整合細節，on-demand）

### Context
- **UC 引用**：實作「/illustrate html 輸出」的完整行為規範
- **依賴**：S1 路由到位；外部 archify SKILL.md（authoring 權威——**委派不重述**，只寫 illustrate 側約定）
- **語義約束**：與 S1 共享模式名與降級目標；與 S3 的 artifact-menu 映射**本段為單一源**（menu 只放 pointer）
- **基礎設施盤點**：pilot report（教訓與成本數據）、archify CLI 穩定面、`~/.zcode/skills/archify` 與 `~/Github/archify/archify` 兩個安裝位置
- **修改要點**（新檔結構）：
  1. **觸發條件**：明示 `html` param；mode D 分享情境增益判斷（互動搜尋/focus/Present 對位軌道 ② 消費方式）建議但不自動切；post-build drift compare（opt-in）
  2. **存在性偵測**（順序；三 skills 根 symlink 同源 ai-rules/skills，故 skills 目錄一處即中）：`<skills 根>/archify/bin/archify.mjs`（任一根）→ `~/Github/archify/archify/bin/archify.mjs`（repo clone）→ 全 miss = 缺場：降級 MD Mermaid ＋ 告知安裝方式，不靜默失敗。**首次偵測到後跑 `doctor` 一次**（在場但壞——node 缺/版本舊/上游 breaking——同降級路徑）。**安裝建議 clone 優先**（`git clone https://github.com/tt-a1i/archify ~/Github/archify`）；`npx skills add -g` 在本部署架構（skills 根 symlink 到 ai-rules repo）會穿 symlink 寫進 ai-rules 版本控管目錄——除非使用者明知，不建議
  3. **類型映射**（illustrate 概念 → archify 圖型；mode B artifact 與 mode A/C city map 共用）：boundary/city map→`architecture`、data-flow→`dataflow`、sequence→`sequence`、call graph→`workflow` 或 `sequence`（**優先語意排版型**——authoring 成本低）、class slice→**無對應，維持 md**（不硬映射）
  4. **Authoring 紀律委派**：渲染端全紀律（bounded path、showcase profile、label 保留、repair 順序）以 archify SKILL.md 為準——本檔不重述；illustrate 側補充：grounding 事實先產（讀 code/arch-thinking §二），JSON IR 從事實作者化（節點帶 sources 證據路徑，私有 repo 帶 meta.repository）。**與 archify standalone 的分工**（觸發詞重疊的裁決）：illustrate 是「讀 code → grounding 結構事實 → 受眾/生命週期管理」的入口，archify skill 被偵測到時 illustrate 仍走自己的委派流程；archify standalone 適合 raw 渲染請求（既有 JSON 渲染、Mermaid beautify、無 grounding 需求的 plain-language 圖）——不競爭，分流
  5. **輪數 guard**：口徑＝validate 呼叫輪數；**單圖 12 輪止損 + session 總預算 18 輪**；「兩連續輪無改善即停」引用 archify 自帶止損。超限 → 降級 Mermaid 版＋回報殘留診斷（不接受半成品 HTML 交付）。**元資訊約束**：skill 檔只寫 guard 值與定性理由（自由排版型 authoring 成本高）——輪數統計數據留 EP/pilot report，不寫進 skill 檔
  6. **產物生命週期**：輸出 `ai-analysis/reports/`（與 md 同層；`--output` 自訂路徑尊崇，track 與否由使用者決定）；**JSON IR 與 HTML 並存**（JSON = 再生源頭，tracked）；HTML 與 visual-check 截圖 sidecar 依 `.gitignore` 規則排除（`ai-analysis/reports/**/*.html`、`ai-analysis/reports/**/*.visual-check.*.png`——visual-check receipt JSON 為驗收證據，tracked）；drift compare 的 base/head/delta 產物一次性——審完即棄不 track；需要沉澱的結構知識仍寫 md（source of record）；同主題 html→md = 同一 grounding 事實再渲染（非 JSON 機械轉譯）
  7. **Pilot 教訓**（指向 report 深讀）：viewBox 縮放物理（寧窄勿寬）、CJK sublabel 字級 6px 門檻、低價值邊先砍再繞、卡片行高參與頁高預算
- **成功標準**：AI 只讀本檔（＋archify SKILL.md）即可完成 html 模式全流程，含降級兩路徑

### 驗證策略（文檔驗證）
- 自足性：本檔含觸發/偵測/映射/guard/生命週期五要素，rg 逐項命中
- 與 pilot report 對照：輪數 guard（6）與映射表皆可回溯 report 成本表
- 元資訊禁令合規

## 段落 3：周邊同步（artifact-menu / structure-viewport / 索引）

### Context
- **UC 引用**：更新「mode B artifact menu」「drift overlay」既有 UC + `skills/CLAUDE.md` 索引
- **依賴**：S2 的映射表（**單一源**——本段只放 pointer 不複製內容）
- **語義約束**：menu 與 viewport 檔的 html 提及一律指回 illustrate-html-mode.md，避免映射表多處定義 drift
- **修改要點**：
  1. `illustrate-artifact-menu.md`：5 artifact 表加一行 pointer「html 圖型映射見 [illustrate-html-mode.md](illustrate-html-mode.md)（class slice 維持 md）」
  2. `illustrate-structure-viewport.md`：drift rendering 段加「HTML compare（opt-in，僅 architecture 型——base/head JSON 由 drift spine 事實作者化；guard 計入 session 總預算合併計；產物一次性審完即棄；細節見 illustrate-html-mode.md）」
  3. `skills/CLAUDE.md` L53 illustrate description：`(console / md)` → `(console / md / html〔archify 展示級，opt-in〕)`
  4. `illustrate-examples.md`：補 html 模式範例一節（一個調用範例＋產物形態說明：JSON IR 並存、HTML 交付路徑——簡短，細節不重複）
- **成功標準**：三處 rg 命中且全部 pointer 化（無映射內容複製）

### 驗證策略（文檔驗證）
- 跨檔一致性：`rg -n "illustrate-html-mode" skills/` 命中 ≥4 檔（SKILL.md、html-mode 本體、artifact-menu、structure-viewport）
- 索引同步：`rg -n "html" skills/CLAUDE.md` 命中 illustrate 行

## 整合策略

- 全段落完成後跑 `/consistency`（文檔自洽 gate——跨檔模式名/映射/降級語句對齊）
- drift 掃描含拼寫變體（`html|HTML`、`archify` 大小寫）——feedback_drift-scan-include-variants 紀律
- 部署驗證：`uv run python scripts/deploy_agents.py`（rules bundle 未動——預期無 diff；skills 是 symlink 部署即時生效）

## 收尾步驟

1. Backlog 卡 `illustrate-html-mode-archify.md` → `.kanban/Done/`
2. `skills/CLAUDE.md` 索引同步（S3 已含）
3. instruction 檔合規檢查（元資訊禁令——三段產出全查）
4. **產物處置**（pilot 遺留）：`.gitignore` 加 `ai-analysis/reports/**/*.html` 與 `ai-analysis/reports/**/*.visual-check.*.png` 兩規則；pilot 的 4 份 JSON IR＋report＋visual-check receipts 列入 commit 範圍（HTML/PNG 依規則排除）
5. docs mode 無 /audit-test（無測試變更，正當跳過）
