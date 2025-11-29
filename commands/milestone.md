---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
usage: "/milestone [任務描述] [選項]"
argument-hint: "[任務描述] [--dry-run] [--restart-only] [--verbose] [--compact]"
allowed-tools: ["Task"]
model: "sonnet"
disable-model-invocation: false
---

Task
  description="執行對話里程碑記錄"
  prompt="參數：$ARGUMENTS。請執行里程碑記錄流程：解析參數、分析環境、生成YAML內容、執行對應操作。輸出格式要求：

1. **執行摘要**：單行顯示模式、意圖、檔案名稱
2. **檔案路徑**：正式模式顯示建立的檔案路徑
3. **重啟指引**：以純文本形式直接輸出到 console，不含代碼塊格式，可直接選擇複製
4. **狀態**：明確的完成狀態

重啟指引應該是一個完整的文本，包含：
- 工作目標和背景
- 當前狀態和進度
- 關鍵檔案路徑
- 下一步具體行動

確保 next_actions 根據實際情況動態生成，不要使用硬編碼內容。"
  subagent_type="milestone-recorder"