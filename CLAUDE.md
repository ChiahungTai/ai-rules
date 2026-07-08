# ai-rules 專案 — Claude wrapper

@AGENTS.md

> **全域開發指南**：由 Claude 經 `~/.claude/CLAUDE.md`（→ `ai-development-guide.md`）獨立載入（演化/驗證/UC-Driven/架構/量化鐵律）—— 不在此 `@import`（全域指南是獨立檔，避免雙源 drift）。

## Claude 專屬機制（AGENTS.md neutral 化後補回）

> ai-rules 轉型 multi-harness——AGENTS.md 已拔除 Claude 專屬機制（保持 neutral，四家 harness 都讀），Claude 端細節在此。

### 載體選擇（Hook/Rule/Skill/Agent）

> 載體維度是「**執行確定性**」（何時載入、多確定會執行），與「受眾」（產出給誰）正交。同一命令（如 `/deliverable-review`，人類受眾）可用 Rule 治理其行為、用 Agent 委派調查。

| 需求 | 用什麼 | 為什麼 |
|------|--------|--------|
| 必須每次零例外執行 | **Hook**（`.claude/settings.json`） | 確定性保證，非建議性 |
| 每次 session 都需遵守的行為規範 | **Rule**（`~/.claude/rules/`） | Auto-loaded，治理性 |
| 不需要每次載入的領域知識或工作流 | **Skill**（`.claude/skills/`） | On-demand，不消耗日常 context |
| 按需委派的專家子能力 | **Agent**（`~/.claude/agents/`，Claude native — 本 repo 不維護，按需在 `.claude/agents/` 自建） | 獨立 context，由主對話視任務委派 |

**判斷原則**：
- 如果忘了執行會造成損害 → Hook（如：攔截 `python -c` 跨行 `#` 註解免觸發權限提示 — `hooks/block-python-c-comment.py`）
- 如果 AI 不知道就會犯錯 → Rule（如：用 `fd` 不用 `find`）
- 如果只在特定任務才需要 → Skill（如：Mermaid 圖表生成）
- 如果需要獨立 context 執行專家任務 → Agent（按需自建於 `~/.claude/agents/`，本 repo 不預定義）
