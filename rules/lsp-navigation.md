---
harness-scope: neutral
---

# LSP 語義導航優先

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）。**深層參考**（反例案例群、方法論限制 loopback、Agent prompt 工具指定模板、跨 harness 載體對照、workspace staleness 處置、驗證輸出格式）見 **lsp-navigation skill**（on-demand）

---

## 核心原則

**語義查詢用 LSP，文字搜尋用 rg/fd。兩者互補，非競爭。**

LSP 提供語義級程式碼導航（~50ms，workspace 索引最新時 100% 準確），rg/fd 提供文字級搜尋。LSP 理解程式碼結構（區分定義、引用、型別、scope）；rg 只匹配字串。

> **搜尋前自問（3 秒）**：找的是**符號**（class/def/引用/型別/呼叫鏈）還是**文字**（字串/註解/config/路徑）？符號 → LSP；文字 → rg/fd。直覺想 rg 時停一下 —— 符號查詢 rg 會 truncated/漏動態引用，LSP 100% 涵蓋（索引最新時）。

**反例速覽**（完整案例群見 lsp-navigation skill）：

- rg 符號查詢結果會 **truncated**（只顯示 `n`）與 **display masking**（把 method 名 mask 掉，輸出看起來像真的但不是——比 truncation 危險：「給錯的」讓你停止往下查）
- **符號覆蓋/存在性判斷**用 rg 會因命名 pattern 差異 false negative，把「自己沒查到」誤判為「不存在」（audit 誤報、judge-review 誤判兩真實案例）
- **依賴枚舉**錨 `^` toplevel 會系統性漏 local import（`# noqa: PLC0415` 是「刻意就地掩蓋」的指紋，恰恰是最該抓的結構債）
- workspace stale 時 LSP `findReferences` 回可疑少（只 intra-file）—— 先 reindex 再下結論，非工具 false-negative（處置見 skill）

**結論**：符號查詢一律 LSP 起手；rg 只做文字/註解/config；依賴分析搭配 LSP `findReferences`（涵蓋 import 行 + call site）。

---

## 任務啟動：Tool Discovery（符號查詢任務強制）

> **此段解決結構性失誤模式**：LLM 遇分析任務（依賴審計、符號引用查證、跨域存取盤點）直覺落 rg 全程不碰 LSP — 即使 LSP 工具可用。被動決策樹攔不住這個慣性；需要任務啟動時的**主動強制 step**。

### 強制 step：符號查詢任務開頭必須測 LSP 可用性

任務涉及以下關鍵詞之一 → **第一步**調用一次 LSP 工具（如 `workspaceSymbol` 或 `hover`）確認可用性，不可跳過：

- 「查詢/盤點/審計依賴」「引用」「reference」「fan-in」「消費者」「呼叫鏈」
- 「跨域」「context」「_private」「邊界洩漏」
- 「循環依賴」「反向耦合」
- 「簽名」「型別」「定義位置」「實作」

反之，純 Read 檔案理解結構、跑 demo、讀 log 等非符號查詢任務不觸發本 gate。

**禁 proxy 測試**：不可用 shell 命令（`timeout`、`which`、`command -v`）測 LSP 可用性 — 這些測的是 shell 環境，與 MCP LSP 工具無關。**唯一有效測試是直接調用 LSP 工具本身**。

| LSP 測試結果 | 行動 |
|-------------|------|
| 成功回傳 | 全程符號查詢用 LSP 為主工具；rg 僅輔助（文字、註解、config） |
| 失敗 / 工具不存在 | 標註「未 LSP 驗證」；rg 為主工具；報告方法論限制段明確記錄（loopback 紀律見 skill：限制段承認的邊界，結論段必須回照，禁自相矛盾的「不存在」斷言） |

---

## 查什麼 → 用什麼工具（LSP×rg/fd 統一速查）

LSP operation 語義跨 harness 一致（`goToDefinition` / `findReferences` / `hover` 等），呼叫載體因 harness 而異（對照表見 lsp-navigation skill）。

