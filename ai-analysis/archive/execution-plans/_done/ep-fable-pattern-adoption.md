# EP: fable-method pattern 借鏡 — AUTH gate 通用化 / TWINS sweep / 決策 flowchart

> **ep_type**: implementation（docs mode — 全為 `.md` 變更，無 `.py` callable）

## 實作總覽

仿造 fable-method 三個 pattern 到 ai-rules：(1) AUTH gate 從 commit 通用化到所有 outward action（rename + 擴張 commit-consent）；(2) TWINS line 強制同類缺陷全專案 sweep（嵌入 fix-test）；(3) 決策 flowchart 選擇性嵌入高分支點 rule（不套整套）。三項同質性高（都是「從 fable 借 pattern」），一個 EP 三段處理。

**架構決策（arch-thinking + deep-thinking）**：AUTH gate 走**路徑 C（rename + 擴張）**——commit-consent.md rename 為 outward-action-consent.md，commit 場景保留「例外：無」最嚴格等級，新增 outward action 框架（reversibility test + AUTH line + 場景表）。不開新 rule（避免 ai-rules「rule 過多 + 無 CI 同步」既有病徵惡化）。

---

## UC 盤點

### Backlog 關聯

- 無對應 Backlog 卡片（本 EP 是 ai-rules 元專案自身演進，非消費端 feature）

### SYSTEM-MAP 影響

- 無 SYSTEM-MAP.md（元專案）

### 掃描範圍

- `rules/commit-consent.md`（被改名標的）
- `rules/AGENTS.md`（rule 分類表 + rule 寫作原則）
- `ai-development-guide.md`（驗證約束引用）
- 11 處引用點：`skills/{CLAUDE,agent-workflow,maintain,metadata-sync,autonomous-execution}` + `commands/{commit,build,metadata-sync}` + `rules/AGENTS.md` + 2 處 `ref-docs/`

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| commit 需用戶確認 | ✅ | `rules/commit-consent.md` | 更新 | rename + 擴張為 outward-action-consent 框架的子場景 |
| outward action（非 commit）需用戶確認 | 🟢 部分覆蓋 | `skills/autonomous-execution/SKILL.md` 紅線清單 | 更新 | 從「只綁 deep-work」升級為通用 rule；autonomous 紅線清單改引用通用 rule |
| fix-test 分類修復 | ✅ | `commands/fix-test.md` | 更新 | 階段 4 後加 TWINS step |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| outward action 通用 consent（reversibility test + AUTH line） | 📋 | `rules/outward-action-consent.md`（rename 自 commit-consent） |
| fix-test TWINS 同類缺陷 sweep | 📋 | `commands/fix-test.md` 階段 4 後新增 step |

### 不追溯清單（歷史分析文檔 + 歸檔 EP，rename 不回填）

rename 後以下檔案仍含 `commit-consent` 字串，**刻意保留**（歷史快照，不追溯）。理由：這些是分析記錄 / 歸檔 EP，不是活規範；追溯會污染歷史語境（當時的設計討論以 `commit-consent` 為名）。

| 檔案 | hits | 性質 | 不追溯理由 |
|------|------|------|-----------|
| `ai-analysis/hermes-agent-synthesis.md` | 5（L17/L38/L86/L115/L136） | 活分析文檔 | Hermes 借鏡分析；L86/L136 建議「擴充 commit-consent」的**建議本身**是歷史記錄，rename 後該建議已由本 EP 落地（擴充為 outward-action-consent），不追溯保留原文以便追溯決策脈絡 |
| `ai-analysis/reports/superpowers/02-sp借鑒到ai-rules.md` | 1 | 分析報告 | superpowers 借鏡分析歷史快照 |
| `ref-docs/Agentic-Design-Patterns-應用分析.md` | 2（L104/L245） | 參考文檔分析 | Agentic design patterns 對照分析歷史快照 |
| `ai-analysis/execution-plans/_done/ep-skill-loading-discipline.md` | 3 | 歸檔 EP | 歷史 EP，已 done |
| `ai-analysis/execution-plans/_done/ep-zcode-migration-gap-closure.md` | 1 | 歸檔 EP | 歷史 EP，已 done |
| `ai-analysis/execution-plans/_done/ep-dev-process-redesign.md` | 1 | 歸檔 EP | 歷史 EP，已 done |

---

## Scenario Matrix

> **docs mode 語境**：checkpoint 是文檔語境驗證（rg 命中 / 條文落地），非 AI 行為驗證（AI 行為留給消費端 use case，非 EP 範圍）。

