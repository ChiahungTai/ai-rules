---
harness-scope: neutral
---

# LSP 語義導航優先

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 核心原則

**語義查詢用 LSP，文字搜尋用 rg/fd。兩者互補，非競爭。**

LSP 提供語義級程式碼導航（~50ms，100% 準確），rg/fd 提供文字級搜尋。LSP 理解程式碼結構（區分定義、引用、型別、scope）；rg 只匹配字串。

> **搜尋前自問（3 秒）**：找的是**符號**（class/def/引用/型別/呼叫鏈）還是**文字**（字串/註解/config/路徑）？符號 → LSP；文字 → rg/fd。直覺想 rg 時停一下 —— 符號查詢 rg 會 truncated/漏動態引用，LSP 100% 涵蓋。

**反例（rg 的陷阱：符號查詢 + 依賴枚舉）**：

- `rg "<ServiceClient>\("` 結果被截斷（只顯示 `n`），只能「推測」呼叫端；`LSP findReferences` 精準列出結構化 references（定義 + import + 型別註解 + 唯一實際呼叫點）。
- **audit 覆蓋判斷（真實案例）**：`rg "list_.*_classes" tests/` → 0 hits，audit 誤報「多個 class 無 membership 斷言」。實際測試用不同符號（列舉函式 / registry 變數），LSP `findReferences` 可找到。**符號覆蓋判斷用 rg 會因命名 pattern 差異 false negative**。
- **judge-review 查證（真實案例）**：審查者 rg 稱「`<ExecutorClass>` 在 `<module>.py` 無建構點」，LSP `findReferences` 立刻列出 import 行 + 建構行。**符號存在性查證用 rg 會因 pattern 失誤 false negative，把「自己沒查到」誤判為「不存在」**。

- **rg display masking（真實案例）**：`rg "_update_x_axis_labels"` 把 method 名 mask 成 `n`（輸出 `def n(self) -> None:`）—— **看起來像真實輸出但不是**。masking 比 truncation 更危險：truncation 是「少給」（你知道有漏），masking 是「給錯的」（誤以為查到了，停止往下查）。符號引用查詢一律 LSP `findReferences`。
- **toplevel-only pattern 漏 local import（真實案例）**：`rg "^from <package>"` 只抓 toplevel import，漏掉函式內的 `from <package>.<module> import ...  # noqa: PLC0415`（local import，被刻意降級以規避循環依賴）。local import 往往是「開發者知道是違規但就地掩蓋」的信號（`# noqa: PLC0415` 是指紋）— 恰恰是最該被抓出的結構債。**依賴分析不可只錨 `^` toplevel**；需搭配 LSP `findReferences`（涵蓋 import 行 + call site）或 rg 不錨 `^` + 篩 `noqa: PLC0415`。

**結論**：符號查詢用 rg 會 truncated/漏/pattern 失誤/masking（給錯的）；LSP 結構化、不截斷、100% 涵蓋（workspace 索引最新時；過時見「Workspace 狀態相依性」段）。**依賴枚舉用錨定 `^` toplevel 會系統性漏一整類（local import）**。

---

## 任務啟動：Tool Discovery（符號查詢任務強制）

> **此段解決一個結構性失誤模式**：LLM 遇到分析任務（依賴審計、符號引用查證、跨域存取盤點）時，直覺落 rg，全程不碰 LSP — 即使 LSP 工具可用。被動的決策樹（下方）攔不住這個慣性；需要任務啟動時的**主動強制 step**。

### 強制 step：符號查詢任務開頭必須測 LSP 可用性

任務涉及以下關鍵詞之一 → **第一步**調用一次 LSP 工具（如 `workspaceSymbol` 或 `hover`）確認可用性，不可跳過：

- 「查詢/盤點/審計依賴」「引用」「reference」「fan-in」「消費者」「呼叫鏈」
- 「跨域」「context」「_private」「邊界洩漏」
- 「循環依賴」「反向耦合」
- 「簽名」「型別」「定義位置」「實作」

反之，純 Read 檔案理解結構、跑 demo、讀 log 等非符號查詢任務不觸發本 gate。

**禁 proxy 測試**：不可用 shell 命令（如 `timeout`、`which`、`command -v`）測 LSP 可用性 — 這些測的是 shell 環境，與 MCP LSP 工具無關。**唯一有效測試是直接調用 LSP 工具本身**。用 proxy 測試下的「不可用」結論屬未驗證（客觀無 LSP 的情況除外，見「何時不用 LSP」段）。

### 測試結果處置

