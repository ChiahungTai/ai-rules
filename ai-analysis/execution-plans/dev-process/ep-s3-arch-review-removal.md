# EP: S3 arch-review 移除 — 能力遷移，命令刪除

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S3 段展開）
> **本 EP**:能力已落地 S1（[architecture-viewport](../../../skills/architecture-viewport/SKILL.md) skill）+ S2（[illustrate](../../../commands/illustrate.md) 人 viewport 載體）。移除 `/arch-review` 命令避免三處重複（arch-review ↔ illustrate 職責重疊，master 問題③）。**受眾靠產出區分不靠命令** — 人 viewport 結構判讀全程保留（載體換 illustrate）。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

`/arch-review` 的能力已分流：S1 skill（機械能力：City Map 資料 / Pattern Radar / LSP 查證）+ S2 illustrate（人 viewport 渲染：city map / call stack / drill，B 軸）。S5（pending）會讓 code-review axis 3 調用 skill 產機器 finding（A 軸）。三消費端各就位後，命令本身是重複（arch-review 與 illustrate 都做結構圖解）。

**移除的是命令，不是能力**。人 viewport 結構判讀（pre-EP / post-EP / post-build）全程保留，載體換 illustrate（S2 已建）。

**本 EP 範圍**（master S3）：刪 `commands/arch-review.md` + 全 repo 活躍文檔 `/arch-review` 引用清到 0 hits（流程位置 / 關係表 / 索引 / 受眾模型改 illustrate）+ memory 同步。

**Scope out**：S5 code-review axis 3 調用 skill（消費端機器，S5 子 EP）；EP 群組 / 歸檔 EP 不動（規劃/歷史記錄，非活躍文檔）。

**清理清單（實證）**：
- 刪 `commands/arch-review.md`
- 根 [CLAUDE.md](../../../CLAUDE.md)（4 處）：受眾視角 `:20` / blind spot 表 `:28` / 三層介入表 `:41` / 命令分類表 `:60`
- [rules/acceptance-evidence.md](../../../rules/acceptance-evidence.md)（2 處）：B 軸表 `:77` / 已落地 `:83`
- [commands/CLAUDE.md](../../../commands/CLAUDE.md)（4 處）：流程圖 `:23`/`:25` / deliverable description `:35` / 命令索引 `:36`（刪整行）
- [commands/deliverable-review.md](../../../commands/deliverable-review.md)（9 處）：frontmatter `:3` / 不做的事 `:15` / 表 `:117` / 流程位置 `:181`/`:210`/`:215`/`:227`/`:231` / 邊界 `:190` / 關係表 `:202`
- [commands/build.md](../../../commands/build.md)（2 處）：流程位置 `:239` / Agent Review 說明 `:244`
- [commands/ep-review.md](../../../commands/ep-review.md)（1 處）：受眾說明 `:15`
- memory `b-axis-human-acceptance-roadmap.md`（若引用 /arch-review）：同步（非 repo，不進 commit）
- `execution-plan.md` / `code-review.md` / `commit.md`：master EP 預防性列出，**實證無引用** → 不需清

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S3a** | 刪 arch-review.md + 核心索引/受眾（commands/CLAUDE.md 命令索引刪行 + 流程圖 + 根 CLAUDE.md 受眾模型 4 處） | S2（illustrate 載體） |
| **S3b** | 消費端引用清理（acceptance-evidence + build + ep-review + deliverable-review）流程位置/關係表 → illustrate | S3a |
| **S3c** | 驗證 rg 活躍文檔 0 hits + lsp-architect agent 保留確認 + memory 同步 | S3a/S3b |

3 段序列（核心索引先 → 消費端引用 → 驗證）。

---

## UC 盤點（docs mode）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 結構 viewport（City Map/Flows/Boundaries/重用） | `commands/arch-review.md` | ✅ → **S3 移除命令入口**；能力已遷 S1（skill）+ S2（illustrate）+ S5（code-review axis3） |

---

