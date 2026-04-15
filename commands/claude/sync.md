---
description: "檢查 Markdown 文檔與程式碼同步性及內部品質（CLAUDE.md 及說明文檔）"
usage: "/claude:sync [目錄路徑] [選項]"
argument-hint: "預設檢查當前目錄，可指定目錄或 .md 檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
permission-mode: "acceptEdits"
---

# CLAUDE.md Sync - 程式碼同步與品質檢查工具

你是 Markdown 文檔同步檢查專家，負責驗證文檔與實際程式碼的一致性、涵蓋性，以及文檔內部品質。

## 🎯 核心目標

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

> **💡 定位說明**: `/claude:sync` 是「檢查與報告」工具，參考 clean 和 distill 的原則來判斷問題。如需實際清理或蒸餾，請執行 `/claude:clean` 或 `/claude:distill`。

---

## 🚀 檢查項目

### 角度一：程式碼一致性

| 檢查項目 | 說明 | 驗證方式 |
|---------|------|----------|
| 檔案路徑引用 | 文檔中的路徑是否存在 | `Bash test -f` |
| 類別/函數簽名 | 描述的簽名是否正確 | `Grep` 搜索實際定義 |
| 行為描述 | 描述的行為是否與實際一致 | `Read` 程式碼內容比對 |
| 目錄結構 | 描述的結構是否正確 | `Bash ls` 驗證 |

### 角度二：涵蓋性檢查

| 檢查項目 | 說明 | 驗證方式 |
|---------|------|----------|
| 重要模組遺漏 | 核心模組是否被記錄 | 掃描目錄結構 |
| API 完整性 | 公開 API 是否都有記錄 | `Grep` 搜索 `def`/`class` |
| 規範覆蓋 | 重要規範是否被記錄 | 檢查配置檔案 |

### 角度三：元資訊檢查（整合 /claude:clean）

> **參考**: `@./clean.md`

#### 應該移除的元資訊

| 模式 | 範例 | 原因 |
|------|------|------|
| 版本號 | `> **版本**: 2.0` | AI 不關心版本歷史 |
| 更新日期 | `> **更新日期**: 2025-01-01` | AI 只需要當前規則 |
| 歷史變更 | `## 變更歷史\n - v1.0: ...` | 應放 CHANGELOG.md |
| 統計資訊 | `行數: 387`, `字數: 5234` | 對 AI 無意義 |
| 生效日期 | `> **生效日期**: 2025-01-01` | 不影響規則內容 |

#### 可以保留的資訊

| 模式 | 範例 | 原因 |
|------|------|------|
| 符號連結說明 | `🔗 Symbolic Link: ...` | 解釋檔案結構 |
| 專案概述 | `## 專案概述\nxxx 專案是...` | AI 需要了解專案 |
| 繼承關係 | `**繼承**: ~/.claude/CLAUDE.md` | AI 需要知道繼承關係 |

### 角度四：蒸餾評估（整合 /claude:distill，--all 選項）

> **參考**: `@./distill.md`

#### 精華 vs 冗餘 vs 灰色地帶分類

**✅ 應該保留的「精華」**：
- 核心原則/約束、絕對約束、設計哲學、開發鐵律
- 🤖 AI 導航資訊（目錄結構、核心 API 描述）
- 架構圖、核心表格、使用範例（< 15 行）、檢查清單

**❌ 應該蒸餾掉的「冗餘」**：
- 過時範例、重複說明、冗長歷史、環境特定、教學細節

**⚠️ 灰色地帶（預設保留）**：

| 內容類型 | 保留條件 | 移除條件 |
|---------|---------|---------|
| 範例程式碼 | 展示核心 API | 過時、重複、> 20 行 |
| 檢查清單 | 行為約束、決策要點 | 顯而易見、過於細節 |
| 配置參數 | 影響行為的關鍵參數 | 很少修改的環境參數 |
| 表格 | 模組職責、組件對照 | 過時資訊、重複內容 |

#### 實作細節處理策略

> **核心原則**：蒸餾不是「直接刪除」，而是「提煉精華」。

**❌ 直接移除**：詳細程式碼步驟、過多配置參數列表、版本變更歷史
**✅ 簡潔描述替代**：重要設計概念（為什麼）、關鍵機制的一句話總結、指向源碼位置的引用

---

