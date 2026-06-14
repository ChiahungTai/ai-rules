# Audit-Test 流程改進建議 — 20260614 Daily Scan 提煉

> **來源**: 2026-06-14 一次大型 `/audit-test --daily` 流程（4 agent 平行 + judge-review + 實作查證）的真實經驗
> **原始報告**: `/Users/ctai/Github/mosaic_alpha_offline_backtesting/ai-analysis/audit-test-report-20260614.md`
> **性質**: 改進建議，**未修改任何 ai-rules 規範檔案**（使用者 review 後併入）
> **預期目標路徑**: `/Users/ctai/Github/ai-rules/ai-analysis/audit-test-improvement-proposals-20260614.md`
> **語言**: 繁體中文 + 英文術語

---

## 背景與提煉方法

本次 Daily Scan 涵蓋 448 test files / ~117,609 行，產出 6 Critical + 15 Important + 19 Suggestion。在後續 judge-review 與實作查證過程中，發現**多個流程層面的問題**（不是 audit findings 本身的對錯，而是「audit / judge-review / 實作三層各自都可能錯」的結構性 gap）。

這份建議提煉 10 個真實經驗教訓，對應到 ai-rules 的具體檔案與段落，產出可執行的改法草稿。**每個建議都引用這次具體案例**（I4/I5/C2/I11/B1 等），不泛泛。

---

## 建議總覽

| # | 標題 | 目標檔案 | 教訓 | 優先級 | 類型 |
|---|------|---------|------|--------|------|
| 1 | audit-test 角度 2/6 搜尋策略改「多工具交叉」 | `commands/audit-test.md` | #1 | **P0** | 規範改進 |
| 2 | audit-test 新增「Audit 誠信約束」段落 | `commands/audit-test.md` | #1,#3,#5,#8 | **P0** | 規範改進 |
| 3 | audit-test 報告模板加「信心水準 + 驗證狀態」欄位 | `commands/audit-test.md` | #1,#8 | **P0** | 流程改進 |
| 4 | judge-review 加「符號查證工具指定 + 自我否證」段落 | `commands/judge-review.md` | #2 | **P0** | 規範改進 |
| 5 | lsp-navigation 反例新增 audit/judge-review 場景 | `rules/lsp-navigation.md` | #1,#2 | **P1** | 規範改進 |
| 6 | acceptance-evidence 新增「L3 整合層正向實例」 | `rules/acceptance-evidence.md` | #9 | **P1** | 規範改進 |
| 7 | audit-test 新增「長任務 findings 即時落盤」段落 | `commands/audit-test.md` | #4 | **P1** | 流程改進 |
| 8 | audit-test Daily Scan 加「反思閉環」段落 | `commands/audit-test.md` | #10 | **P2** | 流程改進 |
| 9 | tests/CLAUDE.md PropertyMock 規範需在 audit prompt 主動注入 | `commands/audit-test.md` + 專案 `tests/CLAUDE.md` | #6,#7 | **P1** | 流程改進 |

---

