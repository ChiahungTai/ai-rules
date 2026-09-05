---
name: memory-audit
description: "memory 清理/稽核/過時/記憶健康檢查＋寫入端紀律（memory audit / audit MEMORY.md / auto memory）。兩級稽核：full 四層（索引機械量測→內容核實 vs repo→清理執行→EP/任務盤點）/ lite 增量核實（git log 驅動）。內容核實預設必做——索引整潔 ≠ 記憶健康。狀態戳 _audit-state.md；advisory→用戶核可→執行三分離。寫 memory 前的寫入六問（任務終態→卡/repo 可推導就不寫/同主題加段/cluster-first/尺寸/載體判定）、單一寫入點（條目檔 frontmatter 唯一、MEMORY.md 機械投影）、desc/條目尺寸預算＋desc 三不＋弧結案蒸餾（含 mem-distill 執行形態）見「寫入端紀律」段。觸發詞：寫入六問、任務終態、cluster-first、單一寫入點、索引投影、desc 上限、結案蒸餾、載體判定、寫 memory。"
argument-hint: "full | lite | 無參數（讀狀態戳後建議）"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Edit", "Write"]
---

# /memory-audit — auto memory 兩級稽核 + 增量核實 + 專案狀態戳

> **適用載體**：Claude Code / ZCode auto memory——per-project memory 目錄（`MEMORY.md` 索引 + 各條目 .md；session 啟動只載索引，超限截斷——**兩端皆 200 行或 25,000 字元（UTF-16，CJK 一字計 1）** 先到為準，截斷附 WARNING、尾端條目不載；「25KB」是警告訊息以 KB 顯示的假象）。ZCode memory 目錄是 symlink → Claude `projects/<project>/memory`，兩端單一真相。memory 跟專案/repo 走：稽核與狀態戳 per-project，跨 worktree 同一份不重複稽核。

## 🔴 反模式警示（最前，必讀）

**索引整潔 ≠ 記憶健康。**

真實案例（2026-08-16，mosaic_alpha）：首輪稽核只做索引層量測（重複/orphan/missing/預算全綠），用戶鞭策後才補內容核實，仍抓到 **3 條 ❌（核心主張被 repo 演進推翻）+ 24 條 🟡（部分過時）**。

根因：「過時」的判準證據**只在 memory claims vs repo 現況對照**——不在索引層。

**自檢句**（advisory 報告產出前必問）：這份報告若只有索引層發現——「過時」的判準證據在哪一層？答案不在「內容 vs repo 對照」就是層次錯了，回去做層 2。內容核實是預設必做，不是升級選項。

## 兩級稽核（開場決策）

> **姊妹弧**：rules audit × bundle 減量（聯合弧——`backlog/` 內 `rules-audit-bundle-diet-joint-arc`〔drafts 或已升卡〕；觸發＝`deploy_agents.py` 輸出 ≥93% gate）。user 2026-09-03 定調與本 skill 同班次聯合執行——lite/full audit 跑時順手執行 `uv run python scripts/deploy_agents.py` 回報 bundle 百分比，過觸發線即提案聯合弧。

開場先讀狀態戳 `memory/_audit-state.md`（規格見下方）：

- 無戳 / `base_commit` 之後 repo 大幅演進 / 距上次 full 已久 → 建議 **full**
- 間隔短或用戶明示 → **lite**

## Full audit — 四層

### 層 1：索引機械量測

> **generator 池**（memory dir 有 `_generate_index.py`）：索引是 frontmatter 投影，重複/orphan/missing 由生成保證不存在——層 1 縮為 `python3 memory/_generate_index.py --check`（硬 gate 22,500 字元〔真線 90%〕/190 行 fail-loud 守兩端共同截斷線〔200 行／25,000 字元〕；bytes >24,000 降為 `[INFO]` 縱深預警不擋寫入——兩端截斷線皆量 chars，CJK 一字 3B、bytes 提前折射；源碼實證與重跑命令見 generator 註解）＋確認 MEMORY.md 非手寫。寫入端另有 PreToolUse hook 治理（`block-memory-index-write.py`：description >100 chars、desc 含 commit hash 形態（09-05 S2）、或條目膨脹 >12,000 chars 硬擋、收斂方向放行）——hook 是流入節流第一道，audit 是存量收斂；**hook 僅攔主 session——subagent 寫入不觸發**（ZCode 實證），寫入型 subagent 的上限＝prompt 紀律。資產源：ai-rules repo `skills/memory-audit/scripts/generate_index.py`（部署 = 複製進各專案 memory dir；Stop hook 自動重生成、PreToolUse hook 擋手寫）；副本新鮮度＝層 1 先 `cmp` 部署副本與資產源（stale 先 cp＋mv 原子刷新再 `--check`——Stop hook 對不符副本跳過執行）；`memory/_regen-failed` 標記存在＝gate 失敗（池超限或 frontmatter 違規——AIR-27 後兩者索引皆已照寫出：超限＝全部條目、違規＝跳過壞條目；修復後 regen 成功即清）。下表全量手檢僅適用未裝 generator 的池。數值調和：下表「≤24,000 bytes」＝兩型池共用 bytes 目標（generator 池＝info 縱深預警線、未裝池＝手檢目標）——單一數值源在 generator 註解；100/12,000 單一源＝hook `DESC_LIMIT`/`BODY_LIMIT`（generator `TRUNCATE_DESC` 對齊，`tests/test_memory_lifecycle.py` cross-layer 錨）。

