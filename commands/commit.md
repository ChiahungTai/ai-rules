---
description: "Commit 入口：lint 閘門 → 分析變更 → 生成 message → 確認後提交"
when_to_use: "Commit current changes after lint check, message generation, and user confirmation. Supports push, rebase, and PR creation after commit."
usage: "/commit [--push] [--rebase <branch>]"
argument-hint: "可選 --push 自動推送，--rebase <branch> rebase 後推送"
allowed-tools: ["Bash", "Read"]
---

# /commit — Commit 入口

Git Commit 工作流入口，從 lint 閘門到提交完成。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 執行流程

### 階段 1：Lint 閘門

**Ruff + MyPy 雙軌閘門**（兩者都必須通過才 commit）：

```bash
# Track A: Ruff（格式 + lint）
uv run ruff check --fix .    # Step 1: 自動修可修的
uv run ruff format .         # Step 2: 格式化
uv run ruff check .          # Step 3: 最終驗證（必須 0 errors）

# Track B: MyPy（型別檢查）
uv run mypy .                # 必須 0 errors
```

**執行順序**：Step 1 → Step 2 → **並行** Step 3 + MyPy（ruff format 後同時跑 ruff verify 和 mypy，省時間）。

Ruff 或 MyPy 有錯誤 → **嘗試手動修正**（不直接放棄）：

| 錯誤類型 | 自動處理策略 |
|---------|------------|
| PLC0415（局部 import） | 移至 top-level import。**禁止假設 circular import** — AI 常偷懶放在函數內，99% 不是 circular。真正循環的解法是重構目錄結構，不是局部 import |
| F841（未使用變數） | 移除或加 `_` 前綴 |
| E402（sys.path 後的 import） | 加 per-file-ignores 到 pyproject.toml |
| MyPy 第三方套件型別缺口 | 依 [python-type-gap](../skills/python-type-gap/SKILL.md) 四層策略處理 |
| 其他可修問題 | 依 `/lint-fix` 指引修正 |

手動修正後仍無法通過 → 提示 `/lint-fix`，中止。

### 階段 2：Git 狀態分析

`git status --porcelain` + `git diff` + `git diff --cached` + `git log --oneline -10`

深度理解：檔案層級（模組、功能區域）+ 程式碼層級（業務邏輯）+ 變更類型（feat/fix/refactor/perf/test/docs/style/chore）

### 階段 2.5：引用同步掃描

**當變更包含 `rules/`、`skills/`、`commands/` 下的 .md 檔案時執行，否則跳過。**

目的：修改 A 後，掃描是否有 B/C/D 引用了 A 但沒同步更新。

掃描範圍（按變更檔案類型）：

| 變更檔案 | 掃描目標 | 搜尋方式 |
|---------|---------|---------|
| `commands/*.md` | `commands/CLAUDE.md` 索引 | `rg "command名" commands/CLAUDE.md` |
| `commands/claude/*.md` | `commands/CLAUDE.md` 索引 + 引用此命令的其他 .md | `rg "命令名或檔名" rules/ skills/ commands/` |
| `skills/*/SKILL.md` | `skills/CLAUDE.md` 索引 + 引用此 skill 的 commands | `rg "skill名" commands/ rules/` |
| `rules/*.md` | 引用此 rule 的 commands 和 skills | `rg "rule名或檔名" commands/ skills/` |
| `ai-development-guide.md` | 所有引用 guide 定義的 commands（如 UC 狀態 emoji） | `rg "具體定義文字" commands/` |

輸出：列出需檢查的檔案（不是要求全部更新，是提醒檢查是否需要更新）。用戶在階段 5 確認時一併判斷。

### 階段 2.6：Review Findings 提醒（optional）

**人主導工作流**（finding 在 review session 對話、`/copy` 搬到實作 LLM）：無 `.review/`，此階段跳過 —— finding 處置由用戶在階段 5 確認時對照 diff 判讀（B 軸 viewport，不靠 status 機械追蹤）。

**跨命令自動化工作流**（`/judge-review` / `/followup-review` 產生 `.review/`）：若 `.review/` 存在，列出殘留 `open` finding 提醒（不阻擋）。`status` 靠 LLM 更新會漏，僅作提醒非閘門。

> 無論哪種工作流，finding 處置的最終把關在階段 5（人確認 commit）—— 機制只列出不保證。

### 階段 2.7：POC/Demo 處置閘門

**commit 前檢查閘門**（與 2.5/2.6 同系列）。機械結算每個 POC/Demo 的去處，不靠 build LLM 自覺回頭看 —— 同 build「整合路徑覆蓋 rg 0 hits 就擋」的機械閘門模式，用「POC 不得無痕消失」倒逼測試覆蓋（預設改寫成 test，delete 須附證據）。

