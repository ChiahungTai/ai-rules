# Morning Report 格式模板

> 供 `/claude:daily-maintain` Phase 3 使用。寫入 `ai-analysis/daily-report/{YYYY-MM-DD}.md`。

---

```markdown
# Morning Report — {YYYY-MM-DD}

**執行模式**: Default / Full Audit
**執行時間**: {start} → {end}（耗時 {duration}）
**處理模組**: N 個（{模組列表}）

---

## 決策摘要

| 模組 | 處理方式 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|---------|
| rule_forge | 重建 source-docs | 7 files rebuilt | Full Compare: 87% | 5 edits |
| indicators | 定向修正 | skip | Quick Scan: ✅ | — |
| common | 跳過（無變更） | skip | Quick Scan: ✅ | — |

## CLAUDE.md 變更摘要

### ✅ 自動修改（{N} 項）

| 模組 | CLAUDE.md 位置 | 修改類型 | 來源 | 修改摘要 |
|------|---------------|---------|------|---------|
| rule_forge | :45 | 過時描述更新 | compare:engine.py:122 | Pipeline v2 描述更新 |
| rule_forge | :78 | 補充型別關係 | compare:types.py:56 | ConditionFilter vs ObservationFilter 區別 |

### ⚠️ 建議修改（{N} 項）— 需要您確認

| # | 模組 | CLAUDE.md 位置 | 建議 | 理由 | 來源 |
|---|------|---------------|------|------|------|
| 1 | rule_forge | (新增) | 新增「FilterTree 的 sequential greedy 設計理由」 | decode-compare 發現此為非顯而易見的設計決策 | compare:sequential_greedy.py:45 |

## Phase 2: Decode-Compare 精度報告

{每個模組的精度總覽表}

## CLAUDE.md Gap Report（--full 專用）

### CLAUDE.md 覆蓋度評分

| 模組 | A 架構 | B 演算法 | C 資料結構 | D 基礎設施 | 整體 |
|------|--------|---------|-----------|-----------|------|
| rule_forge | 92% | 85% | 90% | 70% | 84% |

### 知識缺口（{N} 項）

| 模組 | 缺口類型 | 遺漏內容 | 來源 | 建議動作 |
|------|---------|---------|------|---------|
| rule_forge | 設計理由 | FilterTree 為何用 greedy | engine.py:45 | 新增段落 |

### 基礎設施缺口（{N} 項）

| 遺漏項 | 被使用次數 | 使用模組 | 建議動作 |
|--------|----------|---------|---------|
| ConditionParser | 3 | conditions, adapters, datasets | 加入「可複用基礎設施」 |

### 跨模組重複造輪子風險

{哪些被複用的 class 沒記錄在基礎設施中，EP/build agent 可能重造輪子的項目}

## Decoder Test 結果

| 模組 | 職責 | 設計決策 | 約束 | 邊界 | 通過 |
|------|------|---------|------|------|------|
| rule_forge | ✅ | ✅ | ✅ | ✅ | ✅ |
| indicators | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |

## ⚠️ 未解決問題

| # | 問題 | 嚴重性 | 修復方式 | 建議動作 |
|---|------|--------|---------|---------|
| 1 | indicators source-docs 引用不存在的 ATDDef | 低 | source-docs 定向修正 | 移除引用（Edit） |
| 2 | adapters source-docs 引用已刪除的 .py | 低 | source-docs 定向修正 | 移除引用（Edit） |
| 3 | datasets CLAUDE.md 缺少 ExportConfig 導航 | 低 | CLAUDE.md 定向修正 | 補充導航（Edit） |
| 4 | 4 個過時模組 source-docs 需要重建 | 中 | 自動重建 | 下次 .py 變更時自動處理 |

**修復方式分類**：
- **CLAUDE.md 定向修正**：導航缺口、過時描述 → 直接 Edit，不需要任何模式
- **source-docs 定向修正**：引用斷裂、已刪除檔案 → 直接 Edit source-docs，不需要重建
- **自動重建**：過時模組需要完整重建 source-docs（doc-decode）
- **--full**：CLAUDE.md 完整性審計（含基礎設施覆蓋檢查）

## 下次建議

- {根據本次發現的改善建議}
- ⚠️ 不要對所有問題一律建議 --full：
  - 大部分 source-docs 問題 → 定向 Edit 即可
  - 只有 source-docs 大面積過時（.py 大量變更後）才需要 --full

## 耗時記錄

| Phase | 耗時 | 備註 |
|-------|------|------|
| Phase 0 SCAN | Xs | |
| Phase 0.5 Quick Scan | Xs | |
| Phase 0.6 CLAUDE.md Sync | Xs | |
| Phase 1 Fix & Rebuild | Xs | 每模組明細 |
| Phase 2 Verify | Xs | 每模組明細 |
| Phase 2.5 Gap Report | Xs | --full 專用 |
| Phase 3 Update + Report | Xs | |
| **總計** | **Xs** | |
```
