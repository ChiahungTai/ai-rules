# AIR-48 P4 dogfood 首輪——B 形態行為對照記錄

> 範圍（EP P4 事先定）：N=接下來 3-5 個自然 session 或 48h 先到者；不擴成 benchmark。
> 通過判定＝**有確有知識需求案例且全部可核對軌跡下找得到**——「無 fail」不等於成功；無相關任務或觀測不足→標**未驗證**。
> 觀測限制（已知）：codex/muse/bash-rg 未 instrument——跨通道檢索以命令歷史為軌跡。
> 紅線：不動 `_resident-set.md`（凍結）；不動 generator；不為觀測造需求。
> A 期對照：P1 前的 A 形態時期檢索行為（MEMORY.md 全量開場、無 Routing）為基準——「找不到」事件與 A 期對照歸因。

## 記錄表（session 結束前 append；無需求 session 也記一行——分母）

| case | session | 確有知識需求？ | 可核對軌跡（rg/Read 命令） | 找得到？ | 用得出？ | 歸因/備註 |
|------|---------|--------------|--------------------------|---------|---------|----------|
| （例）#1 | zcode 09-09 | 是——任務涉及 X | `rg -i X _inventory.md`→Read 條目 | 是 | 是——條目教訓改變了處置 | — |
| #1 | zcode 09-08 | 是——commit 紀律＋relay 宣稱驗證 | 常駐即中（開場面：feedback_verify-wt-before-commit、feedback_relay-claims-verify-current-state）；未觸發 rg _inventory.md | 是（常駐） | 是——fresh status 對帳抓出 handoff 宣稱 9 檔→實際 staged 8 檔差異，查證歸因＝卡已被 88dc50f 帶走 | 段範圍＝handoff 接手→P3 commit；Routing 檢索路徑本段未實戰（常駐承載） |
| #1（續） | zcode 09-08 | 是——AIR-49 研究需 codex pipeline 四項實證來源與路由設計 | `rg -i "codex memories pipeline" _inventory.md` 命中→Read reference_codex-native-memory-pipeline.md | 是 | 是——四項設計（git 基線/usage 接線/注入條款/路由選項B）直接構成研究結論骨架 | inventory 首行即中；desc 條件句與任務語句同構——B 形態 Routing 路徑首次實戰成功 |
| #1（P5 段） | zcode 09-08 | 是——codex 執行旗標形態/認證拓撲/已知噪音預期 | `rg -i "codex topology" _inventory.md` 命中→Read reference_codex-config-zai-topology.md | 是 | 是——`--model gpt-5.5 -c model_reasoning_effort=low` 形態＋9×missing-content-type 噪音預期直接採用，探針一次過 | 另一發**事後諸葛**：`rg -rn` 的 `-r n` 替換陷阱踩了才想起 reference_rg-r-flag-display-replacement 在場——需求感知失敗（自認已知）非檢索失敗；recall 紀律候選信號 |

## 開場煙霧（每 session 第一個回報）

| case | 開場面＝12 常駐＋Routing？ | 證據（一行） |
|------|--------------------------|-------------|
| （例）#1 | 是 | system 訊息 MEMORY.md 段含 `## Routing` |
| #1 | 是 | 開場 MEMORY.md header「B 形態——常駐定額」；常駐＝Feedback 11＋Project 1＝12 條；`## Routing` 段在（system 訊息直接可見） |

## 「找不到」事件（最高價值信號——逐案歸因）

歸因類別：清單漏列（該升常駐候選）／desc 觸發詞不配（desc 文法修正候選）／inventory 缺（投影 bug）／關鍵詞選擇問題（檢索技巧）。

| case | 找什麼 | 歸因 | 處置候選 |
|------|--------|------|---------|

## 回餵（首輪結束時填）

- rank/常駐集合調整候選：
- 定義表 v1.1 候選：
- 停止條件覆核（3-5 session 或 48h 到了嗎；有確有需求案例了嗎）：