| LSP 測試結果 | 行動 |
|-------------|------|
| 成功回傳 | 全程符號查詢用 LSP 為主工具；rg 僅輔助（文字、註解、config） |
| 失敗 / 工具不存在 | 標註「未 LSP 驗證」；rg 為主工具；報告方法論限制段明確記錄 |

### 方法論限制 loopback（報告內部一致性）

> **此段解決「自審與作答共享盲點」**：方法論限制段承認了工具的認知邊界（如「未 LSP 驗證」「rg 可能漏 local import」），但結論段若沒回照這個邊界，會產生**自相矛盾的報告** — 限制段說「可能漏」，結論卻斷言「不存在 / 未發現」。這不是工具問題，是報告紀律問題。

**強制 step**：報告完成前，對「方法論限制段」列出的每一項認知邊界，檢查「結論段 / 發現段」是否回照：

| 方法論限制段的承認 | 結論段必須 |
|------------------|-----------|
| 「未 LSP 驗證」 | 該結論標「未確認」而非斷言；或說明為何仍可信 |
| 「rg 可能漏 local import」 | 依賴邊的「未發現」結論改為「toplevel 未發現，local import 未驗證」 |
| 「測試覆蓋 proxy 非行覆蓋率」 | 「薄覆蓋」結論標明是 proxy 訊號 |

**反例（本規則的觸發源）**：依賴審計報告的 methodology limitation 段寫「rg `^from` 無法捕捉函式內 lazy import」，但 🔴 反向耦合段的 feed 結論卻寫「feed → workflows 邊不存在」。兩段自相矛盾 — 限制段承認可能漏，結論卻斷言不存在 — 卻沒被發現，因為寫限制與下結論是同一個 LLM 的同一個信念體系（自審與作答共享盲點，理論基礎見 [acceptance-evidence.md](acceptance-evidence.md)「證據獨立性」）。

> **通用性**：此 loopback 紀律雖在 LSP/rg 場景觸發，但適用任何「方法論限制段 vs 結論段」的組合 — 工具限制、測試覆蓋、取樣口徑皆同。未來其他 rule 觸發同類失誤時可 cross-reference 本段。

### 優先級規則：task prompt 條件句不覆蓋全域規則

task prompt 寫「若有 LSP 工具可用...無 LSP 則用 rg」是**提醒確認可用性**，**不是授權默認假設無 LSP**。衝突時優先級：

```
skill / 全域 rules（本檔）> task prompt 條件句
```

即：task prompt 的條件句要求你「確認可用性」（調用 LSP 測試），全域規則要求你「符號查詢用 LSP」。兩者一致 — 條件句不構成「跳過 LSP」的授權。

> **真實失誤案例（本規則的觸發源）**：分析任務全程用 rg，理由是「task prompt 寫若有 LSP 則用」。實際上 LSP 工具可用，但 LLM (a) 誤讀條件句為「預設 rg」、(b) 全程未調用 LSP、(c) 被提醒後用 `timeout` 命令（shell 工具）測試並下結論「LSP 不可用」 — 三重失誤全因缺強制啟動 step。

> **與「驗證任務 workflow」的關係**：本段是 **task-level gate**（任務開頭測 LSP 可用性，一次性）；下方「驗證任務 workflow」step 1「Start with LSP」是 **action-level 節奏**（每個導航動作先 LSP）。兩者互補不重複 — gate 確保工具可用，節奏確保每步都用。

---

## 決策樹

```
你要找什麼？
│
├─ 符號的定義（class、function、variable、type）
│  → LSP goToDefinition
│
├─ 符號的所有引用（誰在用它）
│  → LSP findReferences
│
├─ 符號的型別資訊
│  → LSP hover
│
├─ 專案中的 class/function（按名稱）
│  → LSP workspaceSymbol
│
├─ 單一檔案的所有符號大綱
│  → LSP documentSymbol
│
├─ 介面的具體實作
│  → LSP goToImplementation
│
├─ 呼叫鏈（誰呼叫它 / 它呼叫誰）
│  → LSP incomingCalls / outgoingCalls
│
├─ 編輯後的型別檢查
│  → LSP diagnostics（即時）→ mypy（完整驗證）
│
├─ 註解、字串、config 值、日誌、TODO、FIXME
│  → rg（LSP 不索引非程式碼內容）
│
├─ 檔案搜尋（按名稱模式）
│  → fd（LSP 不處理檔案系統）
│
└─ Markdown、YAML、TOML、JSON 等非程式碼
   → rg（LSP 只涵蓋已配置的語言伺服器）
```

---

## LSP 工具速查

