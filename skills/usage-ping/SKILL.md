---
name: usage-ping
description: "usage reset 探測叫醒 — 在估計的重置時間排 ping（one-shot 階梯：Claude Code 3 發；ZCode 單發——session 綁定限制），落地即確認配額回來；固定時刻制配額用網格模式 every Nh from HH:MM（recurring cron）。滾動窗口制（GLM 5 小時窗口類）無法自動輪詢——讀 provider UI 邊界重跑一次性，或無參數保底 now+301min（落地後重跑＝手動接力）。每個 trigger 最小 call 成本；只寫時間不帶任務（要接續工作用 /at）。觸發詞：叫醒、ping、配額重置、reset 探測、usage reset、5 小時窗口、滾動窗口"
when_to_use: "LLM provider usage reset 時間是估計值（一次性時刻或固定時刻週期）、只需要叫醒 LLM 確認配額（不接任務、最小 call 成本）時"
argument-hint: "HH:MM | every 5h from HH:MM"
allowed-tools: ["Bash", "CronCreate", "CronDelete", "CronList"]
---

# /usage-ping — usage reset 探測叫醒

在估計的 usage reset 時間排 **ping**，時間到叫醒 LLM——model call 能發生 = 配額已重置（落地即確認）。**只叫醒不接任務**。兩種模式：**一次性**（單一估計時刻 → 階梯 rungs，見「執行流程」）；**週期-網格**（固定時刻 reset → 單條 recurring cron）。滾動窗口制（如 GLM 5 小時窗口）無法自動輪詢（鏈模式已棄用，見該段）——實務為每次讀 provider UI 邊界重跑一次性。

> **與 `/at` 分工**：本命令只寫時間（叫醒＋確認配額）；時間後面要接「做什麼」（reset 後自動接續工作）用 [`/at`](../at/SKILL.md)；要把工作交給另一個 session/provider 用 [`/handoff`](../handoff/SKILL.md)。

## 核心語義：落地即確認 + 單 call 紀律

- reset 時間是**估計值**——估早的 ping 撞死配額 → turn 不發生（0 call）→ 下一 rung 15 分鐘後再試（有界重試）
- ping 觸發時 model turn 能發生 = 配額已重置：call 本身觸發/證明配額回來，**不需查詢 usage 狀態的機制**
- **單 call 紀律**（per-call 計費；一次性模式）：落地 rung 回一行文字、**零工具呼叫**——任何工具 round-trip 都是多一個 request，不划算；網格模式放寬（2 calls——landing 直接 say，理由見「週期模式」）
- 語音召回由 Stop hook 機械執行（ping sentinel，0 LLM call；見 [voice-notification](../voice-notification/SKILL.md)）
- **落地不做清理**：清理成本（CronList + CronDelete ≈ 2-3 calls）與讓後續 rung 空落地（各 1 call）相當，且零失敗模式。殘留有兩種、都由下次 `/usage-ping` 排程時 supersede（Phase 2 刪舊覆蓋）清掉：① 未 fire 的後續 rung（by design 空落地耗盡）；② ZCode one-shot 跑完的 completed/failed 記錄——**不自動刪且佔 20 條名額**（Claude Code one-shot 跑完自刪，無此殘留）。階梯成本上界 = rung 數（3 calls）

## 執行流程

### Phase 1：解析時間

| 輸入格式 | 解析方式 | 範例 |
|---------|---------|------|
| `HH:MM` | 今天指定時間；已過 → 明天 | `14:30` → 今天 14:30 |
| （無參數） | 滾動窗口保底：T = 現在 + 301 分鐘（用 `date` 換算絕對時刻後照 Phase 3；ZCode 可直接 `delayMinutes=301`）——本次對話本身即配額使用，證明錨點 ≤ 現在 → 邊界 ≤ 現在+5h < T，**任何時刻排都保證 ≥ 邊界+1min**；不加 +1、不走 jitter（301 已含 margin）。landing 即新窗口首用、錨定下輪邊界 = landing+5h → **落地後立即重跑本命令＝手動接力**（取代已棄用自排鏈；中途重跑會晚於邊界但仍正確） | 無 UI 邊界時的保底 / 語音後接力 |
| `every Nh from HH:MM` | 週期-網格模式——跳到下方「週期模式」段處理，不走本階梯流程 | `every 5h from 17:41` |

- **絕對時間 only**（同 /at 治理）：用戶給相對時間時，用 `date` 查當前時間換算成絕對時刻（跨日明確向用戶確認目標日期）
- **一律 +1 分鐘（僅 `HH:MM` 輸入）**：T = 輸入時間 + 1 分鐘（秒數誤差防護——輸入的 HH:MM 無秒數，實際 reset 若在 HH:MM:00 邊界，不延後會在重置完成前偷跑，浪費 rung；無參數保底不適用——301 已含 margin）
- **jitter 規則（僅 `HH:MM` 輸入）**：T（+1 後）落在 `:00`/`:30` → 再 +1 分鐘——Claude Code one-shot 在整點/半點最多**提前 90 秒** fire，reset 前偷跑 = 偽陰性
- 計算 3 個 rung 時刻：T、T+15m、T+30m，用 `date` 換算（macOS `-v` 可疊加：`date -v+1M -v+15M`），跨日跨月交給 date 處理，**不手算**
- 用戶在時間後面寫了任務 → 提示「usage-ping 不帶任務；要 reset 後接續工作改用 /at」

### Phase 2：supersede + 名額檢查

1. `CronList` → title/prompt 含 `usage-ping` 的既有排程 → `CronDelete` 全部（**CronCreate 無同名自動覆蓋——不刪舊，舊 rung 會照樣 fire**；completed/failed 殘留記錄一併清——ZCode 這些也佔名額），回報取代了什麼
2. **名額**：ZCode automation 全專案上限 20 條（completed/failed/skipped 都佔位）；清理後餘量 <3 → 降級 rung 數（2 或 1）並在摘要明說

