# EP：CR plugin skill 分層拆遷——ai-rules↔code-reality 內容所有權翻轉

> **ep_type**: implementation（docs mode——變更全為 `.md`，無 `.py` callable 符號）

## 實作總覽

**目標**：把 ai-rules `skills/code-reality/SKILL.md` 中「任何 CR 用戶都需要」的工具事實與坑，拆到 CR repo 的 plugin skill（`plugin/skills/code-reality/SKILL.md`，英文、standalone 定位）；ai-rules 端保留工作流接線與生態慣例，形成**受眾分層雙源**。同班清掉歷輪 CRG→code-reality 翻轉的漏網殘留（含 crg-query query map 死工具名）。

**判定準則**（已 user 對話定案）：工具的「是什麼、怎麼跑、有什麼坑」→ CR repo；生態的「何時跑、接在哪、什麼紀律」→ ai-rules。分層準則＝揮發度：隨工具演進變的歸 CR（綁發版），隨教訓/工作流變的歸 ai-rules（symlink live）。

**裁決更新**（本 EP 落地後記錄）：08-28「plugin 純 MCP carrier 不綁 skill」→「**綁 standalone 級 skill（入門/坑/工具面），不綁 ai-rules 級深度內容（接線/紀律）**」。

**執行形態**：hub-relay——S1 產出 CR handoff（user 貼 CR session，單一寫入者拓撲）；S2 起待回執後在 ai-rules 執行；S3/S4 純 ai-rules 端。S3 與 S2 無依賴，可先做。

## UC 盤點

### Backlog 關聯

- `cr-dist-pypi-install-face-flip.md`——**行管轄互動（已查明）**：該卡 flip 盤點引用 ai-rules skill 三處 cargo install 行（L17 存在性偵測段＋L55-56 pyrefly-index）。本 EP S2 修剪**不動安裝敘述**（觸發條件 S3 PyPI 首發未滿足，安裝面翻轉歸該卡）；S2 若使行號漂移，回執時在該卡 Grounding 段補一行新行號。
- 本 EP 追蹤卡：`ep-cr-plugin-skill-split.md`（EP 生成時已建）
- 無新增能力 UC（docs 治理變更；「CR plugin standalone skill」屬 CR repo 的分發面，非 ai-rules Capabilities）

### 掃描範圍

- ai-rules：`skills/code-reality/SKILL.md`、`skills/crg-query/SKILL.md`、`skills/arch-thinking/SKILL.md`＋`skills/_common/illustrate-artifact-menu.md`（已修未 commit）、`skills/smell-detector/baseline.md`、`skills/corpus-recall/SKILL.md`、`skills/blueprint-bootstrap/SKILL.md`、`skills/CLAUDE.md`、`.kanban/Backlog/`
- CR repo：`plugin/skills/code-reality/SKILL.md`（source；EP 生成時曾驗 identical 於 ZCode cache 0.1.4，後經並行 session 前移——見 D5）、`plugin/README.md`、`README.md`（Quickstart 已覆蓋刷鏈基本面）、`marketplace.json`

### 受影響命令 / rules 清單（docs mode 版 Capabilities）

