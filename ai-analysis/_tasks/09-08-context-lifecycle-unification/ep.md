# EP：context 統一生命週期機制——觸發保證 × 層級優化 × instruction-* 重構

> **ep_type**: blueprint（≥5 段皆中型變更；每段 → 衍生 implementation 子 EP）
> baseline: d90f37d

## 實作總覽

**問題**（四個結構性病根，證據在本 EP 段落 0）：

1. **三 lane 平行半成品**：rules bundle／skills catalog／memory 各自解「知識→context 注入＋預算」，各自重造索引/觸發/蒸餾/新鮮度機制（memory generator＋hooks＋telemetry／deploy gate＋bundle-watch／instruction-sync＋consistency）。
2. **觸發不可靠**：讀取路徑＝平面索引預載＋字面巧合；desc 用語是弧語境（arc id/治理詞彙領頭）非任務語境——觸發面詞彙錯位。
3. **層級倒置**：user 層 79KB 承載 on-demand 級內容；project 層發育不全（mosaic root 42.7KB 例外地大）；muse 串接序（user-first、單 64KiB lane）下 project 層直接餓死。
4. **生命週期碎片化**：掃描/歸類/精煉/淘汰散在 memory-audit、instruction-clean/sync、sync-sources、consistency 各管一段，無統一語義。

**目標**：單一機制（座標系＋投影＋觸發文法＋查詢紀律＋完整生命週期），載體分立（git 商品池 rules/skills／觀察池 memory／harness 原生載入面），**觸發保證（有需要就觸發）為成敗指標**。

**核心設計**（討論定案，子 EP 承接展開）：

- **統一座標系**：一切知識單位 = entry `{情境觸發 desc（任務語境領頭）, 一句核心, body 指針, rank（hot/core/cold）, scope（harness 軸，即既有 harness-scope）}`。
- **投影式讀取**：非 Claude 三端的 bundle 以 rank≤core ∩ scope 投影進 always-on floor（觸發剛性=必中類由 floor 承載）；其餘 → routing 索引＋rg 查詢紀律。Claude Code 保留原生 rules 載入；bundle deploy 不影響其 CLAUDE.md。統一的是知識治理與查詢合約，各端載入 adapter 分立，不把 bundle 的 rank 過濾宣稱為 Claude 原生能力。
- **層級軸**：user floor（跨 repo 必中集）／project 層（repo 特定＋目錄分層，mosaic 52 檔為正面標本）／觸發層（其餘）——三層判準表 + per-harness 預算互動（muse 單 lane 串接 vs ZCode 兩檔獨立預算 vs codex chain cap）。
- **生命週期四動**：掃描（audit/telemetry 跨 lane）→ 歸類（cluster＋promotion：memory→skill/rule 固化既有慣例一般化）→ 精煉（distill 管線）→ 淘汰（retire 流程）——**引擎＝memory-audit**（四動判準/稽核方法論單一源）、**執行工具＝instruction-\* 家族**（clean=精煉/淘汰、sync=掃描）——判準與執行分離，不另創 skill（決策 5 相容）。

### 已決策（user 拍板，勿重辯）

1. 統一機制、**載體分立**——rules 不搬 memory pool（「當然不行」）
2. 生命週期四動（掃描/重新整理歸類/精煉/淘汰）＝機制本體，非附屬
3. **觸發保證**（有需要就觸發）是關鍵需求；desc 用語＝觸發面，情境句領頭
4. **層級軸一等公民**：user-level＋project-level AGENTS.md 優化在範圍內；mosaic 細項目錄分層已 OK（前提），root 42.7KB 是重點改善對象
5. **instruction-\* 四 skill（writing/init/clean/sync）納入重構**——統一機制由它們承載，不另創第五個 skill
6. 不用向後相容
7. draft-3（muse 64KiB A/B）被座標系溶解——併入 S3 投影層結案
8. memory 寫入哲學保留（一句話測試/確定才寫/有進有出/單一寫入點）
9. mosaic 側納入研究（root＋目錄分層實態）
10. **desc 文法 5 條定案**（09-08 user 拍板「go」；P5 三家族 dry-run 全 10/10、B 版同構文法勝出的實證背書）：①條件句領頭（「當你要〈任務動詞〉…時」）②雙語觸發詞③一事一條④desc 不放易變快照⑤≤100 字元、禁引號——S1 lint 規則源（SM-9 hook 擋機械可驗部分）

