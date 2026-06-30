# EP: skills/commands listing 與載入紀律優化

> **ep_type**: implementation
> **mode**: docs（全為 `.md`，無 `.py` callable 變更）
> **review**: EP Review Cycle + Dry Run 實證已完成；lever B 已於 dry run 後移除

## 實作總覽

**背景**：基於 Claude Code 官方 skills 文檔與 monorepo 文檔盤點，ai-rules 的 skills/commands 未使用官方載入控制桿（`disable-model-invocation` 全 repo 0 用、`paths` 僅 1 用）。

**為什麼現在做**：`/doctor` listing 乾淨（`skillListingBudgetFraction: 0.05` 已設），**非急迫 budget 問題** —— 主動衛生 + 語意正確性。

**剩餘三個槓桿**（原四個，B 已移除）：
- **A**：`skills/CLAUDE.md` frontmatter 規範解鎖（1024→1536 + 補欄位文件 + 決策指引）
- **C**：skill 精煉（python-type-gap 拆檔、arch-thinking description、nt-query 驗上限）
- **D**：新增 `dependency-upgrade-watch` skill（NT/SJ 版本漂移主動建議）—— **dry run 強驗證的主價值**
- **S5**：settings.json `batch-task→sequential-batch` 正名 drift 修正 + 新 skill 索引/allow 同步

**❌ 已移除 — lever B（disable-model-invocation 分類）**：dry run 掃 732 個 mosaic session 實證，22 個 disable 集中 11 個被 AI 高頻自動 invoke（execution-plan/spec/build/commit…），設了會打斷自主流程。consent 已在 skill 層確保，invocation 層再加只斷流程不增安全。詳見「Dry Run 實證發現」段。

**不改**：trading skills 不搬進 mosaic（抵觸「ai-rules 共用家」決策 + /doctor 乾淨）；nt-query 維持全域（跨專案依賴）。

---

## Dry Run 實證發現（pre-build validation）— 決議移除 lever B 的依據

掃描 3 個 mosaic worktree session transcript（main 387 + offline 245 + trading-lab 100 = 732 JSONL / 1.85GB），比對 AI 真實 Skill tool_use 行為 vs EP 靜態分類。

**靜態驗證（全綠）**：S1/S3/S4/S5 編輯目標存在、37 command 檔無 typo、`settings.json:18` batch-task drift 確認、`dependency-upgrade-watch` 目標淨空、python-type-gap 578 行確認。

**🔴 Critical：原 S2 分類與實證衝突** → user 決議整支移除 lever B。22 個 disable 集中，**11 個在實際 session 被 AI 透過 Skill tool 自動 invoke**（已核驗 `"type":"tool_use"` 非 user message，跨 3 個 worktree 一致）：

| 命令 | AI auto-invoke 次數（main/offline/trading-lab） |
|---|---|
| execution-plan | 21 / 16 / 12 |
| spec | 8 / 6 / 8 |
| build | 8 / 3 / 6 |
| commit | 7 / 7 / 3 |
| illustrate | 5 / — / 4 |
| deep-work | 5 / 5 / 1 |
| rebase | 4 / 2 / 3 |
| handoff | 4 / 1 / 1 |
| at | 3 / — / 1 |
| daily-maintain | 2 / — / — |
| flow-feedback | 1 / 1 / — |

**根因**：原 S2 依 CLAUDE.md「受眾表」（設計意圖），但 AI 在自主流程（deep-work、EP→build→commit 鏈）高頻自動 invoke。受眾表 ≠ 實際行為；靜態 rg 看 code 引用、看不到 runtime 自主 invoke（L1 vs L4 證據階層落差）。

**為何 disable 是錯層**：(1) skill 自帶內部 gate（commit-consent、build Agent Review）—— 安全在 skill 層確保；(2) disable-model-invocation 擋 Skill tool invoke = 擋 AI 自主流程機制 → 打斷工作鏈。

