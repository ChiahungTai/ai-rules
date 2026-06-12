# LSP 語義導航優先

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 核心原則

**語義查詢用 LSP，文字搜尋用 rg/fd。兩者互補，非競爭。**

LSP 提供語義級程式碼導航（~50ms，100% 準確），rg/fd 提供文字級搜尋。LSP 理解程式碼結構（區分定義、引用、型別、scope）；rg 只匹配字串。

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

---

## Diagnostics 定位

LSP diagnostics 是**快速反饋**（即時型別檢查），mypy 是**權威驗證**（完整分析）。關係類似 IDE linting vs CI linting：

```
Edit → ruff → LSP diagnostics（即時）→ mypy（完整驗證）→ pytest
```

diagnostics 不能取代 mypy 在品質閘門中的角色。
