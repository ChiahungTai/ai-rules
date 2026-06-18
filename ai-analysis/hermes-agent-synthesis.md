# 從 Hermes Agent 學習改善 ai-rules

> 本文 self-contained。提煉 `/Users/ctai/Github/hermes-agent/`（Nous Research 的 Hermes Agent）值得 ai-rules 借鏡的設計，給出改善方向。所有 Hermes 引用**親自查證原始碼**，附 `path:line`。目的只有一個：讓 ai-rules 更好。

---

## 1. 核心判斷

三句話定調從 Hermes 該拿什麼、不該拿什麼：

- **該學 Hermes 的「機械工程防護層」**——並發安全、攻擊面防護、資料完整性、LSP 第二用途。這些是 L1 機械機制（模型守不守都擋得住），正好補 ai-rules「機械閘門 > LLM 自覺」哲學的著力點。
- **不該學 Hermes 的「prompt 層安全」**——Hermes 用 `Do NOT capture` 清單等 prompt 規範（`agent/background_review.py:124-143`）管理自我改進安全，靠模型遵守（L2）。ai-rules 哲學已否定這條路（要求 L1 機械或 L6 人類），搬過來是退步。
- **不能妥協 ai-rules 既有的三個結構優勢**——時間 noise filter、機械閘門哲學、B 軸人類兜底（詳 §4）。任何借鏡若稀釋它們，就會重現 Hermes 的「錯誤偏好主動污染」失敗模式。

---

## 2. 設計基石：為什麼 ai-rules 的自動化天花板天生低

這是不對稱，決定一切後續判斷。

Hermes 自動化的是**軟知識**——memory/skill，runtime 可被新觀察覆蓋（`tools/memory_tool.py`、`tools/skill_manager_tool.py`）。錯了下個 session 自動修。ai-rules 改的是**硬規範**——rules/commands，含 `commit-consent.md` 這種不可妥協鐵律。一條壞 rule 每個 session 重讀，只能 git revert 回滾。

| | 軟知識（Hermes） | 硬規範（ai-rules） |
|---|---|---|
| 錯了的後果 | 一個 session 偏掉，下次自動修 | 每個 session 重讀壞規範 |
| 回滾成本 | 新觀察自然覆蓋 | git revert（需人類介入） |
| 可承受的自動化 | 高（可自動落地） | 低（最多自動到「提案」） |

**結論**：Hermes 能全自動，是因為它自動化的是軟知識。ai-rules 的自動化只能到「提案」，落地這步在人類——是結構使然，不是膽子不夠。ai-rules 唯一「自動落地」的 `/daily-maintain`，嚴格限定只自動 commit 🟢 低風險（機械可判定的路徑/tag）；這個窄豁免定義在 `daily-maintain.md`（`commit-consent.md` 本身明文「例外：無」），正是此原則的實作。

---

## 3. 值得借鏡的具體機制

按「對 ai-rules 價值 × 可落地性」排序。主要機制項標明證據層（L1 機械 / L6 人類 / 理念）；§3.6 為選用輔助原則。

### 3.1 LSP 的第二用途：post-write delta filter（零成本，立即收穫）

ai-rules 的 LSP 哲學（`rules/lsp-navigation.md`）把 LSP 當「導航查詢」（goToDefinition / findReferences / hover）。Hermes 證明 LSP 還有第二個高價值用途：**寫後 delta lint**。

