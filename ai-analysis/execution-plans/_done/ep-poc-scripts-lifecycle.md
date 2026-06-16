# EP：POC/Scripts 定位與生命週期治理（docs mode）

> **🔴 docs mode 聲明**：本 EP 為純文檔改動（全為 rules/skills/commands 下的 .md，無 .py 邏輯）。段落裁剪程式碼導向部分（無 Pseudo Code、無 TDD、無 mypy/ruff/pytest、無整合路徑覆蓋）。驗證策略改為文檔驗證（rg 殘留、跨檔一致性、/consistency）。`/build` 執行本 EP 時，階段 2 的 TDD/mypy/pytest/整合路徑覆蓋**全部跳過**，僅執行「修改 → rg 驗證 → 一致性檢查」。
>
> **觸發判準**〔Review: B-12〕：變更全為 .md **且** 無新增/修改 .py callable 符號（`rg "^def |^class " --type py` 於本 EP 變更範圍為 0）→ docs mode。純 .py 搬移（無邏輯改）→ docs mode + 保留 mypy/pytest baseline。
>
> 〔Review: R2-⚠️6 時態〕本 EP 所有 rg 驗證皆為「改後狀態」期望（改前目標字串存在是預期命中、非殘留；改後須歸 0）。

## 實作總覽

消滅「驗證用非生產可執行程式碼」的半生產中間態：`lab/` 改名 `poc/` 為暫時性驗證腳本（build+commit 後清除），`scripts/` 重定位為 demo 給老闆入口，`/commit` 新增階段 2.7 處置閘門強制顯式歸類（利用「POC 必刪」倒逼測試覆蓋）。

**核心驅動**：結構性強迫提高測試覆蓋 —— POC 預設進 test，commit 時無繼承就消失，倒逼 build 時把驗證行為改寫成正式測試（行為級、貼意圖，優於 coverage gate 的行級數字）。

### Dogfood 暴露的 /execution-plan 縫隙（供 S6 正式化 + 未來 /flow-review）

本次以 docs mode dogfood `/execution-plan`，過程暴露的純文檔/元專案不適配點：

1. **UC 盤點對元專案失效**：ai-rules 無 library Capabilities 表格，能力=命令本身
2. **kanban/SYSTEM-MAP 對元專案不適用**：產出是給消費端的規則，自身不建
3. **程式碼段落對純文檔空洞**：Pseudo Code/TDD/mypy/ruff/pytest/整合路徑覆蓋全不適用
4. **依賴錨點（file:line 符號）對文檔無對象**：文檔引用非符號依賴，改為 file:line 文檔行號錨點
5. **收尾 Capabilities+Kanban 更新對元專案不適用**
6. **EP Review 的 Call Stack/Pattern Alignment 對文檔無意義**：review 維度需改為文檔一致性+設計合理性+引用 drift

---

## UC 盤點（docs mode 適應：元專案無 Capabilities 表格，能力=命令/rules）

### Backlog 關聯
- 無 `.kanban/` 目錄。元專案適應：ai-rules 產出是給消費端用的規則，自身不建 kanban，**跳過建卡**（非缺陷，是 docs mode + 元專案的正當跳過）

### SYSTEM-MAP 影響
- 無 `SYSTEM-MAP.md`。元專案不適用，跳過

### 掃描範圍
- `CLAUDE.md`（root）、`commands/CLAUDE.md`、`rg "^## Capabilities" *.md`（僅 task-status.md 命中，為命令說明非 UC 表）