## 建議 1：audit-test 角度 2/6 搜尋策略改「多工具交叉」（防 false positive）

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md` 角度 2（line 84-114）、角度 6（line 154-167）
- **對應教訓**: #1（audit false positive — I4/I5）
- **現狀問題**:

  角度 2 表格（line 91）寫：
  ```
  | 新增 registry 成員（auto-discovery）但無 membership 斷言 | Important | `rg "list_.*_classes" <test files>` + 檢查 `"<ClassName>" in {c.__name__ ...}` |
  ```

  Agent 2 照此執行：`rg "list_.*_classes"` 結果 0 hits（因為專案用的是 `list_condition_classes` + `CONDITION_REGISTRY`，命名模式不同），誤報「17/28 Condition 無 membership 斷言」（I4）。實作查證推翻：`test_registry_membership.py` 已完整覆蓋 28 class（完整清單比對）。

  I5 同樣模式：`fd "test_alpha158" tests/` → 0 results，誤報「無 test_alpha158.py」。實際上該檔已存在、6 tests PASS。**fd 無結果不等於檔案不存在**（可能是 fd 的 gitignore 或 pattern 差異）。

  **根因**：audit-test.md 角度 2 表格列「單一 rg pattern」當偵測方式，但角度 2 後半（line 97-114）已有「覆蓋搜尋策略 + Method Coverage 流程」明確要求多工具交叉。**表格與流程段不一致**：agent 看表格就停，沒讀到後面的流程段。

- **建議改法**:

  **改 1：角度 2 表格的「驗證方式」欄位不再列單一 pattern，改指向流程段**。

  草稿（替換 line 88-91 該列的「驗證方式」欄）：

  ```markdown
  | 新增 registry 成員（auto-discovery）但無 membership 斷言 | Important | 見下方「Registry Membership 流程」（多工具交叉，禁用單一 rg pattern） |
  ```

  **改 2：新增「Registry Membership 流程」段落**（緊接 Method Coverage 流程之後），明確多工具交叉：

  ```markdown
  **Registry Membership 流程**（避免單一 rg pattern 造成 false positive）：

  > ⚠️ **教訓（20260614 Daily Scan）**：audit 用單一 rg pattern（如 `rg "list_.*_classes"`）判斷 membership 斷言存在與否，但專案可能用不同符號（`list_condition_classes`、`CONDITION_REGISTRY`、registry 本身的 class 名）。單一 pattern 0 hits ≠ 斷言不存在。**必須多工具交叉**。

  1. **候選符號清單**：從 source file 提取 registry 的所有可能符號（registry 變數名 `*_REGISTRY`、列舉函式 `list_*_classes()` / `*_classes()`、registry module 本身的 import）
  2. **多工具交叉搜尋**（至少兩個獨立途徑）：
     - `rg "<registry_var>" tests/ -l`（找直接引用 registry 變數的 test files）
     - `LSP findReferences`（從 registry 變數定義，找所有引用點 — 100% 涵蓋，含動態引用）
     - `rg "<ClassName>.*in.*registry\|<ClassName>.*__name__" tests/`（找 per-class membership 斷言的多種寫法）
  3. **檔案存在性用 fd + ls 雙查**：`fd "<test_name>" tests/` 0 results 時，必須 `ls tests/<expected_path>/` 或 `fd -g "<exact_name>.py" tests/` 確認，**不能單靠 fd 結果下結論**（gitignore、pattern 差異會造成 false negative）
  4. **判定零覆蓋**：只有當上述多個工具都 0 hits 時，才判定為零覆蓋
  5. **報告前交叉驗證**：在報告中列出「已查的工具與結果」，讓 reviewer 可複現
  ```

  **改 3：角度 6 過時偵測流程（line 161-166）同樣問題**，目前是純 git log + git show，沒提「assertion 迎合」的判定要用語義分析而非 pattern。建議在步驟 3 後加：

  ```markdown
  3.5. **判定「迎合」的標準**：assertion 改成等於新實作輸出（literal value 追隨），而非新增獨立案例。需讀完整 test body 判斷 — 不能只看 diff 的 `+/-` 行（rename 也會產生 diff）。若不確定，標「需實作查證」而非定論。
  ```

- **預期效果**: 下次 audit 不再出現「單一 rg 0 hits → 誤報零覆蓋」。Agent 必須列出查過的工具與結果，reviewer 可複現驗證。
- **優先級**: **P0**（這次直接造成 2 個 false positive finding，浪費 judge-review + 實作查證時間）

---

## 建議 2：audit-test 新增「Audit 誠信約束」段落（承認 false positive 可能 + findings 格式 + 技術 rationale 實證）

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md` 新增段落（建議放「執行約束」之前）
- **對應教訓**: #1（false positive）、#3（rationale 過度陳述 — C2）、#5（findings 丟失細節）、#8（多層驗證價值）
- **現狀問題**:

  audit-test.md 現有「執行約束」段落（line 328-335）只列 5 條（只讀不寫、必須讀實際程式碼、引用來源、繁中、不重複 ruff），**完全沒有提到**：
  - audit 本身可能 false positive（agent 預設相信自己的 finding 是對的）
  - 「技術行為 / 套件行為」判斷必須實證（C2 案例：audit 稱「LightGBM 無 seed → 每次訓練結果不同」，實驗推翻 — LightGBM 4.6.0 有預設 seed，同機 deterministic）
  - findings 輸出必須含 file:line + 證據 + 結構化（不能壓成摘要）
  - 三層驗證（audit → judge-review → 實作查證）的設計意圖：每一層都可能錯

  **C2 案例細節**：原報告稱「`LGBMConfig` 無 seed → 每次訓練結果不同」。實驗：同 config（含 `bagging_fraction=0.8, feature_fraction=0.8, bagging_freq=5`）兩次訓練，預測完全相同（max abs diff=0.0）。audit 的技術判斷基於推理（「無 seed → 不 deterministic」），但未實證 LightGBM 實際行為。

- **建議改法**:

  新增「Audit 誠信約束」段落（放現有「執行約束」之前，作為 audit 特有的更高層約束）：

  ```markdown
  ## Audit 誠信約束

  > audit 是偵測器（眼睛），不是判官。偵測結果可能 false positive，必須以「可被下一層（judge-review / 實作查證）推翻」的心態輸出。

  ### 1. Findings 不是定論 — 標示信心水準

  每個 finding 必須標示信心水準，讓下游知道哪些需要重點查證：

  | 信心水準 | 判斷標準 | 範例 |
  |---------|---------|------|
  | **confirmed（已查證）** | 已讀完整 test body + source，比對過具體行/符號 | C5 `test_pattern_conditions_integration.py:24-25` 只有 `pass` — 讀過原始碼確認 |
  | **evidence-based（有證據）** | 有具體 file:line + rg/fd 結果，但未深入驗證符號語義 | 角度 2 多數覆蓋缺口 |
  | **inferred（推理）** | 基於規範 / 套件行為推理，未實證 | C2「LGBMConfig 無 seed → 不 deterministic」 |

  **推理類（inferred）findings 必須額外標註**：「⚠️ 未實證，建議實作層跑 demo 確認」。**禁止把推理類寫成 Critical**（Critical 必須 confirmed 或 evidence-based）。

  ### 2. 技術 / 套件行為判斷必須實證

  對「套件行為」「演算法行為」「數值特性」的判斷（如「無 seed → 不 deterministic」「浮點運算 → 誤差累積」「此 API 會 raise」），**不能只靠推理**。判斷前必須：

  - 寫最小 demo（`uv run python -c "..."` 或獨立腳本）實際跑一次，或
  - 引用套件 source（`.venv/lib/python*/site-packages/<pkg>/`）具體行號佐證，或
  - 標「inferred」+「未實證」並降級為 Suggestion

  **反例（20260614 C2）**：audit 稱「LightGBM 無 seed → 每次訓練結果不同」並列為 Critical。實驗推翻（同 config 兩次訓練 max abs diff=0.0，LightGBM 4.6.0 有預設 seed）。**推理看起來合理但與套件實際行為不符**。

  ### 3. Findings 輸出格式（嚴格）

  每個 finding 必須包含（缺一即不合格）：

  - **file:line**（精確位置，不能只寫檔名）
  - **證據**（rg/fd/LSP 指令 + 結果，或原始碼引用）
  - **角度 + 嚴重程度 + 信心水準**
  - **建議**（具體可執行，不是「建議改善」）

  **禁止**：把多個 finding 壓成摘要（如「2 Critical + 4 Important」）回報 — 摘要丟失 file:line，下游無法定位。摘要只能作為總覽表格，**明細必須完整保留**。

  ### 4. 多層驗證設計意圖

  audit-test → judge-review → 實作查證 是**刻意設計的三層**，每一層都可能錯：

  | 層 | 抓什麼錯 | 這次案例 |
  |---|---------|---------|
  | audit（偵測器） | 測試品質問題 | 主要產出 findings |
  | judge-review（審查者） | audit 的 false positive / 過度陳述 | 推翻 I4/I5（覆蓋其實存在）、C2（LightGBM 有預設 seed）|
  | 實作查證（最終） | judge-review 的查證失誤 / 調查 agent 誤判 | 推翻 I1 查證失誤（`trading_host.py:64,392` 確實有建構）、I11 誤判（fixture 回傳真實 class 非 mock）|

  **啟示**：audit findings 預設「待驗證」，不應被當成已確認的問題清單。Daily Scan 報告開頭必須聲明此性質。
  ```

