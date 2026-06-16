# Hermes Agent vs ai-rules：六軸結構比對（lessons 的深化）

> **與 [`hermes-agent-lessons.md`](./hermes-agent-lessons.md) 的關係**：lessons 是「**逐功能借鏡發想**」（10 條，Hermes 有 X → ai-rules 可借鏡）；本文是「**多維結構比對**」（6 軸）＋**反向視角**（ai-rules 結構性優於 Hermes 之處）＋**移動方向建議**。兩者互補，不重複。
>
> **查證方法**：所有 Hermes 引用**親自查證原始碼**（非 lessons 轉述），附 `path/to/file.py:行號`；ai-rules 引用本 repo 真實檔案。基於 [`hermes-agent/ai-analysis/`](../../../hermes-agent/ai-analysis/) 01-04 深度分析 ＋ 本輪對 `background_review.py`、`cron/suggestions.py`、`memory_manager.py`、`tools/skill_provenance.py` 原始 prompt／實作的逐行查證。

---

## 0. 為什麼 lessons 之後還需要這份

lessons 的 10 條建立在一個未明說的假設上：**「Hermes 是先進的，ai-rules 是追趕的」**。這個假設在「功能有無」的層面對——Hermes 確實有 background review fork、curator、consent queue，ai-rules 沒有等價的自動化。

但**逐功能比對會遮蔽結構性差異**。同樣是「自我改進迴圈」，Hermes 與 ai-rules 在六個結構維度上的取捨**根本不同**，而其中幾個維度 ai-rules 的選擇**結構性優於 Hermes**——lessons 把這些標成「共鳴而非移植」（1.7）埋掉了，導致優先級建議偏向「補齊 ai-rules 缺的功能」，而非「強化 ai-rules 既有的優勢」。

本文用六個軸重新比對，每軸標明「誰的取捨更適合自己的本質」，最後收斂到一個 lessons 沒提出的問題：**兩者其實在往相反方向移動，起點不同，該補的東西也不同。**

---

## 1. 六軸比對矩陣

| 軸 | Hermes | ai-rules | 誰的取捨更適合自己 |
|---|---|---|---|
| 1 觸發模型 | push（計數器每 10 turn 自動 fire） | pull（人類 fire `/flow-review`） | 各適其性——見 §2.1 |
| 2 訊號源 + 過濾 | AI 觀察推論，**無 noise filter** | 人類原話植入 + **「找重複」時間過濾** | **ai-rules 強** |
| 3 產物性質 | 軟知識（memory/skill，runtime 可覆蓋） | 硬規範（rules，git commit，不可妥協） | 各適其性——決定自動化天花板 |
| 4 衝突解決 / consent | 機械 latch（`dedup_key`、`MAX_PENDING=5`） | 社會契約（展示再確認，`commit-consent`） | 處理的問題不同，不可互代 |
| 5 安全剎車層次 | prompt 層（`Do NOT capture` 清單，靠模型遵守） | 機械閘門 ＋ 人 viewport（不信 LLM 自覺） | **ai-rules 強** |
| 6 失敗模式 | 主動污染（錯誤偏好持久化、每 session 重讀） | 被動停滯（摩擦堆積、迴圈消化不及） | 起點相反——決定移動方向 |

---

### 軸 1：觸發模型（push vs pull）

**Hermes**：計數器驅動。`agent/turn_finalizer.py:377-401` 在 `_iters_since_skill >= 10` 時 trip flag，final response 交付後 spawn background review fork（`run_agent.py:1419`）。**不靠任何人記得**——到 turn 數就 fire。

**ai-rules**：人類驅動。`/flow-feedback`（`commands/flow-feedback.md`）由 user 在「不順的 session 後」主動植入摩擦；`/flow-review`（`commands/flow-review.md`）由 user「有時間時」fire。兩者都靠人記得。

**誰強？各適其性。** Hermes 寫的是軟知識（見軸 3），錯了下個 session 可被新觀察覆蓋，所以高頻自動 fire 的風險可接受。ai-rules 改的是硬規範，**靠人 fire 恰恰是 feature 不是 bug**——它強制一個「人類介入點」，沒有人類判讀就不落地（這是 B 軸鐵律）。把 ai-rules 改成 push 模型，等於把硬規範的自動化天花板推高一階，直接違反 `commit-consent.md`。