## 📝 內容變更評估原則

> **核心目標**：當需要新增、刪除、修改 CLAUDE.md 內容時，參考以下原則判斷。

### 新增內容時

**✅ 應該新增**（參考 distill 精華原則）：
- 核心原則/約束、絕對約束、設計哲學
- AI 導航資訊（目錄結構、核心 API 描述）
- 架構圖、核心表格、使用範例（< 15 行）

**❌ 不應該新增**（參考 clean 元資訊原則）：
- 版本號、更新日期、歷史變更
- 統計資訊（行數、字數）
- 過時範例、重複說明、教學細節

### 刪除內容時

**✅ 應該刪除**（參考 clean 原則）：
- 版本號、更新日期、生效日期
- 歷史變更章節（## 變更歷史、## Changelog）
- 統計資訊

**✅ 應該刪除**（參考 distill 冗餘原則）：
- 過時範例、重複說明、冗長歷史
- 環境特定配置、教學細節

**⚠️ 謹慎評估**（灰色地帶，預設保留）：
- 範例程式碼（檢查是否展示核心 API）
- 檢查清單（檢查是否為行為約束）
- 配置參數（檢查是否影響關鍵行為）

### 修改內容時

**✅ 應該簡潔描述替代**（參考 distill 實作細節處理策略）：
- 詳細程式碼步驟 → 一句話總結 + 源碼引用
- 過多配置參數列表 → 關鍵參數 + 配置檔引用
- 版本變更歷史 → 簡化的「已移除」列表

---

### 角度五：內部品質檢查（預設執行）

| 檢查維度 | 說明 | 驗證方式 |
|---------|------|----------|
| **自洽性** | 術語統一、前後描述一致、定義與使用吻合 | 文檔內容比對 |
| **矛盾性** | 規則衝突、範例與說明矛盾 | 邏輯分析 |
| **順序** | 章節編號連續、標題層級正確（不跳級） | 結構掃描 |
| **自包含** | 引用檔案/路徑存在、外部依賴可獲取 | `Bash test` 驗證 |
| **精準度** | 技術描述正確、程式碼範例可執行 | 實際驗證 |

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 檢查當前目錄的 CLAUDE.md
/claude:sync

# 2. 檢查指定檔案
/claude:sync src/core/CLAUDE.md

# 3. 檢查指定目錄（僅該目錄層級）
/claude:sync src/core

# 4. 遞歸檢查所有子目錄的 CLAUDE.md
/claude:sync --recursive
/claude:sync -r

# 5. 遞歸檢查 + 清理元資訊
/claude:sync --recursive --clean
/claude:sync -rc

# 6. 完整處理（檢查 + 清理 + 蒸餾）
/claude:sync --all
/claude:sync -a

# 7. 預覽模式（不實際修改）
/claude:sync --dry-run
/claude:sync --recursive --dry-run
```

### 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 檢查當前目錄的 `CLAUDE.md` |
| **檔案路徑** | 檢查指定的 `CLAUDE.md` 檔案 |
| **目錄路徑** | 檢查指定目錄下的 `CLAUDE.md`（僅該層） |
| **--recursive, -r** | 遞歸檢查所有子目錄的 `CLAUDE.md` |
| **--skip-consistency** | 跳過內部品質檢查（自洽性、矛盾性等） |
| **--dry-run** | 預覽模式，顯示結果但不執行修改 |
| **--verbose** | 顯示詳細檢查過程 |

> **💡 工作流程建議**：
> 1. 執行 `/claude:sync` 檢查問題
> 2. 根據報告決定是否執行 `/claude:clean`（清理元資訊）
> 3. 根據報告決定是否執行 `/claude:distill`（蒸餾精簡）

---

## 📋 執行流程

### 步驟 1: 遞歸發現 CLAUDE.md 檔案

See @./_common/recursive-discovery.md for recursive discovery logic.

### 步驟 2: 掃描程式碼結構

```bash
# 識別重要檔案和目錄（使用括號包裝 -o 條件）
find $TARGET_DIR \( -name "*.py" -o -name "*.pyx" -o -name "*.pxd" \) -type f | head -20
find $TARGET_DIR -type d -maxdepth 2