**🟢 S4 強驗證**：59-80% session 含 NT/SJ 版本 pin，真實 drift（shioaji 1.5.1→1.5.4、yanked 1.5.2 panic）；`upgrade-nt`/`upgrade-sj` **0 次 auto-invoke** —— dep-watch 填的是真實缺口。

**次要觀察**：AI-self 集 `metadata-sync`/`fix-test`/`lint-fix` 部分 worktree 0 命中 —— 可能 inline 執行（讀 SKILL.md 直接做，非 Skill tool）；`disable-model-invocation` 只擋 Skill tool 不擋 inline Read。transcript 見 `arch-review` 但 `commands/` 無此檔（ep-s3-arch-review-removal 已移除，歷史 session）。

---

## UC 盤點（docs mode：受影響命令/rules 清單）

### Backlog 關聯
- 無既有卡片對應；自動建卡：1 張 EP 追蹤卡 `.kanban/Backlog/skill-loading-discipline.md`

### SYSTEM-MAP 影響
- ai-rules 無 SYSTEM-MAP.md → 正當跳過

### 掃描範圍
- `skills/CLAUDE.md`（唯一 frontmatter 規範源）
- `skills/skill-cleaner/scripts/skill-cleaner.ts:49`（`MAX_DESCRIPTION_CHARS = 1536` 真相源）
- `rules/claude-writing.md`（frontmatter 範例，指向單一源）
- `settings.json`（batch-task drift）

### 既有 UC 狀態
| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| Skill listing 載入紀律 | 🟢 部分覆蓋 | skills/CLAUDE.md | 更新 | 規範過時（1024 drift）+ 缺官方欄位文件 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 依賴升級漂移偵測（NT/SJ） | 📋 | `skills/dependency-upgrade-watch/SKILL.md` |

---

## Scenario Matrix（docs mode：文檔語境，rg 命中/0 殘留）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-4 | AI 讀 pyproject.toml 見 nautilus_trader 舊版 | 讀相依檔 | `dependency-upgrade-watch` auto-load → 查 PyPI → 建議 `/upgrade-nt` + 收盤提醒 | paths 命中 `**/pyproject.toml` | 依賴升級漂移偵測 |
| SM-4b | AI 讀相依檔見 NT/SJ 且 pinned == latest | 讀相依檔 | dep-watch load 但**靜默不輸出**（不報「已是最新」） | skill body 條件式 | 依賴升級漂移偵測 |
| SM-5 | AI 讀 pyproject.toml 無 NT/SJ | 讀相依檔 | dep-watch load 但不動作 | skill body 條件式 | 依賴升級漂移偵測 |
| SM-5-offline | PyPI/gh api 不可達 | 離線 / 防火牆 / rate-limit | dep-watch 記「無法查最新版」→ **不建議**（防幻覺版本） | skill body 退化分支 | 依賴升級漂移偵測 |
| SM-6 | python-type-gap 載入 | 觸發 | body < 500 行（reference 外移）；`paths: **/*.py` 限 Python 檔 auto-load | wc -l < 500 | listing 載入紀律 |
| SM-7 | arch-thinking / review-engine description 被截斷 | listing budget 緊 | 觸發詞在前段保住（截斷從尾部丟；dry-run 高頻 auto-invoke） | description 觸發詞位置在前 | listing 載入紀律 |

> 原 SM-1/2/doc-health/3/8（disable-model-invocation 相關）隨 lever B 移除而刪除。

---

## 段落劃分原則

- **語義依賴**：S1（spec）定義 frontmatter 欄位文件 → 治理 S3/S4。S1 最先。
- **獨立性**：S3（skill 精煉）、S4（新 skill）互不依賴，可平行。
- **收尾**：S5 依賴 S1/S3/S4 全部完成。
- **順序**：S1 → (S3 ‖ S4) → S5

> lever B（原 S2）已移除 —— 見 Dry Run 段。

---

## 段落 0：全域研究摘要

> 以直接 LSP/rg/Read + Dry Run transcript 實證完成。

