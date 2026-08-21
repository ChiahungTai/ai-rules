---
name: acceptance-evidence
description: 驗收證據階層深層理論 — 認知誤差與 EP 預見極限、Intent Drift Type A/B、filter trap 重構查證義務、L3 整合測試實例、Runtime Invariant Assurance、B 軸人類驗收層演進。always-on 核心（L1-L6 階層表、證據獨立性、Claim→Evidence）在 rules/acceptance-evidence.md；審查/規劃/測試策略需要深層論證或失敗案例時載入。觸發詞：證據階層、L3、整合測試、filter trap、runtime invariant、intent drift、B 軸、人類驗收、認知誤差、EP 預見極限。
---

# Acceptance Evidence — 驗收證據深層理論

> 本 skill 是 `rules/acceptance-evidence.md` 的 on-demand 深層載體：rule 端保留 always-on 核心（證據獨立性、Claim→Evidence→Trust、L1-L6 階層、A/B 軸分工）；本檔承載審查/規劃/測試策略工作流才需要的深層論證、失敗案例與設計方向。兩者同一概念體系，分層載入。

## Claim 群的真實案例（rule 端舉證義務的案例載體）

> rule 端「Claim→Evidence→Trust」段列同型 claim 群與舉證義務（always-on 核心）；本段承載對應**真實案例**（失敗教訓案例屬 Low Noise 保留例外，須含「真實案例」marker）。

- **數字/清單類 claim**（真實案例）：features leaf 清單把 VolumeFeature 寫成 KeyCandleFeature，與 `list_feature_classes` 實際輸出不符，自審抓不到——AI 寫盤點清單易憑印象混入/漏掉成員（同型：consumers 數 41 誤寫 20，`rg | head -20` 截斷；此簡版 rule 端保留）。
- **silent-failure claim**（真實案例）：smell-detector baseline（原 codebase-sweep）state.yaml 把 Interval 自創名稱（如 `"1M"`）標「silent drift」——靜態推論「1M 撞 1m」沒跑 `Interval("1M")`，實證 StrEnum 精確比對 + raise → loud crash 非 silent。同類：tilde bug 靜態推論「消費端 inline 沒問題」沒執行 → 實證推翻。教訓通用（silent-claim 須執行證據），不依賴特定符號現狀。

## 認知誤差與 EP 的預見極限

證據獨立性解決「驗證者的偏誤」(AI 不能自己驗自己),但解決不了「驗證基準本身可能是錯的」。**規劃層(EP)是人類 + AI 對需求理解的最佳猜測,不是真理**。兩種認知誤差只能在實作呈現時被發現:

- **實作落差**:實作層發現規劃層沒預見的 — EP 的 pseudo code 看起來對,接起來才發現邊界、副作用、組件互動。
- **設計本身錯**:使用者一開始的設計就錯,看到實作呈現才理解 — 「我以為我要的是這個,看到成品才知道不是」。

**Agent Review 解決「球員兼裁判」(同 LLM 審自己),但對認知誤差無效** — review agent 再獨立,審的基準仍是 EP,而 EP 可能從根上錯。問題不在「實作對不對 EP」,而在「EP 和它背後的預期對不對」。

### 對 build 的啟示:EP 是收斂方向,不是合約

- **前線實作 LLM 有裁量權**:實作時發現 EP 的問題(規劃層預見極限外的真相),可調整。這不是「偷懶不照 EP」,而是「實作層有發現真相的責任」 — 死守 EP 會實作一個「忠實但錯誤」的東西,反而妨礙人類在呈現時發現認知誤差。
- **仍要架構化**:實作接近 EP(避免失控)+ 記錄偏差(可追溯)。
- **呈現是唯一觸發器**:認知誤差只能靠「實作呈現給人類判讀」(L6)揭露。沒有可觀察的呈現,認知誤差永遠潛伏 — 這是 B 軸人類驗收層不可省略的根本理由。

