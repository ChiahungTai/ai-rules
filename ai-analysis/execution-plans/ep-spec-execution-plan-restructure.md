# EP: /spec 與 /execution-plan 職責邊界重組

> **ep_type**: implementation
> **規模**: standard（跨 ~10 檔 command/skill 文檔重構）
> **mode**: docs（純 `.md` 變更，無 `.py` callable；`scan-project/scripts/*.py` 為 pre-existing 工具，不在變更範圍）

## 實作總覽

重組 `/spec` 與 `/execution-plan` 的職責邊界，解決「spec 太重常被跳過 → 全域研究/POC/UC 偷工流失」的痛點。核心是**從人性出發**：人走阻力最小的路，所以把有價值的重東西放必走的 EP、把 spec 瘦身為輕量需求釐清。

**重組後新流程**：
```
/spec (輕: User Story + UC定位 + SM + 邊界)  ← 純輔助·需求釐清
  → /execution-plan (自足: 段落0全域研究[含風險假設] + UC盤點[建卡] + SM + 段落[驗證策略含前期POC] + EP Review)
    → [/ep-validate] (EP 後深度驗證, 維持不變)  ← 可選
      → /build → [/code-review] → /commit
```

**四個結構性改變**：
1. spec 瘦身為需求釐清（阻力降 → 更可能用）
2. EP 段落 0 加全域研究（人必走 EP → 研究/風險識別一定執行）
3. spec UC盤點刪除（EP 超集，去冗餘）
4. spec P3 前期 POC 融入 EP 段落驗證策略（前期探索歸必走路徑；`/ep-validate` 不動）

**設計理由（arch bounded context 重新切分）**：
- spec = **What**（需求：User Story / UC定位 / SM / 邊界）
- EP = **How**（實作規劃：全域研究 / UC盤點建卡 / 段落 / 驗證）
- 下游消費關係，非重複。spec 純輔助 = 有它 EP 更快，沒它 EP 自足。

---

## UC 盤點

> docs mode：元專案無 library Capabilities 表格，UC 盤點 = 受影響命令/rules 清單。

### Backlog 關聯
- 掃描 `.kanban/Backlog/`：4 張卡片（docs-mode-adaptation-audit / mechanical-gate-philosophy-hybrid / observe-commit-settlement-finding-gap / observe-review-optional-usage）皆與本次無關
- 自動建卡：本次為 command 重構（非新能力），**不另建 Backlog 卡片**（元專案 command 改造追蹤以 EP 本身為準）

### SYSTEM-MAP 影響
- `SYSTEM-MAP.md` 無 spec/EP/命令流程區塊（元專案追蹤 mosaic 之類功能，非命令）→ **正當跳過**

### 掃描範圍
- `commands/spec.md`、`commands/execution-plan.md`、`commands/build.md`、`commands/CLAUDE.md`、`commands/illustrate.md`、`commands/code-review.md`、`commands/ep-review.md`、`commands/deliverable-review.md`
- `skills/spec-driven-development/SKILL.md`
- `CLAUDE.md`、`ai-development-guide.md`

### 受影響命令清單（docs mode「UC」）
| 命令/skill | 角色 | 變更 |
|-----------|------|------|
| `/spec` | 需求釐清（重定位）| **重寫**：瘦身，刪研究/POC/UC盤點 |
| `/execution-plan` | 實作規劃（自足化）| **修改**：加段落0全域研究 + 強化驗證策略 + 去「基於 spec」 |
| `spec-driven-development` skill | spec 方法論 | **修改**：POC 段歸屬調整（POC 非 spec 職責）|
| `/ep-validate` | EP 後深度驗證 | **職責不動**（明確邊界 Never）；文檔微調（分工段 spec→EP 段落驗證策略，見 S4）|
| 流程圖含 spec 的命令（build/code-review/ep-review/deliverable-review/illustrate/CLAUDE/commands:CLAUDE）| 一致性 | spec 標純輔助 |
| `ai-development-guide` UC 生命週期 | 方法論 | 建卡職責 spec → EP |

