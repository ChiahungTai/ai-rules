---
harness-scope: neutral
---

# 驗收證據階層

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## 核心原則:證據獨立性

傳統 TDD 的權威性建立在一個從未被明說的前提:測試的「意圖」與實作的「理解」分屬不同認知主體。人類寫測試表達需求(程式碼之外),實作面對機械世界,兩者的張力就是驗收的來源。

**AI 同時寫實作與測試時,這個獨立性塌縮。** 測試從「人類意圖的權威表達」降級為「AI 對自己理解的描述」,測試通過從「人類意圖被滿足」降級為「AI 內部自洽」。最危險的不是測試太弱,而是測試與實作共享同一個錯誤前提 — AI 若誤解問題,它寫的測試忠實反映誤解,實作忠實滿足誤解,綠燈只在證明「AI 自洽地重複了自己的錯」。

**判斷準則**:驗收證據的強度,取決於「證據來源是否獨立於被驗證物」。AI 同寫 test + impl = 零獨立性 = 證據強度低。

## 核心原則(續):認知誤差與 EP 的預見極限

證據獨立性解決「驗證者的偏誤」(AI 不能自己驗自己),但解決不了「驗證基準本身可能是錯的」。**規劃層(EP)是人類 + AI 對需求理解的最佳猜測,不是真理**。兩種認知誤差只能在實作呈現時被發現:

- **實作落差**:實作層發現規劃層沒預見的 — EP 的 pseudo code 看起來對,接起來才發現邊界、副作用、組件互動。
- **設計本身錯**:使用者一開始的設計就錯,看到實作呈現才理解 — 「我以為我要的是這個,看到成品才知道不是」。

**Agent Review 解決「球員兼裁判」(同 LLM 審自己),但對認知誤差無效** — review agent 再獨立,審的基準仍是 EP,而 EP 可能從根上錯。問題不在「實作對不對 EP」,而在「EP 和它背後的預期對不對」。

### 對 build 的啟示:EP 是收斂方向,不是合約

- **前線實作 LLM 有裁量權**:實作時發現 EP 的問題(規劃層預見極限外的真相),可調整。這不是「偷懶不照 EP」,而是「實作層有發現真相的責任」 — 死守 EP 會實作一個「忠實但錯誤」的東西,反而妨礙人類在呈現時發現認知誤差。
- **仍要架構化**:實作接近 EP(避免失控)+ 記錄偏差(可追溯)。
- **呈現是唯一觸發器**:認知誤差只能靠「實作呈現給人類判讀」(L6)揭露。沒有可觀察的呈現,認知誤差永遠潛伏 — 這是 B 軸人類驗收層不可省略的根本理由。

## 證據階層

「功能完成」不是布林值,是證據債券 — 不同驗證手段產生不同強度的證據,覆蓋不同 bug 類別:

| 層 | 證據形式 | 抓什麼 bug | AI 造假風險 | 風險映射 |
|--|--|--|--|--|
| L1 靜態 | type check / ruff / ast.parse | 語法、型別契約 | 不能(機械執行) | 🟢 低 |
| L2 單元 | unit test(含 mock) | 函式內部邏輯 | **最易**(同義反覆、mock 假設即 bug、測試反映實作) | 🟡 中 |
| L3 整合 | integration(真實 DB / 跨模組 fixture) | 組合契約、跨檔擴散、FK 約束 | 可能 mock 掉關鍵邊界 | 🟡 中 |
| L4 可執行 demo | 真實跑腳本 / 資料片段 | **AI 幻覺 API、第三方程式庫真實行為** | 不能(程式真的跑了),但會選擇性跑 happy path | 🔴 高(外部依賴) |
| L5 對抗性 POC | 刻意用髒資料 / 邊界 / 已知陷阱 | **AI 對邊界的盲區**(除權息、減資、NaN、時區、溢出) | 若 POC 標的也是 AI 挑,會潛意識避開自己盲區 | 🔴 高(數據完整性) |
| L6 人類觀察 | 人在迴圈看真實輸出 / 畫面 / log | **需求誤解**(AI 正確實作了錯誤的理解) | 不會誤信 PASS,但會「看一眼就夠」 | 單向門決策 |

**根本禁令**:用低層證據冒充高層驗收是核心錯誤 — 不是「測不夠多」,而是「用錯層的證據」。現有零散禁令統一解釋為這個原則的不同表現:

| 既有禁令 | 冒充關係 |
|--|--|
| [must-execute](./must-execute-before-complete.md) 禁 ast.parse 取代執行 | L1 冒充 L4+ |
| [quality-constraints](./quality-constraints.md) 禁隔離 unit test 宣稱功能完成 | L2 冒充 L3+ |
| test-driven-development skill 警告過度 mock | L2 的獨立性被掏空 |
| 消費端驗證模式(見 quality-constraints) | L3 的具體化 |

### L3 整合層的正向價值實例(為什麼整合測試值得)

