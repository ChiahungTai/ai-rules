# EP: review 工作流深化 — 結構維度 + 並發狀態查證 + domain grounding + pipeline recipe

## 動機（self-contained 背景）

review 命令群（arch-review / followup-review / code-review）在四個面向有縫隙，全部來自一個重度使用 review 鏈的 session（期貨 session 分離 + NT margin 問題 A）：

**縫隙①：arch-review City Map 只畫方向，缺 dep weight**（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-18-multi-angle-review-placement-gap.md`，#14）。[arch-review.md](../../commands/arch-review.md) `:83-97` 元件 A 渲染模組 + 依賴方向（A ──uses──▶ B），但**看不出** `catalog_utils` 是 lean（stdlib + urisafe）而 `dataframe_utils` 是重型（numpy/pandas/polars/nautilus）。#14 實證：把 polars/decode helper 抽進 lean 廣用 `catalog_utils` 這個經典 anti-pattern，City Map 上完全不可見 — 第 1 次 arch-review 判「✅ 無 cycle 可 commit」，靠 user 二刷並**手動植入 import 視角**才抓到放置點錯。

**縫隙②：reuse candidate「非阻塞可 commit」沒考慮實作本身是結構變更**（#14）。`:231-233` Recommended Next Steps 從「處理確認的重用/結構問題」直接跳 `/commit`。但實作 RC（抽 helper、合併 method）創造**新 artifact**，其放置點/依賴需 re-review。`--focus`（`:54`）已存在但「實作 reuse 後重跑 --focus 新抽象」的時機沒被推薦。

**縫隙③：followup-review 跨 session 並發用過時 Read 誤判**（`2026-06-18-multi-session-review-chain-and-lint-scoping.md` 摩擦 A，#15A）。[followup-review.md](../../commands/followup-review.md) `:72-79`「必須查證實際程式碼：git diff + Read 確認」— 但**沒強調跨 session 並發時 Read 是快照、會漂移**。#15A 實證：review session 用 code-review 階段的 Read 記憶判「F1-F3 未 apply」，但實作 LLM 期間已 apply，靠 `rg end_date = 0 hits` + test passed 才推翻自己誤判。

**縫隙④：review 未 grounding 外部框架 domain claims**（`2026-06-18-review-not-grounding-nt-claims.md` 的 review 切面，#17）。arch-review/followup-review 對涉及外部框架語意（NT/SJ account/equity/engine）的宣稱，沒強制 nt-query/source grounding 附 path:line。#17 實證：NT 宣稱（A1-A5）在 followup 全標 ✅ verified，但「verified」證據是「EP 這樣寫 + unit test green」，**從未碰 NT 權威源碼** — 未驗證外推隨 fix 寫進 CLAUDE.md 變正式宣稱。

**共同根因**：review 命令的查證對象偏「當前 repo code」（diff/結構/重用），缺三個維度 — (a) 結構的**權重**而非只方向、(b) 跨 session 的**狀態時效**（Read 會過時）、(c) 對**外部框架語意**的 grounding。加上 review 鏈編排（多角度何時跑）缺 recipe，全靠 user 手動驅動。

**本 EP 範圍**（#14 + #15AC + #17 review 切面）：S1 City Map dep weight、S2 reuse lifecycle + --focus 時機、S3 followup 並發查證、S4 domain-claim grounding、收尾 review-pipeline recipe。**Scope out**：#14「executor 把 spec 放置點當假設非指令」（偏 build/handoff，cross-ref）、#15C「.review 跨 session 生命週期」（cross-ref ep-agent-output-verification S4）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | arch-review City Map 加 dep weight（lean/heavy）+ 消費者數維度 | 無 |
| S2 | arch-review reuse candidate 實作後 re-review 放置點 + `--focus` 時機 | S1 |
| S3 | followup-review 跨 session 並發狀態查證（強制 git diff 對照、禁用過時 Read） | 無 |
| S4 | review domain-claim grounding（外部框架語意強制 nt-query/source 附 path:line） | 無 |

S1/S2 同屬 arch-review 結構深化（S2 依賴 S1 的 dep weight 概念）；S3/S4 是另兩個 review 命令的查證強化。收尾補 review-pipeline recipe（跨命令編排）。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（本 EP 源自 #14 + #15AC + #17）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過）。

### 掃描範圍
- [commands/arch-review.md](../../commands/arch-review.md)（`:83-97` City Map、`:124-164` reuse、`:231-233` Next Steps、`:54` --focus、`:264-270` 流程位置）
- [commands/followup-review.md](../../commands/followup-review.md)（`:72-79` 執行約束、`:35` 讀 .review）
- [commands/CLAUDE.md](../../commands/CLAUDE.md)（核心流程段，收尾 recipe 落點）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 結構 viewport（City Map/Flows/Boundaries/重用） | `commands/arch-review.md` | ✅ → S1 加 dep weight、S2 加 reuse lifecycle |
| 審查者驗收實作結果 | `commands/followup-review.md` | ✅ → S3 加並發狀態查證 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| review domain-claim grounding（外部框架語意查證） | 📋 | arch-review + followup-review（S4） |
| review-pipeline recipe（變更類型 → review 序列） | 📋 | commands/CLAUDE.md 核心流程（收尾） |

---

## Scenario Matrix（大型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | City Map 渲染含 lean/heavy 混合模組 | 變更涉及不同 weight 模組 | 每節點標 dep weight（lean/heavy）+ 消費者數；「重型 helper 放 lean 廣用模組」視覺凸顯 | 無 | 結構 viewport |
| SM-2 | reuse candidate 實作後 | RC 標「非阻塞可 commit」後 user 實作抽 helper | Next Steps 標「實作後須 `arch-review --focus <新抽象>` re-review 放置點再 commit」 | 無 | 結構 viewport |
| SM-3 | followup 跨 session 並發 | `.review/<branch>.md` 含 judge-review 決策（實作 LLM 可能並發處理） | 開頭**強制 `git diff --stat` 對照當前 vs 預期**，禁用先前 Read 記憶作結論依據 | 無 | 驗收 |
| SM-4 | review 涉及外部框架語意 | 宣稱含 NT/SJ account/equity/engine 語意 | 強制 nt-query/source grounding 附 path:line；未 grounding 標 `open` 非 `verified` | 無 | domain grounding |
| SM-5 | 大型 refactor 選 review 序列 | 變更類型 = refactor | review-pipeline recipe：arch（結構）→ 實作 → `arch --focus`（新抽象）→ code（正確性）→ commit | 無 | pipeline recipe |

---

## S1: arch-review City Map 加 dep weight + 消費者數

### Context
- **背景**：`:83-97` 元件 A 渲染依賴方向，無 weight。#14 實證：重型（polars/numpy）helper 抽進 lean（stdlib）廣用模組，City Map 不可見 — 方向對、無 cycle，但「耦合重型依賴到廣用模組」這個經典 anti-pattern 隱形。
- **UC 引用**：更新既有「結構 viewport」
- **依賴**：無
- **語義約束**：dep weight 是輔助維度（人判材料），不改變 City Map「方向/循環」的主要判定
- **依賴錨點**：`commands/arch-review.md:83-97`（元件 A City Map）
- **成功標準**：
  - [ ] City Map 每節點標 dep weight（lean = stdlib/輕量；heavy = numpy/pandas/polars/nautilus/大型框架）+ 消費者數（誰 import 它）
  - [ ] 「heavy → lean」的反向耦合（重型 helper 放進被廣泛 import 的 lean 模組）視覺 flag
  - [ ] 渲染範例更新（`catalog_utils`(lean, 12 consumers) vs `dataframe_utils`(heavy, 3 consumers)）

### 修改要點
1. **`:83-97` 元件 A**：節點標註加 `weight` + `consumers`；加偵測規則「heavy symbol 進 lean 廣用模組 → flag（transitive burden：lean 模組的所有消費者被拖入重依賴）」
2. 渲染範例更新（lean/heavy 標註 + 反向耦合 flag）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "dep weight|lean|heavy|消費者數|transitive burden" commands/arch-review.md` → 命中
- **`/consistency`**：跑 `commands/arch-review.md`
- **模擬（SM-1）**：給「catalog_utils(lean) + dataframe_utils(heavy) + polars helper 抽進 catalog_utils」→ 確認 flag 反向耦合

