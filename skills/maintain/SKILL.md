---
name: maintain
description: >
  Core daily maintenance procedure consumed by /daily-maintain.
  4-phase flow, findings risk matrix, auto-fix procedures, kanban hygiene.
when_to_use: >
  Do not invoke directly. Use /daily-maintain.
---

# maintain Skill — 核心維護程序

`/daily-maintain` 的核心程序。

---

## 四階段流程

```
Phase 1: Graph Freshness        Phase 2: Instruction Sync     Phase 3: Doc Health           Phase 4: Report
──────────────────              ──────────────────────      ──────────────────────        ──────────────
code-reality build（opt-in）    /instruction-sync                 /doc-health                    彙總報告
無 index 的 repo skip           LLM 直接讀 instruction 檔        呈現 findings                  跨 phase 關聯
                                品質檢查                    品質檢查 + kanban hygiene       趨勢追蹤
```

### Phase 1: 結構圖新鮮度（code-reality，opt-in）

**步驟 1.1：判斷 opt-in**

project root 有 `.code-reality.toml`（profile）或 `.code-reality/`（sidecar）任一 → opt-in；兩者皆無 → Phase 1 skip（一行帶過，不報錯）。此處偵測的是 **repo 數據面 opt-in**（toml／sidecar 在場）；binary 存在性偵測是另一件事（單一真相源見 [code-reality](../code-reality/SKILL.md) 存在性偵測）。

**步驟 1.2：重建 graph**

```bash
code-reality build --repo <project-root>
```

binary 不存在或 build 失敗 → 記 `[WARN]` 後續行 Phase 2——graph 新鮮度是 nightly prefetch，查詢時 stale WARN 驅動的 lazy rebuild 是兜底（見 [cr-query](../cr-query/SKILL.md)）。

> snapshot 快照鏈（scan_project.py 產出 `.project-snapshot.json` + diff fingerprint + 自動更新 `dependency-graph.md` + commit snapshot）已退役：機械依賴/ripple 查詢由 code-reality graph 承擔（`callers`／`hub_nodes`／`impact_radius`，見 [cr-query](../cr-query/SKILL.md)）；人工策展（Ripple 語義表、分層敘事）由 per-repo 文檔承擔（`dependency-graph.md` opt-in 人工維護，或 `architecture.md`——若該 repo 以此慣例存放 ripple 語義表）。[scan-project](../scan-project/SKILL.md) 保留為 on-demand 機械盤點／findings 工具。

### Phase 2: Instruction 同步

執行 `/instruction-sync --changed-since yesterday --recursive`。（snapshot 的條件式輔助——退役過渡期 `.project-snapshot.json` 仍存在時——由該 skill 自述，此處不重複。）

### Phase 3: 文件健康 + Kanban 維護

執行 `/doc-health` 呈現 findings + 品質檢查。

額外執行 **Kanban 維護**（見下方「Kanban 維護程序」）。

### Phase 4: 統一健康報告

彙總三個 phase 結果：

1. **各 Phase 摘要**：通過/警告/失敗統計
2. **跨 Phase 關聯**：Phase 2 Instruction 問題 ↔ Phase 3 doc-health findings 同根因關聯
3. **趨勢追蹤**：doc-health findings 增減、kanban 卡片流動
4. **寫晨報檔**：若 `<project-root>/ai-analysis/daily-report/` 目錄存在，把報告寫入 `ai-analysis/daily-report/YYYY-MM-DD.md`（**同日 merge 非覆蓋**——重寫 top title + intro + 🔥/✅/📈 owned section，保留其他 op append 的外來 section；格式 + merge 規則見下方「晨報檔格式」）。目錄不存在則 skip——這是跨專案 opt-in guard，避免影響沒有晨報慣例的專案。**無待決項時仍寫檔**（內容標「✅ 無待決項」），以證明排程有跑。

---

## Findings 風險分級矩陣

> X-\* 機械 findings 由 `/scan-project`（on-demand）產出的 `.project-snapshot.json` 供應——夜間鏈已不產 snapshot（Phase 1 退役），無 snapshot 時 doc-health 降級純 LLM、X-\* 缺席屬預期；需要機械 findings 時手動補跑 `/scan-project`。

