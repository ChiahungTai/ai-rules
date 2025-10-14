---
description: 合併工作樹分支並清理
---

在主目錄中執行工作樹完成流程：選擇並合併工作樹分支到 main，然後清理工作樹。

**使用場景**：當您完成工作樹開發，希望將變更合併回主分支並清理工作樹時使用。

執行以下流程：

1. **環境檢查**：

   - 確認當前位於主目錄中
   - 檢查主目錄工作狀態是否清潔
   - 驗證當前在 main 分支

2. **工作樹分支發現**：

   - 自動掃描所有現有的工作樹
   - 檢查每個工作樹分支的狀態和提交情況
   - 顯示可合併的工作樹分支清單（已有提交且工作目錄清潔）

3. **互動式分支選擇**：

   - 顯示工作樹分支清單，包含：
     - 分支名稱
     - 最新提交訊息
     - 提交時間
     - 工作樹路徑
   - 讓使用者選擇要合併的分支
   - 確認合併操作

4. **執行合併流程**：

   - 更新 main 分支：`git pull origin main`
   - 合併選定的工作樹分支到 main
   - 推送合併後的 main 分支到遠端
   - 執行品質檢查確保合併成功

5. **自動清理**：
   - 刪除已合併的工作樹目錄
   - 移除本地工作樹分支
   - 顯示清理結果

**使用範例**：

```bash
# 在主目錄執行
cd /Users/jackle/workspace/Fortuna
/WorkTree:done
```

**輸出範例**：

```
🔍 發現以下可合併的工作樹分支：

1. feature/strapi-typescript-optimization
   📂 /Users/jackle/workspace/fortuna-feature-strapi-typescript-optimization
   📝 feat(typescript): 完成 Strapi v5 TypeScript 優化與 shared 套件建置修正
   🕐 2025-07-19 23:41:23

2. feature/workflow-engine-v2
   📂 /Users/jackle/workspace/fortuna-feature-workflow-engine-v2
   📝 feat(workflow): 實作工作流程執行引擎核心功能
   🕐 2025-07-19 15:30:45

請選擇要合併的分支 (輸入數字):
```

**安全檢查**：

- 僅顯示已提交且工作目錄清潔的工作樹
- 合併前確認 main 分支是最新狀態
- 提供合併預覽和確認步驟

**注意事項**：

- 必須在主目錄中執行（非工作樹目錄）
- 確保選定的工作樹已完成所有開發工作
- 合併後工作樹將被自動清理，請確保重要變更已提交
