# AI coding 開發工作流

> **定位**：本檔把 ai-rules 的工作從「想法」到「運維」收斂成一條可執行主軸，並描述多 session 下 primary、card worktree、board 與 memory 的目標 ownership；尚未落地處明確標示現況。

## 八站主軸

工作流沿同一條主軸理解：

```
① 想法 → ② 規劃 → ③ 開工 → ④ 實作 → ⑤ 驗證 → ⑥ 收斂 → ⑦ 沉澱 → ⑧ 運維
```

| 站 | 一句職責 | 關鍵載體 |
| --- | --- | --- |
| ① 想法 | 把未承諾想法留在 draft／pending 區；一旦承諾工作才由 board control plane 建立 card 與配置 id | Backlog.md draft/task、pending decisions、建卡預掃 |
| ② 規劃 | 把 card intent 轉成可跨 session 接手的 self-contained research／spec／EP，固定 baseline、scope、已決策與驗收 | card `desc`、task home、`research.md`、`spec.md`、`ep.md` |
| ③ 開工 | 為已存在 card 建立「由哪個 branch/WT 執行、起點是哪個 baseline、session cwd 在哪」的機械身份 | `wt-open`、card `In Progress`/refs、persistent card WT、freshness check |
| ④ 實作 | 讓 code/rules/skills/docs/EP 寫入在該工作 execution plane 內完成，避免共享 checkout 的 branch/cwd 被其他 session 改變 | card WT；免卡小修走 ephemeral WT fast-path；implement/TDD |
| ⑤ 驗證 | 讓 claim 對上足夠獨立的 evidence；negative claim 不以單次文字搜尋冒充行為證明 | tests、integration/demo/POC、code-review、acceptance evidence |
| ⑥ 收斂 | 把工作 review、修正並依既有 rebase→ff-only 規則吸回 owning line，再完成 session/card 收尾 | post-build、working branch、`wt-close`、finalization |
| ⑦ 沉澱 | 將完成能力、設計理由與真正值得跨 session 留存的事實放回正確 carrier；memory 不成為規範副本 | AGENTS/Capabilities、architecture/blueprint、memory pointer/facts |
| ⑧ 運維 | 讓 hooks、排程、備份、清理與 fresh-machine recovery 可重建，避免 machine-local state 只存在某台機器或某次 session | hooks、schedule registry、launchd、memory bundle、onboarding runbook、code-reality |

八站是整體敘事，不取代各 skill 的細部 workflow。免 UC 的小型 fix 可以不建立 card/EP，但仍須有明確 execution plane、validation 與收斂路徑。

## Worktree 形態定案

正式裁決採「control plane 與 execution plane 分離」，分界按**寫入責任**，不是按任務時間或大小。

### Primary checkout：control plane — ❌ target 尚未落地

目標形態：

- primary 固定承擔 owning line／trunk 的 control-plane checkout，不供一般實作 session 任意切 working branch。
- primary 的 repo 寫入職責限於 board/card control state：task id allocation、status、refs、final summary 與同類 runtime metadata。
- `backlog browser` 固定從 primary cwd 啟動，使 board 有唯一 working-copy owner。
- code、rules、skills、一般 docs、EP、test、script 的工作寫入走 execution plane。
- 建立／結束 execution WT 的 helper 從 control plane 發起，並用 lock 序列化 board state 變更。

目前 repo 的現行 git 慣例仍是「起手式後在 primary 自 `main` checkout card branch」；因此上述 permanent control-plane 行為尚不能當 runtime 事實。

### Card worktree：execution plane — ❌ target 尚未落地

有 card 的寫入型工作目標採：

```
1 card = 1 branch = 1 persistent worktree
```

- branch 命名、owning line 與最終 rebase/ff-only 規則仍由 repo `AGENTS.md`「git 慣例」定義。
- WT 從 committed owning line 建立；未提交 primary working-copy 狀態不視為 card baseline。
- 一張 card 跨 session 接續時重用同一 persistent WT。
- 同一 card identity 可供 writer 與 reviewer 指向同一份工作狀態；**共用 identity 表示可共同讀取並按流程串行寫入，同檔並發寫仍按 collaboration constraints 處理；board metadata 另外受 primary single-writer 限制。**
- execution plane 可讀 card state；目標架構下不直接寫 board runtime metadata，status/ref/finalization 由 control plane 處理。

目前 `wt-open` / `wt-close` 與 persistent card WT lifecycle 尚未實作，因此這一節是 target contract。

### 免卡小修：ephemeral WT fast-path — ❌ target 尚未落地

