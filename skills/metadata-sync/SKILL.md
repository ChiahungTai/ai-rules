---
name: metadata-sync
description: metadata finalization 單一真相源 — build/commit 後的文檔狀態結算(CLAUDE.md Capabilities 寫入、Kanban 搬 Done、SYSTEM-MAP 生命週期、architecture.md、EP 歸檔、flow-feedback 歸檔、導航文檔 /consistency 閘門)。三 mode(build 進度預覽 / commit 結算 / standalone 補漏)。被 /commit 階段3、/build 階段5、/metadata-sync 共用 invoke。觸發詞：metadata finalization、commit 收尾、Capabilities 同步、Kanban 搬 Done、EP 歸檔、SYSTEM-MAP 更新、architecture.md、漏掉 finalization、build 完更新文檔、flow-feedback 歸檔、文檔狀態結算。
---

# Metadata Sync — metadata finalization 單一真相源

build/commit 後的「文檔狀態結算」方法論。把程式碼變更反映到專案導航文檔的**狀態層**(UC ✅、Kanban lane、SYSTEM-MAP 生命週期、EP 生命週期)——不是文檔「內容」同步(程式碼改 → 文檔描述改,那屬 [claude-writing](../../rules/claude-writing.md) 的職責,在 build 階段 5c 處理)。

**單一源**:本 skill 是 finalization 邏輯的唯一定義處。三個 invoke 點共用,消除「同一邏輯散落多處 → drift」(重構前 SYSTEM-MAP 更新在 build+commit 兩處各自帶邏輯即此病)。

## 三 mode(解 build vs commit 時序張力)

| mode | 觸發者 | 執行子集 | 狀態性質 |
|------|--------|---------|---------|
| **build** | `/build` 階段 5 | 消費場景提煅(暫存供 commit 寫入)+ SYSTEM-MAP 進度預覽(`📋→✅ Built`,**不升級 Verified**) | 暫時(build 可能不 commit) |
| **commit** | `/commit` 階段 3 | 全部項目,**原子操作** | 永久(結算) |
| **standalone** | `/metadata-sync`(獨立入口) | 偵測漏項 → 補漏(可能只補一兩項,不要求原子) | 補救 |

> **build mode 邊界**:只做「暫時狀態」子集(SYSTEM-MAP 進度預覽 + 消費場景提煅),**不做** Capabilities 寫入 / Kanban 搬 Done / EP 歸檔 / flow-feedback 歸檔(那些是 commit 結算;build 提前做會造成「Capabilities 標 ✅ 但沒 commit」的永久狀態與程式碼不一致)。build 後進度可見性(`/standup`、`/task-status`)靠 SYSTEM-MAP 預覽提供。

## finalization 項目(commit mode 全集;build mode 子集標 ✅)

| 項目 | mode | 做什麼 |
|------|------|--------|
| **消費場景提煉** | build | 從 EP Scenario Matrix 提煉引用該 UC 的場景為自包含一句話(不引用 EP/SM 編號),暫存供 commit 寫入 |
| **SYSTEM-MAP 預覽** | build | 讀 SYSTEM-MAP.md,受影響功能生命週期 `📋→✅ Built`(全 UC ✅ + 測試通過 + build loop 收斂);**不升級 Verified**;loop 未收斂 → 阻止升級 + 標 ⚠️;**全域統計由 commit 結算,build 預覽不動** |
| **Capabilities 寫入** | commit | 對應模組 CLAUDE.md `## Capabilities` 表格新增 ✅ 行(格式 `\| 能力 \| 入口 \| 狀態 \|`,入口含 CLI + 函式路徑;見 [ai-development-guide](../../ai-development-guide.md)) |
| **消費場景寫入** | commit | build 提煉的消費場景寫入 Capabilities 備註或 Kanban card |
| **Kanban 搬 Done** | commit | 已完成 UC 的卡片從 active lane(In-Progress/Next-Up)移至 `Done/` |
| **SYSTEM-MAP 結算** | commit | 受影響功能生命週期升級(`✅ Built → ✅🔍 Verified`,若有整合驗證);移除已修復 ⚠️;更新全域統計(若有) |
| **architecture.md** | commit(條件) | 本次涉及設計決策 / 原則 / 模組結構 / 新抽象層 → 同步更新對應段落;純 feature(不改設計)跳過 |
| **EP 歸檔** | commit | 本次為 EP 最後段落(所有段落已 commit)→ `mv ai-analysis/execution-plans/<ep>.md _done/`;子目錄 EP 跨目錄 mv 到統一 `_done/`;綱要 EP(blueprint)等所有衍生子 EP 完成才歸檔 master |
| **flow-feedback 歸檔** | commit | 本次 commit 解決的 `ai-analysis/flow-feedback/*.md`(root)→ `mv _done/`(`_done/` 不存在先建);討論中 / 未解決的不歸檔 |
| **consistency 閘門** | commit | 對本次動過的 CLAUDE.md / architecture.md / SYSTEM-MAP.md 逐一跑 `/consistency`(單檔內部自洽);🔴 / 🟡 inconsistency → 修正後才算完成 |

