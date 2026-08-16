# EP：layer 3 人類 viewport 重構（debrief 新增 / smell-detector 合併 / deliverable-review 退役）

> **ep_type**: implementation
> **mode**: docs（全變更為 `.md` + 一處 `.py` 字串引用 `check_single_source.py`，無 callable 邏輯改動）
> **設計脈絡**：2026-08-16 session 與用戶逐項定案（debrief 名稱 ✅、smell-detector 名稱 ✅、deliverable-review 刪除+吸收 ✅、illustrate 無參數委派 ✅、測試 smell repositioning ✅）。設計決策已由用戶逐項裁決，EP Review 以該討論取代 agent cycle；機械風險（引用殘留、索引 drift）由各段驗證 + 收尾 consistency gate 覆蓋。跨 session 接續時可直接 /implement。

---

## 實作總覽

layer 3（人類 viewport）命令家族從 4 顆（deliverable-review / illustrate / codebase-sweep / human-review）收斂為 3 顆：

| 命令 | 時刻 | 回答的問題 | 來源 |
|------|------|-----------|------|
| `smell-detector` | 行動前／審既有 | 哪裡有壞味道（架構/存在/測試） | codebase-sweep + human-review 合併 |
| `illustrate` | 任何時刻 | 結構長怎樣 | 保留；無參數行為改委派 debrief |
| `debrief` | 行動後 | AI 改了啥、證據在哪、哪裡可能會錯意 | 新增；吸收 deliverable-review post-build |

動機：①「AI coding 之後想理解改了啥」無命令服務（理解 vs 審查 genre 缺口）②sweep 與 human-review 共享方法（§HR 四段深審）且互設邊界表（合併訊號）③deliverable-review post-build 與 debrief 同時刻重複、且「被審者自己策展審查證據」有證據獨立性矛盾。命名病根教訓：命名的動作而非觀看者（"human-review" 命名觀看者）。

---

## UC 盤點（docs mode：受影響命令清單）

### Backlog 關聯
- 既有 Backlog 卡（docs-mode-adaptation-audit 等 5 張）皆與本變更無關
- 自動建卡：本 EP 追蹤卡 `.kanban/Backlog/layer3-viewport-restructure.md`（已建）

### SYSTEM-MAP 影響
- ai-rules 無 SYSTEM-MAP.md → 跳過（元專案正當跳過）

### 掃描範圍
- `skills/CLAUDE.md`（工作流索引 + 核心流程拓撲）、root `AGENTS.md`（命令的受眾視角段）、全 repo `rg --no-ignore`（段落 0 清單）

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 |
|------|------|------|------|
| 結構 viewport（illustrate） | ✅ | skills/CLAUDE.md 索引 | 保留；無參數行為改委派 debrief（S4） |
| 交付驗收（deliverable-review） | ❌ 退役 | 同上 | post-build 吸收進 debrief（S1/S3）；`--ep` mode 移除（方向確認 = 人讀 EP + ep-review） |
| 放大鏡存在質疑（human-review） | ❌ 併入 | 同上 | smell-detector zoom mode（S2） |
| baseline 盤點（codebase-sweep） | ❌ 併入 | 同上 | smell-detector `--baseline`（S2） |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| AI 改動理解簡報（debrief） | 📋 | skills/debrief/SKILL.md |
| 壞味道偵測＋重構前期研究（smell-detector） | 📋 | skills/smell-detector/SKILL.md |

---

