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

## 想法即時落盤（durable checkpoint）

> **核心原則**：context 是揮發性記憶，quota 死亡無預警——值得留下的東西在**產生當下**寫入檔案，不等段落結算或 session 結束。只活在對話裡的思考，恢復時靠 transcript 考古（成本極高；真實案例：codex 連續多日多個 session 死於 usage limit，某審查弧 findings 寫到「中間檢查點」後死亡，最終合成只活在 transcript）。

- **落盤時機**（事件驅動）：關鍵發現、方向決策與其理由、被排除的路徑與原因、下一步意圖——出現即寫
- **落盤位置**（既有載體分流，不新發明）：有 EP → EP 檔進度節即時 append（不等段落完成）；有 backlog 卡 → `task edit --append-notes`；探索期（兩者皆無）→ `.agent-tmp/session-journal.md`（repo 內，夜間清掃兜底）
- **落盤內容自帶完成度狀態**：標明「中間檢查點／最終」＋尚待什麼——死亡後接手者才知道可信邊界，不會把未驗收宣稱當完成
- **與 memory 邊界**：journal 是工作記憶外化（未定案也寫）；memory 仍守一句話測試＋確定才寫——journal 不觸發 memory 寫入
- **spawn 長任務 agent**：prompt 注入「中間發現即時落盤 `.agent-tmp/`」——agent 死於 quota 時 findings 不陪葬
- **quota 死亡接手第一動**：先讀 journal／EP 進度／卡 notes 再續行——現況以檔案為準，非對話記憶

## STATE.md（Last session 觀察層）

STATE.md 定義（定位 / 觀察層 vs 事實層邊界 / 職責矩陣 / 生命週期 / 路徑 / 觸發）與寫入步驟見 state-md-write 共用子範本（Claude: `../skills/_common/state-md-write.md`）（寫入由 at/deep-work 觸發；Open failures 走 kanban 不進 STATE）。

## Memory 生命周期規範（pointer）

寫 memory **前**先過一句話測試（提煉不出一句話＝還沒想清楚＝不寫；提煉得出但屬未定案歸因＝還沒確定＝不寫——user 09-06 拍板）；六問程序、rank 初判、尺寸預算、body 形態等細節**寫前載 memory-audit skill「寫入端紀律」段**（單一源，本 rule 不重述）。索引 ownership：`MEMORY.md` 是條目 frontmatter 的機械投影**禁手寫**（條目檔是唯一寫入點）；弧結案時同步蒸餾條目為終態 facts（結案兩步第三動）。觸發詞：一句話測試、寫入六問、任務終態、cluster-first、索引投影、desc 上限、結案蒸餾、body 形態、確定才寫、歸因未定。
