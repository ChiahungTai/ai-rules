---
name: usage-ping
description: "usage reset 探測叫醒 — 在估計的重置時間排 ping（one-shot 階梯：Claude Code 3 發；ZCode 單發——session 綁定限制），落地即確認配額回來。每個 trigger 頂多 1 個 request call、落地零工具呼叫；只寫時間不帶任務（要接續工作用 /at）。觸發詞：叫醒、ping、配額重置、reset 探測、usage reset"
when_to_use: "LLM provider usage reset 時間是估計值、只需要叫醒 LLM 確認配額（不接任務、最小 call 成本）時"
argument-hint: "HH:MM"
allowed-tools: ["Bash", "CronCreate", "CronDelete", "CronList"]
---

# /usage-ping — usage reset 探測叫醒

在估計的 usage reset 時間排**階梯 ping**，時間到叫醒 LLM——model call 能發生 = 配額已重置（落地即確認）。**只叫醒不接任務**。

> **與 `/at` 分工**：本命令只寫時間（叫醒＋確認配額）；時間後面要接「做什麼」（reset 後自動接續工作）用 [`/at`](../at/SKILL.md)；要把工作交給另一個 session/provider 用 [`/handoff`](../handoff/SKILL.md)。

## 核心語義：落地即確認 + 單 call 紀律

- reset 時間是**估計值**——估早的 ping 撞死配額 → turn 不發生（0 call）→ 下一 rung 15 分鐘後再試（有界重試）
- ping 觸發時 model turn 能發生 = 配額已重置：call 本身觸發/證明配額回來，**不需查詢 usage 狀態的機制**
- **單 call 紀律**（per-call 計費）：落地 rung 回一行文字、**零工具呼叫**——任何工具 round-trip 都是多一個 request，不划算
- 語音召回由 Stop hook 機械執行（ping sentinel，0 LLM call；見 [voice-notification](../voice-notification/SKILL.md)）
- **落地不做清理**：清理成本（CronList + CronDelete ≈ 2-3 calls）與讓後續 rung 空落地（各 1 call）相當，且零失敗模式。殘留有兩種、都由下次 `/usage-ping` 排程時 supersede（Phase 2 刪舊覆蓋）清掉：① 未 fire 的後續 rung（by design 空落地耗盡）；② ZCode one-shot 跑完的 completed/failed 記錄——**不自動刪且佔 20 條名額**（Claude Code one-shot 跑完自刪，無此殘留）。階梯成本上界 = rung 數（3 calls）

## 執行流程

### Phase 1：解析時間

| 輸入格式 | 解析方式 | 範例 |
|---------|---------|------|
| `HH:MM` | 今天指定時間；已過 → 明天 | `14:30` → 今天 14:30 |

- **絕對時間 only**（同 /at 治理）：用戶給相對時間時，用 `date` 查當前時間換算成絕對時刻（跨日明確向用戶確認目標日期）
- **一律 +1 分鐘**：T = 輸入時間 + 1 分鐘（秒數誤差防護——輸入的 HH:MM 無秒數，實際 reset 若在 HH:MM:00 邊界，不延後會在重置完成前偷跑，浪費 rung）
- **jitter 規則**：T（+1 後）落在 `:00`/`:30` → 再 +1 分鐘——Claude Code one-shot 在整點/半點最多**提前 90 秒** fire，reset 前偷跑 = 偽陰性
- 計算 3 個 rung 時刻：T、T+15m、T+30m，用 `date` 換算（macOS `-v` 可疊加：`date -v+1M -v+15M`），跨日跨月交給 date 處理，**不手算**
- 用戶在時間後面寫了任務 → 提示「usage-ping 不帶任務；要 reset 後接續工作改用 /at」

### Phase 2：supersede + 名額檢查

1. `CronList` → title/prompt 含 `usage-ping` 的既有排程 → `CronDelete` 全部（**CronCreate 無同名自動覆蓋——不刪舊，舊 rung 會照樣 fire**；completed/failed 殘留記錄一併清——ZCode 這些也佔名額），回報取代了什麼
2. **名額**：ZCode automation 全專案上限 20 條（completed/failed/skipped 都佔位）；清理後餘量 <3 → 降級 rung 數（2 或 1）並在摘要明說

