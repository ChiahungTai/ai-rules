# Slash Commands 技術規範

## 寫作原則

> **載入時機**：Command 只在被觸發（`/<command>`）時載入，非每次 session 自動載入。Noise 容忍度比 CLAUDE.md 高，但仍應保持 signal 導向。

- **引用語法**：Command 不支援 `@` transclusion。引用其他檔案一律使用 `[描述](path)` markdown link
- **輸出格式模板**：是 command 的核心交付物規格，不算一般程式碼範例，可接受 >5 行
- **實作程式碼**：避免在 command 中嵌入完整 bash/python 實作 — 描述「做什麼、為什麼」，讓 AI 自己決定「怎麼做」
- **禁止元資訊**：版本號、更新日期、統計資訊（同 CLAUDE.md 規範）

> **架構**: `~/.claude/commands` 符號連結指向本目錄，實現 Git 版本控制和跨專案共享。

## Command 與 Skill 目錄分工

> Claude Code harness 層兩者已收斂——`.claude/commands/foo.md` 與 `.claude/skills/foo/SKILL.md` 都產生 `/foo`，frontmatter 機制相通。harness 機械差異僅在 skill 是**目錄制**（可附私有支援檔 reference/scripts/examples）；本 repo 另以 invocation 語意區分兩者用途（見下表）。無 deprecation 訊號，不必跟軟性建議做 blanket 遷移。

### 三層分工（現況）

| 載體 | 形態 | 職責 |
|------|------|------|
| `skills/` | 目錄制 + 私有支援檔 | 領域知識、工作流（auto-loadable，model-invoked） |
| `commands/` | 扁平單檔 | explicit workflow（人類 `/invoke` 觸發） |
| `commands/instruction/_common/` | 共享子範本 | 跨命令共用的流程範本，非 per-skill 支援檔 |

### 轉換觸發（command → skill）

單檔自足的 command 轉目錄制**零增益**。僅以下情境轉：

- **長出私有、非共享支援檔**：command 需專屬 template/examples/scripts → 轉 skill 目錄放進去
- **該被 auto-load**：內容是相關時自動載入的領域知識，非人類顯式觸發 → 本來就該是 skill

**不要 blanket merge**：`_common/` 共享子範本不被 per-skill 目錄取代（轉了要嘛複製違反 DRY、要嘛仍留共享目錄）；單檔 command（如 `/commit`）無私有支援檔需求。

## 命令索引

> 命令依「產出受眾」分類（LLM 執行鏈 / 人類 viewport / 三層介入）見 [AGENTS.md](../AGENTS.md)「命令的受眾視角」（root CLAUDE.md wrapper 經 `@AGENTS.md` 同載入）。

### 核心開發流程

```
〔pre-EP 軟 gate〕對話討論新功能 →〔提醒〕/illustrate 結構化提案（city map/重用，軟 gate 不硬擋）→ 人判讀 → 確認
/spec（純輔助·需求釐清，可選）→ /execution-plan（自足：段落0全域研究 + UC盤點 + EP Review, LLM 自判；引用 UC ID + SYSTEM-MAP）→ [/ep-validate（可選）]
          ↓ post-EP checkpoint: /deliverable-review --ep（layer 3 方向：打算做對嗎）→ /illustrate --ep（layer 3 結構：撐得起嗎）
  → /build（含 Agent Review + /audit-test + 階段 5a metadata-sync 結算 [UC 狀態+SYSTEM-MAP+EP 歸檔]，LLM 鏈）
          ↓ post-build checkpoint（看狀況呼叫，不硬定先後）: /illustrate（layer 3 結構 viewport，漂移/重造檢查）/ /deliverable-review（layer 3 demo 交付）→ /code-review（layer 1/2, LLM 六軸）→ commit 前 /metadata-sync（更新，code-review 後 code 變了）→ /commit（純 git 提交）
```

**review-pipeline recipe**（變更類型 → review 序列，整脊精簡鏈 #B5）：
- **討論/規劃期**：`/illustrate`（結構，人 viewport，pre-EP 軟 gate 提醒，可多次）
- **review 期**：post-build 可選 `/illustrate`（漂移/重造檢查，B 軸）→ `/code-review`（六軸含 axis 3 結構 = arch 吸收，top-down，A 軸機器）→ `/judge-review`（**一次**）
- **不再** arch→judge→code→judge 兩次 judge（code review 已含結構軸，judge 一次即可）
- **既有 core 審查（無 change，純審穩固度）**：P1 識別 → selective review matrix（[arch-thinking](../skills/arch-thinking/SKILL.md)「core identification」lens）→ 依風險排序逐個 core 跑 `/illustrate` mode B（city map / call path，B 軸人 viewport）+ **人讀 code**（VS Code Cmd+Click 跳轉）→（可選）P2 邊界驗證。B 軸；不排 `/code-review`（正確性靠人讀，非機器 finding）；Console 或 MD 模式。Anthropic selective-review：core = heavy human review、leaf = 放過。

