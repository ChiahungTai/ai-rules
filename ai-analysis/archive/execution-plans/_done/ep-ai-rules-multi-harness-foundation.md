# EP: ai-rules 多 harness foundation（dogfood）

> **ep_type**: implementation
> **mode**: docs（變更全為 `.md`，無 `.py` callable；驗證改文檔驗證）
> **parent spec**: [`ai-analysis/specs/ai-rules-multi-harness-foundation-spec.md`](../specs/ai-rules-multi-harness-foundation-spec.md)
> **規模**: 🔴 大型（跨核心 + 單向門：原始檔命名 + 全域載入鏈）

> **🔴 架構修正（B）— supersedes 原 S1/S2 設計**：原 S1 把全域指南（`ai-development-guide.md`）改名佔住 root `AGENTS.md`，**conflation 了兩個角色**（ai-rules 作「專案」有自己的指令 vs 作「全域 source」提供跨專案指南）。矯正為架構 B：
> - **全域指南** = `ai-development-guide.md`（**還原原名**，獨立檔）→ 部署 `~/.{claude/CLAUDE.md, zcode/AGENTS.md, .config/opencode/AGENTS.md}`（所有專案載入）
> - **ai-rules 專案指令** = root `AGENTS.md`（專案 source，從原 CLAUDE.md repo-nav 移來）+ `CLAUDE.md`（`@AGENTS.md` wrapper）
> - **各司其職**：開 ai-rules 在任 harness = 全域指南（`~/.harness/`）+ 專案 AGENTS.md（repo root）兩份獨立。原 S1/S2 段落的舊模型（AGENTS.md=全域指南）已過時，以本修正為準。
> - **已落地**：Phase 1 還原 rename（`git checkout b29ad71^`）+ Phase 2 建專案 AGENTS.md + Phase 3 `instruction-writing.md` 補「全域指南 ≠ 專案 AGENTS.md」區分。S3 雙檔模式（專案層）仍成立。S4 dogfood 待跑。

## 實作總覽

ai-rules 自身 dogfood 成 AGENTS.md-first + 多 harness 可讀，並把「成為多 harness」內化進 CLAUDE.md 相關 skills/commands。四段：① 全域層（rename + symlink）② 專案層（root CLAUDE.md → @AGENTS.md）③ 工具 harness-neutral 化 ④ dogfood 驗證。完成後 mosaic thin EP 才消費此能力。

---

## UC 盤點（docs mode：受影響命令/rules 清單）

### 受影響面（掃描結果）

| 類別 | 對象 |
|------|------|
| **入口檔（本 EP 改動）** | `ai-development-guide.md`（→ rename `AGENTS.md`）、root `CLAUDE.md` |
| **CLAUDE.md 治理工具（harness-neutral 化）** | `rules/instruction-writing.md`、`commands/instruction/{init,clean,sync,distill}.md`、`skills/CLAUDE.md`、`commands/CLAUDE.md` |
| **rename ripple（機械更新引用）** | `rules/{progressive-validation,acceptance-evidence,code-edit-constraints}.md`、`commands/{build,doc-health,execution-plan}.md`、`skills/metadata-sync/SKILL.md`、`ref-docs/Agentic-Design-Patterns-應用分析.md` |
| **全域部署** | `~/.claude/CLAUDE.md`（既有 symlink 重建）、`~/.zcode/AGENTS.md`（新 symlink）、`~/.config/opencode/AGENTS.md`（新，需 mkdir） |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| ai-rules 全域規則可被多 harness 讀取（UC-1） | 📋 | `AGENTS.md`（rename）+ 三 harness 全域 symlink |
| ai-rules 自身專案指令 harness-neutral（UC-2） | 📋 | root `CLAUDE.md` → `@AGENTS.md` + Claude 專屬 repo-nav |
| CLAUDE.md 相關 skills/commands AGENTS.md-aware（UC-3） | 📋 | `instruction-writing.md`、`/instruction:*`、`skills|commands/CLAUDE.md` |
| 跨 harness 可讀性可驗證（UC-4） | 📋 | dogfood ZCode/OpenCode 實跑 |