## Scenario Matrix（文檔語境：rg 命中 / 0 殘留 / 行為宣稱）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | debrief 無參數、uncommitted 存在 | `/debrief` | 七段簡報（含驗證證據 NONE 逼問 + 認知誤差點） | — | debrief |
| SM-2 | debrief 無變更 | working tree 乾淨 | fallback `git diff HEAD~1`（沿 illustrate 既有 fallback 鏈） | — | debrief |
| SM-3 | debrief 面對純 docs/rules 變更 | diff 全為 .md | 行為黑盒子段渲染 behavior delta（AI 讀了會做什麼不同）+ 影響 UC | — | debrief |
| SM-4 | smell-detector zoom | `/smell-detector <dir\|files>` | HR 格式 findings（倒金字塔 + 查證誠信 + 微圖僅當釐清時） | — | smell-detector |
| SM-5 | smell-detector 廣角 | `--baseline <dir>` | sweep 4 檔機制 + 狀態表 + invariants（--status/--stale/--arch 續掛） | — | smell-detector |
| SM-6 | 舊名殘留 | `rg --no-ignore "deliverable-review\|human-review\|codebase-sweep"` | living docs 0 殘留（歷史檔白名單除外，見 S5） | — | 全 |
| SM-7 | 權限/索引 drift | settings.json、skills/CLAUDE.md | 新名允許、索引與 `fd -t d . skills/` 對照一致 | — | 全 |
| SM-8 | 流程拓撲 checkpoint | post-EP 方向確認 | 移除 `/deliverable-review --ep`（方向確認 = 人讀 EP + ep-review） | — | — |
| SM-9 | 機械腳本引用斷裂 | check_single_source.py consumers | 清單更新後 `uv run python skills/scan-project/scripts/check_single_source.py` exit 0 | — | — |

---

## 段落 0：全域研究（引用盤點，已執行）

> implement 時重跑以下 rg 確認清單未漂移（跨 session 可能有其他 commit）：
> `rg -l --no-ignore "human-review"` / `rg -l --no-ignore "codebase-sweep"` / `rg -l --no-ignore "deliverable-review"`

**Deployment 結構**：`~/.claude/skills`、`~/.zcode/skills`、`~/.agents/skills` 三根符號連結**整目錄**指向 `ai-rules/skills/`——新增/刪除 skill 目錄自動生效，無 symlink 操作。

**引用地圖**（living docs = 需改；歷史檔 = 不動）：

| 檔案 | 引用 | 處置 |
|------|------|------|
| `AGENTS.md` | 三名（受眾二分表、三層介入表、核心流程命令分類） | S5 改 |
| `CLAUDE.md`（root）:13 | deliverable-review（Rule/Agent 治理例子） | S5 換例 |
| `settings.json` | 三名（skill 權限 allow-list） | S5 改 |
| `skills/CLAUDE.md` | 三名（索引 :52 :69 :70 + 核心流程拓撲 :30-34 post-EP/post-build checkpoint） | S5 改 |
| `rules/acceptance-evidence.md` | deliverable-review + codebase-sweep（B 軸段） | S5 改 |
| `rules/self-consistency.md` | human-review | S5 改 |
| `rules/modern-cli-preference.md` | codebase-sweep（真實案例：state.yaml 教訓） | S5 改（案例標「原 codebase-sweep 時期」，教訓不依賴命令名） |
| `skills/audit-test/SKILL.md`、`skills/code-review-and-quality/SKILL.md`、`skills/followup-review/SKILL.md` | human-review | S5 改 |
| `skills/agent-workflow/SKILL.md`、`skills/review-engine/SKILL.md` | codebase-sweep | S5 改 |
| `skills/ep-review/SKILL.md`、`skills/flow-review/SKILL.md`、`skills/implement/SKILL.md` | deliverable-review | S5 改 |
| `skills/scan-project/scripts/check_single_source.py`:55 | deliverable-review（consumers 字串） | S5 改 + **跑腳本** |
| `STATE.md`:15 | deliverable-review | **不動**（last session 觀察快照，下次自主 session 覆寫） |
| `ai-analysis/execution-plans/_done/*`、`ai-analysis/flow-feedback/*`、`ai-analysis/reports/superpowers/*`、`ref-docs/*` | 三名 | **不動**（歷史快照，改寫=竄改記錄） |

