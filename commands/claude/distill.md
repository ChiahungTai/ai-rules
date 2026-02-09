---
description: "蒸餾 CLAUDE.md，提煉核心精華"
usage: "/claude:distill [目錄路徑] [選項]"
argument-hint: "預設處理當前目錄，可指定目錄或檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
permission-mode: "acceptEdits"
---

# CLAUDE.md Distill - 蒸餾精簡工具

你是 CLAUDE.md 文檔蒸餾專家，專門負責將肥大的 CLAUDE.md 進行「蒸餾」，提煉出核心精華，去除冗餘細節。

## 🎯 核心目標

當 CLAUDE.md 變得肥大時，使用 `/claude:distill` 指令進行蒸餾：
- **提煉精華**: 保留核心的、不變的開發原則和約束
- **去除冗餘**: 移除具體的實作細節、配置參數、過時範例
- **支援遞歸**: 可一次處理整個目錄樹的所有 CLAUDE.md

**蒸餾比喻**: 如同蒸餾過程提煉出酒精純度，我們提煉出 CLAUDE.md 的核心原則純度。

---

## 📋 核心概念

### 精華 vs 冗餘分類

#### ✅ 應該保留的「精華」
- **核心原則**: 零容錯、高速迭代、極致工程品質
- **絕對約束**: Assert 優先、事實驅動、程式碼驗證
- **設計哲學**: 價值導向思維、問題優先原則
- **開發鐵律**: 量化交易專屬規範、風控機制
- **協作規範**: AI 自我審查機制、文檔使用規範
- **🤖 AI 導航資訊**: 目錄結構和核心 API 的簡要描述（對 AI 極具價值）

#### ❌ 應該蒸餾掉的「冗餘」
- **具體參數**: 測試參數、配置值、路徑規範
- **實作細節**: 函數命名具體規則、lint 錯誤代碼
- **工具配置**: make 命令、IDE 設定、環境變數
- **範例代碼**: 具體的程式碼範例、模板實作
- **詳細檢查清單**: 過於詳細的 step-by-step 檢查項目
  - *保留*: 核心驗證原則和重要檢查要點

### 遞歸處理模式

```
專案根目錄/
├── CLAUDE.md              ← 根層文檔
├── src/
│   ├── CLAUDE.md          ← 子模組文檔
│   ├── core/
│   │   └── CLAUDE.md      ← 深層模組文檔
│   └── utils/
│       └── CLAUDE.md      ← 深層模組文檔
└── tests/
    └── CLAUDE.md          ← 測試模組文檔

# /claude:distill --recursive 會處理全部 5 個 CLAUDE.md
```

---

## 🚀 遞歸發現與處理流程

### 步驟 1: 發現所有 CLAUDE.md

```bash
# 使用 Glob 工具遞歸搜尋
Glob "**/CLAUDE.md" $TARGET_DIR

# 或使用 find 命令
find $TARGET_DIR -name "CLAUDE.md" -type f
```

### 步驟 2: 分類與優先級

```python
def categorize_claude_files(files: list) -> dict:
    """將發現的 CLAUDE.md 按重要性分類"""

    categories = {
        "critical": [],    # 專案根目錄
        "high": [],        # 主要模組 (src/, core/, lib/)
        "medium": [],      # 子模組
        "low": []          # 測試、範例、文檔
    }

    for file_path in files:
        if "/" not in file_path.replace(target_dir, ""):
            categories["critical"].append(file_path)
        elif any(x in file_path for x in ["/src/", "/core/", "/lib/", "/mosaic_alpha/"]):
            if file_path.count("/") > 3:  # 深層目錄
                categories["medium"].append(file_path)
            else:
                categories["high"].append(file_path)
        elif any(x in file_path for x in ["/tests/", "/examples/", "/docs/"]):
            categories["low"].append(file_path)
        else:
            categories["medium"].append(file_path)

    return categories
```

### 步驟 3: 處理順序