## 段落 0：全域研究摘要（既有材料收編＋缺口）

**已到手材料**（子 EP 直接引用，不重做）：

- 兩份 codex 報告：`ai-analysis/reports/2026-09-08-codex-agents-md-usage-and-insights.md`（五層互補、keep it small、犯兩次才 codify、層級倒置診斷、官方三處方）、`2026-09-08-codex-philosophy-instruction-layering.md`（四家截斷地景表、muse 64KiB 機械證據、codex knob 已調、驗收探針）
- flash agent 逐字研究：351 行（AGENTS.md 官方語義/九項 context pattern/巨型單檔反面證據 7 條）——**已複製進任務家** `codex-context-research.md`
- 本 session 實測：muse rules_file lane 串接語義（user+project 共享 64KiB、produced≠檔案、UTF-8 backoff）、memory 池統計（136 條、~22K/25,000 字元〔09-08 快照，池活躍中——S1 開工以 telemetry 重測更新〕）、ZCode 純 markdown＋rg 制無 semantic recall（平台事實）
- mosaic 結構：root 42,740B＋51 個目錄分層 AGENTS.md（52 檔含 root；3 worktree 同 repo ⚠️ review 未覆核，S0 顺帶確認）
- instruction-* 現況：writing 28,043B（文法權威）／init 12,389B（bottom-up 體系生成、Truth-Anchored）／clean 8,036B（元資訊清理＋distill）／sync 6,253B（md↔code 同步檢查）

**可複用基礎設施**：`_generate_index.py`（投影器雛形）、PreToolUse hooks（寫入閘：desc/body 上限）、`memory_telemetry.py`（Read 觀測，rank 晉升訊號源）、`deploy_agents.py`（scope 過濾＋gate，S3 投影器底座）、memory-audit 兩級稽核（生命週期引擎雛形）、harness-scope frontmatter（座標軸一半已在場）、rank 欄位（另一半**機制**在場——generator 有 parse/sort，但 136 條全走預設 core、值未播種：S1 播種）。

**風險假設**（等級→驗證段落）：

| 假設 | 等級 | 驗證 |
|---|---|---|
| ZCode/CC 有無 desc-matching 召回注入（system-reminder 觀測到 recalled memories 形態） | **致命**（決定觸發面投資報酬率） | S0 probe |
| muse 場景 mosaic 級 project 鏈（42.7KB）任何 user floor 都裝不下單 64KiB lane | 高 | S0 研究＋S3 層級策略 |
| generator 升級為全系統投影器後的 bug 半徑擴大 | 高 | S2 起測試護權（test_memory_lifecycle 模式擴充） |
| rank 晉升靠 Read telemetry，索引行「被看見」不可觀測 | 中 | S1 設計（user/session 回報腿） |
| instruction-writing 28KB 重構量與既有引用面（rules/instruction-writing.md pointer 等） | 中 | S5 引用面掃描 |

## EP Review Findings

