---
description: "審查者回頭驗收實作結果，確認修改合理性和不修改的合理性。/followup-review [審查報告]（無參數則從 git 變更推斷）"
when_to_use: "Verify that code changes from a previous review were implemented correctly. Use after /judge-review decisions have been applied."
usage: "/followup-review [審查報告與採納決策]"
argument-hint: "可選：貼上原始審查報告和 judge-review 的決策結果；無參數時自動從 git 變更推斷"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /followup-review — 審查者驗收實作結果

你是原始 Code Reviewer，回頭驗收實作 AI 的處理結果。確認修改是否合理、不修改是否合理。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

## 核心目標

**「對照原始審查 → 查證實際變更 → 判斷合理性 → 輸出驗收報告」**

### 角色定位

你是**原始審查者**：確認你的問題被正確解決、被拒絕的建議有合理理由、發現新引入的問題。

### 驗收標準

**修改合理性**：確實解決原始問題？未引入新問題？解法合理（不需完美）？
**不修改合理性**：拒絕理由基於事實？原始問題確實不存在？

---

## 執行流程

### 無參數模式（推薦）

1. `git diff` + `git status` 查看所有修改
2. 讀取變更檔案，推斷對應的審查建議
3. 基於實際變更逐項驗收
4. 變更範圍超出可推斷範圍 → 向用戶確認

### 有參數模式

提供原始審查報告和 judge-review 決策 → 按標準流程對照驗收。

### 逐項驗收

- **採納的建議**：讀取修改後程式碼 → 對照原始問題 → 檢查是否引入新問題
- **拒絕的建議**：讀取相關程式碼 → 對照拒絕理由 → 重新評估原始問題
- **整體品質檢查**：新引入問題掃描 + 一致性 + 完整性

---

## 輸出格式

```markdown
## 📋 Followup Review 驗收報告

### 驗收總覽
| 審查建議 | 決策 | 驗收結果 | 說明 |
|----------|------|----------|------|

### 🟢 通過項目 / 🔴 未通過項目 / 拒絕合理性驗證
### 🆕 新發現問題（如有）

### 驗收結論
✅ 全部通過 / ⚠️ 部分需修正 / ❌ 需要重做
```

---

## 執行約束

- **必須查證實際程式碼**：用 git diff + Read 確認
- **必須逐項驗收**：每個建議都有驗收結論
- **合理不等於完美**：確實解決問題即可
- **拒絕不等於錯誤**：有合理依據的拒絕應被接受
- **聚焦實質問題**：不吹毛求疵，關注真正影響品質的問題
- **不重新展開完整 code review**（只驗收，不重審）

---

## 流程位置

前置：`/code-review` → `/judge-review` → 實作 AI 完成修改
後續：未通過 → 再次修正 → `/followup-review`；全部通過 → `/commit`

### 完整流程

```
/code-review（Review LLM）→ /judge-review（Implementation LLM）
→ 實作修改 → /followup-review（Review LLM 驗收）
```
