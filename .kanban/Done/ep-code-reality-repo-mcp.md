# EP 追蹤：code-reality 獨立 repo＋統一 MCP（v0）

[tag:code-reality] [ep]

## 目標
code_reality 九工具＋tests big-bang 搬進新 repo（D1），加 caller 邊＋closure（UC-2）與 MCP 薄殼（UC-5），消費端 relay 切換，ai-rules 零殘留。v1（圖層注入/CRG 退役）另行 EP。

## 相關
- EP：`ai-analysis/execution-plans/ep-code-reality-repo-mcp.md`
- Spec（決策真相源）：`ai-analysis/specs/code-reality-repo-mcp-spec.md`
- 研究背景：`ai-analysis/reports/rust-precision-ecosystem-research.md`
- 能力卡：`code-reality-caller-edges.md`、`code-reality-mcp-server.md`

## 驗收標準
- spec 成功條件①-④（v0 範圍）：單一 MCP 完成語義面 UC；`EventStoreLifecycle.open` 17 callers 三源一致；NT 鉤子搬遷前後 byte-identical；搬遷測試全綠＋v0 SM 全覆蓋
- ai-rules `rg "code_reality"` 零可執行殘留（歷史文檔除外）

## 備註
- 硬約束：NT CLI 契約（--json/exit codes/stdout bytes）永不破壞
- Ask First gate：repo 命名已定案 `code-reality`（2026-08-25）、刪碼（S4 gate）、每筆 commit

## 收案（2026-08-26）
S1 完整閉環（`2eafd8a`＋dogfood）；**S2/S3 scope 移交 code-reality repo Rust 軌**（R3 已交付 caller edges）；S4（消費端切換＋ai-rules 舊碼刪除）另立卡追蹤。本卡追蹤目的完成。