## Intent Drift 的兩型(Type A/B)+ 3-signal correlation

認知誤差(上方)是「EP/設計本身可能錯」;intent drift 是另一軸 — **AI 的產出偏離了人類意圖**,即使 code 正確、test 通過(passing test ≠ business intent)。分兩型,偵測法不同:

- **Type A(Specification Drift,靜態)**:AI 誤解 prompt → code 完全正確但不是要的。偵測:意圖先於 code 寫下並保留(story / plan);completion analysis 把生成碼 + transcript 對照原 plan。
- **Type B(Context/Goal Drift,動態)**:AI 不知 project convention / hidden invariant / 歷史 bug,或隨段落推進 / 跨 session 目標悄然偏移。偵測:invariant check + pattern divergence 偵測 + 跨 session 目標描述 drift。

**3-signal correlation**:判讀 passing test 是真通過還是 silent drift,須關聯三訊號 — ① 原始 test intent(story 建立時擷取)② 當前 test result ③ 引入的 code changes。任一單獨不足以判斷。coverage 增加 ≠ 能指出「code 仍做意圖中的事」。

**別混淆三組二分法**:本處的 Type A/B(intent drift 動靜態)≠ fix-test 的 Type A/B(test-failure 分類:實作缺陷 vs 契約變更,Claude command)≠ 既有 impl-discovery / design-error(認知誤差兩型,非 Type A/B 標籤)— 三者語義正交,勿混為一談。

## L3 整合層的正向價值實例(為什麼整合測試值得)

**理論呼應**:"mock 循環論證讓 mock 假設成為 bug 來源"(見 quality-constraints 整合器型變更)。以下實例顯示補整合測試如何**立刻**抓到 mock 抓不到的 source bug。

**實例(真實案例 — DB 序列重置函式)**:

- **audit 發現**:restore flow 新增的 DB 序列重置函式(`pg_get_serial_sequence` + `setval` 動態 SQL),屬整合器型變更(DB catalog + serial sequence + restore flow),但整合測試零覆蓋。
- **補整合測試**(真實 PostgreSQL,跑 restore → reset → INSERT):**立刻崩潰**。
- **source bug**:空 table 時 `setval(seq, COALESCE(MAX(id), 0))` → `setval(seq, 0)`,但 SERIAL 的 `MINVALUE=1`,`setval(seq, 0)` 違反約束 → fresh DB restore 後第一次 INSERT 崩潰。
- **為什麼 mock 抓不到**:mock 假設「table 有資料,MAX 有值」,整個邊界(空 table)不在 mock 的假設世界裡。mock 循環論證讓這個假設成為 bug 來源。

**啟示**:整合器型變更(接 ≥2 真實外部組件)補整合測試不是「儀式」,是**唯一能抓跨組件邊界 bug 的手段**。理論見品質約束「整合器型變更判定」;判定流程見 audit-test 角度 4(Claude command,跨 harness 路徑從略)。

## 重構查證義務:上抬抽象層的 filter trap(通用重構紀律)

> **適用範圍超出整合器型變更** — 任何「移除補丁 / 上抬抽象層」重構都適用。測試角度(mock 偽造 real code 不會算的值)接 L3 證據理論,但**重構查證義務本身是行動紀律,不限整合測試場景**。

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

**與 YAGNI check([collaboration-constraints](../../rules/collaboration-constraints.md))的差異**:YAGNI 是「搜用量 → 沒用 → 移除」;filter trap 是「**code 有用、但 caller chain 中間的 filter 阻斷 case 到達 producer**」。YAGNI 往「刪」走,filter trap 往「驗證不能刪」走 — 方向相反。YAGNI 的 `findReferences` 查「誰引用」;filter trap 的 `findReferences` 查「誰引用 + 其 filter 是否阻斷 case」— 多一層 filter 邏輯查證。

