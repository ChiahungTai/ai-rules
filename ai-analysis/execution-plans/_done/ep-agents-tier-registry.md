# EP: agents tier registry 與兩跳 model 解析

> **build 結算（08-29）**：S1-S4 全段完成；fresh-eyes build 審查 findings（下行稱 **B-F***，B-F1~B-F6＋A1 未驗證記錄一筆，區別於下方「EP Review Findings」表的 F-*）——B-F1（並發 sizing 主體改為 agent tier）、B-F2（舊直達路徑×3→shared/＋順手收 transition→delta_tour 漏網×3）、B-F5/B-F6 已修；B-F3（並行 session 在製品 skills/code-reality/SKILL.md）commit 時排除；B-F4 維持（偏差記錄）。post-build consistency gate 5 findings（稱 **C-F***）：C-F1 neutral 化殘留（絕對路徑＋跨域 ref）、C-F2 並發表 vision 列、C-F3 execution-plan 舊 sizing 殘留、C-F4 Done 卡 EP 指針、C-F5 本 header F-ID 命名空間碰撞——全修。**待驗證**：ZCode spawn smoke（A1 pin 合法性）＋CC 端清單確認。
>
> **⚠️ post-build 修正（08-29 午，並行 session 對照實驗觸發）**：S2 的 symlink 農場假設被實驗證偽——**ZCode registry 不載入 file-level symlink**（目錄 symlink 可穿透、檔案 symlink 靜默不載；code-reviewer/-primed 對新 ZCode session 不可見）；開箱驗證的缺口＝只驗了實檔 agent 的 spawn＋檔案 listing，未驗 symlink agent 的 ZCode spawn。修正＝registry 內改實檔拷貝（shared/ 維持 authoring 單一源＋cmp 同步紀律，hardlink 被 clone 破壞不可用），agents/AGENTS.md 治理段已改寫。**修正驗證已閉環**（08-29 午：CR session spawn code-reviewer PASS＋telemetry `zcode-code-reviewer` 實跑複核）；**CC 臂 spawn 仍未 runtime 驗證**（listing ≠ spawn——與 ZCode 同型缺口，relay 待跑）→ **已閉環（08-29 晚）**：CC session 全新 session spawn code-reviewer 回真審查報告；hub cmp 複核 `~/.claude/agents/` 兩檔＝`agents/claude/` byte-identical。兩家 registry runtime 驗證完畢。

> **ep_type**: implementation
> **mode**: docs mode（repo 檔案變更全為 `.md`；`rg "^def |^class " --type py` 於變更範圍 = 0。**含非 repo 的環境突變**：S2 頂層 symlink 翻轉〔user-level，F-7〕）
> baseline: 5786151（working tree 另有本 session 先行的 model-routing.md 兩行更新——flash 表列＋降級映射註記，由 S1 吸收；`ai-analysis/tours/` untracked 屬並行 session，不屬本 EP——其 ep-cr-plugin-skill-split 系改動已隨 5786151 結算）

## 研究摘要（段落 0）

證據基礎（本規劃 session 已完成，決策全文見 memory `project-agents-registry-split-design`）：

- **telemetry 三報告**（578 sessions／426 subagent spawns）：角色與 agent 面已解耦、read-only 是事實不變量（reviewer/primed/Explore 零 Edit/Write）、主對話佔 90% token → lite-tier 價值＝速度＋並發寬度＋多模、並發 3 是實際瓶頸、callstack writer 判決衝突（A/B 另卡）
- **ccr repo 深挖**（v3.0.21）：direct-first 常態定案（ccr 斷 ZCode usage 顯示）；zcode/ pins 是體系唯一 provider 耦合點——未來改走 ccr 只換 pin 值（`glm-5.3-flash` → `Fusion/lite`），角色/tier/skills 全不動
- **兩跳解析模型**（user 定調）：角色 → tier（通用）→ (model, effort)（per harness×provider 查表）；CC enum 本身是 tier 語彙（GLM provider 別名表解析）

**可複用基礎設施**：`agents/AGENTS.md` 欄位相容策略表（治理底座）、`agents/code-reviewer.md`（一檔兩吃現役範本）、`rules/model-routing.md`（單一源載體）、`skills/agent-workflow/SKILL.md` 偵測表（並發 sizing 消費者）、codex-plugin-cc 的 `codex-rescue` 薄轉發合約範式（S3 body 紀律）