| # | 場景 | 觸發 | 預期行為 | Checkpoint（文檔語境） | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | commit 場景（既有） | AI 想跑 `git commit` | 展示 message → 等用戶確認（行為不變） | `rg "無例外" rules/outward-action-consent.md` 命中（commit 紅線保留） | commit 需用戶確認 |
| SM-1b | commit 連續授權（第二次） | 同 session 緊接第二次 commit（第一次已授權） | 仍需獨立確認（一次授權 ≠ 永久授權） | `rg "一次授權" rules/outward-action-consent.md` 命中（條文落地） | commit 需用戶確認 |
| SM-2 | 互動 session outward action（新） | AI 想跑 deploy/push/send/live order | 跑 reversibility test → 判 outward → 需 AUTH line（user verbatim quote）→ 無 quote 則列 PENDING | `rg "AUTH: user said" rules/outward-action-consent.md` 命中 + flowchart 條文落地 | outward action 通用 consent |
| SM-2b | AUTH line quote scope 模糊 | user 說「測試」但動作是 live order；或 deploy 後連帶 send notification | quote 不涵蓋該動作 → 列 PENDING | `rg "quote scope" rules/outward-action-consent.md` 命中（quote scope 判準節落地） | outward action 通用 consent |
| SM-3 | autonomous session outward action | deep-work 半夜跑到需 deploy 的 step | **autonomous shortcut**：紅線清單優先（行為枚舉），不跑 reversibility test；跳過 + 記錄 completion report | `rg "autonomous shortcut" rules/outward-action-consent.md` 命中（邊界定義落地） | autonomous 紅線（既有）|
| SM-4 | README 教 deploy 但 user 沒授權（fable s9 原型） | AI 修完 config.json 讀到 README 寫「改完跑 deploy.py」| **documentation ≠ authorization** → 不 deploy → 列 PENDING | `rg "documentation ≠ authorization" rules/outward-action-consent.md` 命中 | outward action 通用 consent |
| SM-5 | fix-test 修完任一類缺陷（A/B/C/D/E） | 階段 4 修完碼或重寫測試通過 | 強制 `TWINS: searched <pattern> - found N other sites` line，N>0 則列後續處理 | `rg "TWINS: searched" commands/fix-test.md` 命中（階段 4.5 條文落地） | fix-test TWINS sweep |
| SM-6 | reversibility test 2 分支決策 | AI 判斷「這動作 outward 嗎？」 | 嵌入 rule 的 ASCII flowchart 引導（2 分支：可觀察 → outward / 純 local → 自主執行；outward 後再判 AUTH line）| `rg "另一個人" rules/outward-action-consent.md` 命中（flowchart 落地） | outward action 通用 consent |

**docs mode 不適用欄位**：
- **錯誤操作**（缺參數、assert fail）：docs mode N/A（純文檔變更無執行時參數）；documentation trap（SM-4）已涵蓋核心錯誤操作類型
- **邊界**：SM-4（README≠auth）、SM-6（reversibility 4 分支）、SM-1b（連續授權）、SM-2b（quote scope）涵蓋核心邊界
- **效能期待差異**：N/A（docs mode 純文檔變更，無執行時效）

---

## 段落劃分原則

- **垂直切片**：S1 是 base rule（被 S2 依賴），S2 引用 S1，S3（TWINS）獨立。
- **依賴順序**：S1 → S2 → S3（S1 rename + 擴張完，S2 才有新引用路徑；S3 TWINS 嵌入 fix-test 與 S1/S2 獨立）。
- **flowchart 歸屬**：reversibility test flowchart 嵌入 S1 產出的 `rules/outward-action-consent.md`，**屬於 S1 的修改要點**（S1 改的就是這個檔）；S3 純留 fix-test TWINS step。原設計「S3 處理 flowchart」會跨段修改 S1 產物，違反段落自足。
- **段落自足**：每段含完整 Context + 修改要點 + 文檔驗證。

---

## 段落 0：全域研究摘要

### 可複用基礎設施

- `rules/commit-consent.md` — 既有 commit consent 硬規則，rename + 擴張標的
- `skills/autonomous-execution/SKILL.md` 紅線清單 — 已有 outward action 雛形（`rm -rf` / `git push --force` / DB DROP / 付費操作），**只綁 deep-work 場景**——互動 session 完全沒這套（真正 gap）
- `commands/fix-test.md` 階段 4 — TWINS step 嵌入點
- `scripts/deploy_agents.py` — neutral rule 部署（frontmatter `harness-scope: neutral` auto-discover）+ 斷 ref 檢測（**只掃 rules/ 內**，不掃 skills/commands/ai-analysis/）
- fable-method `skills/fable-method/SKILL.md` Step 3 AUTH gate 原型：`AUTH: user said "<their exact words>"`
- fable-method `skills/fable-method/SKILL.md` Step 5(c) TWINS check 原型：`TWINS: searched <pattern> - found N other sites`

### 依賴關係與關鍵約束

