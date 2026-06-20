# EP: agent 產出機械驗證 + scope fence + classifier 處置 + .review 清理

> ⚠️ **ghost-done 註記（2026-06-20）**：本 EP 歸檔 `_done/` 時 S1/S2/S3/S4 實作**皆未落地**（查證：build.md 無 agent 產出 git diff 驗證、agent-workflow 無 scope fence 模板、無 classifier 重試、commit.md 用 `rm -f .review/*.md` 非 per-branch）。實作由 [ep-verify-chain-landing](../ep-verify-chain-landing.md) S2 補落地。

## 動機（self-contained 背景）

parallel agent 的自述是 L2（同義反覆風險 — agent 寫報告描述自己的作為），缺 L1 機械驗證，曾釀嚴重摩擦：**agent 稱「零修改」、`git diff` 揭露實際有改 + scope-creep（改了 prompt 沙盒外的 `component_base`）差點直接 ship**，靠用戶手動 `/code-review` 才抓到（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-16-log-refactoring-agent-verification.md` §2.2，本 EP 簡稱 #7）。同一類工作模式另有兩個縫隙：

- **classifier unavailable 無處置**（`2026-06-17-subagent-classifier-and-review-rm.md`，#11）：`/build` 階段 4 spawn 2 個 Explore agent，因 `glm-5.2[1m]` safety classifier **間歇** unavailable → 只回警告 note 無 findings → Agent Review 整批失敗，AI 直接降級主 LLM 自審（丟失獨立 review）。事後重 spawn 同 2 agent 都成功 → 確認間歇性，本該重試。
- **`rm -f .review/*.md` 誤刪他 branch**（#11）：`/commit` 階段 6 照指令刪 `.review/` 全部，但 `.review/` 含多 branch（backbone/paper-trading/replay 都 tracked）→ 誤刪他 branch review，靠 `git checkout HEAD -- .review/` 恢復。

**既有覆蓋的不足**：[agent-workflow](../../skills/agent-workflow/SKILL.md) `:74-80`「審查 Agent 產出（不要假設正確）」、`:146-153` 常見失敗模式「信任未驗證」都是**泛指**，沒有「`git diff` 機械比對 agent 自述」的具體步驟，也沒有 scope fence 的 negative-space prompt 模板。`:114-122` Auto Mode 只提 classifier「反覆阻擋 → 中止」，沒提 unavailable（間歇）的重試。[acceptance-evidence](../../rules/acceptance-evidence.md) 談「AI 同寫 test+impl 證據獨立性塌縮」，沒落到「agent 自述 vs git」的機械驗證。

**本 EP 範圍**（#7 的 2.2 產出驗證 + 2.5 scope fence；#11 全）：S1 build post-segment 產出驗證、S2 scope fence 模板、S3 classifier 處置、S4 .review per-branch。**Scope out**：#7 的 2.3 `/code-review` 強制（cross-ref review-pipeline EP）、2.4 L4 runtime 分級（屬 acceptance-evidence，獨立）、2.1 handoff 路由（邊緣）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | build 階段4 後 post-segment agent 產出機械驗證（git diff vs 自述 + scope-creep） | 無 |
| S2 | agent-workflow scope fence prompt 模板（negative-space） | 無 |
| S3 | classifier unavailable 偵測 + 重試/降級 | 無 |
| S4 | commit `.review` per-branch 清除 | 無 |

四段獨立、各自可驗收。S1+S2 是「產出驗證 + 預防 scope-creep」的攻守兩面；S3/S4 是同類工作模式的另外兩個縫隙。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（本 EP 源自 #7 + #11 兩筆 flow-feedback）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過）。

### 掃描範圍
- [commands/build.md](../../commands/build.md)（階段 4 Agent Review Cycle，S1/S3 落點）、[skills/agent-workflow/SKILL.md](../../skills/agent-workflow/SKILL.md)（S2 scope fence、S3 classifier）、[commands/commit.md](../../commands/commit.md)（`:173` .review 清除，S4）、[rules/model-routing.md](../../rules/model-routing.md)（S3 classifier 風險標註）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| Agent Review Cycle（2-perspective code review） | `commands/build.md` 階段 4 | ✅ → S1 補 post-segment 產出驗證；S3 補 classifier 處置 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| agent 產出機械驗證（git diff vs 自述 + scope-creep） | 📋 | `commands/build.md` 階段 4 後（S1） |
| scope fence prompt 模板（negative-space） | 📋 | `skills/agent-workflow/SKILL.md`（S2） |
| `.review` per-branch 清除 | 📋 | `commands/commit.md:173`（S4） |

---

## Scenario Matrix（中型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | parallel agent 段結束 | build 階段 4 平行 agent 回報 | 機械 `git diff --name-only` + 比對各 agent 自述「改哪些檔/幾處」；flag「稱零修改但 git 顯示有改」mismatch | 無 | 產出驗證 |
| SM-2 | agent scope-creep | agent 改了 prompt 指定 scope 外的檔 | diff 範圍比對 prompt scope → flag 超出 | 無 | 產出驗證 |
| SM-3 | classifier 間歇 unavailable | spawn agent 收 classifier unavailable note | **先重試 spawn**（間歇常成功）→ 成功則續 | 無 | classifier 處置 |
| SM-4 | classifier 持續 unavailable | 重試仍失敗 | 降級主 LLM 自審 + **顯式標記 fallback**（警示獨立 review 丟失） | 無 | classifier 處置 |
| SM-5 | commit 清 `.review` | `/commit` 階段 6 | `ls .review/` 確認；多 branch → 只清當前 branch（`.review/<branch>.md`）；單 branch 才 `rm *` | `git checkout HEAD -- .review/` | .review 清除 |

---

## S1: build post-segment agent 產出機械驗證

### Context
- **背景**：build 階段 4 Agent Review Cycle（[build.md](../../commands/build.md) `:138-163`）是 review code **品質**（2-perspective），但**不比對 agent 自述 vs git**。agent 自述是 L2（同義反覆風險），`git diff` 是 L1 機械證據。#7 實證：Agent 2/3 稱「零修改」，`git diff --stat` 揭露 trading_dashboard(+9)/trajectory_viewer(+5) 有改、component_base 丟 callback 名（scope-creep）— 沒手動 git diff 就會 ship。
- **UC 引用**：更新既有「Agent Review Cycle」+ 新增「agent 產出機械驗證」
- **依賴**：無
- **語義約束**：與 S2（scope fence 預防）共享「agent 產出是 L2，git diff 是 L1」的證據階層 — S1 是事後驗證、S2 是事前 prompt 預防，兩者攻守
- **依賴錨點**：`commands/build.md:138-163`（Agent Review Cycle，post-segment 驗證加在階段 4 agent 回報後、review 前）
- **成功標準**：
  - [ ] 階段 4 平行 agent 回報後，機械跑 `git diff --name-only` 列實際變更檔
  - [ ] 比對各 agent 自述「改了哪些檔 / 幾處」vs git 實際 → flag mismatch（稱零修改但有改、稱改 N 處但 git 顯示 M 處）
  - [ ] scope-creep 偵測：每個 agent 編輯檔是否超出其 prompt 指定 scope → flag 超出（附 agent prompt scope 引用）
  - [ ] mismatch / scope-creep → 列為 finding 進 Agent Review（不靜默採信自述）

### 修改要點
1. **`commands/build.md` 階段 4 Agent Review Cycle 段**，在「平行 agent 回報」後加 post-segment 驗證子步驟：
   - `git diff --name-only` 列實際變更檔（機械事實）
   - 比對各 agent 自述 vs git（mismatch flag）
   - scope-creep：diff 檔 vs agent prompt 指定 scope（超出 flag）
   - 原則引用：「agent 自述是 L2，git diff 是 L1（[acceptance-evidence](../../rules/acceptance-evidence.md)）— mismatch 不靜默採信」
2. 不新增獨立命令（#7 傾向 post-segment phase 而非 `/verify-agent-edits`，與既有 build 流程整合）

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "git diff --name-only|scope-creep|自述.*git|mismatch" commands/build.md` → 命中
- **`/consistency`**：跑 `commands/build.md`
- **模擬（SM-1）**：給「Agent 稱零修改、git diff 顯示 +9」→ 確認 flag mismatch 為 finding
- **模擬（SM-2）**：給「agent prompt 限 except 區塊、diff 顯示改了 component_base」→ 確認 flag scope-creep

---

## S2: agent-workflow scope fence prompt 模板（negative-space）

### Context
- **背景**：#7 §2.5 — 機械任務（rename / 補 log）的 agent prompt 只有「做什麼」無「不碰什麼」。4 個 agent 各自找到本來就有 Logger 的區塊「順手重構」（改 severity / 合併 / 丟 callback 名），需 4 處 pure-revert。agent-workflow `:74-80` 談 PoC→Implement 流程，無 negative-space scope fence 模板。
- **UC 引用**：新增「scope fence prompt 模板」
- **依賴**：無（與 S1 攻守：S2 事前預防、S1 事後驗證）
- **語義約束**：scope fence 是「機械任務專用」prompt 結構（rename / 補 log / format），非常規任務（設計、實作）不強制
- **依賴錨點**：`skills/agent-workflow/SKILL.md:74-80`（PoC→Implement 流程，scope fence 模板加這之後或獨立子段）
- **成功標準**：
  - [ ] agent-workflow 新增 scope fence 模板，機械任務 agent prompt 必含：
    - **DO NOT** modify blocks that already contain `<pattern>`（例：`Logger.` 已存在的 except 塊）
    - 只 touch 符合 `<criteria>` 的區塊（例：silent `except: pass` 或 print-only）
    - 完成後自驗：`rg <pattern> <edited_file>` 確認沒碰不該碰的
  - [ ] 模板標註「機械任務（rename/補 log/format）適用；設計/實作任務不強制」

### 修改要點
1. **`skills/agent-workflow/SKILL.md`** 新增「Scope Fence（機械任務 prompt 模板）」子段（緊鄰 PoC→Implement 流程）：
   - negative-space 三要素（DO NOT pattern / 只 touch criteria / 完成後 rg 自驗）
   - 適用判準（機械任務 vs 設計任務）
   - 反例（#7：4 agent 各自「順手重構」已有 Logger 的塊 → pure-revert）

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "scope fence|negative-space|DO NOT modify|機械任務" skills/agent-workflow/SKILL.md` → 命中
- **`/consistency`**：跑 `skills/agent-workflow/SKILL.md`
- **模擬**：給「機械任務：補 Logger 到 silent except 塊」→ 確認 prompt 含 DO NOT（已有 Logger 的塊）+ 完成後 rg 自驗

---

## S3: classifier unavailable 偵測 + 重試/降級

### Context
- **背景**：#11 — classifier 間歇 unavailable 時，build 階段 4 流程沒定義「這是 review 失敗 → 該重試或降級」，AI 自行降級（丟失獨立 review）。agent-workflow `:114-122` Auto Mode 只提 classifier「反覆阻擋 → 中止」（那是 classifier **主動擋**），沒提 classifier **unavailable**（服務端間歇故障）的重試。model-routing 純講 model 分派，無 classifier 風險標註。
- **UC 引用**：更新既有「Agent Review Cycle」+ classifier 處置
- **依賴**：無
- **語義約束**：classifier unavailable（服務端間歇）≠ classifier 阻擋（主動擋 scope 升級）— 兩者處置不同：unavailable 重試、阻擋中止
- **依賴錨點**：`skills/agent-workflow/SKILL.md:114-122`（Auto Mode classifier 段）、`commands/build.md` 階段 4、`rules/model-routing.md`
- **成功標準**：
  - [ ] build 階段 4 / agent-workflow 明確「偵測 classifier unavailable note → **先重試 spawn**（間歇常成功）→ 仍失敗才降級主 LLM 自審 + 顯式標記 fallback（警示獨立 review 丟失）」
  - [ ] `rules/model-routing.md` 補「GLM / 非 Claude model harness 的 classifier 間歇 unavailable 是已知風險 → spawn 收 note 時主動重試」（讓 LLM 知道是已知問題而重試，非異常）
  - [ ] 區分 classifier unavailable（重試）vs classifier 阻擋（中止，既有 `:122`）

### 修改要點
1. **`commands/build.md` 階段 4** + **`skills/agent-workflow/SKILL.md`**：加 classifier 處置分支 — unavailable → 重試 spawn（≤2 次）→ 仍失敗降級 + 標記 fallback
2. **`rules/model-routing.md`**：補 classifier 間歇風險段（GLM harness 已知問題，重試是正解）
3. 區分 unavailable（重試）/ 阻擋（中止，既有不動）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "classifier unavailable|重試 spawn|降級.*fallback" commands/build.md skills/agent-workflow/SKILL.md` → 命中
- **rg 閘門**：`rg "classifier.*間歇|unavailable" rules/model-routing.md` → 命中
- **`/consistency`**：跑三檔
- **模擬（SM-3）**：給「spawn 收 classifier unavailable note」→ 確認重試 spawn
- **模擬（SM-4）**：給「重試仍 unavailable」→ 確認降級 + 標記 fallback（非靜默丟失）

---

## S4: commit `.review` per-branch 清除

### Context
- **背景**：#11 — `/commit` 階段 6 `rm -f .review/*.md`（[commit.md](../../commands/commit.md) `:173`）刪 `.review/` 全部，但 `.review/` 可能含多 branch（per-branch tracked，歷史遺留）→ 誤刪他 branch review。
- **UC 引用**：新增「`.review` per-branch 清除」
- **依賴**：無
- **語義約束**：清除針對「當前 branch 的 review 產物」，非「整個 `.review/` 目錄」
- **依賴錨點**：`commands/commit.md:173`（rm .review 段）、`:74-76`（.review 工作流說明）
- **成功標準**：
  - [ ] `:173` 改「`ls .review/` 確認；多 branch → 只清當前 branch `.review/<current-branch>.md`；確認只剩當前 branch 才 `rm *.md`」
  - [ ] 保留「`.review/` 目錄供下次 review 直接寫入」（既有，不動）

### 修改要點
1. **`commands/commit.md:173`**：`rm -f .review/*.md` → `ls .review/` 確認多 branch → per-branch 清除（只清當前 branch 或確認單 branch 才 `rm *`）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "rm -f \.review/\*\.md" commands/commit.md` → 0 hits（舊指令清除）；`rg "per-branch|ls \.review|當前 branch" commands/commit.md` → 命中
- **`/consistency`**：跑 `commands/commit.md`
- **模擬（SM-5）**：給「`.review/` 含 backbone/paper-trading/replay 三檔，當前 paper-trading」→ 確認只清 paper-trading.md

---

## 收尾

- **受影響命令/skill 行為已反映**：build（post-segment 驗證 + classifier 處置）、agent-workflow（scope fence + classifier）、commit（.review per-branch）、model-routing（classifier 風險）— `commands/CLAUDE.md` / `skills/CLAUDE.md` 索引 description 同步。
- **Scope out**：#7 的 2.3 `/code-review` 強制（cross-ref review-pipeline EP，同屬「review 何時觸發」）、2.4 L4 runtime 分級（屬 acceptance-evidence 證據階層，獨立 EP）、2.1 handoff 路由（邊緣，handoff 慣例非命令缺陷）。
- **風險**：S1 post-segment 驗證增加 build 步驟，可能拖慢。緩解：純機械（`git diff --name-only` + 比對），秒級；且 mismatch/scope-creep 是高 signal（#7 實證差點 ship）。
