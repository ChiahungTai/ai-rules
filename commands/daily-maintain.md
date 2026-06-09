---
description: "每日自動維護（cron 用）— 掃描 + 自動修正低風險問題 + commit + morning report"
when_to_use: "Automated daily maintenance run by cron (launchd). Auto-fixes low-risk findings, commits, and generates a morning report. Do NOT use interactively — use /project-review instead."
usage: "/daily-maintain [--init] [--only dep-graph|sync|doc-health]"
argument-hint: "/daily-maintain — 全部執行 | --only dep-graph | --init"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# /daily-maintain — 自動維護模式

> **cron 自動執行用。** 人類手動維護請用 `/project-review`。

執行 [daily-maintain skill](../skills/daily-maintain/SKILL.md) 的自動版本。

---

## 行為特徵

| 決策點 | 行為 |
|--------|------|
| 🟢 低風險 findings（X-cap-path, X-tag-module） | **自動修正**，不詢問 |
| 🟡 中風險 findings（X-cap-dup, X-ep-ready, X6） | **只報告**，不修正 |
| Kanban 無 tag 卡片 | 自動推導並加上 tag |
| Kanban Done/ > 14 天 | 自動刪除 |
| Kanban stale cards | 只報告 |
| Commit | 自動 commit 🟢 修正 + snapshot（見下方豁免） |
| SYSTEM-MAP 同步 | 不執行（需人類確認狀態語義） |

---

## Commit-Consent 豁免

**調用 `/daily-maintain` 即隱含同意 🟢 低風險修正的 commit。**

理由：用戶透過 launchd 排程此命令 = 明確授權自動維護。只有 🟢 項目（路徑修正、tag 修正）會被 commit，🟡 項目絕不 commit。

Commit message 格式：
```
chore(maintain): daily auto-maintain — X findings fixed, Y reported

Auto-fixed: X-cap-path(N), X-tag-module(N)
Reported: X-cap-dup(N), X6(N)
Snapshot: capabilities N, kanban N, findings N
```

---

## 執行流程

遵循 [daily-maintain skill](../skills/daily-maintain/SKILL.md) 的四階段流程：

1. **Phase 1**: 執行 `/scan-project` → 產出 snapshot → diff fingerprint
2. **Phase 2**: 執行 `/claude:sync --changed-since yesterday --recursive` → 自動修正路徑問題
3. **Phase 3**: 執行 `/doc-health` → 自動修正 🟢 findings + kanban hygiene
4. **Phase 4**: 彙總報告 + commit

**不詢問、不等待、不阻塞。** 所有決策使用 skill 定義的預設值。

---

## 與 launchd 的配合

```bash
# 完整四合一
claude -p "/daily-maintain"

# 拆開執行（避免單次 session 過長）
claude -p "/daily-maintain --only dep-graph"
claude -p "/daily-maintain --only sync"
claude -p "/daily-maintain --only doc-health"
```

---

## 參數

| 參數 | 說明 |
|------|------|
| 無參數 | 依序執行 Phase 1 → 2 → 3 → 4 |
| `--init` | Phase 1 用初始生成模式 |
| `--only dep-graph` | 只跑 Phase 1 |
| `--only sync` | 只跑 Phase 2 |
| `--only doc-health` | 只跑 Phase 3 |
