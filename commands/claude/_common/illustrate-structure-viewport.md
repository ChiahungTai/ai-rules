# 結構 viewport — drill 與機械分工

> **載體**：[illustrate.md](../../illustrate.md) 的結構 viewport 模式（人類 viewport，B 軸）支撐檔。
> **能力來源**：[arch-thinking](../../../skills/arch-thinking/SKILL.md) skill —— City Map 資料 / dep weight / Pattern Radar / domain grounding / LSP 查證 / product-type 雙軌都在 skill（視角 §一、機械 §二）。本檔定義**人 viewport 的互動式 drill 與機械分工** —— 渲染結構心智模型讓人判讀（不產機器 finding，那是 `/code-review` axis 3）。

## drill 指令（whole-picture → 嫌疑）

whole-picture 渲染完（city map / flows / boundaries / 重用枚舉，資料來自 skill），人用 drill 深入：

```
city <module>      — 放大某模組的依賴細節
flow <use-case>    — 畫另一個 use case 的 flow
reuse <RC-XXX>     — 深入某重用嫌疑（含 LOW confidence）
verify <symbol>    — 鎖定嫌疑，用 lsp-architect 驗 refs / call chain
boundary <module>  — 細看某模組邊界
```

或用自然語言描述「這感覺在重造什麼」。完成後說 `done` 或 `summary`。

## Phase 2：互動式調查

人提 whole-picture 線索，LLM 做精確查證：

| Type | 人類說什麼 | LLM 調查 |
|------|------------|----------|
| 🔗 重用嫌疑 | 「這感覺跟那個重複」 | Pattern Radar 枚舉 + 信心度 + lsp-architect 驗 refs |
| 🗺️ 結構可疑 | 「這依賴怪怪的」 | LSP `incomingCalls`/`outgoingCalls` 追蹤 + import graph |
| 📐 邊界 | 「這不該在這模組」 | LSP `findReferences` 看跨域存取 + Read 邊界 |
| 💬 Free-form | 任意 | 自動分類或直接回答 |

## 機械分工（何時用哪個工具）

> **核心**：枚舉（撈全 + 相似）用 scan-project / Pattern Radar；驗證（特定 claim）用 lsp-architect。**人鎖定嫌疑後才上驗證**。

| 子任務 | 工具 | 角色 |
|--------|------|------|
| 撈全既有 symbol、找重用候選 | scan-project / Pattern Radar（枚舉） | **primary** —— 餵人的 whole-picture |
| 人鎖定「這 enum 跟那 enum 可能重疊」後驗證 | lsp-architect（`findReferences` / call chain） | **secondary** —— 確認嫌疑 |
| City Map / Flows 渲染 | /illustrate | 渲染引擎（人 viewport） |

> `lsp-architect` 是**反應式驗證**（驗證特定 claim → ✅/❌），不是 holistic 架構判讀 —— 判讀是人的 whole-picture 工作。它是查證 helper，不是結構判讀本身。

## 位置標示（可點擊）

標定 symbol / 檔案位置用 **repo-root 相對路徑 + 行號**（如 `data/fetcher.py:15`），讓 VSCode terminal Cmd+Click 可跳轉 —— 人類 viewport 判讀需要能鑽進 code 看嫌疑。純檔名 terminal 解析不到。

## Final Summary

```
## 結構 viewport Summary

### Context
- Scope: <module> / EP / 變更
- 覆蓋: City Map | Flows | Boundaries | 重用枚舉

### 結構判定
| 項目 | 判定 | 說明 |
|------|------|------|
| 分層 / 依賴方向 | ✅/⚠️/❌ | ... |
| 邊界 | ... | ... |
| 重用（whole-picture） | N 嫌疑 | ... |

### Confirmed 重用 / 結構問題
| ID | 類型 | 位置 | 判定 | Action |

### Items for Discussion
| # | 嫌疑 | 確認問題 |
```