**風險假設**：
- 中等：smell-detector 合併檔過大（sweep 本體已 135 行 + HR 內容）→ 對策：SKILL.md 保持 router + 核心合約，必要時細節下沉 supporting file（沿 illustrate 慣例）
- 中等：吸收 ghost（宣稱吸收但 S1 內容缺件）→ 對策：S3 逐項吸收對照清單
- 低：ZCode description >1024 字元整顆 drop → 對策：新 skill description 精簡 + 觸發詞前置（skills/CLAUDE.md Frontmatter 規範）

---

## S1：新建 `skills/debrief/SKILL.md`

**Context**
- UC 引用：實作「AI 改動理解簡報」（UC 盤點 📋）
- 依賴：無（純新增）；S3/S4 依賴本段完成
- 基礎設施盤點：fallback 鏈（working tree → staged → HEAD~1）沿 illustrate 無參數既有設計；demo-checklist 表格式 + 認知誤差點四類 + docs/rules product-type 偵測吸收自 `skills/deliverable-review/SKILL.md`（Phase 1 渲染段 + 認知誤差點段）；輸出模式對照（console 預設 / `--md` 寫 `ai-analysis/reports/`）
- 語義約束：與 S4 共享「無參數觸發語義 = 理解 uncommitted 變更」；與 S3 共享吸收清單（見 S3 對照表）

**修改要點**
- frontmatter：`name: debrief`；description 觸發詞前置（「AI 改完 code 想理解改了啥 / what changed / 聽取報告 / brief / debrief / 檢查 AI 產出」），全文 <1024 字元（ZCode drop 上限）；`argument-hint`：無參數=uncommitted / commit hash / branch / `--md`
- 定位行：受眾 = layer 3 人類 viewport / B 軸；產出理解簡報，不產機器 finding（/code-review）、不審結構（/illustrate）
- **七段輸出合約**（倒金字塔）：
  1. 意圖一句話（這次改動解決什麼問題、為什麼改）
  2. 行為黑盒子：改動觸及的核心模組/函式 input/output + 演算法；**明確判定「對外行為變了 vs 純結構重構」**；docs/rules 變更時此段渲染 behavior delta + 影響 UC
  3. 前後差異（語義 diff，非行數）
  4. 檔案地圖：per-file 1-2 行，按角色分組（核心邏輯/配套/測試/文檔）——顯現改動形狀
  5. 波及與缺口：受影響消費者 + 該同步未同步（索引/文件/測試）
  6. 驗證證據：demo-checklist 表（feature → 可跑 target（repo-root 相對路徑）→ 覆蓋 full/partial/NONE）；NONE 不掩蓋——「沒 demo = 沒證明完成」逼問（吸收自 deliverable-review 核心機制）
  7. 認知誤差點：詮釋假設/歧義選擇/推斷行為/動態漂移（Type B），每點附確認問題
- grounding 紀律：先讀受影響檔案 baseline 再讀 diff（不是只看 diff 說故事）；diff 範圍 = `git diff` + `git diff --cached`，無變更 fallback `HEAD~1`
- 深度隨改動規模伸縮（小 fix 不硬撐七段全滿，行為段可一句話）
- 委託 skills：rules-reminder（Bash 規則）

**驗證策略**
- frontmatter description 長度 <1024（`awk` 量測）；無元資訊/版號/統計（`rg -n "版本|更新日期|行數" skills/debrief/SKILL.md` → 0）
- CJK 字元驗證：rg 精確字元抽查（形似異體字防護）
- 內容自檢：七段 + fallback 鏈 + NONE 逼問 + 認知誤差點齊備（對照本段修改要點）

---

## S2：合併 `skills/smell-detector/SKILL.md`，刪除 codebase-sweep/ 與 human-review/