---

## S2: arch-review reuse candidate 實作後 re-review + --focus 時機

### Context
- **背景**：`:231-233` Next Steps 從「處理重用」跳 `/commit`，漏了「實作 RC 本身是結構變更，新抽象放置點需 re-review」。`--focus`（`:54`）已存在但「實作 reuse 後重跑」時機沒推薦。#14 實證：RC-001 抽 `read_session_parquet_raw` 進 catalog_utils 後，第 1 次 arch-review 職責（找重複）已完成，但新 helper 落點依賴無人審，靠 user 二刷 + 植入 import 視角才抓到。
- **UC 引用**：更新既有「結構 viewport」
- **依賴**：S1（dep weight 概念 — re-review 時 --focus 新抽象的落點用 dep weight 判）
- **語義約束**：「非阻塞可 commit」的判定對「實作後」不成立 — 實作 RC 創造新 artifact，其放置點是新結構決策
- **依賴錨點**：`commands/arch-review.md:231-233`（Next Steps）、`:54`（--focus）、`:264-270`（流程位置）
- **成功標準**：
  - [ ] Next Steps 對 reuse candidate 的判定改「非阻塞，但**實作後須 `arch-review --focus <新抽象>` re-review 放置點**（dep weight + 消費者）再 commit」
  - [ ] 流程位置（`:264-270`）補「實作 reuse candidate / 抽 helper 後 → 重跑 `arch-review --focus <新 symbol>`」
  - [ ] --focus 段補「實作新抽象後的首選用途：審新 symbol 的落點依賴（S1 dep weight）」

