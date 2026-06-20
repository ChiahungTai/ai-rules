> **ep_type**: implementation
> **mode**: docs（全為 commands/skills/rules 下 `.md`，無 `.py` callable 符號）

# EP: ghost-done 驗證 EP 補落地（execution-plan-hardening + agent-output-verification）+ judge-review 持久化

## 動機（self-contained 背景）

兩支 EP 已歸檔 `_done/`，但**實作沒有真的寫進檔案**（以實際檔案內容查證，非 EP 狀態）：

| ghost-done EP | 宣稱交付 | 實作查證（rg/read 實際檔） |
|---------------|---------|---------------------------|
| `_done/ep-execution-plan-hardening.md` | S1 兜底假設路徑驗證 + S2 流程分級 | 🔴 `execution-plan.md:278` 只是舊「兜底」（實作落差+drift），**無**「X 處理 Y→驗證 code path 經過 Y」；build.md 階段 0 快掃表無此 check；S2 流程分級（simple/standard/full）查無 |
| `_done/ep-agent-output-verification.md` | S1 agent 產出 git diff 驗證 / S2 scope fence / S3 classifier 重試 / S4 .review per-branch | 🔴 **四段全查無**：build.md 階段 4 無「自述 vs git diff」步驟；agent-workflow 無 scope fence 模板；無 classifier unavailable 重試；commit.md 無 .review per-branch 清除 |

**根因（process 教訓）**：EP 以 `_done/` 狀態代替了實作查證 — 歸檔卻沒落地。本 EP 把這兩支 EP 的設計**真正實作進檔案**（設計已完成且經審查，只差落地；不重新設計，直接 reference）。附帶收一個同類小不一致（R1）。

**設計來源**（本 EP 不重抄，新 session 讀這兩支取詳細設計）：
- `_done/ep-execution-plan-hardening.md`（S1+S2 詳細設計）
- `_done/ep-agent-output-verification.md`（S1/S2/S3/S4 詳細設計）

**來源 flow-feedback**（已歸檔 mosaic `_done/`，提供動機與真實案例）：
- `2026-06-18-ep-safety-net-not-validated.md`（#13 兜底假設 — 29 檔「我以為都搞定」）
- `2026-06-16-log-refactoring-agent-verification.md`（#7 agent 自述失準 + scope-creep 近乎 ship）
- `2026-06-15-indicators-reexport-refactor.md`（#1 簡單功能被完整 EP 流程拖慢 → 流程分級）

**Scope out（刻意不在此 EP，是既定設計決策非 gap）**：
- `/code-review` 強制 post-build（#7-2.3）：review-engine refactor 刻意維持 optional（`build.md:242` `[/code-review]`）
- L4 runtime 分級（#7-2.4）：屬 acceptance-evidence 層，獨立
- handoff→/build 路由（#7-2.1）：邊緣

---

## 實作總覽

| 段落 | 職責（落地哪個 ghost-done EP） | 依賴 |
|------|-------------------------------|------|
| S1 | 落地 `ep-execution-plan-hardening`（兜底假設路徑驗證 + 流程分級） | 無 |
| S2 | 落地 `ep-agent-output-verification`（agent 產出驗證 + scope fence + classifier 重試 + .review per-branch） | 無 |
| S3 | judge-review 持久化位置（R1：`.review/` gitignore → EP review 區段為主） | 無 |

三段獨立、各自可驗收。S1/S2 各「整支落地一支 ghost-done EP」；S3 是獨立小修。

---

## S1：落地 ep-execution-plan-hardening（EP 規劃層驗證）

### Context

`ep-execution-plan-hardening` 的 S1（兜底假設路徑驗證）+ S2（流程分級）設計完整但沒落地。讀 `_done/ep-execution-plan-hardening.md` S1/S2 取詳細設計與用語。

### 修改要點（落地點，已查證存在）

- **兜底假設路徑驗證**（S1）→ `commands/execution-plan.md` EP Review Cycle 的兜底維度（`:278` fallback prompt 目前是舊「實作落差+drift+...」）+ `commands/build.md` 階段 0 EP 快掃表（`:40-47`）：
  - EP 若用「X 段暴露/處理 Y」當兜底 → **必須驗證 X 的 code path 真的經過 Y**（追 dependency / call chain）；否則標「未驗證」而非「handled」
  - 「可觀測 ≠ 已修復」用語顯式化：`handled/exposed` 不得模糊涵蓋 visible / fixed
