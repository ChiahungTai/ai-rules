# EP — tour corpus 治理：source 模型、derived/curated 更新機制與工具收編

> **ep_type**: implementation
> **跨 repo baseline**：ai-rules `002f7edd`／nautilus_trader `61590e4867`（＝NT corpus README 記錄的錨定 commit——**零漂移起點**）／mosaic（v2）`0c2a496c`
> **定位**：把 tour corpus 從「一次性 bootstrap 產物」升級為**可長期維護的衍生資產**——derived/curated 二分、manifest provenance、機械驗證收編 CLI、NT 認真 corpus 遷移新格式、test 作為新 source。設計推導全文見本 EP 前身的 session 深度分析（derived/curated 分類學、四源模型、LLM 三層經濟）。
> **並行宣告**：ai-rules 工作樹有 tour-bootstrap skill 未 commit 修改（受眾分支，本 session 產物，T1 疊加）；mosaic v2 有 35 檔 staged（bootstrap EP 產物，本 EP 僅追加 `.tours/manifest.toml` 一檔，不動 staging 群）；codetour repo 不在本 EP 範圍（其總覽 tour 已獨立完成）。

---

## 實作總覽

| 段 | 交付 | 一句話 | 產物（repo） |
|---|------|--------|------|
| T1 | skill 三模式 | tour-bootstrap skill 補 fresh／audit／migrate 重跑語義＋curated 保護鐵律 | `skills/tour-bootstrap/SKILL.md`（ai-rules，docs mode 段） |
| T2 | tour_validate CLI | 機械驗證收編（JSON／link 鍵／路徑／錨對齊／manifest source 存在）——本 session 已 ad-hoc 寫三次的腳本 | `code_reality/tour_validate.py`＋tests（ai-rules） |
| T3 | manifest 規格＋套用 | `.tours/manifest.toml`（provenance：source×generator×commit；audience）＋讀寫共用＋mosaic corpus 套用 | `code_reality/` 共用＋`.tours/manifest.toml`（mosaic） |
| T4 | NT 遷移 | tour_upgrade CLI（pattern 補全＋cross-ref 活化＋manifest）dry-run 預設；NT 30 條遷移＋進版控 | `code_reality/tour_upgrade.py`＋tests（ai-rules）＋`.tours/`（nautilus_trader） |
| T5 | test_tour generator | tests 作為 source：AST 枚舉 → test case tour 骨架（pattern 錨 `def test_*`＋`>> pytest` 可執行步） | `code_reality/test_tour.py`＋tests（ai-rules） |
| T6 | 更新接線 | post-build／tour-bootstrap skill 掛 audit；mosaic nightly-sequence 可選一行 | `skills/post-build/SKILL.md`＋`skills/tour-bootstrap/SKILL.md`＋mosaic `deploy/`（可選） |

依賴：T2 → T3（manifest 讀取）→ T4/T5/T6；T1 獨立。建議序 T1→T2→T3→T4→T5→T6（T4/T5 可並行）。

---

## UC 盤點

### Backlog 關聯
- ai-rules `.kanban/Backlog/`：本 EP 執行時建卡——`EP tour corpus 治理`（追蹤卡）＋`tour corpus 機械驗證與遷移`（T2/T3/T4）＋`test case tour 骨架`（T5）

### SYSTEM-MAP 影響
- ai-rules 無 SYSTEM-MAP.md——無更新

