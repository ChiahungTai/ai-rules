---
description: "專案狀態總覽（互動模式）— findings + kanban + doc health 一眼看完，人工確認修正"
when_to_use: "Human-initiated project review. Presents findings, kanban health, and doc quality for manual confirmation. Use when you want to review project status interactively. Replaces the old interactive /claude:daily-maintain."
usage: "/project-review [--init] [--quality] [--all]"
argument-hint: "/project-review — 核心檢查 | --quality 加品質層 | --all 全部 | --init 首次"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# /project-review — 互動式專案審查

> **人類手動維護用。** cron 自動維護請用 `/daily-maintain`。

執行 [daily-maintain skill](../skills/daily-maintain/SKILL.md) 的互動版本。

---

## 行為特徵

| 決策點 | 行為 |
|--------|------|
| 🟢 低風險 findings | **呈現待確認**，用戶說 OK 才修正 |
| 🟡 中風險 findings | 呈現，討論處理方式 |
| Kanban hygiene | 呈現建議，等待確認 |
| Commit | 展示 diff，等待用戶確認後 commit |
| SYSTEM-MAP 同步 | `--all` 時執行，展示 diff 待確認 |

---

## 執行流程

遵循 [daily-maintain skill](../skills/daily-maintain/SKILL.md) 的四階段流程：

1. **Phase 1**: 執行 `/scan-project` → 產出 snapshot → diff fingerprint → **展示變化**
2. **Phase 2**: 執行 `/claude:sync --changed-since yesterday --recursive` → **呈現問題待確認**
3. **Phase 3**: 執行 `/doc-health` → **呈現 findings + kanban hygiene 待確認**
4. **Phase 4**: 彙總報告 → **展示 diff 待確認** → 用戶確認後 commit

**每個決策點都暫停等人類。** 不自動修正、不假設、不跳過。

---

## 參數

| 參數 | 說明 |
|------|------|
| 無參數 | Phase 1 → 2 → 3 → 4，每步等待確認 |
| `--init` | Phase 1 用初始生成模式 |
| `--quality` | Phase 3 加入 CLAUDE.md signal/noise + 導航有效性檢查 |
| `--all` | 全部檢查（含過時卡片、SYSTEM-MAP 同步、kanban 完整 hygiene） |

---

## 與 /daily-maintain 的差異

| | `/daily-maintain`（自動） | `/project-review`（互動） |
|--|--------------------------|--------------------------|
| 觸發 | cron（launchd） | 人類手動 |
| 🟢 findings | 自動修正 | 呈現待確認 |
| 🟡 findings | 只報告 | 呈現 + 討論 |
| Commit | 自動（豁免 consent） | 展示 diff，等待確認 |
| SYSTEM-MAP | 不執行 | `--all` 時執行 |
| 適用場景 | 每日凌晨自動維護 | 人想看整體狀態時 |

---

## 語音通知

遵循 `voice-notification.md`：
- **開始**：`say -v Meijia -r 180 "開始專案審查"`
- **完成**：`say -v Meijia -r 180 "主人！專案審查完成，請驗收～"`
