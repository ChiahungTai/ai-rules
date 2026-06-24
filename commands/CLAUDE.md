# Slash Commands 技術規範

## 寫作原則

> **載入時機**：Command 只在被觸發（`/<command>`）時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Command 不支援 `@` transclusion。引用其他檔案一律使用 `[描述](path)` markdown link
- **輸出格式模板**：是 command 的核心交付物規格，不算一般程式碼範例，可接受 >5 行
- **實作程式碼**：避免在 command 中嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

> **架構**: `~/.claude/commands` 符號連結指向本目錄，實現 Git 版本控制和跨專案共享。

## 命令索引

> 命令依「產出受眾」分類（LLM 執行鏈 / 人類 viewport / 三層介入）見 [CLAUDE.md](../CLAUDE.md)「命令的受眾視角」。

### 核心開發流程

```
〔pre-EP 軟 gate〕對話討論新功能 →〔提醒〕/illustrate 結構化提案（city map/重用，軟 gate 不硬擋）→ 人判讀 → 確認
/spec（純輔助·需求釐清，可選）→ /execution-plan（自足：段落0全域研究 + UC盤點 + EP Review, LLM 自判；引用 UC ID + SYSTEM-MAP）→ [/ep-validate（可選）]
          ↓ post-EP checkpoint: /deliverable-review --ep（layer 3 方向：打算做對嗎）→ /illustrate --ep（layer 3 結構：撐得起嗎）
  → /build（含 Agent Review + /audit-test + UC 狀態 + SYSTEM-MAP 同步，LLM 鏈）
          ↓ post-build checkpoint（看狀況呼叫，不硬定先後）: /illustrate（layer 3 結構 viewport，漂移/重造檢查）/ /deliverable-review（layer 3 demo 交付）→ /code-review（layer 1/2, LLM 六軸）→ /commit（UC 狀態確認）
```

**review-pipeline recipe**（變更類型 → review 序列，整脊精簡鏈 #B5）：
- **討論/規劃期**：`/illustrate`（結構，人 viewport，pre-EP 軟 gate 提醒，可多次）
- **review 期**：post-build 可選 `/illustrate`（漂移/重造檢查，B 軸）→ `/code-review`（六軸含 axis 3 結構 = arch 吸收，top-down，A 軸機器）→ `/judge-review`（**一次**）
- **不再** arch→judge→code→judge 兩次 judge（code review 已含結構軸，judge 一次即可）

- `/spec` — 需求釐清（User Story + UC 定位 + Scenario Matrix + 邊界，純輔助；`--write` 寫需求 MD）
- `/execution-plan` — 段落式實作計畫書，自足生成 Self-Contained Segments（含段落0全域研究 + UC盤點 + Scenario Matrix + EP Review Cycle；ep_type blueprint/implementation 支援大型任務綱要+子 EP 結構），掃描 SYSTEM-MAP.md 取得功能上下文
- `/ep-review` — 深層思考審查 Execution Plan 合理性（已內建於 `/execution-plan`，可獨立使用）
- `/ep-validate` — POC 驅動的 EP 技術假設驗證（高技術風險 EP 的動態驗證）
- `/judge-review` — 評估其他 AI 的審查建議，基於深層思考框架決定是否採納
- `/build` — 基於 Execution Plan 逐段實作（TDD + UC 狀態更新 + SYSTEM-MAP 同步）
- `/code-review` — 深層思考六軸代碼審查（含 axis 3 結構 = arch 吸收，top-down；UC 覆蓋度）
- `/deliverable-review` — 人類 viewport 交付軸（layer 3）：天才工程師向老闆 demo 完成的功能——product-type-aware（code: demo-checklist / docs: behavior delta），--ep 審 planned deliverable；方向 >> 品質，不做逐行正確性（交 /code-review）、不審結構（交 /illustrate 結構 viewport）
- `/followup-review` — 審查者回頭驗收實作結果
- `/commit` — Commit 入口（lint 閘門 → POC/Demo 處置 → UC 狀態確認 → message → 確認）

### 自主實作

- `/deep-work` — 用戶離開時的自主實作引擎
- `/batch-task` — 序列批次任務處理器（避免 rate limit）
- `/at` — 排程工作接續（對應 Unix `at`，LLM provider reset usage 後自動 resume）

### 品質工具

- `/lint-fix` — ruff + mypy 自動修正
- `/fix-test` — 測試失敗分類修復（先分類 A/B/C/D/E 再修復，防止盲目讓測試通過）
- `/audit-test` — 測試品質稽核（反模式偵測、覆蓋對稱性、mock 健康度，只讀不寫）
- `/consistency` — 文檔品質檢查（自洽性、矛盾性、順序、自包含、精準度、Signal/Noise）
- `/sync-sources` — 跨檔 single-source invariant 機械檢查（v1：enum + classification 沒被 drift）
- `/distill-spec` — 蒸餾肥大的 spec 文檔

### CLAUDE.md 維護

- `/claude:init` — 為任意專案自動產生 CLAUDE.md（bottom-up，從子模組到 Root）
- `/claude:clean` — 清理 Markdown 元資訊
- `/claude:distill` — 蒸餾文檔，提煉核心精華
- `/claude:sync` — 檢查文檔與程式碼同步性
- `/daily-maintain` — 每日自動維護（cron 用），自動修正低風險問題 + commit
- `/project-review` — 互動式專案審查（人類用），findings + kanban + doc health

### 流程演化回饋

- `/flow-feedback` — session 摩擦收集器：不順 session 後，user 植入摩擦 + AI map 到 skills/commands，產 type-1（時機）/type-2（設計）建議 + 具體例子，寫 `ai-analysis/flow-feedback/`
- `/flow-review` — 定期讀累積 flow-feedback，找重複摩擦 + 聚合 type-2 設計缺陷，跟 user 討論改善 skills/commands（B 軸）；定案 → /execution-plan（大改，必要時先 /spec 釐清需求）/ kanban（小改）→ /build

### 日常工具

- `/standup` — 每日晨間簡報（昨日 commits、未 commit 變更、跨 session 對話摘要、UC 進度 + SYSTEM-MAP 功能進度）
- `/task-status` — Kanban-centric 進度儀表板（Capabilities 完成率 + Kanban lane 分佈 + 模組 Breakdown）
- `/doc-health` — Capabilities + Kanban 健康檢查（12 角度驗證文件準確性）；`--report` 產出完整能力地圖；`--sync-system-map` 用 Capabilities 狀態同步 SYSTEM-MAP.md
- `/rebase <branch> [--autostash]` — Trunk-based rebase（雙向：trunk 上 `merge --ff-only` 吸收 feature / feature 上 rebase onto trunk；trunk 永不被 rebase；可選同步其他 feature worktree）

### 依賴升級（收盤後執行）

- `/upgrade-nt` — 升級 NautilusTrader（breaking changes 掃描 + 跨 worktree 一致性 + SJ external API 測試）
- `/upgrade-sj` — 升級 Shioaji（breaking changes 掃描 + Volume 單位驗證 + SJ external API 測試）

### 其他

- `/illustrate` — 技術概念、架構設計或流程圖解（console / md 模式）+ **4 mode 導向**（設計決策 / 理解既有 / 審查驗證 / 溝通傳達，use case 歸納；結構 viewport city map/call stack/drill 調 arch-thinking skill）
- `/swing-analysis` — Swing Analysis 協作模式（Trajectory Viewer + 日誌監控）
