---
name: upgrade-sj

description: "升級 Shioaji 版本，含 breaking changes 影響掃描與 SJ API 驗證"
when_to_use: "升級 Shioaji 時使用。必須在收盤後執行（需跑 SJ external API 測試）。觸發詞：升級 SJ、update shioaji、SJ 升級、永豐升級。"
argument-hint: "預設升級到最新 release，可指定版本如 1.5.3"
allowed-tools: ["Bash", "Read", "Edit", "Grep", "WebSearch"]
---

# Upgrade SJ — Shioaji 升級流程

Shioaji 升級指揮官。版本差距分析、掃描分級、雙 worktree 升級、DEPTH 驗證、commit、語音通知的**流程骨架見 [upgrade-flow.md](../_common/upgrade-flow.md)**（佔位符代入：`<REPO>`=Sinotrade/Shioaji、`<PACKAGE>`=shioaji、`<SPEC>`=shioaji[speed]、`<NAME>`=SJ）；本檔只承載 SJ 專屬內容。

SJ 佔位符代入值：

- `<IMPORT_CHECK>`：`from mosaic_alpha.adapters.sj.units import sj_vol_to_internal; print('SJ import OK')`
- pyproject 格式：`"shioaji[speed]>=<TARGET_VERSION>"`（帶 extras）

## SJ 專屬掃描項目（Phase: 影響掃描）

Shioaji release notes 通常較簡短（非結構化 changelog），需逐條判斷影響。

| 掃描項目 | 搜尋指令 | 關注對象 |
|---------|---------|---------|
| SJ API callback | `rg "callback\|on_event\|tick_handler\|bidask_handler" mosaic_alpha/adapters/sj/ --type py` | tick/bidask callback 簽名變更 |
| SJ 連線/登入 | `rg "login\|connect\|api\." mosaic_alpha/adapters/sj/ --type py` | 登入流程、session 管理 |
| SJ 下單 | `rg "Order\|order\|submit\|place_order" mosaic_alpha/adapters/sj/ --type py` | 訂單類型、參數變更 |
| SJ KBars/歷史 | `rg "kbars\|ticks\|snapshot\|candles" mosaic_alpha/ --type py` | 歷史資料 API 變更 |
| SJ Stream | `rg "stream\|subscribe\|quote" mosaic_alpha/adapters/sj/ --type py` | 即時串流訂閱變更 |
| Volume 單位 | `rg "volume\|lot\|share\|SJ_SHARES_MULTIPLIER" mosaic_alpha/ --type py` | 張/股單位變更（台股鐵律） |
| SJ 錯誤碼 | `rg "error\|fail\|reject\|status_code" mosaic_alpha/adapters/sj/ --type py` | 錯誤處理邏輯 |
| Feed 聚合 | `rg "feed\|aggregat\|tick_feed\|run_tick_feed" mosaic_alpha/ --type py` | Feed process 對 SJ tick 的依賴 |

**特別注意的 SJ 風險區域**：

| 風險區域 | 位置 | 說明 |
|---------|------|------|
| Volume 單位慣例 | `adapters/sj/units.py` | SJ API 回報張，NT 內部用股，×1000 轉換 |
| Execution adapter | `adapters/sj/execution.py` | 下單/回報/倉位同步 |
| Data fetcher | `adapters/sj/` 各 fetcher | KBars/Ticks/Snapshot API |
| Feed process | `scripts/live_trading/run_tick_feed.py` | 即時 tick 聚合 |
| Session capture | `strategies/` session export | Paper/Live session 持久化 |

## SJ 專屬：查證 API 行為（掃描後、升級前）

若 release notes 提及 API 行為變更（callback、stream、order），使用 **Shioaji Skill**（`shioaji:shioaji`）查證實際行為，不憑記憶猜測。

## 輸出報告

依 [upgrade-flow.md](../_common/upgrade-flow.md) 骨架，抬頭「SJ 升級報告」；另加「Release Notes 分析」表（fix/feat 條目 × 影響分級）。SJ 外部 API 測試是升級的**關鍵驗證**——Shioaji 是台股唯一的交易閘道，任何 API 行為變更都可能在這裡暴露。

## 約束

共用約束見 upgrade-flow。SJ 額外：

- **Volume 單位鐵律**：升級後必須驗證張/股轉換邏輯（`adapters/sj/units.py`）未受影響
- **Shioaji Skill 優先**：API 行為有疑問時用 `shioaji:shioaji` skill 查證，不憑記憶