---

## Scenario Matrix

> docs mode：觸發/預期行為改文檔語境（rg 殘留/0 命中），非程式執行。

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 中型需求，用 spec 釐清後跑 EP（happy）| `/spec` 產出 UC+SM → `/execution-plan` | EP 引用 spec 產出、跳過需求層重做；段落0 全域研究仍執行 | spec 產出被 EP Context 引用 | spec 需求釐清 / EP 自足 |
| SM-2 | 中型需求，跳過 spec 直接 EP（常見路徑）| 對話討論 → `/execution-plan`（無 spec）| EP **自足**：自己做全域研究 + UC盤點 + SM，不缺 spec 也能完整規劃 | `rg "規格摘要.*生成\|基於.*規格摘要" commands/execution-plan.md` = 0 殘留（pattern 收窄，避免誤判「基於需求討論（`/spec`...）」）| EP 自足 |
| SM-3 | 高風險需求，需前期可行性 POC（邊界）| EP 段落設計遇高風險技術假設 | EP **段落驗證策略**含前期 POC（吸收原 spec P3）；深度驗證走 `/ep-validate` | execution-plan 段落設計標準第4點含「前期 POC」 | EP 段落驗證策略 |
| SM-4 | spec 被誤用為「研究/POC 工具」（錯誤路徑）| 用戶期待 spec 做全域研究/POC | spec 文檔**不再宣稱**這些職責；引導至 EP（研究）/ `/ep-validate`（POC）| `rg "codebase 研究\|POC 可行性\|全域研究" commands/spec.md` = 0 殘留（作為 spec 自身職責）| spec 邊界清晰 |
| SM-5 | 跨檔流程圖 drift（一致性）| 重組後舊流程圖未同步 | 所有流程圖 spec 標「純輔助」、無「基於 spec」殘留 | ripple pattern 掃描全清（見 S4 驗證）| 文檔一致性 |

---

## 段落劃分原則

**依賴圖**（執行順序）：
```
S1 (spec 重寫) ──┐
                 ├─語義耦合─→ S3 (skill POC) ─┐
S2 (EP 自足) ────┘                            ├─→ S5 (收尾)
                 └──────────→ S4 (流程圖一致性)┘
```

- **S1、S2 語義耦合**：spec 刪除的 P2/P3/P4 由 EP 接手。共享語義約束（見下）。建議先 S1 定義 spec 新形，再 S2 接手，避免漏接。
- **S3 依賴 S1**：skill POC 段調整取決於 spec 不再做 POC。
- **S4 依賴 S1/S2**：流程圖一致性需知道新流程長怎樣。
- **S5 收尾**：依賴所有段落。

**語義約束（段落間共享，顯式標記）**：
- **與 S1 共享**「spec 刪除 → EP 接手」對應表：P2全域研究→EP段落0、P3前期POC→EP段落驗證策略、P4 UC盤點→EP UC盤點（超集，已存在）。S1 刪除時 S2 必須有對應落點，否則價值流失。
- **與 S2 共享**「EP 自足」：EP description/內文不得宣稱「基於 spec」（否則 SM-2 失敗）。
- **與 S4 共享**「spec 純輔助」統一表述：流程圖用「spec（純輔助·需求釐清）」或「spec 可選」，禁用「基於 spec」。

---

## S1: /spec 瘦身重寫為需求釐清

### Context
- **UC 引用**：重定義 `/spec` 命令職責（需求釐清）
- **依賴關係**：與 S2 語義耦合（刪除的東西由 EP 接手）；與 S3 耦合（spec 不做 POC → skill 調整）
- **語義約束**：與 S2 共享「spec 刪除 → EP 接手」對應表
- **基礎設施盤點**：spec 現有 5 Phase 結構（spec.md:33-156）；委託 spec-driven-development skill（假設浮出/邊界/成功條件量化保留）
- **成功標準**：spec 只剩需求層（User Story + UC定位 + SM + 邊界 + 規模判定），無研究/POC/UC盤點殘留