### Backlog 關聯

`.kanban/Backlog/` 存在。**自動建卡**（收尾段執行）：本 EP 整體追蹤卡 + UC-1~4 各一張（若尚未有）。

### SYSTEM-MAP 影響

ai-rules 為元專案、無 SYSTEM-MAP.md → 跳過（正當跳過：元專案無功能生命週期）。

---

## Scenario Matrix（docs mode：觸發/預期改文檔語境）

| # | 場景 | 觸發 | 預期行為（文檔/載入語境） | 對應能力 |
|---|------|------|---------|---------|
| SM-1 | ZCode 讀到全域 | ZCode 啟動讀 `~/.zcode/AGENTS.md` | symlink 通 → 讀到 neutral 全域規則 | UC-1 |
| SM-2 | OpenCode 讀到 | OpenCode 啟動 | `~/.config/opencode/AGENTS.md` symlink 通 → 讀到 | UC-1 |
| SM-3 | Claude 不退化 | Claude 讀 `~/.claude/CLAUDE.md` / root `CLAUDE.md` | `@AGENTS.md` 展開 + repo-nav → 全內容讀到，`/build``/commit` 行為不變 | UC-2/3 |
| SM-4 | rename ripple 無斷裂 | 改名 `ai-development-guide.md`→`AGENTS.md` | 9 個引用檔全更新；`rg "ai-development-guide"` 0 殘留（或僅刻意保留的歷史引用） | UC-1 |
| SM-5 | neutral 純度 | 寫入 Claude 專用 body 散文進 AGENTS.md | `instruction-writing.md` 約定 + `/instruction:sync` 擋下 | UC-3 |
| SM-6 | dogfood 行為生效 | ZCode/OpenCode 開 ai-rules repo | 代表性規則（fd 不用 find）在 agent 行為觀察到 | UC-4 |

---

## 段落 0：全域研究 + Ask First 決策

### 研究摘要

- **可複用基礎設施**：`@` transclusion 機制權威在 `rules/instruction-writing.md`（17 處 CLAUDE.md 引用）+ `skills/CLAUDE.md`——這兩檔是「如何寫 instruction file」的單一真相源，harness-neutral 化的核心。
- **既有 symlink 全貌**（已查證）：`~/.claude/` 有 6 條 symlink 指向 ai-rules（CLAUDE.md / rules / skills / commands / agents / settings.json）。**改名只斷 `~/.claude/CLAUDE.md` 一條**（唯一指到 `ai-development-guide.md`）；其餘 5 條目標非改名檔，不受影響。
- **@-ref 對 Claude 仍有效**：`~/.claude/rules` → `ai-rules/rules` symlink 存在 → AGENTS.md 內 `@~/.claude/rules/X.md` 對 Claude 仍 resolve（重建 CLAUDE.md symlink 後零退化）；對 ZCode/OpenCode 是不展開的斷裂文字（已知 scope，用戶接受「Claude 有客製化」）。
- **風險假設**：① rename ripple **12 活躍檔**（段 0 作者 `rg | head` 截斷曾漏算為 9，ai2 /ep-review 校正）② CLAUDE.md 引用面廣但多屬「合法提及」（段 3 逐類區分，非全替換）③ ZCode/OpenCode 是否真讀 symlink + 規則生效（段 4 dogfood 驗）④ `~/.zcode/AGENTS.md` 已是實體 copy 檔（7987B，非 symlink，已驗），段 1 需先處理。

### 🔴 Ask First 決策（build 前必確認）：root `AGENTS.md` 歸屬

**背景**：ai-rules「既是專案又是全域 source」雙重身份——root 同時有專案 guide（root `CLAUDE.md`，repo 結構導航）與全域 guide（`ai-development-guide.md`，跨專案 dev 原則）。兩者都想當 root `AGENTS.md`。