| 檔案 | 變更性質 |
|---|---|
| `skills/code-reality/SKILL.md` | 內容所有權修剪＋錨點化＋受眾邊界聲明 |
| `skills/crg-query/SKILL.md` | division 表 4 行補翻＋query map 重寫（死工具名）＋L102-103 注記更新 |
| `skills/implement/SKILL.md`、`skills/execution-plan/SKILL.md`、`skills/code-review/SKILL.md` | 指導性死工具名翻轉（各 1 處，review 補抓） |
| `skills/smell-detector/baseline.md` | CRG 殘留 19 處翻轉＋L37 rustup 副本改錨點 |
| `skills/corpus-recall/SKILL.md`、`skills/blueprint-bootstrap/SKILL.md` | 各 1 行 label 翻轉 |
| `skills/CLAUDE.md` | L141 措辭＋code-reality 索引 description 同步 |
| CR repo `plugin/skills/code-reality/SKILL.md`（relay） | 擴充吸收清單（S1 規格） |

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | standalone 用戶踩 rustup proxy 坑 | 從 slot cwd 重生 index | plugin skill 已教直呼 repo-pin binary（rg `rust-analyzer` 於 plugin skill 命中直呼句） | 無 | — |
| SM-2 | AI session 載 code-reality skill 查刷鏈 | on-demand 載入 | ai-rules 版給接線＋錨點；細節在 CR（兩檔分工聲明在場） | 無 | — |
| SM-3 | 名稱碰撞（plugin 版＋symlink 版同在） | ZCode skill 清單三條目 | ai-rules 版邊界聲明「本檔=操作真相源」在場，AI 選擇有依據 | 無 | — |
| SM-4 | AI 依 crg-query query map 呼叫死工具 | 讀 `refactor_tool`/`get_flow`/`query_graph` | S3 後 map 全為現行工具名，死名 rg 0 命中 | 無 | — |
| SM-5 | S2 誤搶 cr-dist 卡管轄行 | 修剪 L17/L55-56 區域 | 安裝敘述原狀保留（diff 不含 cargo→uv 翻轉） | 無 | — |
| SM-6 | plugin content-only 變更不生效 | CR 改 plugin/ 未 bump | handoff 內建三處版本 bump＋`dist-marketplace.sh` 步驟（plugin README Updating 段流程） | 無 | — |

## 段落 0：全域研究摘要（dry run 已執行，2026-08-29）

**可複用基礎設施**（不重造）：
- CR repo 三層載體已存在：repo README（人類安裝/概觀，Quickstart 已含刷鏈基本面＋W5 注記＋ensure_indexes）、`plugin/README.md`（雙市場檔/版本軸/freshness/更新流程）、`plugin/skills/code-reality/SKILL.md`（AI 操作手冊，現 54 行）。搬遷目標層：**坑與操作語義 → plugin skill**；README 已覆蓋項不重複搬。
- ai-rules symlink farm＝S2 修剪後即時生效，無 deploy 步驟（skill 不進 bundle）。

**關鍵落差**（dry run 實測，CR 端目前缺的四件）：
1. rustup proxy 直呼教訓（ai-rules skill scip_refs 行內，NT 實案 +322/−5 假差）
2. 2442692 安全句——plugin skill Prerequisites 現為舊時序敘述（"stamp/build-cache as usual"），缺「單跑 pyrefly-index 後直接 build 亦安全＋mtime 閘門」
3. refs 密度語義（~12.7x、dunder 崩縮、`golden_corpus --normalize` 預期管理）
4. scip-python fallback 專屬坑（cwd 靜默錯 repo exit 0、fatal 仍寫 partial index）

**風險假設**：
- 🟡 plugin cache 版本鎖：plugin/ 內容變更需三處 bump＋marketplace refresh 才可見（SM-6 已內建對策；handoff 必含）
- 🟡 cr-dist 卡行搶管轄（SM-5 已內建對策）
- 🟢 行號漂移：EP 錨點用「行號＋內容特徵」雙錨，執行前 rg 驗證

**baseline**: `a7dd3f26bbcfdb21e2c54b4d93ec10d02fcba3cc`（working tree 註記：`skills/arch-thinking/SKILL.md`＋`skills/_common/illustrate-artifact-menu.md` 有本弧前置修正未 commit——屬同一 CRG 殘留故事線，隨本 EP 或單獨 commit 皆可；`ai-analysis/tours/` untracked 非本 session 產物不動）

## 段落劃分原則

S1（relay 出）→ S2（回執後）；S3、S4 與 S1/S2 無依賴可先行。段落級驗證全為 docs mode 形態（rg 殘留＋跨檔一致性＋gate 於 S4 統一跑）。

---

## S1：CR handoff 產出與交付

### Context

**UC 引用**：無新增 UC；實作「CR plugin standalone skill 受眾分層」（CR repo 分發面）。

**依賴**：無前置。**語義約束**：與 S2 共享「搬遷清單」單一版本（本段附錄 A 即清單本體，S2 引用之）；與 cr-dist 卡共享「安裝敘述行不動」約束。

