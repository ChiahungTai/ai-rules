# STATE.md 寫入步驟（共享段）

> 共享子範本——`/at`、`/handoff`、`/deep-work` 在 session 結束寫 STATE.md 時引用此處，不各自重寫（DRY，防三處 drift）。STATE.md **定義**（職責 / 邊界 / lifecycle / 路徑）見 [context-management](../../../rules/context-management.md)「STATE.md Last session 觀察層」段；本段僅定義**寫入操作**。

## 寫入時機

session 結束離開前——**寫入**由 `/at` 排程、`/deep-work` completion report 觸發（`/handoff` 僅標示 STATE.md 非交接選項，不寫入）。

## 寫入內容（Last session 觀察）

repo root `STATE.md`，**覆寫**（非累積——每次自主 session（at/deep-work）結束重寫，只保留最近一次觀察）。三要素：

- **卡在哪**：當前進行中、未收尾的工作點
- **為何轉向**：決策轉折理由（為何選 X 不選 Y、為何擱置）
- **下次起手點**：resume 時該從哪接、第一個動作

## A↔C 邊界紀律（negative guidance，強制）

**STATE.md = 觀察層；禁含完成度宣稱**——完成度走事實層（git + EP re-derive，見 [autonomous-execution](../../../skills/autonomous-execution/SKILL.md)「Session 級 Recovery」）。「卡在哪/為何轉向」本質隱含 soft completion signal（轉向=未完成 X），resume LLM 讀到不會自發做觀察/事實區分——須嚴守：

- ✗ **不寫完成度**：「segment 3 未完成、做到一半」「段落 X done」「進度 80%」
- ✓ **寫觀察**：「retry 間隔計算產生 0，推測 BackoffCalculator 邊界條件」「改用 schema-based approach，因 Y 效能瓶頸」

> **指導非強制**（docs-mode 紀律，無 schema enforce）——誠實標記如同其他 docs-mode 強度上限宣告（指導非強制，hook 補強列未來方向）。未來機械補強方向：STATE.md schema 無完成度欄位 / resume re-derive 前不讀 STATE 的流程約束。

## Open failures 不寫此處

跨 session 未結案的 bug/failure（含 repro）→ **走 `.kanban/Backlog/`**（failure card + repro body），**不進 STATE.md**（kanban 已是跨 session 未結案追蹤）。
