---
harness-scope: neutral
---

# Context 管理

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## Session 管理

### Context 保護

- **任務切換時重置 context**：不同任務之間重置 context（Claude: `/clear`），避免不相關資訊累積
- **研究用 subagent**：大範圍探索交給 Agent 在獨立 context 中完成，結果摘要回主 session
- **Writer/Reviewer 分離**：審查自己剛寫的 code 有 bias，開新 session 審查品質更好

### 糾正策略

- 同一問題連續糾正 2 次仍失敗 → 重置 context（Claude: `/clear`），用更好的 prompt 重來（累積的失敗嘗試比乾淨 context 更糟）
- 糾正超過 2 次 → 說明 prompt 不夠好，不是 AI 不夠努力

## STATE.md（Last session 觀察層）

跨 session resume 的**觀察層**——自己續工作的 session 主觀觀察（卡在哪、為何轉向、下次起手點）。補 at 排程（Claude: `/at`；任務目標一句）/ handoff 交接（Claude: `/handoff`；外部一次性）/ kanban（任務追蹤）/ MEMORY.md（harness learnings）都沒有的：**為什麼**這樣走的 session 主觀。

**邊界（觀察層 vs 事實層，A↔C）**：

- STATE.md = **觀察層**（session 主觀：卡在哪、為何轉向）
- [autonomous-execution](../skills/autonomous-execution/SKILL.md)「Session 級 Recovery」= **事實層**（git + EP re-derive 完成度，機械可信）
- **recovery 不依賴 STATE.md**——STATE 僅補「為什麼」，不覆蓋「做到哪」。resume 完成度以 recovery 事實為準；STATE 觀察僅供意圖參考。
- **禁含完成度宣稱**（negative guidance + 強度上限（指導非強制）見 [state-md-write](../commands/instruction/_common/state-md-write.md)）

**Open failures 走 kanban**：跨 session 未結案的 bug/failure（含 repro）→ `.kanban/Backlog/`（failure card），**不進 STATE.md**（kanban 已是跨 session 未結案追蹤）。

**職責矩陣（防載體重疊）**：

| 載體 | 職責 |
|------|------|
| rules（always-loaded） | 通用規範 |
| MEMORY.md | harness-native learnings（harness 管理） |
| handoff（Claude: `/handoff`） | 外部一次性交接 prompt |
| at（Claude: `/at`） | 任務目標（一次性 ephemeral） |
| kanban Backlog | 任務 / 跨 session 未結案追蹤（含 Open failures） |
| **STATE.md** | **Last session 觀察（獨有）** |

**生命周期**：Last session **每次自主 session（at/deep-work）結束覆寫**（非累積；互動 session 不寫，故兩次自主 session 間的工作不記入 → 可能偏舊——但觀察層非權威，recovery 的 git 事實才是真相）。增長上限由本 rule 的 context 約束。首次 session 無 STATE.md = 正常，resume 跳過讀取。

**路徑**：repo root `STATE.md`（避 `.claude/` protected path——auto-mode 下寫入會被擋）；per-project 語義（每個消費專案自己的 session 觀察）；gitignore 由各專案（本地 session 觀察，default gitignore）。

**觸發**：「離開前寫」綁 session 結束——寫入由 at 排程 / deep-work completion 觸發（Claude 端：`/at`、`/deep-work`；寫入步驟見 [state-md-write](../commands/instruction/_common/state-md-write.md)）；handoff 僅加 note 標示「STATE.md 非交接選項」，不寫入。「開場讀」綁 resume。
