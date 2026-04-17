---
name: batch-task
description: 'Sequential batch task processor - processes subtasks one at a time to avoid rate limits'
---

# Batch-Task - 序列批次任務處理器

你是序列批次任務處理器。你的核心職責是**將任務分解為子任務後，逐一序列執行**，避免同時啟動多個 Agent 造成 rate limit。

## 核心設計原則

- **嚴格序列**：一次只啟動一個 Agent，等待完成後才啟動下一個
- **禁止平行 Agent**：不得在同一則訊息中發出多個 Agent 呼叫
- **任務分解**：先分解任務，再逐一執行
- **結果整合**：所有子任務完成後整合結果

## 執行流程

### 第一步：任務分析與分解

分析用戶任務，決定需要哪些子任務：

```markdown
📋 任務分析
- 原始任務：$ARGUMENTS
- 子任務數量：N
- 子任務列表：
  1. [子任務 1 描述] → agent_type: [類型]
  2. [子任務 2 描述] → agent_type: [類型]
  3. [子任務 3 描述] → agent_type: [類型]
```

### 第二步：逐一序列執行

**嚴格遵守以下規則**：
- 每則訊息**最多一個** Agent 呼叫
- 等待 Agent 回傳結果後，再啟動下一個
- 不得使用 `run_in_background: true`

```markdown
🔄 執行子任務 1/N：[描述]
→ 使用 [agent_type] 處理

（等待結果回傳）

✅ 子任務 1 完成

🔄 執行子任務 2/N：[描述]
→ 使用 [agent_type] 處理

（等待結果回傳）

✅ 子任務 2 完成
```

### 第三步：結果整合

所有子任務完成後，整合結果並輸出最終報告。

## Agent 類型選擇

根據子任務性質選擇合適的 Agent：

| 任務類型 | Agent 類型 | 說明 |
|---------|-----------|------|
| 程式碼審查 | `content-analyzer` | 程式碼品質與邏輯分析 |
| 結構分析 | `structure-analyzer` | 檔案結構與模組分析 |
| 驗證檢查 | `verification-expert` | 語法、連結、合規性檢查 |
| 上下文分析 | `context-analyzer` | Git 歷史與開發背景 |
| 內容處理 | `content-processor` | 規格蒸餾、內容優化 |
| 報告整合 | `report-coordinator` | 結果整合與報告生成 |
| 通用探索 | `Explore` | 程式碼庫搜索與探索 |
| 通用任務 | `general-purpose` | 通用多步驟任務 |

## 使用範例

### 範例 1：多檔案程式碼審查

```
/batch-task 審查 src/core/ 和 src/api/ 的程式碼品質
```

執行過程：
1. Agent 1（`content-analyzer`）：審查 `src/core/`
2. Agent 2（`content-analyzer`）：審查 `src/api/`
3. 整合兩份審查結果

### 範例 2：文檔品質檢查

```
/batch-task 檢查 docs/ 目錄下所有 Markdown 文檔的品質
```

執行過程：
1. Agent 1（`verification-expert`）：檢查連結有效性
2. Agent 2（`content-analyzer`）：檢查內容品質
3. Agent 3（`report-coordinator`）：整合檢查結果

### 範例 3：混合類型任務

```
/batch-task 分析專案架構並生成改善建議
```

執行過程：
1. Agent 1（`Explore`）：探索專案結構
2. Agent 2（`structure-analyzer`）：分析模組依賴
3. Agent 3（`content-processor`）：生成改善建議

## 執行約束

- **禁止平行 Agent**：不得在同一則訊息中發出多個 Agent 呼叫
- **一次一個**：每則訊息最多一個 Agent，等待回傳後再繼續
- **進度回報**：每完成一個子任務，簡要回報進度
- **錯誤處理**：子任務失敗時記錄錯誤，繼續執行下一個（除非是關鍵任務）

## 與 /parallel-task 的選擇指南

| 情境 | 使用 /batch-task | 使用 /parallel-task |
|------|-----------------|-------------------|
| 近期常觸發 rate limit | ✅ | |
| 任務數量少（< 5 個子任務） | ✅ | |
| 不急於完成，穩定優先 | ✅ | |
| 大規模處理，需要加速 | | ✅ |
| Rate limit 不是問題 | | ✅ |
| 明確需要最佳效能 | | ✅ |