本輪證據與五維度覆蓋見 [ep-review.md](ep-review.md)。`implemented` 僅表示審查約束已回寫藍圖，不代表機制已實作或 runtime 驗收通過。

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| 1 | 🔴 必須修正 | S5/整合策略 | S5 依賴 S2/S4 卻排在 S4 之前（S3∥S5→S4），依賴不可滿足 | staging 改串行，writing/init 可與 S3 部分平行（L135 已改） | implemented |
| 2 | 🔴 必須修正 | S3/SM-4 | muse gate「60KiB 硬」（61,440B）放行 floor 可達 61,440，＋project 12.5K 必爆 65,536——gate 綠但 SM-4 紅，驗收不可達 | gate 改 user-floor ≤53KB 硬，與 SM-4/S2 對齊（L122 已改） | implemented |
| 3 | 🟡 建議 | 段落 0 | mosaic「52 個目錄分層」實為 51 子目錄＋root＝52 檔 | 數字已修正；worktree 數未覆核 | implemented |
| 4 | 🟡 建議 | S0/SM-2 | SM-2 含 codex 載入面，但 S0 probe 無 codex knob runtime 認證（TOML 過≠runtime 認） | S0 加 probe：codex 新 session 覆述 bundle 尾端 sentinel | implemented（S0⑥） |
| 5 | 🟡 建議 | S5/整合策略 | 回滾快照僅 S1/S3；S5 writing 28KB 重構無快照 | S5 加投影前快照（SKILL.md 原檔進任務家 version 目錄） | implemented（回滾面 S1/S3/S5） |
| 6 | 🟡 建議 | SM-6 | 對應段落 S2/S4；rank 晉升機制在 S1（觀測晉升）＋S4（promotion），S2 僅靜態初判 | 改為 S1/S4 | implemented |
| 7 | 🟡 建議 | 段落 0 | memory 池統計（136 條、21,760/25,000 字元）review 時無覆核路徑 | S1 開工前以 telemetry 重測並更新數字 | implemented（段落 0 已標快照＋重測註記） |
| 8 | 🟡 建議 | S3 | mosaic root 重分配動別 repo（42.7KB＋多 worktree），執行載體（哪個 session/repo 改）未指定 | S3 補跨 repo 路由：mosaic 肢由 mosaic 側 session 執行（工單形態），user 可改指 | implemented |
| 9 | 🟡 建議 | UC 盤點 | `rules/context-management.md`（L37-39 memory 生命週期 pointer：六問/rank/投影禁手寫/蒸餾觸發詞）漏列受影響載體——S1/S4 直接改寫對象 | 已補列（受影響載體表＋S5 引用面） | implemented |
| 10 | 🔴 必須修正 | SM-1 | checkpoint 欄「無」，與驗收總則「SM-1/2 抽測脚本化」自相矛盾——觸發保證是 EP 成敗指標卻無機械驗法 | SM-1 補 N≥10 情境 probe 語句→rg spine＋各池→命中率下界（≥80%） | implemented |
| 11 | 🟡 建議 | SM-6/SM-9 | matrix 與各段驗收欄映射不一致（SM-6 列 S2、SM-9 列 S5 但驗收欄缺） | SM-6→S1/S4、SM-9→S1/S5；S4/S5 驗收欄補列 | implemented |
| 12 | 🟡 建議 | UC 盤點 | hooks/（block-memory-index-write.py）未列——S1 寫入閘放寬與 SM-9 攔截都動它 | 已補列 | implemented |
| 13 | 🟡 建議 | S4/S5 | 生命週期承載者三處張力（instruction-* 承載 vs memory-audit 引擎 vs clean 工具）——引擎/工具職責邊界未釐清 | 定義：memory-audit＝引擎（四動判準/稽核方法論單一源）、instruction-clean 等＝執行工具——判準與執行分離，不另創 skill（決策 5 相容） | implemented |
| 14 | 🟡 建議 | S6 | agents/ registry（roles description＝dispatch 觸發面）未宣告 in/out-of-scope；spine 無候選載體與生成掛點（最薄段落） | S6 補 agents 文法對齊 in-scope（僅文法、registry 投影機制不動）＋spine 候選載體與掛點 | implemented |
| 15 | 🟡 建議 | Backlog 關聯 | draft-1/draft-2（telemetry 接線/探測，Draft 中）與 S4 掃描腿的依賴關係未交代 | 補依賴登記：S4 開工時吸收或宣告阻塞 | implemented |
| 16 | 🔴 必須修正 | 整合策略 | S0 致命假設（有無 desc-matching 召回）驗出「無」且 routing 紀律實測差時，全 EP 無 no-go 分支 | 補 no-go 處置（見整合策略新段） | implemented |
| 17 | 🔴 必須修正（confirmed） | S1/S6/SM-1 | rg 命中率以查詢已發生為前提，不能驗收 session 是否會主動觸發；P5 提供候選清單的 A/B 配對也不能補足 | 分開檢索測試與無提示任務行為 probe；go/no-go 使用後者，no-go 不自動改口徑放行 | implemented |
| 18 | 🔴 必須修正（evidence-based） | S3/SM-4/5 | S0 P3 的 untrusted 32,000 bytes、project 跳過未被 master 驗收承接 | trust 作為前置軸；trusted 驗 lane 總額，untrusted 顯式 degraded，不自動改 trust | implemented |
| 19 | 🟡 建議（confirmed） | 核心設計/S3/受影響載體 | 現有 deploy 僅三個非 Claude target，原文「四投放」及四端投影措辭混淆原生 rules 與 bundle | 依 user 澄清保留 Claude 原生 rules；三端 bundle 與 Claude 分別驗收，非要求 Claude 改走 bundle | implemented |
| 20 | 🟡 建議（confirmed） | 決策 10/S1/S5/SM-9 | 批准 B3/B5/B6/B8 不全符合固定「當你要…時」，且 B5 含引號；直接照規則建 lint 會拒絕批准样本 | 條件句不得窄化為單一固定前綴；禁引號與 B5 的取捨須確認，未裁定前不批次套用相衝突 lint | needs-confirmation |

