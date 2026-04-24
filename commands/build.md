---
description: "基於 Execution Plan 逐段實作 — 準備、TDD 實作、驗證、提交"
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [可選：指定段落編號]"
---

# /build — 基於 Execution Plan 逐段實作

你是實作工程師，負責基於 Execution Plan 進行逐段實作。

## 🎯 核心目標

**「準備 → 逐段實作 → 驗證 → 提交」**

每個段落都是一個 Self-Contained Segment，獨立實作、獨立測試、獨立提交。

## 📚 委託 Skills

實作時自動載入以下 skills，提供 HOW 的方法論：

- **`test-driven-development`** — TDD 循環（RED → GREEN → REFACTOR）、測試寫作規範
- **`incremental-implementation`** — 範圍紀律、簡潔優先、漸進式交付、反合理化
- **`debugging-and-error-recovery`** — demo 執行失敗時的系統化除錯

---

## 📋 執行流程

### 階段 1：準備

1. **讀取計畫書**：完整讀取 Execution Plan，識別段落結構、依賴關係、執行順序
2. **查證現有程式碼**：讀取計畫書提到的檔案，確認現有實作狀態
3. **檢查清單**：
   - [ ] Demo 檔案是否需要新增/修改？（`demo_` 前綴）
   - [ ] 測試檔案是否需要新增/修改？（`test_` 前綴）
   - [ ] CLAUDE.md 是否需要同步更新？
   - [ ] 依賴關係是否完整？有循環依賴風險嗎？
   - [ ] 向後相容：預設不考慮，影響外部系統時需確認

### 階段 2：逐段實作

對每個段落執行實作循環。**EP 段落的四個元素直接對應 TDD 步驟**：

| EP 段落元素 | TDD 步驟 | 說明 |
|---|---|---|
| **Context** | 開始前讀取 | 理解背景、依賴、成功標準 |
| **驗證策略** | RED | 照著設計測試，不用自己想 |
| **Pseudo Code** | GREEN | 照著設計實作，不要自己發明 |
| **核心實作要點** | REFACTOR | 檢查是否都涵蓋到了 |

```
讀取 Context → 依驗證策略寫測試（RED）→ 依 Pseudo Code 實作（GREEN）→ 核心要點檢查（REFACTOR）→ 驗證 → Commit → 下一段
```

TDD 的執行細節（怎麼寫測、怎麼寫最少程式碼、怎麼重構）遵循 `test-driven-development` skill。
範圍紀律和簡潔優先遵循 `incremental-implementation` skill。

#### EP 專屬約束

- **照著 EP 寫，不要自己發明**：測試依驗證策略，實作依 Pseudo Code
- **記錄偏差**：與 Pseudo Code 有出入時，記錄差異原因
- **不確定就問**：計畫書不明確、與現有程式碼有出入、多種技術路徑 → 停下來問
- **錯誤自癒**：連續 3 次失敗 → 記錄問題標記 ⚠️，繼續下一段

#### 驗證

每個段落完成後：
- `uv run ruff check --fix . && uv run ruff format .`
- `uv run mypy .`
- `uv run pytest <test_file> -v`
- 確認通過 → Commit → 下一段

### 階段 3：整合驗證

所有段落完成後：
1. **全量 Lint**：`uv run ruff check --fix . && uv run ruff format .`
2. **全量型別檢查**：`uv run mypy .`
3. **全量測試**：`uv run pytest`
4. **Demo 驗證**：
   - 掃描 `demo_*.py` 和 `examples/*.py`
   - 逐一 `uv run python <path>` 執行
   - 失敗時用 `debugging-and-error-recovery` skill 分析根因
   - 輸出通過/失敗報告

---

## 🔧 執行約束

### 強制執行
1. **必須完整讀取計畫書**
2. **必須查證現有程式碼**
3. **每個段落必須 TDD（RED → GREEN → REFACTOR）**
4. **每個段落必須獨立驗證和提交**
5. **每個段落必須通過 ruff + mypy 檢查**

### 禁止行為
- ❌ 跳過測試直接實作
- ❌ 一個段落提交多個不相關的修改
- ❌ 在段落範圍外修改程式碼
- ❌ 使用 `sed` 修改程式碼
- ❌ 中間狀態提交破損的程式碼

---

## 📚 與其他命令的協作

### 流程位置
```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review
```

### 前置命令
- `/execution-plan` — 生成被實作的計畫書
- `/ep-review` — 審查計畫書合理性（三個 LLM）
- `/verify-review` — 評估審查建議，修正計畫書

### 後續命令
- `/code-review` — 實作完成後審查程式碼
- `/commit-message` — 生成提交訊息（若需）

---

## ✅ 完成標準

1. ✅ 所有段落已實作並通過測試
2. ✅ 每個段落有獨立 commit
3. ✅ ruff check + mypy 全量通過
4. ✅ 全量測試通過
5. ✅ Demo 全部通過