**Context**
- UC 引用：實作「壞味道偵測＋重構前期研究」（UC 盤點 📋）
- 依賴：無外部依賴；S5 依賴本段（引用改寫指向新名）
- 基礎設施盤點：本體以 `skills/codebase-sweep/SKILL.md` 為底（4 檔機制、CRG 整合、invariants、受眾分離 guardrail、執行模式教訓全部保留）；zoom mode 內容來自 `skills/human-review/SKILL.md`（6 判準、誠信 stance、輸出格式、Domain 層判準 4/5 詳定義、編排 audit-test 段、LSP-stale 警告）
- 語義約束：與 S5 共享「舊名引用全面改指向 smell-detector」；測試 smell 邊界與 audit-test 正交（見修改要點）

**修改要點**
- frontmatter：`name: smell-detector`；description 觸發詞前置（「壞味道 / code smell / 架構審查 / 重構前研究 / 測試優化盤點 / 質疑 code 存在 / baseline 盤點 / sweep」），<1024 字元；argument-hint：`<dir|files>`（zoom，預設）/ `--baseline <dir>` / `--status` / `--stale [dir]` / `--architecture` / `--invariants`
- 定位：**架構審查＋重構前期研究＋測試優化盤點**（read-only 偵測器）；smell 語義 = 表面訊號指向不指控（no-severity：只標記「這裡怪」，人判讀——與 illustrate drift overlay 同構）；重構前期第一問 =「最好的重構是刪除」（HR 存在質疑的 reframe）
- **mode 分工**：
  - `<dir|files>`（預設 zoom）：HR 完整傳承——6 判準（YAGNI 嚴格/測試實際價值/嚴格不放水/質疑命名設計/scope 釐清/大改動管控）+ 查證誠信段 + 撤銷透明 + 推薦先行 + LSP-stale 補 rg + 輸出格式（倒金字塔 findings + 狀態標記 + 微圖僅當釐清 problem→fix 時）
  - `--baseline <dir>`（廣角）：sweep 完整傳承——Flow 5 步、tiering、§HR 四段深審、4 檔輸出（README/architecture/review/state.yaml）、CRG 起手 refresh、invariants hybrid 模型、provenance 一致性、受眾分離 guardrail、狀態表
  - 重機制 opt-in 設計理由：誤觸 4 檔重機制代價 >> 誤觸 console 報告
- **測試 smell 三類**（新增；grounded 於 nightly 事件真實案例，案例標「真實案例」marker，教訓不依賴專案符號現狀）：
  1. 資源 smell：per-dir 峰值 RSS / 時長——優先讀既有量測資料（nightly per-batch `/usr/bin/time -l` 落檔），無量測資料時標「無量測資料」不用猜
  2. 怪獸測試 smell：輸入規模 >> 測試意圖（真實案例：37 年全史測 5 年窗即可的行為；data_window 收法 10-16×）
  3. 結構 smell：分批覆蓋 guard / silent skip / junit 合併完整性（真實案例：collect-only guard 防「分批後新目錄靜默漏跑」）
- **邊界**：audit-test = 測試**內容**正確性反模式（同義反覆/mock/幽靈斷言）；smell-detector = 測試**套件地形**的成本與結構；修復走 /implement、/fix-test（read-only，不審又修）
- 與其他命令協作表：/code-review（diff 正確性）/ /debrief（改動理解）/ /illustrate（結構巨觀圖）/ /audit-test / /followup-review
- HR「與 sweep 的區隔」段轉為內部 mode 分工段；voice-notification 段保留
- 檔案太大時細節下沉（sweep Flow 細節可留本體，HR Domain 層判準 4/5 可下沉 supporting file）——以 SKILL.md 單檔可讀為準
- 刪除 `skills/codebase-sweep/`、`skills/human-review/` 兩目錄

**驗證策略**
- 吸收完整性：對照 HR SKILL.md 章節清單（6 判準/誠信 stance/輸出格式/判準 4a-4c/判準 5a-5d/編排 audit-test/LSP-stale/符號路徑陷阱）+ sweep 章節清單（Argument 表/CRG 起手/Flow 5 步/invariants/provenance/受眾分離/output structure）逐項在新檔有落點
- `fd -t d . skills/` 不再出現兩舊目錄；`rg -l "human-review|codebase-sweep" skills/smell-detector/` → 0（新檔不引用舊名）
- description <1024；CJK rg 驗證