- commit-consent 被引用掃描結果（`rg "commit-consent"` 全 repo）：
  - **9 個活檔、16 hits**（rename 後須全改指向 outward-action-consent）：
    - `rules/AGENTS.md`（1）
    - `skills/CLAUDE.md`（1）
    - `skills/agent-workflow/SKILL.md`（1）
    - `skills/maintain/SKILL.md`（2）
    - `skills/metadata-sync/SKILL.md`（2）
    - `skills/autonomous-execution/SKILL.md`（3：L40/L47/L72）
    - `commands/commit.md`（2：L138/L156）
    - `commands/build.md`（2：L73/L246）
    - `commands/metadata-sync.md`（2：L45/L79）
  - **6 個不追溯檔案**（見 UC 盤點「不追溯清單」，共 13 hits）：hermes-agent-synthesis / superpowers 借鏡 / ref-docs / _done EP × 3
- `rules/AGENTS.md` 第 51 行 rule 分類表須更新詞條
- `ai-development-guide.md` **0 hits**（無需動）
- `settings.json` / `hooks/` **0 hits**（無需動）
- neutral rule（frontmatter `harness-scope: neutral`）→ rename 後新檔保留 frontmatter 即被 `deploy_agents.py` auto-discover → 部署到三家非 Claude 端（**不需改 script**）

### 風險假設清單

| 假設 | 等級 | 驗證段落 |
|------|------|---------|
| rename 後 `deploy_agents.py` 斷 ref 檢測能抓出漏改 | 🟡 中（**只掃 rules/ 內**，不掃 skills/commands/ — 真實 safety net 是 S2 整合驗證的 `rg → 0 hits`） | S2 驗證 |
| 9 活檔 16 hits 全部可機械替換（無語義分支） | 🟢 低（rg 可枚舉；每檔 hits 數已標） | S2 驗證 |
| AUTH line 在非 commit 場景（live order 等）語義成立 | 🟡 中（消費端多樣；quote scope 判準需定義） | S1 設計 |
| TWINS line 在 fix-test 嵌入不破壞既有 A/B/C/D/E 流程節奏 | 🟢 低（純附加 step，階段 4.5 不動既有 0-4） | S3 驗證 |

無致命等級假設。

---

## 段落 1：rename + 擴張 commit-consent → outward-action-consent

### Context

**UC 引用**：實作「outward action 通用 consent（reversibility test + AUTH line）」

**背景**：commit-consent 是「outward action consent」的嚴格子集。fable-method 的 AUTH gate 證明（round 11 eval）bare Fable 5 在 README 教 deploy 場景有 1/2 run 真的跑去 deploy——documentation ≠ authorization 是核心發現。ai-rules 互動 session 對 live trading order / broker write / DB migration / `git push` / send / delete shared data 完全沒規範（只有 commit + autonomous 場景紅線清單）。

**依賴關係**：本段是 base rule，被 S2（引用點更新）依賴。

**語義約束**：與 S2 共享「commit-consent 符號 rename 為 outward-action-consent」；與 autonomous-execution SKILL 共享「紅線清單是 outward action 場景列舉」。

**基礎設施盤點**：fable-method Step 3 AUTH gate（`AUTH: user said "<quote>"` + documentation ≠ authorization + reversibility test「另一個人/系統在你 undo 前能觀察到嗎」）；ai-rules `commit-consent.md` 既有結構（核心原則 / 強制規則 / 場景表 / 例外）；ai-rules `autonomous-execution` 紅線清單（行為枚舉：`rm -rf` / `git push --force` / DB DROP / 付費操作）。

**依賴錨點**：
- `rules/commit-consent.md` → 定義 `rules/commit-consent.md:1`（整檔 rename）
- 消費端 11 處：`skills/agent-workflow/SKILL.md`、`skills/maintain/SKILL.md`、`skills/metadata-sync/SKILL.md`、`skills/autonomous-execution/SKILL.md`、`skills/CLAUDE.md`、`commands/commit.md`、`commands/build.md`、`commands/metadata-sync.md`、`rules/AGENTS.md:51`、2 處 ref-docs（不追溯）

**技術選型**：rename（非新增 rule）+ 內容擴張。**成功標準**：commit 場景行為 100% 保留 + 新增 outward action 框架 + 零斷 ref。

### 1b. Invariant Impact

無。純文檔變更，不觸及 invariant-bearing 模組（會計/風控/domain service）。

### 修改要點