全域 guide 允許 simple bug fix／小型調整免 UC、免建 card；WT 化不能反過來強迫所有微小工作先造卡。

目標 routing：

```
免卡 + 會寫 repo
        ↓
建立 ephemeral working branch / WT
        ↓
修改 + 驗證
        ↓
依既有 consent 做 commit / 收斂
        ↓
移除 ephemeral WT
```

約束：

- 不為了取得 WT identity 人工製造假 card。
- ephemeral WT 只適用真正符合 guide 小型免 UC 條件的工作；碰單位、時區、會計、風控、跨模組架構等仍依既有規模規則升級。
- 若修改過程擴大成 standard+ 工作，停止 fast-path，先建立正式 card/EP，再轉 persistent card WT。
- primary 仍不因此重新成為一般 code writer。

具體 helper 是否由 `wt-open --ephemeral`、另一個 wrapper 或 harness-native WT 機制承載，由基建弧決定。

### 唯讀／顧問 session — ⚠️ 現有做法可支撐，尚未統一機械化

- 只讀當前 card 實作：target 形態下優先進該 card WT，使所見 source 與 writer 一致。
- 跨 card audit／顧問：可使用 clean read-only checkout、detached/ephemeral WT 或其他不會改變 active writer cwd/branch 的環境。
- 純架構討論、外部顧問、report 閱讀不必為形式上的「一 session 一 WT」建立 persistent working copy。
- 跨 repo 工作回到各 repo 自己的 ownership，不把 ai-rules primary 當另一 repo 的 execution plane。

## 過渡條款：現行 git 慣例與 target WT 形態

目前 repo AGENTS.md 的有效規則仍要求卡開工後從 `main` 執行 `git checkout -b air-<N>`，收尾再 checkout `main` 並 ff-only merge。這與「primary 永久留 control plane」的 target 形態互斥。

過渡期規則：

1. **WT 基建弧落地前**：repo `AGENTS.md` 現行 git 慣例仍是 runtime authority；本檔 WT 章節只能作 target architecture，不得要求 session 假裝 `wt-open` 已存在。
2. **基建弧落地時**：同一弧同步改版 repo `AGENTS.md`「git 慣例」與 kanban 消費接線，把「primary checkout card branch」換成 control-plane + WT lifecycle。
3. **改版完成後**：`workflow.md` 的 target 標記才能依實際驗證結果升為 `✅/⚠️`。
4. 過渡期間不得混合兩種 lifecycle，例如 primary 已切 card branch、同時又建立同 card persistent WT，否則 ownership 再次不唯一。

## 寫入責任決策樹

```
這個動作會寫入嗎？
│
├─ 否
│  ├─ 只看當前 card → 讀該 card 的 current execution state
│  └─ 跨 card / 顧問 / audit → clean read-only checkout 或 ephemeral WT
│
└─ 是
   │
   ├─ 寫 board/card control state？
   │  └─ primary control plane
   │     └─ 經 single-writer lock 做 id / status / ref / finalization
   │
   ├─ 有 card，且寫 code / rules / skills / docs / EP / tests / scripts？
   │  └─ 該 card persistent WT
   │
   ├─ 無 card，且符合 guide 的小型免 UC 條件？
   │  └─ ephemeral WT fast-path
   │     └─ scope 擴大時升正式 card
   │
   └─ 寫另一個 repo？
      └─ 到該 repo 自己的 control/execution topology
```

判斷核心是「這份 state 的唯一 writer 是誰」。execution identity 可以多人共讀；寫入仍要有明確 serialization／ownership。

## 記憶池拓撲 — ⚠️ primary canonical pool 已落地；card-WT 接線尚未落地

### Primary canonical state：✅

primary repo 內既有 canonical state：

```
<primary>/.agents/
├── memory/          # 實體 canonical pool
└── memory-inbox/    # 實體 canonical inbox
```

WT 化沿用這個 canonical state，不重新遷移 memory 主體。

### Card WT 接線：❌ target

每個 persistent card WT 目標只建立兩條 repo-local symlink：

```
<card-wt>/.agents/
├── memory       -> <primary>/.agents/memory
└── memory-inbox -> <primary>/.agents/memory-inbox
```

約束：