### 修改要點（docs mode，無 pseudo code）
1. **description（spec.md:2）**：去「codebase 研究 + POC 可行性驗證」，改「需求釐清（User Story + UC定位 + Scenario Matrix + 邊界 + 規模判定），為 EP 做需求層準備」
2. **frontmatter when_to_use（:3）/ usage（:4）/ argument-hint（:5）**：去 `--research-only`；usage 改 `/spec [需求描述] [--write]`
3. **參數表（:22-25）**：刪 `--research-only` 行；留 `--write`；無參數預設改「對話中產出需求摘要（UC + SM + 邊界）」
4. **Phase 重組**：原 5 Phase → 需求釐清 流程
   - 保留並強化：Phase 1 對齊（User Story + 範圍 + 規模判定）
   - **刪 Phase 2**（spawn Explore 全域研究）→ 標註「全域研究已移至 /execution-plan 段落 0」
   - **刪 Phase 3**（假設 + POC）→ 標註「前期 POC 已移至 EP 段落驗證策略；深度驗證在 /ep-validate」
   - 保留並強化：UC 定位（需求要什麼能力）+ Scenario Matrix（需求層場景）+ 邊界（Always/Ask First/Never）
   - **刪 Phase 4 的 UC盤點建卡**（EP 超集）→ 保留「UC 定位」（需求層：要實現什麼能力），但建卡/掃 codebase 既有 UC 歸 EP
   - Phase 5 產出：需求摘要（User Story + UC + SM + 邊界）
5. **「與 /ep-validate 的分工」表（:188-200）**：刪除（spec 不再做 POC，無分工可比）
6. **流程位置（:202）**：spec 標「純輔助·需求釐清」
7. **委託 Skills（:14-15）**：spec-driven-development 保留（假設浮出/邊界/成功條件）；移除「POC 可行性」相關委託
8. **規格摘要格式（:168-182）**〔EP Review A5 補〕：模板含「現有基礎設施」「已驗證假設（含 POC 結果）」「技術決策」三段，資料來源是已刪除的 Phase 2/3 → **刪除這三段**；保留 User Story / UC 引用 / 邊界；產出改名「需求摘要」（不再用「規格摘要」，避免暗示含研究/POC 結果）

### 依賴錨點（docs mode file:line）
- `spec.md:2` description / `:3-5` frontmatter / `:22-25` 參數表 / `:33-156` Phase 結構 / `:168-182` 規格摘要格式 / `:188-200` 分工表 / `:202` 流程位置

### 驗證策略（docs mode）
- **rg 殘留**：`rg "codebase 研究|POC 可行性|--research-only|spawn Explore" commands/spec.md` → **0 hits**
- **rg 殘留**：spec.md 不得將「全域研究」「POC」「UC盤點建卡」描述為自身職責
- **規格摘要格式**〔A5〕：`rg "已驗證假設|現有基礎設施|技術決策|規格摘要" commands/spec.md` → 確認三段已刪、產出改名「需求摘要」
- **/consistency** spec.md 自洽（新流程內部一致）

---

## S2: /execution-plan 自足化

### Context
- **UC 引用**：強化 `/execution-plan` 自足能力（全域研究 + 前期 POC + 去 spec 依賴）
- **依賴關係**：與 S1 語義耦合（接手 spec 刪除的 P2/P3）；UC盤點已存在（:56-120，確認是 spec P4 超集）
- **語義約束**：與 S1 共享「接手」對應表；description/內文不得「基於 spec」
- **基礎設施盤點**：EP 現有 UC盤點（:56-120，含自動建卡=spec P4 超集）、段落設計標準（:147-177）、流程規模分級（:42-53）
- **成功標準**：EP 自足（無 spec 也能完整規劃）+ 段落0 全域研究 + 段落驗證策略含前期 POC

