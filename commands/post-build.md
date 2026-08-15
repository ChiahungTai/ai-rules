---
description: "build 後收尾鏈編排：code-review → judge-review → 修正迴圈 → consistency → metadata-sync。/post-build"
when_to_use: "After /build (or any substantial change set) to orchestrate the review chain automatically: diff triage decides which sub-chains run."
usage: "/post-build"
argument-hint: "無參數；自動 triage uncommitted diff"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Edit", "Write", "Agent"]
---

# /post-build — build 後收尾鏈編排

把「build 完手動跑 `/code-review` → `/judge-review` → `/consistency`（→ `/metadata-sync`）」的固定收尾序列編排成一次觸發。本命令**只做編排與 triage**，各步驟的方法論真相源在被編排命令本身，不重抄（防 single-source drift）。

## 受眾

軌道 ①（LLM 執行鏈）——機器自讀自判自修；終點輸出收尾報告給人類判讀是否 commit。

---

## 階段 0 — Diff Triage（決定跑哪些子鏈）

分析 uncommitted diff（`git status` + `git diff` + `git diff --cached` + untracked）：

| Diff 內容 | code 鏈 | docs 鏈 |
|-----------|---------|---------|
| 含 `.py`/程式碼變更 | ✅ 跑 | 視 `.md` 是否也有變更 |
| 僅 `.md` 變更 | ❌ 跳過 | ✅ 跑 |
| 兩者皆有 | ✅ 先跑 | ✅ 後跑（code 修正可能再動 doc，先收斂 code 再驗 doc，避免驗兩次） |

**Resume 場景**：若 `.review/<branch>.md` 已存在且有 `open` 狀態 findings（跨 session 從 reviewer session 帶回），跳過 code-review，直接從階段 2 接續。

印出 triage 結果：`[Post-Build] code=<yes/no> docs=<yes/no> resume=<yes/no>`

## 階段 1 — Code Review（僅 code 鏈）

執行 `/code-review`（無參 = uncommitted diff；dual-context 雙審查者規則見該命令模式 B）。本命令是**跨命令自動化場景**，code-review 產出寫 `.review/<branch>.md`（Finding Record 表格）供後續 judge/followup 讀。primed 側 context 依 code-review 模式 B 餵料清單（EP 路徑由 build 上下文帶入；無 EP 時依模式 B 降級規則處理）。

findings 全空 → 報告並直接進 docs 鏈。

## 階段 2 — Judge Review（僅 code 鏈）

執行 `/judge-review`，**輸入從 `.review/<branch>.md` 讀 findings，不需人工貼上**。產出 ✅/❌/⚠️ 決策清單。

⚠️ 需確認項：彙整到收尾報告給用戶，不阻塞其餘流程。

## 階段 3 — 修正迴圈（僅 code 鏈）

本命令是 judge-review 的**呼叫端**，負責 apply：

1. 實作所有 ✅ 採納項（反拖延原則：合理就當下落地）
2. 執行 `/followup-review`（讀 `.review/<branch>.md`）驗收
3. 未通過 → 再修 → 再驗收（**上限 3 輪**；超過 = 停下，殘留項列入收尾報告標「未收斂」——連續失敗比乾淨報告更糟，不硬撐）

## 階段 4 — Docs 鏈（僅有 `.md` 變更時）

1. 對每個變更的 `.md` 執行 `/consistency <檔案>`；fail 項當場修再驗（**重驗範圍 = 修正觸及的檔**，非整個 docs 鏈重跑；上限同階段 3 的 3 輪）
2. diff 觸及 Capabilities / `SYSTEM-MAP.md` / `dependency-graph.md` / `.kanban/` → 執行 `/metadata-sync`

## 階段 5 — 收尾報告（終點，不 commit）

```markdown
## Post-Build 收尾報告
- code 鏈：findings N（✅N/❌N/⚠️N）、修正 N 項、followup <通過|未收斂(殘留清單)>
- docs 鏈：consistency N 檔（pass N / fail-fixed N）、metadata-sync <跑/跳過>
- ⚠️ 待用戶確認：<決策清單>
- 下一步：`/commit`（commit 需人類確認，本命令止步於此）
```

---

## 執行約束

- **止步於 /commit 之前**：commit 需人類確認（硬規則，自主模式亦然）
- **不重抄被編排命令的方法論**：審查軸、judge 準則、consistency 六維都在各命令/skill 內，本檔只編排
- 修正迴圈上限 3 輪，超過即停（不硬撐原則）

## 流程位置

canonical review flow 以 [code-review.md](./code-review.md)「流程位置」為單一源。本命令是該 flow 中 `/code-review → /judge-review` 段 + docs 鏈（`/consistency` → `/metadata-sync`）的**執行載體**：

```
/build → /post-build（本命令：編排 code-review→judge-review→修正迴圈→consistency→metadata-sync）→ /commit
```