```
1. Critical（根目錄）
   ↓
2. High（主要模組）
   ↓
3. Medium（子模組）
   ↓
4. Low（測試、範例）
```

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 蒸餾當前目錄的 CLAUDE.md
/claude:distill

# 2. 蒸餾指定檔案
/claude:distill src/core/CLAUDE.md

# 3. 蒸餾指定目錄（僅該目錄層級）
/claude:distill src/core

# 4. 遞歸蒸餾所有子目錄的 CLAUDE.md
/claude:distill --recursive
/claude:distill -r

# 5. 遞歸蒸餾指定目錄
/claude:distill /path/to/project --recursive

# 6. 預覽模式（不實際修改）
/claude:distill --dry-run
/claude:distill --recursive --dry-run

# 7. 指定蒸餾程度
/claude:distill --aggressive    # 高純度蒸餾
/claude:distill --moderate      # 標準蒸餾（預設）
/claude:distill --conservative  # 輕度蒸餾
```

### 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 蒸餾當前目錄的 `CLAUDE.md` |
| **檔案路徑** | 蒸餾指定的 `CLAUDE.md` 檔案 |
| **目錄路徑** | 蒸餾指定目錄下的 `CLAUDE.md`（僅該層） |
| **--recursive, -r** | 遞歸處理所有子目錄的 `CLAUDE.md` |
| **--dry-run** | 預覽模式，顯示蒸餾結果但不執行 |
| **--aggressive** | 高純度蒸餾，只保留絕對核心原則 |
| **--moderate** | 標準蒸餾（預設），平衡精華與實用細節 |
| **--conservative** | 輕度蒸餾，只去除明顯的冗餘內容 |

### 輸出範例（單檔案）

```
🔥 開始蒸餾 src/core/CLAUDE.md...
   📊 原料狀態: N 行，M 個主要章節（範例）
   ⚠️  檢測到濃度不足，建議執行蒸餾提純

⚗️  分離精華與雜質...
   ✓ 識別精華內容: N 個核心原則
   ✓ 識別雜質內容: M 個實作細節區塊
   ✓ 疑難成分判斷: K 個需要人工決策

🧪 蒸餾結果預覽 (moderate 純度):
   🎯 精華版本: 約 X 行 (-Y% 體積)
   🗑️  去除雜質: 測試參數、工具配置、檢查清單
   💧 保留精華: M 個重要引用連結

🧪 執行蒸餾過程...
   ✓ 封存原始原料: src/core/CLAUDE.md.backup
   ✓ 蒸餾提煉完成
   ✓ 精華純度檢查通過

✨ src/core/CLAUDE.md 蒸餾完成！純度提升，更易吸收。

📥 原料備份位置: src/core/CLAUDE.md.backup
🔄 如需還原: cp src/core/CLAUDE.md.backup src/core/CLAUDE.md
```

### 輸出範例（遞歸模式）

```
🔥 開始遞歸蒸餾 /path/to/project...

📋 發現 CLAUDE.md 檔案: N 個（範例）
   🔴 Critical: 1 個（專案根目錄）
   🟠 High: 2 個（主要模組）
   🟡 Medium: 1 個（子模組）
   🟢 Low: 1 個（測試）

⚗️ 開始蒸餾處理...

[1/N] 🔴 CLAUDE.md（根目錄）
   ✓ X 行 → Y 行 (-Z%)
   ✓ 備份: CLAUDE.md.backup

[2/N] 🟠 src/CLAUDE.md（主要模組）
   ✓ X 行 → Y 行 (-Z%)
   ✓ 備份: src/CLAUDE.md.backup

[3/N] 🟠 src/core/CLAUDE.md（主要模組）
   ✓ X 行 → Y 行 (-Z%)
   ✓ 備份: src/core/CLAUDE.md.backup

[4/N] 🟡 src/core/utils/CLAUDE.md（子模組）
   ✓ X 行 → Y 行 (-Z%)
   ✓ 備份: src/core/utils/CLAUDE.md.backup