### 受影響能力（更新既有，命令行為改變）
| 能力 | 來源 | 影響 | 說明 |
|------|------|------|------|
| `/spec` POC 可行性驗證 | commands/spec.md | 更新 | POC 路徑 lab→poc、生命週期、檔頭加 EP 段落 |
| `/ep-validate` POC 驗證 | commands/ep-validate.md | 更新 | 生命週期改寫（移除活文件）、不生產化擴充 |
| `/build` 逐段實作 | commands/build.md | 更新 | TDD 衔接 POC、Examples 流程→POC+demo 盤點 |
| `/deep-work` 自主實作 | commands/deep-work.md | 更新 | Examples 流程同步 |
| `/deliverable-review` demo 交付 | commands/deliverable-review.md | 更新 | demo target 挑選規則移除 examples/**、範例路徑同步 |
| `/commit` Commit 入口 | commands/commit.md + commands/CLAUDE.md | 更新 | 新增階段 2.7 處置閘門 + description 同步 |
| `must-execute` 驗證約束 | rules/must-execute-before-complete.md | 更新 | 可執行分類 lab→poc |
| `acceptance-evidence` 證據階層 | rules/acceptance-evidence.md | 更新 | 後設引用同步 + POC 新生命週期 |
| `code-edit-constraints` 編輯約束 | rules/code-edit-constraints.md | 更新 | 依賴方向（scripts 重定位） |
| `python-standards` 命名規範 | rules/python-standards.md | 更新 | demo_ 待處置語境 |
| `code-review` 代碼審查 | commands/code-review.md | 更新 | Demo/Lab 標題→Demo/POC、rg 搜尋範圍 |
| scripts/ 定位 | ai-development-guide.md | 更新 | thin wrapper → demo 入口 |

### 新增能力
| 能力 | 實作路徑 |
|------|---------|
| commit POC/Demo 處置閘門 | commands/commit.md 階段 2.7 |

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應段落 |
|---|------|------|---------|------------|---------|
| SM-1 | commit 時 poc/ 有檔案 | /commit 2.7 掃到 poc/**/*.py | 讀檔頭 EP 段落：所屬段落已完成→強制歸類（預設 test）；所屬段落未完成→標待處置暫不擋 | 補 test 或 delete（附證據）| S2 |
| SM-2 | commit 時 poc/ 空 | /commit 2.7 無命中 | 通過 | 無 | S2 |
| SM-3 | commit 時有 demo_*.py | /commit 2.7 掃到 | 強制歸類檔案去處（預設進 scripts/）| 進 scripts/delete（附證據）| S2 |
| SM-4 | build 段落有對應 POC | /build 階段2 RED | 優先把 POC 提煉改寫成該段 RED 測試（非另起爐灶、非整段貼）| POC 行為進 test | S4 |
| SM-5 | EP 假設被 POC 推翻 | build 中發現矛盾 | 記錄偏差，更新 POC 重驗 | 偏差記錄 | S4 |
| SM-6 | AI 想留驗證在 poc/ 不進 test | commit 2.7 強制歸類 | delete 須附分類證據（test path / EP finding / 探索說明），否則不得 delete | 倒逼寫進 test | S2 |
| SM-7 | scripts/ 累積可複用邏輯 | code-review/arch-review 發現 | 標記上抽進 library | 邏輯進 library | S1 |
| SM-8 | demo 兼具展示+驗證價值 | commit 2.7 判斷 | 檔案進 scripts（呈現）；驗證行為 build 時另提煉 test_<feature>.py（獨立層面，非 2.7 範圍）| 檔案+行為雙軌 | S2 |

---

## 段落劃分原則

先改「定義權威」單點，再核心機制，再 ripple（避免中間不一致態）。段落間語義約束：

- **共用術語**：「poc/ = 暫時性驗證腳本」「scripts/ = demo 給老闆入口」「demo_*.py = 待處置物」三個詞在所有段落一致使用
- **路徑權威**：`poc/poc_*.py`（非 lab/poc_*.py）為唯一 POC 路徑，所有段落引用此
- **處置定義**〔Review: B-04〕：2.7 的「歸類」指**檔案去處**（scripts/test/delete 互斥）；demo 驗證的**行為**是獨立層面（build 時另提煉 test，不在 2.7）。在 S2 定義，S3/S4/S5 引用

---

## S1：核心定義（單點權威）

### Context
- **UC 引用**：更新 `must-execute`（可執行分類）、`code-edit-constraints`（依賴方向）、`ai-development-guide`（scripts/ 定位）
- **語義約束**：與 S2 共享「scripts/ = demo 入口」、與 S3 共享「poc/ = 暫時性」
- **文檔行號錨點**〔Review: B-02〕：此三檔是下游所有段落引用的權威定義源 —— spec/ep-validate/build/commit 的描述都從這裡派生
- **為何先做**：避免 ripple 過程中權威源與派生描述暫時不一致

