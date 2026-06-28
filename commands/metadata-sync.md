---
description: "metadata finalization 獨立補漏入口 — 偵測漏掉的文檔狀態結算(Capabilities/Kanban/SYSTEM-MAP/arch/EP 歸檔/flow-feedback),確認後執行修補"
when_to_use: "When /build or /commit forgot metadata finalization (Capabilities rows, Kanban-to-Done, SYSTEM-MAP lifecycle, arch.md, EP archive, flow-feedback archive), or to re-run finalization independently. Read-only detection first, then execute after confirmation."
usage: "/metadata-sync [--check]"
argument-hint: "[--check 僅報告不執行]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# /metadata-sync — metadata finalization 獨立補漏入口

`/build` 或 `/commit` 漏掉 metadata finalization 時的獨立可重跑入口。偵測漏項 → 展示 → 確認後執行修補。

委託 Skill(單一真相源):
- [metadata-sync](../skills/metadata-sync/SKILL.md) — finalization 方法論 + standalone 偵測維度 + 執行細節

**與 `/commit` 階段 3 的關係**:`/commit` 階段 3 在 commit 流程內 invoke 同一 skill(commit mode,原子結算)。本命令是**獨立**入口(standalone mode)——不綁 commit 線性流程,任何時刻發現漏了都能重跑補救。

---

## 執行流程

### 階段 1:偵測漏項(standalone 偵測維度)

依 [metadata-sync SKILL.md](../skills/metadata-sync/SKILL.md)「standalone 偵測維度」表,逐項偵測:

| 漏項 | 偵測 |
|------|------|
| EP 歸檔漏 | `execution-plans/` root 有「所有段落已 commit 但未歸檔」的 EP |
| Capabilities 漏 | git log 近期 commit UC vs 模組 CLAUDE.md `## Capabilities` 表 |
| Kanban 漏 | `.kanban/In-Progress/` 有已完成但未搬 Done 的卡片 |
| SYSTEM-MAP 漏 | 消費 `/doc-health` findings(SYSTEM-MAP vs Capabilities 不一致) |
| architecture.md 漏 | 近期設計變更但 arch 未更 |
| flow-feedback 漏 | `flow-feedback/` root 有已解決但未歸檔 |

**機械事實優先**:EP / Kanban / flow-feedback 用 `rg` / `fd` / `git log` 撈機械事實;SYSTEM-MAP 消費 doc-health findings 不重造偵測。

### 階段 2:展示清單

輸出漏項清單(每項附偵測證據:檔案路徑 / git log 引用 / doc-health finding ID)。無漏項 → 印 `## metadata-sync:✅ 無漏項` 結束。

`--check` flag:只到本階段(報告),不進階段 3。

### 階段 3:確認 + 執行

展示清單 → **等待用戶確認**(遵循 [commit-consent](../rules/commit-consent.md) 精神)→ 執行修補:

- Capabilities:寫入 ✅ 行
- Kanban:`mv` 卡片至 `Done/`
- SYSTEM-MAP:升級生命週期(Built→Verified 等)
- architecture.md:同步設計段落(若適用)
- EP:`mv ai-analysis/execution-plans/<ep>.md _done/`(含子目錄 / blueprint 規則見 SKILL.md)
- flow-feedback:`mv ai-analysis/flow-feedback/<file>.md _done/`

> **原子性例外**:standalone 補漏不要求「Capabilities + Kanban + SYSTEM-MAP 同時完成」的原子(commit mode 才要求)——補的是各自獨立漏項。但同一 UC 的 Capabilities + Kanban 應一起補(兩者描述同 UC 狀態)。

### 階段 4:consistency 閘門

對本次動過的 CLAUDE.md / architecture.md / SYSTEM-MAP.md 逐一跑 `/consistency`(單檔內部自洽)。🔴 / 🟡 → 修正後才算完成。

---

## 流程位置

```
/build（階段5 invoke metadata-sync·build mode 預覽）
   → /commit（階段3 invoke metadata-sync·commit mode 結算）
   → 漏了？任何時刻 → /metadata-sync（standalone 補漏）

/doc-health（檢出 drift）→ /metadata-sync（執行修補）
```

**與 `/doc-health` 分工**:doc-health = 檢查 / 報告(問「文件準確嗎」);本命令 = 執行修補(問「finalization 漏了嗎,補上」)。SYSTEM-MAP 偵測消費 doc-health findings。

---

## 執行約束

- **未確認不執行**:finalization 改的是永久導航狀態,須用戶確認(同 commit-consent 精神)
- **機械事實優先**:偵測靠 `rg` / `fd` / `git log`,不靠 LLM 記憶
- **消費不重造**:SYSTEM-MAP 偵測消費 doc-health findings;單檔自洽 invoke `/consistency`
- **容錯**:無對應檔案(SYSTEM-MAP.md / `.kanban/` / architecture.md / flow-feedback)→ 該項跳過(邏輯見 [metadata-sync](../skills/metadata-sync/SKILL.md)「容錯(三 mode 共用)」段,單一源)

禁止:未確認就改檔 / 跳過偵測直接宣稱「無漏項」 / 把文檔內容同步(程式碼→描述)混入(那屬 build 5c)
