---
name: maintain
description: >
  Core daily maintenance procedure consumed by /daily-maintain (auto) and /project-review (interactive).
  4-phase flow, findings risk matrix, auto-fix procedures, kanban hygiene.
when_to_use: >
  Do not invoke directly. Use /daily-maintain for autonomous cron mode
  or /project-review for interactive human mode.
---

# maintain Skill — 核心維護程序

被 `/daily-maintain`（自動）和 `/project-review`（互動）共用的核心程序。

---

## 四階段流程

```
Phase 1: Snapshot               Phase 2: CLAUDE.md Sync     Phase 3: Doc Health           Phase 4: Report
─────────────────               ──────────────────────      ──────────────────────        ──────────────
scan_project.py                 /claude:sync                 /doc-health                    彙總報告
→ dep_graph / findings / fp     LLM 直接讀 CLAUDE.md        呈現 findings                  跨 phase 關聯
diff fingerprint                用 dep_graph 驗證 imports   LLM 直接讀 .kanban/            趨勢追蹤
更新 dep-graph.md               品質檢查                    品質檢查 + kanban hygiene
```

### Phase 1: 統一知識快照

**步驟 1.1：執行統一掃描**

```bash
cd <project-root>
uv run python /Users/ctai/Github/ai-rules/skills/scan-project/scripts/scan_project.py --project-root . --output .project-snapshot.json
```

產出 JSON v5（dep_graph / findings / fingerprint），不含 registry。

**步驟 1.2：偵測變化**

- `--init` 模式：跳過 diff
- 維護模式：比較新舊 JSON 的 fingerprint、findings、dep_graph
- 沒變 → 跳過。有變 → 列出具體變更

**步驟 1.3：更新 dependency-graph.md**

根據 dep_graph 資料更新 Mermaid graph、Direct Dependencies、Hotspots、Ripple Impact Rules。
Mermaid 暗色主題：所有 ````mermaid` 區塊第一行加 `%%{init: {'theme': 'dark'}}%%`。

**步驟 1.4：Commit snapshot**

`.project-snapshot.json` 隨程式碼一起 commit，作為下次 diff 基準。

### Phase 2: CLAUDE.md 同步

執行 `/claude:sync --changed-since yesterday --recursive`。

Snapshot 輔助：
- `dep_graph` → 精確 import 依賴鏈
- `findings` → 預計算 X6 等問題

無 snapshot 時降級為獨立模式。

### Phase 3: 文件健康 + Kanban 維護

執行 `/doc-health` 呈現 findings + 品質檢查。

額外執行 **Kanban 維護**（見下方「Kanban 維護程序」）。

### Phase 4: 統一健康報告

彙總三個 phase 結果：

1. **各 Phase 摘要**：通過/警告/失敗統計
2. **跨 Phase 關聯**：
   - Phase 1 import 變化 ↔ Phase 2 CLAUDE.md 問題
   - Phase 1 findings ↔ Phase 3 doc-health 問題
3. **趨勢追蹤**：fingerprint 數量變化、findings 增減

---

## Findings 風險分級矩陣

| check_id | 風險 | 自動模式 | 互動模式 | 修正程序 |
|----------|------|---------|---------|---------|
| X-cap-path | 🟢 Low | 自動修正 | 呈現待確認 | 見下方 |
| X-tag-module | 🟢 Low | 自動修正 | 呈現待確認 | 見下方 |
| X-cap-dup | 🟡 Medium | 只報告 | 呈現待確認 | 需人類判斷歸屬 |
| X-ep-ready | 🟡 Medium | 只報告 | 呈現待確認 | EP 可能未建立 |
| X6 | 🟡 Medium | 只報告 | 呈現待確認 | 需人類決定是否建 CLAUDE.md |

**分級原則**：修正結果可機械驗證（路徑存在、tag 對應目錄）→ 🟢。需語義判斷 → 🟡。

---

## 自動修正程序

### X-cap-path 修正（三層策略）

**第一層：同目錄搜尋**（直接比對）

1. Read 目標 CLAUDE.md，找到含該路徑的 Capabilities 行
2. 在模組目錄下搜尋正確檔名：`fd <basename> <module_dir>/`
3. 單一候選 + class/function 名吻合 → 🟢 更新路徑
4. 多候選或無候選 → 進入第二層

**第二層：git 歷史推導**（改名/搬遷偵測）

1. `git log --oneline --all -- "<original_path>"` 查詢檔案歷史
2. 找到最近一次涉及該檔案的 commit → 檢查 commit message（rename? move? refactor?）
3. 從 commit 推導新位置：
   - 改名（如 `capital_allocation.py → capital.py`）→ 確認新檔案存在 + class 名吻合 → 🟢 更新路徑
   - 搬遷（如 `runner.py → verification/runner.py`）→ 確認新路徑存在 → 🟢 更新路徑
   - 拆分（功能分散到多個檔案）→ 🟡 標記待人工確認
   - 刪除（功能已移除）→ 🟡 標記待人工確認
4. `rg "^class <ClassName>" <new_file>` 驗證 class 仍然存在

**第三層：標記待人工確認**

找不到候選、git 歷史顯示功能已拆分/刪除、或歧義無法解決 → 🟡 報告不修正

**判斷信心等級**：

| 證據 | 信心 | 動作 |
|------|------|------|
| 同目錄找到同名（改副檔名/加後綴）+ class 吻合 | 🟢 高 | 自動修正 |
| git 顯示改名/搬遷 + 新路徑 class 吻合 | 🟢 高 | 自動修正 |
| git 顯示改名 + 新路徑 class 不吻合 | 🟡 中 | 標記待確認 |
| git 顯示功能拆分為多檔 | 🟡 中 | 標記待確認 |
| git 無歷史（從未 commit） | 🟡 中 | 幽靈路徑，標記待確認 |

### X-tag-module 修正

1. Read 卡片檔案，找到第一行的 `[tag:xxx]`
2. 從 scan_project.py 的 valid_tags 或 `fd . mosaic_alpha/ --max-depth 1 --type d` 取得合法 tag 清單
3. 比對卡片內容中的模組引用，推導正確 tag
4. 確定性高（卡片引用單一模組）→ 更新 tag
5. 確定性低（多模組引用或模糊）→ 標記待人工確認

---

## Kanban 維護程序

Phase 3 額外執行的 kanban hygiene 檢查：

### 偵測項目

| 檢查 | 條件 | 嚴重度 | 自動修正 |
|------|------|--------|---------|
| Stale card | Next-Up > 7 天、In-Progress > 14 天無修改 | 🟡 | 不修正（只報告） |
| Done/ 歸檔 | Done/ 卡片 > 14 天 | 🟢 | auto: 移至歸檔或刪除 |
| Lane 限額 | Backlog > 100 張 | 🟡 | 不修正（只報告） |
| 無 tag 卡片 | 卡片第一行無 `[tag:xxx]` | 🟢 | auto: 從內容推導 tag（同 X-tag-module 修正邏輯） |

### 無 tag 卡片推導

1. 讀取卡片內容，搜尋模組引用（程式碼路徑、UC ID prefix、模組名）
2. 對照 `mosaic_alpha/` 子目錄清單
3. 單一匹配 → 加上 `[tag:xxx]` 到第一行
4. 多重匹配或模糊 → 標記待人工確認

### Done/ 歸檔

Done/ 超過 14 天的卡片：
- 自動模式：直接刪除（已完成的任務，資訊已在 Capabilities 表格）
- 互動模式：列出待確認

---

## 決策點預設值

自動模式不詢問，使用以下預設值：

| 決策點 | 自動預設 | 說明 |
|--------|---------|------|
| X-cap-path 修正 | 自動修 | 🟢 low risk |
| X-tag-module 修正 | 自動修 | 🟢 low risk |
| 無 tag 卡片 | 推導後自動加 | 🟢 low risk |
| Done/ 歸檔 | > 14 天自動刪 | 🟢 low risk |
| X-cap-dup / X-ep-ready / X6 | 只報告 | 🟡 需語義判斷 |
| /claude:sync --changed-since | `yesterday` | 每日增量 |
| /doc-health 參數 | 預設（不含 --quality --all） | 核心 findings 即可 |
| SYSTEM-MAP 同步 | 不執行 | 需人類確認狀態語義 |

---

## 報告格式

### 無變化

```
## Daily Maintenance Report

