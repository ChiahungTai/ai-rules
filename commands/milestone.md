---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
usage: "/milestone [任務描述] [選項]"
argument-hint: "[任務描述] [--restart-only]"
allowed-tools: ["Task"]
model: "sonnet"
disable-model-invocation: false
---

# 🔍 執行 milestone 記錄

Task
  description="執行對話里程碑記錄"
  prompt="參數：$ARGUMENTS。請執行里程碑記錄流程：解析參數、分析環境、生成YAML內容、執行對應操作。

## 🎯 里程碑記錄的目的
/milestone 指令專門用於：
- 當對話變長、context 將滿時記錄重要進展
- 解決 context 快滿和浪費問題
- 提供快速重啟指引，節省重複解釋時間

## 🔧 執行模式
- **預設模式**：記錄里程碑到 YAML 檔案，提供重啟指引
- **--restart-only**：只生成重啟指引，不建立里程碑檔案

## 📋 輸出格式要求
1. **執行摘要**：單行顯示模式、意圖、檔案名稱
2. **檔案路徑**：預設模式顯示建立的檔案路徑
3. **重啟指引**：以純文本形式直接輸出到 console，不含代碼塊格式，可直接選擇複製
4. **後續操作說明**：明確告知用戶接下來的選項

## 🔄 重啟指引內容
- 工作目標和背景
- 當前狀態和進度
- 關鍵檔案路徑（包含 CLAUDE.md）
- 下一步具體行動
- **重要提醒**：必須先讀取專案的 CLAUDE.md 和 ~/.claude/CLAUDE.md 來理解 AI 協作開發規範

## ⚠️ 嚴格約束
- **記錄完成後立即停止** - 不要開始執行 next_actions 中的任務
- **純文本輸出** - 重啟指引必須直接輸出到 console，不含任何格式化
- **直接可複製** - 用戶可以直接選擇文字複製使用"
  subagent_type="milestone-recorder"

# ⏹️ Task 執行完成後的處理

**🔴 重要：milestone 記錄完成後，AI 必須立即停止工作**

**絕對不要：**
- ❌ 開始執行 next_actions 中的任何任務
- ❌ 繼續進行對話或討論
- ❌ 提供額外的建議或分析

**必須：**
- ✅ **停止工作** - 等待用戶決定下一步
- ✅ **讓用戶選擇** - clear context 或繼續當前對話
- ✅ **節省 context** - 這是指令的核心價值

**📋 用戶選項說明：**
用戶現在可以：
1. 執行 `/clear` 清除 context，然後複製 milestone 提供的重啟指引
2. 繼續當前對話（如果還有 context 空間）

**AI 應該等待用戶的下一步指示，不要主動繼續工作。**