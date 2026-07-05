---
harness-scope: claude-specific
---

# LSP 語義導航優先

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

---

## 核心原則

**語義查詢用 LSP，文字搜尋用 rg/fd。兩者互補，非競爭。**

LSP 提供語義級程式碼導航（~50ms，100% 準確），rg/fd 提供文字級搜尋。LSP 理解程式碼結構（區分定義、引用、型別、scope）；rg 只匹配字串。

> **搜尋前自問（3 秒）**：找的是**符號**（class/def/引用/型別/呼叫鏈）還是**文字**（字串/註解/config/路徑）？符號 → LSP；文字 → rg/fd。直覺想 rg 時停一下 —— 符號查詢 rg 會 truncated/漏動態引用，LSP 100% 涵蓋。

**反例（rg 找符號的陷阱）**：

- `rg "<ServiceClient>\("` 結果被截斷（只顯示 `n`），只能「推測」呼叫端；`LSP findReferences` 精準列出結構化 references（定義 + import + 型別註解 + 唯一實際呼叫點）。
- **audit 覆蓋判斷（真實案例）**：`rg "list_.*_classes" tests/` → 0 hits，audit 誤報「多個 class 無 membership 斷言」。實際測試用不同符號（列舉函式 / registry 變數），LSP `findReferences` 可找到。**符號覆蓋判斷用 rg 會因命名 pattern 差異 false negative**。
- **judge-review 查證（真實案例）**：審查者 rg 稱「`<ExecutorClass>` 在 `<module>.py` 無建構點」，LSP `findReferences` 立刻列出 import 行 + 建構行。**符號存在性查證用 rg 會因 pattern 失誤 false negative，把「自己沒查到」誤判為「不存在」**。

- **rg display masking（真實案例）**：`rg "_update_x_axis_labels"` 把 method 名 mask 成 `n`（輸出 `def n(self) -> None:`）—— **看起來像真實輸出但不是**。masking 比 truncation 更危險：truncation 是「少給」（你知道有漏），masking 是「給錯的」（誤以為查到了，停止往下查）。符號引用查詢一律 LSP `findReferences`。

**結論**：符號查詢用 rg 會 truncated/漏/pattern 失誤/masking（給錯的）；LSP 結構化、不截斷、100% 涵蓋。

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

Claude Code 內建 `LSP` tool（native，非 MCP）。參數：`operation`, `filePath`, `line`, `character`。

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

**被動能力**：每次檔案編輯後，LSP 自動推送 diagnostics（型別錯誤、missing import）。在同一 turn 修正，不需要等到 mypy。

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

重新命名、改簽名、改回傳型別前，**必須先用 `findReferences` 找出所有呼叫點**。LSP 保證 100% 涵蓋，rg 可能遺漏動態引用。

### 驗證任務 workflow

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
- **audit-test 角度 2 覆蓋判斷** → **禁用單一 rg pattern**；registry membership / class 引用 / method call 必須 LSP findReferences 為主、rg 為輔（見 audit-test.md「Registry Membership 流程」）
- **judge-review 符號查證** → 「X 是否存在 / 在哪引用」必須 LSP findReferences / workspaceSymbol；rg 0 hits 不可直接下「不存在」結論（見 judge-review.md「自我否證義務」）
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
