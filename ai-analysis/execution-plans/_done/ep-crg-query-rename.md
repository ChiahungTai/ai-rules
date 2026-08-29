# EP: crg-query skill 改名 cr-query

> **ep_type**: implementation
> **mode**: docs mode（變更全為 `.md`＋目錄 `git mv`＋**一行 `settings.json` config**〔F1——`Skill(crg-query)` allowlist 同步〕；零 `.py` 符號）
> baseline: fced4f3（build 起點若 HEAD 已前移，以當下 `git rev-parse HEAD` 為準補記）
> **前置 gate（硬性）**：`git status` 中 `skills/crg-query/SKILL.md` 須乾淨——並行 session 現有該檔在製品（pyrefly class 節點過渡警告＋semantic_search 單關鍵詞形態），未落地前不得動工（single-writer 紀律）。**動工時＋commit 前雙重檢查**（TOCTOU 窗口：gate 通過後並行改動才落地的交錯防護——F5；交錯發生時 git 會以衝突顯性暴露，停下重對時序）

## EP Review Findings

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| F-1 | 🔴 | S1/掃描範圍 | `settings.json:18` `"Skill(crg-query)"` permissions allowlist 在掃描範圍外——改名後懸空、新名呼叫觸權限提示 | S1 補同步＋掃描範圍加 root `*.json` | implemented |
| F-2 | 🟡 | S1 白名單 | `ai-analysis/specs/code-reality-repo-mcp-spec.md:99` 命中——白名單缺 specs/，步驟 4 首跑即敗 | 白名單補 `ai-analysis/specs/`（歷史規格快照） | implemented |
| F-3 | 🟡 | S1 白名單 | live EP 自身含 crg-query——歸檔前掃描命中自己 | 白名單補 live EP 自指 | implemented |
| F-4 | 🟡 | 負空間 | 「hooks 由兩家 config 引用」不精確——實測僅 `~/.zcode/cli/config.json:78` 引用，Claude 端 settings.json 無 hook 引用 | 事實陳述修正（裁定不變，hook 不動反而更便宜） | implemented |
| F-5 | 🟡 | 前置 gate | gate 是時間點檢查，缺 TOCTOU 場景（通過後並行才落地） | 動工時＋commit 前雙重檢查＋SM-6 | implemented |
| F-6 | 🟢 | 動機句/S2 | 「最後一個掛 CRG 名」略過度（hook 檔名＋agents/AGENTS.md CRG 教訓語義仍在）；S2 未明說消費端歷史文件處置 | 措辭軟化＋S2 補一句 | implemented |

審查者獨立盤點：範圍內 11 檔與 EP 清單逐檔一致零漏；新名 `cr-query` 全 repo 無佔位衝突；三處 skills 載入點皆目錄級 symlink（「git mv 即時生效」屆實）；消費端實測＝mosaic 三 wt `CLAUDE.md:12` 活性引用、NT/codetour 零命中。

## 研究摘要（段落 0）

**動機**：`crg-query` 是 skill 體系中最後一個掛 CRG 名的命名殘留（CRG MCP 已於 2026-08-26 退役、`b067cfc` 完成內容面殘留清零）——內容早已是 code-reality engine 的查詢紀律層，名不副實且傷 discoverability（未來 session 找「code-reality 查詢紀律」不會搜 "crg"；hook 檔名與既有文檔的 CRG 歷史語義依負空間保留）。

**角色定位（不變）**：查詢紀律層（一條規則 graph=structure≠behavior、GATE assume＋warn、repo_root 規則、LSP-vs-CR 分工、anti-over-reliance）——與 code-reality skill（工具程序層）、CR plugin skill ≥0.1.6（工具事實/坑）三層分治，本 EP 只改名不重組。

