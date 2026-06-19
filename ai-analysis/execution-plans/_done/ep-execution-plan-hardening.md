# EP: execution-plan 強化 — 兜底假設路徑驗證 + 流程分級

## 動機（self-contained 背景）

`/execution-plan` 兩個面向有縫隙，來自兩筆 flow-feedback：

**縫隙①：EP「兜底假設」未驗證路徑是否經過目標**（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-18-ep-safety-net-not-validated.md`，#13）。EP 寫「S6 rebuild 暴露 29 根因」時，**假設 rebuild 會跑到失敗點**。但 rebuild 的 code path（catalog 內部重聚合）**不經過** SJ 寫入鏈（失敗點）— 假設從沒被「rebuild 真的會跑到那條鏈嗎？」驗證。三件事（visible / overlap / 根因）被 EP 框架包裝成「handled」，但**根因從未調查**。對應 acceptance-evidence「測試路徑 ≠ 實際失敗路徑」的 **EP 規劃層版本**：EP 宣稱的處理路徑 ≠ 實際會碰到問題的路徑。build 階段 0「EP 快檢」（[build.md](../../commands/build.md) `:30-34`）只 drift 快掃，沒對「暴露/處理」宣稱追問路徑。加上「可觀測 ≠ 已修復」被 `handled/exposed` 用語模糊涵蓋（S0 = visible、S6 = overlap-fixed，但 root-cause-fixed 是另一件事，不該被前兩者暗示已完成）。

**縫隙②：簡單功能被完整 EP 流程拖慢**（`mosaic_alpha/ai-analysis/flow-feedback/2026-06-15-indicators-reexport-refactor.md`，#1）。當前 `/execution-plan` 對所有規模套同樣結構（UC 盤點 + Scenario Matrix + 多段 + 收尾）。[execution-plan.md](../../commands/execution-plan.md) 段落設計（`:118-176`）有「大型/中型/小型」UC 引用差異，但**無正式「簡單功能不寫 EP」入口**。簡單功能（單檔 bug fix、小 tweak）被「過度流程化」。注意：[docs mode](../../commands/execution-plan.md)（`:178-199`）是 **product-type 分級**（code vs docs），非**規模分級** — 不解決 #1。

**共同根因**：execution-plan 的規劃精確度在兩端不足 — 大型 EP 的「兜底假設」缺路徑驗證（規劃層 over-claim），小型變更缺流程分級（流程層 over-engineering）。

**本 EP 範圍**（#13 + #1）：S1 兜底假設路徑驗證 + 用語區分、S2 流程分級。**Scope out**：#13 附帶的「judge-review 持久化位置（`.review/` gitignore）」（偏 judge-review 命令，獨立）、#1 的「import 盤點全面性 / 測試隔離」具體規範（屬測試 rules，非 EP 命令）。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | EP 兜底假設路徑驗證 + 「可觀測≠已修復」用語顯式化 | 無 |
| S2 | 流程分級（simple 不寫 EP / standard 輕量 / full 完整） | 無 |

兩段獨立、各自可驗收。S1 提升大型 EP 的規劃精確度；S2 為小型變更開輕量入口。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### Backlog 關聯
- 無直接 Backlog card（本 EP 源自 #13 + #1）。

### SYSTEM-MAP 影響
- 元專案無 SYSTEM-MAP.md（正當跳過）。

### 掃描範圍
- [commands/execution-plan.md](../../commands/execution-plan.md)（`:118-176` 段落設計、`:140-147` 驗證策略、`:27-92` UC 盤點規模、`:178-199` docs mode）
- [commands/build.md](../../commands/build.md)（`:30-34` 階段 0 EP 快檢）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 段落式實作計畫書（UC + Scenario Matrix + Self-Contained Segments） | `commands/execution-plan.md` | ✅ → S1 加兜底假設驗證、S2 加流程分級 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 簡單功能流程（不寫 EP，直接 TDD） | 📋 | `commands/execution-plan.md` S2（規模分級入口） |

---

## Scenario Matrix（中型變更，docs mode — 觸發/預期行為為文檔語境：rg 命中 / 模擬）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | EP 用「X 段落暴露/處理 Y」兜底 | EP 段落宣稱會暴露或處理某問題 | 必須驗證 X 的 code path 經過 Y（追 dependency/call chain）；不經過 → 標「未驗證」非「handled」，Y 須另開調查 | 無 | 段落計畫 |
| SM-2 | EP 用語涵蓋 visible 與 fixed | 段落用 `handled/exposed` | 「可觀測 ≠ 已修復」顯式區分：visible（S0 fail-loud）/ overlap-fixed（S6）/ root-cause-fixed 是三件事，不讓前兩者暗示根因已解決 | 無 | 段落計畫 |
| SM-3 | build 階段 0 EP 快檢 | EP 快檢掃兜底宣稱 | 對每個「暴露/處理」宣稱追問「這段落真的會碰到那個問題嗎？」— 路徑未驗證則 flag | 無 | 段落計畫 |
| SM-4 | 簡單功能（單檔 bug fix、小 tweak） | 變更單檔、行為明確、🟢 低風險 | 直接 TDD + 驗證，**不寫 EP**（流程分級 simple） | 無 | 簡單功能流程 |
| SM-5 | 中型（跨檔 feature） | 2-3 檔、🟡 中風險 | 輕量 EP（1-2 段，省 UC 盤點/Scenario Matrix/validate/review/judge） | 無 | 段落計畫 |

---

## S1: EP 兜底假設路徑驗證 + 「可觀測≠已修復」用語

### Context
- **背景**：#13 實證 — EP「S6 rebuild 暴露根因」假設 rebuild 經過失敗點，實際不經過（catalog 內部重聚合 ≠ SJ 寫入鏈）。規劃層的「測試路徑 ≠ 實際失敗路徑」。build 階段 0（`:30-34`）只 drift 快掃，沒驗證兜底路徑。
- **UC 引用**：更新既有「段落式實作計畫書」
- **依賴**：無
- **語義約束**：兜底假設驗證的是「**路徑是否經過目標**」（call chain），非「邏輯是否正確」（後者是實作層）— 規劃層只驗路徑觸及
- **依賴錨點**：`commands/execution-plan.md:140-147`（驗證策略段）、`commands/build.md:30-34`（階段 0 EP 快檢）
- **成功標準**：
  - [ ] execution-plan 段落設計加「兜底假設路徑驗證」：EP 若用「X 段落會暴露/處理 Y 問題」當兜底，**必須驗證 X 的 code path 經過 Y**（追 dependency / call chain，附 path:line）；不經過 → 標「未驗證」，Y 須獨立調查（另開 EP 或段落）
  - [ ] 「可觀測 ≠ 已修復」用語顯式化：EP 用語區分 `visible`（讓失敗可見）/ `overlap-fixed`（重複修）/ `root-cause-fixed`（根因解決）— 避免單一 `handled/exposed` 模糊涵蓋
  - [ ] build 階段 0 EP 快檢（`:30-34`）加此檢查：對每個「暴露/處理」宣稱追問「這段落真的會碰到那個問題嗎？」，路徑未驗證則 flag（计入「⚠️ N 項自行補充」）

### 修改要點
1. **`commands/execution-plan.md:140-147` 驗證策略段**：加「兜底假設路徑驗證」子項 — 「X 處理 Y」宣稱必須附 X→Y 的 call chain 證據；用語三區分（visible / overlap-fixed / root-cause-fixed）
2. **`commands/build.md:30-34` 階段 0**：EP 快檢加「兜底宣稱路徑追問」— 對「暴露/處理」宣稱驗證 code path 觸及，未驗證 flag

### 驗證策略（docs mode）
- **rg 閘門**：`rg "兜底假設|路徑驗證|可觀測.*已修復|visible.*overlap.*root" commands/execution-plan.md` → 命中
- **rg 閘門**：`rg "兜底|暴露.*處理|路徑.*碰到" commands/build.md` → 命中
- **`/consistency`**：跑兩檔
- **模擬（SM-1）**：給「EP 寫 S6 rebuild 暴露根因，但 rebuild 不碰 SJ」→ 確認驗證揭露路徑不經過、標未驗證
- **模擬（SM-3）**：給 build 階段 0 含「S0 處理 X」宣稱 → 確認快檢追問路徑

---

## S2: 流程分級（simple / standard / full）

### Context
- **背景**：#1 實證 — 簡單功能（indicators re-export 重構雖是架構級，但 #1 點出更廣問題）被完整 EP 流程套用。段落設計（`:118-176`）有「大型/中型/小型」UC 引用差異但無「簡單→不寫 EP」入口。docs mode（`:178-199`）是 product-type 分級（code vs docs），非規模分級。與 [ai-development-guide](../../ai-development-guide.md) 變更規模分級（小型 bug fix 不需 UC）未對齊。
- **UC 引用**：新增「簡單功能流程」
- **依賴**：無
- **語義約束**：分級判準 = **規模 + 風險**（單檔/跨檔/跨模組 × 低/中/高風險），非 product-type（docs mode 正交保留）
- **依賴錨點**：`commands/execution-plan.md:27-92`（UC 盤點，大型/中型必填）、`:118-176`（段落設計）
- **成功標準**：
  - [ ] execution-plan 加流程分級入口（建議放命令開頭「何時用 /execution-plan」段）：
    - **simple**（單檔 bug fix、小 tweak、🟢 低風險）→ 直接 TDD + 驗證，**不寫 EP**（走 `/build` 裸任務或直接實作）
    - **standard**（跨檔 feature、🟡 中風險）→ 輕量 EP（1-2 段，省 UC 盤點/Scenario Matrix/`/ep-validate`/review/judge）
    - **full**（架構、跨模組、🔴 高風險）→ 完整流程（spec → EP → validate → review → build → judge）
  - [ ] 分級判準機械化（檔案數 × 跨模組 × 風險等級），附範例
  - [ ] 與 ai-development-guide 變更規模分級對齊（小型 bug fix 不需 UC = simple 不寫 EP）

### 修改要點
1. **`commands/execution-plan.md` 開頭**加「流程分級」段（何時寫 EP、何時不寫）— simple/standard/full 三級 + 判準表 + 範例
2. 對齊 ai-development-guide 變更規模分級引用

### 驗證策略（docs mode）
- **rg 閘門**：`rg "流程分級|simple|standard|full|不寫 EP|輕量 EP" commands/execution-plan.md` → 命中
- **`/consistency`**：跑 `commands/execution-plan.md`（確認與 ai-development-guide 規模分級、docs mode 不衝突）
- **模擬（SM-4）**：給「單檔 bug fix、🟢 低風險」→ 確認判 simple、不寫 EP
- **模擬（SM-5）**：給「2-3 檔 feature、🟡 中風險」→ 確認判 standard、輕量 EP

---

## 收尾

- **受影響命令行為已反映**：execution-plan（兜底假設驗證 + 流程分級）、build 階段 0（兜底路徑追問）— `commands/CLAUDE.md` 索引 `/execution-plan` description 同步（補「規模分級入口；兜底假設路徑驗證」）。
- **Scope out**：#13 附帶「judge-review 持久化位置」（`.review/` gitignore → 決策改寫 kanban/EP review 區段，偏 judge-review 命令，獨立）、#1 的「import 盤點全面性（相對+絕對路徑）/ 測試隔離（禁 purge sys.modules）」（屬測試 rules / tests/CLAUDE.md，非 EP 命令本身）。
- **與 docs mode 正交**：S2 流程分級是**規模**維度（simple/standard/full），docs mode 是 **product-type**維度（code/docs）— 兩者正交，一個 EP 可同時是 standard + docs mode（跨檔 rules 改動）。`/consistency` 驗證此正交不衝突。
- **風險**：S2 simple「不寫 EP」可能被濫用（把該寫 EP 的中型變更降級）。緩解：判準機械化（檔案數 + 跨模組 + 風險），且 simple 仍須 TDD + 驗證（不是跳過品質，是跳過規劃文檔）。
