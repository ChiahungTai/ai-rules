---
name: daily-maintain

description: "每日自動維護（排程用）— 掃描 + 自動修正低風險問題 + commit + morning report"
when_to_use: "Automated daily maintenance run by scheduled agent (ZCode 23:20 定時任務, 2026-08 起; 舊 nightly claude -p 載體已退役). Auto-fixes low-risk findings, commits, and generates a morning report. Do NOT use interactively — use /project-review instead."
argument-hint: "/daily-maintain — 全部執行 | --only graph | sync | doc-health"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# /daily-maintain — 自動維護模式

> **cron 自動執行用。** 人類手動維護請用 `/project-review`。

執行 [daily-maintain skill](../maintain/SKILL.md) 的自動版本。

---

## 行為特徵

| 決策點 | 行為 |
|--------|------|
| 🟢 低風險 findings（X-cap-path, X-tag-module） | **自動修正**，不詢問 |
| 🟡 中風險 findings（X-ep-ready, X6） | **只報告**，不修正 |
| Kanban 無 tag 卡片 | 自動推導並加上 tag |
| Kanban stale cards | 只報告 |
| Commit | 自動 commit 🟢 修正 + 晨報檔（見下方豁免） |
| SYSTEM-MAP 同步 | 不執行（需人類確認狀態語義） |
| Morning report | 若 `ai-analysis/daily-report/` 存在，寫 `YYYY-MM-DD.md`（🔥 待決項置頂），隨 commit 一起進 repo |

---

## Commit-Consent 豁免

**調用 `/daily-maintain` 即隱含同意 🟢 低風險修正的 commit。**

理由：用戶透過排程載體（ZCode 23:20 定時任務）排程此命令 = 明確授權自動維護。只有 🟢 項目（路徑修正、tag 修正）會被 commit，🟡 項目絕不 commit。

Commit message 格式與自動 commit 範圍：見 [maintain](../maintain/SKILL.md)「Commit 規則 — 自動模式」（單一真相源，此處不重複）。

---

## 執行流程

遵循 [daily-maintain skill](../maintain/SKILL.md) 的四階段流程：

1. **Phase 1**: 結構圖新鮮度——opt-in repo 跑 `code-reality build`、無 index 的 repo skip（snapshot 快照鏈已退役，見 [maintain](../maintain/SKILL.md) Phase 1）
2. **Phase 2**: 執行 `/instruction-sync --changed-since yesterday --recursive` → 自動修正路徑問題
3. **Phase 3**: 執行 `/doc-health` → 自動修正 🟢 findings + kanban hygiene
4. **Phase 4**: 彙總報告 → 寫晨報檔到 `ai-analysis/daily-report/YYYY-MM-DD.md`（目錄不存在則 skip）+ commit

**不詢問、不等待、不阻塞。** 所有決策使用 skill 定義的預設值。

---

## 與排程載體的配合

2026-08 起 nightly `claude -p` 載體退役——本 skill 由 **ZCode 每日 23:20 定時任務**執行（讀 skill 檔依規範跑 Phase 1-3；Phase 4 晨報寫檔 skip，report 主體由 nightly-thin 22:57 組裝、判讀節由該任務產生）。手動補跑仍可用：

```bash
# 完整四合一（互動 session 觸發）
/daily-maintain

# 拆開執行（避免單次 session 過長）
/daily-maintain --only graph
/daily-maintain --only sync
/daily-maintain --only doc-health
```

---

## 參數

參數定義見 [maintain](../maintain/SKILL.md)「參數」表（單一真相源：無參數全跑、`--only graph|sync|doc-health`）。

---

## 語音通知

遵循 [voice-notification skill](../voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始每日維護"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「每日維護完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```