**測試假信心(為什麼測試會給綠燈)**:移除補丁後,測試可能 mock 掉 producer 的真實 caller chain,直接偽造 case_X 傳入 producer → producer 處理成功 → 綠燈。但真實 runtime 的 caller filter 把 case_X 擋掉了,producer 從沒收到 → 死碼 → 補丁移除等於功能消失。**對「移除補丁」類重構,測試不能 mock 掉被重構的 producer caller 路徑**,須用真實 caller chain 驅動(L3 整合路徑,非 L2 隔離 unit test)。

## Runtime Invariant Assurance(設計方向)

證據階層的 test 是**時間點證據**(build-time 通過);runtime monitor 是**持續保證**。silent-corruption path(bug 不 crash 但污染下游資料)的 invariant,須有 **runtime 機械檢查**作為 test 之後的持續守衛 — 區分「test-passed-at-build-time」vs「holds-at-runtime」。source review 看得到語法 / 邏輯,看不到 runtime silent corruption。

**獨立性**:runtime check 機械執行,**獨立於 AI mental model**(呼應證據獨立性)。AI 可幫寫 check code,但「該驗什麼 invariant」必須人定 — AI 可能正確實作錯誤模型,讓 AI 列 invariant 會把同一 drift 帶進 spec。

**spec 是上限**:runtime monitor 的上限 = 寫進 spec 的 invariant 完整度。沒寫進 spec 的 invariant = 永遠測不到。

**multi-point placement**(範例 placement,領域特定非規則本體):runtime check 放多個 defense-in-depth 點,依專案生命週期選。範例(量化領域):test-time assert / 對帳外部 truth(broker / account,獨立於內部 state)/ 生產 monitor / 本地 pre-commit(solo 無 CI 時取代 CI gate)。

**降級路徑**(專案無 runtime monitor infra 時):原則不退化為空話 — 至少 ① source-time 強制列舉 invariant(人列,不讓 AI 列)+ ② test-time assert 作 monitor 替代。標「不足但有」。

**asymmetric drift 警覺**(原則層,禁寫死研究數字):AI 在 complex / competing-demand 壓力下傾向破壞 constraint(risk limit 首要受害)→ constraint invariant 的 check 必須**機械、不可被 AI lobby**(AI 產 claim「沒影響 risk」時,assertion 照跑、違規照崩)。

> cross-ref:silent-corruption path 的識別見 execution-plan §1b Invariant Impact(producer 端規劃時識別,Claude command);本段承接其 runtime 保證層。本原則(機械檢查 > AI 自述 / 人審)是 mechanical-gate-philosophy 的具體應用(該 general framework 待建成獨立 skill)。

## 人審結構上限與三層守衛

**人審結構上限**(reviewer 認知上限):人審(B 軸 L6 / reviewer)亦有**結構上限** — 疲勞、注意力瓶頸、確認偏差是認知結構限制,**經驗無關**(資深 reviewer 同樣漏看)。故 P0 invariant 不能只靠人審(B 軸),需 Runtime Invariant Assurance(見上段)補人審結構上限 — A 軸機械、B 軸人審、runtime assurance 三層共同守 silent-corruption invariant。

## B 軸人類驗收層(演進設計方向)

**已落地**:debrief(理解簡報:demo-checklist 驗證證據 + 認知誤差點，承接原 deliverable-review 交付軸) + illustrate(結構 viewport:whole-picture + 重用枚舉) + smell-detector(壞味道:存在質疑/baseline 盤點) 是人類 viewport(三層介入,見 AGENTS.md「命令的受眾視角」)(Claude commands 與路徑,跨 harness 從略)—— 讓人用大原則判讀 EP 或 code,補 LLM 兩個結構性 blind spot(重造既有 / 偏方向)。

**仍為設計方向**(viewport 之外,更深的 B 軸演進):

