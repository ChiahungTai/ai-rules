---
name: metadata-sync
description: metadata finalization 單一真相源 — build 後的文檔狀態結算(模組 Capabilities 寫入——AGENTS.md 為主、CLAUDE.md legacy、Kanban 搬 Done、SYSTEM-MAP 生命週期、architecture.md、EP 歸檔、flow-feedback 歸檔、導航文檔 /consistency 閘門)。兩 mode(build 依情境結算 / standalone 補漏)。被 /build 階段5、/metadata-sync 共用 invoke。觸發詞：metadata finalization、commit 收尾、Capabilities 同步、Kanban 搬 Done、EP 歸檔、SYSTEM-MAP 更新、architecture.md、漏掉 finalization、build 完更新文檔、flow-feedback 歸檔、文檔狀態結算。
---

# Metadata Sync — metadata finalization 單一真相源

build 後的「文檔狀態結算」方法論（commit 不再內嵌 finalization）。把程式碼變更反映到專案導航文檔的**狀態層**(UC ✅、Kanban lane、SYSTEM-MAP 生命週期、EP 生命週期)——不是文檔「內容」同步(程式碼改 → 文檔描述改,那屬 [instruction-writing](../../rules/instruction-writing.md) 的職責,在 build 階段 5c 處理)。

**單一源**:本 skill 是 finalization 邏輯的唯一定義處。兩個 invoke 點(build 階段 5 結算 / standalone 補漏)共用,消除「同一邏輯散落多處 → drift」。

## 兩 mode(finalization 在 build 結算,commit 純提交)

| mode | 觸發者 | 職責 |
|------|--------|------|
| **build** | `/build` 階段 5 | 依情境結算(見情境矩陣)—— 結算是 working tree 編輯,不需 outward-action-consent(commit 場景) |
| **standalone** | `/metadata-sync`(獨立入口) | 偵測漏項/過時 → 補(commit 前更新 + 事後補漏共用) |

> **為什麼結算在 build 不在 commit**:finalization 是 working tree 編輯(改 CLAUDE.md / mv EP / 搬 Kanban),不是 git 寫入 —— build 階段 5 自主做,commit 退回純 git 提交(一次帶走 code + finalization)。舊設計(commit 階段 3 內嵌)對 LLM 是建議性、會漏跑(實證:commit 歷史多個「補漏」單獨 commit)。working tree 編輯沒 commit 就不永久,跟 code 一起 stash/checkout,不會「Capabilities 標 ✅ 但沒進 git」不一致 —— 真正風險是選擇性 commit(只 commit code 不 commit CLAUDE.md),靠 commit `git add` 納入 finalization 檔規範。

### 結算情境矩陣(build mode 核心 spec)

| # | 情境 | UC/EP 完成變化 | 結算動作 |
|---|------|--------------|---------|
| **A** | EP **最後段**,UC 全完成 | ✅ 新 UC + EP 完成 | **全項結算**(Cap+Kanban+SM 原子 + EP 歸檔 + flow-feedback 歸檔 + consistency) |
| **B** | EP **中間段** | ❌ UC 未全完成 | **預覽 only**(SM 📋→✅ Built,不寫 ✅、不升 Verified) |
| **C** | **純 refactor**(無新 UC) | ❌ | **跳過** |
| **D** | **docs-mode EP**(無 .py UC,EP 完成) | EP 完成、無 UC | **EP 歸檔 only**(無 Cap/Kanban) |

> deep-work `/build` 委派 build 全流程,繼承情境 A–D;deep-work 純 fix/debug(不走 build)= 情境 C 跳過。**code-review 後改 code**(UC 已結算過,入口可能變)= standalone mode 更新(冪等重跑);**事後發現漏結算** = standalone mode 補漏。

## finalization 項目(build mode 依情境執行子集)