**時序**：掃描+歸類在階段 3（Capabilities+Kanban）之前執行；處置清單隨階段 5 用戶確認一併確認；確認後在階段 6 commit 執行前，先跑已確認的處置（刪 poc/ 檔、歸併 demo）。

掃描 `poc/**/*.py` + `demo_*.py`（rg glob，機械事實不可靜默跳過）：

| 情境 | 處理 |
|------|------|
| 空（無命中） | 通過 |
| 非空 | 逐個處置（見下） |

**逐個處置**（跨段落豁免）：先讀 POC 檔頭「EP 段落」標注，判斷生命週期：

- 所屬段落尚未 build（活躍 POC）→ 標「待該段落 build 時處置」，暫不擋
- 所屬段落已 build+commit，或檔頭缺失 → 強制顯式歸類檔案去處

**強制歸類（檔案去處三選一）**：

| 產物 | 預設檔案去處 | 偏離預設 |
|------|------------|---------|
| `poc/**/*.py` | 改寫成 test（給測試路徑，須存在）| 選 delete 須附分類證據 |
| `demo_*.py` | 進 scripts/（給 demo 入口路徑）| 選 delete 須附分類證據 |

- 承接物（test/scripts 路徑）不存在 → 當場補，否則擋 commit

**delete 須附分類證據**（非憑空理由，三選一）：

- 「已被既有 test 覆蓋」→ 附 `test_path:line` + 該 assert 驗證的行為一句話（階段 5 可機械核對 assert 真覆蓋 POC 行為，非僅驗檔案存在）
- 「假設被推翻（行為不進生產）」→ 附 EP finding（ep-validate ❌ 結果記錄）
- 「純探索性（無對應 UC）」→ 說明探索目的 + 為何無對應 UC

提不出證據 → 不得 delete，須改寫成 test（倒逼覆蓋）。用戶階段 5 見處置清單（含證據），可核對 AI 是否全選 delete 編理由。

> **demo 雙重**：「檔案去處三選一」是互斥分類（檔案層）。demo 驗證的「行為」是獨立層面 —— 若值得測，build 時另提煉 `test_<feature>.py`（不在 2.7 範圍）。2.7 掃 `demo_*.py` 只管檔案去處（預設 scripts / delete）。

### 階段 2.8：flow-feedback 歸檔識別

**commit 前檢查閘門**（與 2.5/2.6/2.7 同系列）。識別本次 commit 解決了哪些 flow-feedback，標記隨 commit 歸檔到 `_done/`。與階段 3 的 EP 歸檔同屬 metadata finalization，但 **size-independent**——任何大小的 commit 都可能解決一筆 feedback。

掃描 `ai-analysis/flow-feedback/*.md`（root，glob 不含 `_done/` 內）：

| 情境 | 處理 |
|------|------|
| 空（root 無 feedback） | 通過 |
| 非空 | 逐筆判斷「本次 commit 解決這筆摩擦嗎？」→ 標 to-archive 清單 |

**判斷是 judgment 非機械**（feedback↔change 非 1:1，不像 EP↔段落明確）→ forgetting 風險靠**階段 5 可見清單**把關：to-archive 清單隨 commit 確認一併展示，用戶核對 AI 漏標沒。仍在 /flow-review 討論中、未決策的不歸檔（留 root，/flow-review 既有「defer → 留 feedback」規則）。

### 階段 3：顯式收尾三件（Capabilities + Kanban + SYSTEM-MAP）

**大型/中型變更時執行，小型變更跳過。**

> **核心原則**：顯式收尾三件（Capabilities + Kanban + SYSTEM-MAP）+ EP 歸檔是「metadata finalization」，只在用戶確認 commit 時才執行（對齊 [ai-development-guide](../ai-development-guide.md) 三層文件體系：CLAUDE.md Capabilities / SYSTEM-MAP / .kanban）。此類永久狀態更新不在 `/build` 執行（build 可能不 commit）。Kanban 搬至 InProgress/（暫時狀態）已在 `/build` 階段 1 完成。

1. 識別變更涉及的 library 模組目錄
2. 檢查該模組 CLAUDE.md Capabilities 表格和 .kanban/ 卡片：是否有 UC 狀態需要更新？
3. 在 commit message 展示後，提示用戶確認以下操作：
   - **Capabilities 更新**：在對應模組 CLAUDE.md 的 `## Capabilities` 表格新增 ✅ 行
   - **Kanban 卡片搬移**：已完成 UC 的卡片從 active lane 移至 Done/
   - **消費場景寫入**：從 `/build` 提煉的消費場景寫入 Capabilities 備註或 Kanban card
   - **SYSTEM-MAP 狀態更新**：消費專案有 SYSTEM-MAP.md 就顯式更新受影響功能生命週期狀態（ai-rules 元專案無 SYSTEM-MAP，正當跳過）
   - **原子操作**：Capabilities 新增 + Kanban 卡片移動 + SYSTEM-MAP 更新必須同時完成
