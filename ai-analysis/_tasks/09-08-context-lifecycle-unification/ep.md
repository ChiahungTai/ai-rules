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
- **投影式讀取**：rank≤core ∩ scope → 投影進 always-on floor（AGENTS.md bundle 變投影產物；觸發剛性=必中類由 floor 承載）；其餘 → routing 索引＋rg 查詢紀律。
- **層級軸**：user floor（跨 repo 必中集）／project 層（repo 特定＋目錄分層，mosaic 52 檔為正面標本）／觸發層（其餘）——三層判準表 + per-harness 預算互動（muse 單 lane 串接 vs ZCode 兩檔獨立預算 vs codex chain cap）。
- **生命週期四動**：掃描（audit/telemetry 跨 lane）→ 歸類（cluster＋promotion：memory→skill/rule 固化既有慣例一般化）→ 精煉（distill 管線）→ 淘汰（retire 流程）——由重構後的 instruction-* skill 家族承載。

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

## 段落 0：全域研究摘要（既有材料收編＋缺口）

**已到手材料**（子 EP 直接引用，不重做）：

- 兩份 codex 報告：`ai-analysis/reports/2026-09-08-codex-agents-md-usage-and-insights.md`（五層互補、keep it small、犯兩次才 codify、層級倒置診斷、官方三處方）、`2026-09-08-codex-philosophy-instruction-layering.md`（四家截斷地景表、muse 64KiB 機械證據、codex knob 已調、驗收探針）
- flash agent 逐字研究：`.agent-tmp/codex-context-research.md`（351 行，AGENTS.md 官方語義/九項 context pattern/巨型單檔反面證據 7 條——**子 EP 開工前先複製進任務家**，.agent-tmp 會被清）
- 本 session 實測：muse rules_file lane 串接語義（user+project 共享 64KiB、produced≠檔案、UTF-8 backoff）、memory 池統計（136 條、21,760/25,000 字元）、ZCode 純 markdown＋rg 制無 semantic recall（平台事實）
- mosaic 結構：root 42,740B＋52 個目錄分層 AGENTS.md（3 worktree 同 repo）
- instruction-* 現況：writing 28,043B（文法權威）／init 12,389B（bottom-up 體系生成、Truth-Anchored）／clean 8,036B（元資訊清理＋distill）／sync 6,253B（md↔code 同步檢查）

**可複用基礎設施**：`_generate_index.py`（投影器雛形）、PreToolUse hooks（寫入閘：desc/body 上限）、`memory_telemetry.py`（Read 觀測，rank 晉升訊號源）、`deploy_agents.py`（scope 過濾＋gate，S3 投影器底座）、memory-audit 兩級稽核（生命週期引擎雛形）、harness-scope frontmatter（座標軸一半已在場）、rank 欄位（另一半已在場）。

**風險假設**（等級→驗證段落）：

| 假設 | 等級 | 驗證 |
|---|---|---|
| ZCode/CC 有無 desc-matching 召回注入（system-reminder 觀測到 recalled memories 形態） | **致命**（決定觸發面投資報酬率） | S0 probe |
| muse 場景 mosaic 級 project 鏈（42.7KB）任何 user floor 都裝不下單 64KiB lane | 高 | S0 研究＋S3 層級策略 |
| generator 升級為全系統投影器後的 bug 半徑擴大 | 高 | S2 起測試護權（test_memory_lifecycle 模式擴充） |
| rank 晉升靠 Read telemetry，索引行「被看見」不可觀測 | 中 | S2 設計（user/session 回報腿） |
| instruction-writing 28KB 重構量與既有引用面（rules/instruction-writing.md pointer 等） | 中 | S5 引用面掃描 |

## UC 盤點（docs mode：受影響命令/rules 清單）

### 受影響載體（重構對象）

| 載體 | 現況 | 弧內角色 |
|---|---|---|
| `skills/memory-audit/` | 寫入紀律＋兩級稽核單一源 | 擴充為生命週期引擎（四動）之一環 |
| `skills/instruction-writing/` | 28KB 文法權威 | 重構：吸收觸發 desc 文法（情境句領頭）＋層級判準 |
| `skills/instruction-init/` | bottom-up 體系生成 | 重構：新專案初始化對齊層級判準表＋座標系欄位 |
| `skills/instruction-clean/` | 元資訊清理＋distill | 重構：精煉/淘汰動作的承載體 |
| `skills/instruction-sync/` | md↔code 同步檢查 | 重構：掃描動作（新鮮度/跨 lane）承載體 |
| `scripts/deploy_agents.py` | 單 bundle 四投放＋90KiB gate | 退化為投影器（rank∩scope×per-target budget） |
| `rules/AGENTS.md`＋`rules/instruction-writing.md`＋`ai-development-guide.md` | 部署紀律/文法/總覽 | S3/S5 隨機制改寫 |
| 各 repo project AGENTS.md | ai-rules 12.5K／mosaic 42.7K／code-reality 18.5K／muse-plugin-cc 7.4K | 層級軸重整對象（S3，mosaic 為主案） |

