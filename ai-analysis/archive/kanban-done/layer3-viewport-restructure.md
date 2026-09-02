# layer 3 viewport 重構：debrief 新增 + smell-detector 合併 + deliverable-review 退役

**目標**：layer 3（人類 viewport）命令從 4 顆收斂為 3 顆——新增 `debrief`（AI 改動理解簡報，七段含驗證證據+認知誤差點）、`codebase-sweep`+`human-review` 合併為 `smell-detector`（zoom 預設 + --baseline 廣角 + 測試 smell 三類）、`deliverable-review` 刪除（post-build 吸收進 debrief、--ep 移除）、`illustrate` 無參數改委派 debrief。

**相關**：EP `ai-analysis/execution-plans/ep-layer3-viewport-restructure.md`（2026-08-16 與用戶逐項定案）

**驗收標準**：
- living docs 舊名 0 殘留（歷史檔白名單除外）
- skills/CLAUDE.md 索引與 skills/ 目錄對照一致
- check_single_source.py 改後跑過 exit 0
- /consistency gate 通過

**備註**：smell-detector 測試 smell 三類（資源/怪獸/結構）grounded 於 2026-08-15 nightly 記憶體事件修復實例。