**可複用基礎設施 / 真相源**：
- `skills/skill-cleaner/scripts/skill-cleaner.ts:49` — `MAX_DESCRIPTION_CHARS = 1536`（repo description 上限真相源；skills/CLAUDE.md 的 1024 是 drift）
- `commands/CLAUDE.md`「Command 與 Skill 目錄分工」三層表 — invocation 語意區分概念基礎
- `rules/claude-writing.md` frontmatter YAML 範例 — 撰寫範例（不規範上限）

**依賴關係 / 關鍵約束**：
- 個人層級 symlink：`~/.claude/skills` → `ai-rules/skills`、`~/.claude/commands` → `ai-rules/commands`
- settings.json：`skillListingBudgetFraction: 0.05`、`Skill(name)` allow 逐一列出（權限層，與 listing 正交）

**frontmatter 規範源真相**：實際唯一規範源 = `skills/CLAUDE.md`（1 處）；`commands/CLAUDE.md` 概念分工、`claude-writing.md` 範例、`encoder-philosophy.md`/`agents/` 經 rg 確認非規範源。

**dry run 關鍵實證**（取代靜態假設）：
- AI 在自主流程高頻自動 invoke dev-loop 命令（execution-plan/spec/build/commit…）→ `disable-model-invocation` 預設不設
- NT/SJ 版本漂移真實頻繁（59-80% session）、升級命令 0 auto-invoke → dep-watch（S4）填真實缺口

---

## S1：槓桿 A — `skills/CLAUDE.md` frontmatter 規範解鎖

### Context
- **背景**：`skills/CLAUDE.md`「Frontmatter 配置」段（行 82 附近）只列 name/description/allowed-tools/model/skills，且 `description 最多 1024 字元`。官方文檔2 與 `skill-cleaner.ts:49` 都是 1536。
- **UC 引用**：更新「Skill listing 載入紀律」（🟢 部分覆蓋 → 規範完整）。
- **依賴**：S3/S4 套用的欄位文件由此定義。本段最先。
- **語義約束**：`skills/CLAUDE.md` 是 frontmatter 規範**單一真相源**；`claude-writing.md` 範例**指向**此處（不複製欄位清單）。
- **依賴錨點**：定義端 `skills/CLAUDE.md:82`；消費端 `skill-cleaner.ts:49`、所有 SKILL.md `description:`。
- **成功標準**：frontmatter 段涵蓋官方欄位 + 決策指引；`1024` 消失；`claude-writing.md` 指向單一源。

### 修改要點
1. **`description` 上限 1024 → 1536**（`maxSkillDescriptionChars` 可覆寫；`description + when_to_use` 合計截斷 1536）。
2. **補齊官方欄位文件**（逐欄一句用途 + 何時設）：`when_to_use`、`disable-model-invocation`、`user-invocable`、`paths`、`context: fork` + `agent`、`allowed-tools` / `disallowed-tools`、`skillOverrides`、`skillListingBudgetFraction`。
3. **決策指引（核心，dry run 後翻轉）**：
   - **`disable-model-invocation` 預設不設** —— AI 在自主流程（deep-work、EP→build→commit 鏈）會高頻自動 invoke dev-loop 命令；設了會打斷既有工作流（732 session 實證：execution-plan/spec/build/commit 等 11 個命令合計逾百次 AI auto-invoke）
   - consent（如 commit-consent）已在 skill 層確保，**不需**在 invocation 層再加 disable
   - 欄位存在（官方支援），但若要對極少數純人類工具命令設，須以 **transcript 實證**（非受眾表）確認 AI 不會想 invoke
4. **補 description 寫法指引**：觸發詞前置（截斷從尾部丟）。
5. **`rules/claude-writing.md` 同步**：frontmatter 範例段加「完整 frontmatter 欄位與決策指引見 [skills/CLAUDE.md](../skills/CLAUDE.md)」（不複製欄位清單，單一源）。

### 驗證策略（docs mode）
- `rg "1024" skills/CLAUDE.md` → 0 hits
- `rg "disable-model-invocation|paths|when_to_use|skillOverrides|預設不設" skills/CLAUDE.md` → 命中
- `rg "完整 frontmatter 欄位|skills/CLAUDE.md" rules/claude-writing.md` → 命中
- `/consistency skills/CLAUDE.md` → 過

