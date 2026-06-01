---
name: test-driven-development
description: Drives development with tests. Use when implementing any logic, fixing any bug, or changing any behavior. Use when you need to prove that code works, when a bug report arrives, or when you're about to modify existing functionality.
---

# Test-Driven Development

Write a failing test before writing the code that makes it pass. Tests are proof — "seems right" is not done.

---

## The Prove-It Pattern (Bug Fixes)

**Do not start by fixing the bug.** Start by writing a test that reproduces it.

1. Write a test that demonstrates the bug → test FAILS (bug confirmed)
2. Implement the fix → test PASSES (fix proven)
3. Run full suite → no regressions

This guarantees the bug can't resurface silently.

## Tests Verify Intent, Not Just Behavior

Every test must encode **why** the behavior matters. A test that can't fail when business logic changes is a broken test.

**Worthless**: both the function and the test hardcode the same value — proves nothing.
**Meaningful**: test constrains the output against a business rule — would fail if logic changes.

**Rule**: If you can't write a test that fails when the business logic changes, either the function is wrong or the test is wrong.

## 測試反模式自檢

寫完每個測試後，確認沒有踩入以下陷阱：

| 反模式 | 辨識特徵 | 修正 |
|--------|---------|------|
| **幽靈斷言** | 標題說測 X，但 body 只有 `assert result is not None` | 斷言具體業務值 |
| **同義反覆** | function 和 test 都 hardcode 同一個值，證明不了任何事 | 用獨立計算或業務規則驗證 |
| **空殼覆蓋** | 有 test function 但用 `@skip` 跳過或 body 只有 `pass` | 要麼刪要麼補實作 |
| **過度 mock** | test file 中 mock 數量 > assert 數量 | 改用繼承式 mock 或 real impl |
| **標題不符** | test 名稱暗示測某行為，但 assert 驗證的是另一件事 | 名稱和斷言必須一致 |

**自檢時機**：每個 test function 寫完後立即對照此表。RED 階段就該發現反模式，不要等到 GREEN。

## Test What Matters

- **State over interactions**: Assert on outcomes, not on which methods were called. Interaction tests break on refactor.
- **Real implementations over mocks**: Real > Fake > Stub > Mock. Over-mocking creates tests that pass while production breaks.
- **One assertion per concept**: Each test verifies one behavior, named descriptively.

## Subagent Testing Pattern

For complex bug fixes, spawn a subagent to write the reproduction test. The main agent then verifies the test fails, implements the fix, and verifies it passes. This separation ensures the test is written without knowledge of the fix.

## Browser Testing

For anything that runs in a browser, combine unit tests with runtime verification via Chrome DevTools MCP — DOM inspection, console errors, network requests, screenshots. See [browser-testing-with-devtools](../browser-testing-with-devtools/SKILL.md).

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
3. **Fake**：完整實作介面的輕量版本。成本高但最穩定。適用於核心介面、跨多模組共用。

### 資料管線測試模式

- **Ground Truth Pattern**：昂貴計算只做一次（session-scoped fixture），後續測試比對基準值。適用：特徵計算、統計指標。
- **Golden Master Pattern**：持久化預期值到 JSON/檔案。首次執行記錄並 skip，後續執行比對。適用：標籤生成、複雜轉換邏輯。

## EP Integration

EP（Execution Plan）的驗證策略是 TDD 的輸入。在 RED 階段按以下步驟轉譯：

1. **讀「測試類型分佈」**（單元 / 整合 / E2E / 外部 API mock）→ 決定每種測試放哪個目錄、用什麼 fixture scope
2. **讀「關鍵情境覆蓋」**（happy path、邊界案例、error handling、冪等性）→ 每個情境寫一個 test function（這就是 RED 的 test list）
3. **讀「已知未覆蓋的風險」** → 標記為 `# TODO: EP 標記未覆蓋` 或 `@pytest.mark.skip(reason="EP 標記未覆蓋")`，**不默默跳過**
4. **實作完成後** → 對 EP 的「完成檢查」逐項驗證，確認每項都有對應測試覆蓋

**關鍵**：EP 的驗證策略是 TDD 的「合約」— 如果 EP 說要測某個情境但沒測，等同段落在撒謊。

## Verification

After completing any implementation:

- [ ] Every new behavior has a corresponding test
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] No tests were skipped or disabled
