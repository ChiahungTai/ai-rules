---
harness-scope: neutral
---

# 符號／型別查詢路由（code-reality 優先）

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）。檔名保留 lsp-navigation（LSP 殘留面＋skill 同名配對）。**深層參考**（LSP operation 速查表、驗證輸出格式、反例案例群、方法論限制 loopback、Agent prompt 工具指定模板、跨 harness 載體對照、workspace staleness 處置）見 **lsp-navigation skill**（on-demand）

---

## 核心原則（cr-first 路由）

**符號/圖譜查詢用 code-reality（index 在場），型別面（hover/diagnostics）用 code-reality-lsp-bridge（.py→pyrefly、.rs→rust-analyzer 副檔路由），當下編輯回饋與 documentSymbol 即時形用 LSP（ZCode 端無原生 LSP——型別/編輯回饋由 bridge 承接；documentSymbol 即時形為 CC 端原生能力），文字搜尋用 rg，檔案搜尋用 fd。**

> **搜尋前自問（3 秒）**：找的是**符號**（class/def/引用/型別/呼叫鏈）還是**文字**（字串/註解/config/路徑）？符號 → code-reality；文字 → rg/fd。直覺想 rg 時停一下——符號查詢 rg 會 truncated/漏動態引用。

**反例速覽**（完整案例群見 lsp-navigation skill）：

- rg 符號查詢結果會 **truncated**（只顯示 `n`）與 **display masking**（把 method 名 mask 掉，輸出看起來像真的但不是——比 truncation 危險：「給錯的」讓你停止往下查）
- **符號覆蓋/存在性判斷**用 rg 會因命名 pattern 差異 false negative，把「自己沒查到」誤判為「不存在」（audit 誤報、judge-review 誤判兩真實案例）
- **依賴枚舉**錨 `^` toplevel 會系統性漏 local import（`# noqa: PLC0415` 是「刻意就地掩蓋」的指紋，恰恰是最該抓的結構債）
- workspace stale／index 過期時引用查詢回可疑少（只 intra-file）——先 reindex/重建再下結論，非工具 false-negative（處置見 skill）

---

## code-reality 分工

- **符號面**：cr index（Rust＝SCIP、Python＝pyrefly-index）——MCP `refs`/`callers`/`closure`＋`graph_query` 家族；index 在場時優先（`[SRC]` provenance＋stale 守衛、免 workspace stale、跨 session 一致）
- **型別面**：`code-reality-lsp-bridge` MCP（`hover`/`check_file`/`edit_file`；副檔路由 .py→pyrefly、.rs→rust-analyzer；缺場退 LSP）
- **LSP 保留面**：documentSymbol 即時形、**working-tree 即時性**（index 是 build-time 產物——編輯後未重 harvest 前是舊態；查「當下」用 LSP 或先重建 index）。pyright-langserver 是 harvest 的 golden oracle 引擎——不可解除安裝
- index 缺場/過期且不可重建 → **退 LSP**（LSP 面亦缺——subagent worktree、無語言伺服器的語言——才退 rg）＋標「未 index 驗證」；報告方法論限制段必須記錄（loopback 紀律見 skill：限制段承認的邊界，結論段必須回照，禁自相矛盾的「不存在」斷言）

---

## 任務啟動 gate（符號查詢任務強制）

> 此段攔「遇符號分析直覺落 rg 全程」的結構性慣性（被動決策樹攔不住，需要任務啟動的主動強制 step）。

任務涉及「查詢/盤點/審計依賴」「引用/reference」「fan-in」「消費者」「呼叫鏈」「跨域」「context」「_private」「邊界洩漏」「循環依賴」「反向耦合」「簽名」「型別」「定義位置」「實作」之一 → **第一步**確認 cr 引擎在場（MCP 工具可調用或 `.code-reality/graph.db` 存在；detect 細節與 assume+warn gate 見 cr-query skill），不可跳過；**禁 shell proxy 測試**（`timeout`/`which` 測的是 shell 環境非查詢工具）。純 Read 理解結構、跑 demo、讀 log 不觸發本 gate。

---

## 重構前必要步驟

重新命名、改簽名、改回傳型別前，**必須先查所有呼叫點**（cr `refs`/`callers`；cr 缺場用 LSP `findReferences`）——涵蓋所有已索引引用，rg 可能遺漏動態引用。

---

## Diagnostics 定位

bridge `check_file`／LSP diagnostics 是**快速反饋**（即時型別檢查），mypy 是**權威驗證**：

```
Edit → ruff → check_file（即時）→ mypy（完整驗證）→ pytest
```

diagnostics 不能取代 mypy 在品質閘門中的角色。Claude 端每次檔案編輯後 LSP 自動推送 diagnostics（同 turn 修正）；其他 harness 主動觸發。