**但 pull 模型有一個真實弱點**：消化頻寬取決於人類記得 fire。實證——`ai-analysis/flow-feedback/` 今天（2026-06-17）生兩筆（`review-commit-workflow-mismatch.md`、`docs-mode-ep-ripple-gaps.md`），但 repo 內**沒有 `flow-review/proposals/` 或 review 紀錄目錄**。摩擦在產出端順暢，消化端頻寬是未知數。這是 pull 模型唯一值得修的點（見 §6 行動 2）。

---

### 軸 2：訊號源 + 過濾（noise filter）—— ai-rules 結構性強項

**Hermes 的訊號鏈**：fork 重播對話快照 → `_SKILL_REVIEW_PROMPT`（`agent/background_review.py:45-148`）指示 fork **主動**從對話裡推論使用者偏好與挫折。關鍵句（`:47-48`）：「most sessions produce at least one skill update... A pass that does nothing is a missed learning opportunity」——它被指示**每次都要找東西寫**。

**這是一個沒有 noise filter 的設計**。`hermes-agent/ai-analysis/01-self-improvement.md` 可改善點 1 直指後果：「背景 review fork 自己決定寫什麼，沒有獨立驗證。錯誤的偏好推論會被持久化，並在之後每個 session 被重讀。」Hermes 的防線是 `_SKILL_REVIEW_PROMPT:124-143` 的 `Do NOT capture` 清單（見軸 5），但那是 prompt 層規範。

**ai-rules 的訊號鏈**：`/flow-feedback` **保留 user 原話**（`commands/flow-feedback.md:27`「保留 user 原話；AI 改寫會稀釋」）→ 寫檔累積 → `/flow-review` 聚合時的核心方法論是**「找重複」**（`commands/flow-review.md:46`）：「單次摩擦可能是個案，重複才是系統性」。

**這是一個時間維度的 noise filter**：單次摩擦不落地，要跨多筆、跨 session 重複才升級為系統性問題。它**免費**——不需要任何機械實作，純粹靠「累積 → 人類回顧時自然過濾」。

**為什麼 ai-rules 能用這個 filter 而 Hermes 不能？** 因為過濾需要**等待**，而等待的代價是「延遲落地」。Hermes 自動落地，必須當場判斷（沒有累積過濾的餘裕——要嘛當場寫錯，要嘛漏寫）；ai-rules 最終人類決策，可以容忍「累積 N 筆再議」（`flow-review.md:40`「還沒想清楚就留著下次」）。**自動化失去了時間這個免費的 noise filter**——這是 lessons 1.1「把 Hermes 自動化搬過來」沒算進去的隱藏成本。

> **深層洞察**：lessons 把 ai-rules 的「人工驅動」當成落後。但人工驅動附贈了一個自動化買不到的東西——**時間過濾**。任何把 ai-rules 往 push/自動化推的構想，都要問：搬過去之後，這個 noise filter 還在嗎？若不在，用什麼補？

---

### 軸 3：產物性質（軟知識 vs 硬規範）—— 決定自動化天花板

**Hermes 寫的是軟知識**：`MemoryStore` 重寫 `MEMORY.md`/`USER.md`（`tools/memory_tool.py`）、`skill_manage` 在 `~/.hermes/skills/<name>/` 下 create/patch（`tools/skill_manager_tool.py:559/649`）。兩者都是「給同一個 agent 下次讀的 runtime 知識」——**下個 session 的新觀察可以覆蓋它**。

**ai-rules 改的是硬規範**：`rules/`（auto-loaded 行為規範）、`commands/`（slash commands）。其中包含 `commit-consent.md` 這種**不可妥協的鐵律**（「LLM 絕對不執行 git commit 除非用戶明確同意」）。一條壞 rule 進庫，**每個 session 都讀它**，且只能靠 git revert 回滾。

**這個不對稱是整個移植設計的基石**，lessons 沒有顯式點出：

| | 軟知識（Hermes） | 硬規範（ai-rules） |
|---|---|---|
| 錯了的後果 | 一個 session 偏掉，下次自動修 | 每個 session 重讀壞規範 |
| 回滾成本 | 新觀察自然覆蓋 | git revert（需人類介入） |
| 可承受的自動化程度 | 高（可自動落地） | 低（最多自動到「提案」） |

