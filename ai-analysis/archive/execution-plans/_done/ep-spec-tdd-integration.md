# EP: Spec-Driven × TDD 整合 — build.md + TDD Skill 增强

## 實作總覽

| 段落 | 職責 | 依賴 |
|------|------|------|
| S1 | TDD Skill 增强（測試分類 + Fixture 策略 + EP 整合） | 無 |
| S2 | build.md Stage 2 TDD 步驟加强 | S1 |

**段落劃分策略**：S1 是內容主要增量（TDD skill 三個新區段），S2 是消費端改動（build.md 引用 S1 的 EP Integration）。S1 完成後 S2 自然跟進。

---

## S1: TDD Skill 增强

### Context

- **背景**：用戶開發流程偏向 spec-driven（/spec → /execution-plan → /build），但 TDD 端一致性不足。觀察過去一個月 git 歷史：測試有時逐段 TDD、有時整合套件一次性補上、有時從 POC script 遷移。測試品質本身很好（unit/integration/case_studies 三層成熟），但 **TDD 一致性** 和 **EP → TDD 轉譯** 是斷層。
- **UC 引用**：無（跨專案方法論改善，不影響特定 UC）
- **依賴**：無
- **語義約束**：以下術語在 S1 和 S2 間必須一致（取自 `execution-plan.md` 驗證策略格式）：
  - 「測試類型分佈」
  - 「關鍵情境覆蓋」
  - 「已知未覆蓋的風險」
  - 「完成檢查」
- **基礎設施盤點**：
  - `test-driven-development/SKILL.md` → 被修改的目標檔案
  - `mosaic_alpha/tests/` 實際測試體系 → 提煉通用 pattern 的參考來源（已驗證存在，含 unit_tests / integration_tests / external_api / case_studies 四層）
  - `execution-plan.md` 驗證策略格式 → S1 Section C 的消費端
- **依賴錨點**：
  - `test-driven-development` skill → 定義 `skills/test-driven-development/SKILL.md` / 消費 `commands/build.md`（S2 會引用）
- **技術選型**：純 Markdown 編輯，不改程式碼
- **成功標準**：
  - [ ] TDD skill 新增 Test Classification、Fixture Strategy、EP Integration 三個區段
  - [ ] 原有內容（Prove-It Pattern、Tests Verify Intent、Test What Matters、Verification checklist）完整保留
  - [ ] 新區段使用跨專案通用語言，不綁定特定專案（如 mosaic_alpha）— 驗證：`rg "mosaic_alpha" skills/test-driven-development/SKILL.md` 應無匹配

### 核心實作要點

#### 1. 新增區段位置

在現有「## Verification」區段**之前**插入三個新區段，保持原有內容順序不變：

```
現有結構：
  # Test-Driven Development
  ## Overview
  ## The Prove-It Pattern
  ## Tests Verify Intent, Not Just Behavior
  ## Test What Matters
  ## Subagent Testing Pattern
  ## Browser Testing
  ## Verification          ← 在此之前插入

插入後結構：
  # Test-Driven Development
  ## Overview
  ## The Prove-It Pattern
  ## Tests Verify Intent, Not Just Behavior
  ## Test What Matters
  ## Subagent Testing Pattern
  ## Browser Testing
  ## Test Classification          ← NEW A
  ## Fixture & Mock Strategy      ← NEW B
  ## EP Integration               ← NEW C
  ## Verification
```

#### 2. Section A: Test Classification

決策樹讓 AI 判斷每個測試的類型和歸屬目錄。從 mosaic_alpha 的四層測試體系（unit_tests / integration_tests / external_api / case_studies）提煉通用規則。

關鍵判斷軸：
- 是否涉及外部系統（DB、API、filesystem）
- 是否驗證跨模組互動
- 是否需要真實外部服務

#### 3. Section B: Fixture & Mock Strategy

從 mosaic_alpha 實際測試體系提煉的通用 pattern，不提專案名稱：

- **Scope 選擇原則**：session（昂貴資源共用）→ module（同類測試）→ function（隔離）
- **Mock 階層**：繼承式 Mock > Patch > Fake，附理由
- **Ground Truth Pattern**：昂貴計算 session-scoped，後續比對
- **Golden Master Pattern**：持久化預期值，偵測回歸

