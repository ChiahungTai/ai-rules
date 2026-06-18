# 從 Hermes Agent 學習改善 ai-rules（整合參考）

> 本文 self-contained。合併自原 `hermes-agent-lessons`（天馬行空發想）、`hermes-agent-axes`（六軸結構比對）、`hermes-agent-synthesis`（機制整合）三份學習軌跡，**為唯一保留版**。提煉 Hermes（`/Users/ctai/Github/hermes-agent`）值得借鏡的設計、ai-rules 的結構性優勢、與未落地項目 backlog。所有 Hermes 引用親自查證原始碼，附 `path:line`。

---

## 1. 核心判斷（三句話定調）

- **該學 Hermes 的「機械工程防護層」**——並發安全、攻擊面防護、資料完整性、LSP 第二用途。這些是 L1 機械機制（模型守不守都擋得住），正好補 ai-rules「機械閘門 > LLM 自覺」哲學的著力點。
- **不該學 Hermes 的「prompt 層安全」**——`Do NOT capture` 清單等（`agent/background_review.py:124-143`）靠模型遵守（L2）。ai-rules 哲學已否定這條路（要求 L1 機械或 L6 人類），搬過來是退步。
- **不能妥協 ai-rules 既有的結構優勢**（§4）——時間 noise filter、機械閘門哲學、B 軸人類兜底。任何借鏡若稀釋它們，就會重現 Hermes 的「錯誤偏好主動污染」失敗模式。

---

## 2. 基石：為什麼 ai-rules 的自動化天花板天生低

Hermes 自動化的是**軟知識**（memory/skill，runtime 可被新觀察覆蓋：`tools/memory_tool.py`、`tools/skill_manager_tool.py`）。ai-rules 改的是**硬規範**（rules/commands，含 `commit-consent.md` 這種不可妥協鐵律）。一條壞 rule 每個 session 重讀，只能 git revert 回滾。

| | 軟知識（Hermes） | 硬規範（ai-rules） |
|---|---|---|
| 錯了後果 | 一個 session 偏掉，下次自動修 | 每個 session 重讀壞規範 |
| 回滾成本 | 新觀察自然覆蓋 | git revert（需人類介入） |
| 可承受的自動化 | 高（可自動落地） | 低（最多自動到「提案」） |

**結論**：Hermes 能全自動，是因為它自動化的是軟知識。ai-rules 的自動化只能到「提案」，落地這步在人類——是結構使然，不是膽子不夠。ai-rules 唯一「自動落地」的 `/daily-maintain`，嚴格限定只自動 commit 🟢 低風險（機械可判定的路徑/tag；`daily-maintain.md:31-35`），正是此原則的實作。

---

## 3. 六軸結構比對（分析框架）

### 3.1 六軸矩陣

| 軸 | Hermes | ai-rules | 誰的取捨更適己 |
|---|---|---|---|
| 1 觸發模型 | push（計數器每 `_n=10` iters fire，`turn_finalizer.py:375`） | pull（人類 fire `/flow-review`） | 各適其性 |
| 2 訊號源+過濾 | AI 觀察推論，**無 noise filter** | 人類原話 + **「找重複」時間過濾**（`flow-review.md`） | **ai-rules** |
| 3 產物性質 | 軟知識（runtime 可覆蓋） | 硬規範（git，不可妥協） | 各適其性（決定天花板） |
| 4 consent | 機械 latch（`dedup_key`/`MAX_PENDING=5`，`cron/suggestions.py`） | 社會契約（展示再確認，`commit-consent.md`） | 處理問題不同，不可互代 |
| 5 安全剎車 | prompt 層（`Do NOT capture`，靠模型遵守） | 機械閘門 + 人 viewport | **ai-rules** |
| 6 失敗模式 | 主動污染（錯誤偏好持久化、每 session 重讀） | 被動停滯（摩擦堆積、迴圈消化不及） | 起點相反 |

### 3.2 三個深層不對稱

1. **自動化的隱藏成本：失去時間這個免費 noise filter（軸 2）**——Hermes 自動落地必須當場判，沒有「累積→找重複」的餘裕。任何把 ai-rules 往自動化推的構想，要問：搬過去後 noise filter 還在嗎？不在，用什麼補？（補法：daemon 只聚合、只產出已過濾 proposal，而非每筆都寫）
2. **安全剎車層次差距：prompt（L2）不能冒充機械閘門（L1）或人 viewport（L6）（軸 5）**——任何只靠「AI 讀了規則就會遵守」的剎車是 L2，AI 自我改進時 L2 會塌縮。這淘汰了「加條 rule 就好」的構想——它們需要機械著力點，不是更多文字。
3. **移動方向相反（軸 6）**：