[5/N] 🟢 tests/CLAUDE.md（測試）
   ✓ X 行 → Y 行 (-Z%)
   ✓ 備份: tests/CLAUDE.md.backup

✅ 遞歸蒸餾完成！
   📊 處理檔案: N 個
   📉 平均減少: -Z% 體積
   💾 備份檔案: N 個
```

---

## 📄 內容分類規則

### 精華識別模式

```markdown
# 精華內容特徵（高沸點，需要保留）
## 🔴 絕對約束
## 🎯 核心原則
## ❌ 禁止事項
## ✅ 強制事項
## 設計哲學
## 思考框架
## 價值導向
```

### 雜質識別模式

```markdown
# 雜質內容特徵（低沸點，可以蒸發）
### 參數配置
### 範例代碼
### 工具使用
### 具體數值
### 錯誤代碼
### 步驟說明
### 詳細檢查清單 (但保留核心驗證要點)
```

---

## 🎯 執行約束

### 蒸餾專屬約束
- **備份優先**: 蒸餾前必須建立 `.backup` 檔案
- **保留核心**: 絕不刪除核心原則和約束
- **精簡描述**: 縮短冗長說明，保留核心意義
- **結構完整**: 確保蒸餾後文檔結構完整

### 遞歸處理約束
- **使用 Glob 或 find**: 正確發現所有 CLAUDE.md
- **分類處理**: 按重要性分類（Critical/High/Medium/Low），優先處理關鍵文檔
- **順序處理**: 從根目錄到深層模組，按重要性順序處理
- **進度報告**: 每處理一個檔案報告進度
- **錯誤處理**: 單一檔案失敗不影響其他檔案
- **可還原性**: 所有操作都可透過備份還原

---

## 💡 蒸餾最佳實踐

### 文檔維護原則
1. **定期蒸餾**: 每季度評估文檔濃度
2. **持續提純**: 隨時蒸餾新增的冗餘內容
3. **版本記錄**: 重要蒸餾過程需要記錄
4. **團隊品嚐**: 蒸餾前與團隊達成共識

### 內容組織原則
1. **純度優先**: CLAUDE.md 專注於核心原則（為何做）
2. **精簡提煉**: 去除過多的巢狀結構和冗餘細節
3. **易於吸收**: 善用標題、精簡描述
4. **持續蒸餾**: 與專案發展保持同步

### 遞歸處理建議
1. **先預覽**: 使用 `--dry-run` 先看結果
2. **分批處理**: 大型專案可分目錄處理
3. **定期執行**: 每月或每季度執行一次遞歸蒸餾
4. **版本控制**: 執行前先 commit，方便回滾

---

## 🎯 品質檢查清單
- [ ] 發現了所有 CLAUDE.md 檔案（遞歸模式）
- [ ] 按重要性分類處理順序
- [ ] 每個檔案都建立了備份
- [ ] 分析了精華與雜質內容
- [ ] 提供了蒸餾結果預覽
- [ ] 報告了處理進度和統計
- [ ] 驗證了蒸餾後文檔結構完整

---

> 💡 **蒸餾哲學**: 讓 CLAUDE.md 成為高純度的核心原則指南，如同一瓶精緻的蒸餾酒，濃縮了最精華的智慧。蒸餾過程確保 AI 協作時能快速吸收核心原則，而不被冗餘細節干擾。

> 🤖 **AI 導航價值**: 保留目錄結構和核心 API 描述的蒸餾後 CLAUDE.md，對 AI 協作開發極具價值。如同為 AI 提供了濃縮的地圖和詞彙表，讓 AI 能快速理解代碼庫架構，大幅提升開發效率和準確性。

> 🔄 **遞歸處理價值**: 一次處理整個專案的所有 CLAUDE.md，確保文檔一致性，減少維護成本。特別適合有多層子模組的大型專案。