#### 4. Section C: EP Integration

告訴 AI 如何把 EP 驗證策略轉為 TDD 的 test list：

1. 「測試類型分佈」→ 測試目錄 + fixture scope
2. 「關鍵情境覆蓋」→ 每個情境 = 一個 test function（RED 的 test list）
3. 「已知未覆蓋的風險」→ 標記 TODO 或 skip，不默默跳過
4. 實作完成 → 「完成檢查」逐項驗證

### Pseudo Code

```
檔案結構（修改既有檔案）：
skills/test-driven-development/
└── SKILL.md    # 修改（新增三個區段）
```

```markdown
<!-- 在 "## Browser Testing" 和 "## Verification" 之間插入 -->

## Test Classification

在 RED 階段，先分類每個測試的類型，再決定放哪裡、用什麼 fixture。

**分類決策**：

| 問題 | 是 | 否 |
|------|------|------|
| 測試對象涉及外部系統（DB、API、filesystem）？ | integration | unit |
| 測試驗證跨模組互動？ | integration | unit |
| 測試需要真實外部服務（無法 mock）？ | external API test | 用 mock/fake |

**目錄歸屬**：
- **Unit**：`tests/unit_tests/` — 快速、mock、純函數邏輯
- **Integration**：`tests/integration_tests/` — 真實 DB、跨模組、需要 fixture
- **External API**：`tests/external_api/` — 真實外部服務，加 skip 機制（資源限制、時段限制）
- **Case Study**（可選）：`tests/case_studies/` — 理論驗證 vs 真實數據對齊

**原則**：不確定時歸類為 integration — 寧可多隔離也不要 unit test 裡藏外部依賴。

## Fixture & Mock Strategy

### Scope 選擇

| Scope | 適用場景 | 範例 |
|-------|---------|------|
| `session` | 昂貴資源、建構慢、可安全共用 | DB 連線、外部 API 回應快取、Ground Truth 計算 |
| `module` | 同類測試共用、中等建構成本 | 模組級 conftest、同類 API 回應 |
| `function` | 需要隔離、每次用新狀態 | 單一測試的 mock instance |

**錯誤模式**：用 function scope 建立 DB 連線 → 測試慢 10×。用 session scope 建立可變狀態 → 測試互相污染。

### Mock 階層（推薦度由高到低）

1. **繼承式 Mock**：`class MockClient(RealClient)` — 繼承真實 class，只 override 需要的方法。保留真實行為，重構時測試不易斷。
2. **Patch**：`@patch("module.Client")` — 直接替換。簡單但 brittle，重構時容易斷。
3. **Fake**：完整實作介面的輕量版本。成本高但最穩定。

### 資料管線測試模式

- **Ground Truth Pattern**：昂貴計算只做一次（session-scoped fixture），後續測試比對基準值。適用：特徵計算、統計指標。
- **Golden Master Pattern**：持久化預期值到 JSON/檔案。首次執行記錄並 skip，後續執行比對。適用：標籤生成、複雜轉換邏輯。

## EP Integration

EP（Execution Plan）的驗證策略是 TDD 的輸入。在 RED 階段按以下步驟轉譯：

1. **讀「測試類型分佈」**（單元 / 整合 / E2E / 外部 API mock）→ 決定每種測試放哪個目錄、用什麼 fixture scope
2. **讀「關鍵情境覆蓋」**（happy path、邊界案例、error handling、冪等性）→ 每個情境寫一個 test function（這就是 RED 的 test list）
3. **讀「已知未覆蓋的風險」** → 標記為 `# TODO: EP 標記未覆蓋` 或 `pytest.mark.skip(reason="EP 標記未覆蓋")`，**不默默跳過**
4. **實作完成後** → 對 EP 的「完成檢查」逐項驗證，確認每項都有對應測試覆蓋

