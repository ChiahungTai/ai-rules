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

STATE.md 定義（定位 / 觀察層 vs 事實層邊界 / 職責矩陣 / 生命週期 / 路徑 / 觸發）與寫入步驟見 state-md-write 共用子範本（Claude: `../skills/_common/state-md-write.md`）（寫入由 at/deep-work 觸發；Open failures 走 kanban 不進 STATE）。

## Memory 生命周期規範（pointer）

寫 memory **前**先過一句話測試（提煉不出一句話＝還沒想清楚＝不寫；提煉得出但屬未定案歸因＝還沒確定＝不寫——user 09-06 拍板）；六問程序、rank 初判、尺寸預算、body 形態等細節**寫前載 memory-audit skill「寫入端紀律」段**（單一源，本 rule 不重述）。索引 ownership：`MEMORY.md` 是條目 frontmatter 的機械投影**禁手寫**（條目檔是唯一寫入點）；弧結案時同步蒸餾條目為終態 facts（結案兩步第三動）。觸發詞：一句話測試、寫入六問、任務終態、cluster-first、索引投影、desc 上限、結案蒸餾、body 形態、確定才寫、歸因未定。