### 掃描範圍
- `~/Github/ai-rules/skills/code-reality/SKILL.md`（工具表=Capabilities 等價物）、`skills/tour-bootstrap/SKILL.md`、`tests/`（per-tool unit＋integration 慣例）、`.kanban/`

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| chain tour 產出（chain_tour） | ✅ | code-reality skill 工具表 | 更新 | T3 起寫 manifest provenance |
| delta tour 產出（delta_tour） | ✅ | 同上 | 無 | 不動（G4 自動化仍不在範圍） |
| snapshot／transition | ✅ | 同上 | 無 | |
| tour-bootstrap 程序（skill） | ✅ | skills/tour-bootstrap | **更新** | T1 補三模式＋curated 鐵律；T6 引用 tour_validate |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| tour corpus 機械驗證（validate） | 📋 | `code_reality/tour_validate.py` |
| tour corpus 舊格式遷移（upgrade） | 📋 | `code_reality/tour_upgrade.py` |
| test case → tour 骨架 | 📋 | `code_reality/test_tour.py` |
| corpus provenance manifest | 📋 | manifest 讀寫進 T2/T3 共用（能力歸驗證卡） |
| corpus 更新 audit 接線 | 📋 | skills 兩處＋mosaic 可選（能力歸 EP 追蹤卡） |

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | validate happy | 對 codetour `.tours/`（含總覽＋fixture）跑 tour_validate | 0 fails、輸出 per-tour 統計 | 無 | 驗證 |
| SM-2 | validate 抓漏 | 注入壞 JSON／死 link 鍵／漂移錨（fixture） | 對應 FAIL 行＋exit non-zero；修復後歸零 | fixture 還原 | 驗證 |
| SM-3 | validate 漂移錨 | 對「行號漂移但 pattern 命中他行」的步 | 報 corrected（非 fail）——與 player 四態語義一致 | 無 | 驗證 |
| SM-4 | manifest source 失蹤 | manifest 記的 source 檔被刪 | FAIL：source missing（結構腐化偵測） | 無 | manifest |
| SM-5 | NT 遷移 dry-run | tour_upgrade 對 NT 30 條 --dry-run | 每條報告：pattern 補全率、cross-ref 活化數、無法萃取的步清單；**不改任何檔** | 無 | 遷移 |
| SM-6 | NT 遷移 apply＋走讀 | apply 後 codetour 0.0.62 開 NT repo | cross-ref 點擊跳 tour（活 link）；pattern 錨 exact 佔比報告；01 條 isPrimary 冷啟動 | 走讀抽查 | 遷移 |
| SM-7 | test_tour 骨架 | 對 mosaic `tests/` 某子目錄跑 | 每 test 檔一條 tour、每 test 一步（`def test_*` pattern 錨＋`>> pytest path::test` 可執行前綴） | 無 | test 骨架 |
| SM-8 | 三模式保護 | 對有 curated tour 的 repo 跑 audit 模式 | 只產報告不改檔；對 derived tour 重產 diff 非空時標「升 curated」不覆蓋 | 無 | skill 三模式 |
| SM-9 | audit 接線 | repo 有 manifest 時 post-build 尾端 | 自動跑 tour_validate，FAIL 列入收尾報告 | 無 | 接線 |

---

## 段落 0：全域研究摘要

**可複用基礎設施**：
- `code_reality/chain_tour.py`——CLI 形態範本（`main()` argparse／`--repo`／`--out-dir` 預設 `.tours/arch/<stem>/`；writer `chain_tour.py:411-427`、main `:439`）；per-tool 測試慣例 `tests/test_<tool>.py`＋`test_<tool>_integration.py`
- 本 session 三案例實跑過的驗證腳本（mosaic／codetour／本 EP 撰寫時對 NT）＝T2 的行為藍本：TS `getTourTitle` 演算法（`codetour/src/utils.ts:37-43`）、`TOUR_REFERENCE_PATTERN`／`FILE_REFERENCE_PATTERN`（`codetour/src/player/index.ts:57-59`）、錨四態（`codetour/src/player/anchor.ts:103-146`）——**正則語義以 py `re` 重現，已在三 corpus 驗證等價**
- NT corpus 自帶遷移素材：`.tours/README.md` 記錄錨定 commit＋cross-ref 慣例（`[N - 名稱]` 純文字）；step description 內含符號線索（`class DataActor:`、`:731 def on_bar`、`pub struct ... {`）＝T4 pattern 萃取來源

**依賴與約束**：
- NT HEAD＝錨定 commit（零漂移）——T4 不需修漂移，純格式升級；上游 nightly 前進後 manifest 的 `anchored_commit` 語義才上場
- player 消費端已凍結在 codetour 0.0.62（同 ID 側載＋版號壓過 marketplace 0.0.61——上游復活教訓已處理）
- manifest 是跨 generator 共用契約：chain_tour／test_tour 寫入、tour_validate 消費——T3 先立 schema

**風險假設**：
- R1（中）：NT description 符號線索萃取 → pattern 的成功率未量化——若大量步驟無法生成 pattern，T4 降級為「能補的補、其餘 line-only 保留＋報告」（不阻塞）
- R2（低）：py re 與 JS RegExp 對中文／emoji title 的行為差異——三案例已實跑等價，殘餘風險在冷門逸出字元
- R3（低）：`>> pytest` 可執行步在 codetour fork 的 `SHELL_SCRIPT_PATTERN`（`src/player/index.ts:52`）仍在——上游 0.0.61 差異不影響本地側載版
- 無致命級假設（T2 行為已有三案例實證；T4 有 dry-run 保護）

