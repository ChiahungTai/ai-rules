---
name: compact-prep
description: /compact 前的外部化前置：把最後幾輪對話原文（raw tail）落檔＋驗證 memory 新鮮度，然後請 user 執行 /compact。不解決壓縮本身（harness 擁有），只解決 compact 後的接續材料。
---

# compact-prep：/compact 的前置外部化

> 背景：/compact 的摘要會壓掉 verbatim 交付物（實測 A/B：指示要求 verbatim 無效）、re-injection 快照可能過時。結構性解法＝compact 前把 tail 原文落檔。

## 步驟

1. **定位當前 session（自我錨定，禁用「取 db 最新 session」法——同 worktree 並行 session 會撈到別的 session）**：以本 skill 的調用字串為錨——`SELECT DISTINCT session_id FROM part WHERE data LIKE '%compact-prep%' ORDER BY time_created DESC LIMIT 1;`（調用訊息本身就在當前 session 的 part 裡）。撈出後抽查該 session 最後一則 user part 是否為本次調用，確認非鄰近 session 誤中。
2. **落檔 raw tail**：取該 session 最後 6 則 user/assistant text part 原文（唯讀連線），寫入 `<repo>/.agent-tmp/compact-tail-<date>.md`，檔頭標註 session id 與時間。
3. **memory 新鮮度檢查**：本 session 的裁決/教訓是否已寫進 memory（cluster-first）？缺 → 補寫。
4. **交付確認**：印出 tail 檔路徑＋摘要（幾輪、多少字元），然後請 user 執行 `/compact`。
5. **compact 後恢復**（無 hook 環境）：先讀 tail 檔恢復近期上下文，再繼續任務；**已註冊 hook 的環境 tail 已自動注入 context，跳過讀檔直接續任務**。
6. **清理**：tail 檔恢復用途完成後即無價值——依 `.agent-tmp/` 既有清理紀律處理（互動模式完成時列清單保留/刪除）。

## 邊界

- 不做壓縮、不產摘要（harness 職責）；只做 compact 前外部化＋compact 後恢復指針。
- 已註冊 SessionStart(compact) hook（`hooks/compact-tail-inject.py`，tail 自動注入）的環境：步驟 2 的 tail 由 hook 承接，本 skill 職責縮減為**步驟 3 memory 新鮮度檢查**（唯一 hook 做不到的——hook 只恢復材料，不外部化新教訓）。
- Claude Code 環境同樣適用（db 路徑改為該環境的 session 儲存；無 db 時步驟 1-2 改為直接把最後幾輪對話內容手動落檔——模型自己 context 內仍有原文）。