`must-execute-before-complete.md` 把 `.py / demo / poc/ / example` 全歸為「可執行 → 必須 uv run」是**生產側視角**(確保 AI 跑過),完全缺**消費側視角**(給誰看、怎麼看)。B 軸的演進方向:

1. **UC 場景執行驗收(B 軸核心)**:驗收單位是 UC 場景(execution-plan,Claude command)(EP Scenario Matrix,下稱 SM),不是泛泛 demo。SM 欄位「觸發 / 預期行為」是現成的可執行輸入 + 人類可判讀預期,且必須涵蓋 happy / 錯誤 / 邊界 / 效能。**人的角色**:debrief 第 6 段(驗證證據+清單完整性)審「該驗哪些」(範圍,不親跑);LLM 跑場景、人觀察產出 = L6。素材 EP 已產出,不需另發明。
2. **可觀察性合約**:SM 的「預期行為」欄位 = 人類可判讀的結論。執行 SM 場景的 stdout 必須對應預期行為,且至少跑一個錯誤/邊界場景(避免只演 happy path 的 AI 公關稿)。
3. **自動化對照(A/B diff)**:跑新舊版 / 兩 branch / 兩參數比對,人類只判讀 diff 合理性。把「讀」外包給機器,這是長期最該投資的模式。
4. **流程末端驗收步驟**:build / deep-work(Claude commands)在 commit 前缺「執行 SM 代表性場景讓人判讀」的步驟;現有 demo/POC 驗證只驗 exit code 0,不驗輸出內容(silent failure / 語義錯誤偵測不到)。
5. **人類介入點前移到 RED(operational)**:GREEN 後人類讀不完;RED 時刻判讀「失敗是否符合預期」更便宜,是意圖偏移的最早訊號。**operational step**:build 在每段 RED 時刻印出「失敗訊號 + EP 該段預期行為」對照,標「人類 RED checkpoint」(prospective 可選暫停點)。明文 prospective vs retrospective:此 checkpoint 前瞻判意圖,有別於 fix-test(Claude command)retrospective 判舊測試意圖。
6. **session-boundary review**:跨 session 接續時,判讀累積目標是否漂移。**部分落地**:跨 session resume 觸發的 **substrate + 觸發器已落地** —— autonomous-execution「Session 級 Recovery」crash-only reconciliation(resume 時 re-derive「git diff vs EP scope」差異報告);at / handoff / standup 命令(Claude commands)仍非 intent-drift review。本原則效果:單 session batch-ceiling 軟觸發(見 implement skill（原 build）batch ceiling,Claude command)+ 跨 session resume 機械 re-derive(autonomous-execution)。**仍 deferred**:完整 intent-drift review **command**(判讀層:差異報告 → intent 是否漂移,Type B 動態漂移偵測見本檔「Intent Drift 的兩型」)——見 `.kanban/Backlog/` deferred card。

## 內部跨層接線的真實邊界歸屬(A 軸天花板,B 軸補強)

整合器型「真實邊界」的觸發準則鎖定「≥2 真實**外部**組件」。**內部跨層接線 + 真實資料依賴**(例:auto-discovery registry 成員 consume Feature 的真實 dtype、跨層欄位 auto-prefix 展開)不觸發整合器 flag — 這是 by design 而非 gap:

- 這類 bug(接線 guard 通過但真實資料 dtype/契約落差)是 **A 軸 L3 天花板**:跑真實 pipeline 仍可能因 mock/合成資料不反映真實 dtype 而自洽通過。強迫真實邊界收不掉這個天花板。
- 真正能抓此落差的是 **B 軸**(執行 UC/SM 場景,人類觀察真實資料產出,L4-L6)。
- 實務:內部跨層段落,接線 guard(registry membership / 路徑覆蓋)靠 A 軸機械閘門擋高頻 regression;真實 dtype/契約落差靠 B 軸 UC 場景驗收。兩軸分工,不靠收緊整合器 flag 把真實邊界塞回 A 軸(over-classify,違反「避免過度工程」)。