## Scenario Matrix（中型變更，docs mode）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-7 | 整脊完成反查 | `rg "/arch-review"` 活躍文檔（commands/ rules/ CLAUDE.md） | **0 hits**（流程圖/關係表/索引/受眾模型改 illustrate） | 無 | 結構 viewport 遷移 |

---

## S3a: 刪命令 + 核心索引/受眾模型

### Context
- **背景**：刪 `commands/arch-review.md`。核心索引（commands/CLAUDE.md 命令索引刪 arch-review 行 + 流程圖 arch-review → illustrate）+ 根 CLAUDE.md 受眾模型 4 處（arch-review → illustrate）。
- **語義約束**：**受眾靠產出區分不靠命令** — 移除命令，layer 3 結構軸人 viewport 判讀保留（載體換 illustrate）。
- **依賴錨點**：[commands/CLAUDE.md](../../../commands/CLAUDE.md) `:23`/`:25`（流程圖，S2 已改 :21 pre-EP）/`:35`（deliverable desc）/`:36`（命令索引刪行）；根 [CLAUDE.md](../../../CLAUDE.md) `:20`/`:28`/`:41`/`:60`
- **成功標準**：
  - [ ] 刪除 `commands/arch-review.md`
  - [ ] commands/CLAUDE.md 命令索引（`:36`）刪 `/arch-review` 整行
  - [ ] commands/CLAUDE.md 流程圖（`:23`/`:25`）：post-EP `/arch-review --ep` → `/illustrate`（結構）；post-build `/arch-review` → `/illustrate`（漂移/重造檢查）
  - [ ] commands/CLAUDE.md deliverable description（`:35`）：「不審結構（交 /arch-review）」→「不審結構（交 /illustrate 結構 viewport）」
  - [ ] 根 CLAUDE.md 受眾視角（`:20`）：軌道 ②「/deliverable-review（交付）與 /arch-review（結構）」→「...與 /illustrate（結構 viewport）」
  - [ ] 根 CLAUDE.md blind spot 表（`:28`）：「整體直覺 → /arch-review」→「→ /illustrate（結構 viewport）」
  - [ ] 根 CLAUDE.md 三層介入表（`:41`）：layer 3「/deliverable-review + /arch-review」→「...+ /illustrate（結構）」
  - [ ] 根 CLAUDE.md 命令分類表（`:60`）：`/arch-review` 行 → `/illustrate`（結構 viewport，三時點）

### 修改要點
1. **刪 `commands/arch-review.md`**
2. **commands/CLAUDE.md**：命令索引刪 arch-review 行 + 流程圖改 illustrate + deliverable desc 改
3. **根 CLAUDE.md**：4 處受眾模型 arch-review → illustrate

### 驗證策略（docs mode）
- **rg 閘門**：`rg "arch-review" commands/CLAUDE.md CLAUDE.md` → 0 hits（活躍文檔核心索引清）

---

## S3b: 消費端引用清理（流程位置/關係表 → illustrate）

### Context
- **背景**：消費端命令的流程位置 / 關係表 / 邊界引用 arch-review，改 illustrate（人 viewport 結構 viewport 載體）。
- **依賴**：S3a（核心索引已改）
- **依賴錨點**：[rules/acceptance-evidence.md](../../../rules/acceptance-evidence.md) `:77`/`:83`；[commands/build.md](../../../commands/build.md) `:239`/`:244`；[commands/ep-review.md](../../../commands/ep-review.md) `:15`；[commands/deliverable-review.md](../../../commands/deliverable-review.md) `:3`/`:15`/`:117`/`:181`/`:190`/`:202`/`:210`/`:215`/`:227`/`:231`
- **成功標準**：
  - [ ] **acceptance-evidence.md**（`:77`/`:83`）：B 軸人類驗收「deliverable-review + arch-review」→「...+ illustrate（結構 viewport）」；已落地說明同改
  - [ ] **build.md**（`:239`/`:244`）：流程位置 post-EP `/arch-review --ep` → `/illustrate`（結構）；Agent Review 說明 `/arch-review` → `/illustrate`（結構 viewport）
  - [ ] **ep-review.md**（`:15`）：受眾說明「EP 人類 viewport 是 /deliverable-review --ep + /arch-review --ep」→「...+ /illustrate（結構 viewport）」
  - [ ] **deliverable-review.md**（9 處）：frontmatter when_to_use `/arch-review` → `/illustrate`；「不做的事：結構 → /arch-review」→ `/illustrate`；表 `:117`/關係表 `:202`/流程位置×6 / 邊界 `:190` 全改 illustrate