## UC 盤點（docs mode：受影響命令/rules 清單）

### 受影響載體（重構對象）

| 載體 | 現況 | 弧內角色 |
|---|---|---|
| `skills/memory-audit/` | 寫入紀律＋兩級稽核單一源 | 擴充為生命週期引擎（四動）之一環 |
| `skills/instruction-writing/` | 28KB 文法權威 | 重構：吸收觸發 desc 文法（情境句領頭）＋層級判準 |
| `skills/instruction-init/` | bottom-up 體系生成 | 重構：新專案初始化對齊層級判準表＋座標系欄位 |
| `skills/instruction-clean/` | 元資訊清理＋distill | 重構：精煉/淘汰動作的承載體 |
| `skills/instruction-sync/` | md↔code 同步檢查 | 重構：掃描動作（新鮮度/跨 lane）承載體 |
| `scripts/deploy_agents.py` | 單 bundle 投放 ZCode/Codex/Muse 三端＋90KiB gate；Claude 走原生 rules | 非 Claude bundle 投影器（rank∩scope×per-target budget），不改 Claude CLAUDE.md |
| `hooks/block-memory-index-write.py` | 寫入閘（desc>100/body 上限） | S1 寫入閘放寬＋SM-9 desc 文法攔截 |
| `rules/context-management.md` | L37-39 memory 生命週期 pointer（六問/rank 初判/投影禁手寫/蒸餾觸發詞） | S1/S4 改寫對象；S5 引用面同步 |
| `rules/AGENTS.md`＋`rules/instruction-writing.md`＋`ai-development-guide.md` | 部署紀律/文法/總覽 | S3/S5 隨機制改寫 |
| 各 repo project AGENTS.md | ai-rules 12.5K／mosaic 42.7K／code-reality 18.5K／muse-plugin-cc 7.4K | 層級軸重整對象（S3，mosaic 為主案） |

命令面：`/memory-audit`（兩級稽核）、`instruction-clean`/`instruction-sync`/`instruction-init` 指令、夜間收斂 cron（掃描腿）、`uv run python scripts/deploy_agents.py`（投影）——多數隨 S4/S5 改版同步。

### Backlog 關聯

- `backlog/drafts/draft-3`（muse 64KiB 兩案裁決）——**吸收進 S3**（座標系溶解 A/B；S3 結案時 draft 標已吸收）
- `backlog/drafts/draft-1`（codex telemetry 源接線）／`draft-2`（muse+grok 記錄面探測）——**依賴登記**：S4 掃描腿消費 telemetry 源，S4 開工時吸收或宣告阻塞；非本 EP 直接吸收
- 歷史先例（已結，勿重做）：AIR-40/41/42（memory 治理三連）、AIR-43（vocab 治理）、AIR-25（CC 對齊）
- 自動建卡：本 EP 一張追蹤卡（AIR-45，blueprint）；子 EP 開工時逐段建卡

### 同主題 memory 條目（結案蒸餾範圍）

- `project_memory-governance-air40-42`（治理線終態——S4 擴充時蒸）
- `reference_memory-index-load-truncation`（200 行/25K 截斷——S1 的事實基礎）
- `feedback_inflow-needs-outflow`／`feedback_memory-failsoft-importance-ordering`（寫入哲學——保留項的依據）
- `reference_muse-code-cli-facts`／`project_muse-memory-mechanism-divergence`（64KiB lane＋muse memory 三 scope——S0/S3 事實基礎）
- `project_memory-desc-loop-posture-pending`（姿態句待裁——本弧 S1 顺帶裁）
- `reference_zcode-platform-facts`（rg 制無 semantic recall——S0 probe 覆核）

### SYSTEM-MAP 影響

無 SYSTEM-MAP.md（元專案，正當跳過）。