```
Hermes(A強B弱) ───加品質閘門──→ 交匯點 ←──降fire門檻+自動提案─── ai-rules(B強A弱)
                                  (consent + provenance + B軸兜底)
```

兩者在「自動化提案 + consent queue + provenance + B 軸人類兜底」交匯，但路徑相反：Hermes 從全自動往回加剎車；ai-rules 從全人工往前加感知。

---

## 4. ai-rules 不能妥協的結構優勢

借鏡過程若稀釋以下任一，就會重現 Hermes 的失敗模式：

**四個具體優勢**（Hermes 沒有或不夠深）：
1. **「找重複」noise filter**（`flow-review.md`）——Hermes 完全沒有；自動化系統買不到的時間過濾。
2. **type-1/type-2 + counter-factual 結構紀律**（`flow-feedback.md`）——強制 type-2（設計缺陷）不可省略、每建議附 counter-factual。Hermes review prompt 無此結構，只說「ACTIVE 找東西寫」，易停在最淺的 type-1。
3. **A/B 雙軸理論識破「同家族 LLM 共享偏誤」**（`acceptance-evidence.md`）——Hermes 的 background review fork 用同一個模型自審，quorum 對共同盲點無效。
4. **「機械閘門 > LLM 自覺」操作化**——Hermes 的 `Do NOT capture` 仍是「AI 寫規則叫自己遵守」（L2）；ai-rules 從實戰學到要求 L1 或 L6。

**三個原則**：
- **時間 noise filter**：往自動化推前，問「累積→找重複」還在嗎？
- **機械閘門 > LLM 自覺**：新安全機制若無機械訊號（hook、檔案存在性、exit code）或人 viewport，就是 L2，等級不夠。
- **B 軸人類兜底**：A 軸（機器自驗）天花板是 AI 自洽，自我改進必須最終由人類判讀落地。

---

## 5. 值得借鏡的具體機制

按「價值 × 可落地性」。主要機制標證據層（L1 機械 / L6 人類 / 理念）。

### 5.1 LSP 的第二用途：post-write delta filter（L1，零成本，立即收穫）
ai-rules 把 LSP 當導航查詢（`rules/lsp-navigation.md`）。Hermes 證明 LSP 還有第二用途：**寫後 delta lint**——Edit 前 `snapshot_baseline()` 抓 diagnostics，Edit 後只回報「這次新引入」的錯誤，用 line-shift map（`difflib.SequenceMatcher`）重映射 baseline 到 post-edit 座標（`agent/lsp/manager.py:281-384` + `agent/lsp/range_shift.py`）。**落地**：擴充 `lsp-navigation.md` 加「post-edit delta」用途（先記 pre-edit baseline，post-edit 比對，行號偏移重映射）。直接強化 `/fix-test`、`/audit-test`、`/code-review`。

### 5.2 資料完整性損毀防禦（L1）
Hermes 的 SQLite 損毀防禦三件套（`hermes_cli/kanban_db.py:1184-1413`）：拒開 corrupt DB 前 content-addressed backup（`:1303-1354`）、fail-closed 帶路徑（`KanbanDbCorruptError`）、跨進程 init lock（`.init.lock` + `fcntl.flock`，`:1184-1230`）。**落地**：提煉成 `rules/data-integrity.md`，三原則——拒絕前 content-addressed backup + fail-closed 帶路徑、跨進程 file lock 序列化 init、canonical data 永不修改只動 derived schema。
> ⚠️ **fit 注意**：ai-rules 的 `.kanban/` 是 Markdown（git 為完整性層），fcntl.flock/WAL 等 SQLite 機制不直接適用。這條的真實對象是 **ai-rules 所治理的 DB-backed code 專案**（如 mosaic 的 PostgreSQL——`acceptance-evidence.md` L3 序列重置實例已顯示需求），非 ai-rules 自身的 `.kanban/`。

### 5.3 排程 session 特權隔離（L1+L6）
Hermes cron job 執行前清空 session context（`cron/scheduler.py:1499-1528`，`set_session_vars(platform="", ...)`）——排程執行不是用戶意圖，不能繼承用戶 session 特權。**落地**：擴充 `commit-consent.md` 或寫進 `skills/autonomous-execution`——「排程/daemon session 預設無 commit consent，無論上一個互動 session 同意過什麼」。