---

## ~~S2：lever B — `disable-model-invocation` 分類套用~~ 【已移除】

> Dry run 實證（732 session）顯示 11/22 個 disable 集命令被 AI 高頻自動 invoke，設了會打斷自主流程。User 決議整支移除。詳見「Dry Run 實證發現」段。原分類表與 AI-self 識別（consistency/claude:sync/doc-health 等）留存於 Dry Run 段作歷史記錄。

---

## S3：槓桿 C — skill 拆分與 description 修正

> **決策原則：拆分優先、蒸餾僅限噪音**。肥 reference 內容（語法表、判準細節、範例集）→ **拆** supporting file（relocate、無資訊損失，官方推薦）；冗長/可推導 → 蒸餾（移除）；< 500 且精實 → 不動。禁把 reference 細節硬蒸餾成短句（丟細節）。

### Context
- **背景**：python-type-gap 578 行超官方 500 上限（拆 reference.md）；arch-thinking / review-engine description 觸發詞塞尾巴（截斷從尾部丟；dry-run 顯示兩者高頻 auto-invoke，description 品質直接影響觸發）；nt-query 全域但需驗 description 上限。
- **UC 引用**：更新「Skill listing 載入紀律」。
- **依賴**：python-type-gap 被 `build.md` 委派（mypy 失敗時）— 拆 reference.md 後 SKILL.md 仍須保留觸發與導航。
- **語義約束**：python-type-gap 拆檔遵循 idea-refine 模式（SKILL.md + reference.md，markdown link 按需讀）。
- **基礎設施盤點**：`skills/idea-refine/`（examples.md/frameworks.md/refinement-criteria.md 三支撐檔良好範例）。
- **依賴錨點**：`skills/python-type-gap/SKILL.md`（578 行）、`skills/arch-thinking/SKILL.md:3`、`skills/nt-query/SKILL.md:3-4`、`skills/review-engine/SKILL.md:3`。
- **成功標準**：python-type-gap SKILL.md < 500 行 + paths；arch-thinking + review-engine 觸發詞前置；nt-query description+when_to_use < 1536。

### 修改要點

**python-type-gap**：
1. 拆出 `reference.md`（四層判準細節、type-ignore 語法表、mypy overload 細節）— SKILL.md 僅留觸發 + 四層總覽 + 一層範例 + reference link。
2. frontmatter 加 `paths: ["**/*.py"]`。

**arch-thinking**：
1. description 重排 — 觸發詞放前段；功能描述放後。
2. 驗 description < 1536。

**nt-query**：
1. 保持全域（不加 paths — 跨專案依賴）。
2. 驗 `description + when_to_use` < 1536（目前 ~1200，確認即可）。

**review-engine**（dry-run 高頻 auto-invoke，12 次）：
1. description 重排 — 觸發詞（嚴重度分級 Critical/Important/Suggestion、信心水準、審查者自證、LSP 查證、Writer-Reviewer 分離、review 執行預設、spawn-vs-session）放前段；功能描述（review 命令家族通用邏輯 domain 真相源）放後。
2. 驗 description < 1536。

### 驗證策略（docs mode）
- `wc -l skills/python-type-gap/SKILL.md` → < 500
- `test -f skills/python-type-gap/reference.md` → 存在
- `rg "^paths:" skills/python-type-gap/SKILL.md` → 命中
- arch-thinking description 觸發詞在前 200 字元內
- nt-query description+when_to_use 字元數 < 1536
- review-engine description 觸發詞在前 200 字元內 + 字元數 < 1536
- `/consistency skills/python-type-gap/SKILL.md`、`/consistency skills/arch-thinking/SKILL.md` → 過

---

## S4：槓桿 D — 新增 `dependency-upgrade-watch` skill（主價值）

