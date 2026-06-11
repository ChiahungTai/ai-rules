---
description: "結構化需求討論 + codebase 研究 + POC 可行性驗證（User Story、假設浮出、風險分級 POC、UC 定義、邊界），為 EP 做準備。/spec [需求描述] [--write] [--research-only]"
when_to_use: "Structure a feature requirement with codebase research and risk-classified POC validation. Use before /execution-plan to verify assumptions and map existing infrastructure."
usage: "/spec [需求描述] [--write] [--research-only]"
argument-hint: "你要做什麼功能或改變"
---

# /spec — 結構化需求討論

EP 前的研究與結構化階段。透過對話整理需求、深度研究 codebase、驗證假設，為 `/execution-plan` 提供已驗證的結構化輸入。

UC-Driven Development 方法論見 [ai-development-guide.md](../ai-development-guide.md) 的「UC-Driven Development」章節。

委託 Skills：
- [spec-driven-development](../skills/spec-driven-development/SKILL.md) — 假設浮出、邊界定義、成功條件量化

---

## 參數

| 參數 | 說明 |
|------|------|
| 無參數 | 預設：對話中產出規格摘要（不寫檔案），可直接接 `/execution-plan` |
| `--write` | 寫入 `ai-analysis/specs/{feature-name}-spec.md`。適用於換 session 時傳遞 context |
| `--research-only` | 只做 Phase 1-2（對齊 + 研究），不進 UC 定義。適用於「先研究看看」的情境 |

---

## 執行流程

### Phase 1: 對齊（2-3 turns）

快速確認方向和範圍，不填表單。

1. **User Story 一句話**：目標 + 痛點 + 範圍
2. **範圍判斷**：

| 規模 | 後續行為 |
|------|---------|
| 大型（跨模組、新功能） | 完整 Phase 1-5 |
| 中型（功能優化、新 API） | Phase 1-5（Phase 3 深度調整） |
| 小型（bug fix、文檔） | 建議直接做，跳過 `/spec` |

3. **規模判斷**：小型變更建議用戶直接做（跳過 /spec），中大型繼續 Phase 2

User Story 格式（參考）：
```
作為 [角色]，我想要 [功能]，因為 [動機]。
目前的痛點：[問題]
現在怎麼處理：[workaround]
```

### Phase 2: Codebase 研究（自動，spawn Explore Agent）

**先讀程式碼，再提假設。禁止憑訓練資料猜測。**

spawn Explore Agent 深度掃描相關模組：

1. **Capabilities 盤點**：搜尋需求涉及的 CLAUDE.md Capabilities + `.kanban/` cards
2. **依賴分析**：相關模組的 import 依賴和介面
3. **可複用基礎設施**：`rg` 搜尋 class/function 使用模式，找出可複用的 utilities、base classes、protocols
4. **類似實作**：搜尋已有類似功能的程式碼，避免重新發明

**產出研究摘要**（對話中呈現）：
- 可複用基礎設施清單（附 `path/to/file.py:ClassName`）
- 依賴關係和關鍵約束
- 類似功能的既有實作位置

### Phase 3: 假設 + POC（風險分級）

基於 Phase 2 研究結果，列出技術假設並驗證。

**假設浮出格式**（遵循 [spec-driven-development](../skills/spec-driven-development/SKILL.md)）：
```
ASSUMPTIONS I'M MAKING:
1. [假設]（來源：path/to/file.py:ClassName）
2. [假設]（來源：用戶確認）
→ 正確的話請告知，否則我將按照這些假設繼續進行。
```

**風險分級驗證**：

| 風險 | 判定標準 | 驗證方式 |
|------|---------|---------|
| 🔴 高風險 | 外部 API、SDK 行為、架構假設、從未用過的函式庫 | 寫 `lab/poc_*.py` 實際執行驗證 |
| 🟢 低風險 | 內部邏輯、已知模式、已驗證過的函式庫 | 文件記錄 + 來源引用 |

高風險假設的 POC 規範：
- 放置 `lab/poc_<描述性名稱>.py`
- 每個 POC 聚焦一個假設，包含 happy path + 至少一個邊界案例
- 必須 `uv run python` 實際執行（遵守 `must-execute-before-complete` rule）
- 檔頭格式（中文，與 `/ep-validate` 共用規範）：
  ```python
  """POC: [假設描述]

  驗證: [具體驗證標的]
  風險: [高]
  來源: [假設來源，如 path/to/file.py:ClassName]
  """
  ```