### 5.4 自我改進 fork 的並發與攻擊面機械防護（daemon 上線前必備）
Hermes 背景審查 fork（每 ~10 iters，`turn_finalizer.py:376-401`）四層機械安全（全 L1）：壓縮 race prevention（`background_review.py:452-462`，fork 強制 `compression_enabled=False`）、危險指令 auto-deny（`:343-356`）、寫入 drift detection（`tools/memory_tool.py:255-268`，寫入前 re-read under lock，round-trip 失敗拒絕＋備份 `.bak`）、injection 雙層掃描（寫入時 `:78-80` + 載入時 `:160-206`）。**若 ai-rules 未來做任何「AI 自動寫 rule/skill」daemon，這四件是必備清單**。

### 5.5 載體限制：理念可借、實作不可（避免 over-engineering）
**可借理念**：system prompt 三層（stable byte-stable / context cwd 相依 / volatile，`agent/system_prompt.py:62-384`）、時間戳只用日期免每日失效 cache（`:365-371`）、可變資訊注入 user message 而非 system prompt。強化 UC-Driven 三層文件——給「CLAUDE.md 不該放頻繁變動內容」一個機械理由（cache 失效＝成本）。**不能搬的實作**：skills index cache、`compact_categories`、skill 級 `requires_tools`——ai-rules 控制不了（Claude Code 管的）。ai-rules 實際能做：寫好 skill description ＋ 用既有 `skill-cleaner` 定期審查。

### 5.6 Consent 與生命週期（provenance + curator）
- **provenance 決定可整併資格**（`tools/skill_provenance.py:68`）：只有 background-review fork 標記的 `agent-created` skill 才 curator-eligible；前景 user 寫的絕不自動動。**對 ai-rules**：rule provenance 標記（`human-core` 永久 / `ai-proposed` 可演化）是所有未來自動化的前置——低成本 frontmatter。
- **狀態機必須雙向**（`agent/curator.py:255-308`）：自動封存（active→stale 30d→archived 90d）必須有反向復活路徑（reactivated），否則一次誤判永久失能。
- **只 archive 不 delete**（`curator.py:13,17`）：突變前 tar.gz 快照（`curator_backup.py`）。Archive 可復原。
- **accept 是唯一落地入口**（`cron/suggestions.py:220-240`）：proposal 存 job_spec，accept 時直通 create。**但 Hermes 的 `MAX_PENDING`/`dedup_key` 工程複雜度 ai-rules 不需要**——單人規則庫 proposal 量遠低，搬這套是 over-engineering。

---

## 6. 演化種子：感知與蒸餾（capture 相關，尚未成機制）

這些是 lessons 發想中與「capture / 感知層」直接相關、但尚未提煉成正式機制的種子（呼應 capture-bridge EP 的方向）：

- **壓縮前／session 結束前訊號萃取**（`on_pre_compress`，`agent/memory_manager.py:746`）：context 壓縮丟棄舊訊息前，搶救摩擦訊號（連續糾正、權限卡關、同類錯誤重複）。ai-rules 的 session 本身是學習素材，但太多教訓隨 context 消失。
- **成功典範蒸餾**（trajectory，`trajectory_compressor.py`）：`flow-feedback` 只收失敗側；對稱物是「成功蒸餾」——掃描一次過、零 review 修正的 `/build` 軌跡，萃取「為什麼這次順」的可遷移模式。
- **rule 違反遙測**：追蹤每條 rule 被違反的次數（如 `bash-hard-rules` 的「`python -c` 加註解」反覆觸發權限提示）。**違反頻率最高的 rule 不是「執法不力」，而是「規則本身有問題」的訊號**——ai-rules 獨有機會（rule 給 AI 讀，AI 的遵守/違反本身就是遙測）。
- **Hook 點位對照**：整理「Claude Code hook X → ai-rules 自動化 Y」（`SessionStart`→`/standup`、`PreCompact`→flow-feedback 萃取、`Stop`→語音通知），把帶外自動化接上主流程。

---

## 7. 自我改進安全檢查表（落地任何自動化構想前必過）

把散落的 `acceptance-evidence.md` + `commit-consent.md` +「機械閘門 > LLM 自覺」+ provenance + §5.4 fork 機械防護，整理成顯式檢查表。任何「ai-rules 自動化」構想上線前必須回答：