## Scenario Matrix（docs 語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應段落 |
|---|------|------|---------|------------|---------|
| SM-1 | 新 session 需要跨域事實（如 muse bridge 旗標） | 只提供自然任務，不提示查 memory、條目名稱或答案 | 自主啟動 routing → 讀正確 body → 在相關動作前採用約束；S1 驗單池，S6 再驗跨池 | 檢索測試保留 N≥10、≥80% 作 findability 指標；另以預先凍結的任務/答案、真實載入切片及工具軌跡計 trigger/read/use，含無關負例、同義改寫、切片外條目與 compact 後接續。S1 開工先定行為門檻，必中案例不得漏；P5 配對成績不抵此門 | S1/S6 |
| SM-2 | 必中類知識（commit consent、fail-loud） | session 存在 | 非 Claude 三端經 bundle；Claude 經原生 rules；必要內容在各自實際載入面到達 | 每端載入面正例＋非 Claude rank/scope 排除負例；檔案 rg 與 session 載入證據分列 | S3 |
| SM-3 | 池成長至 200+ 條 | 新增條目 | 載入切片尺寸不變（cold 不付預載稅） | 切片 wc 上下界 | S1 |
| SM-4 | muse task 於 ai-rules workspace | 先確認 workspace trust，再按該狀態驗 lane | trusted：user floor＋project＋實際 framing ≤65,536，rendered_bytes 與 text_bytes 對帳且 user/project 關鍵內容到達；untrusted：依 S0 P3 的 32,000 cap／project 跳過驗出 degraded，不冒充全載通過 | 部署後 probe，記 trust/source 數、rendered_bytes、text_bytes 與內容錨點；不自動修改 trust | S3 |
| SM-5 | mosaic 場景（project 42.7K） | ZCode 兩檔預算／muse 單 lane，muse 納入 trust 軸 | ZCode 端全載；muse trusted 驗重分配後完整載入，untrusted 或預算不足顯式 degraded 並阻止宣稱 project 約束全載 | 層級判準表＋部署後 probe；完整性不以處置文件代驗 | S3 |
| SM-6 | 同教訓第二次出現 | 二次命中 | rank 晉升進切片（觀測或回報腿） | rank diff 記錄 | S1/S4 |
| SM-7 | 條目過時 | 掃描（audit/telemetry） | 列淘汰/精煉候選→處置（retire 有證據門檻） | 清單+處置記錄 | S4 |
| SM-8 | 新專案 init | instruction-init | 產出體系符合層級判準表＋觸發 desc 文法＋座標欄位 | init 產物 lint | S5 |
| SM-9 | desc 違反文法（非情境句領頭/弧 id 領頭） | 寫入/修改條目 | lint/hook 擋（文法機械可驗部分） | hook 攔截記錄 | S1/S5 |

## 段落劃分原則

垂直切片：S0（事實補齊）→ S1（單 lane pilot 驗機制）→ S2（座標系上 rules）→ S3（投影＋層級，吸收 draft-3）→ S4（生命週期）→ S5（skill 家族重構）→ S6（跨 lane 對齊＋spine）。S1 完成＝機制 go/no-go 門；S3/S5 可部分平行；每段衍生 implementation 子 EP（標 `parent:` 本檔路徑）。

## 段落（blueprint 藍圖層）

### S0：前置研究與 probe（致命假設先驗）
做什麼：①ZCode/CC 召回機制 probe（desc-matching 注入有無——探針 session＋db 遺測）；②OpenCode AGENTS.md cap 驗證；③muse mosaic 級 project 鏈行為（42.7K 場景）；④mosaic root AGENTS.md 內容盤點（42.7KB 組成分析：多少屬必中集/多少該下沉目錄層/多少該走觸發）；⑤**desc 用語樣本**——挑 10 條熱 memory 條目改寫「情境句領頭」形態，交 user 校準用語風格（文法是設計靈魂，user 拍板後機械化）；⑥codex knob runtime 認證（`project_doc_max_bytes=102400` TOML 過≠runtime 認——新 session 覆述 bundle 尾端 sentinel）。產出：probe 報告＋用語風格定案＋mosaic root 組成分析。依賴：無。吸收：無。→ 衍生子 EP（可與 S1 前半合併）。

### S1：memory 讀取路徑 pilot（routing table）
做什麼：MEMORY.md 改三段式（①觸發地圖～15 行②hot/core 條目行③指向 `_inventory.md` 全量投影不載入）；generator 改造（routing 段生成＋inventory 分離＋desc 文法 lint——S0 定案後規則化）；rank 語義改「觀測晉升」（telemetry 腿＋回報腿）；寫入閘放寬設計（cold 免稅後六問的尺寸焦慮面卸除）。依賴：S0④⑤。吸收：`project_memory-desc-loop-posture-pending`（姿態句順帶裁）。驗收：SM-1/3/6/9。→ 子 EP。

