
---
argument-hint: [name]
description: 建立新的 Git Worktree
related-commands: [done, cleanup, status]
---

根據提供的參數建立新的 Git Worktree 並自動設置完整的開發環境。

參數格式：`/worktree-create [name]`

- `name`: 功能描述或識別名稱（必填，AI 會根據內容自動判斷類型）

範例：

- `/worktree-create user-dashboard` → feature/user-dashboard
- `/worktree-create 使用者儀表板重設計` → feature/user-dashboard-redesign
- `/worktree-create 權限驗證修復` → hotfix/permission-validation-fix（AI 識別為修復）
- `/worktree-create 快取效能實驗` → experiment/cache-performance-experiment（AI 識別為實驗）
- `/worktree-create story-1.5-工作流程整合` → story/1.5-workflow-integration（AI 識別為 story）

執行以下流程：

1. **解析和優化參數**：

   - 分析 `$ARGUMENTS` 中的 name 參數
   - AI 根據內容自動判斷 type：
     - 包含「修復」、「fix」、「bug」→ hotfix
     - 包含「實驗」、「experiment」、「測試」→ experiment
     - 包含「story」或數字編號 → story
     - 其他情況 → feature（預設）
   - **中文名稱轉換**：將中文任務名稱轉換為符合命名規則的英文
     - 翻譯成語意清晰的英文詞彙
     - 轉換為 kebab-case 格式（小寫，用連字號分隔）
     - 避免縮寫，確保名稱具描述性
     - 遵循 Fortuna 專案的 4-6 個單字命名原則

2. **建立 Git Worktree**：

   - 使用 `git worktree add` 建立新 Git Worktree
   - 確保目錄和分支命名符合專案規範

3. **完成報告**：
   提供建立結果摘要，包含：
   - 原始中文輸入 → 轉換後的英文名稱
   - Git Worktree 路徑和分支名稱
   - 下一步指令

執行所有必要的安全檢查，確保不與現有 Git Worktree 衝突。