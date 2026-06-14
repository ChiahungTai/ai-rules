---
description: "測試品質稽核 — 反模式偵測、覆蓋對稱性、mock 健康度。只讀不寫。"
when_to_use: "Audit test quality: detect anti-patterns, coverage gaps, and over-mocking. Use after /build, before /commit, or in nightly scheduled scans. Read-only report, does not modify any files."
usage: "/audit-test [commit-id] [--daily]"
argument-hint: "/audit-test — uncommitted | /audit-test fd7a50e8 — commit | /audit-test --daily — 全專案"
allowed-tools: ["Read", "Bash"]
---

# /audit-test — 測試品質稽核

偵測**通過但品質差**的測試。`ruff` 抓語法問題，`/fix-test` 修失敗測試，本命令抓**隱性品質問題**。

方法論定義見 [test-driven-development](../skills/test-driven-development/SKILL.md)（反模式定義）、[must-execute-before-complete](../rules/must-execute-before-complete.md)（覆蓋對稱性）。

---

## 價值定位

| 工具 | 抓什麼 | 不抓什麼 |
|------|--------|---------|
| `ruff` / `mypy` | 語法、型別、import | 測試邏輯品質 |
| `/fix-test` | **已失敗**的測試（分類 A/B/C/D/E 再修） | **通過但有反模式**的測試 |
| **`/audit-test`** | **通過但有反模式的測試** | 語法問題（交給 ruff） |

測試通過 ≠ 測試有價值。幽靈斷言的測試永遠通過，但它驗證不了任何事。

---

## 三種輸入模式

| 模式 | 參數 | 掃描範圍 | 場景 |
|------|------|---------|------|
| **Diff Audit** | 無參數 | uncommitted test files | pre-commit gate |
| **Commit Audit** | `fd7a50e8` | 該 commit 的 test file 變更 | post-commit review |
| **Daily Scan** | `--daily` | 全部 test files | 每晚排程 → 整合至 /standup |

### 掃描範圍判定

**Diff Audit**：`git diff HEAD` + `git diff --cached` 中 `tests/` 下的 `.py` 檔案。
**Commit Audit**：`git show <commit-id> --stat` 中 `tests/` 下的 `.py` 檔案。讀取 commit diff 取得完整 test body。
**Daily Scan**：`fd -e py . tests/` 全部 test files。受影響的 source files = 所有被 import 的模組。

---

## 6 個檢查角度

| # | 角度 | 對應標準 | 嚴重程度 |
|---|------|---------|---------|
| 1 | 反模式掃描 | test-driven-development SKILL.md（5 項） | Critical / Important |
| 2 | 覆蓋對稱性 | must-execute-before-complete | Important |
| 3 | Mock 健康度 | test-driven-development SKILL.md（Mock 階層） | Important |
| 4 | 消費端驗證覆蓋 | acceptance-evidence L3 + quality-constraints 符號 vs 路徑覆蓋 | Important / Suggestion |
| 5 | 漸進驗證合規 | progressive-validation DEPTH-MIN 集合 | Suggestion |
| 6 | 測試必要性 | acceptance-evidence 證據時效性 | Important / Suggestion |

---

## 檢查角度詳細定義

### 角度 1：反模式掃描

對每個 test function，逐一檢查以下 5 項反模式（定義見 [test-driven-development](../skills/test-driven-development/SKILL.md)）：

| 反模式 | 偵測方式 | 嚴重程度 | 判斷標準 |
|--------|---------|---------|---------|
| **幽靈斷言** | 掃描 assert 語句品質 | Important | test body 只有 `assert result is not None` / `assert len > 0` / 無 assert；或 assert 存在但與 docstring 描述的行為無關 |
| **同義反覆** | 比對 test 與 source 的 hardcoded 值 | Important | test 的 expected value 和 source code 中的值完全相同（同一個 magic number 兩邊各寫一次） |
| **空殼覆蓋** | 掃描 test body 結構 | Critical | test function 只有 `pass` / `...` / `@pytest.mark.skip`（無 reason 或 reason 不含 "EP 標記"） |
| **過度 mock** | 計算 mock/assert 比例 | Important | test file 中 `@patch` / `Mock()` / `mock_` 出現次數 > `assert` 出現次數 |
| **標題不符** | 比對 test name 與 assert 內容 | Suggestion | test function name 暗示測某行為（如 `test_dividend_calculation`），但 assert 驗證的是另一件事（如只檢查 type） |

**偵測方式**：

