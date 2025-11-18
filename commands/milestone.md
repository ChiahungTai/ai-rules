# /milestone 指令 - 對話里程碑記錄工具

你是對話里程碑記錄專家，專門負責將長對話中的重要進展和知識沉澱為結構化的 YAML 檔案，便於清除 context 後快速重啟高品質工作。

## 🎯 核心目標

當對話變得冗長或需要切換焦點時，使用 `/milestone` 指令記錄重要進展：
- **記錄里程碑**: 捕捉已完成的重要成果和關鍵決策
- **沉澱知識**: 提煉可重用的模式和學習
- **快速重啟**: 提供足夠上下文讓新 AI 快速進入狀態
- **清除雜訊**: 過濾掉試錯過程和無關細節

---

## 📋 YAML 結構規範

### 基本結構

```yaml
# 對話里程碑記錄
version: "3.0"
session:
  id: "unique_session_id"
  created: "2025-01-18 HH:MM:SS"
  updated: "2025-01-18 HH:MM:SS"
  duration: "2h 30m"  # 對話持續時間

# 專案上下文
context:
  goal: "整體目標描述"
  why: "執行原因/商業邏輯"
  approach: "使用的方法/策略"
  success_criteria: "成功標準"
  constraints: "限制條件/注意事項"

# 時間線（重要事件，按時間順序）
timeline:
  - t: "10:30"
    desc: "事件摘要描述"
    files: ["path/to/file1.py", "path/to/file2.md"]
    result: "具體結果或成就"
    decision: "重要決策（如有）"

  - t: "11:15"
    desc: "關鍵突破或問題解決"
    files: ["modified/file.py"]
    result: "達成的具體成果"
    learning: "重要學習或發現"

# 當前狀態（只記錄現在）
current:
  working_on: "正在處理的具體任務"
  status: "進度狀態（進行中/暫停/等待）"
  progress: "當前进度百分比或描述"
  blocking_issues: "當前遇到的阻礙"
  next_actions: ["下一步行動1", "下一步行動2"]

# 重要成果里程碑
milestones:
  - "已完成的重要成果1"
  - "關鍵功能實現"
  - "架構決策確定"
  - "測試通過驗證"

# 關鍵知識與模式
learnings:
  patterns:
    - pattern: "可重用的技術模式"
      when: "適用情境"
      avoid: "要避免的做法"
      fix: "標準解法"

  discoveries:
    - "重要技術發現"
    - "最佳實踐確認"
    - "性能優化技巧"

  troubleshooting:
    - symptom: "問題徵狀"
      cause: "根本原因"
      solution: "解決方案"

# 快速重啟指引
restart:
  quick_context: "2-3句描述當前專案狀況"
  priority: "當前最優先的事項"
  immediate_next: "立即要執行的下一步"
  must_understand: "新 AI 必須理解的關鍵資訊"
  critical_files: ["需要優先檢視的重要檔案"]

# 專案特定資訊
project_specific:
  repo_state: "Git 狀態描述（如有重要變更）"
  environment: "開發環境狀態"
  dependencies: "重要依賴或安裝項目"
  testing: "測試狀態或下一步測試計劃"
```

---

## 🔧 使用方式

### 基本命令

```bash
# 生成當前對話的里程碑記錄
/milestone

# 指定輸出檔案路徑
/milestone --output ./milestones/session-001.yaml

# 包含更多細節（verbose 模式）
/milestone --verbose

# 只輸出關鍵資訊（compact 模式）
/milestone --compact

# 預覽模式（不實際寫入檔案）
/milestone --dry-run
```

### 參數說明

- **無參數**: 自動分析對話，生成 milestone.yaml 到當前目錄
- **--output**: 指定輸出檔案路徑
- **--verbose**: 包含更多細節和過程資訊
- **--compact**: 只保留最重要的資訊，適合快速重啟
- **--dry-run**: 顯示將生成的内容但不寫入檔案

---

## 📝 輸出範例

### 完整輸出範例

```bash
/milestone --verbose
```

```
🎯 分析對話內容，生成里程碑記錄...

📊 對話統計:
   對話時長: 2h 15m
   訊息總數: 47 則
   檔案修改: 8 個檔案
   關鍵決策: 3 個

🚀 識別重要成果:
   ✓ 實作核心數據處理模組
   ✓ 建立完整測試框架
   ✓ 解決性能瓶頸問題

📋 生成 milestone.yaml...
   ✓ 時間線: 12 個關鍵事件
   ✓ 里程碑: 5 個重要成果
   ✓ 知識沉澱: 8 個可重用模式
   ✓ 重啟指引: 包含所有必要上下文

💾 檔案已寫入: ./milestone-2025-01-18-session.yaml

🔄 準備清除 context? 使用 'clear' 指令後即可重新開始
```