**結論**：Hermes 能安全自動落地，是因為它自動化的是軟知識。ai-rules 的自動化天花板天生低一階——它只能自動化到「提案」，落地這一步在人類，是**結構使然，不是膽子不夠**。lessons 1.1 把「自動產出提案、不自動落地」講成「把 Hermes 80% 搬過來」的折衷；本文的觀點是：**這不是折衷，是硬規範系統的必然**。

**唯一例外**：`/daily-maintain`（`commands/daily-maintain.md`）是 ai-rules 唯一「自動落地」的命令，但它的 `Commit-Consent 豁免`（`:31-35`）嚴格限定只 commit 🟢 低風險（路徑修正、tag 修正），🟡 絕不 commit。這正是「軟知識可自動、硬規範不可」原則的實作——daily-maintain 處理的實質上是「軟」（機械可判定的路徑/tag），不是「硬」（rule 語意）。

---

### 軸 4：衝突解決 / consent 機制

**Hermes 的 consent 是工程級的**（`cron/suggestions.py`）：
- `MAX_PENDING = 5`（`:54`）——防「nag wall」，滿了新 suggestion 直接 drop
- `dedup_key` latch（`:22`）——dismissed 後不再 re-offer
- 原子寫 + `0600` perms（`:62-66`、`:90-109`）
- 四個 source 統一匯流（`:56`：catalog/blueprint/usage/integration），「acceptance is always explicit (consent-first)」（`:20-22`）

它處理的核心問題是**量**——自動化會產生大量 proposal，需要機械防止嘮叨與重複。

**ai-rules 的 consent 是社會契約級的**（`rules/commit-consent.md`）：展示變更摘要 + commit message → **等待人類明確回覆**「commit/確認/OK」。沒有機械 latch、沒有 dedup_key。它處理的核心問題是**質**——絕不讓 AI 越權 git commit。

**兩者不可互代**。Hermes 的機械 latch 解決「機器嘮叨」，ai-rules 的社會契約解決「AI 越權」。lessons 1.3 建議把 ai-rules 的 daily-maintain suggestion 化，方向對，但要注意：ai-rules 的 suggestion 機制**不需要** Hermes 的 `MAX_PENDING`/`dedup_key` 工程複雜度，因為 ai-rules 的 proposal 量遠低於 Hermes（單人規則庫 vs 多來源自動化）。這裡直接搬 Hermes 的工程是 over-engineering。

---

### 軸 5：安全剎車的層次（prompt vs 機械閘門 vs 人 viewport）—— ai-rules 結構性強項

這是本文最重要的軸，也是 lessons 最沒看透的一層。

**Hermes 的自我改進安全靠 prompt**。`_SKILL_REVIEW_PROMPT:124-143` 有一整段 `Do NOT capture` 清單，設計得相當精緻：

> 「Do NOT capture (these become persistent self-imposed constraints that bite you later)... Environment-dependent failures... Negative claims about tools or features ('browser tools do not work') — **these harden into refusals the agent cites against itself for months** after the actual problem was fixed.」

這段 prompt 對「自我改進的失敗模式」有深刻認知——它知道負面宣稱會「硬化成 agent 引用數月來拒絕自己的 refusal」。配套的還有（`:140-143`）：與其記「工具壞了」，記「修復方法」（capture the FIX, never 'this tool does not work'）——把負面學習翻轉成正面學習。

**但這整段是 L2 證據**（見 `rules/acceptance-evidence.md` 證據階層）——prompt 層規範，完全靠模型遵守，無機械 enforce。`01-self-improvement.md` 可改善點 2 明說：「MEMORY_GUIDANCE 的『宣告性非祈使』是 prompt 層規範，完全靠模型遵守，沒有機械 enforce。」`Do NOT capture` 同理。

**ai-rules 的安全剎車明確拒絕「靠 LLM 自覺」**。這不是推論，是本 repo 從實戰 flow-feedback 蒸餾的核心哲學——`ai-analysis/flow-feedback/review-commit-workflow-mismatch.md:8` 原文：