1. 讀取 test file，提取所有 test function（名稱、docstring、body）
2. 對每個 test function：
   - 計算 assert 數量和類型
   - 計算 mock 數量（`@patch`、`Mock()`、`mock_` 變數）
   - 比對 docstring/test name 語義與 assert 實際驗證對象
   - 檢查是否有 `@skip`、`pass`、`...`
3. 讀取對應的 source file，比對 hardcoded 值

### 角度 2：覆蓋對稱性

**核心原則**：修改了 source code，必須有對應的 test 驗證。

| 檢查項 | 嚴重程度 | 驗證方式 |
|--------|---------|---------|
| 修改了 `.py` 但沒有修改對應 test（或最近 N 個 commit 都沒改 test） | Important | 比對 `git diff` 中 source files vs test files |
| 新增了 public class/function 但無 test 引用 | Important | 見下方「覆蓋搜尋策略」 |
| test file 存在但對應 source file 已刪除 | Important | `test -f` 驗證 source 存在 |
| 新增 registry 成員（auto-discovery）但無 membership 斷言 | Important | `rg "list_.*_classes" <test files>` + 檢查 `"<ClassName>" in {c.__name__ ...}`；per-class 單元測試只 import 不代表接上 registry（見 [quality-constraints](../rules/quality-constraints.md) 符號 vs 路徑覆蓋） |

**判斷邏輯**：
- Source `foo.py` → 對應 test `test_foo.py`（同名慣例）為主要測試檔案
- 新增 class/function 在 `__init__.py` 或 `__all__` → 搜尋所有 test files

**覆蓋搜尋策略**（區分 function vs method）：

覆蓋判斷必須區分三種粒度，不可一概用 import 搜尋：

| 粒度 | 搜尋方式 | 範例 |
|------|---------|------|
| **standalone function** | `rg "from module import func"` 或 `rg "func("` in tests | `rg "compute_adj_factors" tests/` |
| **class 本身** | `rg "from module import ClassName"` in tests | `rg "TWSecurityIndex" tests/` |
| **class method** | 找到 class 的 import 後，追蹤 instance 上的 method call | 見下方 Method Coverage 流程 |

**Method Coverage 流程**（避免將有覆蓋的方法誤判為零覆蓋）：

1. **建立候選清單**：從 source file 提取所有 public method（排除 `_` 開頭）
2. **找測試檔案**：不只看同名 `test_foo.py`，用 `rg "ClassName" tests/ -l` 找所有引用該 class 的 test files
3. **搜尋 method call**：對每個候選 method，在所有找到的 test files 中搜尋 `.method_name(` pattern
4. **判定零覆蓋**：只有當 method 在**所有** test files 中都不出現時，才判定為零覆蓋
5. **交叉驗證**：報告前用 `rg "\.method_name\(" tests/` 確認，避免單一檔案掃描遺漏

### 角度 3：Mock 健康度

**核心原則**：Mock 應該用最少代價隔離外部依賴，不是把被測系統也隔離掉。

| 檢查項 | 嚴重程度 | 判斷標準 |
|--------|---------|---------|
| Mock 比例 > 50%（mock 數 > assert 數） | Important | test file 層級計算 |
| Mock 被測對象本身（mock 了正在測的 class） | Critical | `@patch("module.ClassUnderTest")` — 如果 mock 了主角，測試什麼？ |
| Mock 層級過低（patch private method / 內部函數） | Suggestion | patch 路徑含 `_` 開頭的函數 |
| 未使用繼承式 Mock（可用但未用） | Suggestion | 多個 test 用相同 `@patch` 組合 → 建議抽取 `MockClient(RealClient)` |

### 角度 4：消費端驗證覆蓋

**核心原則**：功能是給特定消費端用的，單元測試通過 ≠ 功能可用。**符號覆蓋（symbol 出現在 tests）≠ 整合路徑覆蓋（新參數 / 新接線 / 多組件組合被實際驅動）** — 見 [acceptance-evidence](../rules/acceptance-evidence.md) L3 + [quality-constraints](../rules/quality-constraints.md) 符號 vs 路徑覆蓋。

| 檢查項 | 嚴重程度 | 判斷標準 |
|--------|---------|---------|
| 新增 public 參數 / 注入點但消費端路徑無測試 | **Important** | `rg "<新參數>=" tests/` → 0 hits，或 hits 僅符號 import 非路徑驅動 |
| 整合器型變更（接 ≥2 真實組件）只在 unit test 驗證 | **Important** | 缺 L2 真實邊界整合測試（`integration_tests/`），mock 循環論證風險 |
| 修改了 library 模組但只在 unit test 驗證 | Suggestion | source 在 library 層，test 只在 `tests/unit_tests/` |
| 修改了共用模組但未跑跨模組測試 | Suggestion | 修改的模組被 ≥ 2 個 test directory 引用 |