**風險假設**：

| ID | 等級 | 假設 | 驗證 |
|----|------|------|------|
| A1 | 中 | ZCode agent 定義 `model: glm-5.3-flash`＋`thoughtLevel: high` 為合法值（欄位名陷阱：非 `reasoningEffort`；flash 於 UI 下拉的實際名稱未確認） | S3 smoke spawn＋telemetry model_id 驗證；建檔前可先查設定 UI 下拉 |
| A2 | 中 | 檔案級 symlink 在兩家 registry 載入路徑正常（ZCode 快照制重讀；CC 檔案監聽）〔**已證偽** 08-29——檔案 symlink 靜默不載，見 header post-build 修正段；修正後 registry 為實檔拷貝〕 | S2 兩家新 session spawn probe〔原驗證未覆蓋 symlink agent 的 spawn——缺口由並行 session 實驗補上〕 |
| A3 | 低 | ZCode UI 編輯 shared 角色會寫穿 symlink（in-place 改到本體或 atomic-replace 弄斷連結） | 治理規則先擋（S2）＋git status 兩種皆可偵測；不預先實測 |
| A4 | 低 | registry 目錄中的 `AGENTS.md`（無 frontmatter）持續被兩家忽略＋診斷（現況即如此） | S2 probe 附帶觀察 |

**致命先驗**：無（結構全可逆：symlink＋git；最大失敗模式＝pin 值不合法，S3 驗證即抓）。

**callstack 菜單**：repo 無 `ai-analysis/blueprint/callstack-plan.md`——跳過。

## EP Review Findings

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| F-1 | 🟡 | SM/S2 | symlink 翻轉時活 session 行為無場景（ZCode 快照免疫但重啟續接即刷新；CC 監聽舊 inode 未驗證） | 補 SM-6＋S2 翻轉時機紀律 | implemented |
| F-2 | 🟡 | S1 | flash rate-limit 列 inline 日期「2026-08-29 情報」——instruction 檔日期禁令（精神面：日期過時） | 整併時刪日期、保留「以 provider dashboard 為準」 | implemented |
| F-3 | 🟡 | S4 | scope flip 漣漪未列全：`rules/AGENTS.md:67` 表列＋`:69` 計數句；bundle 組成變更未列 deploy rerun／斷 ref 檢查 | S4.4 明確兩處；S4.5 加 deploy gate | implemented |
| F-4 | 🟢 | S1/S2 | 錨點微 drift ±1-2 行（review-engine:138→140、code-review:56→55、model-routing :33-35→34-36、agents/AGENTS.md :9-16→9-17）；零錯指 | 錨點清單校正 | implemented |
| F-5 | 🟢 | S1 | `execution-plan/SKILL.md:158`「session 降一級」是語義引用（需改寫），錨點清單只列 :293（pointer） | 補 :158 | implemented |
| F-6 | 🟢 | S2/S3/SM-5 | rg 預設不跟 symlink——S2 後掃描看不穿 registry 視圖；SM-5 pattern 漏「降級」措辭變體（workflow-review-pattern.md:161） | 穿透掃描加 `-L`；pattern 擴「降級」 | implemented |
| F-7 | 🟢 | header | docs mode 宣告未涵蓋環境突變（user-level symlink rm/ln、mkdir/git mv） | 宣告補一句 | implemented |
| F-8 | 🟢 | S2/S3 | lite-verify 名稱含 tier 詞彙、spec-miner 無——命名不對稱 | ❌ 維持現名：對話與 memory 已固化、零功能收益；S2 規則禁的是 provider 引擎名非 tier 詞 | rejected |

## UC 盤點（docs mode：受影響命令/rules 清單）

### 掃描範圍
`rg -l "model-routing" rules/ skills/ agents/` → 八檔（下表）；`.kanban/Backlog/` 8 張卡無重疊主題。

### 受影響清單