---

## S3：刪除 `skills/deliverable-review/`（吸收確認）

**Context**
- UC 引用：退役「交付驗收」UC；post-build 功能由 debrief 承接
- 依賴：S1 必須先完成（吸收對象存在）
- 語義約束：`--ep` mode **不吸收**——直接移除（方向確認 = 人讀 EP + ep-review；YAGNI，日後需要再復活）

**修改要點**
- 刪除 `skills/deliverable-review/` 目錄
- 刪除前逐項對照 S1 已吸收（防 ghost-done）：

| deliverable-review 元素 | 吸收落點 |
|---|---|
| demo-checklist（feature→可跑 target→覆蓋→NONE 逼問） | debrief 第 6 段 |
| demo target 挑選規則（優先序：demo_* → test → 入口 method → NONE） | debrief 第 6 段 |
| 認知誤差點（詮釋假設/歧義選擇/推斷行為/動態漂移） | debrief 第 7 段 |
| product-type 偵測（code/docs/混合） | debrief 第 2 段（docs 語境） |
| Orientation preamble（Diff Map） | debrief 第 4 段（檔案地圖） |
| --ep mode（planned deliverable） | **不吸收**（移除，見語義約束） |
| Phase 2 互動式調查 | 不吸收（debrief 為單發簡報；互動由後續對話自然承接） |

**驗證策略**
- 上表逐項 `rg -n "<關鍵詞>" skills/debrief/SKILL.md` 確認落點存在
- `fd -t d deliverable-review skills/` → 空

---

## S4：illustrate 無參數行為改委派 debrief

**Context**
- UC 引用：更新「結構 viewport」UC 的入口行為
- 依賴：S1 完成（委派目標存在）
- 語義約束：mode C（審查驗證）本身保留——@ep / 重造偵測 / 明確審查意圖仍走 C；只有「無參數」這個 trigger 的預設行為改判為理解意圖

**修改要點**
- `skills/illustrate/SKILL.md`「無參數行為」段：改為「無參數 → 委派 [debrief](../debrief/SKILL.md)（理解 uncommitted 讛更；fallback 鏈同）」，移除語義 diff/交疊偵測/缺口偵測的本地展開（單一真理源在 debrief；波及/缺口由 debrief 第 5 段承接）
- 決策流程段輸入判斷線索：「無參數→C（diff）」改「無參數→委派 debrief」
- 「現有程式碼優先原則」表的「變更審查（無參數）」列對應調整
- 檢查 illustrate supporting files（illustrate-examples / illustrate-structure-viewport 等）有無描述無參數 diff 行為，有則同步（`rg -ln "無參數|git diff" skills/_common/illustrate-*.md`）

**驗證策略**
- `rg -n "無參數" skills/illustrate/SKILL.md` 每處行為描述一致指向 debrief
- 拓撲一致性：illustrate 的 drift spine（post-EP/post-build checkpoint）不受影響（那是 @ep/明確審查路徑，非無參數）

---

## S5：全 repo 引用改寫 + 索引 + 權限 + 機械腳本

**Context**
- 依賴：S1-S4 全部完成（引用才能指向新名）
- 語義約束：歷史檔白名單**不改**（`ai-analysis/execution-plans/_done/*`、`ai-analysis/flow-feedback/*`、`ai-analysis/reports/*`、`ref-docs/*`、`STATE.md`——歷史快照，改寫=竄改記錄）；`rules/modern-cli-preference.md` 的 codebase-sweep 真實案例為唯一例外：命令名更新為 smell-detector 並標「（原 codebase-sweep 時期案例）」，教訓內容不動