**依賴錨點**：
- `plugin/skills/code-reality/SKILL.md` → 定義 `/Users/ctai/Github/code-reality/plugin/skills/code-reality/SKILL.md`（54 行，source==cache 0.1.4 已驗）／消費 ZCode plugin cache `0.1.4/skills/`
- ai-rules 搬遷源 → `skills/code-reality/SKILL.md` L47（rustup 教訓）、L59（2442692 句）、L61（refs 密度）、L63（scip-python 坑）、L65（slot 約束）、L67（邊 kind）、L69-109（profile schema＋authoring 四步）、L111-113（口徑限制）、L115-117（boundary 假設）

### 修改要點（docs mode——無 pseudo code）

產出 **CR handoff prompt**（self-contained，附錄 A 搬遷規格），內容必含：
1. 搬遷清單（附錄 A）——英文重寫進 plugin skill；坑類逐條對應 ai-rules 源行號供對照；**附 L47 切割示意**（rustup 教訓句抽走後，L47 職責欄保留形態＝slot 時序＋`[SRC]` 語義精簡句——供 CR 端對照，也是 S2 的手術邊界）
2. 分層指示：坑/操作語義 → plugin skill；README 已覆蓋項跳過；README 舊時序句補 2442692 句為可選項（CR 自主）
3. 版本紀律：三處 bump（plugin manifest、ZCode marketplace.json、CC `.claude-plugin/marketplace.json`）＋`scripts/dist-marketplace.sh`（plugin README「Updating」段流程）
4. 驗收（CR 端）：plugin skill rg 命中四件關鍵落差關鍵詞（`rust-analyzer` 直呼句、`mtime`、`12.7`/`density`、`partial index`）＋英文＋無 ai-rules 命令名洩漏（`rg '/implement|/debrief|/post-build|/code-review|crg-query'` 零命中——slash 形態＝命令引用判準，bare 英文動詞不計）
5. 回執格式：commit hash＋bump 版本＋變更檔＋上述 rg 證據 → user 貼回 ai-rules 觸發 S2

**成功標準**：handoff prompt 交付 user（本段完成即 EP 首個可結算點）。

### 驗證策略

- handoff 內容自檢：附錄 A 每條附 ai-rules 源錨點（rg 可驗）；回執後 S2 執行前機械核對（rg 搬遷關鍵詞於 CR plugin skill 命中）。

---

## S2：回執後 ai-rules skill 修剪＋邊界聲明

### Context

**UC 引用**：更新既有「code-reality 工具鏈程序層」skill 的形態（接線層強化、工具事實層外移）。

**依賴**：S1 回執。**語義約束**：與 cr-dist 卡——L17/L55-56 安裝敘述原狀保留（SM-5）；與 S1——刪除範圍=附錄 A 已搬項，未搬項全留。

**依賴錨點**：同 S1 源行號；另 `skills/CLAUDE.md` code-reality 索引行（description 同步）。

### 修改要點

1. **刪**（已搬 CR 的，ai-rules 版移除）：rustup 教訓細節、2442692 句、refs 密度三句、scip-python 坑細節、邊 kind 拆分細節、boundary 形狀假設細節、profile authoring 四步全文、口徑限制全文
2. **留錨點**（一行式）：profile schema／口徑限制／坑類 → 「真相源＝CR plugin skill（隨發版）」
3. **留原狀**：存在性偵測述語＋新舊自報一行、MCP↔CLI 對應（L19）、何時跑接線表＋transition gate、工具表接線欄（職責欄縮一行）、pyrefly 段入口命令＋lsp_harvest golden oracle 角色、NT/mosaic profile 示例（領域示例）、安裝敘述（cr-dist 卡管轄）
4. **新增受眾邊界聲明**（開頭段一行）：「plugin 版 skill＝standalone 入門（英文、隨 CR 發版）；本檔＝生態操作真相源（接線/紀律/教訓收編）——同名時以本檔為準」

### 驗證策略

- `rg 'rustup|partial index|12.7|golden_corpus|authoring 程序' skills/code-reality/SKILL.md` → 0 命中（已搬項零殘留）
- `rg 'cargo install' skills/code-reality/SKILL.md` → 命中數與修剪前相同（未搶 cr-dist 管轄）
- 接線表完整性：`rg 'implement 階段 1|debrief 第 5 段|模式 B' skills/code-reality/SKILL.md` → 全命中（接線層未誤刪）
- cr-dist 卡 Grounding 段補新行號