| 檢查 | 命令 | 判準 |
|------|------|------|
| 索引預算 | `wc -l MEMORY.md` / `wc -c MEMORY.md` | 載入上限＝200 行或 25,000 字元（UTF-16，兩端同語義）先到為準，超限截斷（附 WARNING，尾端條目不載）。**bytes ≤24,000＝縱深預警線（與 generator info 同源）**＋ **行數軟上限 150**（逼近=合併建議觸發；預設值可在 `_audit-state.md` per-project 覆寫）。寫入端預算：frontmatter `description` ≤100 chars（hook >100 硬擋）、條目檔（含 frontmatter）≤12,000 chars（膨脹方向 hook 擋、收斂放行） |
| 索引重複 | `rg -o '\]\(([^)]+)\)' -r '$1' MEMORY.md \| sort \| uniq -d` | 0 輸出 |
| orphan（有檔無索引行） | `comm -23 <(ls *.md \| grep -v -e MEMORY.md -e '^_' \| sort) <(rg -o '\]\(([^)]+)\)' -r '$1' MEMORY.md \| sort)` | 0 輸出（`_` 前綴檔不進索引，排除） |
| missing（索引行無檔） | 同上，`comm -13` 反向 | 0 輸出 |
| 非 one-line-per-entry | `rg -v '^(#\| ?- \[\|$)' MEMORY.md` | 0 hits（索引只允許標題與一行條目；` ?` 容許頂格或縮排條目） |

### 層 2：內容核實 vs repo（預設必做）

條目多時 spawn agents 按段平行（每 agent 一段條目清單），少則主 session 直接做；**spawn 失敗（usage limit / 429）→ 降級主 session 分批直接核實，勿中止 audit**：

1. 每檔抽 **3-6 個 load-bearing claims**（路徑、符號、狀態宣稱）
2. 逐項對 repo 驗證：
   - 狀態宣稱（「已修」「已遷移」「已完成」）→ `git log --grep=<關鍵詞>` 找對應 commit
   - 符號/路徑 → rg + fd；**0 hits 先換 2-3 種 pattern 再判不存在**（單一 pattern 會 false negative）
3. verdict：✅ 準確 / 🟡 部分過時 / ❌ 核心被推翻 / ➖ 非程式碼可驗證（用戶偏好、決策脈絡——不標過時）
4. 聚合型條目（一條摘要多檔/多主題）每段抽驗
5. **self-report discount**：memory 記錄的 bug 要**實跑 repro**，不信自述

> 真實案例（self-report discount，mosaic_alpha）：memory 記「sync-stubs loop 有 bug」，實跑無法重現——歷史 commit 已修、memory 沒跟上；實跑反而挖出 memory 沒記的兩個真陷阱（NT source stub 舊於 venv、`set -e` 下 `diff | head` 截斷）。雙向教訓：memory 記的 bug 可能已修（過時），沒記的陷阱仍在（欠收）——兩者都只有實跑能揭露。

### 層 3：清理執行（用戶核可後；夜間 cron 輕量形態預先授權）