> 「status 更新是『元動作』（code 之外的筆記更新），無機械強制，靠 LLM 記得。**違反 repo 核心哲學『機械閘門 > LLM 自覺』**。」

同一份 feedback 還確立了兩軸分工（`:22`）：**「檔案級產物（POC/demo）用機械閘門（commit 2.7 掃 poc/ + demo_*.py 強制歸類），對話級產物（finding）用人 viewport（commit 確認對照 diff）。兩軸分工，不靠收緊機制把對話級也塞進機械閘門。」**

**對照**：

| | Hermes | ai-rules |
|---|---|---|
| 安全剎車載體 | prompt 清單（`Do NOT capture`） | 機械閘門 ＋ 人 viewport |
| 證據層（acceptance-evidence） | L2（靠模型遵守） | L1（機械）＋ L6（人類觀察） |
| 對「LLM 自覺」的信任 | 高（靠 prompt 指令） | 低（明文列為反模式） |
| 失敗時 | 錯誤偏好靜默持久化 | 機械閘門擋住／人 viewport 抓到 |

**這是 ai-rules 結構性優於 Hermes 之處**，且根源於 `acceptance-evidence.md` 的理論：AI 同時寫規則又靠自己的 prompt 遵守規則，是「證據獨立性塌縮」的極致——測試與實作共享同一個錯誤前提。Hermes 的 `Do NOT capture` 再精緻，仍是「AI 寫一條規則叫自己別犯錯」。ai-rules 不信這個，要求要嘛機械（L1）要嘛人（L6）。

> **深層洞察**：lessons 1.7 點出「ai-rules 的 acceptance-evidence 比 Hermes 深刻」卻標成「共鳴而非移植」。但這不是共鳴——這是 **ai-rules 應該主動輸出的設計理論**。Hermes 證明「自我改進可工程化」但缺 B 軸；ai-rules 有 B 軸理論但散在多檔。把 `acceptance-evidence` ＋ `commit-consent` ＋ provenance ＋「機械閘門 > LLM 自覺」整理成一份顯式的**「自我改進安全檢查表」**，是 ai-rules 對「任何自我改進系統（含 Hermes）」的最高價值貢獻（見 §6 行動 1）。

---

### 軸 6：失敗模式（主動污染 vs 被動停滯）—— 決定移動方向

這一軸把前五軸收斂成一個行動指引。

**Hermes 怕的是「主動污染」**：background review fork 寫錯偏好 → 持久化 → 每個 session 重讀 → 自我強化錯誤。失敗是**主動的、傳播的**。它該補的是**品質閘門**（往 B 軸靠）——01 可改善點 1、acceptance-evidence 都指向這個。

**ai-rules 怕的是「被動停滯」**：人類忘了 fire `/flow-review` → 摩擦堆積 → 系統不演化。失敗是**被動的、靜止的**。它該補的是**降低 fire 門檻 ＋ 自動提案**（往 A 軸靠，但停在提案層）。

**兩者起點相反，卻在 lessons 裡被當成同一個方向**（「ai-rules 該學 Hermes 的自動化」）。正確的移動是：

```
Hermes（A 軸強、B 軸弱）  ─────加品質閘門────→  交匯點
                                                        ↑
ai-rules（B 軸強、A 軸弱）  ──降 fire 門檻 + 自動提案──┘  (consent + provenance + B 軸兜底)
```

**交匯點**不是「ai-rules 變成 Hermes」，而是兩者在「自動化提案 ＋ consent queue ＋ provenance ＋ B 軸人類兜底」的設計上趨同。差別在抵達路徑：Hermes 從「全自動」往回加剎車；ai-rules 從「全人工」往前加感知。

---

## 2. 三個 lessons 沒點出的深層不對稱

把六軸濃縮成三個可操作的判別原則：

### 2.1 自動化的隱藏成本：失去時間這個免費 noise filter（軸 2）

任何「把 ai-rules 往自動化推」的構想（lessons 1.1 daemon、1.6 context 萃取），都要先回答：**搬過去之後，「累積 → 找重複」這個 noise filter 還在嗎？** 若自動提案 daemon 每筆摩擦都即時產出 proposal，它就繼承了 Hermes 的「無 filter」缺陷。補法不是不做，是讓 daemon **只聚合、只產出已過濾的 proposal**（type-2 設計缺陷要跨筆重複才提案，type-1 時機問題不提案）——把人類 `/flow-review` 的「找重複」邏輯前移到 daemon，而不是把「每筆都寫」搬過來。

