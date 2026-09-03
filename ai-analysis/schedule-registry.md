# Schedule Registry（排程職責總覽）

> **定位**：人／AI 可讀的**職責總覽**；**機械真相源仍是 `CronList`**（`registry` drift 的後果限縮為認知過時，不是行為錯誤）。  
> **維護規則**：動排程的 session（`CronCreate`／`CronUpdate`／`CronDelete`）順手同步本檔——慣例層；比對腿兜底見週日 23:00 治理看照（[design.md §4](_tasks/09-03-backlog-governance-design/design.md#§4-排程單一真相源)）。  
> **scope**：ai-rules workspace（ZCode cron 3 條＋本 repo `backlog-browser` plist）；mosaic 側排程指針→memory `reference_periodic-task-landscape`（條目名逐字）。  
> **更新時點**：2026-09-03（baseline `d121837`，CronList 實錄；R-8）；下次改動排程時同步更新本表。

## ZCode Cron（3 條，ai-rules workspace）

| # | automationId | cron | 職責一句 | 對象範圍 | 角色／紅線 |
|---|--------------|------|----------|----------|------------|
| 1 | `automation-751ecce2-a79c-4309-a79c-08486e2ee893` | `40 23 * * *`（每晚 23:40） | ai-rules memory 池收斂（輕掃／弧線預警／波段收斂＋regen）——檔案型清淤腿掛此 | 僅 ai-rules 池 `/Users/ctai/.claude/projects/-Users-ctai-Github-ai-rules/memory/` | 寫手（每夜動手）；紅線：不碰 mosaic 池、不 commit、不改 DB schema、不刪 shared |
| 2 | `automation-fed036ff-17bf-4cf0-a50e-3216a7de6665` | `0 23 * * 0`（週日 23:00） | 治理看照：bundle 組成看照（`deploy_agents.py` 三部署檔 cmp）＋memory lite 稽核（advisory） | ai-rules repo＋memory 池 | 審計（advisory 不動手）；禁止改 rules／memory 條目（戳記除外）；比對腿：`CronList` vs 本表 drift 報告（落地 L8） |
| 3 | `automation-370fafc5-a050-479e-b62f-9c7988d23521` | `10 23 * * 6`（週六 23:10） | 糾正模式週報＋CR 使用健檢（`corrections-weekly` skill） | ai-rules workspace | 報告；DB 唯讀、一頁、腳本失敗 2 次即止 |

> 全名照錄 `CronList` 輸出 `automationId`（非前綴），逐字比對通過。

## 本 repo 相關常駐服務

| 服務 | 形態 | 說明 |
|------|------|------|
| `com.ai-rules.backlog-browser` | `launchd` plist（`~/Library/LaunchAgents/com.ai-rules.backlog-browser.plist`） | `deploy/scripts/run-backlog-browser.sh`（`KeepAlive`），供 board Report Shell（`http://127.0.0.1:6421`） |

## 跨 repo 指針

- mosaic 側排程風景（含 `nightly-watch` 23:50 等）→ memory 條目 `reference_periodic-task-landscape`（池路徑：`~/.claude/projects/-Users-ctai-Github-ai-rules/memory/` 與 `~/.zcode/cli/memories/projects/ai-rules-01610fbb20315a8b/memory/` 雙池；不在則以 mosaic repo 的 `CronList` 為準）。

## 同步義務

- 動排程的 session 順手 `rg automationId` 抽 `CronList` 與本表，更新本表對應行與本節「更新時點」；操作後跑 `CronList` 再 `cat` 本表逐字核對。
- 週日治理看照（automation-fed036ff）含 `CronList` vs 本表比對腿——drift 列報告，不自動改（落地 L8）。

---

*機械真相源：`CronList`；本表為職責總覽。*
