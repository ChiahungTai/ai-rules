---
description: "升級 Shioaji 版本，含 breaking changes 影響掃描與 SJ API 驗證"
when_to_use: "升級 Shioaji 時使用。必須在收盤後執行（需跑 SJ external API 測試）。觸發詞：升級 SJ、update shioaji、SJ 升級、永豐升級。"
usage: "/upgrade-sj [目標版本]"
argument-hint: "預設升級到最新 release，可指定版本如 1.5.3"
allowed-tools: ["Bash", "Read", "Edit", "Grep", "WebSearch"]
---

# Upgrade SJ — Shioaji 升級流程

Shioaji 升級指揮官。負責版本差距分析、breaking changes 影響掃描、SJ API 完整驗證。

## 🔴 前置條件

**必須在收盤後執行**（15:30 以後）。原因：
1. 升級後需跑 `tests/external_api/sj/` 完整外部 API 測試
2. 盤中執行會消耗 SJ quota（每日重置 ~08:00）
3. 避免 SDK 變更影響即時交易連線

## 🚀 執行流程

### Phase 1: 版本差距分析

1. **取得當前版本**：
   ```bash
   uv run python -c "import shioaji; print(shioaji.__version__)"
   ```

2. **取得最新 release**：
   ```bash
   gh api repos/Sinotrade/Shioaji/releases/latest --jq '.tag_name, .published_at'
   ```
   如指定版本：
   ```bash
   gh api repos/Sinotrade/Shioaji/releases/tags/v<VERSION> --jq '.tag_name, .published_at'
   ```

3. **取得 release notes**：
   ```bash
   gh api repos/Sinotrade/Shioaji/releases/tags/v<VERSION> --jq '.body'
   ```

4. **產出版本差距報告**（表格格式）：
   - 當前版本 → 目標版本
   - 中間跳過的版本數（Shioaji 發布頻率較低，注意 1.2.x → 1.5.x 可能有大跳躍）
   - fix / feat / breaking 條目分類

### Phase 2: Breaking Changes 影響掃描

Shioaji release notes 通常較簡短（非結構化 changelog），需逐條判斷影響。先用 LSP `workspaceSymbol` 搜尋 release notes 提到的 API 名稱，確認專案是否使用。再用 rg 做完整的文字搜尋。掃描項目：

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

**掃描結果分級**：

| 分級 | 定義 | 行動 |
|------|------|------|
| 🔴 直接命中 | 專案程式碼使用了被變更的 SJ API | 必須修改後才能升級 |
| 🟡 間接影響 | SJ 行為改變（如 callback deadlock 修復） | 需評估，可能需調整 |
| 🟢 無影響 | 專案未使用受影響的 API | 可安全升級 |

### Phase 3: 查證 SJ API 行為（如需）

若 release notes 提及 API 行為變更（callback、stream、order），使用 **Shioaji Skill**（`shioaji:shioaji`）查證實際行為，不憑記憶猜測。

### Phase 4: 執行升級

1. **更新 `pyproject.toml` 下限**（兩個 worktree 都要更新）：
   - `mosaic_alpha_offline_backtesting/pyproject.toml`
   - `mosaic_alpha/pyproject.toml`
   - 格式：`"shioaji[speed]>=<TARGET_VERSION>"`

2. **驗證 TOML 合法**：
   ```bash
   uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
   ```

3. **同步兩個 worktree 的依賴**：
   ```bash
   uv sync
   ```
   在兩個 worktree 都要執行。

4. **確認兩邊版本一致**：
   ```bash
   uv run python -c "import shioaji; print(shioaji.__version__)"
   ```

### Phase 5: 驗證（漸進式）

遵循專案的漸進式驗證策略（DEPTH-MIN → DEPTH-SAMPLE → DEPTH-FULL）：

**DEPTH-MIN（秒級）**：
```bash
uv run python -c "import shioaji; print(shioaji.__version__)"
uv run python -c "from mosaic_alpha.adapters.sj.units import sj_vol_to_internal; print('SJ import OK')"
```

**DEPTH-SAMPLE（分鐘級）**：
```bash
uv run pytest tests/ -x -q --timeout=60 -k "not external_api"
```

**DEPTH-FULL（完整驗證，收盤後執行）**：
```bash
uv run pytest tests/external_api/sj/ -x -q
```

SJ 外部 API 測試是升級的**關鍵驗證**。Shioaji 是台股唯一的交易閘道，任何 API 行為變更都可能在這裡暴露。

### Phase 6: Commit

提交 `pyproject.toml` 變更，commit message 格式：

```
chore(deps): upgrade shioaji[speed] >=X.Y.Z

- Breaking changes impact scan: [結果摘要]
- Internal tests: [PASS/FAIL]
- External API tests (SJ): [PASS/PENDING]
```

## 📋 輸出格式

```
## SJ 升級報告

**版本變更**: 當前 → 目標
**升級風險**: 🟢 低 / 🟡 中 / 🔴 高

### Release Notes 分析
| 類型 | 條目 | 影響 |
|------|------|------|
| fix | ... | 🟢/🟡/🔴 |
| feat | ... | 🟢/🟡/🔴 |

### Breaking Changes 影響掃描
| 掃描項目 | 命中 | 分級 | 說明 |
|---------|------|------|------|

### 驗證結果
| 階段 | 結果 |
|------|------|
| DEPTH-MIN | ✅/❌ |
| DEPTH-SAMPLE | ✅/❌/⏳ 待收盤 |
| DEPTH-FULL (SJ external) | ⏳ 待收盤 / ✅/❌ |

### 跨 Worktree 一致性
| Worktree | 版本 |
|----------|------|
```

## 🔧 約束

- **收盤後才能跑完整驗證**：SJ external API 測試需收盤後（15:30+），避免消耗交易時段 quota
- **兩個 worktree 都要更新**：`mosaic_alpha/` 和 `mosaic_alpha_offline_backtesting/`
- **Volume 單位鐵律**：升級後必須驗證張/股轉換邏輯（`adapters/sj/units.py`）未受影響
- **Shioaji Skill 優先**：API 行為有疑問時，使用 `shioaji:shioaji` skill 查證，不憑記憶
- **pyproject.toml 下限反映實際最低相容版本**

---

## 語音通知

遵循 [voice-notification skill](../skills/voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始升級 SJ"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「SJ 升級完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```