**引用面（08-29 rg 實測＋審查獨立複掃，build 時重掃為準）**：12 處——`skills/crg-query/`（本體）、10 個 `.md` 引用檔（`skills/CLAUDE.md` 索引、code-review、smell-detector×2、corpus-recall、implement、execution-plan、arch-thinking、review-engine、`_common/illustrate-artifact-menu.md`）、**`settings.json:18`（`"Skill(crg-query)"` permissions allowlist——功能性 config 引用，F1）**。`rules/`、root `AGENTS.md`、root `CLAUDE.md`/`STATE.md`、`agents/`、`scripts/`、部署 bundle 零命中（審查者範圍外補掃屆實）。

**部署形態**：skills 走目錄 symlink（`~/.zcode/skills`、`~/.agents/skills` 等 → repo `skills/`）——`git mv` 即時生效；skill 清單為 per-session 快照，新 session 才看得到新名。

**負空間（明確不做）**：
- **`hooks/require-crg-repo-root.py` 檔名不改**——hook 由 `~/.zcode/cli/config.json` 絕對路徑引用（Claude 端 settings.json 實測無 hook 引用——F-4；改名只需動一處 config），但 hook 是內部工件、discoverability 無痛，不動反而最便宜；未來要清另開卡
- **歷史文件不改**：`_done/` EP、`ai-analysis/reports/`、**`ai-analysis/specs/`**（F-2——歷史規格快照）、memory 歷史段的 crg-query 字串屬快照語義（當時事實），不在同步範圍——僅 memory「現況指引」段落的活性引用同步
- skill 內容不重寫（frontmatter `name` 與自清句除外）

**風險假設**：A1（低）——git mv 後 symlink 載入正常（同 registry split 已驗證的模式）；A2（低）——引用掃描漏網（對策：S1 機械雙掃＋大小寫變體）。

## UC 盤點（docs mode：受影響清單）

### 掃描範圍
`rg -ln "crg-query" rules/ skills/ AGENTS.md hooks/ ai-analysis/`（含大小寫變體 `Crg|CRG-query`）＋消費端 repo 掃描（S2）。

### 既有 UC 狀態

| 能力 | 狀態 | 影響 |
|------|------|------|
| code-reality 查詢紀律（crg-query skill） | ✅ | 更新——僅改名，能力描述與入口路徑不變 |

### 新增 UC
無（純改名）。

## Scenario Matrix（docs mode 文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應 |
|---|------|------|---------|------------|------|
| SM-1 | 改名後引用全通 | S1 完成後掃描 | `rg -ln "crg-query"` 全 repo 僅剩允許殘留（hooks 檔名＋歷史文件）；`rg -ln "cr-query"` 覆蓋原 10 檔 | 無 | 引用同步 |
| SM-2 | 並行 session 在製品未落地 | 前置 gate 檢查失敗 | 阻塞動工、回報等待（不硬闖寫衝突） | 無 | 前置 gate |
| SM-3 | 殘留舊名引用（漏改） | 未來 session 依文字導航 | 舊名在 skill 清單不存在 → 導航 miss 被發現 → 補改；機械對策＝SM-1 掃描零漏 | 無 | 引用同步 |
| SM-4 | 新 session 清單驗證 | 改名後首個新 session | skill 清單出現 `cr-query`、無 `crg-query` | 無 | 部署 |
| SM-5 | 消費端 instruction 檔引用舊名 | S2 掃描命中 | 產 handoff（path:line＋proposed patch）交付所屬 session——ai-rules session 不直接改他 repo | 無 | 消費端 handoff |
| SM-6 | TOCTOU 交錯窗口 | gate 通過後並行 session 才落地其 crg-query 改動 | 動工時＋commit 前雙重檢查 `git status` 該檔；交錯落地時 git 以衝突顯性暴露→停下重對時序 | 無 | 前置 gate |

## 段落劃分原則

S1（改名＋repo 內同步）→ S2（消費端 handoff＋memory）→ S3（收尾驗證）。序列剛性：S1 先行（名字先落地）；S2 依賴 S1 的新名；S3 驗證前兩者。