### 修改要點
1. **description（execution-plan.md:2）**：去「基於 /spec 規格摘要」，改「自足段落式實作計畫書（含段落0 全域研究 + UC盤點 + Scenario Matrix + EP Review）」
2. **開頭（:10）**「基於 `/spec` 的規格摘要」→ 改「EP 自足生成段落式實作計畫書（`/spec` 為純輔助需求釐清，有則引用其 UC/SM；無則自產）」〔避免「基於...spec」句式，配合 SM-2 pattern 收窄〕
3. **新增段落 0：全域研究**（放在 UC盤點之後、段落劃分原則之前，作為所有段落的研究前提）
   - spawn Explore Agent（model 依 model-routing 降一級）
   - 盤點：可複用基礎設施、依賴關係、類似實作（原 spec Phase 2 內容）
   - **風險假設識別**：列出高風險技術假設，標注由哪個段落的驗證策略 POC 驗證
   - **深度上限**〔A4〕：研究摘要層級（可複用元件清單 + 風險假設），**非 codebase 全景報告**——避免 EP 膨脹
4. **段落設計標準第 4 點驗證策略（:169-177）**：強化「前期 POC」— 明確段落驗證策略含「高風險假設的可行性 POC（吸收原 spec P3）」，並引用 validation-strategy skill
5. **Context 背景資訊（:153）**「基於 `/spec` 規格摘要」→ 改「基於需求討論（有 spec 則引用 spec 的 UC/SM）」
6. **流程規模分級 full（:50）**：仍含 `/spec` 但標「純輔助」
7. **流程位置（:352,355）**：spec 標純輔助

### 依賴錨點
- `execution-plan.md:2` description / `:10` 開頭 / `:42-53` 流程規模分級 / `:56-120` UC盤點（確認超集）/ `:147-177` 段落設計標準（加全域研究 + 強化驗證策略）/ `:153` Context / `:350-356` 流程位置

### 驗證策略（docs mode）
- **rg 殘留**：`rg "基於.*spec|規格摘要" commands/execution-plan.md` → **0 hits**（改為「需求討論」）
- **新增段落存在**：rg "段落 0|全域研究" execution-plan.md → 命中（新段已加）
- **驗證策略強化**：rg "前期 POC|可行性 POC" execution-plan.md → 命中
- **/consistency** execution-plan.md

---

## S3: spec-driven-development skill POC 段歸屬調整

### Context
- **UC 引用**：調整 spec 方法論 skill 的 POC 歸屬
- **依賴關係**：依賴 S1（spec 不做 POC）
- **語義約束**：skill 通用方法論（specify→plan→tasks→implement 四階段）保留；僅 POC 段歸屬調整
- **定位說明**〔C3〕：skill 是**通用 spec-first 方法論**（任何專案可用，六區塊 spec 範本 + gated workflow 是方法論本體），**非 `/spec` 命令專屬**。`/spec` 命令重組為需求釐清 後，只取 skill 的 Phase 1 Specify 子集（假設浮出 + 邊界 + 成功條件量化）。**不擴大改 gated workflow**（通用方法論不該因 ai-rules 命令重組而改）；僅在 skill 加註此定位，避免讀者誤以為 skill 與命令 1:1 對應
- **基礎設施盤點**：skill「POC Verification Mode」（SKILL.md:192-229）+「Relationship with /ep-validate」（:227-229）
- **成功標準**：skill 不再宣稱 POC 是 spec 階段職責；指向 EP/ep-validate

### 修改要點
1. **「POC Verification Mode」段（:192-229）**：改寫為「POC 不在 spec 階段」說明 — 可行性 POC 在 EP 段落驗證策略（見 /execution-plan），深度驗證在 /ep-validate。或刪除此段並改為指向連結
2. **「Relationship with /ep-validate」（:227-229）**：更新為「spec 不做 POC；EP 段落驗證策略做可行性 POC，/ep-validate 做深度驗證」
3. **frontmatter description（:3）/ When to Use（:14-18）**：若提及 POC 驗證則移除（POC 非 spec 職責）
4. **Overview（:10）**：spec 是「需求 shared source of truth」定位保留（符合需求釐清）