**理論呼應**:"mock 循環論證讓 mock 假設成為 bug 來源"(見 quality-constraints 整合器型變更)。以下實例顯示補整合測試如何**立刻**抓到 mock 抓不到的 source bug。

**實例(真實案例 — DB 序列重置函式)**:

- **audit 發現**:restore flow 新增的 DB 序列重置函式(`pg_get_serial_sequence` + `setval` 動態 SQL),屬整合器型變更(DB catalog + serial sequence + restore flow),但整合測試零覆蓋。
- **補整合測試**(真實 PostgreSQL,跑 restore → reset → INSERT):**立刻崩潰**。
- **source bug**:空 table 時 `setval(seq, COALESCE(MAX(id), 0))` → `setval(seq, 0)`,但 SERIAL 的 `MINVALUE=1`,`setval(seq, 0)` 違反約束 → fresh DB restore 後第一次 INSERT 崩潰。
- **為什麼 mock 抓不到**:mock 假設「table 有資料,MAX 有值」,整個邊界(空 table)不在 mock 的假設世界裡。mock 循環論證讓這個假設成為 bug 來源。

**啟示**:整合器型變更(接 ≥2 真實外部組件)補整合測試不是「儀式」,是**唯一能抓跨組件邊界 bug 的手段**。理論見品質約束「整合器型變更判定」;判定流程見 audit-test 角度 4(Claude command,跨 harness 路徑從略)。

### 重構查證義務:上抬抽象層的 filter trap(通用重構紀律)

> **適用範圍超出整合器型變更** — 任何「移除補丁 / 上抬抽象層」重構都適用。此段放在 L3 整合層下,是因為 filter trap 的測試角度(mock 偽造 real code 不會算的值)接 L3 證據理論,但**重構查證義務本身是行動紀律,不限整合測試場景**。

**機制(為什麼這類重構會回歸)**:「上抬抽象層」重構 = 把 logic 從 consumer 移到 producer(移除 consumer 補丁,改由 producer 統一處理)。直覺假設「producer 能處理 case X → 移除補丁後 case X 仍被處理」。**這個假設漏了一層**:producer 能處理 **≠** producer 會收到 — caller chain 中間的 filter 會阻斷 case 到達 producer。

```
consumer 補丁處理 case_X（原狀）
  ↑ 重構：移除補丁，producer 已加 case_X 處理
  ↓ 假設：producer 會接到 case_X
producer 的 case_X 處理（從沒被觸發 — 死碼）
  ← caller filter 全擋掉 case_X（重構者沒查）
  → 移除補丁後 case_X 完全消失
```

**查證義務(移除補丁前必須執行)**:對 producer(被上抬的抽象層)做 LSP `findReferences` 找所有 caller,逐個讀其 filter 邏輯(條件分支、guard、type narrowing),確認 case 真流入 producer。**禁假設「producer 能處理 = producer 會收到」** — 這個等式只在「無 filter」的直連 caller 成立,真實 codebase 的 caller 幾乎都有 filter。

**與 YAGNI check([collaboration-constraints](./collaboration-constraints.md))的差異**:YAGNI 是「搜用量 → 沒用 → 移除」;filter trap 是「**code 有用、但 caller chain 中間的 filter 阻斷 case 到達 producer**」。YAGNI 往「刪」走,filter trap 往「驗證不能刪」走 — 方向相反。YAGNI 的 `findReferences` 查「誰引用」;filter trap 的 `findReferences` 查「誰引用 + 其 filter 是否阻斷 case」— 多一層 filter 邏輯查證。

**測試假信心(為什麼測試會給綠燈)**:移除補丁後,測試可能 mock 掉 producer 的真實 caller chain,直接偽造 case_X 傳入 producer → producer 處理成功 → 綠燈。但真實 runtime 的 caller filter 把 case_X 擋掉了,producer 從沒收到 → 死碼 → 補丁移除等於功能消失。**對「移除補丁」類重構,測試不能 mock 掉被重構的 producer caller 路徑**,須用真實 caller chain 驅動(L3 整合路徑,非 L2 隔離 unit test)。

### 證據時效性

證據階層談「強度」,但證據還有「時效」— 測試通過的證據會隨系統演化而**腐化**。重構改變行為後,測試可能:

- **過時但仍通過**(死測試):測試被改成迎合新實作,從「驗證意圖」降級為「反映實作」 — 這是同義反覆的動態版本(靜態同義反覆偵測抓不到)。
- **驗證的行為已無關**:測試的消費端 / 情境已不存在。

過時測試比沒測試更危險 — 它給虛假信心。**重構後必須重新確認證據有效**,否則 L2 證據 silently 貶值。偵測見 audit-test 角度 6,修正見 fix-test 必要性審查(Claude commands,跨 harness 路徑從略)。

## A / B 雙軸分工

