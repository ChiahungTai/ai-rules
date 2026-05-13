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

> **必須使用 `python -u`**：背景執行時 Python stdout 會 buffer，`[ACTION]` 不會即時 flush。不加 `-u` 的話 Monitor 完全捕捉不到事件。

```bash
uv run python -u examples/rule_forge/demo_backbone_trajectory_viewer.py
```

在背景執行（`run_in_background: true`），用 `until grep` 等待 UI 就緒：

```bash
until grep -q "\[OK\] load_data" <背景任務output路徑> 2>/dev/null; do sleep 1; done && echo "UI Ready"
```

看到 `[OK] load_data` 後進入 Phase 2。

**重啟時**：先用 `TaskStop` 停掉舊的背景任務和 Monitor，再重新啟動。

## Phase 2：監控操作日誌

使用 Monitor 監控 stdout 的 `[ACTION]` 行：

- **監控目標**：`[ACTION]` 標籤
- **每條 [ACTION] 包含**：序號、操作名稱、摘要
- **互動原則**：使用者提問時，先讀 action log 了解上下文

Monitor 指令（過濾 ACTION + 錯誤輸出）：

```bash
tail -f <背景任務output路徑> | grep --line-buffered "\[ACTION\]\|\[FAIL\]\|\[WARN\]"
```

`<背景任務output路徑>` 是 Phase 1 `run_in_background` 回傳的 output file path。

## Phase 3：讀取 Swing 分析

收到 `[LOG] ai-analysis/llm-analysis/{stock}/swings/{swing_id}_{start}_{end}/swing.md` 後，
主動讀取該檔案。swing.md 包含完整的結構分析、KC 標記、軌跡、Setup 定義等。

需要更多上下文時，透過 `[LOG] rg 'ui_action.*seq=N' {log_path}` 查詢 Logger。

## Phase 4：理解操作上下文

### 操作對照表

| [ACTION] 名稱 | 觸發時機 | LLM 應理解的上下文 | 伴隨輸出 |
|---------------|---------|-------------------|---------|
| `select_swing` | 選取 swing | 使用者正在分析哪個 swing | `[LOG]` swing.md 路徑 → 讀取分析 |
| `change_threshold` | 調整閾值 | 使用者在篩選感興趣的 swing 範圍 | — |
| `select_wave` | 選取 wave node | 使用者正在檢視哪個波段的結構 | — |
| `switch_instrument` | 切換股票 | 使用者轉移注意力到新標的 | — |
| `toggle_condition` | 勾選/取消指標 | 使用者關注哪些技術指標 | — |
| `generate` | 點擊 Generate | 使用者觸發重新分析 | — |
| `rebuild_ui` | UI 重建完成 | 數據載入完成，可互動 | — |

## Phase 5：討論記錄

討論結束後（使用者明確結束或 session 結束前），將結論寫入專案根目錄下：

```
llm-discussions/{stock}/YYYY-MM-DD_{script-name}_{topic-slug}.md
```

- `{stock}`: 至少一層 instrument 目錄
- `{script-name}`: 執行的 demo 腳本名稱（如 `trajectory-viewer`）
- `{topic-slug}`: 討論主題
- 同一天多次討論可用日期序號: `YYYY-MM-DD_01_topic.md`

## 協作模式

- **觀察**：透過 [ACTION] 日誌理解使用者正在做什麼
- **讀取**：收到 `[LOG]` 路徑後主動讀取分析檔案，不等使用者提示
- **等待**：使用者提問時再回應，不主動打擾
- **上下文感知**：回答前先讀 action log + swing.md，確保理解使用者當前關注的 swing/wave/指標
- **記錄**：討論結束後寫入 `llm-discussions/`