### Context
- **背景**：dry run 實證 NT/SJ 版本漂移頻繁（59-80% session），但 `upgrade-nt`/`upgrade-sj` 從未被 AI 自動觸發（0 auto-invoke）—— dep-watch 填的是真實缺口。upgrade-nt/sj 保留 model-invocable，dep-watch 負責在偵測漂移時主動建議。
- **UC 引用**：實作「依賴升級漂移偵測（NT/SJ）」📋 新能力。
- **依賴**：升級時機由 user 決定（commit-consent 精神）；連結 upgrade-nt/upgrade-sj 命令。
- **語義約束**：只建議不執行；含收盤後執行硬約束。
- **依賴錨點**：消費端 `commands/upgrade-nt.md`、`commands/upgrade-sj.md`。
- **成功標準**：碰相依檔含 nautilus_trader/shioaji 時 auto-load；比對 PyPI；漂移建議對應命令 + 收盤提醒；無漂移/無 NT/SJ/離線時行為明確。

### 修改要點

**`skills/dependency-upgrade-watch/SKILL.md`** frontmatter：

```yaml
---
name: dependency-upgrade-watch
description: 偵測 nautilus_trader / shioaji 版本漂移並建議升級。讀取 pyproject.toml / uv.lock / poetry.lock / requirements.txt 相依清單、或討論 NT/SJ 版本/升級時使用 — 比對 pinned 與 PyPI 最新版，漂移時主動建議 /upgrade-nt 或 /upgrade-sj。
paths: ["**/pyproject.toml", "**/uv.lock", "**/poetry.lock", "**/requirements*.txt"]
allowed-tools: ["Bash(uv pip *)", "WebSearch"]
---
```

**body 要點**：
1. 讀/編輯相依清單遇 `nautilus_trader` 或 `shioaji` → 記 pinned 版本
2. 查最新版（PyPI）
3. **pinned < latest** → 點出漂移（X → Y）+ 建議對應命令（nautilus_trader→`/upgrade-nt`；shioaji→`/upgrade-sj`）+ 提醒**收盤後執行**（需跑 SJ external API 測試）
4. **pinned == latest** → **靜默不輸出**（避免噪音）
5. **離線 / PyPI 不可達** → 記「無法查最新版」，**不建議**（防幻覺版本號），可選提示 user 手動確認
6. **scope 限制**：僅處理 `nautilus_trader` 與 `shioaji`；其他 nautilus 套件（`nautilus_pyo3` 等）不建議對應命令（超出 upgrade-nt scope）
7. **不自動執行** — 只建議，時機由 user 決定

### 驗證策略（docs mode）
- `test -d skills/dependency-upgrade-watch` + `test -f .../SKILL.md`
- `rg "^paths:" skills/dependency-upgrade-watch/SKILL.md` → 命中四個 glob
- `rg "upgrade-nt|upgrade-sj|收盤|靜默|不可達|nautilus_pyo3" skills/dependency-upgrade-watch/SKILL.md` → 命中
- description 字元數 < 1536
- `/consistency skills/dependency-upgrade-watch/SKILL.md` → 過
- 手動情境驗證（SM-4/4b/5/5-offline）：mosaic session 讀 pyproject.toml 觀察 auto-load + 各分支行為（build 後人類 viewport 確認）

---

## S5：收尾（settings.json 修正 + index 同步 + 一致性驗證）

### Context
- **背景**：S4 新增 skill + 既有 batch-task 正名 drift → 需同步 settings.json + 索引 + 一致性驗證。
- **依賴**：S1/S3/S4 完成。
- **語義約束**：「格式統一/正名同步」類變更 → ripple 語義反向撈 + 名稱 drift 檢查。

### 修改要點
1. **settings.json 修正**：
   - 加 `Skill(dependency-upgrade-watch)`（新 skill 需 allow）
   - **`Skill(batch-task)` → `Skill(sequential-batch)`**（`settings.json:18` 仍為舊名，與已改名的 sequential-batch.md drift；不改則 `/sequential-batch` 觸發權限 prompt）