消費端驗證模式定義見 [quality-constraints](../rules/quality-constraints.md) 的「消費端驗證模式」表格。

### 角度 5：漸進驗證合規

**核心原則**：測試集應有 DEPTH-MIN 子集可快速確認基本邏輯。

| 檢查項 | 嚴重程度 | 判斷標準 |
|--------|---------|---------|
| 無 DEPTH-MIN / smoke test marker | Suggestion | `tests/` 下無 `@pytest.mark.quick` / `@pytest.mark.smoke` 或對應 marker |
| 全部測試都是慢速（無分層） | Suggestion | `pytest.ini` / `pyproject.toml` 無 marker 定義 |

定義見 [progressive-validation](../rules/progressive-validation.md)。

### 角度 6：測試必要性

**核心原則**：過時測試比沒測試更危險 — 它給虛假信心。角度 1-5 假設「測試該存在」，本角度質疑「測試還有必要存在嗎」。理論見 [acceptance-evidence](../rules/acceptance-evidence.md)「證據時效性」。

| 檢查項 | 嚴重程度 | 判斷標準 |
|--------|---------|---------|
| 過時測試（重構後 assertion 被改成迎合實作） | Important | 測試在最近重構 commit 被改，改動是 assertion 值/邏輯迎合新實作（非新增案例）— 從「驗證意圖」降級為「反映實作」（同義反覆的動態版本） |
| 死測試（還在過但驗證行為已無關） | Important | 測試斷言的行為與當前 EP/spec 無對應；或測試的消費端已不存在 |
| 大型重構後未重評估的測試 | Suggestion | 重構（行為語意改變）後，受影響測試未被重新檢視必要性 |

**過時偵測流程**：

1. `git log --oneline -20` 找最近重構 commit（行為語意改變，非純重命名/格式）
2. `git show <commit> --stat` 找該 commit 改動的 test files
3. 對這些 test files，diff 看改動是「assertion 值/邏輯迎合新實作」（過時信號）還是「新增測試案例」（正常）
4. assertion 被改成等於新實作輸出 → 過時信號，報 Important

**與角度 1 的區別**：角度 1「同義反覆」是靜態（test/source 同值）；角度 6「過時」是動態（重構後 test 被改迎合）。角度 1 抓不到動態漂移。

---

## 輸出格式

### 報告模板

```markdown
## Audit-Test Report

### 總覽

| 指標 | 數值 |
|------|------|
| 掃描模式 | Diff Audit / Commit Audit / Daily Scan |
| 掃描範圍 | N 個 test files |
| 健康度 | XX% |

### 🔴 Critical（必須修正）

- [ ] **空殼覆蓋**: `test_tw_catalog.py:test_adj_weekly` — 只有 `pass`
- [ ] **Mock 被測對象**: `test_classifier.py:test_classify` — `@patch("module.Classifier")` mock 了主角

### 🟡 Important（建議修正）

- [ ] **幽靈斷言**: `test_pipeline.py:test_run` — 只有 `assert result is not None`
- [ ] **過度 mock**: `test_catalog.py` — 23 個 mock / 8 個 assert（比例 2.9:1）
- [ ] **覆蓋缺口**: `tw_catalog.py` 新增 `_build_agg_exprs()` 但無對應 test
- [ ] **同義反覆**: `test_config.py:test_default` — test 和 source 都 hardcode `42`

### 💡 Suggestion（可以改善）

- [ ] **標題不符**: `test_adj_weekly_path` — 名稱暗示路徑測試，但 assert 驗證欄位存在性
- [ ] **消費端缺驗證**: `features/column_metadata.py` 修改只在 unit test 驗證，建議跑 integration
- [ ] **Mock 層級過低**: `test_fetcher.py:test_fetch` — patch `_internal_retry()`（private method）

### 建議處理方式

| 反模式 | 處理路徑 |
|--------|---------|
| 空殼覆蓋 | `/fix-test --redesign` 或刪除空殼 test |
| 幽靈斷言 | 補充具體業務值斷言（先理解測試意圖） |
| 過度 mock | 重構為繼承式 Mock 或 Real-World Fixture Pattern |
| 覆蓋缺口 | 新增測試（RED → GREEN） |
| 消費端缺驗證 | 在消費端上下文中跑一次完整流程 |

### Audit Summary（結構化結論）

- mode: diff|commit|daily
- files_scanned: N
- critical: X
- important: X
- suggestion: X
- health_score: XX%
- needs_action: true/false
```