**EP 採用決策（待你 confirm）**：
- **`AGENTS.md` = rename 自 `ai-development-guide.md`**（全域規則主體 = 通用 dev 原則；含 `@~/.claude/rules/*` 機制引用——對 Claude 仍有效（rules symlink），非-Claude 為已知 scope 取捨，**不強制 strip**，見段 1 要點 2）
- **root `CLAUDE.md` 保留 = repo-nav（Claude-specific）+ `@AGENTS.md`**（把全域規則拉進 Claude session）
- **角色分工**：`AGENTS.md`=neutral core（三家讀、部署全域）；`CLAUDE.md`=Claude 專屬 repo-nav（ai-rules 圍繞 Claude Code 組織：skills symlink `~/.claude/skills`、commands 是 slash command——本質 Claude-flavored，留 CLAUDE.md 合理）

**為何不碰撞**：兩檔角色不同——AGENTS.md 是 neutral 規則內容、CLAUDE.md 是 Claude 專屬導航。mosaic 無此問題（只有專案 guide → 單一 AGENTS.md）。

**確認此決策後**段 1-2 才動。若你要不同歸屬（例：repo-nav 也 neutral 化進 AGENTS.md），段 2 改。

---

## 段落 1：全域層 — rename + 三 harness symlink（UC-1）

### Context
- **UC 引用**：實作「ai-rules 全域規則可被多 harness 讀取」
- **依賴**：段落 0 Ask First 決策確認；無跨段依賴（可最先做）
- **語義約束**：與 S2 共享「AGENTS.md = neutral source」假設

### 修改要點（docs mode，無 pseudo code）
1. **rename**：`ai-development-guide.md` → `AGENTS.md`（`git mv`）
2. **@-ref 處理（降級：非阻塞）**：`ai-development-guide.md` 含 `@~/.claude/rules/*`、`~/.claude` 路徑、CLAUDE.md auto-load 語句（L3/5/41/58/118）。**對 Claude 仍有效**（`~/.claude/rules` symlink 解析，改名不影響 rules symlink）→ **不強制 strip**（用戶接受非-Claude 拿原則級、Claude 有客製化）。可選清理：把斷裂 @ 文字標注「(Claude only)」讓 ZCode/OpenCode 讀時不混淆——視段 4 dogfood 觀測決定，**非 build 阻塞**。
3. **symlink 處理**（改名只斷 1 條；`~/.claude/{rules,skills,commands,agents,settings.json}` 5 條不動）：
   - **重建** `~/.claude/CLAUDE.md` → `ai-rules/AGENTS.md`（唯一斷裂的 symlink；`ln -sf`）
   - **`~/.zcode/AGENTS.md` 已是實體 copy**（7987B，非 symlink，已驗）→ 先 `diff ~/.zcode/AGENTS.md ai-rules/AGENTS.md` 確認一致 → 用戶確認後刪除 → `ln -s ai-rules/AGENTS.md ~/.zcode/AGENTS.md` 重建為 symlink（**勿直接 `ln -sf` 覆蓋實體檔，可能埋用戶手改內容**）
   - **新增** `mkdir -p ~/.config/opencode && ln -s ai-rules/AGENTS.md ~/.config/opencode/AGENTS.md`
4. **rename ripple（12 活躍檔機械更新）**：`rg -l "ai-development-guide"`（排除 `_done/` 歸檔 + 本 EP/spec 自身）逐檔判讀——描述 symlink 關係的更新為 `AGENTS.md`；歷史引用（如應用分析）保留或註記。活躍命中：`rules/{acceptance-evidence,code-edit-constraints,progressive-validation}.md`、`commands/{build,commit,doc-health,execution-plan,spec}.md`、`skills/{arch-thinking,metadata-sync}/SKILL.md`、`ref-docs/Agentic-Design-Patterns-應用分析.md`。目標：`rg "ai-development-guide"` 僅剩 `_done/` 歸檔 + 刻意保留項