2. **`skills/CLAUDE.md` Skill 索引**：加 `dependency-upgrade-watch` 條目。
3. **`commands/CLAUDE.md` 命令索引**：確認 37 個命令列舉無遺漏（sequential-batch 已正名）；本次無新增 command，僅驗證一致性。
4. **ripple 語義反向撈**：`rg -n "description.*字元|description.*最多|1024|disable-model-invocation|when_to_use" rules/ skills/ commands/` — 預期只命中 `skills/CLAUDE.md`；命中他處 → drift，逐筆判讀。
5. **正名 drift 另查**：`rg "batch-task" settings.json` → 改後應 0 hits。

### 驗證策略（docs mode）
- `rg "dependency-upgrade-watch" skills/CLAUDE.md settings.json` → 命中
- `rg "batch-task" settings.json` → 0 hits
- `rg "sequential-batch" settings.json` → 命中
- `/consistency commands/CLAUDE.md` + `/consistency skills/CLAUDE.md` → 過

---

## 整合策略

- **段落執行順序**：S1（spec 先行）→ S3 ‖ S4（獨立，可平行）→ S5（收尾）。
- **跨段落一致性**：S4 的 dep-watch 依賴 upgrade-nt/sj 保持 model-invocable（本 EP 不動這三個的 invocation）。
- **build 後人類 viewport**：建議 `/deliverable-review`（docs mode：behavior delta — 「AI 對 NT/SJ 漂移會主動建議升級」）+ `/doctor` 複驗 listing。

---

## 收尾步驟

1. **Kanban**：追蹤卡 `skill-loading-discipline.md` 搬 Done/。
2. **SYSTEM-MAP**：無，跳過（正當）。
3. **CLAUDE.md 更新**：`skills/CLAUDE.md`（S1 spec + S5 索引）、`commands/CLAUDE.md`（S5 一致性）、`rules/claude-writing.md`（S1 指向單一源）。
4. **/audit-test**：docs mode 無新測試 → 跳過（正當）。

---

## EP Review 區段

> 2 Explore agent 平行審查 + 主 LLM judge-review + Dry Run transcript 實證。

| ID | 來源 | Finding | Verdict | Action |
|----|------|---------|---------|--------|
| R-A1 | agent A | `/doc-health` 被 daily-maintain cron AI invoke，原誤分 disable 集 | ✅ 採納（當時）→ **dry run 後 lever B 整支移除，失依附** | 歷史記錄 |
| R-A2 | agent A | claude:clean/distill borderline | ✅ 採納（當時）→ 同上 | 歷史記錄 |
| R-B1 | agent B | 範圍完整 37=37 | OK | 無 |
| R-B2.1 | agent B | settings.json `batch-task` 舊名 drift | ✅ 採納 | S5 修正 |
| R-B2.2 | agent B | 「三處 ripple 源」過度宣稱 | ✅ 採納 | S1/段落 0 收斂為單一源 |
| R-B2.3 | agent B | 實際規範源只 1 處 | ✅ 採納 | 同上 |
| R-B3.1 | agent B | S4 pinned==latest 未定義 | ✅ 採納 | S4 body 加靜默分支 |
| R-B3.2 | agent B | S4 離線退化未定義 | ✅ 採納 | S4 body 加退化分支 + allowed-tools |
| R-B3.3 | agent B | paths 漏 poetry.lock | ✅ 採納 | S4 paths 補 |
| R-B3.4 | agent B | S4 設計 self-consistent | OK | 無 |
| R-B3.5 | agent B | 多 nautilus 套件未處理 | ✅ 採納 | S4 body 加 scope 限制 |
| R-B3.6 | agent B | S1 與既有內容無矛盾 | OK | 無 |
| R-B3.7 | agent B | S2 驗證改反向掃描 | ✅ 採納（當時）→ **lever B 移除** | 歷史記錄 |
| **DR** | **Dry Run** | **22 disable 集中 11 個被 AI 高頻 auto-invoke（732 session 實證）→ 設 disable 會斷自主流程** | **✅ 採納（Critical）** | **lever B 整支移除；S1 決策指引翻轉為「預設不設」** |
