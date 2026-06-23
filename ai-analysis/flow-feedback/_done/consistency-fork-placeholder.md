# flow-feedback: consistency fork placeholder bug（type-2 設計缺陷）

**摩擦**：build docs mode 階段 5 收尾跑 `/consistency` 驗證改動檔，`Skill(consistency, args=...)` 在 fork execution 時 harness 不替換 args placeholder → 觸發 consistency 自己的 fail-fast guard → 無法用正式命令，只能 inline 六維度補做。

**type-2（設計）**：consistency 是 `context: fork` 命令；fork 時 args placeholder 沒傳進去 → fail-fast。正式報告只能用戶手動 `! /consistency <path>` 繞過 fork。

**session 例子**：ep-adaptive-mechanical-trigger build 階段 5，我 `args=skills/review-engine/SKILL.md` 跑 consistency，fork 卻跑了 build.md（不是我 args 的）；第二次 args 明確又被 interrupt（fork 行為不可預期）。最終 inline 六維度補做（但 inline 是 L2 同義反覆風險 — LLM 審自己改的，獨立性塌縮）。

**counter-factual**：若 consistency fork 正確傳 args，直接得三檔機械 consistency 報告，不需 inline（保留命令的獨立檢查）。

**建議方向**（供 /flow-review）：
- consistency fork 路徑修 args placeholder 替換（harness 層），或
- consistency 文檔明示 fork 限制 + 建議 `! /consistency <path>`（inline shell）繞過；或 consistency 改非 fork 執行

**當前狀態（2026-06-23 盤點）**：
- ✅ **建議方向 2 已實現**：`commands/consistency.md:64` fail-fast guard 已明文此限制（字面 `$ARGUMENTS` 未替換 + `context: fork` + harness 不替換）+ 建議繞過（`/consistency <path>` 或無參數自動偵測）。**ai-rules 層防護已足**。
- ❌ **根因待外部**：harness fork placeholder 替換（建議方向 1）是 harness 行為，ai-rules 改不了。
- ⚠️ **程式化呼叫者的因應**：build/execution-plan docs mode 收尾的 `/consistency` 程式化 `Skill(args)` 會 fail-fast；AI 遇此改**主 LLM inline 六維度**（本 session 所做），代價是 L2 同義反覆風險（LLM 審自己改的）。**待 /flow-review 討論**：docs mode 收尾是否改用獨立性更高的驗證（`/sync-sources` 已機械化 + 跨檔 rg），降低對 inline consistency 的依賴。