### 驗證（文檔驗證）
- `rg "ai-development-guide" rules/ commands/ skills/ ref-docs/` → 0 活躍殘留（`_done/` 歸檔除外）
- 三 harness symlink：`readlink -f ~/.claude/CLAUDE.md ~/.zcode/AGENTS.md ~/.config/opencode/AGENTS.md` 均解析到 `ai-rules/AGENTS.md`，**且 `diff` 內容一致**（不只 readlink——`~/.zcode` 曾是 copy，須確認真為 symlink 且內容同步）
- Claude 不退化：開 Claude session 讀 `~/.claude/CLAUDE.md` → `@~/.claude/rules/*` 仍展開（rules symlink 在）

---

## 段落 2：專案層 dogfood — root CLAUDE.md → @AGENTS.md + repo-nav（UC-2）

### Context
- **UC 引用**：實作「ai-rules 自身專案指令 harness-neutral」
- **依賴**：S1 完成（AGENTS.md 存在）；段落 0 決策的「CLAUDE.md = repo-nav + @AGENTS.md」
- **語義約束**：與 S1 共享 AGENTS.md 為 neutral source

### 修改要點
1. **root `CLAUDE.md` 重組**：
   - 開頭加 `@AGENTS.md`（拉入全域規則給 Claude session）
   - 保留 repo-nav 內容（專案結構、載體選擇、寫作治理——Claude-specific，描述 ai-rules 圍繞 Claude Code 的組織）
   - 移除任何與 AGENTS.md 重複的 neutral 內容（避免 duplicate → drift）
2. **區隔確認**：CLAUDE.md 剩下的都是 Claude-specific（slash command 組織、`~/.claude` symlink 描述、hook 機制）——若殘留 neutral 內容，移到 AGENTS.md

### 驗證（文檔驗證 + Claude 載入）
- root `CLAUDE.md` 含 `@AGENTS.md` 行
- `rg` 確認 CLAUDE.md 無與 AGENTS.md 重複的 neutral 段落
- Claude session 開 ai-rules repo → 確認 `@AGENTS.md` 展開、全域規則可見（SM-3）

---

## 段落 3：CLAUDE.md 治理工具 harness-neutral 化（UC-3）

### Context
- **UC 引用**：實作「CLAUDE.md 相關 skills/commands AGENTS.md-aware」
- **依賴**：S1/S2（新結構成立，工具才能治理它）
- **語義約束**：本段確立「如何寫/治理 instruction file」的新約定，下游所有寫作遵循

### 修改要點（關鍵區分：非「全替換 CLAUDE.md→AGENTS.md」）

**原則**：區分兩類 CLAUDE.md 引用——
- **「假設 CLAUDE.md 是唯一入口」類**（需改）：改為 AGENTS.md-first + CLAUDE.md 為 wrapper 的描述
- **「合法對 CLAUDE.md 操作」類**（保留）：如「更新專案 CLAUDE.md」仍是有效動作（CLAUDE.md 仍存在為 wrapper/nav）

**逐檔**：
1. **`rules/instruction-writing.md`**（17 引用，@ 機制權威）——核心：
   - 新增/改：「instruction file 雙檔模式」：`AGENTS.md`（source, neutral）+ `CLAUDE.md`（`@AGENTS.md` wrapper + Claude 專屬）
   - 釐清：`@` transclusion **Claude 專用**（CLAUDE.md 才展開；AGENTS.md 不展開；ZCode 不展開 @import）
   - 釐清：neutral 純度（AGENTS.md body 無 Claude 散文；frontmatter 欄位可容忍）
   - 「CLAUDE.md 是唯一入口」假設句 → 改為「AGENTS.md 為 source、CLAUDE.md 為 Claude wrapper」