| 軸 | 職責 | 證據層 | 天花板 |
|--|--|--|--|
| **A 機器自驗** | 內部實作細節的正確性 | L1-L3 | **AI 內部自洽** — 機器斷言跳不出 AI 信念體系 |
| **B 人類驗收** | 跨越「自洽 → 對外部正確」的鴻溝 | L4-L6 | 部分落地:deliverable-review(交付) + illustrate(結構 viewport) = 人類 viewport(三層介入);完整 L4-L6 執行驗收仍為設計方向(見下) |

**鐵律**:A 是必要不充分,B 是充分性的來源。A 軸深化有邊際效益遞減 — 天花板是 AI 自洽,真正的驗收鴻溝在 B 軸。Agent Review 的「獨立 context」≠「獨立智能」:同家族 LLM 共享系統性偏誤,quorum 對共同盲點無效,A 軸的深層防線最終仍由 B 軸兜底。

## B 軸人類驗收層

**已落地**:deliverable-review(交付:demo-checklist + 認知誤差點) + illustrate(結構 viewport:whole-picture + 重用枚舉) 是人類 viewport(三層介入,見 AGENTS.md「命令的受眾視角」)(Claude commands 與路徑,跨 harness 從略)—— 讓人用大原則判讀 EP 或 code,補 LLM 兩個結構性 blind spot(重造既有 / 偏方向)。

**仍為設計方向**(viewport 之外,更深的 B 軸演進):

`must-execute-before-complete.md` 把 `.py / demo / poc/ / example` 全歸為「可執行 → 必須 uv run」是**生產側視角**(確保 AI 跑過),完全缺**消費側視角**(給誰看、怎麼看)。B 軸的演進方向:

1. **UC 場景執行驗收(B 軸核心)**:驗收單位是 UC 場景(execution-plan,Claude command)(EP Scenario Matrix,下稱 SM),不是泛泛 demo。SM 欄位「觸發 / 預期行為」是現成的可執行輸入 + 人類可判讀預期,且必須涵蓋 happy / 錯誤 / 邊界 / 效能。**人的角色**:deliverable-review 元件 D(意圖情境完整性)審「該驗哪些」(範圍,不親跑);LLM 跑場景、人觀察產出 = L6。素材 EP 已產出,不需另發明。
2. **可觀察性合約**:SM 的「預期行為」欄位 = 人類可判讀的結論。執行 SM 場景的 stdout 必須對應預期行為,且至少跑一個錯誤/邊界場景(避免只演 happy path 的 AI 公關稿)。
3. **自動化對照(A/B diff)**:跑新舊版 / 兩 branch / 兩參數比對,人類只判讀 diff 合理性。把「讀」外包給機器,這是長期最該投資的模式。
4. **流程末端驗收步驟**:build / deep-work(Claude commands)在 commit 前缺「執行 SM 代表性場景讓人判讀」的步驟;現有 demo/POC 驗證只驗 exit code 0,不驗輸出內容(silent failure / 語義錯誤偵測不到)。
5. **人類介入點前移到 RED**:GREEN 後人類讀不完;RED 時刻判讀「失敗是否符合預期」更便宜,是意圖偏移的最早訊號。

### 內部跨層接線的真實邊界歸屬(A 軸天花板,B 軸補強)

整合器型「真實邊界」的觸發準則鎖定「≥2 真實**外部**組件」。**內部跨層接線 + 真實資料依賴**(例:auto-discovery registry 成員 consume Feature 的真實 dtype、跨層欄位 auto-prefix 展開)不觸發整合器 flag — 這是 by design 而非 gap:

- 這類 bug(接線 guard 通過但真實資料 dtype/契約落差)是 **A 軸 L3 天花板**:跑真實 pipeline 仍可能因 mock/合成資料不反映真實 dtype 而自洽通過。強迫真實邊界收不掉這個天花板。
- 真正能抓此落差的是 **B 軸**(執行 UC/SM 場景,人類觀察真實資料產出,L4-L6)。
- 實務:內部跨層段落,接線 guard(registry membership / 路徑覆蓋)靠 A 軸機械閘門擋高頻 regression;真實 dtype/契約落差靠 B 軸 UC 場景驗收。兩軸分工,不靠收緊整合器 flag 把真實邊界塞回 A 軸(over-classify,違反「避免過度工程」)。

## 與既有規則的關係

- **風險分級**(ai-development-guide「驗證約束」段;source 在 ai-rules repo)決定「爬到第幾層」— 🟢 低風險不需六層,🔴 高風險才強制爬到對應層。避免過度工程是本階層的內建約束。
- **漸進驗證**([progressive-validation](./progressive-validation.md))是 L1 → L2 → L3 的爬坡順序(DEPTH-MIN → SAMPLE → FULL)。
- **消費端驗證模式**([quality-constraints](./quality-constraints.md))是 L3 整合層的具體化,本階層為它提供「為什麼」的理論基礎。
- 階層降低風險,**不消除風險** — 每一層都值得懷疑,包括最頂層(L6 人類觀察會疲勞漏看,L5 POC 可能打自己畫的靶)。