- 刪檔前 `rg "\[\[<name>\]\]"` 查反向引用——不留新 dangling（引用者同步改）
- **多池殘留掃描**：雙 harness 共用腳本跨多池部署後，清理/驗證掃描以「檔名 × 池」為維度——每個 pool 都要 rg（2026-08-30 實例：清理清單漏了 mosaic 池的同名測試條目）
- 合併檔帶 `merged_from` 標記（保留追溯）
- **cluster merge 機械觸發**：同主題散檔 ≥3（rg 主題詞/同前綴判定）→ merge candidate；併入目標優先既有最大 cluster（閾值可在 `_audit-state.md` per-project 覆寫）
- **蒸餾執行載體**：spawn `mem-distill`（role 定義＝`agents/roles/`、lite pin 生成於 zcode/ registry——registry 是 session 快照，須新建 session 才可解析）；prompt 給檔案清單＋每檔硬上限（預設 11,000 chars）＋desc 一併改寫 ≤100 指示
- **固化→濃縮同步義務**（user 2026-09-01 定案）：經驗固化成 ai-rules skill/rule 落地後，對應 memory 條目把已承載段**同步壓成指針**（觸發詞→skill 名＋一句精髓）；user 事實/事故實例/commit 錨留——固化與濃縮不同步＝兩處 drift（skill 演進、memory 停舊版）
- **收斂落點慣例**（與上互補，2026-09-03）：跨 repo 方法論→ai-rules skills/rules；模組知識（project 條目 durable lesson）→對應目錄的模組 AGENTS.md（3-6 行約束形態，非流水帳搬移；root 不動）；user/專案綁定事實→留 memory——三個載體各司其職，收斂時先判條目屬哪類
- **夜間收斂＝流出腿**（user 2026-09-03 定案「有進有出」，gate 22,500 配套）：每日夜間 cron（ZCode automation、owning workspace）跑本層收斂波，輕量形態**隨 cron 預先授權**（heavier 清理仍走「用戶核可後」）。波次：①`--check` 盤點＋弧線軟預警（列單檔 >8,000 chars 且近 7 天活躍的條目——掃描形態 `wc -m *.md` 排序交叉 `fd --changed-within 7d`；僅報告不擋，「禁加段」的軟執行）②觸發（gate FAIL、`_regen-failed` 在場、或逼近線）→ desc>100 掃尾＋同主題 cluster merge ③regen 至過、清 marker。掃尾紀律：**壓縮改寫非截斷**——被刪細節若有價值先落 body（desc 是索引摘要層）；不確定的條目跳過，禁大規模語義重寫（那是 full audit 的事）。週日治理 cron 跑 lite audit（健檢腿）——兩 cron 分工：每日流出、週日健檢
- 索引精簡：generator 池＝修條目檔 description（索引行是投影、禁手寫）；未裝池＝一行 = 主題 + 一個鉤子，細節留在條目檔內
- 每輪結束**重跑層 1**——驗證清理本身沒引入新問題

### 層 4：EP/任務狀態盤點

- 完成態信號：EP 已歸檔（任務家歸檔目錄——`ai-analysis/_tasks/done/`、`ai-analysis/_projects/<線>/done/`、或 `00-tasks/` 下 `done/`//`_done/`；判定單一源見 [metadata-sync](../metadata-sync/SKILL.md)）、工具被取代、等待條件已解除 → 清理候選
- **project-\* 計畫完結收斂**：計畫完成（commit 落地）後，對應 `project-*` 條目收斂——刪現況細節（未 commit 狀態、session 進度），留決策與教訓；主題重疊時併入相關 cluster
- 未完成 → **列表交用戶逐項判斷**；禁自行判斷「應該做完了」——宣稱完成 ≠ 實作落地，查實際檔案與 git 狀態

### 結束：寫狀態戳（見下方規格）

## Lite audit — 增量核實

層 1 機械量測 + 層 2' 增量核實：

```
git log --oneline <base_commit>..HEAD → 抽主題詞（模組名/命令名/遷移動詞）
→ rg <主題詞> memory/ 找命中條目
→ 只核實命中條目
```

drift 原因絕大多數是 repo 演進——git log 就是 drift 索引，沒碰過的主題不過時。

**流入率監控（lite 必做）**：比對本次 `--check` 輸出 chars 與狀態戳 `last_index_chars`（欄位缺＝首次：本次寫入、下輪起監控）——平均日增 >300 chars（總差值 ÷ 距上次 audit 天數）＝流入超過收斂速率訊號，lite 報告列 **mini-merge 觸發**（挑近重複/同主題條目 cluster merge），不等 full audit。寫入治理 hook（desc/body 硬擋，僅主 session）落地後正常流入應 <300/day。

## 狀態戳：`memory/_audit-state.md`

獨立檔（底線前綴**不進索引**；**不放 MEMORY.md frontmatter**——harness 管理索引檔有重寫風險）。欄位：

```
last_full_audit: <date>
last_lite_audit: <date>
base_commit: <sha>    # 用 sha 不用時間——精確對齊 git log 增量範圍
coverage: <n>         # 上次核實覆蓋條目數
last_index_chars: <n> # 上次 --check chars——lite 流入率監控基線
```

## 治理三分離

**advisory 報告 → 用戶核可 → 執行**。稽核不得自行刪改用戶想留的條目；報告每項附機械證據（file:line / 命令輸出）。驗證紀律（Claim→Evidence、self-report discount 理論基礎）見 [acceptance-evidence](../../rules/acceptance-evidence.md)，不重抄。

## 寫入端紀律：寫入六問與單一寫入點（寫 memory 前必查）

> 本段是 `rules/context-management.md`「Memory 生命周期規範」的承載體（rule 留 pointer）——寫入側紀律與稽核側同檔，記憶治理單一源。