**關鍵**：EP 的驗證策略是 TDD 的「合約」— 如果 EP 說要測某個情境但沒測，等同段落在撒謊。
```

### 驗證策略

- **測試類型**：手動閱讀驗證（純 Markdown 修改）
- **關鍵情境覆蓋**：
  - 三個新區段結構完整、內容清晰
  - 原有區段未被修改或刪除
  - 新區段不綁定特定專案名稱（不出現 "mosaic_alpha"）
  - EP Integration 的轉譯步驟具體可執行（AI 能按步驟操作）
- **已知未覆蓋**：專案特定的測試規則（如 trading hours protection）留給專案 CLAUDE.md
- **完成檢查**：
  - [ ] SKILL.md 新增 Test Classification、Fixture & Mock Strategy、EP Integration 三個 `##` 區段
  - [ ] 原有 Prove-It Pattern / Tests Verify Intent / Test What Matters / Subagent / Browser / Verification 區段完整
  - [ ] 新區段無特定專案名稱

---

## S2: build.md Stage 2 TDD 步驟加强

### Context

- **背景**：build.md 的 EP 元素 → TDD 步驟表格只說「驗證策略 | RED | 照設計寫測試」，太模糊。AI 不知道要把 EP 驗證策略轉譯為具體測試分類。S1 已增强 TDD skill 的 EP Integration 區段，S2 讓 build.md 消費這個增强。
- **UC 引用**：無
- **依賴**：S1（TDD skill EP Integration 區段完成）
- **語義約束**：與 S1 共享以下術語（取自 `execution-plan.md` 驗證策略格式）：
  - 「測試類型分佈」
  - 「關鍵情境覆蓋」
  - 「已知未覆蓋的風險」
  - 「完成檢查」
- **基礎設施盤點**：
  - `build.md` → 被修改的目標檔案
  - `test-driven-development` skill → S1 增强的 EP Integration 區段
  - `commands/execution-plan.md` → 引用 build.md workflow（受影響模組）
- **依賴錨點**：
  - TDD skill EP Integration → 定義 `skills/test-driven-development/SKILL.md`（S1 產出）/ 消費 `commands/build.md`（S2 修改處）
- **技術選型**：純 Markdown 編輯，一行表格修改
- **成功標準**：
  - [ ] build.md 的 EP 元素表格中，「驗證策略 | RED」那行更新為具體的轉譯步驟
  - [ ] 「核心要點 | REFACTOR」那行更新為「對 EP 完成檢查逐項驗證」

### 核心實作要點

修改 `commands/build.md` line 65-67 的表格。只改兩行的「說明」欄位：

**現狀**：
```
| 驗證策略 | RED | 照設計寫測試 |
| Pseudo Code | GREEN | 照設計實作 |
| 核心要點 | REFACTOR | 檢查覆蓋 |
```

**改為**：
```
| 驗證策略 | RED | 讀 EP 測試類型 → 分類情境 → 寫對應測試（詳 TDD skill EP Integration） |
| Pseudo Code | GREEN | 照設計實作 |
| 核心要點 | REFACTOR | 對 EP 完成檢查逐項驗證 |
```

### Pseudo Code

```
檔案結構（修改既有檔案）：
commands/
└── build.md    # 修改（Stage 2 表格兩行）
```

精確修改：
1. `照設計寫測試` → `讀 EP 測試類型 → 分類情境 → 寫對應測試（詳 TDD skill EP Integration）`
2. `檢查覆蓋` → `對 EP 完成檢查逐項驗證`

### 驗證策略

- **測試類型**：手動閱讀驗證
- **關鍵情境覆蓋**：
  - 表格修改精確（只改兩行，不動其他行）
  - 新文字與 S1 TDD skill 的 EP Integration 區段用語一致
  - 不破壞 build.md 現有結構
- **完成檢查**：
  - [ ] build.md line 65 說明欄位更新
  - [ ] build.md line 67 說明欄位更新
  - [ ] 其餘行未改動

---

## 整合策略

### 階段閘門

```
S1 完成（TDD skill 三個新區段）
  ↓ 閘門: 閱讀 SKILL.md 確認結構完整 + 無專案名稱洩漏
S2 完成（build.md 表格更新）
  ↓ 閘門: 閱讀 build.md 確認引用一致
```

### 風險與緩解

| 風險 | 緩解 |
|------|------|
| TDD skill 新區段太長，增加 token 消耗 | 每個區段控制在 10-15 行，用表格壓縮 |
| 新區段用語與 build.md 不一致 | S2 完成後交叉檢查用語 |
| AI 無法正確分類測試 | 分類決策樹用 yes/no 表格，非開放式描述 |