### SYSTEM-MAP 生命週期推導(共用規則)

| 條件 | 狀態 |
|------|------|
| 功能內 UC 全 ✅ + 有整合驗證 | ✅🔍 Verified |
| 全 ✅ 但無整合驗證 | ✅ Built |
| 有 📋 / 🔧 | ⚠️ Issues 或 📋 Planned |

build mode 只到 `Built`(預覽);commit mode 憑整合驗證升 `Verified`。

## standalone 偵測維度(獨立入口核心智能)

`/metadata-sync` 無明確 commit context,從現狀推導「哪些 finalization 漏了」:

| 漏項 | 偵測方式 |
|------|---------|
| EP 歸檔漏 | `ai-analysis/execution-plans/` root 有「所有段落已 commit 但未歸檔」的 EP(git log 比對 EP 段落 vs commit 訊息) |
| Capabilities 漏 | git log 近期 commit 的 UC vs 該模組 CLAUDE.md `## Capabilities` 表(已 commit UC 但表內無對應 ✅ 行) |
| Kanban 漏 | `.kanban/In-Progress/` 有「已完成但未搬 Done」的卡片(卡片 UC 已在 Capabilities ✅) |
| SYSTEM-MAP 漏 | SYSTEM-MAP 生命週期 vs Capabilities 狀態不一致(**消費 `/doc-health` findings,不重造偵測**) |
| architecture.md 漏 | 近期 commit 涉及設計變更(新模組 / 新抽象 / 依賴方向調整)但 architecture.md 對應段落未更 |
| flow-feedback 漏 | `ai-analysis/flow-feedback/` root 有已解決但未歸檔的 feedback |

## 兩段式執行(commit / standalone 共用)

1. **偵測 → 展示清單**:本次該做哪些項目 / 漏了哪些(standalone)。commit mode 列結算項;standalone mode 列漏項
2. **用戶確認**:遵循 [commit-consent](../../rules/commit-consent.md) 精神——finalization 改的是永久導航狀態,須確認
3. **執行**:寫入 / 搬移 / 歸檔
4. **consistency 閘門**:對動過的導航文檔跑 `/consistency`

> **原子性**:commit mode 的「Capabilities 寫入 + Kanban 搬 Done + SYSTEM-MAP 結算」必須同時完成(三者描述同一 UC 的狀態,部分完成 = 狀態不一致誤導 LLM)。architecture.md 更新 / EP 歸檔 / flow-feedback 歸檔**非原子**(各自獨立條件時序,與三件狀態結算平行)。standalone 補漏不要求原子(補的是各自獨立的漏項)。

## 容錯(三 mode 共用)

無對應檔案 → 該項跳過不報錯(容錯是方法論的一部分,定義於此單一源,三 mode 共用):

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
- [`kanban-board`](../kanban-board/SKILL.md):看板卡片**通用 CRUD 工具**。本 skill 的「Kanban 搬 Done」是綁定 commit 結算語意的特定操作(可用 kanban-board 的移動能力執行)。
- [`/audit-test`](../../commands/audit-test.md):**測試品質**稽核(反模式 / 覆蓋 / mock)。與文檔 metadata 正交。
- build 階段 5c(CLAUDE.md / arch **內容**同步):反映程式碼變更到文檔描述(導航-A 種子、模組職責),屬 [claude-writing](../../rules/claude-writing.md) 職責,**非**狀態結算;不在本 skill 範圍。

## 不適用

- 文檔**內容**同步(程式碼改 → 描述改)→ build 階段 5c + [claude-writing](../../rules/claude-writing.md)
- 單檔內部自洽檢查 → `/consistency`
- 文件準確性 / 過時 / drift 報告 → `/doc-health`
- 看板通用操作(非 commit 結算)→ `kanban-board`