1. **rename 檔案**：`rules/commit-consent.md` → `rules/outward-action-consent.md`
2. **重寫內容**（保留 commit 「例外：無」最嚴格等級，擴張為通用框架）：
   - 核心原則：從「LLM 絕對不執行 git commit」擴張為「LLM 不執行 outward action，除非用戶明確授權」
   - **reversibility test**（核心新增）：「另一個人或系統能在你 undo 前觀察到嗎？能 → outward → 需 AUTH」
   - **AUTH line 模板**（核心新增）：`AUTH: user said "<their exact words>"`；**documentation ≠ authorization**（README/workflow doc/skill 說 deploy 不算授權）
   - **AUTH line quote scope 判準**（新增節）：user 的 quote 必須**涵蓋該具體動作**，不能是更廣的意圖。例：user 說「測試 strategy」不涵蓋「下 live order」；user 說「跑 deploy」不涵蓋「send notification」。判定：quote 的字面範圍 vs 動作的具體性 — 若需推理才能涵蓋，則不涵蓋 → 列 PENDING
   - **outward action 場景表**（擴張）：commit / push / send / deploy / live trading order / broker write / DB schema change / delete shared data / 付費操作 / 跨 worktree 操作 / 權限變更
   - **commit 專屬段**：保留「例外：無」（commit 永遠需獨立確認，一次授權 ≠ 永久授權）
   - **其他 outward action**：需 AUTH line（user verbatim quote）；無 quote → 列 PENDING（不執行）
   - **autonomous shortcut 節**（新增）：autonomous session（deep-work 等）走紅線清單行為枚舉優先，不跑 reversibility test（紅線清單已枚舉 outward action；reversibility test 是互動 session 的判定機制）。通用 rule 是 source of truth（定義 + 判定），autonomous 紅線清單是 deep-work 場景的快查子集（列最危險不可逆操作），其餘指回通用 rule
   - **source of truth 邊界定義**（新增節）：outward-action-consent rule = 通用定義清單（authoritative）；autonomous-execution 紅線清單 = deep-work 半夜自主場景的快查子集，只列最危險不可逆操作，其餘一律指回通用 rule。未來新增 outward action 時只改通用 rule，紅線清單隨 deep-work 場景需求局部同步
   - 嵌入 **reversibility test ASCII flowchart**（見 §3.2，flowchart 屬 S1 修改要點 — 改的就是這個檔）
3. **保留 frontmatter** `harness-scope: neutral`（跨 harness 部署，auto-discover）
4. **保留 neutral rule 中性化括號註**：既有 `rules/commit-consent.md:45` 的 `（Claude: commands/commit.md）` 括號註格式須保留（rename 後 outward-action-consent 仍引用 commit 命令文檔，須用括號註非跨域 ref；outward action 場景表無對應命令，免）
5. **檔名語義**：檔名 outward-action-consent 反映內容；commit 是其中一節

### 文檔驗證

- `rg "commit-consent" rules/ skills/ commands/ ai-development-guide.md` → 預期 0 hits（全 rename 為 outward-action-consent；不含 ai-analysis/ 不追溯檔）
- `rg "outward-action-consent" rules/ skills/ commands/` → 命中數 ≥ 16（覆蓋原 9 活檔）
- `rg "無例外" rules/outward-action-consent.md` → 命中（commit 場景行為保留驗證）
- `rg "AUTH: user said" rules/outward-action-consent.md` → 命中（AUTH line 條文落地）
- `rg "documentation ≠ authorization" rules/outward-action-consent.md` → 命中
- `rg "quote scope" rules/outward-action-consent.md` → 命中（quote scope 判準節落地）
- `rg "autonomous shortcut" rules/outward-action-consent.md` → 命中（邊界定義落地）
- `rg "另一個人" rules/outward-action-consent.md` → 命中（flowchart 落地）
- `rg "一次授權" rules/outward-action-consent.md` → 命中（連續授權條文落地）
- `uv run python scripts/deploy_agents.py` → exit 0 + 無斷 ref
- `rg "outward-action-consent" ~/.zcode/AGENTS.md ~/.config/opencode/AGENTS.md ~/.codex/AGENTS.md` → 三端 bundle 含新 rule section
- `/consistency rules/outward-action-consent.md` → 自洽、無矛盾

---

## 段落 2：更新 11 處引用 + autonomous-execution 紅線清單引用通用 rule

### Context

**UC 引用**：實作「outward action 通用 consent」的消費端佈線

**背景**：rename 後 11 處引用須改指向 outward-action-consent。其中 autonomous-execution SKILL 紅線清單是關鍵 —— 它已是 outward action 的雛形（`git push --force` / DB DROP / 付費操作），但**只綁 deep-work 場景**，且與新 rule 有重疊。設計：autonomous-execution 紅線清單**保留場景列舉**（deep-work 半夜自主跑的具體禁令），但**引用 outward-action-consent 作為通用定義來源**（reversibility test + AUTH line）。

**依賴關係**：依賴 S1（rule 已 rename）。

**語義約束**：與 S1 共享 rename 符號；與 autonomous-execution 共享「紅線清單是 outward action 場景列舉」。

**基礎設施盤點**：11 處引用點（rg 枚舉）；`rules/AGENTS.md` rule 分類表（第 51 行單行更新）。

**依賴錨點**：
- `skills/autonomous-execution/SKILL.md:40` → 「`git commit`（commit-consent rule...）」rename 為 outward-action-consent
- `skills/autonomous-execution/SKILL.md:47` → 同上（紅線段引用）
- `skills/autonomous-execution/SKILL.md:72` → 黃線段 commit 註解
- `rules/AGENTS.md:51` → rule 分類表詞條

**成功標準**：零斷 ref + autonomous 紅線清單語義不變（行為保留）+ 通用 rule 引用一致。

### 1b. Invariant Impact

無。

### 修改要點

逐檔機械替換 + 語義微調（每檔 hits 數標註，防機械替換漏改）：

