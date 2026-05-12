---
description: "檢查 Markdown 文檔與程式碼同步性及內部品質"
when_to_use: "Check CLAUDE.md synchronization with code: navigation validity, code consistency, signal/noise ratio. Supports --recursive, --changed-since, --quality."
usage: "/claude:sync [目錄路徑] [選項]"
argument-hint: "/claude:sync [目錄路徑] [--recursive] — 預設檢查當前目錄，可指定目錄或 .md 檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# CLAUDE.md Sync - 程式碼同步與品質檢查工具

你是 Markdown 文檔同步檢查專家，負責驗證文檔與實際程式碼的一致性、涵蓋性，以及文檔內部品質。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md) — 讀取此檔案以理解 High Signal / Low Noise 分類標準。

## 核心目標

**適用文檔**：
- **CLAUDE.md**：AI 協作指南，必須與程式碼保持同步
- **說明文檔**：描述現有系統運作的技術文檔（如 call stack、工作流），必須與實際程式碼一致

> **不適用**：設計文檔（描述概念、提案、未來計畫）——沒有對應的現有程式碼可驗證一致性。

### 文檔類型判斷

當處理非 CLAUDE.md 的 `.md` 檔案時，AI 必須先判斷文檔類型：

| 類型 | 判斷依據 | 程式碼一致性 | 範例 |
|------|---------|------------|------|
| **說明文檔** | 描述現有系統的 API、資料結構、流程、call stack | **需要檢查** | callstacks_v3.md, workflow_v3.md |
| **設計文檔** | 描述概念、架構提案、設計決策 | **跳過** | filter_tree_design_v1.md |

**判斷方法**：文檔是否聲稱描述程式碼的「當前狀態」？是的話執行完整流程，否則跳過程式碼一致性檢查，僅做內部品質檢查。

**文檔必須與實際程式碼保持同步，且內部品質良好**：
- **程式碼一致性**: 文檔描述的 API/模組/規範是否與實際一致
- **廣泛涵蓋性**: 重要程式碼模組是否被文檔涵蓋
- **元資訊評估**: 基於 `/claude:clean` 原則判斷是否需要清理
- **蒸餾評估**: 基於 `/claude:distill` 原則識別精華、冗餘、灰色地帶
- **內部品質**: 文檔自洽、無矛盾、結構合理、內容精準
- **實際驗證**: 開啟相關程式碼確認，而非只檢查文檔本身

> **定位說明**: `/claude:sync` 是「檢查與報告」工具，參考 clean 和 distill 的原則來判斷問題。如需實際清理或蒸餾，請執行 `/claude:clean` 或 `/claude:distill`。

---

## 檢查項目

### 執行分層

預設只執行核心層（最關鍵的三個角度）。用 `--quality` 加入品質層，`--all` 執行全部。

| 層級 | 包含角度 | 參數 |
|------|---------|------|
| **核心層** | 導航有效性 + 程式碼一致性 + Signal/Noise | 預設 |
| **品質層** | + 內部品質 + 元資訊 + 引用語法 | `--quality` |
| **完整層** | + 涵蓋性 + 連鎖影響 + 蒸餾評估 | `--all` |

**設計理由**：CLAUDE.md 的價值金字塔 — 導航（LLM 找到程式碼）→ 理解（LLM 知道為什麼）→ 品質（LLM 高效消費）。導航層做不好，其他檢查都沒意義。

### 9 個檢查角度概覽

| 角度 | 層級 | 一行摘要 |
|------|------|---------|
| 1. 導航有效性 | 核心 | CLAUDE.md 是否讓 AI 從概念定位到程式碼（最重要） |
| 2. 程式碼一致性 | 核心 | 檔案路徑、簽名、行為描述是否與實際程式碼一致 |
| 3. 涵蓋性 | 完整 | 核心模組和公開 API 是否被文檔記錄 |
| 4. 元資訊 | 品質 | 是否存在版本號、日期等對 AI 無意義的內容 |
| 5. 蒸餾評估 | 完整 | Signal/Noise ratio 是否健康 |
| 6. 內部品質 | 品質 | 自洽、無矛盾、結構合理、內容精準 |
| 7. Signal/Noise Ratio | 核心 | High Signal 佔比是否足夠 |
| 8. 引用語法 | 品質 | `@` vs `[描述](path)` 選擇是否正確 |
| 9. 連鎖影響 | 完整 | 程式碼變更是否影響消費端文檔 |

完整定義和判斷標準：[sync-check-angles.md](./_common/sync-check-angles.md)

---

## 內容變更評估原則

> **核心目標**：當需要新增、刪除、修改 CLAUDE.md 內容時，參考以下原則判斷。

### 新增內容時