### 健康度計算

```
健康度 = (通過檢查的 test function 數 / 總 test function 數) × 100%
```

每個 test function 的觸發檢查項全通過 = 1 個通過。任一 Critical/Important = 不通過。
Diff/Commit Audit 檢查 5 角度（反模式 + 覆蓋對稱性 + mock 健康度 + 消費端驗證覆蓋 + 測試必要性），Daily Scan 檢查全部 6 角度。

| 評分 | 意義 |
|------|------|
| ≥ 90% | ✅ 健康 |
| 70-89% | ⚠️ 需注意 |
| < 70% | ❌ 需修正 |

---

## 執行流程

| 步驟 | 名稱 | 觸發 |
|------|------|------|
| 1 | 定位掃描範圍 | 預設 |
| 2 | 讀取 test files | 預設 |
| 3 | 讀取對應 source files | 預設 |
| 4 | 反模式掃描（角度 1） | 預設 |
| 5 | 覆蓋對稱性（角度 2） | 預設 |
| 6 | Mock 健康度（角度 3） | 預設 |
| 7 | 消費端驗證覆蓋（角度 4） | 預設 |
| 8 | 漸進驗證合規（角度 5） | `--daily` |
| 9 | 測試必要性（角度 6） | 預設 |
| 10 | 產出報告 | 預設 |

### 步驟 1：定位掃描範圍

**Diff Audit**：
```bash
git diff HEAD --name-only -- "tests/"
git diff --cached --name-only -- "tests/"
```

**Commit Audit**：
```bash
git show <commit-id> --name-only -- "tests/"
```

**Daily Scan**：
```bash
fd -e py . tests/
```

### 步驟 2：讀取 test files

完整讀取掃描範圍內的每個 test file，提取：
- test function 名稱、docstring、body
- `@patch` / `Mock()` / `mock_` 數量
- `assert` 數量和類型
- `@skip` / `pass` / `...` 標記

### 步驟 3：讀取對應 source files

從 test files 的 import 語句推斷 source files，讀取以比對 hardcoded 值。

### 步驟 4-9：逐一檢查

對每個 test function，按角度 1-3 的標準檢查（步驟 4-6）。步驟 7-9（角度 4/5/6）按各自角度定義段落執行。記錄發現。

### 步驟 10：產出報告

按輸出格式模板產出報告。Daily Scan 時，報告寫入 `/Users/ctai/logs/claude-sync-{YYYYMMDD}.log`（由夜間排程腳本管理），供 `/standup` 步驟 5 消費。

---

## 與其他命令的協作

| 命令 | 與 /audit-test 的關係 |
|------|---------------------|
| `/fix-test` | 互補：fix-test 修**失敗**的測試，audit-test 偵測**通過但品質差**的測試 |
| `/standup` | Daily Scan 結果整合至晨間簡報（步驟 5） |
| `/code-review` | Correctness 軸可引用 audit-test 發現 |
| `/build` | 段落完成後跑 audit-test 確認測試品質 |
| `/commit` | pre-commit gate：audit-test 無 Critical 才建議 commit |

### 測試品質完整流程

```
寫測試 → /audit-test（偵測反模式）→ 發現問題 → 人類判斷
  ├─ 簡單修正（改名、補斷言）→ 直接改
  ├─ 重構測試（過度 mock → Real-World Fixture）→ /build 段落
  └─ 刪除壞測試（空殼）→ 確認後刪除
```

### 設計不良測試的處理路徑

| 情境 | 工具 | 說明 |
|------|------|------|
| 測試**失敗**了 | `/fix-test` | 分類 A/B/C/D/E → 修 source 或修 test |
| 測試**通過但有反模式** | `/audit-test` → 人類判斷 → 對話修正 | 偵測 → 報告 → 決策 → 執行 |
| 需要從頭重寫壞測試 | `/build` 段落或對話指令 | 按反模式修正建議重寫 |

**核心原則**：修正反模式需要**理解測試意圖**，無法全自動。`/audit-test` 是偵測器（眼睛），不是修復器（手）。修復的決策權在人類。

---

## 執行約束

- **只讀不寫**：本命令只檢查和報告，不自動修改任何檔案
- **必須讀取實際程式碼**：不憑檔名猜測測試品質，必須讀取 test body
- **引用來源**：報告問題時標註具體位置（test file:function name）
- **繁體中文輸出**：報告使用繁體中文 + 英文術語
- **不重複 ruff 工作**：語法問題交給 ruff，本命令只關注邏輯品質