### Phase 3：建階梯 + 召回 sentinel（獨立呼叫同批並行）

以下獨立動作**同一批並行發出**（tool-discipline：批次化省 request）：

1. `CronCreate` × 3——每發 `recurring: false`、pinned cron（`分 時 日 月 *`）、prompt 用下方模板（prompt 首行自帶 `usage-ping` marker，兩端 supersede 匹配都靠它）；title `usage-ping {rung_i 實際時刻} 叫醒 rung {i}/3`（ZCode 必填；Claude Code 端工具無 title 參數則省略。**標實際觸發時刻（+1 分後的 T），非輸入時間**——標輸入值會讓人誤以為沒 +1）
   - **ZCode session 綁定限制（pending 期間鎖定）**：session 建立首個 automation 後、該 task **未 fire 前**，同 session 後續 `CronCreate` 全拒（錯誤訊息要求「start a new chat」；並行批次與單發重試皆同，2026-08-18 實測）。2026-09-01/09-02 實測推翻「fire 後釋放」舊模型——**pending 或 completed 記錄在場皆鎖，刪除該 session 相關 automation 記錄才釋放**（fire 本身不釋放）。ZCode 實務不變：建 rung 1 即止（rung 2/3 建立時 rung 1 仍 pending → 拒），降級 1-rung 階梯、摘要明說，錯過 T 的召回改由 sentinel 語音承擔；Claude Code 端無此限制（×3 同批照建）
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

> 適用**固定時刻制**（每天同樣牆上時刻 reset、秒級抖動）：網格模式 `every 5h from HH:MM`。**滾動窗口制**（窗口從首用起算、邊界漂移，如 GLM 5 小時窗口）不適用任何自動排程——見下方「鏈模式已棄用」段，實務為讀 UI 邊界重跑一次性。

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

### 鏈模式（滾動窗口）——已棄用（2026-08-20 實測災難，真實案例）

曾設計：landing turn 自排下一發（delayMinutes=301，landing call 即新窗口錨點、每輪重錨零漂移）。實測**首發落地即退化迴圈**：冷 context 下 landing LLM 重複呼叫第一個工具（CronList）約 50 次、從未進入下一步——每輪 context 累積放大、快速燒盡 usage，鏈斷（成功率 0/1）。

**教訓（設計約束）**：
- **冷 context trigger 禁多步工具工作流**——cron dispatch 無對話歷史錨定，LLM 對「下一步」確定性下降，陷入「重複首工具」退化吸引子；一次性 landing「零工具、一行回覆」實測可靠（02:41、17:43 兩次 ✓）
- 退化模式是**重複首工具**——若協議首工具是 CronCreate，迴圈會指數級複製排程（每個複製品再自排），災害遠大於重複讀取。**不可用「重排步驟順序」修**
- prompt 內呼叫上限指令（「3 個 request call 內完成」）擋不住退化——退化時指令被忽略
- 機械斷路器（hook 擋重複呼叫）理論可行但只能限損不能救鏈——landing 沒建出下一發，鏈照樣死

**滾動窗口實務**：讀 provider UI 的下次 reset 時刻 → `/usage-ping HH:MM`（一次性、零工具 landing）；每次邊界重跑一次。僅單一 trivial 工具的 landing（如網格的固定 say 指令）屬可接受邊界，未實測。

## 執行約束

- **host 開啟前提**（同 /at）：排程由 host 在觸發時刻 dispatch——Claude Code 是 terminal session、ZCode 是 app；關閉期間到點不觸發（ZCode 記「跳過」不補跑），需要就把 host 開到觸發時刻
- **失敗消耗假設**（一次性）：fire 失敗（配額仍死）也消耗該 one-shot（兩端文檔皆未記載 retry，保守假設）→ 靠多 rungs 有界取樣，不依賴單發重試（ZCode 僅 1 rung，miss 即無重試——見 Phase 3 session 綁定限制）；網格 recurring 恆存續（miss 週期 = 0 call）
- **sentinel 時窗語義**：Stop hook 只在 [T, T+90min)（上界排除——恰 T+90min 走逾時自清）內有 turn 結束才 say——配額死 = 無 turn = 無誤報；逾時靜默自清（階梯早已耗盡，估計過期）。時窗 90min = hook `PING_STALE=5400`（sync 副本：hooks/stop-notification.sh、本檔、voice-notification——改階梯幾何三處同改）
- **生命週期**（同 /at）：Claude Code 綁 session，session 結束排程消失；ZCode workspace 持久——殘留 completed 記錄佔 20 條名額，下次 supersede 清
- **語音**：遵循 [voice-notification](../voice-notification/SKILL.md) 規範（排程確認即時 say；落地召回走 Stop hook sentinel 機制，非 LLM say——**週期模式例外**：landing 直接 say，理由見該段「成本」）

## 使用範例

```bash
# 估計 14:30 reset → 一律 +1 分鐘 → rungs 14:31 / 14:46 / 15:01
/usage-ping 14:30

# 固定時刻制（每天 02/07/12/17/22 的 ~:41 reset）→ recurring cron 42 2-23/5 * * *（每天五發，各 +1 分 margin）
/usage-ping every 5h from 17:41

# 滾動窗口制（GLM 5h）→ 無法自動輪詢（鏈已棄用）——讀 UI 下次 reset 時刻，每次邊界重跑一次性
/usage-ping 01:02

# 無參數保底（滾動窗口、無 UI 數字）→ T = now+301min；聽到語音後再跑一次＝手動接力下一輪
/usage-ping
```