### 修改要點
1. **`ai-development-guide.md:84`**：「scripts/ 是 thin wrapper」→「scripts/ 是 demo 給老闆的呈現入口（基於 library 重寫，可用 typer），不放 Capabilities」
2. **`rules/code-edit-constraints.md:17`**：依賴方向「library → CLI → scripts」→「library → scripts（demo 入口），scripts 不反向依賴 library 內部；可複用邏輯一旦累積須上抽進 library，不讓 scripts 變第二個 library」
3. **`rules/must-execute-before-complete.md:15`**：可執行分類「.py 腳本、demo、POC、lab、example」→「.py 腳本、demo、poc/、example」，補一句 POC 暫時性生命週期（指向 S3）

### 驗證
- `rg "thin wrapper" rules/ ai-development-guide.md` → 0 殘留（除 init.md 待 S5 處理）
- `rg "library → CLI → scripts" rules/` → 0 殘留
- 三檔術語與 S2-S5 一致（poc/、demo 入口）

---

## S2：核心機制 — /commit 階段 2.7 處置閘門（樞紐，新增能力）

### Context
- **UC 引用**：新增「commit POC/Demo 處置閘門」能力
- **語義約束**：定義「檔案去處歸類」（poc 預設 test、demo 預設 scripts、delete 須證據）+「行為另提煉 test 獨立層面」—— S3/S4/S5 引用此語義
- **文檔行號錨點**：插入 commit.md 現有階段 2.6（:72-81）之後、階段 3（:83）之前；與 2.5/2.6 同屬「commit 前檢查閘門」系列
- **設計理由**：不靠 build LLM 自覺回頭看 POC，靠 commit 閘門逼結算時交代每個 POC 去處（同 build「整合路徑覆蓋 rg 0 hits 就擋」的機械閘門模式）

### 修改要點

**主體：在 `commit.md` 階段 2.6 與階段 3 之間新增「階段 2.7：POC/Demo 處置閘門」**

〔Review: A4/B-05 時序〕2.7 掃描+歸類在階段 3（Capabilities+Kanban）之前執行；處置清單隨階段 5 用戶確認一併確認；確認後在階段 6 commit 執行前，先跑已確認的處置（刪 poc/ 檔、歸併 demo）。

```
掃描 poc/**/*.py + demo_*.py（rg glob，機械事實不可靜默跳過）
- 空 → 通過
- 非空 → 逐個處置：
  〔Review: B-10 跨段落豁免〕先讀 POC 檔頭 EP 段落標注，判斷生命週期：
    - 所屬段落尚未 build（活躍 POC）→ 標「待該段落 build 時處置」，暫不擋
    - 所屬段落已 build+commit，或檔頭缺失 → 強制顯式歸類檔案去處
  強制歸類（檔案去處三選一）：
    | 產物 | 預設檔案去處 | 偏離預設 |
    | poc/**/*.py | 改寫成 test（給測試路徑，須存在）| 選 delete 須附分類證據（見下）|
    | demo_*.py | 進 scripts/（給 demo 入口路徑）| 選 delete 須附分類證據 |
  - 承接物（test/scripts 路徑）不存在 → 當場補，否則擋 commit
```

〔Review: B-09 delete 證據〕delete 非憑空理由，須附可分類證據之一：
- 「已被既有 test 覆蓋」→ 附 test path + rg 驗證存在
- 「假設被推翻（行為不進生產）」→ 附 EP finding（ep-validate ❌ 結果記錄）
- 「純探索性（無對應 UC）」→ 說明探索目的 + 為何無對應 UC

提不出證據 → 不得 delete，須改寫成 test（倒逼覆蓋）。用戶階段 5 見處置清單（含證據），可核對 AI 是否全選 delete 編理由。

〔Review: B-04 demo 雙重〕「檔案去處三選一」是互斥分類（檔案層）。demo 驗證的「行為」是獨立層面 —— 若值得測，build 時另提煉 `test_<feature>.py`（不在 2.7 範圍）。2.7 掃 demo_*.py 只管檔案去處（預設 scripts / delete）。

**連帶同步**：

〔Review: B-06 捷徑〕commit.md:152 捷徑模式明確保留 2.6 + 2.7（均屬 commit 前檢查閘門，非被跳過的階段 2 Git 狀態分析）—— 更新捷徑描述加入 2.7。

〔Review: B-14 description 責任〕同步 `commands/CLAUDE.md:37` 的 `/commit` description：現「lint 閘門 → UC 狀態確認 → message → 確認」→ 加「POC/Demo 處置」（lint 閘門 → ... → POC/Demo 處置 → UC 狀態確認 → message → 確認）。本段落負責此同步（非收尾）。