---

## 段落 T1：skill 三模式（docs mode 段）

### Context
tour-bootstrap skill 目前只有「盤點」，對「repo 已有 corpus」的重跑語義未定義——用戶實測踩到（「目前其實有東西在，這時候該怎樣處理？」）。本段補三模式與保護鐵律。實作 [tour-bootstrap 程序] 之更新。

**依賴錨點**：`skills/tour-bootstrap/SKILL.md` 程序五步（當前版已含受眾分支＋delta 職責精煉——另一 session 已 commit 基礎，本段疊加）

### 核心實作要點
1. 新增「重跑語義（三模式）」段：**fresh**（無 corpus 或用戶明示重建）／**audit**（既有 corpus 跑 `tour_validate` 產報告，**不改檔**）／**migrate**（舊格式升級走 `tour_upgrade --dry-run` 先看報告）
2. 鐵律：**curated 內容不可盲目覆蓋**——derived tour 重產 diff 非空＝該條已被人改過，升級為 curated 只報 diff 不覆蓋
3. manifest 引用：步驟 1 盤點加「有 `.tours/manifest.toml` → 讀 audience 與 provenance」；產出後寫回 manifest
4. 模式判定：`.tours/` 無 tour→fresh；有 corpus 無 manifest→audit（提示 migrate 若格式舊）；有 manifest→audit 為預設

### 驗證策略（docs mode）
- rg 殘留（無「重跑」舊語義碎片）、與 T2/T4 CLI 名一字不差（single-source：skill 引用工具名，工具語義真相在 code-reality skill 工具表——本段同步該表加三工具列）
- `/consistency skills/tour-bootstrap/SKILL.md`

---

## 段落 T2：tour_validate CLI

### Context
機械驗證目前是 ad-hoc heredoc 腳本（本 session 對 mosaic／codetour／NT 各寫一次）——收編為 `code_reality` 工具，三案例＋未來 audit 接線（T6）共用。實作 [tour corpus 機械驗證]。

**依賴錨點**：
- 消費端語義源（唯讀參考，程式碼不 import）：`getTourTitle` → 定義 `codetour/src/utils.ts:37-43`；`TOUR_REFERENCE_PATTERN`/`FILE_REFERENCE_PATTERN` → `codetour/src/player/index.ts:57-59`；錨解析 → `codetour/src/player/anchor.ts:103-146`
- 形態範本：`code_reality/chain_tour.py:439`（main／argparse 慣例）
- 測試慣例：`tests/test_chain_tour.py`（unit）＋`test_chain_tour_integration.py`（真實輸入）

### 核心實作要點
1. CLI：`python -m code_reality.tour_validate --repo <repo> [--tours-dir .tours] [--manifest] [--format text|json]`
2. 檢查項（對 `--tours-dir` 遞迴全部 `.tour`）：
   - JSON parse 全檔
   - tour link：以 TS 演算法重現剝前綴（`^#?\d+\s-` → `split("-")[1].strip()`）算鍵；鍵唯一解析＋步號存在
   - file link（`(\.[^)]+)` 形式）路徑存在（相對 repo root）
   - 錨對齊：有 `line`+`pattern` 的步，pattern 於 1-based 行命中＝exact；他行命中＝**corrected（報告不 fail）**；零命中＝FAIL unverified
   - `--manifest`：manifest 記的 source 檔存在；derived tour 來源 generator 名合法
3. 輸出：per-tour 統計行（`[OK]`/`[WARN]`/`[FAIL]` tag）＋總計＋exit code（任何 FAIL→1）
4. 純 stdlib＋既有 `common.py` 慣例；**不依賴 codetour repo**（正則語義內建，錨點註解標示語義源）

### Pseudo Code
```python
def ts_key(title) -> str: ...          # utils.ts:37-43 重現
def iter_tours(repo, tours_dir): ...    # yield (rel, dict)
def check_links(tour, keyidx) -> list[Fail]
def check_anchors(tour, repo) -> list[Fail | Corrected]
def check_manifest(repo, tours_dir) -> list[Fail]
def main(): argparse; 聚合; print [OK]/[FAIL] 摘要; sys.exit(bool(fails))
```
Call Stack：`main → iter_tours → {check_links, check_anchors, check_manifest} → 彙總輸出`