- **預期效果**:
  - audit findings 自帶信心水準，judge-review 知道哪些重點查
  - 推理類技術判斷被強制實證或降級，避免 C2 類型 over-statement
  - findings 格式嚴格化，不再丟失 file:line
  - 三層驗證意圖文件化，下游不再盲目信任 audit
- **優先級**: **P0**（直接對應 #1/#3/#5/#8 四個教訓，是這次最大的流程 gap）

---

## 建議 3：audit-test 報告模板加「信心水準 + 驗證狀態」欄位

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md`「輸出格式 → 報告模板」（line 174-223）
- **對應教訓**: #1（false positive）、#8（多層驗證）
- **現狀問題**:

  現有報告模板（line 186-202）每個 finding 只有 `**反模式**: file:line — 證據`，**沒有信心水準欄位**。reviewer 看報告時無法區分「confirmed 已查證」vs「inferred 推理」，導致：
  - 把推理類 finding 當成定論去修
  - 或反向：對所有 finding 都懷疑，效率低

  本次 Daily Scan 報告（外部檔案）也沒有信心水準欄位，C2 被列為 Critical 但實際是推理類。

- **建議改法**:

  修改報告模板的 finding 格式（line 188-191 區域），加入信心水準標記：

  ```markdown
  ### 🔴 Critical（必須修正）

  > Critical 只能是 confirmed 或 evidence-based，禁止 inferred。

  - [ ] **[空殼覆蓋]** `[confirmed]` `test_tw_catalog.py:test_adj_weeky:24-25` — 只有 `pass`（讀過原始碼確認）
  - [ ] **[Mock 被測對象]** `[confirmed]` `test_classifier.py:test_classify:42` — `@patch("module.Classifier")` mock 了主角

  ### 🟡 Important（建議修正）

  - [ ] **[覆蓋缺口]** `[evidence-based]` `tw_catalog.py:_build_agg_exprs (line 88)` — `rg "_build_agg_exprs" tests/` → 0 hits。⚠️ 單一 rg，建議下游用 LSP findReferences 交叉確認
  - [ ] **[技術判斷]** `[inferred]` ⚠️ 未實證 `LGBMConfig` 無 seed → 不 deterministic。**禁止列 Critical，建議實作層跑 demo 確認 LightGBM 預設行為**
  ```

  並在「Audit Summary」（line 215-222）加信心水準統計：

  ```markdown
  ### Audit Summary（結構化結論）

  - mode: diff|commit|daily
  - files_scanned: N
  - critical: X（全為 confirmed/evidence-based）
  - important: X（含 Y inferred，已標⚠️）
  - suggestion: X
  - health_score: XX%
  - needs_action: true/false
  - **findings_nature: 待驗證（非定論）** — 建議經 judge-review / 實作查證後再行動
  ```

- **預期效果**: 報告自帶信心水準，reviewer 一眼看出哪些要重點查、哪些可直接行動。推理類被擋在 Critical 之外。
- **優先級**: **P0**（與建議 2 配套，沒有欄位則誠信約束無法落地）

---

## 建議 4：judge-review 加「符號查證工具指定 + 自我否證」段落

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/judge-review.md`（現有「執行約束」line 65-71、「特殊情況」line 75-80）
- **對應教訓**: #2（judge-review 查證本身錯 — I1）
- **現狀問題**:

  judge-review.md「執行約束」只列「必須查證實際程式碼 / 必須第一性原理分析 / 必須等待用戶確認」，**沒有指定查證工具**（rg vs LSP）。結果：

  I1 案例：審查者稱「`FuturesSimpleExecutor` trading_host.py 無建構點，查證失敗」。獨立 rg 確認 `trading_host.py:64`（import）+ `:392`（建構）確實存在。**審查者的 rg pattern 失誤（如 `\|` 轉義誤）或幻覺，回報「查證失敗」但實際上是查證者自己沒查到**。

  judge-review.md「特殊情況」line 79 寫「找不到相關程式碼 → ❌ 不採納（無法驗證）」— 這條規則在 I1 案例會誤導：審查者「找不到」是因為自己 pattern 失誤，不是程式碼不存在。**規則鼓勵「找不到 = 不採納」，但「找不到」可能是查證者錯**。

  另外，lsp-navigation.md 已明確「符號引用查證優先 LSP findReferences（100% 涵蓋），rg 文字搜尋易 pattern 失誤」，但 judge-review.md 完全沒引用此規則。