### 驗證
- 新階段 2.7 編號連續（2.6 → 2.7 → 3）、不與既有衝突
- 處置語義與 S3（poc 生命週期）、S5（demo 規則）一致
- `rg "2.7" commands/commit.md` 確認插入位置；`rg "POC/Demo 處置" commands/CLAUDE.md` 確認 description 同步

---

## S3：POC 生命週期改寫（/ep-validate + /spec）

### Context
- **UC 引用**：更新 `/spec` POC 可行性驗證、`/ep-validate` POC 驗證
- **語義約束**：與 S1 共享「poc/ = 暫時性」、與 S2 共享「處置在 commit + 檔頭 EP 段落」、與 S4 共享「build 時改寫進 test」
- **文檔行號錨點**〔Review: A5 + R2-⚠️4〕：spec.md:85,89,94,194 + 分工表（:189-194）；ep-validate.md:34,96,97,136,139（放置位置 `lab/`）+ 生命週期段（:154-156）+ 不生產化（:184）。註：ep-validate:140-141 為命名慣例範例（`poc_*` 檔名，非 lab/ 路徑），不在改名清單

### 修改要點
**路徑改名（機械）**：上述錨點的 `lab/poc_*.py` → `poc/poc_*.py`、`lab/` → `poc/`。

**生命週期改寫**：
- **移除**（ep-validate.md:154-156）：「驗證期間：保留為活文件（技術決策的證據，可追溯為什麼這樣設計）」「生產化後：由使用者決定何時刪除或歸檔」
- **改為**：POC 為暫時性驗證產物，僅存活到該 EP 的 build+commit 完成；build 時其驗證的行為被改寫成正式測試（提煉行為意圖，非搬檔案），`/commit` 階段 2.7 確認承接後清除 POC 檔案
- **移除**（spec.md:194、ep-validate.md:34 分工表）：「可保留或刪除」→「build+commit 後清除」
- **擴充**（ep-validate.md:184「不生產化」）：補「行為在 /build 改寫成測試，檔案 commit 後清除（見 /commit 階段 2.7）」

**檔頭格式統一**〔Review: B-10 連帶 + R2-🔴2〕：spec.md（:94-99）與 ep-validate.md（:146-151）現有欄位不同（spec 有「來源」、ep-validate 有「EP 段落」），/build LLM 不知該留誰。統一為**聯集 template**，兩檔都對齊：

```python
"""POC: [假設描述]

驗證: [具體驗證標的]
EP 段落: S{N}
風險: [致命/高/中]
來源: [假設來源，如 path/to/file.py:ClassName 或用戶確認]
"""
```

spec 加「EP 段落」（新）、ep-validate 加「來源」（新）。支撐 commit 2.7 跨段落判斷（EP 段落）+ 假設追溯（來源）。

### 驗證
- `rg "活文件|技術決策的證據|可保留或刪除|由使用者決定何時刪除" commands/spec.md commands/ep-validate.md` → 0 殘留
- `rg "lab/" commands/spec.md commands/ep-validate.md` → 0 殘留
- `rg "EP 段落" commands/spec.md commands/ep-validate.md` → 兩處檔頭格式一致
- 生命週期閉環：spec/ep-validate 產生 POC（含檔頭段落）→ build 改寫進 test → commit 2.7 清除（三處描述一致）

---

## S4：/build TDD 衔接 + Examples 流程改寫

### Context
- **UC 引用**：更新 `/build` 逐段實作、`/deep-work` 自主實作
- **語義約束**：與 S3 共享「build 時改寫 POC 進 test」、與 S1 共享「poc/ 路徑」
- **文檔行號錨點**：build.md:68,69,97,113,126；deep-work.md:42,54,82,88

