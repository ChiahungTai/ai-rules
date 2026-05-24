---
description: "測試失敗修復 — 先分類再修復，防止盲目讓測試通過"
when_to_use: "Fix failing tests with first-principles classification. Use when tests fail after refactoring, implementation changes, or when pasting test failure logs. Forces classification before any fix."
usage: "/fix-test [測試失敗 log]"
argument-hint: "可貼測試失敗 log。無參數時自動從 git 變更推斷受影響的測試"
allowed-tools: ["Read", "Edit", "Bash", "Grep", "Agent"]
---

# /fix-test — 測試失敗分類修復

測試失敗不是「讓它通過就好」。重構頻繁的專案中，測試失敗可能代表**程式碼有 bug**，也可能代表**測試該重寫**。本命令強制分類後再修復。

委託 Skills（需要深度 debug 時按需載入）：
- [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md) — 系統化 root cause 診斷（Type A 適用）
- [test-driven-development](../skills/test-driven-development/SKILL.md) — 測試撰寫方法論（Type B/C 適用）

---

## 核心原則

**先分類，再修復。未經分類的修復是盲目的。**

LLM 遇到測試失敗時的預設偏誤是「讓測試通過」。本命令強制在修復前先判斷：**是程式碼錯了，還是測試過時了？**

---

## 執行流程

### 階段 0：Context Gathering

兩種模式：

**模式 A — 用戶已貼 failure log**：
- 解析失敗測試名稱和錯誤訊息
- 若用戶未提及變更範圍，從 `git diff HEAD~1` + uncommitted diff 推斷源碼變更
- 直接進入階段 2

**模式 B — 未貼 log，從 git 推斷**：
1. 分析 uncommitted changes（`git diff HEAD` + `git diff --cached`）和 last commit（`git diff HEAD~1`）
2. 識別變更的 source 檔案 → 推斷對應 test 檔案（同名慣例：`foo.py` → `test_foo.py`）
3. 輸出推斷結果，詢問用戶：
   - 推斷的測試範圍是否正確？
   - 是否要加減測試檔案？
   - 確認後進入階段 1

### 階段 1：Run Tests

```bash
uv run pytest <targets> -v --tb=short
```

- 捕獲完整輸出（含 traceback）
- 識別所有 FAILED 項目
- 無失敗 → 報告通過，結束

### 階段 2：Failure Classification（核心）

對**每個**失敗測試，執行以下分析：

1. **讀取測試碼** — 理解測試的意圖（測的是什麼行為？）
2. **讀取變更的源碼** — 理解最近的契約變化（API 改了什麼？）
3. **分類** — 根據下方標準判斷類型
4. **附理由** — 為什麼是這個類型而非其他

#### 四類失敗分類

| 類型 | 名稱 | 判斷標準 | 行動 |
|------|------|----------|------|
| **A** | 實作缺陷 | 新改的 code 邏輯有錯，測試正確抓到問題 | 修程式碼 |
| **B** | 契約變更 | 重構改了 API 簽名、回傳型別、行為語意，測試仍用舊契約 | 重寫測試 |
| **C** | 測試腐化 | 測試耦合實作細節（private method、內部狀態、排序依賴），非行為面的 | 重寫測試 |
| **D** | 基礎設施 | Import error、fixture 過時、conftest 缺設定、path 問題 | 修測試基礎設施 |

#### 分類決策樹

```
測試失敗
├── 是 import error / fixture error / setup error？
│   └── YES → Type D（基礎設施）
├── 變更了 API 簽名或回傳型別？
│   ├── 測試使用舊簽名 → Type B（契約變更）
│   └── 測試使用新簽名但結果不對 → Type A（實作缺陷）
├── 測試耦合實作細節（private、內部狀態）？
│   └── YES → Type C（測試腐化）
├── 重構改了行為語意（同一函式，不同語意）？
│   └── YES → Type B（契約變更）
└── 以上皆非 → Type A（實作缺陷）
```

#### Type B/C 重寫的強制要求

**Type B（契約變更）** 必須回答：
- 舊契約是什麼？（測試原本期望的行為）
- 新契約是什麼？（重構後的實際行為）
- 新測試如何驗證新契約？

**Type C（測試腐化）** 必須回答：
- 測試耦合了哪些實作細節？
- 正確的行為面測試應該測什麼？
- 新測試如何只測行為不測實作？

### 階段 3：Present + Confirm

**所有類型（A/B/C/D）都須用戶確認後才動手。**

輸出格式：

```
## 測試失敗分類報告

### 摘要

| 測試 | 類型 | 行動 | 說明 |
|------|------|------|------|
| test_xxx | A（實作缺陷） | 修程式碼 | ... |
| test_yyy | B（契約變更） | 重寫測試 | 舊：... → 新：... |
| test_zzz | C（測試腐化） | 重寫測試 | 耦合了 ... |

### 建議執行順序
1. [先修哪個，為什麼]
2. [再修哪個]

確認後開始修復？(y/n/調整)
```

### 階段 4：Execute + Verify

按確認的順序執行修復：

- **Type A**：修程式碼，不改測試。修完跑測試確認通過。
- **Type B/C**：重寫測試。必須先說明新測試的意圖，再撰寫。跑測試確認通過。
- **Type D**：修基礎設施（conftest、fixture、import）。跑測試確認通過。

每個修復完成後立即驗證該測試。全部完成後跑一次受影響的完整測試套件（背景跑）。

---

## 禁止行為

- ❌ 偷改 assertion 數值或字串讓測試通過（未理解契約變更就改 assertion = 盲目修復）
- ❌ 用 `@pytest.skip`、`@pytest.mark.xfail` 壓制失敗
- ❌ 放寬 assertion（`==` → `in`、移除檢查項、`assertAlmostEqual` 替代 `assertEqual`）
- ❌ 改 test setup 繞過失敗路徑（改 fixture 只為了避開報錯的 code path）
- ❌ 只改測試碼但不理解契約為什麼變了
- ❌ 跳過分類直接修復

---

## 與其他命令的協作

```
/refactor 或手動重構 → 測試失敗 → /fix-test → /lint-fix → /commit
/build 段落驗證失敗 → /fix-test（分類後決定修 code 或修 test）
```

---

## 品質檢查清單

- [ ] 每個失敗測試都已分類（A/B/C/D）
- [ ] Type B/C 有說明新契約或正確行為
- [ ] 用戶確認後才開始修復
- [ ] 每個修復後都驗證該測試通過
- [ ] 全部修復後跑完整受影響測試套件
- [ ] 未使用任何禁止行為
