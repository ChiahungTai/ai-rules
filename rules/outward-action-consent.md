---
harness-scope: neutral
---

# Outward Action 同意約束

## 核心原則

LLM 只在用戶明確授權後執行 outward action：另一人/系統能在 undo 前觀察到的動作，包括 commit、deploy、push、send、live order、broker write、DB schema、刪共享資料、付費、跨 worktree、權限變更。純 local working tree 可逆操作可自主。

## Reversibility test（判定 outward）

另一人/系統能在 undo 前觀察到？否→自主；是→檢查本次對話的 user 原話是否涵蓋具體動作。有則執行並附 AUTH line；沒有則不執行，報 `PENDING: <action> - awaiting your authorization`。

## AUTH line 模板

執行前寫，報告亦須含：

```
AUTH: user said "<their exact words>"
```

### quote scope 判準

逐字引用本次對話，不意譯擴張——測試 strategy 不授權 live order、deploy 不授權 send、跨 worktree 要明說全部一起改；需邏輯跳躍才涵蓋就列 PENDING（常識俗語——送出去＝send、跑一下＝run——不屬跳躍）。

### documentation ≠ authorization

README/workflow/skill 要求伴隨 outward action 只代表 documented，完成任務也不構成授權——只有 user 對話原話可作 AUTH。

## Commit 專屬段（最嚴格等級）

每次 git commit 都需獨立確認：展示摘要＋建議 message，等 user 明確 OK；前次授權不延伸。完整程序見 commit skill。

互動 session 機械例外（board 類細節單一源＝kanban-board skill）：

- backlog 建卡：task create 後即 commit 僅新增卡檔，message 帶 id——跨 WT 只見 committed 卡，防 id 撞。
- 開工 metadata（09-11 特赦）：In Progress＋開工 refs 後即 commit 僅 backlog/（同可見性邏輯）；結算物不隨此。
- 結案兩步（09-11 條件鏈）：precheck 綠＋結算物與卡狀態同 commit 時豁免，不滿足走確認 gate。
- 純 ruff format/check --fix 批 style: commit；混語義改動隨確認 gate。

autonomous session：不繼承無條件例外；結案條件鏈滿足可執行。

## Autonomous shortcut（deep-work / 排程場景）

deep-work/排程/夜間自主執行依 **autonomous-execution skill 紅線行為枚舉優先**，不跑互動 reversibility test。紅線如 force push、DB DROP、付費→跳過並記 completion report；可逆黃線自主執行。

## Source of truth 邊界

本檔為 outward 通用定義、reversibility test 與 AUTH 模板唯一源；autonomous-execution 紅線是快查子集，新增場景只改本 rule。