- **機制**（`agent/lsp/manager.py:281-384` ＋ `agent/lsp/range_shift.py`）：Edit 前 `snapshot_baseline()` 抓當前 diagnostics，Edit 後只回報「這次編輯新引入」的錯誤。關鍵是 **line-shift map**：在檔案中間插/刪行時，用 `difflib.SequenceMatcher.get_opcodes()` 建行號映射，把 baseline diagnostic 重映射到 post-edit 座標再比對——否則 set-difference 會把所有既有錯誤誤判為「新增」。
- **對 ai-rules 的價值**：直接強化 `/fix-test`、`/audit-test`、`/code-review`——這些命令目前在「判斷哪些錯誤是這次改動引入的」上靠 LLM 自查（L2）。delta filter 把它變成機械比對（L1），證據獨立性極佳。
- **怎麼落地**：ai-rules 跑在 Claude Code 上，LSP 是 native tool，**不能自己跑 language server**。所以這個 pattern 是寫進規則，不是實作——擴充 `lsp-navigation.md` 加一段「post-edit delta」用途：先記 pre-edit baseline，post-edit 用 LSP diagnostics 比對，行號偏移時重映射。

### 3.2 資料完整性損毀防禦（零成本，立即收穫）

Hermes 的 SQLite 損毀防禦（`hermes_cli/kanban_db.py:1184-1413`）三件套，全是 L1，命中 ai-rules 的 Crash-Only 鐵律與 `.kanban/`：

- **Content-addressed backup before refuse**（`:1303-1354`）：拒開 corrupt DB 前先備份，檔名 ＝ `kanban.db.corrupt.{sha256[:16]}.bak`——重複 quarantine 同一份壞 bytes（gateway 重啟、多 profile 共享）自動覆用一個備份。
- **Fail-closed 帶路徑**（`:1284-1300` `KanbanDbCorruptError`）：錯誤訊息直接告訴 user「Original preserved; backup at ...」。
- **Cross-process init lock**（`:1184-1230`）：`threading.Lock` 只在同 process 有效，用 `.init.lock` sidecar ＋ `fcntl.flock` 序列化跨進程初始化，post-init 並發走 DB 自己的 WAL。

**怎麼落地**：提煉成 `rules/data-integrity.md`（或擴充 `quality-constraints.md` 的 Crash-Only 段），三條原則：拒絕前 content-addressed backup ＋ fail-closed 帶路徑、跨進程用 file lock 序列化 init、canonical data 永不修改只動 derived schema。

### 3.3 排程 session 特權隔離（延伸 commit-consent 鐵律）

Hermes cron job 執行前刻意清空 session context（`cron/scheduler.py:1499-1528`）——`set_session_vars(platform="", chat_id="", chat_name="")`。理由：**排程執行不是用戶意圖，不能繼承用戶 session 特權**。

**對 ai-rules 的價值**：直接延伸 `commit-consent.md`。人類在場的 session 有隱含 consent，但 `/daily-maintain` cron、`/at` 排程 session **人類不在場**。daily-maintain 的「豁免只限 🟢 低風險」處理了一半，但若未來 daemon 繼承了某 session「最近同意過 commit」的狀態，可能越權 commit。

**怎麼落地**：擴充 `commit-consent.md` 或寫進 `skills/autonomous-execution`——明確「排程/daemon session 預設無 commit consent，無論上一個互動 session 同意過什麼」。

### 3.4 自我改進 fork 的並發與攻擊面機械防護（daemon 上線前的必備件）

Hermes 的背景審查 fork（每 ~10 turn 自動觸發，`agent/turn_finalizer.py:376-401`）有四層機械安全，全是 L1。**若 ai-rules 未來做任何「AI 自動寫 rule/skill」的 daemon，這四件是必備清單**：

- **壓縮 race prevention**（`agent/background_review.py:452-462`）：fork 強制 `compression_enabled=False`。共享 parent session_id 的 fork 若贏得壓縮 race，會把 parent rotate 成 child，產生 sibling 地獄。
- **危險指令 auto-deny**（`:343-356`）：工具白名單之外，所有危險指令 approval 一律 deny。白名單擋工具「種類」，auto-deny 擋「同一工具內的危險參數」——防 fork 被誘導跑 `rm -rf`。
- **寫入 drift detection 三件套**（`tools/memory_tool.py:255-268` ＋ `:208-237` ＋ `:597`）：寫入前 re-read from disk under file lock，若 on-disk 內容被並發改動而無法 round-trip，**拒絕此次 mutation 並備份 `.bak.<ts>`**。自動寫 rule/skill 的並發安全最低標準。
- **injection 雙層掃描**（`:78-80` 寫入時 ＋ `:160-206` 載入時）：命中威脅 pattern 不刪明文，但注入 system prompt 時取代為 `[BLOCKED: ...]`。對 ai-rules「AI 寫 rule → 下個 session 讀」路徑的 prompt injection 防線。