### Backlog 關聯

- `backlog/drafts/draft-3`（muse 64KiB 兩案裁決）——**吸收進 S3**（座標系溶解 A/B；S3 結案時 draft 標已吸收）
- 歷史先例（已結，勿重做）：AIR-40/41/42（memory 治理三連）、AIR-43（vocab 治理）、AIR-25（CC 對齊）
- 自動建卡：本 EP 一張追蹤卡（blueprint）；子 EP 開工時逐段建卡

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
| SM-1 | 新 session 需要跨域事實（如 muse bridge 旗標） | routing 地圖行命中情境詞 | rg spine/池 → 條目命中（findability） | 無 | S1/S6 |
| SM-2 | 必中類知識（commit consent、fail-loud） | session 存在 | floor 恆在場——四 harness 投影後各自載入面皆含 | 每端 rg 抽查 | S3 |
| SM-3 | 池成長至 200+ 條 | 新增條目 | 載入切片尺寸不變（cold 不付預載稅） | 切片 wc 上下界 | S1 |
| SM-4 | muse task 於 ai-rules workspace | 64KiB 單 lane 串接 | user floor 投影＋project 12.5K＋framing ≤65,536（部署後 text_bytes==produced） | 部署後 probe | S3 |
| SM-5 | mosaic 場景（project 42.7K） | ZCode 兩檔預算／muse 單 lane | ZCode 端全載；muse 端層級策略有顯式處置（非靜默截斷） | 層級判準表＋muse 處置文件化 | S3 |
| SM-6 | 同教訓第二次出現 | 二次命中 | rank 晉升進切片（觀測或回報腿） | rank diff 記錄 | S2/S4 |
| SM-7 | 條目過時 | 掃描（audit/telemetry） | 列淘汰/精煉候選→處置（retire 有證據門檻） | 清單+處置記錄 | S4 |
| SM-8 | 新專案 init | instruction-init | 產出體系符合層級判準表＋觸發 desc 文法＋座標欄位 | init 產物 lint | S5 |
| SM-9 | desc 違反文法（非情境句領頭/弧 id 領頭） | 寫入/修改條目 | lint/hook 擋（文法機械可驗部分） | hook 攔截記錄 | S1/S5 |

## 段落劃分原則

垂直切片：S0（事實補齊）→ S1（單 lane pilot 驗機制）→ S2（座標系上 rules）→ S3（投影＋層級，吸收 draft-3）→ S4（生命週期）→ S5（skill 家族重構）→ S6（跨 lane 對齊＋spine）。S1 完成＝機制 go/no-go 門；S3/S5 可部分平行；每段衍生 implementation 子 EP（標 `parent:` 本檔路徑）。

## 段落（blueprint 藍圖層）

### S0：前置研究與 probe（致命假設先驗）
做什麼：①ZCode/CC 召回機制 probe（desc-matching 注入有無——探針 session＋db 遺測）；②OpenCode AGENTS.md cap 驗證；③muse mosaic 級 project 鏈行為（42.7K 場景）；④mosaic root AGENTS.md 內容盤點（42.7KB 組成分析：多少屬必中集/多少該下沉目錄層/多少該走觸發）；⑤**desc 用語樣本**——挑 10 條熱 memory 條目改寫「情境句領頭」形態，交 user 校準用語風格（文法是設計靈魂，user 拍板後機械化）。產出：probe 報告＋用語風格定案＋mosaic root 組成分析。依賴：無。吸收：無。→ 衍生子 EP（可與 S1 前半合併）。

### S1：memory 讀取路徑 pilot（routing table）
做什麼：MEMORY.md 改三段式（①觸發地圖～15 行②hot/core 條目行③指向 `_inventory.md` 全量投影不載入）；generator 改造（routing 段生成＋inventory 分離＋desc 文法 lint——S0 定案後規則化）；rank 語義改「觀測晉升」（telemetry 腿＋回報腿）；寫入閘放寬設計（cold 免稅後六問的尺寸焦慮面卸除）。依賴：S0④⑤。吸收：`project_memory-desc-loop-posture-pending`（姿態句順帶裁）。驗收：SM-1/3/6/9。→ 子 EP。

