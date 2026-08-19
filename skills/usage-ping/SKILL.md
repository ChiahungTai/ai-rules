---
name: usage-ping
description: "usage reset 探測叫醒 — 在估計的重置時間排 ping（one-shot 階梯：Claude Code 3 發；ZCode 單發——session 綁定限制），落地即確認配額回來；固定週期配額用週期模式——固定時刻制 every Nh from HH:MM（recurring cron 網格）、滾動窗口制 every 5h rolling（+5h01m 自排程鏈：landing 即新窗口錨點、每輪重錨零漂移）。每個 trigger 最小 call 成本；只寫時間不帶任務（要接續工作用 /at）。觸發詞：叫醒、ping、配額重置、reset 探測、usage reset、5 小時窗口、滾動窗口"
when_to_use: "LLM provider usage reset 時間是估計值（一次性時刻、固定時刻週期、或滾動窗口）、只需要叫醒 LLM 確認配額（不接任務、最小 call 成本）時"
argument-hint: "HH:MM | every 5h from HH:MM | every 5h rolling"
allowed-tools: ["Bash", "CronCreate", "CronDelete", "CronList"]
---

# /usage-ping — usage reset 探測叫醒

在估計的 usage reset 時間排 **ping**，時間到叫醒 LLM——model call 能發生 = 配額已重置（落地即確認）。**只叫醒不接任務**。三種模式：**一次性**（單一估計時刻 → 階梯 rungs，見「執行流程」）；**週期-網格**（固定時刻 reset → 單條 recurring cron）；**週期-鏈**（滾動窗口 reset 如 GLM 5 小時窗口 → landing 自排下一發 +5h01m、零漂移，見「週期模式」段）。

> **與 `/at` 分工**：本命令只寫時間（叫醒＋確認配額）；時間後面要接「做什麼」（reset 後自動接續工作）用 [`/at`](../at/SKILL.md)；要把工作交給另一個 session/provider 用 [`/handoff`](../handoff/SKILL.md)。

## 核心語義：落地即確認 + 單 call 紀律

- reset 時間是**估計值**——估早的 ping 撞死配額 → turn 不發生（0 call）→ 下一 rung 15 分鐘後再試（有界重試）
- ping 觸發時 model turn 能發生 = 配額已重置：call 本身觸發/證明配額回來，**不需查詢 usage 狀態的機制**
- **單 call 紀律**（per-call 計費；一次性模式）：落地 rung 回一行文字、**零工具呼叫**——任何工具 round-trip 都是多一個 request，不划算；週期模式放寬（網格 2 calls；鏈 3 calls——landing 直接 say＋自排下一發，理由見「週期模式」）
- 語音召回由 Stop hook 機械執行（ping sentinel，0 LLM call；見 [voice-notification](../voice-notification/SKILL.md)）
- **落地不做清理**：清理成本（CronList + CronDelete ≈ 2-3 calls）與讓後續 rung 空落地（各 1 call）相當，且零失敗模式。殘留有兩種、都由下次 `/usage-ping` 排程時 supersede（Phase 2 刪舊覆蓋）清掉：① 未 fire 的後續 rung（by design 空落地耗盡）；② ZCode one-shot 跑完的 completed/failed 記錄——**不自動刪且佔 20 條名額**（Claude Code one-shot 跑完自刪，無此殘留）。階梯成本上界 = rung 數（3 calls）

## 執行流程

### Phase 1：解析時間

| 輸入格式 | 解析方式 | 範例 |
|---------|---------|------|
| `HH:MM` | 今天指定時間；已過 → 明天 | `14:30` → 今天 14:30 |
| `every Nh from HH:MM`／`every Nh rolling` | 週期模式（網格／鏈）——跳到下方「週期模式」段處理，不走本階梯流程 | `every 5h from 17:41`；`every 5h rolling` |

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

1. `CronCreate` × 3——每發 `recurring: false`、pinned cron（`分 時 日 月 *`）、prompt 用下方模板（prompt 首行自帶 `usage-ping` marker，兩端 supersede 匹配都靠它）；title `usage-ping {rung_i 實際時刻} 叫醒 rung {i}/3`（ZCode 必填；Claude Code 端工具無 title 參數則省略。**標實際觸發時刻（+1 分後的 T），非輸入時間**——標輸入值會讓人誤以為沒 +1）
   - **ZCode session 綁定限制（pending 期間鎖定）**：session 建立首個 automation 後、該 task **未 fire 前**，同 session 後續 `CronCreate` 全拒（錯誤訊息要求「start a new chat」；並行批次與單發重試皆同，2026-08-18 實測）；task fire 後額度釋放、同 session 可再建（2026-08-19 實測：one-shot 落地後同 session 成功建 recurring）。ZCode 實務不變：建 rung 1 即止（rung 2/3 建立時 rung 1 仍 pending → 拒），降級 1-rung 階梯、摘要明說，錯過 T 的召回改由 sentinel 語音承擔；Claude Code 端無此限制（×3 同批照建）
