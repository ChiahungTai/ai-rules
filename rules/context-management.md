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

## Memory 寫入紀律（cluster-first）

harness auto memory 預設「one file = one fact」的「fact」操作定義 = **一個主題的教訓群（cluster）**，非一個事故；「check for an existing file — update rather than duplicate」的 update 目標 = 既有主題檔**加段**（非開新檔）。

寫入決策（新教訓產生時）：

1. 先掃 `MEMORY.md` 索引＋`rg` 主題詞找同主題既有檔
2. 命中 → **加段**：段標題保留原始條目 name、標 original type（cluster 慣例）；索引行不動
3. 無相似主題 → 才開新檔＋新索引行

索引行數隨**主題數**成長，非事故數。量化清理（同主題散檔合併、索引軟上限、計畫完結收斂）由 memory-audit skill 承載（Claude: `../skills/memory-audit/SKILL.md`），寫入端只管 cluster-first。
