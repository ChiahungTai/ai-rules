---
description: "評估其他 AI 的審查建議，基於深層思考框架決定是否採納。/judge-review <ai1: 建議 [ai2: 建議]"
when_to_use: "Evaluate AI review suggestions using deep thinking (first principles + second-level consequence tracing) against actual code. Decide adopt/reject/needs-confirmation before making changes."
usage: "/judge-review ai1: 建議全文 [ai2: 建議全文]"
argument-hint: "貼上其他 AI 的審查建議，格式：ai1: ... 或 ai1: ... ai2: ..."
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit"]
---

# /judge-review — AI 審查建議評估

實作工程師，評估其他 AI 的代碼審查建議，基於深層思考框架（第一性原理 + 第二層後果追蹤）和實際程式碼查證決定是否採納。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

## 核心目標

**「查證 → 第一性原理分析 → 第二層後果追蹤 → 決策 → 寫持久化」**

---

## 核心原則 — 不盲從

所有決策基於實際程式碼查證，不基於 LLM 訓練資料的經驗推測。

**✅ 採納**：問題真實存在 + 解決方案合理 + 收益 > 成本
**❌ 不採納**：基於錯誤假設 / 問題不存在 / 成本 > 收益 / 與專案規範衝突
**⚠️ 需確認**：無法單方面判斷 / 需用戶決策

---

## 執行流程

1. **解析建議**：識別 AI 來源、提取要點、識別相關程式碼
2. **查證實際程式碼**：讀取相關檔案，確認問題是否真實
3. **第一性原理分析**：本質問題是什麼？問題真的存在嗎？解決方案合理嗎？權衡是什麼？
4. **輸出評估報告**（格式如下）
5. **寫入持久化**：決策更新到 finding 的 `decision`(✅/❌/⚠️)與 `status` 欄 —— ✅→`adopted`、❌→`rejected`、⚠️→`needs-confirmation`(更新 `.review/<branch>.md` 或 EP review 區段,格式見 [workflow-review-pattern.md](./claude/_common/workflow-review-pattern.md))。**judge-review 不實作** —— 實作由呼叫端決定(`/build` Phase 4 直接 apply ✅;獨立使用由用戶判讀決策清單)

---

## 輸出格式

```markdown
## 🔍 AI 審查建議評估報告

### 📋 建議總覽
| 來源 | 建議摘要 | 決策 | 理由 |

### ✅ 採納建議
[原文 + 相關程式碼 + 第一性原理分析 + 修改計畫]

### ❌ 不採納建議
[原文 + 相關程式碼 + 不採納理由]

### ⚠️ 需確認建議
[原文 + 無法判斷原因 + 請確認問題]

### 評估摘要
採納 N / 不採納 N / 需確認 N
```

---

## 執行約束

- **必須查證實際程式碼**
- **必須第一性原理分析**
- **不實作** —— 只評估產出決策清單(✅/❌/⚠️)+ 寫持久化。實作由呼叫端控制

禁止：盲從建議 / 不查證就接受 / 基於假設評估 / 自動開始實作

---

## 特殊情況

- **建議互相矛盾**：基於程式碼判斷採納哪一方，附理由
- **找不到相關程式碼**：❌ 不採納（無法驗證）
- **與專案規範衝突**：❌ 不採納（專案規範優先）

---

## 流程位置

前置：`/code-review`（其他 AI 執行審查）
後續：確認後實作 → `/followup-review`（Review LLM 驗收）→ `/commit`