| check_id | 風險 | 自動模式 | 修正程序 |
|----------|------|---------|---------|
| X-cap-path | 🟢 Low | 自動修正 | 見下方 |
| X-ep-ready | 🟡 Medium | 只報告 | EP 可能未建立 |
| X6 | 🟡 Medium | 只報告 | 需人類決定是否建 instruction 檔 |

**分級原則**：修正結果可機械驗證（路徑存在、tag 對應目錄）→ 🟢。需語義判斷 → 🟡。

---

## 自動修正程序

### X-cap-path 修正（三層策略）

**第一層：同目錄搜尋**（直接比對）

1. Read 目標 instruction 檔（AGENTS.md 為主，CLAUDE.md legacy），找到含該路徑的 Capabilities 行
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

---

## Kanban 維護程序

Phase 3 額外執行的 kanban hygiene 檢查：

### 偵測項目

| 檢查 | 條件 | 嚴重度 | 自動修正 |
|------|------|--------|---------|
| Stale card | To Do > 7 天、In Progress > 14 天無修改 | 🟡 | 不修正（只報告） |
| Lane 限額 | To Do > 100 張 | 🟡 | 不修正（只報告） |
### backlog 卡處置（2026-09-02 起單制）

`backlog/` 制：**completed/ 是歷史檔案庫，不套年齡 stale heuristic**（價值正是歷史追溯——決策脈絡、驗收紀錄；過大由人類留意）。**Done 欄卡清場＝`backlog task complete <id>` 搬 `completed/`**——結案兩步延後的批次執行點（命令合約見 [kanban-board](../kanban-board/SKILL.md)）。活躍卡年齡檢查（To Do/In Progress）＝ doc-health 步驟 4（讀 frontmatter `updated_date`）。無 `backlog/` 的 repo 無卡層清理面。`.kanban/` 四 lane 舊制已退役。

---

## 決策點預設值

自動模式不詢問，使用以下預設值：

| 決策點 | 自動預設 | 說明 |
|--------|---------|------|
| X-cap-path 修正 | 自動修 | 🟢 low risk |
| X-ep-ready / X6 | 只報告 | 🟡 需語義判斷 |
| /instruction-sync --changed-since | `yesterday` | 每日增量 |
| /doc-health 參數 | 預設（不含 --quality --all） | 核心 findings 即可 |
| SYSTEM-MAP 同步 | 不執行 | 需人類確認狀態語義 |

---

## 報告格式

### 無變化

```
## Daily Maintenance Report

### Phase 1: Graph Freshness
✅ code-reality graph 重建完成（opt-in repo）／ skip（無 index 的 repo）

### Phase 2: Instruction Sync
✅ 無問題（檢查 N 個檔案）

### Phase 3: Doc Health + Kanban
✅ 無問題（findings 全部已處理，kanban 健康）

### Phase 4: Health Report
✅ 整體健康，無跨 phase 關聯問題
```

### 有變化

```
## Daily Maintenance Report

### Phase 1: Graph Freshness
⚠️ graph 重建完成（失敗時：`[WARN]` + 原因，續行）

### Phase 2: Instruction Sync
⚠️ 發現 N 個問題
- data/AGENTS.md: 路徑 xxx 已更名 → [自動修正已完成]
- features/CLAUDE.md: 缺少導航 → 建議新增（🟡 未修正）

### Phase 3: Doc Health + Kanban
⚠️ findings: N issues (0 critical, N important)
- [X-cap-path] xxx 不存在 → [自動修正已完成]
Kanban: To Do N 張, In Progress N 張, Done N 張
  - Stale: To Do 'xxx' 已 8 天未更新

### Phase 4: Health Report
- 跨 phase 關聯：Phase 2 Instruction 問題 ↔ Phase 3 findings 同根因
- 未解決 🟡: N 筆（需人工確認）
- 趨勢: findings +N、kanban 卡片流動

### 下一步
- 🟡 待確認項目：列出
```

### 晨報檔格式（寫入 `ai-analysis/daily-report/YYYY-MM-DD.md`）