### 修改要點
1. **build.md 階段1「Examples 盤點」→「POC + demo 盤點」**（:68,69）〔Review: A7 範圍一致〕：掃描範圍統一為 `poc/**/*.py` + `demo_*.py` + `scripts/demo_*.py` + `notebooks/*.ipynb`（移除 `examples/**/*.py`），建立 `{module} → [poc/demo paths]` 映射表。**deep-work.md:54 改後掃描清單須與 build.md:68 完全一致**（非僅改「等」字）
2. **build.md 階段2 TDD 補銜接**（:73-80 RED 步驟）：該段對應的 POC（檔頭標 EP 段落 = 本段）優先被「提煉改寫」成該段 RED 測試，非另起爐灶 —— POC 先於 impl、獨立產生（時間獨立性），改寫保留其驗證意圖
   - 〔Review: B-11 方法提示〕「提煉改寫」= 提煉 POC 的驗證意圖（斷言什麼行為）→ 寫成 pytest test function，assert 的對象（被測函數）尚未實作 → 確保 RED 狀態（test fail）。**非把 POC 整段貼進 test file**（POC 已跑通非 fail）
3. **build.md 階段2/3「Examples 驗證」→「POC/demo 驗證」**（:113,126）：術語同步
4. **deep-work.md 同步**（:42,54,82,88）：與 build 一致的 POC+demo 盤點/驗證，移除 examples/**；:42 引用 build 階段1 名稱一併改

### 驗證
- 〔Review: R2-🔴1〕`rg "examples/\*\*|Examples 盤點|Examples 映射|Examples.*驗證" commands/build.md commands/deep-work.md` → 0 殘留（`.*` 涵蓋 build.md:126 / deep-work.md:88「Examples 全量驗證」，連續 pattern 會假陰性）
- 〔Review: R2-⚠️5〕逐字比對掃描範圍：`rg -o "掃描.*映射表" commands/build.md commands/deep-work.md` → 兩處展開清單逐字相同（現況 build:68 僅 2 類+「等」、deep-work:54 有 4 類，改後須一致，標題比對不足）
- TDD 衔接描述與 S3（POC 改寫進 test）一致

---

## S5：ripple 同步（路徑改名 + scripts 定位 + demo 規則 + deliverable）

### Context
- **語義約束**：引用 S1-S4 已確立的術語與路徑
- **文檔行號錨點**：多處分散引用，機械同步避免 drift

### 修改要點
**A. 路徑改名 lab→poc**：
- `skills/spec-driven-development/SKILL.md:200,207`（`lab/poc_*.py` → `poc/poc_*.py`）
- `commands/code-review.md:136`（rg 搜尋範圍 `lab/` → `poc/`）
- 〔Review: A1〕`commands/code-review.md:82`（引用段落標題名）+ `:132`（段落標題 `## Demo/Lab 影響檢查`）→ `## Demo/POC 影響檢查`（標題語義殘留）

**B. scripts/ 定位同步**：
- `commands/claude/init.md:94`（「CLI 入口、thin wrapper」→「demo 給老闆入口（基於 library）」）
- `commands/code-review.md:117` + `skills/code-review-and-quality/SKILL.md:56`（Capabilities 入口指向 library 非 scripts —— 仍成立，補 scripts 是 demo 入口非能力入口）
- 〔Review: A3〕`agents/README.md:49-51`（「POC 輸出」是 agent 暫存語境 `.agent-tmp/`，**非** POC 生命週期）→ 僅在「POC 輸出」後加交叉引用「（見 poc/ 生命週期）」，**不**改成路徑 `poc/`（兩者是不同概念：agent 暫存 vs POC 正式路徑）

**C. deliverable-review demo target**：
- `deliverable-review.md:100` demo target 挑選規則移除 `examples/**/*.py`（保留 demo_*.py / scripts/demo_*.py / notebooks）
- 〔Review: A2〕`deliverable-review.md:94`（code-mode 範例輸出 `examples/backfill/run_gap.py`）+ `:133`（--ep mode 範例輸出同路徑）→ 改為合規路徑（如 `scripts/demo_backfill.py`）。規則移除 examples/** 後，範例不得再展示 examples/ 路徑（避免矛盾誤導）

**D. demo 命名規則**：
- `python-standards.md:10` 補充：`demo_*.py` 為待處置物（commit 時檔案去處進 scripts/test/delete，見 /commit 2.7），前綴規則保留

**E. acceptance-evidence 後設引用**：
- `acceptance-evidence.md:87`（`.py / demo / POC / lab / example` → `.py / demo / POC / poc/ / example`）〔Review: B-18〕：已查證 :87 確有 lab（reviewer 稱沒命中為 pattern 失誤）。執行時 `rg "lab" rules/acceptance-evidence.md` 確認行號未 drift 再改

### 待決（不需動，僅記錄）
- 〔Review: B-16〕**swing-analysis.md:19** `examples/rule_forge/demo_*.py` 為 **broken reference**（rule_forge 實體在消費端 mosaic_alpha）。驗證方式：`rg "rule_forge" commands/swing-analysis.md` 確認 :76 `from mosaic_alpha.rule_forge import` 指向消費端 → 僅加註「消費端路徑」或不動，不涉及 examples/ 目錄整併
- 歷史 EP（ep-human-review-command.md:443）的 lab/examples 引用：歷史文件不逐份改
- 泛用目錄名（python-type-gap、claude/_common/recursive-*、sync-check-angles）：泛用策略保留

### 驗證
- 〔Review: A6 精確化〕`rg -n "lab/poc_|[/\"]lab/" rules/ skills/ commands/` → 0 殘留（排除：歷史 EP `ai-analysis/execution-plans/`、/tmp 偽命中、swing-analysis.md:14 的 `ui-collab/SKILL.md` false positive）
- `rg "thin wrapper" rules/ skills/ commands/` → 0 殘留
- `rg "Demo/Lab" commands/code-review.md` → 0 殘留（已改 Demo/POC）
- scripts/ 定義在 init/code-review/code-review-and-quality 三處一致

---

## S6：docs mode 正式化（寫回 /execution-plan）+ dogfood 經驗

### Context
- **UC 引用**：更新 `/execution-plan`（新增 docs mode 支援）
- **語義約束**：本段是 meta —— 把本次 dogfood 暴露的縫隙（見實作總覽）轉成 /execution-plan 的正式 docs mode 標準
- **文檔行號錨點**：修改 commands/execution-plan.md 的「段落設計標準」「UC 盤點」「收尾步驟」「EP Review」段落，加入 docs mode 分支

### 修改要點
在 `execution-plan.md` 新增「docs mode（純文檔/rules 改動）」區段，定義：

| EP 段落元素 | 程式碼 mode | docs mode |
|------------|------------|-----------|
| UC 盤點 | 掃 library Capabilities | 掃「受影響命令/rules 清單」（元專案無 Capabilities 表格）|
| kanban/SYSTEM-MAP | 強制 | 元專案/無對應時跳過（正當跳過，標記理由）|
| Context 錨點 | file:line 符號（LSP）| file:line 文檔行號錨點（rg 驗證行號指向預期內容）〔Review: B-02〕|
| Scenario Matrix | 大型/中型必填 | 〔Review: B-01〕影響命令行為時仍填，但「觸發/預期行為」改文檔語境（rg 命中/0 殘留），非程式執行結果 |
| Pseudo Code | 類別+Call Stack | **裁剪**（文檔無類別）；以「修改要點」替代 |
| 驗證策略 | Examples+測試+整合測試 | 改為文檔驗證（rg 殘留、跨檔一致性、/consistency、導航有效性）|
| TDD/mypy/ruff/pytest | 強制 | **跳過**（/build 階段2 僅「修改→rg→一致性」）|
| 整合路徑覆蓋 | rg `<param>=` | **跳過**（或改為跨檔引用一致性 rg）|
| EP Review 維度 | Call Stack/Pattern Alignment | 改為「文檔一致性+設計合理性+引用 drift+漏改」|
| 收尾 Capabilities+Kanban | 強制 | 元專案跳過；改為「受影響命令/rules 行為已反映 + commands/CLAUDE.md 命令索引 description 同步」|

觸發判準〔Review: B-12〕：EP 觸發時若變更全為 .md 且無新增/修改 .py callable 符號 → 自動進 docs mode。

〔Review: R2-流程層 /build 分支，閉環補完〕docs mode 跳過實際發生在 **/build 階段 2（執行端）**，不只 /execution-plan（產出端）。否則 /build.md:211「每段必須 TDD」、:212「每段必須獨立驗證（ruff+mypy+pytest）」與 docs mode 跳過結構衝突 —— 只靠 EP 檔頭聲明 = LLM 自覺，違反「機械閘門 > LLM 自覺」。S6 同步在 **/build.md** 加 docs mode 分支：
- 階段 0（EP 快檢）：偵測 EP 檔頭 docs mode 聲明 → 標記本 EP 為 docs mode
- 階段 2（逐段實作）：docs mode 跳過 TDD（RED/GREEN/REFACTOR）、mypy/ruff/pytest、整合路徑覆蓋；改執行「修改 → rg 殘留 → 跨檔一致性 → /consistency」
- 階段 3（整合驗證）：docs mode 跳過全量 mypy/pytest，改全量 rg 殘留 + /consistency
- 執行約束（:211-212）：補「docs mode EP 除外」分支

### dogfood 經驗記錄（供 /flow-review）
本 EP 本身是 docs mode 首例。記錄執行時再發現的縫隙到 `ai-analysis/flow-feedback/`（若執行後有新摩擦）。本次已記錄的 6 點縫隙見實作總覽。

### 驗證
- execution-plan.md 含 docs mode 區段、觸發判準明確
- docs mode 標準與本 EP 各段實際長相一致（本 EP 即範例）

---

## EP Review Findings（docs mode EP Review，judge-review 決策）

> 兩維度 Explore agent 審查 + judge-review（深層思考）。採納 18 / 不採納 1 / 需確認 1。Apply Changes 已整合進各段落（見各段〔Review: ID〕標記）。

| ID | 嚴重度 | 段落 | 問題 | 決策 | status |
|----|--------|------|------|------|--------|
| A1 | 🔴 | S5 | code-review.md:82/132 標題「Demo/Lab 影響檢查」殘留 Lab | ✅ 改「Demo/POC 影響檢查」 | adopted |
| A2 | 🔴 | S5 | deliverable-review.md:94/133 範例仍展示 examples/，與 :100 規則矛盾 | ✅ 範例路徑改 scripts/demo_*.py | adopted |
| A3 | ⚠️ | S5 | agents/README:49-51「POC 輸出」是暫存語境非生命週期 | ✅ 僅交叉引用，不改路徑 | adopted |
| A4+B-05 | ⚠️ | S2 | commit 2.7 執行時機措辭跨兩句易混淆 | ✅ 統一時序 | adopted |
| A5 | ⚠️ | S3 | Context 漏列 ep-validate:96,97,136 | ✅ 補列 | adopted |
| A6 | ℹ️ | S5 | rg "lab/" 有 ui-collab false positive | ✅ 驗證指令精確化 | adopted |
| A7 | ℹ️ | S4 | build.md:68 與 deep-work.md:54 範圍須一致 | ✅ 改後清單一致 | adopted |
| B-01 | 🔴 | S6 | 對照表漏 Scenario Matrix 裁剪 | ✅ 補 SM 行 | adopted |
| B-02 | ⚠️ | S6 | 依賴錨點描述模糊 | ✅ 改 file:line 文檔錨點 | adopted |
| B-04 | 🔴 | S2 | demo 雙重 vs 三選一矛盾 | ✅ 重定義：檔案去處三選一 + 行為另提煉 test | adopted |
| B-06 | ⚠️ | S2 | 捷徑模式 2.7 保留不明確 | ✅ 明確保留 2.6+2.7 | adopted |
| B-09 | 🔴 | S2 | delete 無機械驗證，可編理由 | ✅ delete 須附分類證據 | adopted |
| B-10 | 🔴 | S2 | 跨段落 POC 誤擋中間 commit | ✅ POC 檔頭加 EP 段落 + 未 build 則豁免 | adopted |
| B-11 | ⚠️ | S4 | POC 改寫 RED 缺方法提示 | ✅ 補提煉方法 | adopted |
| B-12 | ⚠️ | S6 | docs mode 觸發判準誤判 | ✅ 加「無新增 .py callable」 | adopted |
| B-14 | 🔴 | S2 | commands/CLAUDE.md commit description 責任真空 | ✅ 歸 S2 同步 | adopted |
| B-15 | ⚠️ | 收尾 | root CLAUDE.md scripts/ 是否新增 | ⚠️ 傾向不新增（權威在 ai-development-guide），執行時確認 | needs-confirmation |
| B-16 | ⚠️ | S5 | swing-analysis 待決缺驗證 | ✅ 補 rg 驗證 :76 import | adopted |
| B-18 | ⚠️ | S5 | acceptance-evidence:87 行號 drift | ❌ 查證 :87 確有 lab（reviewer pattern 失誤）；採通用「執行時 rg 確認」 | rejected/adopted(輕量) |

**連帶修正（B-10 衍生）**：spec POC 檔頭格式統一加 `EP 段落` 欄位，對齊 ep-validate。

### Round 2 Findings（落地前查證 agent + judge-review，全採納）

| ID | 嚴重度 | 段落 | 問題 | 決策 | status |
|----|--------|------|------|------|--------|
| R2-🔴1 | 🔴 | S4 驗證 | `Examples 驗證` 連續 pattern 不匹配「Examples 全量驗證」→ 假陰性 | ✅ pattern 改 `Examples.*驗證` | adopted |
| R2-🔴2 | 🔴 | S3 檔頭 | spec「來源」vs ep-validate「EP 段落」欄位不同，未定統一目標 | ✅ 補聯集 template，兩檔對齊 | adopted |
| R2-🔴3 | 🔴 | S1 錨點 | code-edit-constraints/must-execute 缺 `rules/` 前綴（S5 有） | ✅ 補 rules/ | adopted |
| R2-⚠️4 | ⚠️ | S3 錨點 | ep-validate:139-141 混列（:139 放置位置 lab/、:140-141 命名慣例非 lab）| ✅ 拆分標註 | adopted |
| R2-⚠️5 | ⚠️ | S4 驗證 | 標題比對不驗掃描範圍逐字一致（現況 build/deep-work 不一致）| ✅ 補逐字比對 | adopted |
| R2-⚠️6 | ⚠️ | 聲明 | 「→ 0 殘留」時態歧義（改前目標存在是預期）| ✅ docs mode 聲明補時態 | adopted |
| R2-流程層 | 🔴 | S6 | /build.md 無 docs mode 分支，:211-212 寫死 TDD/mypy/pytest，跳過只靠 LLM 自覺 | ✅ 選 (a)：S6 補 /build.md docs mode 分支（階段0偵測+階段2/3跳過）| adopted |

**略過（無害）**：S6 標題 drift（EP Review vs EP Review Cycle，rg 子串命中）、A6 排除項（`[/\"]lab/` 本就不命中 swing-analysis:14，多餘但無害）、S3 同行雙 lab/（rg 抓到加註）。

---

## 整合策略

- **執行順序**：S1（定義）→ S2（機制）→ S3（生命週期）→ S4（build）→ S5（ripple）→ S6（docs mode 正式化）。S1-S4 有語義依賴（先定義再引用），S5 ripple 可批次，S6 最後（總結 dogfood）。
- **一致性閘門**：每段後跑 rg 殘留檢查；全部完成後跑 `rg "lab/poc_|[/\"]lab/" rules/ skills/ commands/` + `rg "活文件|thin wrapper|Demo/Lab"` 全域歸零。
- **/build 執行**：本 EP 為 docs mode，/build 階段2 跳過 TDD/mypy/pytest/整合路徑覆蓋，階段3 跳過（純文檔無整合器型）。驗證靠 rg + /consistency。

## 收尾步驟（docs mode 適應）

1. **CLAUDE.md Capabilities + Kanban**：元專案無 Capabilities 表格/kanban，**跳過**。改為確認 `commands/CLAUDE.md` 命令索引中受影響命令的 description 仍準確（commit 已在 S2 同步；spec/ep-validate/build/deep-work/deliverable-review 執行時確認 description 是否需跟著行為更新）。
2. **SYSTEM-MAP.md**：無，跳過。
3. **CLAUDE.md 更新**〔Review: B-15〕：root CLAUDE.md 目前無 scripts/ 提及（已 `rg` 確認）。判斷：scripts/ 重定位為 demo 入口的權威已在 ai-development-guide.md（S1）處理，root CLAUDE.md「專案結構」段未列 scripts/ 目錄用途 → **不新增**（避免重複權威源）。執行時若發現 root CLAUDE.md 有目錄列表需補，再判斷。
4. **/audit-test**：純文檔無測試，跳過。改為 `/consistency` 抽查 commit.md、ep-validate.md、build.md、execution-plan.md 自洽性。

## 流程位置
本 EP 自身以 docs mode dogfood `/execution-plan`（S6 把經驗寫回）。執行：`/build ai-analysis/execution-plans/ep-poc-scripts-lifecycle.md`（docs mode，跳過 TDD/mypy/pytest）。