**Review 承接（17/20）**：S1 子 EP 在改造前凍結 SM-1 的行為 probe 與門檻；單池即可驗 routing，不依賴 S6 尚未建立的 spine。檢索命中率、主動觸發率、正確 body 讀取與採用分列，無關任務亦記誤觸發與載入成本。S0 P5 僅支援文法選擇，不算此 gate 已過。情境句領頭涵蓋批准樣本的不同句式，不直接縮成 `^當你要`。**⚠️ 待確認：禁引號與 B5 的指令引句相衝突；需選「保留禁引號、改 B5 表達」或「禁令僅限實證引句、允許指令引句」；未裁定前不批次套用此拒寫條件。**其餘已定案條款保留。

### S2：座標系擴充——rules/skills 條目化
做什麼：rules frontmatter 增 rank＋觸發 desc 欄位（harness-scope 已在場——兩軸合體）；16 條 rule 逐條條目化改寫（desc 情境句化、rank 初判、on-demand 級內容確認下沉 skill）；floor 預算重定（目標 user floor ~25-35KB 量級，結構必然非手工瘦身）。依賴：S1 文法定案。驗收：抽查 desc 文法全綠＋floor 尺寸落地。→ 子 EP。

### S3：投影器與層級軸優化（吸收 draft-3）
做什麼：deploy_agents.py → 投影器（bundle=rank≤core∩scope 投影；per-target budget gate：muse user-floor ≤50KB 硬（**lane 總額制**：floor＋workspace project＋framing ≤65,536——ai-rules 工作區 floor 上限實算 ≈51.9KB，gate 取 50KB 留 framing 餘裕，防「gate 綠但 SM-4 紅」）＋codex 100K 軟（knob 已調，runtime 認證見 S0⑥）＋zcode 100K 硬＋opencode 依 S0②）；**user floor 收斂**＋**各 repo project 層重整**（層級判準表：user 必中集／project 特定／觸發層——mosaic root 42.7KB 為主案：依 S0④組成分析重分配至目錄層/觸發層）；muse lane 預算分配機制（user-first 串接下 project 保底策略；mosaic 級場景顯式處置）；**mosaic 肢跨 repo——由 mosaic 側 session 執行（工單路由，ai-rules EP 只出判準表與驗收），user 可改指 owning session**；部署驗證探針（SM-2/4/5）。依賴：S2。吸收：draft-3（結案）。→ 子 EP。

**Review 承接（18/19）**：部署面明列 ZCode/Codex/Muse 三個 bundle target；Claude 原生 rules 另行抽驗，bundle deploy 不改其 CLAUDE.md，不以三端投影成功代驗 Claude。Muse 子 EP 必須消費 S0 P3 的 trust 分支與 SM-4/5：以實際 framing/source 集合對帳，50KB 僅是 trusted ai-rules 場景的保守 user 上限，不是所有 workspace 的完整性保證。untrusted、project 省略或超額均記 degraded／不支援完整載入，禁止冒充 SM-2/4/5 通過；任何 trust 變更另依使用者授權。S0 P2 runtime 未驗證不可推成 OpenCode 無上限；OpenCode 若納入部署先在子 EP 明示新增 target 範圍及驗收，未納入時不計入既有四端完成宣稱。

### S4：生命週期統一（掃描/歸類/精煉/淘汰）
做什麼：四動語義定義與掛點——掃描（audit×telemetry 跨 lane 擴充：memory/rules/skills 一致的過時判準）、歸類（cluster＋promotion：memory→skill/rule 固化慣例一般化為座標系內晉升，含「犯兩次才 codify」原則化）、精煉（distill 管線統一：mem-distill 模式擴至 rule/skill 條目）、淘汰（retire 證據門檻＋退出記錄）；memory-audit 擴充為生命週期**引擎**（四動判準/稽核方法論單一源——名稱/職責重整；執行工具見 S5）。依賴：S1/S2。驗收：SM-6/7＋四動各有機械產物。→ 子 EP。