### 3.5 載體限制：理念可借、實作不可（避免 over-engineering）

Hermes 的 prompt cache 工程理念值得借，但**多數 ai-rules 不能實作**——因為 ai-rules 是 Claude Code 上的 Markdown 庫，skill 的載入、cache、index 全是 Claude Code 管的。

- **可借的理念**：system prompt 三層（stable byte-stable / context cwd 相依 / volatile，`agent/system_prompt.py:62-384`）、時間戳只用日期免每日失效 cache（`:365-371`）、可變資訊注入 user message 而非 system prompt（`agent/conversation_loop.py:679-695`）。這強化 UC-Driven 三層文件——給「CLAUDE.md 不該放頻繁變動內容」一個機械理由（cache 失效 ＝ 成本）。
- **不能搬的實作**：skills index 兩層 cache ＋ mtime manifest（`agent/prompt_builder.py:965-996`）、compact_categories 降級、skill 級 `requires_tools` 條件過濾（`agent/skill_utils.py:478-492`）——這些 ai-rules 控制不了。**ai-rules 實際能做的只有：寫好 skill description**（標明環境依賴，讓 Claude 看到沒裝就跳過）＋ 用已存在的 `skill-cleaner` 定期審查。別花力氣實作一個自己控制不了的 cache 機制。

### 3.6 Consent 與生命週期（依規模選用）

- **provenance 決定可整併資格**（`tools/skill_provenance.py:68-70`）：只有自動產生的 skill 才受自動生命週期約束，人寫的不被自動動。**對 ai-rules**：rule provenance 標記（`human-core` 永久 / `ai-proposed` 可演化）是所有未來自動化的前置——低成本的 frontmatter。
- **狀態機必須雙向**（`agent/curator.py:305-308`）：自動封存（active→stale→archived）必須有反向復活路徑（stale→active），否則一次誤判永久失能。
- **accept 是唯一落地入口**（`cron/suggestions.py:220-240`）：提案存的是 job_spec，accept 時直通 create，沒有第二個 engine。**但 Hermes 的 `MAX_PENDING`/`dedup_key` 工程複雜度 ai-rules 不需要**——ai-rules 是單人規則庫，proposal 量遠低，搬這套是 over-engineering。

---

## 4. 不能妥協的 ai-rules 結構優勢

借鏡過程若稀釋以下三點，就會重現 Hermes 的「錯誤偏好持久化、每 session 重讀、自我強化」失敗模式：

### 4.1 時間 noise filter

ai-rules 的 `/flow-review`「找重複」（單次摩擦是個案，重複才是系統性）是一個免費的 noise filter。Hermes 的自動落地必須當場判斷，沒有這個餘裕。**任何把 ai-rules 往自動化推的構想，要問：搬過去後「累積→找重複」還在嗎？不在，用什麼補？**

### 4.2 機械閘門 > LLM 自覺

ai-rules 從實戰學到不信「AI 寫規則叫自己遵守」。新加的安全機制若無機械訊號（hook 攔截、檔案存在性、exit code）或人類 viewport，就是 L2 prompt 層，等級不夠。

### 4.3 B 軸人類兜底

`rules/acceptance-evidence.md` 的鐵律——A 軸（機器自驗）天花板是 AI 自洽，同家族 LLM 共享系統性偏誤，quorum 對共同盲點無效。Hermes 的 background review fork 用同一個模型自審，正踩在這個盲點上。ai-rules 的自我改進必須最終由人類判讀落地。

---

## 5. 改善 ai-rules 的優先級