---

## S1: 改名執行＋repo 內引用同步

### Context

**背景**：名實對齊——內容已是 code-reality 紀律層，名字是最後的 CRG 殘留。

**依賴錨點**：
- 本體：`skills/crg-query/SKILL.md`（frontmatter `name: crg-query`＋description 首句自清句）
- 引用端（rg 實測 10 檔，build 時重掃——**必含大小寫變體與 `crg` 單獨出現的導航語境**）
- 索引：`skills/CLAUDE.md` 的 crg-query 索引行（description 摘要同步）

**語義約束**：與 S2 共享——新名 `cr-query` 全域唯一（`rg -l "cr-query"` 先掃確認無既有衝突佔位）。

### 修改要點

1. `git mv skills/crg-query skills/cr-query`
2. SKILL.md frontmatter：`name: cr-query`；description 首句自清句改寫（保留「CRG retired」歷史註記一句即可）
3. 逐檔同步引用（文字 `crg-query` → `cr-query`；路徑 `../crg-query/SKILL.md` → `../cr-query/SKILL.md`；`skills/CLAUDE.md` 索引行同步）
3b. **MCP roster 名同步（搭車）**：crg-query 表格內的 MCP 工具名（`semantic_search`/`architecture_overview` 等）在 plugin ≥0.3.0 的 real roster 改名為 `search`/`arch_overview`（CR `1f602f2` 裁定＋pinned tests 已換）——S1 觸及同批表格，一併換成 real roster（真相源＝plugin skill ≥0.3.0 的工具清單；動工時以當時 plugin 版本為準）
4. **雙掃驗證**：`rg -ln "crg-query|Crg-query" <repo root 含 root *.json>`——允許殘留白名單：`hooks/require-crg-repo-root.py`（檔名＋其被 SKILL.md 引用的路徑文字保留）、`ai-analysis/execution-plans/_done/`、`ai-analysis/reports/`、`ai-analysis/specs/`、**live EP 本檔（歸檔前自指）**、git 歷史；其餘零命中
5. `rg -ln "cr-query"` 確認覆蓋原引用檔且無意外新命中
6. **`settings.json` 同步**：`"Skill(crg-query)"` → `"Skill(cr-query)"`（一行 JSON edit；改完 `python3 -m json.tool settings.json` 驗合法性）

### 驗證策略（docs mode）

- 雙掃（步驟 4/5）零漏——統計用 `| wc -l`，禁 `head` 截斷
- `ls ~/.zcode/skills/` 經 symlink 見 `cr-query/`（即時）
- 抽 3 個引用檔 Read 確認語境通順（非機械替換破句）

## S2: 消費端 handoff＋memory 同步

### Context

**背景**：消費端 repo（mosaic 三 wt／NT／cr／codetour）的 instruction 檔可能以文字引用 skill 舊名——ai-rules session 不直接改他 repo（雙向對稱紀律），handoff 交付。

**依賴錨點**：S1 新名已落地；handoff 載體＝本 EP 段落產出（清單＋patch）。

### 修改要點

1. `rg -ln "crg-query" ~/Github/mosaic_alpha* ~/Github/nautilus_trader ~/Github/code-reality ~/Github/codetour --glob '!target/**' --glob '!.git/**'`（排除 build 產物；**消費端自身 ai-analysis 歷史文件比照本 repo 負空間邏輯不改**，僅活性 instruction 檔入 handoff——審查實測：mosaic 三 wt `CLAUDE.md:12` 活性引用、NT/codetour 零命中）——命中清單＋逐處 path:line
2. 每命中產 proposed patch（一行文字替換）寫入 handoff 段（本檔附錄或獨立 handoff 檔，依命中量決定）
3. memory 池同步：`rg -l "crg-query" ~/.zcode/cli/memories/`——**僅改活性指引段**（現況敘述），歷史段（決策記錄帶時間戳語境）保留原名的，於該檔加一行導航註（「crg-query 已更名 cr-query」）

