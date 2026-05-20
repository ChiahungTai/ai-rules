# Context 管理

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

## Session 管理

### Context 保護

- **任務切換用 `/clear`**：不同任務之間重置 context，避免不相關資訊累積
- **研究用 subagent**：大範圍探索交給 Agent 在獨立 context 中完成，結果摘要回主 session
- **Writer/Reviewer 分離**：審查自己剛寫的 code 有 bias，開新 session 審查品質更好

### 糾正策略

- 同一問題連續糾正 2 次仍失敗 → `/clear`，用更好的 prompt 重來（累積的失敗嘗試比乾淨 context 更糟）
- 糾正超過 2 次 → 說明 prompt 不夠好，不是 AI 不夠努力
