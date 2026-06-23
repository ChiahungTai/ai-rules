# flow-feedback: consistency fork placeholder bug（type-2 設計缺陷）

**摩擦**：build docs mode 階段 5 收尾跑 `/consistency` 驗證改動檔，`Skill(consistency, args=...)` 在 fork execution 時 harness 不替換 args placeholder → 觸發 consistency 自己的 fail-fast guard → 無法用正式命令，只能 inline 六維度補做。

**type-2（設計）**：consistency 是 `context: fork` 命令；fork 時 args placeholder 沒傳進去 → fail-fast。正式報告只能用戶手動 `! /consistency <path>` 繞過 fork。

**session 例子**：ep-adaptive-mechanical-trigger build 階段 5，我 `args=skills/review-engine/SKILL.md` 跑 consistency，fork 卻跑了 build.md（不是我 args 的）；第二次 args 明確又被 interrupt（fork 行為不可預期）。最終 inline 六維度補做（但 inline 是 L2 同義反覆風險 — LLM 審自己改的，獨立性塌縮）。

**counter-factual**：若 consistency fork 正確傳 args，直接得三檔機械 consistency 報告，不需 inline（保留命令的獨立檢查）。

**建議方向**（供 /flow-review）：
- consistency fork 路徑修 args placeholder 替換（harness 層），或
- consistency 文檔明示 fork 限制 + 建議 `! /consistency <path>`（inline shell）繞過；或 consistency 改非 fork 執行