harness auto memory 預設「one file = one fact」的「fact」操作定義 = **一個主題的教訓群（cluster）**，非一個事故；「check for an existing file — update rather than duplicate」的 update 目標 = 既有主題檔**加段**（非開新檔）。

### 單一寫入點：條目檔 frontmatter

**條目檔（frontmatter `name`/`description`/`type`）是唯一寫入點；`MEMORY.md` 索引是其機械投影，禁手寫**。索引載入上限＝200 行或 25,000 字元（UTF-16，兩端同語義）先到為準，超限截斷（附 WARNING，尾端條目不載）——手維護索引必漂移（截斷 → 查重漏同主題 → 近重複寫入 → 更肥 → 更截斷，正回授；2026-08-30 mosaic 56.6KB 實證）。

- 裝有 generator（`memory/_generate_index.py`）的專案：寫/改條目檔後跑 `python3 <memory-dir>/_generate_index.py`（Stop hook 亦自動重生成；手寫 MEMORY.md 被 PreToolUse hook 擋）。資產源與部署操作見本 skill generator 段
- 未裝 generator 的專案：手維護索引，cluster-first 沿用

### 寫入六問（新教訓產生時依序）

1. **任務終態 or 活知識？**（09-05 user 拍板，MOS-36 實證）→ 知識生命週期跟不跟任務綁：**任務終態**（弧歷程、session 流水、處理軌跡、已結案任務過程細節）→ 卡/report，**不進 memory**；**跨任務活知識**（行為教訓、活躍線 blocker、入口指針）→ 才繼續往下問。**此問先於「repo 可推導」**——它是分類判準（該不該進 memory），非來源判準（哪裡可查）
2. **repo 可推導 or 通用原則？** → git log / instruction 檔 / 程式碼 / **進行中 EP 的進度與狀態（住 EP 檔）**可推導 → 不寫；**LLM 通用做事原則/方法論**（與 user 個人化無關、任何 session 都適用）屬 rules/skills 知識——rule 缺就補 rule，不開 memory 條目。memory 收與 user／專案綁定的事實（偏好、糾正、專案約束、外部資源參照）——通用工程原則不收
3. **同主題已有？** → `rg -i <關鍵詞> <memory-dir>/` 全檔掃（**不信 MEMORY.md 索引**——載入截斷下尾部條目不可見）；命中 → 既有檔加段（段標題保留原始 name、標 original type）；**進行中弧線條目禁加段**——弧線進度每 session 追加是膨脹主因（實證：單檔 98 次 Edit 養到 84KB），等弧線收案一次性蒸餾；無 → 才開新檔
4. **project-\* 已完結？** → 任務閉環先收斂既有 project 條目（刪現況細節、留決策教訓）再開新檔
5. **尺寸預算？** → frontmatter `description` ≤100 chars（索引行原料；>100 被 PreToolUse hook 硬擋——hook 僅攔主 session，subagent 寫入不觸發）；條目檔（含 frontmatter）≤12,000 chars（膨脹超限被 hook 擋；收斂方向＝改後比原檔短，放行）——超額 = 內容該住 EP 檔/repo 的訊號；索引軟上限 150 行，逼近 = cluster merge／收斂觸發
6. **載體對嗎？** → 每次都要的紀律→rule／on-demand 方法論→skill／跨 session 事實→memory（手冊形內容不住 memory——它該住 skill）；**承諾/待辦→backlog 卡**（memory 只收事實與教訓，不收承諾）

量化清理（同主題散檔合併、收斂執行、audit）由本 skill 兩級稽核承載，寫入端只管六問。**弧結案蒸餾**（掛點＝[kanban-board](../kanban-board/SKILL.md) 結案兩步第三動）：弧收案時 owning session 將本弧 project_/feedback_ 條目一次性重寫為終態 facts——narrative 歸 repo（EP/卡/git），memory 留教訓；弧中「禁加段」的積累正是在此時收斂。**蒸餾形態定案**（MOS-36 實證，09-05）：蒸餾＝刪 repo 已承載（宣稱「repo 已承載」須逐項附 rg 驗證路徑——找不到證據的保守留）＋軌跡記卡（final-summary），**不新建歸檔檔**。**執行形態**：肥條目（>30K）派 mem-distill agent 隔離消化（context 不進主 session；prompt 必帶 repo 證據義務）；backref 修復與索引 regen 留主 session（清單外檔案 agent 禁碰）。實證：149K+37K+17K 三條歸線→5.1K（−96%）＋45K/36K 兩條→~5.9K（−86%），教訓帳 49 案流水壓六類一行後教訓模式零損失。**desc 三不**：不 commit hash／不日期流水／不 session id（皆 git/DB 可推導；hash 形態被 PreToolUse hook 硬擋）。
