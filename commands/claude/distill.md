---
description: "蒸餾 Markdown 文檔，提煉核心精華（CLAUDE.md 及說明文檔）"
usage: "/claude:distill [目錄路徑] [選項]"
argument-hint: "預設處理當前目錄，可指定目錄或 .md 檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
permission-mode: "acceptEdits"
---

# CLAUDE.md Distill - 蒸餾精簡工具

你是 Markdown 文檔蒸餾專家，負責將文檔進行 signal/noise 分離，提煉出高 signal 的核心知識。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

## 🎯 核心目標

**適用文檔**：
- **CLAUDE.md**：AI 協作指南，保留核心原則和約束
- **說明文檔**：描述現有系統運作的技術文檔（如 call stack、工作流），保留關鍵行為描述和架構

> **不適用**：設計文檔（描述概念、提案）——設計演進過程可能需要保留歷史脈絡。

使用 `/claude:distill` 指令進行蒸餾：
- **提煉精華**: 保留核心的、不變的開發原則和約束
- **去除冗餘**: 移除具體的實作細節、配置參數、過時範例
- **支援遞歸**: 可一次處理整個目錄樹的所有 CLAUDE.md

**蒸餾比喻**: 如同蒸餾過程提煉出酒精純度，我們提煉出 CLAUDE.md 的核心原則純度。

---

## 📋 核心概念

### Signal / Noise 分類

#### ✅ High Signal — 必須保留

從程式碼**猜不到**的知識：

- **設計理由**: 為什麼這樣做，而非那樣做
- **架構約束**: 不可妥協的設計限制
- **非顯而易見的選擇**: 看起來反直覺但有意義的決策
- **模組邊界**: 這個模組不做什麼
- **失敗教訓**: 從實際 debugging 經驗得到的規則
- **核心原則/約束**: 零容錯、高速迭代、極致工程品質
- **高層級架構圖**: Mermaid/ASCII 展示模組間關係

#### ❌ Low Noise — 應該蒸餾

從程式碼**可直接推導**的內容：

- **API 簽名**: 函數參數和回傳值型別
- **參數表**: 完整的參數列表和預設值
- **欄位列表**: DataFrame 的所有 column 名稱
- **完整範例 (>5 行)**: 應精簡為一句話描述 + `檔案:行號` 引用
- **過時範例**: 不再適用或無法執行的範例
- **重複說明**: 同一概念用不同方式解釋多次
- **通用知識**: LLM 訓練資料已有的知識

#### ⚠️ 灰色地帶（預設保留）

| 內容類型 | 保留條件 | 移除條件 |
|---------|---------|---------|
| **範例程式碼** | <= 5 行，展示關鍵用法 | > 5 行或過時、重複 |
| **檢查清單** | 行為約束、決策要點 | 顯而易見的項目 |
| **配置參數** | 影響行為的關鍵參數 | 很少修改的環境參數 |
| **表格** | 模組職責、組件對照 | 過時資訊、重複內容 |

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

遞歸發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)

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

### High Signal 識別模式

```markdown
# High Signal 特徵
## 設計理由 / 為什麼
## 架構約束 / 不可妥協
## 非顯而易見的選擇
## 失敗教訓 / 踩坑指南
## 模組邊界 / 不做什麼
```

### Low Noise 識別模式

```markdown
# Low Noise 特徵
### API 簽名 / 參數表
### 完整欄位列表
### 程式碼範例 > 5 行
### 過時範例 / 重複說明
### 通用知識
```

### Low Noise 處理策略

> **核心原則**：蒸餾不是「直接刪除」，而是「signal/noise 分離」。Low noise 應轉化為簡潔描述或完全移除。

#### ❌ 直接移除（會失去脈絡）

- 詳細的程式碼步驟
- 過多的配置參數列表
- 版本變更歷史

#### ✅ 簡潔描述替代（保留精華）

- 重要的設計概念（為什麼）
- 關鍵機制的一句話總結
- 指向源碼位置的引用

#### 處理範例

```markdown
## ❌ 錯誤：直接移除（失去脈絡）

### 配置說明
[完全刪除]

## ✅ 正確：簡潔描述替代（保留精華）

### 配置說明
使用環境變數控制日誌級別，預設 INFO。
詳見 `config.py:15-30`。

💡 **原理說明**：直接移除會讓 AI 失去理解「為什麼這樣設計」的脈絡。
簡潔描述保留設計意圖，同時指向源碼讓 AI 需要時可以查證。
```

---

## 🔬 蒸餾執行流程

### 標準流程（非 --dry-run）

1. **掃描文件**：識別 High Signal、Low Noise、灰色地帶
2. **顯示預覽**：

```
⚗️ 蒸餾預覽：

✅ High Signal (N 項)：
  - 設計理由
  - 架構約束
  - 失敗教訓

⚠️ 灰色地帶 (N 項) - 預設保留：
  - 範例程式碼 (X 個) → 保留（<= 5 行）
  - 檢查清單 (X 項) → 保留（行為約束）

❌ Low Noise (N 項)：
  - API 簽名
  - 參數表
  - 完整範例 > 5 行

📊 預估結果：X 行 → Y 行 (-Z%)
```

3. **用戶確認**：詢問「確認執行蒸餾？(y/n)」
4. **執行蒸餾**：備份原檔，寫入蒸餾結果
5. **Decoder Test（dry run）**：驗證蒸餾後的 Encoder 品質
   - 基於蒸餾後的 CLAUDE.md，回答 4 個核心問題（職責、設計決策、約束、邊界）
   - 全部通過 → 完成報告
   - 有失敗 → 從 `.backup` 還原並重新評估
6. **完成報告**：顯示處理統計

### 預覽模式（--dry-run）

只執行步驟 1-2，不實際修改檔案。

---

## 🎯 執行約束

### 遞歸處理約束
遞歸處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

### 蒸餾專屬約束

**🔥 謹慎原則：有疑問就保留**
- 無法確定是否為雜質的內容，優先保留
- 寧可少刪也不要誤刪
- 用戶可以再次執行 `--aggressive` 刪更多

**🎯 AI 導航價值優先**
以下內容對 AI 協作極具價值，必須特別謹慎：
- 架構圖（理解模組關係）
- 核心表格（快速定位 API）
- 使用範例（理解 API 用法）
- 引用來源（查證依據）

**📦 操作約束**
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
- [ ] 識別了 High Signal、Low Noise、灰色地帶三類內容
- [ ] 灰色地帶內容預設保留（謹慎原則）
- [ ] 提供了蒸餾結果預覽
- [ ] 獲得用戶確認後才執行
- [ ] 報告了處理進度和統計
- [ ] 驗證了蒸餾後文檔結構完整
- [ ] 執行 Decoder Test（dry run）驗證 Encoder 品質

---

> 💡 **蒸餾哲學**: 蒸餾 = signal/noise 分離。保留從程式碼猜不到的設計知識，移除可推導的冗餘內容。目標不是讓文檔越短越好，而是提升 signal/noise ratio。

> 🤖 **AI 導航價值**: 高 signal/noise ratio 的 CLAUDE.md 讓 AI 快速理解模組本質，避免被 API 簽名、參數表等雜訊干擾。

> 🔄 **遞歸處理價值**: 一次處理整個專案的所有 CLAUDE.md，確保文檔一致性，減少維護成本。