### 修改要點
1. **acceptance-evidence.md**：2 處 arch-review → illustrate
2. **build.md**：2 處流程位置/Agent Review → illustrate
3. **ep-review.md**：1 處受眾 → illustrate
4. **deliverable-review.md**：9 處 frontmatter/不做/表/流程/關係/邊界 → illustrate

### 驗證策略（docs mode）
- **rg 閘門**：`rg "arch-review" commands/deliverable-review.md commands/build.md commands/ep-review.md rules/acceptance-evidence.md` → 0 hits

---

## S3c: 驗證 + lsp-architect 保留 + memory 同步

### Context
- **背景**：全 repo 活躍文檔 rg 0 hits 驗證（SM-7）。`lsp-architect` agent（[agents/lsp-architect.md](../../../agents/lsp-architect.md)）**保留** — 是 architecture-viewport skill 的查證 helper（非 arch-review 專屬）。memory `b-axis-human-acceptance-roadmap.md` 若引用 arch-review 則同步。
- **依賴**：S3a/S3b
- **成功標準**：
  - [ ] **`rg "/arch-review" commands/ rules/ CLAUDE.md` → 0 hits**（SM-7，活躍文檔；EP 群組/歸檔不計）
  - [ ] **lsp-architect agent 保留**：確認 [agents/lsp-architect.md](../../../agents/lsp-architect.md) 不引用 arch-review（是 skill 的查證 helper，跨命令共用）；若引用則改 architecture-viewport skill
  - [ ] **memory 同步**：`b-axis-human-acceptance-roadmap.md` 若引用 `/arch-review` → `/illustrate`（非 repo，不進 commit，作 memory 維護）

### 修改要點
1. rg 驗證 0 hits
2. lsp-architect agent 確認/清理
3. memory 同步（若需）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "arch-review" commands/ rules/ CLAUDE.md` → 0 hits（活躍文檔 SM-7）
- **`/consistency`**：跑根 CLAUDE.md + commands/CLAUDE.md（確認無斷引用）

---

## 收尾

### 受影響索引同步
- [commands/CLAUDE.md](../../../commands/CLAUDE.md)：命令索引（刪 arch-review）+ 流程圖 + illustrate description（S2 已擴充）— S3a 處理
- [CLAUDE.md](../../../CLAUDE.md)（根）：受眾模型三層介入表 + 命令分類表 — S3a 處理

### 回母 EP
本 EP 完成（master S3 build+commit）後，master 綱要 S3 段標 ✅。**S2 過渡態消除**（arch-review 移除後，CLAUDE.md `:82` illustrate 三時點與流程圖一致；drill 指令只剩 supporting file）。

### 風險與緩解
- **移除破壞肌肉記憶/文檔引用** → rg 全清活躍文檔（SM-7）+ illustrate description 標「原 arch-review 能力」（S2 已做）
- **受眾模型 layer 3 結構軸失去命令入口** → 載體換 illustrate（pre-EP/post-EP/post-build 三時點），受眾靠產出區分不靠命令（master EP S3 語義約束）
- **lsp-architect agent 誤刪** → 明文保留（是 skill 查證 helper，非 arch-review 專屬）
- **EP 群組殘留 /arch-review**（ep-review-pipeline-grounding.md 13 hits / _done/ 1 hit）→ 不動（規劃/歸檔歷史，非活躍文檔；ep-review-pipeline-grounding.md 是 master EP 收尾要吸收歸檔的 EP）