| 檔案 | 變更 | 說明 |
|------|------|------|
| `rules/model-routing.md` | 語義改寫（S1） | 相對降級 → 兩跳解析；frontmatter `claude-specific` → `neutral` |
| `skills/agent-workflow/SKILL.md` | 同步（S1） | 偵測表補 `glm-5.3-flash` 列；「依任務類型降一級」引用語義改寫 |
| `skills/execution-plan/SKILL.md`、`skills/review-engine/SKILL.md`、`skills/code-review/SKILL.md`、`skills/illustrate/SKILL.md`、`skills/_common/agent-review-cycle.md`、`skills/_common/workflow-review-pattern.md`、`rules/AGENTS.md` | drift 檢查（S1） | 引用 model-routing 的語義/路徑是否需同步（多數為 pointer 式引用，逐一驗證） |
| `skills/blueprint-bootstrap/SKILL.md` | 加註（S1） | 內嵌「並行上限 ≤3」是全強度實證——加 flash tier 例外註記 |
| `agents/`（結構） | 重構（S2） | flat → `shared/`＋`zcode/`＋`claude/`＋頂層 symlink 翻轉 |
| `agents/AGENTS.md` | 治理擴充（S2） | registry 段：pin 單一源同步紀律、UI 防護規則、tier 命名規則 |
| `agents/zcode/{spec-miner,lite-verify,vision-review}.md` | 新增（S3） | flash+high 釘死的三顆 tier agent |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 角色→tier→(model, effort) 兩跳解析（單一源） | 📋 | `rules/model-routing.md` |
| per-harness agents registry（shared/zcode/claude 薄視圖） | 📋 | `agents/` |
| ZCode tier-pinned agent 家族（spec-miner／lite-verify／vision-review） | 📋 | `agents/zcode/` |

## Scenario Matrix（docs mode 文檔語境）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 兩家各見正確 registry 成員 | symlink 翻轉後新 session | 兩家 spawn `code-reviewer` 正常；CC 端 agent 清單**無** zcode 專屬檔（fork 只進 zcode registry） | 無 | registry |
| SM-2 | lite 任務跑在 flash+high | ZCode 委派機械驗證/查證任務 | agent 完成回報；telemetry 該 subagent session 的 model_id = `glm-5.3-flash` | 無 | tier 家族 |
| SM-3 | 換 provider/模型換代 | 改 model-routing 解析表 | `rg` 掃 zcode/ pins 同步，零殘留舊值 | 無 | 兩跳解析 |
| SM-4 | UI 誤編 shared 角色 | ZCode 設定頁編輯 code-reviewer 的模型 | 治理規則先擋；違反時 git status 可見（shared/ diff 或 symlink 斷）→ 回復＋改建 zcode fork | `git checkout -- agents/shared/` | registry |
| SM-5 | 舊語義殘留 | S1 改寫後全域掃描 | `rg "降一級|降級" rules/ skills/ agents/ -L` 命中處全同步或標註保留理由（blueprint-bootstrap 歷史實證語境；`-L` 穿透視圖〔F-6〕） | 無 | 兩跳解析 |
| SM-6 | 翻轉時活 session | symlink 翻轉當下有活 CC session（監聽舊 inode）或 ZCode 重啟續接（快照刷新） | 時機紀律先擋（S2 步驟 3〔F-1〕）；未擋住時活 session 行為未驗證→以新 session 重驗 | 無 | registry |

## 段落劃分原則

S1（語義底座）→ S2（結構）→ S3（消費者）→ S4（gate）。S2 必須先於 S3（新檔放 `zcode/` 才會被載入）；S1 先於 S2（AGENTS.md 治理段引用新表語義）。

---

## S1: model-routing.md 兩跳改寫＋引用同步

### Context

**背景**：user 定調「harness awareness 取代相對降級」——任務需求與主 session 模型無關，(model, effort) 是 per (harness×provider) 的靜態解析。本段把 `rules/model-routing.md` 從「偵測主 session model → 降一級」改寫為兩跳表，並同步所有引用者。

**UC 引用**：實作「角色→tier→(model, effort) 兩跳解析（單一源）」。

**依賴錨點**：
- `rules/model-routing.md` 定義端（改寫主體；現內容：降級/inherit 分類 `:9-14`、降級映射 `:16`、rate limit 表 `:18-26`（含未 commit 的 flash 列）、套用兩路徑 `:28-31`、classifier 段 `:34-36`）
- 消費端（rg 實測引用面）：`rules/AGENTS.md`、`skills/agent-workflow/SKILL.md:48,159,213`、`skills/review-engine/SKILL.md:140`（「review→降級」語義引用——S1 改寫標的之一）、`skills/code-review/SKILL.md:56`、`skills/execution-plan/SKILL.md:158,293`（`:158`「session 降一級」是**語義引用**需改寫〔F-5〕）、`skills/illustrate/SKILL.md`（行號 S1 時 rg 定位）、`skills/_common/agent-review-cycle.md`、`skills/_common/workflow-review-pattern.md:161`（「review→降級」措辭——語義引用〔F-6〕）
- 內嵌數字例外：`skills/blueprint-bootstrap/SKILL.md:55`（「並行上限 ≤3」＋實證語境——保留數字、加 flash 例外註記）