- `/spec` — 需求釐清（User Story + UC 定位 + Scenario Matrix + 邊界，純輔助；`--write` 寫需求 MD）
- `/execution-plan` — 段落式實作計畫書，自足生成 Self-Contained Segments（含段落0全域研究 + UC盤點 + Scenario Matrix + EP Review Cycle；ep_type blueprint/implementation 支援大型任務綱要+子 EP 結構），掃描 SYSTEM-MAP.md 取得功能上下文
- `/ep-review` — 深層思考審查 Execution Plan 合理性（已內建於 `/execution-plan`，可獨立使用）
- `/ep-validate` — POC 驅動的 EP 技術假設驗證（高技術風險 EP 的動態驗證）
- `/judge-review` — 評估其他 AI 的審查建議，基於深層思考框架決定是否採納
- `/build` — 基於 Execution Plan 逐段實作（TDD + 階段 5a metadata-sync 結算：UC 狀態 + SYSTEM-MAP + EP 歸檔）
- `/code-review` — 深層思考六軸代碼審查（含 axis 3 結構 = arch 吸收，top-down；UC 覆蓋度）
- `/deliverable-review` — 人類 viewport 交付軸（layer 3）：天才工程師向老闆 demo 完成的功能——product-type-aware（code: demo-checklist / docs: behavior delta），--ep 審 planned deliverable；方向 >> 品質，不做逐行正確性（交 /code-review）、不審結構（交 /illustrate 結構 viewport）
- `/illustrate` — 結構 viewport + 技術圖解（city map / call stack / drill / 流程；console / md）+ **4 mode 導向**（設計決策 / 理解既有 / 審查驗證 / 溝通傳達）；核心流程三 checkpoint（pre-EP 軟 gate / post-EP / post-build 漂移檢查，見上圖），結構能力調 arch-thinking skill
- `/followup-review` — 審查者回頭驗收實作結果
- `/commit` — Commit 入口（lint 閘門 → POC/Demo 處置 → message → 確認）；finalization 已在 build 階段 5a 結算，commit 前可跑 `/metadata-sync` 更新
- `/metadata-sync` — metadata finalization 獨立更新/補漏入口（commit 前更新或事後補漏：偵測漏掉的 Capabilities/Kanban/SYSTEM-MAP/arch/EP 歸檔/flow-feedback，確認後修補）；build 階段 5a 結算 + 本命令 standalone 補漏共用同一 skill

### 自主實作

- `/deep-work` — 用戶離開時的自主實作引擎（收尾寫 STATE.md Last session 觀察）
- `/sequential-batch` — 序列批次任務處理器（避免 rate limit）
- `/at` — 排程工作接續（對應 Unix `at`，LLM provider reset usage 後自動 resume；resume 讀 STATE.md 補 observation）
- `/handoff` — 產出 self-contained 交接 prompt（進度+決策脈絡+下一步），交另一個 session/repo/provider；與 /at 分工（handoff 交別人 / /at 自己續）；STATE.md 非交接選項（Last session 觀察 / 每 session 覆寫，/at resume 讀）

### 品質工具

- `/lint-fix` — ruff + mypy 自動修正
- `/fix-test` — 測試失敗分類修復（先分類 A/B/C/D/E 再修復，防止盲目讓測試通過）
- `/audit-test` — 測試品質稽核（反模式偵測、覆蓋對稱性、mock 健康度，只讀不寫）
- `/consistency` — 文檔品質檢查（自洽性、矛盾性、順序、自包含、精準度、Signal/Noise）
- `/sync-sources` — 跨檔 single-source invariant 機械檢查（v1：enum + classification 沒被 drift）
- `/distill-spec` — 蒸餾肥大的 spec 文檔

### instruction file 維護

- `/instruction:init` — 為任意專案自動產生 instruction file 體系（root + 模組都雙檔：AGENTS.md source + CLAUDE.md @AGENTS.md wrapper，bottom-up）
- `/instruction:clean` — 清理 Markdown 元資訊
- `/instruction:distill` — 蒸餾文檔，提煉核心精華
- `/instruction:sync` — 檢查文檔與程式碼同步性
- `/daily-maintain` — 每日自動維護（cron 用），自動修正低風險問題 + commit
- `/project-review` — 互動式專案審查（人類用），findings + kanban + doc health

### 流程演化回饋

- `/flow-feedback` — session 摩擦收集器：不順 session 後，user 植入摩擦 + AI map 到 skills/commands，產 type-1（時機）/type-2（設計）建議 + 具體例子，寫 `ai-analysis/flow-feedback/`
- `/flow-review` — 定期讀累積 flow-feedback，找重複摩擦 + 聚合 type-2 設計缺陷 + memory-routing 判定（教訓→Skill/STATE/棄），跟 user 討論改善 skills/commands（B 軸）；定案 → /execution-plan（大改，必要時先 /spec 釐清需求）/ kanban（小改）→ /build

### 日常工具

- `/task-status` — Kanban-centric 進度儀表板（Capabilities 完成率 + Kanban lane 分佈 + 模組 Breakdown）
- `/doc-health` — Capabilities + Kanban 健康檢查（12 角度驗證文件準確性）；`--report` 產出完整能力地圖；`--sync-system-map` 用 Capabilities 狀態同步 SYSTEM-MAP.md
- `/rebase <branch> [--autostash]` — Trunk-based rebase。**原則：trunk 永不被 rebase**，故已對齊的 feature 由 trunk 上 `merge --ff-only` 吸收（非 rebase）；feature 可 rebase onto trunk 或另個 feature；Phase 3 報告其他 feature 落後狀況 + 提示自行同步，不自動 rebase

### 依賴升級（收盤後執行）

- `/upgrade-nt` — 升級 NautilusTrader（breaking changes 掃描 + 跨 worktree 一致性 + SJ external API 測試）
- `/upgrade-sj` — 升級 Shioaji（breaking changes 掃描 + Volume 單位驗證 + SJ external API 測試）

### 其他

- `/swing-analysis` — Swing Analysis 協作模式（Trajectory Viewer + 日誌監控）
