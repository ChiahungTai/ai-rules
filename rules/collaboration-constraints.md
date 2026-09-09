---
harness-scope: neutral
---

# 協作約束

## 理解優先實作

需求不明先複述理解、列可能解讀並澄清，不猜測實作；疑問彙整一次問，避免每次往返重送 context。非硬 gate 的確認集中完成報告；commit、破壞性、單向門依 [outward-action-consent](outward-action-consent.md)。

## 事實查證原則

分析結論須依實際程式碼，附 path:line＋具體特徵，不以 LLM 經驗代替證據。

### 對外部系統宣稱的查證（含概覽）

「X 支援/不做 Y」即使只出現在概覽或順口一句也須查證。未驗證就是未驗證；事後自審共享原盲點，不能代替獨立證據（見 [acceptance-evidence](acceptance-evidence.md)）。

- AGPL 可研究行為/設計，禁搬碼或逐行翻譯；實作對自己的規格寫，避免衍生汙染。
- fork/divergent 依賴的 state-dependent 行為查本地 runtime/`.venv/` source，upstream 文檔不代表 fork。

### 破壞性選擇的查證觸發

刪除/整併看似等價的無測試檔案，先查 README 權威指名、Capabilities 入口、git 活躍度與內容完整性＋backlog 卡（To Do／In Progress／drafts）是否提及或依賴，不憑檔名選。存活檔只有路徑修正而無內容吸收，是刪錯訊號，停下重判。（standup 誤刪實證：恢復事實只記在 AIR-52 desc，原清單不含卡面）

## 具體明確表達

避免「大概/可能/應該可以」；提供具體步驟與 path:line。技術對比用 `❌ 錯誤`／`✅ 正確`＋範例＋`💡 原理`。

## 接收建議與回饋（反 Sycophancy）

用戶/其他 AI/reviewer 的建議先查證再評估，不盲目同意或用感謝取代修正：READ→UNDERSTAND→VERIFY against codebase→EVALUATE→RESPOND→IMPLEMENT。核對技術適用、既有功能與決策；查不了明說，錯誤建議附理由反對，成立就簡述修正。盲改指標公式會靜默污染回測。

YAGNI（刪）與 filter trap（驗證不能刪）的判別見 acceptance-evidence skill。

## 工作目錄紀律

- 不 cd 其他 repo；以 harness Primary working directory 為準。跨 repo 讀取用完整路徑或 `git -C`，執行命令用完整路徑，避免改錯 worktree。
- 他人未提交變更預設不相關，不審不改不順手修；commit 只 add 指名檔。**目標檔已有他人變更或同區域不同改法才是停下確認的機械衝突訊號**，否則各自進行。

## Agent 派發與產出回收

跨 repo 寫入由主 session 負責；spawn 前確認 worktree 能力，優先目標 repo session。agent 寫不進目標就寫當前 repo，由主 session 回收，禁把跨 repo 寫入責任丟給受限 agent，避免做到末端才失敗。

spawned/automation session 只在卡的 owning WT 操作；按各 repo 線 tag↔WT 判定，不能判定就回報主 session。真實案例：owning=main 的卡被 warrant 監控 session 錯誤結案，因對方規則未載入。

會寫檔的 agent prompt 必注入：

1. 禁 /tmp，產出留當前 repo/worktree。
2. 寫不進指定路徑回報「環境限制：我寫不進 X」，不可退到 /tmp。
3. 暫存分析/草稿/POC 集中 `.agent-tmp/`；post-build 預設清理，夜掃兜底（`.agent-tmp/`/`.at-contexts/` 7d，`.review/` 30d）。