### 修改要點
1. **`:231-233` Next Steps**：「處理確認的重用」→ 補「實作後 re-review 放置點再 commit」
2. **`:264-270` 流程位置** + **`:54` --focus**：補「實作 reuse/抽 helper 後重跑 --focus 新抽象」時機

### 驗證策略（docs mode）
- **rg 閘門**：`rg "實作後.*re-review|reuse.*實作|--focus.*新抽象|放置點" commands/arch-review.md` → 命中
- **`/consistency`**：跑 `commands/arch-review.md`
- **模擬（SM-2）**：給「RC 標非阻塞可 commit → user 實作抽 helper」→ 確認 Next Steps 標實作後須 --focus re-review

---

## S3: followup-review 跨 session 並發狀態查證

### Context
- **背景**：`:72-79`「必須查證實際程式碼：git diff + Read 確認」— 但跨 session 並發（review session + 實作 session）時，reviewer 的 Read 是**過時快照**。#15A 實證：用 code-review 階段 Read 記憶判「F1-F3 未 apply」，實作 LLM 已 apply，靠 rg + test 才推翻誤判。「記憶是嫌疑犯，當前檔案才是證據」。
- **UC 引用**：更新既有「審查者驗收」
- **依賴**：無
- **語義約束**：git diff（當前機械事實）> 先前 Read 記憶（可能過時）— 並發 session 下 Read 過時是常態非例外
- **依賴錨點**：`commands/followup-review.md:72-79`（執行約束）、`:35`（讀 .review）
- **成功標準**：
  - [ ] 執行約束加「**跨 session 並發警告**」：若 `.review/<branch>.md` 存在 judge-review 決策（表示實作 LLM 可能並發處理過），followup 開頭**強制 `git diff --stat` 對照當前 vs 預期**，禁用先前 Read 記憶作結論依據
  - [ ] 原則明文：「記憶是嫌疑犯，當前檔案（git diff）才是證據 — 並發 session 下 Read 過時是常態」

### 修改要點
1. **`:72-79` 執行約束**：加「並發 session 警告」前置 — `.review` 有 judge-review 決策 → 開頭強制 `git diff --stat` 對照、禁用過時 Read 記憶
2. 無參數模式（`:33-38`）補：讀 .review 後先 git diff --stat 對照當前狀態

### 驗證策略（docs mode）
- **rg 閘門**：`rg "並發|過時|git diff --stat|記憶是嫌疑犯|快照" commands/followup-review.md` → 命中
- **`/consistency`**：跑 `commands/followup-review.md`
- **模擬（SM-3）**：給「.review 有 judge-review 決策 + reviewer 記憶 F1-F3 未 apply」→ 確認開頭 git diff --stat 揭露已 apply、推翻過時記憶

