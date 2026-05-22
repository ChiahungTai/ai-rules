# Slash Commands 技術規範

## 寫作原則

> **載入時機**：Command 只在 `/invoke` 時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Command 不支援 `@` transclusion。引用其他檔案一律使用 `[描述](path)` markdown link
- **輸出格式模板**：是 command 的核心交付物規格，不算一般程式碼範例，可接受 >5 行
- **實作程式碼**：避免在 command 中嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

> **架構**: `~/.claude/commands` 符號連結指向本目錄，實現 Git 版本控制和跨專案共享。

## 命令索引

### 核心開發流程

```
/spec → /execution-plan → /ep-review → /judge-review → /build（含 Agent Review）→ [/code-review] → /commit
```

- `/spec` — 結構化需求討論（User Story、假設、技術選型、邊界）
- `/execution-plan` — 段落式實作計畫書，基於 /spec 生成 Self-Contained Segments
- `/ep-review` — 審查 Execution Plan 合理性
- `/judge-review` — 評估其他 AI 的審查建議，基於第一性原理決定採納與否
- `/build` — 基於 Execution Plan 逐段實作（TDD）
- `/code-review` — 第一性原理代碼審查
- `/followup-review` — 審查者回頭驗收實作結果
- `/commit` — Commit 入口（lint 閘門 → message → 確認）

### 自主實作

- `/deep-work` — 用戶離開時的自主實作引擎
- `/batch-task` — 序列批次任務處理器（避免 rate limit）

### 品質工具

- `/lint-fix` — ruff + mypy 自動修正
- `/fix-test` — 測試失敗分類修復（先分類 A/B/C/D 再修復，防止盲目讓測試通過）
- `/consistency` — 文檔品質檢查（自洽性、矛盾性、精準度）
- `/distill-spec` — 蒸餾肥大的 spec 文檔

### CLAUDE.md 維護

- `/claude:clean` — 清理 Markdown 元資訊
- `/claude:distill` — 蒸餾文檔，提煉核心精華
- `/claude:sync` — 檢查文檔與程式碼同步性
- `/claude:doc-decode` — 從 CLAUDE.md + 程式碼重建理解文檔（source-docs/）
- `/claude:decode-compare` — 對比 source-docs 與程式碼，驗證精度
- `/claude:daily-maintain` — 每日自動化 CLAUDE.md 維護（compare-first）

### 日常工具

- `/standup` — 每日晨間簡報（昨日 commits、未 commit 變更、跨 session 對話摘要）

### 其他

- `/explain` — 技術概念、架構設計或流程解釋（console / md 模式）
- `/swing-analysis` — Swing Analysis 協作模式（Trajectory Viewer + 日誌監控）