### S2：座標系擴充——rules/skills 條目化
做什麼：rules frontmatter 增 rank＋觸發 desc 欄位（harness-scope 已在場——兩軸合體）；16 條 rule 逐條條目化改寫（desc 情境句化、rank 初判、on-demand 級內容確認下沉 skill）；floor 預算重定（目標 user floor ~25-35KB 量級，結構必然非手工瘦身）。依賴：S1 文法定案。驗收：抽查 desc 文法全綠＋floor 尺寸落地。→ 子 EP。

### S3：投影器與層級軸優化（吸收 draft-3）
做什麼：deploy_agents.py → 投影器（bundle=rank≤core∩scope 投影；per-target budget gate：muse 60KiB 硬＋codex 100K 軟＋zcode 100K 硬＋opencode 依 S0②）；**user floor 收斂**＋**各 repo project 層重整**（層級判準表：user 必中集／project 特定／觸發層——mosaic root 42.7KB 為主案：依 S0④組成分析重分配至目錄層/觸發層）；muse lane 預算分配機制（user-first 串接下 project 保底策略；mosaic 級場景顯式處置）；部署驗證探針（SM-2/4/5）。依賴：S2。吸收：draft-3（結案）。→ 子 EP。

### S4：生命週期統一（掃描/歸類/精煉/淘汰）
做什麼：四動語義定義與掛點——掃描（audit×telemetry 跨 lane 擴充：memory/rules/skills 一致的過時判準）、歸類（cluster＋promotion：memory→skill/rule 固化慣例一般化為座標系內晉升，含「犯兩次才 codify」原則化）、精煉（distill 管線統一：mem-distill 模式擴至 rule/skill 條目）、淘汰（retire 證據門檻＋退出記錄）；memory-audit 擴充為生命週期引擎（名稱/職責重整）。依賴：S1/S2。驗收：SM-7＋四動各有機械產物。→ 子 EP。

### S5：instruction-* skill 家族重構
做什麼：四 skill 對齊統一機制——writing=寫入文法權威（吸收觸發 desc 文法＋層級判準表＋座標欄位規範；28KB 瘦身重構）；init=新專案載體初始化（依層級判準表產 user/project/目錄層骨架＋座標欄位）；clean=精煉/淘汰工具（吸收 S4 動作）；sync=掃描/新鮮度（跨 lane 投影新鮮度，deploy_bundle_freshness 模式一般化）。引用面同步：rules/instruction-writing.md、rules/AGENTS.md、ai-development-guide.md、skills/CLAUDE.md。依賴：S2/S4。驗收：SM-8＋引用面 rg 零殘留。→ 子 EP。

### S6：觸發面對齊與 spine
做什麼：skills catalog desc 文法對齊（觸發詞任務語境化——不物理合併 harvest 機制）；跨專案 spine 實體（user-global 一處：harness facts/tool traps/user 工作風格）＋各池/各 repo routing 行（「碰 muse/codex/bridge → rg spine」）；跨 harness 投影確認（CC symlink 面、muse read-only、codex auto-memory 不碰）。依賴：S1-S5。驗收：SM-1 跨池場景＋spine 路由行在場。→ 子 EP。

## 整合策略

- **staging**：S0→S1（go/no-go 門：routing 紀律實測）→S2→S3∥S5（可部分平行）→S4→S6
- **跨 session**：每子 EP 獨立 /implement；本檔攜 baseline 與已決策，子 EP 標 `parent: ai-analysis/_tasks/09-08-context-lifecycle-unification/ep.md`
- **驗收總則**：觸發保證量測（SM-1/2 抽測脚本化）；floor 預算與池成長脫鉤（SM-3）；四端載入面機械驗證（SM-2/4/5 的部署後探針）
- **回滾面**：不用向後相容（user 定調）——但 S1/S3 各留「投影前快照」（舊 MEMORY.md/bundle 形態進任務家 version 目錄），災害時可回看

## 收尾步驟

1. 追蹤卡結案兩步＋弧結案蒸餾（範圍=UC 盤點所列 memory 條目）
2. skills/CLAUDE.md 工作流索引同步（instruction-* description 變更）
3. draft-3 標已吸收（S3 內）
4. 受影響命令/rules 行為已反映＋consistency
5. 殼（index.html）badge 與實作章節隨各子 EP 推進掛鉤