### Phase 3：建階梯 + 召回 sentinel（獨立呼叫同批並行）

以下獨立動作**同一批並行發出**（tool-discipline：批次化省 request）：

1. `CronCreate` × 3——每發 `recurring: false`、pinned cron（`分 時 日 月 *`）、prompt 用下方模板（prompt 首行自帶 `usage-ping` marker，兩端 supersede 匹配都靠它）；title `usage-ping {HH:MM} 叫醒 rung {i}/3`（ZCode 必填；Claude Code 端工具無 title 參數則省略）
   - **ZCode session 綁定限制**：一個 session 僅能成功 `CronCreate` 一次——首發成功後 session 屬於該 task，後續建立全拒（錯誤訊息要求「start a new chat」；並行批次與單發重試皆同，2026-08-18 實測）。ZCode 實務：建 rung 1 即止，降級 1-rung 階梯、摘要明說，錯過 T 的召回改由 sentinel 語音承擔；Claude Code 端無此限制（×3 同批照建）
2. 建召回 sentinel（**原子寫入**，防他 session 的 Stop hook 讀到半寫檔）：`printf '%s\n' {T_epoch} > /tmp/.usage-ping-pending.tmp && mv /tmp/.usage-ping-pending.tmp /tmp/.usage-ping-pending`（內容 = 首 rung 絕對時刻的 epoch 秒；Stop hook 在 [T, T+90min) 內有 turn 結束時機械 say「配額回來了」並自清——0 LLM call）
3. 語音確認：`say -v Meijia -r 180 "已排程在 {HH:MM} 叫醒"`

**rung prompt 模板（每發相同、自足）**：

```
🔴 usage-ping 落地 — usage reset 探測 ping 於 {time} 觸發。
本 turn 能發生 = 配額已重置（落地即確認）。
回應規則（嚴格——per-call 計費，本 trigger 頂多 1 個 request call）：
- 只回一行確認文字，例：「🔴 usage-ping 落地（14:31）— 配額已重置」
- 禁止使用任何工具（CronList/CronDelete/Bash/Read 全不用）
- 不做清理、不查狀態、不接任務——後續 rung 自行空落地（各 1 call），殘留由用戶下次 /usage-ping supersede 清理
- 語音召回由 Stop hook 機械執行，不靠本 turn
```

### Phase 4：確認摘要

```
✅ 排程已建立（/usage-ping）
- 探測時刻：{實際建立的 rung 時刻}（Claude Code 3 發 one-shot；ZCode 僅 rung 1——session 綁定限制見 Phase 3）
- Supersede：{取代的舊排程 or 無}
- 成本：首發落地 1 call；全階梯上界 = 實際 rung 數 calls
- 召回：sentinel 已建，配額回來後 Stop hook 機械語音
```

## 執行約束

- **host 開啟前提**（同 /at）：排程由 host 在觸發時刻 dispatch——Claude Code 是 terminal session、ZCode 是 app；關閉期間到點不觸發（ZCode 記「跳過」不補跑），需要就把 host 開到觸發時刻
- **失敗消耗假設**：fire 失敗（配額仍死）也消耗該 one-shot（兩端文檔皆未記載 retry，保守假設）→ 靠多 rungs 有界取樣，不依賴單發重試（ZCode 僅 1 rung，miss 即無重試——見 Phase 3 session 綁定限制）
- **sentinel 時窗語義**：Stop hook 只在 [T, T+90min)（上界排除——恰 T+90min 走逾時自清）內有 turn 結束才 say——配額死 = 無 turn = 無誤報；逾時靜默自清（階梯早已耗盡，估計過期）。時窗 90min = hook `PING_STALE=5400`（sync 副本：hooks/stop-notification.sh、本檔、voice-notification——改階梯幾何三處同改）
- **生命週期**（同 /at）：Claude Code 綁 session，session 結束排程消失；ZCode workspace 持久——殘留 completed 記錄佔 20 條名額，下次 supersede 清
- **語音**：遵循 [voice-notification](../voice-notification/SKILL.md) 規範（排程確認即時 say；落地召回走 Stop hook sentinel 機制，非 LLM say）

## 使用範例

```bash
# 估計 14:30 reset → 一律 +1 分鐘 → rungs 14:31 / 14:46 / 15:01
/usage-ping 14:30
```