LSP operation 語義跨 harness 一致（`goToDefinition` / `findReferences` / `hover` 等），呼叫載體因 harness 而異（見下方「跨 harness LSP 載體對照」）。

| Operation | 用途 | 典型場景 |
|-----------|------|---------|
| `goToDefinition` | 跳到定義 | 從 import 跳到源碼、從 class 使用跳到 class 定義 |
| `findReferences` | 找所有引用 | 確認 API 變更影響範圍、找 dead code（zero hits） |
| `hover` | 型別資訊 | 不讀檔案就知道變數型別、函式簽名 |
| `workspaceSymbol` | 全域搜尋 | 找特定名稱的 class/function |
| `documentSymbol` | 檔案大綱 | 快速了解檔案結構 |
| `goToImplementation` | 介面實作 | 「誰實作了 Actor？」 |
| `incomingCalls` | 呼叫者 | 「誰呼叫了 submit_order？」 |
| `outgoingCalls` | 被呼叫者 | 「handle_order 呼叫了誰？」 |

**被動能力**（Claude: 每次檔案編輯後 LSP 自動推送 diagnostics — 型別錯誤、missing import，在同一 turn 修正，不需等到 mypy）。其他 harness 機制不同，需主動觸發 diagnostics operation。

### 跨 harness LSP 載體對照

當一個概念跨 harness 通用但呼叫方式不同時，用對照表表達（中性化規範的「跨 harness 載體對照」pattern，見 [rules/AGENTS.md](AGENTS.md)）：

| harness | LSP 機制 | 呼叫方式 |
|---------|---------|---------|
| Claude Code | 原生 plugin set（pyright/rust-analyzer/clangd/gopls/jdtls/...）| `LSP` tool（native，非 MCP），參數 `operation`/`filePath`/`line`/`character` |
| ZCode | 無原生 → 用自建 `lsp-python` MCP server（mosaic_alpha `tools/lsp_mcp/server.py` 參考實作；per-project workspace） | **單一 `mcp__lsp-python__lsp(operation=...)` tool**（CC-aligned dispatch：operation 值 camelCase 對齊 CC `LSP` tool，如 `goToDefinition`/`findReferences`/`hover`/...；hybrid input position + symbol_name fallback；`character` 非 `column`） |
| OpenCode | 原生 LSP（官方文檔說有，未實測） | 原生 tool |
| 未來無 native 的 harness | 用 MCP server 支援 | mosaic_alpha `lsp-python` 為 reference impl（per-project http server） |

LSP operation 語義一致，差異只在載體（native tool vs MCP tool）— 決策樹、反例、驗證 workflow 本檔已通用化。mosaic_alpha `lsp-python` MCP 已進一步對齊 CC：單一 tool + `operation` 參數 + camelCase operation 值，跨 harness 呼叫結構一致（差異僅 `LSP` vs `mcp__lsp-python__lsp` 前綴）。goToImplementation：CC 有、ZCode pyright 不支援（`implementationProvider` 未實作）。

### Workspace 狀態相依性（reindex 後再下結論）

LSP 結果是 workspace 狀態相依的 — 若 `findReferences` 回傳意外少的結果（尤其對 `_`-prefixed 私有 symbol），**先觸發 workspace reindex 再下結論**，不要直接推論為工具固有 false-negative。

| harness | reindex 觸發 |
|---------|-------------|
| ZCode | `mcp__lsp-python__lsp(operation="reloadWorkspace")`（git 操作後、或符號查詢結果異常少時呼叫）。行為依 transport：**http**（共用 WorkspacePool）5-10s 重建 client；**stdio**（無 pool）回降級訊息、需手動重啟 server 觸發 reindex |
| Claude Code | 檔案變更自動推送（見上「被動能力」），但 git rebase/reset 大幅變動後仍可能過時 |

**真實案例（cross-harness 驗證）**：同一 `_PREV_COUNT` 符號（mosaic_alpha `structure/wave_scalars.py:50`），Claude session `findReferences` 只回傳 intra-file ref（誤判為工具對私有 symbol 的 false-negative），ZCode session 卻成功回傳跨檔引用 — 差異根因是 pyright workspace reindex 時機，非 LSP 對私有 symbol 的固有限制。**兩 session 結果矛盾時，先懷疑 workspace 狀態，再懷疑工具能力。**

---

## 與 rg/fd 的分工