### 依賴錨點
- `SKILL.md:2-3` frontmatter / `:10` Overview / `:14-20` When to Use / `:192-229` POC Verification Mode / `:227-229` Relationship

### 驗證策略（docs mode）
- **rg 殘留**：`rg "POC Verification Mode|/spec.*identify high-risk|spec.*POC" skills/spec-driven-development/SKILL.md` → 確認已改寫或移除
- **/consistency** skill 自洽

---

## S4: 跨檔流程圖 + 方法論一致性

### Context
- **UC 引用**：文檔一致性（流程圖 spec 定位 + UC 生命週期建卡職責）
- **依賴關係**：依賴 S1/S2 新定位
- **語義約束**：與 S1/S2 共享「spec 純輔助」統一表述
- **基礎設施盤點**：見查證清單（10 處流程圖 + UC 生命週期）
- **成功標準**：所有流程圖 spec 標記統一、無「基於 spec」殘留、UC 生命週期建卡歸 EP

### 修改要點（逐檔）
| 檔案:行 | 現況 | 改為 |
|--------|------|------|
| `CLAUDE.md:49` | spec 命令受眾表 | spec 定位註記「需求釐清」（受眾仍 LLM 人互動）|
| `commands/CLAUDE.md:22` | `/spec（含 UC 定義 + POC 可行性驗證，spec 可選前置）` | `/spec（純輔助·需求釐清，spec 可選）` |
| `commands/CLAUDE.md:33` | spec description「結構化需求討論 + codebase 研究 + POC 可行性驗證」 | 「需求釐清（User Story + UC定位 + SM + 邊界）」；去 `--research-only` |
| `commands/CLAUDE.md:34` | EP「基於 /spec 生成」 | EP「自足（含段落0全域研究 + UC盤點）」 |
| `commands/build.md:36` | `前置流程確認：/spec → /execution-plan` | `/spec（純輔助·可選）→ /execution-plan（自足）` |
| `commands/build.md:274` | 流程圖含 spec | spec 標純輔助 |
| `commands/illustrate.md:100` | 「EP 必備、spec 可選」 | 微調「spec 純輔助·需求釐清（可選）」|
| `commands/code-review.md:186` | 流程圖 `/spec → /execution-plan` | spec 標純輔助 |
| `commands/ep-review.md:207` | 流程圖 | spec 標純輔助 |
| `commands/deliverable-review.md:225` | 流程圖 | spec 標純輔助 |
| `ai-development-guide.md:64` | UC 生命週期「📋（/spec → Backlog card）」 | 「📋（/execution-plan → Backlog card）」（建卡職責歸 EP）|
| `ai-development-guide.md:90` | 「大型：/spec 必須建立 Kanban Backlog card」 | 「大型：/execution-plan 自動建卡」（EP 已有自動建卡）|
| `ai-development-guide.md:96` | 「/spec → Backlog：建立 card」 | 「/execution-plan → Backlog：自動建卡」|
| `commands/ep-validate.md:25-36`〔C1〕 | 「與 /spec POC 的分工」整段（表格左欄 `/spec POC`）| 「與 EP 段落驗證策略（前期 POC）的分工」；左欄改 `EP 段落驗證策略 POC`。`:82,:130` 提及 /spec 處同步；`:194` 流程圖 spec 標純輔助 |
| `skills/kanban-board/SKILL.md:132-137,159`〔C4〕 | 「/spec 整合」段教 spec 討論完成時建卡 | 「/execution-plan 整合」；建卡歸 EP UC盤點自動建卡機制 |

