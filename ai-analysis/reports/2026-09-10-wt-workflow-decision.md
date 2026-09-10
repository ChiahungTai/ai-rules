# WT 工作流形態裁決（2026-09-10 三方：GLM 5.3 主導 × muse × codex）

> 背景：user 觀察「③開工站」斷點最多（relay 過時×6、外卡落錯 branch×3、checkout 中途被切、卡撞號×2），指示上網研究業界＋問雙顧問。業界查證：Claude Code 官方原生 `--worktree`（每 session/task 一 WT＋branch、隔離四項強制、共享僅 .git/plugins/權限、lock/sweep 清理）——官方語意隱含單 WT 多 session 共改應避免。雙顧問全文：`.agent-tmp/bridge-{muse,codex}-wt-out.txt`（jobs mtuxxx；本文固化後 blueprint 改指本文）。

## 定案

```
primary WT  = control plane——board/卡狀態唯一 writer；一般 code session 不再於此 checkout
card WT     = execution plane——寫入型 session 一律 1 卡 = 1 branch = 1 WT（repo 外路徑，名=branch 名）
memory 池   = primary 實體（AIR-54 形態不動）＋ card WT symlink（.agents/memory 與 memory-inbox 兩項，非整個 .agents/）
board       = 現 primary 升格 board-control/main（非第二 checkout——git 不允許雙 WT 持同 branch）
```

## 關鍵裁決點

1. **混合遷移、分界按寫入責任**（codex 勝出 vs muse 的任務大小分界）：「半天小修留主 WT」例外**刪除**——primary 一旦仍可寫 code，checkout ownership 模糊即復活（rules 檔 M 撞實證——session 中途被切 checkout）。muse 複審接受此取捨（overhead 可優化 vs ownership 模糊是結構性故障）並建議 `wt-open` fast-path（單檔小修復用 card WT）吸收成本論點。決策樹：寫 backlog control state→board-control；寫 code/rules/skills/docs/EP→card WT；只讀當前卡→該 card WT；跨卡唯讀審查→任一 clean checkout；跨 repo→各 repo 自己 WT。
2. **記憶池＝per-WT symlink**：cp 否決（N 池分叉毀 CAS/consolidation/attribution 單一真相）；池遷 repo 外否決（重開 AIR-54，遠期不動）。實證：codex 三 WT 的 `.agents/` 天生空（gitignored 不隨 checkout）；muse 在次 WT 目錄 symlink 失去 native `read_memory` 降級 `read_file`（EP F2 既有降級線索，接受）。並發寫入靠既有 memory-audit 波前二分/mtime×keeper 接（同樹→跨樹，同套 gate）。
3. **board 真相完整形態**（codex 實測補強 muse 方案）：Backlog browser 以啟動 cwd 為基準＋**同 id local card 遮蔽別 branch 新版**——`check_active_branches=true` 只補掃描不補真相。加釘：卡 runtime metadata（status/ref/id allocation）**只有 board-control 可寫**，wt-open/close 經單一 lock 操作，**並配跨 WT 檔案系統 max-id 預掃**（muse 案對策——lock 管 allocation、預掃覆蓋 git 掃描看不見的 untracked/staged 盲區，雙補）——撞號×2 的正解。outward 特赦需裁定是否擴及 metadata commit（避免 dirty main 成新摩擦——user 裁）。
4. **半殘陷阱**：`.muse/hooks.json` 寫死主 WT 絕對路徑——card WT 內 muse「寫得到讀不到」；wt-open 必須重跑 `setup-muse-hooks.sh` 或腳本參數化。
5. **接線**：`scripts/wt-open.sh <卡號>` ／ `wt-close.sh` 慣例腳本（原 muse 案命名 `wt-new/wt-close`，定案更名 open 對稱 close；muse 另建議單檔小修 fast-path 復用 card WT）——開工 transaction：worktree add〔自 owning 線〕→池/inbox symlink→hooks 重跑→{toplevel,branch,card,baseline} 驗證→回報 cwd 啟動 ZCode；收尾 transaction：dirty/baseline 驗證→既有 rebase/ff-only 收斂→board Done/ref finalization→worktree remove。branch/cwd 每次從 Git 現查，relay 只當說明不當位置真相。（業界參照：Claude 官方 `--worktree` 對 isolated WT 有 file-edit/cwd/git-redirect/command-shape 四項強制隔離。）
6. **過渡時點**：main clean＋六線全 To Do＝現在遷（wave -1 前置）；dirty/in-progress 的弧用舊形態收完再切（新 WT 從 committed state 出發）。
7. **不因 WT 消失的**：O1-O8 語義/共享檔衝突（藍圖排序照跑——第一輪仍序列，拿掉「同 repo 絕對不能平行」機械限制，跑一輪後按實際 overlap 放開）；relay 過時（freshness check 保留——起手式 baseline→HEAD 核對）。
8. **Claude 腿**：`--worktree` 對 protected main 有 isolation——symlink 池方案在 Claude 腿啟用前需一次 write→inbox L4 probe；ZCode 主力先落。

## 預期效果

外卡落錯 branch／checkout 中途被切→**結構性歸零**；撞號→board-control 單一 allocation 消除；relay 過時→減少不歸零（freshness 保留）；記憶池→零遷移（AIR-54 不動）。

## 待建（基建弧候選範圍——開卡與否經 blueprint 對齊後定）

wt-open/wt-close 腳本、check_active_branches 翻 true＋kanban 單一 writer 條款、muse hooks 參數化、outward 特赦擴展裁定、試點一卡驗證、AGENTS.md git 慣例 WT 版。
