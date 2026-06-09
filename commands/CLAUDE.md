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
/spec（含 UC 定義）→ /execution-plan（引用 UC ID + SYSTEM-MAP 關聯）→ [/ep-validate（可選，POC 技術驗證）]
  → /build（含 Agent Review + UC 狀態更新 + SYSTEM-MAP 同步）→ /code-review（六軸，含 UC 覆蓋度）→ /commit（含 UC 狀態確認）
```

- `/spec` — 結構化需求討論（User Story、假設、UC 定義、技術選型、邊界）
- `/execution-plan` — 段落式實作計畫書，基於 /spec 生成 Self-Contained Segments（含 Scenario Matrix + EP Review Cycle），掃描 SYSTEM-MAP.md 取得功能上下文
- `/ep-review` — 深層思考審查 Execution Plan 合理性（已內建於 `/execution-plan`，可獨立使用）
- `/ep-validate` — POC 驅動的 EP 技術假設驗證（高技術風險 EP 的動態驗證）
- `/judge-review` — 評估其他 AI 的審查建議，基於深層思考框架決定是否採納
- `/build` — 基於 Execution Plan 逐段實作（TDD + UC 狀態更新 + SYSTEM-MAP 同步）
- `/code-review` — 深層思考六軸代碼審查（含 UC 覆蓋度）
- `/followup-review` — 審查者回頭驗收實作結果
- `/commit` — Commit 入口（lint 閘門 → UC 狀態確認 → message → 確認）

### 自主實作

- `/deep-work` — 用戶離開時的自主實作引擎
- `/batch-task` — 序列批次任務處理器（避免 rate limit）

### 品質工具

- `/lint-fix` — ruff + mypy 自動修正
- `/fix-test` — 測試失敗分類修復（先分類 A/B/C/D 再修復，防止盲目讓測試通過）
- `/audit-test` — 測試品質稽核（反模式偵測、覆蓋對稱性、mock 健康度，只讀不寫）
- `/consistency` — 文檔品質檢查（自洽性、矛盾性、精準度）
- `/distill-spec` — 蒸餾肥大的 spec 文檔

### CLAUDE.md 維護

- `/claude:init` — 為任意專案自動產生 CLAUDE.md（bottom-up，從子模組到 Root）
- `/claude:clean` — 清理 Markdown 元資訊
- `/claude:distill` — 蒸餾文檔，提煉核心精華
- `/claude:sync` — 檢查文檔與程式碼同步性
- `/daily-maintain` — 每日自動維護（cron 用），自動修正低風險問題 + commit
- `/project-review` — 互動式專案審查（人類用），findings + kanban + doc health

### 日常工具

- `/standup` — 每日晨間簡報（昨日 commits、未 commit 變更、跨 session 對話摘要、UC 進度 + SYSTEM-MAP 功能進度）
- `/task-status` — Kanban-centric 進度儀表板（Capabilities 完成率 + Kanban lane 分佈 + 模組 Breakdown + SYSTEM-MAP 功能進度）
- `/doc-health` — Capabilities + Kanban 健康檢查（12 角度驗證文件準確性）；`--report` 產出完整能力地圖；`--sync-system-map` 用 Capabilities 狀態同步 SYSTEM-MAP.md
- `/rebase <target>` — Worktree 分支棧 rebase（當前 branch → target，cascade 子 worktree）

### 依賴升級（收盤後執行）

- `/upgrade-nt` — 升級 NautilusTrader（breaking changes 掃描 + 跨 worktree 一致性 + SJ external API 測試）
- `/upgrade-sj` — 升級 Shioaji（breaking changes 掃描 + Volume 單位驗證 + SJ external API 測試）

### 其他

- `/illustrate` — 技術概念、架構設計或流程圖解（console / md 模式）
- `/swing-analysis` — Swing Analysis 協作模式（Trajectory Viewer + 日誌監控）