### ripple 語義反向撈（本變更屬「職責重定位/術語統一」類，觸發）
逐檔枚舉之外補機械掃描，撈 LLM 想不到的檔：
1. **spec 舊職責描述（定義源 + 使用處）**：`rg "codebase 研究|POC 可行性|結構化需求討論"` — 所有自稱 spec 做 研究/POC 的地方
2. **EP 對 spec 依賴宣稱**：`rg "基於.*spec|規格摘要"` — 所有「EP 基於 spec」殘留
3. **流程圖 spec 定位**：`rg "/spec.*可選|spec.*前置|spec 可選前置|spec →"` — 流程圖 spec 標記，逐一比對是否已改「純輔助」
4. **UC 生命週期建卡**：`rg "/spec → Backlog|spec.*Backlog card|/spec.*建.*卡|/spec 整合|/spec.*建立卡片|spec.*完成時"` — 建卡職責是否仍誤歸 spec〔C4 補：覆蓋「/spec 整合」標題寫法〕

### 依賴錨點
- 見上表 file:line（rg 驗證行號指向預期內容）

### 驗證策略（docs mode）
- **rg 殘留**：上述 ripple pattern 在變更範圍 → **0 hits**（或已改為新表述）
- **跨檔一致性**：所有流程圖的 spec 標記統一為「純輔助」
- **確認不需改**〔C6〕：`audit-test.md:200`（泛指規格非命令職責）、`flow-feedback.md`/`flow-review.md`（spec 作流程入口，純輔助不改語義）、`voice-notification`（列 spec 為耗時任務，無職責宣稱）— 已確認非 spec 職責宣稱，正當不動
- **/consistency** 抽查 CLAUDE.md、commands/CLAUDE.md、ai-development-guide.md

---

## S5: 收尾

### Context
- **依賴關係**：依賴 S1-S4 全部完成
- **成功標準**：命令索引同步、文檔驗證全綠、ripple 全清

### 修改要點
1. **`commands/CLAUDE.md` 命令索引**：spec + execution-plan 兩行 description 同步（與 S4 :33-34 一致，此處為收尾確認）
2. **`skills/CLAUDE.md` skill 索引**：spec-driven-development description 若因 S3 改動，同步索引行
3. **文檔驗證**：對所有變更檔跑 `/consistency`（自洽性、矛盾、引用有效性）

### 驗證策略（docs mode）
- **機械掃描總收**：S4 的 4 組 ripple pattern 跨整個 repo 再跑一次 → 0 殘留
- **/consistency** 對 spec.md、execution-plan.md、ai-development-guide.md（核心三檔）
- **/audit-test**：跳過（docs mode 無測試）

---

## 整合策略

- **語義耦合驗證**：S1（spec 刪）+ S2（EP 接）完成後，必須對照「刪除→接手」對應表逐一確認落點：P2→EP段落0、P3→EP驗證策略、P4→EP UC盤點。任一漏接 = 價值流失（SM-3/SM-4 失敗）。
- **一致性總驗**：S4 ripple 掃描是跨所有段落的整合驗證，須在 S1-S3 後跑，確認無殘留。
- **dogfooding**：本 EP 自身用重組「前」的流程生成（重組未落地）；重組落地後，未來 EP 應直接體現「EP 自足、spec 純輔助」。

---

## 收尾步驟（/build 階段 5 執行）

> docs mode 收尾：元專案無 Capabilities/Kanban/SYSTEM-MAP UC 操作；改為命令索引 + 文檔驗證。

1. **命令索引同步**：`commands/CLAUDE.md` 的 spec + execution-plan description 反映新職責（S5）
2. **CLAUDE.md 更新**：`CLAUDE.md` 命令受眾表 spec 定位 +（若有）流程圖段落一致
3. **文檔驗證**：`/consistency` 對核心變更檔；ripple pattern 全清
4. **/audit-test**：跳過（docs mode 無測試變更）

---

## EP Review Cycle（已執行）