**語義約束**：與 S2 共享——「tier」詞彙定義（full/lite/vision）以本段表為單一源，S2 治理段與 S3 agent 命名引用之，不自帶定義。

**基礎設施盤點**：無程式碼；文檔面可直接複用本 session 已驗證的解析列（ZCode×GLM＝`glm-5.3-flash`＋`thoughtLevel: high`／CC×GLM＝`haiku` 別名／CC×Anthropic＝原生）。

### 修改要點（docs mode 代 pseudo code）

1. frontmatter `harness-scope: claude-specific` → `neutral`（成為雙 harness 單一源）
2. 主體重構為三段：
   - **角色→tier 表**：spec-miner/lite-verify→lite；vision-review→vision；code-reviewer(-primed)/impl/test-gen→full（inherit 或同層最強）；render→lite
   - **tier→(model, effort) 解析表**：欄位＝tier｜harness×provider｜model 欄位值｜effort 編碼｜備註。列：ZCode×GLM（lite=`glm-5.3-flash`+`thoughtLevel: high`；full=inherit）、CC×GLM（`haiku`+`effort: high`，註明 provider 別名表直達 flash）、CC×Anthropic（`haiku` 原生）、（預留 ccr 列：`Fusion/lite`，標「未啟用——direct-first 常態」）
   - **rate limit／並發表**：整併現表（含 flash 高並發列——**整併時刪 inline 日期**、保留「以 provider dashboard 為準」〔F-2〕），spawn 紀律 `[Agent] model=…, max=N` 保留、max 按各 agent 所在 tier 查表
3. 刪除「降級映射」算術式與「session-1」詞彙；classifier 段保留（與 model 分派正交）
4. agent-workflow 偵測表補 `glm-5.3-flash` 列；其「Step 2 依模型查並發上限」語義不變
5. 八個引用檔逐一 drift 檢查：pointer 式引用（路徑對）不動；語義引用（提及降級/任務類型分派）改寫為 tier 語彙；blueprint-bootstrap 加註不刪數字

### 驗證策略（docs mode）

- `rg -n "降一級|降級|session-1" rules/ skills/ agents/ -L` → 零殘留（或僅 blueprint-bootstrap 歷史實證語境＋註記；`-L` 穿透 registry symlink 視圖、pattern 含「降級」措辭變體〔F-6〕）
- `rg -n "model-routing" rules/ skills/ agents/` 逐檔核對引用語義與新表相容
- 表自我一致：S3 三顆 agent 的 tier 在角色→tier 表有列、解析列有對應 (model, effort)
- `/consistency`（S4 formal gate 涵蓋；本段先自查）

---

## S2: agents/ registry split（結構＋symlink＋治理）

### Context

**背景**：把 flat 共用目錄改為「shared 內容切片＋per-harness registry 薄視圖」，使 per-harness 指定從命名紀律變機制（registry membership）。借 code-plugin-cc 三原則：單一 manifest、薄索引、零內容副本——**不搬** marketplace 快取層。

**UC 引用**：實作「per-harness agents registry（shared/zcode/claude 薄視圖）」。

**依賴錨點**：
- 現況：`~/.zcode/agents`、`~/.claude/agents` 兩頂層 symlink → `~/Github/ai-rules/agents/`（flat：`AGENTS.md`＋`code-reviewer.md`＋`code-reviewer-primed.md`）
- 治理底座：`agents/AGENTS.md`（欄位相容策略表 `:9-17`、tools 陷阱 `:19-21`、ZCode 限制 `:27-33`）——保留原內容、擴充 registry 段

**語義約束**：與 S1 共享 tier 詞彙；與 S3 共享——「zcode/ 內實體檔＝ZCode 專屬（含 UI 寫入落地）；shared/ 檔經 symlink 兩家共用」。