4. 用戶確認後，在 commit 前**執行上述操作**（修改 CLAUDE.md + mv 卡片）
5. **EP 歸檔**：如果本次 commit 是 EP 的最後一個段落（所有段落都已 commit），自動執行歸檔：
   - `mv ai-analysis/execution-plans/ep-xxx.md ai-analysis/execution-plans/_done/`
   - **子目錄 EP**（如 `<task-group>/`，整脊曾用 `dev-process/`）：跨目錄 mv 到 `execution-plans/_done/`（統一歸檔區，不另開子目錄 _done/）
   - **綱要 EP（blueprint）**：所有衍生子 EP build+commit 後才歸檔 master（子 EP 未全完成 → master 留在原地，不提早歸檔）
   - 歸檔與顯式收尾三件同為 metadata finalization，一併執行

### 階段 4：生成 Commit Message

**格式**：`<type>(<scope>): <description>`

**語言規範**：

| 部分 | 語言 | 範例 |
|------|------|------|
| type | 英文 | `feat`, `fix`, `refactor` |
| scope | 英文 | `data`, `commands`, `ui` |
| description | **繁體中文**（術語保留英文） | `新增 DataGateway 統一數據介面` |
| body | 繁體中文 + 英文術語 | 說明為什麼這樣改 |

### 階段 5：用戶確認

展示變更摘要 + 建議 commit message + Capabilities/Kanban 狀態提醒（如適用）→ **等待用戶明確確認**。

**遵守 `commit-consent` rule**：未收到確認絕不執行 git commit。

### 階段 6：執行 Commit

確認後 `git add`（**納入本次開發的完整產物**：主變更 + EP（`ai-analysis/execution-plans/`）+ **已解決的 flow-feedback**）+ `git commit`（含 `Co-Authored-By: Claude`）。

**flow-feedback 歸檔**（隨 resolving commit，類比階段 3 EP 歸檔）：階段 2.8 標記 to-archive 的 feedback，commit 前 `mv ai-analysis/flow-feedback/<file>.md ai-analysis/flow-feedback/_done/`（`_done/` 不存在則先建）再 `git add` `_done/` 路徑 → 檔在 resolving commit 直接落地 `_done/`，不留 root。未解決 / 討論中的 feedback 不 add（留 root 未追蹤）。

**commit 成功後清除 ephemeral 工作產物**：`rm -f .review/*.md`（刪 review 筆記檔案、保留 `.review/` 目錄供下次 review 直接寫入；review 筆記為工作過程產物，commit 結算後清除 —— 同 POC 生命週期哲學，不進 git 歷史）。

### 階段 7：選配分支操作

- `--push`：`git push`
- `--rebase <branch>`：fetch + rebase + push
- 建立 PR：`gh pr create`

---

## 執行約束

- **遵守 `commit-consent` rule**：未經確認絕不 commit
- **ruff + mypy 必須雙通過才 commit**（pre-existing 問題也需在此時處理：加 per-file-ignores / type: ignore 或直接修）
- **TEMP diagnostic log 掃描**（防殘留）：commit 前掃描 diff 有無 debug-only log 模式（`Diagnostic:`、`[OK] ...`、症狀導向 debug 變數如 `<debug_var> =` 等 ad-hoc 偵錯輸出）。命中 → flag 給用戶確認移除。未移除的 debug log 不得進 commit（違反 llm-output-convention：print 只用於 state transition）。
- **description 必須繁體中文**（技術術語保留英文）
- **基於實際 diff 分析**，不憑猜測
- **遵循 git log 風格**

禁止：未確認就 commit / 全英文 description / 跳過 ruff 或 mypy / 無意義 message

---

## 流程位置

```
/build（含 Agent Review）→ [/code-review（含 commit message）] → /commit
```

前置：`/lint-fix`（lint 不通過時）、`/code-review`

**捷徑模式**：當 `/code-review` 已產生 commit message 時，跳過階段 2（Git 狀態分析，含 2.5 引用同步掃描）和階段 3（Capabilities + Kanban 狀態確認），直接進入階段 1（Lint）→ **階段 2.7（POC/Demo 處置閘門）+ 階段 2.8（flow-feedback 歸檔識別）** → 階段 5（確認）→ 階段 6（提交）。2.7/2.8 屬 commit 前檢查閘門（非被跳過的階段 2），捷徑保留；2.6 為 optional 提醒，捷徑不強制。
