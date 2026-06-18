# EP: ai-rules Capture Bridge — 跨 session 摩擦半自動捕捉

## 動機（self-contained 背景）

ai-rules 的演化輸入**結構性偏狹**：`/flow-feedback` 是唯一摩擦收集器，但它寫相對路徑 `ai-analysis/flow-feedback/`（`commands/flow-feedback.md:46`），在消費端 session（mosaic / NT）跑時依 cwd 寫進消費端 repo，**永遠到不了 ai-rules**。實證：`ai-analysis/flow-feedback/_done/` 歷史 3 筆，**全部來自 ai-rules dogfood 自己**（`/consistency`、dogfood `/execution-plan`、dogfood `/code-review`），0 筆來自消費端真實使用。

結果：ai-rules 只看得到「怎麼操作 ai-rules」的摩擦，看不到「規則在 mosaic/NT 真實使用時哪裡不準」——dogfood 迴音室。

**Hermes 對照**（已查證 `agent/background_review.py`）：Hermes 每 `_n=10` iters 自動 fork 掃對話、直寫 skill store。它能全自動是因為它**就是 agent**（capture 與 land 同處）且 auto-land 的是 **soft skill**（可復原）。ai-rules 兩個前提都沒有——所以不能搬 Hermes 的 auto-land，但**可以搬它的 capture 精神**，落在 ai-rules 自己的安全模型裡。

**安全分層判斷（本 EP 的設計骨幹）**：演化迴圈三環 Capture → Crystallize → Land，安全門檻不同：
- **Capture**（偵測值得留的教訓）：可回復（漏訊號 = 少資料，無害）→ 允許 LLM-driven + 機械訊號觸發
- **Crystallize / Land**（教訓 → 規則 → 生效）：不可回復（壞規則每 session 重讀）→ 必須 human-gated

本 EP 只動 **Capture**（半自動），Crystallize/Land 維持現有 human-gated（`/flow-review` → `/spec` → `/build`）。這是「半自動→自動」的第一步；「自動 landing」（provenance 沙箱 + curator）為獨立後續 EP，本 EP 明確 scope out。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | `/flow-feedback` 寫入路徑修正（落點 = ai-rules repo，非 cwd）＋ `source` provenance 欄位 | 無 |
| S2 | 新增 auto-loaded rule：跨 session 機械摩擦訊號 → 自動 file 候選 | S1 |
| S3 | `/flow-review` 消費 `auto-signal` 候選，聚類＋人類 triage | S1, S2 |

**段落劃分策略**：S1 是基礎設施（寫入落點 + provenance），單獨可用——即使沒有 S2，修正路徑也讓消費端**手動** `/flow-feedback` 能落地 ai-rules，立刻打破 dogfood 偏狹。S2 在 S1 之上加自動捕捉（半自動）。S3 讓既有 `/flow-review` 消費新料。三者層層疊加、各自獨立驗收。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格，掃受影響命令/rules）

### Backlog 關聯
- `.kanban/Backlog/mechanical-gate-philosophy-hybrid.md` — 相關但**不同**：該卡是「機械閘門哲學」的 skill 顯式化（meta 層）；本 EP 是 capture 橋（流程層）。兩者正交，不衝突。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過：ai-rules 自身無跨域功能狀態總覽）。

### 掃描範圍
- `commands/flow-feedback.md`、`commands/flow-review.md`（受影響命令）
- `rules/`（S2 新增 rule 的落點）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 摩擦收集（user 植入 → type-1/type-2 建議） | `commands/flow-feedback.md` | ✅ → S1 更新（路徑＋source） |
| 摩擦聚類＋人類決策 | `commands/flow-review.md` | ✅ → S3 更新（消費 auto-signal） |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 跨 session 機械摩擦自動捕捉（候選 file，不 landing） | 📋 | `rules/capture-feedback.md`（auto-loaded） |

---

## Scenario Matrix（中型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 0 殘留 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 消費端 session 跑 `/flow-feedback` | cwd = mosaic/NT（非 ai-rules） | 寫入 **ai-rules repo** 的 `ai-analysis/flow-feedback/`，非 cwd repo | 無 | 摩擦收集 |
| SM-2 | session 出現機械摩擦訊號 | `/loop` 觸發、重複 tool 失敗、`/fix-test` 觸發 | AI 自動 file 候選（`source: auto-signal`）到 ai-rules | 無（候選可丟棄） | 自動捕捉 |
| SM-3 | 環境性 glitch | `command not found`、missing binary、一次性錯誤 | **不捕捉**（非 durable lesson） | 無 | 自動捕捉 |
| SM-4 | 同 session 多次同類訊號 | 一個 session 內 3 次 `/fix-test` | 只 file **一筆**（dedup by repo × 訊號類型） | 無 | 自動捕捉 |
| SM-5 | `/flow-review` 讀混合候選 | `flow-feedback/` 含 `human-seed` + `auto-signal` | 聚類（訊號 × repo）＋報告 dogfood vs 消費端比例＋triage | 無 | 摩擦聚類 |