- 不複製 live memory pool；每 WT copy 會形成多份 snapshot，破壞單一真相、CAS、attribution 與 consolidation。
- 不 symlink 整個 `.agents/`；只共享已裁決的 `memory` 與 `memory-inbox` state。
- 夜間 consolidation 仍只消費一份 canonical inbox/pool。
- primary 既有 CC/ZCode memory topology 不因 WT 化重新設計。
- Muse secondary WT 對 directory symlink 的 native memory 能力可能退化，因此 native `read_memory` 不列為所有 secondary WT 的 invariant；必要時按正式契約使用可達 canonical state 的 fallback。
- Muse write gate 必須最終把寫入導向 canonical inbox。

Muse hook 接線的實作策略由 WT 基建弧在兩案中選一並驗證：

1. 每個 WT 生成正確的 machine-local `.muse/hooks.json`；
2. 將 hook implementation 參數化，使同一生成流程可顯式取得 canonical repo/inbox。

本藍圖不預先指定其中一案。

## Board single-writer — ❌ target 尚未落地

目標 invariant：

- backlog/config.yml 使用 `check_active_branches: true`，讓多 WT repo 能發現其他 branch 已 commit card，並讓 cross-branch id 掃描生效。
- `backlog browser` 從 primary control plane 啟動。
- `backlog/tasks` runtime metadata 只有 control plane 是 writer。
- card WT 不直接執行會修改 card runtime state 的 `backlog task edit/create/complete`。
- 建卡 id allocation、開工 status/ref、收尾 finalization 經 control-plane helper，在 repo-local single-writer lock 下執行。
- 建卡保留跨 WT filesystem max-id 預掃，補 `check_active_branches` 看不到 untracked/staged card 的盲區。
- `check_active_branches` 只解 cross-branch discovery；working-copy local card 仍可能遮住其他 branch 同 id 狀態，因此不能以 config flag 取代 single-writer ownership。

目前 backlog/config.yml 仍是 `check_active_branches: false`。

control-plane metadata 若需要自動 commit，基建弧必須同步對齊 outward-action consent；現行規則明確特赦的是建卡 commit，blueprint 不自行把授權擴張到 status/ref/finalization commits。

## `wt-open` / `wt-close`：目標 transaction — ❌ 尚未實作

`wt-open` **只接收已存在 card**。建卡與 id allocation 屬①想法站的 board-control 工作，不塞進開工 transaction。

### 1\. 取得 control-plane lock，讀取已存在 card

`wt-open <card>` 在 primary 取得 single-writer lock後：

- 確認 card 已存在。
- 讀 baseline、已決策、驗收、notes、refs。
- 依 kanban 開工語義處理 `In Progress` 與開工 refs。
- 若這些 metadata 必須成為新 WT 的 committed baseline，依基建弧最後裁定的 commit/consent contract 處理。

找不到 card 時直接停止；`wt-open` 不代建卡、不 allocate id。

### 2\. 建立或重用 persistent card WT

由 committed owning line 建立：

```
owning line → card branch → persistent card WT
```

- branch 命名沿 repo `AGENTS.md` 的 repo-specific 規則。
- branch 已存在時，先驗 owning line 到 branch 的 commits 是否確實屬此卡。
- 非本卡殘留不得直接重用。
- WT path 使用可由 card/branch 機械推導的固定形態，避免 handoff 依賴人記路徑。

### 3\. 驗證 baseline 與 execution identity

啟動 writer 前至少驗證：

```
{git toplevel, current branch, card id, baseline}
```

並執行既有 freshness 語義：

- card baseline 對目前 owning line / HEAD。
- baseline 後已有 commit 時，判斷是否碰 card scope。
- notes/relay 宣稱回查目前 repo state。
- WT isolation 不構成跳過 freshness check 的理由。

失敗即停止 open transaction。

### 4\. 接 shared state，從 WT cwd 啟動 session

建立 card WT 的：

```
.agents/memory
.agents/memory-inbox
```

兩者都解析到 primary canonical state。

再依 WT 基建弧選定的 Muse 接線方案生成或配置正確 hook。

完成後以 **card WT 作 cwd** 啟動寫入型 ZCode／Claude 等 session；branch、cwd、HEAD、dirty state 後續皆以 Git/current filesystem 現查。

open transaction 成功後釋放 control-plane lock。

### 5\. `wt-close` preflight 與 git 收斂

實作、驗證、review、必要修正與 commit consent 都先在 execution WT 完成。

`wt-close` 重新取得 control-plane lock，並驗：

- target WT / branch identity 正確。
- working tree 無未處理變更。
- commits 與工作 scope 相符。
- owning line 的新變更沒有使原 baseline／relay 假設失效。

接著沿既有收斂規則：