---

## S3：CRG 殘留 sync（與 S1/S2 無依賴，可先行）

### Context

**UC 引用**：修復既有 skill 的工具名 drift（crg-query 分工表/arch-thinking 鏡像的下游）。

**依賴**：無。**語義約束**：與 S2 共享「現行工具名清單」（MCP：`refs/callers/closure/audit/impact_radius/detect_changes/hub_nodes/bridge_nodes/list_communities/get_community/architecture_overview/list_flows/affected_flows/semantic_search/get_minimal_context/get_review_context/document_symbols`；CLI ops 以 `code-reality graph_query --repo=<root>` 實測輸出為準——執行時先跑一次取得權威清單）。

**依賴錨點**（現行位點，2026-08-29 掃描＋review 補抓）：
- `skills/crg-query/SKILL.md`：L43（`query_graph` callers_of/callees_of 行）、L45（「CRG `query_graph` 跨語言但無 site 細節」）、L48（CRG `get_affected_flows`）、L49（CRG label）、L51（**死工具** `refactor_tool` mode=dead_code）、L53（Neither LSP nor CRG）、L57-69（Standard CRG query map 全段——`query_graph`/`get_impact_radius`/`get_affected_flows`/`get_flow`/`get_hub_nodes`/`get_bridge_nodes`/`semantic_search_nodes`〔embeddings 注記亦過時——keyword face 已定案〕）、L102（注記自含死名「工具名（`query_graph`、`get_impact_radius`…）省略 `_tool` 後綴」——query map 重寫後同步更新）、L103（「engine semantics 真相源：ai-rules…跨 repo 單一源」——S2 後語義過時，改「接線語義真相源＝ai-rules skill；工具事實真相源＝CR plugin skill」）
- **指導性死工具名三檔（review 補抓，🔴）**：`skills/implement/SKILL.md:166`、`skills/execution-plan/SKILL.md:161`、`skills/code-review/SKILL.md:127`——「用 CRG `query_graph callers_of`／`get_impact_radius`／`get_affected_flows`」是教 AI 呼叫的行為指導（非歷史引述），直接抵觸 SM-4
- `skills/smell-detector/baseline.md`：L7/24/27/32/38/44/50/54/58/68/71/73/82/87/88/90/96/109/127 共 **19 處**（review 修正：EP 初版列 14 漏 5——L50 CRG facts 委託、L58/L88 `get_hub_nodes`/`get_bridge_nodes` 死名、L90 `query_graph callers_of` 死名、L127 Reference CRG facts 紀律；`query_graph importers_of` 該 op 存在性先對 binary 驗證，不在現行 map 則改 `communities`＋rg 目錄聚合替代）＋**L37 rustup 直呼教訓副本**——A1 搬 CR 後留一句操作指引＋錨點指向 plugin skill（分層準則：工具坑單源住 CR，防雙源漂移）
- `skills/code-reality/SKILL.md` L28＋L47「CRG 同鍵去重受害符號」歷史字眼——改述為 graph_audit 缺差對照語義（L28 接線表保留僅換詞、L47 職責欄同）
- `skills/corpus-recall/SKILL.md` L33、`skills/blueprint-bootstrap/SKILL.md` L48（label 翻轉，`hub_refs` 工具本身現行✓）
- `skills/CLAUDE.md` L141（「CRG 裝了才 fire」→「engine 在場才 fire」）

### 修改要點

1. crg-query division 表 4 行：CRG label→code-reality＋工具名對齊現行清單
2. query map 重寫：死工具名全換現行名；`refactor_tool` dead-code 行**刪除**（現行 engine 無此工具——dead-code 判定路徑改述為 `callers` 歸零＋`hub_refs` hazard 安全網，或僅刪行留 LSP zero-hits 對照語義）；L102-103 注記同步更新（見錨點）
3. smell-detector/baseline.md 全檔翻轉（19 處；`importers_of` 驗證後處置；L37 rustup 副本改錨點）
4. 三個指導性死工具名檔翻轉（implement／execution-plan／code-review——工具名對齊現行清單，CRG label 同步換）
5. 單行翻轉批：corpus-recall L33、blueprint-bootstrap L48、skills/CLAUDE.md L141、code-reality SKILL.md L28/L47「CRG 同鍵」字眼