2. 建召回 sentinel（**原子寫入**，防他 session 的 Stop hook 讀到半寫檔）：`printf '%s\n' {T_epoch} > /tmp/.usage-ping-pending.tmp && mv /tmp/.usage-ping-pending.tmp /tmp/.usage-ping-pending`（內容 = 首 rung 絕對時刻的 epoch 秒；Stop hook 在 [T, T+90min) 內有 turn 結束時機械 say「配額回來了」並自清——0 LLM call）
3. 語音確認：`say -v Meijia -r 180 "已排程在 {T} 叫醒"`（T = rung 1 實際時刻，同 title 標實際觸發時刻）

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

## 週期模式（固定週期配額輪詢）

> 按 reset 語義選：**固定時刻制**（每天同樣牆上時刻 reset、秒級抖動）→ 網格模式 `every 5h from HH:MM`；**滾動窗口制**（窗口從首用起算 N 小時、邊界隨使用漂移，如 GLM 5 小時窗口）→ 鏈模式 `every 5h rolling`。一次性階梯不適用此場景——每週期重排 rungs 成本高且 ZCode session 綁定（pending 期間鎖定，見 Phase 3）擋住後續建立。

### 網格模式（固定時刻 reset）

> 用法：`/usage-ping every 5h from 17:41`（from = 觀察到的 reset 邊界，分鐘精度即可）。

- **排程形態**：單條 `recurring: true` cron（無 intervalUnit）。分 = 邊界分 +1（同 +1 分鐘原則）；時網格 = 邊界時 mod 週期起算——`from 17:41`（N=5）→ `42 2-23/5 * * *`，每天 02:42/07:42/12:42/17:42/22:42。通用式：`{M+1} {H mod N}-23/{N} * * *`；N 不整除 24 時有跨日接縫（5h 網格 22→02 只隔 4h）——與 provider 實際排程不符就用觀察 re-anchor
- **秒級重試不存在**：cron 最小粒度 1 分鐘、dispatch 無 retry——「配額過 10 幾秒再試」無法事後補試；但配額死的 fire = turn 不發生 = **0 call 免費失敗**，+1 分鐘 margin 是唯一（且對秒級漂移足夠的）吸收機制
- **prompt 靜態自足、禁引用本檔**：recurring prompt 每週期原樣發送——landing session 去讀 SKILL.md 是每週期多 1 個 Read call，禁
- **成本**：每週期 2 calls（landing + say）；去掉步驟 1 = 1 call 純文字。recurring 不留 completed 記錄、恆佔 1 名額。語音不走 sentinel——hook 時窗 [T, T+90min) 無法跨週期 re-arm（跨日接縫使固定 offset 必錯一次），landing 直接 say 換確定性
- **漂移侵蝕**：邊界秒差每週期累積 → margin 縮；fire 開始 miss（歷史記 failed、無語音）→ 重新錨定：再跑本命令帶新觀察邊界（Phase 2 supersede 刪舊 recurring）。miss 週期 = 0 call
- **ZCode session 綁定**：session 有 pending（未 fire）automation 時建不了新排程，換新 chat；既有 task 已 fire/completed 則同 session 可建（2026-08-19 實測）。recurring 恆 active——建立後同 session 再建其他排程預期被拒（未驗證）

**recurring prompt 模板**：

```
🔴 usage-ping 週期落地 — 配額週期輪詢 ping 觸發。
本 turn 能發生 = 配額已重置（落地即確認）。
回應規則（嚴格——per-call 計費，本 trigger 2 個 request call 內完成）：
- 步驟 1（唯一工具 call）：say -v Meijia -r 180 "配額回來了"
- 步驟 2：回一行確認文字，例：「🔴 usage-ping 週期落地 — 配額已重置」
- 禁止其他工具（CronList/CronDelete/Read 全不用）；不做清理、不查狀態、不接任務
```

title `usage-ping every {N}h 週期叫醒`（保留 marker 供 supersede 匹配）。

### 鏈模式（滾動窗口 reset）

> 用法：`/usage-ping every 5h rolling`。**核心洞察：landing call 即新窗口首用**——roll 後第一個 request 是 ping 自己，邊界被錨定在 landing 時刻、下輪邊界 = landing + 5h → 下一發排 **landing + 5h01m（delayMinutes=301）精確無漂移**（每輪重新錨定、誤差不累積——API 做不到的 301 分鐘累加節奏因此不必要）。

