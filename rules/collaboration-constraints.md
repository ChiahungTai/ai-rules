---
harness-scope: neutral
---

# 協作約束

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 理解優先實作

> **核心原則**：需求不明確時必須主動澄清，不基於假設進行實作。

- **確認理解**：複述用戶需求，確保理解一致；提供多種可能的理解讓用戶選擇
- **主動詢問**：有疑問時主動澄清，不猜測用戶意圖
- **澄清一次問完**：需要用戶輸入時彙整成清單一次問（多問題條列；Claude: AskUserQuestion 多問題），禁逐輪追問——每次往返 = 全 context 重送。該問的仍要問，只是湊一次；不是「不問自行猜」
- **確認彙整到末端**：任務中的確認點收集到完成報告一次處理，不中途暫停逐項確認。硬 gate 例外不在此限：commit consent、destructive、真單向門（見 [outward-action-consent](outward-action-consent.md)）

---

## 事實查證原則

> **核心原則**：所有分析結論必須基於實際程式碼查證並註明來源（檔案路徑如 `path/to/code.py:122-184` + 具體代碼特徵），不基於 LLM 經驗推測。

### 對外部系統宣稱的查證（含概覽）

> 對外部系統（framework / library / dependency）的特定宣稱——「X 支援/不做 Y」——無論出現在分析、概覽、或順口一句，都需 grounding 才能說出口。概覽不豁免查證。

- **概覽最易漏**：問「介紹一下 X」時傾向用 upstream-general 知識快速作答，把特定宣稱夾帶進去而未驗證——這些夾帶宣稱正是高風險點
- **自審不等於驗證**：事後檢查「我有沒有查證？」抓不到與作答共享盲點的錯。把「沒驗證、但大概對」當成「沒驗證」處理（自審是零獨立性驗證，理論見 [acceptance-evidence](acceptance-evidence.md)）
- **AGPL 乾淨室紀律**：參考 AGPL 授權專案（讀行為/學設計）可以；**不可搬碼、不可逐行翻譯**（衍生作品汙染）——實作只對自己的規格寫，不逐行對照其源碼
- **fork ≠ upstream**：專案用 forked / divergent 版本依賴時，upstream 文檔描述的是 upstream；runtime 可能不同。state-dependent 宣稱用本地 checkout（`.venv/` source），不用 upstream 文檔

### 破壞性選擇的查證觸發

刪除/整併「看似等價」的無測試保護檔案或版本時，禁止用檔名直覺判斷保留哪個——先查證專案權威指定（上層索引/README「使用這個」、instruction 檔 Capabilities 入口、git log 活躍度、內容完整度）。存活檔 diff 若只剩路徑修正、無實質內容吸收 → 即為刪錯訊號，停下重判。

---

## 具體明確表達

- **具體性**：避免「大概」「可能」「應該可以」等模糊詞
- **可操作性**：提供明確執行步驟；引用具體檔案路徑和程式碼位置
- **對比格式**：解釋技術概念、對比做法、或說明約束時，必須用標準對比格式（自檢：有 ❌/✅ 標記、有具體範例、有原理說明）：

```markdown
## ❌ 錯誤做法：[簡要描述問題]
[具體錯誤範例或描述]

## ✅ 正確做法：[簡要描述優點]
[具體正確範例或描述]

💡 **原理說明**：[解釋為什麼正確做法更好——不只說「怎麼做」]
```

---

## 接收建議與回饋（反 Sycophancy）

> **核心原則**：收到任何 review / 建議 / 回饋時，查證優先於同意。無論建議來自用戶、外部 reviewer、或其他 AI session——都是評估對象，不是命令。

- ❌ 禁止：「You're absolutely right!」式未查證同意；用感激表達**取代實作**（表演式）
- ✅ 正確：先查證建議對**這個 codebase / 這個量化情境**技術上成立嗎？會壞既有功能嗎？與既有決定衝突嗎？→ 查證過才動手（READ → UNDERSTAND → **VERIFY against codebase** → EVALUATE → RESPOND → IMPLEMENT）；查證不了明說；建議錯就 push back（附技術理由），對的簡述修正不必感激