### Phase 1: Snapshot
✅ 無變化（fingerprint 與上次一致）
   - dep_graph: N modules, findings: N, capabilities: N, kanban: N

### Phase 2: CLAUDE.md Sync
✅ 無問題（檢查 N 個檔案）

### Phase 3: Doc Health + Kanban
✅ 無問題（findings 全部已處理，kanban 健康）

### Phase 4: Health Report
✅ 整體健康，無跨 phase 關聯問題
```

### 有變化

```
## Daily Maintenance Report

### Phase 1: Snapshot
⚠️ 偵測到變更
- fingerprint: capabilities X→Y, kanban X→Y
- findings: X-cap-path 新增 N 筆, X-tag-module 解決 N 筆
- dep_graph: 新增 deps features → data
- 已更新: Mermaid graph, Direct Dependencies 表

### Phase 2: CLAUDE.md Sync
⚠️ 發現 N 個問題
- data/CLAUDE.md: 路徑 xxx 已更名 → [自動修正已完成]
- features/CLAUDE.md: 缺少導航 → 建議新增（🟡 未修正）

### Phase 3: Doc Health + Kanban
⚠️ findings: N issues (0 critical, N important)
- [X-cap-path] xxx 不存在 → [自動修正已完成]
- [X-tag-module] 卡片 'xxx' tag 錯誤 → [自動修正已完成]
- [X-cap-dup] UC ID xxx 重複 → 🟡 待人工確認
Kanban: Backlog N 張, Next-Up N 張, In-Progress N 張, Done N 張
  - Stale: Next-Up 'xxx' 已 8 天未更新
  - Done 歸檔: N 張 > 14 天已清理

### Phase 4: Health Report
- 跨 phase 關聯：Phase 1 新增依賴 ↔ Phase 2 CLAUDE.md 問題
- 未解決 🟡: N 筆（需人工確認）
- 趨勢: capabilities +N（健康），findings +N

### 下一步
- 🟡 待確認項目：列出
```

---

## Commit 規則

### 自動模式（/daily-maintain）

**自動 commit 範圍**：只有 🟢 自動修正的變更 + `.project-snapshot.json` 更新。

Commit message 格式：
```
chore(maintain): daily auto-maintain — X findings fixed, Y reported

Auto-fixed: X-cap-path(N), X-tag-module(N)
Reported: X-cap-dup(N), X6(N)
Snapshot: capabilities N, kanban N, findings N
```

**commit-consent 豁免**：調用 `/daily-maintain`（自動模式）即隱含同意 🟢 低風險修正的 commit。🟡 中風險不 commit。

### 互動模式（/project-review）

遵循 commit-consent 規則：展示 diff，等待用戶確認後 commit。

---

## 參數

| 參數 | 說明 |
|------|------|
| 無參數 | 依序執行 Phase 1 → 2 → 3 → 4 |
| `--init` | Phase 1 用初始生成模式（從零產出 dep-graph） |
| `--only dep-graph` | 只跑 Phase 1 |
| `--only sync` | 只跑 Phase 2 |
| `--only doc-health` | 只跑 Phase 3 |
