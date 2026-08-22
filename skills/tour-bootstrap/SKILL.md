---
name: tour-bootstrap
description: "Repo Tour Bootstrap——把任意 repo 變成可走讀狀態（三層 corpus：Overview Tour 地圖層／Chain Tour 場景層／Delta Tour 時間層）的程序 skill，建在 code-reality 工具鏈之上。何時跑：使用者說「bootstrap 這個 repo 的 tour」／新 repo 冷啟動要導覽／要產 overview tour。含 .tour link 語言契約、機械驗證清單、唯一斷點（AI 輔助生成 callchain 文檔）。"
when_to_use: "Bootstrapping tour corpus for any repo (user says \"幫我 bootstrap 這個 repo 的 tour\"), authoring an Overview Tour (short isPrimary version), converting callstack docs to chain tours, or validating .tour links/anchors. Prerequisite detection: repo 有無 callstack 文檔決定完整三層或 overview-only 最小形態。"
argument-hint: "<repo-root>（要 bootstrap 的 repo；省略即 cwd repo）"
allowed-tools: ["Read", "Bash", "Write", "Edit", "Grep", "Glob"]
---

# Repo Tour Bootstrap（repo 導覽建置程序）

一句話：使用者說「**幫我 bootstrap 這個 repo 的 tour**」→ 產出三層 corpus → 使用者「**走讀**」它（裝 CodeTour vsix，panel 點開即走）。

**分層**：工具層＝[code-reality](../code-reality/SKILL.md)（chain_tour／delta_tour CLI、repo profile）；本 skill＝程序層（工具的編排、`.tour` 語言契約、驗證、停點設計）。能力命名體系：Repo Tour Bootstrap（能力）／Overview·Chain·Delta Tour（三層產物）／Walkthrough 走讀（消費）。**delta 層不在本程序產出**——由 `delta_tour` CLI 在 commit 走讀時按需重產（7 天窗），bootstrap 只負責其目錄版控契約（步驟 1）。

## 前置偵測（決定 corpus 形態）

| 偵測 | 有 | 無 |
|---|---|---|
| callstack 文檔（人寫場景敘事，如 `ai-analysis/blueprint/callstack-v1/`） | **完整三層**（overview＋chain＋delta） | **overview-only 最小形態**（斷點③） |
| `.code-review-graph/graph.db`（chain_tour 重錨的實際開關） | chain_tour 帶 graph 重錨統計 | 純文檔錨退化（不擋） |
| `.tours/` 既有內容 | 盤點前例（產出形態對照、版控契約現況） | 全新 |

## 程序（五步）

1. **盤點**：`.tours/` 現況、文檔源（root／模組 AGENTS.md 群、架構文檔、SYSTEM-MAP）、`.gitignore` 對 `.tours` 的契約。⚠ **arch 進版控是契約變更**（預設 `.tours/` 常被整目錄排除）——改 `.tours/` → `.tours/delta/`（delta 7 天窗不版控不變）＋前例補追蹤，`git check-ignore` 雙向驗證，需用戶知情。
2. **場景層**（有 callstack 文檔才做）：`uv run --project ~/Github/ai-rules python -m code_reality.chain_tour <md> --repo <repo> --out-dir <repo>/.tours/arch/<stem>/`（**不傳 `--primary`**——primary 專屬 overview）。驗收：產出檔數＝文檔場景數（場景＝含樹狀幀的 code block）；重錨分佈統計記錄；每條抽樣 ≤5 步 `line`+`pattern` 與源碼 def 對齊。0-step tour（描述殼）保留但勿連入。
3. **地圖層**：overview 短版（10–14 步、`isPrimary: true`、檔名 `00 - <repo> 總覽.tour`）骨架＝開場（contents 步無檔）＋分層地圖 4–6 步（**錨模組 AGENTS.md h1**，description=職責一句抄自該檔＋file link）＋資料入口 1–2 步（代表檔 `line`+`pattern` 雙錨）＋場景目錄步（tour link）＋開發工作流步＋收尾。長版可選（30–40 步、`00b - `）。**資料源紀律：只引用既有文檔宣稱，不自行發明敘事**——內容錯誤可追溯到文檔源。
4. **`.tour` 語言契約**（消費端 CodeTour 的正則決定，寫錯＝死鏈）：
   - `line` = **1-based**（player 內部 −1）
   - `pattern` = literal-ish regex（`^…$` 行錨定；行漂移時 pattern 最近命中校正，零命中顯性標未驗證）
   - **tour link**＝`[顯示名][匹配鍵#N]`（顯示名可省——單方括號也是合法形式，正是下條誤判的源頭）；markdown `( )` 形式被排除＝死鏈；**匹配鍵**＝title 剝 `^#?\d+\s-` 前綴**且在第一個 ASCII `-` 截斷**（`getTourTitle` 的 `split("-")[1]` quirk——title body 避 ASCII 連字號，撞鍵時 link 落第一條）
   - **file link**＝`[文字](./相對路徑)`——路徑以 `.` 開頭才觸發走讀欄 pinned tab（`./` 為慣例形態）
   - description 內**禁其他裸方括號**（會被誤判為 tour link）
   - `NN - ` 前綴限系列 tour 且**必須補零**（`01 - `）——非補零 `1 - ` 會被 player 誤判 primary；`isPrimary` 限 overview 短版（冷啟動直達＋panel star 置頂）
5. **機械驗證**（初稿產出時＋策展定稿後各一次）：全檔 JSON parse／tour link 匹配鍵逐字對齊＋步號存在（用上述剝前綴演算法算鍵，非肉眼）／file link 路徑存在／自有步 line+pattern 與源碼行對齊。

## 停點設計

初稿產出即**停**——AI 不代終審（敘事品質是使用者策展職責）；使用者裝 vsix 邊走邊改；策展定稿後重跑機械驗證（編輯會引入壞 link／壞 JSON，走查只暴露走到的步）。收尾產 `.tours/README.md`（三層說明＋慣例＋再產 CLI 一行）。

## 斷點③（未解）

**AI 輔助生成 callchain 文檔**——場景層輸入是人寫場景敘事，新 repo 沒有 → overview-only。生成程序（graph／code 結構 → AI 草擬 → 人審）待更多案例沉澱後設計；現階段誠實標記而非跳過。

## 已驗證案例

- **mosaic**（完整三層——規格源）：`~/Github/mosaic_alpha_offline_backtesting/ai-analysis/execution-plans/ep-mosaic-tour-bootstrap.md`
- **codetour**（overview-only 最小形態）：`~/Github/codetour/.tours/00 - codetour 總覽.tour`