### 驗證策略

- 變體掃全綠：`rg 'CRG|query_graph|get_impact_radius|get_hub_nodes|get_bridge_nodes|get_affected_flows|get_flow[^s]|refactor_tool|semantic_search_nodes|get_architecture_overview' skills/ --glob '!**/_done/**'` → 僅剩**允許清單**（機械判準，review 修正後列明）：①crg-query skill 名 `crg-query` 自身與其「Detect CRG」GATE 標題（歷史名保留）；②crg-query L9/L79-94 歷史記錄段（retired museum、cutover 記錄、舊 server 敘述——歷史引述不改寫）；③`_done/`、`.kanban/`、`ai-analysis/` 報告類歷史文檔。清單外命中＝失敗
- 每個改動位點對照本段錨點行（漂移時 rg 內容特徵重定位）

---

## S4：收尾（gate＋結算）

### 修改要點

1. `/consistency` formal gate（範圍=本 EP authored .md 變更檔；forked guard bug 時獨立 agent 等價替代）
2. `skills/CLAUDE.md`：code-reality/crg-query 索引行 description 同步新形態
3. Backlog 結算：追蹤卡（EP 生成時已建 `.kanban/Backlog/ep-cr-plugin-skill-split.md`）搬 Done/；cr-dist 卡 Grounding 補行
4. 裁決記錄：memory/roadmap 補「plugin 綁 standalone 級 skill」定案＋本 EP 收案
5. commit（等 user 原話；建議拆兩 commit：S1-S2 拆遷弧／S3 殘留 sync＋S4——或 user 指定）

### 驗證策略

- gate 綠＋`git status` tree 淨（排除非本 session 產物）＋SM-1~SM-6 逐項複核

---

## EP Review 記錄（2026-08-29，fresh-eyes 獨立 agent＋judge 回寫）

| Finding | 嚴重度 | Judge | 處置 |
|---|---|---|---|
| implement/execution-plan/code-review 三檔指導性死工具名（:166/:161/:127）——S3 掃描範圍未含，自設驗收必失敗 | 🔴 | ✅採納 | S3 錨點＋修改要點 4 已補；UC 盤點清單已補 |
| baseline.md 殘留漏 5 行（L50/58/88/90/127），計數 14→19 | 🟡 | ✅採納 | S3 錨點＋修改要點已改 |
| code-reality L28/L47「CRG 同鍵」歷史字眼無處置 | 🟡 | ✅採納 | S3 修改要點 5 已補（換詞不刪行） |
| crg-query L102 注記自含死名、L103「單一源」S2 後過時 | 🟡 | ✅採納 | S3 錨點＋修改要點 2 已補 |
| A7 錨點區間與禁搬示例塊重疊——機械執行會誤刪 | 🟡 | ✅採納 | 附錄 A7 改逐塊切割表 |
| baseline.md:37 rustup 教訓副本——A1 搬 CR 後雙源 | 🟡 | ✅採納 | S3 錨點已補（留一句＋錨點） |
| S4「建卡」與已存卡矛盾 | 🟡 | ✅採納 | S4 要點 3 已改 |
| plugin skill 行數 55→54 | 🟢 | ✅採納 | 兩處已改 |
| S3 允許項「等」字開放收尾、判讀負擔高 | 🟢 | ✅採納 | 驗證段改機械允許清單 |
| L47 行內多主題混合依賴執行者細心 | 🟢 | ✅採納 | S1 handoff 補 L47 切割示意 |

無否決項。錨點其餘全數機械驗證命中（含 CR 端四件關鍵落差實證、arch-thinking＋menu 殘留 0 命中與 working tree 狀態相符）。

---

## S3+S1 執行偏差記錄（2026-08-29 implement 階段 6 回寫；stage-4 review findings 已 judge 全數處置）