> **執行**：spawn 1 個獨立 Explore agent（GLM, model inherit, read-only），docs mode 審查（文檔一致性 + 設計合理性 + 引用 drift + 漏改）。
> **結果**：錨點（B 維度）全部準確 0 drift；設計（A1-A3）成立。抓 2 Critical + 2 Important + 2 Suggestion，judge-review **全數採納**，已 apply。

### Finding Record

| ID | 嚴重度 | finding | judge | apply 位置 |
|----|--------|---------|-------|-----------|
| A5 | Critical | spec Phase 5 規格摘要格式（:168-182）含「已驗證假設/基礎設施/技術決策」，S1 刪 P2/P3 後失資料來源，未說明處理 | ✅ 採納 | S1 修改要點 +8、依賴錨點 +`:168-182`、驗證策略 +規格摘要 rg |
| C1 | Critical→Important | ep-validate.md:25-36「與 /spec POC 的分工」段重組後指向不存在的 spec 職責；「ep-validate 不動」前提須精確化為「職責不動、文檔微調」 | ✅ 採納 | UC 盤點表 /ep-validate 行、S4 表 +ep-validate.md |
| C7 | Critical | SM-2 rg `"基於.*spec"` 過寬，會誤判 S2 改寫後「基於需求討論（`/spec`...）」| ✅ 採納 | SM-2 Checkpoint pattern 收窄、S2 修改要點 2 避免「基於...spec」句式 |
| C3 | Important | spec-driven-development skill gated workflow（六區塊）與新 spec 命令（需求釐清）斷裂 | ✅ 部分 | S3 +定位說明（skill 是通用方法論，/spec 取子集，**不改 gated workflow**）|
| C4 | Important | kanban-board SKILL.md:132-137「/spec 整合」建卡段漏改 | ✅ 採納 | S4 表 +kanban-board SKILL.md、ripple pattern 4 補 |
| A4 | Suggestion | EP 段落0 全域研究缺深度上限，恐膨脹 | ✅ 採納 | S2 修改要點 3 +深度上限 |
| C6 | Suggestion | audit-test/flow-*/voice-notification 確認不需改，宜註明 | ✅ 採納 | S4 驗證策略 +確認不需改 |
| B1-B4 | — | 錨點全準確 0 drift | — | 無需改（品質亮點）|

> **未採納**：無。所有 finding 合理採納。
> **C1 特註**：修正了討論期共識「/ep-validate 不動」——精確化為「**職責不動**（與共識一致），文檔分工段微調（分工對象 spec→EP 段落驗證策略）」。已向使用者說明。

---

## Code Review Findings（layer 2 post-review judge）

> /spec 重組 code-review → /judge-review 評估。3 findings 全採納；rg 殘留全綠。

| ID | 嚴重度 | 檔案:行 | 問題 | 決策 | 處置 |
|----|--------|---------|------|------|------|
| F1 | Important | execution-plan.md:80 | 「格式見 /spec 階段 3 卡片格式」斷裂（spec 已刪該格式） | ✅ 採納 | 改指向 kanban-board/SKILL.md「建立卡片」段（模板完整：[tag:module]/目標/相關/驗收/備註） |
| F2 | Suggestion | CLAUDE.md:71 / ep-validate:82 / flow-review:3 / flow-feedback:96 | 殘留「/spec → /build」略 EP（重組後 EP 必走、自足） | ✅ 採納 | 補 /execution-plan（大改，必要時先 /spec 釐清需求）/ kanban（小改）→ /build |
| F3 | Suggestion | voice-notification:3/:27 | /spec 列為耗時分析任務（spec 現為輕量需求釐清） | ✅ 採納 | /spec 移出分析任務清單（/execution-plan 留，為耗時規劃） |

**全採納，無 ❌。** F1 是斷裂引用（EP 自足化 UC 盤點建卡會指向不存在內容）；F2/F3 是 spec 重組後的舊表述殘留。