| 檔案 | hits | 原文（rg 命中）| 改為 |
|------|------|----------------|------|
| `skills/CLAUDE.md` | 1 | `consent（如 commit-consent）已在 skill 層確保` | `consent（如 outward-action-consent）已在 skill 層確保` |
| `skills/agent-workflow/SKILL.md` | 1 | `[commit-consent](../../rules/commit-consent.md)` | `[outward-action-consent](../../rules/outward-action-consent.md)` |
| `skills/maintain/SKILL.md` | 2 | `commit-consent 豁免` + `遵循 commit-consent 規則` | `outward-action-consent 豁免` + `遵循 outward-action-consent 規則`（語義不變：daily-maintain 🟢 修正隱含同意 commit） |
| `skills/metadata-sync/SKILL.md` | 2 | `commit-consent` × 2 | `outward-action-consent` × 2 |
| `skills/autonomous-execution/SKILL.md` | 3 | `commit-consent rule 明文「例外：無」`（L40）+ `[commit-consent](../../rules/commit-consent.md)` 連結（L47）+ `commit-consent` 連結（L72）| **引用升級**（條款級 → 規則級）：改為 `outward-action-consent rule commit 段「例外：無」`（L40）+ `[outward-action-consent](../../rules/outward-action-consent.md)` 連結（L47/L72）；**新增一行**：「紅線清單是 outward action 的 deep-work 場景列舉（快查子集），通用定義見 [outward-action-consent](../../rules/outward-action-consent.md)」 |
| `commands/commit.md` | 2 | `遵守 commit-consent rule`（L138）+ 命中（L156） | `遵守 outward-action-consent rule（commit 場景）` × 2 |
| `commands/build.md` | 2 | `commit-consent`（L73）+ `commit-consent`（L246） | `outward-action-consent` × 2 |
| `commands/metadata-sync.md` | 2 | `[commit-consent](../rules/commit-consent.md)` × 2 | `[outward-action-consent](../rules/outward-action-consent.md)` × 2 |
| `rules/AGENTS.md` | 1 | L51 `commit-consent \| 🟢 neutral \| commit 需用戶確認（場景化，不引用命令名）` | `outward-action-consent \| 🟢 neutral \| outward action 需用戶授權（commit / deploy / push / send / live order；reversibility test + AUTH line）` |

**不追溯檔案**（見 UC 盤點「不追溯清單」）：hermes-agent-synthesis.md / superpowers / ref-docs / _done EP — 保留原文（歷史快照）。

### 文檔驗證

- `rg "commit-consent" rules/ skills/ commands/ ai-development-guide.md` → 0 hits
- `rg -c "outward-action-consent" rules/ skills/ commands/` → 每檔命中數對照上表（防漏改）
- `rg "無例外" rules/outward-action-consent.md` → 命中（commit 紅線保留）
- `rg "^\\\| Git" skills/autonomous-execution/SKILL.md` → 紅線清單列數不變（行為保留驗證）
- `uv run python scripts/deploy_agents.py` → exit 0
- 三端 bundle 抽查：`rg "outward-action-consent" ~/.zcode/AGENTS.md` → 命中
- `autonomous-execution` 紅線清單 `/consistency` → 行為保留（紅線禁令不變，只是引用源改）

---

## 段落 3：fix-test 嵌入 TWINS step

### Context

**UC 引用**：實作「fix-test TWINS 同類缺陷 sweep」

**背景**：fable-method Step 5(c) 證明（s13 eval）bare Haiku 在 5-copy bug 只修 1/5 就回報 done；強制 `TWINS:` line 後 sweep 全部。ai-rules 的 fix-test 修完 Type A/B/C/D/E 後沒有強制同類 sweep 步驟。TWINS 嵌入 fix-test（非新 rule）—— use case 證明存在再上抽。

**依賴關係**：S3（TWINS 嵌入 fix-test）與 S1/S2 獨立。flowchart 嵌入已挪到 S1（因為改的是 S1 產出的 rule 檔）。

**語義約束**：與 acceptance-evidence「filter trap」正交（filter trap 是反向 — 移除補丁前查 caller；TWINS 是正向 — 修缺陷後查同類）。方向相反、正交不衝突（工具重疊但用途不同：兩者都用 LSP findReferences / rg，但一個往「驗證不能刪」走、一個往「找還沒修」走）。

**基礎設施盤點**：`commands/fix-test.md` 階段 4（Execute + Verify）；fable-method Step 5(c) `TWINS:` line 模板。

**依賴錨點**：
- `commands/fix-test.md:135-143`（階段 4） → 嵌入點（階段 4 後、禁止行為段前）

**成功標準**：fix-test 階段 4 後有 TWINS step + 不破壞既有 A/B/C/D/E 流程（階段 0-4 行為不變）。

### 1b. Invariant Impact

無。

### 修改要點