- **建議改法**:

  在 judge-review.md「執行約束」段落（line 65-71）後新增「查證工具指定」子段落：

  ```markdown
  ## 查證工具指定

  > 符號引用查證優先 LSP findReferences（100% 涵蓋），rg 文字搜尋易 pattern 失誤。完整工具決策樹見 [lsp-navigation](../rules/lsp-navigation.md)。

  | 查證對象 | 必用工具 | 禁止 |
  |---------|---------|------|
  | 「X class/function 是否存在」「X 在哪裡被引用 / 建構 / 呼叫」 | **LSP findReferences / goToDefinition / workspaceSymbol** | 單一 rg pattern 0 hits 就下結論「不存在」|
  | 「X 字串 / 註解 / config 值是否存在」 | rg | — |
  | 「名為 test_X 的檔案是否存在」 | `fd -g "test_X.py"` + `ls <expected_dir>/` 雙查 | 單一 `fd "test_X"` 無結果就下結論 |

  ### 自我否證義務

  **「找不到」不等於「不存在」**。查證 0 hits 時，必須：

  1. **換工具**：rg 0 hits → 用 LSP findReferences 再查一次（覆蓋動態引用、避免 pattern 失誤）
  2. **換 pattern**：`rg "FuturesSimpleExecutor\("` 失敗 → 試 `rg "FuturesSimpleExecutor"`（去掉 `(`，可能建構方式不同）、`workspaceSymbol "FuturesSimpleExecutor"`
  3. **換位置**：以為在某檔 → 用 `workspaceSymbol` 全域查定義位置
  4. **標註「查證失敗」而非「不存在」**：若三個工具都 0 hits，仍只能標「查證失敗，無法確認」，**禁止標「不存在」**（你可能是查證者錯，不是程式碼錯）

  **反例（20260614 I1）**：審查者稱「`FuturesSimpleExecutor` 在 `trading_host.py` 無建構點，查證失敗」→ 不採納 audit finding。獨立查證：`trading_host.py:64`（import）+ `:392`（建構）確實存在。審查者的 rg pattern 失誤，把「自己沒查到」誤判為「程式碼不存在」。
  ```

  並修改「特殊情況」line 79：

  ```markdown
  - **找不到相關程式碼**：先按「自我否證義務」三工具交叉查證。仍找不到 → 標「查證失敗」並請用戶提供線索，**不直接 ❌ 不採納**（查證者可能是 pattern 失誤，非程式碼不存在）
  ```

- **預期效果**: judge-review 不再出現「查證者 pattern 失誤 → 誤判程式碼不存在 → 不採納正確 finding」。符號查證強制 LSP，降低 pattern 失誤風險。
- **優先級**: **P0**（I1 是 judge-review 直接錯誤案例，影響 audit finding 是否被正確採納）

---

## 建議 5：lsp-navigation 反例新增 audit / judge-review 場景

- **目標檔案**: `/Users/ctai/Github/ai-rules/rules/lsp-navigation.md`「反例」段（line 14-15）、「Agent Prompt 工具選擇」段（line 122-136）
- **對應教訓**: #1（audit false positive）、#2（judge-review 查證失誤）
- **現狀問題**:

  lsp-navigation.md 現有反例（line 15）只舉 `ShioajiDataClient`（一個 import 查證場景）。Agent prompt 工具指定模板（line 127-133）是通用的，**沒有把 audit-test / judge-review 這兩個高風險查證場景納入**。

  結果：audit agent / judge-review agent 的 prompt 沒有強制「符號覆蓋判斷必須用 LSP findReferences」，重蹈 I4/I5/I1 的覆轍。

- **建議改法**:

  **改 1**：反例段（line 14-15）新增 audit / judge-review 案例：

  ```markdown
  **反例（rg 找符號的陷阱）**：

  - `rg "ShioajiDataClient\("` 結果被截斷（只顯示 `n`），只能「推測」呼叫端；`LSP findReferences` 精準列出 4 references（定義 + import + 型別註解 + 唯一實際呼叫點）。
  - **audit-test 覆蓋判斷（20260614 I4）**：`rg "list_.*_classes" tests/` → 0 hits，audit 誤報「17/28 Condition 無 membership 斷言」。實際測試用 `list_condition_classes` + `CONDITION_REGISTRY` 符號，LSP findReferences 可找到。**符號覆蓋判斷用 rg 會因命名 pattern 差異 false negative**。
  - **judge-review 查證（20260614 I1）**：審查者 `rg` 稱「`FuturesSimpleExecutor` 在 trading_host.py 無建構點」，LSP findReferences 立刻列出 `trading_host.py:64`（import）+ `:392`（建構）。**符號存在性查證用 rg 會因 pattern 失誤 false negative，把「自己沒查到」誤判為「不存在」**。

  **結論**：符號查詢用 rg 會 truncated/漏/pattern 失誤；LSP 結構化、不截斷、100% 涵蓋。
  ```

  **改 2**：Agent prompt 工具指定模板（line 127-133）新增 audit / judge-review 專屬條目：

  ```markdown
  **Agent prompt 工具指定模板**：

  # 工具選擇（必填）
  - 簽名/型別/定義位置 → 用 LSP hover / goToDefinition
  - 呼叫鏈/引用 → 用 LSP outgoingCalls / incomingCalls / findReferences
  - 文字搜尋（字串、註解、config）→ 用 rg
  - 檔案搜尋 → 用 fd
  - NT Cython 模組（.pyx/.so）→ 用 rg + Read（LSP 不索引 Cython）
  - **audit-test 角度 2 覆蓋判斷** → **禁用單一 rg pattern**；registry membership / class 引用 / method call 必須 LSP findReferences 為主、rg 為輔（見 audit-test.md「Registry Membership 流程」）
  - **judge-review 符號查證** → 「X 是否存在 / 在哪引用」必須 LSP findReferences / workspaceSymbol；rg 0 hits 不可直接下「不存在」結論（見 judge-review.md「自我否證義務」）
  ```

- **預期效果**: audit / judge-review agent spawn 時，prompt 模板直接指定用 LSP 查符號覆蓋，從源頭擋住 false positive。
- **優先級**: **P1**（lsp-navigation 是自動載入規則，改了所有 agent 都受惠；但需與建議 1/4 配套才完整）

---

## 建議 6：acceptance-evidence 新增「L3 整合層正向實例」（C3 抓 source bug）

- **目標檔案**: `/Users/ctai/Github/ai-rules/rules/acceptance-evidence.md`「證據階層」表（line 32-39）之後，或「兩層整合測試」（quality-constraints.md line 149-160）附近
- **對應教訓**: #9（整合器型真實邊界測試抓 source bug — C3 正向案例）
- **現狀問題**:

  acceptance-evidence.md L3 整合層的「mock 循環論證陷阱」（line 147，在 quality-constraints.md）只有理論 + 時區偏移範例，**沒有正向實例**（「補整合測試 → 立刻抓到 source bug」的成功案例）。結果：agent 對「為什麼要寫整合測試」缺乏具體感受，容易跳過。

  C3 是完美的正向實例：audit 發現 `_reset_sequences` 整合器型零測試 → 補整合測試（真實 PostgreSQL）→ **立刻抓到 source bug**：空 table `setval(seq, COALESCE(MAX,0))` → `setval(seq,0)` 違反 SERIAL MINVALUE=1 → fresh DB restore 崩潰。**mock 永遠抓不到**（mock 假設「MAX 有值」）。

- **建議改法**:

  在 acceptance-evidence.md「證據階層」表之後（line 39 後），新增正向實例小節：

  ```markdown
  ### L3 整合層的正向價值實例（為什麼整合測試值得）

  > 理論：「mock 循環論證讓 mock 假設成為 bug 來源」（見 quality-constraints 整合器型變更）。以下實例顯示補整合測試如何**立刻**抓到 mock 抓不到的 source bug。

  **實例（20260614 C3 `_reset_sequences`）**：

  - **audit 發現**：`backup/pipeline.py:_reset_sequences()` 新增 38 行（pg_get_serial_sequence + setval 動態 SQL），屬整合器型變更（DB catalog + serial sequence + restore flow），但整合測試零覆蓋。
  - **補整合測試**（真實 PostgreSQL，跑 restore → reset → INSERT）：**立刻崩潰**。
  - **source bug**：空 table 時 `setval(seq, COALESCE(MAX(id), 0))` → `setval(seq, 0)`，但 SERIAL 的 MINVALUE=1，`setval(seq, 0)` 違反約束 → fresh DB restore 後第一次 INSERT 崩潰。
  - **為什麼 mock 抓不到**：mock 假設「table 有資料，MAX 有值」，整個邊界（空 table）不在 mock 的假設世界裡。mock 循環論證讓這個假設成為 bug 來源。

  **啟示**：整合器型變更（接 ≥2 真實外部組件）補整合測試不是「儀式」，是**唯一能抓跨組件邊界 bug 的手段**。理論見品質約束「整合器型變更判定」；判定流程見 audit-test 角度 4。
  ```

- **預期效果**: agent 看到「補整合測試 → 立刻抓 bug」的具體案例，對整合測試價值有具體感受，不再當成 optional。
- **優先級**: **P1**（強化既有理論的說服力；C3 是這次最乾淨的正向案例）

---

## 建議 7：audit-test 新增「長任務 findings 即時落盤」段落

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md` 新增段落（Daily Scan 章節附近）
- **對應教訓**: #4（長任務 findings 因 429 中斷未保存）
- **現狀問題**:

  audit-test.md Daily Scan 章節（line 35-41）只描述掃描範圍，**沒有提到 findings 落盤策略**。本次 Agent 4 在 external_api 階段 429，跑了 11 個子任務但 findings 留在 context 中，彙整輸出前中斷 → **resume 需完整重跑**（findings 未保存 ≈ 等於沒做）。

  這與 autonomous-execution / deep-work 的「error self-healing」精神衝突 — 長任務應假設會中斷，findings 應即時落盤。

- **建議改法**:

  在 Daily Scan 章節（line 41 後）新增「長任務 findings 落盤策略」：

  ```markdown
  ### 長任務 findings 落盤策略（Daily Scan 必讀）

  > Daily Scan 涵蓋數百 test files，單一 agent 可能跑數十分鐘。**必須假設會中斷**（429 rate limit、context 上限、network），findings 即時落盤，避免 resume 重跑。

  **策略**：

  1. **分段輸出**：每完成一個子任務（一個 test 目錄 / 一組 test files），立即將該段 findings 寫入中間檔案（如 `ai-analysis/audit-test-daily-scan-{date}-{agent}.partial.md`）。不在 context 中累積全部 findings 才一次輸出。
  2. **格式**：每段 findings 含進度標記（`<!-- agent=2, segment=3/8, completed=true -->`），resume 時可讀 `.partial.md` 判斷哪些段落已完成。
  3. **彙整**：全部子任務完成後，讀所有 `.partial.md` 彙整成最終報告（`audit-test-report-{date}.md`），刪除中間檔。
  4. **resume**：429 / 中斷後 resume 時，先讀 `.partial.md` 確認已完成段落，只重跑未完成段落。

  **反例（20260614 Agent 4）**：Agent 4 跑 11 個子任務，findings 全留 context，彙整前 429 中斷 → resume 需完整重跑 11 個子任務。若即時落盤，只需重跑中斷時正在做的那 1 個。
  ```

- **預期效果**: 長任務 findings 不再因中斷全毀，resume 成本從「重跑全部」降到「重跑當前段」。
- **優先級**: **P1**（429 是反覆發生的問題；即時落盤是通用模式，不只 audit-test 受惠）

---

## 建議 8：audit-test Daily Scan 加「反思閉環」段落

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md` 新增段落（建議放文件末尾，作為流程的最後一步）
- **對應教訓**: #10（流程缺反思閉環）
- **現狀問題**:

  audit-test.md 完全沒有「反思」機制。本次改進 ai-rules 是**手動觸發**（用戶觀察到問題，spawn 反思 agent 提煉）。流程本身無內建「大型 audit 後提煉改進點 → 滾動更新規範」的步驟，導致同類問題會反覆發生。

  這與 ai-development-guide.md「演化性思維」（測試保護下持續演化）精神一致 — 流程本身也應演化。

- **建議改法**:

  在 audit-test.md 文件末尾（line 335 後）新增「反思閉環」段落：

  ```markdown
  ## 反思閉環（大型 Daily Scan 後執行）

  > 每次 Daily Scan 涵蓋全專案、跑數小時、產出數十 findings。這是真實流程經驗的富礦，**不提煉等於浪費**。本段定義大型 audit 後的反思流程。

  ### 觸發條件

  - Daily Scan 完成且 findings ≥ 20（Critical + Important + Suggestion 總和）
  - 或 judge-review / 實作查證階段發現 ≥ 3 個 audit false positive / over-statement
  - 或長任務因 429 / context 中斷重跑

  ### 反思流程

  1. **收集這次經驗的「教訓」**：哪些 finding 被 judge-review 推翻？哪些被實作查證推翻？哪些技術判斷推理錯？哪些流程造成重跑？
  2. **歸因到 ai-rules 具體段落**：每個教訓對應到哪個 rules/commands/skills 檔案的哪段不足？是規範缺（沒寫）還是規範有但 agent 沒讀？
  3. **產出改進建議**：寫到 `ai-analysis/audit-test-improvement-proposals-{date}.md`（不直接改規範，使用者 review 後併入）
  4. **滾動更新**：建議被採納後，更新對應 rules/commands 段落。下次 audit 自動受惠。

  ### 反思的反思

  反思本身也可能 over-engineering。判斷標準：

  - **該提煉**：同類問題在 ≥ 2 次 audit 反覆出現（結構性 gap）
  - **不該提煉**：單一偶發案例（個案，不值得改規範）

  避免把每個個案都上升成規範 — 規範膨脹會降低 signal/noise ratio。
  ```

- **預期效果**: 大型 audit 的經驗自動被提煉，不再依賴用戶手動觸發反思。規範滾動演化。
- **優先級**: **P2**（重要但不緊急；需要先有建議 1-7 落地，反思才有素材）
- **註**: 這份文件本身就是反思閉環的第一次產出，可作為範例引用。

---

## 建議 9：PropertyMock 規範需在 audit prompt 主動注入（fixture 型別確認 + 規範即時性）

- **目標檔案**: `/Users/ctai/Github/ai-rules/commands/audit-test.md` 角度 3（Mock 健康度，line 116-124）+ 專案 `tests/CLAUDE.md`（PropertyMock 例外規範所在）
- **對應教訓**: #6（調查 agent 誤判 fixture 型別 — I11）、#7（規範已補但仍重蹈覆轍 — B1）
- **現狀問題**:

  **兩個獨立但相關的問題**：

  **(a) I11 — 調查 agent 誤判 fixture 回傳型別**：
  調查稱 `test_providers.py:42` 的 `type(obj).attr = PropertyMock(...)` 多餘可刪（認為 `sj_client` fixture 回傳 `MockShioajiClient`）。實作查證推翻：`sj_client` fixture 回傳**真實 `ShioajiClient`**，L42 是唯一讓 `is_connected=True` 的機制，**不能刪**。調查前未確認 fixture 回傳型別（真實 class vs mock）。

  **(b) B1 — 規範已補但 agent 不讀**：
  剛處理完 I11（`tests/CLAUDE.md` 補 PropertyMock 例外：`type(MagicMock_instance)` 安全 vs `type(RealClass)` 危險）。但 B1 立即又用 `type(executor).order_factory = PropertyMock(...)` patch **真實 class**（`test_futures_simple_executor` L100），違反剛補的規範。**文檔規範更新後 agent 不會主動讀**。

  **根因（兩者共通）**：audit-test.md 角度 3 的 Mock 健康度檢查（line 116-124）沒有提到「PropertyMock type-level patch 的 fixture 型別確認義務」，也沒有「調查 / 修改 PropertyMock 前必讀 tests/CLAUDE.md 踩雷指南」的注入機制。

- **建議改法**:

  **改 1**：audit-test.md 角度 3（line 116-124）新增 PropertyMock type-level 檢查項：

  ```markdown
  | 檢查項 | 嚴重程度 | 判斷標準 |
  |--------|---------|---------|
  | ...（既有 4 項）... | | |
  | **`type(obj).attr = PropertyMock(...)` patch 真實 class** | Important | 見下方「PropertyMock type-level 危險性」|
  ```

  新增子段落：

  ```markdown
  #### PropertyMock type-level 危險性

  `type(obj).attr = PropertyMock(...)` 是 class-level patch，跨測試殘留風險真實。但**是否危險取決於 `obj` 的型別**：

  | `obj` 型別 | 風險 | 判定 |
  |-----------|------|------|
  | `MagicMock` instance / 純 mock fixture | 🟢 安全 | `type(obj)` 是 mock 類型，patch 不影響真實 class |
  | 真實 class instance（fixture 回傳 `RealClass()`） | 🔴 危險 | `type(obj)` 是真實 class，patch 污染整個 class，跨測試殘留 |

  **調查 / 修改前的強制義務**：

  1. **確認 fixture 回傳型別**：用 LSP hover / goToDefinition 跳到 fixture 定義，確認回傳的是 `MagicMock` 還是 `RealClass()`。**禁止憑 fixture 名稱猜測**（`sj_client` 可能回傳真實 `ShioajiClient`，不是 mock）。
  2. **必讀專案踩雷指南**：修改 PropertyMock 前，讀專案 `tests/CLAUDE.md` 的 mock 規範段落（每個專案可能有不同的 PropertyMock 例外規則）。

  **反例（20260614）**：
  - **I11**：調查稱 `test_providers.py:42` 多餘可刪，認為 `sj_client` 回傳 mock。實作查證：`sj_client` 回傳**真實 `ShioajiClient`**，L42 是唯一讓 `is_connected=True` 的機制，不能刪。調查前未確認 fixture 型別。
  - **B1**：`tests/CLAUDE.md` 剛補完 PropertyMock 例外規範，B1 立即又用 `type(executor).order_factory = PropertyMock(...)` patch 真實 class（`test_futures_simple_executor` L100），違反剛補的規範。**規範更新後 agent 不會主動讀**。
  ```

  **改 2**：agent-workflow SKILL.md「Agent tool spawn 前」自檢清單（line 128-137）新增規範注入項：

  ```markdown
  - [ ] Prompt 包含足夠 context + 相對路徑 + rules-reminder 六條規則摘要
  - [ ] **若任務涉及 mock / PropertyMock / fixture**：prompt 主動注入專案 `tests/CLAUDE.md` 的 mock 規範段落摘要（agent 不會自己讀專案 CLAUDE.md，必須主動注入）
  ```

  **改 3**：autonomous-execution 或 context-engineering skill 加「規範即時性」段落（這是更深層的問題 — 規範更新與 agent 行為之間無自動同步機制）：

  ```markdown
  ### 規範即時性 gap

  規範（rules/CLAUDE.md）更新後，**已 spawn 的 agent / 進行中的任務不會自動重新讀**。這是結構性 gap：

  - 規範更新點 → agent 行為更新點 之間有時間差
  - 同一 session 內連續任務，後續任務仍用舊 context（除非 /clear）

  **緩解**：
  - 高頻踩雷的規範（如 PropertyMock、mock 階層），在 spawn agent 時**主動注入到 prompt**
  - 規範更新後，下個任務開始前 `/clear` 或重新 `@` 載入規範
  - 不能假設「規範寫了 agent 就會讀」— 重要規範必須在關鍵流程點（audit 角度、agent prompt 模板）重複注入
  ```

- **預期效果**:
  - audit 角度 3 明確 PropertyMock fixture 型別確認義務
  - 涉及 mock 的 agent prompt 強制注入專案踩雷指南
  - 「規範即時性」問題被文件化，後續可在 context-engineering 深化
- **優先級**: **P1**（I11 + B1 兩個案例顯示這是反覆發生的結構性問題）

---

## 優先級總表

| 優先級 | 建議 | 對應教訓 | 影響範圍 | 預估改動量 |
|--------|------|---------|---------|-----------|
| **P0** | 1. audit-test 角度 2/6 多工具交叉 | #1 | audit-test.md（角度 2 表 + 新增流程段） | 中 |
| **P0** | 2. audit-test「Audit 誠信約束」段落 | #1,#3,#5,#8 | audit-test.md（新增大段落） | 中 |
| **P0** | 3. audit-test 報告模板加信心水準 | #1,#8 | audit-test.md（報告模板） | 小 |
| **P0** | 4. judge-review 符號查證 + 自我否證 | #2 | judge-review.md（新增段落 + 改特殊情況） | 中 |
| **P1** | 5. lsp-navigation audit/judge-review 反例 | #1,#2 | lsp-navigation.md（反例 + 模板） | 小 |
| **P1** | 6. acceptance-evidence L3 正向實例 | #9 | acceptance-evidence.md（新增小節） | 小 |
| **P1** | 7. audit-test 長任務即時落盤 | #4 | audit-test.md（Daily Scan 章節） | 小 |
| **P1** | 9. PropertyMock 規範注入 | #6,#7 | audit-test.md + agent-workflow + context-engineering | 中（跨檔） |
| **P2** | 8. audit-test 反思閉環 | #10 | audit-test.md（末尾新增） | 小 |

---

## 實施建議

### 批次分組（建議 3 個 PR）

**PR 1：audit-test 誠信化（P0 核心，建議 1+2+3）**
- 全部改 `commands/audit-test.md`
- 主題一致：「audit findings 不是定論」的誠信化改造
- 影響範圍單一檔案，易 review
- 改動量中等，但邏輯連貫（多工具交叉 → 誠信約束 → 報告模板欄位）

**PR 2：judge-review 查證強化（P0，建議 4）**
- 改 `commands/judge-review.md`
- 主題：符號查證工具指定 + 自我否證義務
- 獨立於 PR 1，可平行 review

**PR 3：規範強化（P1，建議 5+6+7+9）**
- 改 `rules/lsp-navigation.md` + `rules/acceptance-evidence.md` + `commands/audit-test.md`（長任務段落、PropertyMock 段落）+ `skills/agent-workflow/SKILL.md` + 可能新增 context-engineering 段落
- 跨多檔，但每個改動小
- 建議 9（PropertyMock）跨檔較多，可考慮拆出獨立 PR

**建議 8（反思閉環，P2）**
- 單獨處理，等其他建議落地後再回頭看（反思的素材需要其他建議產生）
- 或直接併入 PR 1（同屬 audit-test.md）

### 實施順序建議

```
1. PR 1（audit-test 誠信化）→ 落地後下次 audit 立即受惠
2. PR 2（judge-review 強化）→ 與 PR 1 平行
3. PR 3（規範強化）→ PR 1/2 落地後，避免改動衝突
4. 建議 8（反思閉環）→ 最後，作為流程閉環
```

### 風險評估

| 風險 | 機率 | 緩解 |
|------|------|------|
| audit-test.md 規範膨脹（建議 1+2+3+7+8+9 都改同檔） | 中 | 落地後用 `/claude:distill` 蒸餾，保持 signal/noise |
| 規範改了但 agent 行為不變（建議 9 根因） | 高 | 改規範 + 同時改 agent prompt 模板（lsp-navigation、agent-workflow）雙管齊下 |
| 過度工程（把個案上升成規範） | 中 | 建議 8「反思的反思」段落已內建防護；落地後觀察是否真的反覆發生 |

### 不建議改的（避免過度工程）

以下雖然在這次經驗中出現，但**不建議上升成規範**：

- **「LightGBM 預設 seed 行為」寫進規範** — 這是套件特定知識，寫進通用 ai-rules 會污染（屬專案 `model/CLAUDE.md` 範疇，如果需要的話）
- **「每個 rg pattern 都要雙查」變成通用規則** — 只在 audit/judge-review 的高風險查證場景要求（建議 1/4/5），不擴及日常 rg 使用
- **「所有 audit finding 都要實證」** — 只要求技術/套件行為判斷實證（建議 2.2），證據型 finding（如 `pass` body）讀過原始碼即可

---

## 附錄：這次經驗的「教訓 → 建議 → 規範段落」完整對應表

| 教訓 # | 教訓摘要 | 對應建議 | 規範段落 |
|--------|---------|---------|---------|
| #1 | audit false positive（I4/I5 單一 rg pattern） | 建議 1, 2, 3, 5 | audit-test 角度 2/6、誠信約束、報告模板、lsp-navigation 反例 |
| #2 | judge-review 查證失誤（I1 rg pattern 失誤） | 建議 4, 5 | judge-review 查證工具指定、lsp-navigation 反例 |
| #3 | audit rationale 過度陳述（C2 LightGBM seed） | 建議 2 | audit-test 誠信約束 §2（技術判斷必須實證） |
| #4 | 長任務 findings 因 429 中斷未保存 | 建議 7 | audit-test Daily Scan 長任務落盤 |
| #5 | agent 只回報摘要丟失細節 | 建議 2 | audit-test 誠信約束 §3（findings 格式嚴格） |
| #6 | 調查 agent 誤判 fixture 型別（I11） | 建議 9 | audit-test 角度 3 PropertyMock、agent prompt 注入 |
| #7 | 規範已補但 agent 重蹈覆轍（B1） | 建議 9 | audit-test 角度 3、context-engineering 規範即時性 |
| #8 | 多層驗證價值（audit → judge → 實作） | 建議 2, 3 | audit-test 誠信約束 §4（多層驗證設計意圖） |
| #9 | 整合器型測試抓 source bug（C3 正向） | 建議 6 | acceptance-evidence L3 正向實例 |
| #10 | 流程缺反思閉環 | 建議 8 | audit-test 反思閉環段落 |

---

## 結語

這 10 個教訓的本質是**單一 AI 層（audit / judge-review / 實作）都會錯**，唯一防線是多層交叉驗證 + 每層承認自己可能錯的誠信約束。現有 ai-rules 已有 L3 整合層、整合器型判定、mock 循環論證等理論基礎，**缺的是**：

1. 把「audit / judge-review 也會錯」明確寫進對應命令（建議 2/4）
2. 把「符號查證優先 LSP」落實到 audit / judge-review 的具體場景（建議 1/4/5）
3. 把「findings 是待驗證非定論」變成報告格式（建議 2/3）
4. 把「這次經驗」滾動成下次的規範（建議 8）

落地後，下次大型 audit-test 的 false positive 率應顯著下降，且即使有 false positive，下游客層（judge-review / 實作）也能更快識別。
