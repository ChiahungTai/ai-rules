---
harness-scope: neutral
---

# 符號／型別查詢路由（code-reality 優先）

## 核心原則（cr-first 路由）

搜尋前分清符號/引用/呼叫鏈與字串/config：符號優先 code-reality，文字 rg、檔案 fd。細節、跨 harness 載體、staleness、反例與 loopback 見 symbol-query-routing skill。

## code-reality 分工

- 符號：Rust SCIP／Python pyrefly-index；MCP refs/callers/closure/graph_query，核對 [SRC] provenance 與 stale。
- 型別：code-reality-lsp-bridge hover/check_file/edit_file（.py→pyrefly、.rs→rust-analyzer）；缺場退 LSP。
- 即時 documentSymbol/working-tree 回饋用 LSP；index 是 build-time，編輯後須重 harvest 才代表現況。ZCode 無原生 LSP，由 bridge 承接；pyright-langserver 是 harvest golden oracle，禁解除安裝。
- index 缺/過期且不可重建→LSP；LSP 亦缺才 rg。工單的工具/唯讀限制優先，不為重建越權。降級須標「未 index 驗證」，報告限制與結論一致，禁將未查到斷言為不存在。

## 任務啟動 gate（符號查詢任務強制）

涉及依賴/引用/fan-in/消費者/呼叫鏈/跨域/context/_private/邊界/循環/反向耦合/簽名/型別/定義/實作查詢，**第一步確認 cr 在場**（可調用 MCP 或 `.code-reality/graph.db`；detect 見 cr-query skill）。禁用 which/timeout shell proxy 當工具探測。純 Read 理解、demo、log 不觸發。

rg 的 truncation、display masking、命名差異與只錨 toplevel 都會漏符號/local import；引用可疑少先查 index/workspace 新鮮度，勿直接宣稱零消費者。

## 重構前必要步驟

rename、改簽名/回傳型別前必查全呼叫點：cr refs/callers，缺場用 LSP findReferences；rg 可能漏動態引用。

## Diagnostics 定位

Edit→ruff→check_file（即時）→mypy（權威完整）→pytest；diagnostics 不取代 mypy。Claude 編輯後自動推送時同 turn 修正，其他 harness 主動觸發。