| 查什麼 | 首選（LSP operation） | 降級 | 說明 |
|--------|----------------------|------|------|
| 符號的定義（class/function/variable/type） | `goToDefinition`（跳到定義） | `rg "class\|def"` | LSP 100% 精準（索引最新時），rg 有 false positive |
| 符號的所有引用（誰在用它） | `findReferences`（找所有引用） | `rg "symbol"` | LSP 區分 scope，rg 匹配所有文字；找 dead code（zero hits）、確認 API 變更影響範圍 |
| 符號的型別資訊 | `hover` | Read 檔案 | hover 不消耗 context（不讀檔案知道變數型別、函式簽名） |
| 專案中的 class/function（按名稱） | `workspaceSymbol`（全域搜尋） | — | 找特定名稱的 class/function |
| 單一檔案的所有符號大綱 | `documentSymbol`（檔案大綱） | — | 快速了解檔案結構 |
| 介面的具體實作 | `goToImplementation` | — | 「誰實作了 Actor？」（ZCode pyright 不支援，載體差異見 skill） |
| 呼叫鏈（誰呼叫它） | `incomingCalls` | 手動 rg 追蹤 | LSP 結構化，rg 需逐檔追蹤 |
| 呼叫鏈（它呼叫誰） | `outgoingCalls` | 手動 rg 追蹤 | 「handle_order 呼叫了誰？」 |
| 編輯後的型別檢查 | `diagnostics`（即時） | — | 即時快速反饋；mypy 是權威驗證（見「Diagnostics 定位」） |
| 註解、字串、config 值、日誌、TODO、FIXME | rg | — | LSP 不索引非程式碼內容 |
| 檔案搜尋（按名稱模式） | fd | — | LSP 不處理檔案系統 |
| Markdown、YAML、TOML、JSON 等非程式碼 | rg | — | LSP 只涵蓋已配置的語言伺服器 |

**被動能力**（Claude: 每次檔案編輯後 LSP 自動推送 diagnostics — 型別錯誤、missing import，在同一 turn 修正）。其他 harness 需主動觸發 diagnostics operation。

---

## 何時不用 LSP

- 搜尋 Markdown、YAML、TOML、JSON、INI
- 搜尋註解內容、TODO、FIXME
- 搜尋字串常數、錯誤訊息
- 搜尋配置值、環境變數名
- LSP 不可用時（無語言伺服器的語言、subagent worktree）

---

## 重構前的必要步驟

重新命名、改簽名、改回傳型別前，**必須先用 `findReferences` 找出所有呼叫點**。LSP 涵蓋所有已索引引用（workspace 過時時先 reindex，處置見 skill），rg 可能遺漏動態引用。

---

## 驗證任務 workflow

每次 LSP 驗證任務遵循 5 步：

1. **Start with LSP** — 每個導航動作先 LSP（符號查詢禁 rg 起手）
2. **Verify with evidence** — 禁「looks correct」，一律 LSP 驗簽名/回傳/呼叫鏈
3. **Trace full chains** — 被問函式 → 同時追 incomingCalls + outgoingCalls
4. **Report precise locations** — 每個 finding 附 `file:line`
5. **Cross-verify** — LSP 結果非預期時用 Read 交叉確認

（驗證輸出 4 段格式——State question / Show operation / file:line finding / ✅❌ conclusion——見 lsp-navigation skill）

---

## Diagnostics 定位

LSP diagnostics 是**快速反饋**（即時型別檢查），mypy 是**權威驗證**（完整分析）：

```
Edit → ruff → LSP diagnostics（即時）→ mypy（完整驗證）→ pytest
```

diagnostics 不能取代 mypy 在品質閘門中的角色。

---

## Agent Prompt 工具選擇

spawn agent 時的 prompt 工具指定模板與判斷方式見 lsp-navigation skill「Agent Prompt 工具選擇」章；rule 端 always-on 摘要見 [tool-discipline.md](tool-discipline.md)「工具選擇原則」。