| # | 偏差 | 理由 |
|---|---|---|
| D1 | crg-query L23 部署形態句實質改寫（:5555 殘留→plugin stdio／8200 resident） | 與同檔 Reference 段 L104 矛盾的過時接線——同檔自洽 |
| D2 | crg-query GATE／division／Fallback 標題與 L21-27／L82／L91 內文翻轉（EP 原允許保留歷史名） | 內文翻轉後標題保留歷史名反而不一致 |
| D3 | EP 清單外漏網修復（stage-4 review 抓）：review-engine:81、smell-detector/zoom.md:28、crg-query L31 死名（`list_repos_tool`/`cross_repo_search_tool`——CR codebase 0 命中）、baseline.md:99 死名（`list_graph_stats built_at_sha`——改 `[SRC]`/`--version` 自報錨） | pattern 邊界外殘留 |
| D4 | baseline.md L37 rustup 副本 trim 延後至 S2 | EP 內文「A1 搬 CR 後」條件未滿足——現在 trim 教訓兩邊皆無全文 |
| D5 | handoff「source==cache 0.1.4」宣稱失效 | 並行 CR session 前移 source（L30 slot 路徑分歧、cache 版才符 slot 慣例）——handoff 已改分歧注記＋指示以 ai-rules L47 為準修正 |
| D6 | A7 切割標籤修正（L69-70 實為標題＋空行；欄位語義在示例註解與 authoring 步驟內） | stage-4 review 逐行驗證；EP 附錄 A7 與 handoff 已同步修正 |

---

## 附錄 A：搬遷清單（S1 handoff 規格本體，S2 刪除範圍依據）

| # | 內容塊 | ai-rules 源錨點（skills/code-reality/SKILL.md） | CR 目標層 | 備註 |
|---|---|---|---|---|
| A1 | rustup proxy 直呼教訓（repo-pin binary、cwd 解析 toolchain、+322/−5 假差實案） | L47 scip_refs 行內 | plugin skill（Prerequisites/scip 段） | 最高優先——standalone 用戶必踩 |
| A2 | 2442692 安全句（單跑 pyrefly-index 後直接 build 安全＋自動失效 sidecar＋mtime 閘門） | L59 | plugin skill（Prerequisites）＋README 舊時序句可選同步 | plugin 現為舊時序敘述 |
| A3 | refs 密度語義（~12.7x 預期管理、dunder 崩縮、`golden_corpus --normalize`） | L61 | plugin skill | 輸出語義 |
| A4 | scip-python fallback 專屬坑（cwd 靜默錯 repo exit 0、fatal 仍寫 partial index） | L63 | plugin skill | 工具坑 |
| A5 | slot 不混用約束＋sidecar 時序（stamp→build-cache、lsp cache 短路陷阱） | L47/L59/L65 | plugin skill | 與 A1/A2 同段整合 |
| A6 | 邊 kind 拆分（CALLS vs REFERENCES、ruff parse、dunder class 段回退） | L67 | plugin skill | 工具行為 |
| A7 | profile schema＋authoring 程序（欄位語義、四步、prefix 涵蓋度=幀存活度、exclude 斜線 assert） | L69-109 **區間內逐塊切割**（review 補＋stage-4 修正）：搬 L101-102 無 profile fallback＋L104-109 authoring 四步（欄位語義教學在步驟內）；**L71-100（mosaic/NT/hazard_registry 三示例塊，含其欄位註解）留 ai-rules 不搬** | plugin skill（或 README——CR 自主分層） | 英文重寫帶通用示例；示例塊留 ai-rules |
| A8 | 口徑限制（claims regex prefix 衍生、三態語義、相對路徑正規化） | L111-113 | plugin skill | 輸出語義 |
| A9 | boundary 已知形狀假設（pyi_module NT 假設、crash=loud 設計） | L115-117 | plugin skill 或 docstring/README（CR 自主） | 工具已知限制 |
| A10 | 新舊自報機制細節（`--version` 嵌 rev、stale WARN 雙信號、post-commit hook） | L17 行內 | plugin README 已有 freshness 段——**校對即可，勿重複** | 僅校對 |

**禁搬清單**（S2 全留）：何時跑接線表、transition gate、lsp_harvest golden oracle 角色定位、工具表接線欄、NT/mosaic profile 示例、存在性偵測述語、MCP↔CLI 對應、安裝敘述（cr-dist 卡管轄）。