在 `commands/fix-test.md` 階段 4「Execute + Verify」之後、禁止行為段之前，新增**階段 4.5：Twin Sweep**（編號策略：4.5 插入，不重編既有 0-4 + 禁止行為段；4.5 是子階段語義清晰，不破壞既有流程節奏）：

```markdown
### 階段 4.5：Twin Sweep（修完任一缺陷後強制）

修完 Type A/B/C/D/E 任一類後，搜尋同類缺陷的其他位置。單點修復不是完成。

**強制輸出 line**（必須出現於修復報告）：

    TWINS: searched <pattern> - found <N> other sites: <files, or "none">

- **pattern**：剛修的錯誤構造（rg/LSP 搜尋的精確 pattern）
- **N=0**：完成
- **N>0**：列出位置；建議是否一併修（同一 commit 或分拆由用戶決定）

**搜尋工具**：符號查詢用 LSP `findReferences` / `workspaceSymbol`；文字 pattern 用 rg（工具選擇見 [lsp-navigation](../rules/lsp-navigation.md)）。

**pattern 範例**（依 fix-test 失敗類型）：

| 類型 | pattern 範例 | 搜尋目標 |
|------|-------------|---------|
| A 實作缺陷 | `rg "if x = None"`（漏等號邏輯） | 同類邏輯錯誤 |
| B 契約變更 | `rg "<old_signature>"`（舊 signature 殘留） | 其他用舊契約的 caller |
| C 測試腐化 | LSP `findReferences` on private method | 其他耦合同 private 的測試 |
| D 基礎設施 | `rg "fixture_<name>"` 或 `rg "conftest"` | 同類 fixture 過時 |
| E 測試過時 | `rg "@pytest.mark.<marker>"`（標記的過時意圖） | 其他同類過時測試 |

**與 acceptance-evidence filter trap 的差異**：filter trap 是反向（移除補丁前查 caller 是否阻斷 case）；TWINS 是正向（修缺陷後查同類）。方向相反、正交不衝突（工具重疊但用途不同），並列使用。
```

並更新 fix-test 品質檢查清單，加一條：
- [ ] 修復報告含 `TWINS:` line（階段 4.5）

### 文檔驗證

- `rg "TWINS" commands/fix-test.md` → 命中（階段 4.5 + 品質檢查清單）
- `rg "階段 4.5" commands/fix-test.md` → 命中（子階段插入）
- `/consistency commands/fix-test.md` → 階段編號連續（4 → 4.5 → 禁止行為段）
- fix-test 階段 0-4 行為不變（4.5 是純附加子階段）

---

## flowchart 嵌入 outward-action-consent rule（S1 修改要點的細節補充）

> 歸屬變更（原 S3.2 → 移到 S1）：flowchart 嵌入的就是 S1 產出的 `rules/outward-action-consent.md`，屬 S1 修改要點。原設計放 S3 造成「S3 跨段改 S1 產物」違反段落自足。

在 S1 產出的 `rules/outward-action-consent.md` 內嵌一張 ASCII flowchart（非 Mermaid — ai-rules rules/ 慣例是 ASCII）：

```
即將執行動作
  │
  ▼
另一個人/系統能在你 undo 前觀察到嗎？
  │
  ├─ 否（純 local working tree）→ 可逆 → 自主執行
  │
  └─ 是 → outward action
       │
       ▼
     用戶有明確授權嗎？（AUTH line: user said "<verbatim quote>"）
       │
       ├─ 有 quote 且涵蓋該動作（quote scope 判準見上節）→ 執行 + 報告附 AUTH line
       │
       └─ 無 quote / quote 不涵蓋
            │
            ├─ documentation（README/skill/workflow）教做 → ❌ documentation ≠ authorization
            │
            └─ → 列 PENDING: <action> - awaiting your authorization
```

**commit 場景特殊化**（rule 內專節）：commit 永遠需獨立確認，即使剛授權過上一個 commit（一次授權 ≠ 永久授權）。

**autonomous shortcut**（rule 內專節）：autonomous session（deep-work 等）走紅線清單行為枚舉優先，不跑 reversibility test（紅線清單已枚舉 outward action；reversibility test 是互動 session 的判定機制）。

---

## 收尾步驟

### 1. 模組 instruction 檔 Capabilities + Kanban 更新

- 元專案無 Capabilities 表格；改為 `commands/CLAUDE.md` 命令索引 description 同步：
  - `/fix-test` description 加「含 TWINS 同類缺陷 sweep」
  - `/commit` description 無引用 commit-consent（已確認 0 hits），無需動
- 無 Kanban（元專案）

### 2. SYSTEM-MAP.md 更新

- 無 SYSTEM-MAP.md（元專案）

### 3. instruction 檔更新

- `rules/AGENTS.md` rule 分類表（S2 已處理）+ rule 寫作原則段落（若有提到 commit-consent）→ 同步
- `ai-development-guide.md` **0 hits**（無需動）
- `commands/CLAUDE.md` 命令索引（收尾步驟 1 已處理 fix-test description）

### 4. /audit-test