**基礎設施盤點**：`code-reviewer.md` frontmatter 為一檔兩吃範本（tools 含 MCP 全名＋`background: true`），搬遷零修改。

### 修改要點

1. `git mv agents/code-reviewer.md agents/code-reviewer-primed.md agents/shared/`；`mkdir agents/zcode agents/claude`
2. 連結農場：`agents/zcode/code-reviewer.md → ../shared/code-reviewer.md`（×2 檔）；`agents/claude/` 同構（×2）
3. 頂層 symlink 翻轉：`~/.zcode/agents → ~/Github/ai-rules/agents/zcode`；`~/.claude/agents → …/agents/claude`（先 rm 舊連結再 ln；`ls -la` 驗證指向）。**翻轉時機紀律〔F-1〕**：確認無依賴 agents 的活 CC session（檔案監聽掛舊 symlink inode，行為未驗證）；ZCode 活 session 靠快照免疫，但 app 重啟續接會刷新快照＝中途換 registry——翻轉後以首個新 session 驗證
4. `agents/AGENTS.md` 擴充 registry 治理段：
   - 目錄語義（shared＝內容切片、zcode/claude＝registry 視圖：shared 連結＋該 harness 專屬實體檔）
   - **pin 單一源紀律**：zcode/ 檔的 `model:`/`thoughtLevel:` 值以 `rules/model-routing.md` 解析表為單一源；改表 → `rg` 同步 pins
   - **UI 防護規則**：shared 角色不在 ZCode UI 調 model/思考強度（寫穿 symlink 風險）；要釘 → 建 zcode fork
   - tier 命名規則：能力語義命名（lite-verify 非 glm-flash-*）；rescue 類例外（引擎在本質內）
   - 生效時機：ZCode 改動需新 session（快照）；CC 即時監聽

### 驗證策略

- `ls -la ~/.zcode/agents ~/.claude/agents` 指向正確；`find agents/ -type l` 四條連結存在
- 兩家各開新 session spawn `code-reviewer` probe（read-only 審查行為正常）——A2 驗證
- CC 端 agent 清單無 zcode 專屬檔（SM-1）
- ZCode probe 附帶觀察 AGENTS.md 忽略診斷不影響載入（A4）
- git status 顯示僅預期變更（git mv 呈 rename）

---

## S3: 三顆 zcode tier-pinned agents＋smoke

### Context

**背景**：model-routing 降級類的 ZCode 端材料化。telemetry 依據：spec-miner/lite-verify 兩 cohort 報告一致判可降階；lite-verify 收編 Explore 被挪用的 gate 類（49 次）；vision-review 補 document-skills judge 五類以外的視覺真空。**callstack writer 不在本 EP**（兩報告判決衝突，A/B 另卡）。

**UC 引用**：實作「ZCode tier-pinned agent 家族」。

**依賴錨點**：消費 S1 解析表（lite=`glm-5.3-flash`+`thoughtLevel: high`）；落點依賴 S2（`agents/zcode/` 已是 registry）。範本：codex-plugin-cc `codex-rescue` 薄轉發合約（禁令密度）＋`code-reviewer.md`（tools 行寫法）。

**語義約束**：與 S1/S2 共享 tier 詞彙與目錄語義；三顆 agent 的 description 是 dispatch 依據（觸發語義必須與共享角色明確互斥——不搶 code-reviewer 的審查場景）。

**基礎設施盤點**：`mcp__4_5v_mcp__analyze_image` 全名（harness 隨附、自訂 tools 清單下存活——08-22 實測）；視覺路徑 B（Read 本地 PNG）由 judge 現役證明。

### 修改要點

三顆定義檔（frontmatter 範本）：

```yaml
# agents/zcode/lite-verify.md
name: lite-verify
description: "機械驗證／consistency gate／followup 對帳代理。清單驅動、逐項附證據（rg 命中/exit code/file:line）的查證任務用；非對抗性審查（那是 code-reviewer）。read-only。"
model: glm-5.3-flash        # 值以 model-routing 解析表為單一源（S1）
thoughtLevel: high          # 欄位名非 reasoningEffort；綁具體 model 才生效
tools: Read, Bash, WebFetch
```

