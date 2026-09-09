---
harness-scope: neutral
---

# Context 管理

## Session 管理

不同任務重置 context（Claude: /clear），大範圍探索用獨立 context agent 回摘要；Writer/Reviewer 分離避免自審 bias。同題連續糾正兩次仍失敗就換 prompt、重置 context，不靠累積失敗硬撐；超過兩次應檢討 prompt。

## 想法即時落盤（durable checkpoint）

context 揮發且 quota 可能突然耗盡；真實案例：Codex 審查弧只落中間 findings，最終合成留在 transcript 後 session 死亡，接手需昂貴考古。

- 關鍵發現、方向及理由、排除路徑及原因、下一步意圖，產生即記，不等結算。附「中間檢查點／最終」＋尚待事項，防止未驗收被當完成。
- 有 EP→append 進度；有卡→`task edit --append-notes`；兩者皆無→repo `.agent-tmp/session-journal.md`。長任務 spawn prompt 須注入中間發現落盤要求。
- **唯讀或工單限制寫入時，以該限制為準**：不得自行寫 EP/卡/筆記；以進度訊息回主 session，由有權寫入者保存。checkpoint 不擴張寫入授權。
- 接手 quota 中斷先讀 journal/EP 進度/卡 notes，以檔案現況續行。
- journal 可記未定案工作，不觸發 memory 寫入；memory 須一句話測試＋確定才寫。

## STATE.md（Last session 觀察層）

定位與寫入步驟見 state-md-write 共用子範本（Claude: skills/_common/state-md-write.md）；由 at/deep-work 觸發（Open failures 走 kanban，不進 STATE）。

## Memory 生命周期規範（pointer）

寫前載 memory-audit skill「寫入端紀律」與「載體統一定義表」：一句話都提煉不出或歸因未定就不寫；六問/rank/尺寸/body/desc 等依該 skill。MEMORY.md 是 frontmatter 機械投影禁手寫，條目檔是唯一寫入點；弧結案同步蒸餾終態 facts（結案兩步第三動）。