### S5：instruction-* skill 家族重構
做什麼：四 skill 對齊統一機制——writing=寫入文法權威（吸收觸發 desc 文法＋層級判準表＋座標欄位規範；28KB 瘦身重構）；init=新專案載體初始化（依層級判準表產 user/project/目錄層骨架＋座標欄位）；clean=精煉/淘汰工具（吸收 S4 動作）；sync=掃描/新鮮度（跨 lane 投影新鮮度，deploy_bundle_freshness 模式一般化；執行 S4 引擎定義的動作）。引用面同步：rules/instruction-writing.md、rules/context-management.md、rules/AGENTS.md、ai-development-guide.md、skills/CLAUDE.md。依賴：S2/S4。驗收：SM-8/9＋引用面 rg 零殘留。→ 子 EP。

### S6：觸發面對齊與 spine
做什麼：skills catalog desc 文法對齊（觸發詞任務語境化——不物理合併 harvest 機制）；**agents/ registry 的 roles description 納入文法對齊範圍**（description 也是 dispatch 觸發面——僅文法對齊，registry 投影生成機制不動）；跨專案 spine 實體（**候選載體**：CC/ZCode 共用池兄弟目錄或 `~/.agents/memory-spine/`——plain md、條目用 memory pool 同格式 frontmatter；**生成掛點**：各池 generator 認養 routing 行段，spine 條目由 ai-rules 側 session 寫入）＋各池/各 repo routing 行（「碰 muse/codex/bridge → rg spine」）；跨 harness 投影確認（CC symlink 面、muse read-only、codex auto-memory 不碰）。依賴：S1-S5。驗收：SM-1 跨池場景＋spine 路由行在場。→ 子 EP。

**Review 承接（17/20）**：S5 的 writing 文法與 S1 lint 使用同一組已裁定正負樣本，SM-9 不接受「批准樣本被擋但 regex 通過」；S6 在真實 catalog 載入面重跑 SM-1 跨池版本，納入 S0 P6 觀察到的 desc 縮短情境。Claude symlink 面驗原生 rules/skills 可達性，不宣稱它經過 bundle rank 投影。

## 整合策略

- **staging**：S0→S1（go/no-go 門：routing 紀律實測）→S2→S3→S4→S5→S6（S5 writing/init 可與 S3 部分平行；clean/sync 須隨 S4 後——S5 依賴 S2/S4 不可整段提前）
- **跨 session**：每子 EP 獨立 /implement；本檔攜 baseline 與已決策，子 EP 標 `parent: ai-analysis/_tasks/09-08-context-lifecycle-unification/ep.md`
- **驗收總則**：觸發保證量測（SM-1/2 抽測脚本化）；floor 預算與池成長脫鉤（SM-3）；四端載入面機械驗證（SM-2/4/5 的部署後探針）
- **回滾面**：不用向後相容（user 定調）——但 S1/S3/S5 各留「投影前快照」（舊 MEMORY.md/bundle 形態/SKILL.md 原檔進任務家 version 目錄），災害時可回看
- **S1 no-go 處置**（致命假設驗出「無 desc-matching 召回」且 routing 紀律實測差時）：①floor 擴權——切片放寬至 core 全量（觸發保證改由 floor 覆蓋率承載）；②驗收基準降級——SM-1 從「紀律觸發」改「floor 覆蓋率」並明記於收尾報告；③止損範圍——S2+ 的條目化投資不受影響（floor 投影本就吃座標系），僅查詢紀律的預期報酬下修。no-go 判定權在 user（S1 收尾時攤數據裁定）

**Review 限定（17）**：上述三項是提交 user 的替代方案，不是自動放行流程。S1 原案已含 hot/core，提議「core 全量」時須列出相較原案實際增加的集合、各端預算及仍未覆蓋案例；集合未增不得稱為兜底。未達事先凍結的行為門檻時，保留 no-go 並由 user 裁定是否修改目標與驗收；floor 覆蓋率不能冒充原觸發 gate。任何擴權仍須滿足各端實際載入預算。

## 收尾步驟

1. 追蹤卡結案兩步＋弧結案蒸餾（範圍=UC 盤點所列 memory 條目）
2. skills/CLAUDE.md 工作流索引同步（instruction-* description 變更）
3. draft-3 標已吸收（S3 內）
4. 受影響命令/rules 行為已反映＋consistency
5. 殼（index.html）badge 與實作章節隨各子 EP 推進掛鉤