### 2.2 安全剎車的層次差距：prompt（L2）不能冒充機械閘門（L1）或人 viewport（L6）（軸 5）

lessons 多處提「加 rule 規範 AI 行為」（如 1.1「反模式自動捕獲」、1.4 curator）。但要套 `acceptance-evidence.md` 的階層檢驗：**任何只靠「AI 讀了規則就會遵守」的剎車是 L2，AI 自我改進時 L2 會塌縮**。ai-rules 的鐵律是「機械閘門 > LLM 自覺」——新加的安全機制若無對應的機械訊號（hook 攔截、檔案存在性、exit code）或人類 viewport，就是 prompt 層規範，等級不夠。**這條直接淘汰了 lessons 裡幾個「加條 rule 就好」的構想**——它們需要的是機械著力點，不是更多文字。

### 2.3 移動方向相反：別用「補齊功能」掩蓋「強化優勢」（軸 6）

lessons 的優先級（P0-P3）幾乎都是「補 ai-rules 缺的 Hermes 功能」。但六軸比對顯示 ai-rules 的結構性優勢（noise filter、機械閘門哲學、A/B 雙軸理論）才是護城河。**資源應該先投入強化優勢（把散落的 B 軸理論顯式化），再補功能**——因為補進來的功能若沒有 B 軸理論治理，會重現 Hermes 的「主動污染」失敗模式。

---

## 3. 反向視角：ai-rules 結構性優於 Hermes 的四點

lessons 把這些標成「共鳴」埋掉，本文拉出來——它們是 ai-rules 不該在借鏡過程中妥協掉的東西：

1. **「找重複」noise filter**（`flow-review.md:46`）——Hermes 完全沒有；自動化系統買不到的時間過濾。
2. **type-1/type-2 ＋ counter-factual 結構紀律**（`flow-feedback.md:31-43`）——強制 type-2（設計缺陷）不可省略、每建議附 counter-factual。Hermes 的 `_SKILL_REVIEW_PROMPT` 無此結構，只說「ACTIVE 找東西寫」，容易停在 type-1（最淺）。
3. **A/B 雙軸理論識破「同家族 LLM 共享偏誤」**（`acceptance-evidence.md`「鐵律：A 軸天花板是 AI 自洽」）——Hermes 的 background review fork 用同一個模型，quorum 對共同盲點無效；ai-rules 在理論層就否定了「同模型自審」的有效性。
4. **「機械閘門 > LLM 自覺」操作化**（`review-commit-workflow-mismatch.md:8`）——Hermes 的 `Do NOT capture` 仍是「AI 寫規則叫自己遵守」（L2）；ai-rules 從實戰學到不信這個，要求 L1 或 L6。

---

## 4. 修正 lessons 的優先級

基於六軸比對，重排 lessons 第 4 節的優先級（標 `[修正]` 為本文調整）：

| 修正後優先 | 構想 | 理由 | 對應軸 |
|---|---|---|---|
| 🥇 [修正] P0 | **「自我改進安全檢查表」**（lessons 1.7 的反向輸出，本文 §6 行動 1） | meta 層先於功能；用 ai-rules 既有的 B 軸理論治理未來所有自動化構想。零 daemon | 軸 5、6 |
| 🥇 P0 | **1.2 skill 挑選契約顯式化 ＋ compact_categories** | 34 skills 真實 token 壓力（非 premature）；與 context-engineering 共鳴 | （lessons 原判，維持） |
| 🥈 [修正] P1 | **commit/build 尾巴 nudge**（本文 §6 行動 2） | 直接攻擊 pull 模型真實弱點（消化頻寬）；成本遠低於 daemon | 軸 1、6 |
| 🥈 P1 | **1.4 rule provenance 標記** | 低成本 frontmatter，為提案層鋪路；但**只標 `ai-proposed`/`distilled-from-failure`**，`human-core` 豁免生命週期（雙軌，呼應 Hermes provenance 但更保守） | 軸 3、5 |
| 🥉 [降級] P2→P3 | **1.1 自動提案 daemon** | 除非先解決 noise filter 前移（§2.1），否則繼承 Hermes 無 filter 缺陷 | 軸 2 |
| ⏳ [維持] P3 | **1.4 rule curator（合併建議）** | 19 rules 仍在人心可 hold 範圍；等 provenance 落地且數量成長 | 軸 3 |