**應該新增**（High Signal）：
- 設計理由、架構約束、非顯而易見的選擇
- 模組邊界、失敗教訓
- 核心原則/約束、高層級架構圖

**不應該新增**（Low Noise）：
- API 簽名、參數表、欄位列表
- 完整範例 (>5 行)
- 元資訊（版本號、更新日期、統計）

### 刪除內容時

**應該刪除**（Low Noise + 元資訊）：
- API 簽名、完整欄位列表
- 版本號、更新日期、生效日期
- 歷史變更章節、統計資訊
- 過時範例、重複說明

**謹慎評估**（灰色地帶，預設保留）：
- 範例程式碼 <= 5 行（檢查是否展示關鍵用法）
- 檢查清單（檢查是否為行為約束）

### 修改內容時

**應該簡潔描述替代**（參考 distill 實作細節處理策略）：
- 詳細程式碼步驟 → 一句話總結 + 源碼引用
- 過多配置參數列表 → 關鍵參數 + 配置檔引用
- 版本變更歷史 → 簡化的「已移除」列表

---

## 命令介面設計

### 基本用法

```bash
# 檢查當前目錄的 CLAUDE.md
/claude:sync

# 檢查指定檔案
/claude:sync src/core/CLAUDE.md

# 遞歸檢查所有子目錄的 CLAUDE.md
/claude:sync --recursive
/claude:sync -r

# 遞歸檢查 + 清理元資訊
/claude:sync --recursive --clean

# 完整處理（檢查 + 清理 + 蒸餾）
/claude:sync --all
/claude:sync -a

# 品質層（加入內部品質 + 引用語法檢查）
/claude:sync --quality

# 預覽模式（不實際修改）
/claude:sync --dry-run

# 增量模式（只檢查 git 變更涉及的檔案）
/claude:sync --changed-since "2026-05-08"
/claude:sync --changed-since HEAD~5
```

### 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 檢查當前目錄的 `CLAUDE.md` |
| **檔案路徑** | 檢查指定的 `CLAUDE.md` 檔案 |
| **目錄路徑** | 檢查指定目錄下的 `CLAUDE.md`（僅該層） |
| **--recursive, -r** | 遞歸檢查所有子目錄的 `CLAUDE.md` |
| **--changed-since** | 增量模式：只檢查 git 變更涉及的檔案 |
| **--skip-consistency** | 跳過內部品質檢查（僅搭配 `--quality` / `--all` 時生效） |
| **--quality** | 加入品質層檢查（內部品質 + 元資訊 + 引用語法） |
| **--all, -a** | 完整層（全部 9 個角度 + 清理 + 蒸餾） |
| **--dry-run** | 預覽模式，顯示結果但不執行修改 |
| **--verbose** | 顯示詳細檢查過程 |

> **工作流程建議**：
> 1. 執行 `/claude:sync` 檢查問題
> 2. 根據報告決定是否執行 `/claude:clean`（清理元資訊）
> 3. 根據報告決定是否執行 `/claude:distill`（蒸餾精簡）

---

## 執行流程

### 步驟概覽

| 步驟 | 名稱 | 觸發條件 |
|------|------|---------|
| 1 | 遞歸發現 CLAUDE.md | 預設執行 |
| 1.5 | 依賴鏈擴展 | 目標目錄有 git diff 變更的 .py 檔案，或使用 --changed-since |
| 1.6 | Sub-doc 擴展 | CLAUDE.md 引用了 .md 子文件 |
| 2 | 掃描程式碼結構 | 預設執行 |
| 3 | 提取文檔引用 | 預設執行 |
| 4 | 驗證一致性 | 預設執行 |
| 5 | 命令涵蓋性檢查 | --all |
| 6 | 程式碼涵蓋性檢查 | --all |
| 7 | 清理元資訊 | --clean |
| 8 | 蒸餾 | --all |
| 9 | 內部品質檢查 | --quality |
| 10 | 導航有效性檢查 | 預設執行（最重要） |

步驟 1-10 的詳細實作邏輯（含 pseudo code、驗證方式、增量模式流程）：[sync-implementation-steps.md](./_common/sync-implementation-steps.md)

遞歸發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)

---

## 輸出格式

6 組輸出格式模板（單檔案報告、Sync Summary、ACTION、遞歸報告、清理後、--all 完整處理）：[sync-output-templates.md](./_common/sync-output-templates.md)

遞歸輸出格式: [recursive-output.md](./_common/recursive-output.md)

### 進階驗證建議

> 當本次 sync 發現 ⚠️ 項目 >= 3 個時，建議執行 `/claude:decode-compare {module}` 進行深度精度驗證。sync 檢查「有沒有」，decode-compare 檢查「對不對」。