- docs mode 無測試；跳過（按 execution-plan docs mode 規範）

### 5. 部署驗證（docs mode 特有）

- `uv run python scripts/deploy_agents.py` → exit 0
- 三端 bundle 抽查：
  - `rg "outward-action-consent" ~/.zcode/AGENTS.md` → 命中
  - `rg "outward-action-consent" ~/.config/opencode/AGENTS.md` → 命中
  - `rg "outward-action-consent" ~/.codex/AGENTS.md` → 命中
- Claude 端：`rg "outward-action-consent" ~/.claude/rules/outward-action-consent.md` → 命中（透過 symlink 讀 repo；rename 後 symlink 自動指向新檔名）

### 6. 不追溯檔案標註

以下檔案的 commit-consent 引用**刻意保留**（見 UC 盤點「不追溯清單」），不追溯改名：
- `ai-analysis/hermes-agent-synthesis.md`（5 hits，活分析文檔）
- `ai-analysis/reports/superpowers/02-sp借鑒到ai-rules.md`（1 hit）
- `ref-docs/Agentic-Design-Patterns-應用分析.md`（2 hits）
- `ai-analysis/execution-plans/_done/` 歸檔 EP × 3（5 hits）

本 EP commit message 標註「歷史分析文檔 + 歸檔 EP 的 commit-consent 引用保留」。

---

## 整合驗證（全段完成後）

1. `rg "commit-consent" rules/ skills/ commands/ ai-development-guide.md` → **0 hits**（全 rename；ai-analysis/ + ref-docs/ 不追溯檔案除外，見 UC 盤點）
2. `rg -c "outward-action-consent" rules/ skills/ commands/` → 命中數對照 S2 表格每檔 hits 數（防漏改）
3. `rg "TWINS" commands/fix-test.md` → 命中（階段 4.5 + 檢查清單）
4. `rg "另一個人" rules/outward-action-consent.md` → 命中（flowchart 落地）
5. `rg "無例外" rules/outward-action-consent.md` → 命中（commit 紅線保留）
6. `rg "AUTH: user said" rules/outward-action-consent.md` → 命中
7. `rg "documentation ≠ authorization" rules/outward-action-consent.md` → 命中
8. `rg "quote scope" rules/outward-action-consent.md` → 命中
9. `rg "autonomous shortcut" rules/outward-action-consent.md` → 命中
10. `rg "一次授權" rules/outward-action-consent.md` → 命中
11. `rg "^\\\| Git" skills/autonomous-execution/SKILL.md` → 紅線清單列數不變（行為保留）
12. `uv run python scripts/deploy_agents.py` → exit 0 + 無斷 ref
13. 三端 deployed AGENTS.md 抽查含新 rule section
14. `/consistency rules/outward-action-consent.md` → 自洽
15. `/consistency commands/fix-test.md` → 階段編號連續（4 → 4.5）
16. `/consistency rules/AGENTS.md` → rule 分類表與實際 rule 檔一致

---

## EP Review 區段

**Review 模式**：4 agent 平行 F1-F5 四維度（opus 等級，user override max=4）
**Review 時間**：2026-07-17

### EP Review Findings（獨立 /ep-review，Main LLM 合成）

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| R1 | 🔴 必須修正 | S1 修改要點 4 | `rules/commit-consent.md:50` 行號錯誤——實際檔案只 45 行，括號註 `（Claude: commands/commit.md）` 在 L45（經 Read 全檔查證） | 改為 `:45` | implemented |
| R2 | ℹ️ 提醒 | 收尾步驟 5 | ~~「rename 後 symlink 自動指向新檔名」假設未驗證~~ —— **撤回**：查證 `~/.claude/rules` 是**目錄 symlink**（→ `/Users/ctai/Github/ai-rules/rules`），非每檔各別 symlink。rename 後目錄 symlink 不受影響，Claude 端透過 `~/.claude/rules/outward-action-consent.md` 自動讀到新檔名，無斷裂風險。EP 原文正確 | 無需動；build 仍建議用 `git mv` 保留歷史 | informational |
| R3 | 🟡 建議 | 段落 0 風險假設 | C7 已正確將 deploy_agents.py safety net 降級 🟡；但 EP 對「9 活檔 16 hits 可機械替換」風險 🟢 過樂觀——`autonomous-execution` L40/L72 是 prose context（非 markdown 連結），機械替換會破壞語境 | autonomous-execution row 已標「引用升級（條款級→規則級）」非純機械替換；建議段落 0 風險假設加註「autonomous-execution 3 hits 中 L40/L72 需語義微調非純替換」 | needs-confirmation |
| R4 | ℹ️ 提醒 | 全文 | refs-docs `rules/commit-consent.md:9,37` citation（`ref-docs/Agentic-Design-Patterns-應用分析.md:104`）—— `:9` 與 `:37` 對應檔案實際為「`---` 分隔線」與「`---` 分隔線」，並非內容行；該引用本屬不追溯歷史快照，rename 後更失去語義 | 不追溯處理已涵蓋；build 無需動 | informational |

