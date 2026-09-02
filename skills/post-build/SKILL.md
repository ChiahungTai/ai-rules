---
name: post-build
when_to_use: "After /implement (or any substantial change set) to orchestrate the review chain automatically: diff triage decides which sub-chains run."
argument-hint: "無參數；自動 triage（uncommitted 或 EP baseline 任務弧）"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Edit", "Write", "Agent"]
description: build 後收尾鏈編排 — code-review → judge-review → 修正迴圈 → consistency → metadata-sync → Report Shell refresh（hook 2：實作章節＋badge ✅＋持久 delta tour）一次觸發。只做編排與 diff triage，方法論真相源在各被編排命令/skill。觸發詞：build 後收尾、post-build、收尾鏈、review chain 自動化、commit 前收尾。
---

# post-build — build 後收尾鏈編排

把「build 完手動跑 code-review → judge-review → consistency（→ metadata-sync）」的固定收尾序列編排成一次觸發。本 skill **只做編排與 triage**，各步驟的方法論真相源在被編排命令本身，不重抄（防 single-source drift）。

**受眾**：軌道 ①（LLM 執行鏈）——機器自讀自判自修；終點輸出收尾報告給人類判讀是否 commit。

被編排項目全為 skills（`code-review` / `judge-review` / `followup-review` / `consistency` / `metadata-sync`）：Claude 端以 slash（`/code-review`）或 Skill tool 調用，ZCode 端以 Skill tool 調用——跨 harness 統一。

---

## 階段 0 — Diff Triage（決定跑哪些子鏈）

分析 uncommitted diff（`git status` + `git diff` + `git diff --cached` + untracked）：

| Diff 內容 | code 鏈 | docs 鏈 |
|-----------|---------|---------|
| 含 `.py`/程式碼變更 | ✅ 跑 | 視 `.md` 是否也有變更 |
| 僅 `.md` 變更 | ❌ 跳過 | ✅ 跑 |
| 兩者皆有 | ✅ 先跑 | ✅ 後跑（code 修正可能再動 doc，先收斂 code 再驗 doc，避免驗兩次） |

**逐段 commit 後（弧模式）**：uncommitted 空（或僅尾段殘留）且 context EP 記有 baseline → 切**弧模式**：triage 與階段 1 的審查對象改為 `git diff <baseline>..HEAD`（+ uncommitted；模式細則見 [code-review](../code-review/SKILL.md)「任務弧模式」）。context 無 EP 記憶（跨 session 接續）→ **從殼讀 baseline**：任務家 `*/index.html`（`ai-analysis/_tasks/`、`ai-analysis/_projects/*/tasks/`、或 `00-tasks/`——探測見 [illustrate html-mode](../_common/illustrate-html-mode.md)「產物位置分流」）殼頭部聲明 EP 路徑＋baseline hash（hook 1 起攜帶）——baseline 傳遞不依賴 build session context 存活。uncommitted 空且無 EP baseline（context 與殼皆無）→ 印 `[WARN] no diff（逐段 commit 已落地？弧模式需 EP baseline）` 並停止——收尾鏈靜默 no-op 等於大聲錯誤被靜默化。

**Resume 場景**：若 `.review/<branch>.md` 已存在且有 `open` 狀態 findings（跨 session 從 reviewer session 帶回），跳過 code-review，直接從階段 2 接續。

印出 triage 結果：`[Post-Build] code=<yes/no> docs=<yes/no> resume=<yes/no> mode=<uncommitted|arc>`

## 階段 1 — Code Review（僅 code 鏈）

執行 `code-review`（[skills/code-review/SKILL.md](../code-review/SKILL.md)；無參 = uncommitted diff，弧模式（階段 0 判定）= EP baseline..HEAD——見該命令「任務弧模式」；dual-context 雙審查者規則見該命令模式 B）。本 skill 是**跨命令自動化場景**，code-review 產出寫 `.review/<branch>.md`（Finding Record 表格）供後續 judge/followup 讀。primed 側 context 依 code-review 模式 B 餵料清單（EP 路徑由 build 上下文帶入；含 delta_tour 對照——code_reality baseline snapshot 在場時機械產「EP 宣稱模組 vs 實際變動」對照，機制見模式 B；無 EP 時依模式 B 降級規則處理）。

findings 全空 → 報告並直接進 docs 鏈。

## 階段 2 — Judge Review（僅 code 鏈）

執行 `judge-review`（[skills/judge-review/SKILL.md](../judge-review/SKILL.md)），**輸入從 `.review/<branch>.md` 讀 findings，不需人工貼上**。產出 ✅/❌/⚠️ 決策清單。

⚠️ 需確認項：彙整到收尾報告給用戶，不阻塞其餘流程。

## 階段 3 — 修正迴圈（僅 code 鏈）

本 skill 是 judge-review 的**呼叫端**，負責 apply：

1. 實作所有 ✅ 採納項（反拖延原則：合理就當下落地；**先規劃整批再批次套用**——目標檔先 Read、多個 Edit 同 block 發、鄰近一行式小修合併、真依賴才序列，見 [tool-discipline](../../rules/tool-discipline.md)「獨立呼叫批次化」+「檔案修改禁令」（Read 紀律））
2. 執行 `followup-review`（[skills/followup-review/SKILL.md](../followup-review/SKILL.md)；讀 `.review/<branch>.md`）驗收
3. 未通過 → 再修 → 再驗收（**上限 3 輪**；超過 = 停下，殘留項列入收尾報告標「未收斂」——連續失敗比乾淨報告更糟，不硬撐）

