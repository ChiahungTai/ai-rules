# 方法論載體選擇原則 v2——三方會議裁決書（2026-09-10）

> 會議形態：GLM 5.3（主導）×muse（muse-spark-1.3/medium）×codex（chatgpt-web/high），bridge 直呼兩輪＋`--session-id` 接續。Session：muse `01a0885f-5718-7d02-9604-ac9572ba7580`／codex `01a08858-c9ca-7528-0a48f1611e73`。全程輸出存 `.agent-tmp/bridge-{muse,codex}-carrier-{v2,r2}-out.txt`。發起：user「要跟 5.3 codex muse 共同商討 skills rules memory 的放的原則，通盤影響。我目前沒有專案用的 skills rules，memory 是專案用的」。

## 一、零分歧共識（兩輪全收斂）

1. **層級是硬閘、稀缺是軟優化**：先判 scope（「repo 名替換掉後規則仍應成立」＝user-level；「只描述某 repo 的狀態/參數/入口/例外」＝project-level），層級相容後才判載體，最後才判 residency（always-on／on-demand／檢索）。部署拓撲決定可達性——user-level 知識以 project-only 載體為權威源＝寫了等於沒寫。
2. **「非 resident memory＋imperative guard」＝scope 錯置強證據**：條目教跨 repo 動作卻進不來開場＝該升 user-level rule/skill，而非搶 12 條 resident 名額（稀缺性解冒充邊界解）。
3. **混合內容強制拆開**：通用原則升 user-level、repo specialization 留 project-level，一份文件不得兼任兩層權威。
4. **memory 只留三物**：user/project 綁定的事故證據、偏好/例外、pointer（ 觸發詞＋skill 名＋一句精髓）——不複製規範正文。
5. **regex 只產 candidate 不判決**：命中≠錯置，逐條人裁。

## 二、主導裁決（打破 round-2 立場互換的對稱）

**單一源落點＝memory-audit「載體統一定義表」兩處修補（codex round-2 案）**，不開新 skill。

裁決理由：①codex r2 駁回新 skill 的成本論證更實——第 80 個 skill 的 catalog/觸發詞競爭/ownership 邊界成本 vs 零新獨立 workflow；②零 bundle 增量約束下工程量最小；③muse r2 所慮「memory-audit 宿主偏誤」以流程解（instruction-writing 動筆前＋memory-audit Q6 兩處引用層級閘）承載，不需動宿主。**muse r2 的原子性條件保留適用**：修補一次 commit 完成＋`rg "載體統一定義表|該寫哪"` 驗零殘留正文。

### 層級閘首句（定版條文，codex r2 原文）

> **先判層級，再判稀缺：層級是硬閘，由部署拓撲決定可達性；user-level 知識不得以 project-only 載體作權威源，project-specific 知識不得上提為 user-level 規範；僅在層級相容後，才以 always-on／on-demand／檢索成本選載體。以下表格與「該寫哪」一行流皆先套此閘。**

### 誤置表新增 A/B 兩行（定版）

- **A（user-level 進 project memory）**→ 規範移回 user-level 單一源（rule/skill 依 always-on/on-demand）；memory 只留事故證據/偏好/pointer，不複製規範正文。
- **B（project-specific 進 user-level rule/skill）**→ 下沉 project carrier（repo AGENTS.md／memory／backlog-EP 依規範/事實/任務狀態分流）；user-level 僅留可泛化方法論。

## 三、雙向掃描判準（合成最小形態，candidate-only）

- **Forward lane**（掃 project memory 錯置 A）：情境/行動動詞（當、遇到、先、必須、禁、改、跑、部署、委派、驗證、commit…）**∩** 跨邊界名詞（跨 repo、harness、ZCode、Claude、Codex、Muse、bridge、Backlog、skill、rule、worktree…）取交集；**＋mixed 特徵**（`user-level|project-level|跨專案|per-repo` 命中即拆分候選）。
- **Reverse lane**（掃 rules/skills/guide 錯置 B）：project-local 名詞（具體 repo 名、絕對路徑、專案操作）∩ 規範性動詞。
- 兩 lane union → 套層級硬閘人裁。

## 四、候選清單（首輪掃描命中，全部待裁）

點名現物：`feedback_bridge-job-completion-no-push`（跨 repo How-to 三選一）、`reference_backlog-cli-entry`（自述單一源在 kanban-board）、`global-vs-project-permissions`（mixed 需拆兩層）。
Forward lane 前五候選（codex 實掃）：`feedback_cross-session-commit-on-active-branch`（已自述「規範歸 kanban SKILL＋memory 僅事故證據」——正確形態自測案例）、`feedback_backlog-card-edit-precheck`、`feedback_skill-deletion-consumer-scan`、`feedback_work-order-contract-point-to-source`、`feedback_diagnose-installed-vs-source-first`。

## 五、硬約束

**零 bundle 增量**：deployed 全域 bundle 現值 36,773B、Muse 距 36KiB gate 餘 91B——實施只許等長指針改寫／刪行，任何正文追加違規；驗收含 `deploy_agents.py` 輸出 ≤36,773B。

## 六、實施歸屬（待 user 拍板後開卡）

memory-audit 統一定義表兩處修補＋層級閘首句＋誤置表 A/B＋候選清單逐條裁決（8 條）＋pointer 匯整——一弧收斂。
