---
harness-scope: neutral
---

# 漸進式驗證

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

---

## 核心原則

**大範圍驗證禁止一步到位。先小範圍確認正確，再擴大規模。全量執行耗時長，全跑完才發現問題成本太高。**

---

## 流程

1. **DEPTH-MIN**（最小集合）— 每次修改後跑，確認基本邏輯正確
2. **DEPTH-SAMPLE**（代表性樣本）— 邏輯穩定後跑，涵蓋邊界案例
3. **DEPTH-FULL**（全量）— DEPTH-MIN + DEPTH-SAMPLE 都通過才跑

### 各層適用場景

| 層級 | 觸發時機 | 耗時預期 | 失敗處理 |
|------|---------|---------|---------|
| DEPTH-MIN | 每次修改後 | 秒級~分鐘 | 修 code，重跑 DEPTH-MIN |
| DEPTH-SAMPLE | 策略/邏輯穩定後 | 分鐘級 | 分析失敗案例，修 code，重回 DEPTH-MIN |
| DEPTH-FULL | DEPTH-MIN + DEPTH-SAMPLE 都通過 | 分鐘~小時 | 記錄失敗案例，分析是否需改邏輯 |

### 最小集合的選擇原則

- 優先選能覆蓋多種邏輯分支的標的（如：除權息股、減資股、零股）
- 數量不需要多，3-5 個足以確認基本邏輯
- 必須包含至少一個「已知容易出錯」的案例

### 與風險分級的關係

> 定義見 [ai-development-guide.md](../ai-development-guide.md)「驗證約束 → 風險分級標準」

風險分級決定最終驗證深度（高風險以 DEPTH-FULL 為標準），但即使高風險也應先跑 DEPTH-MIN 確認基本邏輯正確，再逐步擴大。兩個維度互補：風險分級決定「要驗證多深」，漸進驗證決定「用什麼順序到達那個深度」。

---

## 禁止行為

- ❌ 未通過 DEPTH-MIN 就直接跑 DEPTH-FULL
- ❌ 修改後直接跑全量回測/全量驗證
- ❌ DEPTH-FULL 失敗後不分析原因就重跑（先回到 DEPTH-MIN 確認修復）

---

## 為什麼

全量驗證（全量回測、全量 DB 更新、全量特徵計算、全量匯出）通常耗時數十分鐘到數小時。如果基本邏輯有錯，全部跑完才發現是浪費。漸進驗證把問題發現時間從「全量跑完」壓縮到「幾秒到幾分鐘」。

此規則適用於任何涉及大量數據的驗證場景：回測、DB migration、特徵計算、資料匯出、E2E pipeline 等。
