
---
argument-hint: [target]
description: 智能清理 Git Worktrees
---

智能分析並安全清理 Git Worktrees，確保不遺失重要開發成果。

參數格式：`/worktree-cleanup [target]`

- `target`: 清理目標（可選）
  - 特定工作樹名稱（如 "story-1.4", "feature-dashboard"）
  - 不指定：顯示清理建議但不執行

範例：

- `/worktree-cleanup` （僅分析和建議）
- `/worktree-cleanup story-1.4` （清理特定工作樹）

執行以下清理流程：

1. **解析清理參數**：

   - 分析 `$ARGUMENTS` 中指定的清理目標
   - 根據參數選擇適當的清理策略
   - 設定安全檢查級別

2. **清理候選識別**：
   根據參數執行不同的檢測策略：

   - **特定工作樹**：直接清理指定目標

3. **風險評估**：

   - 標記需要使用者確認的工作樹
   - 檢查有未推送提交的完成分支

4. **執行清理**：

   - 提供清理建議和互動選項
   - 自動備份重要資訊到 `.claude/worktree-backups/`
   - 使用 `git worktree remove` 安全移除
   - 清理對應的本地分支

5. **清理報告**：
   - 顯示清理統計（移除數量、釋放空間）
   - 提供備份位置和恢復指令
   - 分析清理後的效能提升

為每個清理候選提供詳細的影響分析和恢復選項。