# EP: /illustrate 從 use case 重構 mode 架構

> **ep_type**: implementation
> **動機來源**: 整脊讓 /illustrate 成為結構 viewport 載體,但 mode/步驟分界不清(見樹不見林:內部能力被誤當 mode)。本 EP 從**使用者日常開發 use case** 出發,歸納高層 mode,重構決策流程為 **mode 驅動**(非內部能力觸發),並加 use cases + 情境矩陣分析步驟。

## 動機（self-contained 背景）

整脊 S2 後,/illustrate 有多個能力(結構 viewport / EP 審查 / 變更圖解 / 概念圖解),但決策流程是「內部能力觸發」導向,沒有從使用者 use case 歸納的高層 mode。結果:

- **見樹不見林**:把內部能力(city map/EP 審查)誤當 mode,實際上能力跨 use case 共用(city map 服務「設計決策」也服務「審查重造」),能力 ≠ mode。
- **mode/步驟混淆**:use cases 分析 + 情境矩陣是「步驟」(可被 mode 組合),不是新模式。
- **缺高層 mode**:/illustrate 該從使用者意圖(設計/理解/審查/溝通)組織,非從內部能力。

**本 EP 方法論**(Clean Arch + DDD 應用到命令設計):use case → 情境矩陣 → 歸納 mode → survey 能力 → 下沉 skill → 每 mode 拉共用 → 編排流程。

**Scope out**:不動 architecture-viewport skill(整脊 S1 已下沉,跨命令共用);不改其他命令。

---

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| **S1** | use cases + 情境矩陣(含 SM-8 commit 前)+ 新 supporting `illustrate-analysis.md`(use cases/情境矩陣分析**步驟**) | 無 |
| **S2** | mode 歸納(4 mode)+ illustrate.md 決策樹改 **mode 驅動** + survey/下沉明文 + 每 mode 流程編排 | S1 |

2 段序列(分析步驟先 → mode 重構)。

---

## UC 盤點（docs mode — 元專案無 Capabilities 表格）

### 既有 UC 狀態
| 能力 | 入口 | 狀態 |
|------|------|------|
| 圖解技術概念/架構/流程 + 結構 viewport | `commands/illustrate.md` | ✅ → 本 EP 從 use case 重構 mode(決策樹 mode 驅動)+ 加分析步驟 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| use cases + 情境矩陣分析步驟(服務 mode A/C) | 📋 | `commands/claude/_common/illustrate-analysis.md`(S1) |

---

## Scenario Matrix（中型變更，docs mode）

| SM | use case | mode | 觸發時機 | 輸入 | /illustrate 手段 | 預期 |
|----|---------|------|---------|------|----------------|------|
| SM-1 | UC-1 設計決策 | A 設計 | 討論新功能/重構 | 設計描述/@模組 | city map + 流程 + 重用枚舉 | 結構提案,人判讀 |
| SM-2 | UC-1/UC-4 | A 設計 | pre-EP 定案前 | 對話討論 | 結構催化(軟 gate) | 方向確認 |
| SM-3 | UC-2 理解既有 | B 理解 | 接手/學習/除錯 | @模組/概念 | 運作流程/資料流/概念圖 | 人理解 |
| SM-4 | UC-3 審查驗證 | C 審查 | code-review 前 | 無參數(git diff) | 語義 diff + 缺口 | 變更影響可見 |
| SM-5 | UC-3 審查驗證 | C 審查 | EP 審查 | @ep | 假設驗證矩陣 | EP 假設 drift 浮現 |
| SM-6 | UC-3 審查驗證 | C 審查 | 懷疑重造/漂移 | @變更範圍 | city map + 重用枚舉 | 重造盲點浮現 |
| SM-7 | UC-5 溝通傳達 | D 溝通 | 寫文檔/demo | 主題 | md Mermaid | 可分享圖 |
| SM-8 | UC-3 審查驗證 | C 審查 | **code-review 完、commit 前** | 無參數(git diff) | 語義 diff + 缺口 | commit 前確認變更全貌 |

---

## S1: use cases + 情境矩陣 + illustrate-analysis.md（分析步驟）

### Context
- **背景**:use cases + 情境矩陣是**分析步驟**(非模式),服務 mode A(設計決策)/C(審查驗證)。新 supporting `illustrate-analysis.md` 定義這兩個分析步驟的方法。**此檔定義「產出情境矩陣」的步驟方法;EP 開頭的 Scenario Matrix(SM-1~8)即此步驟的一次產出(本 EP 的 SM)** — 非 兩個不同東西。
- **語義約束**:**步驟非模式** — use cases/情境矩陣是 mode 可組合的分析動作,不是新模式。避免「見樹不見林」(把分析當 mode)。
- **依賴錨點**:無(新 supporting)
- **成功標準**:
  - [ ] 新檔 `commands/claude/_common/illustrate-analysis.md`:定義 **use cases 分析步驟**(從使用者日常開發出發,非命令內部)+ **情境矩陣分析步驟**(從 use cases 抽 SM:觸發/輸入/手段/預期)
  - [ ] 標明「步驟,可被 mode A/C 組合」(非模式)
  - [ ] [illustrate.md](../../../commands/illustrate.md) supporting files 表加此檔 + 何時讀取(use cases / 情境矩陣分析時;**mode 用語 S2 統一**,S1 時點用中性用語避免前向引用)