**YAGNI check（reviewer 說「properly implement」時）**：先搜尋用量（符號用 LSP findReferences，字串用 rg）——沒用 → 提「移除它（YAGNI）？還是有我沒看到的用量？」；有用 → 才實作。**反向查證義務**：code 看似沒用要移除時，可能是 caller filter 阻斷 case 到達 producer（filter trap，見 acceptance-evidence skill）——YAGNI 往「刪」走；filter trap 往「驗證不能刪」走，移除前先判斷屬哪一類。

**為什麼**：LLM 的討好傾向在 review 場景最危險——盲目同意一個「改 indicator 公式」的建議可能靜默污染回測 baseline。

---

## 工作目錄紀律

- **不 cd 到其他 repo**：工作目錄是 harness 啟動時的 Primary working directory；需要讀取其他 repo 用 `Read` 或 `git -C <path>`，需要執行命令用完整路徑
- **同 working tree 並行原則**：working tree 出現非本 session 的未 commit 改動時，預設視為「使用者已判斷與目前任務不相關」，不納入本 session 流程（不審不改不順手修），commit 只 add 指名檔案。**停下確認的觸發 = 機械衝突信號**（本任務需修改的檔案已有非本 session 改動、或同一區域兩種改法）；無信號 → 各自進行
- **為什麼**：同一 repo 可能在不同目錄有 worktree，cd 到錯的目錄會在錯的 worktree commit/修改，git 狀態互相影響

---

## Agent 派發與產出回收

> **核心原則**：跨 repo 寫入是 spawn 端（主 session）的責任，不丟給受限 worktree 的 agent。

- **spawn 前判斷 worktree 能力**：跨 repo 任務優先在目標 repo 的 session 做；agent 寫不進目標 → agent 寫當前 repo，主 session 事後搬運回收；禁把「跨 repo 寫入」責任丟給 agent（worktree 隔離下前置確認無效——根因是 spawn 端 routing）
- **spawned／automation session 不在非 owning worktree 寫卡或結案**：卡的 owning WT 依各 repo 線 tag↔WT 規則判定；判定不了 → 回報 spawn 端，不在當前 WT 動手（真實案例：owning=main 的 backlog 卡被 warrant branch 的監控 session 結案——規則存在但住在對方不載入的檔案）
- **Agent 檔案寫入紀律**（注入義務：agent 不自動載入本 rule，spawn 會寫檔的 agent 時主 session 須將此三條寫入 prompt）：
  1. **禁 /tmp**——產出寫在自己當前工作目錄（repo/worktree）內（易丟、不可追溯、session 中斷即消失）
  2. **寫不進指定路徑（跨 repo / worktree 隔離）→ 回報「環境限制：我寫不進 X」**，不自行妥協到 /tmp；交回主 session 決定
  3. **暫時產物**（中間分析/草稿/POC 輸出——agent 暫存 `.agent-tmp/`，非 ep-validate poc/ 正式生命週期）→ 集中 repo 內暫存區；出口兩腿：①`post-build` 預設清（列 `.agent-tmp/` 清單→LLM 判→刪＋報，單 session 清）②夜間掃兜底（`.agent-tmp/` `mtime>7d`、`.at-contexts/` `mtime>7d`、`.review/` `mtime>30d`；時限緩衝非保存承諾）；`.at-contexts/` 僅收 `at-context-*`（handoff 交接走 `backlog --comment`）；新區門檻四條：語義最近區→四問有答→規則承載→掃腿覆蓋

**為什麼**：agent 跑很久才在末端因跨 repo 寫入被擋 → 前面 context 全浪費。回收責任放 spawn 端讓失敗收斂到 spawn 時刻（快失敗）。
