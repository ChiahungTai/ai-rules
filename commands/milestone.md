---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
argument-hint: "[任務描述] [--dry-run] [--restart-only] [--verbose] [--compact]"
allowed-tools: ["Task"]
---

# 對話里程碑記錄工具

這個 slash command 會啟動專門的 milestone-recorder agent 來處理對話里程碑記錄，將重要的工作進展和知識沉澱為結構化 YAML 檔案，便於清除 context 後快速重啟高品質工作。

## 用法

```bash
/milestone [任務描述] [選項]
```

## 參數說明

- **任務描述**: 當前正在進行的工作目標或意圖
- `--dry-run`: 預覽模式（不實際寫入檔案）
- `--restart-only`: 只生成重啟 prompt
- `--verbose`: 詳細模式
- `--compact`: 精簡模式

## 立即執行

正在啟動 milestone-recorder agent 來處理您的請求...

參數：**$ARGUMENTS**

## 調用 milestone-recorder Agent

將執行完整的里程碑記錄流程，包括：

### 🔧 核心處理步驟
1. **參數解析**: 識別執行模式和用戶意圖
2. **環境分析**: 自動收集當前工作目錄、Git 狀態、專案類型
3. **檔案生成**: 創建時間戳、檔名規則、YAML 內容
4. **模式執行**: 根據參數執行 dry-run、restart-only 或正式模式
5. **重啟指引**: 生成標準化的重啟 prompt

### 🎯 預期輸出
- 📋 執行摘要（模式、意圖、檔案名稱）
- 📁 建立的里程碑檔案路徑（正式模式）
- 🔄 **重啟指引**（可直接複製使用）
- ✅ 下一步建議

### 💡 智能特性
- 🎯 **智能意圖識別**: 自動分類用戶工作意圖
- 📁 **結構化儲存**: 統一的 YAML 格式和檔案命名
- 🔄 **無縫重啟**: 標準化的上下文恢復流程
- ⚡ **多模式支援**: 預覽、重啟、詳細、精簡模式
- 🛠️ **環境感知**: 自動識別專案類型和狀態

---

**立即執行 milestone 記錄處理...**

# 調用 milestone-recorder sub agent
Task
  description="執行對話里程碑記錄"
  prompt="請分析對話上下文並生成里程碑記錄。參數：$ARGUMENTS。你必須執行完整的里程碑記錄流程，包括：1. 解析參數（意圖、模式）2. 分析當前環境（工作目錄、Git狀態、專案類型）3. 生成時間戳和檔名 4. 建立完整的 YAML 內容 5. 根據模式執行對應操作 6. 輸出完整的重啟指引。重啟指引應包含：📍 里程碑檔案路徑、專案目標和狀態、當前工作進度、立即下一步：讀取里程碑檔案並根據 current.next_actions 執行。請確保輸出結果與原始 milestone.md 的完整功能完全相同。"
  subagent_type="milestone-recorder"