- **建立**：先 Phase 2 supersede（網格與鏈互斥——網格排程多餘且其 fire 也會錨定窗口）；`CronCreate(delayMinutes=301, recurring=false, title="usage-ping 鏈 ping", prompt=下方鏈模板)`。首發 +301min 對任何當前窗口錨點都 ≥ 邊界+1min（錨點 ≤ 現在 → 邊界 ≤ 現在+5h），保證落地後自校正；**用戶已知精確邊界**（provider UI 直示 reset 時刻）→ **僅首發**改釘 邊界+1min 的 pinned cron 貼邊宣告（如邊界 22:43 → cron `44 22 ...`）——後續每發恆為前一落地 +301min 自錨定，不再用 cron
- **landing 協議（3 calls）**：① `CronList` → 刪 title 含 usage-ping 之**非 active** 殘留（防 20 名額塞滿；刪除失敗不重試）② 同批並行 `say`「配額回來了」＋ `CronCreate` 下一發（delayMinutes=301、prompt=鏈模板原文照抄）③ 一行回覆
- **失效模式**：host 關閉錯過 fire → skipped 消耗 one-shot → **鏈死、無自動復活**（有別於網格 recurring 恆存續）→ 重跑本命令重建——**任意時刻重建皆安全**（配額休眠語義：關機期間無請求＝無 roll，開機後首命令才是新窗口錨點 R ≤ 現在 → 新首發 now+301min ≥ R+5h+1min；歸納上鏈只死於 fire 未發生或抄寫變異，不死於邊界估錯）；Mac 睡眠 miss 可用自動化頁「保持喚醒」全局開關緩解；模板照抄變異（quine 風險）→ 落地走樣肉眼可見、重跑修復；provider 實為固定時刻制 → 改用網格模式
- **session 綁定**：鏈落地 session 的前一發已 fire（completed）→ 額度已釋放 → landing 內 CronCreate 可成功（pending-lock 模型，見 Phase 3）。**鏈綁定 session 勿另建 pending 排程**（鎖定會拒 landing 的 CronCreate → 鏈死）——`/at` 用別的 chat；`/usage-ping` rerun 例外（supersede 先刪 active link 釋放額度再建）
- **語音**：landing 直接 say（同網格理由——sentinel 時窗無法跨週期 re-arm）

**鏈模板**（建立與每發照抄用）：

```
🔴 usage-ping 鏈落地 — 滾動 5h 配額窗口輪詢 ping 觸發。
本 turn 能發生 = 配額已重置（落地即確認；本 call 是 roll 後首用，錨定下輪邊界 = 現在 + 5h）。
執行協議（嚴格——per-call 計費，3 個 request call 內完成）：
1. CronList：找出 title 含「usage-ping」且非 active 的殘留排程，逐一 CronDelete（防 20 名額塞滿；刪除失敗不重試）
2. 同批並行兩個工具：say -v Meijia -r 180 "配額回來了"；CronCreate（delayMinutes=301、recurring=false、title「usage-ping 鏈 ping」、prompt=本訊息「🔴 usage-ping 鏈落地」起全文原文照抄、一字不改）
3. 回一行：「🔴 usage-ping 鏈落地 — 配額已重置，下一發 +5h01m」
禁止其他工具與其他操作；不查狀態、不接任務。
```

## 執行約束

- **host 開啟前提**（同 /at）：排程由 host 在觸發時刻 dispatch——Claude Code 是 terminal session、ZCode 是 app；關閉期間到點不觸發（ZCode 記「跳過」不補跑），需要就把 host 開到觸發時刻
- **失敗消耗假設**（一次性）：fire 失敗（配額仍死）也消耗該 one-shot（兩端文檔皆未記載 retry，保守假設）→ 靠多 rungs 有界取樣，不依賴單發重試（ZCode 僅 1 rung，miss 即無重試——見 Phase 3 session 綁定限制）；網格 recurring 恆存續（miss 週期 = 0 call）；鏈模式 one-shot miss = 鏈死（見鏈模式「失效模式」）
- **sentinel 時窗語義**：Stop hook 只在 [T, T+90min)（上界排除——恰 T+90min 走逾時自清）內有 turn 結束才 say——配額死 = 無 turn = 無誤報；逾時靜默自清（階梯早已耗盡，估計過期）。時窗 90min = hook `PING_STALE=5400`（sync 副本：hooks/stop-notification.sh、本檔、voice-notification——改階梯幾何三處同改）
- **生命週期**（同 /at）：Claude Code 綁 session，session 結束排程消失；ZCode workspace 持久——殘留 completed 記錄佔 20 條名額，下次 supersede 清
- **語音**：遵循 [voice-notification](../voice-notification/SKILL.md) 規範（排程確認即時 say；落地召回走 Stop hook sentinel 機制，非 LLM say——**週期模式例外**：landing 直接 say，理由見該段「成本」）

## 使用範例

```bash
# 估計 14:30 reset → 一律 +1 分鐘 → rungs 14:31 / 14:46 / 15:01
/usage-ping 14:30

# 固定時刻制（每天 02/07/12/17/22 的 ~:41 reset）→ recurring cron 42 2-23/5 * * *（每天五發，各 +1 分 margin）
/usage-ping every 5h from 17:41

# 滾動窗口制（GLM 5h 從首用起算、邊界漂移）→ 自排程鏈，每輪 landing+5h01m、零漂移
/usage-ping every 5h rolling
```