### 修改要點
1. **新檔 `illustrate-analysis.md`**:use cases 分析(從使用者日常,高層)+ 情境矩陣(從 use cases 抽)。明文「分析步驟,服務 mode A/C」
2. **illustrate.md supporting files 表**:加此檔

### 驗證策略（docs mode）
- **rg 閘門**:`rg "use cases 分析|情境矩陣|從使用者日常|分析步驟" commands/claude/_common/illustrate-analysis.md` → 命中

---

## S2: mode 歸納 + 決策樹 mode 驅動 + survey/下沉 + 流程編排

### Context
- **背景**:從情境矩陣歸納 4 mode(A 設計/B 理解/C 審查/D 溝通)。illustrate.md 決策樹從「內部能力觸發」改「mode 驅動」。survey 現有能力 + 下沉明文(整脊已下沉結構 viewport,其他留 illustrate 體系)。每 mode 編排流程(共用步驟 + 特有)。
- **語義約束**:**mode = 高層意圖(從 use case 歸納),非內部能力**。能力跨 mode 共用(city map 服務 A 也服務 C)。下沉標準:跨命令共用才沉(整脊已沉結構 viewport;假設驗證/diff/analysis 是 illustrate 特有,留 supporting/本體,不過度下沉)。
- **依賴錨點**:[illustrate.md](../../../commands/illustrate.md) 決策流程段、核心能力段、委託 skills 段
- **成功標準**:
  - [ ] **mode 歸納**(4 mode):A 設計決策(SM-1/2)/ B 理解既有(SM-3)/ C 審查驗證(SM-4/5/6/8)/ D 溝通傳達(SM-7)。明文「mode = 意圖,能力 = 手段(跨 mode 共用)」
  - [ ] **決策樹改 mode 驅動**:從「結構 viewport 觸發 / @ep / md」(內部能力)改「判斷 use case → mode → 組合步驟」。輸入(@ep/@dir/無參數/主題)是 mode 判斷線索(客觀輸入,非「相容保留」— ai-rules 預設不考慮向後相容,演化性重構)
  - [ ] **survey/下沉明文**:列出能力 + 位置(skill/supporting/本體)+ 下沉標準(跨命令共用才沉)。整脊已沉 architecture-viewport;其他留
  - [ ] **每 mode 流程編排**:共用步驟(讀 code + 渲染 + 調 skill)+ mode 特有步驟(city map/diff/假設驗證/概念圖)
  - [ ] [commands/CLAUDE.md](../../../commands/CLAUDE.md) /illustrate description 反映 mode 導向(若需)

### 修改要點
1. **illustrate.md**:核心能力段改 mode 歸納(4 mode,意圖導向);決策樹改 mode 驅動;加 survey/下沉明文段;每 mode 流程編排
2. **commands/CLAUDE.md** /illustrate description(若需反映 mode)
3. **[illustrate-deep-analysis.md](../../../commands/claude/_common/illustrate-deep-analysis.md)**:EP 審查模式(假設驗證矩陣,L64-88)標注歸屬 **mode C(審查驗證)**,與 illustrate.md mode C 流程對齊(避免 mode 驅動後兩處脫鉤)

### 驗證策略（docs mode）
- **rg 閘門**:`rg "mode 驅動|設計決策|理解既有|審查驗證|溝通傳達|能力跨 mode 共用|下沉標準" commands/illustrate.md` → 命中
- **`/consistency`**:跑 illustrate.md(確認 mode/步驟/能力分界自洽)

---

## 收尾

### 受影響索引同步
- [commands/CLAUDE.md](../../../commands/CLAUDE.md):/illustrate description(若反映 mode)— S2 處理
- [skills/CLAUDE.md](../../../skills/CLAUDE.md):無(無新 skill;分析步驟留 supporting)

### 風險與緩解
- **mode 歸納主觀**:4 mode 切分可能調整 → Scenario Matrix 是客觀基礎(use case 浮現 mode),非憑空切
- **決策樹改動無相容包袱**:ai-rules 預設不考慮向後相容(無外部系統依賴舊邏輯)。輸入(@ep/無參數/主題)是 mode 判斷線索,非相容保留 — 該乾淨重構就乾淨重構
- **過度下沉**:只跨命令共用才沉 → 明文下沉標準,analysis/diff/假設驗證留 illustrate(特有)
- **mode/步驟再混淆**:S1 明文「分析步驟非模式」+ S2 明文「mode = 意圖,能力 = 手段」— 三層分界(use case → mode → 步驟/能力)
