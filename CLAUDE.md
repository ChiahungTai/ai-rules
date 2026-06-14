# ai-rules 專案

本專案管理 Claude Code 的 rules、skills、commands。

所有 rules/skills/commands **供 AI 消費**（非人類讀者）—— 寫作以 AI 可消費為準，無需人類式證據出處、版本履歷、精確專案數字（詳見 `rules/_ai-behavior-constraints`、`rules/claude-writing`）。

## 專案結構

- `rules/` — Auto-loaded 行為規範（每次 session 載入）
- `skills/` — On-demand 領域知識和工作流
- `commands/` — Slash commands（`/invoke` 時載入）
- `commands/claude/_common/` — 共用子範本（`claude:*` 命令的引用單元）
- `agents/` — Custom subagent 定義（Agent tool 按需委派，跨專案可用）

## Hooks vs Rules vs Skills 分界

| 需求 | 用什麼 | 為什麼 |
|------|--------|--------|
| 必須每次零例外執行 | **Hook**（`.claude/settings.json`） | 確定性保證，非建議性 |
| 每次 session 都需遵守的行為規範 | **Rule**（`~/.claude/rules/`） | Auto-loaded，治理性 |
| 不需要每次載入的領域知識或工作流 | **Skill**（`.claude/skills/`） | On-demand，不消耗日常 context |
| 按需委派的專家子能力 | **Agent**（`~/.claude/agents/`） | 獨立 context，由主對話視任務委派 |

**判斷原則**：
- 如果忘了執行會造成損害 → Hook（如：commit 前跑 lint）
- 如果 AI 不知道就會犯錯 → Rule（如：用 `fd` 不用 `find`）
- 如果只在特定任務才需要 → Skill（如：Mermaid 圖表生成）
- 如果需要獨立 context 執行專家任務 → Agent（如：LSP 架構驗證）

## 寫作治理

新增 rule/skill/command 時遵守：

1. **先修剪測試**：這行知識從程式碼推導得出嗎？是 → 不寫
2. **選對載體**：Hook？Rule？Skill？按上面的分界判斷
3. **驗證附著**：rule/command 是否包含可驗證的標準？沒有驗證的規則是噪音
4. **長度預算**：CLAUDE.md 越長，AI 越容易忽略重要規則。一條規則一行能說完最好