| 項目 | 情境 | 做什麼 |
|------|------|--------|
| **Capabilities 寫入** | A | 對應模組 instruction 檔（AGENTS.md 為主，legacy CLAUDE.md）`## Capabilities` 表格新增 ✅ 行(格式 `\| 能力 \| 入口 \| 狀態 \|`,入口含 CLI + 函式路徑;見 [ai-development-guide](../../ai-development-guide.md)) |
| **消費場景寫入** | A | 從 EP Scenario Matrix 提煅引用該 UC 的場景為自包含一句話(不引用 EP/SM 編號),寫入 Capabilities 備註或 Kanban card |
| **Kanban 搬 Done** | A | 已完成 UC 的卡片從 active lane(In-Progress/Next-Up)移至 `Done/` |
| **SYSTEM-MAP 結算** | A | 受影響功能生命週期升級(`✅ Built → ✅🔍 Verified`,若有整合驗證);移除已修復 ⚠️;更新全域統計(若有) |
| **SYSTEM-MAP 預覽** | B | 中間段:生命週期 `📋→✅ Built`(全 UC ✅ + 測試通過 + build loop 收斂);**不升級 Verified**;loop 未收斂 → 阻止升級 + 標 ⚠️;**全域統計由情境 A 結算,預覽不動** |
| **architecture.md** | A(條件) | 本次涉及設計決策 / 原則 / 模組結構 / 新抽象層 → 同步更新對應段落;純 feature(不改設計)跳過 |
| **EP 歸檔** | A, D | **歸檔前查證（防 ghost-done）**：列 EP 交付物（UC盤點/收尾/各段 deliverable）逐項 rg/fd/Read 驗落地——「段落完成」≠ codebase 真有（曾發生整份 EP 100% ghost-done 誤歸檔）；有 ghost-done 不歸檔（補做或標 🔧）。全綠才歸檔 → `mv ai-analysis/execution-plans/<ep>.md _done/`;子目錄 EP 跨目錄 mv 到統一 `_done/`;綱要 EP(blueprint)等所有衍生子 EP 完成才歸檔 master |
| **flow-feedback 歸檔** | A | 本次實作解決的 `ai-analysis/flow-feedback/*.md`(root)→ `mv _done/`(`_done/` 不存在先建);討論中 / 未解決的不歸檔。**判斷是 judgment 非機械**(feedback↔change 非 1:1,不像 EP↔段落明確)→ forgetting 風險靠兩段式執行的「展示清單 + 用戶確認」把關(同 standalone mode) |
| **consistency 閘門** | A, B, D | 對本次動過的 AGENTS.md / CLAUDE.md / architecture.md / SYSTEM-MAP.md 逐一跑 `/consistency`(單檔內部自洽);🔴 / 🟡 inconsistency → 修正後才算完成 |

### SYSTEM-MAP 生命週期推導(共用規則)

| 條件 | 狀態 |
|------|------|
| 功能內 UC 全 ✅ + 有整合驗證 | ✅🔍 Verified |
| 全 ✅ 但無整合驗證 | ✅ Built |
| 有 📋 / 🔧 | ⚠️ Issues 或 📋 Planned |

build 情境 A 憑整合驗證升 Verified;情境 B(中間段)只到 Built 預覽。

## standalone 偵測維度(獨立入口核心智能)

`/metadata-sync`(standalone mode)用於 **commit 前更新**(code-review 後 code 變了)或**事後補漏** —— 兩者都從現狀推導「哪些 finalization 漏了 / 過時」:

| 漏項 | 偵測方式 |
|------|---------|
| EP 歸檔漏 | `ai-analysis/execution-plans/` root 有「所有段落已 commit 但未歸檔」的 EP(git log 比對 EP 段落 vs commit 訊息) |
| Capabilities 漏 | git log 近期 commit 的 UC vs 該模組 instruction 檔（AGENTS.md 為主，legacy CLAUDE.md）`## Capabilities` 表(已 commit UC 但表內無對應 ✅ 行) |
| Kanban 漏 | `.kanban/In-Progress/` 有「已完成但未搬 Done」的卡片(卡片 UC 已在 Capabilities ✅) |
| SYSTEM-MAP 漏 | SYSTEM-MAP 生命週期 vs Capabilities 狀態不一致(**消費 `/doc-health` findings,不重造偵測**) |
| architecture.md 漏 | 近期 commit 涉及設計變更(新模組 / 新抽象 / 依賴方向調整)但 architecture.md 對應段落未更 |
| flow-feedback 漏 | `ai-analysis/flow-feedback/` root 有已解決但未歸檔的 feedback |

## 兩段式執行(build / standalone 共用)

1. **偵測 → 展示清單**:build mode 依情境矩陣列該做的結算項;standalone mode 列漏項/過時項
2. **用戶確認**:遵循 [outward-action-consent](../../rules/outward-action-consent.md) 精神——finalization 改的是永久導航狀態,須確認(build 階段 5 結算在 build 流程內確認;standalone 獨立確認)
3. **執行**:寫入 / 搬移 / 歸檔
4. **consistency 閘門**:對動過的導航文檔跑 `/consistency`

> **原子性**:build 情境 A 的「Capabilities 寫入 + Kanban 搬 Done + SYSTEM-MAP 結算」必須同時完成(三者描述同一 UC 的狀態,部分完成 = 狀態不一致誤導 LLM)。architecture.md 更新 / EP 歸檔 / flow-feedback 歸檔**非原子**(各自獨立條件時序,與三件狀態結算平行)。standalone 補漏/更新不要求原子(補的是各自獨立的漏項)。

## 容錯(兩 mode 共用)

無對應檔案 → 該項跳過不報錯(容錯是方法論的一部分,定義於此單一源,兩 mode 共用):

| 缺漏 | 跳過項 |
|------|--------|
| 無 SYSTEM-MAP.md | SYSTEM-MAP 預覽 / 結算(如 ai-rules 元專案無 SYSTEM-MAP) |
| 無 `.kanban/` | Kanban 搬 Done |
| 無 architecture.md | architecture.md 條件更新 |
| 無 `ai-analysis/flow-feedback/` | flow-feedback 歸檔 |

> `/metadata-sync` command 不重列容錯(指向本段,單一源)。

## 與既有邊界

- [`/doc-health`](../../commands/doc-health.md):**檢查 / 報告**(問「文件準確嗎」),消費 scan findings + LLM 讀取驗證,含 `--sync-system-map`。本 skill 是**執行修補**(問「finalization 該做的做了嗎,沒做就補」)。SYSTEM-MAP 偵測消費 doc-health findings,不重造。
- [`/consistency`](../../commands/consistency.md):**單檔內部自洽**(術語 / 章節 / 引用 / 邏輯 / 格式)。本 skill 的 consistency 閘門 invoke 它,非重造自洽邏輯。
- [`kanban-board`](../kanban-board/SKILL.md):看板卡片**通用 CRUD 工具**。本 skill 的「Kanban 搬 Done」是綁定 build 結算語意的特定操作(可用 kanban-board 的移動能力執行)。
- [`/audit-test`](../../commands/audit-test.md):**測試品質**稽核(反模式 / 覆蓋 / mock)。與文檔 metadata 正交。
- build 階段 5c(instruction 檔 / arch **內容**同步):反映程式碼變更到文檔描述(導航-A 種子、模組職責),屬 [instruction-writing](../../rules/instruction-writing.md) 職責,**非**狀態結算;與本 skill 結算在同一段 5 協調(5a 結算寫 ✅ 行、5c 同步描述)。

## 不適用

- 文檔**內容**同步(程式碼改 → 描述改)→ build 階段 5c + [instruction-writing](../../rules/instruction-writing.md)
- 單檔內部自洽檢查 → `/consistency`
- 文件準確性 / 過時 / drift 報告 → `/doc-health`
- 看板通用操作(非 build 結算)→ `kanban-board`