## 階段 4 — Docs 鏈（僅有 `.md` 變更時）

1. 對每個變更的 `.md` 執行 `consistency`（[skills/consistency/SKILL.md](../consistency/SKILL.md)）；fail 項當場修再驗（**重驗範圍 = 修正觸及的檔**，非整個 docs 鏈重跑；上限同階段 3 的 3 輪）
2. diff 觸及 Capabilities / `SYSTEM-MAP.md` / `dependency-graph.md` / `backlog/` → 執行 `metadata-sync`（[skills/metadata-sync](../metadata-sync/SKILL.md)）
3. repo 有 `.tours/manifest.toml` → 跑 `code-reality tour_validate --manifest --repo .`，FAIL 列入收尾報告（tour corpus audit 接線——工具語義見 [code-reality](../code-reality/SKILL.md)）

## 階段 5 — Report Shell refresh（hook 2——commit 前最後穩定點）

本 EP 對應殼存在（任務家 `<task>/index.html`——execution-plan 定稿 hook 1 所建）時，在收尾鏈收斂後 refresh（掛點規格單一源見 [illustrate html-mode](../_common/illustrate-html-mode.md)「殼生命週期掛點」）：

1. **實作章節生長**（同一殼的第二幕；內容＝殼規格「敘事骨架變體」實作完成報告列）：做了什麼（分組檔案地圖）／驗證證據（命令+exit code）／delta 前後對照（archify compare，有圖時）／認知誤差點＋回源連結——**反映修正迴圈後最終態**（排在階段 3 修正迴圈之後，正是為此）
2. **badge ✅**（implement 階段 5a 已同步則驗證、未同步則補上；中間段殘留 → 🟡）
3. **持久版 delta tour 單一產點**：弧條件成立（HEAD 越過 EP baseline、a/b snapshot 在場且非 stale——時點條件真相源見 [code-review](../code-review/SKILL.md) 模式 B）→ `code-reality delta_tour <a> <b> --ep <ep.md> --repo <repo>` 落 `.tours/delta/`（**進 git**，commit 時納入）；未裝/條件不符 → 殼實作章節標明降級，不阻擋
4. 殼不存在（hook 1 未跑、EP 建於舊慣例）→ 跳過並於收尾報告標明

> **為什麼掛這裡**：實作章節要反映修正迴圈後最終態——鏈中任何一步都可能改 code，只有此點是最終態；且這是 commit 前最後穩定點——掛弧後（commit 後）的產物在 session context 耗盡時必死（三弧實證：弧後敘事——debrief／corpus 重產／delta tour——全滅）。

## 階段 6 — 收尾報告（終點，不 commit）

```markdown
## Post-Build 收尾報告
- code 鏈：findings N（✅N/❌N/⚠️N）、修正 N 項、followup <通過|未收斂(殘留清單)>
- EP 對照：delta_tour=<機械底稿|LLM 對照|無（原因：uncommitted 模式/小變更）>——宣稱觸及 vs 實際變動模組、unexplained 差異項
- 殼 refresh（hook 2）：<完成（badge ✅＋持久 delta tour 落點＝任務家殼）|跳過（原因：無殼/條件不符）>
- docs 鏈：consistency N 檔（pass N / fail-fixed N）、metadata-sync <跑/跳過>
- callstack 菜單（repo 有 `ai-analysis/blueprint/callstack-plan.md` 時）：積壓 N 條待生成（機械＝plan **成鏈行數**（①-③ 軌行；④ scripts/索引行不計）− `callstack/` 既有 md 數）——報庫存不催行動，生成＝獨立觸發＋報價（blueprint-bootstrap）
- smell=<建議 zoom 的 dir|無>——訊號源＝階段 1/2 findings 中「疑似 AI 亂加／junk／scope creep」類 finding 所指目錄。**triage 訊號非鏈內調用**：人類看到再決定開 viewport session 跑 [smell-detector](../smell-detector/SKILL.md) zoom（受眾分離——smell-detector 是軌道②人類 viewport，不進本鏈自動跑；baseline/onboarding 盤點屬週期需求，不掛 post-build）
- ⚠️ 待用戶確認：<決策清單>
- 下一步：`/commit`（commit 需人類確認，本 skill 止步於此）
```

**EP 對照行是再次提醒**（主歸納點在 [implement](../implement/SKILL.md) 階段 6——build 現場最清楚）：弧模式帶階段 1 機械底稿；同 session 接續 → 帶入 implement 階段 6 歸納；修正迴圈有新增變動 → 更新後再報。此行是 commit 決策的 triage 訊號（一眼看出 EP 未解釋的變動），深度渲染屬 `/debrief`；delta_tour 機制與時點條件真相源見 code-review 模式 B。

---

## 執行約束

- **止步於 commit 之前**：commit 需人類確認（硬規則，自主模式亦然）
- **不重抄被編排命令的方法論**：審查軸、judge 準則、consistency 六維都在各命令/skill 內，本檔只編排
- 修正迴圈上限 3 輪，超過即停（不硬撐原則）

## 流程位置

canonical review flow 以 [code-review](../code-review/SKILL.md)「流程位置」為單一源。本 skill 是該 flow 中 code-review → judge-review 段 + docs 鏈（consistency → metadata-sync）的**執行載體**：

```
/implement → post-build（本 skill：編排 code-review→judge-review→修正迴圈→consistency→metadata-sync→殼 refresh〔hook 2〕）→ /commit
```