### 驗證策略
- unit：`ts_key`（補零前綴／`00b` 不剝／連字號截斷撞鍵）、link 鍵解析（雙方括號／`(?!\()` 排除形式）、錨三態判定
- integration：fixture corpus（壞 JSON／死鏈／漂移錯各一）→ FAIL 對應；真实 corpus 三案例跑——codetour `.tours/`＝SM-1（0 fails）、mosaic `.tours/arch/`＝0 fails（本 session 已驗的回歸）
- 已知未覆蓋：JS RegExp 與 py re 的罕見逸出字元差異（R2）

---

## 段落 T3：manifest 規格＋mosaic 套用

### Context
derived/curated 二分需要機械載體——provenance 記 source×generator×commit；NT README 手工記 commit 證明需求。實作 [corpus provenance manifest]。

**依賴錨點**：`code_reality/profile.py`（repo 擁有配置的慣例——manifest 屬 `.tours/`（corpus 資產）非 profile）；toml 讀寫用 stdlib `tomllib`＋手寫 writer（無寫入需求依賴）

### 核心實作要點
1. Schema（`.tours/manifest.toml`）：
   ```toml
   version = 1
   audience = "newcomer"            # newcomer | owner
   [tour."00 - mosaic 總覽.tour"]
   generator = "manual"              # manual = curated
   sources = []                      # 手工總覽無機械 source
   anchored_commit = "0c2a496c"
   [tour."chain-01-...tour"]
   generator = "chain_tour"
   sources = ["ai-analysis/blueprint/callstack-v1/backtest-chain.md"]
   anchored_commit = "0c2a496c"
   ```
2. 共用讀寫（`code_reality/tour_manifest.py`：load／upsert_rows／dump）——T4/T5 產出時寫、T2 `--manifest` 消費
3. mosaic 套用：對 staged corpus 生成 manifest（28 chain tours=chain_tour derived＋2 overview=manual curated；audience=newcomer）——**新檔加入 staging 群，不改既有 staged 檔**
4. curated 升級判定（供 audit 用，T6 消費）：derived tour 若 `tour_validate` 後重產 diff 非空 → 報告建議升 `manual`

### 驗證策略
- unit：round-trip（load→dump 等價）、未知鍵容忍、`manual`/工具名列舉
- integration：對 mosaic `.tours/` 生成→`tour_validate --manifest` 綠；`sources` 全存在
- L4：mosaic 工作樹實跑（manifest 檔落在 staged 群旁，不污染其他路徑）

---

## 段落 T4：tour_upgrade CLI＋NT 30 條遷移

### Context
NT corpus（30 條、358 步 line-only 無 pattern、cross-ref 純文字、untracked）是認真產出但舊格式；NT HEAD 恰為錨定 commit（零漂移）。遷移＝格式升級非修漂移。實作 [tour corpus 舊格式遷移]。

**依賴錨點**：
- 遷移對象：`nautilus_trader/.tours/*.tour`（30 條）＋`.tours/README.md`（cross-ref 慣例記錄：`[N - 名稱]` 純文字、號碼＝NN 去零）
- 素材：step description 符號線索（如 `class DataActor:`、`:731`、`pub struct DataActorCore {`——實例見 `.tours/actor-model.tour`）
- 消費端：pattern 語義＝`anchor.ts` `matchAllLines`（`gm` 旗標、多命中取最近行）

### 核心實作要點
1. CLI：`python -m code_reality.tour_upgrade --repo <repo> [--tours-dir .tours] [--apply]`（**預設 dry-run**）
2. 三個轉換（每步可獨立失敗，失敗保留原狀＋報告）：
   - **pattern 補全**：從 description 萃取符號宣告（py `class|def`、rust `pub struct|pub fn|fn|trait`、`:NNN` 行提示）→ 組 `^[ \t]*(pub )?(struct|fn|trait|class|def) <name>` literal-ish pattern；以該步 `file` 驗證 pattern 命中且最近行＝原 line → 寫入；否則 skip＋報告（R1 降級）
   - **cross-ref 活化**：`[N - 名稱]` → `[名稱][<目標 title 剝前綴>#1]`（N→title 映射由 corpus 內 `NN - ` 前綴建）
   - **manifest 寫入**：generator=`manual`（NT corpus 是 docs×code 手工認真產出——**分類為 curated**）、sources=對應 `docs/concepts/<章>.md`（README 索引表有映射）、audience=`newcomer`、anchored_commit=`61590e4867`
3. `--apply` 後自動跑 tour_validate；報告 pattern 補全率／活化數／skip 清單
4. NT 版控：`.tours/` 加入 fork main（upstream 無此目錄，rebase nightly 恆乾淨）——commit 用戶 gate