1. **provenance**：人寫核心 / AI 提案 / 從失敗蒸餾？（決定生命週期：human-core 永久，其餘可 stale/review）
2. **產物性質**：動軟知識（可自動）還是硬規範（最多提案）？（§2）
3. **安全剎車層次**：有機械訊號（L1）或人 viewport（L6）嗎？只靠 prompt（L2）不合格。（§3.2-2、§4）
4. **noise filter**：自動化後「累積→找重複」的過濾還在嗎？用什麼補？（§3.2-1）
5. **consent**：自動落地 vs 只提案？邊界劃在哪？（§5.6）
6. **失敗模式**：這機制失敗時是「主動污染」還是「被動停滯」？對應兜底是什麼？（§3.1 軸 6）

---

## 8. 改善 ai-rules 的優先級

合併三份的優先級判斷（`[修正]` = axes 對 lessons 的調整）：

| 優先 | 行動 | 證據層 | 著力點 |
|---|---|---|---|
| 🥇 P0 | LSP post-write delta 寫進 `lsp-navigation.md`（§5.1）| L1 | rule 擴充，零實作 |
| 🥇 P0 | 資料完整性防禦提煉成 `data-integrity.md`（§5.2，重錨到 DB-backed 專案）| L1 | rule 新增 |
| 🥇 P0 | 自我改進安全檢查表（§7）= `mechanical-gate-philosophy` 卡片正在做 | meta | 新文件/skill |
| 🥈 P1 | rule provenance 標記（§5.6）| — | frontmatter（`human-core`/`ai-proposed`，後者才受生命週期） |
| 🥈 P1 | 排程 session 特權隔離寫進 commit-consent（§5.3）| L1+L6 | rule 擴充 |
| 🥈 P1 | capture bridge（消費端摩擦回流）| L2-grounded | 見 `execution-plans/ep-capture-bridge.md`（進行中）|
| 🥉 P2 | commit/build 尾巴 nudge：結尾提示「有摩擦嗎？flow-feedback 累積 N 筆待 review」| — | command 改（降 pull 模型 fire 門檻）|
| ⏳ P3 | rule curator（合併建議）/ daemon 自動提案 | — | 等 provenance + rule 數量成長；否則 over-engineering |

**兩條零成本即時收穫**：P0 的 LSP delta 與 data-integrity，純 rule、零實作。

---

## 9. 風險與節制

- **證據獨立性塌縮**：AI 自己提案 rule、自己驗證——最危險的不是提案太弱，而是提案與驗證共享同一個錯誤前提。自動提案層絕不能自動驗證自己，必須有獨立人類 viewport（§4 原則 3）。
- **過度工程**：Hermes 是生產級 agent；ai-rules 是個人規則庫。§5.5 的載體限制最該警惕——別實作自己控制不了的東西。daemon、curator 在 rule 數量／摩擦頻率不足時是 over-engineering。
- **A/B 軸鐵律**：A 軸（機器提案）可以自動化，B 軸（人類判斷）絕不能。這是 ai-rules 優於全自動 Hermes 的根本。
- **隱私**：§6 的 context 萃取、session 掃描涉及對話內容分析——需明確邊界（只萃取結構化訊號，不持久化原始對話）。

---

## 10. 願景：ai-rules 2.0 三層

把上述收斂成一個方向（非實作承諾）——ai-rules 從「靜態規則庫」升級為「部分自我改進的作業系統」：

1. **感知層（telemetry）**：rule 違反率、skill 引用率、權限提示頻率、flow-feedback 累積、成功/失敗軌跡——被動收集（掛 Claude Code hooks）。
2. **反思層（background review + curator）**：定期掃描感知層，自動產出**結構化提案**（type-1 時機、type-2 設計缺陷、rule 合併建議、stale rule 候選、成功典範）。產出進 consent queue，**不自動落地**。
3. **治理層（consent + provenance + B 軸）**：人類 `/flow-review`/`/project-review` 判讀提案，決定落地。落地變更帶 provenance、可回滾、受生命週期約束（非 human-core 可 stale/archive）。

**關鍵差異在 B 軸**：ai-rules 的 acceptance-evidence 理論保證「自我改進不會退化為 AI 自我強化錯誤」——這是 ai-rules 比 Hermes 成熟之處，也是護城河。抵達路徑：Hermes 從全自動往回加剎車；ai-rules 從全人工往前加感知，兩者在交匯點趨同。

---

*Hermes 引用親自查證自 `/Users/ctai/Github/hermes-agent/` 原始碼。落地任何構想前，先用 §7 檢查表自審，再走 ai-rules 自己的 `/spec` → `/execution-plan` → `/build`。*