### Compact 模式範例

```bash
/milestone --compact
```

```yaml
version: "3.0"
session:
  id: "compact-session"
  created: "2025-01-18 14:30:00"
  duration: "2h 15m"

restart:
  quick_context: "實作量化交易核心模組，已完成數據處理和回測框架"
  priority: "實作策略執行引擎"
  immediate_next: "在 src/strategy/ 目錄建立執行器類別"
  must_understand: "使用 Nautilus Trader 框架，注重性能和可重現性"
  critical_files: ["src/core/engine.py", "tests/test_strategy.py"]

milestones:
  - "完成數據網關統一接口"
  - "建立事件驅動架構"
  - "實現回測引擎"
```

---

## 🎯 判斷標準

### 什麼是重要里程碑？

#### ✅ 應該記錄
- **功能完成**: 核心功能實現並通過測試
- **架構決策**: 重要的技術選擇和設計決策
- **問題解決**: 復雜問題的根本解決方案
- **性能突破**: 顯著的性能提升或優化
- **測試通過**: 重要的測試里程碑或品質保證
- **文檔建立**: 重要架構或 API 文檔完成

#### ❌ 不應該記錄
- **試錯過程**: 暫時的嘗試和失敗
- **重複操作**: 相似的修改或調整
- **環境問題**: 臨時的環境配置問題
- **工具使用**: 如何使用某個工具的過程
- **無關細節**: 與核心目標無關的技術細節

### 知識模式識別

#### 技術模式
```yaml
patterns:
  - pattern: "使用 Factory Pattern 建立數據源適配器"
    when: "需要支援多種異構數據源時"
    avoid: "直接在客戶端代碼中硬編碼數據源邏輯"
    fix: "建立抽象工廠，統一管理不同數據源的創建"
```

#### 問題解決模式
```yaml
troubleshooting:
  - symptom: "記憶體使用持續增長導致 OOM"
    cause: "DataFrame 引用未正確釋放，造成記憶體洩漏"
    solution: "使用 weak reference 和顯式清理機制"
```

---

## 🔄 重啟流程

### 使用里程碑重啟工作

1. **清除舊 Context**
   ```bash
   /clear
   ```

2. **載入里程碑**
   ```bash
   請讀取 milestone.yaml 檔案，快速了解專案狀況
   ```

3. **確認理解**
   ```bash
   根據 milestone 記錄，我理解到：
   - 專案目標：[goal]
   - 當前狀態：[status]
   - 下一步：[immediate_next]

   我的理解正確嗎？
   ```

### AI 快速上手檢查清單

- [ ] 已讀取並理解 milestone 檔案
- [ ] 確認專案目標和當前狀態
- [ ] 了解優先事項和下一步行動
- [ ] 理解關鍵限制和注意事項
- [ ] 確認需要檢視的重要檔案

---

## 💡 最佳實踐

### 記錄時機
- **對話轉折點**: 重要階段完成時
- **工作切換前**: 從一個模組轉到另一個模組前
- **休息前**: 結束一天工作前
- **問題解決後**: 重要問題完全解決後
- **Context 過多時**: 對話變得冗長難以追蹤時

### 品質要求
- **準確性**: 確保記錄的事實和決策準確無誤
- **完整性**: 包含足夠的上下文供後續使用
- **簡潔性**: 避免冗餘資訊，專注於重要內容
- **可操作性**: 提供明確的下一步指引
- **可重用性**: 提煉的模式應適用於未來類似情況

### 檔案管理
- **命名規範**: 使用 `milestone-YYYY-MM-DD-session.yaml` 格式
- **版本控制**: 里程碑檔案應加入 Git 追蹤
- **定期清理**: 過時的里程碑檔案可歸檔或刪除
- **備份機制**: 重要里程碑建議有額外備份

---

## 🎨 設計哲學

> 💡 **核心價值**: 讓每個里程碑都成為高品質的知識沉澱，確保 AI 協作的連續性和效率。

> 🚀 **目標**: 不只是記錄對話，而是提煉可重用的智慧和經驗，讓每次重啟都比上次更強大。

> ⚡ **原則**: 最好的記錄是讓新 AI 能在 5 分鐘內理解專案狀況並立即開始高效工作。