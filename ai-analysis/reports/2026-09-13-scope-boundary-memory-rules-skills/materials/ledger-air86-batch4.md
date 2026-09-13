# AIR-86 批四 candidate ledger（frozen by 5.3 writer，2026-09-13）

> 高後果壓軸批。卡面警示：reviewer 必查「byte ROI 驅動誤砍 bootstrap」。誠實 triage 結論＝**tool-discipline 僅一段可壓（背景執行，mechanics 已由 agent-workflow L71-75 實證承接）、outward 全 KEEP-C 不動**。本批主要價值＝雙審獨立確認兩檔已達 C-core 地板，非削減量。
> Band 誠實預估：tool-discipline ≈3.47K/2.2–2.7K、outward 2,366B/1.8–2.2K——皆將超 band，理由＝剩餘每一節對應真實事故的高頻 guardrail（§C keep-list 逐項吻合）；交雙審逐列裁決，若 codex 指認具體可砍條文則互改輪處理。

## 檔案 1：rules/tool-discipline.md（3,621B；單段壓縮，其餘 KEEP-C）

| id | 節 | 裁定 | 理由 |
|---|---|---|---|
| TD-1 | 背景執行段壓縮 | A 壓縮 | gate 後行為＋[fg]＋30s 例外＋Bash timeout 案例全在 agent-workflow「Spawn 預設背景」L71-75（實證核過）；rule 留兩個 ZCode trap 錨＋行為核心＋pointer |
| TD-2 | 工具選擇原則 | C | routing＋vision-review 禁主 session Read 圖＋spawn 必指定工具＝事故校準 |
| TD-3 | Skill 調用紀律 | C | 先讀再動手＋裸派 EP 案例 |
| TD-4 | Python 命令執行 | C | canonical 單一源（uv run/背景 pytest/timeout 禁令全 user ruling） |
| TD-5 | zsh 動態 flag | C | 真實案例（--primary 1 argparse 拒絕） |
| TD-6 | 檔案修改禁令 | C | sed 禁令＋Read-before-Edit |
| TD-7 | Edit 失敗處置階梯 | C | 高頻首後果（Edit 失敗當下）；機械階梯 |
| TD-8 | 閘門 pipe 禁令 | C | false-green 防護（本弧兩度實證：pipe 假綠） |
| TD-9 | Read 紀律 | C | 86KB 重讀十九次案例 |
| TD-10 | 批次化／輸出慣例 | C | 併發效率＋繁中慣例 |

**TD-1 定稿**（old→new）：
- old：`pytest/長命令、spawn agent 背景執行：spawn **一律明帶 \`run_in_background: true\`**（各端皆安全；ZCode 原生預設前台——省略即前台阻塞主對話，user 插話中斷會連帶殺 agent），spawn 後回報進行中即結束 turn 等完成通知；**ZCode 端 Agent 派發有背景 gate（rewrite 式）：省略參數不再等於前景——自動補背景，真要前景須 prompt 開頭帶 \`[fg]\`**；背景等待禁長等（行為契約見 **agent-workflow skill「Spawn 預設背景」**）；<30s 前台短 probe 例外（現須配 \`[fg]\` 逃生口）與「spawn 不可繞 Bash timeout」真實案例已下沉同處；依 harness 機制執行，禁臆造工具。`
- new：`pytest/長命令、spawn agent 背景執行：spawn **一律明帶 \`run_in_background: true\`**（各端皆安全——前台阻塞中 user 插話會連帶殺 agent），spawn 後回報進行中即結束 turn 等通知，背景等待禁長等；**ZCode 端派發另有背景 gate：省略自動補背景，真要前景（含 <30s 短 probe）須 prompt 帶 \`[fg]\`**。行為契約與案例（30s 例外、spawn 不可繞 Bash timeout）見 **agent-workflow skill「Spawn 預設背景」**；依 harness 機制執行，禁臆造工具。`

## 檔案 2：rules/outward-action-consent.md（2,366B；全 KEEP-C，零文本變更）

| id | 節 | 裁定 | 理由 |
|---|---|---|---|
| OW-1 | 核心原則（outward 定義＋枚舉） | C | 定義源本體（檔末 SoT 條款自證）；枚舉＝具體 outward 類別校準 |
| OW-2 | Reversibility test | C | 判定機制核心 |
| OW-3 | AUTH line 模板＋quote scope＋documentation≠authorization | C | 逐字引用紀律＝本弧每顆 commit 的操作機制；三小節各自承載判準 |
| OW-4 | Commit 專屬段＋機械例外①-④ | C | 例外條款本檔為權威條文（kanban 是 board 細節源非條款源）——①本弧兩度實用、②③結案鏈依賴、④ style 豁免 |
| OW-5 | autonomous 不繼承條款 | C | 深夜波安全邊界 |
| OW-6 | Autonomous shortcut 段 | C | 紅線/黃線分流 trigger |
| OW-7 | Source of truth 邊界 | C | 單一源宣告（刪它即破壞自身治理） |

## C1 承接
無需新增——agent-workflow skill「Spawn 預設背景」（L71-75）已實證承載 TD-1 釋出的全部 mechanics。

## 機械 gate（flash 執行後自跑）
1. `wc -c` 兩 rule 前後（預期 tool-discipline −~140B、outward 不變）
2. 負詞彙（tool-discipline 內 0 hits）：`原生預設前台`、`rewrite 式`、`已下沉同處`、`逃生口`
3. 正向存活：tool-discipline `一律明帶`、`自動補背景`、`[fg]`、`禁臆造工具`、`uv run python`、`args=(--flag 1)`、`禁 sed`、`set -o pipefail`、`86KB`；outward `PENDING: <action>`、`AUTH: user said`、`前次授權不延伸`、`紅線枚舉優先`
4. outward 零變更驗證：`git diff --stat rules/outward-action-consent.md` 空
5. `uv run pytest`（364 基線）＋`uv run python scripts/deploy_agents.py --dry-run` 綠
6. 跨檔引用：autonomous-execution skill 對本 rule 的引用仍自洽；commit skill 程序引用在場

## 偏差回報義務
同前批。outward 若發現任何必改項＝停手回報（高後果檔禁順手修）。