**lessons 原 P0 的「1.5 byte-stable 視角強化論述」降為 nice-to-have**——它零成本但價值是「提升自覺」而非「解決問題」，排在上表之後。

---

## 5. 給 ai-rules 的最小可行動（三件）

若要把本分析從「文件」變成「下一步」，三件，依優先級：

### 行動 1：自我改進安全檢查表（meta 層，零 daemon）

把散落的 `acceptance-evidence.md` ＋ `commit-consent.md` ＋「機械閘門 > LLM 自覺」＋ provenance 整理成一份顯式檢查表。**任何未來的「ai-rules 自動化」構想（含 lessons 與本文提的所有）上線前必須通過**：

1. **provenance**：這變更屬人寫核心、AI 提案、還是從失敗蒸餾？（決定生命週期：human-core 永久，其餘可 stale/review）
2. **產物性質**：動的是軟知識（可自動）還是硬規範（最多提案）？（軸 3）
3. **安全剎車層次**：有機械訊號（L1）或人 viewport（L6）嗎？還是只靠 prompt（L2，不合格）？（軸 5）
4. **noise filter**：自動化後，「累積 → 找重複」的過濾還在嗎？用什麼補？（軸 2）
5. **consent**：自動落地 vs 只提案？邊界劃在哪？（軸 4）
6. **失敗模式**：這機制失敗時是「主動污染」還是「被動停滯」？對應的兜底是什麼？（軸 6）

**第一個客戶就是 lessons ＋ 本文提的所有構想**——用它逐條審，會發現哪些該做、哪些是 premature、哪些缺機械著力點。這比實作任何單一構想都值錢。

### 行動 2：commit/build 尾巴 nudge（降 fire 門檻）

pull 模型唯一真實弱點是「靠人記得 fire」。比 daemon 便宜十倍的最小修法：在 `/commit` 或 `/build` 結束尾巴加一條件 nudge——「這個 session 有摩擦嗎？`ai-analysis/flow-feedback/` 現累積 N 筆待 review，要 `/flow-feedback` 或 `/flow-review` 嗎？」

這不是自動化（不違反 pull 模型），是在**自然停損點**（commit/build 已是人類介入點）降低 fire 門檻。直接攻擊軸 1 的弱點，成本極低。

### 行動 3：skill 挑選契約顯式化（攻擊真實 token 壓力）

34 skills 已是真實 token 成本（非 premature 的過度工程）。把 Hermes `agent/prompt_builder.py:1356-1384` 的「全 index ＋ 強制掃描 ＋ 漸進揭露」契約，結合 `compact_categories`（依任務網域降級無關 skill 的 description），顯式寫進 `skills/` 索引或 `using-agent-skills`。這是 lessons 1.2，本文維持原判——因為它解決的是**現在就存在**的問題，不是未來的。

---

## 6. 一句話總結

lessons 問「ai-rules 能借鏡 Hermes 什麼功能」；本文的答案是——**先別急著借功能。Hermes 與 ai-rules 在六個結構軸上取捨相反，其中 ai-rules 的 noise filter、機械閘門哲學、A/B 雙軸理論是結構性優勢，借鏡過程若妥協掉它們，就會重現 Hermes 的「主動污染」失敗模式。真正該先做的是把這些散落的優勢顯式化成「自我改進安全檢查表」，用它治理未來所有借鏡——用 ai-rules 自己的規則，篩選 ai-rules 自己該學什麼。**

---

*本文為 [`hermes-agent-lessons.md`](./hermes-agent-lessons.md) 的結構化深化。Hermes 引用親自查證自 [`hermes-agent/`](../../../hermes-agent/) 原始碼與 [`hermes-agent/ai-analysis/`](../../../hermes-agent/ai-analysis/) 01-04。落地任何構想前，先用本文 §5 行動 1 的檢查表自審，再走 ai-rules 自己的 `/spec` → `/execution-plan` → `/build`。*