### Findings 採納清單（20 條，全採納，無不採納）

| # | finding | 採納動作 | 嚴重度 |
|---|---------|---------|--------|
| C1 | hermes-agent-synthesis.md 5 處遺漏（活文件，L86/L136 建議擴充 commit-consent → rename 後斷裂）| UC 盤點新增「不追溯清單」表，顯式列出 hermes + 理由（建議本身是歷史記錄，rename 已由本 EP 落地）| 高 |
| C2 | 路徑 `ref-docs/superpowers/` 不存在 → 實際 `ai-analysis/reports/superpowers/` | 收尾步驟 6 + UC 盤點「不追溯清單」修正路徑 | 高 |
| C3 | 「11 處」計數錯 → 實際 9 活檔 16 hits（+ 不追溯 13 hits）| 段落 0 依賴關係段重寫為精確清單（每檔 hits 數）| 高 |
| C4 | commit.md / build.md 各 2 處（EP 標 1 處低估）| S2 表格每行標 hits 數 | 中 |
| C5 | autonomous-execution 3 處非 2 處（L40/47/72）| S2 表格標 3 hits + 引用升級說明 | 中 |
| C6 | §3.2 flowchart 段落歸屬矛盾（S3「獨立」但又「與 S1 同段」）| flowchart 整段挪到 S1 修改要點；段落劃分原則更新；S3 純留 TWINS | 中 |
| C7 | deploy_agents.py broken-ref 只掃 rules/，風險假設過度樂觀 | 段落 0 風險假設降級 🟢→🟡；真實 safety net 標明是 S2 rg → 0 hits | 中 |
| C8 | SM-5/SM-6 漏 Type D/E（條文說 A/B/C/D/E，SM 只列 A+B/C）| SM-5 合併涵蓋 A/B/C/D/E | 高 |
| C9 | docs mode SM checkpoint 應改文檔語境（rg 命中）非 AI 行為 | Scenario Matrix 加 docs mode 語境註 + 每個 SM checkpoint 改 rg 驗證 | 中 |
| C10 | 漏 `commands/CLAUDE.md` neutral rule 中性化括號註保留 | S1 修改要點加第 4 點（保留 `(Claude: commands/commit.md)` 括號註）| 中 |
| C11 | outward-action-consent vs autonomous 紅線清單 source of truth 邊界 | S1 新增「source of truth 邊界定義」節 | 中 |
| C12 | autonomous-execution 引用「例外：無」條款級引用脆弱 | S2 表格 autonomous-execution row 改「引用升級（條款級 → 規則級）」| 低 |
| C13 | TWINS「不重疊」措辭過強（工具重疊）| S3 語義約束 + 階段 4.5 條文改「正交不衝突（工具重疊但用途不同）」| 低 |
| C14 | commit 連續授權缺 SM（一次授權 ≠ 永久）| 加 SM-1b | 中 |
| C15 | AUTH line quote scope 判準缺 SM | 加 SM-2b + S1 新增「AUTH line quote scope 判準」節 | 中 |
| C16 | SM-3 autonomous vs 通用 rule 邊界（紅線枚舉 vs reversibility test）| S1 新增「autonomous shortcut」節 + SM-3 預期行為明確化 | 中 |
| C17 | 語義保留聲明缺機械驗證 | S1/S2 文檔驗證加 `rg "例外：無"` + `rg "^\| Git"` 機械驗證 | 中 |
| C18 | fix-test 編號策略（4.5 vs 重編）未定 | S3 修改要點明確「4.5 插入，不重編」+ 理由 | 低 |
| C19 | TWINS pattern 各類型範例缺 | 階段 4.5 條文加 pattern 範例表（A/B/C/D/E 各一）| 低 |
| C20 | 收尾步驟 6 ref-docs conditional 措辭 + 路徑錯 | 收尾步驟 1 移除 commit conditional（已確認 0 hits）+ 收尾步驟 6 路徑修正 + 不追溯清單完整列出 | 低 |

### 結構性變更

- **flowchart 歸屬**：原 S3.2 → S1 修改要點（flowchart 改的是 S1 產出的 rule 檔，放 S3 違反段落自足）
- **UC 盤點新增「不追溯清單」表**：6 檔 13 hits 顯式列出 + 不追溯理由（原 EP 只口頭說「ref-docs 2 處」）
- **段落 0 依賴關係精確化**：每檔 hits 數 + 不追溯檔分類
- **風險假設降級**：deploy_agents.py safety net 🟢→🟡（只掃 rules/）

### Review 後結構

S1（rename + 擴張 + flowchart + quote scope + autonomous shortcut + source of truth）→ S2（9 活檔 16 hits 機械替換 + autonomous 引用升級）→ S3（fix-test TWINS step + pattern 範例表）。三段依賴順序不變，但 S1 變厚（吸收 flowchart + 邊界定義）、S3 變薄（純 TWINS）。