| 查詢類型 | 首選 | 降級 | 說明 |
|---------|------|------|------|
| 定義位置 | LSP goToDefinition | `rg "class\|def"` | LSP 100% 精準，rg 有 false positive |
| 所有引用 | LSP findReferences | `rg "symbol"` | LSP 區分 scope，rg 匹配所有文字 |
| 型別資訊 | LSP hover | Read 檔案 | hover 不消耗 context |
| 呼叫鏈 | LSP incomingCalls | 手動 rg 追蹤 | LSP 結構化，rg 需逐檔追蹤 |
| 註解/字串/config | rg | — | LSP 不索引非程式碼 |
| 檔案搜尋 | fd | — | LSP 不處理檔案系統 |
| Markdown/YAML | rg | — | LSP 不涵蓋非程式碼格式 |

---

## 何時不用 LSP

- 搜尋 Markdown、YAML、TOML、JSON、INI
- 搜尋註解內容、TODO、FIXME
- 搜尋字串常數、錯誤訊息
- 搜尋配置值、環境變數名
- LSP 不可用時（無語言伺服器的語言、subagent worktree）

---

## 重構前的必要步驟

重新命名、改簽名、改回傳型別前，**必須先用 `findReferences` 找出所有呼叫點**。LSP 涵蓋所有已索引引用（workspace 過時見「Workspace 狀態相依性」段，重構前先確認 reindex），rg 可能遺漏動態引用。

---

## 驗證任務 workflow

每次 LSP 驗證任務遵循 5 步：

1. **Start with LSP** — 每個導航動作先 LSP（符號查詢禁 rg 起手）
2. **Verify with evidence** — 禁「looks correct」，一律 LSP 驗簽名/回傳/呼叫鏈
3. **Trace full chains** — 被問函式 → 同時追 incomingCalls + outgoingCalls
4. **Report precise locations** — 每個 finding 附 `file:line`
5. **Cross-verify** — LSP 結果非預期時用 Read 交叉確認

---

## Diagnostics 定位

LSP diagnostics 是**快速反饋**（即時型別檢查），mypy 是**權威驗證**（完整分析）。關係類似 IDE linting vs CI linting：

```
Edit → ruff → LSP diagnostics（即時）→ mypy（完整驗證）→ pytest
```

diagnostics 不能取代 mypy 在品質閘門中的角色。

---

## Agent Prompt 工具選擇

> **核心原則**：spawn agent 時，prompt 必須根據任務性質明確指定使用 LSP 或 rg。禁止只寫「驗證/讀取/確認」不指定工具。

**Agent prompt 工具指定模板**：

```
# 工具選擇（必填）
- 簽名/型別/定義位置 → 用 LSP hover / goToDefinition
- 呼叫鏈/引用 → 用 LSP outgoingCalls / incomingCalls / findReferences
- 文字搜尋（字串、註解、config）→ 用 rg
- 檔案搜尋 → 用 fd
- Cython 模組（.pyx/.so）→ 用 rg + Read（LSP 不索引 Cython）
- **audit-test 角度 2 覆蓋判斷** → **禁用單一 rg pattern**；registry membership / class 引用 / method call 必須 LSP findReferences 為主、rg 為輔（Claude: `audit-test.md`「Registry Membership 流程」；跨 harness 為測試 audit 流程，路徑從略）
- **judge-review 符號查證** → 「X 是否存在 / 在哪引用」必須 LSP findReferences / workspaceSymbol；rg 0 hits 不可直接下「不存在」結論（Claude: `judge-review.md`「自我否證義務」；跨 harness 為 review 流程，路徑從略）
```

**判斷方式**：如果任務描述包含「簽名」「型別」「定義」「呼叫」「繼承」「Protocol」→ 主工具是 LSP，輔以 rg 確認。如果任務描述包含「字串」「註解」「config」「檔案路徑」→ 主工具是 rg/fd。

---

## 跨命令共用的 LSP 驗證輸出格式

每次 LSP 驗證任務（驗證特定 claim、refs 查證、call chain 追蹤）產出依此格式：

1. **State the question** — 釐清要驗證什麼（例：「`Strategy.on_bar()` 的簽名是否正確？」）
2. **Show the LSP operation used** — 明示用了哪個 LSP operation（例：`LSP hover on Strategy.on_bar`）
3. **Report the finding with precise file:line** — 每個 finding 附 `file_path:line_number`（禁「looks correct」，必須引用實際位置）
4. **Give a clear ✅/❌ conclusion** — 結論明確（通過/不通過），不留模糊

> 此格式跨 audit-test / judge-review / illustrate verify drill / arch-thinking 驗證段通用。LSP 是反應式驗證工具（驗證特定 claim → ✅/❌），不是 holistic 架構判讀——判讀是人類 viewport 的工作（見 arch-thinking skill）。