2. **`commands/instruction/init.md`**（25 引用，產生 CLAUDE.md）：產出邏輯改為「產 `AGENTS.md`（neutral）+ 選擇性 thin `CLAUDE.md`（@wrapper）」
3. **`commands/instruction/clean.md`**（32 引用）：清理對象加 `AGENTS.md`（neutral 純度檢查：擋 Claude body 散文）
4. **`commands/instruction/sync.md`**（10 引用）：doc↔code sync 對象含 `AGENTS.md`
5. **`commands/instruction/distill.md`**：蒸餾對象 `AGENTS.md`
6. **`skills/CLAUDE.md` + `commands/CLAUDE.md`**（spec 文檔）：更新「skill/command 寫作規範」為 AGENTS.md-aware（入口檔描述、@ 機制釐清）

### 驗證（文檔驗證）
- `rg "CLAUDE\.md 是唯一|CLAUDE\.md 是.*入口" rules/ commands/ skills/` → 0（假設句已改）
- `instruction-writing.md` 含「AGENTS.md 為 source」「@ 是 Claude 專用」「neutral 純度」三要素
- `/instruction:init`、`/instruction:clean`、`/instruction:sync` description 對象含 AGENTS.md
- **抽樣**：隨機挑 3 個非工具檔的 CLAUDE.md 引用，確認屬「合法提及」（保留正確），證明非過度替換

---

## 段落 4：dogfood 驗證（UC-4）

### Context
- **UC 引用**：實作「跨 harness 可讀性可驗證」
- **依賴**：S1-S3 全完成
- **語義約束**：本段是 EP 成功條件的 empirical 驗證（非文檔檢查）

### 修改要點（POC/實跑，非文檔）
1. **ZCode dogfood（具體觸發，非被動觀察）**：`~/.zcode/AGENTS.md` symlink 通（S1）→ 在 ZCode 開 ai-rules repo → 設計**可重現觸發**驗代表性規則生效：
   - 請 agent「列出 rules/ 目錄」→ 觀察是否用 `fd` 而非 `find`（規則：fd 不用 find）
   - 請 agent「跑某個 .py」→ 觀察是否用 `uv run python` 而非 `python`（規則：uv run）
   - 觀察 agent 是否避開 `python -c` 跨行 `#`（規則：bash-hard-rules）
2. **OpenCode dogfood**：同上觸發（`~/.config/opencode/AGENTS.md`）→ 觀察 fallback 讀取 + 同三規則生效
3. **Claude 不退化**：`/build`、`/commit` 在 Claude Code 跑 ai-rules → 行為不變（`@AGENTS.md` 展開完整 + `@~/.claude/rules/*` 仍 resolve）
4. **記錄觀測**：寫進 EP review 區段或 flow-feedback（ZCode/OpenCode 讀 symlink 行為、各規則生效/不生效、silent-success 訊號）

### 驗證（empirical，acceptance-evidence L4-L6）
- ZCode：**≥1 代表性規則在觸發情境中生效**（fd/uv-run/python-c 三選一以上，agent 行為可觀察）——非只「檔案存在」
- OpenCode：同
- Claude：`/build`/`/commit` 行為不變
- **失敗訊號**：檔案在但觸發後 agent 不遵循（用 find、用 python、跨行 #）→ silent success → 記錄並回饋（是否 @-ref 斷裂致規則沒載到、或該 harness 讀取機制不同）

---

## 整合策略

- **順序**：S0 決策確認 → S1（rename+symlink）→ S2（CLAUDE.md 重組）→ S3（工具 neutral 化）→ S4（dogfood）。S1/S2 可緊鄰；S3 需 S1/S2 新結構成立；S4 最後。
- **回歸**：每段完成跑 `/instruction:sync`（現版）確認文檔一致性；S4 是整體回歸。
- **風險**：段 3 過度替換（把合法 CLAUDE.md 引用也改）→ 用「抽樣 3 檔」驗證把關。

---

## 收尾步驟（docs mode）