# 掃描公開 API（分別指定 --include 或使用 find）
grep -r "^def " $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"
grep -r "^class " $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"
```

### 步驟 3: 提取文檔引用

```python
# 從 CLAUDE.md 提取引用
def extract_references(content: str) -> dict:
    """提取文檔中的引用"""

    references = {
        "file_paths": [],      # 檔案路徑
        "class_names": [],     # 類別名稱
        "function_names": [],  # 函數名稱
        "modules": [],         # 模組名稱
    }

    # 提取檔案路徑
    import re
    file_patterns = r'`[\w/.-]+/[\w/.-]+\.(py|yaml|toml)`|`[\w/.-]+/`'
    references["file_paths"] = re.findall(file_patterns, content)

    # 提取類別名稱
    class_patterns = r'\*\*[\w]+\*\*|`[\w]+`[\s]*類|class\s+[\w]+'
    references["class_names"] = re.findall(class_patterns, content)

    # 提取函數名稱
    func_patterns = r'`[\w]+\(\)`|function\s+[\w]+|函數\s+[\w]+'
    references["function_names"] = re.findall(func_patterns, content)

    return references
```

### 步驟 4: 驗證一致性

```bash
# 驗證檔案路徑
for path in "${references[file_paths]}"; do
    if [ -f "$path" ]; then
        echo "✅ $path"
    else
        echo "❌ $path 不存在"
    fi
done

# 驗證類別/函數（分別指定 --include）
for name in "${references[class_names]}"; do
    if grep -r "class $name" $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"; then
        echo "✅ $name"
    else
        echo "⚠️  $name 未找到"
    fi
done
```

### 步驟 5: 命令涵蓋性檢查

```bash
# 重要！掃描所有命令檔案，檢查是否被記錄
ALL_COMMAND_FILES=$(find $TARGET_DIR -name "*.md" -type f | grep -v "CLAUDE.md")

for cmd_file in $ALL_COMMAND_FILES; do
    # 推導命令名稱
    # e.g., "worktree/status.md" -> "/worktree:status"
    # e.g., "claude/clean.md" -> "/claude:clean"
    cmd_name=$(echo "$cmd_file" | sed "s|$TARGET_DIR||" | sed 's|\.md$||' | sed 's|^/|/|')

    # 檢查是否在 CLAUDE.md 中
    if grep -q "$cmd_name" "$CLAUDE_MD"; then
        echo "✅ $cmd_name 已記錄"
    else
        echo "❌ $cmd_name 未記錄"
    fi
done
```

### 步驟 6: 程式碼涵蓋性檢查

```bash
# 如果目錄中有程式碼檔案，檢查是否被記錄
CODE_FILES=$(find $TARGET_DIR \( -name "*.py" -o -name "*.pyx" -o -name "*.pxd" \) -type f 2>/dev/null)
if [ -n "$CODE_FILES" ]; then
    echo ""
    echo "### 程式碼檔案涵蓋性檢查"
    for code_file in $CODE_FILES; do
        filename=$(basename "$code_file")
        if grep -q "$filename" "$CLAUDE_MD"; then
            echo "✅ $filename 已記錄"
        else
            echo "⚠️  $filename 未記錄"
        fi
    done
fi
```

### 步驟 7: 清理元資訊（--clean 選項）

```bash
# 呼叫 /claude:clean 功能
# 移除版本號、日期、統計等元資訊
```

### 步驟 8: 蒸餾（--all 選項）

```bash
# 呼叫 /claude:distill 功能
# 蒸餾精簡 CLAUDE.md
```

### 步驟 9: 內部品質檢查（預設執行，除非 --skip-consistency）

```markdown
## 五維度檢查流程

### 9.1 自洽性檢查
- 術語使用是否統一（相同概念是否用相同詞彙）
- 前後描述是否一致
- 定義與使用是否吻合

### 9.2 矛盾性檢查
- 是否存在互相矛盾的陳述
- 規則之間是否有衝突
- 範例與說明是否矛盾

### 9.3 順序檢查
- 章節編號是否連續
- 標題層級是否正確（`#` → `##` → `###`，不跳級）
- 內容組織是否合理

### 9.4 自包含檢查
- 引用的檔案/路徑是否存在（已在前面的步驟驗證）
- 外部依賴是否可獲取
- 讀者是否需要額外資訊才能理解