晨報檔讀者是「早上想一眼知道今天要決定什麼的人類」。結構**不同於 stdout 的 phase 順序**——把需人類決定的事置頂，已自動處理的簡短帶過：

```markdown
# Daily Briefing — YYYY-MM-DD

## 🔥 今天需要你決定的事
<!-- 無則改標「✅ 無待決項」並仍寫檔，證明排程有跑 -->
- 🟡 [X-ep-ready / X6 / 需語義判斷] — 為什麼需要你決定 + 建議
- Kanban stale: `<card>` 已 N 天未動 — 繼續 or 歸檔？
- 跨 phase 關聯待確認: Phase 1 import 變化 ↔ Phase 2 Instruction 問題

## ✅ 已自動處理（你不用管）
- auto-fixed: X-cap-path(N)

## 📈 趨勢
- findings: X→Y、kanban 卡片流動
- 與昨日 diff 要點
```

**撰寫要點**：

- 🔥 段每項必附「**為什麼需要人類決定** + 建議方向」，不只是列項目——這是晨報的核心價值，呼應 description 的 morning report 承諾
- ✅ 段簡短摘要即可，細節已在 stdout log（`$MOSAIC_OPS_LOG_DIR/daily-maintain-YYYYMMDD.log`）
- 無 🟡 時 🔥 段標「✅ 無待決項」——**仍寫檔**，讓「沒檔」一致意味著「排程沒跑」（避免「沒事」與「沒跑」混淆，正是 2026-06-30 晨報斷更調查的教訓）
- 檔名日期用排程觸發日；同日重跑 **merge**（非覆蓋）：
  - **owned section**（Phase 4 重寫）：top `# Daily Briefing` title + intro（含 blockquote）+ `## 🔥` / `## ✅` / `## 📈`
  - **foreign section**（保留）：其他排程載體 append 的 section——nightly-thin 的 `## test-regression`、ZCode 23:20 任務的 `### 🔍 audit-test`（h3 附屬於前一個 `## ` section 內，split 不切開、隨所屬 section 一併保留）與 `## 📝 昨日活動`
  - **owned 判定（prefix match，去 `## ` 前綴）**：每個 `## ` section 去掉開頭 `## ` 後，header 若 startswith `🔥` / `✅ 已自動處理` / `📈` 即 owned（容忍 `✅` 括號變體：`## ✅ 已自動處理（你不用管）` → 去 `## ` → `✅ 已自動處理（你不用管）` → match）；其餘為 foreign。**比對前必先去 `## `，否則 header 以 `## ` 開頭 ≠ 以 emoji 開頭 → owned 誤判 foreign → 重寫時 duplicate**
  - **merge 流程**：讀現檔 → split `## ` section（不含 top title / pre-first-h2 intro）→ 去 `## ` 前綴比對 owned/foreign → 留 foreign → `merged = new_briefing(含 title+intro+🔥✅📈) + foreign sections` → 寫回。top title + intro + blockquote 隨 new_briefing 每次重生（屬 Phase 4 owned）。

---

## Commit 規則

### 自動模式（/daily-maintain）

**自動 commit 範圍**：🟢 自動修正的變更 + 晨報檔（`ai-analysis/daily-report/YYYY-MM-DD.md`，若產出）。

Commit message 格式：
```
chore(maintain): daily auto-maintain — X findings fixed, Y reported

Auto-fixed: X-cap-path(N)
Reported: X6(N)
Morning report: ai-analysis/daily-report/YYYY-MM-DD.md
```

**outward-action-consent 豁免**：調用 `/daily-maintain`（自動模式）即隱含同意 🟢 低風險修正的 commit。🟡 中風險不 commit。手動補跑時 commit 依 outward-action-consent 規則（展示 diff、等待確認）。

---

## 參數

| 參數 | 說明 |
|------|------|
| 無參數 | 依序執行 Phase 1 → 2 → 3 → 4 |
| `--only graph` | 只跑 Phase 1（graph 新鮮度） |
| `--only sync` | 只跑 Phase 2 |
| `--only doc-health` | 只跑 Phase 3 |