1. **受影響命令/rules 行為反映**：`commands/CLAUDE.md` 命令索引 description 同步（`/instruction:init`、`/instruction:clean`、`/instruction:sync`、`/instruction:distill` 的 description 反映 AGENTS.md-aware）；`rules/instruction-writing.md` 新約定生效。
2. **Kanban**：本 EP 追蹤卡 + UC-1~4 卡片搬 Done/（建於 UC盤點收尾）。
3. **CLAUDE.md（root）反映**：repo-nav 反映新雙檔模式（AGENTS.md + CLAUDE.md wrapper）。
4. **無 Capabilities 表 / SYSTEM-MAP / /audit-test**（元專案 docs mode，正當跳過）。
5. **memory 更新**：`multi-harness-architecture-direction` 補「foundation EP 已落地」狀態。

---

## EP Review（/judge-review 決策 — 全 ✅ 採納，待套用）

> 審查來源：ai2（Agent Tool / Explore，docs-mode 5 維度）。所有 🔴 已 `rg`/`file`/`readlink` 查證 confirmed。

| finding | 段落 | 待套用修正 | 決策 |
|---------|------|-----------|------|
| 🔴 F1/F4 rename ripple 漏 3 檔 | 段 1 要點 4 + UC盤點 ripple 表 | 補 `commands/commit.md`、`commands/spec.md`、`skills/arch-thinking/SKILL.md`；9 → **12 活躍檔**（22 命中 − 8 `_done/` 歸檔 − 2 EP/spec 自身） | ✅ 採納 |
| 🔴 F1/F3 ~/.zcode/AGENTS.md 是實體 copy 非 symlink | 段 1 要點 3 + 驗證 | 補「先檢查 ~/.zcode/AGENTS.md 現況：實體檔（已驗 7987B copy）→ 確認內容一致後刪除重建為 symlink」；驗證改 `readlink -f` + 內容比對（非單純 readlink） | ✅ 採納 |
| 🟡 F3 neutral 純度 | 段 1 要點 2 | 原 ai2 判「必須 neutral 化重構」；**經 `~/.claude` symlink 查證後降級**——改名只斷 `~/.claude/CLAUDE.md` 一條（5 條 rules/skills/... 不動），且 `@~/.claude/rules/*` 對 Claude 仍有效（rules symlink）→ **不強制 strip**（用戶接受非-Claude 拿原則級）。段 1 改為「@-ref 處理（降級：非阻塞）」 | ✅ 採納（降級） |
| 🟡 F5 dogfood 觸發模糊 | 段 4 驗證 | 補具體觸發：「在 ZCode 請 agent 列目錄 → 觀察 fd vs find」「請 agent 跑 python → 觀察 uv run」。把「≥1 規則生效」對應可重現觸發，否則退化 silent success | ✅ 採納 |

**段 0 研究摘要修正**：ripple 數 9 → 12（作者段 0 `rg | head` 截斷致漏算，ai2 抓正確）。

### /judge-review（code-review of S2/S3+rework，ai1）

> 該 review 在架構 B rework 前快照，部分 stale。已對當前狀態查證。

| finding | 決策 | 理由 |
|---------|------|------|
| F1 claude:* body 未隨 description 遷移（overpromise） | ✅ 採納（soften） | 真實：description 說雙檔、body 仍只 CLAUDE.md。修法：description soften「遷移中」+ 全 body 遷移列 follow-up（影響未來 /instruction:init、非 ai-rules 當前狀態） |
| F2 @AGENTS.md inline+重複+未 thin | ❌ stale | rework 已 thin（@AGENTS.md 獨立行）+ 全域≠專案（無重複） |
| F3 project AGENTS.md 違反 no-@ | ❌ stale | rework 後 project AGENTS.md 0 @ token；@ refs 在 ai-development-guide.md（全域指南，獨立檔） |

**阻塞項**：2 個 🔴（ripple 完整性 + symlink 部署正確性）—— build 前必套用，否則 ripple 斷裂 + 覆蓋實體檔。
**Ask First 決策**：不變（rename + neutral），但段 1 需反映 scope 取捨。