### 9.5 精準度檢查
- 技術描述是否正確
- 程式碼範例是否可執行
- 連結是否有效
```

---

## 📊 輸出格式

### 單檔案檢查輸出

```
## CLAUDE.md 同步檢查報告

檔案: /path/to/CLAUDE.md（範例）

### 📋 程式碼一致性檢查

#### 檔案路徑引用
- ✅ src/core/engine.py
- ✅ src/core/config.py
- ❌ src/legacy/old_module.py（檔案不存在）

#### 類別/函數簽名
- ✅ DataEngine
- ✅ process_data()
- ⚠️  validate_input()（簽名已變更：現在需要 config 參數）

#### 行為描述
- ⚠️  "DataEngine 會自動重連" → 實際程式碼沒有自動重連邏輯

### 📂 涵蓋性檢查

#### 重要模組檢查
掃描目錄: /path/to/src/
- ✅ src/core/CLAUDE.md
- ⚠️  src/api/（未記錄在主文檔）
- ⚠️  src/utils/（未記錄在主文檔）

#### 公開 API 檢查
發現 N 個公開函數，文檔記錄 M 個
- ⚠️  遺漏: helper_function(), validate_config(), get_status()

### 🧹 元資訊檢查（整合 /claude:clean）
- ❌ 發現版本號: vX.Y
- ❌ 發現更新日期: YYYY-MM-DD
- ✅ 可保留: 符號連結說明、專案概述、繼承關係
- 💡 建議執行 `/claude:sync --clean` 或 `--all` 清理

### 🍶 蒸餾評估（整合 /claude:distill，--all 選項）
- ✅ 精華: N 個核心原則、M 個架構圖
- ❌ 冗餘: K 個過時範例、L 個重複說明
- ⚠️ 灰色地帶: P 個（預設保留）
- 💡 建議執行 `/claude:sync --all` 完整處理

### 📝 內部品質檢查

#### 自洽性 [✅/⚠️/❌]
[發現的問題或「通過」]

#### 矛盾性 [✅/⚠️/❌]
[發現的問題或「通過」]

#### 順序 [✅/⚠️/❌]
[發現的問題或「通過」]

#### 自包含 [✅/⚠️/❌]
[發現的問題或「通過」]

#### 精準度 [✅/⚠️/❌]
[發現的問題或「通過」]

### 📊 總結
- 程式碼一致性: X%
- 涵蓋性: Y%
- 內部品質: Z/100
- 元資訊: 需要清理

建議優先處理：
1. 移除不存在的檔案引用
2. 更新變更的 API 簽名
3. 補充遺漏的模組說明
4. 修正內部品質問題
5. 清理元資訊
```

### 遞歸模式輸出
See @./_common/recursive-output.md for recursive output format template.

### 遞歸同步檢查報告範例

```
## 遞歸同步檢查報告

目錄: /path/to/project
發現 CLAUDE.md: 5 個

### 🔴 Critical（專案根目錄）
**檔案**: CLAUDE.md
- 程式碼一致性: ✅ 90%
- 涵蓋性: ⚠️ 75%
- 內部品質: ⚠️ 85/100（2 個矛盾問題）
- 元資訊: ❌ 需要清理（版本號、日期）
- 蒸餾評估: ⚠️ 3 個冗餘、2 個灰色地帶

### 🟠 High（主要模組）
**檔案**: src/CLAUDE.md
- 程式碼一致性: ✅ 95%
- 涵蓋性: ✅ 90%
- 內部品質: ✅ 95/100
- 元資訊: ✅ 乾淨
- 蒸餾評估: ✅ 精華為主

**檔案**: src/core/CLAUDE.md
- 程式碼一致性: ⚠️ 80%（2 個 API 簽名變更）
- 涵蓋性: ✅ 85%
- 內部品質: ✅ 90/100
- 元資訊: ❌ 有版本號
- 蒸餾評估: ⚠️ 1 個過時範例

### 🟡 Medium（子模組）
**檔案**: src/core/utils/CLAUDE.md
- 程式碼一致性: ✅ 100%
- 涵蓋性: ⚠️ 70%（遺漏 helper 函數）
- 內部品質: ⚠️ 80/100（術語不一致）
- 元資訊: ✅ 乾淨

### 🟢 Low（測試）
**檔案**: tests/CLAUDE.md
- 程式碼一致性: ✅ 95%
- 涵蓋性: ✅ 90%
- 內部品質: ✅ 100/100
- 元資訊: ✅ 乾淨