### Pseudo Code
```python
def extract_symbol(desc, file_lines) -> str | None: ...   # 符號線索 → pattern 候選
def upgrade_step(step, repo) -> StepResult: ...            # pattern 補全（驗證後寫入）
def revive_crossrefs(text, title_by_num) -> str: ...
def main(): dry-run 報告 / --apply + validate
```

### 驗證策略
- unit：符號萃取（py/rust 宣告各形態）、cross-ref rewrite（含撞鍵偵測——NT title body 若含連字號如 `cache-persistence` 要以截斷鍵活化）、dry-run 不改檔（mtime/diff 斷言）
- integration：NT 真實 corpus dry-run→報告→apply→validate 綠；pattern exact 佔比量化
- L6（用戶）：codetour 0.0.62 開 NT repo 走 `01 - LiveNode 生命週期`——cross-ref 點擊跳 tour（SM-6）；isPrimary 冷啟動提示
- 已知未覆蓋：R1 萃取率——低則殘留 line-only（行為不劣於現狀）

---

## 段落 T5：test_tour generator

### Context
tests 是腐化最慢的 source（fail 即修）＋上游 `>> pytest` 可執行步（`SHELL_SCRIPT_PATTERN`，`codetour/src/player/index.ts:52`）讓 test tour 天生互動。斷點③（AI 生成 callchain 文檔）的拆小替代：先機械骨架。實作 [test case → tour 骨架]。

**依賴錨點**：形態範本 `chain_tour.py:411-427`（writer 慣例）；骨架源＝target repo `tests/`（AST 直讀，不 spawn pytest）；`code_reality/exclusions.py`（.venv 等排除慣例）

### 核心實作要點
1. CLI：`python -m code_reality.test_tour --repo <repo> [--tests-dir tests/<sub>] [--out-dir .tours/tests/<sub>] [--primary N]`（primary 預設不標）
2. 枚舉：`ast.walk` 收 `test_*` 函數（含 class 內 method）→ 每個 test 檔一條 tour（title `NN - tests/<rel>`）、每 test 一步：
   - `line`＝函數 1-based 行、`pattern`＝`^([ \t]*)def test_<name>\(`（縮排容 class method）
   - `title`＝test 名；`description`＝docstring 首行（無則骨架佔位文字）＋第一行 `` >> pytest <file>::<test> ``（可執行）
3. manifest 寫入（generator=`test_tour`、sources=［test 檔］）
4. 骨架免 LLM；敘事填充是後續人/LLM 策展層（本 EP 不做 LLM 填充）

### 驗證策略
- unit：AST 枚舉（module 級/class 級/nested、非 test 函數排除）、pattern 對齊、`>>` 行格式符合 SHELL_SCRIPT_PATTERN
- integration：對 mosaic `tests/` 某子目錄實跑→tour_validate 綠＋步數=test 數
- 已知未覆蓋：parametrize 展開（AST 看不見 fixture 參數空間——一個 test 一步，不做 case 展開，標記為已知限制）

---

## 段落 T6：更新接線

### Context
audit 沒有觸發時機＝機制空轉。三個消費點：post-build（任務收尾）、tour-bootstrap（audit 模式）、mosaic nightly-sequence（日常）。實作 [corpus 更新 audit 接線]。

**依賴錨點**：`skills/post-build/SKILL.md` 階段 4（docs 鏈——audit 列入收尾報告）；`deploy/scripts/` nightly-sequence（mosaic launchd 22:57 thin 序列——**改動列可選、用戶 gate**：ops 排程變更需知情）

### 核心實作要點
1. post-build skill：階段 4 加一行——「repo 有 `.tours/manifest.toml` → 跑 `tour_validate --manifest`，FAIL 進收尾報告」（G4 delta 自動化維持不在範圍，僅 audit 消費）
2. tour-bootstrap skill：audit 模式（T1）引用 `tour_validate` CLI 名——一字不差
3. mosaic 可選：nightly-sequence 尾端一行 audit→`ops/tour-audit-YYYYMMDD.log`（launchd plist 不動，僅腳本；**commit 前用戶確認**）

### 驗證策略（docs mode＋一行 shell）
- skill 引用與工具名 single-source 對齊（rg）；nightly-sequence 改動跑一次 shellcheck 等價（bash -n）＋實跑 dry

---

## 整合策略