**技術選型**（如有需要）：在此階段用 POC 結果佐證方案選擇。

### Phase 4: UC + 邊界（結構化產出）

**UC 是開發的驅動層，不是事後追蹤。大型/中型變更必須在此階段定義或更新 UC。**

1. **掃描相關 CLAUDE.md Capabilities + .kanban/ 卡片**：搜尋需求涉及的 library 模組目錄的 CLAUDE.md Capabilities 表格 + `.kanban/` cards，確認是否已有相關 UC
2. **判斷變更規模**：

| 規模 | UC 行為 |
|------|--------|
| 大型 | 建立 **Kanban Backlog 卡片**（含能力描述、目標、驗收標準） |
| 中型 | 更新既有 Kanban 卡片的描述或狀態；或更新 CLAUDE.md Capabilities 表格的描述 |
| 小型 | 跳過（bug fix、文檔不需要 UC） |

3. **確認 UC 不重複**：已有 UC（Capabilities ✅ 或 Kanban 📋）能覆蓋需求 → 更新描述，不另建新卡片
4. **記錄能力描述**：後續 EP 和 /build 會引用此能力描述
5. **消費場景欄位**：大型變更新增 UC 時可先留空，由後續 `/execution-plan` 產出 Scenario Matrix 後、`/build` 階段 5a 從矩陣提煉自包含描述填入。中型變更若影響使用情境，可於此階段直接更新既有 UC 的消費場景

**Kanban Backlog 卡片格式**（📋 新建時使用）：
```markdown
[tag:module]

# [中文標題，與檔名相同]

## 目標
[簡述，或完整 spec（詳細 📋 時）]

## 相關
- EP: [ep-xxx.md，如有]

## 驗收標準
- [ ] [主要驗收條件]

## 備註
[依賴、前置條件]
```
- **檔名**：繁體中文標題，保留必要英文縮寫。範例：`訂閱分級語意重構.md`
- 📋 簡單（< 10 行描述）：`## 目標` 放一句話
- 📋 詳細（≥ 10 行）：`## 目標` 放完整描述（卡片是 markdown，長度不限）
- **Tag**：掃描 `mosaic_alpha/` 子目錄決定 tag 名（見專案 CLAUDE.md「Tag 慣例」）。`adapters/sj` → `sj`

**邊界定義**：
```
Always（一定做）：[列表]
Ask First（先討論再做）：[列表]
Never（不做）：[列表]
```

**成功條件量化**：將模糊需求轉為可驗證的目標（測試類型分佈、關鍵情境覆蓋，不寫數量）。

**對接校驗**：對照 Phase 2 研究摘要中的 callers 使用模式，確認邊界定義涵蓋所有下游消費者。

### Phase 5: 產出

**預設（無參數）**：在對話中產出規格摘要，不寫檔案。用戶可直接接 `/execution-plan`。

**`--write`**：寫入 `ai-analysis/specs/{feature-name}-spec.md`。適用於：
- 換 session 時傳遞 context
- 需要跨 session 協作

**`--research-only`**：只做 Phase 1-2，產出研究報告（對話中或寫入）。不進 UC 定義。適用於：
- 「先研究看看，還沒確定要做」
- 技術選型前的可行性調查

**規格摘要格式**（`--write` 時使用，向後相容 EP 輸入）：

```markdown
## 規格摘要
### 目標 / User Story / 核心功能 / 技術約束
### UC 引用
- 新增：[能力描述]（📋）
- 更新：[能力描述]（描述更新）
### 現有基礎設施
- `path/to/file.py:ClassName` — 用途簡述
### 已驗證假設（含 POC 結果）
| 假設 | 風險 | 驗證方式 | 結果 |
|------|------|---------|------|
### 技術決策 / 成功條件 / 邊界
```

此摘要直接作為 `/execution-plan` 的輸入。

---

## 與 /ep-validate 的分工

| | /spec Phase 3 | /ep-validate |
|--|---------------|-------------|
| 時機 | EP 之前 | EP 之後 |
| 深度 | 可行性驗證（能不能做） | 深度驗證（效能、邊界、壓力） |
| 範圍 | 2-3 個關鍵假設 | EP 所有段落的假設 |
| 產出 | `lab/poc_*.py`（可保留或刪除） | EP 回寫 + `lab/poc_*.py` |

---

## 流程位置

```
/spec（含 UC 定義 + POC 可行性驗證）→ /execution-plan（含 EP Review）→ [/ep-validate] → /build（含 Agent Review + UC 更新）→ /code-review → /commit
```
