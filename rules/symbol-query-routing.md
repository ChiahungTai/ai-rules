---
harness-scope: neutral
---

# 符號／型別查詢路由（code-reality 優先）

## 核心原則（cr-first 路由）

搜尋前分清符號/引用/呼叫鏈與字串/config：符號優先 code-reality，文字 rg、檔案 fd；跨 harness 載體、staleness、反例、重構/diagnostics 查證義務與 loopback 見 symbol-query-routing skill。

## code-reality 分工

- 符號：Rust SCIP／Python pyrefly-index；用 refs/callers/closure/graph_query 並核對 [SRC] provenance/stale。
- 型別：code-reality-lsp-bridge hover/check_file/edit_file（.py→pyrefly、.rs→rust-analyzer）；缺場退 LSP。即時 documentSymbol/working-tree 回饋亦用 LSP；index 屬 build-time，編輯後須重 harvest。
- index 缺/過期且不可重建→LSP；LSP 亦缺才 rg。工單工具/唯讀限制優先；降級須標「未 index 驗證」，禁把未查到斷言為不存在。ZCode 無原生 LSP 由 bridge 承接；pyright-langserver 是 harvest golden oracle，禁解除安裝。

## 任務啟動 gate（符號查詢任務強制）

涉及依賴/引用/fan-in/消費者/呼叫鏈/跨域/context/_private/邊界/循環/反向耦合/簽名/型別/定義/實作查詢，**第一步確認 cr 在場**（MCP 或 `.code-reality/graph.db`；detect 見 cr-query skill）；禁用 which/timeout shell proxy 探測。純 Read 理解、demo、log 不觸發。

rg 的 truncation、display masking、命名差異與只錨 toplevel 都會漏符號/local import；引用可疑少先查 index/workspace 新鮮度，勿直接宣稱零消費者。