### 驗證策略

- handoff 清單與 rg 命中逐條對帳（數字一致）
- memory 改動後 `rg "crg-query"` 僅剩歷史語境命中

## S3: 收尾（gate＋結算）

### 修改要點

1. `/consistency`（獨立 agent 等價或 formal）抽查：`skills/cr-query/SKILL.md`＋`skills/CLAUDE.md`＋改動量最大的 2 個引用檔
2. kanban：本 EP 追蹤卡進 Done（含 SM-4 新 session 清單驗證待辦行）
3. `git add` 具名（排除並行 session 檔案）

### 驗證策略

- consistency 抽查 pass
- SM-4 留待下一個新 session：清單見 `cr-query` 無 `crg-query`——relay 一行給下個 session

## 整合策略

- 全序列剛性 S1→S2→S3；與並行 session 的互斥面＝`skills/crg-query/SKILL.md`（前置 gate）＋`skills/code-reality/SKILL.md`（本 EP 不碰）
- 回滾＝`git mv` 回＋引用反向同步（全可逆）

## 收尾步驟

1. docs mode 情境 D：EP 歸檔 `_done/`
2. `skills/CLAUDE.md` 索引（S1 已含）；root `AGENTS.md` 無引用（已驗）不動
3. /audit-test：無測試變更——跳過

> **build 結算（08-29 午）**：S1-S3 完成。動工時 gate 狀態＝`skills/crg-query/SKILL.md` 仍有並行 session 未 commit 內容（semantic_search 單關鍵詞永久註記一行——判定為已定稿，user 授權動工；TOCTOU 未發生）。執行：git mv＋frontmatter name/title＋**33 處 token 替換跨 11 檔**（計數斷言）＋`settings.json:18` allowlist 同步（json.tool 驗證）；雙掃殘留＝8 檔全在白名單類（reports/specs/_done/live EP），零活性殘留；`~/.zcode/skills` 目錄 symlink 即時見 `cr-query`。**偏差：S1 3b（MCP roster 名同步）暫緩**——直接 probe 安裝版 `code-reality-mcp --stdio` tools/list＝17 工具仍為舊名（`semantic_search`/`architecture_overview` 在場、無 `search`/`arch_overview`），現在改文檔名會與部署中 binary 脫鉤；3b 移交 plugin 0.3.0 落地軸（屆時 binary 重裝後以新 roster 對齊）。S2：消費端命中＝mosaic 三 wt `CLAUDE.md:12` 各一處（handoff 交付，ai-rules 不直接改他 repo）；memory 池 3 檔命中屬 CR 專案歷史敘述（負空間不改）。

> **post-build gate（08-29 午）**：consistency 5/5 PASS（0 🔴）。兩 🟡 記錄不動——①SKILL.md :87-93 Boundary 節現在式時態（內容修訂項，非改名範圍）；②smell-detector/baseline.md:84 `crg_facts` state.yaml 欄位名（序列化相容，刻意保留）。

> **3b 結案（08-29 晚，CR 回執推翻暫緩理由）**：**no-op**——MCP 面從未改名。`search`/`arch_overview` 是 CLI `graph_query` 的 op 名（graph_engine.rs task_suggestions 語境），battery 回執「router 為準」措辭未標面、被概化到 MCP 面造成假性暫緩。證據鏈：兩支 bin 同版 0.3.0+1f602f2→重裝 a1bce6b；`git log 1f602f2..HEAD -- src` 空；HEAD ToolRouter（mcp_server.rs:231-258）註冊 17 現名；probe 逐字吻合。cr-query 文檔的 MCP 工具名**本來就正確**（semantic_search/architecture_overview/list_communities…），零同步需求。兩面對照表（CLI op ↔ MCP tool）真相源留 CR plugin skill，本 EP 不複製。教訓：回執引用工具名必須標面別（CLI／MCP）。