- **baseline**：ai-rules `002f7edd`／nautilus_trader `61590e4867`／mosaic `0c2a496c`（各 repo 弧邊界由本行管轄）
- **執行 session**：ai-rules session（工具主戰場；NT/mosaic 段以絕對路徑跨 repo 寫入——spawn 端責任，不 cd）
- **寫入白名單**：ai-rules `code_reality/`＋`tests/`＋`skills/{tour-bootstrap,post-build,code-reality}/SKILL.md`＋`ai-analysis/execution-plans/ep-tour-corpus-governance.md`＋`.kanban/Backlog/` 三卡；nautilus_trader `.tours/`（含 manifest）；mosaic `.tours/manifest.toml`＋（可選）`deploy/scripts/nightly-sequence` 一行
- **commit 順序**（各自用戶 gate）：ai-rules（工具＋skill＋EP＋kanban）→ nautilus_trader（`.tours/` 升級＋manifest 進 fork main）→ mosaic（manifest 加入既有 staged 群）
- **語義約束**：curated 保護貫穿 T3/T4/T6——任何「重產/遷移」預設 dry-run 或 diff 報告；工具輸出 tag 遵守 `[OK]/[WARN]/[FAIL]` 慣例

## 收尾步驟

1. code-reality skill 工具表加三列（tour_validate／tour_upgrade／test_tour——職責一行）；tour-bootstrap skill 反映三模式（T1）
2. kanban：三卡（EP 追蹤／驗證遷移／test 骨架）搬 In-Progress→Done（build 階段 5a 結算）
3. NT `.tours/README.md` 更新：cross-ref 段改為活 link 語法說明＋manifest 引用（保留錨定 commit 記錄）
4. /audit-test：對三工具測試跑品質稽核
5. mosaic `.tours/README.md` 補 manifest 與 audit 一行（「如何再產」旁）

## EP Review 記錄

依用戶指示跳過雙軸 EP review 與 Agent Review（ctx 約束＋deep-work 直跑）——品質防線＝機械驗證閘門（ruff clean／212 tests passed／三 corpus validate 全綠）＋建置中自抓 5 缺（check_links 髒行、docstring None、manifest 路徑基準、fail 未逐行印、delta 排除）。跨 session review 建議：commit 前可跑獨立 /code-review 補層。

## 執行記錄（同 session build）

- T1~T6 全段完成；SM-1~9 對應驗證：SM-1 codetour 0 fails／SM-2/3 fixture+實例／SM-5 NT dry-run 報告（pattern +241/358、crossref 165）／SM-6 NT apply 後 validate 0 fails（165 live links；L6 用戶走讀待驗）／SM-7 mosaic case_studies 6 tests 骨架綠／SM-8 dry-run 預設＋curated 鐵律入 skill／SM-9 post-build 接線完成（nightly-sequence 行 pending 用戶 gate）
- 建置中發現並修：NT 舊描述的 rust 屬性方括號（`[pyclass(...)]` 等 62 處）會被 player TOUR_REF 誤判壞 link——upgrade 加全形括號 sanitize；驗證器「單方括號未解析」降 WARN（prose 誤判）、「雙方括號未解析」維持 FAIL
- mosaic corpus 重跑 chain×3 與 staged 零差異（generator 冪等實證）＋manifest 原生寫入（23 chain rows 帶 callstack sources＋2 manual＋4 test_tour rows）

## 結算（2026-08-23——M1 dogfood 後）

- **T5 test_tour 除役**（user 裁定 M1 D2：方向錯誤——本意是「每個 call path 應該都有 test cover」，tests 是驗證資產非敘事素材；工具＋測試已刪、skill 工具表同步）。本文檔 T5 段與 schema 範例的 test_tour／audience 內容為歷史記錄，隨歸檔凍結。
- **manifest audience 欄廢除**（M1 D3：全工具鏈零讀取點＋newcomer 寫死與地圖層退役後語義矛盾）——load 容忍舊檔、dump 自然淘汰（codetour／NT manifest 既有鍵 lazy migration）。
- **承接方向（user 裁決語義）**：coverage 三軸對帳（test→source 既有／tour→source 雛形／test→tour 缺）——產出＝**缺口報告生成器**（backlog 生成），非 tour 生成器、**永遠不是 gate**（Goodhart 防護）。規格另立 session 對齊，載體＝`.kanban/Backlog/coverage-triaxis-spec.md`。
- 收尾步驟 2 補執行：三卡搬 Done；本文檔歸檔 `_done/`。