1. owning line 沒前進且 branch 可直接吸收 → ff-only candidate。
2. owning line 已前進 → rebase working branch onto owning line。
3. rebase 成功 → owning line ff-only absorb。
4. ff-only 仍失敗 → 停下查原因。
5. owning line / trunk 本身不被 rebase、不 force。

### 6\. Finalization

只有 git convergence 成功後，primary control plane 才進行：

- status → `Done`
- final summary
- 完成態 refs
- 既有流程要求的 Capabilities／metadata 結算
- 有值得保存的 project memory 時，按 memory-audit 寫入端紀律蒸餾終態 facts

board `Done` 應表示工作已被 owning line 接收，不先於 convergence。

### 7\. 移除 execution plane

finalization 完成後：

- 移除 card WT。
- 刪除已被 owning line 完整吸收的 working branch。
- 用 `git worktree list` 與 ancestry 做最終確認。
- 釋放 lock。
- card 留在 `Done`；archive/complete 仍由既有延後清理與 precheck 負責。

任一步失敗都要保留可判斷的 branch/WT/control state；不得靠刪 WT 或 branch 製造表面完成。

## 收斂序列：既有 git 紀律不變

WT target 改的是 working-directory ownership，不改 trunk-based convergence：

```
execution WT
  │
  ├─ work / validate / review / commit
  │
  ├─ owning line advanced?
  │      ├─ no  → ff-only candidate
  │      └─ yes → rebase working branch onto owning line
  │
  └─ owning line ff-only absorb
         │
         └─ success → finalization → remove WT/branch
```

仍維持：

- trunk 不 rebase。
- 不以 merge commit 迴避 ff-only 失敗。
- branch 承載工作生命週期；WT path 承載穩定 execution location。
- `/rebase all` 等 repo 級操作仍服從既有 active-card 護欄。
- commit consent 不因 WT helper 自動失效。

## Relay freshness check 保留

persistent WT 能解 shared checkout 被別 session 切 branch 的競爭，但不會讓舊資訊自動更新。

因此開工 freshness invariant 保留：

```
card baseline
    ↓ compare
current owning-line / HEAD
    ↓
relay / notes claim
    ↓ mechanically verify
current repo state
```

原則：

- relay 是接手說明，不是 repository truth。
- branch、cwd、HEAD、dirty state、檔案內容由當前環境讀。
- baseline→HEAD 有新 commit 時，先判是否碰工作 scope。
- persistent WT 不構成跳過 baseline 驗證的理由。

WT 處理的是 execution-location interference；relay freshness 是獨立問題，兩者不能互相替代。

## 六線波次在 WT 形態下的語義

衝突矩陣 O1–O8 描述 shared files、定義源與語義先後依賴。每 card 一個 WT 不會讓這些衝突消失。

第一輪排序維持：

```
L6 = AIR-68：跨 repo，可獨立平行

ai-rules 主序列：
L1 = AIR-58
  ↓
L3 = AIR-70
  ↓
L2 = AIR-67
  ↓
L4 = AIR-60
  ↓
L5 = AIR-63
```

- O1 的 `work-order` 是 L3/L2/L4 真正同源衝突。
- O2 要求 L4 先於 L5。
- O3/O5 讓 L4 等 L3/L2 定義先收斂。
- O4/O6/O7 是較弱共享面，WT 只能降低 checkout interference。
- O8 的 `memory-audit` 落點仍由 owning arc 裁決。

WT 基建落地後，可以移除「因共享單一 checkout，所以同 repo card session 絕不能並存」這個機械限制；是否真的平行仍依 shared-file / semantic overlap 判斷，不能直接打散既有波次。

## 待建基建

目前 target architecture 尚缺以下 substrate：

- `wt-open`：只接已存在 card，建立／重用 persistent card WT。
- `wt-close`：preflight、rebase/ff-only、finalization、WT/branch removal 的可重入 transaction。
- primary board single-writer lock。
- [backlog/config.yml](../../backlog/config.yml) 多 WT 設定與實際 board 驗證。
- card WT 的 canonical `memory` / `memory-inbox` symlink 接線。
- Muse secondary-WT hook 接線；「每 WT 生成 hooks.json」與「hook 參數化」二選一由基建弧裁決。
- 免卡小修的 ephemeral WT fast-path。
- control-plane status/ref/finalization 與 commit-consent contract 的一致化。
- repo `AGENTS.md` git 慣例從現行 primary checkout 模式遷到 WT lifecycle。

這些項目應由同一個 WT 基建弧整體收斂；完成前仍以「過渡條款」中的現行 repo 規則執行。