---

## 執行約束

### 遞歸處理約束
遞歸處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

### 同步檢查專屬約束
- **實際驗證**: 必須開啟程式碼檔案確認，不猜測
- **引用來源**: 報告問題時標註具體位置和證據（檔案:行號）
- **涵蓋性掃描**: 檢查命令檔案和程式碼檔案是否被記錄
- **報告先行**: 先報告發現，再詢問是否執行清理或蒸餾

### 整合選項約束
- **--clean**: 檢查後執行清理，建立備份
- **--all**: 順序執行（檢查 → 清理 → 蒸餾），每步驟建立備份
- **--dry-run**: 預覽所有操作，不實際修改

---

## 使用建議

### 定期檢查
1. **每週執行**: `/claude:sync --recursive` 檢查同步性
2. **每月清理**: `/claude:sync --recursive --clean` 清理元資訊
3. **每季蒸餾**: `/claude:sync --all` 完整處理

### 觸發時機
- 新增多個程式碼檔案後
- 重構 API 介面後
- 發現文檔描述與實際不符時
- 版本發布前

### 最佳實踐
1. **先預覽**: 使用 `--dry-run` 先看結果
2. **分批處理**: 大型專案可分目錄處理
3. **版本控制**: 執行前先 commit，方便回滾
4. **記錄問題**: 將發現的同步問題記錄到待辦清單

---

## 品質檢查清單

### 核心層檢查（預設執行）

#### 導航有效性（角度一，最重要）
- [ ] 抽取了 3-5 個關鍵概念，驗證每個概念是否有程式碼位置指引
- [ ] 對照職責描述與檔案結構，驗證每項職責有對應的檔案指引
- [ ] 檢查了跨模組依賴是否具體到 class/function（不只是模組名）
- [ ] 對多步驟流程驗證了 step 間 input/output 可追蹤性（無流程的模組標 N/A）
- [ ] 執行了導航 Decoder Test（3 個導航問題，不查源碼）

#### 程式碼一致性（角度二）
- [ ] 發現了所有 CLAUDE.md 檔案（遞歸模式）
- [ ] 從 CLAUDE.md 提取了 sub-doc 引用，分類為說明文檔/設計文檔
- [ ] 對說明文檔執行了程式碼一致性檢查（設計文檔跳過）
- [ ] 掃描了程式碼結構和重要檔案（Python/Cython）
- [ ] 提取了文檔中的所有引用（檔案路徑、類別、函數）
- [ ] 驗證了檔案路徑存在性
- [ ] 驗證了類別/函數簽名正確性（實際讀取程式碼確認）
- [ ] 執行了語義正確性 spot-check（抽查核心演算法描述是否準確）

#### Signal/Noise Ratio（角度七）
- [ ] 評估了 Signal/Noise Ratio（High Signal 比例、Low Noise 識別）

### 品質層檢查（--quality）

#### 內部品質（角度六）
- [ ] 檢查了自洽性（術語統一、定義吻合）
- [ ] 檢查了矛盾性（規則衝突、範例矛盾）
- [ ] 檢查了順序（章節編號、標題層級）
- [ ] 檢查了自包含（引用完整、依賴可獲取）
- [ ] 檢查了精準度（技術描述、程式碼可執行）

#### 元資訊（角度四）
- [ ] 檢查了元資訊（--clean 選項）

#### 引用語法（角度八）
- [ ] 檢查了引用語法正確性（`@` vs `[描述](path)` 選擇）

### 完整層檢查（--all）

#### 涵蓋性（角度三）
- [ ] 檢查了命令涵蓋性（.md 檔案是否被記錄）
- [ ] 檢查了程式碼涵蓋性（.py/.pyx/.pxd 檔案是否被記錄）

#### 蒸餾評估（角度五）
- [ ] 執行了清理（--clean 或 --all）
- [ ] 執行了蒸餾（--all）

#### 連鎖影響（角度九）
- [ ] 追蹤了 import 鏈找出消費端目錄
- [ ] 檢查了消費端 CLAUDE.md 是否需要同步更新
- [ ] 檢查了其他相關 .md 文檔（examples/、docs/ 等）是否需要同步更新

### 報告與備份
- [ ] 提供了完整的檢查報告（含具體位置和證據）
- [ ] 建立了備份檔案

---

> **同步哲學**: CLAUDE.md 是活文檔，必須與程式碼同步演進。定期檢查同步性，確保 AI 協作時獲得準確的資訊。

> **工作流程**: `/claude:clean`（清理 noise）→ `/claude:distill`（蒸餾 signal）→ `/claude:sync`（靜態一致性）→ `/claude:doc-decode`（理解度測試）→ `/claude:decode-compare`（精度驗證）
