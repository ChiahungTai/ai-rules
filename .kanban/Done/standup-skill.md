[tag:skills] standup skill — 昨日活動 digest

# 目標
standup 從 command 升級為 skill（`skills/standup/` SKILL.md + `scripts/aggregate_sessions.py`），產出跨 worktree 昨日活動 digest；mosaic_alpha nightly-sequence op4 整合（append `## 📝 昨日活動` 進 daily-report），退役 05:30 孤兒 log job。

# 相關
- EP: `ai-analysis/execution-plans/ep-standup-skill.md`

# 驗收標準
- [x] `aggregate_sessions.py` dogfood 通過（mosaic 3 wt 含 trading_lab hyphen drift + ai-rules 單 wt；local-tz 時間過濾）
- [x] `skills/standup/SKILL.md` 產出 body（無 `## ` header；empty-sessions 分支）
- [x] maintain Phase 4 merge（owned prefix match，保留外來 section）
- [x] mosaic_alpha nightly-sequence op4 + 完整退役（install.sh PLISTS / README / AGENTS / SYSTEM-MAP / plist + script 註解 / rm plist + run-standup.sh）
- [x] 05:30 job `launchctl bootout`（已執行 gui/502 + 驗證 unloaded）

# 備註
- 決策 A：skill 無雙模式，body only（header 由 invoker echo）
- 決策 B：`## 📝 昨日活動` section append 進 daily-report 最末
- 決策 C：`aggregate_sessions.py` 不加測試（nightly-sequence + 人讀 report = observation loop；套用 feedback_check-trigger-before-adding-tests 教訓）
