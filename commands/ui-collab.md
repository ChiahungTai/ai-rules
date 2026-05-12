---
description: "UI-LLM 協作模式 — 啟動 UI 並監控操作日誌"
when_to_use: "Launch the Backbone Trajectory Viewer UI and monitor [ACTION] logs so the LLM can understand user UI interactions in real time."
usage: "/ui-collab"
argument-hint: "無參數"
allowed-tools: ["Bash", "Read", "Monitor"]
---

# UI-LLM 協作模式

啟動 Backbone Trajectory Viewer 並監控 `[ACTION]` 操作日誌，讓 LLM 即時理解使用者 UI 操作上下文。

## Phase 1：啟動 UI

```bash
uv run python examples/rule_forge/demo_backbone_trajectory_viewer.py
```

在背景執行，等待 `[OK] load_data` 出現後進入 Phase 2。

## Phase 2：監控操作日誌

使用 Monitor 監控 stdout 的 `[ACTION]` 行：

- **監控目標**：`[ACTION]` 標籤
- **每條 [ACTION] 包含**：序號、操作名稱、摘要
- **互動原則**：使用者提問時，先讀 action log 了解上下文

Monitor 範例（過濾 ACTION + 錯誤輸出）：

```bash
tail -f /dev/stdout | grep --line-buffered "\[ACTION\]\|\[FAIL\]\|\[WARN\]"
```

## Phase 3：理解操作上下文

使用者提問時，透過 `[LOG] rg 'ui_action.*seq=N' {log_path}` 查詢完整上下文。

### 操作對照表

| [ACTION] 名稱 | 觸發時機 | LLM 應理解的上下文 |
|---------------|---------|-------------------|
| `select_swing` | 選取 swing | 使用者正在分析哪個 swing |
| `change_threshold` | 調整閾值 | 使用者在篩選感興趣的 swing 範圍 |
| `select_wave` | 選取 wave node | 使用者正在檢視哪個波段的結構 |
| `switch_instrument` | 切換股票 | 使用者轉移注意力到新標的 |
| `toggle_condition` | 勾選/取消指標 | 使用者關注哪些技術指標 |
| `generate` | 點擊 Generate | 使用者觸發重新分析 |
| `rebuild_ui` | UI 重建完成 | 數據載入完成，可互動 |

## 協作模式

- **觀察**：透過 [ACTION] 日誌理解使用者正在做什麼
- **等待**：使用者提問時再回應，不主動打擾
- **上下文感知**：回答前先讀 action log，確保理解使用者當前關注的 swing/wave/指標