**修改要點**（依段落 0 引用地圖，implement 時重跑 rg 後逐檔處理）
- root `AGENTS.md`：「命令的受眾視角」三張表——受眾二分、三層介入（第 3 層命令列舉）、核心流程命令分類：移除 deliverable-review/human-review/codebase-sweep 三行，新增 debrief（人類·理解簡報·3）/ smell-detector（人類·壞味道偵測·3）兩行；B 軸已落地段敘述同步
- root `CLAUDE.md`:13：治理例子 `/deliverable-review` → `/debrief`（同語義：人類受眾命令）
- `skills/CLAUDE.md`：
  - 索引：刪 :52（deliverable-review）、:69（human-review）、:70（codebase-sweep）三行；「核心開發流程」群新增 debrief 行、「品質工具」群新增 smell-detector 行（描述含 zoom/baseline mode 與觸發詞）
  - 核心流程拓撲（:30-34）：post-EP checkpoint 移除 `/deliverable-review --ep`（留 `/illustrate --ep`）；post-build checkpoint `/deliverable-review` → `/debrief`
- `settings.json`：skill 權限 allow-list 三舊名 → `debrief`、`smell-detector`（先讀現有結構再改，保持格式）
- `rules/acceptance-evidence.md`：B 軸段「deliverable-review（交付）+ illustrate（結構 viewport）」→「debrief（理解+證據，承接 deliverable-review 交付軸）+ illustrate」；codebase-sweep 提及處改 smell-detector（歷史案例語境標註同 modern-cli 模式）
- `rules/self-consistency.md`：human-review 引用 → smell-detector
- 其餘 skills 散文引用（audit-test / code-review-and-quality / followup-review / agent-workflow / review-engine / ep-review / flow-review / implement）：舊名 → 新名 + 語義校正（如 review-engine「codebase-sweep 非 review 命令家族」→ smell-detector）
- `skills/scan-project/scripts/check_single_source.py`:55：consumers 清單 `skills/deliverable-review/SKILL.md` → `skills/debrief/SKILL.md`（layer 3 標註保留）；**改後執行** `uv run python skills/scan-project/scripts/check_single_source.py` 確認 exit 0（先讀該腳本確認 consumers 語義——它檢查的是 layer 3 命令對 single source 的引用，路徑換掉即語義等價）

**驗證策略**
- 殘留驗證：`rg -l --no-ignore "deliverable-review|human-review|codebase-sweep"` → 輸出僅含歷史檔白名單 + `rules/modern-cli-preference.md`（例外標註）+ 本 EP
- 索引對照：`fd -t d -d 1 . skills/` 目錄清單 vs `skills/CLAUDE.md` 索引行比對（無多無漏）
- 腳本執行 exit 0
- CJK rg 驗證（本段改動檔數最多）

---

## 收尾段（S6）

1. **/consistency gate**：必跑正式閘門（非 manual rg 替代；撞 guard bug 時用獨立 agent 同 6 維度等價替代）
2. **memory 更新**：`project_layer3-viewport-restructure` memory 標記已實作 + commit hash
3. **Kanban**：追蹤卡 `.kanban/Backlog/layer3-viewport-restructure.md` → Done/（隨 commit 帶走）
4. **EP 歸檔**：本檔 → `ai-analysis/execution-plans/_done/`
5. **commit**：git add 具體檔名（禁 -A）；commit 前查 `git log --oneline -3` + `git diff --stat`（concurrent session 防護，檔數與預期不符=紅燈）；commit message 語意：`refactor(skills): layer 3 viewport 重構——debrief 新增、smell-detector 合併（sweep+HR）、deliverable-review 退役`

## 整合策略

- 段落依賴：S1 →（S2、S3、S4 可平行）→ S5 → 收尾。S3 的吸收確認對照 S1；S4/S5 指向 S1/S2 新名
- 本 session 已承載完整設計脈絡；跨 session 接續時本 EP 自足（所有決策與理由已內嵌，無需依賴對話歷史）
