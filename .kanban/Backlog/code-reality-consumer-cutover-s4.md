# 原 EP S4 殘留義務：消費端切換＋ai-rules 舊碼刪除

[tag:code-reality]

## 目標
code-reality repo 成熟後：消費端（NT 治理鉤子／mosaic／ai-rules skills 路徑）切換 `--project ~/Github/code-reality`，確認後刪 ai-rules 的 code_reality/＋tests/（最終零殘留——主判準：`rg "uv run --project ~/Github/ai-rules" --type md` 歸零，豁免 zcode-session-query）。

## 相關
- 源 EP：`ai-analysis/execution-plans/ep-code-reality-repo-mcp.md`（已收案 Done/）
- 對象 repo：~/Github/code-reality（Rust 軌進行中——R2/R3 已落地、R4 起草）
- delta_tour 修復 canonical：ai-rules `8ae1f9e`（吸收參考）

## 驗收標準
- NT：`--project` 切換後 query/audit/graph_audit 三面 byte-identical（NT 側驗收）
- mosaic：hub_refs --hazard 驗收命令新路徑命中
- ai-rules：零殘留掃過＋consistency gate＋POC 清理

## 備註
gate＝code-reality Rust 軌成熟（NT 契約面覆蓋）＋user 確認；relay 一次打包（NT＋mosaic 文檔面同步清單含）