---

## S1: `/flow-feedback` 寫入路徑修正 ＋ source provenance

### Context
- **背景**：`commands/flow-feedback.md:46` 寫相對路徑，消費端 session 依 cwd 寫錯 repo。修正後，**手動**捕捉也能從消費端落地——即使 S2 不做，S1 單獨就打破 dogfood 偏狹。
- **UC 引用**：更新既有「摩擦收集」能力
- **依賴**：無（基礎設施段落）
- **語義約束**：與 S2/S3 共享「ai-rules repo 錨點 = `commands/flow-feedback.md` 命令檔所在 repo」
- **依賴錨點**：`commands/flow-feedback.md:46`（寫入路徑定義行）
- **成功標準**：
  - [ ] `flow-feedback.md` 寫入指示含 ai-rules repo 錨點（命令檔所在 repo），非裸相對路徑
  - [ ] 輸出格式模板新增 frontmatter `source`（`human-seed` | `auto-signal`）；既有檔案不強制回填
  - [ ] 模擬：在 cwd ≠ ai-rules 下，AI 依指示把寫入目標解析為 ai-rules repo

### 修改要點
1. **`commands/flow-feedback.md:46` 寫入路徑段**：明確「寫入 **ai-rules repo**（即本命令檔 `commands/flow-feedback.md` 所在的 repo），路徑 `ai-analysis/flow-feedback/{YYYY-MM-DD}-{topic-slug}.md`」。以命令檔位置為可移植錨點，不寫死絕對路徑。
2. **輸出格式模板**：加 frontmatter `source`。user 植入 → `human-seed`；S2 自動捕捉 → `auto-signal`。

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "ai-analysis/flow-feedback" commands/flow-feedback.md` 確認路徑說明綁定 ai-rules repo 錨點
- **跨檔一致**：`commands/flow-review.md` 讀取路徑（S3）與 S1 寫入路徑一致
- **`/consistency`**：跑 `commands/flow-feedback.md` 自洽性檢查
- **模擬驗收**：在非 ai-rules cwd 下要求 AI 複述寫入目標，確認指向 ai-rules repo

---

## S2: 跨 session 摩擦自動捕捉 rule（auto-loaded）

### Context
- **背景**：捕捉目前純 MANUAL。ai-rules 經全局 symlink（`~/.claude/CLAUDE.md → ai-rules`）每個 session（含消費端）都讀。一條 **auto-loaded rule** 讓 AI 在任何 session 偵測機械摩擦訊號、自動 file 候選——S1 的路徑修正讓候選落地 ai-rules。這是「半自動」核心：AI 自動捕捉、人類 gate landing。
- **安全層級**：Capture 可回復 → 允許 LLM-driven。但訊號是**機械列舉**（非純自覺），且**只 file 候選、不 landing**——呼應 ai-rules「機械閘門 > LLM 自覺」應用在可回復階段的合理降級。
- **UC 引用**：新增「跨 session 機械摩擦自動捕捉」
- **依賴**：S1（寫入路徑 + `source` 欄位）
- **語義約束**：機械訊號清單與 S3 triage 的分組維度**一致**（同一份清單兩處引用）
- **技術選型**：落點 `rules/`（auto-loaded，每 session 見）而非 `skills/`（on-demand）。捕捉必須被動發生，不能靠 AI「記得載入 skill」——auto-loaded 是結構保證。
- **成功標準**：
  - [ ] 新 rule 列舉機械訊號：`/loop` 觸發、重複（≥3）tool 失敗、`/fix-test` 觸發、`/audit-test` 有 finding
  - [ ] 命中時 file 候選到 ai-rules `flow-feedback/`（`source: auto-signal`），含 session context（發生 repo、訊號類型、一句描述）
  - [ ] **dedup**：同 session 同 (repo × 訊號類型) 只 file 一筆
  - [ ] **不 landing**：不建 kanban card、不改 rule/skill/command，只 file 候選
  - [ ] **反模式排除**：環境性 glitch（missing binary、`command not found`、一次性已解決錯誤）不捕捉——用「訊號是否 durable」機械判準，非 prompt 黑名單

### 修改要點
1. **新增 `rules/capture-feedback.md`**（auto-loaded）：
   - 機械訊號清單（上述）
   - file 候選流程（寫入 ai-rules `flow-feedback/`，`source: auto-signal`，含 repo + 訊號 + 描述）
   - dedup 規則（session × repo × 訊號類型）
   - **不 landing 約束**（顯式：本 rule 只捕捉，落地走 `/flow-review`）
   - 反模式排除（durable vs 環境性判準）
2. **訊號清單單一來源**：S2 定義、S3 引用——避免兩處 drift。

### 驗證策略（docs mode）
- **auto-loaded 確認**：檔在 `rules/` → 載入機制保證（無需測試載入）
- **rg 鍘門**：`rg "auto-signal|source:" rules/capture-feedback.md` 命中
- **模擬 happy path**：給 AI 一個含 `/loop` 觸發的 session 摘要 → 確認 file 候選到 ai-rules（`source: auto-signal`）
- **模擬反模式（SM-3）**：給環境性 glitch（`command not found`）→ 確認**不**捕捉
- **模擬 dedup（SM-4）**：同 session 多次 `/fix-test` → 確認只一筆

---

## S3: `/flow-review` 消費 auto-signal 候選

### Context
- **背景**：`/flow-review` 目前讀 `flow-feedback/` 聚類找重複（既有 noise filter，是 ai-rules 相對 Hermes 的結構優勢——Hermes 必須當場判，ai-rules 有「累積→找重複」餘裕）。S2 產生 `auto-signal` 候選後，flow-review 需消費——但 auto-signal 是機械原始訊號（噪音高），需 triage：聚類 + 人類決定升級 / 丟棄 / 觀察。
- **UC 引用**：更新既有「摩擦聚類＋人類決策」能力
- **依賴**：S1（`source` 欄位）、S2（auto-signal 候選來源 + 訊號清單）
- **語義約束**：聚類分組維度（訊號類型 × repo）與 S2 訊號清單一致
- **依賴錨點**：`commands/flow-review.md`（讀取 + 聚類邏輯）
- **成功標準**：
  - [ ] flow-review 讀取含 `source: auto-signal` 的候選
  - [ ] 聚類維度：**訊號類型 × 發生 repo**，報告 dogfood（ai-rules）vs 消費端（mosaic/NT/...）比例——直接量化 capture gap 改善
  - [ ] 輸出 triage：哪些 auto-signal 升級為 type-1/type-2 flow-feedback、哪些丟棄、哪些觀察（累積下次）
  - [ ] 人類決策落地（B 軸）：升級項走既有 `/spec` / kanban 流程，不自動動 rule

### 修改要點
1. **`commands/flow-review.md` 讀取段**：纳入 `source: auto-signal` 候選（與 `human-seed` 並列）
2. **聚類邏輯**：加「訊號類型 × repo」分組；輸出含 dogfood vs 消費端比例（可觀測 capture gap 是否縮小）
3. **輸出模板**：auto-signal triage 區塊（升級 / 丟棄 / 觀察 三欄）

### 驗證策略（docs mode）
- **rg 鍘門**：`rg "auto-signal" commands/flow-review.md` 命中
- **跨檔一致**：訊號清單與 S2 `rules/capture-feedback.md` 一致（`diff` 兩處列舉）
- **`/consistency`**：跑 `commands/flow-review.md` 自洽性
- **模擬（SM-5）**：餵入混合 `human-seed` + `auto-signal` 候選 → 確認聚類 + repo 分佈報告 + triage 三欄輸出

---

## 收尾

- **受影響命令行為已反映**：`/flow-feedback`（路徑＋source）、`/flow-review`（消費 auto-signal）——`commands/CLAUDE.md` 命令索引 description 同步（`/flow-feedback` 補「跨 repo 落地 ai-rules」；`/flow-review` 補「消費 auto-signal」）。
- **Scope out（明確不在本 EP）**：「自動 landing」= provenance 邊界（`human-core` / `ai-proposed` 標記）＋ ai-proposed 沙箱＋ curator 生命週期。這是「半自動→自動」的第二步，獨立 EP。本 EP 只做 Capture，**不碰 landing**——故無 hard-rule 中毒風險（acceptance-evidence L3）。
- **可觀測性**：S3 的 dogfood vs 消費端比例是本 EP 成功的量化指標——建 EP 前 dogfood ≈ 100%，本 EP 後應見消費端比例上升。若 `/flow-review` 數次後仍 100% dogfood → S2 訊號未在消費端觸發，回頭檢查訊號清單。