---

## S4: review domain-claim grounding（外部框架語意查證）

### Context
- **背景**：arch-review/followup-review 對涉及外部框架語意（NT/SJ account/equity/engine）的宣稱，沒強制 grounding。#17 實證：NT 宣稱 A1-A5 在 followup 全標 ✅ verified，但證據是「EP 這樣寫 + unit test green」，從未碰 NT 源碼 — A4/A5 未驗證外推隨 fix 寫進 CLAUDE.md 變正式宣稱。CLAUDE.md 模組觸發器明訂「NT 概念/實作」應載入 nt-query，但 review 流程沒觸發。
- **UC 引用**：新增「review domain-claim grounding」
- **依賴**：無（nt-query skill 已存在，本段是讓 review 命令觸發它）
- **語義約束**：grounding 針對「外部框架語意宣稱」（NT/SJ/第三方能力邊界），非「當前 repo code」（後者已由 diff/結構查證涵蓋）
- **依賴錨點**：`commands/arch-review.md`（Phase 2 查證）、`commands/followup-review.md:44-48`（逐項驗收）
- **成功標準**：
  - [ ] arch-review + followup-review 對「涉及外部框架語意（NT/SJ account/equity/engine/第三方能力邊界）的宣稱」強制一步 grounding：nt-query / sj source（附 path:line）
  - [ ] 未 grounding 的 domain claim 標 `open`（未驗證）非 `verified` — 不隨 fix 寫進 CLAUDE.md 變正式宣稱
  - [ ] 觸發訊號：宣稱含「X 支援/不做 Y」「X 底層是 Z」「跨三模型成立」等能力邊界語句

### 修改要點
1. **arch-review Phase 2** + **followup-review 逐項驗收**：加 domain-claim grounding 步驟 — 宣稱涉及外部框架語意 → 强制 nt-query/sj source grounding（path:line）；未 grounding 標 open
2. 觸發訊號清單（能力邊界語句）

### 驗證策略（docs mode）
- **rg 閘門**：`rg "domain.claim grounding|外部框架語意|nt-query.*grounding|能力邊界" commands/arch-review.md commands/followup-review.md` → 命中
- **`/consistency`**：跑兩檔
- **模擬（SM-4）**：給「宣稱『NT Cash 擋 short』未查源碼」→ 確認強制 grounding，未 grounding 標 open 非 verified

---

## 收尾

- **review-pipeline recipe（#14/#15C，收尾指引）**：在 [commands/CLAUDE.md](../../commands/CLAUDE.md) 核心流程段補「變更類型 → review 序列」recipe，避免 user 每次手動重組：
  - **refactor / 結構變更**：`/arch-review`（結構）→ 實作 → `/arch-review --focus <新抽象>`（放置點，S2）→ `/code-review`（正確性）→ `/commit`
  - **大型新功能**：post-EP `/arch-review --ep` + `/deliverable-review --ep` → `/build` → post-build `/arch-review` + `/deliverable-review` → `/code-review` → `/commit`
  - **多角度深化**：correctness（code-review）與 structure（arch-review）是不同認知模式，大型變更分多次、每次一深度，不強求一次全包（#15C 觀察）
- **受影響命令行為已反映**：arch-review（dep weight + reuse lifecycle + domain grounding）、followup-review（並發查證 + domain grounding）— `commands/CLAUDE.md` 索引 description 同步。
- **Scope out**：#14「executor 把 spec 放置點當假設」（偏 build/handoff，cross-ref 未來 build EP）、#15C「.review 跨 session 生命週期」（cross-ref ep-agent-output-verification S4）、#17 的 spec↔code drift 查證（屬 doc-health/sync，獨立）。
- **風險**：S1 dep weight 判定 lean/heavy 需主觀（numpy 算 heavy、stdlib 算 lean）。緩解：列常見 heavy 依賴清單（numpy/pandas/polars/nautilus/大型框架）作機械判準起點；邊界由人 whole-picture 判。