| 優先 | 行動 | 證據層 | 著力點 |
|---|---|---|---|
| 🥇 P0 | LSP post-write delta 寫進 `lsp-navigation.md`（§3.1）| L1 | rule 擴充，零實作 |
| 🥇 P0 | 資料完整性損毀防禦提煉成 `data-integrity.md`（§3.2）| L1 | rule 新增 |
| 🥇 P0 | 自我改進安全檢查表（§6）| meta | 新文件 |
| 🥈 P1 | 排程 session 特權隔離寫進 commit-consent（§3.3）| L1+L6 | rule 擴充 |
| 🥈 P1 | rule provenance 標記（§3.6）| — | frontmatter |
| 🥉 P2 | commit/build 尾巴 nudge：結尾提示「有摩擦嗎？flow-feedback 累積 N 筆待 review」| — | command 改 |

**兩條零成本即時收穫**：P0 的 LSP delta 與 data-integrity，純 rule、零實作，立刻提升既有命令（`/fix-test`、`/audit-test`）與既有鐵律（Crash-Only）的操作具體度。

---

## 6. 自我改進安全檢查表（落地任何自動化構想前必過）

把散落的 `acceptance-evidence.md` ＋ `commit-consent.md` ＋「機械閘門 > LLM 自覺」＋ provenance ＋ §3.4 fork 機械防護清單，整理成顯式檢查表。任何「ai-rules 自動化」構想上線前必須回答：

1. **provenance**：人寫核心 / AI 提案 / 從失敗蒸餾？（決定生命週期：human-core 永久，其餘可 stale/review）
2. **產物性質**：動軟知識（可自動）還是硬規範（最多提案）？（§2）
3. **安全剎車層次**：有機械訊號（L1）或人 viewport（L6）嗎？只靠 prompt（L2）不合格。（§4.2）
4. **noise filter**：自動化後「累積→找重複」的過濾還在嗎？用什麼補？（§4.1）
5. **consent**：自動落地 vs 只提案？邊界劃在哪？
6. **失敗模式**：這機制失敗時是「主動污染」還是「被動停滯」？對應的兜底是什麼？

---

## 7. 風險與節制

- **證據獨立性塌縮**：AI 自己提案 rule、自己驗證——最危險的不是提案太弱，而是提案與驗證共享同一個錯誤前提。自動提案層絕不能自動驗證自己，必須有獨立人類 viewport。
- **過度工程**：Hermes 是生產級 agent；ai-rules 是個人規則庫。§3.5 的載體限制最該警惕——別實作自己控制不了的東西。daemon、curator 在 rule 數量／摩擦頻率不足時是 over-engineering。
- **A/B 軸鐵律**：A 軸（機器提案）可以自動化，B 軸（人類判斷）絕不能。這是 ai-rules 優於全自動 Hermes 的根本。

---

## 8. 總結

從 Hermes 該學的不是它的 prompt（L2，ai-rules 哲學已否定），而是它的**機械工程防護層**（L1）——LSP 寫後 delta、損毀防禦三件套、排程特權隔離、fork 並發/攻擊面防護。這些全有機械著力點，全命中 ai-rules 既有鐵律（機械閘門 > LLM 自覺、Crash-Only、commit-consent）。

兩者起點相反：Hermes（A 軸強、B 軸弱）該加品質閘門；ai-rules（B 軸強、A 軸弱）該補機械感知，但停在提案層。真正該先做的是把散落的 B 軸優勢顯式化成 §6 的安全檢查表，用它治理所有借鏡——用 ai-rules 自己的規則，篩選該學什麼。在那之前，LSP delta 與 data-integrity 兩條純 L1 rule 是零成本即時收穫。

---

*Hermes 引用親自查證自 `/Users/ctai/Github/hermes-agent/` 原始碼。落地任何構想前，先用 §6 檢查表自審，再走 ai-rules 自己的 `/spec` → `/execution-plan` → `/build`。*