- **流程分級**（S2）→ `commands/execution-plan.md`：先查證 simple/standard/full（或不寫 EP）分級是否已存在；若無，依 ghost-done EP S2 設計補（小型變更輕量入口）。**先查證再決定改動量**（避免重複落地）。

### 驗證策略（docs mode）

- `rg "兜底假設|路徑驗證|處理路徑|可觀測.*修復"` 確認 execution-plan.md / build.md **真有**此 check（改後須命中、非殘留）
- `rg "simple|standard|流程分級"` 確認流程分級落地狀態
- `/consistency` 對 execution-plan.md + build.md

---

## S2：落地 ep-agent-output-verification（build/agent 驗證）

### Context

`ep-agent-output-verification` S1/S2/S3/S4 **四段全沒落地**。讀 `_done/ep-agent-output-verification.md` 取四段詳細設計。核心動機：agent 自述是 L2（同義反覆），`git diff` 是 L1 機械證據 — 缺機械驗證步驟曾讓 scope-creep 近乎 ship。

### 修改要點（落地點，已查證存在）

- **agent 產出 git diff 驗證**（S1）→ `commands/build.md` 階段 4 Agent Review Cycle（`:143-168`）：平行 agent 段結束後，機械跑 `git diff --name-only` + 比對各 agent 自述「改了哪些檔」→ flag「自述零修改但 git 顯示有改」mismatch + scope-creep（diff 超出 prompt 指定 scope）
- **scope fence 模板**（S2）→ `skills/agent-workflow/SKILL.md`：機械任務 agent prompt 必含 negative-space fence（「DO NOT modify blocks already containing `<pattern>`」+「只 touch 符合 `<criteria>` 的區塊」+ 完成後 `rg <pattern> <file>` 自驗）
- **classifier unavailable 重試**（S3）→ `commands/build.md` 階段 4 + `skills/agent-workflow/SKILL.md` + `rules/model-routing.md`：classifier safety 間歇 unavailable（只回警告 note 無 findings）→ 重試而非直接降級主 LLM 自審
- **.review per-branch 清除**（S4）→ `commands/commit.md` 階段 6（`.review/` 清除處）：`rm -f .review/*.md` 會誤刪他 branch → 改 per-branch 清除（只清當前 branch 的 `.review/<branch>.md`）

### 驗證策略（docs mode）

- `rg "git diff.*自述|自述.*git diff|零修改|scope.creep|產出.*驗證"` 確認 build.md **真有** agent 產出驗證步驟
- `rg "scope fence|negative.space|DO NOT modify"` 確認 agent-workflow **真有** fence 模板
- `rg "classifier.*unavailable|重試"` 確認 classifier 重試落地
- `rg "per-branch|\.review/<branch>"` 確認 commit.md per-branch 清除
- `/consistency` 對 build.md + agent-workflow + commit.md

---

## S3：judge-review 持久化位置（R1）

### Context

`commands/judge-review.md:40` 將 `.review/<branch>.md`（**已被 gitignore**，`git check-ignore .review/main.md` 證實）列為持久化點 → 決策寫進去等於丟失（不合專案慣例）。源自 `2026-06-18-ep-safety-net-not-validated.md` 附帶點。

### 修改要點

`judge-review.md:40` 持久化首選改 **EP review 區段 / kanban**（tracked），`.review/` 降為次要或移除（gitignore 不該是決策預設落點）。同步檢查 `code-review.md` / `workflow-review-pattern.md` 的 `.review/` 引用是否一致。

### 驗證策略（docs mode）

- `rg "\.review/" commands/judge-review.md` 確認 `.review/` 不再是預設持久化首選
- `/consistency`

---

## 收尾步驟（docs mode）

1. **ghost-done EP 處置**（已完成）：兩支 `_done/` EP（ep-execution-plan-hardening / ep-agent-output-verification）已加 ghost-done 註記，反向連回本 EP ——「done」狀態由本 EP 落地才真成立
2. **索引/CLAUDE.md**：docs mode 變更，確認受影響命令 description 無誤述
3. **跳過**（docs mode + 元專案）：Capabilities 表格、SYSTEM-MAP、mypy/ruff/pytest
4. **本 EP 歸檔**：完成後搬 `execution-plans/_done/`（EP 檔歸處；`.kanban/Done/` 是 kanban 卡用，非 EP）。**歸檔時同步更新兩支 ghost-done 註記的相對路徑**：`[ep-verify-chain-landing](../ep-verify-chain-landing.md)` → `[ep-verify-chain-landing](./ep-verify-chain-landing.md)`（歸檔後同在 `_done/`）
