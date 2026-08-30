---
name: ui-visual-verify
description: UI 開發/健檢驗收編排配方。觸發詞：UI 驗收、視覺健檢、UI 視覺驗證、playwright 截圖、截圖判讀、DOM 量測、盲判讀、UI component 瀏覽器測試、flash lane。三鏈合流：app 啟動（port 錯開＋就緒判定）→ playwright 截圖＋shadow DOM 機械量測 → vision-review agent 盲判讀 → findings 合流；確定性契約沉澱 pytest，LLM 判讀 opt-in 不入 hard gate。與 ui-collab 分工＝驗收期 vs 互動期。
---

# UI 視覺驗證（ui-visual-verify）

> UI 開發/健檢**驗收**的編排配方：視覺狀態（截圖）＋幾何鐵證（DOM 量測）＋獨立判讀（vision-review 盲判讀）三鏈合流，findings 沉澱為元件測試。

## 定位與邊界

- 與 [ui-collab](../ui-collab/SKILL.md)：ui-collab＝**互動期**協作（Monitor `[ACTION]` 操作日誌、行為時序、用戶在場操作）；本 skill＝**驗收期**編排（機器截圖＋量測＋盲判讀，人不需在場）。同一 app 可先後兩用（開發互動期 ui-collab → 交付驗收本 skill）
- 與 vision-review agent：本 skill 是**編排層**（決定截什麼、量什麼、怎麼引導判讀）；agent 是**判讀層**（讀圖對照預期回報差異）
- 證據分層：DOM 量測＝L4 機械鐵證（幾何數字可直接成 finding）；盲判讀＝獨立 LLM 判讀（抓 orchestrator 沒預期的副作用——Writer/Reviewer 分離在 UI 軸的收益）

## 流程總覽

啟動 → 截圖 → DOM 量測 →（互動驗證 → re-find → 再截圖）→ 盲判讀 spawn → findings 合流（DOM 證據 × 判讀觀察交叉）→ 確定性契約沉澱 pytest

## 啟動

- 背景執行、port 錯開（並行 session 不撞）、log 落 `.agent-tmp/<run>/`
- **就緒判定＝port listen**（`lsof -nP -iTCP:<port> -sTCP:LISTEN`），**非僅 log 行**——factory serve 形態（session callback 建構）首個瀏覽器連線才 build session，process ready ≠ session ready；連線後 wait 渲染完成再操作
- 產物（截圖/metrics）集中 `.agent-tmp/<run>/`——playwright 截圖預設落 cwd root，截完搬移（該目錄須在 gitignore 內）

## 截圖要點

- **viewport 須涵蓋目標元素中心**——tooltip/floating 元件常在 fold 下，不在 viewport 內就截不到
- fullpage 高度可能被 body min-height 夾住（scrollHeight ≠ 實際內容高度）——fullpage 不必然等於全內容
- **前後對照**（互動前後同視角各一張）是抓預期外副作用的基本功

## DOM 量測（L4 鐵證）

- **shadow DOM 遞迴 walk**——naive `querySelectorAll` 漏 shadow root 內元素（Bokeh/Tabulator 全在 shadow DOM），canvas 計數同理（naive 查詢回 0）
- overflow 基準用**固定 viewport 寬**——`clientWidth` 受垂直 scrollbar 出現與否影響
- metrics JSON 與截圖並存——量測出數字、截圖供判讀，兩者交叉才成 finding
- 框架 class 名匹配用 case-insensitive regex——class 命名大小寫隨版本變（如 Bokeh 3.x `bk-Tooltip` 大寫 T），精確匹配會漏

## 互動驗證

- **互動後 DOM refs 全過期**（互動觸發元件 rebuild，如 group toggle → 全圖 rebuild）→ 每次互動後 re-find 再截圖，禁跨互動 ref 重用
- locator 穿透 open shadow DOM＋auto-scroll **優先於座標 click**；無 a11y label 的框架 widget 靠可見文字錨多跳定位
- Range/CDS 斷言以 **server 端 model id 錨定**（如 `figure.x_range.id` 傳進 JS）——幾何/量級推測會撞隱藏碰撞（其他 pane 的 range 值域與目標量級重疊時偽裝成目標，如 RSI y_range (0,100) 偽裝 x range）
- attach 後 mutation 走 framework doc-lock（marshal 路徑）——測試 thread 裸 mutate 觸發 RuntimeError 是 crash-only 如設計，不是 bug
- `evaluate` 只收單一 arg（陣列不會解構成多參數）
- **UI 元件 YAGNI 判定：零直呼 ≠ 零消費**——UI 元件常經內部工廠鏈渲染（無外部 caller 但每張圖都建）；判 dormant 前先追工廠鏈（filter trap 的 UI 變體。真實案例：mosaic kchart `create_all_buttons` 無外部直呼但經 `from_behaviors` 工廠鏈活躍渲染，兩輪 AI 審查皆誤判、二次查證才翻案）

## 盲判讀 spawn 模板

spawn vision-review（背景），prompt 要點：

- **給**：use case 動線說明（這畫面給誰、做什麼決策）、預期描述（畫面應有哪些元素/行為）、截圖清單（含前後對照組）
- **不給**：已知缺口清單——引導偏差，盲判的價值在抓 orchestrator 沒預期的
- **預期描述須 code＋instruction 檔雙源核對**——過時文檔直接污染判讀 prompt（真實案例：mosaic ui/AGENTS.md drift 把窗格數寫錯，判讀預期跟著錯、險些反過來被當成 finding）
- 判讀回報「預期與實牆不符」→ **先懷疑預期**（drift 機率不低），code 查證後再定 finding 歸屬
- 多輪追加的 findings report，「最終/現況」結論須帶**時間錨**（標明屬哪輪範圍）——末節易沉積過時結論

## 測試端整合（shift-left）

健檢是一次性的；其中的**確定性契約**（幾何不溢出、渲染到達 client、range 不變）沉澱為 pytest 元件測試：

- 元件級 host：最小 layout 直掛目標元件（真依賴、剝離 app 殼），秒級跑完進 build 迴圈
- **flash lane（opt-in）**：env flag 開時測試落截圖＋metrics JSON 產物 → 供 vision-review 盲判讀消費；**LLM 判讀不入 hard gate**（成本＋非確定性，gate 會飄）
- silent-skip 防護：real-browser 測試線依賴 browser binary 與 playwright 版本同步——升級 playwright 未重裝 browser → 整線 silent skip、綠燈零覆蓋；nightly/regression 加「browser 線 skipped 數 > 0 即 WARN」機械檢查
- 真實案例：mosaic `tests/integration_tests/ui/browser/test_kchart_component.py`（元件直掛 host 三契約＋flash lane 範本）