- `spec-miner`：rg+Read 挖規格/凍結源碼，回 file:line＋逐字引用（協議強制 anti-幻覺：「不意譯」）
- `vision-review`：`tools: Read, Bash, mcp__4_5v_mcp__analyze_image`——Read 本地 PNG（路徑 B）＋4.5V MCP 全名（remote URL，路徑 A）；職責＝mermaid 渲染檢查、UI screenshot、圖表驗收（judge 五類文件以外）
- **body 薄**（codex-rescue 紀律）：角色一句＋工具紀律＋輸出格式＋反擴權禁令（「只做 X，不做 Y」）；不蒸餾 skill 內容（需要時 prompt 寫「先 Read ~/.zcode/skills/<x>/SKILL.md」）
- 建檔前先開 ZCode 設定 UI 確認下拉的 flash 實際名稱（A1 前置）

### 驗證策略

每顆一個 smoke（ZCode 新 session）：
- `spec-miner`：查一個已知符號（如 `deploy_agents.py` 的 main），回傳須含 file:line＋逐字引用
- `lite-verify`：跑一個三項機械驗證清單（如 rg 殘留掃描），回傳逐項附證據
- `vision-review`：讀一張本地 PNG（repo 既有圖檔）出描述；telemetry 驗該 subagent session model_id=`glm-5.3-flash`（A1 驗證——**pin 不合法即本段失敗回報，不靜默降級**）
- 失敗處置：pin 值不合法 → 查 UI 實名 → 改 frontmatter → 重跑 smoke（不動結構）

---

## S4: 收尾（gate＋kanban＋部署驗證）

### Context

docs mode 收尾：formal gate 不可跳（memory：manual rg 不替代 `/consistency`）；model-routing 是定義源 → sync-sources invariants 過一輪。

### 修改要點

1. `/consistency` formal gate（範圍＝authored .md；排除 crawl 抽取檔）
2. `/sync-sources`（model-routing 語義改寫的定義源新鮮度檢查）
3. `.kanban/Backlog/` 建卡：本 EP 追蹤卡＋三張 UC 卡（兩跳解析／registry／tier 家族）；callstack A/B 試點卡（`[tag:agents]`，驗收基準＝blueprint-bootstrap 既有「錨定率 >90%」golden 對照）
4. `rules/AGENTS.md` **兩處**同步〔F-3〕：`:67` 表列（model-routing 的 scope 欄 claude-specific→neutral）＋`:69` 計數句（neutral/claude-specific 條數）
5. **bundle 組成變更 gate**〔F-3〕：跑 `uv run python scripts/deploy_agents.py` 重部署＋斷 ref 檢查（scope flip 改變 bundle 成員）；`~/.claude/rules/` symlink 讀到改寫後檔案（`rules/AGENTS.md` 部署紀律）

### 驗證策略

- consistency gate 綠燈；sync-sources invariants 全綠
- kanban 卡存在且格式合 `kanban-board`「建立卡片」段
- 兩家新 session 各一次 end-to-end：CC spawn code-reviewer（繼承面不受影響）＋ZCode spawn lite-verify（新能力可用）

---

## 整合策略

- 段落順序剛性：S1 → S2 → S3 → S4（S2 依賴 S1 語義；S3 依賴 S2 結構）
- 跨段落一致性：tier 詞彙單一源＝S1 表；目錄語義單一源＝S2 治理段
- **行為凍結面**：code-reviewer/-primed 的定義內容零修改（純搬遷）；CC 端行為完全不變（claude/ registry 只含 shared 連結）——回滾＝翻回 symlink＋git mv 回 flat
- 併行 session 干擾面：其 ep-cr-plugin-skill-split 全弧已隨 baseline `5786151` 結算（transition→delta_tour 改名漣漪與本 EP 零語義碰撞）；殘留 untracked `ai-analysis/tours/` 不 add、不改；本 EP 變更檔與其零重疊

## 收尾步驟

1. Capabilities/Kanban：docs mode 元專案跳過 Capabilities 表；`.kanban/` 建卡照 S4
2. `skills/CLAUDE.md` 工作流索引：無新 skill——檢查 agents 相關描述是否需補一行（registry 位置變更影響導航）
3. `/audit-test`：無測試變更——跳過（docs mode）
4. instruction 檔同步：`agents/AGENTS.md`（S2 已含）；root `AGENTS.md` 專案結構段的 agents/ 描述同步（`AGENTS.md:agents 行`）