### 📊 整體統計
- 檔案數量: 5 個
- 平均程式碼一致性: 90%
- 平均涵蓋性: 82%
- 平均內部品質: 90/100
- 需要清理: 2 個
- 需要蒸餾: 1 個

建議執行: `/claude:sync --recursive --clean`
```

### 執行清理後輸出

```
## CLAUDE.md 同步檢查 + 清理完成

檔案: /path/to/CLAUDE.md（範例）

### ✅ 檢查完成
- 一致性: X%（已報告問題）
- 涵蓋性: Y%（已報告遺漏）

### 🧹 清理完成
- 移除版本號: vX.Y
- 移除更新日期: YYYY-MM-DD
- 移除歷史章節: 無
- 移除統計資訊: 無

### 📄 處理結果
- 原始行數: N 行
- 清理後: M 行 (-Z%)
- 備份檔案: CLAUDE.md.backup
```

### --all 完整處理輸出

```
## CLAUDE.md 完整處理（檢查 + 清理 + 蒸餾）

檔案: /path/to/CLAUDE.md（範例）

### 步驟 1: 同步檢查
- 一致性問題: N 項
- 涵蓋性遺漏: M 項
- 元資訊問題: K 項

### 步驟 2: 清理元資訊
- 移除版本號、日期
- 移除統計資訊
- X 行 → Y 行

### 步驟 3: 蒸餾精簡
- 識別精華: N 個核心原則
- 移除冗餘: M 個實作細節
- Y 行 → Z 行

### ✅ 最終結果
- 原始: X 行
- 處理後: Z 行 (-P%)
- 備份: CLAUDE.md.backup (原始)
- 備份: CLAUDE.md.pre-distill.md (清理後)
```

---

## 🎯 執行約束

### 遞歸處理約束
See @./_common/recursive-constraints.md

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

## 💡 使用建議

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

## 🎯 品質檢查清單

### 程式碼同步檢查
- [ ] 發現了所有 CLAUDE.md 檔案（遞歸模式）
- [ ] 掃描了程式碼結構和重要檔案（Python/Cython）
- [ ] 提取了文檔中的所有引用（檔案路徑、類別、函數）
- [ ] 驗證了檔案路徑存在性
- [ ] 驗證了類別/函數簽名正確性（實際讀取程式碼確認）
- [ ] 檢查了命令涵蓋性（.md 檔案是否被記錄）
- [ ] 檢查了程式碼涵蓋性（.py/.pyx/.pxd 檔案是否被記錄）

### 內部品質檢查（預設執行）
- [ ] 檢查了自洽性（術語統一、定義吻合）
- [ ] 檢查了矛盾性（規則衝突、範例矛盾）
- [ ] 檢查了順序（章節編號、標題層級）
- [ ] 檢查了自包含（引用完整、依賴可獲取）
- [ ] 檢查了精準度（技術描述、程式碼可執行）

### 清理與蒸餾
- [ ] 檢查了元資訊（--clean 選項）
- [ ] 執行了清理（--clean 或 --all）
- [ ] 執行了蒸餾（--all）

### 報告與備份
- [ ] 提供了完整的檢查報告（含具體位置和證據）
- [ ] 建立了備份檔案

---

> 💡 **同步哲學**: CLAUDE.md 是活文檔，必須與程式碼同步演進。定期檢查同步性，確保 AI 協作時獲得準確的資訊，避免過時文檔導致誤導。

> 🔍 **涵蓋性價值**: 完整的文檔涵蓋讓 AI 更全面理解專案，減少「不知道有這個功能」的情況，提升開發效率和準確性。

> 📝 **內部品質價值**: 文檔自洽、無矛盾、結構合理，讓 AI 能正確理解規則，避免因文檔問題導致的錯誤決策。

> 🧹 **元資訊評估價值**: 參考 `/claude:clean` 原則，識別對 AI 無意義的元資訊，減少 token 消耗。

> 🍶 **蒸餾評估價值**: 參考 `/claude:distill` 原則，識別精華、冗餘、灰色地帶，指導內容變更決策。

> ⚡ **工作流程**: `/claude:sync` 檢查 → 根據報告決定是否執行 `/claude:clean` 或 `/claude:distill`
